with open('main.py', 'r') as f:
    content = f.read()

new_content = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SlopeGuard API",
    description="AI-Powered Landslide Risk Prediction and Early Warning System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""

content = content.replace('from fastapi import FastAPI\n\napp = FastAPI(\n    title="SlopeGuard API",\n    description="AI-Powered Landslide Risk Prediction and Early Warning System",\n    version="1.0.0",\n)', new_content)

with open('main.py', 'w') as f:
    f.write(content)
