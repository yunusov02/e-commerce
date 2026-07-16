from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.schemas.product import (
    ProductCreate,
    ProductRead,
    ProductUpdate
)

from app.models.product import Product
from app.models.category import Category

from app.core.database import SessionDependency
from app.core.exceptions import NotFoundError, ConflictError


product_router = APIRouter(
    prefix="/product",
    tags=["product"],
)


@product_router.get("/")
async def get_all_products(session: SessionDependency) -> list[ProductRead]:

    stmt = select(Product)
    products = await session.execute(stmt)
    return products.scalars().all()


@product_router.get("/{id}")
async def get_product(id: int, session: SessionDependency) -> ProductRead:
    product = await session.get(Product, id)

    if product is None:
        raise NotFoundError(detail="Product not found")

    return product


@product_router.post("/", status_code=201)
async def create_product(product: ProductCreate, session: SessionDependency) -> ProductRead:

    category = await session.get(Category, product.category_id)
    if category is None:
        raise NotFoundError(detail="Category not found")

    new_product = Product(**product.model_dump())
    session.add(new_product)

    try:
        await session.commit()
        await session.refresh(new_product)
    except IntegrityError:
        await session.rollback()
        raise ConflictError(detail="Product with this sku already exists")

    return new_product


@product_router.put("/{id}", status_code=200)
async def update_product(id: int, product: ProductUpdate, session: SessionDependency) -> ProductRead:

    product_update = await session.get(Product, id)

    if product_update is None:
        raise NotFoundError(detail="Product not found")

    category = await session.get(Category, product.category_id)
    if category is None:
        raise NotFoundError(detail="Category not found")

    for key, value in product.model_dump().items():
        setattr(product_update, key, value)

    try:
        await session.commit()
        await session.refresh(product_update)
    except IntegrityError:
        await session.rollback()
        raise ConflictError(detail="Product with this sku already exists")

    return product_update


@product_router.delete("/{id}", status_code=204)
async def delete_product(id: int, session: SessionDependency) -> None:

    product_delete = await session.get(Product, id)

    if product_delete is None:
        raise NotFoundError(detail="Product not found")

    await session.delete(product_delete)
    await session.commit()
