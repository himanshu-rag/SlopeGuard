with open("frontend/src/App.tsx", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    # Left Panel Badge
    if "bg-yellow-500/10 text-yellow-500" in line:
        lines[i] = line.replace("dvrMode ?", "dvrEvent ?")
    if "bg-yellow-500' : 'bg-red-500'" in line:
        lines[i] = line.replace("dvrMode ?", "dvrEvent ?")
    
    # Right Panel Header
    if "DVR HISTORICAL LOG" in line:
        lines[i] = line.replace("dvrMode ?", "dvrEvent ?")
    if "ARCHIVE" in line:
        lines[i] = line.replace("dvrMode ?", "dvrEvent ?")

with open("frontend/src/App.tsx", "w") as f:
    f.writelines(lines)
