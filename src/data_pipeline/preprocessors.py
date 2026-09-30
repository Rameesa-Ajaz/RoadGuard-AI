"""
Data preprocessing for Pakistan traffic datasets.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from loguru import logger


class PakistanDataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()

    def clean_traffic_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess traffic data."""
        df = df.copy()

        # Handle missing values with sensible defaults for Pakistan
        df = df.fillna({
            'speed_limit_kmh': 50,
            'num_lanes': 2,
            'road_curvature': 0.5,
            'congestion_multiplier': 1.0,
            'distance_km': df['distance_km'].median() if 'distance_km' in df.columns else 3.0
        })

        # Remove outliers (Pakistan speed limits typically 20-120 km/h)
        df = df[df['speed_limit_kmh'] <= 120]
        df = df[df['speed_limit_kmh'] >= 20]
        df = df[df['num_lanes'] <= 6]
        df = df[df['num_lanes'] >= 1]

        logger.info(f"Cleaned traffic data: {len(df)} records remaining")
        return df

    def create_risk_labels(self, df: pd.DataFrame) -> np.ndarray:
        """Create risk labels from features based on Pakistan accident data patterns."""
        risk_score = np.zeros(len(df))

        # Speed risk (higher speed = higher risk)
        risk_score += (df['speed_limit_kmh'] / 120) * 20

        # Congestion risk (extreme congestion increases accident risk)
        congestion = df['congestion_multiplier'].clip(0.5, 3.0)
        risk_score += congestion * 15

        # Road type risk
        road_risk = {'Highway': 20, 'Arterial': 15, 'Local': 5, 'Residential': 3}
        risk_score += df['road_type'].map(road_risk).fillna(10)

        # Weather risk
        weather_risk = {'Rain': 20, 'Fog': 30, 'Clear': 5, 'Dust': 25, 'Storm': 35}
        risk_score += df['weather_condition'].map(weather_risk).fillna(10)

        # Construction zone risk
        if 'is_construction' in df.columns:
            risk_score += df['is_construction'].astype(int) * 15

        return np.clip(risk_score, 0, 100)
