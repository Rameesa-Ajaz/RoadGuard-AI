"""
Feature engineering for Pakistan traffic risk analysis.
"""
import pandas as pd
import numpy as np
from loguru import logger


class PakistanFeatureEngineer:
    def create_features(self, traffic_data, surface_data, accident_data, challan_data):
        """Create comprehensive risk features from multiple data sources."""
        features = pd.DataFrame()
        n_samples = len(traffic_data)

        # Infrastructure features
        features['infrastructure_score'] = self._calc_infrastructure_score(surface_data, n_samples)

        # Traffic features
        features['traffic_flow'] = traffic_data['congestion_multiplier'].values * 1000
        features['avg_speed'] = (
            traffic_data['speed_limit_kmh'].values * 
            (1 - traffic_data['congestion_multiplier'].values * 0.3)
        ).clip(5, 120)

        # Control features
        features['signal_efficiency'] = traffic_data['has_signal'].astype(int).values * 75 + 25

        # Divergence (lane change chaos indicator)
        features['divergence_rate'] = traffic_data['road_curvature'].values * 50

        # Road management efficiency
        features['root_efficiency'] = 100 - traffic_data['road_curvature'].values * 30

        # Enforcement indicator
        features['challan_ratio'] = self._calc_challan_ratio(challan_data, n_samples)

        # Historical accident risk proxy
        features['accident_risk'] = self._calc_accident_risk(accident_data, n_samples)

        logger.info(f"Engineered {len(features.columns)} features for {n_samples} records")
        return features

    def _calc_infrastructure_score(self, surface_data, n_samples):
        """Calculate infrastructure score from surface data."""
        if len(surface_data) > 0 and 'pred_class' in surface_data.columns:
            # Map surface class to score
            surface_scores = surface_data['pred_class'].map({
                'paved': 85, 'unpaved': 30, 'concrete': 90, 'asphalt': 88
            }).fillna(50)
            # Repeat or sample to match n_samples
            if len(surface_scores) >= n_samples:
                return surface_scores.iloc[:n_samples].values
            else:
                return np.resize(surface_scores.values, n_samples)
        return np.random.uniform(30, 90, n_samples)

    def _calc_challan_ratio(self, challan_data, n_samples):
        """Calculate enforcement ratio from challan data."""
        # Use Karachi 2026 average as proxy
        karachi_vals = challan_data.get('Karachi_2026', {})
        if karachi_vals:
            avg_challans = sum(karachi_vals.values()) / len(karachi_vals)
            # Normalize to a ratio scale (approximate)
            ratio = min(avg_challans / 10000, 25)
            return np.full(n_samples, ratio)
        return np.random.uniform(3, 25, n_samples)

    def _calc_accident_risk(self, accident_data, n_samples):
        """Calculate historical accident risk proxy."""
        total = accident_data.get('total_accidents_2019_2024', 2500000)
        fatalities = accident_data.get('fatalities', 70600)
        # Fatality rate per 1000 accidents
        fatality_rate = (fatalities / total) * 1000 if total > 0 else 28
        # Normalize to 0-100 scale
        risk = min(fatality_rate * 2, 80)
        return np.full(n_samples, risk) + np.random.normal(0, 5, n_samples)
