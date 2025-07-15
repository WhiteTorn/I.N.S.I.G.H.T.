# 🛠️ I.N.S.I.G.H.T. Connector Tools Development Guide

## 📋 Table of Contents
1. [What are Connector Tools?](#what-are-connector-tools)
2. [The @expose_tool Decorator](#the-expose_tool-decorator)
3. [Step-by-Step: Creating Your First Tool](#step-by-step-creating-your-first-tool)
4. [Parameter Types & Validation](#parameter-types--validation)
5. [Best Practices](#best-practices)
6. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
7. [Testing Your Tools](#testing-your-tools)

---

## 🎯 What are Connector Tools?

**Connector Tools** are special methods in your connector classes that can be discovered and used in **Interactive Mode**. Think of them as "superpowers" that users can call directly without writing code.

### 🔄 Normal Method vs Tool Method

**❌ Normal Method (Hidden):**
```python
async def fetch_posts(self, channel: str, limit: int):
    """This method exists but users can't discover it"""
    return await self._fetch_internal(channel, limit)
```

**✅ Tool Method (Discoverable):**
```python
@expose_tool(
    name="fetch_recent_posts",
    description="Fetch recent posts from a channel", 
    parameters={"channel": {"type": "str", "description": "Channel name", "required": True}},
    category="telegram"
)
async def fetch_posts(self, channel: str, limit: int):
    """This method can be discovered and used in interactive mode!"""
    return await self._fetch_internal(channel, limit)
```

---

## 🎨 The @expose_tool Decorator

The `@expose_tool` decorator is like a "label" you put on methods to make them discoverable. Here's what each part does:

### 📝 Basic Structure
```python
@expose_tool(
    name="tool_name",           # What users type to call it
    description="What it does", # Human-readable explanation
    parameters={},              # What inputs it needs
    category="platform_name"    # Which group it belongs to
)
async def your_method(self, param1, param2):
    # Your code here
    pass
```

### 🧩 Parameter Breakdown

#### 1. **name** (Required)
- **What it is:** The command name users will type
- **Rules:** 
  - Use snake_case (lowercase with underscores)
  - Be descriptive but not too long
  - Unique within your connector

```python
# ✅ Good names
name="fetch_recent_posts"
name="get_user_info" 
name="search_messages"

# ❌ Bad names  
name="fetch"           # Too vague
name="FetchPosts"      # Wrong case
name="fetch-posts"     # Wrong separator
```

#### 2. **description** (Required)
- **What it is:** A clear explanation of what the tool does
- **Rules:**
  - Write for humans, not programmers
  - Start with a verb (action word)
  - Be specific about what it returns

```python
# ✅ Good descriptions
description="Fetch the most recent posts from a Telegram channel"
description="Search for messages containing specific keywords"
description="Get detailed information about a YouTube video"

# ❌ Bad descriptions
description="Gets stuff"                    # Too vague
description="This method fetches posts"     # Too technical
description="Posts"                         # Not a sentence
```

#### 3. **parameters** (Required)
- **What it is:** Dictionary describing each input your method needs
- **Structure:** `{"param_name": {"type": "...", "description": "...", "required": True/False}}`

```python
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
    },
    "include_media": {
        "type": "bool",
        "description": "Whether to include media URLs",
        "required": False,
        "default": True
    }
}
```

#### 4. **category** (Required)
- **What it is:** Which platform/connector this belongs to
- **Rules:** Should match your connector's platform_name

```python
# For TelegramConnector
category="telegram"

# For YouTubeConnector  
category="youtube"

# For RssConnector
category="rss"
```

#### 5. **examples** (Optional but Recommended)
- **What it is:** List of example commands showing how to use the tool
- **Purpose:** Helps users understand the syntax

```python
examples=[
    "fetch_recent_posts('durov', 10)",
    "fetch_recent_posts('@telegram', 50)",
    "fetch_recent_posts('news_channel', 20)"
]
```

#### 6. **returns** (Optional but Recommended)
- **What it is:** Description of what the tool gives back
- **Purpose:** Helps users understand what to expect

```python
returns="List of posts in unified format with content, date, and media URLs"
```

#### 7. **notes** (Optional)
- **What it is:** Important warnings or additional information
- **Purpose:** Help users avoid common mistakes

```python
notes="Large channels may take several minutes. Use limit wisely to avoid timeouts."
```

---

## 🚀 Step-by-Step: Creating Your First Tool

Let's create a simple tool for getting channel information:

### Step 1: Write the Method
```python
async def get_channel_info(self, channel_name: str) -> Dict[str, Any]:
    """Get basic information about a Telegram channel."""
    # Your implementation here
    channel_data = await self._fetch_channel_details(channel_name)
    return {
        "name": channel_data.title,
        "subscribers": channel_data.participants_count,
        "description": channel_data.about
    }
```

### Step 2: Add the Decorator
```python
@expose_tool(
    name="get_channel_info",
    description="Get basic information about a Telegram channel",
    parameters={
        "channel_name": {
            "type": "str",
            "description": "Channel username (with or without @)",
            "required": True
        }
    },
    category="telegram",
    examples=["get_channel_info('durov')", "get_channel_info('@telegram')"],
    returns="Dictionary with channel name, subscriber count, and description"
)
async def get_channel_info(self, channel_name: str) -> Dict[str, Any]:
    """Get basic information about a Telegram channel."""
    # Implementation stays the same
    channel_data = await self._fetch_channel_details(channel_name)
    return {
        "name": channel_data.title,
        "subscribers": channel_data.participants_count,
        "description": channel_data.about
    }
```

### Step 3: Import the Decorator
At the top of your connector file:
```python
from .tool_registry import expose_tool
```

### Step 4: Test It
Your tool is now discoverable! Users can:
- See it in tool lists
- Get help about it
- Execute it in interactive mode

---

## 📊 Parameter Types & Validation

### Common Parameter Types

| Type | Python Type | Description | Example |
|------|-------------|-------------|---------|
| `"str"` | string | Text input | `"hello"` |
| `"int"` | integer | Whole numbers | `42` |
| `"float"` | float | Decimal numbers | `3.14` |
| `"bool"` | boolean | True/False | `True` |
| `"list"` | list | Array of items | `[1, 2, 3]` |
| `"list[str]"` | list of strings | Array of text | `["a", "b"]` |
| `"dict"` | dictionary | Key-value pairs | `{"key": "value"}` |

### 📝 Parameter Definition Template
```python
"parameter_name": {
    "type": "str",                    # Required: What type of data
    "description": "What this does",  # Required: Human explanation  
    "required": True,                 # Required: Must be provided?
    "default": "default_value"        # Optional: Default if not provided
}
```

### 🔍 Real Examples

#### Simple String Parameter
```python
"channel": {
    "type": "str",
    "description": "Telegram channel username",
    "required": True
}
```

#### Optional Integer with Default
```python
"limit": {
    "type": "int", 
    "description": "Maximum number of posts to fetch",
    "required": False,
    "default": 50
}
```

#### List of Strings
```python
"keywords": {
    "type": "list[str]",
    "description": "Keywords to search for in posts", 
    "required": True
}
```

#### Boolean Flag
```python
"include_media": {
    "type": "bool",
    "description": "Whether to include media URLs in results",
    "required": False, 
    "default": True
}
```

---

## ✅ Best Practices

### 1. **Method Naming**
```python
# ✅ Good: Clear, descriptive, follows convention
@expose_tool(name="fetch_recent_posts", ...)
@expose_tool(name="search_messages", ...)
@expose_tool(name="get_user_profile", ...)

# ❌ Bad: Vague or inconsistent
@expose_tool(name="fetch", ...)
@expose_tool(name="getStuff", ...)
@expose_tool(name="do_thing", ...)
```

### 2. **Error Handling**
Always handle errors gracefully:
```python
@expose_tool(...)
async def my_tool(self, channel: str) -> List[Dict]:
    try:
        # Your main logic
        result = await self.fetch_data(channel)
        return result
    except Exception as e:
        self.logger.error(f"Tool failed: {e}")
        return []  # Return empty list, not None
```

### 3. **Logging**
Add helpful log messages:
```python
@expose_tool(...)
async def my_tool(self, channel: str, limit: int) -> List[Dict]:
    self.logger.info(f"🔍 Fetching {limit} posts from {channel}")
    
    result = await self.fetch_posts(channel, limit)
    
    self.logger.info(f"✅ Retrieved {len(result)} posts from {channel}")
    return result
```

### 4. **Input Validation**
Validate inputs early:
```python
@expose_tool(...)
async def my_tool(self, limit: int) -> List[Dict]:
    if limit <= 0 or limit > 1000:
        self.logger.error("Limit must be between 1 and 1000")
        return []
    
    # Continue with valid input
    return await self.fetch_posts(limit)
```

### 5. **Consistent Return Types**
Always return the same type:
```python
# ✅ Good: Always returns List[Dict]
@expose_tool(...)
async def my_tool(self, channel: str) -> List[Dict[str, Any]]:
    if not channel:
        return []  # Empty list, not None
    
    result = await self.fetch_posts(channel)
    return result if result else []  # Always a list

# ❌ Bad: Sometimes returns different types
async def bad_tool(self, channel: str):
    if not channel:
        return None  # Wrong!
    
    result = await self.fetch_posts(channel)
    if not result:
        return "No posts found"  # Wrong type!
    
    return result
```

---

## 🚫 Common Mistakes to Avoid

### 1. **Wrong Decorator Placement**
```python
# ❌ Wrong: Decorator too far from method
@expose_tool(...)

# Some other code here

async def my_method(self):
    pass

# ✅ Correct: Decorator immediately above method
@expose_tool(...)
async def my_method(self):
    pass
```

### 2. **Missing Import**
```python
# ❌ Wrong: Forgot to import
class MyConnector(BaseConnector):
    @expose_tool(...)  # NameError: 'expose_tool' not defined
    async def my_method(self):
        pass

# ✅ Correct: Import at top of file
from .tool_registry import expose_tool

class MyConnector(BaseConnector):
    @expose_tool(...)
    async def my_method(self):
        pass
```

### 3. **Parameter Mismatch**
```python
# ❌ Wrong: Parameters don't match method signature
@expose_tool(
    parameters={
        "channel": {"type": "str", "required": True},
        "limit": {"type": "int", "required": True}
    }
)
async def my_method(self, different_name: str):  # Wrong parameter name!
    pass

# ✅ Correct: Parameters match exactly
@expose_tool(
    parameters={
        "channel": {"type": "str", "required": True}
    }
)
async def my_method(self, channel: str):
    pass
```

### 4. **Missing Required Fields**
```python
# ❌ Wrong: Missing required fields
@expose_tool(
    name="my_tool"
    # Missing description, parameters, category!
)

# ✅ Correct: All required fields present
@expose_tool(
    name="my_tool",
    description="What this tool does",
    parameters={},
    category="my_platform"
)
```

---

## 🧪 Testing Your Tools

### 1. **Check Discovery**
Make sure your tool is found:
```python
# In your test or interactive mode
from connectors.tool_registry import discover_tools

connector = MyConnector()
tools = discover_tools(connector)
print(f"Found {len(tools)} tools")
for tool in tools:
    print(f"- {tool.name}: {tool.description}")
```

### 2. **Test Parameter Validation**
```python
from connectors.tool_registry import validate_tool_parameters

# Test with correct parameters
result = validate_tool_parameters(tool_metadata, {"channel": "test", "limit": 10})
assert result["valid"] == True

# Test with missing required parameter
result = validate_tool_parameters(tool_metadata, {"channel": "test"})  # Missing limit
assert result["valid"] == False
assert "Missing required parameter: limit" in result["errors"]
```

### 3. **Test Tool Execution**
```python
# Test the actual tool method
connector = MyConnector()
await connector.setup_connector()
await connector.connect()

result = await connector.my_tool("test_channel", 5)
assert isinstance(result, list)  # Check return type
assert len(result) <= 5          # Check limit respected
```

---

## 🎓 Quick Reference Checklist

Before submitting your tool, check:

- [ ] ✅ Imported `expose_tool` from `.tool_registry`
- [ ] ✅ Decorator has all required fields (name, description, parameters, category)
- [ ] ✅ Parameter names match method signature exactly  
- [ ] ✅ Parameter types are correct ("str", "int", etc.)
- [ ] ✅ Method returns consistent type (usually `List[Dict[str, Any]]`)
- [ ] ✅ Added error handling with try/catch
- [ ] ✅ Added logging for important operations
- [ ] ✅ Tested the tool works in isolation
- [ ] ✅ Added examples showing real usage
- [ ] ✅ Method name uses snake_case
- [ ] ✅ Description starts with a verb and is clear

---

## 🎯 Summary

**Connector Tools** make your methods discoverable and usable in interactive mode. The key steps are:

1. **Import** the `expose_tool` decorator
2. **Add** the decorator with all required information  
3. **Match** parameter definitions to your method signature
4. **Test** that everything works

Following this guide will ensure your tools are professional, discoverable, and easy for users to understand and use! 🚀

---

*Need help? Check the existing tools in `telegram_connector.py` for working examples!*