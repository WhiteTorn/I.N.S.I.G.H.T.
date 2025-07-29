"""
I.N.S.I.G.H.T. Tool Registry System v1.0
Automatic discovery and exposure of connector capabilities for interactive mode.

This module provides a decorator-based system for marking connector methods
as interactive tools, with automatic discovery, validation, and execution.

Architecture:
- @expose_tool decorator: Mark methods as interactive tools
- ToolMetadata: Store tool information and parameters  
- ToolRegistry: Central registry for all tools
- discover_tools(): Find all exposed tools in a connector
"""

import inspect
from typing import Dict, List, Any, Callable, Optional, Union, get_type_hints
from dataclasses import dataclass, field
from functools import wraps
import asyncio

from ..logs.core.logger_config import get_component_logger

@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    type_hint: str
    description: str
    required: bool = True
    default: Any = None
    
@dataclass 
class ToolMetadata:
    """Comprehensive metadata for a connector tool."""
    name: str
    description: str
    parameters: Dict[str, ToolParameter]
    category: str = "general"
    examples: List[str] = field(default_factory=list)
    returns: str = "Data from the connector"
    notes: str = ""

class ToolRegistry:
    """
    Central registry for all connector tools.
    
    Manages tool discovery, registration, and execution across
    all available connectors in the I.N.S.I.G.H.T. system.
    """
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.logger = get_component_logger('tool_registry')
    
    def register_tool(self, connector_name: str, method: Callable, metadata: ToolMetadata):
        """Register a tool from a connector."""
        tool_id = f"{connector_name}.{metadata.name}"
        
        self.tools[tool_id] = {
            "connector": connector_name,
            "method": method,
            "metadata": metadata,
            "signature": inspect.signature(method)
        }
        
        self.logger.debug(f"Registered tool: {tool_id}")
    
    def get_available_tools(self, connector_name: Optional[str] = None) -> Dict[str, ToolMetadata]:
        """Get all available tools, optionally filtered by connector."""
        if connector_name:
            return {
                tool_id: tool_info["metadata"] 
                for tool_id, tool_info in self.tools.items() 
                if tool_info["connector"] == connector_name
            }
        return {tool_id: tool_info["metadata"] for tool_id, tool_info in self.tools.items()}
    
    def get_tool_by_id(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get tool information by ID."""
        return self.tools.get(tool_id)
    
    def get_categories(self) -> List[str]:
        """Get all available tool categories."""
        categories = set()
        for tool_info in self.tools.values():
            categories.add(tool_info["metadata"].category)
        return sorted(list(categories))
    
    def list_tools_by_category(self, category: str) -> Dict[str, ToolMetadata]:
        """Get tools filtered by category."""
        return {
            tool_id: tool_info["metadata"]
            for tool_id, tool_info in self.tools.items()
            if tool_info["metadata"].category == category
        }

# Global registry instance
tool_registry = ToolRegistry()

def expose_tool(
    name: str,
    description: str,
    parameters: Dict[str, Dict[str, Any]],
    category: str = "general",
    examples: List[str] = None,
    returns: str = "Data from the connector",
    notes: str = ""
):
    """
    Decorator to mark a method as an exposed interactive tool.
    
    Args:
        name: Tool name for interactive mode
        description: Human-readable description of what the tool does
        parameters: Dict of parameter_name -> {type: str, description: str, required: bool, default: Any}
        category: Tool category for organization (telegram, rss, youtube, etc.)
        examples: List of usage examples 
        returns: Description of what the tool returns
        notes: Additional notes or warnings
    
    Example:
        @expose_tool(
            name="fetch_recent_posts",
            description="Fetch the most recent posts from a Telegram channel",
            parameters={
                "channel": {
                    "type": "str", 
                    "description": "Channel username (with or without @)", 
                    "required": True
                },
                "limit": {
                    "type": "int", 
                    "description": "Number of posts to fetch (1-100)", 
                    "required": True
                }
            },
            category="telegram",
            examples=[
                "fetch_recent_posts('durov', 10)",
                "fetch_recent_posts('@telegram', 5)"
            ],
            returns="List of posts in unified format"
        )
    """
    def decorator(method):
        # Convert parameters dict to ToolParameter objects
        tool_parameters = {}
        for param_name, param_info in parameters.items():
            tool_parameters[param_name] = ToolParameter(
                type_hint=param_info.get("type", "Any"),
                description=param_info.get("description", "No description provided"),
                required=param_info.get("required", True),
                default=param_info.get("default", None)
            )
        
        # Store metadata on the method
        metadata = ToolMetadata(
            name=name,
            description=description,
            parameters=tool_parameters,
            category=category,
            examples=examples or [],
            returns=returns,
            notes=notes
        )
        
        method._tool_metadata = metadata
        method._is_exposed_tool = True
        
        @wraps(method)
        async def wrapper(*args, **kwargs):
            # The actual method call - no changes to functionality
            return await method(*args, **kwargs)
        
        return wrapper
    return decorator

def discover_tools(connector_instance) -> List[ToolMetadata]:
    """
    Discover all exposed tools in a connector instance.
    
    Args:
        connector_instance: Instance of a connector class that inherits from BaseConnector
        
    Returns:
        List of discovered tool metadata
    """
    logger = get_component_logger('tool_discovery')
    discovered_tools = []
    
    logger.info(f"🔍 Discovering tools in {connector_instance.platform_name} connector...")
    
    for attr_name in dir(connector_instance):
        try:
            attr = getattr(connector_instance, attr_name)
            
            # Check if it's an exposed tool
            if (callable(attr) and 
                hasattr(attr, '_is_exposed_tool') and 
                hasattr(attr, '_tool_metadata')):
                
                # Register with global registry
                tool_registry.register_tool(
                    connector_instance.platform_name,
                    attr,
                    attr._tool_metadata
                )
                
                discovered_tools.append(attr._tool_metadata)
                logger.debug(f"  ✅ Found tool: {attr._tool_metadata.name}")
                
        except Exception as e:
            logger.warning(f"  ⚠️ Error inspecting {attr_name}: {e}")
            continue
    
    logger.info(f"🎯 Discovered {len(discovered_tools)} tools in {connector_instance.platform_name}")
    return discovered_tools

def validate_tool_parameters(tool_metadata: ToolMetadata, provided_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate provided parameters against tool metadata.
    
    Args:
        tool_metadata: Tool metadata with parameter definitions
        provided_params: Parameters provided by user
        
    Returns:
        Dict with validation results: {"valid": bool, "errors": List[str], "warnings": List[str]}
    """
    errors = []
    warnings = []
    
    # Check required parameters
    for param_name, param_def in tool_metadata.parameters.items():
        if param_def.required and param_name not in provided_params:
            errors.append(f"Missing required parameter: {param_name}")
    
    # Check for unexpected parameters
    expected_params = set(tool_metadata.parameters.keys())
    provided_params_set = set(provided_params.keys())
    unexpected = provided_params_set - expected_params
    
    for param in unexpected:
        warnings.append(f"Unexpected parameter: {param}")
    
    # Basic type validation (can be extended)
    for param_name, value in provided_params.items():
        if param_name in tool_metadata.parameters:
            param_def = tool_metadata.parameters[param_name]
            if not _check_parameter_type(value, param_def.type_hint):
                errors.append(
                    f"Parameter '{param_name}' should be {param_def.type_hint}, "
                    f"got {type(value).__name__}"
                )
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def _check_parameter_type(value: Any, expected_type: str) -> bool:
    """Basic type checking for common types."""
    type_checkers = {
        "str": lambda x: isinstance(x, str),
        "int": lambda x: isinstance(x, int),
        "float": lambda x: isinstance(x, (int, float)),
        "bool": lambda x: isinstance(x, bool),
        "list": lambda x: isinstance(x, list),
        "dict": lambda x: isinstance(x, dict),
        "list[str]": lambda x: isinstance(x, list) and all(isinstance(i, str) for i in x),
        "list[int]": lambda x: isinstance(x, list) and all(isinstance(i, int) for i in x),
        "Any": lambda x: True,
        "Union[int, str]": lambda x: isinstance(x, (int, str))
    }
    
    checker = type_checkers.get(expected_type)
    if checker:
        return checker(value)
    
    # For unknown types, assume valid
    return True

# Utility functions for interactive mode
def get_tool_help_text(tool_id: str) -> Optional[str]:
    """Generate formatted help text for a tool."""
    tool_info = tool_registry.get_tool_by_id(tool_id)
    if not tool_info:
        return None
    
    metadata = tool_info["metadata"]
    
    help_text = f"""
🔧 {tool_id}
{'=' * (len(tool_id) + 3)}

Description: {metadata.description}
Category: {metadata.category}
Returns: {metadata.returns}

Parameters:
"""
    
    for param_name, param_def in metadata.parameters.items():
        required_text = "✅ Required" if param_def.required else "⚪ Optional"
        default_text = f" (default: {param_def.default})" if param_def.default is not None else ""
        
        help_text += f"  • {param_name} ({param_def.type_hint}) - {required_text}{default_text}\n"
        help_text += f"    {param_def.description}\n"
    
    if metadata.examples:
        help_text += "\nExamples:\n"
        for example in metadata.examples:
            help_text += f"  {example}\n"
    
    if metadata.notes:
        help_text += f"\nNotes: {metadata.notes}\n"
    
    return help_text

def list_tools_summary() -> str:
    """Generate a summary of all available tools."""
    tools_by_category = {}
    
    for tool_id, metadata in tool_registry.get_available_tools().items():
        category = metadata.category
        if category not in tools_by_category:
            tools_by_category[category] = []
        tools_by_category[category].append((tool_id, metadata.description))
    
    summary = "🛠️  Available Tools Summary\n"
    summary += "=" * 30 + "\n\n"
    
    for category, tools in sorted(tools_by_category.items()):
        summary += f"📁 {category.title()}\n"
        for tool_id, description in tools:
            summary += f"  🔧 {tool_id}: {description}\n"
        summary += "\n"
    
    summary += f"Total: {len(tool_registry.tools)} tools across {len(tools_by_category)} categories\n"
    summary += "Use 'help <tool_id>' for detailed information about specific tools.\n"
    
    return summary