with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

target = "setLoading(true);"
replacement = "setLoading(true);\\n    setTelemetry([]); // Clear any DVR telemetry"

# But wait, there are two setLoading(true) in the file. Let's be more specific.
target2 = "if (dvrMode) return;\\n    setLoading(true);"
replacement2 = "if (dvrMode) return;\\n    setLoading(true);\\n    setTelemetry([]); // Clear any DVR telemetry"
content = content.replace(target2, replacement2)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
