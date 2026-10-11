# AegisCommerce

**AegisCommerce** is a next-generation, high-performance E-Commerce Platform featuring **Multimodal Search**, **Multi-Agent AI Workflows**, and an **Event-Driven Microservices Architecture**.

---

## 🏛️ System Architecture

```text
aegis-commerce/
├── docker/                 # Containerization (Dockerfiles & Compose)
│   ├── api.Dockerfile
│   ├── worker.Dockerfile
│   └── docker-compose.yml
├── services/               # Microservices & Frontends
│   ├── backend/            # FastAPI, LangChain/LangGraph Agents, Celery Workers
│   │   ├── app/
│   │   │   ├── api/v1/endpoints/
│   │   │   ├── core/
   │   │   ├── models/
   │   │   ├── schemas/
   │   │   ├── services/
   │   │   └── main.py
│   │   ├── workers/        # Async task processors (Image embeddings, Event listeners)
│   │   ├── agents/         # Multi-Agent orchestrators & specialized tools
│   │   │   ├── nodes/
│   │   │   └── tools/
│   │   ├── tests/
│   │   └── requirements.txt
│   ├── web/                # Web Frontend Application (Next.js / React)
│   └── mobile/             # Mobile Application (React Native / Flutter)
├── scripts/                # DevOps & Automation Utilities
├── .env.example            # Environment templates
└── README.md               # Project documentation
```

---

## 🚀 Key Features

1. **Multimodal Vector Search:** Search products using text descriptions, images, or hybrid queries (CLIP + Qdrant / PgVector).
2. **Multi-Agent Intelligence:** Autonomous agents for customer support, dynamic pricing, product recommendation, and order processing (LangGraph).
3. **Event-Driven Microservices:** Asynchronous messaging via RabbitMQ / Redis Streams for order status, inventory updates, and notifications.
4. **Containerized MLOps Infrastructure:** Production-ready Docker Compose environment with health checks and worker scaling.

---

## 🛠️ Quick Start Guide

### Prerequisites
- Docker & Docker Compose
- Python 3.11+

### Running with Docker Compose
```bash
# 1. Clone & enter directory
cd aegis-commerce

# 2. Configure Environment Variables
cp .env.example .env

# 3. Start Infrastructure & Backend
docker-compose -f docker/docker-compose.yml up --build -d

# 4. Access Services:
# FastAPI Docs: http://localhost:8000/docs
# Qdrant Dashboard: http://localhost:6333/dashboard
# RabbitMQ Management: http://localhost:15672
```

---

## 🧪 Local Backend Setup (Without Docker)

```bash
cd services/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```
