# FastChat Backend

A production-ready **FastAPI** backend with **JWT authentication**, **async Azure OpenAI** integration, and **structured + audit logging**. Built to power a chat UI (e.g., Next.js).

## ✨ Features

- **FastAPI** with async endpoints
- **JWT** login and protected routes
- **Azure OpenAI** chat completions
- **Structured logging** + request IDs + audit trail
- Clean, extensible project layout

## 🛠️ Tech Stack

**Python** • **FastAPI** • **Uvicorn** • **Pydantic v2** • **PyJWT** • **HTTPX** • **Azure OpenAI**

## 🚀 Quick Start

```bash
git clone https://github.com/ieddie217/FastChat.git
cd FastChat
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Unix/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and fill in ENDPOINT, KEY, JWT_SECRET, etc.

# Run the server
uvicorn app.main:app --reload
```

## 🔐 Authentication

### Obtain a JWT Access Token

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo123"
```

### Use the Token for Chat

```bash
TOKEN="<paste_your_token_here>"
curl -s -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Say hello!"}]}'
```

## 🏥 Health Endpoints

- `GET /health` - Basic liveness check
- `GET /health/secure` - Requires JWT authentication
- `GET /health/full` - Uptime + cached Azure GPT probe

## 📁 Project Structure

```
app/
├── api/
│   └── routers/          # API endpoints
├── core/                 # Configs, auth, logging, middleware
├── schemas/              # Pydantic models
├── services/             # Azure OpenAI client
└── main.py               # App factory & router registration
```

##Todo
Implement Front-End
RAG
Dockerize
