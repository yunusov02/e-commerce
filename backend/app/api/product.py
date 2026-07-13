from fastapi import APIRouter


product_router = APIRouter(
    prefix="/product",
    tags=["product"],    
)




@product_router.get("/")
async def get_products():
    return "products"

