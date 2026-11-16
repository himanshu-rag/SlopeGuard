with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

injection = """
  // Evacuation Routing State
  const [evacuationRoute, setEvacuationRoute] = useState<any>(null);
  const [isRouting, setIsRouting] = useState(false);

  const calculateEvacuation = async () => {
    setIsRouting(true);
    const startLng = currentZone.lng - 0.01;
    const startLat = currentZone.lat + 0.01;
    const safeLng = currentZone.lng + 0.08;
    const safeLat = currentZone.lat - 0.05;

    try {
      const res = await fetch(`http://router.project-osrm.org/route/v1/driving/${startLng},${startLat};${safeLng},${safeLat}?overview=full&geometries=geojson`);
      const routeData = await res.json();
      if (routeData.routes && routeData.routes[0]) {
        setEvacuationRoute({
          type: 'FeatureCollection',
          features: [
            { type: 'Feature', geometry: routeData.routes[0].geometry, properties: { type: 'route' } },
            { type: 'Feature', geometry: { type: 'Point', coordinates: [safeLng, safeLat] }, properties: { type: 'safezone', name: 'Evacuation Center Alpha' } }
          ]
        });
        setViewState({ longitude: (startLng + safeLng)/2, latitude: (startLat + safeLat)/2, zoom: 11.5 });
      }
    } catch (e) { console.error("OSRM Error", e); }
    setIsRouting(false);
  };

  useEffect(() => { setEvacuationRoute(null); }, [currentZone.id]);

  // DVR Replay State
  const [dvrMode, setDvrMode] = useState(false);
  const [dvrEvent, setDvrEvent] = useState<string | null>(null);

  const startDvrReplay = (eventName: string) => {
    setDvrEvent(eventName);
    setDvrMode(true);
    setShowLayers(false);
    
    if (eventName === '2024 Wayanad') {
       setViewState({ longitude: 76.0822, latitude: 11.5549, zoom: 14.5 });
       setCurrentZone({ id: 'wayanad_1', name: 'Wayanad, KL', type: 'Western Ghats', lng: 76.0822, lat: 11.5549, slope: 62.0, aspect: 180, curvature: -0.9, twi: 12.5 });
    } else if (eventName === '2013 Kedarnath') {
       setViewState({ longitude: 79.0669, latitude: 30.7352, zoom: 14.0 });
       setCurrentZone({ id: 'kedar_1', name: 'Kedarnath, UK', type: 'Himalayan Slopes', lng: 79.0669, lat: 30.7352, slope: 75.0, aspect: 220, curvature: -1.2, twi: 14.0 });
    }
  };

  useEffect(() => {
    if (!dvrMode) return;
    setLoading(true);
    setTimeout(() => {
       const syntheticRain = Array(25).fill(10).concat([45, 90, 150, 280, 420]);
       setRainData(syntheticRain);
       setData({
         susceptibility_probability: 0.98,
         trigger_probability: 0.99,
         final_score: 98.7,
         risk_level: 'CRITICAL',
         reason_code: 'HIGH_TERRAIN_SUSCEPTIBILITY+HIGH_ANTECEDENT_RAINFALL'
       });
       setLoading(false);
       
       setTelemetry([
         { id: '1', node_id: 'NODE-Alpha (Crest)', type: 'GPS Displacement', val: '45.2mm', status: 'critical', time: '-1hr' },
         { id: '2', node_id: 'NODE-Beta (Mid-Slope)', type: 'Inclinometer', val: '4.5°/h', status: 'critical', time: '-1hr' },
         { id: '3', node_id: 'NODE-Gamma (Base)', type: 'Soil Moisture', val: '99.9%', status: 'critical', time: '-2hr' },
       ]);
    }, 1500);
  }, [dvrMode, dvrEvent]);
"""

target = "const [currentZone, setCurrentZone] = useState({ id: '5', name: 'Guwahati, AS', type: 'Urban Hills', lng: 91.76, lat: 26.14, slope: 45.0, aspect: 140.0, curvature: -0.5, twi: 8.2 });"
content = content.replace(target, target + "\n" + injection)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
