# I.N.S.I.G.H.T. Unified Structure Documentation

## Overview

The I.N.S.I.G.H.T. Mark II system implements a **unified data structure** across all platform connectors (Telegram, YouTube, Reddit, RSS/Atom). This structure was designed with **RSS-inspired simplicity** to ensure consistency, database readiness, and optimal LLM processing.

## The Unified Structure

Every post from any platform is normalized into this standardized format:

```python
{
    "platform": str,           # Platform identifier ("telegram", "youtube", "reddit", "rss")  
    "source": str,             # Source exactly as user enters (no normalization)
    "url": str,                # Direct link to original post (serves as unique ID)
    "content": str,            # Full text content
    "date": datetime,          # Precise UTC timestamp
    "media_urls": List[str],   # List of media URLs
    "categories": List[str],   # Tags/topics/hashtags (empty list if none)
    "metadata": Dict[str, Any] # Platform-specific data (empty dict for Mark II)
}
```

## Design Principles

### 1. **RSS-Inspired Simplicity**
Like RSS feeds, our structure focuses on the essential elements needed to render and process content uniformly across platforms.

### 2. **Exact User Input Preservation**
The `source` field stores exactly what the user enters:
- Telegram: `@channel_name` or `channel_name`
- YouTube: Full channel URL or video URL
- Reddit: Subreddit name or post URL
- RSS: Complete feed URL

### 3. **URL as Universal ID**
Instead of platform-specific IDs, we use the `url` field as a unique identifier:
- **Telegram**: `https://t.me/channel_name/message_id`
- **YouTube**: `https://www.youtube.com/watch?v=video_id`
- **Reddit**: `https://reddit.com/r/subreddit/comments/post_id/`
- **RSS**: Direct link from feed entry

### 4. **Future-Ready Architecture**
- **Categories**: Ready for content classification and filtering
- **Metadata**: Extensible for platform-specific features

## Field Specifications

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `platform` | `str` | Platform identifier | `"telegram"`, `"rss"`, `"youtube"`, `"reddit"` |
| `source` | `str` | User input exactly as entered | `"@technews"`, `"https://feeds.example.com/rss"` |
| `url` | `str` | Canonical link to original content | `"https://t.me/technews/1234"` |
| `content` | `str` | Full text content | `"Breaking: New AI model released..."` |
| `date` | `datetime` | UTC timestamp of publication | `datetime(2025, 6, 18, 12, 30, 40, tzinfo=timezone.utc)` |
| `media_urls` | `List[str]` | Media attachments | `["https://example.com/image.jpg"]` |
| `categories` | `List[str]` | Content tags/topics | `["ai", "technology", "news"]` |
| `metadata` | `Dict[str, Any]` | Platform-specific data | `{}` (empty for Mark II) |

### Field Details

#### `platform`
- **Purpose**: Identifies the source platform
- **Values**: `"telegram"`, `"youtube"`, `"reddit"`, `"rss"`
- **Usage**: Routing, analytics, platform-specific rendering

#### `source`
- **Purpose**: Preserves exact user input for authenticity
- **Format**: No normalization applied
- **Examples**:
  - `"@elonmusk"` (Telegram)
  - `"https://simonwillison.net/atom/everything"` (RSS)
  - `"r/programming"` (Reddit)

#### `url`
- **Purpose**: Unique identifier and direct link
- **Requirements**: Must be accessible URL
- **Fallback**: Generated URL if original unavailable

#### `content`
- **Purpose**: Main text content
- **Format**: Plain text (HTML stripped for Telegram/Reddit)
- **Limits**: No artificial truncation

#### `date`
- **Purpose**: Precise timestamp for chronological sorting
- **Format**: Python `datetime` object with UTC timezone
- **Source**: Original publication time from platform

#### `media_urls`
- **Purpose**: Associated media files
- **Format**: List of direct URLs
- **Types**: Images, videos, audio, documents
- **Empty**: `[]` if no media

#### `categories`
- **Purpose**: Content classification and filtering
- **Sources**:
  - **RSS**: Native category/tag fields
  - **Reddit**: Post flair, subreddit topics
  - **YouTube**: Video tags (when available)
  - **Telegram**: Extracted hashtags (future enhancement)
- **Empty**: `[]` if no categories available

#### `metadata`
- **Purpose**: Platform-specific additional data
- **Current**: Empty `{}` for Mark II simplicity
- **Future**: Platform-specific fields (view counts, engagement metrics, etc.)

## Platform-Specific Implementation

### Telegram Connector
```python
{
    "platform": "telegram",
    "source": "@channel_name",  # Exactly as user enters
    "url": "https://t.me/channel_name/message_id",
    "content": "Message text content...",
    "date": datetime(2025, 6, 18, 12, 30, 40, tzinfo=timezone.utc),
    "media_urls": ["https://cdn.telegram.org/file/image.jpg"],
    "categories": [],  # Empty for now, hashtag extraction planned
    "metadata": {}
}
```

### RSS/Atom Connector
```python
{
    "platform": "rss",
    "source": "https://simonwillison.net/atom/everything",
    "url": "https://simonwillison.net/2025/Jun/18/post-title/",
    "content": "Blog post content...",
    "date": datetime(2025, 6, 18, 4, 30, 40, tzinfo=timezone.utc),
    "media_urls": [],
    "categories": ["ai", "technology", "programming"],  # From RSS categories
    "metadata": {}
}
```

### YouTube Connector
```python
{
    "platform": "youtube",
    "source": "https://www.youtube.com/@channel",  # User input preserved
    "url": "https://www.youtube.com/watch?v=video_id",
    "content": "Video transcript content...",
    "date": datetime(2025, 6, 18, 10, 15, 30, tzinfo=timezone.utc),
    "media_urls": ["https://img.youtube.com/vi/video_id/maxresdefault.jpg"],
    "categories": ["technology", "tutorial"],  # From video tags
    "metadata": {}
}
```

### Reddit Connector
```python
{
    "platform": "reddit",
    "source": "r/programming",
    "url": "https://reddit.com/r/programming/comments/abc123/post_title/",
    "content": "Post content and top comments...",
    "date": datetime(2025, 6, 18, 8, 45, 20, tzinfo=timezone.utc),
    "media_urls": ["https://i.redd.it/image.jpg"],
    "categories": ["Discussion"],  # From post flair
    "metadata": {}
}
```

## Benefits

### 1. **Database Storage**
- **Consistent Schema**: Same table structure for all platforms
- **Easy Indexing**: Standard fields for efficient queries
- **Scalable**: Simple structure supports millions of posts

### 2. **LLM Processing**
- **Unified Prompts**: Same prompt templates work across platforms
- **Context Clarity**: Clear separation of content vs metadata
- **Category-Aware**: Built-in topic classification for smarter processing

### 3. **Cross-Platform Analytics**
- **Unified Metrics**: Compare engagement across platforms
- **Content Analysis**: Analyze trends across all sources
- **Source Tracking**: Maintain authentic source attribution

### 4. **Future Extensibility**
- **Categories**: Ready for ML-based classification
- **Metadata**: Platform-specific features without breaking structure
- **New Platforms**: Easy to add with same structure

## Migration from Legacy Structure

### Old Structure (Deprecated)
```python
{
    "source_platform": "telegram",
    "source_id": "@channel",
    "post_id": "12345",
    "author": "Channel Name",
    "content": "...",
    "timestamp": datetime,
    "media_urls": [...],
    # Various platform-specific fields
}
```

### New Structure (Current)
```python
{
    "platform": "telegram",
    "source": "@channel",
    "url": "https://t.me/channel/12345",
    "content": "...",
    "date": datetime,
    "media_urls": [...],
    "categories": [],
    "metadata": {}
}
```

### Key Changes
1. **`source_platform` → `platform`**: Shorter, clearer
2. **`source_id` → `source`**: Preserves exact user input
3. **`post_id` removed**: URL serves as unique identifier
4. **`author` removed**: Simplified for RSS-style uniformity
5. **`timestamp` → `date`**: More intuitive naming
6. **Added `categories`**: Future-ready classification
7. **Added `metadata`**: Extensible platform-specific data

## Validation

The system validates all posts against this structure:

```python
def validate_post(post):
    required_fields = [
        'platform', 'source', 'url', 'content', 
        'date', 'media_urls', 'categories', 'metadata'
    ]
    
    # Check required fields exist
    for field in required_fields:
        if field not in post or post[field] is None:
            return False
    
    # Validate types
    if not isinstance(post['media_urls'], list):
        return False
    if not isinstance(post['categories'], list):
        return False
    if not isinstance(post['metadata'], dict):
        return False
        
    return True
```

## Best Practices

### For Developers

1. **Always Use Helper Method**: Use `_create_unified_post()` from base connector
2. **Preserve User Input**: Never modify the `source` field
3. **Handle Missing Data**: Provide empty list/dict for optional fields
4. **UTC Timestamps**: Always use UTC timezone for `date` field

### For Data Processing

1. **Use URL for Deduplication**: URL field is the unique identifier
2. **Category Filtering**: Leverage categories for content filtering
3. **Platform-Specific Logic**: Check `platform` field for special handling
4. **Date Sorting**: Use `date` field for chronological operations

## Examples

### RSS Feed Processing
```python
# Fetching from RSS feed
posts = rss_connector.fetch_posts("https://feeds.example.com/rss", 10)

# All posts follow unified structure
for post in posts:
    print(f"Platform: {post['platform']}")
    print(f"Source: {post['source']}")
    print(f"Title: Extract from {post['content']}")
    print(f"Categories: {', '.join(post['categories'])}")
    print(f"URL: {post['url']}")
```

### Cross-Platform Analysis
```python
# Combine posts from multiple platforms
all_posts = []
all_posts.extend(telegram_connector.fetch_posts("@news", 20))
all_posts.extend(rss_connector.fetch_posts("https://feeds.news.com/rss", 20))
all_posts.extend(reddit_connector.fetch_posts("r/worldnews", 20))

# Sort chronologically (works across all platforms)
all_posts.sort(key=lambda p: p['date'])

# Filter by categories (works across all platforms)
tech_posts = [p for p in all_posts if 'technology' in p['categories']]
```

## Future Enhancements

### Mark III Planned Features

1. **Enhanced Categories**:
   - ML-based automatic categorization
   - User-defined category mapping
   - Cross-platform category normalization

2. **Rich Metadata**:
   - Engagement metrics (views, likes, shares)
   - Author information (when available)
   - Content quality scores

3. **Advanced Validation**:
   - Content quality checks
   - Duplicate detection across platforms
   - Sentiment analysis integration

### Extension Points

The unified structure is designed for easy extension:

```python
# Future metadata examples
"metadata": {
    "engagement": {
        "views": 10000,
        "likes": 500,
        "shares": 50
    },
    "quality_score": 0.85,
    "sentiment": "positive",
    "language": "en"
}
```

## Conclusion

The I.N.S.I.G.H.T. unified structure provides a solid foundation for multi-platform content processing. Its RSS-inspired simplicity ensures consistency while remaining extensible for future enhancements. The structure successfully balances simplicity with functionality, making it ideal for database storage, LLM processing, and cross-platform analytics.

---

*Last Updated: June 18, 2025*  
*I.N.S.I.G.H.T. Mark II v2.4 - The Inquisitor - Citadel Edition* 