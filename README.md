# 🌱 Al-Khabir Agro (الخبير الزراعي)
> **Precision Irrigation Advisor powered by Satellite Data & AI** 🛰️🧠

Al-Khabir Agro is a smart irrigation decision-support system designed for farmers in the **Oriental region of Morocco**. It leverages real-time European satellite data (**ECMWF/ERA5**) and the **FAO-56 Penman-Monteith** scientific framework to calculate exact water needs, promoting water sovereignty and agricultural efficiency.

## ✨ Key Features
- **🛰️ Satellite-Driven:** Real-time Soil Moisture and Evapotranspiration data via Open-Meteo.
- **🏗️ FAO-56 Standard:** Precise irrigation scheduling based on crop-specific (Kc) factors and growth stages.
- **🧠 AI Reasoning:** Integrated Gemini 1.5 Flash to translate technical data into actionable advice.
- **🔊 Voice Feedback:** High-speed Arabic voice output (Edge-TTS) for accessibility.
- **📅 Predictive Analytics:** 7-day irrigation outlook using advanced weather forecasts.
- **🗺️ Interactive Map:** Precision selection of farm coordinates via Morocco-centered Leaflet map.

## 🚀 Deployment Instructions
This application is built with **Streamlit**. While GitHub Pages is for static files, you can deploy this live using **Streamlit Community Cloud**:

1. **Upload to GitHub:** Push this entire directory to a new GitHub repository.
2. **Connect to Streamlit:** Sign in at [share.streamlit.io](https://share.streamlit.io).
3. **Deploy:** Select your repository and `app.py` as the main file.
4. **Secrets:** In Streamlit Cloud settings, add your API keys:
   - `GEMINI_API_KEY`
   - `WEATHER_API_KEY`

## 🛠️ Local Installation
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📜 Scientific Basis
The logic is based on the **Allowable Depletion** model, particularly optimized for **Tirs** (Heavy Clay) and **Raml** (Sandy) soils, ensuring deep root growth and maximum water savings.

---
*Created for the National Smart Agriculture Hackathon - Morocco 🇲🇦*
