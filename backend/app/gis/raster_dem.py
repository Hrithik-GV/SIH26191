"""Elevation and slope processing from raster Digital Elevation Model (DEM) data.

Implements terrain analysis using Rasterio and NumPy, computing slope in degrees
via Horn's 3x3 gradient algorithm, and calculating zonal statistics (mean, min, max slope
and elevation) across vulnerable habitation polygons.
"""

from typing import Union, Tuple, Optional, Dict, Any, List
from pathlib import Path
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.io import DatasetReader
import shapely.geometry

from backend.app.gis.exceptions import RasterProcessingError
from backend.app.gis.geometry_utils import validate_and_clean_geometries
from backend.app.gis.crs import validate_crs


def calculate_slope(
    dem_source: Union[str, Path, DatasetReader, np.ndarray],
    cell_size_x: float = 30.0,
    cell_size_y: float = 30.0,
    nodata: Optional[float] = None,
    method: str = "horn",
) -> Tuple[np.ndarray, Optional[Any]]:
    """Calculate terrain slope in degrees (0° - 90°) from a Digital Elevation Model.
    
    Uses Horn's formula (standard in USGS and GDAL/GIS systems), which weighs adjacent cells
    higher than diagonal cells in a 3x3 sliding neighborhood to produce realistic gradients:
    
      dz/dx = ((c + 2*f + i) - (a + 2*d + g)) / (8 * cell_size_x)
      dz/dy = ((g + 2*h + i) - (a + 2*b + c)) / (8 * cell_size_y)
      slope_degrees = arctan(sqrt(dz/dx^2 + dz/dy^2)) * (180 / pi)
      
    Args:
        dem_source: File path, open rasterio dataset, or 2D numpy array containing elevation in meters.
        cell_size_x: Spatial resolution in X (meters). Extracted from raster if dataset supplied.
        cell_size_y: Spatial resolution in Y (meters). Extracted from raster if dataset supplied.
        nodata: Value indicating missing/void elevation data.
        method: Gradient method ('horn' or 'finite_diff').
        
    Returns:
        Tuple of (slope_degrees_array, raster_profile_or_none)
    """
    profile = None
    close_dataset = False
    dataset = None
    
    if isinstance(dem_source, (str, Path)):
        try:
            dataset = rasterio.open(str(dem_source))
            close_dataset = True
        except Exception as e:
            raise RasterProcessingError(f"Failed to open DEM raster file '{dem_source}': {e}")
            
    elif isinstance(dem_source, DatasetReader):
        dataset = dem_source
        
    if dataset is not None:
        profile = dataset.profile.copy()
        # Resolution in meters (assumes projected DEM or extracts from affine transform)
        res_x = abs(dataset.transform.a)
        res_y = abs(dataset.transform.e)
        if res_x > 0:
            cell_size_x = res_x
        if res_y > 0:
            cell_size_y = res_y
        nodata = dataset.nodata
        elevation = dataset.read(1).astype(np.float64)
        if close_dataset:
            dataset.close()
    elif isinstance(dem_source, np.ndarray):
        elevation = dem_source.astype(np.float64)
        if elevation.ndim != 2:
            raise RasterProcessingError(f"Elevation array must be 2D, got shape {elevation.shape}")
    else:
        raise RasterProcessingError(f"Unsupported DEM source type: {type(dem_source)}")
        
    rows, cols = elevation.shape
    if rows < 3 or cols < 3:
        # Array too small for 3x3 kernel
        return np.zeros_like(elevation), profile
        
    # Mask nodata
    valid_mask = np.ones_like(elevation, dtype=bool)
    if nodata is not None:
        valid_mask = ~np.isclose(elevation, nodata)
        
    # Pad elevation edges using edge replication to compute gradients at boundaries
    padded = np.pad(elevation, pad_width=1, mode="edge")
    
    # 3x3 neighborhood extraction:
    # [a, b, c]
    # [d, e, f]
    # [g, h, i]
    a = padded[:-2, :-2]
    b = padded[:-2, 1:-1]
    c = padded[:-2, 2:]
    d = padded[1:-1, :-2]
    # e is the center cell
    f = padded[1:-1, 2:]
    g = padded[2:, :-2]
    h = padded[2:, 1:-1]
    i = padded[2:, 2:]
    
    if method == "horn":
        dz_dx = ((c + 2.0 * f + i) - (a + 2.0 * d + g)) / (8.0 * cell_size_x)
        dz_dy = ((g + 2.0 * h + i) - (a + 2.0 * b + c)) / (8.0 * cell_size_y)
    else:
        dz_dx = (f - d) / (2.0 * cell_size_x)
        dz_dy = (h - b) / (2.0 * cell_size_y)
        
    rise_run = np.sqrt(dz_dx**2 + dz_dy**2)
    slope_radians = np.arctan(rise_run)
    slope_degrees = np.degrees(slope_radians)
    
    # Re-apply nodata
    if nodata is not None:
        slope_degrees[~valid_mask] = np.nan
        
    # Clip to valid degree range [0.0, 90.0]
    slope_degrees = np.clip(slope_degrees, 0.0, 90.0)
    
    return slope_degrees, profile


def extract_habitation_terrain_stats(
    dem_dataset: DatasetReader,
    habitations_gdf: gpd.GeoDataFrame,
    slope_nodata: float = -9999.0,
) -> gpd.GeoDataFrame:
    """Extract zonal elevation and slope statistics for habitation settlement polygons.
    
    Computes:
    - elevation_mean, elevation_min, elevation_max
    - slope_mean_deg, slope_max_deg
    - is_steep_slope: True if mean slope > 25° or max slope > 35° (high landslide hazard)
    
    Args:
        dem_dataset: Open Rasterio DatasetReader representing DEM raster.
        habitations_gdf: GeoDataFrame of habitation settlement boundaries.
        slope_nodata: NoData value for masked slope calculations.
        
    Returns:
        habitations_gdf enriched with terrain attributes.
    """
    if habitations_gdf.empty:
        res = habitations_gdf.copy()
        for col in ["elevation_mean", "elevation_min", "elevation_max", "slope_mean_deg", "slope_max_deg", "is_steep_slope"]:
            res[col] = 0.0 if "slope" in col or "elevation" in col else False
        return res
        
    clean_habs = validate_and_clean_geometries(habitations_gdf, layer_name="Terrain Habitations")
    
    # Ensure habitations match DEM CRS
    dem_crs = dem_dataset.crs
    if dem_crs is not None and clean_habs.crs != dem_crs:
        aligned_habs = clean_habs.to_crs(dem_crs)
    else:
        aligned_habs = clean_habs
        
    result = habitations_gdf.copy()
    result["elevation_mean"] = 0.0
    result["elevation_min"] = 0.0
    result["elevation_max"] = 0.0
    result["slope_mean_deg"] = 0.0
    result["slope_max_deg"] = 0.0
    result["is_steep_slope"] = False
    
    # Pre-calculate full raster slope
    full_dem = dem_dataset.read(1)
    res_x = abs(dem_dataset.transform.a)
    res_y = abs(dem_dataset.transform.e)
    slope_grid, _ = calculate_slope(full_dem, cell_size_x=res_x, cell_size_y=res_y, nodata=dem_dataset.nodata)
    
    for idx, row in aligned_habs.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
            
        try:
            # Mask DEM using habitation geometry
            geom_geojson = [shapely.geometry.mapping(geom)]
            out_image, out_transform = mask(dem_dataset, geom_geojson, crop=True, all_touched=True)
            elev_band = out_image[0]
            
            # Mask out nodata
            valid_elev = elev_band[elev_band != dem_dataset.nodata]
            if len(valid_elev) > 0:
                result.at[idx, "elevation_mean"] = round(float(np.mean(valid_elev)), 1)
                result.at[idx, "elevation_min"] = round(float(np.min(valid_elev)), 1)
                result.at[idx, "elevation_max"] = round(float(np.max(valid_elev)), 1)
                
            # Compute slope on the cropped patch
            if elev_band.shape[0] >= 3 and elev_band.shape[1] >= 3:
                cropped_slope, _ = calculate_slope(elev_band, cell_size_x=res_x, cell_size_y=res_y, nodata=dem_dataset.nodata)
                valid_slope = cropped_slope[~np.isnan(cropped_slope)]
                if len(valid_slope) > 0:
                    mean_sl = float(np.mean(valid_slope))
                    max_sl = float(np.max(valid_slope))
                    result.at[idx, "slope_mean_deg"] = round(mean_sl, 1)
                    result.at[idx, "slope_max_deg"] = round(max_sl, 1)
                    result.at[idx, "is_steep_slope"] = bool(mean_sl > 25.0 or max_sl > 35.0)
        except Exception:
            # Point or sliver outside raster bounds
            continue
            
    return result
