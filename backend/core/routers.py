from fastapi import FastAPI

from apps.category.api import category_router
from apps.products.api import product_router


def include_routers(app: FastAPI) -> None:
    app.include_router(category_router, prefix="/categories", tags=["Categories"])
    app.include_router(product_router, prefix="/products", tags=["Products"])

