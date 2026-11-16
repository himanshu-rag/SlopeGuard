with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

# 1. Inject the riskStyles mapping
target_map = "  const [searchQuery, setSearchQuery] = useState(\"\");"
new_map = """  const [searchQuery, setSearchQuery] = useState("");
  
  const riskStyles = {
    CRITICAL: { title: 'text-red-500', boxBg: 'bg-red-500/5', boxBorder: 'border-red-500/20', icon: 'text-red-400', iconBg: 'bg-red-500/20 group-hover:bg-red-500/30', label: 'text-red-400', desc: 'text-red-300' },
    HIGH: { title: 'text-orange-500', boxBg: 'bg-orange-500/5', boxBorder: 'border-orange-500/20', icon: 'text-orange-400', iconBg: 'bg-orange-500/20 group-hover:bg-orange-500/30', label: 'text-orange-400', desc: 'text-orange-300' },
    MEDIUM: { title: 'text-yellow-500', boxBg: 'bg-yellow-500/5', boxBorder: 'border-yellow-500/20', icon: 'text-yellow-400', iconBg: 'bg-yellow-500/20 group-hover:bg-yellow-500/30', label: 'text-yellow-400', desc: 'text-yellow-300' },
    LOW: { title: 'text-emerald-500', boxBg: 'bg-emerald-500/5', boxBorder: 'border-emerald-500/20', icon: 'text-emerald-400', iconBg: 'bg-emerald-500/20 group-hover:bg-emerald-500/30', label: 'text-emerald-400', desc: 'text-emerald-300' }
  };"""
content = content.replace(target_map, new_map)

# 2. Replace the hardcoded RISK level text color
target_risk_text = '<div className="text-sm font-bold text-red-400 tracking-wide">{data.risk_level} RISK</div>'
new_risk_text = '<div className={`text-sm font-bold tracking-wide ${(riskStyles[data.risk_level as keyof typeof riskStyles] || riskStyles.LOW).title}`}>{data.risk_level} RISK</div>'
content = content.replace(target_risk_text, new_risk_text)

# 3. Replace the Primary Factor Box
target_factor_box = """                <motion.button 
                  onClick={() => setActiveModal('factor')}
                  whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}
                  className="w-full mt-4 bg-red-500/5 border border-red-500/20 rounded-2xl p-4 flex items-start gap-3 relative overflow-hidden group text-left focus:outline-none"
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
                </motion.button>"""

new_factor_box = """                <motion.button 
                  onClick={() => setActiveModal('factor')}
                  whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}
                  className={`w-full mt-4 ${(riskStyles[data.risk_level as keyof typeof riskStyles] || riskStyles.LOW).boxBg} border ${(riskStyles[data.risk_level as keyof typeof riskStyles] || riskStyles.LOW).boxBorder} rounded-2xl p-4 flex items-start gap-3 relative overflow-hidden group text-left focus:outline-none transition-colors`}
                >
                  <div className={`p-2 ${(riskStyles[data.risk_level as keyof typeof riskStyles] || riskStyles.LOW).iconBg} rounded-lg transition-colors`}>
                     <AlertTriangle className={`${(riskStyles[data.risk_level as keyof typeof riskStyles] || riskStyles.LOW).icon} shrink-0`} size={16} />
                  </div>
                  <div>
                    <h4 className={`text-[10px] font-black ${(riskStyles[data.risk_level as keyof typeof riskStyles] || riskStyles.LOW).label} uppercase tracking-widest mb-1`}>Primary Factor</h4>
                    <p className={`text-xs ${(riskStyles[data.risk_level as keyof typeof riskStyles] || riskStyles.LOW).desc} font-bold tracking-wide`}>
                      {data.reason_code?.replace(/_/g, ' ') || 'AWAITING TELEMETRY'}
                    </p>
                  </div>
                </motion.button>"""

content = content.replace(target_factor_box, new_factor_box)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
