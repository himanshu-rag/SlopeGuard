with open("README.md", "r") as f:
    content = f.read()

mermaid_old = """```mermaid
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
```"""

mermaid_new = """```mermaid
flowchart TD
    subgraph Frontend [Frontend Command Center]
        UI["Bento UI / Framer Motion"]
        Map["MapLibre GL JS"]
        WS_Client["WebSocket Client"]
    end

    subgraph Backend [Backend API Engine]
        API["REST API"]
        WS_Server["Telemetry Stream"]
        DB_Layer["PostGIS & SQLAlchemy"]
    end

    subgraph Intelligence [ML Fusion Core]
        XGB["XGBoost: Susceptibility"]
        LSTM["PyTorch: Trigger Model"]
        ONNX["ONNX Runtime"]
    end

    subgraph DataSources [Live Data Feeds]
        OpenMeteo["Open-Meteo Archive"]
        IoT["Physical Hardware Nodes"]
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
```"""

content = content.replace(mermaid_old, mermaid_new)

with open("README.md", "w") as f:
    f.write(content)
