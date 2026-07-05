from pydantic import BaseModel, Field

from apps.category.schemas import CategoryDetailSchema


class ProductSchema(BaseModel):
    name: str = Field(..., description="Name of the product")
    slug: str = Field(..., description="URL-friendly version of the product name")
    description: str | None = Field(None, description="Description of the product")
    price: float = Field(..., description="Price of the product")
    category_id: int = Field(..., description="Reference to the category the product belongs to")

    class Config:
        orm_mode = True



class ProductCreateSchema(ProductSchema):
    sku: str = Field(..., description="Stock Keeping Unit (SKU) for the product")


class ProductUpdateSchema(ProductCreateSchema):
    pass



class ProductDetailSchema(ProductSchema):
    id: int = Field(..., description="Unique identifier for the product")
    sku: str = Field(..., description="Stock Keeping Unit (SKU) for the product")
    category: CategoryDetailSchema


class ProductListSchema(ProductSchema):
    id: int = Field(..., description="Unique identifier for the product")




