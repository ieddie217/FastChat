from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings, allowed_origins
from .core.logging import setup_logging
from .core.middleware import http_access_middleware
from .api.routers import auth, chat, health

# logging first
setup_logging()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION_STR,
    description=settings.API_DESCRIPTION,
)

# middleware order matters; access log outermost
app.middleware("http")(http_access_middleware)

# CORS for your chat UI(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins() or ["*"],  # tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(health.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Chat API",
        "docs": "/docs",
        "version": settings.API_VERSION_STR,
    }
