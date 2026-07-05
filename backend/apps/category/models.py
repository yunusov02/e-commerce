from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.products.models import Product # This never executed, only for type checking

class Category(Base):
    __tablename__ = "categories"


    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)

    parent: Mapped["Category | None"] = relationship(
        remote_side=[id],
        back_populates="children"
    )

    children: Mapped[list["Category"]] = relationship(
        back_populates="parent"
    )


    products: Mapped[list["Product"]] = relationship( # !nqa
        back_populates="category"
    )

    def __repr__(self) -> str:
        return f"Category: {self.name}"
    

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "parent_id": self.parent_id,
        }
    
