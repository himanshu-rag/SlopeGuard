import { motion, AnimatePresence } from 'framer-motion';
import { X, CloudRain, Activity, Shield, Thermometer, Navigation, ShieldAlert, Layers, Check } from 'lucide-react';

interface RiskModalProps {
  activeModal: 'lstm' | 'hospital' | 'bridge' | 'factor' | 'xgb' | null;
  currentZone: any;
  data: any;
  rainData: number[];
  onClose: () => void;
}

export default function RiskModal({
  activeModal,
  currentZone,
  data,
  rainData,
  onClose,
}: RiskModalProps) {
  if (!activeModal) return null;

  const renderLSTMModal = () => {
    const maxRain = Math.max(...rainData.slice(-7), 50);
    return (
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
                animate={{ height: `${Math.max(8, (val / maxRain) * 100)}%` }}
                transition={{ delay: i * 0.1, type: "spring", stiffness: 100 }}
                className="w-full bg-gradient-to-t from-blue-600/40 to-blue-400/80 rounded-t-lg hover:to-blue-400 transition-all cursor-pointer shadow-[0_0_15px_rgba(59,130,246,0.2)]"
              />
              <div className="text-[9px] text-gray-500 font-extrabold uppercase mt-3">T-{6 - i}</div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderHospitalModal = () => {
    return (
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-between mb-8 pb-6 border-b border-white/10">
          <div className="flex items-center gap-4">
            <div className="p-4 bg-blue-500/20 rounded-[1.25rem] border border-blue-500/30 shadow-[0_0_20px_rgba(59,130,246,0.3)]">
              <Activity size={28} className="text-blue-400" />
            </div>
            <div>
              <h3 className="text-2xl font-black text-white tracking-tight">{currentZone.name.split(",")[0]} District Hospital</h3>
              <p className="text-[10px] text-red-400 font-black uppercase tracking-[0.2em] mt-1">100% Slide Exposure</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-black text-white">{Math.round(200 + currentZone.slope * 4)}</div>
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
    );
  };

  const renderBridgeModal = () => {
    return (
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-between mb-8 pb-6 border-b border-white/10">
          <div className="flex items-center gap-4">
            <div className="p-4 bg-orange-500/20 rounded-[1.25rem] border border-orange-500/30 shadow-[0_0_20px_rgba(249,115,22,0.3)]">
              <Layers size={28} className="text-orange-400" />
            </div>
            <div>
              <h3 className="text-2xl font-black text-white tracking-tight">{currentZone.name.split(",")[0]} Route 42</h3>
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
    );
  };

  const renderFactorModal = () => {
    const recommendation = data.reason_code === 'HIGH_TERRAIN_SUSCEPTIBILITY'
      ? "The physical geometry of this zone is highly unstable. While current weather is not extreme, any minor seismic activity or sudden cloudburst will result in immediate catastrophic failure. Pre-position heavy excavation equipment at the base and restrict heavy transit."
      : "The soil has reached absolute saturation due to prolonged rainfall. The terrain itself is moderately stable, but the hydrostatic pressure is critical. Initiate mandatory evacuation of all structures within a 500m radius of the slope base immediately.";

    return (
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
          <div className="bg-white/5 p-5 rounded-2xl border border-white/10 text-sm text-gray-300 leading-relaxed shadow-lg">{recommendation}</div>
        </div>
      </div>
    );
  };

  const renderXGBModal = () => {
    return (
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

          <div className="bg-gradient-to-br from-white/[0.08] to-transparent border border-white/10 rounded-3xl p-5 relative overflow-hidden group hover:bg-white/[0.12] transition-colors cursor-default">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-1.5 h-1.5 rounded-full bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.8)]" />
              <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Elevation</div>
            </div>
            <div className="text-3xl font-black text-white tracking-tight">{Math.round(Math.abs(currentZone.lat * currentZone.slope * 2.5))}<span className="text-lg text-yellow-500 ml-1">m</span></div>
            <div className="mt-5 h-1.5 w-full bg-black/60 rounded-full overflow-hidden border border-white/5">
              <motion.div initial={{ width: 0 }} animate={{ width: `${Math.min(95, currentZone.slope * 1.2).toFixed(0)}%` }} transition={{ delay: 0.2, type: "spring", stiffness: 100 }} className="h-full bg-gradient-to-r from-yellow-600 to-yellow-400 rounded-full shadow-[0_0_15px_rgba(234,179,8,0.6)]" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-white/[0.08] to-transparent border border-white/10 rounded-3xl p-5 relative overflow-hidden group hover:bg-white/[0.12] transition-colors cursor-default">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]" />
              <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Wetness (TWI)</div>
            </div>
            <div className="text-3xl font-black text-white tracking-tight">{currentZone.twi}<span className="text-lg text-red-500 ml-1"></span></div>
            <div className="mt-5 h-1.5 w-full bg-black/60 rounded-full overflow-hidden border border-white/5">
              <motion.div initial={{ width: 0 }} animate={{ width: `${Math.min(95, (currentZone.twi / 20) * 100).toFixed(0)}%` }} transition={{ delay: 0.3, type: "spring", stiffness: 100 }} className="h-full bg-gradient-to-r from-red-600 to-red-400 rounded-full shadow-[0_0_15px_rgba(239,68,68,0.6)]" />
            </div>
          </div>
        </div>
      </div>
    );
  };

  const modalContent = {
    lstm: renderLSTMModal(),
    hospital: renderHospitalModal(),
    bridge: renderBridgeModal(),
    factor: renderFactorModal(),
    xgb: renderXGBModal(),
  };

  return (
    <AnimatePresence>
      {activeModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 z-[100] flex items-center justify-center bg-black/30 backdrop-blur-[2px] p-4 pointer-events-auto"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, y: 20, opacity: 0 }}
            animate={{ scale: 1, y: 0, opacity: 1 }}
            exit={{ scale: 0.9, y: 20, opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="glass-panel rounded-[2rem] p-7 w-[480px] relative overflow-hidden shadow-2xl"
            onClick={e => e.stopPropagation()}
          >
            <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 p-2 rounded-full transition-colors">
              <X size={16} />
            </button>
            {modalContent[activeModal]}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}