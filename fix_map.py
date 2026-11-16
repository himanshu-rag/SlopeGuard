with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

target = """const satelliteStyle = {
  version: 8,
  sources: { 'satellite': { type: 'raster', tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'], tileSize: 256, attribution: '&copy; Esri', maxzoom: 17 } },
  layers: [{ id: 'satellite-layer', type: 'raster', source: 'satellite', minzoom: 0 }]
};"""

replacement = """const satelliteStyle = {
  version: 8,
  sources: { 
    'satellite': { type: 'raster', tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'], tileSize: 256, attribution: '&copy; Esri' },
    'labels': { type: 'raster', tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}'], tileSize: 256 }
  },
  layers: [
    { id: 'satellite-layer', type: 'raster', source: 'satellite', minzoom: 0 },
    { id: 'labels-layer', type: 'raster', source: 'labels', minzoom: 0 }
  ]
};"""

content = content.replace(target, replacement)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
