"""
I.N.S.I.G.H.T. Mark II - Connector Package
The modular connector architecture for multi-source intelligence gathering.

This package provides a unified interface for all I.N.S.I.G.H.T. connectors
with automatic setup and configuration management.
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

from logs.core.logger_config import get_component_logger
from config.config_manager import ConfigManager

from .base_connector import BaseConnector
from .telegram_connector import TelegramConnector
from .rss_connector import RssConnector
from .youtube_connector import YouTubeConnector
from .reddit_connector import RedditConnector

# __all__ = ['BaseConnector', 'TelegramConnector', 'RssConnector', 'YouTubeConnector', 'RedditConnector'] 

# Load environment variables
load_dotenv()

# Initialize logger for connector management
logger = get_component_logger('connector_package')

AVAILABLE_CONNECTORS = {
    'telegram': TelegramConnector,
    'rss': RssConnector,
    'youtube': YouTubeConnector,
    'reddit': RedditConnector
}

def setup_connectors(config_manager: ConfigManager) -> Dict[str, BaseConnector]:
    """
    Setup all enabled connectors based on configuration.
    
    Args:
        config_manager: ConfigManager instance with loaded configuration
        
    Returns:
        Dictionary of successfully setup connectors {platform_name: connector_instance}
    """
    config = config_manager.load_config()
    enabled_sources = config_manager.get_enabled_sources(config)
    
    setup_connectors_dict = {}
    
    logger.info(f"Setting up connectors for enabled sources: {enabled_sources}")
    
    for source_name in enabled_sources:
        if source_name not in AVAILABLE_CONNECTORS:
            logger.warning(f"No connector available for source: {source_name}")
            continue
            
        try:
            # Create connector instance
            connector_class = AVAILABLE_CONNECTORS[source_name]
            connector = connector_class()
            
            # Setup connector with credentials and configuration
            if connector.setup_connector():
                setup_connectors_dict[source_name] = connector
                logger.info(f"✅ {source_name.title()} connector setup successful")
            else:
                logger.warning(f"❌ {source_name.title()} connector setup failed")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize {source_name} connector: {e}")
    
    logger.info(f"Successfully setup {len(setup_connectors_dict)} out of {len(enabled_sources)} enabled connectors")
    return setup_connectors_dict

def get_available_connector_types() -> List[str]:
    """
    Get list of all available connector types.
    
    Returns:
        List of platform names that have connectors available
    """
    return list(AVAILABLE_CONNECTORS.keys())

def create_connector(platform: str) -> Optional[BaseConnector]:
    """
    Create a single connector instance for the specified platform.
    
    Args:
        platform: Platform name (telegram, rss, youtube, reddit)
        
    Returns:
        Connector instance if successful, None otherwise
    """
    if platform not in AVAILABLE_CONNECTORS:
        logger.error(f"No connector available for platform: {platform}")
        return None
        
    try:
        connector_class = AVAILABLE_CONNECTORS[platform]
        connector = connector_class()
        
        if connector.setup_connector():
            logger.info(f"✅ {platform.title()} connector created and setup successful")
            return connector
        else:
            logger.warning(f"❌ {platform.title()} connector setup failed")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to create {platform} connector: {e}")
        return None

__all__ = [
    'BaseConnector', 
    'TelegramConnector', 
    'RssConnector', 
    'YouTubeConnector', 
    'RedditConnector',
    'setup_connectors',
    'get_available_connector_types',
    'create_connector',
    'AVAILABLE_CONNECTORS'
]