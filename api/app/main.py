from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_tables
from .routers import sensors, readings
from .config import settings

app = FastAPI(
    title="Breatheasy API",
    description="Air Quality Monitoring System API",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sensors.router, prefix="/api/sensors", tags=["sensors"])
app.include_router(readings.router, prefix="/api/readings", tags=["readings"])


@app.on_event("startup")
async def startup_event():
    await create_tables()


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Breatheasy API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
