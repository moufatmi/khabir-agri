import os

# 1. API Keys (Prioritize env vars for deployment security)
# For local use, you can set these in your terminal or a .env file
# For Streamlit Cloud, add these to the 'Secrets' section
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

# 2. Regional Settings & Coordinates for Mapping
REGIONS = {
    "بركان": [34.92, -2.32],
    "وجدة": [34.68, -1.91],
    "تاوريرت": [34.41, -2.89],
    "الناظور": [35.16, -2.93]
}

# 3. Crop Factors (Kc) for FAO-56 based on ORMVAM
CROP_FACTORS = {
    "ليمون": 0.85,
    "زيتون": 0.70,
    "لوز": 0.75,
    "نخيل": 0.90,
    "عنب": 0.75,
    "خضروات": 1.05,
    "حبوب": 1.15
}

# 4. Growth Stages (Multipliers for Kc based on FAO-56)
GROWTH_STAGES = {
    "بداية النمو (Initial)": 0.50,
    "مرحلة الإثمار/النمو الأقصى (Mid)": 1.00,
    "مرحلة النضج/الحصاد (End)": 0.70
}

# 5. Soil Types (Impacts water retention, currently qualitative context)
SOIL_TYPES = [
    "تيرس (Tirs - طينية ثقيلة)", 
    "حرش (Hriouch - حجرية)", 
    "رمل (Raml - رملية خفيفة)"
]

# 6. Soil Water Thresholds (Trigger irrigation when deficit > threshold mm)
# Based on FAO-56 Readily Available Water (RAW) for initial growth stages
SOIL_THRESHOLDS = {
    "تيرس (Tirs - طينية ثقيلة)": 12.0,  # mm
    "حرش (Hriouch - حجرية)": 6.0,      # mm
    "رمل (Raml - رملية خفيفة)": 8.0     # mm
}

# 7. Default Pump Settings
DEFAULT_PUMP_FLOW_RATE = 5000  # Liters per hour
