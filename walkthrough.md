# 🏛️ AL-KHABIR AGRI — COMPLETE TECHNICAL LORE (Source-Verified)

> **Written after a complete deep scan of all project files.**
> For any AI model picking up this project: read every section. This document is your ground truth.

---

## 📁 File Structure Map
```
agri AI/
├── app.py                  → Streamlit entry point, map UI, sidebar inputs
├── config.py               → All constants: API keys, Kc, Stages, Soils, Thresholds
├── prototype1.py           → Historical V0 prototype (kept for reference)
├── requirements.txt        → All 83 Python dependencies (pinned versions)
├── components/
│   └── ui_irrigation.py    → Core UI rendering (traffic light, chat, charts)
├── services/
│   ├── api_gemini.py       → Gemini AI integration + local fallback engine
│   ├── api_weather.py      → OpenWeatherMap + 7-day forecast simulator
│   ├── api_wapor.py        → Open-Meteo ERA5 satellite data pipeline
│   └── api_tts.py          → Text-to-Speech (edge-tts, Microsoft Neural)
└── utils/
    └── calculations.py     → Pure science: ETc, Liters, Hours, MAD cost
```

---

## 🔑 [config.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/config.py) — The Knowledge Base

### API Keys (Environment-first with fallback)
```python
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDZ77xzZ13g6UZYuX0SGknEBRsU2WTB91A")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "c4377ce01ad081892081c897b12890d7")
```
> **Security Note:** Keys are hardcoded for hackathon ease. In production, these MUST be environment variables only.

### Regional Coordinates (REGIONS dict)
Pre-seeded city coordinates for the Oriental region:
- بركان: `[34.92, -2.32]`
- وجدة: `[34.68, -1.91]`
- تاوريرت: `[34.41, -2.89]`
- الناظور: `[35.16, -2.93]`

### FAO-56 Crop Factors (`CROP_FACTORS` dict — Kc values)
| Crop | Kc |
|---|---|
| ليمون | 0.85 |
| زيتون | 0.70 |
| لوز | 0.75 |
| نخيل | 0.90 |
| عنب | 0.75 |
| خضروات | 1.05 |
| حبوب | 1.15 |

### Growth Stage Multipliers (`GROWTH_STAGES` dict)
| Stage (Arabic) | Multiplier |
|---|---|
| بداية النمو (Initial) | 0.50 |
| مرحلة الإثمار (Mid) | 1.00 |
| مرحلة النضج (End) | 0.70 |
> The effective `kc` is: `kc = CROP_FACTORS[crop] × GROWTH_STAGES[stage]`

### Soil Types & Irrigation Thresholds (MAD - Readily Available Water)
| Soil | Arabic Name | Threshold (mm) |
|---|---|---|
| Clay | تيرس (Tirs) | **12.0** — High retention, longest skip days |
| Rocky | حرش (Hriouch) | **6.0** — Medium retention |
| Sandy | رمل (Raml) | **8.0** — Noted: sand is paradoxically higher than Rocky. |

> **Note for next AI:** The Rmel (Sand) threshold of 8mm may seem counter-intuitive. Sand has LOW retention so it should be LOWER, not higher than clay. This may need revision in V2.

### Default Pump Flow Rate
`DEFAULT_PUMP_FLOW_RATE = 5000 L/hr`

---

## 🧬 [utils/calculations.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/utils/calculations.py) — The Pure Science Engine

### [calculate_etc(kc, eto) → float](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/utils/calculations.py#1-7)
```
ETc = Kc × ETo
```
Simple, direct FAO-56 crop evapotranspiration.

### [get_water_savings(etc, area_ha) → dict](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/utils/calculations.py#8-25)
```python
etc_liters_per_ha = etc × 10000        # 1mm over 1ha = 10,000 Liters
traditional_liters = etc_liters × 1.43 # Baseline: 30% over-watering assumed
saved_liters = (traditional - recommended) × area
recommended_liters = etc_liters × area
```
Returns: `{ recommended_liters, saved_liters, percent_saved: 30 }`

### [calculate_pumping_hours(liters, flow_rate) → float](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/utils/calculations.py#26-37)
```
Hours = Liters / Flow Rate (L/hr)
```
Returns rounded to 2 decimal places. Returns `0.0` if flow_rate ≤ 0.

### [get_economic_impact(saved_liters) → float](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/utils/calculations.py#38-46)
```
Saved MAD = (saved_liters / 1000) × 0.5 MAD/m³
```
Uses regional estimate of **0.5 MAD per cubic meter** for diesel/electric pumping cost.

---

## 🛰️ [services/api_wapor.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_wapor.py) — Satellite Data Pipeline

**Cache:** `@st.cache_data(ttl=86400)` — refreshes once per day.

### Strategy: Dual-Source with Fallback
1. **Primary: Open-Meteo Forecast API**
   - URL: `https://api.open-meteo.com/v1/forecast`
   - Parameters: `soil_moisture_0_to_7cm`, `et0_fao_evapotranspiration`
   - Coverage: Last 24h, near real-time
   - **Normalization:** `soil_moisture_percent = min(100, (raw_value / 0.4) × 100)`

2. **Fallback: ERA5-Land Archive API**
   - URL: `https://archive-api.open-meteo.com/v1/archive`
   - Fetches data from **7 days ago** to ensure processing is complete (ERA5 has ~5-7 day delay)
   - **Normalization:** `soil_moisture_percent = min(100, (raw_value / 0.45) × 100)` (Adjusted Field Capacity for ERA5)

### Output Dict
```python
{
  "actual_et": float,       # ETo in mm/day
  "soil_moisture": float,   # % (0-100)
  "biomass_index": float,   # soil_moisture / 100 (used as ETo corrector)
  "lat": float,
  "lon": float,
  "source": str             # "Open-Meteo Forecast (Live)" or "ERA5 Satellite (7-Day Avg)"
}
```

---

## 🌦️ [services/api_weather.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_weather.py) — Real-Time & Forecast

**Cache:** `@st.cache_data(ttl=3600)` — refreshes hourly.

### [get_weather_data(lat, lon) → dict](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_weather.py#10-62)
- Source: OpenWeatherMap `/data/2.5/weather`
- **ETo Estimation:** `eto = max(2.2, temp × 0.16 + 1.25)` — linear regression-style approximation.
- **Rain Detection:** Checks description for keywords: `rain, drizzle, thunderstorm, مطر, زخات, عاصفة`
- **Heatwave Alert:** Set to `True` if `temp > 38.0°C`

### [get_forecast_data(lat, lon) → list](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_weather.py#62-102)
> **SIMULATED**: This function uses `random.uniform()` to add ±3°C temperature variation and ±0.5 ETo variation around current weather.
> This is the **only simulation** in the entire project. All other data is live from APIs.

Returns 7-day list with: `date`, `day_name (Arabic)`, `temperature`, `eto`, `description`

---

## 🤖 [services/api_gemini.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_gemini.py) — AI Brain & Fallback Engine

### Model Configuration
```python
@st.cache_resource
def get_agricultural_model():
    # Primary model
    return genai.GenerativeModel('gemini-2.0-flash-lite', system_instruction=...)
    # Fallback model if primary fails at init
    return genai.GenerativeModel('gemini-flash-latest', ...)
```

### System Instruction (Persona)
The AI is given the persona of **"خبير الشرق الزراعي"** with:
- All crop Kc values hardcoded into the prompt
- Rule: "Tirs soil likes deep, spaced irrigation (Allowable Depletion)"
- Language: Modern Standard Arabic (فصحى مبسطة)

### [analyze_irrigation(...)](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_gemini.py#48-86) — Main Analysis Function
Takes: `user_prompt, weather, etc, pumping_hours, traffic_light, region, crop, soil, area, stream`

Context injected into Gemini prompt:
- Region, crop, stage, soil, area
- Weather: temp, humidity, description
- Traffic light status (translated to Arabic phrase)
- Pumping hours and pump rate

**Error Handling:**
- If `429` quota exceeded → calls [generate_local_advice()](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_gemini.py#87-97) and returns `LOCAL_FALLBACK:...`
- Other errors → returns error string

### [generate_local_advice(crop, traffic, hours, etc)](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_gemini.py#87-97) — The Guardian
Pure Python `if-else` fallback engine. Never fails. Produces 1-2 sentence expert advice:
- **Red** → Warns about root asphyxiation risk
- **Green** → Recommends [hours](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/utils/calculations.py#26-37) of pumping based on ETc
- **Yellow/Skip** → Explains Allowable Depletion logic and deep-rooting benefit

### [get_map_pro_tip(region, crop, moisture)](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_gemini.py#37-47) — Micro-advice
One sentence tip for map tooltips. Has its own silent try/except fallback.

---

## 🖥️ [components/ui_irrigation.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/components/ui_irrigation.py) — The Full UI Engine

### [get_traffic_light(weather, soil_moisture, soil_type) → tuple](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/components/ui_irrigation.py#16-34)
| Condition | Result |
|---|---|
| Rain detected in weather | 🔴 Red |
| `soil_moisture > 35%` (Tirs) / `> 20%` (Sand) / `> 40%` (Default) | 🟡 Yellow |
| Below threshold | 🟢 Green |
> Wind override (speed > 15 m/s) forces **🚩 Red** with "Sharqi Wind" message

### [render_irrigation_advisor(...)](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/components/ui_irrigation.py#35-251) — Main Rendering Function
**Input widgets:**
- `st.audio_input()` — Voice recording (UI only, not transcribed yet)
- `st.text_input()` — Text question

**Calculation pipeline (on button press):**
1. [get_weather_data(lat, lon)](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_weather.py#10-62) → weather dict
2. [get_wapor_data(lat, lon)](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_wapor.py#5-72) → satellite dict
3. `kc = CROP_FACTORS[crop] × GROWTH_STAGES[stage]`
4. `eto = weather.eto × wapor.biomass_index` ← **Key correction**
5. `etc = calculate_etc(kc, eto)`
6. [get_traffic_light(weather, soil_moisture, soil)](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/components/ui_irrigation.py#16-34) → color
7. **Skip Day Logic:** `if etc < (threshold × 0.4) AND soil_moisture > 25%` → pumping_hours = 0, force Yellow if Green
8. [get_water_savings(etc, area)](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/utils/calculations.py#8-25) → liters & savings
9. [calculate_pumping_hours(scheduled_liters, pump_rate)](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/utils/calculations.py#26-37) → hours
10. [get_economic_impact(saved_liters)](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/utils/calculations.py#38-46) → MAD savings
11. [analyze_irrigation(...)](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_gemini.py#48-86) → AI or fallback advice (streamed)

**Results stored in:** `st.session_state.irrigation_results` (dict)

**Rendered metrics:**
- Traffic light (H1 header)
- MAD savings badge (green card)
- Expert advice with voice playback button
- Proposed schedule (start 06:00 AM + pumping_hours)
- `daily_need_liters` vs `scheduled_liters` (Demand vs. Action)
- Sanity warning if `hours > area × 12`

### 7-Day Predictive Analytics
Built via [get_forecast_data()](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_weather.py#62-102) + cumulative deficit loop:
```
For each forecast day:
  accumulated_deficit += ETc(day)
  if accumulated_deficit >= SOIL_THRESHOLD:
    → Schedule irrigation! Reset deficit to 0.
  else:
    → Skip Day
```
Displayed as two tabs:
- `⏲️ الساعات المبرمجة` — Area chart
- `💧 توزيع اللترات` — Clustered bar chart (demand vs scheduled)

---

## 🔊 [services/api_tts.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_tts.py) — Voice Engine

- **Library:** `edge-tts` v7.2.7
- **Voice ID:** `ar-SA-HamedNeural` (Saudi Arabic Neural)
  - **Note for V2:** Consider switching to `ar-MA-MounaNeural` for Moroccan dialect
- Saves MP3 to [tmp/advice_voice.mp3](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/tmp/advice_voice.mp3)
- Uses `asyncio.run()` as sync wrapper for Streamlit compatibility

---

## 📦 [requirements.txt](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/requirements.txt) — Full Dependency Stack (Key Packages)

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | 1.54.0 | Web UI framework |
| `streamlit-folium` | 0.26.2 | Interactive map |
| `google-generativeai` | 0.8.6 | Gemini API (legacy SDK — FutureWarning: migrate to `google.genai`) |
| `edge-tts` | 7.2.7 | Arabic TTS |
| `folium` | 0.20.0 | Map rendering |
| `pydeck` | 0.9.1 | 3D deck.gl layers (imported but underused) |
| `pandas` | 2.3.3 | DataFrame for charts |
| `requests` | 2.32.5 | HTTP calls |
| `pillow` | 12.1.1 | Image handling (ready for Vision V2) |
| `openai` | 2.21.0 | **NOT USED** — Available if user wants OpenAI fallback |

> **IMPORTANT:** `google-generativeai` is deprecated. Migrate to `google.genai` (new SDK) in V2.

---

## 🕰️ [prototype1.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/prototype1.py) — The V0 Origin

This file is the historical starting point. Key insights:
- Had T@swiq marketing platform integration (sidebar)
- Used `gemini-1.5-flash` directly
- No FAO-56 integration, no satellite data
- Voice input was just file upload, no analysis
- **Keep this file for history. Do NOT delete.**

---

## ⚠️ Known Issues & Technical Debt

| Issue | Location | Impact | Fix for V2 |
|---|---|---|---|
| Deprecated Gemini SDK | [api_gemini.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_gemini.py) L4 | FutureWarning in logs | Migrate to `google.genai` |
| Voice not transcribed | [ui_irrigation.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/components/ui_irrigation.py) L40 | Audio recorded but ignored | Add Whisper/Gemini Audio API |
| Sand threshold may be wrong | [config.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/config.py) L44-45 | Rmel threshold (8mm) seems too high | Validate with soil science data |
| 7-day forecast is simulated | [api_weather.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_weather.py) L68-101 | Not real forecast data | Use Open-Meteo forecast API for real future ETo |
| TTS voice is Saudi, not Moroccan | [api_tts.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_tts.py) L10 | Accent mismatch | Switch to `ar-MA-MounaNeural` |

---

## 🚀 V2 NATIONAL LEVEL — Mission Briefing

**Priority 1: Fix Gemini SDK Deprecation**
```python
# OLD (deprecated)
import google.generativeai as genai
# NEW
from google import genai
client = genai.Client(api_key=KEY)
```

**Priority 2: AI Vision Tab**
```python
# In services/api_vision.py
img_bytes = st.file_uploader("صور ورقة المحصول", type=["jpg","png"])
response = model.generate_content([
    "أنت مهندس مختبر النبات. حلل هذه الورقة وأعطِ: [الآفة، الخطورة، العلاج]",
    PIL.Image.open(img_bytes)
])
```

**Priority 3: NDVI from Sentinel-2**
- Endpoint: `https://api.open-meteo.com/v1/forecast?hourly=ndvi` (check availability)
- NDVI < 0.2 = Stressed/Bare Soil → Force Red regardless of moisture

**Priority 4: Moroccan Voice**
```python
voice = "ar-MA-MounaNeural"  # Change in api_tts.py line 10
```

---

**Signed: AGENT ANTIGRAVITY**
*Regional Champion. National Mission Active.* 🏆🇲🇦🌾
