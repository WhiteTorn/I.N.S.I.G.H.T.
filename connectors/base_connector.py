from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

class BaseConnector(ABC):
    """
    The abstract blueprint for all I.N.S.I.G.H.T. connectors.
    
    This class defines the standard interface for fetching and processing data
    from any source platform. All connectors must implement this contract
    to ensure consistency and interoperability within the I.N.S.I.G.H.T. ecosystem.
    
    The Unified Data Model:
    Every connector must return data in this standardized format:
    {
        "platform": str,           # Platform identifier ("telegram", "youtube", "reddit", "rss")  
        "source": str,             # Source exactly as user enters (no normalization)
        "url": str,                # Direct link to original post (serves as unique ID)
        "content": str,            # Full text content
        "date": datetime,          # Precise UTC timestamp
        "media_urls": List[str],   # Media URLs
        "categories": List[str],   # Tags/topics/hashtags (empty list if none)
        "metadata": Dict[str, Any] # Platform-specific data (empty dict for Mark II)
    }
    
    This structure follows the principle of maximum simplicity while maintaining
    all essential information needed for post rendering and processing.
    Future-ready with categories and metadata for advanced features.
    """
    
    def __init__(self, platform_name: str):
        """
        Initialize the connector with its platform identifier.
        
        Args:
            platform_name: The name of the platform this connector handles
        """
        self.platform_name = platform_name
        self.logger = logging.getLogger(f"{__name__}.{platform_name}")
        
    @abstractmethod
    async def connect(self) -> None:
        """
        Establish connection to the data source.
        This method should handle authentication, API setup, etc.
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Gracefully disconnect from the data source.
        Clean up resources, close connections, etc.
        """
        pass
    
    @abstractmethod
    async def fetch_posts(self, source_identifier: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch the latest N posts from the specified source.
        
        This is the core method that every connector must implement.
        It should fetch raw data from the source, process it, and return
        it in the Unified Data Model format.
        
        Args:
            source_identifier: Platform-specific identifier (channel name, feed URL, etc.)
            limit: Maximum number of posts to fetch
            
        Returns:
            List of post dictionaries in Unified Data Model format
            
        Raises:
            ConnectionError: If unable to connect to the source
            ValueError: If source_identifier is invalid
            Exception: For other platform-specific errors
        """
        pass
    
    @abstractmethod
    async def fetch_posts_by_timeframe(self, sources: List[str], days: int) -> List[Dict[str, Any]]:
        """
        Fetch all posts from multiple sources within a specific timeframe.
        
        This method supports the briefing functionality where we want to gather
        intelligence from multiple sources over a specific time period.
        
        Args:
            sources: List of source identifiers to monitor
            days: Number of days to look back (0 for "today only")
            
        Returns:
            List of post dictionaries in Unified Data Model format, sorted chronologically
        """
        pass
    
    def _validate_unified_post(self, post: Dict[str, Any]) -> bool:
        """
        Validate that a post dictionary conforms to the Unified Data Model.
        
        Args:
            post: Post dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            "platform", "source", "url", "content", "date", "media_urls", "categories", "metadata"
        ]
        
        for field in required_fields:
            if field not in post:
                self.logger.error(f"Missing required field '{field}' in post data")
                return False
                
        # Validate types
        if not isinstance(post["media_urls"], list):
            self.logger.error("media_urls must be a list")
            return False
            
        if not isinstance(post["categories"], list):
            self.logger.error("categories must be a list")
            return False
            
        if not isinstance(post["metadata"], dict):
            self.logger.error("metadata must be a dict")
            return False
            
        return True
    
    def _create_unified_post(self, **kwargs) -> Dict[str, Any]:
        """
        Helper method to create a properly formatted unified post.
        
        This ensures all connectors create posts with the same structure.
        """
        post = {
            "platform": kwargs.get("platform", self.platform_name),
            "source": kwargs.get("source", ""),
            "url": kwargs.get("url", ""),
            "content": kwargs.get("content", ""),
            "date": kwargs.get("date", None),
            "media_urls": kwargs.get("media_urls", []),
            "categories": kwargs.get("categories", []),
            "metadata": kwargs.get("metadata", {})
        }
        
        if not self._validate_unified_post(post):
            raise ValueError("Created post does not conform to Unified Data Model")
            
        return post 