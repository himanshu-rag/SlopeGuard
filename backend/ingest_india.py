import datetime
import requests
from database import SessionLocal
from models import TerrainZone, RainfallObservation
from sqlalchemy import text

db = SessionLocal()

# Clear existing data
db.query(RainfallObservation).delete()
db.query(TerrainZone).delete()
db.commit()

# Real Landslide Prone Regions in India
zones_data = [
    {"name": "Shimla, HP", "lat": 31.1048, "lon": 77.1734, "slope": 55.0, "elev": 2276, "twi": 5.2, "type": "Himalayan Slopes"},
    {"name": "Darjeeling, WB", "lat": 27.0360, "lon": 88.2627, "slope": 48.0, "elev": 2042, "twi": 6.1, "type": "Steep Tea Estates"},
    {"name": "Munnar, KL", "lat": 10.0889, "lon": 77.0595, "slope": 35.0, "elev": 1532, "twi": 8.5, "type": "Western Ghats"},
    {"name": "Guwahati, AS", "lat": 26.1400, "lon": 91.7600, "slope": 45.0, "elev": 320, "twi": 8.2, "type": "Urban Hills"}
]

end_date = datetime.date.today() - datetime.timedelta(days=1)
start_date = end_date - datetime.timedelta(days=29) # 30 days total

for zd in zones_data:
    lon = zd['lon']
    lat = zd['lat']
    # Create a tiny 0.01 degree polygon (approx 1km square)
    d = 0.01
    poly = f"POLYGON(({lon-d} {lat-d}, {lon+d} {lat-d}, {lon+d} {lat+d}, {lon-d} {lat+d}, {lon-d} {lat-d}))"
    
    # 1. Create Zone
    zone = TerrainZone(
        geom=poly,
        slope_deg=zd['slope'],
        aspect_deg=180.0,
        curvature=-0.5,
        twi=zd['twi']
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    print(f"Created Zone: {zd['name']} (ID: {zone.id})")

    # 2. Fetch Real Weather Data from Open-Meteo (Historical/Archive API)
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={zd['lat']}&longitude={zd['lon']}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=auto"
    print(f"Fetching real weather for {zd['name']}...")
    try:
        response = requests.get(url)
        data = response.json()
        daily_rain = data['daily']['precipitation_sum']
        dates = data['daily']['time']
        
        # 3. Insert Rainfall
        for i, rain_val in enumerate(daily_rain):
            # If API returns None for a day, assume 0
            val = float(rain_val) if rain_val is not None else 0.0
            date_obj = datetime.datetime.strptime(dates[i], "%Y-%m-%d").date()
            obs = RainfallObservation(
                zone_id=zone.id,
                observed_at=date_obj,
                rainfall_mm=val
            )
            db.add(obs)
        db.commit()
        print(f"-> Seeded 30 days of real rainfall.")
    except Exception as e:
        print(f"-> Failed to fetch weather for {zd['name']}: {e}")

print("Phase 6 Data Ingestion Complete! Real India data loaded.")
