import { motion, AnimatePresence } from 'framer-motion';
import { Radio, Search, Layers, MapPin, Crosshair, Activity } from 'lucide-react';
import { useState, useEffect } from 'react';

interface TopNavProps {
  dvrMode: boolean;
  dvrEvent: string | null;
  setDvrMode: (mode: boolean) => void;
  setDvrEvent: (event: string | null) => void;
  startDvrReplay: (eventName: string) => void;
  handleFlyTo: (zone: any) => void;
  onBaseMapChange: (map: 'dark' | 'satellite') => void;
  onToggleTerrain: () => void;
  onToggleFieldReports: () => void;
  onReportClick: () => void;
  onMyLocation: () => void;
  SEARCH_DB: any[];
}

export default function TopNav({
  dvrMode,
  dvrEvent,
  setDvrMode,
  setDvrEvent,
  startDvrReplay,
  handleFlyTo,
  onBaseMapChange,
  onToggleTerrain,
  onToggleFieldReports,
  onReportClick,
  onMyLocation,
  SEARCH_DB,
}: TopNavProps) {
  // DVR toggle
  const handleDvrToggle = () => {
    const turningOff = dvrMode;
    setDvrMode(!dvrMode);
    if (turningOff) {
      setDvrEvent(null);
      const guwahati = SEARCH_DB.find((z: any) => z.id === '5');
      if (guwahati) {
        handleFlyTo(guwahati);
      }
    }
  };

  // Search state
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [globalResults, setGlobalResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Layers state
  const [showLayers, setShowLayers] = useState(false);
  const [baseMap, setBaseMap] = useState<'dark' | 'satellite'>('satellite');
  const [showTerrainLayer, setShowTerrainLayer] = useState(false);
  const [showFieldReports, setShowFieldReports] = useState(true);

  // Debounced global search (Nominatim)
  useEffect(() => {
    if (searchQuery.length < 3) { setGlobalResults([]); return; }
    const timeout = setTimeout(async () => {
      setIsSearching(true);
      try {
        const res = await fetch(`https://nominatim.openstreetmap.org/search?q=${searchQuery}&format=json&limit=3`, { headers: { 'Accept-Language': 'en' } });
        const data = await res.json();
        setGlobalResults(data.filter((d: any) => d.lat && d.lon).map((d: any) => ({
          id: `global_${d.lat}_${d.lon}`,
          name: (d.display_name?.split(',').slice(0, 2).join(',') || d.name || 'Unknown Location'),
          lat: parseFloat(d.lat),
          lng: parseFloat(d.lon),
          type: 'Global Query',
          slope: 40.0,
          aspect: 180.0,
          curvature: -0.5,
          twi: 8.0,
          isGlobal: true
        })));
      } catch (e) {}
      setIsSearching(false);
    }, 600);
    return () => clearTimeout(timeout);
  }, [searchQuery]);

  const searchResults = SEARCH_DB.filter((z: any) =>
    z.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    z.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Sync local layer state with parent callbacks
  useEffect(() => {
    onBaseMapChange(baseMap);
  }, [baseMap, onBaseMapChange]);

  useEffect(() => {
    onToggleTerrain();
  }, [showTerrainLayer, onToggleTerrain]);

  useEffect(() => {
    onToggleFieldReports();
  }, [showFieldReports, onToggleFieldReports]);

  return (
    <nav className="absolute top-0 w-full z-50 px-6 py-6 flex items-center justify-between pointer-events-none">
      <div className="flex items-center gap-4 glass-panel px-5 py-3 rounded-2xl pointer-events-auto">
        <div className="bg-red-500/20 p-2.5 rounded-xl border border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.2)]">
          <Radio size={22} className="text-red-500" />
        </div>
        <div>
          <h1 className="font-extrabold text-base tracking-wide text-white">SlopeGuard</h1>
          <p className="text-[10px] text-gray-400 font-semibold tracking-widest uppercase">Risk Intelligence</p>
        </div>
      </div>

      <div className="flex gap-3 pointer-events-auto relative">
        <div className="relative">
          <button
            onClick={handleDvrToggle}
            className={`glass-button px-5 py-2.5 rounded-2xl flex items-center gap-2 transition-all hover:bg-white/10 ${dvrMode ? 'bg-red-500/20 border-red-500/50 text-red-400' : 'text-gray-300'}`}
          >
            <Radio size={18} className={dvrMode ? "animate-pulse" : ""} /> <span className="text-sm font-semibold tracking-wide">DVR Replay</span>
          </button>

          <AnimatePresence>
            {dvrMode && !dvrEvent && (
              <motion.div
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                className="absolute top-14 left-0 w-64 glass-panel rounded-3xl p-3"
              >
                <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest px-2 py-2">Select Historical Event</h4>
                <div className="space-y-1">
                  <button onClick={() => startDvrReplay('2024 Wayanad')} className="w-full text-left px-3 py-3 rounded-xl hover:bg-white/10 text-sm font-semibold text-white transition-all flex justify-between items-center group">
                    2024 Wayanad Landslides <span className="opacity-0 group-hover:opacity-100 text-red-400 text-[10px] tracking-widest font-black uppercase">Play</span>
                  </button>
                  <button onClick={() => startDvrReplay('2013 Kedarnath')} className="w-full text-left px-3 py-3 rounded-xl hover:bg-white/10 text-sm font-semibold text-white transition-all flex justify-between items-center group">
                    2013 Kedarnath Floods <span className="opacity-0 group-hover:opacity-100 text-red-400 text-[10px] tracking-widest font-black uppercase">Play</span>
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* SEARCH BUTTON */}
        <button
          onClick={() => { setShowSearch(!showSearch); setShowLayers(false); }}
          className={`glass-button px-5 py-2.5 rounded-2xl flex items-center gap-2 transition-all hover:bg-white/10 ${showSearch ? 'bg-white/10 border-white/30 text-white' : 'text-gray-300'}`}
        >
          <Search size={18} /> <span className="text-sm font-semibold tracking-wide">Search</span>
        </button>

        {/* LAYERS BUTTON */}
        <button
          onClick={() => { setShowLayers(!showLayers); setShowSearch(false); }}
          className={`glass-button px-5 py-2.5 rounded-2xl flex items-center gap-2 transition-all hover:bg-white/10 ${showLayers ? 'bg-white/10 border-white/30 text-white' : 'text-gray-300'}`}
        >
          <Layers size={18} /> <span className="text-sm font-semibold tracking-wide">Map Layers</span>
        </button>

        {/* FIELD REPORT BUTTON */}
        <button
          onClick={() => { onReportClick(); setShowSearch(false); setShowLayers(false); }}
          className="glass-button px-5 py-2.5 rounded-2xl flex items-center gap-2 transition-all hover:bg-white/10 border-red-500/30 text-red-400 hover:bg-red-500/10"
        >
          <Activity size={18} className="animate-pulse" /> <span className="text-sm font-semibold tracking-wide">Field Report</span>
        </button>

        {/* MY LOCATION BUTTON */}
        <button
          onClick={onMyLocation}
          className="glass-button px-5 py-2.5 rounded-2xl flex items-center gap-2 transition-all hover:bg-white/10 border-blue-500/30 text-blue-400 hover:bg-blue-500/10"
        >
          <MapPin size={18} className="animate-pulse" /> <span className="text-sm font-semibold tracking-wide">My Location</span>
        </button>

        {/* SEARCH MODAL */}
        <AnimatePresence>
          {showSearch && (
            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              className="absolute top-16 right-36 w-80 glass-panel rounded-3xl p-3"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="relative">
                <Search className="absolute left-4 top-3.5 text-gray-400" size={16} />
                <input
                  type="text"
                  placeholder="Search coordinates or zones..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-black/50 border border-white/10 rounded-2xl py-3 pl-11 pr-4 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-red-500/50 transition-colors shadow-inner"
                />
              </div>

              <div className="mt-2 space-y-1 max-h-[300px] overflow-y-auto">
                {(searchResults.length > 0 || globalResults.length > 0) ? (
                  <>
                    {searchResults.map((zone: any) => (
                      <button
                        key={zone.id}
                        onClick={() => { handleFlyTo(zone); setShowSearch(false); setSearchQuery(""); }}
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

                    {globalResults.length > 0 && <div className="text-[9px] font-bold tracking-widest text-blue-400 pt-2 pb-1 pl-2 uppercase sticky top-0 bg-black/80 backdrop-blur-md z-10">Global Satellites</div>}
                    {globalResults.map((zone: any) => (
                      <button
                        key={zone.id}
                        onClick={() => { handleFlyTo(zone); setShowSearch(false); setSearchQuery(""); }}
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
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* LAYERS MODAL */}
        <AnimatePresence>
          {showLayers && (
            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              className="absolute top-16 right-0 w-72 glass-panel rounded-3xl p-3"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="px-3 py-2 text-[10px] font-bold text-gray-400 uppercase tracking-widest">Base Maps</div>
              <button onClick={() => { setBaseMap('dark'); onBaseMapChange('dark'); }} className={`w-full flex items-center justify-between p-3.5 rounded-2xl border text-sm transition-colors mb-2 ${baseMap === 'dark' ? 'bg-white/10 border-white/20 text-white shadow-inner' : 'border-transparent text-gray-400 hover:bg-white/5'}`}>
                <span className="font-medium">Dark Raster (OSM)</span>
                {baseMap === 'dark' && <div className="w-5 h-5 rounded-full bg-blue-400" />}
              </button>
              <button onClick={() => { setBaseMap('satellite'); onBaseMapChange('satellite'); }} className={`w-full flex items-center justify-between p-3.5 rounded-2xl border text-sm transition-colors ${baseMap === 'satellite' ? 'bg-white/10 border-white/20 text-white shadow-inner' : 'border-transparent text-gray-400 hover:bg-white/5'}`}>
                <span className="font-medium">Satellite Hybrid</span>
                {baseMap === 'satellite' && <div className="w-5 h-5 rounded-full bg-blue-400" />}
              </button>
              <div className="px-3 py-2 text-[10px] font-bold text-gray-400 uppercase tracking-widest mt-3">Overlays</div>
              <button onClick={() => { setShowTerrainLayer(!showTerrainLayer); onToggleTerrain(); }} className="w-full flex items-center justify-between p-3.5 hover:bg-white/5 rounded-2xl text-sm text-white transition-colors">
                <span className="font-medium">Terrain Susceptibility</span>
                <div className={`w-11 h-6 rounded-full relative transition-colors border border-white/10 ${showTerrainLayer ? 'bg-red-500' : 'bg-black/50'}`}>
                  <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all shadow-sm ${showTerrainLayer ? 'left-6' : 'left-1'}`} />
                </div>
              </button>
              <button onClick={() => { setShowFieldReports(!showFieldReports); onToggleFieldReports(); }} className="w-full flex items-center justify-between p-3.5 hover:bg-white/5 rounded-2xl text-sm text-white transition-colors">
                <span className="font-medium">Field Reports</span>
                <div className={`w-11 h-6 rounded-full relative transition-colors border border-white/10 ${showFieldReports ? 'bg-blue-500' : 'bg-black/50'}`}>
                  <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all shadow-sm ${showFieldReports ? 'left-6' : 'left-1'}`} />
                </div>
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </nav>
  );
}

