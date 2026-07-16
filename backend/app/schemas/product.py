from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    price: Decimal = Field(max_digits=10, decimal_places=2, gt=0)


class ProductCreate(ProductBase):
    sku: str
    category_id: int


class ProductUpdate(ProductBase):
    category_id: int


class ProductRead(ProductBase):
    id: int
    category_id: int

