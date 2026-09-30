"""
Application settings with environment variable support.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load .env file if present
load_dotenv()

BASE_DIR = Path(__file__).parent.parent

# Directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODEL_DIR = DATA_DIR / "models"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
for d in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODEL_DIR, OUTPUT_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DATA_MODE = os.getenv("DATA_MODE", "mock")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/traffic.db")

# API Keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:8501").split(",")]

# Dashboard
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8501"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOG_DIR / "app.log"))

# Configure loguru
logger.add(LOG_FILE, level=LOG_LEVEL, rotation="10 MB", retention="7 days")

# Data sources
DATA_SOURCES = {
    "lahore_traffic": {
        "name": "HaajraMumtaz/LahoreTrafficData",
        "type": "huggingface"
    },
    "road_surface": {
        "url": "https://data.humdata.org/dataset/pakistan-road-surface-data",
        "type": "hdx"
    }
}

# Model parameters
MODEL_CONFIG = {
    "lstm": {
        "sequence_length": 24,
        "hidden_size": 64,
        "num_layers": 2
    },
    "xgboost": {
        "n_estimators": 200,
        "max_depth": 8,
        "learning_rate": 0.1
    }
}

# Risk thresholds
RISK_THRESHOLDS = {
    "critical": 80,
    "high": 60,
    "moderate": 40,
    "low": 20
}
