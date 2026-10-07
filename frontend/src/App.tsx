import React, { useEffect, useState, useRef } from 'react';
import Map, { NavigationControl, Source, Layer, useMap } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import { Activity, ShieldAlert, TrendingUp, MapPin, Search, AlertTriangle, Layers, CloudRain, Check, Radio, Thermometer, Crosshair, X, Phone, Ambulance, Shield, Navigation, Wifi, Battery, Cpu } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

const osmStyle = {
  version: 8,
  sources: { 'osm': { type: 'raster', tiles: ['https://a.tile.openstreetmap.org/{z}/{x}/{y}.png', 'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png', 'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png'], tileSize: 256, attribution: '&copy; OpenStreetMap Contributors' } },
  layers: [{ id: 'osm-layer', type: 'raster', source: 'osm', minzoom: 0, maxzoom: 19 }]
};

const satelliteStyle = {
  version: 8,
  sources: { 'satellite': { type: 'raster', tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'], tileSize: 256, attribution: '&copy; Esri', maxzoom: 17 } },
  layers: [{ id: 'satellite-layer', type: 'raster', source: 'satellite', minzoom: 0 }]
};



const SEARCH_DB = [
  { id: '2', name: 'Shimla, HP',      lat: 31.1048, lng: 77.1734, type: 'Himalayan Slopes',  slope: 55.0, aspect: 220.0, curvature: -0.8, twi: 5.2 },
  { id: '3', name: 'Darjeeling, WB',  lat: 27.0360, lng: 88.2627, type: 'Steep Tea Estates', slope: 48.0, aspect: 160.0, curvature: -0.3, twi: 6.1 },
  { id: '4', name: 'Munnar, KL',      lat: 10.0889, lng: 77.0595, type: 'Western Ghats',     slope: 35.0, aspect: 270.0, curvature:  0.2, twi: 8.5 },
  { id: '5', name: 'Guwahati, AS',    lat: 26.1400, lng: 91.7600, type: 'Urban Hills',       slope: 45.0, aspect: 140.0, curvature: -0.5, twi: 8.2 }
];

function App() {
  const [data, setData] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [loading, setLoading] = useState(true);
  const [showLayers, setShowLayers] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeModal, setActiveModal] = useState<'lstm' | 'xgb' | null>(null);

  const [baseMap, setBaseMap] = useState<'dark' | 'satellite'>('satellite');
  const [showTerrainLayer, setShowTerrainLayer] = useState(false);
  const [showFieldReports, setShowFieldReports] = useState(true);

  const [telemetry, setTelemetry] = useState<any[]>([]);
  const [rainData, setRainData] = useState<number[]>([]);
  
  // Controlled Map State
  const [viewState, setViewState] = useState({ longitude: 91.76, latitude: 26.14, zoom: 14 });
  const [currentZone, setCurrentZone] = useState({ id: '5', name: 'Guwahati, AS', type: 'Urban Hills', lng: 91.76, lat: 26.14, slope: 45.0, aspect: 140.0, curvature: -0.5, twi: 8.2 });

  useEffect(() => {
    setLoading(true);
    fetch(`http://127.0.0.1:8000/zones/${currentZone.id}/rainfall`).then(res => res.json()).then(fetchedRainData => {
         setRainData(fetchedRainData);
         return fetch(`${API_BASE}/simulate`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ slope_deg: currentZone.slope, aspect_deg: currentZone.aspect ?? 180.0, curvature: currentZone.curvature ?? -0.5, twi: currentZone.twi, rainfall_seq: fetchedRainData })
          });
      }).then(res => res.json()).then(res => { setData(res); setLoading(false); }).catch(() => setLoading(false));
      
    // FIX #11: Close previous connection before opening a new one (prevents memory leak)
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }
    const ws = new WebSocket(`${API_BASE.replace("http", "ws")}/ws/telemetry/${currentZone.id}`);
    wsRef.current = ws;
    ws.onmessage = (event) => { setTelemetry(prev => [JSON.parse(event.data), ...prev].slice(0, 5)); };
    return () => { ws.close(); wsRef.current = null; };
  }, [currentZone.id]);

  const searchResults = SEARCH_DB.filter(z => 
    z.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    z.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleFlyTo = (zone: any) => {
    setViewState({ longitude: zone.lng, latitude: zone.lat, zoom: 15.5 });
    setCurrentZone({ id: zone.id, name: zone.name, type: zone.type, lng: zone.lng, lat: zone.lat, slope: zone.slope, aspect: zone.aspect ?? 180.0, curvature: zone.curvature ?? -0.5, twi: zone.twi });
    setShowSearch(false);
    setSearchQuery("");
  };


  const d = 0.015;
  const dynamicTerrain = {
    type: 'FeatureCollection',
    features: [{ type: 'Feature', geometry: { type: 'Polygon', coordinates: [[[currentZone.lng - d, currentZone.lat - d], [currentZone.lng + d, currentZone.lat - d], [currentZone.lng + d, currentZone.lat + d], [currentZone.lng - d, currentZone.lat + d], [currentZone.lng - d, currentZone.lat - d]]] } }]
  };
  const dynamicReports = {
    type: 'FeatureCollection',
    features: [
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng - 0.005, currentZone.lat + 0.005] } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng + 0.008, currentZone.lat - 0.002] } }
    ]
  };


  const dynamicNodes = {
    type: 'FeatureCollection',
    features: [
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng - 0.003, currentZone.lat + 0.005] }, properties: { name: 'NODE-Alpha', status: 'online' } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng + 0.001, currentZone.lat + 0.001] }, properties: { name: 'NODE-Beta', status: 'online' } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng + 0.004, currentZone.lat - 0.004] }, properties: { name: 'NODE-Gamma', status: 'offline' } }
    ]
  };

  return (
    <div className="relative w-screen h-screen bg-[#0a0a0a]">
      <style>{`
        .dark-map-layer .maplibregl-canvas { filter: invert(100%) hue-rotate(180deg) brightness(85%) contrast(110%); }
        .glass-panel { background: rgba(17, 17, 17, 0.75); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
        .glass-button { background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }
      `}</style>

      {/* FULL SCREEN MAP */}
      <div className={`absolute inset-0 z-0 ${baseMap === 'dark' ? 'dark-map-layer' : ''}`}>
        <Map
          {...viewState}
          onMove={evt => setViewState(evt.viewState)}
          mapStyle={baseMap === 'dark' ? osmStyle as any : satelliteStyle as any}
          style={{ width: '100%', height: '100%' }}
        >
          {showTerrainLayer && (
            <Source id="terrain" type="geojson" data={dynamicTerrain as any}>
              <Layer id="terrain-fill" type="fill" paint={{ 'fill-color': '#ef4444', 'fill-opacity': 0.3 }} />
              <Layer id="terrain-line" type="line" paint={{ 'line-color': '#ef4444', 'line-width': 2, 'line-dasharray': [2, 2] }} />
            </Source>
          )}

          {showFieldReports && (
            <Source id="reports" type="geojson" data={dynamicReports as any}>
              <Layer 
                id="reports-circle" type="circle" 
                paint={{ 'circle-radius': 8, 'circle-color': '#3b82f6', 'circle-stroke-width': 3, 'circle-stroke-color': '#ffffff' }} 
              />
            </Source>
          )}

          {/* HARDWARE IOT NODES (ALWAYS VISIBLE) */}
          <Source id="iot-nodes" type="geojson" data={dynamicNodes as any}>
            <Layer 
              id="nodes-circle" type="circle" 
              paint={{ 
                'circle-radius': 6, 
                'circle-color': ['match', ['get', 'status'], 'online', '#22c55e', '#ef4444', '#ef4444'], 
                'circle-stroke-width': 2, 
                'circle-stroke-color': '#000000' 
              }} 
            />
            <Layer
              id="nodes-label" type="symbol"
              layout={{
                'text-field': ['get', 'name'],
                'text-size': 11,
                'text-offset': [0, 1.2],
                'text-anchor': 'top'
              }}
              paint={{
                'text-color': '#ffffff',
                'text-halo-color': '#000000',
                'text-halo-width': 2
              }}
            />
          </Source>
        </Map>
      </div>

      {/* TOP NAVIGATION BAR */}
      <nav className="absolute top-0 w-full z-50 px-6 py-6 flex items-center justify-between pointer-events-none">
        <div className="flex items-center gap-4 glass-panel px-5 py-3 rounded-2xl pointer-events-auto">
          <div className="bg-red-500/20 p-2.5 rounded-xl border border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.2)]">
            <ShieldAlert className="text-red-500" size={22} />
          </div>
          <div>
            <h1 className="font-extrabold text-base tracking-wide text-white">SlopeGuard</h1>
            <p className="text-[10px] text-gray-400 font-semibold tracking-widest uppercase">Risk Intelligence</p>
          </div>
        </div>

        <div className="flex gap-3 pointer-events-auto relative">
          <button 
            onClick={() => { setShowSearch(!showSearch); setShowLayers(false); }}
            className={`glass-button px-5 py-2.5 rounded-2xl flex items-center gap-2 transition-all hover:bg-white/10 ${showSearch ? 'bg-white/10 border-white/30 text-white' : 'text-gray-300'}`}
          >
             <Search size={18} /> <span className="text-sm font-semibold tracking-wide">Search</span>
          </button>
          
          <button 
            onClick={() => { setShowLayers(!showLayers); setShowSearch(false); }}
            className={`glass-button px-5 py-2.5 rounded-2xl flex items-center gap-2 transition-all hover:bg-white/10 ${showLayers ? 'bg-white/10 border-white/30 text-white' : 'text-gray-300'}`}
          >
             <Layers size={18} /> <span className="text-sm font-semibold tracking-wide">Map Layers</span>
          </button>

          {/* SEARCH MODAL */}
          <AnimatePresence>
            {showSearch && (
              <motion.div 
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                className="absolute top-16 right-36 w-80 glass-panel rounded-3xl p-3"
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
                
                <div className="mt-2 space-y-1">
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
              >
                 <div className="px-3 py-2 text-[10px] font-bold text-gray-400 uppercase tracking-widest">Base Maps</div>
                 <button onClick={() => setBaseMap('dark')} className={`w-full flex items-center justify-between p-3.5 rounded-2xl border text-sm transition-colors mb-2 ${baseMap === 'dark' ? 'bg-white/10 border-white/20 text-white shadow-inner' : 'border-transparent text-gray-400 hover:bg-white/5'}`}>
                   <span className="font-medium">Dark Raster (OSM)</span>
                   {baseMap === 'dark' && <Check size={16} className="text-blue-400" />}
                 </button>
                 <button onClick={() => setBaseMap('satellite')} className={`w-full flex items-center justify-between p-3.5 rounded-2xl border text-sm transition-colors ${baseMap === 'satellite' ? 'bg-white/10 border-white/20 text-white shadow-inner' : 'border-transparent text-gray-400 hover:bg-white/5'}`}>
                   <span className="font-medium">Satellite Hybrid</span>
                   {baseMap === 'satellite' && <Check size={16} className="text-blue-400" />}
                 </button>
                 <div className="px-3 py-2 text-[10px] font-bold text-gray-400 uppercase tracking-widest mt-3">Overlays</div>
                 <button onClick={() => setShowTerrainLayer(!showTerrainLayer)} className="w-full flex items-center justify-between p-3.5 hover:bg-white/5 rounded-2xl text-sm text-white transition-colors">
                   <span className="font-medium">Terrain Susceptibility</span>
                   <div className={`w-11 h-6 rounded-full relative transition-colors border border-white/10 ${showTerrainLayer ? 'bg-red-500' : 'bg-black/50'}`}>
                      <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all shadow-sm ${showTerrainLayer ? 'left-6' : 'left-1'}`} />
                   </div>
                 </button>
                 <button onClick={() => setShowFieldReports(!showFieldReports)} className="w-full flex items-center justify-between p-3.5 hover:bg-white/5 rounded-2xl text-sm text-white transition-colors">
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

      {/* LEFT PANEL: RISK ANALYSIS */}
      <AnimatePresence>
        <motion.aside 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="absolute top-28 left-6 z-10 w-96 flex flex-col gap-5 pointer-events-auto"
        >
          {/* MAIN SCORE CARD */}
          <div className="glass-panel rounded-[2rem] p-6 relative overflow-hidden">
            <div className="absolute -top-24 -right-24 w-48 h-48 bg-red-500/20 blur-[50px] rounded-full pointer-events-none" />
            <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-red-500 via-orange-500 to-transparent" />
            
            <div className="flex justify-between items-start mb-8 relative z-10">
              <div>
                <h2 className="text-xl font-extrabold text-white tracking-tight">{currentZone.name}</h2>
                <div className="flex items-center gap-1.5 text-xs text-gray-400 mt-1.5 font-medium">
                  <MapPin size={14} /> Zone ID: ZN-{currentZone.id} • {currentZone.type}
                </div>
              </div>
              <div className="flex items-center gap-2 bg-red-500/10 text-red-400 px-3 py-1.5 rounded-full text-[10px] font-bold tracking-widest uppercase border border-red-500/20 shadow-[0_0_10px_rgba(239,68,68,0.1)]">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" /> Live
              </div>
            </div>

            {loading ? (
              <div className="h-32 flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500" />
              </div>
            ) : data ? (
              <div className="space-y-6 relative z-10">
                <div className="flex items-end gap-4">
                  <div className="text-7xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-white to-gray-400 drop-shadow-sm">
                    {data.final_score?.toFixed(1)}
                  </div>
                  <div className="pb-3">
                    <div className="text-sm font-bold text-red-400 tracking-wide">{data.risk_level} RISK</div>
                    <div className="text-[10px] text-gray-500 uppercase tracking-widest mt-1 font-semibold">AI Confidence: High</div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <motion.button whileHover={{ y: -4, scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={() => setActiveModal('lstm')} className="bg-black/40 border border-white/5 rounded-2xl p-4 relative overflow-hidden group hover:bg-black/60 transition-colors text-left focus:outline-none">
                    <div className="flex items-center justify-between mb-3 relative z-10">
                      <div className="flex items-center gap-2">
                        <CloudRain size={16} className="text-blue-400" />
                        <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Trigger (LSTM)</span>
                      </div>
                    </div>
                    <div className="flex items-end justify-between relative z-10">
                      <div className="text-2xl font-bold text-white tracking-tight">{(data.trigger_probability * 100)?.toFixed(1)}%</div>
                      <div className="flex items-center gap-1 text-[9px] font-bold text-red-400 bg-red-500/10 px-1.5 py-0.5 rounded-md border border-red-500/20 shadow-sm">
                        <TrendingUp size={10} /> +4.2%
                      </div>
                    </div>
                    <svg className="absolute bottom-0 left-0 w-full h-12 opacity-30 group-hover:opacity-50 transition-opacity" viewBox="0 0 100 30" preserveAspectRatio="none">
                      <path d="M0,30 L0,25 L10,28 L20,20 L30,22 L40,15 L50,18 L60,10 L70,12 L80,5 L90,8 L100,2 L100,30 Z" fill="url(#blue-gradient)" />
                      <defs>
                        <linearGradient id="blue-gradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#3b82f6" />
                          <stop offset="100%" stopColor="transparent" />
                        </linearGradient>
                      </defs>
                    </svg>
                  </motion.button>
                  
                  <motion.button whileHover={{ y: -4, scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={() => setActiveModal('xgb')} className="bg-black/40 border border-white/5 rounded-2xl p-4 relative overflow-hidden group hover:bg-black/60 transition-colors text-left focus:outline-none">
                    <div className="flex items-center gap-2 mb-3 relative z-10">
                      <Activity size={16} className="text-orange-400" />
                      <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Terrain (XGB)</span>
                    </div>
                    <div className="flex items-end justify-between relative z-10">
                      <div className="text-2xl font-bold text-white tracking-tight">{(data.susceptibility_probability * 100)?.toFixed(1)}%</div>
                      <div className="text-[9px] font-bold text-gray-500 bg-white/5 px-1.5 py-0.5 rounded-md border border-white/10 shadow-sm">
                        STATIC
                      </div>
                    </div>
                    <svg className="absolute bottom-0 left-0 w-full h-12 opacity-20 group-hover:opacity-40 transition-opacity" viewBox="0 0 100 30" preserveAspectRatio="none">
                      <path d="M0,30 L0,15 L15,10 L30,20 L45,5 L60,12 L75,8 L90,25 L100,20 L100,30 Z" fill="url(#orange-gradient)" />
                      <defs>
                        <linearGradient id="orange-gradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#f97316" />
                          <stop offset="100%" stopColor="transparent" />
                        </linearGradient>
                      </defs>
                    </svg>
                  </motion.button>
                </div>

                <motion.button 
                  whileHover={{ y: -2, scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setActiveModal('factor')}
                  className="w-full bg-red-500/10 border border-red-500/20 rounded-2xl p-4 flex gap-4 items-start hover:bg-red-500/20 transition-all text-left focus:outline-none shadow-[0_0_15px_rgba(239,68,68,0.1)] hover:shadow-[0_0_20px_rgba(239,68,68,0.2)] group"
                >
                  <div className="p-2 bg-red-500/20 rounded-lg group-hover:bg-red-500/30 transition-colors">
                     <AlertTriangle className="text-red-400 shrink-0" size={16} />
                  </div>
                  <div>
                    <h4 className="text-[10px] font-black text-red-400 uppercase tracking-widest mb-1">Primary Factor</h4>
                    <p className="text-xs text-red-300 font-bold tracking-wide">
                      {data.reason_code?.replace(/_/g, ' ') || 'AWAITING TELEMETRY'}
                    </p>
                  </div>
                </motion.button>
              </div>
            ) : null}
          </div>

          {/* INFRASTRUCTURE CARD */}
          <div className="glass-panel rounded-[2rem] p-6">
            <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-5">Critical Infrastructure at Risk</h3>
            <div className="space-y-3">
              <motion.button 
                whileHover={{ y: -3, scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => { setViewState({ longitude: 91.755, latitude: 26.155, zoom: 16 }); setActiveModal('hospital'); }}
                className="w-full flex items-center justify-between bg-black/40 p-3.5 rounded-2xl border border-white/5 hover:bg-white/10 hover:border-white/20 transition-all text-left focus:outline-none"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center shadow-[0_0_10px_rgba(59,130,246,0.2)]">
                    <Activity size={16} className="text-blue-400" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white">District Hospital</div>
                    <div className="text-[10px] text-gray-500 mt-0.5 uppercase tracking-wider font-bold">Medical Facility • 2.1km</div>
                  </div>
                </div>
                <div className="text-[9px] font-black text-red-400 bg-red-500/10 border border-red-500/20 px-2.5 py-1.5 rounded-lg tracking-widest shadow-sm">100% EXPOSURE</div>
              </motion.button>

              <motion.button 
                whileHover={{ y: -3, scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => { setViewState({ longitude: 91.730, latitude: 26.170, zoom: 16 }); setActiveModal('bridge'); }}
                className="w-full flex items-center justify-between bg-black/40 p-3.5 rounded-2xl border border-white/5 hover:bg-white/10 hover:border-white/20 transition-all text-left focus:outline-none"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center shadow-[0_0_10px_rgba(249,115,22,0.2)]">
                    <Layers size={16} className="text-orange-400" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white">Hwy Bridge 42</div>
                    <div className="text-[10px] text-gray-500 mt-0.5 uppercase tracking-wider font-bold">Transit Route • 0.8km</div>
                  </div>
                </div>
                <div className="text-[9px] font-black text-orange-400 bg-orange-500/10 border border-orange-500/20 px-2.5 py-1.5 rounded-lg tracking-widest shadow-sm">EVAC ROUTE</div>
              </motion.button>
            </div>
          </div>
        </motion.aside>
      </AnimatePresence>

      {/* RIGHT PANEL: LIVE TELEMETRY FEED */}
      <aside className="absolute top-28 right-6 z-10 w-[280px] pointer-events-auto flex flex-col gap-3">
        
        {/* HARDWARE STATUS GRID */}
        <div className="flex gap-2 w-full">
           <div className="flex-1 glass-panel bg-black/60 rounded-2xl p-3 border border-white/10 shadow-lg relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-[2px] bg-green-500" />
              <div className="flex justify-between items-start mb-1.5">
                 <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)] animate-pulse" />
                 <Wifi size={10} className="text-green-400" />
              </div>
              <div className="text-[10px] font-black text-white tracking-tight">NODE-A</div>
              <div className="text-[8px] text-gray-400 font-bold tracking-widest uppercase mt-0.5">Crest</div>
           </div>
           <div className="flex-1 glass-panel bg-black/60 rounded-2xl p-3 border border-white/10 shadow-lg relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-[2px] bg-green-500" />
              <div className="flex justify-between items-start mb-1.5">
                 <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)] animate-pulse" />
                 <Wifi size={10} className="text-green-400" />
              </div>
              <div className="text-[10px] font-black text-white tracking-tight">NODE-B</div>
              <div className="text-[8px] text-gray-400 font-bold tracking-widest uppercase mt-0.5">Mid</div>
           </div>
           <div className="flex-1 glass-panel bg-red-900/20 rounded-2xl p-3 border border-red-500/30 shadow-lg relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-[2px] bg-red-500" />
              <div className="flex justify-between items-start mb-1.5">
                 <div className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]" />
                 <Wifi size={10} className="text-red-400 opacity-50" />
              </div>
              <div className="text-[10px] font-black text-gray-300 tracking-tight">NODE-G</div>
              <div className="text-[8px] text-red-400 font-bold tracking-widest uppercase mt-0.5">Base</div>
           </div>
        </div>

        <div className="glass-panel rounded-[1.5rem] p-4 flex-1">
           <div className="flex items-center justify-between mb-5">
             <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                <Radio size={12} className="text-blue-400 animate-pulse" /> Real-Time Packet Stream
             </h3>
             <span className="text-[9px] font-black text-blue-400 bg-blue-500/10 px-2 py-1 rounded-lg border border-blue-500/20 shadow-sm">TCP/IP</span>
           </div>
           
           <div className="space-y-3">
             <AnimatePresence>
               {telemetry.map(t => (
                 <motion.div 
                   key={t.id}
                   initial={{ opacity: 0, x: 20, height: 0, marginBottom: 0 }}
                   animate={{ opacity: 1, x: 0, height: 'auto', marginBottom: 12 }}
                   className="bg-gradient-to-r from-black/60 to-black/30 border border-white/10 p-4 rounded-[1.25rem] flex items-center justify-between group hover:border-white/20 transition-all relative overflow-hidden shadow-lg"
                 >
                   {t.status === 'warning' && (
                     <div className="absolute inset-0 bg-orange-500/10 opacity-60 pointer-events-none" />
                   )}
                   
                   <div className="flex items-center gap-4 relative z-10">
                     <div className="relative flex h-2.5 w-2.5">
                       {t.status === 'warning' ? (
                          <>
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-orange-500 shadow-[0_0_12px_rgba(249,115,22,1)]"></span>
                          </>
                       ) : (
                          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.8)]"></span>
                       )}
                     </div>
                     <div>
                       <div className="flex items-center gap-2 mb-0.5">
                          <Cpu size={10} className="text-gray-500" />
                          <div className="text-[9px] font-black text-gray-400 uppercase tracking-widest">{t.node_id || 'NODE-Alpha'}</div>
                       </div>
                       <div className="text-[13px] font-bold text-white tracking-tight leading-none">{t.type}</div>
                     </div>
                   </div>
                   
                   <div className={`relative z-10 text-sm font-mono font-bold px-3 py-1.5 rounded-xl border flex items-center justify-center min-w-[75px] shadow-inner transition-colors ${t.status === 'warning' ? 'bg-orange-500/15 text-orange-400 border-orange-500/30 shadow-[0_0_10px_rgba(249,115,22,0.2)]' : 'bg-black/60 text-gray-300 border-white/10'}`}>
                     {t.val}
                   </div>
                 </motion.div>
               ))}
             </AnimatePresence>
             {telemetry.length === 0 && (
                <div className="text-xs text-gray-500 text-center py-4">Connecting to WebSocket...</div>
             )}
           </div>
        </div>
      </aside>

      {/* DETAILS MODAL */}
      <AnimatePresence>
        {activeModal && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-[100] flex items-center justify-center bg-black/30 backdrop-blur-[2px] p-4 pointer-events-auto"
            onClick={() => setActiveModal(null)}
          >
            <motion.div 
              initial={{ scale: 0.9, y: 20, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.9, y: 20, opacity: 0 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="glass-panel rounded-[2rem] p-7 w-[480px] relative overflow-hidden shadow-2xl"
              onClick={e => e.stopPropagation()}
            >
              <button 
                onClick={() => setActiveModal(null)}
                className="absolute top-4 right-4 text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 p-2 rounded-full transition-colors"
              >
                <X size={16} />
              </button>

              {activeModal === 'lstm' && (
                 <div>
                    <div className="flex items-center gap-3 mb-8">
                      <div className="p-3 bg-blue-500/20 rounded-2xl border border-blue-500/30">
                         <CloudRain size={24} className="text-blue-400" />
                      </div>
                      <div>
                         <h3 className="text-xl font-black text-white tracking-tight">LSTM Trigger Analysis</h3>
                         <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">7-Day Rainfall Accumulation</p>
                      </div>
                    </div>
                    
                    <div className="flex items-end gap-3 h-40 mt-4 px-2">
                       {rainData.slice(-7).map((val, i) => (
                         <div key={i} className="flex-1 flex flex-col items-center justify-end group relative h-full">
                            <div className="absolute -top-7 text-[10px] font-bold text-white bg-black/80 px-2 py-1 rounded border border-white/10 opacity-0 group-hover:opacity-100 transition-opacity shadow-lg">{val.toFixed(1)}mm</div>
                            <motion.div 
                               initial={{ height: 0 }}
                               animate={{ height: `${Math.max(8, (val / Math.max(...rainData.slice(-7), 50)) * 100)}%` }}
                               transition={{ delay: i * 0.1, type: "spring", stiffness: 100 }}
                               className="w-full bg-gradient-to-t from-blue-600/40 to-blue-400/80 rounded-t-lg hover:to-blue-400 transition-all cursor-pointer shadow-[0_0_15px_rgba(59,130,246,0.2)]"
                            />
                            <div className="text-[9px] text-gray-500 font-extrabold uppercase mt-3">T-{6-i}</div>
                         </div>
                       ))}
                    </div>
                 </div>
              )}


              {activeModal === 'hospital' && (
                 <div className="flex flex-col h-full">
                    <div className="flex items-center justify-between mb-8 pb-6 border-b border-white/10">
                      <div className="flex items-center gap-4">
                        <div className="p-4 bg-blue-500/20 rounded-[1.25rem] border border-blue-500/30 shadow-[0_0_20px_rgba(59,130,246,0.3)]">
                           <Activity size={28} className="text-blue-400" />
                        </div>
                        <div>
                           <h3 className="text-2xl font-black text-white tracking-tight">District Hospital</h3>
                           <p className="text-[10px] text-red-400 font-black uppercase tracking-[0.2em] mt-1">100% Slide Exposure</p>
                        </div>
                      </div>
                      <div className="text-right">
                         <div className="text-3xl font-black text-white">450</div>
                         <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Active Beds</div>
                      </div>
                    </div>
                    
                    <div className="space-y-3 mb-8">
                       <div className="bg-white/5 p-4 rounded-2xl flex justify-between items-center border border-white/5">
                          <div className="flex items-center gap-3">
                             <Thermometer size={16} className="text-gray-400" />
                             <span className="text-xs font-bold text-gray-300">Backup Generators</span>
                          </div>
                          <span className="text-xs font-black text-green-400">48 HRS (FULL)</span>
                       </div>
                       <div className="bg-white/5 p-4 rounded-2xl flex justify-between items-center border border-white/5">
                          <div className="flex items-center gap-3">
                             <Navigation size={16} className="text-gray-400" />
                             <span className="text-xs font-bold text-gray-300">Helipad Status</span>
                          </div>
                          <span className="text-xs font-black text-white">OPERATIONAL</span>
                       </div>
                    </div>

                    <button className="w-full py-4 bg-red-600 hover:bg-red-500 transition-colors rounded-2xl font-black text-white tracking-widest uppercase text-xs flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(220,38,38,0.4)]">
                       <Shield size={16} /> Initiate Evacuation Protocol
                    </button>
                 </div>
              )}

              {activeModal === 'bridge' && (
                 <div className="flex flex-col h-full">
                    <div className="flex items-center justify-between mb-8 pb-6 border-b border-white/10">
                      <div className="flex items-center gap-4">
                        <div className="p-4 bg-orange-500/20 rounded-[1.25rem] border border-orange-500/30 shadow-[0_0_20px_rgba(249,115,22,0.3)]">
                           <Layers size={28} className="text-orange-400" />
                        </div>
                        <div>
                           <h3 className="text-2xl font-black text-white tracking-tight">Hwy Bridge 42</h3>
                           <p className="text-[10px] text-orange-400 font-black uppercase tracking-[0.2em] mt-1">Primary Evac Route</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-3 mb-8">
                       <div className="bg-white/5 p-4 rounded-2xl flex justify-between items-center border border-white/5">
                          <span className="text-xs font-bold text-gray-300">Traffic Volume</span>
                          <span className="text-xs font-black text-red-400">SEVERE (JAMMED)</span>
                       </div>
                       <div className="bg-white/5 p-4 rounded-2xl flex justify-between items-center border border-white/5">
                          <span className="text-xs font-bold text-gray-300">Structural Integrity</span>
                          <span className="text-xs font-black text-yellow-500">WARNING - STRAIN</span>
                       </div>
                    </div>

                    <button className="w-full py-4 bg-orange-600 hover:bg-orange-500 transition-colors rounded-2xl font-black text-white tracking-widest uppercase text-xs flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(234,88,12,0.4)]">
                       <Shield size={16} /> Deploy Police Barricades
                    </button>
                 </div>
              )}


              {activeModal === 'factor' && (
                 <div className="flex flex-col h-full">
                    <div className="flex items-center justify-between mb-6 pb-6 border-b border-red-500/20">
                      <div className="flex items-center gap-4">
                        <div className="p-3 bg-red-500/20 rounded-2xl border border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.3)]">
                           <ShieldAlert size={24} className="text-red-400" />
                        </div>
                        <div>
                           <h3 className="text-2xl font-black text-white tracking-tight">Executive Summary</h3>
                           <p className="text-[10px] text-red-400 font-black uppercase tracking-[0.2em] mt-1">Plain-Language AI Assessment</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white/5 rounded-[1.25rem] p-6 border border-white/10 mb-6 shadow-inner relative overflow-hidden">
                       <div className="flex items-start gap-4 mb-6">
                          <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center shrink-0 border border-blue-500/30">
                             <Layers size={18} className="text-blue-400" />
                          </div>
                          <div>
                             <h4 className="text-sm font-bold text-white mb-1.5">Terrain Assessment</h4>
                             <p className="text-xs text-gray-400 leading-relaxed">
                               This region is characterized by a steep <strong>{currentZone.slope}°</strong> slope and a high Topographic Wetness Index of <strong>{currentZone.twi}</strong>. Our machine learning models indicate that the natural physical geometry of this landmass is inherently unstable and highly susceptible to gravitational failure.
                             </p>
                          </div>
                       </div>
                       
                       <div className="flex items-start gap-4">
                          <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center shrink-0 border border-orange-500/30">
                             <CloudRain size={18} className="text-orange-400" />
                          </div>
                          <div>
                             <h4 className="text-sm font-bold text-white mb-1.5">Weather Trigger Analysis</h4>
                             <p className="text-xs text-gray-400 leading-relaxed">
                               Over the past 30 days, this zone has absorbed significant precipitation. While the rainfall volume alone might not be unprecedented, when combined with the severe slope angle, the internal hydrostatic pressure of the soil is rapidly approaching critical limits.
                             </p>
                          </div>
                       </div>
                    </div>

                    <div>
                       <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                          <Check size={14} className="text-blue-400" /> Recommended Commander Action
                       </h4>
                       <div className="bg-white/5 p-5 rounded-2xl border border-white/10 text-sm text-gray-300 leading-relaxed shadow-lg">
                          {data.reason_code === 'HIGH_TERRAIN_SUSCEPTIBILITY' ? 
                            "The physical geometry of this zone is highly unstable. While current weather is not extreme, any minor seismic activity or sudden cloudburst will result in immediate catastrophic failure. Pre-position heavy excavation equipment at the base and restrict heavy transit." : 
                            "The soil has reached absolute saturation due to prolonged rainfall. The terrain itself is moderately stable, but the hydrostatic pressure is critical. Initiate mandatory evacuation of all structures within a 500m radius of the slope base immediately."}
                       </div>
                    </div>
                 </div>
              )}

              {activeModal === 'xgb' && (
                 <div className="flex flex-col h-full">
                    <div className="flex items-center gap-5 mb-8 pb-6 border-b border-white/10 relative">
                      <div className="absolute -left-10 -top-10 w-32 h-32 bg-orange-500/20 blur-[40px] rounded-full pointer-events-none" />
                      <div className="p-4 bg-gradient-to-br from-orange-500/20 to-orange-900/40 rounded-[1.25rem] border border-orange-500/30 shadow-[0_0_25px_rgba(249,115,22,0.25)] relative z-10">
                         <Activity size={32} className="text-orange-400 drop-shadow-[0_0_10px_rgba(249,115,22,0.8)]" />
                      </div>
                      <div className="relative z-10">
                         <h3 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 tracking-tight">Terrain Topology</h3>
                         <p className="text-[10px] text-orange-400 font-black uppercase tracking-[0.2em] mt-1.5 drop-shadow-sm">Static Geomorphology</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                       {/* Slope Box (Spans 2 columns) */}
                       <div className="col-span-2 bg-gradient-to-br from-white/[0.08] to-transparent border border-white/10 rounded-3xl p-6 relative overflow-hidden group hover:bg-white/[0.12] transition-colors cursor-default">
                         <div className="absolute right-0 top-0 w-40 h-40 bg-orange-500/10 blur-[40px] rounded-full group-hover:bg-orange-500/20 transition-all" />
                         <div className="relative z-10 flex justify-between items-center">
                            <div>
                              <div className="flex items-center gap-2 mb-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.8)]" />
                                <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Slope Angle</div>
                              </div>
                              <div className="text-5xl font-black text-white tracking-tighter">{currentZone.slope}<span className="text-2xl text-orange-500 ml-1">°</span></div>
                            </div>
                            <div className="relative w-[80px] h-[80px]">
                              {/* Geometric representation of a 45 degree slope */}
                              <svg width="100%" height="100%" viewBox="0 0 100 100" className="drop-shadow-[0_0_15px_rgba(249,115,22,0.4)]">
                                <path d="M10,90 L90,10" stroke="url(#orange-grad)" strokeWidth="6" strokeLinecap="round" />
                                <path d="M10,90 L90,90" stroke="rgba(255,255,255,0.1)" strokeWidth="6" strokeLinecap="round" />
                                <path d="M10,10 L10,90" stroke="rgba(255,255,255,0.1)" strokeWidth="6" strokeLinecap="round" strokeDasharray="4 4" />
                                <defs>
                                  <linearGradient id="orange-grad" x1="0" y1="1" x2="1" y2="0">
                                    <stop offset="0%" stopColor="#ea580c" />
                                    <stop offset="100%" stopColor="#f97316" />
                                  </linearGradient>
                                </defs>
                              </svg>
                            </div>
                         </div>
                       </div>

                       {/* Elevation Box */}
                       <div className="bg-gradient-to-br from-white/[0.08] to-transparent border border-white/10 rounded-3xl p-5 relative overflow-hidden group hover:bg-white/[0.12] transition-colors cursor-default">
                         <div className="flex items-center gap-2 mb-3">
                            <div className="w-1.5 h-1.5 rounded-full bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.8)]" />
                            <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Elevation</div>
                         </div>
                         <div className="text-3xl font-black text-white tracking-tight">320<span className="text-lg text-yellow-500 ml-1">m</span></div>
                         <div className="mt-5 h-1.5 w-full bg-black/60 rounded-full overflow-hidden border border-white/5">
                            <motion.div initial={{width:0}} animate={{width:"32%"}} transition={{delay:0.2, type:"spring", stiffness:100}} className="h-full bg-gradient-to-r from-yellow-600 to-yellow-400 rounded-full shadow-[0_0_15px_rgba(234,179,8,0.6)]" />
                         </div>
                       </div>

                       {/* TWI Box */}
                       <div className="bg-gradient-to-br from-white/[0.08] to-transparent border border-white/10 rounded-3xl p-5 relative overflow-hidden group hover:bg-white/[0.12] transition-colors cursor-default">
                         <div className="flex items-center gap-2 mb-3">
                            <div className="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]" />
                            <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Wetness (TWI)</div>
                         </div>
                         <div className="text-3xl font-black text-white tracking-tight">{currentZone.twi}<span className="text-lg text-red-500 ml-1"></span></div>
                         <div className="mt-5 h-1.5 w-full bg-black/60 rounded-full overflow-hidden border border-white/5">
                            <motion.div initial={{width:0}} animate={{width:"54%"}} transition={{delay:0.3, type:"spring", stiffness:100}} className="h-full bg-gradient-to-r from-red-600 to-red-400 rounded-full shadow-[0_0_15px_rgba(239,68,68,0.6)]" />
                         </div>
                       </div>
                    </div>
                 </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

            {/* BOTTOM PANEL: TIME SERIES SCRUBBER */}
      <div className="absolute bottom-6 left-[420px] right-[320px] z-10 pointer-events-auto min-w-[400px]">
         <div className="glass-panel rounded-3xl p-4 border-t border-white/10 shadow-[0_-15px_50px_rgba(0,0,0,0.6)]">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] flex items-center gap-2">
                 <CloudRain size={16} className="text-blue-400" /> 30-Day Precipitation Timeline
              </h3>
              <div className="flex items-center gap-3">
                 <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Source: Open-Meteo Archive</div>
                 <div className="text-xs font-black bg-blue-500/10 text-blue-400 px-3 py-1.5 rounded-xl border border-blue-500/20 shadow-inner">
                   TOTAL: {rainData.reduce((a, b) => a + b, 0).toFixed(1)}mm
                 </div>
              </div>
            </div>
            
            {/* Scrubber Chart */}
            <div className="h-16 flex items-end gap-1.5 w-full px-2 relative group cursor-crosshair border-b border-white/5 pb-1">
               
               {rainData.map((val, i) => {
                 const maxVal = Math.max(...rainData, 20);
                 const heightPct = Math.max(5, (val / maxVal) * 100);
                 
               
  const dynamicNodes = {
    type: 'FeatureCollection',
    features: [
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng - 0.003, currentZone.lat + 0.005] }, properties: { name: 'NODE-Alpha', status: 'online' } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng + 0.001, currentZone.lat + 0.001] }, properties: { name: 'NODE-Beta', status: 'online' } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng + 0.004, currentZone.lat - 0.004] }, properties: { name: 'NODE-Gamma', status: 'offline' } }
    ]
  };

  return (
                   <div key={i} className="flex-1 flex flex-col justify-end group/bar relative h-full">
                     {/* Hover Tooltip */}
                     <div className="absolute -top-12 left-1/2 -translate-x-1/2 opacity-0 group-hover/bar:opacity-100 transition-opacity z-30 pointer-events-none flex flex-col items-center">
                        <div className="bg-white text-black text-[11px] font-black px-2.5 py-1.5 rounded-lg shadow-[0_0_20px_rgba(255,255,255,0.4)] whitespace-nowrap">
                          {val.toFixed(1)} mm
                        </div>
                        <div className="w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-t-[5px] border-t-white -mt-[1px]" />
                     </div>

                     {/* The Bar */}
                     <motion.div 
                        initial={{ height: 0 }}
                        animate={{ height: `${heightPct}%` }}
                        transition={{ delay: i * 0.015, type: 'spring', stiffness: 100 }}
                        className="w-full bg-gradient-to-t from-blue-600/30 to-blue-400/60 rounded-t-md group-hover/bar:from-blue-500 group-hover/bar:to-blue-300 group-hover/bar:shadow-[0_0_15px_rgba(59,130,246,0.8)] transition-all border-t border-white/20 group-hover/bar:border-white"
                     />
                   </div>
                 );
               })}
               
               {/* Red Playhead / Scrubber (Fixed to Today by default) */}
               <div className="absolute top-0 bottom-0 right-2 w-[1px] bg-red-500/80 group-hover:opacity-0 transition-opacity pointer-events-none shadow-[0_0_15px_red] z-20">
                 <div className="absolute -top-1 -left-[5px] w-3 h-3 bg-red-500 rounded-full border-[2px] border-black shadow-[0_0_10px_red]" />
                 <div className="absolute -bottom-4 -left-3 text-[9px] font-black text-red-500 tracking-widest bg-black/80 px-1 rounded">TODAY</div>
               </div>

               {rainData.length === 0 && (
                 <div className="absolute inset-0 flex items-center justify-center text-xs text-gray-500 font-bold tracking-widest uppercase">Fetching Historical Telemetry...</div>
               )}
            </div>
            
            <div className="flex justify-between text-[9px] text-gray-500 font-black uppercase tracking-[0.3em] mt-3 px-2">
              <span>T-30 Days</span>
              <span></span>
            </div>
         </div>
      </div>

    </div>
  );
}

export default App;
