import sys
import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeVideo
from datetime import datetime
import html
import os

# Read config from .env file
def load_env(path=".env"):
    env = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    env[k.strip()] = v.strip()
    return env

env = load_env()
API_ID = int(env.get('TELEGRAM_API_ID', '0'))
API_HASH = env.get('TELEGRAM_API_HASH', '')
SESSION_FILE = "telegram.session"  # Always use this, will be auto-created by Telethon
CHANNEL = sys.argv[1] if len(sys.argv) > 1 else 'telegram'
OUTFILE = "feed.xml"

async def main():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.start()
    messages = []
    async for msg in client.iter_messages(CHANNEL, limit=3):
        messages.append(msg)
    messages.reverse()

    rss = []
    rss.append('<?xml version="1.0" encoding="UTF-8"?>')
    rss.append('<rss version="2.0">')
    rss.append('<channel>')
    rss.append(f'<title>{html.escape(CHANNEL)} Telegram Channel</title>')
    rss.append(f'<link>https://t.me/{CHANNEL.lstrip("@")}</link>')
    rss.append(f'<description>Latest 3 posts from {html.escape(CHANNEL)}</description>')

    for msg in messages:
        title = f"Post {msg.id}"
        pubDate = msg.date.strftime("%a, %d %b %Y %H:%M:%S +0000")
        link = f'https://t.me/{CHANNEL.lstrip("@")}/{msg.id}'
        description = html.escape(msg.text or '')
        enclosure = ''

        # Media: photo/document/video
        if msg.media:
            if isinstance(msg.media, MessageMediaPhoto):
                media_url = f'https://t.me/{CHANNEL.lstrip("@")}/{msg.id}?media=1'
                enclosure = f'<enclosure url="{media_url}" type="image/jpeg" />'
            elif isinstance(msg.media, MessageMediaDocument):
                doc = msg.document
                is_video = any(isinstance(attr, DocumentAttributeVideo) for attr in doc.attributes)
                media_url = f'https://t.me/{CHANNEL.lstrip("@")}/{msg.id}?media=1'
                if is_video:
                    enclosure = f'<enclosure url="{media_url}" type="video/mp4" />'
                else:
                    enclosure = f'<enclosure url="{media_url}" type="application/octet-stream" />'

        rss.append('<item>')
        rss.append(f'<title>{html.escape(title)}</title>')
        rss.append(f'<link>{link}</link>')
        rss.append(f'<guid>{link}</guid>')
        rss.append(f'<pubDate>{pubDate}</pubDate>')
        rss.append(f'<description><![CDATA[{description}]]></description>')
        if enclosure:
            rss.append(enclosure)
        rss.append('</item>')

    rss.append('</channel>')
    rss.append('</rss>')

    with open(OUTFILE, "w", encoding="utf-8") as f:
        f.write('\n'.join(rss))
    print(f"RSS XML written to {OUTFILE}")

if __name__ == "__main__":
    asyncio.run(main())