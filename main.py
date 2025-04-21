import argparse
import logging
import sys
from pathlib import Path
from src.config import BASE_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.scraper.utils import fetch_url, extract_domain
from src.parser.parsers import ArticleParser
from src.analyzer.text_analysis import TextAnalyzer
from src.analyzer.visualizations import Visualizer
from src.database.models import init_db, Website, Page
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import time
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

def setup_database():
    """Initialize database and return session."""
    init_db()
    engine = create_engine(DB_CONNECTION_STRING)
    Session = sessionmaker(bind=engine)
    return Session()

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
    parser = ArticleParser(html_content, url)
    
    # Extract data
    data = {
        'url': url,
        'domain': extract_domain(url),
        'title': parser.get_title(),
        'meta_description': parser.get_meta_description(),
        'content_text': parser.get_clean_text(),
        'content_html': html_content,
        'author': parser.get_author(),
        'published_date': parser.get_publish_date(),
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

def analyze_content(content_text):
    """Analyze text content."""
    if not content_text:
        logger.warning("No content to analyze")
        return None
        
    analyzer = TextAnalyzer(content_text)
    
    # Perform various analyses
    word_freq = analyzer.get_word_frequency(top_n=50)
    sentences = analyzer.get_sentences()
    sentiment = analyzer.get_sentiment()
    entities = analyzer.extract_entities()
    readability = analyzer.get_readability_scores()
    
    analysis_results = {
        'word_frequency': dict(word_freq),
        'sentence_count': len(sentences),
        'average_sentence_length': sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0,
        'sentiment': sentiment,
        'entities': entities,
        'readability': readability
    }
    
    return analysis_results

def visualize_results(analysis_results, output_dir=None):
    """Create visualizations from analysis results."""
    if not analysis_results:
        logger.warning("No analysis results to visualize")
        return
        
    visualizer = Visualizer(output_dir)
    
    # Word frequency visualization
    word_freq = analysis_results.get('word_frequency', {})
    if word_freq:
        visualizer.plot_word_frequency(word_freq, top_n=20, 
                                     title="Top 20 Words by Frequency", 
                                     filename="word_frequency.png")
        visualizer.generate_wordcloud(word_freq, 
                                    title="Word Cloud Visualization", 
                                    filename="wordcloud.png")
    
    # Sentiment visualization if multiple documents
    if isinstance(analysis_results.get('sentiment', {}), list):
        visualizer.plot_sentiment_distribution(analysis_results['sentiment'],
                                            title="Sentiment Distribution",
                                            filename="sentiment_distribution.png")
    
    # Entity visualization if multiple documents
    if isinstance(analysis_results.get('entities', {}), list):
        visualizer.plot_entity_counts(analysis_results['entities'],
                                    title="Named Entity Counts",
                                    filename="entity_counts.png")
    
    logger.info(f"Created visualizations in {output_dir}")

def main():
    """Main function to run the scraper and analyzer."""
    parser = argparse.ArgumentParser(description="Web Scraper and Analyzer")
    parser.add_argument("url", nargs="?", help="URL to scrape")
    parser.add_argument("--urls-file", help="File containing URLs to scrape (one per line)")
    parser.add_argument("--output-dir", default=str(RAW_DATA_DIR), help="Directory to save output files")
    parser.add_argument("--analyze", action="store_true", help="Analyze scraped content")
    parser.add_argument("--visualize", action="store_true", help="Create visualizations")
    parser.add_argument("--save-to-db", action="store_true", help="Save data to database")
    
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
    
    # Database session if needed
    db_session = None
    if args.save_to_db:
        db_session = setup_database()
    
    all_results = []
    all_analyses = []
    
    # Process each URL
    for url in urls:
        try:
            # Scrape URL
            result = scrape_url(url, output_dir)
            if not result:
                continue
                
            all_results.append(result)
            
            # Save to database if requested
            if args.save_to_db and db_session:
                try:
                    # Check if website exists
                    website = db_session.query(Website).filter_by(domain=result['domain']).first()
                    if not website:
                        website = Website(
                            domain=result['domain'],
                            name=result['domain'].split('.')[0],
                            root_url=f"https://{result['domain']}",
                            last_scraped_at=datetime.datetime.utcnow()
                        )
                        db_session.add(website)
                        db_session.commit()
                    
                    # Create page entry
                    page = Page(
                        website_id=website.id,
                        url=result['url'],
                        title=result['title'],
                        meta_description=result['meta_description'],
                        content_text=result['content_text'],
                        content_html=result['content_html'],
                        author=result['author'],
                        published_date=result['published_date']
                    )
                    db_session.add(page)
                    db_session.commit()
                    logger.info(f"Saved {url} to database")
                except Exception as e:
                    logger.error(f"Error saving to database: {e}")
                    db_session.rollback()
            
            # Analyze content if requested
            if args.analyze:
                analysis = analyze_content(result['content_text'])
                if analysis:
                    all_analyses.append(analysis)
                    
                    # Save analysis results
                    analysis_path = output_dir / f"{result['domain']}_{int(time.time())}_analysis.json"
                    with open(analysis_path, 'w', encoding='utf-8') as f:
                        json.dump(analysis, f, ensure_ascii=False, indent=2)
                    logger.info(f"Saved analysis to {analysis_path}")
        
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
    
    # Visualize results if requested
    if args.visualize and all_analyses:
        # Combine analyses for visualizations
        combined_analysis = {
            'word_frequency': {},
            'sentiment': [],
            'entities': []
        }
        
        for analysis in all_analyses:
            # Combine word frequencies
            for word, count in analysis.get('word_frequency', {}).items():
                combined_analysis['word_frequency'][word] = combined_analysis['word_frequency'].get(word, 0) + count
            
            # Collect sentiments
            if 'sentiment' in analysis:
                combined_analysis['sentiment'].append(analysis['sentiment'])
            
            # Collect entities
            if 'entities' in analysis:
                combined_analysis['entities'].append(analysis['entities'])
        
        # Create visualizations
        visualize_dir = PROCESSED_DATA_DIR / 'visualizations'
        visualize_dir.mkdir(exist_ok=True)
        visualize_results(combined_analysis, visualize_dir)
    
    logger.info(f"Processed {len(all_results)} URLs")

if __name__ == "__main__":
    main()