# Teeow.ai Microservices Backend

This is the backend architecture for Teeow.ai, built with FastAPI in a modular microservices structure.

## 🚀 Getting Started

### 1. Install Dependencies (Locally)
```bash
pip install -r requirements.txt
```

### 2. Run All Services (Locally)
```bash
python run_all_services.py
```

### 3. Run via Docker
```bash
docker build -t teeow_ai .
docker run -p 8000-8006:8000-8006 teeow_ai
```

### 4. Or Use Docker Compose
```bash
docker-compose up --build
```

Each service runs on its own port:
- `api_gateway`: 8000
- `user_management_service`: 8001
- `chat_service`: 8002
- `ai_assistant_service`: 8003
- `trip_service`: 8004
- `external_api_proxy_service`: 8005
- `payment_service`: 8006
