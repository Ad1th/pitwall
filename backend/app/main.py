"""
PITWALL FastAPI Backend Application Entry Point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.router import api_v1_router
from backend.app.db.connection import DatabaseManager

app = FastAPI(
    title="PITWALL API",
    description="The Counterfactual Race Strategy Engine REST API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Ensure DuckDB schema is initialized on startup."""
    DatabaseManager().connect("data/pitwall.duckdb")


@app.get("/api/v1/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "PITWALL API", "version": "0.1.0"}


app.include_router(api_v1_router, prefix="/api/v1")
