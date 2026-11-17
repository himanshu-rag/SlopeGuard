from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Header
from fastapi.middleware.cors import CORSMiddleware
from api_ml import risk_engine  # Fail fast at startup if models not found # top-level
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime, timezone
import asyncio
import json
import random
import uuid
import os

app = FastAPI(
    title="SlopeGuard API",
    description="AI-Powered Landslide Risk Prediction and Early Warning System",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://10.154.148.46:8000",
        "capacitor://localhost",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# OPTIONAL API-KEY AUTH (enabled when API_KEY env var is set)
# ─────────────────────────────────────────────────────────────
API_KEY = os.getenv("API_KEY", "")


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Enforce API key on write endpoints when API_KEY is configured.
    If API_KEY is not set, auth is bypassed (dev mode)."""
    if not API_KEY:
        return True  # auth disabled
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True


# ─────────────────────────────────────────────────────────────
# DATABASE DEPENDENCY
# ─────────────────────────────────────────────────────────────
from sqlalchemy.orm import Session
from database import SessionLocal, IS_POSTGRES


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "SlopeGuard API v2 is running. All systems online."}


@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# ─────────────────────────────────────────────────────────────
# ML SIMULATION ENDPOINT
# ─────────────────────────────────────────────────────────────
class SimulationRequest(BaseModel):
    zone_id:     Optional[int] = None
    slope_deg:   float
    aspect_deg:  float
    curvature:   float
    twi:         float
    rainfall_seq: List[float]  # 1–30 days (FIX #3: no longer hard-crashes on < 30)

    @validator('slope_deg')
    def slope_in_range(cls, v):
        if not (0 <= v <= 90):
            raise ValueError('slope_deg must be between 0 and 90')
        return v

    @validator('twi')
    def twi_in_range(cls, v):
        if not (0 <= v <= 20):
            raise ValueError('twi must be between 0 and 20')
        return v


@app.post("/simulate")
async def simulate_risk(req: SimulationRequest, db: Session = Depends(get_db), _auth: bool = Depends(verify_api_key)):
    # FIX #8: Return proper HTTP 500 on error, not HTTP 200 with error body
    try:
        from api_ml import risk_engine  # Imported at module level; any failure raises at startup
        susc_prob   = risk_engine.predict_susceptibility(
            req.slope_deg, req.aspect_deg, req.curvature, req.twi
        )
        trig_prob   = risk_engine.predict_trigger(req.rainfall_seq)
        final_score, risk_level, reason = risk_engine.calculate_final_risk(susc_prob, trig_prob)

        # Persist risk score to database
        from models import RiskScore
        risk_record = RiskScore(
            zone_id=req.zone_id,
            computed_at=datetime.now(timezone.utc),
            susceptibility=susc_prob,
            trigger_prob=trig_prob,
            final_score=final_score,
            confidence=round(min(susc_prob, trig_prob) * 100, 2),
            reason_code=reason,
            risk_level=risk_level,
        )
        db.add(risk_record)
        db.commit()
        db.refresh(risk_record)

        return {
            "susceptibility_probability": round(susc_prob, 3),
            "trigger_probability":        round(trig_prob, 3),
            "final_score":                final_score,
            "risk_level":                 risk_level,
            "reason_code":                reason,
            "risk_score_id": str(risk_record.id),
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # FIX #8: Was returning {"error": str(e)} with HTTP 200 — now returns HTTP 500
        raise HTTPException(status_code=500, detail=f"Simulation engine error: {str(e)}")


# ─────────────────────────────────────────────────────────────
# ZONES — FIX #10: Return centroid coordinates so frontend
# can render zones on the map without hardcoded SEARCH_DB
# ─────────────────────────────────────────────────────────────
@app.get("/zones")
async def list_zones(db: Session = Depends(get_db)):
    """Returns all terrain zones with centroid coordinates for map display."""
    from models import TerrainZone
    from sqlalchemy import text

    zones = db.query(TerrainZone).limit(100).all()

    results = []
    for z in zones:
        lat, lng = None, None

        if IS_POSTGRES:
            # PostGIS: compute centroid from geometry
            centroid = db.execute(
                text("SELECT ST_X(ST_Centroid(geom)), ST_Y(ST_Centroid(geom)) FROM terrain_zones WHERE id = :id"),
                {"id": z.id}
            ).fetchone()
            if centroid:
                lng, lat = round(centroid[0], 6), round(centroid[1], 6)
        else:
            # SQLite: no SpatiaLite — parse WKT POLYGON centroid as average of vertices
            try:
                import re
                wkt = z.geom or ""
                coords = re.findall(r"([\d.-]+)\s([\d.-]+)", wkt)
                if coords:
                    lons = [float(c[0]) for c in coords]
                    lats = [float(c[1]) for c in coords]
                    lng = round(sum(lons) / len(lons), 6)
                    lat = round(sum(lats) / len(lats), 6)
            except Exception:
                lat, lng = None, None

        results.append({
            "id":        z.id,
            "slope":     z.slope_deg,
            "twi":       z.twi,
            "aspect":    z.aspect_deg,
            "curvature": z.curvature,
            "lng":       lng,
            "lat":       lat,
        })

    return results


# ─────────────────────────────────────────────────────────────
# RAINFALL TIME SERIES
# ─────────────────────────────────────────────────────────────
@app.get("/zones/{zone_id}/rainfall")
async def get_zone_rainfall(zone_id: int, db: Session = Depends(get_db)):
    from models import RainfallObservation
    observations = (
        db.query(RainfallObservation)
          .filter(RainfallObservation.zone_id == zone_id)
          .order_by(RainfallObservation.observed_at.asc())
          .limit(30)
          .all()
    )
    if not observations:
        raise HTTPException(status_code=404, detail=f"No rainfall data found for zone {zone_id}")
    return [obs.rainfall_mm for obs in observations]


# ─────────────────────────────────────────────────────────────
# INFRASTRUCTURE IMPACT ANALYSIS
# ─────────────────────────────────────────────────────────────
@app.get("/zones/{zone_id}/impact")
async def get_zone_impact(zone_id: int, db: Session = Depends(get_db)):
    """Finds infrastructure intersecting the given terrain zone using PostGIS."""
    from sqlalchemy import text

    if IS_POSTGRES:
        query = text("""
            SELECT i.name, i.type
            FROM infrastructure i
            JOIN terrain_zones z ON ST_Intersects(i.geom, z.geom)
            WHERE z.id = :zone_id
        """)
        result = db.execute(query, {"zone_id": zone_id}).fetchall()
        return {"zone_id": zone_id, "affected_infrastructure": [{"name": r[0], "type": r[1]} for r in result]}
    else:
        # SQLite: no SpatiaLite — return infrastructure in the same zone as a best-effort
        result = db.execute(
            text("SELECT name, type FROM infrastructure WHERE 1=0")
        ).fetchall()
        return {
            "zone_id": zone_id,
            "affected_infrastructure": [],
            "note": "Spatial intersection requires PostGIS. Running on SQLite fallback.",
        }


# ─────────────────────────────────────────────────────────────
# FIELD REPORTS
# ─────────────────────────────────────────────────────────────
class FieldReportCreate(BaseModel):
    longitude:   float
    latitude:    float
    zone_id:     Optional[int] = None   # null for custom/arbitrary locations
    reporter_id: str
    crack_width: Optional[float] = None
    seepage:     Optional[bool]  = False
    vegetation:  Optional[str]   = None
    notes:       Optional[str]   = None


@app.post("/reports")
async def submit_field_report(report: FieldReportCreate, db: Session = Depends(get_db), _auth: bool = Depends(verify_api_key)):
    """Accepts a field report from the mobile app."""
    from models import FieldReport

    # Only validate zone existence when a zone_id is provided.
    # Custom locations (zone_id=None) are accepted with raw GPS coords.
    if report.zone_id is not None:
        from models import TerrainZone
        zone = db.query(TerrainZone).filter(TerrainZone.id == report.zone_id).first()
        if not zone:
            raise HTTPException(status_code=404, detail="Zone not found")

    new_report = FieldReport(
        zone_id=report.zone_id,
        geom=f"SRID=4326;POINT({report.longitude} {report.latitude})",
        reporter_id=report.reporter_id,
        crack_width=report.crack_width,
        seepage=report.seepage,
        vegetation=report.vegetation,
        notes=report.notes,
        reported_at=datetime.now(timezone.utc),
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return {"status": "success", "report_id": str(new_report.id)}


# ─────────────────────────────────────────────────────────────
# WEBSOCKET: REAL-TIME IOT TELEMETRY
# FIX #7: WebSocket now accepts zone_id and generates sensor
# readings calibrated to the zone's actual terrain properties.
# ─────────────────────────────────────────────────────────────
@app.websocket("/ws/telemetry/{zone_id}")
async def websocket_endpoint(websocket: WebSocket, zone_id: str):
    await websocket.accept()

    # Load zone terrain data to calibrate sensor ranges
    db = SessionLocal()
    try:
        from models import TerrainZone
        if zone_id.startswith("global_"):
            slope = 40.0
            twi = 8.0
        elif zone_id.lstrip('-').isdigit():
            zone = db.query(TerrainZone).filter(TerrainZone.id == int(zone_id)).first()
            slope = zone.slope_deg if zone else 35.0
            twi   = zone.twi       if zone else 7.0
        else:
            # Historical / unknown non-integer IDs — use defaults
            slope = 50.0
            twi = 10.0
    finally:
        db.close()

    # Calibrate sensor ranges to real terrain
    # Steeper slopes → higher inclinometer readings
    # Higher TWI    → higher soil moisture baseline
    inclinometer_max = max(0.01, slope / 1000)          # e.g., 55° slope → 0.055°/h max
    moisture_baseline = min(80.0, 25.0 + twi * 4.0)     # e.g., TWI=8 → 57% moisture baseline

    node_ids = ["NODE-Alpha (Crest)", "NODE-Beta (Mid-Slope)", "NODE-Gamma (Base)"]
    node_weights = [0.4, 0.4, 0.2]  # NODE-Gamma is offline, rarely sends

    try:
        while True:
            # Simulate NODE-Gamma occasionally going offline (20% chance it sends)
            node = random.choices(node_ids, weights=node_weights)[0]

            sensor_type = random.choice(['Inclinometer', 'Soil Moisture', 'GPS Displacement'])

            if sensor_type == 'Inclinometer':
                val    = f"{random.uniform(0.001, inclinometer_max):.3f}°/h"
                status = "warning" if float(val[:-3]) > inclinometer_max * 0.75 else "normal"
            elif sensor_type == 'Soil Moisture':
                reading = random.gauss(moisture_baseline, 5.0)
                reading = max(10.0, min(99.0, reading))
                val     = f"{reading:.1f}%"
                status  = "warning" if reading > 70.0 else "normal"
            else:  # GPS Displacement
                # Higher slope → more likely to have displacement
                disp_max = max(0.5, slope / 20.0)
                reading  = random.uniform(0.0, disp_max)
                val      = f"{reading:.2f}mm"
                status   = "warning" if reading > disp_max * 0.7 else "normal"

            event = {
                "id":      str(uuid.uuid4()),
                "node_id": node,
                "type":    sensor_type,
                "val":     val,
                "status":  status,
                "time":    "Just now",
            }
            await websocket.send_text(json.dumps(event))
            await asyncio.sleep(4)

    except WebSocketDisconnect:
        print(f"[WS] Client disconnected from zone {zone_id} telemetry feed.")
