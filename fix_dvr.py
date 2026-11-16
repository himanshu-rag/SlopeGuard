with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

target = "useEffect(() => {\\n    setLoading(true);"
replacement = "useEffect(() => {\\n    if (dvrMode) return;\\n    setLoading(true);"

content = content.replace(target, replacement)

# We also need to add dvrMode to the dependency array
target_deps = "}, [currentZone.id]);"
replacement_deps = "}, [currentZone.id, dvrMode]);"

content = content.replace(target_deps, replacement_deps)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
