import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("supabase_operations")

# Load environment variables
load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Check if credentials are available
if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("Supabase credentials are missing. Make sure to set SUPABASE_URL and SUPABASE_KEY environment variables.")
    logger.warning("Operations will fail until these are properly configured.")

# Initialize Supabase client only if credentials are available
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}")

def save_product(product):
    """Upsert a product to Supabase"""
    if not supabase:
        logger.error("Cannot save product: Supabase client not initialized. Please check your credentials.")
        return
    
    try:
        now = datetime.now().isoformat()
        product_data = {
            "id": product['id'],
            "name": product['name'],
            "tagline": product.get('tagline'),
            "description": product.get('description'),
            "url": product.get('url'),
            "website_url": product.get('website_url'),
            "thumbnail_url": product.get('thumbnail_url'),
            "launch_date": product.get('launch_date'),
            "upvotes": product.get('upvotes', 0),
            "maker_ids": product.get('maker_ids', []),
            "topics": product.get('topics', []),
            "updated_at": now
        }
        # Upsert product (insert or update by id)
        supabase.table('products').upsert(product_data, on_conflict=['id']).execute()
        logger.info(f"Upserted product: {product['name']}")
    except Exception as e:
        logger.error(f"Error upserting product {product.get('name', 'unknown')}: {str(e)}")

def get_products_by_date(date_str):
    """Get products launched on a specific date"""
    if not supabase:
        logger.error("Cannot get products: Supabase client not initialized. Please check your credentials.")
        return []
    
    try:
        response = supabase.table('products') \
                          .select('*') \
                          .eq('launch_date', date_str) \
                          .order('upvotes', desc=True) \
                          .execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching products by date {date_str}: {str(e)}")
        return []

def get_top_products(limit=10):
    """Get top products by upvotes"""
    if not supabase:
        logger.error("Cannot get products: Supabase client not initialized. Please check your credentials.")
        return []
    
    try:
        response = supabase.table('products') \
                          .select('*') \
                          .order('upvotes', desc=True) \
                          .limit(limit) \
                          .execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching top products: {str(e)}")
        return []