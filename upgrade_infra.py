with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# Add new icons to import if needed
if "Phone" not in content:
    content = content.replace("from 'lucide-react';", "Phone, Ambulance, Shield, Navigation } from 'lucide-react';")

old_infra = """
          {/* INFRASTRUCTURE CARD */}
          <div className="glass-panel rounded-[2rem] p-6">
            <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-5">Critical Infrastructure at Risk</h3>
            <div className="space-y-3">
              <div className="group flex items-center justify-between bg-black/40 p-3.5 rounded-2xl border border-white/5 hover:bg-white/10 hover:border-white/20 transition-all cursor-pointer">
                <div className="flex items-center gap-3.5">
                  <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center group-hover:bg-blue-500/30 transition-colors">
                    <Activity size={16} className="text-blue-400" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white">District Hospital</div>
                    <div className="text-xs text-gray-500 mt-0.5">Medical Facility • 2.1km</div>
                  </div>
                </div>
                <div className="text-[10px] font-bold text-gray-400 bg-black/60 border border-white/5 px-2.5 py-1.5 rounded-lg tracking-wider">100% EXPOSURE</div>
              </div>

              <div className="group flex items-center justify-between bg-black/40 p-3.5 rounded-2xl border border-white/5 hover:bg-white/10 hover:border-white/20 transition-all cursor-pointer">
                <div className="flex items-center gap-3.5">
                  <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center group-hover:bg-orange-500/30 transition-colors">
                    <Layers size={16} className="text-orange-400" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white">Hwy Bridge 42</div>
                    <div className="text-xs text-gray-500 mt-0.5">Transit Route • 0.8km</div>
                  </div>
                </div>
                <div className="text-[10px] font-bold text-gray-400 bg-black/60 border border-white/5 px-2.5 py-1.5 rounded-lg tracking-wider">EVAC ROUTE</div>
              </div>
            </div>
          </div>
"""

new_infra = """
          {/* INFRASTRUCTURE CARD */}
          <div className="glass-panel rounded-[2rem] p-6">
            <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-5">Critical Infrastructure at Risk</h3>
            <div className="space-y-3">
              <motion.button 
                whileHover={{ y: -3, scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => { handleFlyTo(91.755, 26.155); setActiveModal('hospital'); }}
                className="w-full flex items-center justify-between bg-black/40 p-3.5 rounded-2xl border border-white/5 hover:bg-white/10 hover:border-white/20 transition-all text-left focus:outline-none"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center shadow-[0_0_10px_rgba(59,130,246,0.2)]">
                    <Activity size={16} className="text-blue-400" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white">District Hospital</div>
                    <div className="text-[10px] text-gray-500 mt-0.5 uppercase tracking-wider font-bold">Medical Facility • 2.1km</div>
                  </div>
                </div>
                <div className="text-[9px] font-black text-red-400 bg-red-500/10 border border-red-500/20 px-2.5 py-1.5 rounded-lg tracking-widest shadow-sm">100% EXPOSURE</div>
              </motion.button>

              <motion.button 
                whileHover={{ y: -3, scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => { handleFlyTo(91.730, 26.170); setActiveModal('bridge'); }}
                className="w-full flex items-center justify-between bg-black/40 p-3.5 rounded-2xl border border-white/5 hover:bg-white/10 hover:border-white/20 transition-all text-left focus:outline-none"
              >
                <div className="flex items-center gap-3.5">
                  <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center shadow-[0_0_10px_rgba(249,115,22,0.2)]">
                    <Layers size={16} className="text-orange-400" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white">Hwy Bridge 42</div>
                    <div className="text-[10px] text-gray-500 mt-0.5 uppercase tracking-wider font-bold">Transit Route • 0.8km</div>
                  </div>
                </div>
                <div className="text-[9px] font-black text-orange-400 bg-orange-500/10 border border-orange-500/20 px-2.5 py-1.5 rounded-lg tracking-widest shadow-sm">EVAC ROUTE</div>
              </motion.button>
            </div>
          </div>
"""

content = content.replace(old_infra.strip(), new_infra.strip())

# Add new modals
new_modals = """
              {activeModal === 'hospital' && (
                 <div className="flex flex-col h-full">
                    <div className="flex items-center justify-between mb-8 pb-6 border-b border-white/10">
                      <div className="flex items-center gap-4">
                        <div className="p-4 bg-blue-500/20 rounded-[1.25rem] border border-blue-500/30 shadow-[0_0_20px_rgba(59,130,246,0.3)]">
                           <Activity size={28} className="text-blue-400" />
                        </div>
                        <div>
                           <h3 className="text-2xl font-black text-white tracking-tight">District Hospital</h3>
                           <p className="text-[10px] text-red-400 font-black uppercase tracking-[0.2em] mt-1">100% Slide Exposure</p>
                        </div>
                      </div>
                      <div className="text-right">
                         <div className="text-3xl font-black text-white">450</div>
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
              )}

              {activeModal === 'bridge' && (
                 <div className="flex flex-col h-full">
                    <div className="flex items-center justify-between mb-8 pb-6 border-b border-white/10">
                      <div className="flex items-center gap-4">
                        <div className="p-4 bg-orange-500/20 rounded-[1.25rem] border border-orange-500/30 shadow-[0_0_20px_rgba(249,115,22,0.3)]">
                           <Layers size={28} className="text-orange-400" />
                        </div>
                        <div>
                           <h3 className="text-2xl font-black text-white tracking-tight">Hwy Bridge 42</h3>
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
              )}
"""

# Insert the new modals right after the XGB modal
content = content.replace(
    "              {activeModal === 'xgb' && (", 
    new_modals + "\n              {activeModal === 'xgb' && ("
)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
