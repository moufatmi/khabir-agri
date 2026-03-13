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
            
            # Scheduled Logic: Consolidation (Skip Days)
            if etc < (soil_threshold * 0.4) and current_moisture > 25.0:
                pumping_hours = 0.0
                scheduled_liters = 0
            else:
                scheduled_liters = daily_need_liters
                pumping_hours = calculate_pumping_hours(scheduled_liters, pump_rate)
            
            savings_money = get_economic_impact(full_savings['saved_liters'])
            
            # --- Traffic Light Logic ---
            traffic_color, traffic_msg, traffic_icon = get_traffic_light(weather, current_moisture, soil)

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
            advice_stream = analyze_irrigation(user_prompt, weather, round(etc, 2), pumping_hours, traffic_color, location_label, crop, soil, area, stream=True)
            
            placeholder = st.empty()
            if advice_stream:
                for chunk in advice_stream:
                    if chunk.text:
                        advice_text += chunk.text
                        placeholder.markdown(f"**{advice_text}**" + " ▌")
                # Removed final placeholder write to avoid duplication
                placeholder.empty()
            
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
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.markdown(f"<h1 style='margin:0;'>{traffic_icon} {traffic_msg}</h1>", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"<div style='background-color:#E8F5E9; border-radius:10px; padding:10px; text-align:center; color:#2E7D32; font-weight:bold;'>💧 توفير التكاليف: {savings_money} درهم</div>", unsafe_allow_html=True)
        
        from services.api_tts import speak_advice_sync
        col_t1, col_t2 = st.columns([0.85, 0.15])
        with col_t1:
            st.info("💡 نصيحة الخبير الشخصية:")
        with col_t2:
            if st.button("🔊", help="استمع للنصيحة بصوت الخبير"):
                with st.spinner("جاري تحضير صوت الخبير..."):
                    voice_path = speak_advice_sync(advice_text)
                    st.audio(voice_path, format="audio/mp3", autoplay=True)

        st.markdown(f"**{advice_text}**")
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### ⏲️ جدول الري المقترح")
            if pumping_hours > 0:
                prompt_time = "06:00 AM" 
                end_time = (datetime.datetime.strptime(prompt_time, "%I:%M %p") + datetime.timedelta(hours=pumping_hours)).strftime("%I:%M %p")
                st.success(f"**الفترة:** {prompt_time} - {end_time}")
                st.metric("مدة التشغيل اليوم", f"{pumping_hours} ساعة")
            else:
                st.warning("📴 لا توجد حاجة للري اليوم (Skip Day).")
                st.info("التربة لا تزال تحتوي على رصيد مائي كافٍ.")

        with c2:
            st.markdown("### ⚠️ تنبيهات استباقية")
            if is_windy:
                st.error(f"⚠️ **تنبيه رياح:** هناك رياح قوية ({weather.get('wind_speed')} م/ث).")
            elif weather.get("heatwave_alert"):
                st.error("🔥 **موجة حر:** تجنب الري في وقت الظهيرة.")
            else:
                st.info("🌤️ الجو مناسب حالياً للري.")

        m_need, m_sched = st.columns(2)
        m_need.metric("الاحتياج اليومي (العلومي)", f"{res['daily_need_liters']} لتر")
        m_sched.metric("الكمية المقررة لليوم", f"{res['scheduled_liters']} لتر")
        
        if pumping_hours > (area * 12):
            st.warning("⚠️ تنبيه: المدة تتجاوز 12س/هكتار.")

        # --- 7-Day Forecast ---
        st.markdown("---")
        st.markdown("### 📅 توقعات الري للأسبوع القادم (Predictive Analytics)")
        
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
            
        chart_df = pd.DataFrame(forecast_chart_data).set_index("اليوم")
        c_h, c_l = st.tabs(["⏲️ الساعات المبرمجة", "💧 توزيع اللترات"])
        
        with c_h:
            st.area_chart(chart_df["ساعات الري"], color="#1E88E5")
            st.caption("تظهر الساعات فقط في الأيام التي نحتاج فيها لري عميق وكبير.")
            
        with c_l:
            st.bar_chart(chart_df[["الاحتياج العلمي اليومي (لتر)", "الري المبرمج (لتر)"]])
            st.caption("اللون الأزرق الداكن يمثل عطش النبات اليومي، واللون الفاتح يمثل متى سنقوم بالري فعلياً.")
            
        st.info(f"إجمالي مياه الأسبوع المتوقعة: {int(total_weekly_liters)} لتر.")
