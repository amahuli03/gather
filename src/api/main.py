"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import chat, health

# Create FastAPI app
app = FastAPI(
    title="Gather API",
    description="API service for Gather coordination assistant",
    version="1.0.0"
)

# Configure CORS
# TODO: Update allowed_origins with your frontend URL(s) when deploying
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(health.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Gather API",
        "docs": "/docs",
        "health": "/api/health"
    }

