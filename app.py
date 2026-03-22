import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Al-Khabir Agri | الخبير الزراعي",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Optional: Add custom CSS for Premium Dark UI matching the requested design
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
        background-color: #0E1117;
        color: #FFFFFF;
        font-family: 'Cairo', sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-left: 1px solid #30363D;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        color: #8B949E;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        color: #58A6FF !important;
        border-bottom-color: #58A6FF !important;
    }

    /* Custom Card Design */
    .metric-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-label {
        color: #8B949E;
        font-size: 0.9rem;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #58A6FF;
        font-size: 1.8rem;
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #238636;
        color: white;
        border: none;
        padding: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #2EA043;
        border: none;
    }

    /* Info/Success/Warning boxes */
    .stAlert {
        background-color: #161B22;
        border: 1px solid #30363D;
        color: #C9D1D9;
    }
</style>
""", unsafe_allow_html=True)

from components.ui_irrigation import render_irrigation_advisor
from components.ui_vision import render_vision_dashboard
from components.ui_pitch import render_competition_pitch
from config import CROP_FACTORS, GROWTH_STAGES, SOIL_TYPES, DEFAULT_PUMP_FLOW_RATE
import folium
from streamlit_folium import st_folium

def main():
    st.sidebar.title("⚙️ إعدادات المزرعة")
    st.sidebar.subheader("الخبير الزراعي - الري الذكي")
    
    st.sidebar.markdown("---")
    
    # Selection of Crop and Soil remains in sidebar
    selected_crop = st.sidebar.selectbox("🌱 المحصول:", list(CROP_FACTORS.keys()))
    selected_stage = st.sidebar.selectbox("📅 مرحلة النمو:", list(GROWTH_STAGES.keys()))
    selected_soil = st.sidebar.selectbox("🏺 نوع التربة:", SOIL_TYPES)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**معطيات تقنية:**")
    
    area_ha = st.sidebar.number_input(
        "📏 مساحة الري (هكتار):", 
        min_value=0.1, max_value=100.0, value=1.0, step=0.1
    )
    
    pump_rate = st.sidebar.number_input(
        "💦 قدرة المضخة (لتر/ساعة):", 
        min_value=100, max_value=100000, value=DEFAULT_PUMP_FLOW_RATE, step=100
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 **نصيحة للمسابقة الوطنية:**\n\n"
        "الآن التطبيق يحتوي على محركين: الري الذكي، وفحص الأمراض."
    )

    # --- National Level Tabs ---
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div style="font-size: 2rem;">📡</div>
        <div style="text-align: center;">
            <h1 style="color: #FFFFFF; margin: 0; font-size: 1.8rem;">الخبير الزراعي 🌳💧</h1>
            <p style="color: #8B949E; margin: 0; font-size: 0.8rem;">AL-KHABIR AGRI V2</p>
        </div>
        <div style="font-size: 2rem;">🛰️</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab_pitch, tab_irrigation, tab_vision = st.tabs(
        ["🇲🇦 العرض والأثر", "💧 مستشار الري الذكي", "📸 عين الخبير (التشخيص)"]
    )

    with tab_pitch:
        render_competition_pitch()
    
    # === TAB 1: SMART IRRIGATION ===
    with tab_irrigation:
        st.info(
            "💡 **تحديد الموقع:** "
            "الرجاء الضغط على موقع ضيعتك في الخريطة لبدء التحليل الحقيقي للاحتياج المائي."
        )
        
        # Map centered on Oriental Morocco (Berkan / Oujda region)
        m = folium.Map(location=[34.25, -2.35], zoom_start=8, tiles="OpenStreetMap")
        
        # If we have a clicked point in session state, add a marker
        if "clicked_coords" in st.session_state:
            folium.Marker(st.session_state.clicked_coords).add_to(m)

        output = st_folium(m, width="100%", height=400, key="map")
        
        # Capture click
        if output and output.get("last_clicked"):
            lat = output["last_clicked"]["lat"]
            lon = output["last_clicked"]["lng"]
            st.session_state.clicked_coords = [lat, lon]
            st.rerun()

        # Render Advisor if location selected
        if "clicked_coords" in st.session_state:
            lat, lon = st.session_state.clicked_coords
            st.markdown("---")
            render_irrigation_advisor(lat, lon, selected_crop, selected_stage, selected_soil, area_ha, pump_rate)
        else:
            st.warning("⚠️ يرجى الضغط على الخريطة لتحديد موقع الضيعة.")

    # === TAB 2: AI VISION ===
    with tab_vision:
        render_vision_dashboard(selected_crop)

if __name__ == "__main__":
    main()
