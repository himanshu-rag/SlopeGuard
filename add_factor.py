import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# Make the Primary Factor box a button
old_factor = """
                <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-4 flex gap-3 items-start">
                  <AlertTriangle className="text-red-400 shrink-0 mt-0.5" size={18} />
                  <div>
                    <h4 className="text-[10px] font-bold text-red-400 uppercase tracking-widest mb-1.5">Primary Factor</h4>
                    <p className="text-xs text-red-300/80 leading-relaxed font-medium">
                      {data.reason_code?.replace(/_/g, ' ') || 'AWAITING TELEMETRY'}
                    </p>
                  </div>
                </div>
"""
new_factor = """
                <motion.button 
                  whileHover={{ y: -2, scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setActiveModal('factor')}
                  className="w-full bg-red-500/10 border border-red-500/20 rounded-2xl p-4 flex gap-4 items-start hover:bg-red-500/20 transition-all text-left focus:outline-none shadow-[0_0_15px_rgba(239,68,68,0.1)] hover:shadow-[0_0_20px_rgba(239,68,68,0.2)] group"
                >
                  <div className="p-2 bg-red-500/20 rounded-lg group-hover:bg-red-500/30 transition-colors">
                     <AlertTriangle className="text-red-400 shrink-0" size={16} />
                  </div>
                  <div>
                    <h4 className="text-[10px] font-black text-red-400 uppercase tracking-widest mb-1">Primary Factor</h4>
                    <p className="text-xs text-red-300 font-bold tracking-wide">
                      {data.reason_code?.replace(/_/g, ' ') || 'AWAITING TELEMETRY'}
                    </p>
                  </div>
                </motion.button>
"""
content = content.replace(old_factor.strip(), new_factor.strip())

# Add the 'factor' modal
new_modal = """
              {activeModal === 'factor' && (
                 <div className="flex flex-col h-full">
                    <div className="flex items-center justify-between mb-6 pb-6 border-b border-red-500/20">
                      <div className="flex items-center gap-4">
                        <div className="p-3 bg-red-500/20 rounded-2xl border border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.3)]">
                           <ShieldAlert size={24} className="text-red-400" />
                        </div>
                        <div>
                           <h3 className="text-2xl font-black text-white tracking-tight">AI Reasoning Trace</h3>
                           <p className="text-[10px] text-red-400 font-black uppercase tracking-[0.2em] mt-1">Neural Network Diagnostics</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-black/80 rounded-2xl p-5 border border-white/10 font-mono text-[10px] text-green-400/80 mb-6 shadow-inner relative overflow-hidden">
                       <div className="absolute top-0 left-0 w-full h-[1px] bg-green-500/30 shadow-[0_0_10px_#22c55e]" />
                       <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}><p className="mb-2">&gt; INIT XGB_TERRAIN_CLASSIFIER...</p></motion.div>
                       <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}><p className="mb-2">&gt; ANALYZING GEOMORPHOLOGY: SLOPE={currentZone.slope}° TWI={currentZone.twi}</p></motion.div>
                       <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }}><p className="mb-2 text-orange-400 font-bold">&gt; WARNING: GEOMETRY EXCEEDS STABILITY THRESHOLDS</p></motion.div>
                       <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.0 }}><p className="mb-2">&gt; INIT LSTM_TRIGGER_MODEL...</p></motion.div>
                       <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.3 }}><p className="mb-2">&gt; ANALYZING 30-DAY PRECIPITATION TENSORS...</p></motion.div>
                       <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.6 }}><p className="text-red-400 font-black text-xs mt-4">&gt; FINAL CLASSIFICATION: {data.reason_code?.replace(/_/g, ' ')}</p></motion.div>
                    </div>

                    <div>
                       <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                          <Check size={14} className="text-blue-400" /> Recommended Commander Action
                       </h4>
                       <div className="bg-white/5 p-5 rounded-2xl border border-white/10 text-sm text-gray-300 leading-relaxed shadow-lg">
                          {data.reason_code === 'HIGH_TERRAIN_SUSCEPTIBILITY' ? 
                            "The physical geometry of this zone is highly unstable. While current weather is not extreme, any minor seismic activity or sudden cloudburst will result in immediate catastrophic failure. Pre-position heavy excavation equipment at the base and restrict heavy transit." : 
                            "The soil has reached absolute saturation due to prolonged rainfall. The terrain itself is moderately stable, but the hydrostatic pressure is critical. Initiate mandatory evacuation of all structures within a 500m radius of the slope base immediately."}
                       </div>
                    </div>
                 </div>
              )}
"""

# Insert the new modal right after the XGB modal
content = content.replace(
    "              {activeModal === 'xgb' && (", 
    new_modal + "\n              {activeModal === 'xgb' && ("
)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
