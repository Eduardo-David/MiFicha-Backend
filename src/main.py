from fastapi import FastAPI
from src.core.config import Settings

settings = Settings()
app = FastAPI()

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
