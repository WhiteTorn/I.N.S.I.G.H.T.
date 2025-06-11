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
    I.N.S.I.G.H.T. Mark I (v1.3) - The Evidentiary Analyst
    This version enhances the synthesizer to include direct URLs for all
    associated media, providing actionable links to the evidence.
    """
    def __init__(self):
        logging.info("I.N.S.I.G.H.T. Mark I (v1.3) Initializing...")
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

    # --- PASTE THIS FUNCTION INTO YOUR InsightApp CLASS, REPLACING THE OLD ONE ---

    async def fetch_and_synthesize_posts(self, channel_username: str, limit: int = 3):
        """
        Implements the Fetch -> Synthesize -> Process pattern.
        v1.4: Media URLs now use the '?single' parameter for a focused view.
        """
        fetch_limit = limit * 5
        logging.info(f"Fetching last {fetch_limit} items from @{channel_username} to analyze for groups...")
        try:
            # We must use the raw channel username for the API call
            raw_channel_entity = await self.client.get_entity(channel_username)
            raw_messages = await self.client.get_messages(raw_channel_entity, limit=fetch_limit)
            if not raw_messages:
                logging.warning("No posts found for the given channel.")
                return []
        except Exception as e:
            logging.error(f"Failed to fetch posts from '{channel_username}': {e}")
            return []

        # Use the resolved username for constructing URLs to handle redirects, etc.
        resolved_username = raw_channel_entity.username
        logging.info(f"Synthesizing raw messages into logical posts for @{resolved_username}...")
        logical_posts = []
        processed_group_ids = set()

        for msg in raw_messages:
            if msg.grouped_id and msg.grouped_id in processed_group_ids:
                continue

            post_data = {}
            
            if msg.grouped_id:
                group = [m for m in raw_messages if m.grouped_id == msg.grouped_id]
                main_msg = next((m for m in group if m.text), group[0])
                text = main_msg.text
                
                # UPGRADED: Generate a list of URLs with '?single'
                media_urls = [f'https://t.me/{resolved_username}/{m.id}?single' for m in group]

                post_data = {
                    'id': main_msg.id,
                    'date': main_msg.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'text': text,
                    'media_urls': media_urls,
                    'link': f'https://t.me/{resolved_username}/{main_msg.id}'
                }
                processed_group_ids.add(msg.grouped_id)

            elif msg.text:
                # UPGRADED: Generate a URL with '?single' if this single post has media
                media_urls = [f'https://t.me/{resolved_username}/{msg.id}?single'] if msg.media else []

                post_data = {
                    'id': msg.id,
                    'date': msg.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'text': msg.text,
                    'media_urls': media_urls,
                    'link': f'https://t.me/{resolved_username}/{msg.id}'
                }
            
            if post_data:
                logical_posts.append(post_data)

        final_posts = sorted(logical_posts, key=lambda p: p['id'], reverse=True)[:limit]
        logging.info(f"Synthesis complete. Found {len(final_posts)} logical posts.")
        return sorted(final_posts, key=lambda p: p['id'])

    def render_posts_to_console(self, posts: list):
        """Renders the clean list of synthesized posts, including media URLs."""
        print("\n" + "="*20 + " I.N.S.I.G.H.T. REPORT " + "="*20)
        if not posts:
            print("\nNo displayable posts found.")
        
        for i, post_data in enumerate(posts):
            media_count = len(post_data['media_urls'])
            media_indicator = f"[+{media_count} MEDIA]" if media_count > 0 else ""
            
            print(f"\n--- Post {i+1}/{len(posts)} | ID: {post_data['id']} | Date: {post_data['date']} {media_indicator} ---")
            print(post_data['text'])
            print(f"Post Link: {post_data['link']}")

            # NEW: Render the list of media URLs
            if post_data['media_urls']:
                print("Media Links:")
                for url in post_data['media_urls']:
                    print(f"  - {url}")

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