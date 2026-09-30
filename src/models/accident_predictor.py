"""
Accident prediction using XGBoost with SHAP explanations.
"""
import xgboost as xgb
import shap
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from loguru import logger
from config.settings import MODEL_DIR


class AccidentPredictor:
    def __init__(self, model_path=None):
        self.model_path = model_path or MODEL_DIR / "accident_xgb.pkl"
        self.model = None
        self.explainer = None

    def train(self, X: pd.DataFrame, y: pd.Series):
        """Train XGBoost model."""
        self.model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        self.model.fit(X, y)

        # Save
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        logger.info(f"Accident predictor trained and saved to {self.model_path}")

        # Initialize SHAP explainer
        self._init_explainer(X)
        return self.model

    def _init_explainer(self, X_background=None):
        """Initialize SHAP TreeExplainer."""
        if self.model is None:
            return
        try:
            self.explainer = shap.TreeExplainer(self.model)
            logger.info("SHAP explainer initialized")
        except Exception as e:
            logger.warning(f"Could not initialize SHAP explainer: {e}")

    def predict_risk(self, features: dict) -> dict:
        """Predict accident risk from feature dictionary."""
        if self.model is None:
            self.load()

        # Convert dict to DataFrame (single row)
        df = pd.DataFrame([features])

        # Ensure column order matches training
        expected_cols = self.model.get_booster().feature_names
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0
        df = df[expected_cols]

        prob = self.model.predict_proba(df)[0, 1]

        if prob < 0.3:
            level = 'low'
        elif prob < 0.6:
            level = 'moderate'
        elif prob < 0.8:
            level = 'high'
        else:
            level = 'critical'

        return {
            'probability': float(prob),
            'risk_level': level,
            'risk_score': float(prob * 100)
        }

    def explain_prediction(self, features: dict) -> dict:
        """Generate SHAP explanation for a prediction."""
        if self.model is None:
            self.load()
        if self.explainer is None:
            self._init_explainer()

        df = pd.DataFrame([features])
        expected_cols = self.model.get_booster().feature_names
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0
        df = df[expected_cols]

        shap_values = self.explainer.shap_values(df)

        # Get feature contributions
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # For binary classification

        contributions = dict(zip(expected_cols, shap_values[0].tolist()))
        # Sort by absolute contribution
        sorted_contributions = dict(sorted(
            contributions.items(), 
            key=lambda x: abs(x[1]), 
            reverse=True
        ))

        return {
            'shap_values': contributions,
            'sorted_contributions': sorted_contributions,
            'base_value': float(self.explainer.expected_value[1] if isinstance(self.explainer.expected_value, list) else self.explainer.expected_value)
        }

    def load(self):
        """Load trained model."""
        if not Path(self.model_path).exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                f"Run training first: python scripts/run_pipeline.py"
            )
        self.model = joblib.load(self.model_path)
        logger.info(f"Model loaded from {self.model_path}")
