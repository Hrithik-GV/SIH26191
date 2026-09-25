# FastAPI Backend — SIH 2026 Problem Statement 26191

High-performance asynchronous backend providing spatial query endpoints, risk computation interfaces, and PostGIS database connectors.

## Tech Stack
- **Framework**: FastAPI (Python 3.11+)
- **Validation**: Pydantic v2 & Pydantic-Settings
- **ORM & DB**: SQLAlchemy 2.0, GeoAlchemy2, PostgreSQL 16 + PostGIS 3.4
- **GIS Engine**: GeoPandas, Shapely, Rasterio
- **AI/ML Engine**: Scikit-Learn, XGBoost, Pandas, NumPy

## Folder Structure
```
backend/
├── app/
│   ├── api/v1/         # Versioned API routes & endpoints
│   ├── core/           # Configuration, logging, exception handlers
│   ├── db/             # SQLAlchemy engine, session maker & models
│   ├── models/         # Database ORM models
│   ├── schemas/        # Pydantic request/response schemas
│   ├── services/       # Business logic & GIS/ML service layers
│   └── main.py         # FastAPI application entrypoint & middleware
├── tests/              # Test suite (pytest)
├── requirements.txt    # Core API & database dependencies
└── requirements-gis-ml.txt # Geospatial and ML packages
```

## Quick Start (Local Development)

### 1. Create and Activate Virtual Environment
```bash
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Linux / macOS
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt

# (Optional for GIS/ML analysis):
# pip install -r requirements-gis-ml.txt
```

### 3. Setup Environment Variables
```bash
cp .env.example .env
```

### 4. Run Development Server
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **ReDoc Alternative Docs**: http://localhost:8000/redoc
- **Direct Health Check**: http://localhost:8000/health
