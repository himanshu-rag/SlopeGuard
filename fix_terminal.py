import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

old_modal = """
                    <div className="bg-black/80 rounded-2xl p-5 border border-white/10 font-mono text-[10px] text-green-400/80 mb-6 shadow-inner relative overflow-hidden">
                       <div className="absolute top-0 left-0 w-full h-[1px] bg-green-500/30 shadow-[0_0_10px_#22c55e]" />
                       <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}><p className="mb-2">&gt; INIT XGB_TERRAIN_CLASSIFIER...</p></motion.div>
                       <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}><p className="mb-2">&gt; ANALYZING GEOMORPHOLOGY: SLOPE={currentZone.slope}° TWI={currentZone.twi}</p></motion.div>
                       <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }}><p className="mb-2 text-orange-400 font-bold">&gt; WARNING: GEOMETRY EXCEEDS STABILITY THRESHOLDS</p></motion.div>
                       <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.0 }}><p className="mb-2">&gt; INIT LSTM_TRIGGER_MODEL...</p></motion.div>
                       <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.3 }}><p className="mb-2">&gt; ANALYZING 30-DAY PRECIPITATION TENSORS...</p></motion.div>
                       <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.6 }}><p className="text-red-400 font-black text-xs mt-4">&gt; FINAL CLASSIFICATION: {data.reason_code?.replace(/_/g, ' ')}</p></motion.div>
                    </div>
"""

new_modal = """
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
"""

content = content.replace(old_modal.strip(), new_modal.strip())

# Fix title
content = content.replace(">AI Reasoning Trace<", ">Executive Summary<")
content = content.replace(">Neural Network Diagnostics<", ">Plain-Language AI Assessment<")

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
