from pydantic import BaseModel, Field

class CategoryListSchema(BaseModel):
    id: int = Field(..., description="Unique identifier for the category")
    name: str = Field(..., description="Name of the category")
    slug: str = Field(..., description="URL-friendly version of the category name")
    parent_id: int | None = Field(None, description="Reference to the parent category (can be null for top-level categories)")

    class Config:
        form_attributes = True


class CategoryCreateSchema(BaseModel):
    name: str = Field(..., description="Name of the category")
    slug: str = Field(..., description="URL-friendly version of the category name")
    parent_id: int | None = Field(None, description="Reference to the parent category (can be null for top-level categories)")

    class Config:
        form_attributes = True


class CategoryUpdateSchema(BaseModel):
    name: str | None = Field(None, description="Name of the category")
    slug: str | None = Field(None, description="URL-friendly version of the category name")
    parent_id: int | None = Field(None, description="Reference to the parent category (can be null for top-level categories)")

    class Config:
        form_attributes = True



class CategoryDetailSchema(BaseModel):
    id: int = Field(..., description="Unique identifier for the category")
    name: str = Field(..., description="Name of the category")
    slug: str = Field(..., description="URL-friendly version of the category name")
    parent_id: int | None = Field(None, description="Reference to the parent category (can be null for top-level categories)")
    children: list["CategoryDetailSchema"] = Field(default_factory=list, description="List of child categories")

    class Config:
        form_attributes = True