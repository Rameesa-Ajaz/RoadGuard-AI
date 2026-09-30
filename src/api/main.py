"""
FastAPI backend for Smart Traffic Risk System - Pakistan.
Enhanced with export functionality and report generation.
"""
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import os
import json

from config.settings import (
    CORS_ORIGINS, API_HOST, API_PORT, ENVIRONMENT, DEBUG, MODEL_DIR, OUTPUT_DIR
)
from src.database.models import init_db, get_db
from src.database import crud
from src.models.accident_predictor import AccidentPredictor
from src.models.traffic_flow_predictor import TrafficFlowPredictor
from src.explanation.causal_analyzer import CausalTrafficAnalyzer
from src.explanation.explanation_generator import ExplanationGenerator
from src.recommendation.decision_engine import TrafficDecisionEngine
from src.recommendation.route_optimizer import RiskAwareRouteOptimizer
from src.analysis.risk_factor_analysis import RiskFactorAnalyzer
from src.analysis.spatial_analysis import SpatialAnalyzer
from loguru import logger

# Initialize FastAPI
app = FastAPI(
    title="Smart Traffic Risk System - Pakistan",
    description="Explainable AI for traffic safety analysis using Pakistan data",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None
)

# CORS - configurable via environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize components (lazy loading for models)
accident_predictor: Optional[AccidentPredictor] = None
traffic_predictor = TrafficFlowPredictor()
causal_analyzer = CausalTrafficAnalyzer()
explanation_generator = ExplanationGenerator()
decision_engine = TrafficDecisionEngine()
route_optimizer = RiskAwareRouteOptimizer()
risk_analyzer = RiskFactorAnalyzer()
spatial_analyzer = SpatialAnalyzer()


# --- Pydantic Models ---

class RoadFeatures(BaseModel):
    """Validated input features for road risk analysis."""
    infrastructure_score: float = Field(..., ge=0, le=100, description="Road infrastructure quality score")
    traffic_flow: float = Field(..., ge=0, le=5000, description="Traffic flow in vehicles/hour")
    avg_speed: float = Field(..., ge=5, le=120, description="Average speed in km/h")
    signal_efficiency: float = Field(..., ge=0, le=100, description="Signal coordination efficiency")
    divergence_rate: float = Field(..., ge=0, le=100, description="Lane change divergence rate")
    challan_ratio: float = Field(..., ge=0, le=100, description="Enforcement challan ratio")
    root_efficiency: float = Field(..., ge=0, le=100, description="Road management efficiency")
    accident_risk: float = Field(..., ge=0, le=100, description="Historical accident risk proxy")


class RoadAnalysisRequest(BaseModel):
    road_id: str = Field(..., min_length=1, max_length=100)
    city: Optional[str] = "Unknown"
    features: RoadFeatures


class RoadAnalysisResponse(BaseModel):
    road_id: str
    timestamp: datetime
    risk_score: float
    risk_level: str
    explanation: Dict
    recommendations: Dict
    alternative_routes: Dict


class HealthResponse(BaseModel):
    status: str
    environment: str
    model_loaded: bool
    model_path_exists: bool
    version: str
    timestamp: str


class ExportRequest(BaseModel):
    road_id: str
    format: str = Field(default="json", pattern="^(json|csv|pdf)$")


# --- Startup / Health ---

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    logger.info("Database initialized")

    # Check model existence but don't fail startup
    model_exists = Path(MODEL_DIR / "accident_xgb.pkl").exists()
    if not model_exists:
        logger.warning(
            f"Model not found at {MODEL_DIR}/accident_xgb.pkl. "
            f"API will return 503 for /analyze until trained."
        )


@app.get("/", tags=["General"])
async def root():
    return {
        "message": "Smart Traffic Risk System - Pakistan",
        "version": "1.0.0",
        "status": "Operational",
        "environment": ENVIRONMENT,
        "docs": "/docs" if DEBUG else None,
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "explain": "/explain/{road_id}",
            "export": "/export/{road_id}",
            "summary": "/dashboard/summary",
            "routes": "/routes/compare"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check endpoint."""
    model_path = MODEL_DIR / "accident_xgb.pkl"
    model_exists = model_path.exists()

    return HealthResponse(
        status="ok",
        environment=ENVIRONMENT,
        model_loaded=accident_predictor is not None and accident_predictor.model is not None,
        model_path_exists=model_exists,
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


# --- Main Analysis Endpoint ---

@app.post("/analyze", response_model=RoadAnalysisResponse, tags=["Analysis"])
async def analyze_road(request: RoadAnalysisRequest):
    """Analyze a road segment for risk and return explanations + recommendations."""
    global accident_predictor

    # Lazy-load model
    if accident_predictor is None:
        try:
            accident_predictor = AccidentPredictor()
            accident_predictor.load()
        except FileNotFoundError:
            raise HTTPException(
                status_code=503,
                detail="Model not trained. Run: python scripts/run_pipeline.py"
            )

    try:
        features_dict = request.features.dict()

        # Predict risk
        risk = accident_predictor.predict_risk(features_dict)

        # Generate explanation
        causal_chain = causal_analyzer.trace_causal_chain(features_dict)
        counterfactual = causal_analyzer.get_counterfactual(
            features_dict, 'Infrastructure', 'good'
        )

        explanation = explanation_generator.generate_explanation(
            risk, causal_chain, counterfactual
        )

        # Get recommendations
        recommendations = decision_engine.decide_action(
            risk['risk_score'],
            request.features.traffic_flow,
            request.features.divergence_rate
        )

        # Find alternative routes
        routes = route_optimizer.find_alternative_routes(
            request.road_id, "destination"
        )

        # Persist to database
        try:
            from sqlalchemy.orm import Session
            db = next(get_db())
            crud.create_risk_assessment(db, {
                'road_id': request.road_id,
                'risk_score': risk['risk_score'],
                'risk_level': risk['risk_level'],
                'probability': risk['probability'],
                **features_dict,
                'explanation': explanation['full_explanation']
            })
        except Exception as e:
            logger.warning(f"Failed to persist assessment: {e}")

        return RoadAnalysisResponse(
            road_id=request.road_id,
            timestamp=datetime.now(),
            risk_score=risk['risk_score'],
            risk_level=risk['risk_level'],
            explanation=explanation,
            recommendations=recommendations,
            alternative_routes=routes
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/explain/{road_id}", tags=["Analysis"])
async def explain_road(road_id: str):
    """Get SHAP explanation for a road's last assessment."""
    global accident_predictor

    if accident_predictor is None:
        try:
            accident_predictor = AccidentPredictor()
            accident_predictor.load()
        except FileNotFoundError:
            raise HTTPException(status_code=503, detail="Model not trained.")

    # In production, fetch features from DB by road_id
    # For now, return a template explanation
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

    explanation = accident_predictor.explain_prediction(sample_features)
    return {
        'road_id': road_id,
        'shap_explanation': explanation,
        'top_drivers': list(explanation['sorted_contributions'].items())[:5]
    }


# --- EXPORT ENDPOINTS ---

@app.get("/export/{road_id}", tags=["Export"])
async def export_road_report(
    road_id: str, 
    format: str = Query(default="json", pattern="^(json|csv)$"),
    features: Optional[str] = None
):
    """Export road analysis report in JSON or CSV format."""
    global accident_predictor

    if accident_predictor is None:
        try:
            accident_predictor = AccidentPredictor()
            accident_predictor.load()
        except FileNotFoundError:
            raise HTTPException(status_code=503, detail="Model not trained.")

    # Parse features if provided
    if features:
        try:
            features_dict = json.loads(features)
        except:
            features_dict = {
                'infrastructure_score': 35, 'traffic_flow': 1800, 'avg_speed': 55,
                'signal_efficiency': 45, 'divergence_rate': 38, 'challan_ratio': 4,
                'root_efficiency': 55, 'accident_risk': 72
            }
    else:
        features_dict = {
            'infrastructure_score': 35, 'traffic_flow': 1800, 'avg_speed': 55,
            'signal_efficiency': 45, 'divergence_rate': 38, 'challan_ratio': 4,
            'root_efficiency': 55, 'accident_risk': 72
        }

    risk = accident_predictor.predict_risk(features_dict)
    causal_chain = causal_analyzer.trace_causal_chain(features_dict)
    counterfactual = causal_analyzer.get_counterfactual(features_dict, 'Infrastructure', 'good')
    explanation = explanation_generator.generate_explanation(risk, causal_chain, counterfactual)
    recommendations = decision_engine.decide_action(risk['risk_score'], features_dict['traffic_flow'], features_dict['divergence_rate'])

    report = {
        "road_id": road_id,
        "timestamp": datetime.now().isoformat(),
        "risk_assessment": risk,
        "features": features_dict,
        "explanation": explanation,
        "recommendations": recommendations,
        "system_version": "1.0.0"
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if format == "json":
        file_path = OUTPUT_DIR / f"report_{road_id.replace(' ', '_').replace(',', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(file_path, 'w') as f:
            json.dump(report, f, indent=2)
        return FileResponse(file_path, media_type="application/json", filename=file_path.name)

    elif format == "csv":
        import csv
        file_path = OUTPUT_DIR / f"report_{road_id.replace(' ', '_').replace(',', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Field", "Value"])
            writer.writerow(["Road ID", road_id])
            writer.writerow(["Timestamp", report["timestamp"]])
            writer.writerow(["Risk Score", risk['risk_score']])
            writer.writerow(["Risk Level", risk['risk_level']])
            writer.writerow(["Probability", risk['probability']])
            for k, v in features_dict.items():
                writer.writerow([k, v])
            writer.writerow(["Explanation", explanation['full_explanation'][:500]])
            writer.writerow(["Action Type", recommendations['action_type']])
            writer.writerow(["Alert Level", recommendations['alert_level']])
        return FileResponse(file_path, media_type="text/csv", filename=file_path.name)


@app.get("/export/summary", tags=["Export"])
async def export_dashboard_summary(format: str = Query(default="json", pattern="^(json|csv)$")):
    """Export dashboard summary data."""
    summary = {
        "total_roads": 250,
        "critical_risk": 23,
        "high_risk": 45,
        "moderate_risk": 78,
        "low_risk": 104,
        "recent_accidents": 12,
        "system_status": "Operational",
        "last_update": datetime.now().isoformat(),
        "province_breakdown": {
            "Punjab": {"accidents": 1560000, "fatalities": 18001},
            "Sindh": {"accidents": 700000, "fatalities": 12286},
            "KPK": {"accidents": 314000, "fatalities": 7545},
            "Balochistan": {"accidents": 111245, "fatalities": 5969}
        }
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_path = OUTPUT_DIR / f"dashboard_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"

    if format == "json":
        with open(file_path, 'w') as f:
            json.dump(summary, f, indent=2)
        return FileResponse(file_path, media_type="application/json", filename=file_path.name)
    else:
        import csv
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Total Roads", summary["total_roads"]])
            writer.writerow(["Critical Risk", summary["critical_risk"]])
            writer.writerow(["High Risk", summary["high_risk"]])
            writer.writerow(["Moderate Risk", summary["moderate_risk"]])
            writer.writerow(["Low Risk", summary["low_risk"]])
            writer.writerow(["Recent Accidents", summary["recent_accidents"]])
        return FileResponse(file_path, media_type="text/csv", filename=file_path.name)


@app.get("/dashboard/summary", tags=["Dashboard"])
async def get_summary():
    """Get dashboard summary statistics."""
    return {
        "total_roads": 250,
        "critical_risk": 23,
        "high_risk": 45,
        "moderate_risk": 78,
        "low_risk": 104,
        "recent_accidents": 12,
        "system_status": "Operational",
        "last_update": datetime.now().isoformat()
    }


@app.get("/routes/compare", tags=["Routes"])
async def compare_routes(origin: str, destination: str, risk_tolerance: float = 0.5):
    """Compare routes between two points."""
    routes = route_optimizer.find_alternative_routes(origin, destination)
    ranked = route_optimizer.rank_routes_by_preference(routes, risk_tolerance)

    return {
        'origin': origin,
        'destination': destination,
        'risk_tolerance': risk_tolerance,
        'routes': ranked
    }


@app.get("/analytics/province", tags=["Analytics"])
async def get_provincial_analytics():
    """Get provincial accident analytics."""
    accident_data = {
        'province_breakdown': {
            'Punjab': {'accidents': 1560000, 'fatalities': 18001},
            'Sindh': {'accidents': 700000, 'fatalities': 12286},
            'KPK': {'accidents': 314000, 'fatalities': 7545},
            'Balochistan': {'accidents': 111245, 'fatalities': 5969}
        }
    }
    return risk_analyzer.provincial_comparison(accident_data).to_dict(orient='records')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
