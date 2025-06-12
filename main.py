# main.py
import os
import logging
import asyncio
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError

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
    I.N.S.I.G.H.T. Mark I (v1.7) - The Operator
    The definitive, flexible, and robust version of the Mark I engine.
    Capable of performing multiple mission profiles: Deep Scans and Daily Briefings.
    """
    def __init__(self):
        logging.info("I.N.S.I.G.H.T. Mark I (v1.7) Initializing...")
        load_dotenv()
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.session_file = 'insight_session'
        self.client = None
        self.request_counter = 0
        self.REQUEST_THRESHOLD = 25  # Slightly increased for multi-channel fetches
        self.COOLDOWN_SECONDS = 60 # Shorter cooldown, more adaptive

    async def throttle_if_needed(self):
        """Checks the request counter and pauses if the threshold is exceeded."""
        if self.request_counter >= self.REQUEST_THRESHOLD:
            logging.warning(
                f"Request threshold ({self.REQUEST_THRESHOLD}) reached. "
                f"Initiating {self.COOLDOWN_SECONDS}-second cooldown."
            )
            await asyncio.sleep(self.COOLDOWN_SECONDS)
            self.request_counter = 0 # Reset after cooldown
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

    async def _synthesize_messages(self, raw_messages, resolved_username):
        """A private helper method to handle the synthesis logic."""
        synthesized_groups = {}
        for msg in raw_messages:
            if not msg: continue
            
            # Use the group ID as a key, or the message ID if it's not part of a group
            group_id = msg.grouped_id or msg.id
            
            if group_id not in synthesized_groups:
                synthesized_groups[group_id] = {'messages': [], 'text': None, 'main_msg': msg}
            
            synthesized_groups[group_id]['messages'].append(msg)
            
            # The message with text defines the group's text
            if msg.text:
                synthesized_groups[group_id]['text'] = msg.text
                synthesized_groups[group_id]['main_msg'] = msg

        logical_posts = []
        for group_id, group_data in synthesized_groups.items():
            main_msg = group_data['main_msg']
            text = group_data['text']

            # We only create a post if there is text content
            if text:
                media_urls = [f'https://t.me/{resolved_username}/{m.id}?single' for m in group_data['messages'] if m.media]
                post_data = {
                    'id': main_msg.id,
                    'date': main_msg.date, # Keep datetime object for sorting
                    'text': text,
                    'media_urls': media_urls,
                    'link': f'https://t.me/{resolved_username}/{main_msg.id}'
                }
                logical_posts.append(post_data)
        
        return logical_posts

    # --- MISSION PROFILE 1: DEEP SCAN ---
    async def get_n_posts(self, channel_username: str, limit: int):
        """Fetches the last N logical posts from a single channel."""
        logging.info(f"Starting Deep Scan for {limit} posts from @{channel_username}...")
        all_synthesized_posts = []
        last_message_id = 0
        fetch_chunk_size = 100
        max_fetches = 20

        try:
            await self.throttle_if_needed()
            entity = await self.client.get_entity(channel_username)
            resolved_username = entity.username
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
                
                synthesized = await self._synthesize_messages(messages, resolved_username)
                
                # Avoid adding duplicates
                existing_ids = {p['id'] for p in all_synthesized_posts}
                for post in synthesized:
                    if post['id'] not in existing_ids:
                        all_synthesized_posts.append(post)

                last_message_id = messages[-1].id
            except FloodWaitError as e:
                logging.warning(f"Flood wait error. Sleeping for {e.seconds} seconds.")
                await asyncio.sleep(e.seconds + 5)
            except Exception as e:
                logging.error(f"Error during message fetching: {e}")
                break
        
        # Sort and trim to the final limit
        final_posts = sorted(all_synthesized_posts, key=lambda p: p['id'], reverse=True)[:limit]
        return sorted(final_posts, key=lambda p: p['date']) # Return in chronological order

    # --- MISSION PROFILE 2: DAILY BRIEFING ---
    async def get_daily_briefing(self, channels: list, days: int):
        """Fetches all posts from a list of channels for the last N days."""
        logging.info(f"Starting Daily Briefing generation for the last {days} days...")
        # The date N days ago, in UTC
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        briefing_data = {}

        for channel in channels:
            logging.info(f"Gathering intel from @{channel}...")
            channel_posts = []
            try:
                await self.throttle_if_needed()
                entity = await self.client.get_entity(channel)
                
                # Use iter_messages for efficient, deep history traversal
                async for message in self.client.iter_messages(entity, limit=None):
                    if message.date < cutoff_date:
                        logging.info(f"Reached cutoff date for @{channel}. Moving on.")
                        break # Stop searching this channel
                    
                    # We can reuse our synthesizer on single messages
                    synthesized = await self._synthesize_messages([message], entity.username)
                    if synthesized:
                        channel_posts.extend(synthesized)
                
                briefing_data[channel] = sorted(channel_posts, key=lambda p: p['date'])
            except Exception as e:
                logging.error(f"Failed to process channel @{channel}: {e}")
                briefing_data[channel] = []
        
        return briefing_data

    # --- RENDER METHODS ---
    def render_report(self, posts: list, title: str):
        """A generic renderer for a list of posts."""
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

    def render_briefing(self, briefing_data: dict, days: int):
        """A specific renderer for the daily briefing format."""
        print("\n" + "#"*25 + f" I.N.S.I.G.H.T. BRIEFING: LAST {days} DAYS " + "#"*25)
        
        for channel, posts in briefing_data.items():
            if not posts: continue
            
            print(f"\n\n{'='*25} INTEL FROM: @{channel.upper()} {'='*25}")
            # Group posts by day
            posts_by_day = {}
            for post in posts:
                day = post['date'].strftime('%Y-%m-%d, %A')
                if day not in posts_by_day:
                    posts_by_day[day] = []
                posts_by_day[day].append(post)
            
            for day, day_posts in sorted(posts_by_day.items()):
                print(f"\n--- {day} ---")
                for post_data in day_posts:
                    print(f"\n  [{post_data['date'].strftime('%H:%M:%S')}] ID: {post_data['id']}")
                    # Print a snippet of text for brevity in briefing format
                    text_snippet = (post_data['text'][:120] + '...').replace('\n', ' ')
                    print(f"    {text_snippet}")
                    print(f"    Link: {post_data['link']}")

        print("\n" + "#"*30 + " END OF BRIEFING " + "#"*30)

    async def run(self):
        """The main execution flow, presenting the user with mission choices."""
        try:
            await self.connect()
            
            print("\nI.N.S.I.G.H.T. Operator Online. Choose your mission:")
            print("1. Deep Scan (Get last N posts from one channel)")
            print("2. Daily Briefing (Get posts from the last N days from multiple channels)")
            choice = input("Enter mission number (1 or 2): ")

            if choice == '1':
                channel = input("Enter the target channel username: ")
                limit = int(input("How many posts to retrieve? "))
                posts = await self.get_n_posts(channel, limit)
                self.render_report(posts, f"{limit} posts from @{channel}")
            
            elif choice == '2':
                channels_str = input("Enter channel usernames, separated by commas (e.g., durov,telegram): ")
                channels = [c.strip() for c in channels_str.split(',')]
                days = int(input("How many days of history to include? (e.g., 5): "))
                briefing = await self.get_daily_briefing(channels, days)
                self.render_briefing(briefing, days)
            
            else:
                print("Invalid mission choice. Aborting.")

        except Exception as e:
            logging.critical(f"A critical error occurred: {e}", exc_info=True)
        finally:
            await self.disconnect()

# --- Execution ---
if __name__ == "__main__":
    app = InsightOperator()
    asyncio.run(app.run())