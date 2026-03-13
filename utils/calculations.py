def calculate_etc(kc: float, eto: float) -> float:
    """
    Calculate Crop Evapotranspiration (ETc) using FAO-56.
    ETc = Kc * ETo
    """
    return kc * eto

def get_water_savings(etc: float, area_ha: float = 1.0) -> dict:
    """
    Calculate potential water savings (target 30%).
    Returns recommended volume and saved volume in Liters for the given area.
    """
    # 1 mm of water over 1 Hectare = 10,000 Liters
    etc_liters_per_ha = etc * 10000 
    traditional_liters_per_ha = etc_liters_per_ha * 1.43 # assumed 30% excessive watering

    saved_liters = (traditional_liters_per_ha - etc_liters_per_ha) * area_ha
    recommended_liters = etc_liters_per_ha * area_ha
    
    return {
        "recommended_liters": int(recommended_liters),
        "saved_liters": int(saved_liters),
        "percent_saved": 30
    }

def calculate_pumping_hours(recommended_liters: float, pump_flow_rate: float) -> float:
    """
    Calculate required pumping duration in hours.
    Duration = Total Water Needed / Pump Flow Rate
    Returns rounded hours (2 decimal places).
    """
    if pump_flow_rate <= 0:
        return 0.0
    # Sanity: (Liters / FlowRate)
    hours = recommended_liters / pump_flow_rate
    return round(hours, 2)

def get_economic_impact(saved_liters: float) -> float:
    """
    Estimate the financial savings in MAD (Moroccan Dirhams).
    Assumption: Average cost of 0.5 MAD per m3 (1000L) for diesel/electric pumping.
    """
    saved_m3 = saved_liters / 1000
    cost_per_m3 = 0.5 # Estimated regional pumping cost
    return round(saved_m3 * cost_per_m3, 2)
