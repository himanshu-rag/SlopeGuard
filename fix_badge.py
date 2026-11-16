with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

target = """              <div className="flex items-center gap-2 bg-red-500/10 text-red-400 px-3 py-1.5 rounded-full text-[10px] font-bold tracking-widest uppercase border border-red-500/20 shadow-[0_0_10px_rgba(239,68,68,0.1)]">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" /> Live
              </div>"""

replacement = """              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-[10px] font-bold tracking-widest uppercase border shadow-sm ${dvrMode ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20 shadow-[0_0_10px_rgba(234,179,8,0.1)]' : 'bg-red-500/10 text-red-400 border-red-500/20 shadow-[0_0_10px_rgba(239,68,68,0.1)]'}`}>
                <span className={`w-2 h-2 rounded-full animate-pulse ${dvrMode ? 'bg-yellow-500' : 'bg-red-500'}`} /> {dvrMode ? 'REPLAY' : 'Live'}
              </div>"""

content = content.replace(target, replacement)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
