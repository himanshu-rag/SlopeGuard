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
  findNearestZone,
} from './data/search-db';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

const riskStyles = {
  CRITICAL: { title: 'text-red-500', boxBg: 'bg-red-500/5', boxBorder: 'border-red-500/20', icon: 'text-red-400', iconBg: 'bg-red-500/20 group-hover:bg-red-500/30', label: 'text-red-400', desc: 'text-red-300' },
  HIGH: { title: 'text-orange-500', boxBg: 'bg-orange-500/5', boxBorder: 'border-orange-500/20', icon: 'text-orange-400', iconBg: 'bg-orange-500/20 group-hover:bg-orange-500/30', label: 'text-orange-400', desc: 'text-orange-300' },
  MEDIUM: { title: 'text-yellow-500', boxBg: 'bg-yellow-500/5', boxBorder: 'border-yellow-500/20', icon: 'text-yellow-400', iconBg: 'bg-yellow-500/20 group-hover:bg-yellow-500/30', label: 'text-yellow-400', desc: 'text-yellow-300' },
  LOW: { title: 'text-emerald-500', boxBg: 'bg-emerald-500/5', boxBorder: 'border-emerald-500/20', icon: 'text-emerald-400', iconBg: 'bg-emerald-500/20 group-hover:bg-emerald-500/30', label: 'text-emerald-400', desc: 'text-emerald-300' }
};

type ModalType = 'lstm' | 'xgb' | 'factor' | 'hospital' | 'bridge';

function App() {
  const [data, setData] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [loading, setLoading] = useState(true);

  const [activeModal, setActiveModal] = useState<ModalType | null>(null);
  const [showFieldReport, setShowFieldReport] = useState(false);
  const [fieldReportLocation, setFieldReportLocation] = useState<{ lat: number; lng: number } | null>(null);

  const [baseMap, setBaseMap] = useState<'dark' | 'satellite'>('satellite');
  const [showTerrainLayer, setShowTerrainLayer] = useState(false);
  const [showFieldReports, setShowFieldReports] = useState(true);

  const [telemetry, setTelemetry] = useState<any[]>([]);
  const [rainData, setRainData] = useState<number[]>([]);

  const [viewState, setViewState] = useState({ longitude: 91.76, latitude: 26.14, zoom: 14 });
  const [currentZone, setCurrentZone] = useState({ id: '5', name: 'Guwahati, AS', type: 'Urban Hills', lng: 91.76, lat: 26.14, slope: 45.0, aspect: 140.0, curvature: -0.5, twi: 8.2 });

  const [evacuationRoute, setEvacuationRoute] = useState<any>(null);
  const [isRouting, setIsRouting] = useState(false);

  const [dvrMode, setDvrMode] = useState(false);
  const [dvrEvent, setDvrEvent] = useState<string | null>(null);

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
      setCurrentZone({ id: 'wayanad_1', name: 'Wayanad, KL', type: 'Western Ghats', lng: 76.0822, lat: 11.5549, slope: 62.0, aspect: 180, curvature: -0.9, twi: 12.5 });
    } else if (eventName === '2013 Kedarnath') {
      setViewState({ longitude: 79.0669, latitude: 30.7352, zoom: 14.0 });
      setCurrentZone({ id: 'kedar_1', name: 'Kedarnath, UK', type: 'Himalayan Slopes', lng: 79.0669, lat: 30.7352, slope: 75.0, aspect: 220, curvature: -1.2, twi: 14.0 });
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
  }, [currentZone.id, currentZone.lat, currentZone.lng, currentZone.slope, currentZone.aspect, currentZone.curvature, currentZone.twi, dvrMode]);

  const handleFlyTo = (zone: any) => {
    if (zone.isHistorical) {
      startDvrReplay(zone.eventName);
    } else {
      setDvrMode(false);
      setDvrEvent(null);
      setViewState({ longitude: zone.lng, latitude: zone.lat, zoom: 15.5 });
      setCurrentZone({ id: zone.id, name: zone.name, type: zone.type, lng: zone.lng, lat: zone.lat, slope: zone.slope, aspect: zone.aspect ?? 180.0, curvature: zone.curvature ?? -0.5, twi: zone.twi });
    }
  };

  const handleMyLocation = async () => {
    if (!navigator.geolocation) {
      alert("Geolocation not supported by your browser.");
      return;
    }
    try {
      const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000,
        });
      });
      const { latitude, longitude } = pos.coords;

      // Center the map on user's location
      setViewState({ longitude, latitude, zoom: 15 });

      // Stash location for the field report form
      setFieldReportLocation({ lat: latitude, lng: longitude });

      // Auto-select nearest zone for risk context
      const nearest = findNearestZone(latitude, longitude);
      if (nearest) {
        setDvrMode(false);
        setDvrEvent(null);
        setCurrentZone({
          id: nearest.id,
          name: nearest.name,
          type: nearest.type ?? 'Urban Hills',
          lng: nearest.lng,
          lat: nearest.lat,
          slope: nearest.slope ?? 45.0,
          aspect: nearest.aspect ?? 180.0,
          curvature: nearest.curvature ?? -0.5,
          twi: nearest.twi ?? 8.0,
        });
      }

      // Open the field report modal pre-filled with this location
      setShowFieldReport(true);
    } catch (err: any) {
      console.error("[SlopeGuard] Geolocation error:", err.message);
      alert("Unable to get your location. Please enable location services.");
    }
  };

  return (
    <div className="relative w-screen h-screen bg-[#0a0a0a]">
      <style>{`
        .dark-map-layer .maplibregl-canvas { filter: invert(100%) hue-rotate(180deg) brightness(85%) contrast(110%); }
        .glass-panel { background: rgba(17, 17, 17, 0.75); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
        .glass-button { background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }
      `}</style>

      <MapView
        viewState={viewState}
        baseMap={baseMap}
        showTerrainLayer={showTerrainLayer}
        showFieldReports={showFieldReports}
        currentZone={currentZone}
        evacuationRoute={evacuationRoute}
        onMove={(evt) => setViewState(evt.viewState)}
      />

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

      <div className="absolute top-28 left-6 z-10 w-96 flex flex-col gap-5 pointer-events-auto">
        <RiskCard
          currentZone={currentZone}
          data={data}
          loading={loading}
          dvrEvent={dvrEvent}
          riskStyles={riskStyles}
          setActiveModal={setActiveModal}
        />
        <InfrastructureCard
          currentZone={currentZone}
          data={data}
          setViewState={setViewState}
          setActiveModal={setActiveModal}
          calculateEvacuation={calculateEvacuation}
          isRouting={isRouting}
        />
      </div>

      <TelemetryPanel telemetry={telemetry} dvrEvent={dvrEvent} />

      <RiskModal
        activeModal={activeModal}
        currentZone={currentZone}
        data={data}
        rainData={rainData}
        onClose={() => setActiveModal(null)}
      />

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

      <div className="absolute bottom-6 left-[420px] right-[320px] z-10 pointer-events-auto min-w-[400px]">
        <PrecipitationChart rainData={rainData} />
      </div>
    </div>
  );
}

export default App;