"""Geometry validation, repair, cleaning, and sanitization utilities.

Ensures that all input geometries conform to OGC standards before running
spatial intersections, buffers, and distance calculations.
"""

from typing import Union, List, Optional
import logging
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection
from shapely.geometry.base import BaseGeometry
import shapely

from backend.app.gis.exceptions import InvalidGeometryError
from backend.app.gis.crs import to_metric_crs

logger = logging.getLogger(__name__)


def clean_single_geometry(
    geom: Optional[BaseGeometry],
    repair: bool = True,
    target_type: Optional[str] = None
) -> Optional[BaseGeometry]:
    """Validate and optionally repair a single Shapely geometry.
    
    Args:
        geom: Input Shapely geometry or None.
        repair: If True, uses shapely.make_valid on invalid geometries.
        target_type: Optional filter like 'Polygon' to retain only polygonal components.
        
    Returns:
        Repaired/cleaned geometry or None if empty/unrepairable.
    """
    if geom is None or geom.is_empty:
        return None
        
    # Check validity
    if not geom.is_valid:
        if repair:
            try:
                geom = shapely.make_valid(geom)
            except Exception as e:
                logger.warning(f"Failed to repair geometry with shapely.make_valid: {e}")
                return None
        else:
            return None
            
    # Handle GeometryCollection unpacking if target_type is specified
    if target_type == "Polygon" and isinstance(geom, GeometryCollection):
        polygons = [g for g in geom.geoms if isinstance(g, (Polygon, MultiPolygon))]
        if not polygons:
            return None
        if len(polygons) == 1:
            geom = polygons[0]
        else:
            # Combine multiple polygon parts into a MultiPolygon
            parts: List[Polygon] = []
            for p in polygons:
                if isinstance(p, Polygon):
                    parts.append(p)
                elif isinstance(p, MultiPolygon):
                    parts.extend(p.geoms)
            geom = MultiPolygon(parts) if parts else None
            
    return geom


def validate_and_clean_geometries(
    gdf: gpd.GeoDataFrame,
    repair: bool = True,
    drop_empty: bool = True,
    target_type: Optional[str] = None,
    layer_name: str = "Layer"
) -> gpd.GeoDataFrame:
    """Validate and clean all geometries in a GeoDataFrame.
    
    - Checks geom.is_valid for each row.
    - If repair is True, applies shapely.make_valid to repair self-intersections / bowties.
    - Drops or flags empty/null geometries based on drop_empty.
    - Preserves CRS and all attribute columns.
    
    Returns:
        Cleaned GeoDataFrame with guaranteed valid geometries.
    """
    if gdf.empty:
        return gdf.copy()
        
    out = gdf.copy()
    initial_count = len(out)
    
    # 1. Flag and repair invalid geometries
    def _process_geom(g):
        return clean_single_geometry(g, repair=repair, target_type=target_type)
        
    out[out.geometry.name] = out[out.geometry.name].apply(_process_geom)
    
    # 2. Drop None or empty geometries if requested
    if drop_empty:
        valid_mask = out.geometry.notna() & (~out.geometry.is_empty)
        dropped_count = initial_count - valid_mask.sum()
        if dropped_count > 0:
            logger.info(f"[{layer_name}] Dropped {dropped_count} invalid or empty geometries out of {initial_count}.")
        out = out[valid_mask].copy()
        
    # Final check
    invalid_mask = ~out.geometry.is_valid
    if invalid_mask.any():
        num_invalid = invalid_mask.sum()
        logger.error(f"[{layer_name}] {num_invalid} geometries remain invalid after cleaning.")
        raise InvalidGeometryError(
            f"{num_invalid} geometries in {layer_name} could not be repaired.",
            details={"invalid_indices": out[invalid_mask].index.tolist()}
        )
        
    return out


def calculate_area_sqm(gdf: gpd.GeoDataFrame) -> gpd.GeoSeries:
    """Calculate the precise area in square meters for each polygon feature.
    
    Automatically transforms geographic coordinates (degrees) to the optimal
    metric projected CRS before computing area, preventing erroneous degree-squared results.
    """
    if gdf.empty:
        return gpd.GeoSeries(dtype=float)
        
    projected, _ = to_metric_crs(gdf)
    return projected.geometry.area
