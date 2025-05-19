#!/usr/bin/env python3
"""
ProductHunt Scraper - Tool to fetch top products launched today from ProductHunt
"""

import requests
import json
import os
import datetime
import argparse
import sys
import logging
import time
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs, urlunparse

# Load environment variables from .env file
load_dotenv()


class ProductHuntError(Exception):
    """Base exception for ProductHunt API errors"""
    pass


class ProductHuntScraper:
    """Client for scraping ProductHunt top products"""
    
    BASE_URL = "https://api.producthunt.com/v2/api/graphql"
    
    def __init__(self, access_token: Optional[str] = None, logger=None):
        """Initialize the scraper with an access token"""
        self.access_token = access_token or os.environ.get("PRODUCTHUNT_TOKEN")
        if not self.access_token:
            raise ValueError("Access token must be provided either directly or via PRODUCTHUNT_TOKEN environment variable")
        
        self.logger = logger or logging.getLogger(__name__)
    
    def _clean_url(self, url: str) -> str:
        """Clean URL by removing tracking parameters"""
        if not url:
            return ""
            
        try:
            # Parse the URL
            parsed = urlparse(url)
            
            # Parse query parameters
            query_params = parse_qs(parsed.query)
            
            # Remove common tracking parameters
            tracking_params = ['ref', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
            for param in tracking_params:
                query_params.pop(param, None)
            
            # Reconstruct the URL without tracking parameters
            cleaned_query = '&'.join(f"{k}={v[0]}" for k, v in query_params.items())
            cleaned_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                cleaned_query if cleaned_query else '',
                parsed.fragment
            ))
            
            return cleaned_url
        except Exception as e:
            self.logger.warning(f"Failed to clean URL {url}: {str(e)}")
            return url
    
    def _get_final_url(self, url: str, max_redirects: int = 5) -> str:
        """
        Follow redirects to get the final URL
        """
        if not url:
            return ""
            
        try:
            # Add headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Start with the initial URL
            current_url = url
            redirect_count = 0
            
            while redirect_count < max_redirects:
                # Make the request
                response = requests.get(current_url, headers=headers, allow_redirects=False)
                
                # If we get a redirect
                if response.status_code in (301, 302, 303, 307, 308):
                    # Get the new URL
                    new_url = response.headers.get('Location')
                    if not new_url:
                        break
                        
                    # Handle relative URLs
                    if not new_url.startswith(('http://', 'https://')):
                        parsed = urlparse(current_url)
                        new_url = f"{parsed.scheme}://{parsed.netloc}{new_url}"
                    
                    current_url = new_url
                    redirect_count += 1
                    
                    # Add a small delay to be nice to the server
                    time.sleep(0.5)
                else:
                    break
            
            # Clean the final URL
            final_url = self._clean_url(current_url)
            self.logger.info(f"Original URL: {url}")
            self.logger.info(f"Final URL: {final_url}")
            return final_url
            
        except Exception as e:
            self.logger.error(f"Error getting final URL for {url}: {str(e)}")
            return url
    
    def _make_request(self, query: str) -> Dict[str, Any]:
        """Make a GraphQL request to the ProductHunt API"""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://api.producthunt.com/",
            "Origin": "https://api.producthunt.com"
        }
        
        # Log the request for debugging
        self.logger.debug(f"Making request to {self.BASE_URL}")
        self.logger.debug(f"Headers: {headers}")
        self.logger.debug(f"Query: {query}")
        
        data = {"query": query}
        
        try:
            response = requests.post(self.BASE_URL, headers=headers, json=data)
            
            # Log the full response for debugging
            self.logger.debug(f"Response status: {response.status_code}")
            try:
                response_json = response.json()
                self.logger.debug(f"Response JSON: {json.dumps(response_json, indent=2)}")
            except:
                self.logger.debug(f"Response text: {response.text[:500]}")
            
            response.raise_for_status()
            
            result = response.json()
            
            # Check for GraphQL errors
            if "errors" in result:
                error_message = "; ".join([err.get("message", "Unknown error") for err in result["errors"]])
                self.logger.error(f"GraphQL errors: {json.dumps(result.get('errors', []), indent=2)}")
                raise ProductHuntError(f"GraphQL error: {error_message}")
            
            return result
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise ProductHuntError(f"API request failed: {str(e)}") from e
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse API response: {str(e)}")
            raise ProductHuntError(f"Failed to parse API response: {str(e)}") from e
    
    def _extract_post_data(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract post data from a GraphQL node"""
        if not node:
            return None
        
        # Extract topics safely
        topics = []
        for topic_edge in node.get("topics", {}).get("edges", []):
            topic_node = topic_edge.get("node", {})
            if topic_node and "name" in topic_node:
                topics.append(topic_node["name"])
        
        # Extract makers with updated format
        makers = []
        makers_data = node.get("makers", [])
        if isinstance(makers_data, list):
            for maker in makers_data:
                if maker and "name" in maker:
                    maker_info = {
                        "name": maker.get("name", ""),
                        "username": maker.get("username", ""),
                        "profile_url": f"https://producthunt.com/@{maker.get('username', '')}" if maker.get("username") else ""
                    }
                    makers.append(maker_info)
        
        # Get the final company URLs by following redirects
        website_url = self._get_final_url(node.get("website", ""))
        product_url = self._get_final_url(node.get("url", ""))
        
        return {
            "id": node.get("id"),
            "name": node.get("name", "Unnamed Product"),
            "tagline": node.get("tagline", ""),
            "description": node.get("description", ""),
            "url": product_url,
            "votes_count": node.get("votesCount", 0),
            "comments_count": node.get("commentsCount", 0),
            "website": website_url,
            "product_url": f"https://producthunt.com/products/{node.get('slug', '')}" if node.get("slug") else "",
            "created_at": node.get("createdAt", ""),
            "thumbnail": node.get("thumbnail", {}).get("url", ""),
            "topics": topics,
            "makers": makers
        }
    
    def _create_weekly_query(self, year: int, week: int) -> str:
        """Create a GraphQL query to fetch posts for a specific week"""
        # Calculate the start and end dates for the week
        start_date = datetime.datetime.strptime(f"{year}-W{week:02d}-1", "%Y-W%W-%w")
        end_date = start_date + datetime.timedelta(days=6)
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        return f"""
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
                commentsCount
                website
                createdAt
                thumbnail {{
                  url
                }}
                topics {{
                  edges {{
                    node {{
                      name
                    }}
                  }}
                }}
                makers {{
                  id
                  name
                  username
                }}
              }}
            }}
          }}
        }}
        """
    
    def get_weekly_posts(self, year: int, week: int, limit: Optional[int] = 20) -> List[Dict[str, Any]]:
        """
        Get top posts from ProductHunt for a specific week
        
        Args:
            year: Year to fetch (e.g., 2025)
            week: Week number (1-52)
            limit: Number of posts to return
        """
        if not 1 <= week <= 52:
            raise ProductHuntError(f"Invalid week number: {week}. Week must be between 1 and 52.")
            
        self.logger.info(f"Fetching top products for week {week} of {year}")
        
        # Create and execute the query
        query = self._create_weekly_query(year, week)
        result = self._make_request(query)
        
        posts = []
        edges = result.get("data", {}).get("posts", {}).get("edges", [])
        
        if not edges:
            self.logger.warning(f"No posts found in API response for week {week} of {year}")
            return []
        
        for edge in edges:
            post_data = self._extract_post_data(edge.get("node", {}))
            if post_data:
                posts.append(post_data)
        
        # Sort by votes count in descending order (highest votes first)
        posts.sort(key=lambda x: x.get("votes_count", 0), reverse=True)
        
        # Limit the results to the requested number
        return posts[:limit]


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr
    )
    return logging.getLogger("ph_scraper")


def main():
    """Main function to run the scraper"""
    parser = argparse.ArgumentParser(description="Scrape top products from ProductHunt")
    parser.add_argument("--token", help="ProductHunt API access token (or set PRODUCTHUNT_TOKEN environment variable)")
    parser.add_argument("--limit", type=int, default=20, help="Number of products to fetch (default: 20)")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format (default: text)")
    parser.add_argument("--output", help="Output file path (if not specified, prints to stdout)")
    parser.add_argument("--year", type=int, help="Year to fetch (default: current year)")
    parser.add_argument("--week", type=int, help="Week number to fetch (1-52, default: current week)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    logger = setup_logging(args.verbose)
    
    try:
        # Get current year and week if not specified
        now = datetime.datetime.now()
        year = args.year or now.year
        week = args.week or now.isocalendar()[1]
        
        scraper = ProductHuntScraper(access_token=args.token, logger=logger)
        posts = scraper.get_weekly_posts(year=year, week=week, limit=args.limit)
        
        if not posts:
            logger.warning(f"No posts found for week {week} of {year}")
            print(f"No products found for week {week} of {year} on ProductHunt.")
            return 0
        
        if args.format == "json":
            output = json.dumps(posts, indent=2)
        else:
            output_lines = [f"Week {week} of {year}'s Top {len(posts)} Products on ProductHunt:", ""]
            
            for i, post in enumerate(posts, 1):
                output_lines.append(f"{i}. {post['name']} - {post['tagline']}")
                output_lines.append(f"   Votes: {post['votes_count']} | Comments: {post['comments_count']}")
                
                if post['website']:
                    output_lines.append(f"   Website: {post['website']}")
                
                if post['product_url']:
                    output_lines.append(f"   ProductHunt: {post['product_url']}")
                
                if post['makers']:
                    makers_str = ", ".join([maker['name'] for maker in post['makers']])
                    output_lines.append(f"   Makers: {makers_str}")
                
                if post['topics']:
                    output_lines.append(f"   Topics: {', '.join(post['topics'])}")
                
                output_lines.append("")
            
            output = "\n".join(output_lines)
        
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            logger.info(f"Results saved to {args.output}")
            print(f"Results saved to {args.output}")
        else:
            print(output)
            
    except ProductHuntError as e:
        logger.error(f"ProductHunt API error: {str(e)}")
        print(f"Error: {str(e)}")
        return 1
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"Error: {str(e)}")
        return 1
    
    return 0


def get_top_products(limit: int = 10, date: Optional[datetime.date] = None, year: Optional[int] = None, week: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Wrapper function to get top products from ProductHunt.
    This function exists to provide compatibility with the daily_update.py script.
    
    Args:
        limit: Number of products to return
        date: Optional date to fetch products for. If None, uses today's date.
        year: Optional year for weekly pull.
        week: Optional week number for weekly pull.
    
    Returns:
        List of product dictionaries with standardized format for Supabase
    """
    logger = setup_logging()
    
    try:
        # Get access token from environment
        access_token = os.environ.get("PRODUCTHUNT_TOKEN")
        if not access_token:
            logger.error("PRODUCTHUNT_TOKEN environment variable not set")
            return []
        
        # Use weekly pull if year and week are provided
        if year is not None and week is not None:
            scraper = ProductHuntScraper(access_token=access_token, logger=logger)
            raw_products = scraper.get_weekly_posts(year=year, week=week, limit=limit)
        else:
            # Fallback to daily pull (not used in your workflow now)
            now = datetime.datetime.now()
            date_str = date.isoformat() if date else now.date().isoformat()
            scraper = ProductHuntScraper(access_token=access_token, logger=logger)
            raw_products = scraper.get_todays_posts(limit=limit, specific_date=date_str)
        
        # Transform to format expected by Supabase
        products = []
        for product in raw_products:
            # Get maker IDs
            maker_ids = [maker.get("username", "") for maker in product.get("makers", [])]
            
            # Extract topics as a list of strings
            topics = product.get("topics", [])
            
            # Create standardized product entry
            supabase_product = {
                "id": product.get("id"),
                "name": product.get("name"),
                "tagline": product.get("tagline"),
                "description": product.get("description", ""),
                "url": product.get("product_url", ""),
                "website_url": product.get("website", ""),
                "thumbnail_url": product.get("thumbnail", ""),
                "launch_date": product.get("created_at", ""),
                "upvotes": product.get("votes_count", 0),
                "maker_ids": maker_ids,
                "topics": topics
            }
            products.append(supabase_product)
        return products
    except Exception as e:
        logger.exception(f"Error fetching top products: {str(e)}")
        return []


if __name__ == "__main__":
    exit(main()) 