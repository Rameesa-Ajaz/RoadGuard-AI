"""
Training script for all models.
"""
import pandas as pd
import numpy as np
from loguru import logger
from config.settings import MODEL_DIR
from src.models.traffic_flow_predictor import TrafficFlowPredictor
from src.models.accident_predictor import AccidentPredictor


def generate_synthetic_training_data(n_samples=1000):
    """Generate realistic synthetic training data for Pakistan roads."""
    np.random.seed(42)

    X = pd.DataFrame({
        'infrastructure_score': np.random.uniform(20, 90, n_samples),
        'traffic_flow': np.random.uniform(500, 2000, n_samples),
        'avg_speed': np.random.uniform(20, 60, n_samples),
        'signal_efficiency': np.random.uniform(40, 90, n_samples),
        'divergence_rate': np.random.uniform(5, 45, n_samples),
        'challan_ratio': np.random.uniform(3, 25, n_samples),
        'root_efficiency': np.random.uniform(40, 90, n_samples),
        'accident_risk': np.random.uniform(20, 80, n_samples)
    })

    # Create target: high risk if infrastructure is poor AND speed is high
    y = (
        (X['infrastructure_score'] < 50) & 
        (X['avg_speed'] > 45) |
        (X['divergence_rate'] > 35) |
        (X['accident_risk'] > 65)
    ).astype(int)

    logger.info(f"Generated {n_samples} synthetic training samples ({y.sum()} positive)")
    return X, y


def train_all_models():
    """Train all models on Pakistan data."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("=== Starting Model Training ===")

    # 1. Traffic Flow Predictor (LSTM)
    logger.info("Training Traffic Flow Predictor (LSTM)...")
    flow_model = TrafficFlowPredictor(sequence_length=12)
    # Generate synthetic time series for demo
    synthetic_series = np.cumsum(np.random.randn(500)) + 1000
    flow_model.train(synthetic_series, epochs=30)
    logger.info("Traffic Flow Predictor trained successfully")

    # 2. Accident Predictor (XGBoost)
    logger.info("Training Accident Predictor (XGBoost)...")
    accident_model = AccidentPredictor()
    X_train, y_train = generate_synthetic_training_data(n_samples=2000)
    accident_model.train(X_train, y_train)
    logger.info("Accident Predictor trained successfully")

    logger.info("=== All Models Trained ===")
    return flow_model, accident_model


def main():
    train_all_models()


if __name__ == "__main__":
    main()
