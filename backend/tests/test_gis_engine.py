"""Comprehensive unit test suite for the SIH 2026 GIS Processing Engine.

Validates:
1. Coordinate Reference System (CRS) management, UTM auto-detection, and error handling.
2. Geometry sanitization, OGC validity checks, and self-intersecting polygon repair.
3. Metric buffer generation (guaranteeing buffers are in meters, never degrees).
4. Spatial intersection, area overlap, and percentage calculations.
5. Distance calculations and distance-to-hazard evaluations.
6. Point-in-polygon checks and count aggregations.
7. Habitation hazard exposure assessment for flood, landslide, cloudburst, and multi-hazard.
8. Road network accessibility and connectivity scoring.
9. Relocation-site proximity ranking and hazard avoidance filtering.
10. Raster DEM slope processing using Horn's gradient formula and in-memory GeoTIFFs.
11. Multi-hazard layer synthesis and compound risk index calculation.
"""

import math
import numpy as np
import pytest
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

from backend.app.gis.exceptions import (
    GISEngineError,
    CRSCompatibilityError,
    InvalidGeometryError,
    RasterProcessingError,
)
from backend.app.gis.crs import (
    get_utm_epsg_for_lon_lat,
    validate_crs,
    ensure_crs,
    ensure_compatible_crs,
    to_metric_crs,
    estimate_optimal_metric_crs,
)
from backend.app.gis.geometry_utils import (
    validate_and_clean_geometries,
    calculate_area_sqm,
    clean_single_geometry,
)
from backend.app.gis.buffers import create_buffer, create_geometry_buffer
from backend.app.gis.intersection import spatial_intersection, calculate_polygon_overlap
from backend.app.gis.distance import calculate_pairwise_distances, calculate_distance_to_hazard
from backend.app.gis.pip import points_in_polygons, count_points_in_polygons
from backend.app.gis.exposure import calculate_hazard_exposure, calculate_habitation_exposure
from backend.app.gis.accessibility import calculate_site_accessibility
from backend.app.gis.proximity import calculate_relocation_proximity, filter_safe_relocation_sites
from backend.app.gis.raster_dem import calculate_slope, extract_habitation_terrain_stats
from backend.app.gis.hazard_combination import combine_hazard_layers, score_to_severity
from backend.app.gis.engine import GISEngine


# ============================================================================
# 1. CRS Tests
# ============================================================================

def test_utm_epsg_calculation_for_wayanad():
    """Verify optimal UTM zone calculation for Wayanad, Kerala (approx 76.13° E, 11.68° N)."""
    # 76.13° E is in UTM Zone 43 North -> EPSG:32643
    epsg = get_utm_epsg_for_lon_lat(76.13, 11.68)
    assert epsg == "EPSG:32643"


def test_utm_epsg_invalid_coordinates():
    """Test that out-of-bounds geographic coordinates raise ValueError."""
    with pytest.raises(ValueError):
        get_utm_epsg_for_lon_lat(200.0, 45.0)
    with pytest.raises(ValueError):
        get_utm_epsg_for_lon_lat(50.0, 95.0)


def test_validate_crs_raises_on_missing_crs():
    """Test that missing CRS triggers CRSCompatibilityError."""
    poly = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
    gdf_no_crs = gpd.GeoDataFrame(geometry=[poly])  # crs is None
    with pytest.raises(CRSCompatibilityError):
        validate_crs(gdf_no_crs, "TestLayer")


def test_ensure_compatible_crs_reprojects():
    """Test that two layers with different CRSes are harmonized to the same CRS."""
    pt_4326 = gpd.GeoDataFrame(geometry=[Point(76.13, 11.68)], crs="EPSG:4326")
    poly_3857 = gpd.GeoDataFrame(geometry=[Point(8474744, 1308354).buffer(1000)], crs="EPSG:3857")
    
    a, b = ensure_compatible_crs(pt_4326, poly_3857)
    assert a.crs == b.crs
    assert a.crs.to_string() == "EPSG:4326"


# ============================================================================
# 2. Geometry Validation & Auto-Repair Tests
# ============================================================================

def test_clean_self_intersecting_bowtie_polygon():
    """Test that an invalid self-intersecting 'bowtie' polygon is automatically repaired."""
    # Self-intersecting bowtie polygon
    bowtie = Polygon([(0, 0), (2, 2), (2, 0), (0, 2), (0, 0)])
    assert not bowtie.is_valid
    
    gdf = gpd.GeoDataFrame(geometry=[bowtie], crs="EPSG:4326")
    cleaned = validate_and_clean_geometries(gdf, repair=True)
    
    assert len(cleaned) == 1
    assert cleaned.geometry.iloc[0].is_valid


def test_clean_drops_empty_geometries():
    """Test that empty or null geometries are cleanly handled without crashing."""
    valid_poly = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
    empty_poly = Polygon()
    gdf = gpd.GeoDataFrame(geometry=[valid_poly, empty_poly, None], crs="EPSG:4326")
    
    cleaned = validate_and_clean_geometries(gdf, drop_empty=True)
    assert len(cleaned) == 1
    assert cleaned.geometry.iloc[0].is_valid


def test_calculate_area_sqm_in_meters():
    """Test that polygon area is computed in square meters even if input is in EPSG:4326."""
    # A 100m x 100m square in UTM Zone 43N (EPSG:32643) centered near Wayanad
    # In UTM meters: (600000, 1290000)
    utm_poly = Polygon([
        (600000, 1290000),
        (600000, 1290100),
        (600100, 1290100),
        (600100, 1290000),
        (600000, 1290000)
    ])
    gdf_utm = gpd.GeoDataFrame(geometry=[utm_poly], crs="EPSG:32643")
    
    # 100m * 100m = 10,000 sqm
    area_series = calculate_area_sqm(gdf_utm)
    assert pytest.approx(area_series.iloc[0], rel=1e-3) == 10000.0
    
    # Convert to EPSG:4326 and compute area again
    gdf_4326 = gdf_utm.to_crs("EPSG:4326")
    area_series_4326 = calculate_area_sqm(gdf_4326)
    # Even in 4326, the engine should project to metric and return ~10,000 sqm (not ~0.0000008 deg^2)
    assert pytest.approx(area_series_4326.iloc[0], rel=0.05) == 10000.0


# ============================================================================
# 3. Buffer Generation Tests
# ============================================================================

def test_metric_buffer_generation_radius():
    """Test that create_buffer generates buffers using meters, never degrees."""
    # Point in Wayanad (EPSG:4326)
    pt = Point(76.13, 11.68)
    gdf = gpd.GeoDataFrame(geometry=[pt], crs="EPSG:4326")
    
    # Generate 500m buffer
    buffered = create_buffer(gdf, distance_meters=500.0)
    
    assert len(buffered) == 1
    assert buffered.crs.to_string() == "EPSG:4326"
    assert buffered.geometry.iloc[0].geom_type in ["Polygon", "MultiPolygon"]
    
    # Calculate area of the 500m buffer: Area = pi * r^2 = pi * 500^2 ~ 785,398 sqm
    area_sqm = calculate_area_sqm(buffered).iloc[0]
    expected_area = math.pi * (500.0 ** 2)
    assert pytest.approx(area_sqm, rel=0.05) == expected_area


def test_buffer_dissolve():
    """Test that overlapping buffers dissolve into a single geometry when requested."""
    pt1 = Point(76.130, 11.680)
    pt2 = Point(76.131, 11.680)  # ~110m away
    gdf = gpd.GeoDataFrame(geometry=[pt1, pt2], crs="EPSG:4326")
    
    # 200m buffer causes them to heavily overlap
    buffered = create_buffer(gdf, distance_meters=200.0, dissolve=True)
    assert len(buffered) == 1


# ============================================================================
# 4. Spatial Intersection & Overlap Tests
# ============================================================================

def test_spatial_intersection_and_overlap_percentage():
    """Test exact area intersection and percentage overlap calculation."""
    # Use UTM 43N metric squares
    # Base box: (0,0) to (100, 100) -> Area 10,000 sqm
    base_box = Polygon([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)])
    base_gdf = gpd.GeoDataFrame({"id": ["base_1"], "geometry": [base_box]}, crs="EPSG:32643")
    
    # Overlay box covering half the base: (0, 0) to (50, 100) -> Area 5,000 sqm
    half_box = Polygon([(0, 0), (0, 100), (50, 100), (50, 0), (0, 0)])
    overlay_gdf = gpd.GeoDataFrame({"id": ["ov_1"], "geometry": [half_box]}, crs="EPSG:32643")
    
    result = calculate_polygon_overlap(base_gdf, overlay_gdf, base_id_col="id")
    
    assert len(result) == 1
    assert pytest.approx(result.iloc[0]["base_area_sqm"], rel=1e-2) == 10000.0
    assert pytest.approx(result.iloc[0]["overlap_area_sqm"], rel=1e-2) == 5000.0
    assert pytest.approx(result.iloc[0]["overlap_percentage"], rel=1e-2) == 50.0


# ============================================================================
# 5. Distance Calculations Tests
# ============================================================================

def test_calculate_distance_to_hazard():
    """Test distance to hazard boundary: 0.0m if inside, positive if outside."""
    # Hazard zone at (0,0)-(100,100)
    hazard_poly = Polygon([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)])
    hazard_gdf = gpd.GeoDataFrame({
        "id": ["hz_1"],
        "hazard_type": ["LANDSLIDE"],
        "severity": ["VERY_HIGH"],
        "geometry": [hazard_poly]
    }, crs="EPSG:32643")
    
    # Point 1 inside hazard: (50, 50)
    # Point 2 outside hazard: (150, 50) -> distance to right edge (x=100) is exactly 50m
    targets_gdf = gpd.GeoDataFrame({
        "id": ["pt_inside", "pt_outside"],
        "geometry": [Point(50, 50), Point(150, 50)]
    }, crs="EPSG:32643")
    
    evaluated = calculate_distance_to_hazard(targets_gdf, hazard_gdf)
    
    inside_row = evaluated[evaluated["id"] == "pt_inside"].iloc[0]
    outside_row = evaluated[evaluated["id"] == "pt_outside"].iloc[0]
    
    assert inside_row["distance_to_hazard_meters"] == 0.0
    assert inside_row["is_inside_hazard"] == True
    assert inside_row["nearest_hazard_type"] == "LANDSLIDE"
    
    assert outside_row["distance_to_hazard_meters"] == pytest.approx(50.0, abs=0.1)
    assert outside_row["is_inside_hazard"] == False


def test_pairwise_distances():
    """Test pairwise distance calculation between origins and destinations in meters."""
    orig = gpd.GeoDataFrame({"id": ["A"]}, geometry=[Point(0, 0)], crs="EPSG:32643")
    dest = gpd.GeoDataFrame({"id": ["B"]}, geometry=[Point(300, 400)], crs="EPSG:32643")
    
    # Pythagorean 3-4-5 triangle -> distance = 500m
    df = calculate_pairwise_distances(orig, dest, origin_id_col="id", dest_id_col="id")
    assert len(df) == 1
    assert df.iloc[0]["distance_meters"] == pytest.approx(500.0, rel=1e-3)
    assert df.iloc[0]["distance_km"] == pytest.approx(0.5, rel=1e-3)


# ============================================================================
# 6. Point-in-Polygon Tests
# ============================================================================

def test_point_in_polygon_and_counts():
    """Test point containment within polygons and aggregation counts."""
    poly = Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])
    poly_gdf = gpd.GeoDataFrame({"id": ["poly_1"]}, geometry=[poly], crs="EPSG:32643")
    
    pts = [Point(5, 5), Point(8, 8), Point(20, 20)]  # 2 inside, 1 outside
    pts_gdf = gpd.GeoDataFrame({"id": ["p1", "p2", "p3"]}, geometry=pts, crs="EPSG:32643")
    
    joined = points_in_polygons(pts_gdf, poly_gdf)
    assert joined.loc[joined["id"] == "p1", "is_contained"].iloc[0] == True
    assert joined.loc[joined["id"] == "p2", "is_contained"].iloc[0] == True
    assert joined.loc[joined["id"] == "p3", "is_contained"].iloc[0] == False
    
    counted = count_points_in_polygons(poly_gdf, pts_gdf)
    assert counted.iloc[0]["point_count"] == 2


# ============================================================================
# 7. Habitation Hazard Exposure Tests
# ============================================================================

def test_calculate_hazard_exposure_metrics():
    """Test habitation hazard exposure evaluation and critical threshold triggering."""
    hab_box = Polygon([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)])
    hab_gdf = gpd.GeoDataFrame({
        "id": ["hab_chooralmala"],
        "name": ["Chooralmala"],
        "geometry": [hab_box]
    }, crs="EPSG:32643")
    
    # 70% overlap with a VERY_HIGH severity landslide red zone
    hazard_box = Polygon([(0, 0), (0, 100), (70, 100), (70, 0), (0, 0)])
    hazard_gdf = gpd.GeoDataFrame({
        "id": ["hz_landslide_1"],
        "hazard_type": ["LANDSLIDE"],
        "severity": ["VERY_HIGH"],
        "geometry": [hazard_box]
    }, crs="EPSG:32643")
    
    exposure_df = calculate_hazard_exposure(hab_gdf, hazard_gdf)
    row = exposure_df.iloc[0]
    
    assert row["overlap_percentage"] == pytest.approx(70.0, abs=0.5)
    assert row["max_hazard_severity"] == "VERY_HIGH"
    assert row["is_critical_exposure"] == True
    assert row["exposure_score"] >= 75.0


def test_calculate_habitation_exposure_breakdown():
    """Test detailed breakdown per hazard type (Flood, Landslide, Rainfall)."""
    hab_box = Polygon([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)])
    hab_gdf = gpd.GeoDataFrame({"id": ["hab_1"], "geometry": [hab_box]}, crs="EPSG:32643")
    
    hz_flood = Polygon([(0, 0), (0, 100), (30, 100), (30, 0), (0, 0)])
    hz_ls = Polygon([(50, 0), (50, 100), (80, 100), (80, 0), (50, 0)])
    
    hazards_gdf = gpd.GeoDataFrame({
        "id": ["f1", "l1"],
        "hazard_type": ["FLOOD", "LANDSLIDE"],
        "severity": ["HIGH", "VERY_HIGH"],
        "geometry": [hz_flood, hz_ls]
    }, crs="EPSG:32643")
    
    result = calculate_habitation_exposure(hab_gdf, hazards_gdf)
    assert result.iloc[0]["flood_overlap_pct"] == pytest.approx(30.0, abs=0.5)
    assert result.iloc[0]["landslide_overlap_pct"] == pytest.approx(30.0, abs=0.5)


# ============================================================================
# 8. Road Accessibility Analysis Tests
# ============================================================================

def test_site_accessibility_score():
    """Test road accessibility distance and scoring."""
    # Road line running along x=0 from y=-500 to y=500
    road = LineString([(0, -500), (0, 500)])
    roads_gdf = gpd.GeoDataFrame({"id": ["nh_766"]}, geometry=[road], crs="EPSG:32643")
    
    # Site 1 close to road (50m away)
    # Site 2 far from road (2000m away, exceeds max threshold)
    sites_gdf = gpd.GeoDataFrame({
        "id": ["site_near", "site_far"],
        "geometry": [Point(50, 0), Point(2000, 0)]
    }, crs="EPSG:32643")
    
    access_df = calculate_site_accessibility(
        sites_gdf, roads_gdf, max_acceptable_distance_meters=1000.0, catchment_radius_meters=300.0
    )
    
    near = access_df[access_df["id"] == "site_near"].iloc[0]
    far = access_df[access_df["id"] == "site_far"].iloc[0]
    
    assert near["is_road_accessible"] == True
    assert near["distance_to_road_meters"] == pytest.approx(50.0, abs=0.1)
    assert near["road_accessibility_score"] > 80.0
    
    assert far["is_road_accessible"] == False
    assert far["road_accessibility_score"] == 0.0


# ============================================================================
# 9. Relocation Proximity & Hazard Avoidance Tests
# ============================================================================

def test_relocation_hazard_filtering_and_ranking():
    """Verify that candidate sites inside hazard zones are excluded and safe sites are ranked."""
    hab = gpd.GeoDataFrame({"id": ["hab_vulnerable"]}, geometry=[Point(0, 0)], crs="EPSG:32643")
    
    # Site A: 500m away, but inside a VERY_HIGH landslide red zone
    # Site B: 1500m away, in safe terrain with 250 capacity
    site_a = Point(500, 0)
    site_b = Point(1500, 0)
    sites_gdf = gpd.GeoDataFrame({
        "id": ["site_a_unsafe", "site_b_safe"],
        "name": ["Unsafe Site", "Safe Site"],
        "available_capacity": [200, 250],
        "geometry": [site_a, site_b]
    }, crs="EPSG:32643")
    
    hazard_poly = Polygon([(400, -100), (400, 100), (600, 100), (600, -100), (400, -100)])
    hazard_gdf = gpd.GeoDataFrame({
        "id": ["hz_severe"],
        "hazard_type": ["LANDSLIDE"],
        "severity": ["VERY_HIGH"],
        "geometry": [hazard_poly]
    }, crs="EPSG:32643")
    
    ranking = calculate_relocation_proximity(hab, sites_gdf, hazard_zones_gdf=hazard_gdf)
    
    # Only safe site B should remain
    assert len(ranking) == 1
    assert ranking.iloc[0]["site_id"] == "site_b_safe"
    assert ranking.iloc[0]["distance_meters"] == pytest.approx(1500.0, abs=0.5)


# ============================================================================
# 10. Raster DEM & Slope Calculation Tests
# ============================================================================

def test_calculate_slope_flat_and_inclined():
    """Test slope angle in degrees on synthetic terrain."""
    # Flat terrain: all cells = 100.0m -> slope should be 0.0°
    flat = np.full((10, 10), 100.0)
    slope_flat, _ = calculate_slope(flat, cell_size_x=30.0, cell_size_y=30.0)
    assert np.allclose(slope_flat, 0.0)
    
    # 45-degree slope in X: elevation increases by 30m every 30m cell (dz/dx = 1.0)
    # arctan(1.0) = 45 degrees
    x_coords = np.arange(10) * 30.0
    incline = np.tile(x_coords, (10, 1))
    slope_incline, _ = calculate_slope(incline, cell_size_x=30.0, cell_size_y=30.0)
    
    # Interior cells should be exactly 45.0 degrees
    interior = slope_incline[1:-1, 1:-1]
    assert np.allclose(interior, 45.0, atol=0.1)


def test_extract_habitation_terrain_stats_with_rasterio_memoryfile():
    """Test extraction of elevation and slope stats from an in-memory raster DEM."""
    # Create 50x50 elevation raster (1000m to 1500m elevation)
    width, height = 50, 50
    res = 30.0
    elev_array = np.linspace(1000, 1500, width * height, dtype=np.float32).reshape((height, width))
    
    transform = from_origin(600000, 1300000, res, res)
    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 1,
        "dtype": "float32",
        "crs": "EPSG:32643",
        "transform": transform,
        "nodata": -9999.0,
    }
    
    with MemoryFile() as memfile:
        with memfile.open(**profile) as dataset:
            dataset.write(elev_array, 1)
            
            # Habitation box in the middle of the raster
            hab_box = Polygon([(600300, 1298800), (600300, 1299400), (600900, 1299400), (600900, 1298800), (600300, 1298800)])
            hab_gdf = gpd.GeoDataFrame({"id": ["hab_mountain"]}, geometry=[hab_box], crs="EPSG:32643")
            
            stats_df = extract_habitation_terrain_stats(dataset, hab_gdf)
            
            assert len(stats_df) == 1
            row = stats_df.iloc[0]
            assert 1000.0 < row["elevation_mean"] < 1500.0
            assert row["slope_mean_deg"] > 0.0


# ============================================================================
# 11. Multi-Hazard Layer Combination Tests
# ============================================================================

def test_combine_hazard_layers_and_synergy():
    """Test synthesis of multiple hazard layers into a combined multi-hazard layer."""
    # Flood zone
    flood_box = Polygon([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)])
    flood_gdf = gpd.GeoDataFrame({
        "id": ["f1"],
        "severity": ["HIGH"],
        "geometry": [flood_box]
    }, crs="EPSG:32643")
    
    # Landslide zone overlapping half of the flood zone
    ls_box = Polygon([(50, 0), (50, 100), (150, 100), (150, 0), (50, 0)])
    ls_gdf = gpd.GeoDataFrame({
        "id": ["l1"],
        "severity": ["VERY_HIGH"],
        "geometry": [ls_box]
    }, crs="EPSG:32643")
    
    combined = combine_hazard_layers({"flood": flood_gdf, "landslide": ls_gdf})
    
    # Should contain individual hazard geometries and an intersection MULTI_HAZARD zone
    assert len(combined) >= 3
    multi_records = combined[combined["hazard_type"] == "MULTI_HAZARD"]
    assert len(multi_records) >= 1
    
    multi_row = multi_records.iloc[0]
    assert multi_row["is_multi_hazard"] == True
    assert "FLOOD" in multi_row["active_hazards"]
    assert "LANDSLIDE" in multi_row["active_hazards"]
    assert multi_row["composite_risk_score"] > 80.0
    assert multi_row["severity"] in ["CRITICAL", "HIGH"]


# ============================================================================
# 12. GISEngine Facade Tests
# ============================================================================

def test_gis_engine_facade_interface():
    """Test that GISEngine facade exposes all required entrypoints cleanly."""
    pt = Point(76.13, 11.68)
    gdf = gpd.GeoDataFrame(geometry=[pt], crs="EPSG:4326")
    
    buf = GISEngine.create_buffer(gdf, distance_meters=100.0)
    assert not buf.empty
    
    # Check severity mapping helper
    assert score_to_severity(95.0) == "CRITICAL"
    assert score_to_severity(70.0) == "HIGH"
    assert score_to_severity(45.0) == "MODERATE"
    assert score_to_severity(15.0) == "LOW"
