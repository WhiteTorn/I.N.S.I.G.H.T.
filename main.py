import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
import sys

# Core Modules
from logs.core.logger_config import setup_logging, get_component_logger
from config.config_manager import ConfigManager

# Modules
from connectors import TelegramConnector, RssConnector, YouTubeConnector, RedditConnector
from output import ConsoleOutput, HTMLOutput, JSONOutput

# Old self.logger configuration.
# # --- Configuration and Setup ---
# self.logger.basicConfig(
#     level=self.logger.INFO,
#     format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
#     handlers=[
#         self.logger.FileHandler("insight_debug.log", encoding='utf-8'),
#         self.logger.StreamHandler()
#     ]
# )

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
    
    def __init__(self, debug_mode: bool = False):
        # Set up self.logger first
        self.logger_config = setup_logging(debug_mode = debug_mode)
        self.logger = get_component_logger('insight_operator')

        self.logger.info("I.N.S.I.G.H.T. Mark II (v2.6) - The Grand Marshal - Citadel Edition - Initializing...")

        load_dotenv()

        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        # Validate the config
        self.logger.info(self.config_manager.validate_config(self.config))

        # How to use it now
        # enabled_sources = self.config_manager.get_enabled_sources(self.config)
        # if enabled_sources.get("telegram", {}).get("enabled", False):
        # else self.logger.info("Telegram is not enabled")
        
        # Initialize available connectors
        self.connectors = {}
        self._setup_connectors()
        
        # Global timeout configuration for The Citadel
        self.GLOBAL_TIMEOUT_SECONDS = 30
        
        self.logger.info("Mark II Orchestrator ready with Citadel-grade protection.")
    
    def _setup_connectors(self):
        """Initialize and register all available connectors based on the configuration."""
        enabled_sources = self.config_manager.get_enabled_sources(self.config)

        if "telegram" in enabled_sources:
            # Telegram Connector
            api_id = os.getenv('TELEGRAM_API_ID')
            api_hash = os.getenv('TELEGRAM_API_HASH')
        
            if api_id and api_hash:
                self.connectors['telegram'] = TelegramConnector(
                    api_id=api_id,
                    api_hash=api_hash,
                    session_file='insight_session'
                )
                self.logger.info("Telegram connector registered")
            else:
                self.logger.warning("Telegram credentials not found in .env file")
        else:
            self.logger.info("telegram Connectors disabled in configuration")
        
        if "rss" in enabled_sources:
            # RSS Connector (always available - no credentials needed)
            self.connectors['rss'] = RssConnector()
            self.logger.info("RSS connector registered")
        else:
            self.logger.info("RSS Connectors disabled in configuration")

        if "youtube" in enabled_sources:
            # YouTube Connector - NO API KEY REQUIRED (uses yt-dlp)
            self.connectors['youtube'] = YouTubeConnector(
                preferred_languages=['en', 'ru', 'ka']  # Configurable language preferences
            )
            self.logger.info("YouTube connector registered (yt-dlp powered - no API key needed)")
        else:
            self.logger.info("YouTube Connectors disabled in configuration")
        
        if "reddit" in enabled_sources:
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
                self.logger.info("Reddit connector registered (PRAW powered)")
            else:
                self.logger.warning("Reddit credentials not found in .env file")
        else:
            self.logger.info("Reddit Connectors disabled in configuration")
    
    async def connect_all(self):
        """Connect all available connectors."""
        for platform, connector in self.connectors.items():
            try:
                await connector.connect()
                self.logger.info(f"Connected to {platform}")
            except Exception as e:
                self.logger.error(f"Failed to connect to {platform}: {e}")
                # Remove failed connector to prevent issues
                del self.connectors[platform]
    
    async def disconnect_all(self):
        """Disconnect all connectors gracefully."""
        for platform, connector in self.connectors.items():
            try:
                await connector.disconnect()
                self.logger.info(f"Disconnected from {platform}")
            except Exception as e:
                self.logger.error(f"Error disconnecting from {platform}: {e}")
    
    # --- MISSION PROFILE 1: DEEP SCAN (Telegram) ---
    async def get_n_posts(self, channel_username: str, limit: int):
        """
        Fetches the last N logical posts from a single Telegram source.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'telegram' not in self.connectors:
            self.logger.error("Telegram connector not available")
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
            self.logger.warning(f"WARNING: Fetch from @{channel_username} timed out after {self.GLOBAL_TIMEOUT_SECONDS}s")
            return []
        except Exception as e:
            self.logger.error(f"ERROR: Critical failure fetching from @{channel_username}: {str(e)}")
            return []
    
    # --- MISSION PROFILE 2 & 3: BRIEFINGS (Telegram) ---
    async def get_briefing_posts(self, channels: list, days: int):
        """
        Fetches all posts from a list of Telegram sources for the last N days.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'telegram' not in self.connectors:
            self.logger.error("Telegram connector not available")
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
            self.logger.warning(f"WARNING: Briefing fetch from {len(channels)} channels timed out after {self.GLOBAL_TIMEOUT_SECONDS * len(channels)}s")
            return []
        except Exception as e:
            self.logger.error(f"ERROR: Critical failure fetching briefing from channels: {str(e)}")
            return []
    
    # --- RSS MISSIONS (Enhanced in v2.3 with Citadel protection) ---
    async def analyze_rss_feed(self, feed_url: str):
        """
        Analyze an RSS/Atom feed and return metadata including available entry count.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'rss' not in self.connectors:
            self.logger.error("RSS connector not available")
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
            self.logger.warning(f"WARNING: RSS feed analysis of {feed_url} timed out after {self.GLOBAL_TIMEOUT_SECONDS}s")
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
            self.logger.error(f"ERROR: Critical failure analyzing RSS feed {feed_url}: {str(e)}")
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
            self.logger.error("RSS connector not available")
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
            self.logger.warning(f"WARNING: RSS fetch from {feed_url} timed out after {self.GLOBAL_TIMEOUT_SECONDS}s")
            return []
        except Exception as e:
            self.logger.error(f"ERROR: Critical failure fetching RSS posts from {feed_url}: {str(e)}")
            return []
    
    async def get_multi_rss_posts(self, feed_urls: list, limit_per_feed: int):
        """
        Fetch N posts from multiple RSS/Atom feeds.
        HARDENED: Protected by global timeout and comprehensive error handling.
        Individual feed failures do not affect other feeds.
        """
        if 'rss' not in self.connectors:
            self.logger.error("RSS connector not available")
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
                    self.logger.info(f"Successfully fetched {len(posts)} posts from {feed_url}")
                else:
                    failed_feeds += 1
                    self.logger.warning(f"No posts retrieved from {feed_url}")
                    
            except asyncio.TimeoutError:
                failed_feeds += 1
                self.logger.warning(f"WARNING: RSS fetch from {feed_url} timed out after {self.GLOBAL_TIMEOUT_SECONDS}s")
                continue  # Continue processing other feeds
                
            except Exception as e:
                failed_feeds += 1
                self.logger.error(f"ERROR: Failed to fetch from {feed_url}: {str(e)}")
                continue  # Continue processing other feeds
        
        self.logger.info(f"Multi-RSS operation complete: {successful_feeds} successful, {failed_feeds} failed feeds")
        
        # Sort by timestamp for unified timeline
        try:
            return sorted(all_posts, key=lambda p: p.get('date', datetime.min), reverse=True)
        except Exception as e:
            self.logger.error(f"Error sorting multi-RSS posts: {e}")
            return all_posts
    
    # --- YOUTUBE MISSIONS (New in v2.4 "The Spymaster") ---
    async def get_youtube_transcript(self, video_url: str):
        """
        Fetch transcript from a single YouTube video.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'youtube' not in self.connectors:
            self.logger.error("YouTube connector not available")
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
            self.logger.warning(f"WARNING: YouTube transcript fetch from {video_url} timed out after {self.GLOBAL_TIMEOUT_SECONDS}s")
            return []
        except Exception as e:
            self.logger.error(f"ERROR: Critical failure fetching YouTube transcript from {video_url}: {str(e)}")
            return []
    
    async def get_youtube_channel_transcripts(self, channel_identifier: str, limit: int):
        """
        Fetch transcripts from the latest N videos in a YouTube channel.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'youtube' not in self.connectors:
            self.logger.error("YouTube connector not available")
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
            self.logger.warning(f"WARNING: YouTube channel transcript fetch from {channel_identifier} timed out after {self.GLOBAL_TIMEOUT_SECONDS * 2}s")
            return []
        except Exception as e:
            self.logger.error(f"ERROR: Critical failure fetching YouTube channel transcripts from {channel_identifier}: {str(e)}")
            return []
    
    async def get_youtube_playlist_transcripts(self, playlist_url: str, limit: int):
        """
        BONUS: Fetch transcripts from a YouTube playlist.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'youtube' not in self.connectors:
            self.logger.error("YouTube connector not available")
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
            self.logger.warning(f"WARNING: YouTube playlist transcript fetch from {playlist_url} timed out after {self.GLOBAL_TIMEOUT_SECONDS * 3}s")
            return []
        except Exception as e:
            self.logger.error(f"ERROR: Critical failure fetching YouTube playlist transcripts from {playlist_url}: {str(e)}")
            return []
    
    async def search_youtube_transcripts(self, search_query: str, limit: int):
        """
        BONUS: Search for YouTube videos and extract their transcripts.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'youtube' not in self.connectors:
            self.logger.error("YouTube connector not available")
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
            self.logger.warning(f"WARNING: YouTube search for '{search_query}' timed out after {self.GLOBAL_TIMEOUT_SECONDS * 2}s")
            return []
        except Exception as e:
            self.logger.error(f"ERROR: Critical failure searching YouTube for '{search_query}': {str(e)}")
            return []
    
    # --- REDDIT MISSIONS (v2.6 "The Crowd Crier") ---
    async def get_reddit_post_with_comments(self, post_url: str):
        """
        Fetch a single Reddit post with all its comments.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'reddit' not in self.connectors:
            self.logger.error("Reddit connector not available")
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
            self.logger.warning(f"WARNING: Reddit post fetch from '{post_url}' timed out after {self.GLOBAL_TIMEOUT_SECONDS * 2}s")
            return []
        except Exception as e:
            self.logger.error(f"ERROR: Critical failure fetching Reddit post '{post_url}': {str(e)}")
            return []
    
    async def get_posts_from_subreddit(self, subreddit: str, limit: int = 10, sort: str = 'hot'):
        """
        Fetch posts from a subreddit with interactive selection.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'reddit' not in self.connectors:
            self.logger.error("Reddit connector not available")
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
            self.logger.warning(f"WARNING: Reddit subreddit fetch from 'r/{subreddit}' timed out after {self.GLOBAL_TIMEOUT_SECONDS * 3}s")
            return []
        except Exception as e:
            self.logger.error(f"ERROR: Critical failure fetching Reddit subreddit 'r/{subreddit}': {str(e)}")
            return []
    
    async def get_posts_from_multiple_subreddits(self, subreddits: list, limit_per_subreddit: int = 5):
        """
        Fetch posts from multiple subreddits.
        HARDENED: Protected by global timeout and comprehensive error handling.
        """
        if 'reddit' not in self.connectors:
            self.logger.error("Reddit connector not available")
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
                    self.logger.warning(f"No posts retrieved from r/{subreddit}")
                    
            except asyncio.TimeoutError:
                failed_subreddits += 1
                self.logger.warning(f"WARNING: Reddit subreddit r/{subreddit} timed out after {self.GLOBAL_TIMEOUT_SECONDS}s")
            except Exception as e:
                failed_subreddits += 1
                self.logger.error(f"ERROR: Failed to fetch from r/{subreddit}: {str(e)}")
        
        self.logger.info(f"Reddit multi-subreddit mission: {successful_subreddits} successful, {failed_subreddits} failed")
        return all_posts
    
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
            ConsoleOutput.display_startup_banner(available_connectors, self.GLOBAL_TIMEOUT_SECONDS)
            ConsoleOutput.display_mission_menu()
            
            mission_choice = input("\nEnter mission number (1-14): ")

            # Enhanced error reporting for user feedback - moved to ConsoleOutput
            # Telegram missions (enhanced with JSON output)
            if mission_choice in ['1', '2', '3']:
                if 'telegram' not in self.connectors:
                    print("❌ Telegram connector not available. Please check your .env configuration.")
                    return
                
                if mission_choice == '1':
                    channel = input("\nEnter the target channel username: ")
                    limit = int(input("How many posts to retrieve? "))
                    
                    ConsoleOutput.display_output_format_menu()
                    output_choice = input("Enter format number (1-7): ")

                    posts = await self.get_n_posts(channel, limit)
                    title = f"{limit} posts from @{channel}"

                    if output_choice in ['1', '4', '5', '7']:
                        ConsoleOutput.render_report_to_console(posts, title)
                    
                    if output_choice in ['2', '4', '6', '7']:
                        html_output = HTMLOutput(f"I.N.S.I.G.H.T. Deep Scan: {title}")
                        html_output.render_report(posts)
                        html_output.save_to_file(f"deep_scan_{channel.lstrip('@')}.html")
                    
                    if output_choice in ['3', '5', '6', '7']:
                        json_output = JSONOutput()
                        mission_context = json_output.create_mission_summary(posts, f"Deep Scan @{channel}", [channel])
                        filename = json_output.export_to_file(posts, f"deep_scan_{channel.lstrip('@')}.json", mission_context=mission_context)
                        print(f"\n📁 JSON export saved to: {filename}")
                        print("🔄 This file is ready for Mark III 'Scribe' processing.")
                    
                    # Report mission outcome
                    ConsoleOutput.report_mission_outcome(len(posts), 1, f"Deep Scan @{channel}")
                
                elif mission_choice in ['2', '3']:
                    days = 0
                    if mission_choice == '2':
                        title_prefix = "Historical Briefing"
                        days = int(input("How many days of history to include? "))
                    else: # mission_choice == '3'
                        title_prefix = "End of Day Report"
                    
                    channels_str = input("Enter channel usernames, separated by commas: ")
                    channels = [c.strip() for c in channels_str.split(',')]
                    
                    ConsoleOutput.display_output_format_menu()
                    output_choice = input("Enter format number (1-7): ")
                    
                    all_posts = await self.get_briefing_posts(channels, days)
                    
                    title = f"{title_prefix} for {', '.join(channels)}"
                    
                    if output_choice in ['1', '4', '5', '7']:
                        ConsoleOutput.render_briefing_to_console(all_posts, title)
                    
                    if output_choice in ['2', '4', '6', '7']:
                        # Prepare data for HTML output
                        html_output = HTMLOutput()
                        briefing_data_for_html = {channel: [] for channel in channels}
                        for post in all_posts:
                            briefing_data_for_html[post['source']].append(post)

                        html_output.render_briefing(briefing_data_for_html, days)
                        
                        filename_date = datetime.now().strftime('%Y-%m-%d')
                        filename = f"briefing_{filename_date}.html"
                        html_output.save_to_file(filename)
                    
                    if output_choice in ['3', '5', '6', '7']:
                        json_output = JSONOutput()
                        mission_context = json_output.create_mission_summary(all_posts, title, channels)
                        filename_date = datetime.now().strftime('%Y%m%d')
                        filename = json_output.export_to_file(all_posts, f"briefing_{filename_date}.json", mission_context=mission_context)
                        print(f"\n📁 JSON export saved to: {filename}")
                        print("🔄 This file is ready for Mark III 'Scribe' processing.")
                    
                    # Report mission outcome
                    ConsoleOutput.report_mission_outcome(len(all_posts), len(channels), title_prefix)
            
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
                    ConsoleOutput.render_feed_info(feed_info)
                
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
                    
                    ConsoleOutput.display_output_format_menu()
                    output_choice = input("Enter format number (1-7): ")
                    
                    posts = await self.get_rss_posts(feed_url, limit)
                    title = f"{limit} posts from {feed_info['title']}"
                    
                    if output_choice in ['1', '4', '5', '7']:
                        ConsoleOutput.render_report_to_console(posts, title)
                    
                    if output_choice in ['2', '4', '6', '7']:
                        html_output = HTMLOutput(f"I.N.S.I.G.H.T. RSS Scan: {title}")
                        html_output.render_rss_briefing(posts, title)
                        
                        # Create safe filename from feed title
                        safe_name = "".join(c for c in feed_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        safe_name = safe_name.replace(' ', '_')[:50]  # Limit length
                        html_output.save_to_file(f"rss_scan_{safe_name}.html")
                    
                    if output_choice in ['3', '5', '6', '7']:
                        safe_name = "".join(c for c in feed_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        safe_name = safe_name.replace(' ', '_')[:50]
                        json_output = JSONOutput()
                        mission_context = json_output.create_mission_summary(posts, f"RSS Scan - {feed_info['title']}", [feed_info['title']])
                        filename = json_output.export_to_file(posts, f"rss_scan_{safe_name}.json", mission_context=mission_context)
                        print(f"\n📁 JSON export saved to: {filename}")
                        print("🔄 This file is ready for Mark III 'Scribe' processing.")
                    
                    # Report mission outcome
                    ConsoleOutput.report_mission_outcome(len(posts), 1, f"RSS Scan - {feed_info['title']}")
                
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
                    
                    ConsoleOutput.display_output_format_menu()
                    output_choice = input("Enter format number (1-7): ")
                    
                    posts = await self.get_multi_rss_posts(feed_urls, limit_per_feed)
                    title = f"Multi-RSS scan: {limit_per_feed} posts from {len(feed_urls)} feeds"
                    
                    if output_choice in ['1', '4', '5', '7']:
                        ConsoleOutput.render_briefing_to_console(posts, title)
                    
                    if output_choice in ['2', '4', '6', '7']:
                        html_output = HTMLOutput(f"I.N.S.I.G.H.T. Multi-RSS Briefing")
                        html_output.render_rss_briefing(posts, title)
                        
                        filename_date = datetime.now().strftime('%Y-%m-%d')
                        html_output.save_to_file(f"multi_rss_briefing_{filename_date}.html")
                    
                    if output_choice in ['3', '5', '6', '7']:
                        json_output = JSONOutput()
                        mission_context = json_output.create_mission_summary(posts, title, [f.split('/')[-1] for f in feed_urls])
                        filename_date = datetime.now().strftime('%Y%m%d')
                        filename = json_output.export_to_file(posts, f"multi_rss_briefing_{filename_date}.json", mission_context=mission_context)
                        print(f"\n📁 JSON export saved to: {filename}")
                        print("🔄 This file is ready for Mark III 'Scribe' processing.")
                    
                    # Report mission outcome
                    ConsoleOutput.report_mission_outcome(len(posts), len(feed_urls), "Multi-RSS Scan")
            
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
                        ConsoleOutput.render_report_to_console(posts, title)
                        json_output = JSONOutput()
                        mission_context = json_output.create_mission_summary(posts, title, [video_url])
                        filename = json_output.export_to_file(posts, f"youtube_transcript_{video_url.replace('/', '_')}.json", mission_context=mission_context)
                        print(f"\n📁 JSON export saved to: {filename}")
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
                        ConsoleOutput.render_briefing_to_console(posts, title)
                        json_output = JSONOutput()
                        mission_context = json_output.create_mission_summary(posts, title, [channel_identifier])
                        filename = json_output.export_to_file(posts, f"youtube_channel_transcripts_{channel_identifier.replace('/', '_')}.json", mission_context=mission_context)
                        print(f"\n📁 JSON export saved to: {filename}")
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
                        ConsoleOutput.render_briefing_to_console(posts, title)
                        json_output = JSONOutput()
                        mission_context = json_output.create_mission_summary(posts, title, [playlist_url])
                        filename = json_output.export_to_file(posts, f"youtube_playlist_transcripts_{playlist_url.replace('/', '_')}.json", mission_context=mission_context)
                        print(f"\n📁 JSON export saved to: {filename}")
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
                        ConsoleOutput.render_briefing_to_console(posts, title)
                        json_output = JSONOutput()
                        mission_context = json_output.create_mission_summary(posts, title, [search_query])
                        filename = json_output.export_to_file(posts, f"youtube_search_{search_query.replace(' ', '_')}.json", mission_context=mission_context)
                        print(f"\n📁 JSON export saved to: {filename}")
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
                    
                    ConsoleOutput.display_output_format_menu()
                    output_choice = input("Enter format number (1-7): ")
                    
                    posts = await self.get_reddit_post_with_comments(post_url)
                    title = f"Reddit Post Analysis: {post_url}"
                    
                    if posts:
                        if output_choice in ['1', '4', '5', '7']:
                            ConsoleOutput.render_report_to_console(posts, title)
                        
                        if output_choice in ['2', '4', '6', '7']:
                            html_output = HTMLOutput(f"I.N.S.I.G.H.T. Reddit Post Analysis: {title}")
                            html_output.render_report(posts)
                            safe_url = post_url.replace('/', '_').replace('.', '_').replace(':', '_')
                            html_output.save_to_file(f"reddit_post_analysis_{safe_url}.html")
                        
                        if output_choice in ['3', '5', '6', '7']:
                            json_output = JSONOutput()
                            mission_context = json_output.create_mission_summary(posts, title, [post_url])
                            filename = json_output.export_to_file(posts, f"reddit_post_analysis_{safe_url}.json", mission_context=mission_context)
                            print(f"\n📁 JSON export saved to: {filename}")
                            print("🔄 This file is ready for Mark III 'Scribe' processing.")
                        
                        # Report mission outcome
                        ConsoleOutput.report_mission_outcome(len(posts), 1, "Reddit Post Analysis")
                    else:
                        print("\n❌ No comments found for the given post URL.")
                
                elif mission_choice == '13':
                    # Reddit Subreddit Explorer
                    subreddit = input("\nEnter Reddit subreddit name: ")
                    print(f"\n🔍 Exploring posts from subreddit: {subreddit}")
                    
                    ConsoleOutput.display_output_format_menu()
                    output_choice = input("Enter format number (1-7): ")
                    
                    posts = await self.get_posts_from_subreddit(subreddit)
                    title = f"Reddit Posts from {subreddit}"
                    
                    if posts:
                        if output_choice in ['1', '4', '5', '7']:
                            ConsoleOutput.render_briefing_to_console(posts, title)
                        
                        if output_choice in ['2', '4', '6', '7']:
                            html_output = HTMLOutput(f"I.N.S.I.G.H.T. Reddit Subreddit Explorer: {title}")
                            html_output.render_briefing({subreddit: posts}, 0)  # 0 days for current posts
                            html_output.save_to_file(f"reddit_subreddit_{subreddit.replace('/', '_')}.html")
                        
                        if output_choice in ['3', '5', '6', '7']:
                            json_output = JSONOutput()
                            mission_context = json_output.create_mission_summary(posts, title, [subreddit])
                            filename = json_output.export_to_file(posts, f"reddit_subreddit_explorer_{subreddit.replace('/', '_')}.json", mission_context=mission_context)
                            print(f"\n📁 JSON export saved to: {filename}")
                            print("🔄 This file is ready for Mark III 'Scribe' processing.")
                        
                        # Report mission outcome
                        ConsoleOutput.report_mission_outcome(len(posts), 1, f"Reddit Subreddit Explorer - {subreddit}")
                    else:
                        print("\n❌ No posts found for the given subreddit.")
                
                elif mission_choice == '14':
                    # Reddit Multi-Source Briefing
                    subreddits_str = input("\nEnter Reddit subreddits, separated by commas: ")
                    subreddits = [sr.strip() for sr in subreddits_str.split(',')]
                    
                    ConsoleOutput.display_output_format_menu()
                    output_choice = input("Enter format number (1-7): ")
                    
                    print(f"\n🔍 Fetching posts from {len(subreddits)} subreddits...")
                    posts = await self.get_posts_from_multiple_subreddits(subreddits)
                    title = f"Reddit Multi-Source Briefing: {', '.join(subreddits)}"
                    
                    if posts:
                        if output_choice in ['1', '4', '5', '7']:
                            ConsoleOutput.render_briefing_to_console(posts, title)
                        
                        if output_choice in ['2', '4', '6', '7']:
                            html_output = HTMLOutput(f"I.N.S.I.G.H.T. Reddit Multi-Source Briefing")
                            # Organize posts by subreddit for HTML rendering
                            briefing_data_for_html = {sr: [] for sr in subreddits}
                            for post in posts:
                                subreddit_name = post.get('subreddit', 'unknown')
                                if subreddit_name in briefing_data_for_html:
                                    briefing_data_for_html[subreddit_name].append(post)
                            
                            html_output.render_briefing(briefing_data_for_html, 0)
                            
                            filename_date = datetime.now().strftime('%Y-%m-%d')
                            html_output.save_to_file(f"reddit_multi_source_briefing_{filename_date}.html")
                        
                        if output_choice in ['3', '5', '6', '7']:
                            json_output = JSONOutput()
                            mission_context = json_output.create_mission_summary(posts, title, subreddits)
                            filename = json_output.export_to_file(posts, f"reddit_multi_source_briefing_{'_'.join(subreddits).replace('/', '_')}.json", mission_context=mission_context)
                            print(f"\n📁 JSON export saved to: {filename}")
                            print("🔄 This file is ready for Mark III 'Scribe' processing.")
                        
                        # Report mission outcome
                        ConsoleOutput.report_mission_outcome(len(posts), len(subreddits), "Reddit Multi-Source Briefing")
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
                    json_output = JSONOutput()
                    mission_context = json_output.create_mission_summary(test_posts, "Mark III Compatibility Test", [f"{p.get('platform', 'unknown')} ({p.get('source', 'unknown')})" for p in test_posts])
                    filename = json_output.export_to_file(test_posts, "mark_iii_compatibility_test.json", mission_context=mission_context)
                    print(f"\n🎯 Test JSON export created: {filename}")
                    print("\n📋 JSON Export Summary:")
                    print(f"   • Total posts: {len(test_posts)}")
                    print(f"   • Platforms included: {', '.join(set(p.get('platform', 'unknown') for p in test_posts))}")
                    print(f"   • Format version: 2.4.0")
                    print(f"   • Mark III ready: ✅")
                    print(f"   • Mark IV ready: ✅")
                    
                    print("\n🔍 Would you like to view the JSON structure? (y/n): ", end="")
                    if input().lower() == 'y':
                        with open(filename, 'r', encoding='utf-8') as f:
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

            self.logger.info("Mission complete.")

        except Exception as e:
            self.logger.critical(f"A critical error occurred: {e}", exc_info=True)
        finally:
            await self.disconnect_all()

# --- Execution ---
if __name__ == "__main__":

    debug_mode = '--debug' in sys.argv

    app = InsightOperator(debug_mode=debug_mode)
    asyncio.run(app.run())