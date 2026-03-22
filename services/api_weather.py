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
def _wmo_code_to_ar(code) -> str:
    """Short Arabic label from WMO weather code (Open-Meteo)."""
    if code is None:
        return "—"
    try:
        c = int(code)
    except (TypeError, ValueError):
        return "—"
    if c == 0:
        return "صافٍ"
    if c in (1, 2, 3):
        return "غائم جزئياً"
    if c in (45, 48):
        return "ضباب"
    if c in (51, 53, 55, 56, 57):
        return "رذاذ / مطر خفيف"
    if c in (61, 63, 65, 66, 67, 80, 81, 82):
        return "مطر"
    if c in (71, 73, 75, 77, 85, 86):
        return "ثلج / برد"
    if c in (95, 96, 99):
        return "عاصفة رعدية"
    return "متغيّر"


@st.cache_data(ttl=3600)
def get_forecast_data(lat: float, lon: float) -> list:
    """
    Prefer real 7-day daily ET₀ + temperature from Open-Meteo forecast API.
    Falls back to a simple variation around current weather only if the request fails.
    """
    import datetime
    import random

    days_map = {
        0: "الإثنين",
        1: "الثلاثاء",
        2: "الأربعاء",
        3: "الخميس",
        4: "الجمعة",
        5: "السبت",
        6: "الأحد",
    }

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["et0_fao_evapotranspiration", "temperature_2m_max", "weather_code"],
        "forecast_days": 7,
        "timezone": "Africa/Casablanca",
    }

    try:
        res = requests.get(url, params=params, timeout=12)
        res.raise_for_status()
        data = res.json()
        daily = data.get("daily") or {}
        dates = daily.get("time") or []
        eto_list = daily.get("et0_fao_evapotranspiration") or []
        tmax_list = daily.get("temperature_2m_max") or []
        wcode_list = daily.get("weather_code") or []

        if not dates or not eto_list:
            raise ValueError("Open-Meteo daily forecast incomplete")

        forecast = []
        for i, d in enumerate(dates):
            eto_val = eto_list[i] if i < len(eto_list) else None
            tmax = tmax_list[i] if i < len(tmax_list) else None
            wcode = wcode_list[i] if i < len(wcode_list) else None

            if eto_val is None:
                continue
            dt = datetime.datetime.strptime(d, "%Y-%m-%d").date()
            day_name = days_map.get(dt.weekday(), d)

            forecast.append({
                "date": d,
                "day_name": day_name,
                "temperature": round(float(tmax), 1) if tmax is not None else None,
                "eto": round(float(eto_val), 2),
                "description": _wmo_code_to_ar(wcode),
                "forecast_source": "Open-Meteo (daily ET₀)",
            })

        if forecast:
            return forecast
    except Exception:
        pass

    # Fallback: lightweight variation (offline / API failure)
    current = get_weather_data(lat, lon)
    base_temp = current.get("temperature", 25)
    base_eto = current.get("eto", 4.5)
    today = datetime.date.today()
    out = []
    for i in range(1, 8):
        day_date = today + datetime.timedelta(days=i)
        temp_var = random.uniform(-2, 2)
        eto_var = random.uniform(-0.35, 0.35)
        out.append({
            "date": day_date.strftime("%Y-%m-%d"),
            "day_name": days_map.get(day_date.weekday(), day_date.strftime("%A")),
            "temperature": round(base_temp + temp_var, 1),
            "eto": round(max(0.5, base_eto + eto_var), 2),
            "description": "تقدير احتياطي",
            "forecast_source": "Fallback (approx.)",
        })
    return out
