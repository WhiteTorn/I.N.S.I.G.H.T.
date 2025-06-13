import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api.formatters import TextFormatter
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .base_connector import BaseConnector


class YouTubeConnector(BaseConnector):
    """
    I.N.S.I.G.H.T. YouTube Connector v2.4 - "The Spymaster"
    
    Expands intelligence gathering into the audio-visual domain by extracting
    transcripts from YouTube videos and channels.
    
    Features:
    - Single video transcript extraction by URL
    - Channel-based transcript collection (latest N videos)
    - Playlist transcript extraction
    - Search-based transcript collection
    - Language preference system with fallbacks
    - HARDENED: Bulletproof error handling for all failure scenarios
    
    This connector treats transcript failures as expected battlefield conditions
    and continues operations despite individual video failures.
    """
    
    def __init__(self, api_key: str, preferred_languages: List[str] = None):
        """
        Initialize the YouTube connector.
        
        Args:
            api_key: YouTube Data API v3 key from Google Cloud Console
            preferred_languages: List of preferred language codes (e.g., ['en', 'es', 'fr'])
                                If None, defaults to ['en'] with auto-fallback to available languages
        """
        super().__init__("youtube")
        
        self.api_key = api_key
        self.preferred_languages = preferred_languages or ['en']
        self.youtube_service = None
        self.transcript_formatter = TextFormatter()
        
        # Quality preferences - prefer manual transcripts over auto-generated
        self.prefer_manual = True
        
        self.logger.info("YouTubeConnector v2.4 'The Spymaster' initialized with audio-visual intelligence capabilities")
    
    async def connect(self) -> None:
        """
        Establishes connection to YouTube Data API.
        """
        try:
            self.youtube_service = build('youtube', 'v3', developerKey=self.api_key)
            self.logger.info("Connected to YouTube Data API v3")
        except Exception as e:
            self.logger.error(f"Failed to connect to YouTube Data API: {str(e)}")
            raise ConnectionError(f"YouTube API connection failed: {str(e)}")
    
    async def disconnect(self) -> None:
        """
        Gracefully disconnects from YouTube services.
        """
        if self.youtube_service:
            self.youtube_service.close()
            self.youtube_service = None
            self.logger.info("Disconnected from YouTube Data API")
    
    def _extract_video_id(self, video_url: str) -> Optional[str]:
        """
        Extracts video ID from various YouTube URL formats.
        Supports youtu.be, youtube.com/watch, youtube.com/embed formats.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Extracted video ID or None if invalid
        """
        try:
            # Handle youtu.be short URLs
            if "youtu.be" in video_url:
                return video_url.split("/")[-1].split("?")[0]
            
            # Handle youtube.com URLs
            elif "youtube.com" in video_url:
                # Standard watch URLs
                if "v=" in video_url:
                    return video_url.split("v=")[1].split("&")[0]
                # Embed URLs
                elif "embed/" in video_url:
                    return video_url.split("embed/")[1].split("?")[0]
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to extract video ID from URL {video_url}: {e}")
            return None
    
    def _extract_channel_id(self, channel_identifier: str) -> str:
        """
        Processes channel identifier to determine if it's a channel ID or username.
        
        Args:
            channel_identifier: Channel ID, username, or channel URL
            
        Returns:
            Processed channel identifier for API calls
        """
        # If it's a full URL, extract the identifier
        if "youtube.com" in channel_identifier:
            if "/channel/" in channel_identifier:
                return channel_identifier.split("/channel/")[1].split("/")[0]
            elif "/user/" in channel_identifier or "/c/" in channel_identifier:
                return channel_identifier.split("/")[-1]
        
        # Clean up @ symbol if present
        return channel_identifier.lstrip('@')
    
    def _get_best_transcript(self, video_id: str) -> Optional[str]:
        """
        Fetches the best available transcript for a video using language preferences.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Formatted transcript text or None if no transcript available
        """
        try:
            # Get available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try preferred languages first
            for lang_code in self.preferred_languages:
                try:
                    # Try manual transcript first
                    if self.prefer_manual:
                        try:
                            transcript = transcript_list.find_manually_created_transcript([lang_code])
                            transcript_data = transcript.fetch()
                            return self.transcript_formatter.format_transcript(transcript_data)
                        except NoTranscriptFound:
                            pass  # Fall back to auto-generated
                    
                    # Try any transcript (manual or auto) in preferred language
                    transcript = transcript_list.find_transcript([lang_code])
                    transcript_data = transcript.fetch()
                    return self.transcript_formatter.format_transcript(transcript_data)
                    
                except NoTranscriptFound:
                    continue
            
            # If no preferred language found, try any available transcript
            try:
                # Get first available transcript
                available_transcripts = list(transcript_list)
                if available_transcripts:
                    first_transcript = available_transcripts[0]
                    transcript_data = first_transcript.fetch()
                    return self.transcript_formatter.format_transcript(transcript_data)
            except Exception:
                pass
            
            return None
            
        except (NoTranscriptFound, TranscriptsDisabled) as e:
            self.logger.warning(f"No transcript available for video {video_id}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching transcript for video {video_id}: {e}")
            return None
    
    async def _get_video_metadata(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches video metadata using YouTube Data API.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video metadata dictionary or None if failed
        """
        try:
            response = self.youtube_service.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()
            
            if not response.get('items'):
                self.logger.warning(f"No metadata found for video {video_id}")
                return None
            
            return response['items'][0]
            
        except HttpError as e:
            self.logger.error(f"YouTube API error fetching metadata for video {video_id}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching metadata for video {video_id}: {e}")
            return None
    
    async def _get_channel_videos(self, channel_identifier: str, limit: int) -> List[str]:
        """
        Fetches latest video IDs from a YouTube channel.
        
        Args:
            channel_identifier: Channel ID or username
            limit: Maximum number of video IDs to fetch
            
        Returns:
            List of video IDs
        """
        try:
            # First, resolve channel ID if we have a username
            channel_id = await self._resolve_channel_id(channel_identifier)
            if not channel_id:
                return []
            
            # Get uploads playlist ID
            channel_response = self.youtube_service.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response.get('items'):
                self.logger.error(f"Channel {channel_identifier} not found")
                return []
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            videos = []
            next_page_token = None
            
            while len(videos) < limit:
                playlist_response = self.youtube_service.playlistItems().list(
                    part='contentDetails',
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, limit - len(videos)),
                    pageToken=next_page_token
                ).execute()
                
                for item in playlist_response.get('items', []):
                    videos.append(item['contentDetails']['videoId'])
                
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return videos[:limit]
            
        except HttpError as e:
            self.logger.error(f"YouTube API error fetching videos from channel {channel_identifier}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error fetching videos from channel {channel_identifier}: {e}")
            return []
    
    async def _resolve_channel_id(self, channel_identifier: str) -> Optional[str]:
        """
        Resolves a channel username to channel ID.
        
        Args:
            channel_identifier: Channel username or ID
            
        Returns:
            Channel ID or None if not found
        """
        try:
            # If it already looks like a channel ID, return it
            if channel_identifier.startswith('UC') and len(channel_identifier) == 24:
                return channel_identifier
            
            # Try to find by username
            response = self.youtube_service.channels().list(
                part='id',
                forUsername=channel_identifier
            ).execute()
            
            if response.get('items'):
                return response['items'][0]['id']
            
            # Try to find by custom URL (search)
            search_response = self.youtube_service.search().list(
                part='snippet',
                q=channel_identifier,
                type='channel',
                maxResults=1
            ).execute()
            
            if search_response.get('items'):
                return search_response['items'][0]['snippet']['channelId']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error resolving channel ID for {channel_identifier}: {e}")
            return None
    
    async def fetch_posts(self, source_identifier: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fetches transcripts from YouTube videos.
        
        Supports two modes:
        1. Single video URL - extracts transcript from one video
        2. Channel identifier - extracts transcripts from latest N videos
        
        HARDENED: Individual video failures do not affect other videos.
        
        Args:
            source_identifier: YouTube video URL or channel identifier
            limit: Maximum number of transcripts to fetch (ignored for single video)
            
        Returns:
            List of posts in unified format with transcript content
        """
        if not self.youtube_service:
            self.logger.error("ERROR: YouTube connector not connected to API")
            return []
        
        # Determine if this is a video URL or channel identifier
        video_id = self._extract_video_id(source_identifier)
        
        if video_id:
            # Single video mode
            return await self._fetch_single_video_transcript(video_id)
        else:
            # Channel mode
            return await self._fetch_channel_transcripts(source_identifier, limit)
    
    async def _fetch_single_video_transcript(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Fetches transcript from a single YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List containing single post with transcript or empty list if failed
        """
        self.logger.info(f"Extracting intelligence from video {video_id}...")
        
        try:
            # Get video metadata
            metadata = await self._get_video_metadata(video_id)
            if not metadata:
                self.logger.error(f"ERROR: Failed to fetch metadata for video {video_id}")
                return []
            
            # Get transcript
            transcript = self._get_best_transcript(video_id)
            if not transcript:
                self.logger.warning(f"WARNING: Could not retrieve transcript for video {video_id}. Skipping.")
                return []
            
            # Create unified post
            snippet = metadata['snippet']
            
            # Parse publish date
            publish_date = datetime.fromisoformat(
                snippet['publishedAt'].replace('Z', '+00:00')
            )
            
            unified_post = self._create_unified_post(
                source_platform="youtube",
                source_id=f"video:{video_id}",
                post_id=video_id,
                author=snippet['channelTitle'],
                content=transcript,
                timestamp=publish_date,
                media_urls=[f"https://www.youtube.com/watch?v={video_id}"],
                post_url=f"https://www.youtube.com/watch?v={video_id}"
            )
            
            # Add YouTube-specific metadata
            unified_post['video_title'] = snippet['title']
            unified_post['video_description'] = snippet.get('description', '')
            unified_post['channel_id'] = snippet['channelId']
            unified_post['view_count'] = metadata.get('statistics', {}).get('viewCount', 0)
            
            self.logger.info(f"Successfully extracted transcript from video {video_id}")
            return [unified_post]
            
        except Exception as e:
            self.logger.error(f"ERROR: Failed to process video {video_id} - Reason: {str(e)}")
            return []
    
    async def _fetch_channel_transcripts(self, channel_identifier: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fetches transcripts from latest videos in a YouTube channel.
        
        HARDENED: Individual video failures do not affect the overall operation.
        
        Args:
            channel_identifier: Channel ID or username
            limit: Maximum number of video transcripts to fetch
            
        Returns:
            List of posts with transcripts in unified format
        """
        cleaned_channel = self._extract_channel_id(channel_identifier)
        self.logger.info(f"Starting intelligence extraction from channel {cleaned_channel} (limit: {limit})...")
        
        try:
            # Get video IDs from channel
            video_ids = await self._get_channel_videos(cleaned_channel, limit)
            if not video_ids:
                self.logger.error(f"ERROR: No videos found for channel {cleaned_channel}")
                return []
            
            self.logger.info(f"Found {len(video_ids)} videos in channel {cleaned_channel}")
            
            # Process each video with individual error handling
            all_posts = []
            successful_extractions = 0
            failed_extractions = 0
            
            for i, video_id in enumerate(video_ids):
                self.logger.info(f"Processing video {i+1}/{len(video_ids)}: {video_id}")
                
                try:
                    # Get video metadata
                    metadata = await self._get_video_metadata(video_id)
                    if not metadata:
                        self.logger.warning(f"WARNING: Could not retrieve metadata for video {video_id}. Skipping.")
                        failed_extractions += 1
                        continue
                    
                    # Get transcript
                    transcript = self._get_best_transcript(video_id)
                    if not transcript:
                        self.logger.warning(f"WARNING: Could not retrieve transcript for video {video_id}. Skipping.")
                        failed_extractions += 1
                        continue
                    
                    # Create unified post
                    snippet = metadata['snippet']
                    
                    # Parse publish date
                    publish_date = datetime.fromisoformat(
                        snippet['publishedAt'].replace('Z', '+00:00')
                    )
                    
                    unified_post = self._create_unified_post(
                        source_platform="youtube",
                        source_id=f"channel:{cleaned_channel}",
                        post_id=video_id,
                        author=snippet['channelTitle'],
                        content=transcript,
                        timestamp=publish_date,
                        media_urls=[f"https://www.youtube.com/watch?v={video_id}"],
                        post_url=f"https://www.youtube.com/watch?v={video_id}"
                    )
                    
                    # Add YouTube-specific metadata
                    unified_post['video_title'] = snippet['title']
                    unified_post['video_description'] = snippet.get('description', '')
                    unified_post['channel_id'] = snippet['channelId']
                    unified_post['view_count'] = metadata.get('statistics', {}).get('viewCount', 0)
                    
                    all_posts.append(unified_post)
                    successful_extractions += 1
                    
                except Exception as e:
                    self.logger.error(f"ERROR: Failed to process video {video_id} - Reason: {str(e)}")
                    failed_extractions += 1
                    continue
            
            # Sort by publish date (newest first)
            all_posts.sort(key=lambda p: p.get('timestamp', datetime.min.replace(tzinfo=timezone.utc)), reverse=True)
            
            self.logger.info(f"Channel processing complete: {successful_extractions} successful, {failed_extractions} failed extractions")
            return all_posts
            
        except Exception as e:
            self.logger.error(f"ERROR: Failed to process channel {cleaned_channel} - Reason: Critical error: {str(e)}")
            return []
    
    async def fetch_posts_by_timeframe(self, sources: List[str], days: int) -> List[Dict[str, Any]]:
        """
        Fetches YouTube transcripts from multiple sources within a specific timeframe.
        
        HARDENED: Individual source failures do not affect other sources.
        
        Args:
            sources: List of YouTube video URLs or channel identifiers
            days: Number of days to look back (0 for "today only")
            
        Returns:
            List of posts with transcripts in unified format, sorted chronologically
        """
        if not self.youtube_service:
            self.logger.error("ERROR: YouTube connector not connected to API")
            return []
        
        if days == 0:
            self.logger.info("Starting 'End of Day' YouTube intelligence briefing for today...")
            cutoff_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            self.logger.info(f"Starting Historical YouTube intelligence briefing for the last {days} days...")
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        all_posts = []
        successful_sources = 0
        failed_sources = 0
        
        for source in sources:
            self.logger.info(f"Processing YouTube source: {source}")
            
            try:
                # Fetch posts from this source (use high limit for timeframe filtering)
                source_posts = await self.fetch_posts(source, 50)  # Get more videos to filter by date
                
                # Filter by timeframe
                filtered_posts = [
                    post for post in source_posts
                    if post.get('timestamp') and post['timestamp'] >= cutoff_date
                ]
                
                if filtered_posts:
                    all_posts.extend(filtered_posts)
                    successful_sources += 1
                    self.logger.info(f"Successfully collected {len(filtered_posts)} transcripts from {source}")
                else:
                    self.logger.warning(f"No transcripts found in timeframe for {source}")
                    
            except Exception as e:
                self.logger.error(f"ERROR: Failed to process YouTube source {source} - Reason: {str(e)}")
                failed_sources += 1
                continue
        
        self.logger.info(f"Multi-source YouTube processing complete: {successful_sources} successful, {failed_sources} failed sources")
        
        # Sort chronologically
        try:
            return sorted(all_posts, key=lambda p: p.get('timestamp', datetime.min.replace(tzinfo=timezone.utc)))
        except Exception as e:
            self.logger.error(f"Error sorting YouTube posts chronologically: {e}")
            return all_posts
    
    async def fetch_playlist_transcripts(self, playlist_url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        BONUS FEATURE: Fetches transcripts from all videos in a YouTube playlist.
        
        Args:
            playlist_url: YouTube playlist URL
            limit: Maximum number of videos to process
            
        Returns:
            List of posts with transcripts in unified format
        """
        try:
            # Extract playlist ID from URL
            playlist_id = None
            if "list=" in playlist_url:
                playlist_id = playlist_url.split("list=")[1].split("&")[0]
            
            if not playlist_id:
                self.logger.error(f"Invalid playlist URL: {playlist_url}")
                return []
            
            self.logger.info(f"Extracting intelligence from playlist {playlist_id}...")
            
            # Get videos from playlist
            videos = []
            next_page_token = None
            
            while len(videos) < limit:
                response = self.youtube_service.playlistItems().list(
                    part='contentDetails',
                    playlistId=playlist_id,
                    maxResults=min(50, limit - len(videos)),
                    pageToken=next_page_token
                ).execute()
                
                for item in response.get('items', []):
                    videos.append(item['contentDetails']['videoId'])
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            # Process each video
            all_posts = []
            for video_id in videos[:limit]:
                video_posts = await self._fetch_single_video_transcript(video_id)
                if video_posts:
                    # Update source_id to indicate playlist
                    video_posts[0]['source_id'] = f"playlist:{playlist_id}"
                    all_posts.extend(video_posts)
            
            self.logger.info(f"Successfully extracted {len(all_posts)} transcripts from playlist {playlist_id}")
            return all_posts
            
        except Exception as e:
            self.logger.error(f"ERROR: Failed to process playlist {playlist_url} - Reason: {str(e)}")
            return []
    
    async def search_video_transcripts(self, search_query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        BONUS FEATURE: Searches for videos and extracts their transcripts.
        
        Args:
            search_query: YouTube search query
            limit: Maximum number of videos to process
            
        Returns:
            List of posts with transcripts in unified format
        """
        try:
            self.logger.info(f"Searching for videos matching: '{search_query}'")
            
            # Search for videos
            search_response = self.youtube_service.search().list(
                part='id',
                q=search_query,
                type='video',
                maxResults=limit
            ).execute()
            
            if not search_response.get('items'):
                self.logger.warning(f"No videos found for search query: {search_query}")
                return []
            
            # Extract video IDs
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # Process each video
            all_posts = []
            for video_id in video_ids:
                video_posts = await self._fetch_single_video_transcript(video_id)
                if video_posts:
                    # Update source_id to indicate search
                    video_posts[0]['source_id'] = f"search:{search_query}"
                    all_posts.extend(video_posts)
            
            self.logger.info(f"Successfully extracted {len(all_posts)} transcripts from search '{search_query}'")
            return all_posts
            
        except Exception as e:
            self.logger.error(f"ERROR: Failed to search for videos with query '{search_query}' - Reason: {str(e)}")
            return [] 