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
# THE FIX IS HERE: We explicitly set the encoding for both handlers to 'utf-8'.
# This ensures they can handle any Unicode character from any language.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    handlers=[
        logging.FileHandler("insight_debug.log", encoding='utf-8'),
        logging.StreamHandler() # The stream handler will respect the console's encoding, 
                                # but modern terminals (like Windows Terminal) handle UTF-8 well.
                                # Forcing it on the file handler is the most critical part.
    ]
)
# Forcing the console (StreamHandler) can also be done if needed, but let's start with the file.
# If the console still shows errors, we can wrap the StreamHandler too:
# logging.StreamHandler(stream=open(1, 'w', encoding='utf-8', closefd=False)) # This is more advanced

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
    session_file = 'insight_session'
    
    async with TelegramClient(session_file, int(API_ID), API_HASH) as client:
        logging.info(f"Telegram Client instantiated. Attempting to connect...")
        
        try:
            if not await client.is_user_authorized():
                logging.warning("Client not authorized. Awaiting user interaction for login.")
                await client.send_code_request(input("Enter your phone number (e.g., +1234567890): "))
                await client.sign_in(password=input("Enter your 2FA password (if any): "))

            logging.info(f"Connection successful. Targeting channel: @{channel_username}")

            target_channel = await client.get_entity(channel_username)
            
            # This line will now log correctly to the file.
            logging.info(f"Successfully resolved channel: '{target_channel.title}'. Fetching last {limit} posts.")
            
            posts = await client.get_messages(target_channel, limit=limit)

            for i, post in enumerate(posts):
                if post and post.text:
                    print("\n--- PRINTING POST ---")
                    print(f"Post {i+1}/{limit} | ID: {post.id} | Text is present.")
                    print(post.text)
                else:
                    print("\n--- SKIPPING POST ---")
                    if post:
                        print(f"Post {i+1}/{limit} | ID: {post.id} | This post has NO TEXT.")
                        # Let's see what it is, if we can.
                        print(f"Debug Info: {post.to_dict()}") 
                    else:
                        print(f"Post {i+1}/{limit} is None.")
            
            print("\n" + "="*20 + " LATEST POSTS " + "="*20)
            for i, post in enumerate(posts):
                if post and post.text:
                    print(f"\n--- Post {i+1}/{limit} | ID: {post.id} | Date: {post.date.strftime('%Y-%m-%d %H:%M:%S')} ---")
                    # The `print` function itself might also have issues depending on the console.
                    # A robust solution is to encode manually before printing, though often unnecessary in modern terminals.
                    try:
                        print(post.text)
                    except UnicodeEncodeError:
                        print(post.text.encode('utf-8', 'replace').decode('utf-8')) # A fallback for problematic terminals
                    print("-"*(40 + len(" LATEST POSTS ")))
            
            logging.info(f"Successfully parsed and displayed {len(posts)} posts.")

        except SessionPasswordNeededError:
            logging.error("Two-factor authentication is enabled. Please run this script in an interactive terminal to enter your password.")
        except (ChannelInvalidError, ValueError):
            logging.error(f"The provided channel username '{channel_username}' is invalid or the channel does not exist.")
        except ChannelPrivateError:
            logging.error(f"The channel '@{channel_username}' is private. I.N.S.I.G.H.T. requires access, or you must be a member.")
        except Exception as e:
            logging.critical(f"An unexpected error occurred: {e}", exc_info=True)
        finally:
            logging.info("Operation complete. Disconnecting Telegram Client.")


# --- Execution ---

if __name__ == "__main__":
    target = input("Enter the public Telegram channel username (e.g., 'durov'): ")
    if not target:
        logging.error("No target channel provided. Aborting.")
    else:
        asyncio.run(parse_latest_posts(channel_username=target))