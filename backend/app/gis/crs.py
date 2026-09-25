"""Coordinate Reference System (CRS) management and validation utilities.

Key Guiding Principles:
1. Never silently perform metric calculations (distances, areas, buffers) in geographic degrees (EPSG:4326).
2. Explicitly validate coordinate systems; fail fast with CRSCompatibilityError if incompatible or undefined.
3. Automatically determine the most accurate local UTM projection for regional calculations (e.g. Kerala / Western Ghats: UTM Zone 43N - EPSG:32643).
"""

from typing import Optional, Tuple, Union
import math
import geopandas as gpd
from pyproj import CRS
from shapely.geometry.base import BaseGeometry

from backend.app.gis.exceptions import CRSCompatibilityError

DEFAULT_GEOGRAPHIC_CRS = "EPSG:4326"
DEFAULT_PROJECTED_CRS = "EPSG:3857"  # Web Mercator


def get_utm_epsg_for_lon_lat(longitude: float, latitude: float) -> str:
    """Calculate the EPSG code for the UTM zone covering the given coordinate.
    
    Args:
        longitude: Longitude in degrees (-180 to 180).
        latitude: Latitude in degrees (-90 to 90).
        
    Returns:
        EPSG string like 'EPSG:32643' (Northern hemisphere) or 'EPSG:32743' (Southern hemisphere).
    """
    if not (-180.0 <= longitude <= 180.0 and -90.0 <= latitude <= 90.0):
        raise ValueError(f"Coordinate ({longitude}, {latitude}) out of valid range [-180, 180], [-90, 90].")
    
    zone_number = int(math.floor((longitude + 180.0) / 6.0)) + 1
    if zone_number > 60:
        zone_number = 60
    elif zone_number < 1:
        zone_number = 1
        
    epsg_code = (32600 if latitude >= 0 else 32700) + zone_number
    return f"EPSG:{epsg_code}"


def estimate_optimal_metric_crs(data: Union[gpd.GeoDataFrame, gpd.GeoSeries, BaseGeometry]) -> str:
    """Determine the optimal metric projected CRS for a spatial dataset.
    
    If the data is in geographic coordinates (EPSG:4326 or similar), computes the centroid
    and returns the local UTM EPSG code to ensure minimal distortion in distance/area calculations.
    """
    if isinstance(data, (gpd.GeoDataFrame, gpd.GeoSeries)):
        if data.empty:
            return DEFAULT_PROJECTED_CRS
        
        # If already projected, return its current CRS
        if data.crs and data.crs.is_projected:
            return data.crs.to_string()
            
        # If geographic or not set, compute centroid in 4326
        gdf = data.copy()
        if gdf.crs is None:
            gdf = gdf.set_crs(DEFAULT_GEOGRAPHIC_CRS)
        elif gdf.crs.to_string() != DEFAULT_GEOGRAPHIC_CRS:
            gdf = gdf.to_crs(DEFAULT_GEOGRAPHIC_CRS)
            
        bounds = gdf.total_bounds  # minx, miny, maxx, maxy
        mid_lon = (bounds[0] + bounds[2]) / 2.0
        mid_lat = (bounds[1] + bounds[3]) / 2.0
        return get_utm_epsg_for_lon_lat(mid_lon, mid_lat)
    
    elif isinstance(data, BaseGeometry):
        centroid = data.centroid
        return get_utm_epsg_for_lon_lat(centroid.x, centroid.y)
    
    return DEFAULT_PROJECTED_CRS


def validate_crs(gdf: Union[gpd.GeoDataFrame, gpd.GeoSeries], layer_name: str = "Layer") -> CRS:
    """Validate that the GeoDataFrame has a valid, non-null CRS.
    
    Raises:
        CRSCompatibilityError: If CRS is None or invalid.
    """
    if gdf.crs is None:
        raise CRSCompatibilityError(
            f"{layer_name} does not have a Coordinate Reference System (CRS) defined. "
            f"Specify a CRS explicitly (e.g. .set_crs('{DEFAULT_GEOGRAPHIC_CRS}')) before processing."
        )
    return gdf.crs


def ensure_crs(
    gdf: gpd.GeoDataFrame,
    default_crs: str = DEFAULT_GEOGRAPHIC_CRS,
    force_crs: Optional[str] = None
) -> gpd.GeoDataFrame:
    """Ensure a GeoDataFrame has a CRS assigned or transformed to force_crs.
    
    Args:
        gdf: Input GeoDataFrame.
        default_crs: Assigned if input has no CRS.
        force_crs: If provided, reprojects the layer to this CRS.
    """
    out_gdf = gdf.copy()
    if out_gdf.crs is None:
        out_gdf = out_gdf.set_crs(default_crs)
        
    if force_crs is not None and out_gdf.crs.to_string() != CRS.from_user_input(force_crs).to_string():
        out_gdf = out_gdf.to_crs(force_crs)
        
    return out_gdf


def ensure_compatible_crs(
    gdf_a: gpd.GeoDataFrame,
    gdf_b: gpd.GeoDataFrame,
    target_crs: Optional[str] = None,
    name_a: str = "Layer A",
    name_b: str = "Layer B",
) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Verify that both layers have valid CRSes and reproject them to match.
    
    Never silently assumes two layers in different or undefined CRSes are compatible.
    
    Args:
        gdf_a: First GeoDataFrame.
        gdf_b: Second GeoDataFrame.
        target_crs: Optional specific CRS to reproject both to. If None, reprojects gdf_b to match gdf_a.
        name_a: Name of first layer for clear error messages.
        name_b: Name of second layer for clear error messages.
        
    Returns:
        Tuple of (reprojected_gdf_a, reprojected_gdf_b) in identical CRS.
        
    Raises:
        CRSCompatibilityError: If either layer is missing a CRS.
    """
    validate_crs(gdf_a, name_a)
    validate_crs(gdf_b, name_b)
    
    out_a = gdf_a.copy()
    out_b = gdf_b.copy()
    
    if target_crs is not None:
        target = CRS.from_user_input(target_crs)
        if out_a.crs != target:
            out_a = out_a.to_crs(target)
        if out_b.crs != target:
            out_b = out_b.to_crs(target)
        return out_a, out_b
        
    # If no target specified, match layer_b to layer_a
    if out_a.crs != out_b.crs:
        out_b = out_b.to_crs(out_a.crs)
        
    return out_a, out_b


def to_metric_crs(
    gdf: gpd.GeoDataFrame,
    target_metric_crs: Optional[str] = None
) -> Tuple[gpd.GeoDataFrame, str]:
    """Reproject a GeoDataFrame to an appropriate metric projected coordinate system.
    
    If the layer is already in a projected CRS (meters), it is returned unchanged.
    If it is in geographic coordinates (degrees), it is reprojected to the optimal
    local UTM zone or user-specified metric CRS.
    
    Returns:
        Tuple of (metric_projected_gdf, original_crs_str)
    """
    validate_crs(gdf, "Input layer")
    original_crs_str = gdf.crs.to_string()
    
    if gdf.crs.is_projected:
        return gdf.copy(), original_crs_str
        
    metric_crs = target_metric_crs or estimate_optimal_metric_crs(gdf)
    projected_gdf = gdf.to_crs(metric_crs)
    return projected_gdf, original_crs_str
