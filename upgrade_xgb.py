with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

old_xgb = """
              {activeModal === 'xgb' && (
                 <div>
                    <div className="flex items-center gap-3 mb-8">
                      <div className="p-3 bg-orange-500/20 rounded-2xl border border-orange-500/30">
                         <Activity size={24} className="text-orange-400" />
                      </div>
                      <div>
                         <h3 className="text-xl font-black text-white tracking-tight">XGB Terrain Profile</h3>
                         <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">Static Geomorphology</p>
                      </div>
                    </div>
                    
                    <div className="space-y-6">
                       {[
                         { label: 'Slope Angle', val: 45, max: 90, unit: '°', color: 'from-orange-600 to-orange-400', shadow: 'shadow-[0_0_15px_rgba(249,115,22,0.3)]' },
                         { label: 'Elevation', val: 320, max: 1000, unit: 'm', color: 'from-yellow-600 to-yellow-400', shadow: 'shadow-[0_0_15px_rgba(234,179,8,0.3)]' },
                         { label: 'Wetness Index (TWI)', val: 8.2, max: 15, unit: '', color: 'from-red-600 to-red-400', shadow: 'shadow-[0_0_15px_rgba(239,68,68,0.3)]' }
                       ].map((stat, i) => (
                         <div key={i}>
                           <div className="flex justify-between text-xs font-bold text-gray-300 mb-2">
                             <span className="uppercase tracking-wider">{stat.label}</span>
                             <span className="text-white">{stat.val}{stat.unit}</span>
                           </div>
                           <div className="h-3 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
                             <motion.div 
                               initial={{ width: 0 }}
                               animate={{ width: `${(stat.val / stat.max) * 100}%` }}
                               transition={{ delay: i * 0.15, type: "spring", stiffness: 100 }}
                               className={`h-full bg-gradient-to-r ${stat.color} rounded-full ${stat.shadow}`}
                             />
                           </div>
                         </div>
                       ))}
                    </div>
                 </div>
              )}
"""

new_xgb = """
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
                              <div className="text-5xl font-black text-white tracking-tighter">45<span className="text-2xl text-orange-500 ml-1">°</span></div>
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
                         <div className="text-3xl font-black text-white tracking-tight">8.2<span className="text-lg text-red-500 ml-1"></span></div>
                         <div className="mt-5 h-1.5 w-full bg-black/60 rounded-full overflow-hidden border border-white/5">
                            <motion.div initial={{width:0}} animate={{width:"54%"}} transition={{delay:0.3, type:"spring", stiffness:100}} className="h-full bg-gradient-to-r from-red-600 to-red-400 rounded-full shadow-[0_0_15px_rgba(239,68,68,0.6)]" />
                         </div>
                       </div>
                    </div>
                 </div>
              )}
"""

content = content.replace(old_xgb.strip(), new_xgb.strip())

# Make the modal slightly wider to accommodate the bento grid
content = content.replace("w-[400px]", "w-[480px]")

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
