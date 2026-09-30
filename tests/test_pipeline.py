"""
Tests for the pipeline.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_pipeline.feature_engineering import PakistanFeatureEngineer
from src.data_pipeline.preprocessors import PakistanDataPreprocessor
from src.models.accident_predictor import AccidentPredictor
from src.models.traffic_flow_predictor import TrafficFlowPredictor


def test_feature_creation():
    engineer = PakistanFeatureEngineer()
    traffic = pd.DataFrame({
        'congestion_multiplier': [1.5, 1.2],
        'speed_limit_kmh': [60, 50],
        'road_type': ['Highway', 'Local'],
        'weather_condition': ['Clear', 'Rain'],
        'has_signal': [True, False],
        'road_curvature': [0.5, 0.3]
    })
    surface = pd.DataFrame({'pred_class': ['paved', 'unpaved']})
    features = engineer.create_features(traffic, surface, {}, {})
    assert 'infrastructure_score' in features.columns
    assert len(features) == 2


def test_preprocessor_cleaning():
    preprocessor = PakistanDataPreprocessor()
    df = pd.DataFrame({
        'speed_limit_kmh': [80, 50, 150, 30],
        'num_lanes': [4, 3, 2, 0],
        'congestion_multiplier': [1.5, np.nan, 1.2, 0.8],
        'road_type': ['Highway', 'Local', 'Highway', 'Local'],
        'weather_condition': ['Clear', 'Rain', 'Clear', 'Clear']
    })
    cleaned = preprocessor.clean_traffic_data(df)
    assert len(cleaned) == 3
    assert cleaned['congestion_multiplier'].isna().sum() == 0


def test_accident_predictor():
    predictor = AccidentPredictor(model_path='data/models/test_xgb.pkl')
    X = pd.DataFrame({
        'infrastructure_score': np.random.uniform(20, 90, 100),
        'traffic_flow': np.random.uniform(500, 2000, 100),
        'avg_speed': np.random.uniform(20, 60, 100),
        'signal_efficiency': np.random.uniform(40, 90, 100),
        'divergence_rate': np.random.uniform(5, 45, 100),
        'challan_ratio': np.random.uniform(3, 25, 100),
        'root_efficiency': np.random.uniform(40, 90, 100),
        'accident_risk': np.random.uniform(20, 80, 100)
    })
    y = (X['infrastructure_score'] < 50).astype(int)
    predictor.train(X, y)
    result = predictor.predict_risk(X.iloc[0].to_dict())
    assert 'probability' in result
    assert 0 <= result['risk_score'] <= 100


def test_lstm_save_load():
    model = TrafficFlowPredictor(sequence_length=5, model_path='data/models/test_lstm.pt')
    series = np.cumsum(np.random.randn(50)) + 100
    model.train(series, epochs=5)
    model2 = TrafficFlowPredictor(sequence_length=5, model_path='data/models/test_lstm.pt')
    model2.load()
    assert model2._trained is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
