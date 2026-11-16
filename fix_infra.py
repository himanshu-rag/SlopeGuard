with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# Replace hardcoded hospital name
target_hospital = '<div className="text-sm font-bold text-white">District Hospital</div>'
new_hospital = '<div className="text-sm font-bold text-white">{currentZone.name.split(",")[0]} Gen. Hospital</div>'
content = content.replace(target_hospital, new_hospital)

# Replace hardcoded highway name
target_highway = '<div className="text-sm font-bold text-white">Hwy Bridge 42</div>'
new_highway = '<div className="text-sm font-bold text-white">{currentZone.name.split(",")[0]} Regional Hwy</div>'
content = content.replace(target_highway, new_highway)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
