"""Spatial intersection and geometric overlap calculations.

Provides functions to compute spatial intersections, area overlaps, and percentage
coverage between habitations, hazard zones, and candidate relocation sites.
"""

from typing import Optional, List, Dict, Any
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

from backend.app.gis.crs import (
    validate_crs,
    ensure_compatible_crs,
    to_metric_crs,
)
from backend.app.gis.geometry_utils import (
    validate_and_clean_geometries,
    calculate_area_sqm,
)


def spatial_intersection(
    gdf_a: gpd.GeoDataFrame,
    gdf_b: gpd.GeoDataFrame,
    keep_geom_type: Optional[str] = "Polygon",
    name_a: str = "Layer A",
    name_b: str = "Layer B",
) -> gpd.GeoDataFrame:
    """Compute geometric intersection between two layers with CRS compatibility enforcement.
    
    Args:
        gdf_a: Primary GeoDataFrame.
        gdf_b: Secondary GeoDataFrame.
        keep_geom_type: If 'Polygon', retains only 2D polygonal intersections (filtering out sliver points/lines).
        name_a: Label for first layer in logging/errors.
        name_b: Label for second layer in logging/errors.
        
    Returns:
        GeoDataFrame of intersected geometries with combined attributes and 'intersection_area_sqm'.
    """
    if gdf_a.empty or gdf_b.empty:
        # Return empty GeoDataFrame with merged columns
        cols = list(gdf_a.columns) + [c for c in gdf_b.columns if c not in gdf_a.columns and c != "geometry"]
        cols.append("intersection_area_sqm")
        return gpd.GeoDataFrame(columns=cols, crs=gdf_a.crs)
        
    # 1. Clean geometries before overlay
    clean_a = validate_and_clean_geometries(gdf_a, layer_name=name_a)
    clean_b = validate_and_clean_geometries(gdf_b, layer_name=name_b)
    
    if clean_a.empty or clean_b.empty:
        return gpd.GeoDataFrame(crs=gdf_a.crs)
        
    # 2. Ensure both layers share the exact same CRS
    matched_a, matched_b = ensure_compatible_crs(clean_a, clean_b, name_a=name_a, name_b=name_b)
    
    # 3. Perform overlay intersection
    intersected = gpd.overlay(matched_a, matched_b, how="intersection", keep_geom_type=False)
    
    if intersected.empty:
        intersected["intersection_area_sqm"] = 0.0
        return intersected
        
    # 4. Clean post-intersection geometries
    intersected = validate_and_clean_geometries(
        intersected,
        repair=True,
        drop_empty=True,
        target_type=keep_geom_type,
        layer_name="Intersection Result"
    )
    
    # 5. Compute metric intersection area in square meters
    if not intersected.empty:
        intersected["intersection_area_sqm"] = calculate_area_sqm(intersected)
    else:
        intersected["intersection_area_sqm"] = 0.0
        
    return intersected


def calculate_polygon_overlap(
    base_gdf: gpd.GeoDataFrame,
    overlay_gdf: gpd.GeoDataFrame,
    base_id_col: str = "id",
    overlay_id_col: str = "id",
) -> gpd.GeoDataFrame:
    """Calculate the precise overlap area (sqm) and percentage of base polygons covered by overlay polygons.
    
    Args:
        base_gdf: Base polygons (e.g. habitations).
        overlay_gdf: Overlay polygons (e.g. hazard red zones).
        base_id_col: Unique identifier column in base_gdf.
        overlay_id_col: Unique identifier column in overlay_gdf.
        
    Returns:
        base_gdf copy enriched with:
        - 'base_area_sqm': Total area of base feature in square meters.
        - 'overlap_area_sqm': Area of intersection with overlay in square meters.
        - 'overlap_percentage': Percentage of base feature covered (0.0 to 100.0%).
    """
    if base_gdf.empty:
        res = base_gdf.copy()
        res["base_area_sqm"] = 0.0
        res["overlap_area_sqm"] = 0.0
        res["overlap_percentage"] = 0.0
        return res
        
    result = base_gdf.copy()
    
    # Ensure metric area on base geometries
    result["base_area_sqm"] = calculate_area_sqm(result)
    result["overlap_area_sqm"] = 0.0
    result["overlap_percentage"] = 0.0
    
    if overlay_gdf.empty:
        return result
        
    # Perform intersection
    inter = spatial_intersection(base_gdf, overlay_gdf, keep_geom_type="Polygon")
    
    if inter.empty:
        return result
        
    # Aggregate overlap area per base_id
    id_col = base_id_col if base_id_col in inter.columns else f"{base_id_col}_1"
    if id_col not in inter.columns and base_id_col in result.columns:
        # Try matching by index or available column
        id_col = base_id_col
        
    if id_col in inter.columns:
        overlap_by_id = inter.groupby(id_col)["intersection_area_sqm"].sum()
        
        for idx, row in result.iterrows():
            feat_id = row[base_id_col]
            if feat_id in overlap_by_id:
                ov_area = float(overlap_by_id[feat_id])
                base_area = float(row["base_area_sqm"])
                pct = (ov_area / base_area * 100.0) if base_area > 0 else 0.0
                result.at[idx, "overlap_area_sqm"] = round(ov_area, 2)
                result.at[idx, "overlap_percentage"] = round(min(100.0, max(0.0, pct)), 2)
                
    return result
