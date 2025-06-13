import os
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from connectors import TelegramConnector
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
    I.N.S.I.G.H.T. Mark II (v2.0) - The Inquisitor Platform
    
    The modular intelligence platform that can gather intel from multiple sources.
    This version maintains 100% backward compatibility with Mark I while introducing
    a connector-based architecture that enables multi-source intelligence gathering.
    
    Architecture:
    - Orchestrator pattern for connector management
    - Unified data model for cross-platform compatibility  
    - Preserved user interface for seamless transition
    """
    
    def __init__(self):
        logging.info("I.N.S.I.G.H.T. Mark II (v2.0) - The Inquisitor - Initializing...")
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
        
        # Future connectors will be registered here:
        # self.connectors['rss'] = RssConnector()
        # self.connectors['youtube'] = YouTubeConnector()
    
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
    
    # --- MISSION PROFILE 1: DEEP SCAN ---
    async def get_n_posts(self, channel_username: str, limit: int):
        """
        Fetches the last N logical posts from a single source.
        
        For now, this assumes Telegram sources, but the architecture 
        supports auto-detection of source type in future versions.
        """
        # For Mark II v2.0, we assume Telegram sources
        # Future versions will auto-detect source type
        if 'telegram' not in self.connectors:
            logging.error("Telegram connector not available")
            return []
        
        connector = self.connectors['telegram']
        return await connector.fetch_posts(channel_username, limit)
    
    # --- MISSION PROFILE 2 & 3: BRIEFINGS ---
    async def get_briefing_posts(self, channels: list, days: int):
        """
        Fetches all posts from a list of sources for the last N days,
        and returns them as a single, chronologically sorted list.
        
        This method supports multi-source briefings, though Mark II v2.0
        focuses on Telegram sources for architectural compatibility.
        """
        # For Mark II v2.0, we assume all sources are Telegram
        # Future versions will route to appropriate connectors based on source type
        if 'telegram' not in self.connectors:
            logging.error("Telegram connector not available")
            return []
        
        connector = self.connectors['telegram']
        return await connector.fetch_posts_by_timeframe(channels, days)
    
    # --- RENDER METHODS (Preserved from Mark I for backward compatibility) ---
    def render_report_to_console(self, posts: list, title: str):
        """A generic renderer for a list of posts, providing full details."""
        print("\n" + "#"*25 + f" I.N.S.I.G.H.T. REPORT: {title.upper()} " + "#"*25)
        if not posts:
            print("\nNo displayable posts found for this report.")
        
        for i, post_data in enumerate(posts):
            media_count = len(post_data['media_urls'])
            media_indicator = f"[+{media_count} MEDIA]" if media_count > 0 else ""
            
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
        """Renders a chronologically sorted briefing, grouping posts by day."""
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
                
                print(f"\n--- [{post_data['date'].strftime('%H:%M:%S')}] From: @{post_data['channel']} (ID: {post_data['id']}) {media_indicator} ---")
                print(post_data['text'])
                print(f"Post Link: {post_data['link']}")

                if post_data['media_urls']:
                    print("Media Links:")
                    for url in post_data['media_urls']:
                        print(f"  - {url}")
                print("-" * 60)

        print("\n" + "#"*30 + " END OF BRIEFING " + "#"*30)

    # --- MAIN EXECUTION LOOP (Preserved interface from Mark I) ---
    async def run(self):
        """
        The main execution flow with preserved mission choices.
        
        This maintains the exact same user interface as Mark I while
        leveraging the new modular architecture under the hood.
        """
        try:
            await self.connect_all()
            
            if not self.connectors:
                print("\nNo connectors available. Please check your configuration.")
                return
            
            print("\nI.N.S.I.G.H.T. Mark II - The Inquisitor - Operator Online.")
            print("Choose your mission:")
            print("1. Deep Scan (Get last N posts from one channel)")
            print("2. Historical Briefing (Get posts from the last N days from multiple channels)")
            print("3. End of Day Briefing (Get all of today's posts from multiple channels)")
            mission_choice = input("Enter mission number (1, 2, or 3): ")

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