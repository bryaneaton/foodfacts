"""Unit tests for the process module using mock data."""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from src.process import (
    capitalize_text,
    create_categories,
    create_countries,
    create_ingredients,
    create_nutrition,
    create_product,
    get_packaging,
    normalize_text,
    save_data,
    split_text,
)


@pytest.fixture
def mock_response():
    """Load mock data from JSON file."""
    with open("./mock_response.json", "r") as f:
        return json.load(f)


@pytest.fixture
def mock_product(mock_response):
    """Extract product data from mock response."""
    return mock_response["product"]


@pytest.fixture
def mock_session():
    """Create mock session."""
    return MagicMock()


def test_split_text_default_separator():
    """Test split_text function with default separator and index."""
    result = split_text("en:sugar", ":", 1)
    assert result == "sugar"


def test_split_text_custom_separator():
    """Test split_text function with custom separator."""
    result = split_text("a-b-c", "-", 1)
    assert result == "b"


def test_split_text_index_zero():
    """Test split_text function with index 0."""
    result = split_text("en:sugar", ":", 0)
    assert result == "en"


def test_normalize_text_basic():
    """Test normalize_text function with basic input."""
    result = normalize_text("sugar")
    assert result == "Sugar"


def test_normalize_text_with_hyphens():
    """Test normalize_text function with hyphens."""
    result = normalize_text("palm-oil")
    assert result == "Palm oil"


def test_capitalize_text():
    """Test capitalize_text function."""
    result = capitalize_text("hello world")
    assert result == "Hello World"


def test_create_nutrition_success(mock_product, mock_session):
    """Test create_nutrition function with valid data."""
    product_id = 1
    create_nutrition(product_id, mock_product, mock_session)

    mock_session.add.assert_called_once()

    added_nutrient = mock_session.add.call_args[0][0]

    assert added_nutrient.product_id == 1
    assert added_nutrient.energy_kcal_100g == 539
    assert added_nutrient.fat_100g == 30.9
    assert added_nutrient.saturated_fat_100g == 10.6
    assert added_nutrient.carbohydrates_100g == 57.5
    assert added_nutrient.sugars_100g == 56.3
    assert added_nutrient.proteins_100g == 6.3
    assert added_nutrient.salt_100g == 0.107
    assert added_nutrient.sodium_100g == 0.0428


def test_create_categories_success(mock_product, mock_session):
    """Test create_categories function with valid data."""
    product_id = 1
    create_categories(product_id, mock_product, mock_session)

    expected_count = len(mock_product["categories"].split(","))

    assert mock_session.add.call_count == expected_count


def test_create_countries_success(mock_product, mock_session):
    """Test create_countries function with valid data."""
    product_id = 1
    create_countries(product_id, mock_product, mock_session)

    mock_session.add.assert_called_once()


def test_get_packaging_with_english_text():
    """Test get_packaging function with English packaging text."""
    product_with_english_packaging = {"packaging_text_en": "Glass jar, plastic lid"}
    result = get_packaging(product_with_english_packaging)
    assert result == "Glass jar, plastic lid"


def test_get_packaging_with_generic_text():
    """Test get_packaging function with generic packaging text."""
    product_with_generic_packaging = {"packaging_text": "pot en verre"}
    result = get_packaging(product_with_generic_packaging)
    assert result == "Pot en verre"


def test_get_packaging_none_product():
    """Test get_packaging function with None product."""
    result = get_packaging(None)
    assert result == ""


def test_get_packaging_invalid_product():
    """Test get_packaging function with invalid product type."""
    result = get_packaging("not a dict")
    assert result == ""


@patch("src.process.SessionLocal")
@patch("src.process.Product")
def test_create_product_success(
    mock_product_class, mock_session_local, mock_product, mock_session
):
    """Test create_product function with valid data."""
    mock_session.query().filter().first.return_value = None

    result = create_product(mock_product, mock_session)

    assert result is True
    mock_session.add.assert_called()
