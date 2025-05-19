import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from scraper import get_top_products
from supabase_operations import save_product

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def clean_database():
    """Clean the database by removing all existing products"""
    try:
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials")
            
        supabase = create_client(supabase_url, supabase_key)
        
        # Delete all products
        response = supabase.table('products').delete().neq('id', '0').execute()
        logger.info("Successfully cleaned database")
        
    except Exception as e:
        logger.error(f"Error cleaning database: {str(e)}")
        raise

def rescrape_data():
    """Re-scrape data for week 20 of 2025"""
    try:
        # Use week 20 of 2025
        year = 2025
        week = 20
        
        logger.info(f"Fetching products for week {week} of {year}")
        
        # Get top products
        products = get_top_products(limit=20, year=year, week=week)
        
        if not products:
            logger.warning("No products found")
            return
        
        logger.info(f"Found {len(products)} products")
        
        # Save each product to the database
        for product in products:
            try:
                save_product(product)
                logger.info(f"Successfully saved product: {product['name']}")
            except Exception as e:
                logger.error(f"Failed to save product {product.get('name', 'unknown')}: {str(e)}")
                continue
        
        logger.info("Database update completed successfully")
        
    except Exception as e:
        logger.error(f"Error updating database: {str(e)}")
        raise

if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "PRODUCTHUNT_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    try:
        # First clean the database
        clean_database()
        
        # Then re-scrape the data
        rescrape_data()
        
    except Exception as e:
        logger.error(f"Failed to clean and re-scrape: {str(e)}")
        sys.exit(1) 