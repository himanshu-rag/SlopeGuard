import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# 1. Update SEARCH_DB to include historical events
target_db = """const SEARCH_DB = [
  { id: '2', name: 'Shimla, HP',      lat: 31.1048, lng: 77.1734, type: 'Himalayan Slopes',  slope: 55.0, aspect: 220.0, curvature: -0.8, twi: 5.2 },
  { id: '3', name: 'Darjeeling, WB',  lat: 27.0360, lng: 88.2627, type: 'Steep Tea Estates', slope: 48.0, aspect: 160.0, curvature: -0.3, twi: 6.1 },
  { id: '4', name: 'Munnar, KL',      lat: 10.0889, lng: 77.0595, type: 'Western Ghats',     slope: 35.0, aspect: 270.0, curvature:  0.2, twi: 8.5 },
  { id: '5', name: 'Guwahati, AS',    lat: 26.1400, lng: 91.7600, type: 'Urban Hills',       slope: 45.0, aspect: 140.0, curvature: -0.5, twi: 8.2 }
];"""

new_db = """const SEARCH_DB = [
  { id: '2', name: 'Shimla, HP',      lat: 31.1048, lng: 77.1734, type: 'Himalayan Slopes',  slope: 55.0, aspect: 220.0, curvature: -0.8, twi: 5.2 },
  { id: '3', name: 'Darjeeling, WB',  lat: 27.0360, lng: 88.2627, type: 'Steep Tea Estates', slope: 48.0, aspect: 160.0, curvature: -0.3, twi: 6.1 },
  { id: '4', name: 'Munnar, KL',      lat: 10.0889, lng: 77.0595, type: 'Western Ghats',     slope: 35.0, aspect: 270.0, curvature:  0.2, twi: 8.5 },
  { id: '5', name: 'Guwahati, AS',    lat: 26.1400, lng: 91.7600, type: 'Urban Hills',       slope: 45.0, aspect: 140.0, curvature: -0.5, twi: 8.2 },
  { id: 'wayanad_1', name: 'Wayanad, KL (2024)', lat: 11.5549, lng: 76.0822, type: 'Historical Event', slope: 62.0, aspect: 180, curvature: -0.9, twi: 12.5, isHistorical: true, eventName: '2024 Wayanad' },
  { id: 'kedar_1', name: 'Kedarnath, UK (2013)', lat: 30.7352, lng: 79.0669, type: 'Historical Event', slope: 75.0, aspect: 220, curvature: -1.2, twi: 14.0, isHistorical: true, eventName: '2013 Kedarnath' }
];"""

content = content.replace(target_db, new_db)

# 2. Update the onClick handler for search results
target_click = "onClick={() => { setCurrentZone(z); setViewState({ longitude: z.lng, latitude: z.lat, zoom: 14 }); setShowSearch(false); setSearchQuery(''); }}"
new_click = "onClick={() => { if (z.isHistorical) { startDvrReplay(z.eventName); } else { setDvrMode(false); setDvrEvent(null); setCurrentZone(z); setViewState({ longitude: z.lng, latitude: z.lat, zoom: 14 }); } setShowSearch(false); setSearchQuery(''); }}"

content = content.replace(target_click, new_click)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
