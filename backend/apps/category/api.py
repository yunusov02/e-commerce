from fastapi import APIRouter

from core.depends import SessionDependency

from .models import Category
from .schemas import (
    CategoryCreateSchema,
    CategoryDetailSchema,
    CategoryListSchema,
    CategoryUpdateSchema,
)


category_router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    responses={404: {"description": "Not found"}},
)


@category_router.get("/", summary="Get all categories")
async def get_categories(session: SessionDependency) -> list[CategoryListSchema]:

    stmt = session.query(Category).all()
    return stmt


@category_router.get("/{category_id}", summary="Get category by ID")
async def get_category_by_id(
    category_id: int, session: SessionDependency
) -> CategoryDetailSchema:

    stmt = session.query(Category).filter(Category.id == category_id).first()
    return stmt


@category_router.post("/", summary="Create a new category")
async def create_category(
    category: CategoryCreateSchema, session: SessionDependency
) -> CategoryDetailSchema:

    new_category = Category(**category.model_dump())
    session.add(new_category)
    session.commit()
    session.refresh(new_category)

    return new_category




@category_router.put("/{category_id}", summary="Update a category")
async def update_category(
    category_id: int, category: CategoryUpdateSchema, session: SessionDependency
) -> CategoryDetailSchema:

    stmt = session.query(Category).filter(Category.id == category_id).first()
    if not stmt:
        return None

    for key, value in category.model_dump().items():
        setattr(stmt, key, value)

    session.commit()
    session.refresh(stmt)
    return stmt



@category_router.delete("/{category_id}", summary="Delete a category")
async def delete_category(category_id: int, session: SessionDependency) -> dict:

    stmt = session.query(Category).filter(Category.id == category_id).first()
    if not stmt:
        return {"message": "Category not found"}

    session.delete(stmt)
    session.commit()
    return {"message": "Category deleted successfully"}

