from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

from apps.category.models import Category


class Product(Base):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[float] = mapped_column(nullable=False)
    sku: Mapped[str] = mapped_column(unique=True, index=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    category: Mapped["Category"] = relationship(
        back_populates="products"
    )

    def __repr__(self) -> str:
        return f"Product: {self.name}"
    

