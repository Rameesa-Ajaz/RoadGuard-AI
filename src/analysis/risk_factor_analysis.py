"""
Statistical risk factor analysis for Pakistan traffic data.
"""
import pandas as pd
import numpy as np
from scipy import stats
from loguru import logger


class RiskFactorAnalyzer:
    def __init__(self):
        self.factor_importance = {}

    def analyze_correlations(self, df: pd.DataFrame, target_col: str = 'risk_score') -> pd.DataFrame:
        """Analyze correlations between features and risk."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlations = df[numeric_cols].corr()[target_col].drop(target_col, errors='ignore')
        correlations = correlations.sort_values(ascending=False)

        logger.info(f"Analyzed correlations for {len(correlations)} features")
        return correlations.to_frame('correlation_with_risk')

    def chi_square_test(self, df: pd.DataFrame, feature: str, target: str) -> dict:
        """Perform chi-square test for categorical features."""
        contingency = pd.crosstab(df[feature], df[target])
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

        return {
            'feature': feature,
            'chi2': chi2,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'degrees_of_freedom': dof
        }

    def provincial_comparison(self, accident_data: dict) -> pd.DataFrame:
        """Compare accident statistics across provinces."""
        provinces = accident_data.get('province_breakdown', {})

        rows = []
        for province, data in provinces.items():
            accidents = data.get('accidents', 0)
            fatalities = data.get('fatalities', 0)
            fatality_rate = (fatalities / accidents * 100000) if accidents > 0 else 0

            rows.append({
                'province': province,
                'total_accidents': accidents,
                'fatalities': fatalities,
                'fatality_rate_per_100k': round(fatality_rate, 2)
            })

        df = pd.DataFrame(rows)
        return df.sort_values('fatality_rate_per_100k', ascending=False)
