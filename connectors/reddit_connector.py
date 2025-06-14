import asyncio
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

import praw
from praw.exceptions import InvalidURL, RedditAPIException, ResponseException
from prawcore.exceptions import Forbidden, NotFound, ServerError

from .base_connector import BaseConnector


class RedditConnector(BaseConnector):
    """
    I.N.S.I.G.H.T. Reddit Connector v2.6 - "The Crowd Crier"
    
    Taps into the real-time pulse of public opinion and breaking news through Reddit.
    Uses PRAW (Python Reddit API Wrapper) for comprehensive Reddit access.
    
    Features:
    - Single post URL extraction (post + comments)
    - Subreddit monitoring with multiple sorting options (Hot, New, Top, Best, Rising)
    - Interactive post selection from subreddit listings
    - Automatic comment extraction and threading
    - HARDENED: Bulletproof error handling for all Reddit API scenarios
    - Rate limiting compliance and timeout protection
    
    This connector treats Reddit API failures as expected battlefield conditions
    and continues operations despite individual post/comment failures.
    """
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize the Reddit connector.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret  
            user_agent: User agent string for Reddit API
        """
        super().__init__("reddit")
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        
        # Reddit API instance
        self.reddit = None
        
        # Configuration
        self.max_comments_per_post = 50  # Limit comments to prevent overwhelming data
        self.comment_depth_limit = 3     # How deep to traverse comment threads
        
        self.logger.info("RedditConnector v2.6 'The Crowd Crier' initialized")
    
    async def connect(self) -> None:
        """
        Establish connection to Reddit API using PRAW.
        """
        try:
            # Initialize Reddit API client (read-only)
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            
            # Test the connection by accessing user (this will trigger auth)
            test_user = self.reddit.user.me()
            self.logger.info(f"Connected to Reddit API successfully (read-only mode)")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Reddit API: {e}")
            raise ConnectionError(f"Reddit API connection failed: {e}")
    
    async def disconnect(self) -> None:
        """
        Clean up Reddit API connection.
        """
        if self.reddit:
            # PRAW doesn't require explicit disconnection, but we'll log it
            self.reddit = None
        self.logger.info("Reddit connector disconnected")
    
    def _extract_post_id_from_url(self, reddit_url: str) -> Optional[str]:
        """
        Extract Reddit post ID from various Reddit URL formats.
        
        Args:
            reddit_url: Reddit post URL
            
        Returns:
            Extracted post ID or None if invalid
        """
        try:
            # Common Reddit URL patterns
            patterns = [
                r'reddit\.com/r/\w+/comments/([a-zA-Z0-9]+)',
                r'redd\.it/([a-zA-Z0-9]+)',
                r'/comments/([a-zA-Z0-9]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, reddit_url)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to extract post ID from URL {reddit_url}: {e}")
            return None
    
    def _extract_comments(self, submission, max_comments: int = None) -> List[Dict[str, Any]]:
        """
        Extract comments from a Reddit submission with depth limiting.
        
        Args:
            submission: PRAW submission object
            max_comments: Maximum number of comments to extract
            
        Returns:
            List of comment dictionaries
        """
        comments = []
        max_comments = max_comments or self.max_comments_per_post
        
        try:
            # Replace "MoreComments" objects to get actual comments
            submission.comments.replace_more(limit=0)
            
            def extract_comment_recursive(comment, depth=0):
                if len(comments) >= max_comments or depth > self.comment_depth_limit:
                    return
                
                try:
                    # Skip deleted/removed comments
                    if hasattr(comment, 'body') and comment.body not in ['[deleted]', '[removed]']:
                        comment_data = {
                            'id': comment.id,
                            'author': str(comment.author) if comment.author else '[deleted]',
                            'body': comment.body,
                            'score': comment.score,
                            'created_utc': datetime.fromtimestamp(comment.created_utc, tz=timezone.utc),
                            'permalink': f"https://reddit.com{comment.permalink}",
                            'depth': depth,
                            'is_submitter': comment.is_submitter,
                            'parent_id': comment.parent_id
                        }
                        comments.append(comment_data)
                        
                        # Recursively extract replies
                        if hasattr(comment, 'replies') and comment.replies:
                            for reply in comment.replies:
                                extract_comment_recursive(reply, depth + 1)
                                
                except Exception as e:
                    self.logger.warning(f"Error extracting comment {getattr(comment, 'id', 'unknown')}: {e}")
                    pass
            
            # Start extraction from top-level comments
            for comment in submission.comments:
                extract_comment_recursive(comment)
                if len(comments) >= max_comments:
                    break
            
            return comments
            
        except Exception as e:
            self.logger.error(f"Error extracting comments from submission: {e}")
            return []
    
    def _create_post_with_comments(self, submission, source_id: str) -> Dict[str, Any]:
        """
        Create unified post data including comments.
        
        Args:
            submission: PRAW submission object
            source_id: Source identifier
            
        Returns:
            Unified post dictionary with comments
        """
        try:
            # Extract post content
            post_content = submission.title
            if submission.selftext and submission.selftext.strip():
                post_content += f"\n\n{submission.selftext}"
            
            # Get media URLs
            media_urls = []
            if submission.url and not submission.is_self:
                media_urls.append(submission.url)
            
            # Extract comments
            comments = self._extract_comments(submission)
            
            # Create main post
            unified_post = self._create_unified_post(
                source_platform="reddit",
                source_id=source_id,
                post_id=submission.id,
                author=str(submission.author) if submission.author else '[deleted]',
                content=post_content,
                timestamp=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                media_urls=media_urls,
                post_url=f"https://reddit.com{submission.permalink}"
            )
            
            # Add Reddit-specific metadata
            unified_post['subreddit'] = str(submission.subreddit)
            unified_post['score'] = submission.score
            unified_post['upvote_ratio'] = submission.upvote_ratio
            unified_post['num_comments'] = submission.num_comments
            unified_post['is_over_18'] = submission.over_18
            unified_post['post_flair'] = submission.link_flair_text
            unified_post['comments'] = comments
            unified_post['comments_extracted'] = len(comments)
            
            return unified_post
            
        except Exception as e:
            self.logger.error(f"Error creating post data for submission {submission.id}: {e}")
            raise ValueError(f"Failed to create unified post: {e}")
    
    async def _fetch_post_by_url(self, reddit_url: str) -> List[Dict[str, Any]]:
        """
        Fetch a single Reddit post by URL including comments.
        
        Args:
            reddit_url: Reddit post URL
            
        Returns:
            List containing single post with comments
        """
        self.logger.info(f"Extracting Reddit post from URL: {reddit_url}")
        
        try:
            # Extract post ID from URL
            post_id = self._extract_post_id_from_url(reddit_url)
            if not post_id:
                self.logger.error(f"Could not extract post ID from URL: {reddit_url}")
                return []
            
            # Get submission
            submission = self.reddit.submission(id=post_id)
            
            # Create unified post with comments
            unified_post = self._create_post_with_comments(submission, f"url:{reddit_url}")
            
            self.logger.info(f"Successfully extracted post {post_id} with {unified_post['comments_extracted']} comments")
            return [unified_post]
            
        except (InvalidURL, NotFound) as e:
            self.logger.error(f"Reddit post not found or invalid URL {reddit_url}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error fetching Reddit post from URL {reddit_url}: {e}")
            return []
    
    async def _fetch_subreddit_posts(self, subreddit_name: str, sort_method: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch posts from a subreddit with specified sorting.
        
        Args:
            subreddit_name: Name of the subreddit (without r/)
            sort_method: Sorting method (hot, new, top, best, rising)
            limit: Maximum number of posts to fetch
            
        Returns:
            List of posts with comments in unified format
        """
        self.logger.info(f"Fetching {limit} {sort_method} posts from r/{subreddit_name}")
        
        try:
            # Get subreddit
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get posts based on sort method
            if sort_method == 'hot':
                submissions = subreddit.hot(limit=limit)
            elif sort_method == 'new':
                submissions = subreddit.new(limit=limit)
            elif sort_method == 'top':
                submissions = subreddit.top(limit=limit, time_filter='day')
            elif sort_method == 'best':
                submissions = subreddit.best(limit=limit)
            elif sort_method == 'rising':
                submissions = subreddit.rising(limit=limit)
            else:
                self.logger.error(f"Invalid sort method: {sort_method}")
                return []
            
            # Process each submission
            all_posts = []
            successful_extractions = 0
            failed_extractions = 0
            
            for submission in submissions:
                try:
                    unified_post = self._create_post_with_comments(
                        submission, 
                        f"r/{subreddit_name}:{sort_method}"
                    )
                    all_posts.append(unified_post)
                    successful_extractions += 1
                    
                    self.logger.info(f"Processed post {submission.id}: '{submission.title[:50]}...' "
                                   f"({unified_post['comments_extracted']} comments)")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process submission {submission.id}: {e}")
                    failed_extractions += 1
                    continue
            
            self.logger.info(f"Subreddit processing complete: {successful_extractions} successful, "
                           f"{failed_extractions} failed extractions")
            return all_posts
            
        except Forbidden as e:
            self.logger.error(f"Access forbidden to r/{subreddit_name}: {e}")
            return []
        except NotFound as e:
            self.logger.error(f"Subreddit r/{subreddit_name} not found: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error fetching from r/{subreddit_name}: {e}")
            return []
    
    async def fetch_posts(self, source_identifier: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch posts from Reddit.
        
        Supports two modes:
        1. Reddit post URL - extracts single post with comments
        2. Subreddit name - extracts N posts with comments (interactive mode in main app)
        
        HARDENED: Individual post failures do not affect other posts.
        
        Args:
            source_identifier: Reddit post URL or subreddit name (r/subredditname or subredditname)
            limit: Maximum number of posts to fetch (ignored for single URL)
            
        Returns:
            List of posts in unified format with comments
        """
        if not self.reddit:
            self.logger.error("Reddit client not connected")
            return []
        
        try:
            # Check if it's a Reddit URL
            if 'reddit.com' in source_identifier or 'redd.it' in source_identifier:
                return await self._fetch_post_by_url(source_identifier)
            
            # Treat as subreddit name
            subreddit_name = source_identifier.replace('r/', '').strip()
            
            # Default to 'hot' sorting for basic fetch_posts call
            # Interactive selection will be handled in main application
            return await self._fetch_subreddit_posts(subreddit_name, 'hot', limit)
            
        except Exception as e:
            self.logger.error(f"Error in fetch_posts for {source_identifier}: {e}")
            return []
    
    async def fetch_posts_by_timeframe(self, sources: List[str], days: int) -> List[Dict[str, Any]]:
        """
        Fetch Reddit posts from multiple sources within a specific timeframe.
        
        HARDENED: Individual source failures do not affect other sources.
        
        Args:
            sources: List of Reddit URLs or subreddit names
            days: Number of days to look back (used for 'top' sorting)
            
        Returns:
            List of posts with comments in unified format, sorted chronologically
        """
        if days == 0:
            self.logger.info("Starting Reddit 'End of Day' intelligence briefing for today...")
            time_filter = 'day'
        else:
            self.logger.info(f"Starting Reddit Historical intelligence briefing for the last {days} days...")
            time_filter = 'week' if days <= 7 else 'month' if days <= 30 else 'year'
        
        all_posts = []
        successful_sources = 0
        failed_sources = 0
        
        for source in sources:
            self.logger.info(f"Processing Reddit source: {source}")
            
            try:
                if 'reddit.com' in source or 'redd.it' in source:
                    # Single URL
                    posts = await self._fetch_post_by_url(source)
                else:
                    # Subreddit - use 'top' sorting for timeframe
                    subreddit_name = source.replace('r/', '').strip()
                    posts = await self._fetch_subreddit_posts(subreddit_name, 'top', 25)
                
                if posts:
                    all_posts.extend(posts)
                    successful_sources += 1
                    self.logger.info(f"Successfully collected {len(posts)} posts from {source}")
                else:
                    self.logger.warning(f"No posts found for {source}")
                    
            except Exception as e:
                self.logger.error(f"Failed to process Reddit source {source}: {e}")
                failed_sources += 1
                continue
        
        self.logger.info(f"Multi-source Reddit processing complete: {successful_sources} successful, "
                        f"{failed_sources} failed sources")
        
        # Sort chronologically
        try:
            return sorted(all_posts, key=lambda p: p.get('timestamp', datetime.min.replace(tzinfo=timezone.utc)))
        except Exception as e:
            self.logger.error(f"Error sorting Reddit posts chronologically: {e}")
            return all_posts
    
    async def get_subreddit_post_titles(self, subreddit_name: str, sort_method: str, limit: int) -> List[Dict[str, str]]:
        """
        BONUS FEATURE: Get post titles from subreddit for interactive selection.
        
        Args:
            subreddit_name: Name of the subreddit
            sort_method: Sorting method (hot, new, top, best, rising)
            limit: Maximum number of titles to fetch
            
        Returns:
            List of dictionaries with post metadata for selection
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get submissions based on sort method
            if sort_method == 'hot':
                submissions = subreddit.hot(limit=limit)
            elif sort_method == 'new':
                submissions = subreddit.new(limit=limit)
            elif sort_method == 'top':
                submissions = subreddit.top(limit=limit, time_filter='day')
            elif sort_method == 'best':
                submissions = subreddit.best(limit=limit)
            elif sort_method == 'rising':
                submissions = subreddit.rising(limit=limit)
            else:
                return []
            
            post_titles = []
            for i, submission in enumerate(submissions, 1):
                try:
                    post_info = {
                        'index': str(i),
                        'id': submission.id,
                        'title': submission.title,
                        'author': str(submission.author) if submission.author else '[deleted]',
                        'score': str(submission.score),
                        'comments': str(submission.num_comments),
                        'url': f"https://reddit.com{submission.permalink}"
                    }
                    post_titles.append(post_info)
                except Exception as e:
                    self.logger.warning(f"Error processing submission for title list: {e}")
                    continue
            
            return post_titles
            
        except Exception as e:
            self.logger.error(f"Error getting post titles from r/{subreddit_name}: {e}")
            return []
    
    async def get_specific_posts_by_ids(self, post_ids: List[str], source_id: str) -> List[Dict[str, Any]]:
        """
        BONUS FEATURE: Get specific posts by their IDs (for interactive selection).
        
        Args:
            post_ids: List of Reddit post IDs
            source_id: Source identifier for tracking
            
        Returns:
            List of posts with comments in unified format
        """
        all_posts = []
        
        for post_id in post_ids:
            try:
                submission = self.reddit.submission(id=post_id)
                unified_post = self._create_post_with_comments(submission, source_id)
                all_posts.append(unified_post)
                
                self.logger.info(f"Successfully extracted post {post_id} with "
                               f"{unified_post['comments_extracted']} comments")
                
            except Exception as e:
                self.logger.error(f"Failed to extract post {post_id}: {e}")
                continue
        
        return all_posts 