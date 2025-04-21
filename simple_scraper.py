import argparse
import logging
import sys
import time
import json
from pathlib import Path
from src.config import BASE_DIR, RAW_DATA_DIR
from src.scraper.utils import fetch_url, extract_domain
from src.parser.parsers import BaseParser
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(BASE_DIR / "scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def scrape_url(url, output_dir=None):
    """Scrape a URL and save content."""
    start_time = time.time()
    logger.info(f"Scraping URL: {url}")
    
    # Fetch HTML content
    html_content = fetch_url(url)
    if not html_content:
        logger.error(f"Failed to fetch {url}")
        return None
        
    # Parse content
    parser = BaseParser(html_content, url)
    
    # Extract data
    data = {
        'url': url,
        'domain': extract_domain(url),
        'title': parser.get_title(),
        'meta_description': parser.get_meta_description(),
        'main_content_length': len(parser.get_main_content()) if parser.get_main_content() else 0,
        'links_count': len(parser.get_all_links()),
        'images_count': len(parser.get_images()),
        'scraped_at': datetime.datetime.utcnow().isoformat(),
    }
    
    # Save raw data
    if output_dir:
        output_path = Path(output_dir) / f"{data['domain']}_{int(time.time())}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved raw data to {output_path}")
    
    logger.info(f"Scraped {url} in {time.time() - start_time:.2f} seconds")
    return data

def main():
    """Main function to run the scraper."""
    parser = argparse.ArgumentParser(description="Web Scraper")
    parser.add_argument("url", nargs="?", help="URL to scrape")
    parser.add_argument("--urls-file", help="File containing URLs to scrape (one per line)")
    parser.add_argument("--output-dir", default=str(RAW_DATA_DIR), help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Create output directories
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    urls = []
    
    # Get URLs from command line or file
    if args.url:
        urls.append(args.url)
    elif args.urls_file:
        try:
            with open(args.urls_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logger.error(f"URLs file not found: {args.urls_file}")
            sys.exit(1)
    else:
        logger.error("No URL or URLs file provided")
        parser.print_help()
        sys.exit(1)
    
    all_results = []
    
    # Process each URL
    for url in urls:
        try:
            # Scrape URL
            result = scrape_url(url, output_dir)
            if result:
                all_results.append(result)
                logger.info(f"Successfully scraped {url}")
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
    
    logger.info(f"Processed {len(all_results)} URLs")
    logger.info(f"Results saved to {output_dir}")

if __name__ == "__main__":
    main()