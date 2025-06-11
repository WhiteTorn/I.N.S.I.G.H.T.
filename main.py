import os
import logging
import asyncio
from dotenv import load_dotenv
from telethon.sync import TelegramClient

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

class InsightApp:
    """
    I.N.S.I.G.H.T. Mark I (v1.2) - The Synthesizer
    This version understands and processes Telegram's media groups (albums)
    by synthesizing multiple related messages into a single logical post.
    """
    def __init__(self):
        logging.info("I.N.S.I.G.H.T. Mark I (v1.2) Initializing...")
        load_dotenv()
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.session_file = 'insight_session'
        self.client = None

        if not self.api_id or not self.api_hash:
            logging.critical("FATAL: TELEGRAM_API_ID or TELEGRAM_API_HASH not found in .env file.")
            exit()

    async def connect(self):
        """Establishes and authorizes the Telegram client connection."""
        self.client = TelegramClient(self.session_file, int(self.api_id), self.api_hash)
        logging.info("Connecting to Telegram...")
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            logging.warning("Client not authorized. Please follow the prompts.")
            phone = input("Enter your phone number (e.g., +1234567890): ")
            await self.client.send_code_request(phone)
            await self.client.sign_in(phone, input("Enter the code you received: "))
            
            if not await self.client.is_user_authorized():
                 await self.client.sign_in(password=input("Enter your 2FA password: "))

        logging.info("Connection successful and authorized.")

    async def disconnect(self):
        """Gracefully disconnects the client."""
        if self.client and self.client.is_connected():
            logging.info("Disconnecting from Telegram...")
            await self.client.disconnect()

    async def fetch_and_synthesize_posts(self, channel_username: str, limit: int = 3):
        """
        Implements the Fetch -> Synthesize -> Process pattern.
        """
        # 1. FETCH a larger buffer to catch all parts of a group
        fetch_limit = limit * 5 # Fetch more to ensure we don't miss group parts
        logging.info(f"Fetching last {fetch_limit} items from @{channel_username} to analyze for groups...")
        try:
            raw_messages = await self.client.get_messages(channel_username, limit=fetch_limit)
            if not raw_messages:
                logging.warning("No posts found for the given channel.")
                return []
        except Exception as e:
            logging.error(f"Failed to fetch posts from '{channel_username}': {e}")
            return []

        # 2. SYNTHESIZE into logical posts
        logging.info("Synthesizing raw messages into logical posts...")
        logical_posts = []
        processed_group_ids = set()

        for msg in raw_messages:
            # If it's part of a group we've already processed, skip it
            if msg.grouped_id and msg.grouped_id in processed_group_ids:
                continue

            post_data = {}
            
            if msg.grouped_id:
                # This is the first message of a group we've seen. Process the whole group now.
                group = [m for m in raw_messages if m.grouped_id == msg.grouped_id]
                
                # Find the message with the caption and the main details
                main_msg = next((m for m in group if m.text), group[0])
                text = main_msg.text
                media_count = len(group)

                post_data = {
                    'id': main_msg.id,
                    'date': main_msg.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'text': text,
                    'media_count': media_count,
                    'link': f'https://t.me/{channel_username}/{main_msg.id}'
                }
                processed_group_ids.add(msg.grouped_id)

            elif msg.text:
                # This is a standard, non-grouped message with text
                post_data = {
                    'id': msg.id,
                    'date': msg.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'text': msg.text,
                    'media_count': 1 if msg.media else 0,
                    'link': f'https://t.me/{channel_username}/{msg.id}'
                }
            
            if post_data:
                logical_posts.append(post_data)

        # 3. PROCESS (Return the correct number of final posts)
        # We return the latest 'limit' number of *logical* posts
        final_posts = sorted(logical_posts, key=lambda p: p['id'], reverse=True)[:limit]
        logging.info(f"Synthesis complete. Found {len(final_posts)} logical posts.")
        return sorted(final_posts, key=lambda p: p['id']) # Return in chronological order for display

    def render_posts_to_console(self, posts: list):
        """Renders the clean list of synthesized posts."""
        print("\n" + "="*20 + " I.N.S.I.G.H.T. REPORT " + "="*20)
        if not posts:
            print("\nNo displayable posts found.")
        
        for i, post_data in enumerate(posts):
            media_indicator = f"[+{post_data['media_count']} MEDIA]" if post_data['media_count'] > 0 else ""
            
            print(f"\n--- Post {i+1}/{len(posts)} | ID: {post_data['id']} | Date: {post_data['date']} {media_indicator} ---")
            print(post_data['text'])
            print(f"Link: {post_data['link']}")
            print("-" * 60)
        
        print("\n" + "="*20 + " END OF REPORT " + "="*24)

    async def run(self):
        """The main execution flow of the application."""
        try:
            await self.connect()
            
            channel = input("Enter the public Telegram channel username (e.g., 'durov'): ")
            if not channel:
                logging.error("No target channel provided. Aborting.")
                return

            processed_data = await self.fetch_and_synthesize_posts(channel, limit=3)
            self.render_posts_to_console(processed_data)

        except Exception as e:
            logging.critical(f"A critical error occurred in the main run loop: {e}", exc_info=True)
        finally:
            await self.disconnect()

# --- Execution ---
if __name__ == "__main__":
    app = InsightApp()
    asyncio.run(app.run())