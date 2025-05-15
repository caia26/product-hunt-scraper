import datetime
import logging
import os
from scraper import get_top_products  # Import from the same directory
from supabase_operations import save_product

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("daily_update")

def update_database():
    """Fetch today's products and update the database"""
    try:
        # Check if environment variables are set
        if not os.getenv("PRODUCTHUNT_TOKEN"):
            logger.error("PRODUCTHUNT_TOKEN environment variable is not set")
            return
            
        if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
            logger.error("SUPABASE_URL and/or SUPABASE_KEY environment variables are not set")
            return
            
        # Get today's date
        today = datetime.date.today()
        date_str = today.strftime("%Y-%m-%d")
        
        logger.info(f"Fetching ProductHunt products for {date_str}...")
        
        # Use your existing scraper to get products
        products = get_top_products(date=today)
        
        if not products:
            logger.warning("No products found for today.")
            return
        
        logger.info(f"Found {len(products)} products. Updating database...")
        
        # Save each product to the database
        success_count = 0
        for product in products:
            try:
                save_product(product)
                success_count += 1
            except Exception as e:
                logger.error(f"Error saving product {product.get('name')}: {e}")
        
        if success_count > 0:
            logger.info(f"Successfully saved {success_count} products to the database.")
        else:
            logger.warning("No products were successfully saved to the database.")
            
    except Exception as e:
        logger.exception(f"Error in update_database: {e}")

if __name__ == "__main__":
    update_database()