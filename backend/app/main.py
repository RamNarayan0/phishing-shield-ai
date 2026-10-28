import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.mongodb import init_db, close_db
from .core.security import ContentLengthLimitMiddleware, SecurityHeadersMiddleware
from .api.routes import health, verify

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to database & ensure unique indexes
    init_db()
    yield
    # Shutdown: cleanly close database connection pool
    close_db()

app = FastAPI(
    title="Phishing Shield AI",
    description="Real-Time Threat Detection & Explainable Risk API",
    version="1.0.0",
    lifespan=lifespan
)

# Security Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ContentLengthLimitMiddleware)

# Secure CORS Configuration
configured_origins = os.getenv("CORS_ORIGINS", "")
if configured_origins.strip():
    allowed_origins = [orig.strip() for orig in configured_origins.split(",") if orig.strip()]
else:
    allowed_origins = [
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://ramnarayan0.github.io",
        "https://phishing-shield-ai.vercel.app",
        "https://phishing-shield-ai-frontend.onrender.com",
        "https://phishing-shield-ai.onrender.com"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ["*"] else ["*"],
    allow_origin_regex=r"^chrome-extension://.*" if allowed_origins != ["*"] else None,
    allow_credentials=True if allowed_origins != ["*"] else False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(health.router, tags=["Health"])
app.include_router(verify.router, prefix="/api", tags=["Verification"])
