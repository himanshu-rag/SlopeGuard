<div align="center">
  <img src="https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/shield-alert.svg" width="80" height="80" alt="SlopeGuard Icon"/>
  <h1 align="center">SlopeGuard</h1>
  <p align="center">
    <strong>Military-Grade Geospatial AI for Real-Time Landslide Prediction</strong>
  </p>
  <p align="center">
    <a href="#architecture">Architecture</a> • 
    <a href="#ml-engine">ML Engine</a> • 
    <a href="#setup-guide">Setup Guide</a> • 
    <a href="#collaborators">Team</a>
  </p>
</div>

<br/>

## 🌍 Overview
**SlopeGuard** is an advanced risk intelligence platform designed to predict and monitor landslide threats in real time. It fuses live IoT telemetry, physical terrain geometry (XGBoost), and historical rainfall patterns (PyTorch LSTM) to provide a unified, WebGL-powered command center.

Instead of static dashboards, SlopeGuard calculates **probabilistic failure modes** on the fly and routes physical hardware sensors directly onto a 3D-capable map.

---

## 🏗️ System Architecture

SlopeGuard operates on a high-performance modern stack divided into three primary layers:

```mermaid
flowchart TD
    subgraph Frontend [Command Center (React + Vite)]
        UI[Bento UI / Framer Motion]
        Map[MapLibre GL JS]
        WS_Client[WebSocket Client]
    end

    subgraph Backend [FastAPI Engine]
        API[REST API]
        WS_Server[Telemetry Stream]
        DB_Layer[PostGIS & SQLAlchemy]
    end

    subgraph Intelligence [ML Fusion Core]
        XGB[XGBoost: Susceptibility]
        LSTM[PyTorch: Trigger Model]
        ONNX[ONNX Runtime]
    end

    subgraph DataSources [Live Feeds]
        OpenMeteo[Open-Meteo Archive]
        IoT[Physical Hardware Nodes]
    end

    UI --> Map
    UI <--> API
    WS_Client <--> WS_Server
    
    API <--> Intelligence
    API <--> DB_Layer
    
    XGB --> ONNX
    LSTM --> ONNX
    
    OpenMeteo --> DB_Layer
    IoT --> WS_Server
```

---

## 🧠 The AI Pipeline
SlopeGuard does not rely on simple thresholds. It utilizes a scientifically-grounded **Joint Probability Fusion Engine**.

### 1. Terrain Susceptibility (XGBoost)
Evaluates the physical geometry of the mountain.
* **Features:** Slope Angle, Aspect (Direction), Curvature, Topographic Wetness Index (TWI).
* **Model:** Gradient Boosted Trees with Platt Scaling (Calibrated Classifier).
* **Output:** $P(Failure \mid Terrain)$

### 2. Meteorological Trigger (PyTorch LSTM)
Evaluates the sequence and intensity of recent weather.
* **Features:** 30-day sequential rainfall curves, 7-day antecedent moisture, 3-day peak intensity.
* **Model:** 2-layer Long Short-Term Memory (LSTM) network exported via ONNX.
* **Output:** $P(Failure \mid Rainfall)$

### 3. Joint Probability Fusion
Both conditions must be met for a catastrophic event. We calculate the joint probability using a weighted geometric mean of complements:
`Risk Score = [1 - (1 - P_susc)^0.4 * (1 - P_trig)^0.6] * 100`

---

## 🚀 Features
* **Dark-Mode Geospatial Mapping:** Vector-tile rendering via MapLibre GL.
* **Dynamic Geomorphology Inference:** Modifies model predictions on the fly based on the specific lat/lng you are viewing.
* **Live IoT Telemetry:** Real-time WebSockets stream from physical hardware (Inclinometers, Soil Moisture Probes, GPS Displacement).
* **Network Status Grid:** See exactly which nodes (Alpha, Beta, Gamma) are active on the physical slope.

---

## 🛠️ Local Development

### 1. Database Setup
Ensure PostgreSQL with the PostGIS extension is running.
```bash
# Create database
createdb slopeguard
psql -d slopeguard -c "CREATE EXTENSION postgis;"
```

### 2. Backend Engine
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Seed the real-world terrain and rainfall data
python ingest_india.py

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

### 3. ML Model Retraining
```bash
cd ml
source ../backend/venv/bin/activate
python train.py
```

### 4. Command Center (Frontend)
```bash
cd frontend
npm install
npm run dev
```

---

## 🤝 Collaborators
This project is actively maintained and developed by:
* [@himanshu-rag](https://github.com/himanshu-rag)
* [sharmat3420@gmail.com](mailto:sharmat3420@gmail.com)
* [parasnegi378@gmail.com](mailto:parasnegi378@gmail.com)

<div align="center">
  <br/>
  <i>Built to save lives. Deployed at the edge.</i>
</div>
