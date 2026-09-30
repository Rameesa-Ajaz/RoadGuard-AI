"""
Causal analysis using Bayesian Networks.
"""
import pandas as pd
import numpy as np
from loguru import logger


class CausalTrafficAnalyzer:
    def __init__(self):
        self.model = None
        self.inference = None
        self._define_structure()

    def _define_structure(self):
        """Define causal DAG structure."""
        try:
            from pgmpy.models import BayesianNetwork
            self.model = BayesianNetwork([
                ('Infrastructure', 'Divergence'),
                ('Infrastructure', 'Accident'),
                ('Flow', 'Divergence'),
                ('Flow', 'Accident'),
                ('ControlEfficiency', 'Flow'),
                ('ControlEfficiency', 'Accident'),
                ('Divergence', 'Accident'),
                ('Enforcement', 'ChallanRatio'),
                ('Enforcement', 'Accident'),
                ('ChallanRatio', 'Accident')
            ])
            logger.info("Causal structure defined")
        except ImportError:
            logger.warning("pgmpy not installed. Causal analysis will use heuristic fallback.")
            self.model = None

    def train_causal_model(self, df: pd.DataFrame):
        """Train Bayesian Network on discretized data."""
        if self.model is None:
            logger.warning("Causal model not available. Skipping training.")
            return

        try:
            from pgmpy.estimators import BayesianEstimator
            from pgmpy.inference import VariableElimination

            df_discrete = self.discretize_data(df)
            self.model.fit(df_discrete, estimator=BayesianEstimator)
            self.inference = VariableElimination(self.model)
            logger.info("Causal model trained")
        except Exception as e:
            logger.error(f"Failed to train causal model: {e}")

    def discretize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Discretize continuous variables for Bayesian Network."""
        df_copy = df.copy()

        if 'infrastructure_score' in df_copy.columns:
            df_copy['Infrastructure'] = pd.cut(
                df_copy['infrastructure_score'],
                bins=[0, 40, 70, 100],
                labels=['poor', 'moderate', 'good']
            )

        if 'traffic_flow' in df_copy.columns:
            df_copy['Flow'] = pd.cut(
                df_copy['traffic_flow'],
                bins=[0, 800, 1500, 3000],
                labels=['low', 'moderate', 'high']
            )

        if 'signal_efficiency' in df_copy.columns:
            df_copy['ControlEfficiency'] = pd.cut(
                df_copy['signal_efficiency'],
                bins=[0, 50, 75, 100],
                labels=['poor', 'moderate', 'good']
            )

        if 'divergence_rate' in df_copy.columns:
            df_copy['Divergence'] = pd.cut(
                df_copy['divergence_rate'],
                bins=[0, 20, 40, 100],
                labels=['low', 'moderate', 'high']
            )

        if 'challan_ratio' in df_copy.columns:
            df_copy['ChallanRatio'] = pd.cut(
                df_copy['challan_ratio'],
                bins=[0, 5, 15, 30],
                labels=['low', 'moderate', 'high']
            )

        return df_copy

    def trace_causal_chain(self, features: dict) -> list:
        """Trace causal chain leading to accident risk."""
        # Heuristic causal chain based on feature values
        chain = []

        infra = features.get('infrastructure_score', 50)
        if infra < 50:
            chain.append({'factor': 'Infrastructure', 'contribution': 35, 'state': 'poor'})

        div = features.get('divergence_rate', 20)
        if div > 30:
            chain.append({'factor': 'Divergence', 'contribution': 28, 'state': 'high'})

        challan = features.get('challan_ratio', 10)
        if challan < 5:
            chain.append({'factor': 'ChallanRatio', 'contribution': 20, 'state': 'low'})

        flow = features.get('traffic_flow', 1000)
        if flow > 1500:
            chain.append({'factor': 'Flow', 'contribution': 12, 'state': 'high'})

        control = features.get('signal_efficiency', 60)
        if control < 50:
            chain.append({'factor': 'ControlEfficiency', 'contribution': 5, 'state': 'poor'})

        if not chain:
            chain = [{'factor': 'General Conditions', 'contribution': 100, 'state': 'moderate'}]

        return chain

    def get_counterfactual(self, features: dict, target: str, value: str) -> dict:
        """Compute counterfactual: what if target factor was improved?"""
        current_risk = self._estimate_risk(features)

        # Simulate improvement
        improved = features.copy()
        if target == 'Infrastructure':
            improved['infrastructure_score'] = 85
        elif target == 'Divergence':
            improved['divergence_rate'] = 10
        elif target == 'ChallanRatio':
            improved['challan_ratio'] = 20
        elif target == 'ControlEfficiency':
            improved['signal_efficiency'] = 90

        new_risk = self._estimate_risk(improved)
        reduction = ((current_risk - new_risk) / current_risk * 100) if current_risk > 0 else 0

        return {
            'target_factor': target,
            'current_value': features.get(target.lower(), 'moderate'),
            'suggested_value': value,
            'original_risk': round(current_risk, 2),
            'counterfactual_risk': round(new_risk, 2),
            'percentage_reduction': round(reduction, 1)
        }

    def _estimate_risk(self, features: dict) -> float:
        """Simple heuristic risk estimation for counterfactuals."""
        risk = 30
        risk += max(0, (100 - features.get('infrastructure_score', 50)) * 0.35)
        risk += features.get('divergence_rate', 20) * 0.5
        risk += max(0, (20 - features.get('challan_ratio', 10)) * 1.5)
        risk += features.get('traffic_flow', 1000) / 100
        return min(risk, 100)
