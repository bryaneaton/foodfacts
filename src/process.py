from typing import Iterator
import logging
from time import sleep
import niquests as niq
from src.models import Product, Nutrient, Ingredient, Category, Country, SessionLocal
from sqlalchemy.orm.session import Session
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def save_product(product: dict, session: Session):
    try:
        barcode = product.get('code', '')
        if not barcode:
            logger.warning("Skipping product with empty barcode")
            return
            
        # Check if product already exists
        existing_product = session.query(Product).filter(Product.barcode == barcode).first()
        if existing_product:
            logger.debug(f"Product with barcode {barcode} already exists, skipping")
            return
            
        session.add(Product(
            barcode=barcode,
            product_name=product.get('product_name', product.get('name', '')),
            brand=product.get('brand', ''),
            packaging=product.get('packaging', ''),
            created_at=datetime.fromtimestamp(product.get('created_t', 0), tz=timezone.utc),
            updated_at=datetime.fromtimestamp(product.get('last_modified_t', 0), tz=timezone.utc),
        ))
        session.commit()
        logger.debug(f"Successfully saved product with barcode {barcode}")
    except Exception as e:
        logger.error(f"Error saving product {product.get('code', 'unknown')}: {e}")
        session.rollback()

def save_data(products: Iterator[dict]):
    """Process the products iterator"""
    session = SessionLocal()
    for product in products:
        save_product(product, session)
    session.close()

def paginate_products(base_url, params, max_pages=None) -> Iterator[dict]:
    page = 1
    total_products_yielded = 0
    
    logger.info(f"Starting product pagination with params: {params}")
    if max_pages:
        logger.debug(f"Max pages limit set to: {max_pages}")
    
    while True:
        # Add pagination parameters
        current_params = params.copy()
        current_params['page'] = page
        current_params['page_size'] = 250
        
        logger.debug(f"Fetching page {page} with {current_params['page_size']} items per page")
        
        try:
            response = niq.get(base_url, params=current_params, 
                                  headers={'User-Agent': 'fetch-openfoodfacts/0.1 (your@email.com)'})
            response.raise_for_status()
            data = response.json()
            product_count = data['count']
            page_products = data['products']
            
            # Yield each product individually
            for product in page_products:
                yield product
                total_products_yielded += 1
            
            logger.info(f"Page {page}: Retrieved {len(page_products)} products. Total yielded: {total_products_yielded}/{product_count}")
            
        except Exception as e:
            logger.error(f"Error fetching page {page}: {e}")
            break
        
        # Check if we've processed all products on this page
        if len(page_products) == 0:
            logger.info("No more products to fetch - empty page")
            break
            
        # Check if we've hit our max page limit
        if max_pages and page >= max_pages:
            logger.warning(f"Reached max page limit: {max_pages}")
            break
            
        page += 1
        logger.debug(f"Waiting 0.6s before next request (rate limit compliance)")
        sleep(0.6)  # Respect rate limit (100/min = 1 every 0.6s)
    
    logger.info(f"Pagination complete. Total products yielded: {total_products_yielded}")