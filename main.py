#!/usr/bin/env python
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
    args = parse_args()
    logger = setup_logging(args.verbose)

    BASE_URL = "https://world.openfoodfacts.org/cgi/search.pl"

    logger.info(f"Starting Food Facts application for search: '{args.search_terms}'")

    try:
        # Create database and tables
        logger.info("Initializing database...")
        create_database()
        logger.info("Database initialization complete")

        params = {"search_terms": args.search_terms, "json": 1, "search_simple": 1}
        logger.info(f"Searching for products with terms: {params['search_terms']}")

        if args.max_pages:
            logger.info(f"Limited to maximum {args.max_pages} pages")

        products, total_count = paginate_products(BASE_URL, params, args.max_pages)
        save_data(products, total_count)
        logger.info("Search complete. Products processed successfully")

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)

    logger.info("Food Facts database loaded!")


if __name__ == "__main__":
    main()
