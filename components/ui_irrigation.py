import streamlit as st
import sys
import os
import pandas as pd
import pydeck as pdk
import datetime

# Add parent dir to path to import services and config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.api_weather import get_weather_data, get_forecast_data
from services.api_wapor import get_wapor_data
from services.api_gemini import analyze_irrigation, get_map_pro_tip
from utils.calculations import calculate_etc, get_water_savings, calculate_pumping_hours, get_economic_impact
from config import CROP_FACTORS, GROWTH_STAGES, SOIL_THRESHOLDS

def get_traffic_light(weather: dict, soil_moisture: float, soil_type: str) -> tuple:
    """
    Determine the Irrigation Traffic Light status based on weather and soil type.
    """
    if weather.get("rain_coming", False):
        return ("Red", "توقف! هناك أمطار قادمة.", "🔴")
    
    # Custom thresholds for different soils
    threshold = 40.0 # Default
    if "تيرس" in soil_type:
        threshold = 35.0 # Tirs holds water, so >35% is very wet
    elif "رمل" in soil_type:
        threshold = 20.0 # Sand is dry at >20%
        
    if soil_moisture > threshold:
        return ("Yellow", "راقب! التربة لا تزال رطبة.", "🟡")
    else:
        return ("Green", "قم بالري الآن! التربة جافة.", "🟢")

def render_irrigation_advisor(lat: float, lon: float, crop: str, stage: str, soil: str, area: float, pump_rate: float):
    st.header("💧 مستشار الري الذكي")
    st.markdown("سجل مقطعاً صوتياً (مثلاً: هل يجب تشغيل المضخة اليوم؟) أو اكتب سؤالك.")
    
    # Audio Input Placeholder & Text Input
    audio_bytes = st.audio_input("🎤 اضغط هنا لتسجيل رسالتك الصوتية")
    text_input = st.text_input("...أو اكتب سؤالك هنا:")
    
    # --- Initialize Session State ---
    if 'irrigation_results' not in st.session_state:
        st.session_state.irrigation_results = None

    if st.button("تحليل وبحث 🧠", use_container_width=True, type="primary"):
        if not audio_bytes and not text_input:
            st.warning("رجاءً أدخل سؤالاً صوتياً أو كتابياً.")
            return
            
        with st.spinner("الخبير يحلل البيانات حالياً..."):
            # 1. Fetch Context Data
            weather = get_weather_data(lat, lon)
            wapor = get_wapor_data(lat, lon)
            
            if "error" in wapor:
                st.error(f"❌ **فشل جلب بيانات القمر الصناعي:** {wapor['error']}")
                return
            
            # 2. Agricultural Calculations (FAO-56)
            base_kc = CROP_FACTORS[crop]
            stage_multiplier = GROWTH_STAGES[stage]
            kc = base_kc * stage_multiplier 
            
            eto = weather.get('eto', 4.5) * wapor.get('biomass_index', 1.0)
            etc = calculate_etc(kc, eto)
            
            # Allowable Depletion Logic for Today:
            soil_threshold = SOIL_THRESHOLDS.get(soil, 8.0)
            current_moisture = wapor.get("soil_moisture", 30.0)
            
            # Theoretical Daily Need (Always calculated for the UI)
            full_savings = get_water_savings(etc, area)
            daily_need_liters = full_savings['recommended_liters']
            
            # --- Traffic Light Logic ---
            traffic_color, traffic_msg, traffic_icon = get_traffic_light(weather, current_moisture, soil)

            # Scheduled Logic: Consolidation (Skip Days) override
            if etc < (soil_threshold * 0.4) and current_moisture > 25.0:
                pumping_hours = 0.0
                scheduled_liters = 0
                if traffic_color == "Green": # Avoid confusing the user with Green + Skip
                    traffic_color, traffic_msg, traffic_icon = ("Yellow", "التربة جيدة، انتظر يوم السقي الموالي.", "🟡")
            else:
                scheduled_liters = daily_need_liters
                pumping_hours = calculate_pumping_hours(scheduled_liters, pump_rate)
            
            savings_money = get_economic_impact(full_savings['saved_liters'])
            
            # --- Proactive Wind Logic ---
            is_windy = weather.get("wind_speed", 0) > 15
            if is_windy:
                traffic_color, traffic_msg, traffic_icon = ("Red", "توقف! رياح 'الشرقي' قوية.", "🚩")

            # 3. Determine User Prompt
            user_prompt = text_input if text_input else "هل يجب تشغيل المضخة اليوم؟ وكم ساعة؟"

            # 4. Generate AI Advice
            weather['pump_rate'] = pump_rate 
            weather['growth_stage'] = stage 
            location_label = f"({lat}, {lon})"
            
            advice_text = ""
            advice_stream, error_api = analyze_irrigation(user_prompt, weather, round(etc, 2), pumping_hours, traffic_color, location_label, crop, soil, area, stream=True)
            
            placeholder = st.empty()
            if advice_stream:
                try:
                    for chunk in advice_stream:
                        if chunk.text:
                            advice_text += chunk.text
                            placeholder.markdown(f"**{advice_text}**" + " ▌")
                    placeholder.empty()
                except Exception as e:
                    advice_text = f"تعذر الحصول على النصيحة: {str(e)}"
                    placeholder.error(advice_text)
            else:
                if error_api and error_api.startswith("LOCAL_FALLBACK:"):
                    advice_text = error_api.replace("LOCAL_FALLBACK:", "")
                    st.info("ℹ️ نصيحة تقنية (محرك احتياطي):") # Optional indicator
                else:
                    advice_text = f"الخبير الفني غير متاح حالياً. السبب: {error_api if error_api else 'فشل غير معروف'}"
                    placeholder.warning(advice_text)
            
            st.session_state.irrigation_results = {
                "weather": weather,
                "wapor": wapor,
                "advice": advice_text,
                "pumping_hours": pumping_hours,
                "daily_need_liters": daily_need_liters,
                "scheduled_liters": scheduled_liters,
                "savings": full_savings,
                "savings_money": savings_money,
                "traffic": (traffic_color, traffic_msg, traffic_icon),
                "is_windy": is_windy,
                "etc": round(etc, 2),
                "kc": kc
            }

    # --- Render Results ---
    if st.session_state.irrigation_results:
        res = st.session_state.irrigation_results
        weather, wapor = res["weather"], res["wapor"]
        traffic_color, traffic_msg, traffic_icon = res["traffic"]
        pumping_hours = res["pumping_hours"]
        savings_money = res["savings_money"]
        savings = res["savings"]
        is_windy = res["is_windy"]
        advice_text = res["advice"]
        
        st.markdown("---")
        
        # 1. Irrigation Gauge (Custom HTML/CSS)
        irrigation_percent = 0
        gauge_color = "#30363D"
        if traffic_color == "Green":
            irrigation_percent = 100
            gauge_color = "#238636"
        elif traffic_color == "Yellow":
            irrigation_percent = 50
            gauge_color = "#D29922"
        else:
            irrigation_percent = 10
            gauge_color = "#DA3633"

        st.markdown(f"""
        <div style="background-color: #161B22; border: 1px solid #30363D; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 20px;">
            <h3 style="color: #8B949E; margin-bottom: 10px;">حالة الري: {traffic_msg}</h3>
            <div style="width: 200px; height: 100px; margin: 0 auto; position: relative; overflow: hidden;">
                <div style="width: 200px; height: 200px; border-radius: 50%; border: 15px solid #30363D; position: absolute; top: 0; left: 0; box-sizing: border-box;"></div>
                <div style="width: 200px; height: 200px; border-radius: 50%; border: 15px solid {gauge_color}; position: absolute; top: 0; left: 0; box-sizing: border-box; clip-path: inset(0 0 50% 0); transform: rotate({(irrigation_percent * 1.8) - 180}deg);"></div>
                <div style="position: absolute; bottom: 10px; left: 0; width: 100%; color: #FFFFFF; font-size: 1.2rem; font-weight: bold;">{traffic_icon} {traffic_color}</div>
            </div>
            <p style="color: #8B949E; margin-top: 10px;">باقي {int(pumping_hours * 60) if pumping_hours > 0 else 0} دقيقة</p>
        </div>
        """, unsafe_allow_html=True)

        # 2. Premium Metrics Row
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">الاحتياج اليومي</div>
                <div class="metric-value">{int(res['scheduled_liters'])} لتر</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">التوفير الشهري</div>
                <div class="metric-value">{int(savings_money * 30)} درهم</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">رطوبة التربة</div>
                <div class="metric-value">{wapor['soil_moisture']}%</div>
            </div>
            """, unsafe_allow_html=True)

        # 3. AI Advice Section
        st.markdown(f"""
        <div style="background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; padding: 20px; margin-top: 20px; border-right: 5px solid #58A6FF;">
            <h4 style="color: #58A6FF; margin-top: 0;">🤖 المستشار الذكي</h4>
            <p style="color: #C9D1D9; line-height: 1.6;">{advice_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Audio Playback
        from services.api_tts import speak_advice_sync
        if st.button("🔊 استمع للنصيحة بصوت الخبير", use_container_width=True):
            with st.spinner("جاري تحضير صوت الخبير..."):
                voice_path = speak_advice_sync(advice_text)
                st.audio(voice_path, format="audio/mp3", autoplay=True)

        # 4. 7-Day Predictive Graph (Matching Style)
        forecast_list = get_forecast_data(lat, lon)
        accumulated_deficit_mm = 0
        soil_threshold = SOIL_THRESHOLDS.get(soil, 8.0)
        forecast_chart_data = []
        total_weekly_liters = 0
        
        base_kc = CROP_FACTORS[crop]
        stage_multiplier = GROWTH_STAGES[stage]
        kc = base_kc * stage_multiplier

        for day in forecast_list:
            # 1. Scientific Daily Need (The thirsty level of the crop)
            d_etc = calculate_etc(kc, day['eto'])
            d_daily_savings = get_water_savings(d_etc, area)
            d_daily_liters = d_daily_savings['recommended_liters']
            
            # 2. Scheduled Decision (Allowable Depletion)
            accumulated_deficit_mm += d_etc
            if accumulated_deficit_mm >= soil_threshold:
                d_scheduled_savings = get_water_savings(accumulated_deficit_mm, area)
                d_scheduled_liters = d_scheduled_savings['recommended_liters']
                d_pumping = calculate_pumping_hours(d_scheduled_liters, pump_rate)
                accumulated_deficit_mm = 0
            else:
                d_scheduled_liters = 0.0
                d_pumping = 0.0
            
            forecast_chart_data.append({
                "اليوم": day['day_name'],
                "الاحتياج العلمي اليومي (لتر)": d_daily_liters,
                "الري المبرمج (لتر)": d_scheduled_liters,
                "ساعات الري": d_pumping
            })
            total_weekly_liters += d_daily_liters

        st.markdown("### 📅 7-day predictive graph")
        st.markdown(f'<p style="color: #8B949E; margin-top: -10px;">مجموع الأسبوع: {int(total_weekly_liters)} لتر</p>', unsafe_allow_html=True)
        
        chart_df = pd.DataFrame(forecast_chart_data)
        
        # We use a custom bar chart with Altair for better color control matching the image
        import altair as alt
        
        base = alt.Chart(chart_df).encode(x=alt.X('اليوم:N', sort=None, title=None))
        
        bar1 = base.mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, size=30).encode(
            y=alt.Y('الاحتياج العلمي اليومي (لتر):Q', title=None),
            color=alt.value('#238636'), # Darker Green
            tooltip=['اليوم', 'الاحتياج العلمي اليومي (لتر)']
        )
        
        bar2 = base.mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, size=20).encode(
            y=alt.Y('الري المبرمج (لتر):Q', title=None),
            color=alt.value('#7EE787'), # Brighter Green matching the image
            tooltip=['اليوم', 'الري المبرمج (لتر)']
        )
        
        final_chart = alt.layer(bar1, bar2).configure_view(stroke=None).configure_axis(
            grid=False, domain=False, labelColor='#8B949E', tickColor='#8B949E'
        ).properties(width='container', height=300)
        
        st.altair_chart(final_chart, use_container_width=True)
        
        st.markdown(f"""
        <div style="background-color: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 10px; display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #8B949E; font-size: 0.8rem;">Weekly Total: {int(total_weekly_liters)} Liters</span>
            <div style="display: flex; gap: 15px;">
                <span style="color: #238636; font-size: 0.8rem;">● الاحتياج</span>
                <span style="color: #7EE787; font-size: 0.8rem;">● المبرمج</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
