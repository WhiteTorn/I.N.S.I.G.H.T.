import os
import logging
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from connectors import TelegramConnector, RssConnector, YouTubeConnector, RedditConnector
from html_renderer import HTMLRenderer

# --- Configuration and Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    handlers=[
        logging.FileHandler("insight_debug.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- The Core Application Class (Mark II Orchestrator) ---
class InsightOperator:
    """
    I.N.S.I.G.H.T. Mark II (v2.4) - The Inquisitor Platform - Citadel Edition
    
    The modular intelligence platform that can gather intel from multiple sources.
    Version 2.4 introduces unified JSON output for seamless Mark III integration,
    creating a standardized data pipeline for the entire I.N.S.I.G.H.T. ecosystem.
    
    Hardened in v2.3 "The Citadel" with:
    - Global timeout protection (30s per operation)
    - Bulletproof error handling across all connectors
    - Graceful failure recovery - no single source can crash the system
    
    Architecture:
    - Orchestrator pattern for connector management
    - Unified data model for cross-platform compatibility  
    - Enhanced JSON serialization for Mark III compatibility
    - Independent connector testing capabilities
    - Category-aware content processing
    - Metadata enrichment and validation
    - HARDENED: Global timeout and error isolation
    """
    
    def __init__(self):
        logging.info("I.N.S.I.G.H.T. Mark II (v2.4) - The Inquisitor - Citadel Edition - Initializing...")
        load_dotenv()
        
        # Initialize available connectors
        self.connectors = {}
        self._setup_connectors()
        
        # JSON output configuration
        self.json_config = {
            'ensure_ascii': False,
            'indent': 4,
            'sort_keys': True,
            'default': self._json_serializer
        }
        
        # Global timeout configuration for The Citadel
        self.GLOBAL_TIMEOUT_SECONDS = 30
        
        logging.info("Mark II Orchestrator ready with unified JSON output capabilities and Citadel-grade protection.")
    
    def _json_serializer(self, obj):
        """
        Custom JSON serializer for handling datetime objects and other non-serializable types.
        
        This ensures that our unified data model can be cleanly serialized to JSON
        for Mark III consumption while maintaining all temporal and metadata information.
        """
        if isinstance(obj, datetime):
            return obj.isoformat() + 'Z'  # ISO format with UTC indicator
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _enrich_post_metadata(self, post: dict) -> dict:
        """
        Enrich a post with additional metadata for enhanced Mark III processing.
        
        This adds computed fields that will be valuable for Mark IV LLM analysis
        while maintaining backward compatibility with existing connectors.
        """
        enriched_post = post.copy()
        
        # Add Mark II processing metadata
        enriched_post['processing_metadata'] = {
            'processed_by': 'I.N.S.I.G.H.T. Mark II v2.4',
            'processed_at': datetime.utcnow().isoformat() + 'Z',
            'data_version': '2.4.0',
            'content_length': len(post.get('content', '')),
            'has_media': len(post.get('media_urls', [])) > 0,
            'media_count': len(post.get('media_urls', []))
        }
        
        # Add content analysis hints for Mark IV
        content = post.get('content', '')
        enriched_post['content_analysis_hints'] = {
            'estimated_reading_time_seconds': max(1, len(content.split()) * 0.25),  # ~250 WPM
            'contains_urls': 'http' in content.lower(),
            'contains_mentions': '@' in content,
            'contains_hashtags': '#' in content,
            'language_hint': 'en',  # Default, can be enhanced with detection
            'content_type': self._classify_content_type(post)
        }
        
        return enriched_post
    
    def _classify_content_type(self, post: dict) -> str:
        """
        Classify the type of content for enhanced Mark IV processing.
        
        Returns content type classification for LLM context optimization.
        """
        source_platform = post.get('source_platform', '')
        content = post.get('content', '').lower()
        
        if source_platform == 'rss':
            if post.get('categories'):
                return 'news_article'
            return 'feed_content'
        elif source_platform == 'telegram':
            if len(post.get('media_urls', [])) > 0:
                return 'media_post'
            elif len(content) > 500:
                return 'long_form_message'
            else:
                return 'short_message'
        
        return 'unknown'
    
    def _validate_json_payload(self, posts: list) -> dict:
        """
        Validate the JSON payload before export to ensure Mark III compatibility.
        
        Returns validation report with any issues found.
        """
        validation_report = {
            'status': 'valid',
            'total_posts': len(posts),
            'issues': [],
            'warnings': [],
            'metadata': {
                'platforms_included': set(),
                'date_range': {'earliest': None, 'latest': None},
                'total_media_items': 0
            }
        }
        
        for i, post in enumerate(posts):
            post_id = post.get('post_id', f'post_{i}')
            
            # Check required fields
            required_fields = ['source_platform', 'source_id', 'post_id', 'content', 'timestamp']
            for field in required_fields:
                if field not in post or post[field] is None:
                    validation_report['issues'].append(f"Post {post_id}: Missing required field '{field}'")
            
            # Track metadata
            if 'source_platform' in post:
                validation_report['metadata']['platforms_included'].add(post['source_platform'])
            
            if 'timestamp' in post and isinstance(post['timestamp'], datetime):
                ts = post['timestamp']
                if validation_report['metadata']['date_range']['earliest'] is None or ts < validation_report['metadata']['date_range']['earliest']:
                    validation_report['metadata']['date_range']['earliest'] = ts
                if validation_report['metadata']['date_range']['latest'] is None or ts > validation_report['metadata']['date_range']['latest']:
                    validation_report['metadata']['date_range']['latest'] = ts
            
            if 'media_urls' in post and isinstance(post['media_urls'], list):
                validation_report['metadata']['total_media_items'] += len(post['media_urls'])
        
        # Convert set to list for JSON serialization
        validation_report['metadata']['platforms_included'] = list(validation_report['metadata']['platforms_included'])
        
        if validation_report['issues']:
            validation_report['status'] = 'errors_found'
        elif validation_report['warnings']:
            validation_report['status'] = 'warnings_found'
        
        return validation_report
    
    def export_to_json(self, posts: list, filename: str = None, include_metadata: bool = True) -> str:
        """
        Export posts to a standardized JSON file for Mark III consumption.
        
        This is the core method that transforms our unified data into the standard
        payload format that Mark III "The Scribe" will consume for database storage.
        
        Args:
            posts: List of posts in unified format
            filename: Output filename (auto-generated if None)
            include_metadata: Whether to include enriched metadata
            
        Returns:
            The filename of the exported JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"inquisitor_report_{timestamp}.json"
        
        # Enrich posts with metadata if requested
        if include_metadata:
            enriched_posts = [self._enrich_post_metadata(post) for post in posts]
        else:
            enriched_posts = posts
        
        # Sort by timestamp for chronological processing
        enriched_posts.sort(key=lambda p: p.get('timestamp', datetime.min), reverse=True)
        
        # Validate the payload
        validation_report = self._validate_json_payload(enriched_posts)
        
        # Create the complete JSON payload
        json_payload = {
            'report_metadata': {
                'generated_by': 'I.N.S.I.G.H.T. Mark II v2.4',
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'total_posts': len(enriched_posts),
                'platforms_included': validation_report['metadata']['platforms_included'],
                'date_range': validation_report['metadata']['date_range'],
                'total_media_items': validation_report['metadata']['total_media_items'],
                'format_version': '2.4.0',
                'compatible_with': ['Mark III v3.0+', 'Mark IV v4.0+']
            },
            'validation_report': validation_report,
            'posts': enriched_posts
        }
        
        # Write to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_payload, f, **self.json_config)
            
            logging.info(f"Successfully exported {len(enriched_posts)} posts to {filename}")
            logging.info(f"Validation status: {validation_report['status']}")
            
            if validation_report['issues']:
                logging.warning(f"Validation found {len(validation_report['issues'])} issues")
                for issue in validation_report['issues'][:5]:  # Show first 5 issues
                    logging.warning(f"  - {issue}")
            
            return filename
            
        except Exception as e:
            logging.error(f"Failed to export JSON file {filename}: {e}")
            raise
    
    def _setup_connectors(self):
        """Initialize and register all available connectors."""
        # Telegram Connector
        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')
        
        if api_id and api_hash:
            self.connectors['telegram'] = TelegramConnector(
                api_id=api_id,
                api_hash=api_hash,
                session_file='insight_session'
            )
            logging.info("Telegram connector registered")
        else:
            logging.warning("Telegram credentials not found in .env file")
        
        # RSS Connector (always available - no credentials needed)
        self.connectors['rss'] = RssConnector()
        logging.info("RSS connector registered")
        
        # YouTube Connector - NO API KEY REQUIRED (uses yt-dlp)
        self.connectors['youtube'] = YouTubeConnector(
            preferred_languages=['en', 'ru', 'ka']  # Configurable language preferences
        )
        logging.info("YouTube connector registered (yt-dlp powered - no API key needed)")
        
        # Reddit Connector - Requires Reddit API credentials
        reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        reddit_user_agent = os.getenv('REDDIT_USER_AGENT', 'I.N.S.I.G.H.T. v2.6 The Crowd Crier')
        
        if reddit_client_id and reddit_client_secret:
            self.connectors['reddit'] = RedditConnector(
                client_id=reddit_client_id,
                client_secret=reddit_client_secret,
                user_agent=reddit_user_agent
            )
            logging.info("Reddit connector registered (PRAW powered)")
        else:
            logging.warning("Reddit credentials not found in .env file")
    
    async def connect_all(self):
        """Connect all available connectors."""
        for platform, connector in self.connectors.items():
            try:
                await connector.connect()
                logging.info(f"Connected to {platform}")
            except Exception as e:
                logging.error(f"Failed to connect to {platform}: {e}")
                # Remove failed connector to prevent issues
                del self.connectors[platform]
    
    async def disconnect_all(self):
        """Disconnect all connectors gracefully."""
        for platform, connector in self.connectors.items():
            try:
                await connector.disconnect()
                logging.info(f"Disconnected from {platform}")
            except Exception as e:
                logging.error(f"Error disconnecting from {platform}: {e}")
    
    # --- MISSION PROFILE 1: DEEP SCAN (Telegram) ---
    async def get_n_posts(self, channel_username: str, limit: int):
        """
        Fetches the last N logical posts from a single Telegram source.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'telegram' not in self.connectors:
            logging.error("Telegram connector not available")
            return []
        
        connector = self.connectors['telegram']
        
        try:
            # Wrap connector call with global timeout protection
            posts = await asyncio.wait_for(
                connector.fetch_posts(channel_username, limit),
                timeout=self.GLOBAL_TIMEOUT_SECONDS
            )
            return posts
            
        except asyncio.TimeoutError:
            logging.warning(f"WARNING: Fetch from @{channel_username} timed out after {self.GLOBAL_TIMEOUT_SECONDS}s")
            return []
        except Exception as e:
            logging.error(f"ERROR: Critical failure fetching from @{channel_username}: {str(e)}")
            return []
    
    # --- MISSION PROFILE 2 & 3: BRIEFINGS (Telegram) ---
    async def get_briefing_posts(self, channels: list, days: int):
        """
        Fetches all posts from a list of Telegram sources for the last N days.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'telegram' not in self.connectors:
            logging.error("Telegram connector not available")
            return []
        
        connector = self.connectors['telegram']
        
        try:
            # Wrap connector call with global timeout protection
            posts = await asyncio.wait_for(
                connector.fetch_posts_by_timeframe(channels, days),
                timeout=self.GLOBAL_TIMEOUT_SECONDS * len(channels)  # Scale timeout with number of channels
            )
            return posts
            
        except asyncio.TimeoutError:
            logging.warning(f"WARNING: Briefing fetch from {len(channels)} channels timed out after {self.GLOBAL_TIMEOUT_SECONDS * len(channels)}s")
            return []
        except Exception as e:
            logging.error(f"ERROR: Critical failure fetching briefing from channels: {str(e)}")
            return []
    
    # --- RSS MISSIONS (Enhanced in v2.3 with Citadel protection) ---
    async def analyze_rss_feed(self, feed_url: str):
        """
        Analyze an RSS/Atom feed and return metadata including available entry count.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'rss' not in self.connectors:
            logging.error("RSS connector not available")
            return None
        
        connector = self.connectors['rss']
        
        try:
            # Wrap connector call with global timeout protection
            feed_info = await asyncio.wait_for(
                connector.get_feed_info(feed_url),
                timeout=self.GLOBAL_TIMEOUT_SECONDS
            )
            return feed_info
            
        except asyncio.TimeoutError:
            logging.warning(f"WARNING: RSS feed analysis of {feed_url} timed out after {self.GLOBAL_TIMEOUT_SECONDS}s")
            return {
                "url": feed_url,
                "title": "Timeout Error",
                "description": f"Feed analysis timed out after {self.GLOBAL_TIMEOUT_SECONDS} seconds",
                "total_entries": 0,
                "feed_type": "unknown",
                "common_categories": [],
                "category_count": 0,
                "status": "error",
                "error": f"Analysis timed out after {self.GLOBAL_TIMEOUT_SECONDS}s"
            }
        except Exception as e:
            logging.error(f"ERROR: Critical failure analyzing RSS feed {feed_url}: {str(e)}")
            return {
                "url": feed_url,
                "title": "Critical Error",
                "description": f"Critical error during analysis: {str(e)}",
                "total_entries": 0,
                "feed_type": "unknown",
                "common_categories": [],
                "category_count": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def get_rss_posts(self, feed_url: str, limit: int):
        """
        Fetch N posts from a single RSS/Atom feed.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'rss' not in self.connectors:
            logging.error("RSS connector not available")
            return []
        
        connector = self.connectors['rss']
        
        try:
            # Wrap connector call with global timeout protection
            posts = await asyncio.wait_for(
                connector.fetch_posts(feed_url, limit),
                timeout=self.GLOBAL_TIMEOUT_SECONDS
            )
            return posts
            
        except asyncio.TimeoutError:
            logging.warning(f"WARNING: RSS fetch from {feed_url} timed out after {self.GLOBAL_TIMEOUT_SECONDS}s")
            return []
        except Exception as e:
            logging.error(f"ERROR: Critical failure fetching RSS posts from {feed_url}: {str(e)}")
            return []
    
    async def get_multi_rss_posts(self, feed_urls: list, limit_per_feed: int):
        """
        Fetch N posts from multiple RSS/Atom feeds.
        HARDENED: Protected by global timeout and comprehensive error handling.
        Individual feed failures do not affect other feeds.
        """
        if 'rss' not in self.connectors:
            logging.error("RSS connector not available")
            return []
        
        connector = self.connectors['rss']
        all_posts = []
        successful_feeds = 0
        failed_feeds = 0
        
        for feed_url in feed_urls:
            try:
                # Wrap each individual feed fetch with timeout protection
                posts = await asyncio.wait_for(
                    connector.fetch_posts(feed_url, limit_per_feed),
                    timeout=self.GLOBAL_TIMEOUT_SECONDS
                )
                
                if posts:
                    all_posts.extend(posts)
                    successful_feeds += 1
                    logging.info(f"Successfully fetched {len(posts)} posts from {feed_url}")
                else:
                    failed_feeds += 1
                    logging.warning(f"No posts retrieved from {feed_url}")
                    
            except asyncio.TimeoutError:
                failed_feeds += 1
                logging.warning(f"WARNING: RSS fetch from {feed_url} timed out after {self.GLOBAL_TIMEOUT_SECONDS}s")
                continue  # Continue processing other feeds
                
            except Exception as e:
                failed_feeds += 1
                logging.error(f"ERROR: Failed to fetch from {feed_url}: {str(e)}")
                continue  # Continue processing other feeds
        
        logging.info(f"Multi-RSS operation complete: {successful_feeds} successful, {failed_feeds} failed feeds")
        
        # Sort by timestamp for unified timeline
        try:
            return sorted(all_posts, key=lambda p: p.get('timestamp', datetime.min), reverse=True)
        except Exception as e:
            logging.error(f"Error sorting multi-RSS posts: {e}")
            return all_posts
    
    # --- YOUTUBE MISSIONS (New in v2.4 "The Spymaster") ---
    async def get_youtube_transcript(self, video_url: str):
        """
        Fetch transcript from a single YouTube video.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'youtube' not in self.connectors:
            logging.error("YouTube connector not available")
            return []
        
        connector = self.connectors['youtube']
        
        try:
            # Wrap connector call with global timeout protection
            posts = await asyncio.wait_for(
                connector.fetch_posts(video_url, 1),  # limit=1 for single video
                timeout=self.GLOBAL_TIMEOUT_SECONDS
            )
            return posts
            
        except asyncio.TimeoutError:
            logging.warning(f"WARNING: YouTube transcript fetch from {video_url} timed out after {self.GLOBAL_TIMEOUT_SECONDS}s")
            return []
        except Exception as e:
            logging.error(f"ERROR: Critical failure fetching YouTube transcript from {video_url}: {str(e)}")
            return []
    
    async def get_youtube_channel_transcripts(self, channel_identifier: str, limit: int):
        """
        Fetch transcripts from the latest N videos in a YouTube channel.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'youtube' not in self.connectors:
            logging.error("YouTube connector not available")
            return []
        
        connector = self.connectors['youtube']
        
        try:
            # Wrap connector call with global timeout protection
            posts = await asyncio.wait_for(
                connector.fetch_posts(channel_identifier, limit),
                timeout=self.GLOBAL_TIMEOUT_SECONDS * 2  # YouTube API calls take longer
            )
            return posts
            
        except asyncio.TimeoutError:
            logging.warning(f"WARNING: YouTube channel transcript fetch from {channel_identifier} timed out after {self.GLOBAL_TIMEOUT_SECONDS * 2}s")
            return []
        except Exception as e:
            logging.error(f"ERROR: Critical failure fetching YouTube channel transcripts from {channel_identifier}: {str(e)}")
            return []
    
    async def get_youtube_playlist_transcripts(self, playlist_url: str, limit: int):
        """
        BONUS: Fetch transcripts from a YouTube playlist.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'youtube' not in self.connectors:
            logging.error("YouTube connector not available")
            return []
        
        connector = self.connectors['youtube']
        
        try:
            # Wrap connector call with global timeout protection
            posts = await asyncio.wait_for(
                connector.fetch_playlist_transcripts(playlist_url, limit),
                timeout=self.GLOBAL_TIMEOUT_SECONDS * 3  # Playlist processing takes longer
            )
            return posts
            
        except asyncio.TimeoutError:
            logging.warning(f"WARNING: YouTube playlist transcript fetch from {playlist_url} timed out after {self.GLOBAL_TIMEOUT_SECONDS * 3}s")
            return []
        except Exception as e:
            logging.error(f"ERROR: Critical failure fetching YouTube playlist transcripts from {playlist_url}: {str(e)}")
            return []
    
    async def search_youtube_transcripts(self, search_query: str, limit: int):
        """
        BONUS: Search for YouTube videos and extract their transcripts.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'youtube' not in self.connectors:
            logging.error("YouTube connector not available")
            return []
        
        connector = self.connectors['youtube']
        
        try:
            # Wrap connector call with global timeout protection
            posts = await asyncio.wait_for(
                connector.search_video_transcripts(search_query, limit),
                timeout=self.GLOBAL_TIMEOUT_SECONDS * 2  # Search + transcript processing
            )
            return posts
            
        except asyncio.TimeoutError:
            logging.warning(f"WARNING: YouTube search for '{search_query}' timed out after {self.GLOBAL_TIMEOUT_SECONDS * 2}s")
            return []
        except Exception as e:
            logging.error(f"ERROR: Critical failure searching YouTube for '{search_query}': {str(e)}")
            return []
    
    # --- REDDIT MISSIONS (v2.6 "The Crowd Crier") ---
    async def get_reddit_post_with_comments(self, post_url: str):
        """
        Fetch a single Reddit post with all its comments.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'reddit' not in self.connectors:
            logging.error("Reddit connector not available")
            return []
        
        connector = self.connectors['reddit']
        
        try:
            # Wrap connector call with global timeout protection
            posts = await asyncio.wait_for(
                connector.fetch_post_with_comments(post_url),
                timeout=self.GLOBAL_TIMEOUT_SECONDS * 2  # Extra time for comment extraction
            )
            return posts
            
        except asyncio.TimeoutError:
            logging.warning(f"WARNING: Reddit post fetch from '{post_url}' timed out after {self.GLOBAL_TIMEOUT_SECONDS * 2}s")
            return []
        except Exception as e:
            logging.error(f"ERROR: Critical failure fetching Reddit post '{post_url}': {str(e)}")
            return []
    
    async def get_posts_from_subreddit(self, subreddit: str, limit: int = 10, sort: str = 'hot'):
        """
        Fetch posts from a subreddit with interactive selection.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'reddit' not in self.connectors:
            logging.error("Reddit connector not available")
            return []
        
        connector = self.connectors['reddit']
        
        try:
            # Wrap connector call with global timeout protection
            posts = await asyncio.wait_for(
                connector.fetch_subreddit_posts_interactive(subreddit, limit, sort),
                timeout=self.GLOBAL_TIMEOUT_SECONDS * 3  # Extra time for interactive selection
            )
            return posts
            
        except asyncio.TimeoutError:
            logging.warning(f"WARNING: Reddit subreddit fetch from 'r/{subreddit}' timed out after {self.GLOBAL_TIMEOUT_SECONDS * 3}s")
            return []
        except Exception as e:
            logging.error(f"ERROR: Critical failure fetching Reddit subreddit 'r/{subreddit}': {str(e)}")
            return []
    
    async def get_posts_from_multiple_subreddits(self, subreddits: list, limit_per_subreddit: int = 5):
        """
        Fetch posts from multiple subreddits.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'reddit' not in self.connectors:
            logging.error("Reddit connector not available")
            return []
        
        connector = self.connectors['reddit']
        all_posts = []
        successful_subreddits = 0
        failed_subreddits = 0
        
        for subreddit in subreddits:
            try:
                # Wrap each individual subreddit fetch with timeout protection
                posts = await asyncio.wait_for(
                    connector.fetch_posts(f"r/{subreddit}", limit_per_subreddit),
                    timeout=self.GLOBAL_TIMEOUT_SECONDS
                )
                
                if posts:
                    all_posts.extend(posts)
                    successful_subreddits += 1
                else:
                    failed_subreddits += 1
                    logging.warning(f"No posts retrieved from r/{subreddit}")
                    
            except asyncio.TimeoutError:
                failed_subreddits += 1
                logging.warning(f"WARNING: Reddit subreddit r/{subreddit} timed out after {self.GLOBAL_TIMEOUT_SECONDS}s")
            except Exception as e:
                failed_subreddits += 1
                logging.error(f"ERROR: Failed to fetch from r/{subreddit}: {str(e)}")
        
        logging.info(f"Reddit multi-subreddit mission: {successful_subreddits} successful, {failed_subreddits} failed")
        return all_posts
    
    # --- RENDER METHODS (Enhanced for RSS v2.3) ---
    def render_report_to_console(self, posts: list, title: str):
        """A generic renderer for a list of posts, supporting Telegram, RSS, and YouTube content."""
        print("\n" + "#"*25 + f" I.N.S.I.G.H.T. REPORT: {title.upper()} " + "#"*25)
        if not posts:
            print("\nNo displayable posts found for this report.")
        
        for i, post_data in enumerate(posts):
            media_count = len(post_data.get('media_urls', []))
            media_indicator = f"[+{media_count} MEDIA]" if media_count > 0 else ""
            
            # Handle platform-specific fields
            if post_data.get('source_platform') == 'youtube':
                video_title = post_data.get('video_title', 'Unknown Video')
                channel_name = post_data.get('author', 'Unknown Channel')
                view_count = post_data.get('view_count', 0)
                
                print(f"\n--- Video {i+1}/{len(posts)} | {video_title} ---")
                print(f"📺 Channel: {channel_name} | 📅 Date: {post_data.get('timestamp', 'Unknown').strftime('%Y-%m-%d %H:%M:%S') if post_data.get('timestamp') else 'Unknown'}")
                print(f"👀 Views: {view_count:,} | Video ID: {post_data.get('post_id', 'Unknown')} {media_indicator}")
                print(f"\n🎬 TRANSCRIPT:")
                
            elif post_data.get('source_platform') == 'rss':
                title_field = post_data.get('title', 'No title')
                feed_title = post_data.get('feed_title', 'Unknown Feed')
                feed_type = post_data.get('feed_type', 'rss').upper()
                categories = post_data.get('categories', [])
                
                print(f"\n--- Post {i+1}/{len(posts)} | {title_field} ---")
                print(f"Feed: {feed_title} ({feed_type}) | Date: {post_data.get('date', post_data.get('timestamp', 'Unknown')).strftime('%Y-%m-%d %H:%M:%S') if post_data.get('date') or post_data.get('timestamp') else 'Unknown'} {media_indicator}")
                if categories:
                    print(f"Categories: {', '.join(categories)}")
            else:
                # Telegram and other platforms
                print(f"\n--- Post {i+1}/{len(posts)} | ID: {post_data.get('id', post_data.get('post_id', 'Unknown'))} | Date: {post_data.get('date', post_data.get('timestamp', 'Unknown')).strftime('%Y-%m-%d %H:%M:%S') if post_data.get('date') or post_data.get('timestamp') else 'Unknown'} {media_indicator} ---")
            
            # Display content (text or transcript)
            content = post_data.get('content', post_data.get('text', 'No content available'))
            print(content)
            
            # Display link
            link = post_data.get('post_url', post_data.get('link', 'No link available'))
            print(f"🔗 Link: {link}")

            if post_data.get('media_urls'):
                print("📎 Media Links:")
                for url in post_data['media_urls']:
                    print(f"  - {url}")
            print("-" * 60)
        print("\n" + "#"*30 + " END OF REPORT " + "#"*30)

    def render_briefing_to_console(self, posts: list, title: str):
        """Renders a chronologically sorted briefing, supporting both platforms with categories."""
        print("\n" + "#"*25 + f" I.N.S.I.G.H.T. BRIEFING: {title.upper()} " + "#"*25)
        if not posts:
            print("\nNo intelligence gathered for this period.")
            print("\n" + "#"*30 + " END OF BRIEFING " + "#"*30)
            return

        posts_by_day = {}
        for post in posts:
            day_str = post['date'].strftime('%Y-%m-%d, %A')
            if day_str not in posts_by_day:
                posts_by_day[day_str] = []
            posts_by_day[day_str].append(post)
        
        for day, day_posts in sorted(posts_by_day.items()):
            print(f"\n\n{'='*25} INTEL FOR: {day} {'='*25}")
            for i, post_data in enumerate(day_posts):
                media_count = len(post_data.get('media_urls', []))
                media_indicator = f"[+{media_count} MEDIA]" if media_count > 0 else ""
                
                # Handle different source types
                if post_data.get('source_platform') == 'rss':
                    feed_title = post_data.get('feed_title', 'RSS Feed')
                    feed_type = post_data.get('feed_type', 'rss').upper()
                    categories = post_data.get('categories', [])
                    
                    print(f"\n--- [{post_data['date'].strftime('%H:%M:%S')}] From: {feed_title} ({feed_type}) {media_indicator} ---")
                    if categories:
                        print(f"Categories: {', '.join(categories)}")
                else:
                    print(f"\n--- [{post_data['date'].strftime('%H:%M:%S')}] From: @{post_data['channel']} (ID: {post_data['id']}) {media_indicator} ---")
                
                print(post_data['text'])
                print(f"Link: {post_data['link']}")

                if post_data.get('media_urls'):
                    print("Media Links:")
                    for url in post_data['media_urls']:
                        print(f"  - {url}")
                print("-" * 60)

        print("\n" + "#"*30 + " END OF BRIEFING " + "#"*30)

    def render_feed_info(self, feed_info: dict):
        """Render RSS/Atom feed analysis information with category insights."""
        print("\n" + "#"*25 + " RSS/ATOM FEED ANALYSIS " + "#"*25)
        
        if feed_info['status'] == 'error':
            print(f"❌ Error analyzing feed: {feed_info['error']}")
            return
        
        print(f"📰 Feed Title: {feed_info['title']}")
        print(f"🌐 URL: {feed_info['url']}")
        print(f"📝 Description: {feed_info['description']}")
        print(f"🔗 Website: {feed_info['link']}")
        print(f"🌍 Language: {feed_info['language']}")
        print(f"📊 Total Entries Available: {feed_info['total_entries']}")
        print(f"🔄 Feed Type: {feed_info['feed_type'].upper()}")
        print(f"🏷️  Categories Found: {feed_info['category_count']}")
        
        if feed_info.get('common_categories'):
            print(f"📂 Common Categories: {', '.join(feed_info['common_categories'][:10])}")  # Show first 10
            if len(feed_info['common_categories']) > 10:
                print(f"   ... and {len(feed_info['common_categories']) - 10} more")
        
        print(f"🕒 Last Updated: {feed_info['last_updated']}")
        print("\n" + "#"*30 + " END OF ANALYSIS " + "#"*30)

    # --- ENHANCED MAIN EXECUTION LOOP ---
    async def run(self):
        """
        The main execution flow with enhanced RSS testing missions and HTML output.
        """
        try:
            await self.connect_all()
            
            if not self.connectors:
                print("\nNo connectors available. Please check your configuration.")
                return
            
            available_connectors = list(self.connectors.keys())
            print(f"\nI.N.S.I.G.H.T. Mark II (v2.4) - The Inquisitor - Citadel Edition - Operator Online.")
            print(f"Available connectors: {', '.join(available_connectors)}")
            print(f"🛡️  Citadel Protection: {self.GLOBAL_TIMEOUT_SECONDS}s global timeout, bulletproof error handling")
            print("\nChoose your mission:")
            print("\n--- TELEGRAM MISSIONS ---")
            print("1. Deep Scan (Get last N posts from one Telegram channel)")
            print("2. Historical Briefing (Get posts from the last N days from multiple Telegram channels)")
            print("3. End of Day Briefing (Get all of today's posts from multiple Telegram channels)")
            print("\n--- RSS/ATOM MISSIONS ---")
            print("4. RSS Feed Analysis (Analyze a single RSS/Atom feed)")
            print("5. RSS Single Feed Scan (Get N posts from a single RSS/Atom feed)")
            print("6. RSS Multi-Feed Scan (Get N posts from multiple RSS/Atom feeds)")
            print("\n--- YOUTUBE MISSIONS ---")
            print("7. YouTube Transcript (Get transcript from a single YouTube video)")
            print("8. YouTube Channel Transcripts (Get transcripts from the latest N videos in a YouTube channel)")
            print("9. YouTube Playlist Transcripts (Get transcripts from a YouTube playlist)")
            print("10. YouTube Search (Search for YouTube videos and extract their transcripts)")
            print("\n--- REDDIT MISSIONS ---")
            print("12. Reddit Post Analysis (Get single Reddit post with comments by URL)")
            print("13. Reddit Subreddit Explorer (Browse and select posts from subreddit)")
            print("14. Reddit Multi-Source Briefing (Get posts from multiple subreddits/URLs)")
            print("\n--- UNIFIED OUTPUT MISSIONS ---")
            print("11. JSON Export Test (Export sample data to test Mark III compatibility)")
            
            mission_choice = input("\nEnter mission number (1-14): ")

            # Enhanced error reporting for user feedback
            def report_mission_outcome(posts_collected: int, sources_attempted: int, mission_name: str):
                """Report mission outcome with Citadel-enhanced feedback."""
                if posts_collected > 0:
                    print(f"\n✅ Mission '{mission_name}' completed successfully!")
                    print(f"   📊 Intelligence gathered: {posts_collected} posts")
                    if sources_attempted > 1:
                        print(f"   🎯 Sources processed: {sources_attempted}")
                elif sources_attempted > 0:
                    print(f"\n⚠️  Mission '{mission_name}' completed with no intelligence gathered.")
                    print(f"   🔍 This may indicate:")
                    print(f"      • Sources are currently inaccessible")
                    print(f"      • No content available in the specified timeframe")
                    print(f"      • Network connectivity issues")
                    print(f"   🛡️  Citadel Protection: System remained stable despite source failures")
                else:
                    print(f"\n❌ Mission '{mission_name}' failed to initiate.")
                    print(f"   🛡️  Citadel Protection: System protected from cascading failures")

            # Telegram missions (enhanced with JSON output)
            if mission_choice in ['1', '2', '3']:
                if 'telegram' not in self.connectors:
                    print("❌ Telegram connector not available. Please check your .env configuration.")
                    return
                
                if mission_choice == '1':
                    channel = input("\nEnter the target channel username: ")
                    limit = int(input("How many posts to retrieve? "))
                    
                    print("\nChoose your output format:")
                    print("1. Console Only")
                    print("2. HTML Dossier Only")
                    print("3. JSON Export Only")
                    print("4. Console + HTML")
                    print("5. Console + JSON")
                    print("6. HTML + JSON")
                    print("7. All Formats (Console + HTML + JSON)")
                    output_choice = input("Enter format number (1-7): ")

                    posts = await self.get_n_posts(channel, limit)
                    title = f"{limit} posts from @{channel}"

                    if output_choice in ['1', '4', '5', '7']:
                        self.render_report_to_console(posts, title)
                    
                    if output_choice in ['2', '4', '6', '7']:
                        html_dossier = HTMLRenderer(f"I.N.S.I.G.H.T. Deep Scan: {title}")
                        html_dossier.render_report(posts)
                        html_dossier.save_to_file(f"deep_scan_{channel.lstrip('@')}.html")
                    
                    if output_choice in ['3', '5', '6', '7']:
                        json_filename = self.export_to_json(posts, f"deep_scan_{channel.lstrip('@')}.json")
                        print(f"\n📁 JSON export saved to: {json_filename}")
                        print("🔄 This file is ready for Mark III 'Scribe' processing.")
                    
                    # Report mission outcome
                    report_mission_outcome(len(posts), 1, f"Deep Scan @{channel}")
                
                elif mission_choice in ['2', '3']:
                    days = 0
                    if mission_choice == '2':
                        title_prefix = "Historical Briefing"
                        days = int(input("How many days of history to include? "))
                    else: # mission_choice == '3'
                        title_prefix = "End of Day Report"
                    
                    channels_str = input("Enter channel usernames, separated by commas: ")
                    channels = [c.strip() for c in channels_str.split(',')]
                    
                    print("\nChoose your output format:")
                    print("1. Console Only")
                    print("2. HTML Dossier Only")
                    print("3. JSON Export Only")
                    print("4. Console + HTML")
                    print("5. Console + JSON")
                    print("6. HTML + JSON")
                    print("7. All Formats (Console + HTML + JSON)")
                    output_choice = input("Enter format number (1-7): ")
                    
                    all_posts = await self.get_briefing_posts(channels, days)
                    
                    title = f"{title_prefix} for {', '.join(channels)}"
                    
                    if output_choice in ['1', '4', '5', '7']:
                        self.render_briefing_to_console(all_posts, title)
                    
                    if output_choice in ['2', '4', '6', '7']:
                        # Prepare data for HTML renderer
                        html_renderer = HTMLRenderer()
                        briefing_data_for_html = {channel: [] for channel in channels}
                        for post in all_posts:
                            briefing_data_for_html[post['channel']].append(post)

                        html_renderer.render_briefing(briefing_data_for_html, days)
                        
                        filename_date = datetime.now().strftime('%Y-%m-%d')
                        filename = f"briefing_{filename_date}.html"
                        html_renderer.save_to_file(filename)
                    
                    if output_choice in ['3', '5', '6', '7']:
                        filename_date = datetime.now().strftime('%Y%m%d')
                        json_filename = self.export_to_json(all_posts, f"briefing_{filename_date}.json")
                        print(f"\n📁 JSON export saved to: {json_filename}")
                        print("🔄 This file is ready for Mark III 'Scribe' processing.")
                    
                    # Report mission outcome
                    report_mission_outcome(len(all_posts), len(channels), title_prefix)
            
            # RSS missions (enhanced with JSON output)
            elif mission_choice in ['4', '5', '6']:
                if 'rss' not in self.connectors:
                    print("❌ RSS connector not available.")
                    return
                
                if mission_choice == '4':
                    # RSS Feed Analysis
                    feed_url = input("\nEnter RSS/Atom feed URL: ")
                    print(f"\n🔍 Analyzing RSS/Atom feed: {feed_url}")
                    
                    feed_info = await self.analyze_rss_feed(feed_url)
                    self.render_feed_info(feed_info)
                
                elif mission_choice == '5':
                    # RSS Single Feed Scan
                    feed_url = input("\nEnter RSS/Atom feed URL: ")
                    
                    # First, analyze the feed to show available entries
                    print(f"\n🔍 Analyzing feed...")
                    feed_info = await self.analyze_rss_feed(feed_url)
                    
                    if feed_info['status'] == 'error':
                        print(f"❌ Cannot access feed: {feed_info['error']}")
                        return
                    
                    print(f"📊 Feed '{feed_info['title']}' ({feed_info['feed_type'].upper()}) has {feed_info['total_entries']} entries available")
                    if feed_info.get('common_categories'):
                        print(f"🏷️  Common categories: {', '.join(feed_info['common_categories'][:5])}")
                    
                    limit = int(input(f"How many posts to retrieve (max {feed_info['total_entries']})? "))
                    
                    print("\nChoose your output format:")
                    print("1. Console Only")
                    print("2. HTML Dossier Only")
                    print("3. JSON Export Only")
                    print("4. Console + HTML")
                    print("5. Console + JSON")
                    print("6. HTML + JSON")
                    print("7. All Formats (Console + HTML + JSON)")
                    output_choice = input("Enter format number (1-7): ")
                    
                    posts = await self.get_rss_posts(feed_url, limit)
                    title = f"{limit} posts from {feed_info['title']}"
                    
                    if output_choice in ['1', '4', '5', '7']:
                        self.render_report_to_console(posts, title)
                    
                    if output_choice in ['2', '4', '6', '7']:
                        html_dossier = HTMLRenderer(f"I.N.S.I.G.H.T. RSS Scan: {title}")
                        html_dossier.render_rss_briefing(posts, title)
                        
                        # Create safe filename from feed title
                        safe_name = "".join(c for c in feed_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        safe_name = safe_name.replace(' ', '_')[:50]  # Limit length
                        html_dossier.save_to_file(f"rss_scan_{safe_name}.html")
                    
                    if output_choice in ['3', '5', '6', '7']:
                        safe_name = "".join(c for c in feed_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        safe_name = safe_name.replace(' ', '_')[:50]
                        json_filename = self.export_to_json(posts, f"rss_scan_{safe_name}.json")
                        print(f"\n📁 JSON export saved to: {json_filename}")
                        print("🔄 This file is ready for Mark III 'Scribe' processing.")
                    
                    # Report mission outcome
                    report_mission_outcome(len(posts), 1, f"RSS Scan - {feed_info['title']}")
                
                elif mission_choice == '6':
                    # RSS Multi-Feed Scan
                    feeds_str = input("\nEnter RSS/Atom feed URLs, separated by commas: ")
                    feed_urls = [url.strip() for url in feeds_str.split(',')]
                    
                    # Analyze each feed first
                    print(f"\n🔍 Analyzing {len(feed_urls)} feeds...")
                    feed_infos = []
                    for feed_url in feed_urls:
                        feed_info = await self.analyze_rss_feed(feed_url)
                        feed_infos.append(feed_info)
                        if feed_info['status'] == 'success':
                            print(f"✅ {feed_info['title']} ({feed_info['feed_type'].upper()}): {feed_info['total_entries']} entries")
                        else:
                            print(f"❌ {feed_url}: Error - {feed_info['error']}")
                    
                    limit_per_feed = int(input("\nHow many posts per feed to retrieve? "))
                    
                    print("\nChoose your output format:")
                    print("1. Console Only")
                    print("2. HTML Dossier Only")
                    print("3. JSON Export Only")
                    print("4. Console + HTML")
                    print("5. Console + JSON")
                    print("6. HTML + JSON")
                    print("7. All Formats (Console + HTML + JSON)")
                    output_choice = input("Enter format number (1-7): ")
                    
                    posts = await self.get_multi_rss_posts(feed_urls, limit_per_feed)
                    title = f"Multi-RSS scan: {limit_per_feed} posts from {len(feed_urls)} feeds"
                    
                    if output_choice in ['1', '4', '5', '7']:
                        self.render_briefing_to_console(posts, title)
                    
                    if output_choice in ['2', '4', '6', '7']:
                        html_renderer = HTMLRenderer(f"I.N.S.I.G.H.T. Multi-RSS Briefing")
                        html_renderer.render_rss_briefing(posts, title)
                        
                        filename_date = datetime.now().strftime('%Y-%m-%d')
                        html_renderer.save_to_file(f"multi_rss_briefing_{filename_date}.html")
                    
                    if output_choice in ['3', '5', '6', '7']:
                        filename_date = datetime.now().strftime('%Y%m%d')
                        json_filename = self.export_to_json(posts, f"multi_rss_briefing_{filename_date}.json")
                        print(f"\n📁 JSON export saved to: {json_filename}")
                        print("🔄 This file is ready for Mark III 'Scribe' processing.")
                    
                    # Report mission outcome
                    report_mission_outcome(len(posts), len(feed_urls), "Multi-RSS Scan")
            
            # YouTube missions (enhanced with JSON output)
            elif mission_choice in ['7', '8', '9', '10']:
                if 'youtube' not in self.connectors:
                    print("❌ YouTube connector not available.")
                    return
                
                if mission_choice == '7':
                    # YouTube Transcript
                    video_url = input("\nEnter YouTube video URL: ")
                    print(f"\n🔍 Fetching YouTube transcript for: {video_url}")
                    
                    posts = await self.get_youtube_transcript(video_url)
                    title = f"YouTube Transcript: {video_url}"
                    
                    if posts:
                        self.render_report_to_console(posts, title)
                        json_filename = self.export_to_json(posts, f"youtube_transcript_{video_url.replace('/', '_')}.json")
                        print(f"\n📁 JSON export saved to: {json_filename}")
                        print("🔄 This file is ready for Mark III 'Scribe' processing.")
                    else:
                        print("\n❌ No transcript found for the given video URL.")
                
                elif mission_choice == '8':
                    # YouTube Channel Transcripts
                    channel_identifier = input("\nEnter YouTube channel identifier (username or channel ID): ")
                    print(f"\n🔍 Fetching YouTube channel transcripts for: {channel_identifier}")
                    
                    limit = int(input("How many videos to retrieve? "))
                    
                    posts = await self.get_youtube_channel_transcripts(channel_identifier, limit)
                    title = f"YouTube Channel Transcripts: {channel_identifier}"
                    
                    if posts:
                        self.render_briefing_to_console(posts, title)
                        json_filename = self.export_to_json(posts, f"youtube_channel_transcripts_{channel_identifier.replace('/', '_')}.json")
                        print(f"\n📁 JSON export saved to: {json_filename}")
                        print("🔄 This file is ready for Mark III 'Scribe' processing.")
                    else:
                        print("\n❌ No transcripts found for the given channel identifier.")
                
                elif mission_choice == '9':
                    # YouTube Playlist Transcripts
                    playlist_url = input("\nEnter YouTube playlist URL: ")
                    print(f"\n🔍 Fetching YouTube playlist transcripts for: {playlist_url}")
                    
                    limit = int(input("How many videos to retrieve? "))
                    
                    posts = await self.get_youtube_playlist_transcripts(playlist_url, limit)
                    title = f"YouTube Playlist Transcripts: {playlist_url}"
                    
                    if posts:
                        self.render_briefing_to_console(posts, title)
                        json_filename = self.export_to_json(posts, f"youtube_playlist_transcripts_{playlist_url.replace('/', '_')}.json")
                        print(f"\n📁 JSON export saved to: {json_filename}")
                        print("🔄 This file is ready for Mark III 'Scribe' processing.")
                    else:
                        print("\n❌ No transcripts found for the given playlist URL.")
                
                elif mission_choice == '10':
                    # YouTube Search
                    search_query = input("\nEnter YouTube search query: ")
                    print(f"\n🔍 Searching YouTube for: {search_query}")
                    
                    limit = int(input("How many videos to retrieve? "))
                    
                    posts = await self.search_youtube_transcripts(search_query, limit)
                    title = f"YouTube Search Results: {search_query}"
                    
                    if posts:
                        self.render_briefing_to_console(posts, title)
                        json_filename = self.export_to_json(posts, f"youtube_search_{search_query.replace(' ', '_')}.json")
                        print(f"\n📁 JSON export saved to: {json_filename}")
                        print("🔄 This file is ready for Mark III 'Scribe' processing.")
                    else:
                        print("\n❌ No search results found for the given query.")
            
            # Reddit missions (enhanced with JSON output)
            elif mission_choice in ['12', '13', '14']:
                if 'reddit' not in self.connectors:
                    print("❌ Reddit connector not available.")
                    return
                
                if mission_choice == '12':
                    # Reddit Post Analysis
                    post_url = input("\nEnter Reddit post URL: ")
                    print(f"\n🔍 Fetching Reddit post with comments for: {post_url}")
                    
                    print("\nChoose your output format:")
                    print("1. Console Only")
                    print("2. HTML Dossier Only")
                    print("3. JSON Export Only")
                    print("4. Console + HTML")
                    print("5. Console + JSON")
                    print("6. HTML + JSON")
                    print("7. All Formats (Console + HTML + JSON)")
                    output_choice = input("Enter format number (1-7): ")
                    
                    posts = await self.get_reddit_post_with_comments(post_url)
                    title = f"Reddit Post Analysis: {post_url}"
                    
                    if posts:
                        if output_choice in ['1', '4', '5', '7']:
                            self.render_report_to_console(posts, title)
                        
                        if output_choice in ['2', '4', '6', '7']:
                            html_dossier = HTMLRenderer(f"I.N.S.I.G.H.T. Reddit Post Analysis: {title}")
                            html_dossier.render_report(posts)
                            safe_url = post_url.replace('/', '_').replace('.', '_').replace(':', '_')
                            html_dossier.save_to_file(f"reddit_post_analysis_{safe_url}.html")
                        
                        if output_choice in ['3', '5', '6', '7']:
                            json_filename = self.export_to_json(posts, f"reddit_post_analysis_{post_url.replace('/', '_').replace('.', '_')}.json")
                            print(f"\n📁 JSON export saved to: {json_filename}")
                            print("🔄 This file is ready for Mark III 'Scribe' processing.")
                        
                        # Report mission outcome
                        report_mission_outcome(len(posts), 1, "Reddit Post Analysis")
                    else:
                        print("\n❌ No comments found for the given post URL.")
                
                elif mission_choice == '13':
                    # Reddit Subreddit Explorer
                    subreddit = input("\nEnter Reddit subreddit name: ")
                    print(f"\n🔍 Exploring posts from subreddit: {subreddit}")
                    
                    print("\nChoose your output format:")
                    print("1. Console Only")
                    print("2. HTML Dossier Only")
                    print("3. JSON Export Only")
                    print("4. Console + HTML")
                    print("5. Console + JSON")
                    print("6. HTML + JSON")
                    print("7. All Formats (Console + HTML + JSON)")
                    output_choice = input("Enter format number (1-7): ")
                    
                    posts = await self.get_posts_from_subreddit(subreddit)
                    title = f"Reddit Posts from {subreddit}"
                    
                    if posts:
                        if output_choice in ['1', '4', '5', '7']:
                            self.render_briefing_to_console(posts, title)
                        
                        if output_choice in ['2', '4', '6', '7']:
                            html_dossier = HTMLRenderer(f"I.N.S.I.G.H.T. Reddit Subreddit Explorer: {title}")
                            html_dossier.render_briefing({subreddit: posts}, 0)  # 0 days for current posts
                            html_dossier.save_to_file(f"reddit_subreddit_{subreddit.replace('/', '_')}.html")
                        
                        if output_choice in ['3', '5', '6', '7']:
                            json_filename = self.export_to_json(posts, f"reddit_subreddit_explorer_{subreddit.replace('/', '_')}.json")
                            print(f"\n📁 JSON export saved to: {json_filename}")
                            print("🔄 This file is ready for Mark III 'Scribe' processing.")
                        
                        # Report mission outcome
                        report_mission_outcome(len(posts), 1, f"Reddit Subreddit Explorer - {subreddit}")
                    else:
                        print("\n❌ No posts found for the given subreddit.")
                
                elif mission_choice == '14':
                    # Reddit Multi-Source Briefing
                    subreddits_str = input("\nEnter Reddit subreddits, separated by commas: ")
                    subreddits = [sr.strip() for sr in subreddits_str.split(',')]
                    
                    print("\nChoose your output format:")
                    print("1. Console Only")
                    print("2. HTML Dossier Only")
                    print("3. JSON Export Only")
                    print("4. Console + HTML")
                    print("5. Console + JSON")
                    print("6. HTML + JSON")
                    print("7. All Formats (Console + HTML + JSON)")
                    output_choice = input("Enter format number (1-7): ")
                    
                    print(f"\n🔍 Fetching posts from {len(subreddits)} subreddits...")
                    posts = await self.get_posts_from_multiple_subreddits(subreddits)
                    title = f"Reddit Multi-Source Briefing: {', '.join(subreddits)}"
                    
                    if posts:
                        if output_choice in ['1', '4', '5', '7']:
                            self.render_briefing_to_console(posts, title)
                        
                        if output_choice in ['2', '4', '6', '7']:
                            html_renderer = HTMLRenderer(f"I.N.S.I.G.H.T. Reddit Multi-Source Briefing")
                            # Organize posts by subreddit for HTML rendering
                            briefing_data_for_html = {sr: [] for sr in subreddits}
                            for post in posts:
                                subreddit_name = post.get('subreddit', 'unknown')
                                if subreddit_name in briefing_data_for_html:
                                    briefing_data_for_html[subreddit_name].append(post)
                            
                            html_renderer.render_briefing(briefing_data_for_html, 0)
                            
                            filename_date = datetime.now().strftime('%Y-%m-%d')
                            html_renderer.save_to_file(f"reddit_multi_source_briefing_{filename_date}.html")
                        
                        if output_choice in ['3', '5', '6', '7']:
                            json_filename = self.export_to_json(posts, f"reddit_multi_source_briefing_{'_'.join(subreddits).replace('/', '_')}.json")
                            print(f"\n📁 JSON export saved to: {json_filename}")
                            print("🔄 This file is ready for Mark III 'Scribe' processing.")
                        
                        # Report mission outcome
                        report_mission_outcome(len(posts), len(subreddits), "Reddit Multi-Source Briefing")
                    else:
                        print("\n❌ No posts found for the given subreddits.")
            
            # New unified output testing mission
            elif mission_choice == '11':
                print("\n🧪 JSON Export Test Mode")
                print("This mission demonstrates the unified JSON output format for Mark III compatibility testing.")
                
                # Generate sample data from available connectors
                test_posts = []
                
                if 'telegram' in self.connectors:
                    print("\n📱 Include Telegram test data? (y/n): ", end="")
                    if input().lower() == 'y':
                        channel = input("Enter a Telegram channel username for test data: ")
                        try:
                            telegram_posts = await self.get_n_posts(channel, 3)
                            test_posts.extend(telegram_posts)
                            print(f"✅ Added {len(telegram_posts)} Telegram posts")
                        except Exception as e:
                            print(f"❌ Failed to fetch Telegram data: {e}")
                
                if 'rss' in self.connectors:
                    print("\n📰 Include RSS test data? (y/n): ", end="")
                    if input().lower() == 'y':
                        feed_url = input("Enter an RSS feed URL for test data: ")
                        try:
                            rss_posts = await self.get_rss_posts(feed_url, 3)
                            test_posts.extend(rss_posts)
                            print(f"✅ Added {len(rss_posts)} RSS posts")
                        except Exception as e:
                            print(f"❌ Failed to fetch RSS data: {e}")
                
                if 'youtube' in self.connectors:
                    print("\n📺 Include YouTube test data? (y/n): ", end="")
                    if input().lower() == 'y':
                        video_url = input("Enter a YouTube video URL for test data: ")
                        try:
                            youtube_posts = await self.get_youtube_transcript(video_url)
                            test_posts.extend(youtube_posts)
                            print(f"✅ Added {len(youtube_posts)} YouTube posts")
                        except Exception as e:
                            print(f"❌ Failed to fetch YouTube data: {e}")
                
                if test_posts:
                    json_filename = self.export_to_json(test_posts, "mark_iii_compatibility_test.json")
                    print(f"\n🎯 Test JSON export created: {json_filename}")
                    print("\n📋 JSON Export Summary:")
                    print(f"   • Total posts: {len(test_posts)}")
                    print(f"   • Platforms included: {', '.join(set(p.get('source_platform', 'unknown') for p in test_posts))}")
                    print(f"   • Format version: 2.4.0")
                    print(f"   • Mark III ready: ✅")
                    print(f"   • Mark IV ready: ✅")
                    
                    print("\n🔍 Would you like to view the JSON structure? (y/n): ", end="")
                    if input().lower() == 'y':
                        with open(json_filename, 'r', encoding='utf-8') as f:
                            sample_data = json.load(f)
                        
                        print("\n" + "="*60)
                        print("SAMPLE JSON STRUCTURE (first post only):")
                        print("="*60)
                        if sample_data['posts']:
                            print(json.dumps(sample_data['posts'][0], indent=2, ensure_ascii=False))
                        print("="*60)
                else:
                    print("\n❌ No test data collected. Please check your connector configurations.")
            
            else:
                print("Invalid mission choice. Aborting.")

            logging.info("Mission complete.")

        except Exception as e:
            logging.critical(f"A critical error occurred: {e}", exc_info=True)
        finally:
            await self.disconnect_all()

# --- Execution ---
if __name__ == "__main__":
    app = InsightOperator()
    asyncio.run(app.run())