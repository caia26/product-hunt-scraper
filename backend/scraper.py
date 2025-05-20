#!/usr/bin/env python3
"""
Unified ProductHunt Scraper - Scrape top products in a date range and upsert to Supabase
"""
import os
import sys
import logging
import time
import argparse
import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from supabase_operations import save_product

# --- ProductHunt API logic ---
import requests
from urllib.parse import urlparse, parse_qs, urlunparse

print("RUNNING LATEST scraper.py VERSION")

class ProductHuntError(Exception):
    pass

class ProductHuntScraper:
    BASE_URL = "https://api.producthunt.com/v2/api/graphql"

    def __init__(self, access_token: Optional[str] = None, logger=None):
        self.access_token = access_token or os.environ.get("PRODUCTHUNT_TOKEN")
        if not self.access_token:
            raise ValueError("Access token must be provided or set PRODUCTHUNT_TOKEN env var")
        self.logger = logger or logging.getLogger(__name__)

    def _clean_url(self, url: str) -> str:
        if not url:
            return ""
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            tracking_params = ['ref', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
            for param in tracking_params:
                query_params.pop(param, None)
            cleaned_query = '&'.join(f"{k}={v[0]}" for k, v in query_params.items())
            cleaned_url = urlunparse((
                parsed.scheme, parsed.netloc, parsed.path, parsed.params, cleaned_query if cleaned_query else '', parsed.fragment
            ))
            return cleaned_url
        except Exception as e:
            self.logger.warning(f"Failed to clean URL {url}: {str(e)}")
            return url

    def _get_final_url(self, url: str, max_redirects: int = 5) -> str:
        if not url:
            return ""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
            current_url = url
            redirect_count = 0
            while redirect_count < max_redirects:
                try:
                    response = requests.get(current_url, headers=headers, allow_redirects=False)
                except requests.exceptions.SSLError as e:
                    self.logger.warning(f"SSL error for {current_url}: {e}. Skipping URL.")
                    return url
                if response.status_code in (301, 302, 303, 307, 308):
                    new_url = response.headers.get('Location')
                    if not new_url:
                        break
                    if not new_url.startswith(('http://', 'https://')):
                        parsed = urlparse(current_url)
                        new_url = f"{parsed.scheme}://{parsed.netloc}{new_url}"
                    current_url = new_url
                    redirect_count += 1
                    time.sleep(0.5)
                else:
                    break
            return self._clean_url(current_url)
        except Exception as e:
            self.logger.error(f"Error getting final URL for {url}: {str(e)}")
            return url

    def _make_request(self, query: str) -> Dict[str, Any]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": "Mozilla/5.0",
        }
        data = {"query": query}
        try:
            response = requests.post(self.BASE_URL, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            if "errors" in result:
                error_message = "; ".join([err.get("message", "Unknown error") for err in result["errors"]])
                self.logger.error(f"GraphQL errors: {result.get('errors', [])}")
                raise ProductHuntError(f"GraphQL error: {error_message}")
            return result
        except Exception as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise ProductHuntError(f"API request failed: {str(e)}")

    def _extract_post_data(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not node:
            return None
        topics = [edge.get("node", {}).get("name") for edge in node.get("topics", {}).get("edges", []) if edge.get("node", {}).get("name")]
        makers = []
        makers_data = node.get("makers", [])
        if isinstance(makers_data, list):
            for maker in makers_data:
                if maker and "name" in maker:
                    makers.append({
                        "name": maker.get("name", ""),
                        "username": maker.get("username", ""),
                        "profile_url": f"https://producthunt.com/@{maker.get('username', '')}" if maker.get("username") else ""
                    })
        website_url = self._get_final_url(node.get("website", ""))
        product_url = self._get_final_url(node.get("url", ""))
        return {
            "id": node.get("id"),
            "name": node.get("name", "Unnamed Product"),
            "tagline": node.get("tagline", ""),
            "description": node.get("description", ""),
            "url": product_url,
            "website_url": website_url,
            "thumbnail_url": node.get("thumbnail", {}).get("url", ""),
            "launch_date": node.get("createdAt", ""),
            "upvotes": node.get("votesCount", 0),
            "maker_ids": [maker.get("username", "") for maker in makers],
            "topics": topics
        }

    def _create_daily_query(self, date: datetime.date) -> str:
        start_str = date.strftime("%Y-%m-%d")
        end_str = date.strftime("%Y-%m-%d")
        return f'''
        query {{
          posts(first: 50, postedAfter: "{start_str}T00:00:00Z", postedBefore: "{end_str}T23:59:59Z", order: VOTES) {{
            edges {{
              node {{
                id
                name
                tagline
                description
                url
                slug
                votesCount
                website
                createdAt
                thumbnail {{ url }}
                topics {{ edges {{ node {{ name }} }} }}
                makers {{ id name username }}
              }}
            }}
          }}
        }}
        '''

    def get_posts_by_date(self, date: datetime.date, limit: int = 20) -> List[Dict[str, Any]]:
        self.logger.info(f"Fetching top products for {date}")
        query = self._create_daily_query(date)
        result = self._make_request(query)
        posts = []
        edges = result.get("data", {}).get("posts", {}).get("edges", [])
        for edge in edges:
            post_data = self._extract_post_data(edge.get("node", {}))
            if post_data:
                posts.append(post_data)
        posts.sort(key=lambda x: x.get("upvotes", 0), reverse=True)
        return posts[:limit]

# --- End ProductHuntScraper ---

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)

def get_date_range(start_date: datetime.date, end_date: datetime.date) -> List[datetime.date]:
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += datetime.timedelta(days=1)
    return date_list

def scrape_date_range(
    start_date: datetime.date,
    end_date: datetime.date,
    max_products_per_day: int = 20,
    max_total_products: int = 100,
    delay_between_requests: float = 1.0
) -> Dict[str, Any]:
    logger = setup_logging()
    scraper = ProductHuntScraper()
    date_list = get_date_range(start_date, end_date)
    total_products = 0
    for date in date_list:
        try:
            date_str = date.isoformat()
            logger.info(f"Processing date: {date_str}")
            if total_products >= max_total_products:
                logger.warning(f"Reached maximum total products limit ({max_total_products})")
                break
            remaining_products = max_total_products - total_products
            current_limit = min(max_products_per_day, remaining_products)
            logger.info(f"Scraping products for {date_str} (limit: {current_limit})")
            products = scraper.get_posts_by_date(date, limit=current_limit)
            if not products:
                logger.warning(f"No products found for {date_str}")
                continue
            for product in products:
                save_product(product)
                total_products += 1
                if total_products >= max_total_products:
                    break
            time.sleep(delay_between_requests)
        except Exception as e:
            logger.error(f"Error scraping products for {date_str}: {str(e)}")
            continue
    return {
        "total_products": total_products,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "total_dates": len(date_list)
    }

def parse_args():
    parser = argparse.ArgumentParser(description='Scrape ProductHunt products within a date range')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--max-products-per-day', type=int, default=20, help='Maximum products to scrape per day')
    parser.add_argument('--max-total-products', type=int, default=100, help='Maximum total products to scrape')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds')
    return parser.parse_args()

if __name__ == "__main__":
    load_dotenv()
    args = parse_args()
    try:
        start_date = datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(args.end_date, '%Y-%m-%d').date()
    except ValueError as e:
        print(f"Error parsing dates: {str(e)}")
        sys.exit(1)
    stats = scrape_date_range(
        start_date=start_date,
        end_date=end_date,
        max_products_per_day=args.max_products_per_day,
        max_total_products=args.max_total_products,
        delay_between_requests=args.delay
    )
    print(f"Scraping completed: {stats}") 