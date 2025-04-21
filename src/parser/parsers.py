import re
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class BaseParser:
    """Base parser class with common parsing methods."""
    
    def __init__(self, html_content, url=''):
        self.html = html_content
        self.url = url
        self.soup = BeautifulSoup(html_content, 'html.parser') if html_content else None
        
    def get_title(self):
        """Extract page title."""
        if not self.soup:
            return None
        title_tag = self.soup.find('title')
        return title_tag.text.strip() if title_tag else None
    
    def get_meta_description(self):
        """Extract meta description."""
        if not self.soup:
            return None
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else None
    
    def get_main_content(self):
        """Extract main content (basic implementation)."""
        if not self.soup:
            return None
        # Try to find main content containers
        main_containers = self.soup.find_all(['article', 'main', 'div'], 
                                           attrs={'class': re.compile('(content|article|post|main)', re.I)})
        
        if main_containers:
            # Find the largest content block by text length
            main_content = max(main_containers, key=lambda x: len(x.get_text(strip=True)))
            return main_content.get_text(separator=' ', strip=True)
        
        # Fallback to body text
        body = self.soup.find('body')
        return body.get_text(separator=' ', strip=True) if body else None
    
    def get_all_links(self):
        """Extract all links from the page."""
        if not self.soup:
            return []
        return [a.get('href') for a in self.soup.find_all('a', href=True)]
    
    def get_images(self):
        """Extract all images from the page."""
        if not self.soup:
            return []
        return [img.get('src') for img in self.soup.find_all('img', src=True)]
    
    def get_clean_text(self):
        """Get clean text content without scripts, styles, etc."""
        if not self.soup:
            return ""
            
        # Remove unwanted elements
        for element in self.soup(['script', 'style', 'head', 'header', 'footer', 'nav']):
            element.decompose()
            
        text = self.soup.get_text(separator=' ', strip=True)
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class ArticleParser(BaseParser):
    """Parser specialized for article content."""
    
    def get_author(self):
        """Extract article author."""
        if not self.soup:
            return None
            
        # Try various common author patterns
        author_patterns = [
            {'attrs': {'class': re.compile('(author|byline)', re.I)}},
            {'attrs': {'rel': 'author'}},
            {'itemprop': 'author'},
            {'name': re.compile('author', re.I)}
        ]
        
        for pattern in author_patterns:
            author_tag = self.soup.find(['a', 'span', 'div', 'p'], **pattern)
            if author_tag:
                return author_tag.get_text(strip=True)
                
        return None
    
    def get_publish_date(self):
        """Extract article publish date."""
        if not self.soup:
            return None
            
        # Try to find date in meta tags
        meta_date = self.soup.find('meta', attrs={
            'property': ['article:published_time', 'og:published_time']
        })
        if meta_date:
            return meta_date.get('content')
            
        # Look for time tags
        time_tag = self.soup.find('time')
        if time_tag and time_tag.has_attr('datetime'):
            return time_tag['datetime']
            
        # Look for date in common format classes
        date_tag = self.soup.find(['span', 'div', 'p'], attrs={
            'class': re.compile('(date|time|publish)', re.I)
        })
        if date_tag:
            return date_tag.get_text(strip=True)
            
        return None