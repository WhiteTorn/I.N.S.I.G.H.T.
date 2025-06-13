import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError, ChannelInvalidError, ChannelPrivateError, UsernameInvalidError, UsernameNotOccupiedError, RPCError
from .base_connector import BaseConnector

class TelegramConnector(BaseConnector):
    """
    I.N.S.I.G.H.T. Telegram Connector v2.3 - The Citadel
    
    Handles all Telegram-specific logic including:
    - Telethon client management
    - Album synthesis (grouping related media posts)
    - Request throttling to avoid rate limits
    - Message processing and normalization
    - ENHANCED: Comprehensive error handling and resilience
    
    This connector preserves all the advanced logic from Mark I v1.10
    while conforming to the new modular architecture.
    Hardened in v2.3 with bulletproof error handling.
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
        
        self.logger.info("TelegramConnector v2.3 'The Citadel' initialized with hardened error handling")
    
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
        HARDENED: Bulletproof error handling for all failure scenarios.
        
        Args:
            source_identifier: Telegram channel username (with or without @)
            limit: Maximum number of logical posts to fetch
            
        Returns:
            List of posts in unified format, empty list on failure
        """
        # Clean the channel identifier
        channel_username = source_identifier.lstrip('@')
        
        self.logger.info(f"Starting Deep Scan for {limit} posts from @{channel_username}...")
        
        # Validate client connection
        if not self.client or not self.client.is_connected():
            self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Telegram client not connected")
            return []
        
        all_synthesized_posts = []
        processed_ids = set()
        last_message_id = 0
        fetch_chunk_size = 100
        max_fetches = 20
        
        try:
            # Get channel entity with comprehensive error handling
            await self.throttle_if_needed()
            
            try:
                entity = await self.client.get_entity(channel_username)
            except ChannelInvalidError:
                self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Channel does not exist or is invalid")
                return []
            except ChannelPrivateError:
                self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Channel is private or requires subscription")
                return []
            except UsernameInvalidError:
                self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Invalid username format")
                return []
            except UsernameNotOccupiedError:
                self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Username not found")
                return []
            except ConnectionError as e:
                self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Network connection error: {str(e)}")
                return []
            except TimeoutError:
                self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Request timed out")
                return []
            except FloodWaitError as e:
                self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Rate limit exceeded, need to wait {e.seconds} seconds")
                return []
            except RPCError as e:
                self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Telegram API error: {str(e)}")
                return []
            except Exception as e:
                self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Unexpected error resolving channel: {str(e)}")
                return []
            
            # Fetch messages in chunks with individual error handling
            for fetch_attempt in range(max_fetches):
                if len(all_synthesized_posts) >= limit:
                    break
                
                self.logger.info(f"Fetch attempt #{fetch_attempt+1} for @{channel_username}...")
                
                try:
                    await self.throttle_if_needed()
                    
                    try:
                        messages = await self.client.get_messages(
                            entity, 
                            limit=fetch_chunk_size, 
                            offset_id=last_message_id
                        )
                    except ChannelPrivateError:
                        self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Channel became private during operation")
                        break
                    except FloodWaitError as e:
                        self.logger.warning(f"Rate limit hit for @{channel_username}, waiting {e.seconds} seconds...")
                        await asyncio.sleep(e.seconds)
                        continue
                    except ConnectionError as e:
                        self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Connection lost: {str(e)}")
                        break
                    except TimeoutError:
                        self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Message fetch timed out")
                        break
                    except RPCError as e:
                        self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Telegram API error during fetch: {str(e)}")
                        break
                    except Exception as e:
                        self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Unexpected error during message fetch: {str(e)}")
                        break
                    
                    if not messages: 
                        self.logger.info(f"No more messages available from @{channel_username}")
                        break
                    
                    # Synthesize messages with error handling
                    try:
                        synthesized = await self._synthesize_messages(messages, channel_username)
                        
                        for post in synthesized:
                            try:
                                if post.get('id') and post['id'] not in processed_ids:
                                    all_synthesized_posts.append(post)
                                    processed_ids.add(post['id'])
                            except Exception as e:
                                self.logger.warning(f"Error processing synthesized post: {e}")
                                continue
                        
                        last_message_id = messages[-1].id
                        
                    except Exception as e:
                        self.logger.error(f"Error synthesizing messages from @{channel_username}: {e}")
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error during fetch attempt #{fetch_attempt+1} for @{channel_username}: {e}")
                    # Continue with next attempt unless it's a critical error
                    if fetch_attempt >= max_fetches - 1:
                        break
                    continue
            
            # Sort and return posts with error handling
            try:
                # Sort by ID (newest first), then take the limit, then sort chronologically
                final_posts = sorted(all_synthesized_posts, key=lambda p: p.get('id', 0), reverse=True)[:limit]
                result = sorted(final_posts, key=lambda p: p.get('date', datetime.min.replace(tzinfo=timezone.utc)))
                
                self.logger.info(f"Successfully fetched {len(result)} posts from @{channel_username}")
                return result
                
            except Exception as e:
                self.logger.error(f"Error sorting posts from @{channel_username}: {e}")
                return all_synthesized_posts[:limit]  # Return unsorted if sorting fails
                
        except Exception as e:
            self.logger.error(f"ERROR: Failed to fetch from @{channel_username} - Reason: Critical error: {str(e)}")
            return []
    
    async def fetch_posts_by_timeframe(self, sources: List[str], days: int) -> List[Dict[str, Any]]:
        """
        Fetches all posts from multiple Telegram channels within a specific timeframe.
        This implements the "Historical Briefing" and "End of Day" mission profiles.
        HARDENED: Individual channel failures do not affect other channels.
        
        Args:
            sources: List of Telegram channel usernames
            days: Number of days to look back (0 for "today only")
            
        Returns:
            List of posts in unified format, sorted chronologically
        """
        # Validate client connection
        if not self.client or not self.client.is_connected():
            self.logger.error("ERROR: Failed to fetch briefing posts - Reason: Telegram client not connected")
            return []
        
        if days == 0:
            self.logger.info("Starting 'End of Day' briefing generation for today...")
            now_utc = datetime.now(timezone.utc)
            cutoff_date = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            self.logger.info(f"Starting Historical Briefing generation for the last {days} days...")
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        all_posts = []
        successful_channels = 0
        failed_channels = 0
        
        for channel in sources:
            # Clean the channel identifier
            channel_username = channel.lstrip('@')
            self.logger.info(f"Gathering intel from @{channel_username}...")
            
            try:
                # Get channel entity with comprehensive error handling
                await self.throttle_if_needed()
                
                try:
                    entity = await self.client.get_entity(channel_username)
                except ChannelInvalidError:
                    self.logger.error(f"ERROR: Failed to process @{channel_username} - Reason: Channel does not exist or is invalid")
                    failed_channels += 1
                    continue
                except ChannelPrivateError:
                    self.logger.error(f"ERROR: Failed to process @{channel_username} - Reason: Channel is private or requires subscription")
                    failed_channels += 1
                    continue
                except UsernameInvalidError:
                    self.logger.error(f"ERROR: Failed to process @{channel_username} - Reason: Invalid username format")
                    failed_channels += 1
                    continue
                except UsernameNotOccupiedError:
                    self.logger.error(f"ERROR: Failed to process @{channel_username} - Reason: Username not found")
                    failed_channels += 1
                    continue
                except FloodWaitError as e:
                    self.logger.error(f"ERROR: Failed to process @{channel_username} - Reason: Rate limit exceeded, need to wait {e.seconds} seconds")
                    failed_channels += 1
                    continue
                except Exception as e:
                    self.logger.error(f"ERROR: Failed to process @{channel_username} - Reason: Error resolving channel: {str(e)}")
                    failed_channels += 1
                    continue
                
                # Fetch all relevant messages with error handling
                channel_messages = []
                message_count = 0
                
                try:
                    async for message in self.client.iter_messages(entity, limit=None):
                        try:
                            if message.date < cutoff_date:
                                break
                            channel_messages.append(message)
                            message_count += 1
                            
                            # Add periodic throttling for large channels
                            if message_count % 100 == 0:
                                await self.throttle_if_needed()
                                
                        except Exception as e:
                            self.logger.warning(f"Error processing individual message from @{channel_username}: {e}")
                            continue
                            
                except ChannelPrivateError:
                    self.logger.error(f"ERROR: Failed to process @{channel_username} - Reason: Channel became private during iteration")
                    failed_channels += 1
                    continue
                except FloodWaitError as e:
                    self.logger.error(f"ERROR: Failed to process @{channel_username} - Reason: Rate limit during message iteration, need to wait {e.seconds} seconds")
                    failed_channels += 1
                    continue
                except Exception as e:
                    self.logger.error(f"ERROR: Failed to process @{channel_username} - Reason: Error during message iteration: {str(e)}")
                    failed_channels += 1
                    continue
                
                if not channel_messages:
                    self.logger.warning(f"No messages found in timeframe for @{channel_username}")
                    continue
                
                # Process the buffered messages with error handling
                try:
                    processed_ids = set()
                    channel_posts = []
                    
                    for message in channel_messages:
                        try:
                            if message.id in processed_ids:
                                continue
                            
                            synthesized = []
                            if message.grouped_id:
                                # This is part of an album. Find all its siblings in our buffer.
                                try:
                                    group = [
                                        m for m in channel_messages 
                                        if m and m.grouped_id == message.grouped_id
                                    ]
                                    synthesized = await self._synthesize_messages(group, channel_username)
                                    # Mark all parts of this group as processed
                                    for m in group:
                                        processed_ids.add(m.id)
                                except Exception as e:
                                    self.logger.warning(f"Error processing album group from @{channel_username}: {e}")
                                    continue
                            else:
                                # This is a single message
                                try:
                                    synthesized = await self._synthesize_messages([message], channel_username)
                                    processed_ids.add(message.id)
                                except Exception as e:
                                    self.logger.warning(f"Error processing single message from @{channel_username}: {e}")
                                    continue
                            
                            if synthesized:
                                channel_posts.extend(synthesized)
                                
                        except Exception as e:
                            self.logger.warning(f"Error processing message {getattr(message, 'id', 'unknown')} from @{channel_username}: {e}")
                            continue
                    
                    all_posts.extend(channel_posts)
                    successful_channels += 1
                    self.logger.info(f"Successfully collected {len(channel_posts)} posts from @{channel_username}")
                    
                except Exception as e:
                    self.logger.error(f"ERROR: Failed to process @{channel_username} - Reason: Error during message synthesis: {str(e)}")
                    failed_channels += 1
                    continue
                        
            except Exception as e:
                self.logger.error(f"ERROR: Failed to process @{channel_username} - Reason: Critical error: {str(e)}")
                failed_channels += 1
                continue
        
        self.logger.info(f"Multi-channel processing complete: {successful_channels} successful, {failed_channels} failed channels")
        
        # Sort chronologically with error handling
        try:
            return sorted(all_posts, key=lambda p: p.get('date', datetime.min.replace(tzinfo=timezone.utc)))
        except Exception as e:
            self.logger.error(f"Error sorting posts chronologically: {e}")
            return all_posts 