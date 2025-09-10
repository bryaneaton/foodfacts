import logging
import os
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class AuditMixin:
    """Base class with audit fields for all tables."""

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# Database configuration
DATABASE_URL = "sqlite:///food_products.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Product(Base, AuditMixin):
    __tablename__ = "products"

    barcode = Column(BigInteger, primary_key=True)
    product_name = Column(String)
    brand = Column(String)
    packaging = Column(String)

    # Relationships
    nutrients = relationship(
        "Nutrient", back_populates="product", cascade="all, delete-orphan"
    )
    ingredients = relationship(
        "Ingredient", back_populates="product", cascade="all, delete-orphan"
    )
    categories = relationship(
        "Category", back_populates="product", cascade="all, delete-orphan"
    )
    countries = relationship(
        "Country", back_populates="product", cascade="all, delete-orphan"
    )


class Nutrient(Base, AuditMixin):
    __tablename__ = "nutrients"

    barcode = Column(BigInteger, ForeignKey("products.barcode"), primary_key=True)
    energy_kcal_100g = Column(Float)
    fat_100g = Column(Float)
    saturated_fat_100g = Column(Float)
    carbohydrates_100g = Column(Float)
    sugars_100g = Column(Float)
    fiber_100g = Column(Float)
    proteins_100g = Column(Float)
    salt_100g = Column(Float)
    sodium_100g = Column(Float)

    # Relationship
    product = relationship("Product", back_populates="nutrients")


class Ingredient(Base, AuditMixin):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True)
    barcode = Column(BigInteger, ForeignKey("products.barcode"))
    ingredient_text = Column(Text)

    # Relationship
    product = relationship("Product", back_populates="ingredients")


class Category(Base, AuditMixin):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    barcode = Column(BigInteger, ForeignKey("products.barcode"))
    category = Column(String)

    # Relationship
    product = relationship("Product", back_populates="categories")


class Country(Base, AuditMixin):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    barcode = Column(BigInteger, ForeignKey("products.barcode"))
    country = Column(String)

    # Relationship
    product = relationship("Product", back_populates="countries")


def create_database():
    """Create all tables in the database."""
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        db_path = os.path.abspath("food_products.db")
        logger.info(f"Database created successfully at: {db_path}")
        print(f"Database created successfully at: {db_path}")
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise


def get_db():
    """Get database session."""
    logger.debug("Creating database session")
    try:
        db = SessionLocal()
        return db
    except Exception as e:
        logger.error(f"Error creating database session: {e}")
        raise
