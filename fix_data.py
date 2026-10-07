import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# Update SEARCH_DB
old_search = """
const SEARCH_DB = [
  { id: '2', name: 'Shimla, HP', lat: 31.1048, lng: 77.1734, type: 'Himalayan Slopes' },
  { id: '3', name: 'Darjeeling, WB', lat: 27.0360, lng: 88.2627, type: 'Steep Tea Estates' },
  { id: '4', name: 'Munnar, KL', lat: 10.0889, lng: 77.0595, type: 'Western Ghats' },
  { id: '5', name: 'Guwahati, AS', lat: 26.1400, lng: 91.7600, type: 'Urban Hills' }
];
"""
new_search = """
const SEARCH_DB = [
  { id: '2', name: 'Shimla, HP', lat: 31.1048, lng: 77.1734, type: 'Himalayan Slopes', slope: 55.0, twi: 5.2 },
  { id: '3', name: 'Darjeeling, WB', lat: 27.0360, lng: 88.2627, type: 'Steep Tea Estates', slope: 48.0, twi: 6.1 },
  { id: '4', name: 'Munnar, KL', lat: 10.0889, lng: 77.0595, type: 'Western Ghats', slope: 35.0, twi: 8.5 },
  { id: '5', name: 'Guwahati, AS', lat: 26.1400, lng: 91.7600, type: 'Urban Hills', slope: 45.0, twi: 8.2 }
];
"""
content = content.replace(old_search.strip(), new_search.strip())

# Update initial state
old_state = "const [currentZone, setCurrentZone] = useState({ id: '5', name: 'Guwahati, AS', type: 'Urban Hills', lng: 91.76, lat: 26.14 });"
new_state = "const [currentZone, setCurrentZone] = useState({ id: '5', name: 'Guwahati, AS', type: 'Urban Hills', lng: 91.76, lat: 26.14, slope: 45.0, twi: 8.2 });"
content = content.replace(old_state, new_state)

# Update handleFlyTo
old_fly = "setCurrentZone({ id: zone.id, name: zone.name, type: zone.type, lng: zone.lng, lat: zone.lat });"
new_fly = "setCurrentZone({ id: zone.id, name: zone.name, type: zone.type, lng: zone.lng, lat: zone.lat, slope: zone.slope, twi: zone.twi });"
content = content.replace(old_fly, new_fly)

# Update fetch to /simulate
old_fetch = "body: JSON.stringify({ slope_deg: 45.0, aspect_deg: 180.0, curvature: -0.5, twi: 8.0, rainfall_seq: fetchedRainData })"
new_fetch = "body: JSON.stringify({ slope_deg: currentZone.slope, aspect_deg: 180.0, curvature: -0.5, twi: currentZone.twi, rainfall_seq: fetchedRainData })"
content = content.replace(old_fetch, new_fetch)

# Update XGB Modal values (replace hardcoded 45 and 8.2)
old_xgb_val1 = '<div className="text-5xl font-black text-white tracking-tighter">45<span'
new_xgb_val1 = '<div className="text-5xl font-black text-white tracking-tighter">{currentZone.slope}<span'
content = content.replace(old_xgb_val1, new_xgb_val1)

old_xgb_val2 = '<div className="text-3xl font-black text-white tracking-tight">8.2<span className="text-lg text-red-500 ml-1"></span></div>'
new_xgb_val2 = '<div className="text-3xl font-black text-white tracking-tight">{currentZone.twi}<span className="text-lg text-red-500 ml-1"></span></div>'
content = content.replace(old_xgb_val2, new_xgb_val2)

# Update the XGB logic loop
old_loop = """{ label: 'Slope Angle', val: 45, max: 90, unit: '°', color: 'from-orange-600 to-orange-400', shadow: 'shadow-[0_0_15px_rgba(249,115,22,0.3)]' },
                         { label: 'Elevation', val: 320, max: 1000, unit: 'm', color: 'from-yellow-600 to-yellow-400', shadow: 'shadow-[0_0_15px_rgba(234,179,8,0.3)]' },
                         { label: 'Wetness Index (TWI)', val: 8.2, max: 15, unit: '', color: 'from-red-600 to-red-400', shadow: 'shadow-[0_0_15px_rgba(239,68,68,0.3)]' }"""

new_loop = """{ label: 'Slope Angle', val: currentZone.slope, max: 90, unit: '°', color: 'from-orange-600 to-orange-400', shadow: 'shadow-[0_0_15px_rgba(249,115,22,0.3)]' },
                         { label: 'Elevation', val: 320, max: 3000, unit: 'm', color: 'from-yellow-600 to-yellow-400', shadow: 'shadow-[0_0_15px_rgba(234,179,8,0.3)]' },
                         { label: 'Wetness Index (TWI)', val: currentZone.twi, max: 15, unit: '', color: 'from-red-600 to-red-400', shadow: 'shadow-[0_0_15px_rgba(239,68,68,0.3)]' }"""
content = content.replace(old_loop.strip(), new_loop.strip())

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
