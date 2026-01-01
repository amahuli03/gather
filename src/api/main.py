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
# Allow Apps Script (script.google.com) and localhost for development
allowed_origins = [
    "https://script.google.com",
    "https://script.googleusercontent.com",
    "http://localhost:8000",  # Local development
    "http://localhost:8501",  # Streamlit local
]

# Allow all origins in development, specific origins in production
import os
if os.getenv("ENVIRONMENT") != "production":
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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

