#!/bin/bash

# 1. Fix main.py Field Reports (Hardcoded coordinates)
sed -i '' 's/class FieldReportCreate(BaseModel):/class FieldReportCreate(BaseModel):\n    longitude: float\n    latitude: float/g' backend/main.py
sed -i '' 's/geom="SRID=4326;POINT(91.01 26.01)",/geom=f"SRID=4326;POINT({report.longitude} {report.latitude})",/g' backend/main.py

# 2. Fix api_ml.py (Handle incorrect rainfall sequence length)
sed -i '' 's/x = np.array(rainfall_seq, dtype=np.float32).reshape(1, -1, 1)/if len(rainfall_seq) != 30:\n            raise ValueError("Rainfall sequence must be exactly 30 days")\n        x = np.array(rainfall_seq, dtype=np.float32).reshape(1, 30, 1)/g' backend/api_ml.py

# 3. Fix ml/dataset.py (Removed sqlalchemy engine causes crash if fetch_terrain_features is called)
cat << 'PY' > ml/dataset.py
import pandas as pd
import numpy as np

def generate_synthetic_data(num_zones=200, num_days=30):
    print(f"Generating synthetic data for {num_zones} zones over {num_days} days...")
    terrain = pd.DataFrame({
        'zone_id': range(1, num_zones + 1),
        'slope_deg': np.random.uniform(0, 60, num_zones),
        'aspect_deg': np.random.uniform(0, 360, num_zones),
        'curvature': np.random.normal(0, 1, num_zones),
        'twi': np.random.uniform(2, 10, num_zones),
    })
    terrain['historical_landslide'] = ((terrain['slope_deg'] > 30) & (terrain['twi'] > 6)).astype(int)
    noise = np.random.choice([0, 1], size=num_zones, p=[0.9, 0.1])
    terrain['historical_landslide'] = (terrain['historical_landslide'] | noise)
    
    rainfall_data = []
    for zone in range(1, num_zones + 1):
        rain_seq = np.random.exponential(scale=5, size=num_days)
        trigger = 1 if sum(rain_seq[-3:]) > 40 else 0
        rainfall_data.append({'zone_id': zone, 'rainfall_sequence': rain_seq, 'trigger_event': trigger})
    
    return terrain, pd.DataFrame(rainfall_data)
PY

echo "Bugs fixed."
