# System Architecture

## Architectural Flow
```text
┌────────────────────────────────────────────────────────┐
│               Frontend Presentation Layer              │
│       React + Vite + Tailwind CSS + MapLibre GL        │
└───────────────────────────┬────────────────────────────┘
                            │ REST / GeoJSON / JSON
                            ▼
┌────────────────────────────────────────────────────────┐
│                  FastAPI Backend Core                  │
│       Pydantic Validation + SQLAlchemy ORM + Logging   │
└─────────────┬────────────────────────────┬─────────────┘
              │ PostGIS Queries            │ Spatial Analytics
              ▼                            ▼
┌───────────────────────────┐ ┌──────────────────────────┐
│   PostgreSQL + PostGIS    │ │   GIS & ML Engine        │
│ Vector & Attribute Stores │ │ GeoPandas, Shapely,      │
│ Spatial Index (GIST)      │ │ Rasterio, Scikit-learn,  │
│                           │ │ XGBoost                  │
└───────────────────────────┘ └──────────────────────────┘
```

## Layer Responsibilities
1. **Frontend**: Interactive hazard mapping (MapLibre GL JS), carrying capacity graphs (Recharts), relocation priority dashboard, light civic theme.
2. **FastAPI Backend**: API routing, CORS handling, authentication/authorization, data validation, database connection pooling.
3. **PostgreSQL / PostGIS**: Spatial persistence for hazard red zones, vulnerable habitation polygons, infrastructure buffers, and demographic metadata.
4. **GIS / ML Engine**: Multi-hazard risk raster processing (DEM slope, rainfall, flood contours) and relocation scoring algorithms.
