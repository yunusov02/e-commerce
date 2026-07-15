from fastapi import APIRouter

from sqlalchemy import select

from app.schemas.category import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate
)

from app.models.category import Category

from app.core.database import SessionDependency

category_router = APIRouter(
    prefix="/category",
    tags=["category"],
)



@category_router.get("/")
async def get_all_categories(session: SessionDependency):
    
    stmt = select(Category)
    categories = await session.execute(stmt)
    return categories.scalars().all()
    
    
@category_router.get("/{id}")
async def get_category(id: int, session: SessionDependency):
    category = await session.get(Category, id)
    return category
    

    
@category_router.post("/")
async def create_category(category: CategoryCreate, session: SessionDependency):
    
    new_category = Category(**category.model_dump())
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)
    return new_category


@category_router.put("/{id}")
async def update_category(id: int, category: CategoryUpdate, session: SessionDependency):
    stmt = select(Category).where(Category.id == id)
    result = await session.execute(stmt)
    category_update = result.scalars().one()
    
    for key, value in category.model_dump():
        setattr(category_update, key, value)
    
    await session.commit()
    await session.refresh(category)
    return category



@category_router.delete("/{id}")
async def delete_category(id: int, session: SessionDependency):
    
    stmt = select(Category).where(Category.id == id)
    result = await session.execute(stmt)
    
    category_delete = result.scalars().one()
    
    await session.delete(category_delete)
    await session.commit()
    
    return "ok"
