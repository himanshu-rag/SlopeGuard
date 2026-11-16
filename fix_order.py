with open("frontend/src/App.tsx", "r") as f:
    lines = f.readlines()

out_lines = []
for i in range(len(lines)):
    line = lines[i]
    if "useEffect(() => {" in line and "if (dvrMode) return; setEvacuationRoute(null); }, [currentZone.id, dvrMode]);" in lines[i+1]:
        # Delete these two lines and we'll reinsert them AFTER dvrMode is declared.
        lines[i] = ""
        lines[i+1] = ""
        continue
    
    out_lines.append(line)

# Now we need to insert the useEffect right after `const [dvrEvent, setDvrEvent] = useState<string | null>(null);`
final_lines = []
for line in out_lines:
    final_lines.append(line)
    if "const [dvrEvent, setDvrEvent] = useState<string | null>(null);" in line:
        final_lines.append("  useEffect(() => { if (dvrMode) return; setEvacuationRoute(null); }, [currentZone.id, dvrMode]);\n")

with open("frontend/src/App.tsx", "w") as f:
    f.writelines(final_lines)

