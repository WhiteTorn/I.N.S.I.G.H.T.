import os
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from connectors import TelegramConnector, RssConnector
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
    I.N.S.I.G.H.T. Mark II (v2.1) - The Inquisitor Platform
    
    The modular intelligence platform that can gather intel from multiple sources.
    Version 2.1 adds RSS feed support with dedicated missions for testing
    RSS functionality independently before multi-source integration.
    
    Architecture:
    - Orchestrator pattern for connector management
    - Unified data model for cross-platform compatibility  
    - Preserved user interface for seamless transition
    - Independent connector testing capabilities
    """
    
    def __init__(self):
        logging.info("I.N.S.I.G.H.T. Mark II (v2.1) - The Inquisitor - Initializing...")
        load_dotenv()
        
        # Initialize available connectors
        self.connectors = {}
        self._setup_connectors()
        
        logging.info("Mark II Orchestrator ready.")
    
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
        """
        if 'telegram' not in self.connectors:
            logging.error("Telegram connector not available")
            return []
        
        connector = self.connectors['telegram']
        return await connector.fetch_posts(channel_username, limit)
    
    # --- MISSION PROFILE 2 & 3: BRIEFINGS (Telegram) ---
    async def get_briefing_posts(self, channels: list, days: int):
        """
        Fetches all posts from a list of Telegram sources for the last N days.
        """
        if 'telegram' not in self.connectors:
            logging.error("Telegram connector not available")
            return []
        
        connector = self.connectors['telegram']
        return await connector.fetch_posts_by_timeframe(channels, days)
    
    # --- NEW RSS MISSIONS ---
    async def analyze_rss_feed(self, feed_url: str):
        """
        Analyze an RSS feed and return metadata including available entry count.
        """
        if 'rss' not in self.connectors:
            logging.error("RSS connector not available")
            return None
        
        connector = self.connectors['rss']
        return await connector.get_feed_info(feed_url)
    
    async def get_rss_posts(self, feed_url: str, limit: int):
        """
        Fetch N posts from a single RSS feed.
        """
        if 'rss' not in self.connectors:
            logging.error("RSS connector not available")
            return []
        
        connector = self.connectors['rss']
        return await connector.fetch_posts(feed_url, limit)
    
    async def get_multi_rss_posts(self, feed_urls: list, limit_per_feed: int):
        """
        Fetch N posts from multiple RSS feeds.
        """
        if 'rss' not in self.connectors:
            logging.error("RSS connector not available")
            return []
        
        connector = self.connectors['rss']
        all_posts = []
        
        for feed_url in feed_urls:
            posts = await connector.fetch_posts(feed_url, limit_per_feed)
            all_posts.extend(posts)
        
        # Sort by timestamp for unified timeline
        return sorted(all_posts, key=lambda p: p['timestamp'], reverse=True)
    
    # --- RENDER METHODS (Enhanced for RSS) ---
    def render_report_to_console(self, posts: list, title: str):
        """A generic renderer for a list of posts, supporting both Telegram and RSS."""
        print("\n" + "#"*25 + f" I.N.S.I.G.H.T. REPORT: {title.upper()} " + "#"*25)
        if not posts:
            print("\nNo displayable posts found for this report.")
        
        for i, post_data in enumerate(posts):
            media_count = len(post_data['media_urls'])
            media_indicator = f"[+{media_count} MEDIA]" if media_count > 0 else ""
            
            # Handle RSS-specific fields
            if post_data.get('source_platform') == 'rss':
                title_field = post_data.get('title', 'No title')
                feed_title = post_data.get('feed_title', 'Unknown Feed')
                print(f"\n--- Post {i+1}/{len(posts)} | {title_field} | From: {feed_title} | Date: {post_data['date'].strftime('%Y-%m-%d %H:%M:%S')} {media_indicator} ---")
            else:
                print(f"\n--- Post {i+1}/{len(posts)} | ID: {post_data['id']} | Date: {post_data['date'].strftime('%Y-%m-%d %H:%M:%S')} {media_indicator} ---")
            
            print(post_data['text'])
            print(f"Post Link: {post_data['link']}")

            if post_data['media_urls']:
                print("Media Links:")
                for url in post_data['media_urls']:
                    print(f"  - {url}")
            print("-" * 60)
        print("\n" + "#"*30 + " END OF REPORT " + "#"*30)

    def render_briefing_to_console(self, posts: list, title: str):
        """Renders a chronologically sorted briefing, supporting both platforms."""
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
                media_count = len(post_data['media_urls'])
                media_indicator = f"[+{media_count} MEDIA]" if media_count > 0 else ""
                
                # Handle different source types
                if post_data.get('source_platform') == 'rss':
                    feed_title = post_data.get('feed_title', 'RSS Feed')
                    print(f"\n--- [{post_data['date'].strftime('%H:%M:%S')}] From: {feed_title} (RSS) {media_indicator} ---")
                else:
                    print(f"\n--- [{post_data['date'].strftime('%H:%M:%S')}] From: @{post_data['channel']} (ID: {post_data['id']}) {media_indicator} ---")
                
                print(post_data['text'])
                print(f"Post Link: {post_data['link']}")

                if post_data['media_urls']:
                    print("Media Links:")
                    for url in post_data['media_urls']:
                        print(f"  - {url}")
                print("-" * 60)

        print("\n" + "#"*30 + " END OF BRIEFING " + "#"*30)

    def render_feed_info(self, feed_info: dict):
        """Render RSS feed analysis information."""
        print("\n" + "#"*25 + " RSS FEED ANALYSIS " + "#"*25)
        
        if feed_info['status'] == 'error':
            print(f"❌ Error analyzing feed: {feed_info['error']}")
            return
        
        print(f"📰 Feed Title: {feed_info['title']}")
        print(f"🌐 URL: {feed_info['url']}")
        print(f"📝 Description: {feed_info['description']}")
        print(f"🔗 Website: {feed_info['link']}")
        print(f"🌍 Language: {feed_info['language']}")
        print(f"📊 Total Entries Available: {feed_info['total_entries']}")
        print(f"🕒 Last Updated: {feed_info['last_updated']}")
        print("\n" + "#"*30 + " END OF ANALYSIS " + "#"*30)

    # --- ENHANCED MAIN EXECUTION LOOP ---
    async def run(self):
        """
        The main execution flow with RSS testing missions.
        """
        try:
            await self.connect_all()
            
            if not self.connectors:
                print("\nNo connectors available. Please check your configuration.")
                return
            
            available_connectors = list(self.connectors.keys())
            print(f"\nI.N.S.I.G.H.T. Mark II (v2.1) - The Inquisitor - Operator Online.")
            print(f"Available connectors: {', '.join(available_connectors)}")
            print("\nChoose your mission:")
            print("\n--- TELEGRAM MISSIONS ---")
            print("1. Deep Scan (Get last N posts from one Telegram channel)")
            print("2. Historical Briefing (Get posts from the last N days from multiple Telegram channels)")
            print("3. End of Day Briefing (Get all of today's posts from multiple Telegram channels)")
            print("\n--- RSS MISSIONS ---")
            print("4. RSS Feed Analysis (Analyze a single RSS feed)")
            print("5. RSS Single Feed Scan (Get N posts from a single RSS feed)")
            print("6. RSS Multi-Feed Scan (Get N posts from multiple RSS feeds)")
            
            mission_choice = input("\nEnter mission number (1-6): ")

            # Telegram missions (preserved from v2.0)
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
                    print("3. Both Console and HTML")
                    output_choice = input("Enter format number (1, 2, or 3): ")

                    posts = await self.get_n_posts(channel, limit)
                    title = f"{limit} posts from @{channel}"

                    if output_choice in ['1', '3']:
                        self.render_report_to_console(posts, title)
                    
                    if output_choice in ['2', '3']:
                        html_dossier = HTMLRenderer(f"I.N.S.I.G.H.T. Deep Scan: {title}")
                        html_dossier.render_report(posts)
                        html_dossier.save_to_file(f"deep_scan_{channel.lstrip('@')}.html")
                
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
                    print("3. Both Console and HTML")
                    output_choice = input("Enter format number (1, 2, or 3): ")
                    
                    all_posts = await self.get_briefing_posts(channels, days)
                    
                    title = f"{title_prefix} for {', '.join(channels)}"
                    
                    if output_choice in ['1', '3']:
                        self.render_briefing_to_console(all_posts, title)
                    
                    if output_choice in ['2', '3']:
                        # Prepare data for HTML renderer
                        html_renderer = HTMLRenderer()
                        briefing_data_for_html = {channel: [] for channel in channels}
                        for post in all_posts:
                            briefing_data_for_html[post['channel']].append(post)

                        html_renderer.render_briefing(briefing_data_for_html, days)
                        
                        filename_date = datetime.now().strftime('%Y-%m-%d')
                        filename = f"briefing_{filename_date}.html"
                        html_renderer.save_to_file(filename)
            
            # RSS missions (new in v2.1)
            elif mission_choice in ['4', '5', '6']:
                if 'rss' not in self.connectors:
                    print("❌ RSS connector not available.")
                    return
                
                if mission_choice == '4':
                    # RSS Feed Analysis
                    feed_url = input("\nEnter RSS feed URL: ")
                    print(f"\n🔍 Analyzing RSS feed: {feed_url}")
                    
                    feed_info = await self.analyze_rss_feed(feed_url)
                    self.render_feed_info(feed_info)
                
                elif mission_choice == '5':
                    # RSS Single Feed Scan
                    feed_url = input("\nEnter RSS feed URL: ")
                    
                    # First, analyze the feed to show available entries
                    print(f"\n🔍 Analyzing feed...")
                    feed_info = await self.analyze_rss_feed(feed_url)
                    
                    if feed_info['status'] == 'error':
                        print(f"❌ Cannot access feed: {feed_info['error']}")
                        return
                    
                    print(f"📊 Feed '{feed_info['title']}' has {feed_info['total_entries']} entries available")
                    limit = int(input(f"How many posts to retrieve (max {feed_info['total_entries']})? "))
                    
                    posts = await self.get_rss_posts(feed_url, limit)
                    title = f"{limit} posts from {feed_info['title']}"
                    
                    self.render_report_to_console(posts, title)
                
                elif mission_choice == '6':
                    # RSS Multi-Feed Scan
                    feeds_str = input("\nEnter RSS feed URLs, separated by commas: ")
                    feed_urls = [url.strip() for url in feeds_str.split(',')]
                    
                    # Analyze each feed first
                    print(f"\n🔍 Analyzing {len(feed_urls)} feeds...")
                    for feed_url in feed_urls:
                        feed_info = await self.analyze_rss_feed(feed_url)
                        if feed_info['status'] == 'success':
                            print(f"✅ {feed_info['title']}: {feed_info['total_entries']} entries")
                        else:
                            print(f"❌ {feed_url}: Error - {feed_info['error']}")
                    
                    limit_per_feed = int(input("\nHow many posts per feed to retrieve? "))
                    
                    posts = await self.get_multi_rss_posts(feed_urls, limit_per_feed)
                    title = f"Multi-RSS scan: {limit_per_feed} posts from {len(feed_urls)} feeds"
                    
                    self.render_briefing_to_console(posts, title)
            
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