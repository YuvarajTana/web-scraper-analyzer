from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
from ..config import DB_CONNECTION_STRING

Base = declarative_base()

class Website(Base):
    """Website model representing a scraped website."""
    __tablename__ = 'websites'
    
    id = Column(Integer, primary_key=True)
    domain = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    root_url = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_scraped_at = Column(DateTime)
    
    pages = relationship("Page", back_populates="website")
    
    def __repr__(self):
        return f"<Website {self.domain}>"

class Page(Base):
    """Page model representing a scraped web page."""
    __tablename__ = 'pages'
    
    id = Column(Integer, primary_key=True)
    website_id = Column(Integer, ForeignKey('websites.id'), nullable=False)
    url = Column(String(1024), unique=True, nullable=False)
    title = Column(String(512))
    meta_description = Column(Text)
    content_text = Column(Text)
    content_html = Column(Text)
    author = Column(String(255))
    published_date = Column(String(255))
    scraped_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)
    
    website = relationship("Website", back_populates="pages")
    
    def __repr__(self):
        return f"<Page {self.url}>"

def init_db():
    """Initialize the database by creating all tables."""
    engine = create_engine(DB_CONNECTION_STRING)
    Base.metadata.create_all(engine)