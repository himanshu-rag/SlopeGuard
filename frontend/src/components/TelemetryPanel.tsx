import { motion, AnimatePresence } from 'framer-motion';
import { Wifi, Radio, Cpu } from 'lucide-react';

interface TelemetryPanelProps {
  telemetry: any[];
  dvrEvent: string | null;
}

export default function TelemetryPanel({ telemetry, dvrEvent }: TelemetryPanelProps) {
  return (
    <aside className="absolute top-28 right-6 z-10 w-[280px] pointer-events-auto flex flex-col gap-3">
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
            <Radio size={12} className={dvrEvent ? "text-red-400 animate-pulse" : "text-blue-400 animate-pulse"} /> {dvrEvent ? "DVR HISTORICAL LOG" : "Real-Time Packet Stream"}
          </h3>
          <span className={`text-[9px] font-black px-2 py-1 rounded-lg border shadow-sm ${dvrEvent ? 'text-red-400 bg-red-500/10 border-red-500/20' : 'text-blue-400 bg-blue-500/10 border-blue-500/20'}`}>
            {dvrEvent ? "ARCHIVE" : "TCP/IP"}
          </span>
        </div>

        <div className="space-y-3">
          <AnimatePresence>
            {telemetry.map((t) => (
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
            {telemetry.length === 0 && (
              <div className="text-xs text-gray-500 text-center py-4">Connecting to WebSocket...</div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </aside>
  );
}