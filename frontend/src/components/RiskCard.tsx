import { motion } from 'framer-motion';
import { MapPin, CloudRain, Activity, AlertTriangle, TrendingUp } from 'lucide-react';

interface RiskCardProps {
  currentZone: any;
  data: any;
  loading: boolean;
  dvrEvent: string | null;
  riskStyles: any;
  setActiveModal: (modal: any) => void;
}

export default function RiskCard({
  currentZone,
  data,
  loading,
  dvrEvent,
  riskStyles,
  setActiveModal,
}: RiskCardProps) {
  const style = riskStyles[data?.risk_level as keyof typeof riskStyles] || riskStyles.LOW;

  return (
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
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-[10px] font-bold tracking-widest uppercase border shadow-sm ${dvrEvent ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20 shadow-[0_0_10px_rgba(234,179,8,0.1)]' : 'bg-red-500/10 text-red-400 border-red-500/20 shadow-[0_0_10px_rgba(239,68,68,0.1)]'}`}>
          <span className={`w-2 h-2 rounded-full animate-pulse ${dvrEvent ? 'bg-yellow-500' : 'bg-red-500'}`} /> {dvrEvent ? 'REPLAY' : 'Live'}
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
              <div className={`text-sm font-bold tracking-wide ${style.title}`}>{data.risk_level} RISK</div>
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
              <div className="flex items-center justify-between mb-3 relative z-10">
                <div className="flex items-center gap-2">
                  <Activity size={16} className="text-orange-400" />
                  <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Terrain (XGB)</span>
                </div>
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
            className={`w-full ${style.boxBg} border ${style.boxBorder} rounded-2xl p-4 flex gap-4 items-start transition-all text-left focus:outline-none shadow-sm group`}
          >
            <div className={`p-2 ${style.iconBg} rounded-lg transition-colors`}>
              <AlertTriangle className={`${style.icon} shrink-0`} size={16} />
            </div>
            <div>
              <h4 className={`text-[10px] font-black ${style.label} uppercase tracking-widest mb-1`}>Primary Factor</h4>
              <p className={`text-xs ${style.desc} font-bold tracking-wide`}>
                {data.reason_code?.replace(/_/g, ' ') || 'AWAITING TELEMETRY'}
              </p>
            </div>
          </motion.button>
        </div>
      ) : null}
    </div>
  );
}