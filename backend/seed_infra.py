import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Infrastructure, TerrainZone

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://localhost/slopeguard")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_data():
    db = SessionLocal()
    
    # 1. Insert a dummy terrain zone (A steep hill)
    zone = TerrainZone(
        geom="SRID=4326;POLYGON((91.0 26.0, 91.0 26.1, 91.1 26.1, 91.1 26.0, 91.0 26.0))",
        slope_deg=45.0,
        aspect_deg=180.0,
        curvature=-0.5,
        twi=8.0
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    print(f"Inserted TerrainZone {zone.id}")

    # 2. Insert dummy infrastructure (A hospital and a road inside/near the zone)
    hospital = Infrastructure(
        geom="SRID=4326;POINT(91.05 26.05)",
        type="hospital",
        name="District Hospital, Guwahati",
        source="OSM"
    )
    bridge = Infrastructure(
        geom="SRID=4326;POINT(91.08 26.08)",
        type="bridge",
        name="Brahmaputra Highway Bridge",
        source="State Govt"
    )
    db.add(hospital)
    db.add(bridge)
    db.commit()
    print("Inserted Infrastructure")

if __name__ == "__main__":
    seed_data()
