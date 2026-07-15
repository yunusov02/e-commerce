from fastapi import APIRouter

from sqlalchemy import select

from app.schemas.product import (
    ProductCreate,
    ProductRead,
    ProductUpdate
)

from app.models.product import Product

from app.core.database import SessionDependency

product_router = APIRouter(
    prefix="/product",
    tags=["product"],    
)




@product_router.get("/")
async def get_all_products(session: SessionDependency):
    
    stmt = select(Product)
    products = await session.execute(stmt)
    return products.scalars().all()



@product_router.get("/{id}")
async def get_product(id: int, session: SessionDependency):
    product = await session.get(Product, id)
    return product

@product_router.post("/")
async def create_product(product: ProductCreate, session: SessionDependency):
    
    new_product = Product(**product.model_dump())
    await session.add(new_product)
    await session.commit()
    
    await session.refresh(new_product)
    
    return new_product



@product_router.put("/{id}")
async def update_product(id: int, product: ProductUpdate, session: SessionDependency):
    
    product_update = await session.get(Product, id)
    
    for key, value in product.model_dump():
        setattr(product_update, key, value)
        
    await session.commit()
    await session.refresh(product_update)
    
    return product_update



@product_router.delete("/{id}")
async def delete_product(id: int, session: SessionDependency):
    
    product_delete = await session.get(Product, id)
    
    await session.delete(product_delete)
    await session.commit()
    
    
    return "ok"


