from fastapi import FastAPI

app = FastAPI(
    title="SlopeGuard API",
    description="AI-Powered Landslide Risk Prediction and Early Warning System",
    version="1.0.0",
)

@app.get("/")
async def root():
    return {"message": "SlopeGuard API is running. Systems online."}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
