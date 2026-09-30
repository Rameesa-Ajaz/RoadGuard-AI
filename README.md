# 🚦 Smart Traffic Risk & Mitigation System - Pakistan Edition

A complete AI-powered traffic safety analysis system using publicly available Pakistan data.

## Features
- ✅ Risk analysis using Pakistan traffic data
- ✅ Explainable AI (causal + SHAP explanations)
- ✅ Route planning with risk-aware suggestions
- ✅ No CCTV/IoT required - uses public datasets
- ✅ Interactive Streamlit dashboard
- ✅ FastAPI backend with health checks
- ✅ SQLite database persistence
- ✅ Docker support

## Quick Start

### Option 1: Local Python

```bash
# 1. Clone and setup
cd smart-traffic-system-pakistan
cp .env.example .env
pip install -r requirements.txt

# 2. Train models (REQUIRED before API)
python scripts/run_pipeline.py

# 3. Start API
uvicorn src.api.main:app --reload --port 8000

# 4. Start Dashboard (new terminal)
streamlit run dashboard/app.py
```

### Option 2: Docker

```bash
# Build and run everything
docker-compose up --build

# API: http://localhost:8000
# Dashboard: http://localhost:8501
```

## Project Structure

```
smart-traffic-system-pakistan/
├── requirements.txt
├── pyproject.toml
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.dashboard
├── .env.example
├── .gitignore
├── README.md
│
├── config/
│   ├── settings.py
│   └── data_sources.yaml
│
├── src/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── crud.py
│   ├── data_pipeline/
│   │   ├── __init__.py
│   │   ├── downloaders.py
│   │   ├── preprocessors.py
│   │   └── feature_engineering.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── traffic_flow_predictor.py
│   │   ├── accident_predictor.py
│   │   └── train_models.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── risk_factor_analysis.py
│   │   └── spatial_analysis.py
│   ├── explanation/
│   │   ├── __init__.py
│   │   ├── causal_analyzer.py
│   │   └── explanation_generator.py
│   ├── recommendation/
│   │   ├── __init__.py
│   │   ├── route_optimizer.py
│   │   └── decision_engine.py
│   └── api/
│       ├── __init__.py
│       └── main.py
│
├── dashboard/
│   ├── __init__.py
│   ├── app.py
│   └── pages/
│       ├── __init__.py
│       ├── 1_Overview.py
│       ├── 2_Road_Analysis.py
│       └── 3_Explanations.py
│
├── scripts/
│   ├── download_all_data.py
│   └── run_pipeline.py
│
├── notebooks/
│   └── sample_analysis.ipynb
│
└── tests/
    └── test_pipeline.py
```

## Data Sources
- LahoreTrafficData (Hugging Face)
- Pakistan Road Surface (HDX)
- Rescue 1122 Accident Reports
- E-Challan Statistics
- OpenStreetMap Pakistan

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
OPENWEATHER_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here
HUGGINGFACE_TOKEN=your_token_here
```

Set `DATA_MODE=mock` for demo without real data, or `DATA_MODE=live` for production.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | System info |
| `/health` | GET | Health check |
| `/analyze` | POST | Analyze road risk |
| `/explain/{road_id}` | GET | SHAP explanation |
| `/dashboard/summary` | GET | Dashboard stats |
| `/routes/compare` | GET | Compare routes |

## Testing

```bash
pytest tests/test_pipeline.py -v
```

## License
MIT
