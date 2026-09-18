from fastapi import FastAPI
from src.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
