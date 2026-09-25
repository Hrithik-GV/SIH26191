"""Hazard-layer combination and multi-hazard spatial synthesis.

Combines disparate spatial hazard red-zone layers (Flood, Landslide, Rainfall/Cloudburst)
into a unified multi-hazard risk layer, computing compound risk intensity in co-located hazard areas.
"""

from typing import Dict, List, Optional, Any, Union
import pandas as pd
import geopandas as gpd
from shapely.ops import unary_union
import shapely

from backend.app.gis.crs import (
    validate_crs,
    ensure_compatible_crs,
    to_metric_crs,
    DEFAULT_GEOGRAPHIC_CRS,
)
from backend.app.gis.geometry_utils import validate_and_clean_geometries
from backend.app.gis.intersection import spatial_intersection


DEFAULT_HAZARD_WEIGHTS = {
    "FLOOD": 0.35,
    "LANDSLIDE": 0.35,
    "RAINFALL": 0.30,
}

SEVERITY_SCORE_MAP = {
    "LOW": 25.0,
    "MODERATE": 50.0,
    "MEDIUM": 50.0,
    "HIGH": 75.0,
    "VERY_HIGH": 100.0,
    "CRITICAL": 100.0,
}


def score_to_severity(score: float) -> str:
    """Map a 0-100 composite risk score to standard severity tier."""
    if score >= 81.0:
        return "CRITICAL"
    elif score >= 61.0:
        return "HIGH"
    elif score >= 31.0:
        return "MODERATE"
    return "LOW"


def combine_hazard_layers(
    hazard_layers: Dict[str, gpd.GeoDataFrame],
    weights: Optional[Dict[str, float]] = None,
    target_crs: Optional[str] = None,
) -> gpd.GeoDataFrame:
    """Synthesize multiple hazard layers into a unified multi-hazard GeoDataFrame.
    
    Supports:
    - FLOOD: Inundation zones, river overflow contours.
    - LANDSLIDE: Slope instability zones, debris flow corridors.
    - RAINFALL: Cloudburst high-intensity catchment buffers.
    - GENERAL MULTI-HAZARD: Coincident hazard intersection zones.
    
    Args:
        hazard_layers: Mapping of hazard name to GeoDataFrame, e.g.
                       {'flood': flood_gdf, 'landslide': ls_gdf, 'rainfall': rain_gdf}
        weights: Optional importance weights per hazard type (normalized to 1.0).
        target_crs: Target coordinate system for output layer (default: CRS of first layer or EPSG:4326).
        
    Returns:
        Unified GeoDataFrame containing individual and intersecting multi-hazard zones with:
        - 'hazard_type': 'MULTI_HAZARD' for overlapping zones, or original hazard type.
        - 'active_hazards': List or comma-separated string of co-located hazards.
        - 'composite_risk_score': 0-100 weighted compound risk score.
        - 'severity': 'LOW', 'MODERATE', 'HIGH', or 'CRITICAL'.
        - 'is_multi_hazard': Boolean flag indicating coincident hazards.
    """
    # Filter empty layers
    active_layers = {
        k.upper(): v for k, v in hazard_layers.items()
        if v is not None and not v.empty
    }
    
    if not active_layers:
        return gpd.GeoDataFrame(
            columns=[
                "geometry", "hazard_type", "active_hazards",
                "composite_risk_score", "severity", "is_multi_hazard"
            ],
            crs=target_crs or DEFAULT_GEOGRAPHIC_CRS
        )
        
    # Determine reference CRS
    ref_crs = target_crs or next(iter(active_layers.values())).crs or DEFAULT_GEOGRAPHIC_CRS
    
    # Standardize weights
    w_dict = (weights or DEFAULT_HAZARD_WEIGHTS).copy()
    w_clean = {k.upper(): float(v) for k, v in w_dict.items()}
    total_w = sum(w_clean.get(k, 1.0) for k in active_layers.keys())
    norm_weights = {k: (w_clean.get(k, 1.0) / total_w) if total_w > 0 else 1.0 for k in active_layers.keys()}
    
    # Clean and reproject all layers to common CRS
    processed_layers: Dict[str, gpd.GeoDataFrame] = {}
    for h_type, layer in active_layers.items():
        clean_layer = validate_and_clean_geometries(layer, layer_name=f"Hazard Layer {h_type}")
        if clean_layer.crs is None:
            clean_layer = clean_layer.set_crs(DEFAULT_GEOGRAPHIC_CRS)
        if clean_layer.crs != ref_crs:
            clean_layer = clean_layer.to_crs(ref_crs)
            
        # Ensure severity and base score columns exist
        if "severity" not in clean_layer.columns:
            clean_layer["severity"] = "HIGH"
            
        clean_layer["base_score"] = clean_layer["severity"].astype(str).str.upper().map(
            lambda s: SEVERITY_SCORE_MAP.get(s, 50.0)
        )
        clean_layer["hazard_name"] = h_type
        processed_layers[h_type] = clean_layer
        
    # If only one hazard type provided, return standardized version directly
    if len(processed_layers) == 1:
        h_name, single_layer = next(iter(processed_layers.items()))
        res = single_layer.copy()
        res["hazard_type"] = h_name
        res["active_hazards"] = h_name
        res["composite_risk_score"] = res["base_score"]
        res["severity"] = res["composite_risk_score"].apply(score_to_severity)
        res["is_multi_hazard"] = False
        return res[[
            "geometry", "hazard_type", "active_hazards",
            "composite_risk_score", "severity", "is_multi_hazard"
        ]]
        
    # Multi-layer combination:
    # 1. Collect all individual polygons
    records = []
    layer_keys = list(processed_layers.keys())
    
    for h_name, layer in processed_layers.items():
        for _, row in layer.iterrows():
            records.append({
                "geometry": row.geometry,
                "hazard_type": h_name,
                "active_hazards": h_name,
                "composite_risk_score": float(row["base_score"]),
                "severity": score_to_severity(row["base_score"]),
                "is_multi_hazard": False,
            })
            
    # 2. Check for intersections between each pair of hazard layers to find compound co-located hotspots
    for i in range(len(layer_keys)):
        for j in range(i + 1, len(layer_keys)):
            k1 = layer_keys[i]
            k2 = layer_keys[j]
            l1 = processed_layers[k1]
            l2 = processed_layers[k2]
            
            inter = spatial_intersection(l1, l2, keep_geom_type="Polygon", name_a=k1, name_b=k2)
            if not inter.empty:
                w1 = norm_weights.get(k1, 0.5)
                w2 = norm_weights.get(k2, 0.5)
                w_sub_total = w1 + w2
                
                for _, row in inter.iterrows():
                    s1 = float(row.get("base_score_1", 50.0))
                    s2 = float(row.get("base_score_2", 50.0))
                    
                    # Compound risk calculation: weighted average + synergy amplifier for dual hazard
                    synergy_boost = 15.0  # Coinciding hazards amplify vulnerability
                    compound_score = ((s1 * w1 + s2 * w2) / w_sub_total) + synergy_boost
                    compound_score = min(100.0, max(0.0, compound_score))
                    
                    records.append({
                        "geometry": row.geometry,
                        "hazard_type": "MULTI_HAZARD",
                        "active_hazards": f"{k1}, {k2}",
                        "composite_risk_score": round(compound_score, 2),
                        "severity": score_to_severity(compound_score),
                        "is_multi_hazard": True,
                    })
                    
    combined_gdf = gpd.GeoDataFrame(records, crs=ref_crs)
    combined_gdf = validate_and_clean_geometries(
        combined_gdf, repair=True, drop_empty=True, layer_name="Combined Hazard Layer"
    )
    return combined_gdf
