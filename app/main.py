from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Research Agent",
    description="MVP de um AI Research Agent com LangGraph e tool calling",
    version="0.1.0",
)

app.include_router(router)
