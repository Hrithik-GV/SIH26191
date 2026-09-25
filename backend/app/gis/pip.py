"""Point-in-Polygon (PIP) checks and spatial join operations.

Supports assessing which habitations, sensors, or evacuation assembly points
fall within designated administrative boundaries or hazard impact zones.
"""

from typing import Optional, List, Dict, Any
import pandas as pd
import geopandas as gpd

from backend.app.gis.crs import (
    validate_crs,
    ensure_compatible_crs,
)
from backend.app.gis.geometry_utils import validate_and_clean_geometries


def points_in_polygons(
    points_gdf: gpd.GeoDataFrame,
    polygons_gdf: gpd.GeoDataFrame,
    predicate: str = "within",
    polygon_id_col: str = "id",
) -> gpd.GeoDataFrame:
    """Perform spatial join to identify which polygon contains each point feature.
    
    Args:
        points_gdf: GeoDataFrame containing point geometries (e.g. weather stations, dwellings).
        polygons_gdf: GeoDataFrame containing polygon geometries (e.g. hazard zones, habitations).
        predicate: Spatial predicate ('within', 'intersects').
        polygon_id_col: Column from polygons_gdf to retain in the result.
        
    Returns:
        points_gdf joined with polygon attributes. Adds 'is_contained' boolean flag.
    """
    if points_gdf.empty:
        res = points_gdf.copy()
        res["is_contained"] = False
        res[f"poly_{polygon_id_col}"] = None
        return res
        
    if polygons_gdf.empty:
        res = points_gdf.copy()
        res["is_contained"] = False
        res[f"poly_{polygon_id_col}"] = None
        return res
        
    clean_pts = validate_and_clean_geometries(points_gdf, layer_name="PIP Points")
    clean_poly = validate_and_clean_geometries(polygons_gdf, layer_name="PIP Polygons")
    
    matched_pts, matched_poly = ensure_compatible_crs(
        clean_pts, clean_poly, name_a="Points", name_b="Polygons"
    )
    
    joined = gpd.sjoin(matched_pts, matched_poly, how="left", predicate=predicate)
    
    # Restore original column names if they collided with polygon columns
    for col in clean_pts.columns:
        if col != "geometry" and col not in joined.columns and f"{col}_left" in joined.columns:
            joined[col] = joined[f"{col}_left"]
            
    # Add clear boolean column
    index_right_col = "index_right"
    joined["is_contained"] = joined[index_right_col].notna().astype(bool)
    
    return joined


def count_points_in_polygons(
    polygons_gdf: gpd.GeoDataFrame,
    points_gdf: gpd.GeoDataFrame,
    count_col_name: str = "point_count",
) -> gpd.GeoDataFrame:
    """Count the number of point features falling inside each polygon.
    
    Args:
        polygons_gdf: Base polygons (e.g. habitations or hazard zones).
        points_gdf: Point observations or assets (e.g. houses, telemetry stations).
        count_col_name: Name of the resulting count column.
        
    Returns:
        polygons_gdf enriched with point_count column.
    """
    result = polygons_gdf.copy()
    result[count_col_name] = 0
    
    if polygons_gdf.empty or points_gdf.empty:
        return result
        
    joined = points_in_polygons(points_gdf, polygons_gdf, predicate="within")
    
    # Count occurrences by polygon index
    if "index_right" in joined.columns:
        counts = joined["index_right"].value_counts()
        for poly_idx, cnt in counts.items():
            if poly_idx in result.index:
                result.at[poly_idx, count_col_name] = int(cnt)
                
    return result
