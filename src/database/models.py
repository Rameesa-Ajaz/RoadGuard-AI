"""
SQLAlchemy database models for traffic data persistence.
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from config.settings import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class RoadSegment(Base):
    __tablename__ = "road_segments"

    id = Column(Integer, primary_key=True, index=True)
    road_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    city = Column(String, index=True)
    province = Column(String)
    road_type = Column(String)
    num_lanes = Column(Integer)
    speed_limit_kmh = Column(Float)
    is_one_way = Column(Boolean)
    has_signal = Column(Boolean)
    surface_condition = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    road_id = Column(String, index=True, nullable=False)
    risk_score = Column(Float)
    risk_level = Column(String)
    probability = Column(Float)
    infrastructure_score = Column(Float)
    traffic_flow = Column(Float)
    avg_speed = Column(Float)
    signal_efficiency = Column(Float)
    divergence_rate = Column(Float)
    challan_ratio = Column(Float)
    accident_risk = Column(Float)
    explanation = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class AccidentRecord(Base):
    __tablename__ = "accident_records"

    id = Column(Integer, primary_key=True, index=True)
    province = Column(String, index=True)
    district = Column(String)
    year = Column(Integer, index=True)
    total_accidents = Column(Integer)
    fatalities = Column(Integer)
    injuries = Column(Integer)
    primary_cause = Column(String)
    vehicle_type = Column(String)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
