with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# Fix sidebar Hospital
content = content.replace(
    '<div className="text-sm font-semibold text-white">District Hospital</div>',
    '<div className="text-sm font-semibold text-white">{currentZone.name.split(",")[0]} District Hospital</div>'
)

# Fix modal Hospital
content = content.replace(
    '<h3 className="text-2xl font-black text-white tracking-tight">District Hospital</h3>',
    '<h3 className="text-2xl font-black text-white tracking-tight">{currentZone.name.split(",")[0]} District Hospital</h3>'
)

# Fix sidebar Highway
content = content.replace(
    '<div className="text-sm font-semibold text-white">Hwy Bridge 42</div>',
    '<div className="text-sm font-semibold text-white">{currentZone.name.split(",")[0]} Route 42</div>'
)

# Fix modal Highway
content = content.replace(
    '<h3 className="text-2xl font-black text-white tracking-tight">Hwy Bridge 42</h3>',
    '<h3 className="text-2xl font-black text-white tracking-tight">{currentZone.name.split(",")[0]} Route 42</h3>'
)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
