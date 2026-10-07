import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# 1. Fix Right Panel UI (Alignment, Size, and Spacing)
old_right = """
      {/* RIGHT PANEL: LIVE TELEMETRY FEED */}
      <aside className="absolute top-28 right-6 z-10 w-80 pointer-events-auto">
        
        {/* HARDWARE STATUS GRID */}
        <div className="glass-panel rounded-[1.5rem] p-4 mb-4 flex gap-2">
           <div className="flex-1 bg-black/40 border border-white/5 rounded-xl p-2.5 relative overflow-hidden group">
              <div className="flex justify-between items-start mb-2">
                 <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)] animate-pulse" />
                 <Wifi size={10} className="text-green-400" />
              </div>
              <div className="text-[9px] font-black text-white tracking-widest uppercase">Node-Alpha</div>
              <div className="text-[8px] text-gray-500 font-bold tracking-widest uppercase mt-0.5">Crest</div>
           </div>
           <div className="flex-1 bg-black/40 border border-white/5 rounded-xl p-2.5 relative overflow-hidden group">
              <div className="flex justify-between items-start mb-2">
                 <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)] animate-pulse" />
                 <Wifi size={10} className="text-green-400" />
              </div>
              <div className="text-[9px] font-black text-white tracking-widest uppercase">Node-Beta</div>
              <div className="text-[8px] text-gray-500 font-bold tracking-widest uppercase mt-0.5">Mid-Slope</div>
           </div>
           <div className="flex-1 bg-black/40 border border-red-500/20 rounded-xl p-2.5 relative overflow-hidden group">
              <div className="flex justify-between items-start mb-2">
                 <div className="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]" />
                 <Wifi size={10} className="text-red-400 opacity-50" />
              </div>
              <div className="text-[9px] font-black text-gray-400 tracking-widest uppercase">Node-Gamma</div>
              <div className="text-[8px] text-red-500 font-bold tracking-widest uppercase mt-0.5">Offline</div>
           </div>
        </div>

        <div className="glass-panel rounded-[2rem] p-5">
"""

new_right = """
      {/* RIGHT PANEL: LIVE TELEMETRY FEED */}
      <aside className="absolute top-28 right-6 z-10 w-[280px] pointer-events-auto flex flex-col gap-3">
        
        {/* HARDWARE STATUS GRID */}
        <div className="flex gap-2 w-full">
           <div className="flex-1 glass-panel bg-black/60 rounded-2xl p-3 border border-white/10 shadow-lg relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-[2px] bg-green-500" />
              <div className="flex justify-between items-start mb-1.5">
                 <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)] animate-pulse" />
                 <Wifi size={10} className="text-green-400" />
              </div>
              <div className="text-[10px] font-black text-white tracking-tight">NODE-A</div>
              <div className="text-[8px] text-gray-400 font-bold tracking-widest uppercase mt-0.5">Crest</div>
           </div>
           <div className="flex-1 glass-panel bg-black/60 rounded-2xl p-3 border border-white/10 shadow-lg relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-[2px] bg-green-500" />
              <div className="flex justify-between items-start mb-1.5">
                 <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)] animate-pulse" />
                 <Wifi size={10} className="text-green-400" />
              </div>
              <div className="text-[10px] font-black text-white tracking-tight">NODE-B</div>
              <div className="text-[8px] text-gray-400 font-bold tracking-widest uppercase mt-0.5">Mid</div>
           </div>
           <div className="flex-1 glass-panel bg-red-900/20 rounded-2xl p-3 border border-red-500/30 shadow-lg relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-[2px] bg-red-500" />
              <div className="flex justify-between items-start mb-1.5">
                 <div className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]" />
                 <Wifi size={10} className="text-red-400 opacity-50" />
              </div>
              <div className="text-[10px] font-black text-gray-300 tracking-tight">NODE-G</div>
              <div className="text-[8px] text-red-400 font-bold tracking-widest uppercase mt-0.5">Base</div>
           </div>
        </div>

        <div className="glass-panel rounded-[1.5rem] p-4 flex-1">
"""
content = content.replace(old_right.strip(), new_right.strip())

# 2. Add IoT Nodes to the Map
dynamic_nodes = """
  const dynamicNodes = {
    type: 'FeatureCollection',
    features: [
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng - 0.003, currentZone.lat + 0.005] }, properties: { name: 'NODE-Alpha', status: 'online' } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng + 0.001, currentZone.lat + 0.001] }, properties: { name: 'NODE-Beta', status: 'online' } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng + 0.004, currentZone.lat - 0.004] }, properties: { name: 'NODE-Gamma', status: 'offline' } }
    ]
  };

  return (
"""
content = content.replace("  return (\n", dynamic_nodes)

# Add MapLibre Source for IoT Nodes
map_layers = """
          {showFieldReports && (
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
          )}
"""

content = content.replace("        </Map>", map_layers + "        </Map>")

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
