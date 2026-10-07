import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# ─── FIX #12: Replace ALL hardcoded localhost URLs with env variable ───────
# Add constant at top of the component/file after imports
API_BASE_CONST = "const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';\n"
if "const API_BASE" not in content:
    # Insert after last import line
    last_import = content.rfind("import ")
    end_of_last_import = content.find("\n", last_import) + 1
    content = content[:end_of_last_import] + "\n" + API_BASE_CONST + content[end_of_last_import:]

content = content.replace("'http://127.0.0.1:8000/zones/", '`${API_BASE}/zones/')
content = content.replace("'http://127.0.0.1:8000/simulate'", '`${API_BASE}/simulate`')
content = content.replace('"http://127.0.0.1:8000/simulate"', '`${API_BASE}/simulate`')
# Fix template literals that now have double backticks
content = content.replace("``${API_BASE}", "`${API_BASE}")

# ─── FIX #13: Add aspect_deg and curvature to SEARCH_DB and zones ──────────
old_search_db = """const SEARCH_DB = [
  { id: '2', name: 'Shimla, HP', lat: 31.1048, lng: 77.1734, type: 'Himalayan Slopes', slope: 55.0, twi: 5.2 },
  { id: '3', name: 'Darjeeling, WB', lat: 27.0360, lng: 88.2627, type: 'Steep Tea Estates', slope: 48.0, twi: 6.1 },
  { id: '4', name: 'Munnar, KL', lat: 10.0889, lng: 77.0595, type: 'Western Ghats', slope: 35.0, twi: 8.5 },
  { id: '5', name: 'Guwahati, AS', lat: 26.1400, lng: 91.7600, type: 'Urban Hills', slope: 45.0, twi: 8.2 }
];"""

new_search_db = """const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

const SEARCH_DB = [
  { id: '2', name: 'Shimla, HP',      lat: 31.1048, lng: 77.1734, type: 'Himalayan Slopes',  slope: 55.0, aspect: 220.0, curvature: -0.8, twi: 5.2 },
  { id: '3', name: 'Darjeeling, WB',  lat: 27.0360, lng: 88.2627, type: 'Steep Tea Estates', slope: 48.0, aspect: 160.0, curvature: -0.3, twi: 6.1 },
  { id: '4', name: 'Munnar, KL',      lat: 10.0889, lng: 77.0595, type: 'Western Ghats',     slope: 35.0, aspect: 270.0, curvature:  0.2, twi: 8.5 },
  { id: '5', name: 'Guwahati, AS',    lat: 26.1400, lng: 91.7600, type: 'Urban Hills',       slope: 45.0, aspect: 140.0, curvature: -0.5, twi: 8.2 }
];"""

content = content.replace(old_search_db, new_search_db)
# Remove duplicate API_BASE that was added before
content = content.replace("\nconst API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';\n\nconst API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';", 
                          "\nconst API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';")

# Update initial zone state to include aspect+curvature
content = content.replace(
    "const [currentZone, setCurrentZone] = useState({ id: '5', name: 'Guwahati, AS', type: 'Urban Hills', lng: 91.76, lat: 26.14, slope: 45.0, twi: 8.2 });",
    "const [currentZone, setCurrentZone] = useState({ id: '5', name: 'Guwahati, AS', type: 'Urban Hills', lng: 91.76, lat: 26.14, slope: 45.0, aspect: 140.0, curvature: -0.5, twi: 8.2 });"
)

# Update handleFlyTo to carry aspect+curvature
content = content.replace(
    "setCurrentZone({ id: zone.id, name: zone.name, type: zone.type, lng: zone.lng, lat: zone.lat, slope: zone.slope, twi: zone.twi });",
    "setCurrentZone({ id: zone.id, name: zone.name, type: zone.type, lng: zone.lng, lat: zone.lat, slope: zone.slope, aspect: zone.aspect ?? 180.0, curvature: zone.curvature ?? -0.5, twi: zone.twi });"
)

# FIX #13: Pass aspect_deg and curvature dynamically in simulate call
content = content.replace(
    "body: JSON.stringify({ slope_deg: currentZone.slope, aspect_deg: 180.0, curvature: -0.5, twi: currentZone.twi, rainfall_seq: fetchedRainData })",
    "body: JSON.stringify({ slope_deg: currentZone.slope, aspect_deg: currentZone.aspect ?? 180.0, curvature: currentZone.curvature ?? -0.5, twi: currentZone.twi, rainfall_seq: fetchedRainData })"
)

# ─── FIX #7: Update WebSocket URL to include zone_id ───────────────────────
content = content.replace(
    'const ws = new WebSocket("ws://127.0.0.1:8000/ws/telemetry");',
    'const ws = new WebSocket(`${API_BASE.replace("http", "ws")}/ws/telemetry/${currentZone.id}`);'
)

# ─── FIX #11: Add useRef to prevent double WebSocket connections ────────────
# Check if wsRef is already in the file
if "wsRef" not in content:
    content = content.replace(
        "  const [loading, setLoading] = useState(true);",
        "  const wsRef = useRef<WebSocket | null>(null);\n  const [loading, setLoading] = useState(true);"
    )
    
    # Check if useRef is imported
    if "useRef" not in content:
        content = content.replace(
            "import { useState, useEffect,",
            "import { useState, useEffect, useRef,"
        )
        content = content.replace(
            "import { useState, useEffect ",
            "import { useState, useEffect, useRef "
        )
        content = content.replace(
            "import React, { useState, useEffect }",
            "import React, { useState, useEffect, useRef }"
        )

    # Replace WebSocket block to use ref
    old_ws_block = """    const ws = new WebSocket(`${API_BASE.replace("http", "ws")}/ws/telemetry/${currentZone.id}`);
    ws.onmessage = (event) => { setTelemetry(prev => [JSON.parse(event.data), ...prev].slice(0, 5)); };
    return () => ws.close();"""
    
    new_ws_block = """    // FIX #11: Close previous connection before opening a new one (prevents memory leak)
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }
    const ws = new WebSocket(`${API_BASE.replace("http", "ws")}/ws/telemetry/${currentZone.id}`);
    wsRef.current = ws;
    ws.onmessage = (event) => { setTelemetry(prev => [JSON.parse(event.data), ...prev].slice(0, 5)); };
    return () => { ws.close(); wsRef.current = null; };"""
    
    content = content.replace(old_ws_block, new_ws_block)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)

print("Frontend bug fixes applied.")
