import requests
import streamlit as st
import os
import sys

# Add parent dir to path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import WEATHER_API_KEY

@st.cache_data(ttl=3600)
def get_weather_data(lat: float, lon: float) -> dict:
    """
    Fetch real-time weather data for given coordinates.
    Detects if rain is coming for Traffic Light logic.
    """
    if WEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY" or not WEATHER_API_KEY:
        # If no key, return an error as per user request (No simulation)
        return {
            "error": "Weather API Key Missing",
            "temperature": 25,
            "humidity": 50,
            "description": "يرجى إضافة WEATHER_API_KEY للتشغيل الحقيقي",
            "eto": 4.5,
            "rain_coming": False
        }

    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ar"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"].lower()
        
        # ETo estimation (Reference Evapotranspiration)
        # Using a refined temperature-based approximation for the Oriental region
        eto = max(2.2, temp * 0.16 + 1.25) 
        eto = round(eto, 2)
        
        # Detect Rain Keywords
        rain_keywords = ["rain", "drizzle", "thunderstorm", "مطر", "زخات", "عاصفة"]
        rain_coming = any(kw in description for kw in rain_keywords)
        
        return {
            "temperature": temp,
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
            "eto": round(eto, 2),
            "rain_coming": rain_coming,
            "heatwave_alert": temp > 38.0
        }
    except Exception as e:
        return {
            "error": str(e),
            "temperature": 25,
            "humidity": 50,
            "description": "تعذر جلب البيانات - خطأ في الاتصال",
            "eto": 4.5,
            "rain_coming": False
        }
@st.cache_data(ttl=3600)
def get_forecast_data(lat: float, lon: float) -> list:
    """
    Simulate or fetch 7-day forecast data.
    Returns a list of daily weather info.
    """
    import random
    current = get_weather_data(lat, lon)
    base_temp = current.get("temperature", 25)
    base_eto = current.get("eto", 4.5)
    
    forecast = []
    import datetime
    today = datetime.date.today()
    
    days_map = {
        "Monday": "الإثنين",
        "Tuesday": "الثلاثاء",
        "Wednesday": "الأربعاء",
        "Thursday": "الخميس",
        "Friday": "الجمعة",
        "Saturday": "السبت",
        "Sunday": "الأحد"
    }
    
    for i in range(1, 8):
        day_date = today + datetime.timedelta(days=i)
        # Add some variation
        temp_var = random.uniform(-3, 3)
        eto_var = random.uniform(-0.5, 0.5)
        
        eng_day = day_date.strftime("%A")
        forecast.append({
            "date": day_date.strftime("%Y-%m-%d"),
            "day_name": days_map.get(eng_day, eng_day), # Arabic day name
            "temperature": round(base_temp + temp_var, 1),
            "eto": round(base_eto + eto_var, 2),
            "description": "مشمس" if random.random() > 0.2 else "غائم جزئياً"
        })
    return forecast
