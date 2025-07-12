"""
INSIGHT Post Utilities - Robust Post Sorting and Processing
==========================================================

Extracted from test files and enhanced with error handling
Handles all post types with unified date processing
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date, timezone, timedelta
from collections import defaultdict
import logging

class PostSorter:
    """
    Robust post sorting utilities with comprehensive error handling
    Supports all post types from any connector (Telegram, RSS, Reddit, etc.)
    """
    
    @staticmethod
    def _safe_get_date(post: Dict[str, Any]) -> datetime:
        """
        Safely extract date from post with multiple fallback strategies
        
        Args:
            post: Post dictionary from any connector
            
        Returns:
            datetime object (defaults to datetime.min if no valid date found)
        """
        if not isinstance(post, dict):
            return datetime.min
        
        # Try multiple date field names
        date_fields = ['date', 'created_at', 'published', 'timestamp', 'time']
        
        for field in date_fields:
            date_value = post.get(field)
            
            if date_value is None:
                continue
            
            try:
                # Already a datetime object
                if isinstance(date_value, datetime):
                    return date_value
                
                # String date - try to parse
                if isinstance(date_value, str):
                    # Common formats
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                        try:
                            return datetime.strptime(date_value, fmt)
                        except ValueError:
                            continue
                    
                    # Try ISO format parsing
                    try:
                        return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                    except ValueError:
                        continue
                
                # Unix timestamp (int or float)
                if isinstance(date_value, (int, float)):
                    return datetime.fromtimestamp(date_value)
                
            except (ValueError, TypeError, OSError) as e:
                logging.warning(f"Failed to parse date field '{field}' with value '{date_value}': {e}")
                continue
        
        # No valid date found
        logging.warning(f"No valid date found in post: {post.get('title', 'Unknown')}")
        return datetime.min
    
    @staticmethod
    def sort_posts_by_date(posts: List[Dict[str, Any]], reverse: bool = True) -> List[Dict[str, Any]]:
        """
        Sort posts by date with robust error handling
        
        Args:
            posts: List of post dictionaries from any connector
            reverse: True for newest first, False for oldest first
            
        Returns:
            Sorted list of posts
        """
        if not posts or not isinstance(posts, list):
            return []
        
        try:
            return sorted(
                [post for post in posts if isinstance(post, dict)],  # Filter out invalid posts
                key=lambda post: PostSorter._safe_get_date(post),
                reverse=reverse
            )
        except Exception as e:
            logging.error(f"Failed to sort posts by date: {e}")
            return posts  # Return original list if sorting fails
    
    @staticmethod
    def sort_posts_by_day(posts: List[Dict[str, Any]]) -> Dict[date, List[Dict[str, Any]]]:
        """
        Group and sort posts by day with robust error handling
        
        Args:
            posts: List of post dictionaries from any connector
            
        Returns:
            Dictionary with date keys and sorted post lists as values
            Dates are sorted newest first, posts within each day are newest first
        """
        if not posts or not isinstance(posts, list):
            return {}
        
        posts_by_day = defaultdict(list)
        
        # Group posts by day
        posts = PostSorter._convert_posts_timezone(posts)
        for post in posts:
            if not isinstance(post, dict):
                continue
            
            try:
                post_date = PostSorter._safe_get_date(post)
                if post_date != datetime.min:
                    day_key = post_date.date()
                    posts_by_day[day_key].append(post)
            except Exception as e:
                logging.warning(f"Failed to process post for day grouping: {e}")
                continue
        
        # Sort days (newest first) and posts within each day (newest first)
        try:
            sorted_by_days = {}
            for day in sorted(posts_by_day.keys(), reverse=True):
                sorted_by_days[day] = PostSorter.sort_posts_by_date(posts_by_day[day], reverse=True)
            
            return sorted_by_days
        except Exception as e:
            logging.error(f"Failed to sort posts by day: {e}")
            return dict(posts_by_day)  # Return unsorted if sorting fails
    
    @staticmethod
    def filter_posts_by_date_range(
        posts: List[Dict[str, Any]], 
        start_date: Optional[Union[date, datetime]] = None,
        end_date: Optional[Union[date, datetime]] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter posts by date range with robust error handling
        
        Args:
            posts: List of post dictionaries
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            Filtered list of posts within date range
        """
        if not posts or not isinstance(posts, list):
            return []
        
        if start_date is None and end_date is None:
            return posts
        
        filtered_posts = []
        
        for post in posts:
            if not isinstance(post, dict):
                continue
            
            try:
                post_date = PostSorter._safe_get_date(post)
                if post_date == datetime.min:
                    continue
                
                post_date_only = post_date.date()
                
                # Check start date
                if start_date is not None:
                    start_date_only = start_date.date() if isinstance(start_date, datetime) else start_date
                    if post_date_only < start_date_only:
                        continue
                
                # Check end date
                if end_date is not None:
                    end_date_only = end_date.date() if isinstance(end_date, datetime) else end_date
                    if post_date_only > end_date_only:
                        continue
                
                filtered_posts.append(post)
                
            except Exception as e:
                logging.warning(f"Failed to filter post by date range: {e}")
                continue
        
        return filtered_posts
    
    @staticmethod
    def get_posts_for_specific_day(posts: List[Dict[str, Any]], target_date: Union[date, datetime]) -> List[Dict[str, Any]]:
        """
        Get all posts for a specific day
        
        Args:
            posts: List of post dictionaries
            target_date: Target date to filter by
            
        Returns:
            List of posts from the specified day, sorted newest first
        """
        if isinstance(target_date, datetime):
            target_date = target_date.date()
        
        return PostSorter.filter_posts_by_date_range(posts, target_date, target_date)
    

    def _convert_to_user_timezone(self, dt: datetime) -> datetime:
        """
        Convert a datetime object to the user's timezone
        """
        if dt == datetime.min:
            return dt
        
        try:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(self.user_timezone)
        except Exception:
            logging.warning(f"Failed to convert datetime to user timezone: {dt}")
            return dt
        
    def _convert_posts_timezone(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        converted_posts = []
        for post in posts:
            if not isinstance(post, dict):
                continue
        
            if 'date' in post:
                original_date = post['date']
                converted_date = self._convert_to_user_timezone(original_date)
                post['date'] = converted_date

            converted_posts.append(post)
        return converted_posts
        
    
    
