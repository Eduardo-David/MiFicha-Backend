from fastapi import FastAPI
from src.core.config import settings
from src.features.users.presentation.routes import router as auth_router

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])

