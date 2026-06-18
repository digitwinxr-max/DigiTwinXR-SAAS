"""GCDTP Backend API - Asset, Sensor, Measurement, Threshold, Event & Health Engine."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database.config import engine, Base
from .routes.asset_routes import router as asset_router
from .routes.sensor_routes import router as sensor_router
from .routes.measurement_routes import router as measurement_router
from .routes.threshold_routes import router as threshold_router
from .routes.event_routes import router as event_router
from .routes.health_routes import router as health_router
from .routes.asset_relationship_routes import router as relationship_router
from .routes.propagation_routes import router as propagation_router
from .routes.network_health_routes import router as network_health_router
from .routes.scenario_routes import router as scenario_router
from .routes.recovery_routes import router as recovery_router
from .routes.resilience_routes import router as resilience_router
from .routes.semantic_routes import router as semantic_router
from .routes.timeline_routes import router as timeline_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GCDTP Health Engine",
    description="Asset, Sensor, Measurement, Threshold, Event & Health Engine for GCDTP",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(asset_router)
app.include_router(sensor_router)
app.include_router(measurement_router)
app.include_router(threshold_router)
app.include_router(event_router)
app.include_router(health_router)
app.include_router(relationship_router)
app.include_router(propagation_router)
app.include_router(network_health_router)
app.include_router(scenario_router)
app.include_router(recovery_router)
app.include_router(resilience_router)
app.include_router(semantic_router)
app.include_router(timeline_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
