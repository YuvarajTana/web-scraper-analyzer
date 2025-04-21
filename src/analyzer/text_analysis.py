import re
import string
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from collections import Counter
import logging

logger = logging.getLogger(__name__)

# Download necessary NLTK datasets
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class TextAnalyzer:
    """Class for text analysis functions."""
    
    def __init__(self, text, language='english'):
        self.text = text
        self.language = language
        self.stop_words = set(stopwords.words(language)) if language in stopwords._fileids else set()
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        
    def preprocess(self, lowercase=True, remove_punctuation=True, remove_stopwords=True):
        """Preprocess text for analysis."""
        text = self.text
        
        # Convert to lowercase
        if lowercase:
            text = text.lower()
            
        # Remove punctuation
        if remove_punctuation:
            text = text.translate(str.maketrans('', '', string.punctuation))
            
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        if remove_stopwords:
            tokens = [token for token in tokens if token not in self.stop_words]
            
        return tokens
    
    def get_word_frequency(self, top_n=None, min_word_length=3):
        """Get word frequency distribution."""
        tokens = self.preprocess()
        # Filter words by minimum length
        tokens = [token for token in tokens if len(token) >= min_word_length]
        # Get frequency distribution
        freq_dist = Counter(tokens)
        
        # Return top N if specified
        if top_n:
            return freq_dist.most_common(top_n)
        return freq_dist
    
    def get_sentences(self):
        """Get sentences from text."""
        return sent_tokenize(self.text)
    
    def get_sentiment(self):
        """Basic sentiment analysis using TextBlob."""
        try:
            from textblob import TextBlob
            blob = TextBlob(self.text)
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except ImportError:
            logger.warning("TextBlob not available. Install with 'pip install textblob'")
            return {'polarity': 0, 'subjectivity': 0}
    
    def extract_entities(self):
        """Extract named entities using spaCy if available."""
        try:
            import spacy
            try:
                nlp = spacy.load('en_core_web_sm')
            except OSError:
                logger.warning("Downloading spaCy model. This may take a moment...")
                from spacy.cli import download
                download('en_core_web_sm')
                nlp = spacy.load('en_core_web_sm')
                
            doc = nlp(self.text)
            entities = {}
            
            for ent in doc.ents:
                entity_type = ent.label_
                if entity_type not in entities:
                    entities[entity_type] = []
                entities[entity_type].append(ent.text)
                
            return entities
        except ImportError:
            logger.warning("spaCy not available. Install with 'pip install spacy' and 'python -m spacy download en_core_web_sm'")
            return {}
    
    def get_readability_scores(self):
        """Calculate readability scores."""
        try:
            import textstat
            return {
                'flesch_reading_ease': textstat.flesch_reading_ease(self.text),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(self.text),
                'smog_index': textstat.smog_index(self.text),
                'coleman_liau_index': textstat.coleman_liau_index(self.text),
                'automated_readability_index': textstat.automated_readability_index(self.text),
            }
        except ImportError:
            logger.warning("textstat not available. Install with 'pip install textstat'")
            return {}