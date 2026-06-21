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
from .routes.logbook_routes import router as logbook_router
from .routes.knowledge_routes import router as knowledge_router
from .routes.copilot_routes import router as copilot_router
from .routes.rag_routes import router as rag_router
from .routes.agent_routes import router as agent_router
from .routes.predictive_routes import router as predictive_router
from .routes.root_cause_routes import router as root_cause_router
from .routes.cognitive_routes import router as cognitive_router

# AI Intelligence Layer routers
from .ai.ollama import router as ollama_router
from .ai.langgraph import router as langgraph_router
from .ai.memory import router as context_router
from .ai.reasoning import router as reasoning_router
from .ai.copilot import router as copilot_ai_router

# Video Intelligence Layer routers
from .video.frigate import router as frigate_router
from .video.opencv import router as opencv_router
from .video.yolo import router as yolo_router
from .video.deepstream import router as deepstream_router

# Autonomous Cognitive Twin routers
from .agents import router as agents_router
from .reasoning import router as reasoning_fusion_router
from .learning import router as learning_router
from .simulation import router as simulation_router
from .prescriptive import router as prescriptive_router
from .autonomy import router as autonomy_router

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
app.include_router(logbook_router)
app.include_router(knowledge_router)
app.include_router(copilot_router)
app.include_router(rag_router)
app.include_router(agent_router)
app.include_router(predictive_router)
app.include_router(root_cause_router)
app.include_router(cognitive_router)

# AI Intelligence Layer routers
app.include_router(ollama_router)
app.include_router(langgraph_router)
app.include_router(context_router)
app.include_router(reasoning_router)
app.include_router(copilot_ai_router)

# Video Intelligence Layer routers
app.include_router(frigate_router)
app.include_router(opencv_router)
app.include_router(yolo_router)
app.include_router(deepstream_router)

# Autonomous Cognitive Twin routers
app.include_router(agents_router)
app.include_router(reasoning_fusion_router)
app.include_router(learning_router)
app.include_router(simulation_router)
app.include_router(prescriptive_router)
app.include_router(autonomy_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
