"""
I.N.S.I.G.H.T. Mark II - Connector Package
The modular connector architecture for multi-source intelligence gathering.

This package provides a unified interface for all I.N.S.I.G.H.T. connectors
with automatic setup and configuration management.
"""

import os
import importlib
import inspect
from typing import Dict, List, Optional, Type
from dotenv import load_dotenv

from ..logs.core.logger_config import get_component_logger
from ..config.config_manager import ConfigManager

# __all__ = ['BaseConnector', 'TelegramConnector', 'RssConnector', 'YouTubeConnector', 'RedditConnector'] 

# Load environment variables
load_dotenv()

# Initialize logger for connector management
logger = get_component_logger('connector_package')

def discover_connectors() -> Dict[str, Type]:
    """
    Automatically discover all connector classes in the connectors package.
    
    Convention: 
    - Files must be named *_connector.py
    - Must contain a class inheriting from BaseConnector
    - Class name should end with 'Connector'
    
    Returns:
        Dictionary mapping platform names to connector classes
    """
    # Import BaseConnector first
    from .base_connector import BaseConnector
    
    connectors = {}
    connectors_dir = os.path.dirname(__file__)
    
    logger.info("🔍 Discovering connectors...")
    
    # Scan for connector files
    for filename in os.listdir(connectors_dir):
        if not filename.endswith('_connector.py') or filename.startswith('base_'):
            continue
        
        module_name = filename[:-3]  # Remove .py extension
        platform_name = module_name.replace('_connector', '')
        
        try:
            # Dynamic import
            module = importlib.import_module(f'.{module_name}', package=__name__)
            
            # Find connector classes in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if it's a connector class (inherits from BaseConnector but isn't BaseConnector itself)
                if (issubclass(obj, BaseConnector) and 
                    obj != BaseConnector and 
                    name.endswith('Connector')):
                    
                    connectors[platform_name] = obj
                    logger.info(f"✅ Discovered {platform_name} connector: {name}")
                    break
            else:
                logger.warning(f"⚠️ No valid connector class found in {filename}")
                
        except Exception as e:
            logger.error(f"❌ Failed to import {filename}: {e}")
    
    logger.info(f"🎯 Discovery complete: {len(connectors)} connectors found")
    return connectors

# Automatically discover all available connectors
AVAILABLE_CONNECTORS = discover_connectors()

def setup_connectors(config_manager: ConfigManager) -> Dict[str, 'BaseConnector']:
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
    
    logger.info(f"🚀 Setting up connectors for enabled sources: {enabled_sources}")
    
    for source_name in enabled_sources:
        if source_name not in AVAILABLE_CONNECTORS:
            logger.warning(f"❌ No connector available for source: {source_name}")
            logger.info(f"📋 Available connectors: {list(AVAILABLE_CONNECTORS.keys())}")
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
    
    logger.info(f"🎉 Setup complete: {len(setup_connectors_dict)}/{len(enabled_sources)} connectors ready")
    return setup_connectors_dict

def get_available_connector_types() -> List[str]:
    """
    Get list of all available connector types.
    
    Returns:
        List of platform names that have connectors available
    """
    return list(AVAILABLE_CONNECTORS.keys())

def create_connector(platform: str) -> Optional['BaseConnector']:
    """
    Create a single connector instance for the specified platform.
    
    Args:
        platform: Platform name (automatically detected from available connectors)
        
    Returns:
        Connector instance if successful, None otherwise
    """
    if platform not in AVAILABLE_CONNECTORS:
        logger.error(f"❌ No connector available for platform: {platform}")
        logger.info(f"📋 Available platforms: {list(AVAILABLE_CONNECTORS.keys())}")
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

def list_discovered_connectors() -> Dict[str, str]:
    """
    Get detailed information about all discovered connectors.
    
    Returns:
        Dictionary mapping platform names to their class names
    """
    return {platform: cls.__name__ for platform, cls in AVAILABLE_CONNECTORS.items()}



# Import BaseConnector for external use
from .base_connector import BaseConnector

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