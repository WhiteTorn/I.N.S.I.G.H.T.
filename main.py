import os
import logging
import asyncio
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError
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
    I.N.S.I.G.H.T. Mark I (v1.10) - The Chronos Engine
    The final version of the Mark I. Introduces chronological sorting for
    briefings and a dedicated 'End of Day' automation protocol.
    """
    def __init__(self):
        logging.info("I.N.S.I.G.H.T. Mark I (v1.10) Initializing...")
        load_dotenv()
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.session_file = 'insight_session'
        self.client = None
        self.request_counter = 0
        self.REQUEST_THRESHOLD = 25
        self.COOLDOWN_SECONDS = 60

    async def throttle_if_needed(self):
        """Checks the request counter and pauses if the threshold is exceeded."""
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
        """Establishes and authorizes the Telegram client connection."""
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
        """Gracefully disconnects the client."""
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

    # --- MISSION PROFILE 2 & 3: BRIEFINGS ---
    async def get_briefing_posts(self, channels: list, days: int):
        """
        Fetches all posts from a list of channels for the last N days,
        and returns them as a single, chronologically sorted list.
        v1.10.1: Corrects the album processing logic.
        """
        if days == 0:
            logging.info("Starting 'End of Day' briefing generation for today...")
            now_utc = datetime.now(timezone.utc)
            cutoff_date = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            logging.info(f"Starting Historical Briefing generation for the last {days} days...")
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        all_posts = []
        
        for channel in channels:
            logging.info(f"Gathering intel from @{channel}...")
            
            # --- THE FIX: We fetch all messages for the period into a list first ---
            try:
                await self.throttle_if_needed()
                entity = await self.client.get_entity(channel)
                
                # Fetch all relevant messages into memory for this channel
                channel_messages = []
                async for message in self.client.iter_messages(entity, limit=None):
                    if message.date < cutoff_date:
                        break
                    channel_messages.append(message)

                # Now process the buffered messages with correct album logic
                processed_ids = set()
                for message in channel_messages:
                    if message.id in processed_ids:
                        continue

                    synthesized = []
                    if message.grouped_id:
                        # This is part of an album. Find all its siblings in our buffer.
                        group = [m for m in channel_messages if m and m.grouped_id == message.grouped_id]
                        synthesized = await self._synthesize_messages(group, channel)
                        # Mark all parts of this group as processed
                        for m in group:
                            processed_ids.add(m.id)
                    else:
                        # This is a single message
                        synthesized = await self._synthesize_messages([message], channel)
                        processed_ids.add(message.id)

                    if synthesized:
                        # Add channel source to each post for rendering
                        for post in synthesized:
                            post['channel'] = channel
                            all_posts.append(post)

            except Exception as e:
                logging.error(f"Failed to process channel @{channel}: {e}", exc_info=True)
        
        return sorted(all_posts, key=lambda p: p['date'])

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

    # --- MAIN EXECUTION LOOP ---
    async def run(self):
        """The main execution flow, with updated mission choices."""
        try:
            await self.connect()
            
            print("\nI.N.S.I.G.H.T. Operator Online. Choose your mission:")
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
                    html_dossier.render_report(posts) # render_report in HTMLRenderer only needs the post list
                    html_dossier.save_to_file(f"deep_scan_{channel}.html")
            
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
                    # The HTML renderer needs the raw post data and the number of days for its title
                    html_renderer = HTMLRenderer()
                    # The briefing data needs to be structured by channel for the renderer
                    briefing_data_for_html = {channel: [] for channel in channels}
                    for post in all_posts:
                        briefing_data_for_html[post['channel']].append(post)

                    html_renderer.render_briefing(briefing_data_for_html, days) # Pass both arguments
                    
                    filename_date = datetime.now().strftime('%Y-%m-%d')
                    filename = f"briefing_{filename_date}.html"
                    html_renderer.save_to_file(filename)
            
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