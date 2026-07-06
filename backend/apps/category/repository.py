from core.depends import SessionDependency

from .models import Category
from .schemas import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
)


# Repository talks with the database and performs CRUD opeations


class CategoryRepository:
    
    @classmethod
    def get_all(
        cls,
        session: SessionDependency,
    ) -> list[Category]:

        stmt = session.query(Category).all()

        return stmt

    
    @classmethod
    def get_by_id(
        cls,
        category_id: int,
        session: SessionDependency,
    ) -> Category | None:
        
        stmt = (
            session.query(Category).
            filter(Category.id == category_id).first()
        )

        return stmt


    @classmethod
    def get_by_slug(
        cls,
        category_slug: str,
        session: SessionDependency,
    ) -> Category | None:
        
        stmt = (
            session.query(Category).
            filter(Category.slug == category_slug).first()
        )

        return stmt
    

    @classmethod
    def create(
        cls,
        category: CategoryCreateSchema,
        session: SessionDependency,
    ) -> Category:

        db_category = Category(**category.model_dump())
        session.add(db_category)
        session.commit()
        session.refresh(db_category)

        return db_category
    

    @classmethod
    def update(
        cls,
        category_id: int,
        category: CategoryUpdateSchema,
        session: SessionDependency,
    ) -> Category | None:

        db_category = session.query(Category).filter(Category.id == category_id).first()

        if not db_category:
            return None

        for key, value in category.model_dump(exclude_unset=True).items():
            setattr(db_category, key, value)

        session.commit()
        session.refresh(db_category)

        return db_category
    

    @classmethod
    def delete(
        cls,
        category_id: int,
        session: SessionDependency,
    ) -> bool:

        db_category = session.query(Category).filter(Category.id == category_id).first()

        if not db_category:
            return False

        session.delete(db_category)
        session.commit()

        return True
    

