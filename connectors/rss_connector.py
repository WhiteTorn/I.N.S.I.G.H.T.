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
    I.N.S.I.G.H.T. RSS Connector v2.3
    
    Handles RSS/Atom feed processing including:
    - Feed parsing and validation
    - Content extraction and cleaning
    - Timestamp normalization
    - Media extraction from enclosures
    - Multi-feed aggregation
    - Category extraction (RSS & Atom)
    - Adaptive feed format handling
    
    This connector follows the unified architecture while providing
    RSS-specific functionality for feed analysis and content retrieval.
    Enhanced in v2.3 with category support and HTML output capabilities.
    """
    
    def __init__(self):
        """Initialize the RSS connector."""
        super().__init__("rss")
        
        # RSS-specific configuration
        self.timeout = 30  # Feed fetch timeout in seconds
        self.user_agent = "I.N.S.I.G.H.T. Mark II RSS Connector v2.3"
        
        self.logger.info("RSS Connector v2.3 initialized with category support")
    
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
    
    def _detect_feed_type(self, feed) -> str:
        """
        Detect whether this is RSS, Atom, or other feed format.
        
        Args:
            feed: Parsed feedparser feed object
            
        Returns:
            Feed type string ("rss", "atom", "unknown")
        """
        if hasattr(feed, 'version'):
            if feed.version and 'atom' in feed.version.lower():
                return "atom"
            elif feed.version and 'rss' in feed.version.lower():
                return "rss"
        
        # Check for Atom-specific elements
        if hasattr(feed.feed, 'id') and hasattr(feed.feed, 'updated'):
            return "atom"
        
        # Default assumption
        return "rss"
    
    def _extract_categories(self, entry, feed_type: str) -> List[str]:
        """
        Extract categories/tags from RSS entry, handling both RSS and Atom formats.
        
        Args:
            entry: RSS/Atom entry object
            feed_type: Type of feed ("rss", "atom", "unknown")
            
        Returns:
            List of category strings
        """
        categories = []
        
        try:
            # Handle Atom categories (like in your example)
            if hasattr(entry, 'tags'):
                for tag in entry.tags:
                    if hasattr(tag, 'term') and tag.term:
                        categories.append(tag.term)
                    elif hasattr(tag, 'label') and tag.label:
                        categories.append(tag.label)
            
            # Handle RSS categories
            elif hasattr(entry, 'category'):
                if isinstance(entry.category, list):
                    categories.extend(entry.category)
                else:
                    categories.append(entry.category)
            
            # Additional category extraction methods for different feed formats
            if hasattr(entry, 'categories'):
                for cat in entry.categories:
                    if isinstance(cat, dict):
                        if 'term' in cat:
                            categories.append(cat['term'])
                        elif 'label' in cat:
                            categories.append(cat['label'])
                    else:
                        categories.append(str(cat))
        
        except Exception as e:
            self.logger.warning(f"Error extracting categories: {e}")
        
        # Clean and deduplicate categories
        categories = [cat.strip() for cat in categories if cat and cat.strip()]
        return list(set(categories))  # Remove duplicates
    
    def _normalize_timestamp(self, time_struct) -> datetime:
        """
        Convert various RSS timestamp formats to UTC datetime.
        Enhanced for Atom feed compatibility.
        
        Args:
            time_struct: RSS/Atom time structure (various formats)
            
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
                # Try to parse string timestamp (common in Atom feeds)
                try:
                    return parsedate_to_datetime(time_struct)
                except:
                    # Try ISO format parsing for Atom feeds
                    try:
                        # Handle formats like "2025-06-13T13:26:43+00:00"
                        return datetime.fromisoformat(time_struct.replace('Z', '+00:00'))
                    except:
                        # Fallback to current time if parsing fails
                        return datetime.now(timezone.utc)
            else:
                # Fallback to current time
                return datetime.now(timezone.utc)
        except Exception as e:
            self.logger.warning(f"Timestamp normalization failed: {e}")
            return datetime.now(timezone.utc)
    
    def _extract_content(self, entry, feed_type: str) -> tuple[str, str]:
        """
        Extract both cleaned text and original HTML content from an RSS/Atom entry.
        
        Args:
            entry: RSS/Atom entry object
            feed_type: Type of feed for format-specific handling
            
        Returns:
            Tuple of (cleaned_text, original_html)
        """
        content_html = ""
        
        # Priority order varies by feed type
        if feed_type == "atom":
            # Atom feeds often have richer content structure
            if hasattr(entry, 'content') and entry.content:
                if isinstance(entry.content, list):
                    # Take the first content entry, preferably HTML
                    for content_item in entry.content:
                        if hasattr(content_item, 'type') and content_item.type == 'html':
                            content_html = content_item.value
                            break
                        elif hasattr(content_item, 'value'):
                            content_html = content_item.value
                    if not content_html and entry.content:
                        content_html = entry.content[0].value if hasattr(entry.content[0], 'value') else str(entry.content[0])
                else:
                    content_html = entry.content
            elif hasattr(entry, 'summary') and entry.summary:
                content_html = entry.summary
        else:
            # RSS feeds - use existing logic
            if hasattr(entry, 'content') and entry.content:
                content_html = entry.content[0].value if isinstance(entry.content, list) else entry.content
            elif hasattr(entry, 'summary') and entry.summary:
                content_html = entry.summary
            elif hasattr(entry, 'description') and entry.description:
                content_html = entry.description
        
        # Fallback to title if no content found
        if not content_html and hasattr(entry, 'title') and entry.title:
            content_html = entry.title
        
        # Ensure we have content
        content_html = content_html or ""
        
        # Unescape HTML entities for both versions
        content_html = html.unescape(content_html)
        
        # Create cleaned text version for console
        cleaned_text = re.sub(r'<[^>]+>', '', content_html)  # Strip HTML tags
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()  # Normalize whitespace
        
        return cleaned_text, content_html
    
    def _extract_media_urls(self, entry) -> List[str]:
        """
        Extract media URLs from RSS entry enclosures and links.
        Enhanced for Atom feed support.
        
        Args:
            entry: RSS/Atom entry object
            
        Returns:
            List of media URLs
        """
        media_urls = []
        
        # Extract from enclosures (RSS style)
        if hasattr(entry, 'enclosures'):
            for enclosure in entry.enclosures:
                if hasattr(enclosure, 'href') and enclosure.href:
                    media_urls.append(enclosure.href)
        
        # Extract from media content (some feeds use this)
        if hasattr(entry, 'media_content'):
            for media in entry.media_content:
                if hasattr(media, 'url') and media.url:
                    media_urls.append(media.url)
        
        # Extract from links (Atom style)
        if hasattr(entry, 'links'):
            for link in entry.links:
                if hasattr(link, 'type') and link.type and 'image' in link.type.lower():
                    if hasattr(link, 'href') and link.href:
                        media_urls.append(link.href)
        
        return media_urls
    
    async def get_feed_info(self, feed_url: str) -> Dict[str, Any]:
        """
        Analyze an RSS/Atom feed and return metadata including entry count.
        Enhanced with feed type detection and category analysis.
        
        Args:
            feed_url: URL of the RSS/Atom feed
            
        Returns:
            Feed information dictionary
        """
        try:
            self.logger.info(f"Analyzing RSS/Atom feed: {feed_url}")
            
            # Parse feed asynchronously
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(
                None, 
                lambda: feedparser.parse(feed_url, agent=self.user_agent)
            )
            
            if feed.bozo:
                self.logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
            
            # Detect feed type
            feed_type = self._detect_feed_type(feed)
            
            # Analyze categories across all entries
            all_categories = set()
            for entry in feed.entries[:10]:  # Sample first 10 entries for category analysis
                categories = self._extract_categories(entry, feed_type)
                all_categories.update(categories)
            
            # Extract feed metadata
            feed_info = {
                "url": feed_url,
                "title": getattr(feed.feed, 'title', 'Unknown Feed'),
                "description": getattr(feed.feed, 'description', 'No description available'),
                "link": getattr(feed.feed, 'link', feed_url),
                "language": getattr(feed.feed, 'language', 'Unknown'),
                "total_entries": len(feed.entries),
                "last_updated": getattr(feed.feed, 'updated', 'Unknown'),
                "feed_type": feed_type,
                "common_categories": sorted(list(all_categories)),
                "category_count": len(all_categories),
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
                "feed_type": "unknown",
                "common_categories": [],
                "category_count": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def fetch_posts(self, source_identifier: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch the latest N posts from a single RSS/Atom feed.
        Enhanced with category extraction and adaptive feed handling.
        
        Args:
            source_identifier: RSS/Atom feed URL
            limit: Maximum number of posts to fetch
            
        Returns:
            List of posts in unified format with categories
        """
        feed_url = source_identifier
        self.logger.info(f"Fetching {limit} posts from RSS/Atom feed: {feed_url}")
        
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
            
            # Detect feed type for adaptive processing
            feed_type = self._detect_feed_type(feed)
            self.logger.info(f"Detected feed type: {feed_type}")
            
            unified_posts = []
            
            # Process entries up to the limit
            for entry in feed.entries[:limit]:
                try:
                    # Extract categories
                    categories = self._extract_categories(entry, feed_type)
                    
                    # Extract both cleaned text and original HTML
                    cleaned_text, original_html = self._extract_content(entry, feed_type)
                    
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
                        content=cleaned_text,  # Use cleaned text for console display
                        timestamp=timestamp,
                        media_urls=self._extract_media_urls(entry),
                        post_url=getattr(entry, 'link', feed_url)
                    )
                    
                    # Add RSS/Atom-specific fields for backward compatibility
                    unified_post['title'] = getattr(entry, 'title', 'No title')
                    unified_post['feed_title'] = getattr(feed.feed, 'title', 'Unknown Feed')
                    unified_post['feed_type'] = feed_type
                    unified_post['categories'] = categories  # NEW: Category support
                    unified_post['content_html'] = original_html  # NEW: Original HTML for rich rendering
                    
                    # Legacy compatibility fields
                    unified_post['id'] = unified_post['post_id']
                    unified_post['date'] = timestamp
                    unified_post['text'] = unified_post['content']  # Cleaned text for console
                    unified_post['link'] = unified_post['post_url']
                    
                    unified_posts.append(unified_post)
                    
                except Exception as e:
                    self.logger.error(f"Error processing RSS entry: {e}")
                    continue
            
            self.logger.info(f"Successfully processed {len(unified_posts)} posts from {feed_url} ({feed_type})")
            return unified_posts
            
        except Exception as e:
            self.logger.error(f"Failed to fetch RSS/Atom feed {feed_url}: {e}")
            return []
    
    async def fetch_posts_by_timeframe(self, sources: List[str], days: int) -> List[Dict[str, Any]]:
        """
        Fetch posts from multiple RSS/Atom feeds within a timeframe.
        Enhanced with category aggregation across sources.
        
        Note: RSS feeds typically don't support date filtering server-side,
        so we fetch all available posts and filter client-side.
        
        Args:
            sources: List of RSS/Atom feed URLs
            days: Number of days to look back (0 for all available)
            
        Returns:
            List of posts in unified format, sorted chronologically
        """
        if days == 0:
            self.logger.info("Fetching all available posts from RSS/Atom feeds")
            cutoff_date = None
        else:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            self.logger.info(f"Fetching posts from last {days} days from {len(sources)} RSS/Atom feeds")
        
        all_posts = []
        
        for feed_url in sources:
            self.logger.info(f"Processing RSS/Atom feed: {feed_url}")
            
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
                self.logger.error(f"Failed to process RSS/Atom feed {feed_url}: {e}")
        
        # Sort chronologically
        return sorted(all_posts, key=lambda p: p['timestamp']) 