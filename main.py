import os
import logging
import asyncio
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

class InsightApp:
    """
    I.N.S.I.G.H.T. Mark I (v1.6) - The Final Build
    This definitive version combines the "Deep Scanner" adaptive fetch logic
    with the "Paced Operator" throttling mechanism for a robust, stable,
    and intelligent data gathering engine.
    """
    def __init__(self):
        logging.info("I.N.S.I.G.H.T. Mark I (v1.6) Initializing...")
        load_dotenv()
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.session_file = 'insight_session'
        self.client = None

        # --- INTEGRATED: Throttling state from v1.5 ---
        self.request_counter = 0
        self.REQUEST_THRESHOLD = 20
        self.COOLDOWN_SECONDS = 120

        if not self.api_id or not self.api_hash:
            logging.critical("FATAL: TELEGRAM_API_ID or TELEGRAM_API_HASH not found in .env file.")
            exit()

    # --- INTEGRATED: Throttling method from v1.5 ---
    async def throttle_if_needed(self):
        """Checks the request counter and pauses if the threshold is exceeded."""
        if self.request_counter >= self.REQUEST_THRESHOLD:
            logging.warning(
                f"Request threshold ({self.REQUEST_THRESHOLD}) reached. "
                f"Initiating {self.COOLDOWN_SECONDS}-second cooldown to respect API limits."
            )
            self.request_counter = 0
            await asyncio.sleep(self.COOLDOWN_SECONDS)
            logging.info("Cooldown complete. Resuming operations.")
        
        self.request_counter += 1
        logging.info(f"Making API call #{self.request_counter}...")

    async def connect(self):
        """Establishes and authorizes the Telegram client connection."""
        self.client = TelegramClient(self.session_file, int(self.api_id), self.api_hash)
        logging.info("Connecting to Telegram...")
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            logging.warning("Client not authorized. Please follow the prompts.")
            phone = input("Enter your phone number (e.g., +1234567890): ")
            await self.client.send_code_request(phone)
            try:
                await self.client.sign_in(phone, input("Enter the code you received: "))
            except Exception:
                await self.client.sign_in(password=input("2FA Password Required. Please enter: "))

        logging.info("Connection successful and authorized.")

    async def disconnect(self):
        """Gracefully disconnects the client."""
        if self.client and self.client.is_connected():
            logging.info("Disconnecting from Telegram...")
            await self.client.disconnect()

    async def fetch_and_synthesize_posts(self, channel_username: str, limit: int = 3):
        """
        The definitive v1.6 fetch/synthesis engine.
        """
        logical_posts = []
        last_message_id = 0
        fetch_chunk_size = 50
        max_fetches = 10
        fetches = 0

        logging.info(f"Starting adaptive fetch for {limit} logical posts from @{channel_username}...")

        # We only need to get the entity once.
        try:
            await self.throttle_if_needed()
            raw_channel_entity = await self.client.get_entity(channel_username)
            resolved_username = raw_channel_entity.username
        except Exception as e:
            logging.error(f"Could not resolve channel entity for '{channel_username}': {e}")
            return []

        while len(logical_posts) < limit and fetches < max_fetches:
            fetches += 1
            logging.info(f"Fetch attempt #{fetches}: Fetching {fetch_chunk_size} messages...")
            
            await self.throttle_if_needed()
            
            try:
                raw_messages = await self.client.get_messages(
                    raw_channel_entity,
                    limit=fetch_chunk_size,
                    offset_id=last_message_id
                )
            except FloodWaitError as e:
                logging.critical(f"FLOOD WAIT ERROR: Server forcing a wait of {e.seconds}s.")
                await asyncio.sleep(e.seconds + 5) # Wait a little extra
                continue # Retry the same chunk after waiting
            except Exception as e:
                logging.error(f"API call failed during adaptive fetch: {e}")
                break

            if not raw_messages:
                logging.warning("No more messages found in channel history.")
                break

            synthesized_groups = {}
            for msg in raw_messages:
                if not msg: continue
                group_id = msg.grouped_id or msg.id
                if group_id not in synthesized_groups:
                    synthesized_groups[group_id] = {'messages': [], 'text': None}
                synthesized_groups[group_id]['messages'].append(msg)
                if msg.text:
                    synthesized_groups[group_id]['text'] = msg.text

            for group_id, group_data in synthesized_groups.items():
                if any(p['id'] == group_data['messages'][0].id for p in logical_posts):
                    continue
                
                main_msg = group_data['messages'][0]
                if main_msg.grouped_id:
                    main_msg = next((m for m in group_data['messages'] if m.text), main_msg)

                if main_msg.text:
                    media_urls = [f'https://t.me/{resolved_username}/{m.id}?single' for m in group_data['messages'] if m.media]
                    post_data = {
                        'id': main_msg.id,
                        'date': main_msg.date.strftime('%Y-%m-%d %H:%M:%S'),
                        'text': main_msg.text,
                        'media_urls': media_urls,
                        'link': f'https://t.me/{resolved_username}/{main_msg.id}'
                    }
                    logical_posts.append(post_data)

            last_message_id = raw_messages[-1].id

        final_posts = sorted(logical_posts, key=lambda p: p['id'], reverse=True)[:limit]
        logging.info(f"Synthesis complete. Found {len(final_posts)} logical posts after {fetches} fetch(es).")
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