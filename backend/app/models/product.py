from sqlalchemy import Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base
from .category import Category


class Product(Base):

    __tablename__ = "product"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    sku: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"))
    category = relationship("Category", back_populates="products")
    
    
