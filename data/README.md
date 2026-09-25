# GIS & Geospatial Data Repository

This directory contains spatial and tabular data used for hazard-based red zone mapping and carrying capacity estimation.

## Directory Structure:
- `raw/`: Raw geospatial files (satellite imagery, DEM, rainfall data, settlement shapefiles).
- `processed/`: Preprocessed and cleaned layers (clipped rasters, normalized vector polygons).
- `geojson/`: Exported GeoJSON datasets optimized for MapLibre GL frontend rendering.
- `raster/`: Digital Elevation Models (DEM), slope maps, flood inundation grids, and raster risk indices.

*Note: Raw spatial and raster binaries are excluded from version control via `.gitignore`.*
