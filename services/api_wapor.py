from __future__ import annotations

import requests
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Tuple


def _ndvi_from_soil_proxy(sm_percent: float) -> float:
    """
    Deterministic NDVI-like index (0.15–0.85) from volumetric soil moisture %.
    Used when satellite NDVI endpoint is unavailable — not random.
    """
    x = max(0.0, min(100.0, sm_percent)) / 100.0
    return round(min(0.85, max(0.15, 0.15 + 0.70 * x)), 2)


def _fetch_ndvi_satellite(lat: float, lon: float, archive_date: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Try Open-Meteo Satellite API for last valid hourly NDVI on a given day.
    Returns (ndvi_float_or_none, source_str_or_none).
    """
    url = "https://satellite-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": archive_date,
        "end_date": archive_date,
        "hourly": "ndvi",
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code != 200:
            return None, None
        data = res.json()
        hourly = data.get("hourly") or {}
        series = hourly.get("ndvi") or []
        for val in reversed(series):
            if val is not None:
                return round(float(val), 2), "Sentinel-2 NDVI (Open-Meteo)"
    except Exception:
        pass
    return None, None


def _build_payload(
    lat: float,
    lon: float,
    sm_percent: float,
    et_val: float,
    source_label: str,
    archive_date_for_ndvi: Optional[str] = None,
) -> dict:
    ndvi_sat, ndvi_src = (None, None)
    if archive_date_for_ndvi:
        ndvi_sat, ndvi_src = _fetch_ndvi_satellite(lat, lon, archive_date_for_ndvi)

    if ndvi_sat is not None:
        ndvi_val = ndvi_sat
        ndvi_note = ndvi_src
    else:
        ndvi_val = _ndvi_from_soil_proxy(sm_percent)
        ndvi_note = "تقدير من رطوبة التربة (بدون عشوائية)"

    # Biomass correction: moisture × (NDVI-driven transpiration hint)
    biomass_corr = (sm_percent / 100.0) * min(1.15, ndvi_val + 0.25)
    return {
        "actual_et": round(et_val if et_val else 4.5, 2),
        "soil_moisture": round(sm_percent, 1),
        "ndvi": ndvi_val,
        "ndvi_note": ndvi_note,
        "biomass_index": round(min(1.2, biomass_corr), 2),
        "lat": lat,
        "lon": lon,
        "source": source_label,
    }


@st.cache_data(ttl=86400)  # Daily cache for satellite data
def get_wapor_data(lat: float, lon: float) -> dict:
    """
    Fetch soil moisture + ET₀ from Open-Meteo (forecast), else ERA5-Land archive.
    NDVI: real Sentinel-2 via Open-Meteo Satellite API when possible; else soil proxy.
    """
    url_forecast = "https://api.open-meteo.com/v1/forecast"
    params_forecast = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["soil_moisture_0_to_7cm", "et0_fao_evapotranspiration"],
        "timezone": "auto",
        "forecast_days": 1,
    }

    archive_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    try:
        res = requests.get(url_forecast, params=params_forecast, timeout=10)
        if res.status_code == 200:
            data = res.json()
            hourly = data.get("hourly", {})
            sm_val = next(
                (x for x in reversed(hourly.get("soil_moisture_0_to_7cm", [])) if x is not None),
                None,
            )
            et_val = next(
                (x for x in reversed(hourly.get("et0_fao_evapotranspiration", [])) if x is not None),
                None,
            )

            if sm_val is not None:
                sm_percent = min(100.0, (sm_val / 0.4) * 100.0)
                return _build_payload(
                    lat,
                    lon,
                    sm_percent,
                    et_val,
                    "Open-Meteo Forecast (حي)",
                    archive_date_for_ndvi=archive_date,
                )

        # Fallback: ERA5-Land Archive (~7 day processing lag)
        url_archive = "https://archive-api.open-meteo.com/v1/archive"
        params_archive = {
            "latitude": lat,
            "longitude": lon,
            "start_date": archive_date,
            "end_date": archive_date,
            "hourly": ["soil_moisture_0_to_7cm", "et0_fao_evapotranspiration"],
        }

        res_arch = requests.get(url_archive, params=params_archive, timeout=10)
        if res_arch.status_code == 200:
            data_arch = res_arch.json()
            hourly_arch = data_arch.get("hourly", {})
            sm_arch = next(
                (x for x in reversed(hourly_arch.get("soil_moisture_0_to_7cm", [])) if x is not None),
                None,
            )
            et_arch = next(
                (x for x in reversed(hourly_arch.get("et0_fao_evapotranspiration", [])) if x is not None),
                None,
            )

            if sm_arch is not None:
                sm_percent = min(100.0, (sm_arch / 0.45) * 100.0)
                return _build_payload(
                    lat,
                    lon,
                    sm_percent,
                    et_arch,
                    "ERA5-Land (أرشيف ~7 أيام)",
                    archive_date_for_ndvi=archive_date,
                )

        return {
            "error": "لا توجد بيانات أقمار صناعية لهذا الموقع حالياً. يرجى تجربة منطقة زراعية معروفة."
        }

    except Exception as e:
        return {"error": f"تعذر الاتصال بمصدر البيانات الحقيقي (Error: {str(e)})"}
