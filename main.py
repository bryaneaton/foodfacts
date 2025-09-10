#!/usr/bin/env python
"""Food Facts application for fetching and storing product data.

This module provides functionality to search for food products using the
OpenFoodFacts API and store the results in a local database.
"""
import argparse
import logging
import sys

from src.api import paginate_products
from src.models import create_database
from src.process import save_data


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("food_products.log"), logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Fetch and store food product data from OpenFoodFacts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "coca cola"
  %(prog)s "chocolate cookies" --max-pages 5
  %(prog)s "organic milk" --verbose
        """,
    )

    parser.add_argument(
        "search_terms",
        help="Search terms to find products (e.g., 'coca cola', 'chocolate')",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        help="Maximum number of pages to fetch (default: all pages)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    return parser.parse_args()


def main():
    """Main application entry point.

    Parses command line arguments, sets up logging, initializes the database,
    and processes product search requests.
    """
    args = parse_args()
    logger = setup_logging(args.verbose)

    base_url = "https://world.openfoodfacts.org/cgi/search.pl"

    logger.info("Starting Food Facts application for search: '%s'", args.search_terms)

    try:
        # Create database and tables
        logger.info("Initializing database...")
        create_database()
        logger.info("Database initialization complete")

        params = {"search_terms": args.search_terms, "json": 1, "search_simple": 1}
        logger.info("Searching for products with terms: %s", params["search_terms"])

        if args.max_pages:
            logger.info("Limited to maximum %d pages", args.max_pages)

        products, total_count = paginate_products(base_url, params, args.max_pages)
        save_data(products, total_count)
        logger.info("Search complete. Products processed successfully")

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except (ConnectionError, TimeoutError, ValueError) as e:
        logger.error("Application error: %s", e, exc_info=True)
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error: %s", e, exc_info=True)
        sys.exit(1)

    logger.info("Food Facts database loaded!")


if __name__ == "__main__":
    main()
