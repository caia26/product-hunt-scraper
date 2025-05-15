# ProductHunt Scraper

A tool to fetch and display the top products launched on ProductHunt using their GraphQL API. The scraper retrieves products sorted by votes and provides detailed information about each product.

## Features

- Fetch today's top products or products from a specific date
- Sort products by number of votes
- Display product details including name, tagline, description, website, and vote count
- Show makers information
- Export results in text or JSON format
- Save results to a file

## Requirements

- Python 3.6+
- `requests` library

## Installation

1. Clone this repository or download the files
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Authentication

You'll need a ProductHunt API access token. You can:
- Pass it directly using the `--token` argument
- Set it as the `PRODUCTHUNT_TOKEN` environment variable
- Create a `.env` file in the project directory with the format:
  ```
  PRODUCTHUNT_TOKEN=your_token_here
  ```

To get a token, you need to:
1. Create an account on ProductHunt
2. Register an application at https://api.producthunt.com/v2/oauth/applications
3. Get your developer token from the API dashboard

### Basic Usage

```bash
# Display today's top 10 products
python ph_scraper.py --token YOUR_TOKEN

# Get the top 20 products in JSON format
python ph_scraper.py --token YOUR_TOKEN --limit 20 --format json

# Fetch products for a specific date
python ph_scraper.py --token YOUR_TOKEN --date 2023-01-15

# Save results to a file
python ph_scraper.py --token YOUR_TOKEN --output results.txt

# Enable verbose logging
python ph_scraper.py --token YOUR_TOKEN --verbose
```

### Command Line Options

- `--token`: Your ProductHunt API access token
- `--limit`: Number of products to fetch (default: 10)
- `--format`: Output format - "text" or "json" (default: text)
- `--output`: File to save results (if not specified, prints to stdout)
- `--date`: Specific date to fetch products from (format: YYYY-MM-DD, default: today)
- `--verbose`, `-v`: Enable verbose logging

## Sample Output

```
Today's Top 5 Products on ProductHunt:

1. Example Product - This is a sample tagline
   Votes: 150 | Comments: 25
   Website: https://example.com
   ProductHunt: https://producthunt.com/products/example-product
   Makers: John Doe, Jane Smith
   Topics: Productivity, Design Tools

2. Another Product - Another sample tagline
   Votes: 120 | Comments: 15
   Website: https://anotherexample.com
   ProductHunt: https://producthunt.com/products/another-product
   Makers: Bob Johnson
   Topics: Developer Tools, Utilities
```

## Attribution

This tool uses the ProductHunt API. As per ProductHunt's requirements, please attribute ProductHunt when using this tool.

## License

MIT 