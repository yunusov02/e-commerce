from fastapi import FastAPI

from app.api import (
    category_router, 
    product_router
)


def init_routers(app: FastAPI):
    app.include_router(category_router)
    app.include_router(product_router)
    
    
