import asyncio
import html
import re
import urllib.error
import socket
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from email.utils import parsedate_to_datetime
import feedparser
from .base_connector import BaseConnector

class RssConnector(BaseConnector):
    """
    I.N.S.I.G.H.T. RSS Connector v2.3 - The Citadel
    
    Handles RSS/Atom feed processing including:
    - Feed parsing and validation
    - Content extraction and cleaning
    - Timestamp normalization
    - Media extraction from enclosures
    - Multi-feed aggregation
    - Category extraction (RSS & Atom)
    - Adaptive feed format handling
    - ENHANCED: Comprehensive error handling and resilience
    
    This connector follows the unified architecture while providing
    RSS-specific functionality for feed analysis and content retrieval.
    Hardened in v2.3 with bulletproof error handling.
    """
    
    def __init__(self):
        """Initialize the RSS connector."""
        super().__init__("rss")
        
        # RSS-specific configuration
        self.timeout = 30  # Feed fetch timeout in seconds
        self.user_agent = "I.N.S.I.G.H.T. Mark II RSS Connector v2.3 - The Citadel"
        
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
        HARDENED: Comprehensive error handling for network and parsing failures.
        
        Args:
            feed_url: URL of the RSS/Atom feed
            
        Returns:
            Feed information dictionary
        """
        self.logger.info(f"Analyzing RSS/Atom feed: {feed_url}")
        
        try:
            # Parse feed asynchronously with comprehensive error handling
            loop = asyncio.get_event_loop()
            
            # Wrap the feedparser call with timeout and error handling
            try:
                feed = await asyncio.wait_for(
                    loop.run_in_executor(
                        None, 
                        lambda: feedparser.parse(feed_url, agent=self.user_agent)
                    ),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                error_msg = f"Feed analysis timed out after {self.timeout}s"
                self.logger.error(f"ERROR: Failed to analyze RSS feed from {feed_url} - Reason: {error_msg}")
                return self._create_error_response(feed_url, error_msg)
            except Exception as e:
                error_msg = f"Network or parsing error: {str(e)}"
                self.logger.error(f"ERROR: Failed to analyze RSS feed from {feed_url} - Reason: {error_msg}")
                return self._create_error_response(feed_url, error_msg)
            
            # Check for feed parsing errors
            if hasattr(feed, 'bozo') and feed.bozo:
                if hasattr(feed, 'bozo_exception') and feed.bozo_exception:
                    bozo_error = str(feed.bozo_exception)
                    self.logger.warning(f"Feed parsing warning for {feed_url}: {bozo_error}")
                    
                    # For severe parsing errors, treat as failure
                    if any(severe_error in bozo_error.lower() for severe_error in ['not found', '404', '403', '500']):
                        self.logger.error(f"ERROR: Failed to analyze RSS feed from {feed_url} - Reason: {bozo_error}")
                        return self._create_error_response(feed_url, f"Feed parsing failed: {bozo_error}")
            
            # Check if feed has any usable content
            if not hasattr(feed, 'feed') or not hasattr(feed, 'entries'):
                error_msg = "Feed contains no parseable content"
                self.logger.error(f"ERROR: Failed to analyze RSS feed from {feed_url} - Reason: {error_msg}")
                return self._create_error_response(feed_url, error_msg)
            
            # Detect feed type
            feed_type = self._detect_feed_type(feed)
            
            # Analyze categories across all entries (with error handling)
            all_categories = set()
            try:
                for entry in feed.entries[:10]:  # Sample first 10 entries for category analysis
                    try:
                        categories = self._extract_categories(entry, feed_type)
                        all_categories.update(categories)
                    except Exception as e:
                        self.logger.warning(f"Error extracting categories from entry: {e}")
                        continue
            except Exception as e:
                self.logger.warning(f"Error during category analysis: {e}")
            
            # Extract feed metadata with safe attribute access
            try:
                feed_info = {
                    "url": feed_url,
                    "title": getattr(feed.feed, 'title', 'Unknown Feed'),
                    "description": getattr(feed.feed, 'description', 'No description available'),
                    "link": getattr(feed.feed, 'link', feed_url),
                    "language": getattr(feed.feed, 'language', 'Unknown'),
                    "total_entries": len(feed.entries) if hasattr(feed, 'entries') else 0,
                    "last_updated": getattr(feed.feed, 'updated', 'Unknown'),
                    "feed_type": feed_type,
                    "common_categories": sorted(list(all_categories)),
                    "category_count": len(all_categories),
                    "status": "success"
                }
                
                self.logger.info(f"Successfully analyzed feed {feed_url}: {feed_info['total_entries']} entries, type: {feed_type}")
                return feed_info
                
            except Exception as e:
                error_msg = f"Error extracting feed metadata: {str(e)}"
                self.logger.error(f"ERROR: Failed to analyze RSS feed from {feed_url} - Reason: {error_msg}")
                return self._create_error_response(feed_url, error_msg)
                
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP {e.code}: {e.reason}"
            self.logger.error(f"ERROR: Failed to analyze RSS feed from {feed_url} - Reason: {error_msg}")
            return self._create_error_response(feed_url, error_msg)
            
        except urllib.error.URLError as e:
            error_msg = f"Network error: {str(e.reason)}"
            self.logger.error(f"ERROR: Failed to analyze RSS feed from {feed_url} - Reason: {error_msg}")
            return self._create_error_response(feed_url, error_msg)
            
        except socket.timeout:
            error_msg = f"Connection timed out"
            self.logger.error(f"ERROR: Failed to analyze RSS feed from {feed_url} - Reason: {error_msg}")
            return self._create_error_response(feed_url, error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"ERROR: Failed to analyze RSS feed from {feed_url} - Reason: {error_msg}")
            return self._create_error_response(feed_url, error_msg)
    
    def _create_error_response(self, feed_url: str, error_message: str) -> Dict[str, Any]:
        """Create a standardized error response for feed analysis failures."""
        return {
            "url": feed_url,
            "title": "Error",
            "description": f"Failed to parse feed: {error_message}",
            "link": feed_url,
            "language": "Unknown",
            "total_entries": 0,
            "last_updated": "Unknown",
            "feed_type": "unknown",
            "common_categories": [],
            "category_count": 0,
            "status": "error",
            "error": error_message
        }
    
    async def fetch_posts(self, source_identifier: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch the latest N posts from a single RSS/Atom feed.
        Enhanced with category extraction and adaptive feed handling.
        HARDENED: Bulletproof error handling for all failure scenarios.
        
        Args:
            source_identifier: RSS/Atom feed URL
            limit: Maximum number of posts to fetch
            
        Returns:
            List of posts in unified format with categories, empty list on failure
        """
        feed_url = source_identifier
        self.logger.info(f"Fetching {limit} posts from RSS/Atom feed: {feed_url}")
        
        try:
            # Parse feed asynchronously with comprehensive error handling
            loop = asyncio.get_event_loop()
            
            try:
                feed = await asyncio.wait_for(
                    loop.run_in_executor(
                        None, 
                        lambda: feedparser.parse(feed_url, agent=self.user_agent)
                    ),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                self.logger.error(f"ERROR: Failed to fetch RSS feed from {feed_url} - Reason: Timeout after {self.timeout}s")
                return []
            except Exception as e:
                self.logger.error(f"ERROR: Failed to fetch RSS feed from {feed_url} - Reason: Network/parsing error: {str(e)}")
                return []
            
            # Check for critical parsing errors
            if hasattr(feed, 'bozo') and feed.bozo:
                if hasattr(feed, 'bozo_exception') and feed.bozo_exception:
                    bozo_error = str(feed.bozo_exception)
                    self.logger.warning(f"Feed parsing warning for {feed_url}: {bozo_error}")
                    
                    # For severe parsing errors, fail gracefully
                    if any(severe_error in bozo_error.lower() for severe_error in ['not found', '404', '403', '500', 'connection']):
                        self.logger.error(f"ERROR: Failed to fetch RSS feed from {feed_url} - Reason: {bozo_error}")
                        return []
            
            # Validate feed structure
            if not hasattr(feed, 'entries'):
                self.logger.error(f"ERROR: Failed to fetch RSS feed from {feed_url} - Reason: Invalid feed structure, no entries found")
                return []
            
            if not feed.entries:
                self.logger.warning(f"No entries found in feed: {feed_url}")
                return []
            
            # Detect feed type for adaptive processing
            try:
                feed_type = self._detect_feed_type(feed)
                self.logger.info(f"Detected feed type: {feed_type}")
            except Exception as e:
                self.logger.warning(f"Error detecting feed type: {e}, defaulting to 'rss'")
                feed_type = 'rss'
            
            unified_posts = []
            
            # Process entries up to the limit with individual error handling
            entries_processed = 0
            for entry in feed.entries:
                if entries_processed >= limit:
                    break
                    
                try:
                    # Extract categories with error handling
                    try:
                        categories = self._extract_categories(entry, feed_type)
                    except Exception as e:
                        self.logger.warning(f"Error extracting categories from entry: {e}")
                        categories = []
                    
                    # Extract both cleaned text and original HTML with error handling
                    try:
                        cleaned_text, original_html = self._extract_content(entry, feed_type)
                    except Exception as e:
                        self.logger.warning(f"Error extracting content from entry: {e}")
                        cleaned_text = getattr(entry, 'title', 'No content available')
                        original_html = cleaned_text
                    
                    # Extract and normalize timestamp with error handling
                    try:
                        timestamp = self._normalize_timestamp(
                            getattr(entry, 'published_parsed', None) or 
                            getattr(entry, 'updated_parsed', None)
                        )
                    except Exception as e:
                        self.logger.warning(f"Error normalizing timestamp: {e}")
                        timestamp = datetime.now(timezone.utc)
                    
                    # Extract media URLs with error handling
                    try:
                        media_urls = self._extract_media_urls(entry)
                    except Exception as e:
                        self.logger.warning(f"Error extracting media URLs: {e}")
                        media_urls = []
                    
                    # Create unified post using base connector helper
                    try:
                        unified_post = self._create_unified_post(
                            platform="rss",
                            source=feed_url,  # Exactly as user enters
                            url=getattr(entry, 'link', feed_url),
                            content=cleaned_text,
                            date=timestamp,
                            media_urls=media_urls,
                            categories=categories,  # Use extracted categories
                            metadata={}  # Empty for Mark II
                        )
                        
                        # Add RSS/Atom-specific fields for backward compatibility
                        unified_post['title'] = getattr(entry, 'title', 'No title')
                        unified_post['feed_title'] = getattr(feed.feed, 'title', 'Unknown Feed')
                        unified_post['feed_type'] = feed_type
                        unified_post['content_html'] = original_html
                        
                        # Remove all legacy compatibility fields - use ONLY new structure
                        unified_posts.append(unified_post)
                        entries_processed += 1
                        
                    except Exception as e:
                        self.logger.error(f"Error creating unified post from entry: {e}")
                        continue
                        
                except Exception as e:
                    self.logger.error(f"Error processing RSS entry: {e}")
                    continue
            
            self.logger.info(f"Successfully processed {len(unified_posts)} posts from {feed_url} ({feed_type})")
            return unified_posts
            
        except urllib.error.HTTPError as e:
            self.logger.error(f"ERROR: Failed to fetch RSS feed from {feed_url} - Reason: HTTP {e.code}: {e.reason}")
            return []
            
        except urllib.error.URLError as e:
            self.logger.error(f"ERROR: Failed to fetch RSS feed from {feed_url} - Reason: Network error: {str(e.reason)}")
            return []
            
        except socket.timeout:
            self.logger.error(f"ERROR: Failed to fetch RSS feed from {feed_url} - Reason: Connection timed out")
            return []
            
        except Exception as e:
            self.logger.error(f"ERROR: Failed to fetch RSS feed from {feed_url} - Reason: Unexpected error: {str(e)}")
            return []
    
    async def fetch_posts_by_timeframe(self, sources: List[str], days: int) -> List[Dict[str, Any]]:
        """
        Fetch posts from multiple RSS/Atom feeds within a timeframe.
        Enhanced with category aggregation across sources.
        HARDENED: Individual source failures do not affect other sources.
        
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
        successful_sources = 0
        failed_sources = 0
        
        for feed_url in sources:
            self.logger.info(f"Processing RSS/Atom feed: {feed_url}")
            
            try:
                # Fetch all available posts from this feed with individual error handling
                feed_posts = await self.fetch_posts(feed_url, limit=100)  # Reasonable limit
                
                if feed_posts:
                    # Filter by timeframe if specified
                    if cutoff_date:
                        original_count = len(feed_posts)
                        feed_posts = [
                            post for post in feed_posts 
                            if post.get('date') and post['date'] >= cutoff_date
                        ]
                        self.logger.info(f"Filtered {original_count} posts to {len(feed_posts)} within timeframe from {feed_url}")
                    
                    all_posts.extend(feed_posts)
                    successful_sources += 1
                    self.logger.info(f"Successfully collected {len(feed_posts)} posts from {feed_url}")
                else:
                    failed_sources += 1
                    self.logger.warning(f"No posts collected from {feed_url}")
                
            except Exception as e:
                failed_sources += 1
                self.logger.error(f"ERROR: Failed to process RSS/Atom feed {feed_url} - Reason: {str(e)}")
                # Continue processing other sources
                continue
        
        self.logger.info(f"Multi-feed processing complete: {successful_sources} successful, {failed_sources} failed sources")
        
        # Sort chronologically with error handling
        try:
            return sorted(all_posts, key=lambda p: p.get('date', datetime.min.replace(tzinfo=timezone.utc)))
        except Exception as e:
            self.logger.error(f"Error sorting posts chronologically: {e}")
            return all_posts 