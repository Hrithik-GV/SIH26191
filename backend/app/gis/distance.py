"""Distance calculations and proximity analysis in metric space.

Ensures that all distance calculations are evaluated in meters using appropriate
projected coordinate systems rather than degree-based Euclidean calculations.
"""

from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.ops import nearest_points

from backend.app.gis.crs import (
    validate_crs,
    ensure_compatible_crs,
    to_metric_crs,
)
from backend.app.gis.geometry_utils import validate_and_clean_geometries


def calculate_pairwise_distances(
    origins_gdf: gpd.GeoDataFrame,
    destinations_gdf: gpd.GeoDataFrame,
    origin_id_col: str = "id",
    dest_id_col: str = "id",
) -> pd.DataFrame:
    """Calculate pairwise distances in meters between two sets of spatial geometries.
    
    Args:
        origins_gdf: Starting geometries (e.g. habitations).
        destinations_gdf: Target geometries (e.g. relocation sites or shelters).
        origin_id_col: ID column in origins_gdf.
        dest_id_col: ID column in destinations_gdf.
        
    Returns:
        DataFrame with columns: [origin_id, dest_id, distance_meters, distance_km]
    """
    if origins_gdf.empty or destinations_gdf.empty:
        return pd.DataFrame(columns=[origin_id_col, dest_id_col, "distance_meters", "distance_km"])
        
    clean_orig = validate_and_clean_geometries(origins_gdf, layer_name="Origins")
    clean_dest = validate_and_clean_geometries(destinations_gdf, layer_name="Destinations")
    
    # Transform to common metric CRS
    metric_orig, _ = to_metric_crs(clean_orig)
    metric_orig, metric_dest = ensure_compatible_crs(metric_orig, clean_dest, target_crs=metric_orig.crs)
    
    rows = []
    for _, o_row in metric_orig.iterrows():
        o_geom = o_row.geometry
        o_id = o_row[origin_id_col] if origin_id_col in o_row else o_row.name
        
        # Calculate distance to all destinations
        distances = metric_dest.geometry.distance(o_geom)
        for d_idx, dist in distances.items():
            d_row = metric_dest.loc[d_idx]
            d_id = d_row[dest_id_col] if dest_id_col in d_row else d_idx
            rows.append({
                origin_id_col: o_id,
                dest_id_col: d_id,
                "distance_meters": round(float(dist), 2),
                "distance_km": round(float(dist) / 1000.0, 3),
            })
            
    return pd.DataFrame(rows)


def calculate_distance_to_hazard(
    target_gdf: gpd.GeoDataFrame,
    hazard_gdf: gpd.GeoDataFrame,
    hazard_type: Optional[str] = None,
    max_search_distance_meters: Optional[float] = None,
) -> gpd.GeoDataFrame:
    """Calculate distance in meters from each target feature to the nearest hazard zone boundary.
    
    If the target geometry touches or overlaps the hazard zone, the distance is 0.0m.
    
    Args:
        target_gdf: GeoDataFrame of habitations, relocation sites, or infrastructure.
        hazard_gdf: GeoDataFrame of designated hazard red zones (Flood, Landslide, etc.).
        hazard_type: Optional filter (e.g. 'FLOOD', 'LANDSLIDE').
        max_search_distance_meters: Optional cutoff; features farther than this are capped or flagged.
        
    Returns:
        target_gdf enriched with:
        - 'distance_to_hazard_meters': Distance in meters to nearest hazard boundary (0.0 if inside).
        - 'is_inside_hazard': Boolean flag.
        - 'nearest_hazard_id': ID of the nearest hazard zone.
        - 'nearest_hazard_type': Type of the nearest hazard zone.
        - 'nearest_hazard_severity': Severity tier of the nearest hazard zone.
    """
    if target_gdf.empty:
        res = target_gdf.copy()
        res["distance_to_hazard_meters"] = np.nan
        res["is_inside_hazard"] = False
        res["nearest_hazard_id"] = None
        res["nearest_hazard_type"] = None
        res["nearest_hazard_severity"] = None
        return res
        
    result = target_gdf.copy()
    
    # Initialize default result columns
    result["distance_to_hazard_meters"] = float("inf")
    result["is_inside_hazard"] = False
    result["nearest_hazard_id"] = None
    result["nearest_hazard_type"] = None
    result["nearest_hazard_severity"] = None
    
    if hazard_gdf.empty:
        return result
        
    filtered_hazard = hazard_gdf.copy()
    if hazard_type:
        filtered_hazard = filtered_hazard[
            filtered_hazard["hazard_type"].astype(str).str.upper() == hazard_type.upper()
        ]
        if filtered_hazard.empty:
            return result
            
    clean_target = validate_and_clean_geometries(result, layer_name="Distance Targets")
    clean_hazard = validate_and_clean_geometries(filtered_hazard, layer_name="Distance Hazards")
    
    # Project to common metric coordinate system
    metric_target, _ = to_metric_crs(clean_target)
    metric_target, metric_hazard = ensure_compatible_crs(metric_target, clean_hazard, target_crs=metric_target.crs)
    
    for t_idx, t_row in metric_target.iterrows():
        t_geom = t_row.geometry
        distances = metric_hazard.geometry.distance(t_geom)
        
        if distances.empty:
            continue
            
        min_idx = distances.idxmin()
        min_dist = float(distances.loc[min_idx])
        nearest_row = metric_hazard.loc[min_idx]
        
        # Check intersection
        is_inside = bool(min_dist == 0.0 or t_geom.intersects(nearest_row.geometry))
        if is_inside:
            min_dist = 0.0
            
        if max_search_distance_meters is not None and min_dist > max_search_distance_meters:
            continue
            
        result.at[t_idx, "distance_to_hazard_meters"] = round(min_dist, 2)
        result.at[t_idx, "is_inside_hazard"] = is_inside
        result.at[t_idx, "nearest_hazard_id"] = str(nearest_row.get("id", min_idx))
        result.at[t_idx, "nearest_hazard_type"] = str(nearest_row.get("hazard_type", "UNKNOWN"))
        result.at[t_idx, "nearest_hazard_severity"] = str(nearest_row.get("severity", "UNKNOWN"))
        
    return result
