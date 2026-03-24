from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from services.api_weather import get_weather_data
from services.api_wapor import get_wapor_data
from services.api_gemini import analyze_irrigation
from utils.calculations import calculate_etc, calculate_pumping_hours
from config import CROP_FACTORS, GROWTH_STAGES

app = FastAPI(title="Al-Khabir Agri API Bridge")

# Allow Lovable/Blackbox to talk to this backend
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
