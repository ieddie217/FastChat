# FastChat Backend

A scalable, production-ready **FastAPI backend** with JWT authentication, Azure OpenAI integration, and structured logging.  
Designed to serve as the backend for an AI-powered chatbot UI.

## Features

- **FastAPI** – High-performance Python backend framework
- **JWT Authentication** – Secure login & protected endpoints
- **Async Azure OpenAI Integration** – Streaming chat completions
- **Audit Logging** – Request-level tracking for observability
- **Structured Project Layout** – Clean and production-friendly architecture

## API Endpoints

| Method | Endpoint      | Auth Required | Description               |
| ------ | ------------- | ------------- | ------------------------- |
| POST   | `/auth/login` | ❌ No         | Obtain JWT access token   |
| POST   | `/chat`       | ✅ Yes        | Send chat messages to GPT |
| GET    | `/health`     | ❌ No         | Service liveness check    |

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/fastchat-backend.git
cd fastchat-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

```
curl -X POST http://localhost:8000/chat \
     -H "Authorization: Bearer <JWT>" \
     -H "Content-Type: application/json" \
     -d '{
           "messages": [{"role":"user","content":"Hello!"}]
         }'
```
