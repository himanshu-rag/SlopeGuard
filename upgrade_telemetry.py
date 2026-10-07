with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

old_telemetry = """
               {telemetry.map(t => (
                 <motion.div 
                   key={t.id}
                   initial={{ opacity: 0, x: 20, height: 0 }}
                   animate={{ opacity: 1, x: 0, height: 'auto' }}
                   className="bg-black/40 border border-white/5 p-3.5 rounded-2xl flex items-center justify-between"
                 >
                   <div className="flex items-center gap-3">
                     <div className={`w-2 h-2 rounded-full ${t.status === 'warning' ? 'bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.6)]' : 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]'}`} />
                     <div>
                       <div className="text-xs font-semibold text-white">{t.type}</div>
                       <div className="text-[10px] text-gray-500 mt-0.5">{t.time}</div>
                     </div>
                   </div>
                   <div className="text-sm font-mono font-bold text-gray-300 bg-black/50 px-2 py-1 rounded-lg border border-white/5">
                     {t.val}
                   </div>
                 </motion.div>
               ))}
"""

new_telemetry = """
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
                       <div className="text-[13px] font-bold text-white tracking-tight">{t.type}</div>
                       <div className="text-[9px] font-black text-gray-500 uppercase tracking-widest mt-1">{t.time}</div>
                     </div>
                   </div>
                   
                   <div className={`relative z-10 text-sm font-mono font-bold px-3 py-1.5 rounded-xl border flex items-center justify-center min-w-[75px] shadow-inner transition-colors ${t.status === 'warning' ? 'bg-orange-500/15 text-orange-400 border-orange-500/30 shadow-[0_0_10px_rgba(249,115,22,0.2)]' : 'bg-black/60 text-gray-300 border-white/10'}`}>
                     {t.val}
                   </div>
                 </motion.div>
               ))}
"""

content = content.replace(old_telemetry.strip(), new_telemetry.strip())

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
