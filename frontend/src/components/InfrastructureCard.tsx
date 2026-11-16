import { motion } from 'framer-motion';
import { Activity, Layers, Navigation } from 'lucide-react';

type ModalType = 'lstm' | 'xgb' | 'factor' | 'hospital' | 'bridge';

interface InfrastructureCardProps {
  currentZone: any;
  data: any;
  setViewState: (state: any) => void;
  setActiveModal: (modal: ModalType | null) => void;
  calculateEvacuation: () => void;
  isRouting: boolean;
}

export default function InfrastructureCard({
  currentZone,
  data,
  setViewState,
  setActiveModal,
  calculateEvacuation,
  isRouting,
}: InfrastructureCardProps) {
  const exposureLevel = data?.risk_level === "CRITICAL" ? "100% EXPOSURE" : data?.risk_level === "HIGH" ? "HIGH EXPOSURE" : data?.risk_level === "MEDIUM" ? "MED EXPOSURE" : "LOW EXPOSURE";
  const exposureClass = data?.risk_level === "CRITICAL" || data?.risk_level === "HIGH" ? "text-red-400 bg-red-500/10 border border-red-500/20" : data?.risk_level === "MEDIUM" ? "text-yellow-400 bg-yellow-500/10 border border-yellow-500/20" : "text-emerald-400 bg-emerald-500/10 border border-emerald-500/20";

  const showEvacButton = data?.risk_level === 'HIGH' || data?.risk_level === 'CRITICAL';

  return (
    <div className="glass-panel rounded-[2rem] p-6">
      <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-5">Critical Infrastructure at Risk</h3>
      <div className="space-y-3">
        <motion.button
          whileHover={{ y: -3, scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => { setViewState({ longitude: currentZone.lng - 0.005, latitude: currentZone.lat + 0.015, zoom: 16 }); setActiveModal('hospital'); }}
          className="w-full flex items-center justify-between bg-black/40 p-3.5 rounded-2xl border border-white/5 hover:bg-white/10 hover:border-white/20 transition-all text-left focus:outline-none"
        >
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center shadow-[0_0_10px_rgba(59,130,246,0.2)]">
              <Activity size={16} className="text-blue-400" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">{currentZone.name.split(",")[0]} District Hospital</div>
              <div className="text-[10px] text-gray-500 mt-0.5 uppercase tracking-wider font-bold">Medical Facility • {(Math.abs(currentZone.lat * 0.07 + currentZone.lng * 0.03) % 3.5 + 0.8).toFixed(1)}km</div>
            </div>
          </div>
          {data && <div className={`text-[9px] font-black px-2.5 py-1.5 rounded-lg tracking-widest shadow-sm ${exposureClass}`}>{exposureLevel}</div>}
        </motion.button>

        <motion.button
          whileHover={{ y: -3, scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => { setViewState({ longitude: currentZone.lng + 0.010, latitude: currentZone.lat - 0.020, zoom: 16 }); setActiveModal('bridge'); }}
          className="w-full flex items-center justify-between bg-black/40 p-3.5 rounded-2xl border border-white/5 hover:bg-white/10 hover:border-white/20 transition-all text-left focus:outline-none"
        >
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center shadow-[0_0_10px_rgba(249,115,22,0.2)]">
              <Layers size={16} className="text-orange-400" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">{currentZone.name.split(",")[0]} Route 42</div>
              <div className="text-[10px] text-gray-500 mt-0.5 uppercase tracking-wider font-bold">Transit Route • {(Math.abs(currentZone.lng * 0.05 + currentZone.lat * 0.02) % 1.5 + 0.4).toFixed(1)}km</div>
            </div>
          </div>
          <div className="text-[9px] font-black text-orange-400 bg-orange-500/10 border border-orange-500/20 px-2.5 py-1.5 rounded-lg tracking-widest shadow-sm">EVAC ROUTE</div>
        </motion.button>

        {showEvacButton && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={calculateEvacuation}
            className="w-full mt-4 flex items-center justify-center gap-2 bg-yellow-500/20 text-yellow-500 hover:bg-yellow-500/30 border border-yellow-500/30 py-3 rounded-2xl font-black uppercase tracking-widest text-[11px] transition-all shadow-[0_0_15px_rgba(234,179,8,0.2)]"
          >
            {isRouting ? (
              <div className="w-4 h-4 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin" />
            ) : (
              <Navigation size={14} />
            )}
            {isRouting ? 'CALCULATING ROUTE...' : 'MAP EVACUATION ROUTE'}
          </motion.button>
        )}
      </div>
    </div>
  );
}