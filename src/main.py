from fastapi import FastAPI
from src.core.config import Settings

app = FastAPI()

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "project": Settings.PROJECT_NAME}
