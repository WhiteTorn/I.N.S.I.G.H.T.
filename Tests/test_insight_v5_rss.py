import asyncio
import os
import sys
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connectors.telegram_connector import TelegramConnector
from connectors.rss_connector import RssConnector

from config.config_manager import ConfigManager
from output.console_output import ConsoleOutput
from output.html_output import HTMLOutput

class InsightV5RSS:

    def __init__(self):
        self.config_manager = ConfigManager()
        self.limit = 10

    async def fetch_telegram_posts(self, config) -> List[Dict[str, Any]]:
        """Fetch posts from all Telegram channels"""
        telegram_config = self.config_manager.get_platform_config(config, 'telegram')

        channels = telegram_config.get('channels', [])

        telegram_connector = TelegramConnector()
        telegram_connector.setup_connector()
        await telegram_connector.connect()

        all_posts = []
        for channel in channels:
            posts = await telegram_connector.fetch_posts(channel, self.limit)
            all_posts.extend(posts)
            
        await telegram_connector.disconnect()
        return all_posts
    
    async def fetch_rss_posts(self, config) -> List[Dict[str, Any]]:
        """Fetch posts from all RSS feeds"""
        rss_config = self.config_manager.get_platform_config(config, 'rss')

        feeds = rss_config.get('feeds', [])

        rss_connector = RssConnector()
        rss_connector.setup_connector()
        await rss_connector.connect()

        all_posts = []
        for feed in feeds:
            posts = await rss_connector.fetch_posts(feed, self.limit)
            all_posts.extend(posts)
            
        await rss_connector.disconnect()
        return all_posts

    async def run(self):
        config = self.config_manager.load_config()

        telegram_posts = await self.fetch_telegram_posts(config)
        rss_posts = await self.fetch_rss_posts(config)

        all_posts = telegram_posts + rss_posts

        ConsoleOutput.render_report_to_console(all_posts, "All Posts")

if __name__ == "__main__":
    test_v5 = InsightV5RSS()
    asyncio.run(test_v5.run())