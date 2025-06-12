import os
import logging
import asyncio
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError

# NEW: Import our dedicated HTML renderer
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

# --- The Core Application Class ---

class InsightOperator:
    """
    I.N.S.I.G.H.T. Mark I (v1.8) - The High-Fidelity Operator
    The definitive, flexible, and robust version of the Mark I engine.
    Corrects all known bugs and provides full-text, high-fidelity briefings.
    """
    def __init__(self):
        logging.info("I.N.S.I.G.H.T. Mark I (v1.8) Initializing...")
        load_dotenv()
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.session_file = 'insight_session'
        self.client = None
        self.request_counter = 0
        self.REQUEST_THRESHOLD = 15
        self.COOLDOWN_SECONDS = 60

    async def throttle_if_needed(self):
        if self.request_counter >= self.REQUEST_THRESHOLD:
            logging.warning(
                f"Request threshold ({self.REQUEST_THRESHOLD}) reached. "
                f"Initiating {self.COOLDOWN_SECONDS}-second cooldown."
            )
            await asyncio.sleep(self.COOLDOWN_SECONDS)
            self.request_counter = 0
            logging.info("Cooldown complete. Resuming operations.")
        self.request_counter += 1

    async def connect(self):
        self.client = TelegramClient(self.session_file, int(self.api_id), self.api_hash)
        logging.info("Connecting to Telegram...")
        await self.client.connect()
        if not await self.client.is_user_authorized():
            logging.warning("Client not authorized. Please follow prompts for first-time login.")
            phone = input("Enter your phone number: ")
            await self.client.send_code_request(phone)
            try:
                await self.client.sign_in(phone, input("Enter the code you received: "))
            except Exception:
                await self.client.sign_in(password=input("2FA Password Required. Please enter: "))
        logging.info("Connection successful.")

    async def disconnect(self):
        if self.client and self.client.is_connected():
            logging.info("Disconnecting from Telegram...")
            await self.client.disconnect()

    async def _synthesize_messages(self, raw_messages, channel_alias):
        """A private helper method to handle the synthesis logic."""
        synthesized_groups = {}
        for msg in raw_messages:
            if not msg: continue
            group_id = msg.grouped_id or msg.id
            if group_id not in synthesized_groups:
                synthesized_groups[group_id] = {'messages': [], 'text': None, 'main_msg': msg}
            synthesized_groups[group_id]['messages'].append(msg)
            if msg.text:
                synthesized_groups[group_id]['text'] = msg.text
                synthesized_groups[group_id]['main_msg'] = msg

        logical_posts = []
        for group_id, group_data in synthesized_groups.items():
            main_msg = group_data['main_msg']
            text = group_data['text']
            if text:
                media_urls = [f'https://t.me/{channel_alias}/{m.id}?single' for m in group_data['messages'] if m.media]
                post_data = {
                    'id': main_msg.id,
                    'date': main_msg.date,
                    'text': text,
                    'media_urls': media_urls,
                    'link': f'https://t.me/{channel_alias}/{main_msg.id}'
                }
                logical_posts.append(post_data)
        return logical_posts

    # --- MISSION PROFILE 1: DEEP SCAN ---
    async def get_n_posts(self, channel_username: str, limit: int):
        """Fetches the last N logical posts from a single channel."""
        logging.info(f"Starting Deep Scan for {limit} posts from @{channel_username}...")
        all_synthesized_posts = []
        processed_ids = set()
        last_message_id = 0
        fetch_chunk_size = 100
        max_fetches = 20

        try:
            await self.throttle_if_needed()
            entity = await self.client.get_entity(channel_username)
        except Exception as e:
            logging.error(f"Could not resolve channel entity for '{channel_username}': {e}")
            return []

        for i in range(max_fetches):
            if len(all_synthesized_posts) >= limit:
                break
            
            logging.info(f"Fetch attempt #{i+1}...")
            await self.throttle_if_needed()
            try:
                messages = await self.client.get_messages(entity, limit=fetch_chunk_size, offset_id=last_message_id)
                if not messages: break
                
                # BUG FIX: Pass the original channel username for link building
                synthesized = await self._synthesize_messages(messages, channel_username)
                
                for post in synthesized:
                    if post['id'] not in processed_ids:
                        all_synthesized_posts.append(post)
                        processed_ids.add(post['id'])

                last_message_id = messages[-1].id
            except Exception as e:
                logging.error(f"Error during message fetching: {e}")
                break
        
        final_posts = sorted(all_synthesized_posts, key=lambda p: p['id'], reverse=True)[:limit]
        return sorted(final_posts, key=lambda p: p['date'])

    # --- MISSION PROFILE 2: DAILY BRIEFING ---
    async def get_daily_briefing(self, channels: list, days: int):
        """Fetches all posts from a list of channels for the last N days."""
        logging.info(f"Starting Daily Briefing generation for the last {days} days...")
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        briefing_data = {channel: [] for channel in channels}

        for channel in channels:
            logging.info(f"Gathering intel from @{channel}...")
            channel_posts = []
            processed_ids = set()
            try:
                await self.throttle_if_needed()
                entity = await self.client.get_entity(channel)
                async for message in self.client.iter_messages(entity, limit=None):
                    if message.date < cutoff_date: break
                    if message.id in processed_ids: continue
                    
                    synthesized = await self._synthesize_messages([message], channel)
                    if synthesized:
                        channel_posts.extend(synthesized)
                        # For albums, add all message IDs to prevent re-processing
                        if message.grouped_id:
                            group_msgs = await self.client.get_messages(entity, limit=20, offset_id=message.id+10)
                            for m in group_msgs:
                                if m and m.grouped_id == message.grouped_id:
                                    processed_ids.add(m.id)
                        else:
                            processed_ids.add(message.id)
                
                briefing_data[channel] = sorted(channel_posts, key=lambda p: p['date'])
            except Exception as e:
                logging.error(f"Failed to process channel @{channel}: {e}")
        return briefing_data

    # --- RENDER METHODS ---
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

    def render_briefing_to_console(self, briefing_data: dict, days: int):
        """
        Renders the daily briefing with full post content, organized by
        channel and date, without using snippets or recursive calls.
        """
        print("\n" + "#"*25 + f" I.N.S.I.G.H.T. BRIEFING: LAST {days} DAYS " + "#"*25)
        
        # Iterate through each channel in the briefing data
        for channel, posts in briefing_data.items():
            if not posts:
                # Optionally, mention channels with no new posts
                # logging.info(f"No new posts found for @{channel} in the last {days} days.")
                continue
            
            print(f"\n\n{'='*25} INTEL FROM: @{channel.upper()} {'='*25}")
            
            # Group the posts from this channel by day
            posts_by_day = {}
            for post in posts:
                day_str = post['date'].strftime('%Y-%m-%d, %A')
                if day_str not in posts_by_day:
                    posts_by_day[day_str] = []
                posts_by_day[day_str].append(post)
            
            # Render the posts for each day
            for day, day_posts in sorted(posts_by_day.items()):
                print(f"\n{'~'*15} {day} {'~'*15}")
                
                # Now, iterate through the posts for that specific day
                for i, post_data in enumerate(day_posts):
                    media_count = len(post_data['media_urls'])
                    media_indicator = f"[+{media_count} MEDIA]" if media_count > 0 else ""
                    
                    # This is the full post rendering logic, adapted for the briefing format
                    print(f"\n--- Post {i+1}/{len(day_posts)} | ID: {post_data['id']} | Time: {post_data['date'].strftime('%H:%M:%S')} {media_indicator} ---")
                    print(post_data['text'])
                    print(f"Post Link: {post_data['link']}")

                    if post_data['media_urls']:
                        print("Media Links:")
                        for url in post_data['media_urls']:
                            print(f"  - {url}")
                    print("-" * 60)
        
        print("\n\n" + "#"*30 + " END OF BRIEFING " + "#"*30)

    async def run(self):
        """
        The main execution flow, now with user choice for output format.
        """
        try:
            await self.connect()
            
            print("\nI.N.S.I.G.H.T. Operator Online. Choose your mission:")
            print("1. Deep Scan (Get last N posts from one channel)")
            print("2. Daily Briefing (Get posts from the last N days from multiple channels)")
            mission_choice = input("Enter mission number (1 or 2): ")

            # --- NEW: Ask for output format ---
            print("\nChoose your output format:")
            print("1. Console Only")
            print("2. HTML Dossier Only")
            print("3. Both Console and HTML")
            output_choice = input("Enter format number (1, 2, or 3): ")

            # --- Mission Execution Logic ---
            if mission_choice == '1':
                channel = input("\nEnter the target channel username: ")
                limit = int(input("How many posts to retrieve? "))
                posts = await self.get_n_posts(channel, limit)
                
                title = f"{limit} posts from @{channel}"

                # Conditional Rendering
                if output_choice in ['1', '3']:
                    self.render_report_to_console(posts, title)
                
                if output_choice in ['2', '3']:
                    html_dossier = HTMLRenderer(f"I.N.S.I.G.H.T. Deep Scan: {title}")
                    html_dossier.render_report(posts)
                    html_dossier.save_to_file(f"deep_scan_{channel}.html")

            elif mission_choice == '2':
                channels_str = input("\nEnter channel usernames, separated by commas: ")
                channels = [c.strip() for c in channels_str.split(',')]
                days = int(input("How many days of history to include? "))
                briefing = await self.get_daily_briefing(channels, days)
                
                # Conditional Rendering
                if output_choice in ['1', '3']:
                    self.render_briefing_to_console(briefing, days)

                if output_choice in ['2', '3']:
                    html_dossier = HTMLRenderer() # Title is set inside the method
                    html_dossier.render_briefing(briefing, days)
                    filename_date = datetime.now().strftime('%Y-%m-%d')
                    html_dossier.save_to_file(f"daily_briefing_{filename_date}.html")
            
            else:
                print("Invalid mission choice. Aborting.")

            logging.info("Mission complete.")

        except Exception as e:
            logging.critical(f"A critical error occurred: {e}", exc_info=True)
        finally:
            await self.disconnect()

# --- Execution ---
if __name__ == "__main__":
    app = InsightOperator()
    asyncio.run(app.run())