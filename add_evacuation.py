import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# 1. Add state for evacuation routing
state_injection = """  const [evacuationRoute, setEvacuationRoute] = useState<any>(null);
  const [isRouting, setIsRouting] = useState(false);

  const calculateEvacuation = async () => {
    setIsRouting(true);
    // Dynamic starting point: current hazard zone
    const startLng = currentZone.lng - 0.01;
    const startLat = currentZone.lat + 0.01;
    
    // Dynamic safe zone (evacuation center roughly 10-15km away)
    const safeLng = currentZone.lng + 0.08;
    const safeLat = currentZone.lat - 0.05;

    try {
      const res = await fetch(`http://router.project-osrm.org/route/v1/driving/${startLng},${startLat};${safeLng},${safeLat}?overview=full&geometries=geojson`);
      const data = await res.json();
      if (data.routes && data.routes[0]) {
        setEvacuationRoute({
          type: 'FeatureCollection',
          features: [
            { type: 'Feature', geometry: data.routes[0].geometry, properties: { type: 'route' } },
            { type: 'Feature', geometry: { type: 'Point', coordinates: [safeLng, safeLat] }, properties: { type: 'safezone', name: 'Evacuation Center Alpha' } }
          ]
        });
        // Pan the map to show the whole route
        setViewState({ longitude: (startLng + safeLng)/2, latitude: (startLat + safeLat)/2, zoom: 11.5 });
      }
    } catch (e) { console.error("OSRM Error", e); }
    setIsRouting(false);
  };

  // Clear route when changing zones
  useEffect(() => { setEvacuationRoute(null); }, [currentZone.id]);"""

content = content.replace("  const [activeModal, setActiveModal] = useState<string | null>(null);", 
                          "  const [activeModal, setActiveModal] = useState<string | null>(null);\n" + state_injection)

# 2. Add Map Layers for Evacuation Route
map_layer = """          {/* EVACUATION ROUTE LAYER */}
          {evacuationRoute && (
            <Source id="evac-route" type="geojson" data={evacuationRoute}>
              {/* Glowing outer line for the route */}
              <Layer 
                id="evac-route-glow" 
                type="line" 
                filter={['==', 'type', 'route']}
                paint={{ 'line-color': '#eab308', 'line-width': 8, 'line-opacity': 0.4, 'line-blur': 4 }} 
              />
              {/* Inner dashed line for the route */}
              <Layer 
                id="evac-route-line" 
                type="line" 
                filter={['==', 'type', 'route']}
                paint={{ 'line-color': '#eab308', 'line-width': 3, 'line-dasharray': [2, 2] }} 
              />
              {/* Safe Zone Marker */}
              <Layer 
                id="safe-zone-circle" 
                type="circle" 
                filter={['==', 'type', 'safezone']}
                paint={{ 'circle-radius': 12, 'circle-color': '#10b981', 'circle-stroke-width': 3, 'circle-stroke-color': '#ffffff' }} 
              />
              <Layer
                id="safe-zone-label" type="symbol" filter={['==', 'type', 'safezone']}
                layout={{ 'text-field': ['get', 'name'], 'text-size': 12, 'text-offset': [0, 1.5], 'text-anchor': 'top' }}
                paint={{ 'text-color': '#ffffff', 'text-halo-color': '#000000', 'text-halo-width': 2 }}
              />
            </Source>
          )}"""

content = content.replace("        </Map>", map_layer + "\n        </Map>")

# 3. Add Evacuation Button below the Infrastructure Cards
evac_btn = """              </motion.button>
              
              {/* EVACUATION BUTTON */}
              {(data?.risk_level === 'HIGH' || data?.risk_level === 'CRITICAL') && (
                 <motion.button
                   whileHover={{ scale: 1.02 }}
                   whileTap={{ scale: 0.98 }}
                   onClick={calculateEvacuation}
                   className="w-full mt-4 flex items-center justify-center gap-2 bg-yellow-500/20 text-yellow-500 hover:bg-yellow-500/30 border border-yellow-500/30 py-3 rounded-2xl font-black uppercase tracking-widest text-[11px] transition-all shadow-[0_0_15px_rgba(234,179,8,0.2)]"
                 >
                   {isRouting ? (
                     <div className="w-4 h-4 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin" />
                   ) : (
                     <Navigation size={14} /> 
                   )}
                   {isRouting ? 'CALCULATING ROUTE...' : 'MAP EVACUATION ROUTE'}
                 </motion.button>
              )}
            </div>"""

content = content.replace("              </motion.button>\n            </div>", evac_btn)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
