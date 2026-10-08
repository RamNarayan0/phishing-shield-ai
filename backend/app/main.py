from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import health, verify

app = FastAPI(
    title="Phishing Shield AI",
    description="Real-Time Threat Detection API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For prototype, allow all
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health.router, tags=["Health"])
app.include_router(verify.router, prefix="/api", tags=["Verification"])
