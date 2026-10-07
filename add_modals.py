with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# Add state
if "activeModal" not in content:
    content = content.replace(
        "const [searchQuery, setSearchQuery] = useState(\"\");", 
        "const [searchQuery, setSearchQuery] = useState(\"\");\n  const [activeModal, setActiveModal] = useState<'lstm' | 'xgb' | null>(null);"
    )

# Replace cards to add motion.button and onClick
old_lstm = """<div className="bg-black/40 border border-white/5 rounded-2xl p-4 relative overflow-hidden group hover:bg-black/60 transition-colors cursor-default">"""
new_lstm = """<motion.button whileHover={{ y: -4, scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={() => setActiveModal('lstm')} className="bg-black/40 border border-white/5 rounded-2xl p-4 relative overflow-hidden group hover:bg-black/60 transition-colors text-left focus:outline-none">"""
content = content.replace(old_lstm, new_lstm, 1) # Only first one for LSTM

old_xgb = """<div className="bg-black/40 border border-white/5 rounded-2xl p-4 relative overflow-hidden group hover:bg-black/60 transition-colors cursor-default">"""
new_xgb = """<motion.button whileHover={{ y: -4, scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={() => setActiveModal('xgb')} className="bg-black/40 border border-white/5 rounded-2xl p-4 relative overflow-hidden group hover:bg-black/60 transition-colors text-left focus:outline-none">"""
content = content.replace(old_xgb, new_xgb, 1) # Second one for XGB

# Close the buttons
content = content.replace("</svg>\n                  </div>\n                  \n                  <motion.button whileHover={{ y: -4, scale: 1.02 }}", "</svg>\n                  </motion.button>\n                  \n                  <motion.button whileHover={{ y: -4, scale: 1.02 }}")
content = content.replace("</svg>\n                  </div>\n                </div>", "</svg>\n                  </motion.button>\n                </div>")


modal_ui = """
      {/* BOTTOM PANEL: TIME SERIES SCRUBBER */}
"""

new_modal_ui = """
      {/* DETAILS MODAL */}
      <AnimatePresence>
        {activeModal && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-md p-4 pointer-events-auto"
            onClick={() => setActiveModal(null)}
          >
            <motion.div 
              initial={{ scale: 0.9, y: 20, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.9, y: 20, opacity: 0 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="glass-panel rounded-[2rem] p-7 w-[400px] relative overflow-hidden shadow-2xl"
              onClick={e => e.stopPropagation()}
            >
              <button 
                onClick={() => setActiveModal(null)}
                className="absolute top-4 right-4 text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 p-2 rounded-full transition-colors"
              >
                <X size={16} />
              </button>

              {activeModal === 'lstm' && (
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
                               animate={{ height: `${Math.max(8, (val / Math.max(...rainData.slice(-7), 50)) * 100)}%` }}
                               transition={{ delay: i * 0.1, type: "spring", stiffness: 100 }}
                               className="w-full bg-gradient-to-t from-blue-600/40 to-blue-400/80 rounded-t-lg hover:to-blue-400 transition-all cursor-pointer shadow-[0_0_15px_rgba(59,130,246,0.2)]"
                            />
                            <div className="text-[9px] text-gray-500 font-extrabold uppercase mt-3">T-{6-i}</div>
                         </div>
                       ))}
                    </div>
                 </div>
              )}

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
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* BOTTOM PANEL: TIME SERIES SCRUBBER */}
"""

content = content.replace(modal_ui.strip(), new_modal_ui.strip())
with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
