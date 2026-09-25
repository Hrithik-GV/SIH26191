# React Frontend — SIH 2026 Problem Statement 26191

Interactive GIS and analytical dashboard for Hazard Red Zone mapping, carrying capacity calculations, and relocation urgency prioritization.

## Tech Stack
- **Framework**: React 19 + Vite 6
- **Styling**: Tailwind CSS v4 (Light civic theme)
- **Map & Spatial Viz**: MapLibre GL JS
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Project Structure
```
frontend/
├── src/
│   ├── assets/       # Static branding assets & icons
│   ├── services/     # Axios API client, interceptors & endpoint helpers
│   ├── App.jsx       # Connectivity dashboard & layout
│   ├── index.css     # Tailwind v4 directives & light theme styling
│   └── main.jsx      # React DOM bootstrap
├── index.html        # HTML5 entrypoint with Google Fonts
├── vite.config.js    # Vite configuration with React and Tailwind plugins
└── package.json
```

## Quick Start (Local Development)

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
```
Ensure `VITE_API_BASE_URL` points to `http://localhost:8000/api/v1`.

### 3. Run Dev Server
```bash
npm run dev
```
The application will launch at `http://localhost:5173`.

### 4. Production Build
```bash
npm run build
npm run preview
```
