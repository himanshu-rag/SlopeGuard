with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# Fix Hospital click
target_hosp = "onClick={() => { setViewState({ longitude: 91.755, latitude: 26.155, zoom: 16 }); setActiveModal('hospital'); }}"
new_hosp = "onClick={() => { setViewState({ longitude: currentZone.lng - 0.005, latitude: currentZone.lat + 0.015, zoom: 16 }); setActiveModal('hospital'); }}"
content = content.replace(target_hosp, new_hosp)

# Fix Bridge click
target_bridge = "onClick={() => { setViewState({ longitude: 91.730, latitude: 26.170, zoom: 16 }); setActiveModal('bridge'); }}"
new_bridge = "onClick={() => { setViewState({ longitude: currentZone.lng + 0.010, latitude: currentZone.lat - 0.020, zoom: 16 }); setActiveModal('bridge'); }}"
content = content.replace(target_bridge, new_bridge)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
