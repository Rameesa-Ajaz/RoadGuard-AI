"""
End-to-end pipeline runner.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import json
from loguru import logger

from config.settings import OUTPUT_DIR, MODEL_DIR
from src.database.models import init_db
from src.data_pipeline.downloaders import (
    download_lahore_traffic_data,
    download_road_surface_data,
    load_accident_data,
    load_challan_data
)
from src.data_pipeline.preprocessors import PakistanDataPreprocessor
from src.data_pipeline.feature_engineering import PakistanFeatureEngineer
from src.models.train_models import train_all_models
from src.explanation.causal_analyzer import CausalTrafficAnalyzer
from src.explanation.explanation_generator import ExplanationGenerator


def run_pipeline():
    logger.info("🚀 Running Full Pipeline...")

    # 0. Initialize database
    print("0. Initializing database...")
    init_db()
    print("   ✓ Database ready")

    # 1. Download data
    print("1. Downloading data...")
    lahore_data = download_lahore_traffic_data()
    surface_data = download_road_surface_data()
    accident_data = load_accident_data()
    challan_data = load_challan_data()
    print("   ✓ Data loaded")

    # 2. Preprocess
    print("2. Preprocessing traffic data...")
    preprocessor = PakistanDataPreprocessor()
    cleaned = preprocessor.clean_traffic_data(lahore_data)
    risk_labels = preprocessor.create_risk_labels(cleaned)
    print(f"   ✓ Cleaned {len(cleaned)} records")

    # 3. Feature engineering
    print("3. Engineering features...")
    engineer = PakistanFeatureEngineer()
    features = engineer.create_features(
        cleaned, surface_data, accident_data, challan_data
    )
    print(f"   ✓ Created {len(features.columns)} features")

    # 4. Train models
    print("4. Training models...")
    train_all_models()
    print("   ✓ Models trained and saved")

    # 5. Generate sample explanation
    print("5. Generating sample explanation...")
    causal_analyzer = CausalTrafficAnalyzer()
    explanation_gen = ExplanationGenerator()

    sample_features = {
        'infrastructure_score': 35,
        'traffic_flow': 1800,
        'avg_speed': 55,
        'signal_efficiency': 45,
        'divergence_rate': 38,
        'challan_ratio': 4,
        'root_efficiency': 55,
        'accident_risk': 72
    }

    sample_explanation = explanation_gen.generate_explanation(
        {'risk_score': 92, 'risk_level': 'critical'},
        causal_analyzer.trace_causal_chain(sample_features),
        causal_analyzer.get_counterfactual(sample_features, 'Infrastructure', 'good')
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DIR / "sample_explanation.json", "w") as f:
        json.dump(sample_explanation, f, indent=2)
    print("   ✓ Sample explanation saved")

    # 6. Save feature summary
    feature_summary = features.describe().to_dict()
    with open(OUTPUT_DIR / "feature_summary.json", "w") as f:
        json.dump(feature_summary, f, indent=2, default=str)
    print("   ✓ Feature summary saved")

    logger.info("✅ Pipeline Complete! Check output/ and data/models/ directories.")
    print("\nNext steps:")
    print("  • Start API:  uvicorn src.api.main:app --reload")
    print("  • Start Dashboard:  streamlit run dashboard/app.py")


def main():
    run_pipeline()


if __name__ == "__main__":
    main()
