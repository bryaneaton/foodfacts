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

1. Clone the repository:
```bash
git clone <repository-url>
cd foodfacts
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Search for products and store in database:
```bash
python main.py "coca cola"
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
├── src/
│   ├── api.py          # OpenFoodFacts API client
│   ├── models.py       # SQLAlchemy database models  
│   └── process.py      # Data processing and storage
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .venv/             # Virtual environment
```

## Code Quality

The project maintains high code quality standards:
- **Pylint Score**: 9.77/10 (main.py), 9.55/10 (src/)
- **Type Hints**: Full type annotation support
- **Documentation**: Comprehensive docstrings and comments
- **Error Handling**: Robust exception handling throughout
- **Logging**: Structured logging with configurable levels

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
pylint main.py src/

# Run type checking (if mypy is available)
mypy main.py src/
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

## Contributing

1. Ensure code passes pylint with score > 9.0
2. Add type hints to all functions
3. Include comprehensive docstrings
4. Follow existing code style and patterns
5. Test with various search terms and edge cases

## License

This project is licensed under the MIT License.