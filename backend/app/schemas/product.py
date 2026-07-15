from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from .category import CategoryRead


class ProductBase(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    price: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    category_id: int

class ProductCreate(ProductBase):
    sku: str
    
    
class ProductUpdate(ProductBase):
    pass    
    
    
class ProductRead(ProductBase):
    id: int
    category: CategoryRead
    
    
