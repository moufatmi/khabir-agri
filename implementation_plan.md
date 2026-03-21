# 🏆 Al-Khabir Agri - National Level Phase (V2)

## Goal Description
Transform the prototype into a comprehensive agricultural expert system by adding "Eyes" (AI Vision) and "Deep Vision" (NDVI Satellite Indices) to better compete at the national level.

## Proposed Changes

### [Component] AI Vision Service (Leaf Health)
- #### [NEW] [api_vision.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_vision.py)
  - Integration with Gemini Multi-modal API.
  - Specifically tuned prompt for Moroccan crops (Olives, Citrus, Almounds).
  - Ability to detect pests, nutrient deficiencies, and diseases from photos.

### [Component] UI Enhancements (Multi-Tab Expert View)
- #### [MODIFY] [app.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/app.py)
  - Introduce Tabs: (1) Smart Irrigation, (2) Health Check (AI Vision), (3) Field Insights (Advanced Maps).
  - Improve RTL layout for a more premium "Expert" feel.

### [Component] Advanced Satellite Metrics (NDVI)
- #### [MODIFY] [api_wapor.py](file:///c:/Users/Moussab/Desktop/RamadanIA/agri%20AI/services/api_wapor.py)
  - Add NDVI (Normalized Difference Vegetation Index) fetching to assess real plant vigor.
  - Correlate NDVI with Irrigation needs to prevent over-watering of stressed plants.

## Verification Plan

### Automated Tests
- Diagnostic script to test image upload and Gemini Vision analysis.
- Script to verify NDVI data fetching from Open-Meteo Satellite endpoints.

### Manual Verification
- Testing with sample photos of Olive Peacock Spot and Citrus Leaf Miner.
- Verifying the Map Polygon selection for more precise area calculations.
