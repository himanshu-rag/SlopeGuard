import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# Add TrendingUp to lucide-react imports
if "TrendingUp" not in content:
    content = content.replace("Activity, ShieldAlert", "Activity, ShieldAlert, TrendingUp")

old_cards = """
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-black/40 border border-white/5 rounded-2xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <CloudRain size={16} className="text-blue-400" />
                      <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Trigger (LSTM)</span>
                    </div>
                    <div className="text-2xl font-bold text-white tracking-tight">{(data.trigger_probability * 100)?.toFixed(1)}%</div>
                  </div>
                  <div className="bg-black/40 border border-white/5 rounded-2xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Activity size={16} className="text-orange-400" />
                      <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Terrain (XGB)</span>
                    </div>
                    <div className="text-2xl font-bold text-white tracking-tight">{(data.susceptibility_probability * 100)?.toFixed(1)}%</div>
                  </div>
                </div>
"""

new_cards = """
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-black/40 border border-white/5 rounded-2xl p-4 relative overflow-hidden group hover:bg-black/60 transition-colors cursor-default">
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
                  </div>
                  
                  <div className="bg-black/40 border border-white/5 rounded-2xl p-4 relative overflow-hidden group hover:bg-black/60 transition-colors cursor-default">
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
                  </div>
                </div>
"""

content = content.replace(old_cards.strip(), new_cards.strip())

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
