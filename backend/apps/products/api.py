from fastapi import APIRouter

from core.depends import SessionDependency


from .models import Product
from .schemas import (
    ProductCreateSchema,
    ProductDetailSchema,
    ProductListSchema,
    ProductUpdateSchema,
)

product_router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"description": "Not found"}},
)



@product_router.get("/", summary="Get all products")
async def get_products(session: SessionDependency) -> list[ProductListSchema]:

    stmt = session.query(Product).all()
    return stmt


@product_router.get("/{product_id}", summary="Get product by ID")
async def get_product_by_id(
    product_id: int, session: SessionDependency
) -> ProductDetailSchema:

    stmt = session.query(Product).filter(Product.id == product_id).first()
    return stmt


@product_router.post("/", summary="Create a new product")
async def create_product(
    product: ProductCreateSchema, session: SessionDependency
) -> ProductDetailSchema:

    new_product = Product(**product.model_dump())
    session.add(new_product)
    session.commit()
    session.refresh(new_product)

    return new_product



@product_router.put("/{product_id}", summary="Update a product")
async def update_product(
    product_id: int, product: ProductUpdateSchema, session: SessionDependency
) -> ProductDetailSchema:

    stmt = session.query(Product).filter(Product.id == product_id).first()
    if not stmt:
        return None

    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(stmt, key, value)

    session.commit()
    session.refresh(stmt)

    return stmt


@product_router.delete("/{product_id}", summary="Delete a product")
async def delete_product(
    product_id: int, session: SessionDependency
) -> dict[str, str]:

    stmt = session.query(Product).filter(Product.id == product_id).first()
    if not stmt:
        return {"message": "Product not found"}

    session.delete(stmt)
    session.commit()

    return {"message": "Product deleted successfully"}


