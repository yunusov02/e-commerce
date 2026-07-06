
from core.depends import SessionDependency

from .models import Product
from .schemas import (
    ProductCreateSchema,
    ProductUpdateSchema,
)



class ProductRepository:

    @classmethod
    def get_all(
        cls,
        session: SessionDependency,
    ) -> list[Product]:

        stmt = session.query(Product).all()

        return stmt

    
    @classmethod
    def get_by_id(
        cls,
        product_id: int,
        session: SessionDependency,
    ) -> Product | None:
        
        stmt = (
            session.query(Product).
            filter(Product.id == product_id).first()
        )

        return stmt


    @classmethod
    def get_by_slug(
        cls,
        product_slug: str,
        session: SessionDependency,
    ) -> Product | None:
        
        stmt = (
            session.query(Product).
            filter(Product.slug == product_slug).first()
        )

        return stmt
    

    @classmethod
    def create(
        cls,
        product: ProductCreateSchema,
        session: SessionDependency,
    ) -> Product:
        
        new_product = Product(**product.model_dump())
        session.add(new_product)
        session.commit()
        session.refresh(new_product)

        return new_product
    

    @classmethod
    def update(
        cls,
        product_id: int,
        product: ProductUpdateSchema,
        session: SessionDependency,
    ) -> Product | None:

        db_product = (
            session.query(Product).
            filter(Product.id == product_id).first()
        )

        if not db_product:
            return None

        for key, value in product.model_dump(exclude_unset=True).items():
            setattr(db_product, key, value)

        session.commit()
        session.refresh(db_product)

        return db_product  
    
    @classmethod
    def delete(
        cls,
        product_id: int,
        session: SessionDependency,
    ) -> bool:

        db_product = (
            session.query(Product).
            filter(Product.id == product_id).first()
        )

        if not db_product:
            return False

        session.delete(db_product)
        session.commit()

        return True