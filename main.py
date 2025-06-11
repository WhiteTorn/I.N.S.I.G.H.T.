import os
import logging
import asyncio
from dotenv import load_dotenv
from telethon.sync import TelegramClient

# --- Configuration and Setup ---

# No debug switch needed for now. We build for stability first.
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
    A structured, robust class for the I.N.S.I.G.H.T. application.
    This encapsulates the logic and prevents chaotic I/O.
    """
    def __init__(self):
        logging.info("I.N.S.I.G.H.T. Mark I (v1.1) Initializing...")
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
            
            # Handle Two-Factor Authentication if enabled
            if await self.client.is_user_authorized() == False:
                 await self.client.sign_in(password=input("Enter your 2FA password: "))

        logging.info("Connection successful and authorized.")

    async def disconnect(self):
        """Gracefully disconnects the client."""
        if self.client and self.client.is_connected():
            logging.info("Disconnecting from Telegram...")
            await self.client.disconnect()

    async def fetch_and_process_posts(self, channel_username: str, limit: int = 3):
        """
        Implements the Fetch -> Process -> Render pattern.
        Fetches posts, processes them into a clean data structure, and then renders them.
        """
        # 1. FETCH
        logging.info(f"Fetching last {limit} items from channel: @{channel_username}")
        try:
            raw_posts = await self.client.get_messages(channel_username, limit=limit)
            if not raw_posts:
                logging.warning("No posts found for the given channel.")
                return []
        except Exception as e:
            logging.error(f"Failed to fetch posts from '{channel_username}': {e}")
            return []

        # 2. PROCESS
        logging.info("Processing fetched items into structured data...")
        processed_posts = []
        for post in raw_posts:
            if not post or not post.text:
                logging.info(f"Skipping item ID {post.id if post else 'N/A'} - no text/caption found.")
                continue

            # Create a clean dictionary for each post. This is our standard format.
            post_data = {
                'id': post.id,
                'date': post.date.strftime('%Y-%m-%d %H:%M:%S'),
                'text': post.text,
                'has_media': bool(post.media),
                'link': f'https://t.me/{channel_username}/{post.id}'
            }
            processed_posts.append(post_data)
        
        logging.info(f"Successfully processed {len(processed_posts)} posts with text.")
        return processed_posts

    def render_posts_to_console(self, posts: list):
        """
        3. RENDER
        Takes the clean list of processed posts and prints it.
        This function is completely separate from the fetching logic.
        """
        print("\n" + "="*20 + " I.N.S.I.G.H.T. REPORT " + "="*20)
        if not posts:
            print("\nNo displayable posts found.")
        
        for i, post_data in enumerate(posts):
            media_indicator = "[+MEDIA]" if post_data['has_media'] else ""
            
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

            # This is the core workflow
            processed_data = await self.fetch_and_process_posts(channel)
            self.render_posts_to_console(processed_data)

        except Exception as e:
            logging.critical(f"A critical error occurred in the main run loop: {e}", exc_info=True)
        finally:
            await self.disconnect()

# --- Execution ---
if __name__ == "__main__":
    app = InsightApp()
    asyncio.run(app.run())