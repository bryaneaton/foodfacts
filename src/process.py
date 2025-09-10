"""Data processing module for food product information.

This module handles the processing and storage of food product data,
including normalization, database operations, and batch processing.
"""

import logging
from datetime import datetime, timezone
from typing import Iterator

from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from sqlalchemy.orm.session import Session

from src.models import Category, Country, Ingredient, Nutrient, Product, SessionLocal

logger = logging.getLogger(__name__)


def split_text(text: str, seperator=":", index=1) -> str:
    """Splits the text by seperator"""
    return text.split(seperator)[index]


def normalize_text(text: str) -> str:
    """Normalize text with first word capitalized, rest lowercase"""
    # Replace hyphens with spaces, split into words
    words = text.replace("-", " ").split()
    if not words:
        return text

    # First word capitalized, rest lowercase, join with spaces
    return (
        words[0].capitalize() + " " + " ".join(word.lower() for word in words[1:])
        if len(words) > 1
        else words[0].capitalize()
    )


def capitalize_text(text: str):
    return text.title()


def create_nutrition(product: dict, session: Session) -> None:
    """Create nutrition for a product"""
    nutrients = product.get("nutriments", {})
    barcode = product.get("code", "")
    if nutrients and barcode:
        product_nutrients = Nutrient(
            barcode=barcode,
            energy_kcal_100g=nutrients.get("energy-kcal_100g", 0),
            fat_100g=nutrients.get("fat_100g", 0),
            saturated_fat_100g=nutrients.get("saturated-fat_100g", 0),
            carbohydrates_100g=nutrients.get("carbohydrates_100g", 0),
            sugars_100g=nutrients.get("sugars_100g", 0),
            fiber_100g=nutrients.get("fiber_100g", 0),
            proteins_100g=nutrients.get("proteins_100g", 0),
            salt_100g=nutrients.get("salt_100g", 0),
            sodium_100g=nutrients.get("sodium_100g", 0),
            created_at=datetime.fromtimestamp(
                product.get("created_t", 0), tz=timezone.utc
            ),
            updated_at=datetime.fromtimestamp(
                product.get("last_modified_t", 0), tz=timezone.utc
            ),
        )
        session.add(product_nutrients)


def create_ingredients(product: dict, session: Session) -> None:
    """Create ingredients for a product"""
    ingredients = product.get("ingredients_tags", [])
    barcode = product.get("code", "")
    if ingredients and barcode:
        for ingredient in ingredients:
            try:
                product_ingredients = Ingredient(
                    barcode=barcode,
                    ingredient_text=split_text(normalize_text(ingredient)),
                    created_at=datetime.fromtimestamp(
                        product.get("created_t", 0), tz=timezone.utc
                    ),
                    updated_at=datetime.fromtimestamp(
                        product.get("last_modified_t", 0), tz=timezone.utc
                    ),
                )
                session.add(product_ingredients)
            except IndexError as e:
                logger.error("Error saving ingredient %s: %s", ingredient, e)
                continue


def create_categories(product: dict, session: Session) -> None:
    """Create categories for a product"""
    categories = product.get("categories", "")
    barcode = product.get("code", "")
    if categories and barcode:
        for category in categories.split(","):
            product_categories = Category(
                barcode=barcode,
                category=category.strip(),
                created_at=datetime.fromtimestamp(
                    product.get("created_t", 0), tz=timezone.utc
                ),
                updated_at=datetime.fromtimestamp(
                    product.get("last_modified_t", 0), tz=timezone.utc
                ),
            )
            session.add(product_categories)


def create_countries(product: dict, session: Session) -> None:
    """Create countries for a product"""
    countries = product.get("countries_tags", [])
    barcode = product.get("code", "")
    if countries and barcode:
        for country in countries:
            try:
                product_countries = Country(
                    barcode=barcode,
                    country=capitalize_text(normalize_text(country.split(":")[1])),
                    created_at=datetime.fromtimestamp(
                        product.get("created_t", 0), tz=timezone.utc
                    ),
                    updated_at=datetime.fromtimestamp(
                        product.get("last_modified_t", 0), tz=timezone.utc
                    ),
                )
                session.add(product_countries)
            except IndexError as e:
                logger.error("Error saving country %s: %s", country, e)
                continue


def get_packaging(product: dict) -> str:
    """Get the packaging from a product dictionary with priority order."""
    if not product or not isinstance(product, dict):
        return ""

    # Priority order: English first, then any other language
    packaging_keys = [
        "packaging_text_en",  # English (highest priority)
        "packaging_text",  # Generic packaging text
    ]

    # Check priority keys first
    for key in packaging_keys:
        value = product.get(key, "")
        if value and isinstance(value, str) and value.strip():
            return normalize_text(value.strip())

    # Fallback: find any packaging_text_* key with a value
    # Only check keys that start with 'packaging_text' for better performance
    packaging_text_keys = [k for k in product.keys() if k.startswith("packaging_text")]
    for key in packaging_text_keys:
        value = product.get(key, "")
        if value and isinstance(value, str) and value.strip():
            return normalize_text(value.strip())

    # If all else fails, pull from the packaging_tags array
    packaging_tags = product.get("packaging_tags", [])
    if packaging_tags and isinstance(packaging_tags, list):
        try:
            # Filter out invalid entries and handle potential errors
            valid_tags = []
            for tag in packaging_tags:
                if isinstance(tag, str) and ":" in tag:
                    parts = tag.split(":", 1)  # Split only on first colon
                    if len(parts) > 1 and parts[1].strip():
                        valid_tags.append(normalize_text(parts[1].strip()))

            if valid_tags:
                return ", ".join(valid_tags)
        except (AttributeError, TypeError) as e:
            logger.debug("Error processing packaging_tags: %s", e)

    return ""


def create_product(product: dict, session: Session) -> bool:
    """Create a product and return True if created, False if skipped"""
    try:
        barcode = product.get("code", "")
        if not barcode:
            logger.warning("Skipping product with empty barcode")
            return False

        # Check if product already exists
        existing_product = (
            session.query(Product).filter(Product.barcode == barcode).first()
        )
        if existing_product:
            logger.debug("Product with barcode %s already exists, skipping", barcode)
            return False

        # Create new product using utility functions
        new_product = Product(
            barcode=barcode,
            product_name=product.get("product_name", product.get("name", "")),
            brand=product.get("brand", ""),
            packaging=get_packaging(product),
            created_at=datetime.fromtimestamp(
                product.get("created_t", 0), tz=timezone.utc
            ),
            updated_at=datetime.fromtimestamp(
                product.get("last_modified_t", 0), tz=timezone.utc
            ),
        )
        session.add(new_product)

        # Create related data
        create_nutrition(product, session)
        create_ingredients(product, session)
        create_categories(product, session)
        create_countries(product, session)

        return True

    except Exception as e:
        logger.error("Error creating product %s: %s", product.get("code", "unknown"), e)
        raise  # Re-raise to let save_data handle the rollback


def save_data(products: Iterator[dict], total_count: int = None):
    """Process the products iterator"""
    session = SessionLocal()
    products_saved = 0
    products_processed = 0

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Saving products..."),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("products"),
            TimeRemainingColumn(),
            console=None,
        ) as progress:
            task = progress.add_task("Saving", total=total_count)

            for product in products:
                try:
                    if create_product(product, session):
                        products_saved += 1
                    products_processed += 1
                    progress.update(task, advance=1)
                except Exception as e:
                    logger.error(
                        "Failed to process product %s: %s",
                        product.get("code", "unknown"),
                        e,
                    )
                    products_processed += 1
                    progress.update(task, advance=1)
                    # Continue processing other products

        # Single commit for all products at the end
        session.commit()
        logger.info("Transaction committed successfully")

    except Exception as e:
        logger.error("Error during batch processing: %s", e)
        session.rollback()
        logger.info("Transaction rolled back")
        raise
    finally:
        logger.info("Products processed: %d", products_processed)
        logger.info("Products saved to database: %d", products_saved)
        logger.info(
            "Products skipped (duplicates): %d", products_processed - products_saved
        )
        session.close()
