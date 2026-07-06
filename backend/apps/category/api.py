from fastapi import APIRouter

from core.depends import SessionDependency

from .models import Category
from .schemas import (
    CategoryCreateSchema,
    CategoryDetailSchema,
    CategoryListSchema,
    CategoryUpdateSchema,
)

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.logging import get_logger

category_router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    responses={404: {"description": "Not found"}},
)



logger = get_logger("category")

@category_router.get("/", summary="Get all categories")
async def get_categories(session: SessionDependency) -> list[CategoryListSchema]:

    stmt = select(Category)

    result = await session.execute(stmt)

    categories = result.scalars().all()

    logger.info("Fetched all categories", count=len(categories))
    return categories

@category_router.get("/{category_id}", summary="Get category by ID")
async def get_category_by_id(
    category_id: int, session: SessionDependency
) -> CategoryDetailSchema:
    
    stmt = (
        select(Category)
        .options(selectinload(Category.children).selectinload(Category.children))
        .where(Category.id == category_id)
    )

    result = await session.execute(stmt)
    category = result.scalar_one_or_none()

    logger.info(f"Fetched category with ID: {category_id}")
    return category


@category_router.post("/", summary="Create a new category")
async def create_category(
    category: CategoryCreateSchema, session: SessionDependency
) -> CategoryDetailSchema:

    new_category = Category(**category.model_dump())

    session.add(new_category)

    await session.commit()
    await session.refresh(new_category)

    logger.info(f"Created new category with ID: {new_category.id}", name=new_category.name, slug=new_category.slug)
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

    await session.commit()
    await session.refresh(stmt)

    logger.info(f"Updated category with ID: {category_id}", name=stmt.name, slug=stmt.slug)
    return stmt



@category_router.delete("/{category_id}", summary="Delete a category")
async def delete_category(category_id: int, session: SessionDependency) -> dict:

    stmt = session.query(Category).filter(Category.id == category_id).first()
    if not stmt:
        return {"message": "Category not found"}

    session.delete(stmt)
    await session.commit()

    logger.info(f"Category deleted: {category_id}")
    return {"message": "Category deleted successfully"}

