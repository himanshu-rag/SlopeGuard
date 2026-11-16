from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from geoalchemy2 import Geometry
import uuid
from database import Base, IS_POSTGRES
import enum

# On SQLite (no SpatiaLite), store geometry as plain WKT text instead of Geometry type.
# Spatial queries (ST_Centroid, ST_Intersects) will gracefully degrade on SQLite.
def _geom(geom_type):
    return Geometry(geom_type, srid=4326) if IS_POSTGRES else String()


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TerrainZone(Base):
    __tablename__ = "terrain_zones"

    id = Column(Integer, primary_key=True, index=True)
    geom = Column(_geom('POLYGON'), nullable=False)
    slope_deg = Column(Float)
    aspect_deg = Column(Float)
    curvature = Column(Float)
    twi = Column(Float)
    soil_class = Column(String)
    land_cover = Column(String)
    lithology = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    rainfall_observations = relationship("RainfallObservation", back_populates="zone")
    risk_scores = relationship("RiskScore", back_populates="zone")


class RainfallObservation(Base):
    __tablename__ = "rainfall_observations"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("terrain_zones.id"), nullable=False)
    observed_at = Column(DateTime(timezone=True), nullable=False)
    rainfall_mm = Column(Float, nullable=False)
    source = Column(String)

    zone = relationship("TerrainZone", back_populates="rainfall_observations")


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("terrain_zones.id"), nullable=True)
    computed_at = Column(DateTime(timezone=True), nullable=False)
    susceptibility = Column(Float)
    trigger_prob = Column(Float)
    final_score = Column(Float)
    confidence = Column(Float)
    reason_code = Column(Text)
    risk_level = Column(Enum(RiskLevel))

    zone = relationship("TerrainZone", back_populates="risk_scores")


class Infrastructure(Base):
    __tablename__ = "infrastructure"

    id = Column(Integer, primary_key=True, index=True)
    geom = Column(_geom('POINT'), nullable=False)
    type = Column(String)
    name = Column(String)
    source = Column(String)


class FieldReport(Base):
    __tablename__ = "field_reports"

    id = Column(String(36) if not IS_POSTGRES else PG_UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()) if not IS_POSTGRES else uuid.uuid4)
    zone_id = Column(Integer, ForeignKey("terrain_zones.id"), nullable=True)
    geom = Column(_geom('POINT'), nullable=False)
    reporter_id = Column(String)
    photo_url = Column(String)
    crack_width = Column(Float)
    seepage = Column(Boolean)
    vegetation = Column(String)
    notes = Column(Text)
    reported_at = Column(DateTime(timezone=True), nullable=False)
    synced_at = Column(DateTime(timezone=True), server_default=func.now())