with open("main.py", "r") as f:
    content = f.read()

new_endpoints = """
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json
import random

@app.get("/zones/{zone_id}/rainfall")
async def get_zone_rainfall(zone_id: int, db: Session = Depends(get_db)):
    from models import RainfallObservation
    observations = db.query(RainfallObservation).filter(RainfallObservation.zone_id == zone_id).order_by(RainfallObservation.observed_at.asc()).limit(30).all()
    # return just the array of floats
    return [obs.rainfall_mm for obs in observations]

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Simulate real-time sensor data from PostGIS/IoT stream
            sensor_type = random.choice(['Inclinometer', 'Soil Moisture', 'GPS Displacement'])
            val = ""
            if sensor_type == 'Inclinometer':
                val = f"{random.uniform(0.01, 0.05):.2f}°/h"
            elif sensor_type == 'Soil Moisture':
                val = f"{random.uniform(30.0, 50.0):.1f}%"
            else:
                val = f"{random.uniform(0.1, 1.5):.1f}mm"
                
            status = 'warning' if random.random() > 0.8 else 'normal'
            
            event = {
                "id": random.randint(10000, 99999),
                "type": sensor_type,
                "val": val,
                "status": status,
                "time": "Just now"
            }
            await websocket.send_text(json.dumps(event))
            await asyncio.sleep(5) # send every 5 seconds
    except WebSocketDisconnect:
        print("Client disconnected")
"""

content += new_endpoints
with open("main.py", "w") as f:
    f.write(content)
