import random
import time
import logging
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from ..config import USER_AGENT, REQUEST_TIMEOUT, RETRY_COUNT, DELAY_BETWEEN_REQUESTS, USE_PROXY, PROXY_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_random_user_agent():
    """Return a random user agent from a predefined list."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
    return random.choice(user_agents)

def get_session():
    """Create and return a requests session with appropriate headers and proxies."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',  # Do Not Track
    })
    
    if USE_PROXY and PROXY_URL:
        session.proxies = {
            'http': PROXY_URL,
            'https': PROXY_URL
        }
        
    return session

def fetch_url(url, session=None, retry=RETRY_COUNT):
    """
    Fetch content from URL with retry logic and rate limiting.
    
    Args:
        url (str): URL to fetch
        session (requests.Session, optional): Session to use
        retry (int): Number of retries
        
    Returns:
        str: HTML content if successful, None otherwise
    """
    if session is None:
        session = get_session()
        
    # Add jitter to delay to avoid detection
    delay = DELAY_BETWEEN_REQUESTS * (0.5 + random.random())
    time.sleep(delay)
    
    try:
        logger.info(f"Fetching URL: {url}")
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        if retry > 0:
            logger.info(f"Retrying... ({retry} attempts left)")
            time.sleep(delay * 2)  # Increase delay for retry
            return fetch_url(url, session, retry - 1)
        return None

def parse_html(html, parser='html.parser'):
    """Parse HTML content with BeautifulSoup."""
    return BeautifulSoup(html, parser)

def extract_domain(url):
    """Extract domain from URL."""
    parsed_url = urlparse(url)
    return parsed_url.netloc

def is_valid_url(url):
    """Check if URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False