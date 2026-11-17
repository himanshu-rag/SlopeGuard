import { useEffect, useState, useRef } from 'react';
import MapView from './components/MapView';
import TopNav from './components/TopNav';
import RiskCard from './components/RiskCard';
import InfrastructureCard from './components/InfrastructureCard';
import TelemetryPanel from './components/TelemetryPanel';
import RiskModal from './components/RiskModal';
import PrecipitationChart from './components/PrecipitationChart';
import FieldReportForm from './components/FieldReportForm';
import {
  SEARCH_DB,
  CUSTOM_LOCATION_ID,
} from './data/search-db';
import {
  initCapacitor,
  hideSplashScreen,
  getCurrentPosition,
} from './capacitor';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

const riskStyles = {
  CRITICAL: { title: 'text-red-500', boxBg: 'bg-red-500/5', boxBorder: 'border-red-500/20', icon: 'text-red-400', iconBg: 'bg-red-500/20 group-hover:bg-red-500/30', label: 'text-red-400', desc: 'text-red-300' },
  HIGH: { title: 'text-orange-500', boxBg: 'bg-orange-500/5', boxBorder: 'border-orange-500/20', icon: 'text-orange-400', iconBg: 'bg-orange-500/20 group-hover:bg-orange-500/30', label: 'text-orange-400', desc: 'text-orange-300' },
  MEDIUM: { title: 'text-yellow-500', boxBg: 'bg-yellow-500/5', boxBorder: 'border-yellow-500/20', icon: 'text-yellow-400', iconBg: 'bg-yellow-500/20 group-hover:bg-yellow-500/30', label: 'text-yellow-400', desc: 'text-orange-300' },
  LOW: { title: 'text-emerald-500', boxBg: 'bg-emerald-500/5', boxBorder: 'border-emerald-500/20', icon: 'text-emerald-400', iconBg: 'bg-emerald-500/20 group-hover:bg-emerald-500/30', label: 'text-emerald-400', desc: 'text-emerald-300' }
};

type ModalType = 'lstm' | 'xgb' | 'factor' | 'hospital' | 'bridge';

function App() {
  const [data, setData] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [loading, setLoading] = useState(true);

  // Initialize Capacitor native plugins on mount
  useEffect(() => {
    initCapacitor();
    hideSplashScreen();
  }, []);

  const [activeModal, setActiveModal] = useState<ModalType | null>(null);
  const [showFieldReport, setShowFieldReport] = useState(false);
  const [fieldReportLocation, setFieldReportLocation] = useState<{ lat: number; lng: number } | null>(null);

  const [baseMap, setBaseMap] = useState<'dark' | 'satellite'>('satellite');
  const [showTerrainLayer, setShowTerrainLayer] = useState(false);
  const [showFieldReports, setShowFieldReports] = useState(true);

  const [telemetry, setTelemetry] = useState<any[]>([]);
  const [rainData, setRainData] = useState<number[]>([]);

  const [viewState, setViewState] = useState({ longitude: 91.76, latitude: 26.14, zoom: 14 });
  const [currentZone, setCurrentZone] = useState({ id: '5', name: 'Guwahati, AS', type: 'Urban Hills', lng: 91.76, lat: 26.14, slope: 45.0, aspect: 140.0, curvature: -0.5, twi: 8.2, isCustom: false });

  const [evacuationRoute, setEvacuationRoute] = useState<any>(null);
  const [isRouting, setIsRouting] = useState(false);

  const [dvrMode, setDvrMode] = useState(false);
  const [dvrEvent, setDvrEvent] = useState<string | null>(null);

  // Bottom sheet state for mobile
  const [sheetExpanded, setSheetExpanded] = useState(false);

  const calculateEvacuation = async () => {
    setIsRouting(true);
    const startLng = currentZone.lng - 0.01;
    const startLat = currentZone.lat + 0.01;
    const safeLng = currentZone.lng + 0.08;
    const safeLat = currentZone.lat - 0.05;

    try {
      const res = await fetch(`http://router.project-osrm.org/route/v1/driving/${startLng},${startLat};${safeLng},${safeLat}?overview=full&geometries=geojson`);
      const routeData = await res.json();
      if (routeData.routes && routeData.routes.length > 0 && routeData.routes[0]) {
        setEvacuationRoute({
          type: 'FeatureCollection',
          features: [
            { type: 'Feature', geometry: routeData.routes[0].geometry, properties: { type: 'route' } },
            { type: 'Feature', geometry: { type: 'Point', coordinates: [safeLng, safeLat] }, properties: { type: 'safezone', name: 'Evacuation Center Alpha' } }
          ]
        });
        setViewState({ longitude: (startLng + safeLng) / 2, latitude: (startLat + safeLat) / 2, zoom: 11.5 });
      }
    } catch (e: any) {
      console.error("OSRM Error", e);
      alert("Evacuation route unavailable: No road network found near this location.");
    }
    setIsRouting(false);
  };

  const startDvrReplay = (eventName: string) => {
    setDvrEvent(eventName);
    setDvrMode(true);

    if (eventName === '2024 Wayanad') {
      setViewState({ longitude: 76.0822, latitude: 11.5549, zoom: 14.5 });
      setCurrentZone({ id: 'wayanad_1', name: 'Wayanad, KL', type: 'Western Ghats', lng: 76.0822, lat: 11.5549, slope: 62.0, aspect: 180, curvature: -0.9, twi: 12.5, isCustom: false });
    } else if (eventName === '2013 Kedarnath') {
      setViewState({ longitude: 79.0669, latitude: 30.7352, zoom: 14.0 });
      setCurrentZone({ id: 'kedar_1', name: 'Kedarnath, UK', type: 'Himalayan Slopes', lng: 79.0669, lat: 30.7352, slope: 75.0, aspect: 220, curvature: -1.2, twi: 14.0, isCustom: false });
    }
  };

  const handleBaseMapChange = (map: 'dark' | 'satellite') => {
    setBaseMap(map);
  };

  const handleToggleTerrain = () => {
    setShowTerrainLayer(!showTerrainLayer);
  };

  const handleToggleFieldReports = () => {
    setShowFieldReports(!showFieldReports);
  };

  // DVR simulation
  useEffect(() => {
    if (!dvrMode || !dvrEvent) return;
    setLoading(true);
    setTelemetry([]);

    const runDvrSimulation = async () => {
      try {
        const syntheticRain = Array(25).fill(10).concat([45, 90, 150, 280, 420]);
        setRainData(syntheticRain);

        const simRes = await fetch(`${API_BASE}/simulate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            slope_deg: currentZone.slope,
            aspect_deg: currentZone.aspect ?? 180.0,
            curvature: currentZone.curvature ?? -0.5,
            twi: currentZone.twi,
            rainfall_seq: syntheticRain,
          }),
        });
        if (!simRes.ok) throw new Error('Simulate endpoint error');
        const simJson = await simRes.json();
        setData(simJson);
      } catch (e: any) {
        console.error('[SlopeGuard] DVR simulate error:', e.message);
        setData({ final_score: 0, risk_level: 'LOW', reason_code: 'API_UNAVAILABLE', susceptibility_probability: 0, trigger_probability: 0 });
      } finally {
        setLoading(false);
      }
    };

    runDvrSimulation();

    setTelemetry([
      { id: '1', node_id: 'NODE-Alpha (Crest)', type: 'GPS Displacement', val: '45.2mm', status: 'critical', time: '-1hr' },
      { id: '2', node_id: 'NODE-Beta (Mid-Slope)', type: 'Inclinometer', val: '4.5°/h', status: 'critical', time: '-1hr' },
      { id: '3', node_id: 'NODE-Gamma (Base)', type: 'Soil Moisture', val: '99.9%', status: 'critical', time: '-2hr' },
    ]);
  }, [dvrMode, dvrEvent, currentZone]);

  // Live data fetch + WebSocket
  useEffect(() => {
    if (dvrMode) return;
    setLoading(true);
    setTelemetry([]);
    setData(null);

    const controller = new AbortController();
    const { signal } = controller;

    const fetchRain = async () => {
      try {
        let fetchedRainData: number[] = [];
        if (currentZone.id.startsWith('global_')) {
          const res = await fetch(
            `https://api.open-meteo.com/v1/forecast?latitude=${currentZone.lat}&longitude=${currentZone.lng}&daily=rain_sum&past_days=30&forecast_days=1`,
            { signal }
          );
          if (!res.ok) throw new Error('Open-Meteo API error');
          const json = await res.json();
          fetchedRainData = (json?.daily?.rain_sum ?? []).slice(0, 30).map((r: any) => r === null ? 0 : r);
        } else {
          const res = await fetch(`${API_BASE}/zones/${currentZone.id}/rainfall`, { signal });
          if (!res.ok) throw new Error('Backend zone rainfall error');
          const json = await res.json();
          fetchedRainData = Array.isArray(json) ? json : [];
        }
        setRainData(fetchedRainData);

        const simRes = await fetch(`${API_BASE}/simulate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            slope_deg: currentZone.slope,
            aspect_deg: currentZone.aspect ?? 180.0,
            curvature: currentZone.curvature ?? -0.5,
            twi: currentZone.twi,
            rainfall_seq: fetchedRainData
          }),
          signal
        });
        if (!simRes.ok) throw new Error('Simulate endpoint error');
        const simJson = await simRes.json();
        setData(simJson);
      } catch (e: any) {
        if (e.name !== 'AbortError') {
          console.error('[SlopeGuard] Fetch error:', e.message);
          setData({ final_score: 0, risk_level: 'LOW', reason_code: 'API_UNAVAILABLE', susceptibility_probability: 0, trigger_probability: 0 });
        }
      } finally {
        if (!signal.aborted) setLoading(false);
      }
    };

    fetchRain();

    if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSING && wsRef.current.readyState !== WebSocket.CLOSED) wsRef.current.close();
    const ws = new WebSocket(`${API_BASE.replace(/^http/, "ws")}/ws/telemetry/${currentZone.id}`);
    wsRef.current = ws;
    ws.onmessage = (event) => {
      try {
        setTelemetry(prev => [JSON.parse(event.data), ...prev].slice(0, 5));
      } catch {}
    };
    ws.onerror = () => console.warn('[SlopeGuard] WebSocket error for zone', currentZone.id);

    return () => {
      controller.abort();
      ws.close();
      wsRef.current = null;
    };
  }, [currentZone.id, currentZone.lat, currentZone.lng, currentZone.slope, currentZone.aspect, currentZone.curvature, currentZone.twi, currentZone.isCustom, dvrMode]);

  const handleFlyTo = (zone: any) => {
    if (zone.isHistorical) {
      startDvrReplay(zone.eventName);
    } else {
      setDvrMode(false);
      setDvrEvent(null);
      setViewState({ longitude: zone.lng, latitude: zone.lat, zoom: 15.5 });
      setCurrentZone({ id: zone.id, name: zone.name, type: zone.type, lng: zone.lng, lat: zone.lat, slope: zone.slope, aspect: zone.aspect ?? 180.0, curvature: zone.curvature ?? -0.5, twi: zone.twi, isCustom: false });
      setSheetExpanded(false);
    }
  };

  const handleMyLocation = async () => {
    try {
      const pos = await getCurrentPosition();
      const { latitude, longitude } = pos;

      setViewState({ longitude, latitude, zoom: 15 });
      setFieldReportLocation({ lat: latitude, lng: longitude });

      let placeName = "Your Location";
      try {
        const res = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}&accept-language=en`,
          { headers: { "Accept-Language": "en" } }
        );
        const data = await res.json();
        if (data?.display_name) {
          placeName = data.display_name.split(",").slice(0, 3).join(", ");
        }
      } catch {}

      const DEFAULT_SLOPE = 3.0;
      const DEFAULT_TWI = 4.0;
      const DEFAULT_ASPECT = 180.0;
      const DEFAULT_CURVATURE = 0.0;

      setDvrMode(false);
      setDvrEvent(null);
      setCurrentZone({
        id: CUSTOM_LOCATION_ID,
        name: placeName,
        type: "Custom Location",
        lng: longitude,
        lat: latitude,
        slope: DEFAULT_SLOPE,
        aspect: DEFAULT_ASPECT,
        curvature: DEFAULT_CURVATURE,
        twi: DEFAULT_TWI,
        isCustom: true,
      });

      setShowFieldReport(true);
      setSheetExpanded(true);
    } catch (err: any) {
      console.error("[SlopeGuard] Geolocation error:", err.message);
      alert("Unable to get your location. Please enable location services.");
    }
  };

  return (
    <div className="relative w-screen h-screen bg-[#0a0a0a] overflow-hidden">
      <style>{`
        .dark-map-layer .maplibregl-canvas { filter: invert(100%) hue-rotate(180deg) brightness(85%) contrast(110%); }
        .glass-panel { background: rgba(17, 17, 17, 0.85); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
        .glass-button { background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .bottom-sheet {
          background: rgba(17, 17, 17, 0.95);
          backdrop-filter: blur(24px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-top-left-radius: 24px;
          border-top-right-radius: 24px;
        }
      `}</style>

      {/* Map - full screen behind everything */}
      <MapView
        viewState={viewState}
        baseMap={baseMap}
        showTerrainLayer={showTerrainLayer}
        showFieldReports={showFieldReports}
        currentZone={currentZone}
        evacuationRoute={evacuationRoute}
        onMove={(evt) => setViewState(evt.viewState)}
      />

      {/* Top Navigation - thumb reachable */}
      <TopNav
        dvrMode={dvrMode}
        dvrEvent={dvrEvent}
        setDvrMode={setDvrMode}
        setDvrEvent={setDvrEvent}
        startDvrReplay={startDvrReplay}
        handleFlyTo={handleFlyTo}
        onBaseMapChange={handleBaseMapChange}
        onToggleTerrain={handleToggleTerrain}
        onToggleFieldReports={handleToggleFieldReports}
        onReportClick={() => setShowFieldReport(true)}
        onMyLocation={handleMyLocation}
        SEARCH_DB={SEARCH_DB}
      />

      {/* Bottom Sheet - Risk Card + Details */}
      <div className={`bottom-sheet absolute bottom-0 left-0 right-0 h-[60%] md:h-[55%] z-50 transition-all duration-300 transform ${sheetExpanded ? 'translate-y-0' : 'translate-y-[70%]'} shadow-2xl`}>
        {/* Sheet handle */}
        <div className="flex justify-center pt-3">
          <div className="w-12 h-1.5 bg-gray-600 rounded-full mx-auto"></div>
        </div>

        {/* Sheet content - scrollable */}
        <div className="p-4 space-y-4 max-h-[calc(100vh-100px)] overflow-y-auto">
          
          {/* Risk Card */}
          <RiskCard
            currentZone={currentZone}
            data={data}
            loading={loading}
            dvrEvent={dvrEvent}
            riskStyles={riskStyles}
            setActiveModal={setActiveModal}
          />

          {/* Infrastructure Card */}
          <InfrastructureCard
            currentZone={currentZone}
            data={data}
            setViewState={setViewState}
            setActiveModal={setActiveModal}
            calculateEvacuation={calculateEvacuation}
            isRouting={isRouting}
          />

          {/* Telemetry Panel - compact */}
          <TelemetryPanel telemetry={telemetry} dvrEvent={dvrEvent} />

          {/* Precipitation Chart */}
          <div className="relative h-48 w-full">
            <PrecipitationChart rainData={rainData} />
          </div>

          {/* Field Report Form trigger hint */}
          {dvrEvent && (
            <div className="px-4 py-3 bg-yellow-500/10 border border-yellow-500/20 rounded-xl">
              <p className="text-sm text-yellow-400 font-medium">
                DVR Replay: {dvrEvent} — tap map to explore
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Risk Modal */}
      <RiskModal
        activeModal={activeModal}
        currentZone={currentZone}
        data={data}
        rainData={rainData}
        onClose={() => setActiveModal(null)}
      />

      {/* Field Report Form */}
      <FieldReportForm
        isOpen={showFieldReport}
        onClose={() => {
          setShowFieldReport(false);
          setFieldReportLocation(null);
        }}
        onReportSubmitted={() => {
          setShowFieldReport(false);
          setFieldReportLocation(null);
        }}
        initialLocation={fieldReportLocation || undefined}
      />

      {/* Floating Action Buttons - bottom right, thumb reachable */}
      <div className="absolute bottom-[110px] right-4 z-40 flex flex-col gap-2">
        <button
          onClick={handleMyLocation}
          className="w-14 h-14 rounded-full bg-black/60 backdrop-blur-md border border-white/10 flex items-center justify-center text-white shadow-lg active:scale-95 transition-transform"
          aria-label="My Location"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 12m-3 0a3 3 0 116 0a3 3 0 01-6 0z" />
          </svg>
        </button>
        <button
          onClick={() => setShowFieldReport(true)}
          className="w-14 h-14 rounded-full bg-red-500 backdrop-blur-md border border-red-500/30 flex items-center justify-center text-white shadow-lg active:scale-95 transition-transform"
          aria-label="Field Report"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
      </div>

      {/* Sheet expand hint */}
      {!sheetExpanded && (
        <div className="absolute bottom-[90px] left-1/2 -translate-x-1/2 z-30 flex items-center gap-1 px-3 py-1.5 bg-black/60 backdrop-blur rounded-full text-xs text-gray-300 border border-white/10">
          <span className="w-2 h-2 rounded-full bg-white/30"></span>
          <span>Slide up for details</span>
        </div>
      )}
    </div>
  );
}

export default App;
