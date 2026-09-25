"""Buffer generation module with strict metric CRS enforcement.

Ensures that buffer distances are always computed in meters rather than degrees,
avoiding the common pitfall of buffering in geographic coordinates (EPSG:4326).
"""

from typing import Union, Optional
import geopandas as gpd
from shapely.geometry.base import BaseGeometry
import shapely

from backend.app.gis.crs import (
    validate_crs,
    to_metric_crs,
    DEFAULT_GEOGRAPHIC_CRS,
    DEFAULT_PROJECTED_CRS,
    estimate_optimal_metric_crs,
)
from backend.app.gis.geometry_utils import validate_and_clean_geometries


def create_buffer(
    gdf: gpd.GeoDataFrame,
    distance_meters: float,
    resolution: int = 16,
    cap_style: str = "round",
    join_style: str = "round",
    mitre_limit: float = 5.0,
    single_sided: bool = False,
    dissolve: bool = False,
    metric_crs: Optional[str] = None
) -> gpd.GeoDataFrame:
    """Generate a metric buffer around all features in a GeoDataFrame.
    
    Workflow:
    1. Validates input CRS (raises CRSCompatibilityError if missing).
    2. Reprojects to metric CRS (UTM or Web Mercator) so distance_meters is strictly in meters.
    3. Performs buffer operation using Shapely/GeoPandas.
    4. Automatically cleans and repairs resulting buffered geometries.
    5. Optionally dissolves boundaries into a single contiguous polygon.
    6. Reprojects back to the original input CRS.
    
    Args:
        gdf: Input GeoDataFrame (Point, LineString, Polygon, MultiPolygon).
        distance_meters: Buffer radius in meters. Can be negative for inner buffer of polygons.
        resolution: Number of segments used to approximate a quarter circle (default 16).
        cap_style: Style of buffer ends ('round', 'flat', 'square').
        join_style: Style of buffer joins ('round', 'mitre', 'bevel').
        mitre_limit: Maximum ratio of distance to mitre apex (default 5.0).
        single_sided: If True, buffers only one side of LineStrings.
        dissolve: If True, dissolves all overlapping buffer polygons into unified multipart geometries.
        metric_crs: Optional explicit metric CRS; if None, uses optimal local UTM.
        
    Returns:
        GeoDataFrame containing buffered geometries in original CRS.
    """
    if gdf.empty:
        return gdf.copy()
        
    validate_crs(gdf, "Buffer input layer")
    original_crs = gdf.crs
    
    # 1. Ensure geometries are valid before buffering
    clean_gdf = validate_and_clean_geometries(gdf, layer_name="Buffer pre-clean")
    
    # 2. Transform to metric CRS
    projected_gdf, _ = to_metric_crs(clean_gdf, target_metric_crs=metric_crs)
    
    # 3. Buffer in metric space
    buffered_series = projected_gdf.geometry.buffer(
        distance=distance_meters,
        resolution=resolution,
        cap_style=cap_style,
        join_style=join_style,
        mitre_limit=mitre_limit,
        single_sided=single_sided
    )
    
    result = projected_gdf.copy()
    result[result.geometry.name] = buffered_series
    
    # 4. Clean post-buffer geometries
    result = validate_and_clean_geometries(result, repair=True, drop_empty=True, layer_name="Buffer post-clean")
    
    # 5. Dissolve if requested
    if dissolve and not result.empty:
        dissolved = result.dissolve()
        result = dissolved
        
    # 6. Reproject back to original CRS
    if result.crs != original_crs:
        result = result.to_crs(original_crs)
        
    return result


def create_geometry_buffer(
    geom: BaseGeometry,
    distance_meters: float,
    src_crs: str = DEFAULT_GEOGRAPHIC_CRS,
    metric_crs: Optional[str] = None
) -> BaseGeometry:
    """Buffer an individual Shapely geometry by a distance in meters.
    
    Reprojects from src_crs to metric, applies buffer, and reprojects back.
    """
    if geom is None or geom.is_empty:
        return geom
        
    gs = gpd.GeoSeries([geom], crs=src_crs)
    buffered_gdf = create_buffer(
        gpd.GeoDataFrame(geometry=gs, crs=src_crs),
        distance_meters=distance_meters,
        metric_crs=metric_crs
    )
    if buffered_gdf.empty:
        return shapely.geometry.Polygon()
    return buffered_gdf.geometry.iloc[0]
