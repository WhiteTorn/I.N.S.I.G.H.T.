# I.N.S.I.G.H.T. Mark II v2.4 - Unified JSON Output Schema

## Overview

This document defines the standardized JSON format that Mark II "The Inquisitor" produces for consumption by Mark III "The Scribe" and ultimately Mark IV "The Vision". This format serves as the universal data exchange protocol for the entire I.N.S.I.G.H.T. ecosystem.

## File Structure

### Top-Level Schema

```json
{
  "report_metadata": { ... },
  "validation_report": { ... },
  "posts": [ ... ]
}
```

### Report Metadata Object

Contains metadata about the entire intelligence report:

```json
{
  "report_metadata": {
    "generated_by": "I.N.S.I.G.H.T. Mark II v2.4",
    "generated_at": "2024-01-15T14:30:45Z",
    "total_posts": 150,
    "platforms_included": ["telegram", "rss"],
    "date_range": {
      "earliest": "2024-01-15T08:00:00Z",
      "latest": "2024-01-15T14:30:00Z"
    },
    "total_media_items": 25,
    "format_version": "2.4.0",
    "compatible_with": ["Mark III v3.0+", "Mark IV v4.0+"]
  }
}
```

### Validation Report Object

Provides quality assurance information for Mark III processing:

```json
{
  "validation_report": {
    "status": "valid",
    "total_posts": 150,
    "issues": [],
    "warnings": ["Post telegram_123: Content length exceeds 4000 characters"],
    "metadata": {
      "platforms_included": ["telegram", "rss"],
      "date_range": {
        "earliest": "2024-01-15T08:00:00Z",
        "latest": "2024-01-15T14:30:00Z"
      },
      "total_media_items": 25
    }
  }
}
```

### Posts Array

The core intelligence data in unified format:

## Unified Post Schema

Each post in the `posts` array follows this standardized schema:

### Core Fields (Required)

These fields are guaranteed to be present in every post, regardless of source platform:

```json
{
  "source_platform": "telegram",
  "source_id": "@example_channel",
  "post_id": "12345",
  "author": "example_channel",
  "content": "Breaking: Major development in...",
  "timestamp": "2024-01-15T14:30:45Z",
  "media_urls": ["https://t.me/example_channel/12345?single"],
  "post_url": "https://t.me/example_channel/12345"
}
```

### Processing Metadata (Mark II v2.4+)

Added by Mark II for enhanced Mark III/IV processing:

```json
{
  "processing_metadata": {
    "processed_by": "I.N.S.I.G.H.T. Mark II v2.4",
    "processed_at": "2024-01-15T14:30:45Z",
    "data_version": "2.4.0",
    "content_length": 256,
    "has_media": true,
    "media_count": 1
  }
}
```

### Content Analysis Hints (Mark IV Optimization)

Pre-computed analysis hints for LLM processing:

```json
{
  "content_analysis_hints": {
    "estimated_reading_time_seconds": 60,
    "contains_urls": true,
    "contains_mentions": false,
    "contains_hashtags": true,
    "language_hint": "en",
    "content_type": "news_article"
  }
}
```

### Platform-Specific Fields

#### Telegram Posts

Additional fields for Telegram-sourced content:

```json
{
  "channel": "example_channel",
  "id": 12345,
  "date": "2024-01-15T14:30:45Z",
  "text": "Breaking: Major development in...",
  "link": "https://t.me/example_channel/12345"
}
```

#### RSS/Atom Posts

Additional fields for RSS/Atom-sourced content:

```json
{
  "title": "Breaking News: Major Development",
  "feed_title": "Example News RSS",
  "feed_type": "rss",
  "categories": ["politics", "breaking-news"],
  "content_html": "<p>Breaking: Major development in...</p>",
  "id": "https://example.com/news/article-123",
  "date": "2024-01-15T14:30:45Z",
  "text": "Breaking: Major development in...",
  "link": "https://example.com/news/article-123"
}
```

## Content Type Classifications

The `content_type` field helps Mark IV optimize processing:

- `news_article`: RSS feeds with categories (structured news)
- `feed_content`: General RSS/Atom content
- `media_post`: Telegram posts with media attachments
- `long_form_message`: Telegram posts > 500 characters
- `short_message`: Brief Telegram posts
- `unknown`: Unable to classify

## Complete Example

### Telegram Post
```json
{
  "source_platform": "telegram",
  "source_id": "@geopolitics_intel",
  "post_id": "1337",
  "author": "geopolitics_intel",
  "content": "🚨 BREAKING: NATO forces conducting exercises near eastern border. Full details in thread. #NATO #Security",
  "timestamp": "2024-01-15T14:30:45Z",
  "media_urls": ["https://t.me/geopolitics_intel/1337?single"],
  "post_url": "https://t.me/geopolitics_intel/1337",
  "processing_metadata": {
    "processed_by": "I.N.S.I.G.H.T. Mark II v2.4",
    "processed_at": "2024-01-15T14:31:00Z",
    "data_version": "2.4.0",
    "content_length": 108,
    "has_media": true,
    "media_count": 1
  },
  "content_analysis_hints": {
    "estimated_reading_time_seconds": 15,
    "contains_urls": false,
    "contains_mentions": false,
    "contains_hashtags": true,
    "language_hint": "en",
    "content_type": "short_message"
  },
  "channel": "geopolitics_intel",
  "id": 1337,
  "date": "2024-01-15T14:30:45Z",
  "text": "🚨 BREAKING: NATO forces conducting exercises near eastern border. Full details in thread. #NATO #Security",
  "link": "https://t.me/geopolitics_intel/1337"
}
```

### RSS Post
```json
{
  "source_platform": "rss",
  "source_id": "https://example-news.com/rss",
  "post_id": "https://example-news.com/article/nato-exercises-2024",
  "author": "Example News",
  "content": "NATO announced large-scale military exercises scheduled for next month near the eastern border...",
  "timestamp": "2024-01-15T14:25:00Z",
  "media_urls": [],
  "post_url": "https://example-news.com/article/nato-exercises-2024",
  "processing_metadata": {
    "processed_by": "I.N.S.I.G.H.T. Mark II v2.4",
    "processed_at": "2024-01-15T14:31:00Z",
    "data_version": "2.4.0",
    "content_length": 342,
    "has_media": false,
    "media_count": 0
  },
  "content_analysis_hints": {
    "estimated_reading_time_seconds": 85,
    "contains_urls": false,
    "contains_mentions": false,
    "contains_hashtags": false,
    "language_hint": "en",
    "content_type": "news_article"
  },
  "title": "NATO Announces Eastern Border Exercises",
  "feed_title": "Example News RSS",
  "feed_type": "rss",
  "categories": ["military", "nato", "europe"],
  "content_html": "<p>NATO announced large-scale military exercises...</p>",
  "id": "https://example-news.com/article/nato-exercises-2024",
  "date": "2024-01-15T14:25:00Z",
  "text": "NATO announced large-scale military exercises scheduled for next month near the eastern border...",
  "link": "https://example-news.com/article/nato-exercises-2024"
}
```

## Mark III Integration Guidelines

### Database Schema Design

When Mark III processes these JSON files, it should:

1. **Store Core Fields**: Always store the unified core fields in the main posts table
2. **Handle Platform-Specific Data**: Store platform-specific fields in separate tables or JSON columns
3. **Index Key Fields**: Create indexes on `timestamp`, `source_platform`, and `content_type` for fast queries
4. **Preserve Metadata**: Store processing metadata for debugging and audit trails

### Recommended Database Structure

```sql
-- Core posts table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    source_platform VARCHAR(50) NOT NULL,
    source_id VARCHAR(500) NOT NULL,
    post_id VARCHAR(500) NOT NULL,
    author VARCHAR(200),
    content TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    post_url VARCHAR(1000),
    content_type VARCHAR(50),
    processing_metadata JSONB,
    platform_specific_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes for common queries
    INDEX idx_posts_timestamp (timestamp),
    INDEX idx_posts_platform (source_platform),
    INDEX idx_posts_content_type (content_type),
    
    -- Unique constraint to prevent duplicates
    UNIQUE(source_platform, source_id, post_id)
);

-- Media URLs table (for efficient querying)
CREATE TABLE post_media (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id),
    media_url VARCHAR(1000) NOT NULL,
    media_order INTEGER DEFAULT 0
);
```

## Mark IV LLM Integration

### Optimized Data Retrieval

Mark IV should leverage the standardized format for efficient LLM processing:

```python
# Example query for Mark IV context building
def build_llm_context(topic_keywords, hours_back=24):
    posts = query_posts_by_timeframe_and_content(
        keywords=topic_keywords,
        hours_back=hours_back,
        content_types=['news_article', 'long_form_message']
    )
    
    # Use content_analysis_hints for context optimization
    context = []
    for post in posts:
        hints = post.get('content_analysis_hints', {})
        if hints.get('estimated_reading_time_seconds', 0) < 120:  # Under 2 minutes
            context.append({
                'source': f"{post['source_platform']}:{post['author']}",
                'content': post['content'],
                'timestamp': post['timestamp'],
                'type': hints.get('content_type', 'unknown')
            })
    
    return context
```

### Content Type Processing

Different content types should be processed differently by Mark IV:

- **news_article**: Full analysis with entity extraction
- **media_post**: Focus on visual content description and context
- **short_message**: Rapid sentiment and keyword extraction
- **long_form_message**: Detailed content analysis and summarization

## Validation Rules

Mark III should validate incoming JSON files against these rules:

### Required Field Validation
- All core fields must be present and non-null
- `timestamp` must be valid ISO 8601 format
- `media_urls` must be a valid array (can be empty)
- `content` must be a non-empty string

### Data Quality Checks
- Check for duplicate posts using `(source_platform, source_id, post_id)` combination
- Validate URLs in `post_url` and `media_urls` fields
- Ensure `timestamp` is within reasonable bounds (not future, not too old)

### Error Handling
- Log validation errors with specific post identifiers
- Continue processing valid posts even if some posts fail validation
- Generate validation reports for debugging

## Version Compatibility

This format is designed to be backward and forward compatible:

- **Backward Compatibility**: Mark III v3.0+ can read this format
- **Forward Compatibility**: Additional fields can be added without breaking existing consumers
- **Version Detection**: Use `format_version` field to handle schema evolution

## File Naming Convention

JSON files should follow this naming pattern:
- Single source scans: `{mission_type}_{source_identifier}_{timestamp}.json`
- Multi-source briefings: `{mission_type}_{date}.json`
- Test files: `mark_iii_compatibility_test.json`

Examples:
- `deep_scan_geopolitics_intel_20240115_143045.json`
- `briefing_20240115.json`
- `rss_scan_example_news_20240115_143045.json` 