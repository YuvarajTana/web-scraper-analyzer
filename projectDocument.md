# Web Scraper and Analyzer

A Python project for scraping web content and performing text analysis on the scraped data. This tool can extract content from websites, analyze the text, generate visualizations, and store the results in a database.

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command Line Options](#command-line-options)
  - [Examples](#examples)
- [Technical Details](#technical-details)
  - [Scraping Module](#scraping-module)
  - [Parser Module](#parser-module)
  - [Analyzer Module](#analyzer-module)
  - [Database Module](#database-module)
- [Visualizations](#visualizations)
- [Extending the Project](#extending-the-project)

## Features

- **Web scraping** with request throttling and retry logic
- **HTML parsing** and content extraction with sophisticated fallback mechanisms
- **Text analysis** including:
  - Word frequency analysis
  - Sentiment analysis
  - Named entity recognition
  - Readability scoring
- **Database storage** for scraped content
- **Data visualization** including:
  - Word frequency charts
  - Word clouds
  - Sentiment distributions
  - Entity visualizations
- **Support for multiple scraping strategies**
- **Rate limiting** to avoid overloading servers
- **Proxy support** for handling IP restrictions

## Project Structure

```
web-scraper-analyzer/
├── data/                     # Storage for scraped and processed data
│   ├── raw/                  # Raw scraped content
│   └── processed/            # Processed data and visualizations
├── src/                      # Source code
│   ├── analyzer/             # Text analysis and visualization
│   │   ├── text_analysis.py  # Text analysis methods
│   │   └── visualizations.py # Visualization methods
│   ├── config.py             # Configuration settings
│   ├── database/             # Database models and operations
│   │   └── models.py         # SQLAlchemy ORM models
│   ├── parser/               # HTML parsing
│   │   └── parsers.py        # Content extraction logic
│   └── scrapper/             # Web scraping
│       └── utils.py          # Scraping utilities
├── tests/                    # Test suite
├── main.py                   # Command-line interface
├── requirements.txt          # Project dependencies
└── scrapy.cfg                # Scrapy configuration (for extended scraping)
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/web-scraper-analyzer.git
   cd web-scraper-analyzer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv webscraper-env
   source webscraper-env/bin/activate  # On Windows: webscraper-env\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Optional: Download additional language resources:
   ```bash
   python -m spacy download en_core_web_sm
   python -m nltk.downloader punkt stopwords wordnet
   ```

## Configuration

The project uses a configuration file (`src/config.py`) for various settings:

- **Project directories**: Base directories for raw and processed data
- **Scraping configurations**: User agents, timeout, retry count, robots.txt respect
- **Rate limiting**: Requests per minute, delay between requests
- **Database settings**: Database type and connection string
- **Proxy settings**: Proxy URL and usage flag

You can also use environment variables to override these settings by creating a `.env` file in the project root.

Example `.env` file:
```
DB_TYPE=sqlite
DB_CONNECTION_STRING=sqlite:///data/scraped_data.db
USE_PROXY=False
PROXY_URL=
LOG_LEVEL=INFO
```

## Usage

The primary interface is through the command-line tool in `main.py`.

### Command Line Options

```
python main.py [URL] [OPTIONS]
```

Options:
- `URL`: The URL to scrape (required unless `--urls-file` is provided)
- `--urls-file FILE`: File containing URLs to scrape (one per line)
- `--output-dir DIR`: Directory to save output files (default: data/raw)
- `--analyze`: Analyze scraped content
- `--visualize`: Create visualizations from analysis
- `--save-to-db`: Save scraped data to the database

### Examples

1. Scrape a single URL and analyze the content:
   ```bash
   python main.py https://example.com --analyze
   ```

2. Scrape multiple URLs from a file and generate visualizations:
   ```bash
   python main.py --urls-file urls.txt --analyze --visualize
   ```

3. Scrape, analyze, visualize, and save to the database:
   ```bash
   python main.py https://example.com --analyze --visualize --save-to-db
   ```

## Technical Details

### Scraping Module

The scraping module (`src/scrapper/utils.py`) handles:
- Fetching content with retry logic
- Rate limiting to avoid detection
- User agent rotation
- Proxy support for bypassing IP restrictions

Core functions:
- `fetch_url()`: Retrieves HTML content with retry logic and rate limiting
- `get_random_user_agent()`: Rotates between different user agents
- `extract_domain()`: Extracts the domain from a URL

### Parser Module

The parser module (`src/parser/parsers.py`) extracts structured content:
- `BaseParser`: Common parsing methods for HTML content
- `ArticleParser`: Specialized for extracting article content

Key features:
- Extract title, meta description, main content
- Clean HTML content to plain text
- Extract article metadata (author, publish date)
- Find all links and images

### Analyzer Module

The text analysis module (`src/analyzer/text_analysis.py`) offers:
- Word frequency analysis
- Sentence extraction and analysis
- Sentiment analysis using TextBlob
- Named entity recognition using spaCy
- Readability scoring

The visualization module (`src/analyzer/visualizations.py`) provides:
- Word frequency bar charts
- Word cloud generation
- Sentiment distribution visualization
- Entity count visualization

### Database Module

The database module (`src/database/models.py`) defines:
- SQLAlchemy ORM models for storage
- Website model for tracking domains
- Page model for storing individual page content and metadata

## Visualizations

The project generates multiple types of visualizations:

1. **Word Frequency Charts**: Bar charts showing most common words
2. **Word Clouds**: Visual representation of text with word size corresponding to frequency
3. **Sentiment Distribution**: Histograms of polarity and subjectivity scores
4. **Entity Visualizations**: Bar charts of named entity types found in the text

All visualizations are saved to the `data/processed/visualizations` directory by default.

## Extending the Project

### Adding New Parsers

1. Create a new parser class in `src/parser/parsers.py` that inherits from `BaseParser`
2. Implement specialized extraction methods for your content type
3. Use your new parser in the main script

Example:
```python
class ProductParser(BaseParser):
    def get_price(self):
        # Implementation to extract product price
        pass
        
    def get_availability(self):
        # Implementation to extract availability
        pass
```

### Adding New Analysis Methods

1. Add new methods to the `TextAnalyzer` class in `src/analyzer/text_analysis.py`
2. Add corresponding visualization methods in `src/analyzer/visualizations.py`
3. Update the main script to use your new analysis methods

### Adding New Database Models

1. Define new models in `src/database/models.py`
2. Update the database initialization and query logic in the main script