import datetime
import random
from database import SessionLocal
from models import RainfallObservation, TerrainZone

db = SessionLocal()

# Ensure zone 1 exists
zone = db.query(TerrainZone).filter(TerrainZone.id == 1).first()
if not zone:
    print("Zone 1 not found!")
    exit(1)

# Delete existing rainfall for zone 1
db.query(RainfallObservation).filter(RainfallObservation.zone_id == 1).delete()

# Insert 30 days of rainfall
today = datetime.date.today()
for i in range(30, 0, -1):
    day = today - datetime.timedelta(days=i)
    # create realistic rainfall (mostly 0, some storms)
    rain = 0.0
    if random.random() > 0.7:
        rain = random.uniform(5.0, 45.0)
    if i < 5: # recent heavy rain
        rain += random.uniform(20.0, 60.0)
        
    obs = RainfallObservation(
        zone_id=1,
        observed_at=day,
        rainfall_mm=round(rain, 1)
    )
    db.add(obs)

db.commit()
print("Successfully seeded 30 days of rainfall for Zone 1.")
