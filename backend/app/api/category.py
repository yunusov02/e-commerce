from fastapi import APIRouter


category_router = APIRouter(
    prefix="/category",
    tags=["category"],
)



@category_router.get("/")
async def get_categories():
    return "categories"


