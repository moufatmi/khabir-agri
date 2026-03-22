"""
Competition / impact pitch — presentation-only UI for judges and demos.
"""
import streamlit as st


def render_competition_pitch():
    """Short RTL-friendly section explaining value for Moroccan citizens."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #161B22 0%, #0d2818 100%);
         border: 1px solid #30363D; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;">
        <h2 style="margin:0 0 0.5rem 0; color: #58A6FF; font-size: 1.25rem;">
            🇲🇦 حل ذكي عملي للمواطن المغربي
        </h2>
        <p style="color: #C9D1D9; line-height: 1.75; margin: 0; font-size: 0.95rem;">
            <strong>المشكلة:</strong> قرار الري غالباً يعتمد على الحدس — فيضيع الماء والطاقة وقد يضرّ بالجذور.<br>
            <strong>الحل:</strong> قرار يومي مبني على طقس حقيقي + تربة (Open-Meteo / ERA5) + معيار FAO-56،
            مع نصيحة ذكية (Gemini) ومحرك احتياطي إذا انقطع الذكاء الاصطناعي.<br>
            <strong>الأثر:</strong> توفير ماء وتكلفة ضخ أوضح للفلاح، وخطوة نحو الزراعة الدقيقة في المغرب.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**1️⃣ حدد الموقع** على الخريطة.")
    with c2:
        st.markdown("**2️⃣ اختر المحصول والتربة** من الشريط الجانبي.")
    with c3:
        st.markdown("**3️⃣ اضغط التحليل** — احصل على ضوء المرور + الساعات + النصيحة.")

    with st.expander("ما الذي يحدث تقنياً تحت الغطاء؟", expanded=False):
        st.markdown("""
        - **OpenWeatherMap**: حرارة، رياح، وصف الطقس (كشف المطر).
        - **Open-Meteo**: رطوبة تربة سطحية + ET₀ FAO؛ مع **أرشيف ERA5** إذا تعذر التوقع اللحظي.
        - **توقعات 7 أيام**: ET₀ يومي من Open-Meteo (ليس عشوائياً عند نجاح الشبكة).
        - **Gemini**: صياغة النصيحة؛ عند الحصص/الخطأ → **نصيحة محلية** من `generate_local_advice`.
        """)
