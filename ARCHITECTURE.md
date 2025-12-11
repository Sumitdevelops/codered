# AI Workload Orchestrator - System Architecture

## System Flow Diagram

```mermaid
flowchart TD
    Start([User Submits Task via Demo UI]) --> Ingest[Task Ingestion Module<br/>FastAPI Endpoint]
    
    Ingest --> Validate{Validate Task<br/>Metadata}
    Validate -->|Invalid| Error[Return Error to UI]
    Validate -->|Valid| Metrics[Metrics Collector]
    
    Metrics --> Collect[Collect Real-Time Metrics:<br/>- Edge Load<br/>- Cloud Load<br/>- GPU Load<br/>- Network Latency<br/>- Cost Multipliers]
    
    Collect --> ML[AI Decision Engine<br/>RandomForest Model]
    
    ML --> Features[Extract Features:<br/>1. Task Priority<br/>2. Latency Requirement<br/>3. GPU Requirement<br/>4. Node Loads<br/>5. Cost Sensitivity]
    
    Features --> Predict[ML Model Inference<br/>96.55% Accuracy]
    
    Predict --> Decision{Routing Decision}
    
    Decision -->|EDGE| EdgeNode[Edge Node<br/>Low Latency<br/>50-150ms<br/>$0.01/task]
    Decision -->|CLOUD| CloudNode[Cloud Node<br/>High Compute<br/>200-500ms<br/>$0.025/task]
    Decision -->|GPU| GPUNode[GPU Node<br/>ML Accelerated<br/>300-600ms<br/>$0.05/task]
    
    EdgeNode --> Execute1[Execute Task]
    CloudNode --> Execute2[Execute Task]
    GPUNode --> Execute3[Execute Task]
    
    Execute1 --> Results[Collect Results:<br/>- Execution Time<br/>- Cost<br/>- Status]
    Execute2 --> Results
    Execute3 --> Results
    
    Results --> Log[Log to SQLite Database]
    Log --> Metrics2[Update Prometheus Metrics]
    Metrics2 --> UI[Return to Demo UI]
    
    UI --> Display[Display Results:<br/>✓ Chosen Node<br/>✓ Confidence Score<br/>✓ Execution Time<br/>✓ Cost<br/>✓ AI Explanation]
    
    Display --> Monitor{User Actions}
    Monitor -->|View History| Dashboard[Admin Dashboard]
    Monitor -->|Submit Another| Start
    Monitor -->|View Metrics| Grafana[Grafana Visualization]
    
    Dashboard --> Charts[Interactive Charts:<br/>- Task Distribution<br/>- Cost Analysis<br/>- Node Health<br/>- Performance Trends]
    
    Grafana --> Dashboards[Pre-configured Dashboards:<br/>- Workload Distribution<br/>- Execution Latency<br/>- Cost Tracking]
    
    style ML fill:#4CAF50,color:#fff
    style Predict fill:#2196F3,color:#fff
    style Decision fill:#FF9800,color:#fff
    style EdgeNode fill:#8BC34A,color:#fff
    style CloudNode fill:#03A9F4,color:#fff
    style GPUNode fill:#E91E63,color:#fff
```

## Component Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[Demo UI - Streamlit<br/>Port 8501]
        Dashboard[Admin Dashboard - Streamlit<br/>Port 8502]
    end
    
    subgraph "Orchestrator Service - Port 8000"
        API[FastAPI Routes]
        Engine[AI Decision Engine<br/>RandomForest ML Model]
        Collector[Metrics Collector]
        Scheduler[Task Scheduler]
        DB[(SQLite Database)]
    end
    
    subgraph "Compute Nodes"
        Edge[Edge Node<br/>Port 8001<br/>Low Latency]
        Cloud[Cloud Node<br/>Port 8002<br/>High Compute]
        GPU[GPU Node<br/>Port 8003<br/>GPU Accelerated]
    end
    
    subgraph "Monitoring Stack"
        Prom[Prometheus<br/>Port 9090]
        Graf[Grafana<br/>Port 3000]
    end
    
    UI -->|HTTP POST| API
    Dashboard -->|HTTP GET| API
    
    API --> Engine
    API --> Collector
    API --> Scheduler
    API --> DB
    
    Engine --> Scheduler
    Collector --> Engine
    
    Scheduler -->|Dispatch| Edge
    Scheduler -->|Dispatch| Cloud
    Scheduler -->|Dispatch| GPU
    
    API -->|Export| Prom
    Graf -->|Query| Prom
    
    style Engine fill:#4CAF50,color:#fff
    style UI fill:#2196F3,color:#fff
    style Dashboard fill:#2196F3,color:#fff
    style Edge fill:#8BC34A,color:#fff
    style Cloud fill:#03A9F4,color:#fff
    style GPU fill:#E91E63,color:#fff
```

## ML Model Decision Flow

```mermaid
flowchart LR
    Input[Task Input] --> F1[Priority: 1-10]
    Input --> F2[Latency Req: 1-10]
    Input --> F3[Requires GPU: 0/1]
    Input --> F4[Edge Load: 0-100%]
    Input --> F5[Cloud Load: 0-100%]
    Input --> F6[GPU Load: 0-100%]
    Input --> F7[Network Latency: 10-500ms]
    Input --> F8[Cost Sensitivity: 1-10]
    
    F1 --> Model[RandomForest<br/>Classifier<br/>96.55% Accuracy]
    F2 --> Model
    F3 --> Model
    F4 --> Model
    F5 --> Model
    F6 --> Model
    F7 --> Model
    F8 --> Model
    
    Model --> Prob[Probability<br/>Distribution]
    
    Prob --> P1[EDGE: 0.05]
    Prob --> P2[CLOUD: 0.03]
    Prob --> P3[GPU: 0.92]
    
    P1 --> Max{Select<br/>Max}
    P2 --> Max
    P3 --> Max
    
    Max --> Output[GPU Node<br/>92% Confidence]
    
    style Model fill:#4CAF50,color:#fff
    style F3 fill:#FF9800,color:#fff
    style Output fill:#E91E63,color:#fff
```

## Technology Stack

```mermaid
graph TB
    subgraph "Backend"
        FastAPI[FastAPI<br/>Async REST API]
        ML[Scikit-learn<br/>RandomForest]
        Python[Python 3.11<br/>Type Hints]
    end
    
    subgraph "Frontend"
        Streamlit[Streamlit<br/>Interactive UI]
        Plotly[Plotly<br/>Visualizations]
    end
    
    subgraph "Data"
        SQLite[(SQLite<br/>Task History)]
        Pandas[Pandas<br/>Data Processing]
    end
    
    subgraph "Monitoring"
        Prometheus[Prometheus<br/>Metrics]
        Grafana[Grafana<br/>Dashboards]
    end
    
    subgraph "Infrastructure"
        Docker[Docker<br/>Containerization]
        Compose[Docker Compose<br/>Orchestration]
    end
    
    Python --> FastAPI
    Python --> ML
    FastAPI --> SQLite
    
    Streamlit --> Plotly
    Streamlit --> Pandas
    
    FastAPI --> Prometheus
    Grafana --> Prometheus
    
    Docker --> Compose
    
    style FastAPI fill:#009688,color:#fff
    style ML fill:#4CAF50,color:#fff
    style Streamlit fill:#2196F3,color:#fff
    style Docker fill:#2496ED,color:#fff
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Local Development"
        Local[5 Python Processes<br/>Running Locally]
    end
    
    subgraph "Docker Deployment"
        Compose[Docker Compose]
        
        subgraph "Containers"
            C1[orchestrator:8000]
            C2[edge-node:8001]
            C3[cloud-node:8002]
            C4[gpu-node:8003]
            C5[demo-ui:8501]
            C6[admin-dashboard:8502]
            C7[prometheus:9090]
            C8[grafana:3000]
        end
        
        Network[Bridge Network]
    end
    
    subgraph "Cloud Production (Future)"
        AWS[AWS Lambda +<br/>Lambda@Edge +<br/>SageMaker]
        Azure[Azure Functions +<br/>CDN +<br/>ML Service]
        GCP[Cloud Functions +<br/>Cloud CDN +<br/>AI Platform]
    end
    
    Local --> Compose
    Compose --> Network
    Network --> C1
    Network --> C2
    Network --> C3
    Network --> C4
    Network --> C5
    Network --> C6
    Network --> C7
    Network --> C8
    
    style Local fill:#8BC34A,color:#fff
    style Compose fill:#2496ED,color:#fff
    style AWS fill:#FF9900,color:#fff
    style Azure fill:#0078D4,color:#fff
    style GCP fill:#4285F4,color:#fff
```

## Key Features Highlighted

### ✅ Real-Time Workload Analysis
- Dynamic metrics collection every request
- ML-based decision making (<10ms inference)
- Adaptive load balancing

### ✅ Automated Resource Allocation
- Zero manual intervention required
- Intelligent routing based on 8 features
- 96.55% routing accuracy

### ✅ Performance Monitoring
- Prometheus metrics export
- Grafana visualization dashboards
- SQLite persistent logging
- Real-time admin dashboard

### ✅ Cost Optimization
- Per-task cost tracking
- Cost-aware routing decisions
- Total cost analytics

### ✅ Industry Applications
- **Finance**: Fraud detection (Edge - low latency)
- **Healthcare**: Medical imaging (GPU - ML acceleration)
- **Logistics**: Route optimization (Cloud - batch processing)
- **Manufacturing**: IoT sensor processing (Edge - real-time)
