# SIH 2026 — Problem Statement 26191
# Intelligent Identification of Hazard-Based Red Zones, Carrying Capacity Assessment, and Immediate Relocation Needs for Vulnerable Habitations

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?style=flat&logo=github)](https://github.com/Hrithik-GV/SIH26191)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_19-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Bundler-Vite_6-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/CSS-Tailwind_v4-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL_16-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![PostGIS](https://img.shields.io/badge/GIS-PostGIS_3.4-5B8A3C?style=flat)](https://postgis.net/)
[![Docker](https://img.shields.io/badge/Containers-Docker_Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

---

## 📌 Problem Overview

In disaster-prone terrains (landslides, flash floods, seismic faultlines), vulnerable human habitations face acute existential hazards. 

This platform provides:
1. **Multi-Hazard Red Zone Delineation**: Combining DEM terrain slope, hydrological flow accumulation, seismic vulnerability, and rainfall intensity.
2. **Carrying Capacity Assessment**: Computing structural, ecological, and civil infrastructure safety limits for settlements.
3. **Immediate Relocation Engine**: Multi-criteria prioritization model scoring habitations by risk exposure, evacuation route accessibility, and shelter proximity.

---

## 🏗️ Architecture & Technology Stack

```text
┌────────────────────────────────────────────────────────┐
│                   React 19 Frontend                    │
│    Vite • Tailwind CSS v4 • MapLibre GL • Recharts     │
└───────────────────────────┬────────────────────────────┘
                            │ REST / GeoJSON
                            ▼
┌────────────────────────────────────────────────────────┐
│                  FastAPI Backend Core                  │
│    Pydantic v2 • SQLAlchemy 2.0 • CORS • Diagnostics   │
└─────────────┬────────────────────────────┬─────────────┘
              │ PostGIS Queries            │ Spatial Analytics
              ▼                            ▼
┌───────────────────────────┐ ┌──────────────────────────┐
│   PostgreSQL + PostGIS    │ │     GIS & ML Layer       │
│ Spatial Index (GiST)      │ │ GeoPandas • Shapely      │
│ Vector Polygons & Rasters │ │ Rasterio • Scikit-learn  │
│                           │ │ XGBoost • Pandas • NumPy │
└───────────────────────────┘ └──────────────────────────┘
```

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 19, Vite, Tailwind CSS, MapLibre GL JS, Recharts, Axios | Interactive hazard maps, civic light theme UI, demographic graphs, health dashboard |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 | Async REST API, CORS middleware, centralized exception handling, database pooling |
| **Database** | PostgreSQL 16 + PostGIS 3.4 | Geospatial storage for hazard zones, buffers, vulnerable habitations |
| **GIS** | GeoPandas, Shapely, Rasterio, PyProj | Raster terrain processing, DEM slope extraction, polygon intersections |
| **AI/ML** | Scikit-learn, XGBoost, Pandas, NumPy | Vulnerability scoring models, priority relocation ranking algorithms |
| **Infrastructure** | Docker, Docker Compose, NGINX | Multi-container orchestration and automated service readiness |

---

## 📁 Monorepo Structure

```text
SIH26191/
├── frontend/                     # React 19 + Vite + Tailwind application
│   ├── src/
│   │   ├── services/api.js       # Axios client and connectivity helpers
│   │   ├── App.jsx               # Health monitoring and architecture view
│   │   ├── index.css             # Tailwind v4 directives & light theme styles
│   │   └── main.jsx              # Application bootstrap
│   ├── package.json              # Frontend dependencies
│   ├── vite.config.js            # Vite bundler configuration
│   └── .env.example              # Frontend environment template
│
├── backend/                      # FastAPI Python application
│   ├── app/
│   │   ├── api/v1/endpoints/     # Versioned endpoints (health, ping, etc.)
│   │   ├── core/                 # Config (BaseSettings), structured logging, exceptions
│   │   ├── db/                   # SQLAlchemy engine, session maker, PostGIS ping
│   │   ├── schemas/              # Pydantic validation schemas
│   │   └── main.py               # FastAPI application factory & CORS setup
│   ├── tests/                    # Pytest test suite
│   ├── requirements.txt          # Core FastAPI & Database dependencies
│   ├── requirements-gis-ml.txt   # GIS & ML dependencies (GeoPandas, XGBoost)
│   ├── README.md                 # Backend documentation
│   └── .env.example              # Backend environment template
│
├── data/                         # Geospatial and raster repository
│   ├── raw/                      # Satellite data, raw DEM rasters (.tif)
│   ├── processed/                # Normalized polygon layers
│   ├── geojson/                  # Optimized GeoJSON for MapLibre GL
│   └── raster/                   # Inundation grids, slope maps
│
├── ml/                           # AI/ML models and pipelines
│   ├── models/                   # Serialized model weights (.joblib, .pkl)
│   ├── training/                 # Model training and hyperparameter tuning
│   ├── features/                 # Spatial and demographic feature engineering
│   └── notebooks/                # Exploratory data analysis notebooks
│
├── docker/                       # Container definitions
│   ├── Dockerfile.backend        # Python 3.11 with GDAL, GEOS, and PROJ
│   ├── Dockerfile.frontend       # Multi-stage Node 22 build with NGINX
│   ├── nginx.conf                # NGINX reverse proxy & SPA router
│   └── init-db.sql               # PostGIS extension initialization script
│
├── docs/                         # Engineering & schema documentation
│   ├── architecture.md           # Architectural blueprints & layer responsibilities
│   └── README.md
│
├── docker-compose.yml            # Multi-service composition (db, backend, frontend)
├── pytest.ini                    # Root pytest configuration with pythonpath
├── .env.example                  # Root global environment template
├── .gitignore                    # Full-stack git ignore rules
└── README.md                     # Monorepo documentation
```

---

## 🚀 Quick Start Guide

### Option A: Using Docker Compose (Recommended)

Start the entire full-stack ecosystem (PostGIS Database + FastAPI Backend + React NGINX Frontend) with a single command:

```bash
# 1. Clone the repository
git clone https://github.com/Hrithik-GV/SIH26191.git
cd SIH26191

# 2. Start all services
docker compose up --build
```

**Service Endpoints:**
- **Frontend Web UI**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Root Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Interactive Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **PostgreSQL / PostGIS Port**: `localhost:5432`

To stop the containers:
```bash
docker compose down
```

---

### Option B: Local Development (Without Docker)

#### 1. Backend Setup

**Prerequisites:** Python 3.11+ installed.

```bash
# Navigate to backend directory or root
cd SIH26191

# Create and activate virtual environment
python -m venv backend/.venv

# On Windows:
.\backend\.venv\Scripts\Activate.ps1

# On Linux/macOS:
source backend/.venv/bin/activate

# Install core dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# (Optional) For GIS and ML pipeline support:
# pip install -r backend/requirements-gis-ml.txt

# Run the test suite
pytest

# Launch FastAPI development server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be accessible at [http://localhost:8000](http://localhost:8000).

#### 2. Frontend Setup

**Prerequisites:** Node.js 20+ and npm installed.

```bash
# In a new terminal window:
cd SIH26191/frontend

# Install frontend dependencies
npm install

# Start Vite development server
npm run dev
```

Frontend will be accessible at [http://localhost:5173](http://localhost:5173).

---

## 🔍 Health Check & Diagnostic Endpoints

The backend provides built-in system telemetry:

### 1. Root Health Check (`GET /health`)
Response Schema:
```json
{
  "status": "healthy",
  "app_name": "SIH 2026 - Disaster Risk & Relocation Assessment",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2026-09-25T06:55:00.000000+00:00",
  "database": {
    "connected": true,
    "latency_ms": 1.45,
    "postgis_version": "POSTGIS=\"3.4.2\" [EXTENSION] ...",
    "detail": "Database connection healthy"
  },
  "services": {
    "api": "operational",
    "gis_layer": "configured",
    "ml_layer": "configured"
  }
}
```

### 2. Lightweight Ping (`GET /api/v1/ping`)
```json
{
  "ping": "pong",
  "timestamp": "2026-09-25T06:55:00.000000+00:00",
  "status": "online"
}
```

---

## 🎨 Design System: Light Theme

In strict adherence to project specifications:
- **Theme**: Crisp Light Civic / Emergency Response Theme.
- **Background**: Neutral `#f8fafc` (Slate-50) and `#ffffff`.
- **Accents**: Emergency Crimson (`#dc2626`), Amber Warning (`#d97706`), Operational Emerald (`#059669`), and Deep Slate typography (`#0f172a`).
- **Dark Mode / AI Colors**: Dark mode and synthetic purple/dark blue gradients have been completely excluded in favor of clean, professional, government-grade disaster dashboard aesthetics.

---

## 🧪 Testing & Verification

Run the automated backend test suite:
```bash
pytest backend/tests
```

Run frontend production build verification:
```bash
cd frontend && npm run build
```

---

## 📄 License & Hackathon Submission

Developed for **Smart India Hackathon (SIH) 2026** — Problem Statement ID: **26191**.
GitHub Repository: [https://github.com/Hrithik-GV/SIH26191](https://github.com/Hrithik-GV/SIH26191)
