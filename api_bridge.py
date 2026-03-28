from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from services.api_weather import get_weather_data
from services.api_wapor import get_wapor_data
from services.api_gemini import analyze_irrigation
from utils.calculations import calculate_etc, calculate_pumping_hours
from config import CROP_FACTORS, GROWTH_STAGES
import os

app = FastAPI(title="Al-Khabir Agri Hub")

# Serving the Frontend directly
@app.get("/")
async def read_index():
    return FileResponse('front end.html')

# Allow origins for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/advisor/irrigation")
def get_irrigation_advice(lat: float, lon: float, crop: str, stage: str, soil: str, area: float, pump_rate: float):
    weather = get_weather_data(lat, lon)
    wapor = get_wapor_data(lat, lon)
    
    # Logic mirror from ui_irrigation.py
    kc = CROP_FACTORS.get(crop, 0.7) * GROWTH_STAGES.get(stage, 1.0)
    eto = weather.get('eto', 4.5) * wapor.get('biomass_index', 1.0)
    etc = calculate_etc(kc, eto)
    
    # Placeholder for traffic light logic
    traffic = "Green" if wapor.get("soil_moisture", 30) < 30 else "Yellow"
    hours = calculate_pumping_hours(etc * 10000 * area, pump_rate)

    return {
        "weather": weather,
        "wapor": wapor,
        "etc": etc,
        "hours": hours,
        "traffic_light": traffic
    }

from services.api_vision import analyze_crop_image

@app.post("/advisor/vision")
async def analyze_plant(crop: str, file: UploadFile = File(...)):
    """
    Endpoint for AI Vision Diagnostics.
    Expects a crop name and an image file.
    """
    image_bytes = await file.read()
    
    # We call our existing vision service
    # Note: analyze_crop_image returns a stream or string based on success/fallback
    result = analyze_crop_image(image_bytes, crop)
    
    # Handle stream or string
    text = ""
    if hasattr(result, 'text'):
        text = result.text
    else:
        # If it's the stream generator or a fallback string
        for chunk in result:
             if hasattr(chunk, 'text'):
                 text += chunk.text
             else:
                 text += str(chunk)

    return {
        "crop": crop,
        "analysis": text,
        "status": "success"
    }

from services.api_gemini import model

@app.get("/advisor/chat")
async def chat_with_advisor(message: str):
    """
    General purpose chat endpoint with fallback for quota errors.
    """
    try:
        response = model.generate_content(message)
        return {"response": response.text, "status": "success"}
    except Exception as e:
        # Professional fallback message
        fallback = "مرحباً! يبدو أنني مشغول قليلاً في تحليل بعض البيانات الضخمة. كقاعدة عامة في هذا الموسم بالمغرب، تأكد من مراقبة رطوبة التربة في الصباح الباكر وتجنب السقي وقت الظهيرة."
        return {"response": fallback, "status": "success", "warning": "quota_limit"}

@app.get("/advisor/agri-weather")
async def agri_weather_risk(lat: float, lon: float, crop: str):
    """
    Get weather and provide risk analysis with safety fallback.
    """
    try:
        from services.api_weather import get_weather_forecast
        weather = get_weather_forecast(lat, lon)
        prompt = f"حلل حالة الطقس الحالية لمحصول {crop} في المغرب: {weather['temperature']}°C، {weather['humidity']}% رطوبة. هل هناك مخاطر؟ أجب باختصار (جملة واحدة)."
        try:
            response = model.generate_content(prompt)
            risk = response.text
        except:
            risk = "الجو مستقر عموماً، لكن احذر من تقلبات الرطوبة الليلية التي قد تشجع الفطريات."
        return {"risk_analysis": risk, "weather": weather}
    except Exception as e:
        return {"risk_analysis": "تعذر جلب بيانات الطقس، تأكد من الاتصال.", "weather": {"temperature": "--", "humidity": "--"}}

@app.get("/advisor/fertilizer")
async def get_fertilizer_plan(crop: str, stage: str):
    """
    Fertilization plan with hardcoded expert fallback.
    """
    expert_tips = {
        "tomato": "يفضل إضافة مادة البوتاسيوم في مرحلة الإثمار لتحسين جودة الثمار.",
        "olive": "ركز على التربية والتسميد الأزوتي في هذه المرحلة لدعم النمو الخضري.",
        "citrus": "تأكد من توازن الكالسيوم والمغنيسيوم لتفادي تساقط الثمار الصغير."
    }
    fallback = expert_tips.get(crop.lower(), "ننصح دائماً باستشارة خبير تربة محلي لتحديد كميات NPK الدقيقة.")
    
    try:
        prompt = f"نصيحة تسميد لمزارع {crop} في مرحلة {stage} باختصار."
        response = model.generate_content(prompt)
        return {"plan": response.text}
    except:
        return {"plan": fallback}

@app.get("/advisor/market")
async def get_market_prices(crop: str):
    """
    Simulated market prices for Moroccan regions.
    """
    import random
    prices = {
        "tomato": {"Souss": "4.50", "Gharb": "5.00", "Berkane": "4.80"},
        "pepper": {"Souss": "6.00", "Gharb": "6.50", "Meknes": "6.20"},
        "olive": {"Haouz": "80.00", "Tadla": "85.00", "Oriental": "82.00"},
        "citrus": {"Souss": "3.50", "Berkane": "4.00", "Gharb": "3.80"}
    }
    crop_prices = prices.get(crop.lower(), {"الوطني": f"{random.uniform(4, 9):.2f}"})
    return {"prices": crop_prices, "currency": "MAD/KG"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
