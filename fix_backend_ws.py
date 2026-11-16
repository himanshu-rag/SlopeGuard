with open("backend/main.py", "r") as f:
    content = f.read()

target = """@app.websocket("/ws/telemetry/{zone_id}")
async def websocket_endpoint(websocket: WebSocket, zone_id: int):
    await websocket.accept()

    # Load zone terrain data to calibrate sensor ranges
    db = SessionLocal()
    try:
        from models import TerrainZone
        zone = db.query(TerrainZone).filter(TerrainZone.id == zone_id).first()
        slope = zone.slope_deg if zone else 35.0
        twi   = zone.twi       if zone else 7.0"""

replacement = """@app.websocket("/ws/telemetry/{zone_id}")
async def websocket_endpoint(websocket: WebSocket, zone_id: str):
    await websocket.accept()

    # Load zone terrain data to calibrate sensor ranges
    db = SessionLocal()
    try:
        from models import TerrainZone
        if zone_id.startswith("global_"):
            slope = 40.0
            twi = 8.0
        else:
            zone = db.query(TerrainZone).filter(TerrainZone.id == int(zone_id)).first()
            slope = zone.slope_deg if zone else 35.0
            twi   = zone.twi       if zone else 7.0"""

content = content.replace(target, replacement)

with open("backend/main.py", "w") as f:
    f.write(content)
