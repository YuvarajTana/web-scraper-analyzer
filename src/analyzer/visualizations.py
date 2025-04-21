import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import logging
from pathlib import Path
from ..config import PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)

class Visualizer:
    """Class for data visualization methods."""
    
    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir) if output_dir else PROCESSED_DATA_DIR
        self.output_dir.mkdir(exist_ok=True)
        
        # Set styling
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        
    def save_or_show(self, plt, filename=None):
        """Save figure to file or show it."""
        if filename:
            filepath = self.output_dir / filename
            plt.savefig(filepath, bbox_inches='tight', dpi=300)
            logger.info(f"Saved figure to {filepath}")
            plt.close()
        else:
            plt.tight_layout()
            plt.show()
    
    def plot_word_frequency(self, word_freq, top_n=20, title="Word Frequency", filename=None):
        """
        Plot word frequency bar chart.
        
        Args:
            word_freq (dict or list): Word frequency dictionary or list of (word, count) tuples
            top_n (int): Number of top words to show
            title (str): Plot title
            filename (str, optional): If provided, save to this filename
        """
        if isinstance(word_freq, dict):
            # Convert dict to sorted list of tuples
            word_freq = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
        # Take only top N
        word_freq = word_freq[:top_n]
        
        # Convert to DataFrame for plotting
        df = pd.DataFrame(word_freq, columns=['Word', 'Frequency'])
        
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(x='Frequency', y='Word', data=df, palette='viridis')
        
        # Add value labels
        for i, v in enumerate(df['Frequency']):
            ax.text(v + 0.1, i, str(v), va='center')
            
        plt.title(title, fontsize=16)
        plt.xlabel('Frequency', fontsize=12)
        plt.ylabel('Word', fontsize=12)
        
        self.save_or_show(plt, filename)
        
    def generate_wordcloud(self, text_or_freq, title="Word Cloud", filename=None, 
                          width=800, height=400, max_words=200):
        """
        Generate a word cloud visualization.
        
        Args:
            text_or_freq: Either text string or word frequency dictionary
            title (str): Plot title
            filename (str, optional): If provided, save to this filename
        """
        plt.figure(figsize=(12, 8))
        
        if isinstance(text_or_freq, str):
            wordcloud = WordCloud(width=width, height=height, max_words=max_words, 
                                background_color='white', collocations=False).generate(text_or_freq)
        else:
            wordcloud = WordCloud(width=width, height=height, max_words=max_words, 
                                background_color='white').generate_from_frequencies(text_or_freq)
        
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=16)
        
        self.save_or_show(plt, filename)
        
    def plot_sentiment_distribution(self, sentiment_data, title="Sentiment Distribution", filename=None):
        """
        Plot sentiment distribution.
        
        Args:
            sentiment_data (list): List of sentiment dictionaries with 'polarity' and 'subjectivity'
            title (str): Plot title
            filename (str, optional): If provided, save to this filename
        """
        df = pd.DataFrame(sentiment_data)
        
        plt.figure(figsize=(12, 8))
        
        plt.subplot(1, 2, 1)
        sns.histplot(df['polarity'], kde=True, bins=20)
        plt.title('Polarity Distribution')
        plt.xlabel('Polarity (-1 to 1)')
        plt.ylabel('Frequency')
        
        plt.subplot(1, 2, 2)
        sns.histplot(df['subjectivity'], kde=True, bins=20)
        plt.title('Subjectivity Distribution')
        plt.xlabel('Subjectivity (0 to 1)')
        plt.ylabel('Frequency')
        
        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        
        self.save_or_show(plt, filename)
        
    def plot_entity_counts(self, entities_list, top_n=10, title="Named Entity Counts", filename=None):
        """
        Plot entity type counts from multiple documents.
        
        Args:
            entities_list (list): List of entity dictionaries from multiple documents
            top_n (int): Number of top entity types to show
            title (str): Plot title
            filename (str, optional): If provided, save to this filename
        """
        # Combine all entity dictionaries
        all_entities = {}
        for entities in entities_list:
            for ent_type, ent_list in entities.items():
                if ent_type not in all_entities:
                    all_entities[ent_type] = 0
                all_entities[ent_type] += len(ent_list)
                
        # Convert to DataFrame and sort
        df = pd.DataFrame({'Entity Type': list(all_entities.keys()),
                          'Count': list(all_entities.values())})
        df = df.sort_values('Count', ascending=False).head(top_n)
        
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(x='Count', y='Entity Type', data=df, palette='Blues_d')
        
        # Add value labels
        for i, v in enumerate(df['Count']):
            ax.text(v + 0.1, i, str(v), va='center')
            
        plt.title(title, fontsize=16)
        plt.xlabel('Count', fontsize=12)
        plt.ylabel('Entity Type', fontsize=12)
        
        self.save_or_show(plt, filename)