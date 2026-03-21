def calculate_etc(kc: float, eto: float) -> float:
    """
    Calculate Crop Evapotranspiration (ETc) using FAO-56.
    ETc = Kc * ETo
    """
    return kc * eto

def get_water_savings(etc_mm: float, area_ha: float = 1.0) -> dict:
    """
    Calculate required water volume in Liters based on ETc (mm) and area (ha).
    Includes a wetted area factor (0.6) to represent drip irrigation efficiency.
    """
    # 1 mm over 1 ha = 10,000 Liters.
    # Wetted area factor (0.6) represents that we only water the root zone.
    wetted_area_factor = 0.6
    recommended_liters = etc_mm * 10000 * area_ha * wetted_area_factor
    
    # Traditional flooding uses ~2x more water due to evaporation/runoff.
    traditional_liters = recommended_liters * 2.0 
    saved_liters = traditional_liters - recommended_liters
    
    return {
        "recommended_liters": int(recommended_liters),
        "saved_liters": int(saved_liters),
        "percent_saved": 50
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
