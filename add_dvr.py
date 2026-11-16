with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# Add DVR State
state_injection = """  const [dvrMode, setDvrMode] = useState(false);
  const [dvrEvent, setDvrEvent] = useState<string | null>(null);

  // DVR Replay Logic
  const startDvrReplay = (eventName: string) => {
    setDvrEvent(eventName);
    setDvrMode(true);
    setShowLayers(false);
    
    // Hardcode map location to the disaster site
    if (eventName === '2024 Wayanad') {
       setViewState({ longitude: 76.0822, latitude: 11.5549, zoom: 14.5 });
       setCurrentZone({ id: 'wayanad_1', name: 'Wayanad, KL', type: 'Western Ghats', lng: 76.0822, lat: 11.5549, slope: 62.0, aspect: 180, curvature: -0.9, twi: 12.5 });
    } else if (eventName === '2013 Kedarnath') {
       setViewState({ longitude: 79.0669, latitude: 30.7352, zoom: 14.0 });
       setCurrentZone({ id: 'kedar_1', name: 'Kedarnath, UK', type: 'Himalayan Slopes', lng: 79.0669, lat: 30.7352, slope: 75.0, aspect: 220, curvature: -1.2, twi: 14.0 });
    }
  };

  useEffect(() => {
    if (!dvrMode) return;
    
    // Override the live risk data with extreme historical data
    setLoading(true);
    setTimeout(() => {
       // Massive synthetic rainfall array (showing a huge spike at the end)
       const syntheticRain = Array(25).fill(10).concat([45, 90, 150, 280, 420]);
       setRainData(syntheticRain);
       setData({
         susceptibility_probability: 0.98,
         trigger_probability: 0.99,
         final_score: 98.7,
         risk_level: 'CRITICAL',
         reason_code: 'HIGH_TERRAIN_SUSCEPTIBILITY+HIGH_ANTECEDENT_RAINFALL'
       });
       setLoading(false);
       
       // Flood the telemetry queue with extreme values
       setTelemetry([
         { id: '1', node_id: 'NODE-Alpha (Crest)', type: 'GPS Displacement', val: '45.2mm', status: 'critical', time: '-1hr' },
         { id: '2', node_id: 'NODE-Beta (Mid-Slope)', type: 'Inclinometer', val: '4.5°/h', status: 'critical', time: '-1hr' },
         { id: '3', node_id: 'NODE-Gamma (Base)', type: 'Soil Moisture', val: '99.9%', status: 'critical', time: '-2hr' },
         { id: '4', node_id: 'NODE-Alpha (Crest)', type: 'GPS Displacement', val: '22.1mm', status: 'warning', time: '-4hr' },
         { id: '5', node_id: 'NODE-Beta (Mid-Slope)', type: 'Soil Moisture', val: '88.5%', status: 'warning', time: '-6hr' },
       ]);
    }, 1500);
  }, [dvrMode, dvrEvent]);
"""

content = content.replace("  const [isRouting, setIsRouting] = useState(false);", "  const [isRouting, setIsRouting] = useState(false);\n" + state_injection)

# Add DVR Button to the top nav
nav_injection = """          <div className="relative">
            <button 
              onClick={() => { setDvrMode(!dvrMode); setShowLayers(false); setShowSearch(false); if (dvrMode) setDvrEvent(null); }}
              className={`glass-button px-5 py-2.5 rounded-2xl flex items-center gap-2 transition-all hover:bg-white/10 ${dvrMode ? 'bg-red-500/20 border-red-500/50 text-red-400' : 'text-gray-300'}`}
            >
               <Radio size={18} className={dvrMode ? "animate-pulse" : ""} /> <span className="text-sm font-semibold tracking-wide">DVR Replay</span>
            </button>

            {/* DVR DROPDOWN */}
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

          <button"""

content = content.replace("          <button", nav_injection, 1)

# Modify right panel header to show DVR mode
dvr_header = """             <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                <Radio size={12} className={dvrMode ? "text-red-400 animate-pulse" : "text-blue-400 animate-pulse"} /> {dvrMode ? "DVR HISTORICAL LOG" : "Real-Time Packet Stream"}
             </h3>
             <span className={`text-[9px] font-black px-2 py-1 rounded-lg border shadow-sm ${dvrMode ? 'text-red-400 bg-red-500/10 border-red-500/20' : 'text-blue-400 bg-blue-500/10 border-blue-500/20'}`}>
                {dvrMode ? "ARCHIVE" : "TCP/IP"}
             </span>"""

content = content.replace("""             <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                <Radio size={12} className="text-blue-400 animate-pulse" /> Real-Time Packet Stream
             </h3>
             <span className="text-[9px] font-black text-blue-400 bg-blue-500/10 px-2 py-1 rounded-lg border border-blue-500/20 shadow-sm">TCP/IP</span>""", dvr_header)

# Modify Top Left Badge to show DVR mode
live_badge = """        <div className="absolute top-4 right-5 flex items-center gap-2">
          {dvrMode ? (
            <span className="flex items-center gap-1.5 text-[9px] font-black text-red-500 tracking-widest uppercase bg-red-500/10 px-2 py-1 rounded-md border border-red-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" /> REPLAYING
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-[9px] font-black text-red-500 tracking-widest uppercase bg-red-500/10 px-2 py-1 rounded-md border border-red-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" /> LIVE
            </span>
          )}
        </div>"""

content = content.replace("""        <div className="absolute top-4 right-5 flex items-center gap-2">
          <span className="flex items-center gap-1.5 text-[9px] font-black text-red-500 tracking-widest uppercase bg-red-500/10 px-2 py-1 rounded-md border border-red-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" /> LIVE
          </span>
        </div>""", live_badge)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
