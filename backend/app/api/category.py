from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.schemas.category import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate
)

from app.models.category import Category
from app.models.product import Product
from app.core.database import SessionDependency
from app.core.exceptions import NotFoundError, ConflictError

category_router = APIRouter(
    prefix="/category",
    tags=["category"],
)



@category_router.get("/")
async def get_all_categories(session: SessionDependency) -> list[CategoryRead]:

    stmt = select(Category)
    categories = await session.execute(stmt)
    return categories.scalars().all()


@category_router.get("/{id}")
async def get_category(id: int, session: SessionDependency) -> CategoryRead:
    category = await session.get(Category, id)

    if category is None:
        raise NotFoundError(detail="Category not found")

    return category
    

    
@category_router.post("/")
async def create_category(category: CategoryCreate, session: SessionDependency) -> CategoryRead:
    
    new_category = Category(**category.model_dump())
    session.add(new_category)
    
    try:
        await session.commit()
        await session.refresh(new_category)

    except IntegrityError:
        await session.rollback()
        raise ConflictError(detail="Category with this slug already exists")

    return new_category


@category_router.put("/{id}")
async def update_category(id: int, category: CategoryUpdate, session: SessionDependency) -> CategoryRead:
    
    # stmt = select(Category).where(Category.id == id)
    # result = await session.execute(stmt)
    # category_update = result.scalars().one()
    
    category_update = await session.get(Category, id)
    
    if category_update is None:
        raise NotFoundError(detail="Category not found")
     
    for key, value in category.model_dump().items():
        setattr(category_update, key, value)

    await session.commit()
    await session.refresh(category_update)
    return category_update



@category_router.delete("/{id}")
async def delete_category(id: int, session: SessionDependency) -> None:

    category_delete = await session.get(Category, id)

    if category_delete is None:
        raise NotFoundError(detail="Category not found")

    has_children = await session.scalar(
        select(Category.id).where(Category.parent_id == id).limit(1)
    )
    if has_children is not None:
        raise ConflictError(detail="Category has subcategories and cannot be deleted")

    has_products = await session.scalar(
        select(Product.id).where(Product.category_id == id).limit(1)
    )
    if has_products is not None:
        raise ConflictError(detail="Category has products and cannot be deleted")

    await session.delete(category_delete)
    await session.commit()
    
    