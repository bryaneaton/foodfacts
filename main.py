#!/usr/bin/env python
import logging
from src.models import create_database, get_db, Product, Nutrient, Ingredient, Category, Country
from src.process import paginate_products, save_data
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('food_products.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_URL = 'https://world.openfoodfacts.org/cgi/search.pl'


def query_all_products():
    """Query all products from the database with their related data."""
    logger.info("Querying all products from database...")
    
    db = get_db()
    try:
        # Get database statistics
        product_count = db.query(Product).count()
        nutrient_count = db.query(Nutrient).count()
        ingredient_count = db.query(Ingredient).count()
        category_count = db.query(Category).count()
        country_count = db.query(Country).count()
        
        print(f"\n=== DATABASE STATISTICS ===")
        print(f"Products: {product_count}")
        print(f"Nutrient records: {nutrient_count}")
        print(f"Ingredient records: {ingredient_count}")
        print(f"Category records: {category_count}")
        print(f"Country records: {country_count}")
        print("=" * 30)
        
        if product_count == 0:
            print("\nNo products found in database.")
            print("To add products, you can:")
            print("1. Run the original main.py to fetch products from OpenFoodFacts")
            print("2. Add products manually using the database")
            return []
        
        # Query all products with their relationships
        products = db.query(Product).all()
        
        logger.info(f"Found {len(products)} products in database")
        
        for i, product in enumerate(products, 1):
            print(f"\n--- Product {i}: {product.product_name or 'Unknown'} ---")
            print(f"Barcode: {product.barcode}")
            print(f"Brand: {product.brand or 'Unknown'}")
            print(f"Packaging: {product.packaging or 'Unknown'}")
            print(f"Created: {product.create_t}")
            
            # Get nutrients
            nutrients = db.query(Nutrient).filter(Nutrient.barcode == product.barcode).first()
            if nutrients:
                print("\nNutritional Information (per 100g):")
                if nutrients.energy_kcal_100g:
                    print(f"  Energy: {nutrients.energy_kcal_100g} kcal")
                if nutrients.fat_100g:
                    print(f"  Fat: {nutrients.fat_100g}g")
                if nutrients.saturated_fat_100g:
                    print(f"  Saturated Fat: {nutrients.saturated_fat_100g}g")
                if nutrients.carbohydrates_100g:
                    print(f"  Carbohydrates: {nutrients.carbohydrates_100g}g")
                if nutrients.sugars_100g:
                    print(f"  Sugars: {nutrients.sugars_100g}g")
                if nutrients.fiber_100g:
                    print(f"  Fiber: {nutrients.fiber_100g}g")
                if nutrients.proteins_100g:
                    print(f"  Proteins: {nutrients.proteins_100g}g")
                if nutrients.salt_100g:
                    print(f"  Salt: {nutrients.salt_100g}g")
                if nutrients.sodium_100g:
                    print(f"  Sodium: {nutrients.sodium_100g}g")
            else:
                print("\nNo nutritional information available")
            
            # Get ingredients
            ingredients = db.query(Ingredient).filter(Ingredient.barcode == product.barcode).first()
            if ingredients and ingredients.ingredient_text:
                print(f"\nIngredients: {ingredients.ingredient_text}")
            else:
                print("\nNo ingredient information available")
            
            # Get categories
            categories = db.query(Category).filter(Category.barcode == product.barcode).all()
            if categories:
                category_names = [cat.category for cat in categories]
                print(f"Categories: {', '.join(category_names)}")
            else:
                print("No category information available")
            
            # Get countries
            countries = db.query(Country).filter(Country.barcode == product.barcode).all()
            if countries:
                country_names = [country.country for country in countries]
                print(f"Countries: {', '.join(country_names)}")
            else:
                print("No country information available")
            
            print("-" * 50)
        
        return products
        
    except Exception as e:
        logger.error(f"Error querying products: {e}")
        raise
    finally:
        db.close()



def main():
    logger.info("Starting Food Facts application")
    
    try:
        # Create database and tables
        logger.info("Initializing database...")
        create_database()
        logger.info("Database initialization complete")
        
        params = {
            'search_terms': 'coca cola',
            'json': 1
        }
        logger.info(f"Searching for products with terms: {params['search_terms']}")
        products = paginate_products(BASE_URL, params)
        save_data(products)
        logger.info("Search complete. Products processed successfully")
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise
    
    logger.info("Food Facts database loaded!")






if __name__ == '__main__':
    main()
