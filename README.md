# FoodFacts Application

A Python application for fetching and storing food product data from OpenFoodFacts API with robust data processing and SQLite storage.

## Features

- **OpenFoodFacts API Integration**: Search and retrieve product data with pagination support
- **SQLite Database Storage**: Store products with related nutritional, ingredient, category, and country data
- **Data Processing & Normalization**: Clean and normalize text data with consistent formatting
- **Batch Processing**: Efficiently process large datasets with progress tracking
- **Robust Error Handling**: Comprehensive logging and error recovery mechanisms
- **Rate Limiting**: Built-in API rate limiting to respect service quotas
- **Command Line Interface**: Easy-to-use CLI with configurable options

## Installation

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

### Setup


1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Search for products and store in database:
```bash
python main.py "pepperoni pizza"
```

### Advanced Options

```bash
# Limit the number of pages to fetch
python main.py "chocolate cookies" --max-pages 5

# Enable verbose logging
python main.py "organic milk" --verbose

# Combine options
python main.py "gluten free bread" --max-pages 3 --verbose
```

### Command Line Arguments

- `search_terms`: Search terms to find products (required)
- `--max-pages`: Maximum number of pages to fetch (optional)
- `--verbose, -v`: Enable verbose logging (optional)

## SQLAlchemy
- SQLAlchemy was selected for this project due to its intuitive database connection handling and its code-first paradigm, which allows for defining database schemas directly in Python code.

## Assumptions
- I tried to split the text of the appropriate columns where possible, if empty or non-existant, i used the array and formatted the resulting strings.
- With more time available, i would achieve ~100% coverage for unit testing.

## Database Schema

The application creates an SQLite database (`food_products.db`) with the following tables:

- **products**: Main product information (barcode, name, brand, packaging)
- **nutrients**: Nutritional information per 100g
- **ingredients**: Product ingredients
- **categories**: Product categories
- **countries**: Product origin countries

All tables include audit fields (`created_at`, `updated_at`) for tracking changes.

## Project Structure

```
foodfacts/
├── main.py              # Main application entry point
├── tests/
│   ├── test_process.py # Basic Pytests
├── src/
│   ├── api.py          # OpenFoodFacts API client
│   ├── models.py       # SQLAlchemy database models  
│   └── process.py      # Data processing to SQLite
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .venv/             # Virtual environment
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run linting
pylint main.py src/

# Run type checking (if mypy is available)
mypy main.py src/

# Run Pytests
python -m pytest -v ./tests
```

### Data Processing Functions

The application includes several utility functions:

- `normalize_text()`: Normalize text with proper capitalization
- `split_text()`: Split text by separator with index selection
- `capitalize_text()`: Convert text to title case
- `get_packaging()`: Extract packaging information with fallback logic

## Logging

The application generates detailed logs in `food_products.log` including:
- API request/response information
- Database operations
- Error details with stack traces
- Processing statistics

## Error Handling

- **API Errors**: Graceful handling of network issues and API rate limits
- **Database Errors**: Transaction rollback on failures
- **Data Validation**: Skip invalid products while continuing processing
- **Graceful Degradation**: Continue processing even if individual items fail

