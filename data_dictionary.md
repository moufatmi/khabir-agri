| Variable | Description | Source | Unit |
| :--- | :--- | :--- | :--- |
| `latitude` | Coordinate of the farm location | User Input / Map | Decimal Degrees |
| `longitude` | Coordinate of the farm location | User Input / Map | Decimal Degrees |
| `temp_avg` | Average daily air temperature | OpenWeather API | °C |
| `wind_speed` | Wind speed at 10m height (Critical for evaporation) | OpenWeather API | m/s |
| `eto` | Reference Evapotranspiration (Standard grass) | Open-Meteo (FAO-56) | mm/day |
| `soil_moisture` | Volumetric soil water content (0-7cm depth) | Open-Meteo (Satellite) | % |
| `crop_type` | Type of crop (e.g., Citrus, Olive, Almond) | User Selection | Category |
| `growth_stage` | Lifecycle phase (Initial, Mid, End) | User Selection | Category |
| `kc_factor` | Crop coefficient based on FAO-56 standards | Config Calculation | Coefficient |
| `etc_calculated` | Actual Crop Water Need (ETc = ETo * Kc) | System Calculation | mm/day |
| `water_needed_liters`| Total volume required based on farm area | System Calculation | Liters |
| `pumping_hours` | Duration required to deliver water volume | System Calculation | Hours |
| `irrigation_trigger` | Decision flag (0: Skip, 1: Irrigate) | AI Logic (Allowable Depletion) | Boolean |
