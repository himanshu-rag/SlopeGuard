import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# 1. Update handleFlyTo
target_fly = """  const handleFlyTo = (zone: any) => {
    setViewState({ longitude: zone.lng, latitude: zone.lat, zoom: 15.5 });
    setCurrentZone({ id: zone.id, name: zone.name, type: zone.type, lng: zone.lng, lat: zone.lat, slope: zone.slope, aspect: zone.aspect ?? 180.0, curvature: zone.curvature ?? -0.5, twi: zone.twi });
    setShowSearch(false);
    setSearchQuery("");
  };"""

new_fly = """  const handleFlyTo = (zone: any) => {
    if (zone.isHistorical) {
      startDvrReplay(zone.eventName);
    } else {
      setDvrMode(false);
      setDvrEvent(null);
      setViewState({ longitude: zone.lng, latitude: zone.lat, zoom: 15.5 });
      setCurrentZone({ id: zone.id, name: zone.name, type: zone.type, lng: zone.lng, lat: zone.lat, slope: zone.slope, aspect: zone.aspect ?? 180.0, curvature: zone.curvature ?? -0.5, twi: zone.twi });
    }
    setShowSearch(false);
    setSearchQuery("");
  };"""

content = content.replace(target_fly, new_fly)

# 2. Update Search Menu UI
target_menu = """                <div className="mt-2 space-y-1">
                  {searchQuery && searchResults.length === 0 ? (
                    <div className="p-4 bg-white/5 rounded-xl border border-white/5 flex items-center justify-center text-xs text-gray-400">
                      No zones matching "{searchQuery}"
                    </div>
                  ) : (
                    searchResults.map(zone => (
                      <button 
                        key={zone.id}
                        onClick={() => handleFlyTo(zone)}
                        className="w-full flex items-center gap-3 p-3 hover:bg-white/10 rounded-xl transition-colors text-left"
                      >
                         <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
                           <Crosshair size={14} className="text-gray-400" />
                         </div>
                         <div>
                           <div className="text-sm font-semibold text-white">{zone.name}</div>
                           <div className="text-[10px] text-gray-500 uppercase tracking-widest mt-0.5">{zone.id} • {zone.type}</div>
                         </div>
                      </button>
                    ))
                  )}
                </div>"""

new_menu = """                <div className="mt-2 space-y-1 max-h-[300px] overflow-y-auto">
                  {(searchResults.length > 0 || globalResults.length > 0) ? (
                    <>
                      {searchResults.map(zone => (
                        <button 
                          key={zone.id}
                          onClick={() => handleFlyTo(zone)}
                          className={`w-full flex items-center gap-3 p-3 hover:bg-white/10 rounded-xl transition-colors text-left ${zone.isHistorical ? 'bg-yellow-500/10 hover:bg-yellow-500/20' : ''}`}
                        >
                           <div className="w-8 h-8 flex-shrink-0 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
                             <Crosshair size={14} className={zone.isHistorical ? 'text-yellow-500' : 'text-gray-400'} />
                           </div>
                           <div>
                             <div className={`text-sm font-semibold ${zone.isHistorical ? 'text-yellow-500' : 'text-white'}`}>{zone.name}</div>
                             <div className="text-[10px] text-gray-500 uppercase tracking-widest mt-0.5">{zone.id} • {zone.type}</div>
                           </div>
                        </button>
                      ))}
                      
                      {globalResults.length > 0 && <div className="text-[9px] font-black tracking-widest text-blue-400 pt-2 pb-1 pl-2 uppercase sticky top-0 bg-black/80 backdrop-blur-md z-10">Global Satellites</div>}
                      {globalResults.map((zone: any) => (
                        <button 
                          key={zone.id}
                          onClick={() => handleFlyTo(zone)}
                          className="w-full flex items-center gap-3 p-3 hover:bg-blue-500/10 rounded-xl transition-colors text-left group"
                        >
                           <div className="w-8 h-8 flex-shrink-0 rounded-full bg-blue-500/5 flex items-center justify-center border border-blue-500/10 group-hover:border-blue-500/30">
                             <MapPin size={14} className="text-blue-400" />
                           </div>
                           <div>
                             <div className="text-sm font-semibold text-blue-100 group-hover:text-blue-400 transition-colors">{zone.name.split(',')[0]}</div>
                             <div className="text-[10px] text-blue-500/70 uppercase tracking-widest mt-0.5">OPEN-METEO • {zone.lat.toFixed(2)}, {zone.lng.toFixed(2)}</div>
                           </div>
                        </button>
                      ))}
                    </>
                  ) : searchQuery ? (
                    <div className="p-4 bg-white/5 rounded-xl border border-white/5 flex flex-col items-center justify-center text-xs text-gray-400 gap-2">
                      {isSearching ? 'Connecting to Global Satellites...' : `No locations found for "${searchQuery}"`}
                    </div>
                  ) : null}
                </div>"""

content = content.replace(target_menu, new_menu)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
