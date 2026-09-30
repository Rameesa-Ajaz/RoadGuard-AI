"""
Spatial analysis for traffic risk mapping.
"""
import pandas as pd
import numpy as np
from loguru import logger


class SpatialAnalyzer:
    def __init__(self):
        self.hotspots = []

    def identify_hotspots(self, df: pd.DataFrame, lat_col='lat', lon_col='lon', 
                         risk_col='risk_score', threshold=70) -> pd.DataFrame:
        """Identify high-risk spatial clusters."""
        hotspots = df[df[risk_col] >= threshold].copy()
        logger.info(f"Identified {len(hotspots)} risk hotspots (threshold={threshold})")
        return hotspots

    def generate_heat_map_data(self, df: pd.DataFrame, lat_col='lat', lon_col='lon',
                               risk_col='risk_score') -> list:
        """Generate data for folium heatmap."""
        if lat_col not in df.columns or lon_col not in df.columns:
            logger.warning("Lat/Lon columns not found. Cannot generate heatmap data.")
            return []

        heat_data = []
        for _, row in df.iterrows():
            heat_data.append([
                row[lat_col],
                row[lon_col],
                row[risk_col]
            ])
        return heat_data

    def calculate_spatial_risk_index(self, df: pd.DataFrame, grid_size=0.01) -> pd.DataFrame:
        """Calculate risk index for spatial grid cells."""
        # Simplified grid-based aggregation
        if 'lat' not in df.columns or 'lon' not in df.columns:
            return pd.DataFrame()

        df['lat_grid'] = (df['lat'] / grid_size).astype(int) * grid_size
        df['lon_grid'] = (df['lon'] / grid_size).astype(int) * grid_size

        grid_risk = df.groupby(['lat_grid', 'lon_grid']).agg({
            'risk_score': ['mean', 'max', 'count']
        }).reset_index()

        grid_risk.columns = ['lat_grid', 'lon_grid', 'avg_risk', 'max_risk', 'num_segments']
        return grid_risk
