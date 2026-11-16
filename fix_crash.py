with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# 1. Reset zone when turning off DVR mode
target_btn = "onClick={() => { setDvrMode(!dvrMode); setShowLayers(false); setShowSearch(false); if (dvrMode) setDvrEvent(null); }}"
replacement_btn = "onClick={() => { setDvrMode(!dvrMode); setShowLayers(false); setShowSearch(false); if (dvrMode) { setDvrEvent(null); setCurrentZone(SEARCH_DB[3]); } }}"
content = content.replace(target_btn, replacement_btn)

# 2. Add array safeguard to Live Fetch
target_fetch = "setRainData(fetchedRainData);"
replacement_fetch = "setRainData(Array.isArray(fetchedRainData) ? fetchedRainData : []);"
content = content.replace(target_fetch, replacement_fetch)

# 3. Add array safeguard to reduce function just in case
target_reduce = "rainData.reduce((a, b) => a + b, 0).toFixed(1)"
replacement_reduce = "(Array.isArray(rainData) ? rainData : []).reduce((a, b) => a + b, 0).toFixed(1)"
content = content.replace(target_reduce, replacement_reduce)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
