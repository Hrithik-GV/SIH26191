"""Relocation-site proximity analysis and candidate site screening.

Identifies the nearest, safest, and most viable candidate relocation parcels
for displaced populations, strictly enforcing safety exclusions against active hazard zones.
"""

from typing import Optional, List, Dict, Any
import numpy as np
import pandas as pd
import geopandas as gpd

from backend.app.gis.crs import (
    validate_crs,
    ensure_compatible_crs,
    to_metric_crs,
)
from backend.app.gis.geometry_utils import validate_and_clean_geometries
from backend.app.gis.buffers import create_buffer


def filter_safe_relocation_sites(
    relocation_sites_gdf: gpd.GeoDataFrame,
    hazard_zones_gdf: gpd.GeoDataFrame,
    safety_buffer_meters: float = 100.0,
    excluded_severities: Optional[List[str]] = None,
) -> gpd.GeoDataFrame:
    """Filter candidate relocation sites, strictly excluding parcels inside or near hazard zones.
    
    A candidate relocation site must NEVER be located inside an active hazard red zone
    or within its immediate safety clearance buffer.
    
    Args:
        relocation_sites_gdf: Candidate relocation land parcels.
        hazard_zones_gdf: Active hazard zones (landslide, flood, cloudburst, etc.).
        safety_buffer_meters: Buffer distance around severe hazards where relocation is prohibited.
        excluded_severities: Severities to exclude (default: ['VERY_HIGH', 'CRITICAL', 'HIGH']).
        
    Returns:
        GeoDataFrame of verified safe relocation parcels with 'hazard_safe' = True.
    """
    if relocation_sites_gdf.empty:
        return relocation_sites_gdf.copy()
        
    if hazard_zones_gdf.empty:
        res = relocation_sites_gdf.copy()
        res["hazard_safe"] = True
        return res
        
    ex_sev = [s.upper() for s in (excluded_severities or ["VERY_HIGH", "CRITICAL", "HIGH"])]
    
    # Filter severe hazards
    severe_hazards = hazard_zones_gdf[
        hazard_zones_gdf["severity"].astype(str).str.upper().isin(ex_sev)
    ]
    
    if severe_hazards.empty:
        res = relocation_sites_gdf.copy()
        res["hazard_safe"] = True
        return res
        
    clean_sites = validate_and_clean_geometries(relocation_sites_gdf, layer_name="Candidate Sites")
    clean_hazards = validate_and_clean_geometries(severe_hazards, layer_name="Severe Hazards")
    
    metric_sites, _ = to_metric_crs(clean_sites)
    metric_sites, metric_hazards = ensure_compatible_crs(metric_sites, clean_hazards, target_crs=metric_sites.crs)
    
    # Apply safety buffer to severe hazards in metric units
    buffered_hazards = create_buffer(
        metric_hazards,
        distance_meters=safety_buffer_meters,
        metric_crs=metric_sites.crs.to_string(),
        dissolve=True
    )
    
    hazard_union = buffered_hazards.geometry.iloc[0] if not buffered_hazards.empty else None
    
    safe_mask = []
    for _, s_row in metric_sites.iterrows():
        s_geom = s_row.geometry
        if hazard_union is not None and s_geom.intersects(hazard_union):
            safe_mask.append(False)
        else:
            safe_mask.append(True)
            
    result = relocation_sites_gdf.iloc[[i for i, sm in enumerate(safe_mask) if sm]].copy()
    result["hazard_safe"] = True
    return result


def calculate_relocation_proximity(
    habitations_gdf: gpd.GeoDataFrame,
    relocation_sites_gdf: gpd.GeoDataFrame,
    hazard_zones_gdf: Optional[gpd.GeoDataFrame] = None,
    max_distance_meters: float = 35000.0,
    min_capacity: int = 0,
    hab_id_col: str = "id",
    site_id_col: str = "id",
) -> pd.DataFrame:
    """Analyze proximity and suitability between habitations and candidate relocation sites.
    
    Args:
        habitations_gdf: Habitations requiring relocation or safety analysis.
        relocation_sites_gdf: Available relocation sites with capacity.
        hazard_zones_gdf: Optional hazard zones to filter unsafe relocation sites.
        max_distance_meters: Maximum travel radius (default 35 km).
        min_capacity: Minimum available capacity required.
        hab_id_col: Column name for habitation ID.
        site_id_col: Column name for relocation site ID.
        
    Returns:
        DataFrame ranking candidate sites per habitation by proximity and capacity.
    """
    if habitations_gdf.empty or relocation_sites_gdf.empty:
        return pd.DataFrame(columns=[
            "habitation_id", "site_id", "site_name", "distance_meters", "distance_km",
            "available_capacity", "proximity_rank"
        ])
        
    # 1. Filter out unsafe sites if hazard zones provided
    valid_sites = relocation_sites_gdf.copy()
    if hazard_zones_gdf is not None and not hazard_zones_gdf.empty:
        valid_sites = filter_safe_relocation_sites(valid_sites, hazard_zones_gdf)
        
    # 2. Filter by minimum capacity
    if "available_capacity" in valid_sites.columns:
        valid_sites = valid_sites[valid_sites["available_capacity"] >= min_capacity]
        
    if valid_sites.empty:
        return pd.DataFrame(columns=[
            "habitation_id", "site_id", "site_name", "distance_meters", "distance_km",
            "available_capacity", "proximity_rank"
        ])
        
    clean_habs = validate_and_clean_geometries(habitations_gdf, layer_name="Habitations")
    clean_sites = validate_and_clean_geometries(valid_sites, layer_name="Safe Sites")
    
    metric_habs, _ = to_metric_crs(clean_habs)
    metric_habs, metric_sites = ensure_compatible_crs(metric_habs, clean_sites, target_crs=metric_habs.crs)
    
    rows = []
    for h_idx, h_row in metric_habs.iterrows():
        h_id = h_row[hab_id_col] if hab_id_col in h_row else h_idx
        h_geom = h_row.geometry
        
        # Calculate distances to all candidate sites
        distances = metric_sites.geometry.distance(h_geom)
        
        site_matches = []
        for s_idx, dist in distances.items():
            dist_val = float(dist)
            if dist_val <= max_distance_meters:
                s_row = metric_sites.loc[s_idx]
                s_id = s_row[site_id_col] if site_id_col in s_row else s_idx
                cap = int(s_row.get("available_capacity", 0))
                site_matches.append({
                    "habitation_id": h_id,
                    "site_id": s_id,
                    "site_name": s_row.get("name", f"Site {s_id}"),
                    "distance_meters": round(dist_val, 2),
                    "distance_km": round(dist_val / 1000.0, 2),
                    "available_capacity": cap,
                })
                
        # Sort matches by distance ascending
        site_matches.sort(key=lambda x: x["distance_meters"])
        for rank, match in enumerate(site_matches, start=1):
            match["proximity_rank"] = rank
            rows.append(match)
            
    df = pd.DataFrame(rows)
    # If callers expect hab_id_col / site_id_col columns:
    if not df.empty:
        if hab_id_col not in df.columns:
            df[hab_id_col] = df["habitation_id"]
        if site_id_col != hab_id_col and site_id_col not in df.columns:
            df[site_id_col] = df["site_id"]
    return df
