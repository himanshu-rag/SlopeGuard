import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# Replace SEARCH_DB
old_search = """
const SEARCH_DB = [
  { id: 'ZN-420', name: 'Guwahati Sector A', lat: 26.14, lng: 91.76, type: 'High Elevation' },
  { id: 'ZN-112', name: 'Dispur Hills', lat: 26.143, lng: 91.789, type: 'Urban Slopes' },
  { id: 'ZN-808', name: 'Brahmaputra Embankment', lat: 26.183, lng: 91.751, type: 'Flood Risk' }
];
"""

new_search = """
const SEARCH_DB = [
  { id: '2', name: 'Shimla, HP', lat: 31.1048, lng: 77.1734, type: 'Himalayan Slopes' },
  { id: '3', name: 'Darjeeling, WB', lat: 27.0360, lng: 88.2627, type: 'Steep Tea Estates' },
  { id: '4', name: 'Munnar, KL', lat: 10.0889, lng: 77.0595, type: 'Western Ghats' },
  { id: '5', name: 'Guwahati, AS', lat: 26.1400, lng: 91.7600, type: 'Urban Hills' }
];
"""
content = content.replace(old_search.strip(), new_search.strip())

# Add dynamic state
state_replace = """
  const [viewState, setViewState] = useState({ longitude: 91.76, latitude: 26.14, zoom: 14 });

  useEffect(() => {
    fetch('http://127.0.0.1:8000/zones/1/rainfall').then(res => res.json()).then(fetchedRainData => {
"""

new_state = """
  const [viewState, setViewState] = useState({ longitude: 91.76, latitude: 26.14, zoom: 14 });
  const [currentZone, setCurrentZone] = useState({ id: '5', name: 'Guwahati, AS', type: 'Urban Hills' });

  useEffect(() => {
    setLoading(true);
    fetch(`http://127.0.0.1:8000/zones/${currentZone.id}/rainfall`).then(res => res.json()).then(fetchedRainData => {
"""
content = content.replace(state_replace.strip(), new_state.strip())

# Add dependency array fix
content = content.replace("return () => ws.close();\n  }, []);", "return () => ws.close();\n  }, [currentZone.id]);")

# Update handleFlyTo
old_fly = """
  const handleFlyTo = (lng: number, lat: number) => {
    setViewState({ longitude: lng, latitude: lat, zoom: 15.5 });
    setShowSearch(false);
    setSearchQuery("");
  };
"""

new_fly = """
  const handleFlyTo = (zone: any) => {
    setViewState({ longitude: zone.lng, latitude: zone.lat, zoom: 15.5 });
    setCurrentZone({ id: zone.id, name: zone.name, type: zone.type });
    setShowSearch(false);
    setSearchQuery("");
  };
"""
content = content.replace(old_fly.strip(), new_fly.strip())

# Update Search click
content = content.replace("onClick={() => handleFlyTo(zone.lng, zone.lat)}", "onClick={() => handleFlyTo(zone)}")

# Update Title card
content = content.replace(
    '<h2 className="text-xl font-extrabold text-white tracking-tight">Guwahati Sector A</h2>',
    '<h2 className="text-xl font-extrabold text-white tracking-tight">{currentZone.name}</h2>'
)
content = content.replace(
    '<MapPin size={14} /> Zone ID: ZN-420 • High Elevation',
    '<MapPin size={14} /> Zone ID: ZN-{currentZone.id} • {currentZone.type}'
)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
