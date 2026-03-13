import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Al-Khabir Agro | الخبير الزراعي",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Optional: Add custom CSS for larger font UI and Traffic Light
st.markdown("""
<style>
    /* Global RTL Support for Arabic */
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }
    
    /* Make text bigger for farmers */
    .stMarkdown, .stText, p, span {
        font-size: 1.1rem !important;
        direction: rtl;
        text-align: right;
    }
    .stButton>button {
        font-size: 1.3rem !important;
        font-weight: bold;
        border-radius: 8px;
    }
    
    /* Improve Sidebar look */
    [data-testid="stSidebar"] {
        background-color: #f7f9f3;
        direction: rtl;
    }
</style>
""", unsafe_allow_html=True)

from components.ui_irrigation import render_irrigation_advisor
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
        "💡 **تحديد الموقع:**\n\n"
        "الرجاء الضغط على موقع ضيعتك في الخريطة لبدء التحليل الحقيقي."
    )

    # Main Area: Interactive Map Selection
    st.header("📍 حدد موقع ضيعتك بدقة")
    st.write("اضغط على الخريطة لتحديد موقع الضيعة وجلب بيانات WaPOR الحقيقية:")
    
    # Initialize Map centered on Morocco
    m = folium.Map(location=[32.0, -6.0], zoom_start=6)
    
    # If we have a clicked point in session state, add a marker
    if "clicked_coords" in st.session_state:
        folium.Marker(st.session_state.clicked_coords).add_to(m)

    output = st_folium(m, width=900, height=500)
    
    # Capture click
    if output.get("last_clicked"):
        lat = output["last_clicked"]["lat"]
        lon = output["last_clicked"]["lng"]
        st.session_state.clicked_coords = [lat, lon]
        st.rerun()

    # Render Advisor if location selected
    if "clicked_coords" in st.session_state:
        lat, lon = st.session_state.clicked_coords
        render_irrigation_advisor(lat, lon, selected_crop, selected_stage, selected_soil, area_ha, pump_rate)
    else:
        st.warning("⚠️ يرجى الضغط على الخريطة لتحديد موقع الضيعة.")

if __name__ == "__main__":
    main()
