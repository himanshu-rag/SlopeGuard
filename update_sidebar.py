import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# Add Wifi/Battery icons if missing
if "Wifi" not in content:
    content = content.replace("from 'lucide-react';", "Wifi, Battery, Cpu } from 'lucide-react';")

old_sidebar = """
      {/* RIGHT PANEL: LIVE TELEMETRY FEED */}
      <aside className="absolute top-28 right-6 z-10 w-72 pointer-events-auto">
        <div className="glass-panel rounded-[2rem] p-5">
           <div className="flex items-center justify-between mb-5">
             <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                <Radio size={12} className="text-green-400 animate-pulse" /> IoT Telemetry Feed
             </h3>
             <span className="text-[10px] text-gray-500 font-medium">LIVE (WS)</span>
           </div>
           
           <div className="space-y-3">
"""

new_sidebar = """
      {/* RIGHT PANEL: LIVE TELEMETRY FEED */}
      <aside className="absolute top-28 right-6 z-10 w-80 pointer-events-auto">
        
        {/* HARDWARE STATUS GRID */}
        <div className="glass-panel rounded-[1.5rem] p-4 mb-4 flex gap-2">
           <div className="flex-1 bg-black/40 border border-white/5 rounded-xl p-2.5 relative overflow-hidden group">
              <div className="flex justify-between items-start mb-2">
                 <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)] animate-pulse" />
                 <Wifi size={10} className="text-green-400" />
              </div>
              <div className="text-[9px] font-black text-white tracking-widest uppercase">Node-Alpha</div>
              <div className="text-[8px] text-gray-500 font-bold tracking-widest uppercase mt-0.5">Crest</div>
           </div>
           <div className="flex-1 bg-black/40 border border-white/5 rounded-xl p-2.5 relative overflow-hidden group">
              <div className="flex justify-between items-start mb-2">
                 <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)] animate-pulse" />
                 <Wifi size={10} className="text-green-400" />
              </div>
              <div className="text-[9px] font-black text-white tracking-widest uppercase">Node-Beta</div>
              <div className="text-[8px] text-gray-500 font-bold tracking-widest uppercase mt-0.5">Mid-Slope</div>
           </div>
           <div className="flex-1 bg-black/40 border border-red-500/20 rounded-xl p-2.5 relative overflow-hidden group">
              <div className="flex justify-between items-start mb-2">
                 <div className="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]" />
                 <Wifi size={10} className="text-red-400 opacity-50" />
              </div>
              <div className="text-[9px] font-black text-gray-400 tracking-widest uppercase">Node-Gamma</div>
              <div className="text-[8px] text-red-500 font-bold tracking-widest uppercase mt-0.5">Offline</div>
           </div>
        </div>

        <div className="glass-panel rounded-[2rem] p-5">
           <div className="flex items-center justify-between mb-5">
             <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                <Radio size={12} className="text-blue-400 animate-pulse" /> Real-Time Packet Stream
             </h3>
             <span className="text-[9px] font-black text-blue-400 bg-blue-500/10 px-2 py-1 rounded-lg border border-blue-500/20 shadow-sm">TCP/IP</span>
           </div>
           
           <div className="space-y-3">
"""

content = content.replace(old_sidebar.strip(), new_sidebar.strip())

# Update the telemetry mapping to show Node ID
old_feed_item = """
                     <div>
                       <div className="text-[13px] font-bold text-white tracking-tight">{t.type}</div>
                       <div className="text-[9px] font-black text-gray-500 uppercase tracking-widest mt-1">{t.time}</div>
                     </div>
"""
new_feed_item = """
                     <div>
                       <div className="flex items-center gap-2 mb-0.5">
                          <Cpu size={10} className="text-gray-500" />
                          <div className="text-[9px] font-black text-gray-400 uppercase tracking-widest">{t.node_id || 'NODE-Alpha'}</div>
                       </div>
                       <div className="text-[13px] font-bold text-white tracking-tight leading-none">{t.type}</div>
                     </div>
"""
content = content.replace(old_feed_item.strip(), new_feed_item.strip())

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
