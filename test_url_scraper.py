import requests
import logging
from urllib.parse import urlparse, parse_qs, urlunparse
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_url(url: str) -> str:
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
        logger.warning(f"Failed to clean URL {url}: {str(e)}")
        return url

def get_final_url(url: str, max_redirects: int = 5) -> str:
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
        final_url = clean_url(current_url)
        logger.info(f"Original URL: {url}")
        logger.info(f"Final URL: {final_url}")
        return final_url
        
    except Exception as e:
        logger.error(f"Error getting final URL for {url}: {str(e)}")
        return url

def test_urls():
    """Test the URL extraction with some example Product Hunt URLs"""
    test_urls = [
        "https://www.producthunt.com/r/PRI3IBUFUIETLY",  # Appwrite Sites
        "https://www.producthunt.com/r/JVLQLRXRET363P",  # BnbIcons
        "https://www.producthunt.com/r/W5F6VSAVA6PGBZ",  # Distro
        "https://www.producthunt.com/r/VA2EFJVKOHS474",  # Ollama v0.7
        "https://www.producthunt.com/r/LAMWJ2QDZQVMRB",  # AI Operator
    ]
    
    for url in test_urls:
        final_url = get_final_url(url)
        print(f"\nTesting URL: {url}")
        print(f"Final URL: {final_url}")
        print("-" * 80)

if __name__ == "__main__":
    test_urls() 