from fastapi import APIRouter, FastAPI

from app.api import (
    category_router,
    product_router
)


def init_routers(app: FastAPI):
    
    api_v1_router = APIRouter(prefix="/api/v1")
    api_v1_router.include_router(category_router)
    api_v1_router.include_router(product_router)

    app.include_router(api_v1_router)
    
    
