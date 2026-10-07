import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# Remove the static GeoJSON globals
content = re.sub(r"const terrainGeoJSON =.*?;\n", "", content)
content = re.sub(r"const reportsGeoJSON =.*?;\n", "", content)

# Update currentZone initial state to include lng/lat
content = content.replace(
    "const [currentZone, setCurrentZone] = useState({ id: '5', name: 'Guwahati, AS', type: 'Urban Hills' });",
    "const [currentZone, setCurrentZone] = useState({ id: '5', name: 'Guwahati, AS', type: 'Urban Hills', lng: 91.76, lat: 26.14 });"
)

# Update handleFlyTo to save lng/lat
content = content.replace(
    "setCurrentZone({ id: zone.id, name: zone.name, type: zone.type });",
    "setCurrentZone({ id: zone.id, name: zone.name, type: zone.type, lng: zone.lng, lat: zone.lat });"
)

# Inject dynamic geojson calculation inside the component, right before return
dynamic_geojson = """
  const d = 0.015;
  const dynamicTerrain = {
    type: 'FeatureCollection',
    features: [{ type: 'Feature', geometry: { type: 'Polygon', coordinates: [[[currentZone.lng - d, currentZone.lat - d], [currentZone.lng + d, currentZone.lat - d], [currentZone.lng + d, currentZone.lat + d], [currentZone.lng - d, currentZone.lat + d], [currentZone.lng - d, currentZone.lat - d]]] } }]
  };
  const dynamicReports = {
    type: 'FeatureCollection',
    features: [
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng - 0.005, currentZone.lat + 0.005] } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng + 0.008, currentZone.lat - 0.002] } }
    ]
  };

  return (
"""
content = content.replace("  return (\n", dynamic_geojson)

# Update the Map Source props to use dynamic data
content = content.replace('data={terrainGeoJSON}', 'data={dynamicTerrain as any}')
content = content.replace('data={reportsGeoJSON}', 'data={dynamicReports as any}')

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
