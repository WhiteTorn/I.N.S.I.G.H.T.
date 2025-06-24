from abc import ABC, abstractmethod
from typing import List, Dict, Any
# import logging

from logs.core.logger_config import get_component_logger

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
        # self.logger = logging.getLogger(f"{__name__}.{platform_name}")
        self.logger = get_component_logger(f"{platform_name} Connector")
        
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
    def setup_connector(self) -> bool:
        """
        Setup the connector with platform-specific configuration and credentials.
        
        This method should handle:
        - Loading credentials from environment variables
        - Validating required configuration
        - Initializing platform-specific clients/sessions
        - Setting up any platform-specific parameters
        
        Returns:
            bool: True if setup was successful, False otherwise
            
        Note:
            This method should NOT establish connection - that's handled by connect().
            This is purely for initialization and credential validation.
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