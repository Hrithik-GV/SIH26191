"""Hazard-zone intersection with habitations and exposure assessment.

Evaluates spatial exposure for:
- Flood inundation zones
- Landslide susceptibility red zones
- Heavy rainfall / cloudburst catchment zones
- General multi-hazard risk overlays
"""

from typing import Optional, List, Dict, Any, Union
import numpy as np
import pandas as pd
import geopandas as gpd

from backend.app.gis.crs import (
    validate_crs,
    ensure_compatible_crs,
    to_metric_crs,
)
from backend.app.gis.geometry_utils import (
    validate_and_clean_geometries,
    calculate_area_sqm,
)
from backend.app.gis.intersection import spatial_intersection


# Severity rank weights for determining peak severity
SEVERITY_RANKS = {
    "VERY_HIGH": 4,
    "CRITICAL": 4,
    "HIGH": 3,
    "MODERATE": 2,
    "MEDIUM": 2,
    "LOW": 1,
}


def calculate_hazard_exposure(
    habitations_gdf: gpd.GeoDataFrame,
    hazard_zones_gdf: gpd.GeoDataFrame,
    hazard_types: Optional[List[str]] = None,
    min_severity: Optional[str] = None,
    habitation_id_col: str = "id",
) -> gpd.GeoDataFrame:
    """Calculate precise geometric exposure of habitations to hazard red zones.
    
    Computes total area, overlapping square meters, percentage coverage,
    and highest severity tier intersecting each habitation boundary.
    
    Args:
        habitations_gdf: Polygons representing village/ward settlements.
        hazard_zones_gdf: Polygons of demarcated hazard zones.
        hazard_types: Optional list of hazard types to include (e.g. ['FLOOD', 'LANDSLIDE']).
        min_severity: Optional filter to ignore hazards below a given severity tier.
        habitation_id_col: Primary key or unique column name for habitations.
        
    Returns:
        habitations_gdf enriched with:
        - 'habitation_area_sqm': Total area of habitation in square meters.
        - 'hazard_overlap_sqm': Area of overlap with hazard zones.
        - 'overlap_percentage': Percentage of settlement inside hazard zones (0-100%).
        - 'intersecting_hazard_count': Number of intersecting hazard polygons.
        - 'max_hazard_severity': Highest severity tier found ('VERY_HIGH', 'HIGH', etc.).
        - 'is_critical_exposure': True if overlap >= 50% or max severity is VERY_HIGH.
        - 'exposure_score': 0-100 normalized spatial exposure score.
    """
    if habitations_gdf.empty:
        res = habitations_gdf.copy()
        for col in [
            "habitation_area_sqm", "hazard_overlap_sqm", "overlap_percentage",
            "intersecting_hazard_count", "max_hazard_severity", "is_critical_exposure", "exposure_score"
        ]:
            res[col] = 0.0 if "sqm" in col or "score" in col or "pct" in col else (False if "is_" in col else None)
        return res
        
    result = habitations_gdf.copy()
    
    # 1. Metric habitation area
    result["habitation_area_sqm"] = calculate_area_sqm(result)
    result["hazard_overlap_sqm"] = 0.0
    result["overlap_percentage"] = 0.0
    result["intersecting_hazard_count"] = 0
    result["max_hazard_severity"] = "NONE"
    result["is_critical_exposure"] = False
    result["exposure_score"] = 0.0
    
    if hazard_zones_gdf.empty:
        return result
        
    filtered_hazards = hazard_zones_gdf.copy()
    
    # Filter hazard types if specified
    if hazard_types:
        types_upper = [t.upper() for t in hazard_types]
        filtered_hazards = filtered_hazards[
            filtered_hazards["hazard_type"].astype(str).str.upper().isin(types_upper)
        ]
        if filtered_hazards.empty:
            return result
            
    # Filter by minimum severity if specified
    if min_severity:
        min_rank = SEVERITY_RANKS.get(min_severity.upper(), 1)
        filtered_hazards = filtered_hazards[
            filtered_hazards["severity"].astype(str).str.upper().map(lambda s: SEVERITY_RANKS.get(s, 0)) >= min_rank
        ]
        if filtered_hazards.empty:
            return result
            
    # 2. Perform intersection
    inter = spatial_intersection(
        result,
        filtered_hazards,
        keep_geom_type="Polygon",
        name_a="Habitations",
        name_b="Hazard Zones",
    )
    
    if inter.empty:
        return result
        
    # Determine the habitation ID column in intersection
    hid_col = habitation_id_col if habitation_id_col in inter.columns else f"{habitation_id_col}_1"
    if hid_col not in inter.columns and habitation_id_col in result.columns:
        hid_col = habitation_id_col
        
    # Group by habitation ID
    grouped = inter.groupby(hid_col)
    
    for idx, row in result.iterrows():
        hab_id = row[habitation_id_col] if habitation_id_col in row else idx
        if hab_id not in grouped.groups:
            continue
            
        group_df = grouped.get_group(hab_id)
        
        # Dissolve overlapping hazard geometries for this habitation to avoid double-counting overlapping zones
        hab_area = float(row["habitation_area_sqm"])
        overlap_sqm = float(group_df["intersection_area_sqm"].sum())
        
        # If multiple hazards overlap the same habitation, dissolve geometries to find true union area
        if len(group_df) > 1:
            try:
                union_geom = group_df.geometry.union_all()
                union_gs = gpd.GeoSeries([union_geom], crs=group_df.crs)
                union_proj, _ = to_metric_crs(gpd.GeoDataFrame(geometry=union_gs, crs=group_df.crs))
                overlap_sqm = float(union_proj.geometry.iloc[0].area)
            except Exception:
                overlap_sqm = min(hab_area, overlap_sqm)
                
        pct = (overlap_sqm / hab_area * 100.0) if hab_area > 0 else 0.0
        pct = min(100.0, max(0.0, pct))
        
        # Find highest severity in group
        severities = group_df["severity"].astype(str).str.upper().tolist() if "severity" in group_df.columns else []
        max_rank = 0
        peak_sev = "NONE"
        for s in severities:
            rk = SEVERITY_RANKS.get(s, 0)
            if rk > max_rank:
                max_rank = rk
                peak_sev = s
                
        is_crit = (pct >= 50.0) or (peak_sev in ["VERY_HIGH", "CRITICAL"])
        
        # Composite spatial exposure score (0-100)
        # Weights: 60% overlap percentage, 40% peak severity weight
        sev_score = (max_rank / 4.0) * 100.0
        exposure_score = (pct * 0.6) + (sev_score * 0.4)
        
        result.at[idx, "hazard_overlap_sqm"] = round(overlap_sqm, 2)
        result.at[idx, "overlap_percentage"] = round(pct, 2)
        result.at[idx, "intersecting_hazard_count"] = len(group_df)
        result.at[idx, "max_hazard_severity"] = peak_sev
        result.at[idx, "is_critical_exposure"] = bool(is_crit)
        result.at[idx, "exposure_score"] = round(min(100.0, exposure_score), 2)
        
    return result


def calculate_habitation_exposure(
    habitations_gdf: gpd.GeoDataFrame,
    hazard_zones_gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Convenience pipeline function calculating multi-hazard exposure for habitations.
    
    Explicitly breaks down exposure across the prototype hazards:
    - FLOOD
    - LANDSLIDE
    - RAINFALL / CLOUDBURST
    - MULTI_HAZARD
    
    Returns:
        habitations_gdf enriched with comprehensive spatial exposure statistics.
    """
    # 1. Base overall hazard exposure
    res = calculate_hazard_exposure(habitations_gdf, hazard_zones_gdf)
    
    # 2. Add individual hazard breakdowns if hazard_zones_gdf contains hazard_type column
    if not hazard_zones_gdf.empty and "hazard_type" in hazard_zones_gdf.columns:
        hazard_types = ["FLOOD", "LANDSLIDE", "RAINFALL"]
        for ht in hazard_types:
            sub_res = calculate_hazard_exposure(habitations_gdf, hazard_zones_gdf, hazard_types=[ht])
            col_name = f"{ht.lower()}_overlap_pct"
            res[col_name] = sub_res["overlap_percentage"]
            
    return res
