from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class News(Base):
    """News article database model."""
    
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    headline = Column(String(500), nullable=False, index=True)
    link = Column(Text, nullable=False, unique=True)
    source = Column(String(100), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=func.now(),
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=func.now(),
        onupdate=func.now()
    )
    
    # Add composite indexes for better query performance
    __table_args__ = (
        Index('idx_source_created', 'source', 'created_at'),
        Index('idx_headline_search', 'headline'),
    )
    
    def __repr__(self):
        return f"<News(id={self.id}, headline='{self.headline[:50]}...', source='{self.source}')>"
