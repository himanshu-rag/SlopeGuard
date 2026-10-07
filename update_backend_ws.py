with open("backend/main.py", "r") as f:
    content = f.read()

import re

old_ws = """
            if val_type == "Soil Moisture":
                val = f"{random.uniform(30.0, 50.0):.1f}%"
                status = "warning" if random.random() > 0.8 else "normal"
            elif val_type == "GPS Displacement":
                val = f"{random.uniform(0.0, 2.0):.1f}mm"
                status = "warning" if random.random() > 0.7 else "normal"
            else:
                val = f"{random.uniform(0.0, 0.05):.2f}°/h"
                status = "normal"
                
            payload = {
                "id": str(uuid.uuid4()),
                "type": val_type,
                "val": val,
                "status": status,
                "time": "Just now"
            }
"""

new_ws = """
            node = random.choice(["NODE-Alpha (Crest)", "NODE-Beta (Mid-Slope)", "NODE-Gamma (Base)"])
            if val_type == "Soil Moisture":
                val = f"{random.uniform(30.0, 50.0):.1f}%"
                status = "warning" if random.random() > 0.8 else "normal"
            elif val_type == "GPS Displacement":
                val = f"{random.uniform(0.0, 2.0):.1f}mm"
                status = "warning" if random.random() > 0.7 else "normal"
            else:
                val = f"{random.uniform(0.0, 0.05):.2f}°/h"
                status = "normal"
                
            payload = {
                "id": str(uuid.uuid4()),
                "node_id": node,
                "type": val_type,
                "val": val,
                "status": status,
                "time": "Just now"
            }
"""
content = content.replace(old_ws.strip(), new_ws.strip())

with open("backend/main.py", "w") as f:
    f.write(content)
