#  `CategoryCreate`, `CategoryUpdate`, `CategoryRead` 

from pydantic import BaseModel, ConfigDict



class CategoryBase(BaseModel):
    
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    slug: str
    description: str
    parent_id: int | None



class CategoryCreate(CategoryBase):
    pass    
    
    
class CategoryUpdate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int

