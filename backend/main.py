"""
Smart Differentiated Case Flow Management (DCM) System with BNS Assist
FastAPI Backend Application
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.exceptions import setup_exception_handlers
from app.routers import auth, cases, schedule, reports, nlp


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    create_db_and_tables()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="DCM System with BNS Assist",
    description="Smart Differentiated Case Flow Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Setup global exception handlers
setup_exception_handlers(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(cases.router, prefix="/cases", tags=["Cases"])
app.include_router(schedule.router, prefix="/schedule", tags=["Scheduling"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
app.include_router(nlp.router, prefix="/nlp", tags=["NLP"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "DCM System with BNS Assist API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "dcm-system",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
