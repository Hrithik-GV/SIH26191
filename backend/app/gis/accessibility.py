"""Road and infrastructure accessibility analysis for settlements and relocation sites.

Calculates distance to nearest transport corridors, road density in catchment zones,
and normalized accessibility scores (0-100) essential for emergency evacuation
and logistical viability of candidate relocation parcels.
"""

from typing import Optional, Dict, Any, Union
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


def calculate_site_accessibility(
    sites_gdf: gpd.GeoDataFrame,
    roads_gdf: gpd.GeoDataFrame,
    max_acceptable_distance_meters: float = 1500.0,
    catchment_radius_meters: float = 500.0,
    site_id_col: str = "id",
) -> gpd.GeoDataFrame:
    """Evaluate transport accessibility for candidate relocation sites or habitations.
    
    Computes:
    1. Distance in meters to the nearest road network feature.
    2. Road network density (total length of roads in meters within catchment radius).
    3. Normalized accessibility score (0-100), where 100 indicates immediate direct arterial access.
    
    Args:
        sites_gdf: GeoDataFrame of points or polygons representing sites/habitations.
        roads_gdf: GeoDataFrame of LineStrings/MultiLineStrings representing roads/highways.
        max_acceptable_distance_meters: Distance beyond which accessibility is penalized to zero.
        catchment_radius_meters: Radius in meters around the site to measure road density.
        site_id_col: Identifier column in sites_gdf.
        
    Returns:
        sites_gdf copy enriched with:
        - 'distance_to_road_meters': Distance to closest road feature in meters.
        - 'road_catchment_length_meters': Total road length within catchment buffer.
        - 'is_road_accessible': Boolean (True if distance <= max_acceptable_distance_meters).
        - 'road_accessibility_score': 0-100 composite accessibility score.
    """
    if sites_gdf.empty:
        res = sites_gdf.copy()
        res["distance_to_road_meters"] = np.nan
        res["road_catchment_length_meters"] = 0.0
        res["is_road_accessible"] = False
        res["road_accessibility_score"] = 0.0
        return res
        
    result = sites_gdf.copy()
    result["distance_to_road_meters"] = float("inf")
    result["road_catchment_length_meters"] = 0.0
    result["is_road_accessible"] = False
    result["road_accessibility_score"] = 0.0
    
    if roads_gdf.empty:
        return result
        
    clean_sites = validate_and_clean_geometries(result, layer_name="Accessibility Sites")
    clean_roads = validate_and_clean_geometries(roads_gdf, layer_name="Accessibility Roads")
    
    # 1. Transform both to common metric projection
    metric_sites, _ = to_metric_crs(clean_sites)
    metric_sites, metric_roads = ensure_compatible_crs(metric_sites, clean_roads, target_crs=metric_sites.crs)
    
    # 2. Compute catchment buffers in metric space
    catchment_buffers = create_buffer(
        metric_sites,
        distance_meters=catchment_radius_meters,
        metric_crs=metric_sites.crs.to_string()
    )
    
    for s_idx, s_row in metric_sites.iterrows():
        s_geom = s_row.geometry
        
        # Distance to closest road
        road_distances = metric_roads.geometry.distance(s_geom)
        if road_distances.empty:
            continue
            
        min_dist = float(road_distances.min())
        is_accessible = bool(min_dist <= max_acceptable_distance_meters)
        
        # Road length in catchment buffer
        catchment_geom = catchment_buffers.loc[s_idx].geometry
        clipped_roads = metric_roads.geometry.intersection(catchment_geom)
        road_length_in_buffer = float(clipped_roads.length.sum())
        
        # Calculate 0-100 accessibility score:
        # Distance component: 100 at 0m, decaying to 0 at max_acceptable_distance_meters
        if min_dist >= max_acceptable_distance_meters:
            dist_score = 0.0
        else:
            dist_score = 100.0 * (1.0 - (min_dist / max_acceptable_distance_meters))
            
        # Density bonus: up to 20 bonus points scaled by road length in buffer (e.g. 500m of roads = full bonus)
        density_bonus = min(20.0, (road_length_in_buffer / 500.0) * 20.0)
        
        final_score = min(100.0, max(0.0, (dist_score * 0.8) + density_bonus))
        
        result.at[s_idx, "distance_to_road_meters"] = round(min_dist, 2)
        result.at[s_idx, "road_catchment_length_meters"] = round(road_length_in_buffer, 2)
        result.at[s_idx, "is_road_accessible"] = is_accessible
        result.at[s_idx, "road_accessibility_score"] = round(final_score, 2)
        
    return result
