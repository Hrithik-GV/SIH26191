"""Unified GIS Processing Engine Facade for SIH 2026 Problem Statement 26191.

Provides independent, reusable geospatial processing services powered by
GeoPandas, Shapely, PyProj, and Rasterio.
"""

from typing import Optional, List, Dict, Any, Union, Tuple
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from rasterio.io import DatasetReader

from backend.app.gis.exceptions import (
    GISEngineError,
    CRSCompatibilityError,
    InvalidGeometryError,
    RasterProcessingError,
    EmptyLayerError,
)
from backend.app.gis.crs import (
    validate_crs,
    ensure_crs,
    ensure_compatible_crs,
    to_metric_crs,
    estimate_optimal_metric_crs,
    DEFAULT_GEOGRAPHIC_CRS,
    DEFAULT_PROJECTED_CRS,
)
from backend.app.gis.geometry_utils import (
    validate_and_clean_geometries,
    calculate_area_sqm,
)
from backend.app.gis.buffers import create_buffer, create_geometry_buffer
from backend.app.gis.intersection import spatial_intersection, calculate_polygon_overlap
from backend.app.gis.distance import calculate_pairwise_distances, calculate_distance_to_hazard
from backend.app.gis.pip import points_in_polygons, count_points_in_polygons
from backend.app.gis.exposure import calculate_hazard_exposure, calculate_habitation_exposure
from backend.app.gis.accessibility import calculate_site_accessibility
from backend.app.gis.proximity import calculate_relocation_proximity, filter_safe_relocation_sites
from backend.app.gis.raster_dem import calculate_slope, extract_habitation_terrain_stats
from backend.app.gis.hazard_combination import combine_hazard_layers


class GISEngine:
    """Unified Facade for Disaster Management Geospatial Operations."""

    @staticmethod
    def calculate_hazard_exposure(
        habitations_gdf: gpd.GeoDataFrame,
        hazard_zones_gdf: gpd.GeoDataFrame,
        hazard_types: Optional[List[str]] = None,
        min_severity: Optional[str] = None,
        habitation_id_col: str = "id",
    ) -> gpd.GeoDataFrame:
        """Calculate geometric intersection and exposure score between habitations and hazard zones."""
        return calculate_hazard_exposure(
            habitations_gdf,
            hazard_zones_gdf,
            hazard_types=hazard_types,
            min_severity=min_severity,
            habitation_id_col=habitation_id_col,
        )

    @staticmethod
    def calculate_habitation_exposure(
        habitations_gdf: gpd.GeoDataFrame,
        hazard_zones_gdf: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """Comprehensive multi-hazard exposure assessment with per-hazard breakdown."""
        return calculate_habitation_exposure(habitations_gdf, hazard_zones_gdf)

    @staticmethod
    def calculate_distance_to_hazard(
        target_gdf: gpd.GeoDataFrame,
        hazard_gdf: gpd.GeoDataFrame,
        hazard_type: Optional[str] = None,
        max_search_distance_meters: Optional[float] = None,
    ) -> gpd.GeoDataFrame:
        """Calculate distance in meters from each target feature to the nearest hazard boundary."""
        return calculate_distance_to_hazard(
            target_gdf,
            hazard_gdf,
            hazard_type=hazard_type,
            max_search_distance_meters=max_search_distance_meters,
        )

    @staticmethod
    def calculate_slope(
        dem_source: Union[str, Path, DatasetReader, np.ndarray],
        cell_size_x: float = 30.0,
        cell_size_y: float = 30.0,
        nodata: Optional[float] = None,
        method: str = "horn",
    ) -> Tuple[np.ndarray, Optional[Any]]:
        """Calculate terrain slope in degrees (0°-90°) from raster DEM."""
        return calculate_slope(
            dem_source,
            cell_size_x=cell_size_x,
            cell_size_y=cell_size_y,
            nodata=nodata,
            method=method,
        )

    @staticmethod
    def calculate_site_accessibility(
        sites_gdf: gpd.GeoDataFrame,
        roads_gdf: gpd.GeoDataFrame,
        max_acceptable_distance_meters: float = 1500.0,
        catchment_radius_meters: float = 500.0,
        site_id_col: str = "id",
    ) -> gpd.GeoDataFrame:
        """Calculate road network accessibility and distance for habitations or relocation sites."""
        return calculate_site_accessibility(
            sites_gdf,
            roads_gdf,
            max_acceptable_distance_meters=max_acceptable_distance_meters,
            catchment_radius_meters=catchment_radius_meters,
            site_id_col=site_id_col,
        )

    @staticmethod
    def combine_hazard_layers(
        hazard_layers: Dict[str, gpd.GeoDataFrame],
        weights: Optional[Dict[str, float]] = None,
        target_crs: Optional[str] = None,
    ) -> gpd.GeoDataFrame:
        """Combine multiple hazard layers into a unified multi-hazard risk layer."""
        return combine_hazard_layers(
            hazard_layers,
            weights=weights,
            target_crs=target_crs,
        )

    @staticmethod
    def create_buffer(
        gdf: gpd.GeoDataFrame,
        distance_meters: float,
        dissolve: bool = False,
        metric_crs: Optional[str] = None,
    ) -> gpd.GeoDataFrame:
        """Create a metric buffer with distance guaranteed in meters."""
        return create_buffer(
            gdf,
            distance_meters=distance_meters,
            dissolve=dissolve,
            metric_crs=metric_crs,
        )

    @staticmethod
    def spatial_intersection(
        gdf_a: gpd.GeoDataFrame,
        gdf_b: gpd.GeoDataFrame,
        keep_geom_type: Optional[str] = "Polygon",
    ) -> gpd.GeoDataFrame:
        """Perform spatial intersection between two layers with CRS harmonization."""
        return spatial_intersection(gdf_a, gdf_b, keep_geom_type=keep_geom_type)

    @staticmethod
    def calculate_relocation_proximity(
        habitations_gdf: gpd.GeoDataFrame,
        relocation_sites_gdf: gpd.GeoDataFrame,
        hazard_zones_gdf: Optional[gpd.GeoDataFrame] = None,
        max_distance_meters: float = 35000.0,
        min_capacity: int = 0,
    ) -> pd.DataFrame:
        """Find and rank candidate relocation parcels based on distance and capacity."""
        return calculate_relocation_proximity(
            habitations_gdf,
            relocation_sites_gdf,
            hazard_zones_gdf=hazard_zones_gdf,
            max_distance_meters=max_distance_meters,
            min_capacity=min_capacity,
        )
