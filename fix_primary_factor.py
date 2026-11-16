with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

target = """                <motion.button 
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
                </motion.button>"""

replacement = """                <motion.button 
                  whileHover={{ y: -2, scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setActiveModal('factor')}
                  className={`w-full ${(riskStyles[data.risk_level as keyof typeof riskStyles] || riskStyles.LOW).boxBg} border ${(riskStyles[data.risk_level as keyof typeof riskStyles] || riskStyles.LOW).boxBorder} rounded-2xl p-4 flex gap-4 items-start transition-all text-left focus:outline-none shadow-sm group`}
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

content = content.replace(target, replacement)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
