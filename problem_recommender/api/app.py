from __future__ import annotations

from fastapi import FastAPI

from api.routes.health import router as health_router
from api.routes.recommend import router as recommend_router

app = FastAPI(
    title="Problem Recommender API",
    version="0.1.0",
    description="HTTP surface for the problem recommender MVP.",
)

app.include_router(health_router)
app.include_router(recommend_router)
