from fastapi import APIRouter
from app.api.v1.endpoints import health, search, agents, products

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(products.router, tags=["Products & Database"])
api_router.include_router(search.router, tags=["Multimodal Search"])
api_router.include_router(agents.router, tags=["Multi-Agent System"])
