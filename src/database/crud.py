"""
CRUD operations for database models.
"""
from sqlalchemy.orm import Session
from src.database.models import RoadSegment, RiskAssessment, AccidentRecord


def create_road_segment(db: Session, road_data: dict):
    db_road = RoadSegment(**road_data)
    db.add(db_road)
    db.commit()
    db.refresh(db_road)
    return db_road


def get_road_segment(db: Session, road_id: str):
    return db.query(RoadSegment).filter(RoadSegment.road_id == road_id).first()


def create_risk_assessment(db: Session, assessment_data: dict):
    db_assessment = RiskAssessment(**assessment_data)
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


def get_latest_risk_assessment(db: Session, road_id: str):
    return (
        db.query(RiskAssessment)
        .filter(RiskAssessment.road_id == road_id)
        .order_by(RiskAssessment.timestamp.desc())
        .first()
    )


def create_accident_record(db: Session, record_data: dict):
    db_record = AccidentRecord(**record_data)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_accidents_by_province(db: Session, province: str, year: int = None):
    query = db.query(AccidentRecord).filter(AccidentRecord.province == province)
    if year:
        query = query.filter(AccidentRecord.year == year)
    return query.all()
