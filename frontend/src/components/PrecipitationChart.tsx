import { motion } from 'framer-motion';
import { CloudRain } from 'lucide-react';

interface PrecipitationChartProps {
  rainData: number[];
}

export default function PrecipitationChart({ rainData }: PrecipitationChartProps) {
  const total = rainData.reduce((a, b) => a + b, 0);

  return (
    <div className="glass-panel rounded-3xl p-4 border-t border-white/10 shadow-[0_-15px_50px_rgba(0,0,0,0.6)]">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] flex items-center gap-2">
          <CloudRain size={16} className="text-blue-400" /> 30-Day Precipitation Timeline
        </h3>
        <div className="flex items-center gap-3">
          <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Source: Open-Meteo Archive</div>
          <div className="text-xs font-black bg-blue-500/10 text-blue-400 px-3 py-1.5 rounded-xl border border-blue-500/20 shadow-inner">
            TOTAL: {total.toFixed(1)}mm
          </div>
        </div>
      </div>

      <div className="h-16 flex items-end gap-1.5 w-full px-2 relative group cursor-crosshair border-b border-white/5 pb-1">
        {rainData.map((val, i) => {
          const maxVal = Math.max(...rainData, 20);
          const heightPct = Math.max(5, (val / maxVal) * 100);

          return (
            <div key={i} className="flex-1 flex flex-col justify-end group/bar relative h-full">
              <div className="absolute -top-12 left-1/2 -translate-x-1/2 opacity-0 group-hover/bar:opacity-100 transition-opacity z-30 pointer-events-none flex flex-col items-center">
                <div className="bg-white text-black text-[11px] font-black px-2.5 py-1.5 rounded-lg shadow-[0_0_20px_rgba(255,255,255,0.4)] whitespace-nowrap">
                  {val.toFixed(1)} mm
                </div>
                <div className="w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-t-[5px] border-t-white -mt-[1px]" />
              </div>

              <motion.div 
                initial={{ height: 0 }}
                animate={{ height: `${heightPct}%` }}
                transition={{ delay: i * 0.015, type: 'spring', stiffness: 100 }}
                className="w-full bg-gradient-to-t from-blue-600/30 to-blue-400/60 rounded-t-md group-hover/bar:from-blue-500 group-hover/bar:to-blue-300 group-hover/bar:shadow-[0_0_15px_rgba(59,130,246,0.8)] transition-all border-t border-white/20 group-hover/bar:border-white"
              />
            </div>
          );
        })}

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
  );
}