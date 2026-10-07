with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

old_code = """          {showFieldReports && (
            <Source id="iot-nodes" type="geojson" data={dynamicNodes as any}>
              <Layer 
                id="nodes-circle" type="circle" 
                paint={{ 
                  'circle-radius': 5, 
                  'circle-color': ['match', ['get', 'status'], 'online', '#22c55e', '#ef4444', '#ef4444'], 
                  'circle-stroke-width': 2, 
                  'circle-stroke-color': '#000000' 
                }} 
              />
              <Layer
                id="nodes-label" type="symbol"
                layout={{
                  'text-field': ['get', 'name'],
                  'text-size': 9,
                  'text-offset': [0, 1.2],
                  'text-anchor': 'top'
                }}
                paint={{
                  'text-color': '#ffffff',
                  'text-halo-color': '#000000',
                  'text-halo-width': 2
                }}
              />
            </Source>
          )}"""

new_code = """          {/* HARDWARE IOT NODES (ALWAYS VISIBLE) */}
          <Source id="iot-nodes" type="geojson" data={dynamicNodes as any}>
            <Layer 
              id="nodes-circle" type="circle" 
              paint={{ 
                'circle-radius': 6, 
                'circle-color': ['match', ['get', 'status'], 'online', '#22c55e', '#ef4444', '#ef4444'], 
                'circle-stroke-width': 2, 
                'circle-stroke-color': '#000000' 
              }} 
            />
            <Layer
              id="nodes-label" type="symbol"
              layout={{
                'text-field': ['get', 'name'],
                'text-size': 11,
                'text-offset': [0, 1.2],
                'text-anchor': 'top'
              }}
              paint={{
                'text-color': '#ffffff',
                'text-halo-color': '#000000',
                'text-halo-width': 2
              }}
            />
          </Source>"""

content = content.replace(old_code, new_code)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
