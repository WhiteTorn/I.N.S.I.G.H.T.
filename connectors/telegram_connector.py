import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError
from .base_connector import BaseConnector

class TelegramConnector(BaseConnector):
    """
    I.N.S.I.G.H.T. Telegram Connector
    
    Handles all Telegram-specific logic including:
    - Telethon client management
    - Album synthesis (grouping related media posts)
    - Request throttling to avoid rate limits
    - Message processing and normalization
    
    This connector preserves all the advanced logic from Mark I v1.10
    while conforming to the new modular architecture.
    """
    
    def __init__(self, api_id: str, api_hash: str, session_file: str = "insight_session"):
        """
        Initialize the Telegram connector.
        
        Args:
            api_id: Telegram API ID from developer portal
            api_hash: Telegram API hash from developer portal
            session_file: Path to store Telegram session data
        """
        super().__init__("telegram")
        
        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.session_file = session_file
        self.client = None
        
        # Rate limiting configuration
        self.request_counter = 0
        self.REQUEST_THRESHOLD = 15
        self.COOLDOWN_SECONDS = 60
        
        self.logger.info("TelegramConnector initialized")
    
    async def throttle_if_needed(self):
        """
        Checks the request counter and pauses if the threshold is exceeded.
        Preserves the original Mark I throttling logic.
        """
        if self.request_counter >= self.REQUEST_THRESHOLD:
            self.logger.warning(
                f"Request threshold ({self.REQUEST_THRESHOLD}) reached. "
                f"Initiating {self.COOLDOWN_SECONDS}-second cooldown."
            )
            await asyncio.sleep(self.COOLDOWN_SECONDS)
            self.request_counter = 0
            self.logger.info("Cooldown complete. Resuming operations.")
        self.request_counter += 1
    
    async def connect(self) -> None:
        """
        Establishes and authorizes the Telegram client connection.
        Preserves the original Mark I connection logic.
        """
        self.client = TelegramClient(self.session_file, self.api_id, self.api_hash)
        self.logger.info("Connecting to Telegram...")
        
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            self.logger.warning("Client not authorized. Please follow prompts for first-time login.")
            phone = input("Enter your phone number: ")
            await self.client.send_code_request(phone)
            try:
                await self.client.sign_in(phone, input("Enter the code you received: "))
            except Exception:
                await self.client.sign_in(password=input("2FA Password Required. Please enter: "))
        
        self.logger.info("Telegram connection successful.")
    
    async def disconnect(self) -> None:
        """
        Gracefully disconnects the Telegram client.
        """
        if self.client and self.client.is_connected():
            self.logger.info("Disconnecting from Telegram...")
            await self.client.disconnect()
    
    async def _synthesize_messages(self, raw_messages: List, channel_alias: str) -> List[Dict[str, Any]]:
        """
        A private helper method to handle the advanced album synthesis logic.
        This preserves the exact logic from Mark I that groups related media posts.
        
        Args:
            raw_messages: List of raw Telegram messages
            channel_alias: Channel username for URL generation
            
        Returns:
            List of synthesized logical posts in unified format
        """
        synthesized_groups = {}
        
        for msg in raw_messages:
            if not msg: 
                continue
                
            group_id = msg.grouped_id or msg.id
            if group_id not in synthesized_groups:
                synthesized_groups[group_id] = {
                    'messages': [], 
                    'text': None, 
                    'main_msg': msg
                }
            
            synthesized_groups[group_id]['messages'].append(msg)
            
            if msg.text:
                synthesized_groups[group_id]['text'] = msg.text
                synthesized_groups[group_id]['main_msg'] = msg
        
        logical_posts = []
        for group_id, group_data in synthesized_groups.items():
            main_msg = group_data['main_msg']
            text = group_data['text']
            
            if text:  # Only process posts with text content
                media_urls = [
                    f'https://t.me/{channel_alias}/{m.id}?single' 
                    for m in group_data['messages'] 
                    if m.media
                ]
                
                # Create unified post using the base connector helper
                unified_post = self._create_unified_post(
                    source_platform="telegram",
                    source_id=f"@{channel_alias}",
                    post_id=str(main_msg.id),
                    author=channel_alias,  # Best effort author identification
                    content=text,
                    timestamp=main_msg.date,
                    media_urls=media_urls,
                    post_url=f'https://t.me/{channel_alias}/{main_msg.id}'
                )
                
                # Add the legacy 'channel' field for backward compatibility with existing renderers
                unified_post['channel'] = channel_alias
                # Add legacy fields for backward compatibility
                unified_post['id'] = main_msg.id
                unified_post['date'] = main_msg.date
                unified_post['text'] = text
                unified_post['link'] = f'https://t.me/{channel_alias}/{main_msg.id}'
                
                logical_posts.append(unified_post)
        
        return logical_posts
    
    async def fetch_posts(self, source_identifier: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fetches the last N logical posts from a single Telegram channel.
        This implements the "Deep Scan" mission profile from Mark I.
        
        Args:
            source_identifier: Telegram channel username (with or without @)
            limit: Maximum number of logical posts to fetch
            
        Returns:
            List of posts in unified format, sorted chronologically
        """
        # Clean the channel identifier
        channel_username = source_identifier.lstrip('@')
        
        self.logger.info(f"Starting Deep Scan for {limit} posts from @{channel_username}...")
        
        all_synthesized_posts = []
        processed_ids = set()
        last_message_id = 0
        fetch_chunk_size = 100
        max_fetches = 20
        
        try:
            await self.throttle_if_needed()
            entity = await self.client.get_entity(channel_username)
        except Exception as e:
            self.logger.error(f"Could not resolve channel entity for '{channel_username}': {e}")
            return []
        
        for i in range(max_fetches):
            if len(all_synthesized_posts) >= limit:
                break
            
            self.logger.info(f"Fetch attempt #{i+1}...")
            await self.throttle_if_needed()
            
            try:
                messages = await self.client.get_messages(
                    entity, 
                    limit=fetch_chunk_size, 
                    offset_id=last_message_id
                )
                if not messages: 
                    break
                
                synthesized = await self._synthesize_messages(messages, channel_username)
                
                for post in synthesized:
                    if post['id'] not in processed_ids:
                        all_synthesized_posts.append(post)
                        processed_ids.add(post['id'])
                
                last_message_id = messages[-1].id
                
            except Exception as e:
                self.logger.error(f"Error during message fetching: {e}")
                break
        
        # Sort by ID (newest first), then take the limit, then sort chronologically
        final_posts = sorted(all_synthesized_posts, key=lambda p: p['id'], reverse=True)[:limit]
        return sorted(final_posts, key=lambda p: p['date'])
    
    async def fetch_posts_by_timeframe(self, sources: List[str], days: int) -> List[Dict[str, Any]]:
        """
        Fetches all posts from multiple Telegram channels within a specific timeframe.
        This implements the "Historical Briefing" and "End of Day" mission profiles.
        
        Args:
            sources: List of Telegram channel usernames
            days: Number of days to look back (0 for "today only")
            
        Returns:
            List of posts in unified format, sorted chronologically
        """
        if days == 0:
            self.logger.info("Starting 'End of Day' briefing generation for today...")
            now_utc = datetime.now(timezone.utc)
            cutoff_date = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            self.logger.info(f"Starting Historical Briefing generation for the last {days} days...")
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        all_posts = []
        
        for channel in sources:
            # Clean the channel identifier
            channel_username = channel.lstrip('@')
            self.logger.info(f"Gathering intel from @{channel_username}...")
            
            try:
                await self.throttle_if_needed()
                entity = await self.client.get_entity(channel_username)
                
                # Fetch all relevant messages into memory for this channel
                channel_messages = []
                async for message in self.client.iter_messages(entity, limit=None):
                    if message.date < cutoff_date:
                        break
                    channel_messages.append(message)
                
                # Process the buffered messages with correct album logic
                processed_ids = set()
                for message in channel_messages:
                    if message.id in processed_ids:
                        continue
                    
                    synthesized = []
                    if message.grouped_id:
                        # This is part of an album. Find all its siblings in our buffer.
                        group = [
                            m for m in channel_messages 
                            if m and m.grouped_id == message.grouped_id
                        ]
                        synthesized = await self._synthesize_messages(group, channel_username)
                        # Mark all parts of this group as processed
                        for m in group:
                            processed_ids.add(m.id)
                    else:
                        # This is a single message
                        synthesized = await self._synthesize_messages([message], channel_username)
                        processed_ids.add(message.id)
                    
                    if synthesized:
                        all_posts.extend(synthesized)
                        
            except Exception as e:
                self.logger.error(f"Failed to process channel @{channel_username}: {e}", exc_info=True)
        
        return sorted(all_posts, key=lambda p: p['date']) 