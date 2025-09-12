"""Database models for food product data.

This module defines SQLAlchemy models for storing food product information
including products, nutrients, ingredients, categories, and countries.
"""

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
    event,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class AuditMixin:
    """Base class with audit fields for all tables.

    Provides created_at and updated_at timestamp fields that are automatically
    managed for all models that inherit from this mixin.
    """

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
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Enable foreign key enforcement for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Product(Base, AuditMixin):
    """Product model for storing basic product information."""

    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    barcode = Column(String)
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
    """Nutrient model for storing nutritional information per 100g."""

    __tablename__ = "nutrients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.id"))
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
    """Ingredient model for storing product ingredients."""

    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.id"))
    ingredient_text = Column(Text)

    # Relationship
    product = relationship("Product", back_populates="ingredients")


class Category(Base, AuditMixin):
    """Category model for storing product categories."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.id"))
    category = Column(String)

    # Relationship
    product = relationship("Product", back_populates="categories")


class Country(Base, AuditMixin):
    """Country model for storing product origin countries."""

    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("products.id"))
    country = Column(String)

    # Relationship
    product = relationship("Product", back_populates="countries")


def create_database():
    """Create all tables in the database."""
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        db_path = os.path.abspath("food_products.db")
        logger.info("Database created successfully at: %s", db_path)
        print(f"Database created successfully at: {db_path}")
    except Exception as e:
        logger.error("Error creating database: %s", e)
        raise


def get_db():
    """Get database session."""
    logger.debug("Creating database session")
    try:
        db = SessionLocal()
        return db
    except Exception as e:
        logger.error("Error creating database session: %s", e)
        raise


def get_product_id_by_barcode(barcode: str, db: SessionLocal) -> int | None:
    """Lookup product ID by barcode."""
    try:
        product = db.query(Product).filter(Product.barcode == barcode).first()
        return product.id if product else None
    except Exception as e:
        logger.error("Error looking up product by barcode %s: %s", barcode, e)
        return None
