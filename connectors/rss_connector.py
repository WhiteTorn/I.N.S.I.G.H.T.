import asyncio
import logging
import html
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from email.utils import parsedate_to_datetime
import feedparser
from .base_connector import BaseConnector

class RssConnector(BaseConnector):
    """
    I.N.S.I.G.H.T. RSS Connector
    
    Handles RSS/Atom feed processing including:
    - Feed parsing and validation
    - Content extraction and cleaning
    - Timestamp normalization
    - Media extraction from enclosures
    - Multi-feed aggregation
    
    This connector follows the unified architecture while providing
    RSS-specific functionality for feed analysis and content retrieval.
    """
    
    def __init__(self):
        """Initialize the RSS connector."""
        super().__init__("rss")
        
        # RSS-specific configuration
        self.timeout = 30  # Feed fetch timeout in seconds
        self.user_agent = "I.N.S.I.G.H.T. Mark II RSS Connector v2.1"
        
        self.logger.info("RSS Connector initialized")
    
    async def connect(self) -> None:
        """
        RSS feeds don't require persistent connections.
        This method validates that feedparser is available.
        """
        try:
            # Test that feedparser is working
            test_feed = feedparser.parse("", agent=self.user_agent)
            self.logger.info("RSS connector ready - feedparser operational")
        except Exception as e:
            self.logger.error(f"RSS connector initialization failed: {e}")
            raise ConnectionError(f"RSS connector setup failed: {e}")
    
    async def disconnect(self) -> None:
        """
        RSS feeds don't require disconnection.
        This method is a no-op for RSS but maintains interface compliance.
        """
        self.logger.info("RSS connector cleanup complete")
    
    def _normalize_timestamp(self, time_struct) -> datetime:
        """
        Convert various RSS timestamp formats to UTC datetime.
        
        Args:
            time_struct: RSS time structure (various formats)
            
        Returns:
            UTC datetime object
        """
        try:
            if hasattr(time_struct, 'tm_year'):
                # It's a time.struct_time
                dt = datetime(*time_struct[:6])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            elif isinstance(time_struct, str):
                # Try to parse string timestamp
                try:
                    return parsedate_to_datetime(time_struct)
                except:
                    # Fallback to current time if parsing fails
                    return datetime.now(timezone.utc)
            else:
                # Fallback to current time
                return datetime.now(timezone.utc)
        except Exception as e:
            self.logger.warning(f"Timestamp normalization failed: {e}")
            return datetime.now(timezone.utc)
    
    def _extract_content(self, entry) -> str:
        """
        Extract the best available content from an RSS entry.
        
        Args:
            entry: RSS entry object
            
        Returns:
            Cleaned text content
        """
        content = ""
        
        # Priority order: content > summary > description > title
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if isinstance(entry.content, list) else entry.content
        elif hasattr(entry, 'summary') and entry.summary:
            content = entry.summary
        elif hasattr(entry, 'description') and entry.description:
            content = entry.description
        elif hasattr(entry, 'title') and entry.title:
            content = entry.title
        
        # Clean HTML and normalize whitespace
        content = html.unescape(content)
        content = re.sub(r'<[^>]+>', '', content)  # Strip HTML tags
        content = re.sub(r'\s+', ' ', content).strip()  # Normalize whitespace
        
        return content
    
    def _extract_media_urls(self, entry) -> List[str]:
        """
        Extract media URLs from RSS entry enclosures and links.
        
        Args:
            entry: RSS entry object
            
        Returns:
            List of media URLs
        """
        media_urls = []
        
        # Extract from enclosures
        if hasattr(entry, 'enclosures'):
            for enclosure in entry.enclosures:
                if hasattr(enclosure, 'href') and enclosure.href:
                    media_urls.append(enclosure.href)
        
        # Extract from media content (some feeds use this)
        if hasattr(entry, 'media_content'):
            for media in entry.media_content:
                if hasattr(media, 'url') and media.url:
                    media_urls.append(media.url)
        
        return media_urls
    
    async def get_feed_info(self, feed_url: str) -> Dict[str, Any]:
        """
        Analyze an RSS feed and return metadata including entry count.
        
        Args:
            feed_url: URL of the RSS feed
            
        Returns:
            Feed information dictionary
        """
        try:
            self.logger.info(f"Analyzing RSS feed: {feed_url}")
            
            # Parse feed asynchronously
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(
                None, 
                lambda: feedparser.parse(feed_url, agent=self.user_agent)
            )
            
            if feed.bozo:
                self.logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
            
            # Extract feed metadata
            feed_info = {
                "url": feed_url,
                "title": getattr(feed.feed, 'title', 'Unknown Feed'),
                "description": getattr(feed.feed, 'description', 'No description available'),
                "link": getattr(feed.feed, 'link', feed_url),
                "language": getattr(feed.feed, 'language', 'Unknown'),
                "total_entries": len(feed.entries),
                "last_updated": getattr(feed.feed, 'updated', 'Unknown'),
                "status": "success"
            }
            
            return feed_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze feed {feed_url}: {e}")
            return {
                "url": feed_url,
                "title": "Error",
                "description": f"Failed to parse feed: {e}",
                "total_entries": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def fetch_posts(self, source_identifier: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch the latest N posts from a single RSS feed.
        
        Args:
            source_identifier: RSS feed URL
            limit: Maximum number of posts to fetch
            
        Returns:
            List of posts in unified format
        """
        feed_url = source_identifier
        self.logger.info(f"Fetching {limit} posts from RSS feed: {feed_url}")
        
        try:
            # Parse feed asynchronously to avoid blocking
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(
                None, 
                lambda: feedparser.parse(feed_url, agent=self.user_agent)
            )
            
            if feed.bozo:
                self.logger.warning(f"Feed parsing warning: {feed.bozo_exception}")
            
            if not feed.entries:
                self.logger.warning(f"No entries found in feed: {feed_url}")
                return []
            
            unified_posts = []
            
            # Process entries up to the limit
            for entry in feed.entries[:limit]:
                try:
                    # Extract and normalize timestamp
                    timestamp = self._normalize_timestamp(
                        getattr(entry, 'published_parsed', None) or 
                        getattr(entry, 'updated_parsed', None)
                    )
                    
                    # Create unified post using base connector helper
                    unified_post = self._create_unified_post(
                        source_platform="rss",
                        source_id=feed_url,
                        post_id=getattr(entry, 'id', getattr(entry, 'link', f"rss_{len(unified_posts)}")),
                        author=getattr(entry, 'author', getattr(feed.feed, 'title', 'Unknown')),
                        content=self._extract_content(entry),
                        timestamp=timestamp,
                        media_urls=self._extract_media_urls(entry),
                        post_url=getattr(entry, 'link', feed_url)
                    )
                    
                    # Add RSS-specific fields for backward compatibility
                    unified_post['title'] = getattr(entry, 'title', 'No title')
                    unified_post['feed_title'] = getattr(feed.feed, 'title', 'Unknown Feed')
                    
                    # Legacy compatibility fields
                    unified_post['id'] = unified_post['post_id']
                    unified_post['date'] = timestamp
                    unified_post['text'] = unified_post['content']
                    unified_post['link'] = unified_post['post_url']
                    
                    unified_posts.append(unified_post)
                    
                except Exception as e:
                    self.logger.error(f"Error processing RSS entry: {e}")
                    continue
            
            self.logger.info(f"Successfully processed {len(unified_posts)} posts from {feed_url}")
            return unified_posts
            
        except Exception as e:
            self.logger.error(f"Failed to fetch RSS feed {feed_url}: {e}")
            return []
    
    async def fetch_posts_by_timeframe(self, sources: List[str], days: int) -> List[Dict[str, Any]]:
        """
        Fetch posts from multiple RSS feeds within a timeframe.
        
        Note: RSS feeds typically don't support date filtering server-side,
        so we fetch all available posts and filter client-side.
        
        Args:
            sources: List of RSS feed URLs
            days: Number of days to look back (0 for all available)
            
        Returns:
            List of posts in unified format, sorted chronologically
        """
        if days == 0:
            self.logger.info("Fetching all available posts from RSS feeds")
            cutoff_date = None
        else:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            self.logger.info(f"Fetching posts from last {days} days from {len(sources)} RSS feeds")
        
        all_posts = []
        
        for feed_url in sources:
            self.logger.info(f"Processing RSS feed: {feed_url}")
            
            try:
                # Fetch all available posts from this feed
                feed_posts = await self.fetch_posts(feed_url, limit=100)  # Reasonable limit
                
                # Filter by timeframe if specified
                if cutoff_date:
                    feed_posts = [
                        post for post in feed_posts 
                        if post['timestamp'] >= cutoff_date
                    ]
                
                all_posts.extend(feed_posts)
                
            except Exception as e:
                self.logger.error(f"Failed to process RSS feed {feed_url}: {e}")
        
        # Sort chronologically
        return sorted(all_posts, key=lambda p: p['timestamp']) 