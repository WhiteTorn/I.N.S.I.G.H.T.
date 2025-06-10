import os
import logging
import asyncio
from dotenv import load_dotenv

from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.errors.rpcerrorlist import ChannelInvalidError, ChannelPrivateError

# --- Configuration and Setup ---

# 1. Setup sophisticated logging
# This will log INFO level messages and above to the console and a file.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    handlers=[
        logging.FileHandler("insight_debug.log"),
        logging.StreamHandler()
    ]
)
logging.info("I.N.S.I.G.H.T. Mark I Initializing...")

# 2. Load environment variables from .env file
load_dotenv()
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')

# 3. Basic validation of credentials
if not API_ID or not API_HASH:
    logging.critical("FATAL ERROR: TELEGRAM_API_ID or TELEGRAM_API_HASH not found in .env file.")
    logging.critical("Project I.N.S.I.G.H.T. cannot proceed. Shutting down.")
    exit()

# --- Core Logic ---

async def parse_latest_posts(channel_username: str, limit: int = 3):
    """
    Connects to Telegram and fetches the last 'limit' posts from a given public channel.
    This is the foundational ingestion function for the I.N.S.I.G.H.T. system.
    """
    # We use a session file to store authentication details after the first login.
    # Think of it as the suit remembering my biometric data.
    session_file = 'insight_session'
    
    # The 'with' statement ensures the client is always properly disconnected,
    # even if things go sideways. No loose ends.
    async with TelegramClient(session_file, int(API_ID), API_HASH) as client:
        logging.info(f"Telegram Client instantiated. Attempting to connect...")
        
        try:
            # Ensure we are connected
            if not await client.is_user_authorized():
                logging.warning("Client not authorized. Awaiting user interaction for login.")
                # This part handles the first-time login flow if you're not already authorized.
                # Telethon will prompt you in the console for your phone number, code, and 2FA password.
                await client.send_code_request(input("Enter your phone number (e.g., +1234567890): "))
                await client.sign_in(password=input("Enter your 2FA password (if any): "))

            logging.info(f"Connection successful. Targeting channel: @{channel_username}")

            # Fetch the channel entity. This is a good way to check if it exists.
            target_channel = await client.get_entity(channel_username)
            
            logging.info(f"Successfully resolved channel: '{target_channel.title}'. Fetching last {limit} posts.")
            
            # The main event: getting the messages.
            posts = await client.get_messages(target_channel, limit=limit)
            
            print("\n" + "="*20 + " LATEST POSTS " + "="*20)
            for i, post in enumerate(posts):
                # We only care about posts with text for this prototype.
                if post and post.text:
                    print(f"\n--- Post {i+1}/{limit} | ID: {post.id} | Date: {post.date.strftime('%Y-%m-%d %H:%M:%S')} ---")
                    print(post.text)
                    print("-"*(40 + len(" LATEST POSTS ")))
            
            logging.info(f"Successfully parsed and displayed {len(posts)} posts.")

        except SessionPasswordNeededError:
            logging.error("Two-factor authentication is enabled. Please run this script in an interactive terminal to enter your password.")
        except (ChannelInvalidError, ValueError):
            logging.error(f"The provided channel username '{channel_username}' is invalid or the channel does not exist.")
        except ChannelPrivateError:
            logging.error(f"The channel '@{channel_username}' is private. I.N.S.I.G.H.T. requires access, or you must be a member.")
        except Exception as e:
            # Catch-all for any other unexpected explosions.
            logging.critical(f"An unexpected error occurred: {e}", exc_info=True)
        finally:
            logging.info("Operation complete. Disconnecting Telegram Client.")
            # The 'async with' handles disconnection, but an explicit log is good practice.


# --- Execution ---

if __name__ == "__main__":
    # This makes the script runnable from the command line.
    # It's the "J.A.R.V.I.S., execute" command.
    target = input("Enter the public Telegram channel username (e.g., 'durov'): ")
    if not target:
        logging.error("No target channel provided. Aborting.")
    else:
        # asyncio.run() is the modern way to run the top-level async function.
        asyncio.run(parse_latest_posts(channel_username=target))