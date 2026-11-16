import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# 1. Update the search state to hold global results
target_state = "const [searchQuery, setSearchQuery] = useState(\"\");"
new_state = """const [searchQuery, setSearchQuery] = useState("");
  const [globalResults, setGlobalResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Debounced Global Search
  useEffect(() => {
    if (searchQuery.length < 3) { setGlobalResults([]); return; }
    const timeout = setTimeout(async () => {
      setIsSearching(true);
      try {
        const res = await fetch(`https://nominatim.openstreetmap.org/search?q=${searchQuery}&format=json&limit=3`, { headers: { 'Accept-Language': 'en' }});
        const data = await res.json();
        setGlobalResults(data.map((d: any) => ({
          id: `global_${d.lat}_${d.lon}`,
          name: d.name + ', ' + (d.address?.country ?? ''),
          lat: parseFloat(d.lat),
          lng: parseFloat(d.lon),
          type: 'Global Query',
          slope: 40.0, // Assumed moderate-high slope for global tests
          aspect: 180.0,
          curvature: -0.5,
          twi: 8.0,
          isGlobal: true
        })));
      } catch (e) {}
      setIsSearching(false);
    }, 600);
    return () => clearTimeout(timeout);
  }, [searchQuery]);"""

content = content.replace(target_state, new_state)

# 2. Update Live fetch hook to support global zones
old_fetch = """    fetch(`http://127.0.0.1:8000/zones/${currentZone.id}/rainfall`).then(res => res.json()).then(fetchedRainData => {"""
new_fetch = """    // Check if it's a Global Zone or Local DB Zone
    const rainPromise = currentZone.id.startsWith('global_') 
      ? fetch(`https://api.open-meteo.com/v1/forecast?latitude=${currentZone.lat}&longitude=${currentZone.lng}&daily=rain_sum&past_days=30&forecast_days=1`)
          .then(res => res.json())
          .then(data => data.daily.rain_sum.slice(0, 30).map((r: any) => r === null ? 0 : r))
      : fetch(`http://127.0.0.1:8000/zones/${currentZone.id}/rainfall`).then(res => res.json());

    rainPromise.then(fetchedRainData => {"""
content = content.replace(old_fetch, new_fetch)

# 3. Update the search UI rendering
target_ui = """            <AnimatePresence>
              {showSearch && (
                <motion.div 
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  className="absolute top-14 left-0 w-80 glass-panel rounded-3xl p-3 overflow-hidden shadow-2xl"
                >
                  <div className="relative mb-2">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                    <input 
                      type="text" 
                      autoFocus
                      placeholder="Search zones..." 
                      className="w-full bg-black/40 text-white text-sm rounded-2xl pl-10 pr-4 py-3 focus:outline-none focus:ring-1 focus:ring-white/20 border border-white/5 placeholder-gray-500"
                      value={searchQuery}
                      onChange={e => setSearchQuery(e.target.value)}
                    />
                  </div>
                  
                  {searchResults.length > 0 ? (
                    <div className="space-y-1 max-h-64 overflow-y-auto pr-1">
                      {searchResults.map(z => ("""

new_ui = """            <AnimatePresence>
              {showSearch && (
                <motion.div 
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  className="absolute top-14 left-0 w-80 glass-panel rounded-3xl p-3 overflow-hidden shadow-2xl"
                >
                  <div className="relative mb-2">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                    <input 
                      type="text" 
                      autoFocus
                      placeholder="Search any global location..." 
                      className="w-full bg-black/40 text-white text-sm rounded-2xl pl-10 pr-4 py-3 focus:outline-none focus:ring-1 focus:ring-white/20 border border-white/5 placeholder-gray-500"
                      value={searchQuery}
                      onChange={e => setSearchQuery(e.target.value)}
                    />
                  </div>
                  
                  {(searchResults.length > 0 || globalResults.length > 0) ? (
                    <div className="space-y-1 max-h-64 overflow-y-auto pr-1 custom-scrollbar">
                      {searchResults.map(z => ("""

content = content.replace(target_ui, new_ui)

# 4. Add Global Results below Local Results
target_empty = """                    </div>
                  ) : (
                    <div className="p-4 text-center text-sm text-gray-500">
                      No zones matching "{searchQuery}"
                    </div>
                  )}"""

new_empty = """                      {globalResults.length > 0 && <div className="text-[9px] font-black tracking-widest text-blue-400/70 pt-2 pb-1 pl-2 uppercase">Global Database (OpenStreetMap)</div>}
                      {globalResults.map((z: any) => (
                        <button 
                          key={z.id}
                          onClick={() => { setDvrMode(false); setDvrEvent(null); setCurrentZone(z); setViewState({ longitude: z.lng, latitude: z.lat, zoom: 12 }); setShowSearch(false); setSearchQuery(''); }}
                          className="w-full text-left p-3 rounded-2xl hover:bg-white/10 transition-colors group flex justify-between items-center"
                        >
                          <div>
                            <div className="font-semibold text-white text-sm group-hover:text-blue-400 transition-colors">{z.name.split(',')[0]}</div>
                            <div className="text-[10px] text-gray-400 mt-0.5 tracking-wider uppercase flex items-center gap-1.5"><MapPin size={10} /> {z.lat.toFixed(2)}, {z.lng.toFixed(2)}</div>
                          </div>
                          <div className="opacity-0 group-hover:opacity-100 bg-blue-500/20 text-blue-400 text-[9px] px-2 py-1 rounded-md border border-blue-500/30">
                            TELEPORT
                          </div>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 text-center text-sm text-gray-500">
                      {isSearching ? 'Scanning global satellites...' : `No locations matching "${searchQuery}"`}
                    </div>
                  )}"""

content = content.replace(target_empty, new_empty)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
