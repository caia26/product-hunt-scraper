# ProductHunt Scraper with Supabase Integration

A tool to fetch and display the top products launched on ProductHunt using their GraphQL API, with integration to store data in Supabase. The scraper retrieves products sorted by votes, provides detailed information about each product, and allows for storing this data in a Supabase database for further analysis.

## Features

- Fetch today's top products or products from a specific date
- Sort products by number of votes
- Display product details including name, tagline, description, website, and vote count
- Show makers information
- Export results in text or JSON format
- Save results to a file
- **Store product data in Supabase database**
- **Automatic daily updates**

## Requirements

- Python 3.6+
- `requests` library
- `python-dotenv` library
- `supabase` library

## Installation

1. Clone this repository or download the files
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

### ProductHunt API

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

### Supabase Configuration

To enable Supabase integration, you need to set up:
1. Create a Supabase account at https://supabase.com/
2. Create a new project
3. Add the following environment variables to your `.env` file:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_api_key
   ```
4. Create a `products` table in your Supabase project with the following schema:

```sql
create table products (
  id text primary key,
  name text not null,
  tagline text,
  description text,
  url text,
  website_url text,
  thumbnail_url text,
  launch_date date,
  upvotes integer,
  maker_ids jsonb,
  topics jsonb,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone
);

-- Optional index for faster retrieval by date
create index idx_products_launch_date on products(launch_date);
```

## Usage

### Basic Usage (Command Line)

```bash
# Display today's top 10 products
python scraper.py --token YOUR_TOKEN

# Get the top 20 products in JSON format
python scraper.py --token YOUR_TOKEN --limit 20 --format json

# Fetch products for a specific date
python scraper.py --token YOUR_TOKEN --date 2023-01-15

# Save results to a file
python scraper.py --token YOUR_TOKEN --output results.txt

# Enable verbose logging
python scraper.py --token YOUR_TOKEN --verbose
```

### Daily Updates with Supabase Integration

To update your Supabase database with the latest products:

```bash
# Run the daily update script
python daily_update.py
```

You can automate this script with a cron job or a scheduler to run daily.

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

## Supabase Integration Features

- **Automatic Deduplication**: The system checks if a product already exists before inserting it
- **Daily Updates**: Can be scheduled to run daily to keep your database updated
- **Data Querying**: Retrieve products by date or get the top products by upvotes
- **Error Handling**: Robust error handling for API and database operations

## Attribution

This tool uses the ProductHunt API. As per ProductHunt's requirements, please attribute ProductHunt when using this tool.

## License

MIT 