"""SIH 2026 Problem Statement 26191 — GIS Processing Engine.

Independent geospatial processing library powered by GeoPandas, Shapely, PyProj, and Rasterio.
"""

from backend.app.gis.exceptions import (
    GISEngineError,
    CRSCompatibilityError,
    InvalidGeometryError,
    EmptyLayerError,
    RasterProcessingError,
    MissingHazardDataError,
)
from backend.app.gis.crs import (
    validate_crs,
    ensure_crs,
    ensure_compatible_crs,
    to_metric_crs,
    estimate_optimal_metric_crs,
    get_utm_epsg_for_lon_lat,
    DEFAULT_GEOGRAPHIC_CRS,
    DEFAULT_PROJECTED_CRS,
)
from backend.app.gis.geometry_utils import (
    validate_and_clean_geometries,
    clean_single_geometry,
    calculate_area_sqm,
)
from backend.app.gis.buffers import (
    create_buffer,
    create_geometry_buffer,
)
from backend.app.gis.intersection import (
    spatial_intersection,
    calculate_polygon_overlap,
)
from backend.app.gis.distance import (
    calculate_pairwise_distances,
    calculate_distance_to_hazard,
)
from backend.app.gis.pip import (
    points_in_polygons,
    count_points_in_polygons,
)
from backend.app.gis.exposure import (
    calculate_hazard_exposure,
    calculate_habitation_exposure,
)
from backend.app.gis.accessibility import (
    calculate_site_accessibility,
)
from backend.app.gis.proximity import (
    calculate_relocation_proximity,
    filter_safe_relocation_sites,
)
from backend.app.gis.raster_dem import (
    calculate_slope,
    extract_habitation_terrain_stats,
)
from backend.app.gis.hazard_combination import (
    combine_hazard_layers,
    score_to_severity,
)
from backend.app.gis.engine import GISEngine

__all__ = [
    # Top-level requested functions
    "calculate_hazard_exposure",
    "calculate_distance_to_hazard",
    "calculate_slope",
    "calculate_site_accessibility",
    "calculate_habitation_exposure",
    "combine_hazard_layers",
    
    # Reusable module functions
    "spatial_intersection",
    "create_buffer",
    "create_geometry_buffer",
    "calculate_pairwise_distances",
    "points_in_polygons",
    "count_points_in_polygons",
    "calculate_polygon_overlap",
    "calculate_relocation_proximity",
    "filter_safe_relocation_sites",
    "extract_habitation_terrain_stats",
    "score_to_severity",
    
    # CRS & Geometry utilities
    "validate_crs",
    "ensure_crs",
    "ensure_compatible_crs",
    "to_metric_crs",
    "estimate_optimal_metric_crs",
    "get_utm_epsg_for_lon_lat",
    "validate_and_clean_geometries",
    "clean_single_geometry",
    "calculate_area_sqm",
    "DEFAULT_GEOGRAPHIC_CRS",
    "DEFAULT_PROJECTED_CRS",
    
    # Exceptions
    "GISEngineError",
    "CRSCompatibilityError",
    "InvalidGeometryError",
    "EmptyLayerError",
    "RasterProcessingError",
    "MissingHazardDataError",
    
    # Unified Class Facade
    "GISEngine",
]
