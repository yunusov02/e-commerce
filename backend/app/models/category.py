
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column


from .base import Base

class Category(Base):
    
    __tablename__ = "category"
    
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("category.id"), nullable=True)
    
    parent = relationship("Category", remote_side=[id])
    children = relationship("Category", back_populates="parent")
    
