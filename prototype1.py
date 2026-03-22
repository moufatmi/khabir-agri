import streamlit as st
import google.generativeai as genai
import requests

# 1. إعدادات الـ APIs (حط مفاتيحك هنا)
genai.configure(api_key="AIzaSyDXlsZ3xmat11cYvzocVQR9Da42QsH57Ww")
WEATHER_API_KEY = "c4377ce01ad081892081c897b12890d7"

# 2. منطق الحساب الفلاحي (FAO-56 & ORMVAM)
# المعادلة: ETc = Kc * ETo
CROP_FACTORS = {
    "ليمون (بركان)": 0.85,
    "زيتون": 0.70,
    "خضروات (الناظور)": 1.05
}

def get_weather(city):
    # كيجيب بيانات الطقس و WaPOR (تبسيطاً هنا نستخدم الطقس)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    res = requests.get(url).json()
    return res

# 3. واجهة المستخدم بـ Streamlit
st.title("🌱 Al-Khabir AI | الخبير الفلاحي")
st.subheader("مساعدك الذكي للسقي والتسويق بجهة الشرق")

# استقبال الصوت (Placeholder لخاصية الأوديو)
audio_file = st.file_uploader("سجل أوديو بالدارجة (واش نسقي اليوم؟ / بغيت نبيع...)", type=["wav", "mp3"])

if audio_file:
    st.audio(audio_file)
    with st.spinner('الخبير كيححلل البيانات...'):
        # هنا غادي ندمجو الـ System Prompt اللي فيه كاع القواعد اللي اتفقنا عليها
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # نرسل البيانات لـ Gemini مع سياق WaPOR و T@swiq
        prompt = f"""
        أنت 'الخبير الفلاحي'. المزارع في جهة الشرق أرسل لك رسالة صوتية.
        المعطيات التقنية الحالية (WaPOR & Weather): مدينة بركان، حرارة 28، رطوبة 40%.
        القواعد:
        1. استعمل معايير FAO-56 و ORMVAM لاتخاذ قرار السقي.
        2. إذا أراد البيع، استخرج البيانات لمنصة T@swiq.
        3. الجواب يكون بالدارجة المغربية (لهجة الشرق) وصوتي (نصي).
        """
        
        response = model.generate_content(prompt)
        st.success("✅ نصيحة الخبير:")
        st.write(response.text)

# 4. الربط مع T@swiq (Visual Reference)
st.sidebar.image("https://play-lh.googleusercontent.com/...") # رابط أيقونة T@swiq
st.sidebar.write("🔗 مرتبط بمنصة T@swiq للتسويق")   