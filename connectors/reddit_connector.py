import asyncio
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

# Primary: Async PRAW for official Reddit API access in async environments
try:
    import asyncpraw
    from asyncpraw.exceptions import InvalidURL, RedditAPIException, ClientException
    from asyncprawcore.exceptions import Forbidden, NotFound, ServerError
    ASYNCPRAW_AVAILABLE = True
except ImportError:
    ASYNCPRAW_AVAILABLE = False
    asyncpraw = None

# Fallback: Regular PRAW (for backwards compatibility)
try:
    import praw
    from praw.exceptions import InvalidURL, RedditAPIException, ClientException
    from prawcore.exceptions import Forbidden, NotFound, ServerError
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    praw = None

# Fallback: requests for JSON scraping (YARS-style)
import requests
import json

from .base_connector import BaseConnector


class RedditConnector(BaseConnector):
    """
    I.N.S.I.G.H.T. Reddit Connector v2.7 - "The Crowd Crier" - ASYNC EDITION
    
    Taps into the real-time pulse of public opinion and breaking news through Reddit.
    
    🔄 HYBRID APPROACH WITH ASYNC SUPPORT:
    • PRIMARY: Async PRAW - Native async/await support, perfect for async environments
    • FALLBACK: Regular PRAW - For backwards compatibility
    • TERTIARY: JSON Scraping - No API keys needed, YARS-style functionality
    
    Features:
    - Single post URL extraction (post + comments)
    - Subreddit monitoring with multiple sorting options (Hot, New, Top, Best, Rising)
    - Interactive post selection from subreddit listings
    - Automatic comment extraction and threading
    - HARDENED: Bulletproof error handling for all Reddit scenarios
    - Rate limiting compliance and timeout protection
    - Automatic fallback when API credentials not available
    - Native async/await support with Async PRAW
    
    This connector treats Reddit API failures as expected battlefield conditions
    and continues operations despite individual post/comment failures.
    """
    
    def __init__(self, client_id: str = None, client_secret: str = None, user_agent: str = None):
        """
        Initialize the Reddit connector with hybrid async approach.
        
        Args:
            client_id: Reddit API client ID (optional)
            client_secret: Reddit API client secret (optional) 
            user_agent: User agent string for Reddit API (optional)
        """
        super().__init__("reddit")
        
        # Configuration
        self.max_comments_per_post = 50  # Limit comments to prevent overwhelming data
        self.comment_depth_limit = 3     # How deep to traverse comment threads
        
        # Determine mode based on available libraries and credentials
        if client_id and client_secret:
            if ASYNCPRAW_AVAILABLE:
                self.mode = "asyncpraw"
                self.logger.info("Reddit Connector initialized in Async PRAW mode (native async support)")
            elif PRAW_AVAILABLE:
                self.mode = "praw"
                self.logger.warning("Async PRAW not available, falling back to regular PRAW (may show async warnings)")
            else:
                self.mode = "scraper"
                self.logger.warning("No PRAW libraries available, using scraper mode")
            
            self.client_id = client_id
            self.client_secret = client_secret
            self.user_agent = user_agent or "I.N.S.I.G.H.T. v2.7 The Crowd Crier - Async Edition"
            self.reddit = None
        else:
            self.mode = "scraper"
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': user_agent or 'I.N.S.I.G.H.T. v2.7 The Crowd Crier - Async Edition/1.0'
            })
            self.logger.info("No Reddit API credentials provided, using scraper mode")
    
    async def connect(self) -> None:
        """
        Establish connection to Reddit (API or scraper setup).
        """
        try:
            if self.mode == "asyncpraw":
                # Initialize Async Reddit API client (read-only)
                self.reddit = asyncpraw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                
                # Test the connection
                try:
                    # Try to access a public subreddit to test connection
                    test_sub = await self.reddit.subreddit("test")
                    await test_sub.load()  # Load basic info
                    self.logger.info(f"Connected to Reddit API successfully (Async PRAW mode)")
                except Exception as e:
                    self.logger.warning(f"Async PRAW connection test failed, falling back to scraper mode: {e}")
                    await self.reddit.close()  # Clean up
                    self.mode = "scraper"
                    self._setup_scraper_session()
                    
            elif self.mode == "praw":
                # Initialize regular Reddit API client (read-only)
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                
                # Test the connection
                try:
                    test_sub = self.reddit.subreddit("test") 
                    test_sub.display_name  # This should work for read-only
                    self.logger.info(f"Connected to Reddit API successfully (regular PRAW mode)")
                except Exception as e:
                    self.logger.warning(f"PRAW connection test failed, falling back to scraper mode: {e}")
                    self.mode = "scraper"
                    self._setup_scraper_session()
            else:
                self._setup_scraper_session()
                
        except Exception as e:
            self.logger.error(f"Failed to connect to Reddit: {e}")
            # Fall back to scraper mode if PRAW fails
            if self.mode in ["asyncpraw", "praw"]:
                self.logger.info("Falling back to scraper mode")
                self.mode = "scraper"
                self._setup_scraper_session()
            else:
                raise ConnectionError(f"Reddit connection failed: {e}")
    
    def _setup_scraper_session(self):
        """Setup session for JSON scraping."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'I.N.S.I.G.H.T. v2.7 The Crowd Crier - Async Edition/1.0'
        })
        self.logger.info("Reddit connector ready in scraper mode (no API key required)")
    
    async def disconnect(self) -> None:
        """
        Clean up Reddit connection.
        """
        if self.mode == "asyncpraw" and self.reddit:
            await self.reddit.close()
            self.reddit = None
        elif self.mode == "praw" and self.reddit:
            # Regular PRAW doesn't require explicit disconnection
            self.reddit = None
        elif self.mode == "scraper" and self.session:
            self.session.close()
        self.logger.info(f"Reddit connector disconnected ({self.mode} mode)")
    
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
    
    # --- Async PRAW-based methods ---
    async def _extract_comments_asyncpraw(self, submission, max_comments: int = None) -> List[Dict[str, Any]]:
        """
        Extract comments from a Reddit submission using Async PRAW with depth limiting.
        """
        comments = []
        max_comments = max_comments or self.max_comments_per_post
        
        try:
            # Replace "MoreComments" objects to get actual comments
            await submission.comments.replace_more(limit=0)
            
            async def extract_comment_recursive(comment, depth=0):
                if len(comments) >= max_comments or depth > self.comment_depth_limit:
                    return
                
                try:
                    # Load comment data
                    await comment.load()
                    
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
                            async for reply in comment.replies:
                                await extract_comment_recursive(reply, depth + 1)
                                
                except Exception as e:
                    self.logger.warning(f"Error extracting comment {getattr(comment, 'id', 'unknown')}: {e}")
                    pass
            
            # Start extraction from top-level comments
            async for comment in submission.comments:
                await extract_comment_recursive(comment)
                if len(comments) >= max_comments:
                    break
            
            return comments
            
        except Exception as e:
            self.logger.error(f"Error extracting comments from submission: {e}")
            return []
    
    # --- Regular PRAW-based methods (for backwards compatibility) ---
    def _extract_comments_praw(self, submission, max_comments: int = None) -> List[Dict[str, Any]]:
        """
        Extract comments from a Reddit submission using regular PRAW with depth limiting.
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
    
    # --- JSON Scraper methods (YARS-style) ---
    def _fetch_reddit_json(self, url: str) -> Optional[Dict]:
        """
        Fetch Reddit data via JSON endpoint (no API key required).
        """
        try:
            # Add .json to Reddit URLs to get JSON response
            if not url.endswith('.json'):
                url = url.rstrip('/') + '.json'
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Failed to fetch Reddit JSON from {url}: {e}")
            return None
    
    def _extract_comments_json(self, post_data: Dict, max_comments: int = None) -> List[Dict[str, Any]]:
        """
        Extract comments from Reddit JSON response.
        """
        comments = []
        max_comments = max_comments or self.max_comments_per_post
        
        try:
            # Reddit JSON structure: [post_data, comments_data]
            if len(post_data) < 2:
                return comments
            
            comments_data = post_data[1]['data']['children']
            
            def extract_comment_recursive(comment_item, depth=0):
                if len(comments) >= max_comments or depth > self.comment_depth_limit:
                    return
                
                try:
                    comment = comment_item['data']
                    
                    # Skip deleted/removed comments and "more" objects
                    if comment.get('body') and comment['body'] not in ['[deleted]', '[removed]'] and comment.get('author'):
                        comment_data = {
                            'id': comment['id'],
                            'author': comment['author'],
                            'body': comment['body'],
                            'score': comment.get('score', 0),
                            'created_utc': datetime.fromtimestamp(comment['created_utc'], tz=timezone.utc),
                            'permalink': f"https://reddit.com{comment['permalink']}",
                            'depth': depth,
                            'is_submitter': comment.get('is_submitter', False),
                            'parent_id': comment.get('parent_id', '')
                        }
                        comments.append(comment_data)
                        
                        # Process replies
                        if comment.get('replies') and isinstance(comment['replies'], dict):
                            replies = comment['replies']['data']['children']
                            for reply in replies:
                                if reply['kind'] == 't1':  # Comment type
                                    extract_comment_recursive(reply, depth + 1)
                                
                except Exception as e:
                    self.logger.warning(f"Error extracting comment: {e}")
                    pass
            
            # Process top-level comments
            for comment_item in comments_data:
                if comment_item['kind'] == 't1':  # Comment type
                    extract_comment_recursive(comment_item)
                    if len(comments) >= max_comments:
                        break
            
            return comments
            
        except Exception as e:
            self.logger.error(f"Error extracting comments from JSON: {e}")
            return []
    
    async def _create_post_with_comments(self, submission_data, source_id: str, comments: List[Dict] = None) -> Dict[str, Any]:
        """
        Create unified post data including comments (works with all modes).
        """
        try:
            if self.mode == "asyncpraw":
                # Async PRAW submission object
                await submission_data.load()  # Ensure all data is loaded
                
                post_content = submission_data.title
                if submission_data.selftext and submission_data.selftext.strip():
                    post_content += f"\n\n{submission_data.selftext}"
                
                # Get media URLs
                media_urls = []
                if submission_data.url and not submission_data.is_self:
                    media_urls.append(submission_data.url)
                
                # Extract comments if not provided
                if comments is None:
                    comments = await self._extract_comments_asyncpraw(submission_data)
                
                # Create main post
                unified_post = self._create_unified_post(
                    source_platform="reddit",
                    source_id=source_id,
                    post_id=submission_data.id,
                    author=str(submission_data.author) if submission_data.author else '[deleted]',
                    content=post_content,
                    timestamp=datetime.fromtimestamp(submission_data.created_utc, tz=timezone.utc),
                    media_urls=media_urls,
                    post_url=f"https://reddit.com{submission_data.permalink}"
                )
                
                # Add Reddit-specific metadata
                unified_post['subreddit'] = str(submission_data.subreddit)
                unified_post['score'] = submission_data.score
                unified_post['upvote_ratio'] = submission_data.upvote_ratio
                unified_post['num_comments'] = submission_data.num_comments
                unified_post['is_over_18'] = submission_data.over_18
                unified_post['post_flair'] = submission_data.link_flair_text
                
            elif self.mode == "praw":
                # Regular PRAW submission object
                post_content = submission_data.title
                if submission_data.selftext and submission_data.selftext.strip():
                    post_content += f"\n\n{submission_data.selftext}"
                
                # Get media URLs
                media_urls = []
                if submission_data.url and not submission_data.is_self:
                    media_urls.append(submission_data.url)
                
                # Extract comments if not provided
                if comments is None:
                    comments = self._extract_comments_praw(submission_data)
                
                # Create main post
                unified_post = self._create_unified_post(
                    source_platform="reddit",
                    source_id=source_id,
                    post_id=submission_data.id,
                    author=str(submission_data.author) if submission_data.author else '[deleted]',
                    content=post_content,
                    timestamp=datetime.fromtimestamp(submission_data.created_utc, tz=timezone.utc),
                    media_urls=media_urls,
                    post_url=f"https://reddit.com{submission_data.permalink}"
                )
                
                # Add Reddit-specific metadata
                unified_post['subreddit'] = str(submission_data.subreddit)
                unified_post['score'] = submission_data.score
                unified_post['upvote_ratio'] = submission_data.upvote_ratio
                unified_post['num_comments'] = submission_data.num_comments
                unified_post['is_over_18'] = submission_data.over_18
                unified_post['post_flair'] = submission_data.link_flair_text
                
            else:
                # JSON submission data
                post_data = submission_data['data']
                post_content = post_data['title']
                if post_data.get('selftext') and post_data['selftext'].strip():
                    post_content += f"\n\n{post_data['selftext']}"
                
                # Get media URLs
                media_urls = []
                if post_data.get('url') and not post_data.get('is_self'):
                    media_urls.append(post_data['url'])
                
                # Create main post
                unified_post = self._create_unified_post(
                    source_platform="reddit",
                    source_id=source_id,
                    post_id=post_data['id'],
                    author=post_data.get('author', '[deleted]'),
                    content=post_content,
                    timestamp=datetime.fromtimestamp(post_data['created_utc'], tz=timezone.utc),
                    media_urls=media_urls,
                    post_url=f"https://reddit.com{post_data['permalink']}"
                )
                
                # Add Reddit-specific metadata
                unified_post['subreddit'] = post_data.get('subreddit', 'unknown')
                unified_post['score'] = post_data.get('score', 0)
                unified_post['upvote_ratio'] = post_data.get('upvote_ratio', 0)
                unified_post['num_comments'] = post_data.get('num_comments', 0)
                unified_post['is_over_18'] = post_data.get('over_18', False)
                unified_post['post_flair'] = post_data.get('link_flair_text')
            
            # Add comments to post
            unified_post['comments'] = comments or []
            unified_post['comments_extracted'] = len(comments or [])
            
            # Add legacy compatibility fields (like other connectors do)
            unified_post['date'] = unified_post['timestamp']  # Critical: render_briefing_to_console expects 'date' field
            unified_post['text'] = unified_post['content']     # Backwards compatibility
            unified_post['link'] = unified_post['post_url']    # Backwards compatibility
            unified_post['id'] = unified_post['post_id']       # Backwards compatibility
            
            return unified_post
            
        except Exception as e:
            self.logger.error(f"Error creating post data: {e}")
            raise ValueError(f"Failed to create unified post: {e}")
    
    async def _fetch_post_by_url(self, reddit_url: str) -> List[Dict[str, Any]]:
        """
        Fetch a single Reddit post by URL including comments (hybrid approach).
        """
        self.logger.info(f"Extracting Reddit post from URL: {reddit_url} (mode: {self.mode})")
        
        try:
            post_id = self._extract_post_id_from_url(reddit_url)
            if not post_id:
                self.logger.error(f"Could not extract post ID from URL: {reddit_url}")
                return []
            
            if self.mode == "asyncpraw":
                # Use Async PRAW
                submission = await self.reddit.submission(id=post_id)
                unified_post = await self._create_post_with_comments(submission, f"url:{reddit_url}")
            elif self.mode == "praw":
                # Use regular PRAW
                submission = self.reddit.submission(id=post_id)
                unified_post = await self._create_post_with_comments(submission, f"url:{reddit_url}")
            else:
                # Use JSON scraping
                json_data = self._fetch_reddit_json(reddit_url)
                if not json_data or len(json_data) < 1:
                    return []
                
                submission_data = json_data[0]['data']['children'][0]
                comments = self._extract_comments_json(json_data)
                unified_post = await self._create_post_with_comments(submission_data, f"url:{reddit_url}", comments)
            
            self.logger.info(f"Successfully extracted post {post_id} with {unified_post['comments_extracted']} comments")
            return [unified_post]
            
        except Exception as e:
            self.logger.error(f"Error fetching Reddit post from URL {reddit_url}: {e}")
            return []
    
    async def _fetch_subreddit_posts(self, subreddit_name: str, sort_method: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch posts from a subreddit with specified sorting (hybrid approach).
        """
        self.logger.info(f"Fetching {limit} {sort_method} posts from r/{subreddit_name} (mode: {self.mode})")
        
        try:
            if self.mode == "asyncpraw":
                return await self._fetch_subreddit_posts_asyncpraw(subreddit_name, sort_method, limit)
            elif self.mode == "praw":
                return await self._fetch_subreddit_posts_praw(subreddit_name, sort_method, limit)
            else:
                return await self._fetch_subreddit_posts_json(subreddit_name, sort_method, limit)
                
        except Exception as e:
            self.logger.error(f"Error fetching from r/{subreddit_name}: {e}")
            return []
    
    async def _fetch_subreddit_posts_asyncpraw(self, subreddit_name: str, sort_method: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch subreddit posts using Async PRAW."""
        try:
            subreddit = await self.reddit.subreddit(subreddit_name)
            
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
            
            async for submission in submissions:
                try:
                    unified_post = await self._create_post_with_comments(
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
            
            self.logger.info(f"Async subreddit processing complete: {successful_extractions} successful, "
                           f"{failed_extractions} failed extractions")
            return all_posts
            
        except Exception as e:
            self.logger.error(f"Async PRAW error fetching from r/{subreddit_name}: {e}")
            return []
    
    async def _fetch_subreddit_posts_praw(self, subreddit_name: str, sort_method: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch subreddit posts using regular PRAW."""
        try:
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
                    unified_post = await self._create_post_with_comments(
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
            
        except Exception as e:
            self.logger.error(f"PRAW error fetching from r/{subreddit_name}: {e}")
            return []
    
    async def _fetch_subreddit_posts_json(self, subreddit_name: str, sort_method: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch subreddit posts using JSON scraping."""
        try:
            # Build Reddit JSON URL
            url = f"https://www.reddit.com/r/{subreddit_name}/{sort_method}.json?limit={limit}"
            
            json_data = self._fetch_reddit_json(url)
            if not json_data or 'data' not in json_data:
                return []
            
            posts_data = json_data['data']['children']
            all_posts = []
            successful_extractions = 0
            failed_extractions = 0
            
            for post_item in posts_data:
                try:
                    if post_item['kind'] != 't3':  # Not a submission
                        continue
                        
                    # For JSON mode, we'll skip individual comment extraction per post
                    # to avoid too many requests. Just get the main post.
                    unified_post = await self._create_post_with_comments(
                        post_item,
                        f"r/{subreddit_name}:{sort_method}",
                        []  # No comments for subreddit listings in scraper mode
                    )
                    all_posts.append(unified_post)
                    successful_extractions += 1
                    
                    self.logger.info(f"Processed post {post_item['data']['id']}: "
                                   f"'{post_item['data']['title'][:50]}...'")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process post: {e}")
                    failed_extractions += 1
                    continue
            
            self.logger.info(f"JSON subreddit processing complete: {successful_extractions} successful, "
                           f"{failed_extractions} failed extractions")
            return all_posts
            
        except Exception as e:
            self.logger.error(f"JSON error fetching from r/{subreddit_name}: {e}")
            return []
    
    # --- Main interface methods ---
    async def fetch_posts(self, source_identifier: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch posts from Reddit using hybrid async approach.
        
        Supports two modes:
        1. Reddit post URL - extracts single post with comments
        2. Subreddit name - extracts N posts (with/without comments based on mode)
        
        HARDENED: Individual post failures do not affect other posts.
        
        Args:
            source_identifier: Reddit post URL or subreddit name (r/subredditname or subredditname)
            limit: Maximum number of posts to fetch (ignored for single URL)
            
        Returns:
            List of posts in unified format with comments
        """
        if not (self.reddit or self.session):
            self.logger.error("Reddit connector not connected")
            return []
        
        try:
            # Check if it's a Reddit URL
            if 'reddit.com' in source_identifier or 'redd.it' in source_identifier:
                return await self._fetch_post_by_url(source_identifier)
            
            # Treat as subreddit name
            subreddit_name = source_identifier.replace('r/', '').strip()
            
            # Default to 'hot' sorting for basic fetch_posts call
            return await self._fetch_subreddit_posts(subreddit_name, 'hot', limit)
            
        except Exception as e:
            self.logger.error(f"Error in fetch_posts for {source_identifier}: {e}")
            return []
    
    async def fetch_posts_by_timeframe(self, sources: List[str], days: int) -> List[Dict[str, Any]]:
        """
        Fetch Reddit posts from multiple sources within a specific timeframe.
        
        HARDENED: Individual source failures do not affect other sources.
        """
        if days == 0:
            self.logger.info(f"Starting Reddit 'End of Day' briefing ({self.mode} mode)...")
            time_filter = 'day'
        else:
            self.logger.info(f"Starting Reddit Historical briefing for {days} days ({self.mode} mode)...")
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
    
    # --- Placeholder methods for the advanced features referenced in main.py ---
    async def fetch_post_with_comments(self, post_url: str) -> List[Dict[str, Any]]:
        """Fetch a single post with comments (alias for URL fetching)."""
        return await self._fetch_post_by_url(post_url)
    
    async def fetch_subreddit_posts_interactive(self, subreddit: str, limit: int, sort: str) -> List[Dict[str, Any]]:
        """Fetch subreddit posts (simplified interactive mode).""" 
        return await self._fetch_subreddit_posts(subreddit, sort, limit) 