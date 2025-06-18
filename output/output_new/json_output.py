"""
I.N.S.I.G.H.T. JSON Output Handler

This module handles JSON file output for the I.N.S.I.G.H.T. platform.
It provides structured, standardized JSON export capabilities for all platform data
with enhanced metadata and validation for Mark III compatibility.

Features:
- Unified JSON schema across all platforms
- Rich metadata enrichment
- Data validation and error reporting
- Mark III/IV compatibility layer
- Custom serialization for complex types
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional


class JSONOutput:
    """
    JSON output handler for I.N.S.I.G.H.T. intelligence data.
    
    Provides structured JSON export with enhanced metadata, validation,
    and compatibility layers for downstream processing systems.
    """
    
    def __init__(self):
        """Initialize JSON output handler with default configuration."""
        self.json_config = {
            'ensure_ascii': False,
            'indent': 4,
            'sort_keys': True,
            'default': self._json_serializer
        }
    
    def _json_serializer(self, obj: Any) -> str:
        """
        Custom JSON serializer for handling datetime objects and other non-serializable types.
        
        Args:
            obj: Object to serialize
            
        Returns:
            Serialized string representation
            
        Raises:
            TypeError: If object type is not supported
        """
        if isinstance(obj, datetime):
            return obj.isoformat() + 'Z'  # ISO format with UTC indicator
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _enrich_post_metadata(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a post with additional metadata for enhanced downstream processing.
        
        Args:
            post: Post dictionary to enrich
            
        Returns:
            Enhanced post dictionary with additional metadata
        """
        enriched_post = post.copy()
        
        # Add processing metadata
        enriched_post['processing_metadata'] = {
            'processed_by': 'I.N.S.I.G.H.T. Mark II v2.4 JSON Output Handler',
            'processed_at': datetime.utcnow().isoformat() + 'Z',
            'data_version': '2.4.0',
            'content_length': len(post.get('content', '')),
            'has_media': len(post.get('media_urls', [])) > 0,
            'media_count': len(post.get('media_urls', []))
        }
        
        # Add content analysis hints
        content = post.get('content', '')
        enriched_post['content_analysis_hints'] = {
            'estimated_reading_time_seconds': max(1, len(content.split()) * 0.25),  # ~250 WPM
            'contains_urls': 'http' in content.lower(),
            'contains_mentions': '@' in content,
            'contains_hashtags': '#' in content,
            'language_hint': 'en',  # Default, can be enhanced with detection
            'content_type': self._classify_content_type(post)
        }
        
        return enriched_post
    
    def _classify_content_type(self, post: Dict[str, Any]) -> str:
        """
        Classify the type of content for enhanced processing context.
        
        Args:
            post: Post dictionary to classify
            
        Returns:
            Content type classification string
        """
        source_platform = post.get('platform', '')
        content = post.get('content', '').lower()
        
        if source_platform == 'rss':
            if post.get('categories'):
                return 'news_article'
            return 'feed_content'
        elif source_platform == 'telegram':
            if len(post.get('media_urls', [])) > 0:
                return 'media_post'
            elif len(content) > 500:
                return 'long_form_message'
            else:
                return 'short_message'
        elif source_platform == 'youtube':
            return 'video_transcript'
        elif source_platform == 'reddit':
            if post.get('comment_count', 0) > 0:
                return 'discussion_thread'
            else:
                return 'reddit_post'
        
        return 'unknown'
    
    def _validate_json_payload(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate the JSON payload before export to ensure data integrity.
        
        Args:
            posts: List of posts to validate
            
        Returns:
            Validation report dictionary
        """
        validation_report = {
            'status': 'valid',
            'total_posts': len(posts),
            'issues': [],
            'warnings': [],
            'metadata': {
                'platforms_included': set(),
                'date_range': {'earliest': None, 'latest': None},
                'total_media_items': 0,
                'content_types': set()
            }
        }
        
        for i, post in enumerate(posts):
            post_id = post.get('url', f'post_{i}')
            
            # Check required fields for unified structure
            required_fields = ['platform', 'source', 'url', 'content', 'date', 'media_urls', 'categories', 'metadata']
            for field in required_fields:
                if field not in post or post[field] is None:
                    validation_report['issues'].append(f"Post {post_id}: Missing required field '{field}'")
            
            # Track metadata
            if 'platform' in post:
                validation_report['metadata']['platforms_included'].add(post['platform'])
            
            if 'date' in post and isinstance(post['date'], datetime):
                ts = post['date']
                if validation_report['metadata']['date_range']['earliest'] is None or ts < validation_report['metadata']['date_range']['earliest']:
                    validation_report['metadata']['date_range']['earliest'] = ts
                if validation_report['metadata']['date_range']['latest'] is None or ts > validation_report['metadata']['date_range']['latest']:
                    validation_report['metadata']['date_range']['latest'] = ts
            
            if 'media_urls' in post and isinstance(post['media_urls'], list):
                validation_report['metadata']['total_media_items'] += len(post['media_urls'])
            
            # Track content types
            if 'content_analysis_hints' in post and 'content_type' in post['content_analysis_hints']:
                validation_report['metadata']['content_types'].add(post['content_analysis_hints']['content_type'])
        
        # Convert sets to lists for JSON serialization
        validation_report['metadata']['platforms_included'] = list(validation_report['metadata']['platforms_included'])
        validation_report['metadata']['content_types'] = list(validation_report['metadata']['content_types'])
        
        if validation_report['issues']:
            validation_report['status'] = 'errors_found'
        elif validation_report['warnings']:
            validation_report['status'] = 'warnings_found'
        
        return validation_report
    
    def export_to_file(self, 
                      posts: List[Dict[str, Any]], 
                      filename: Optional[str] = None, 
                      include_metadata: bool = True,
                      mission_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Export posts to a standardized JSON file with comprehensive metadata.
        
        Args:
            posts: List of posts in unified format
            filename: Output filename (auto-generated if None)
            include_metadata: Whether to include enriched metadata
            mission_context: Additional context about the mission/operation
            
        Returns:
            The filename of the exported JSON file
            
        Raises:
            Exception: If file export fails
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"insight_export_{timestamp}.json"
        
        # Enrich posts with metadata if requested
        if include_metadata:
            enriched_posts = [self._enrich_post_metadata(post) for post in posts]
        else:
            enriched_posts = posts
        
        # Sort by timestamp for chronological processing
        enriched_posts.sort(key=lambda p: p.get('date', datetime.min), reverse=True)
        
        # Validate the payload
        validation_report = self._validate_json_payload(enriched_posts)
        
        # Create the complete JSON payload
        json_payload = {
            'export_metadata': {
                'generated_by': 'I.N.S.I.G.H.T. Mark II v2.4 JSON Output Handler',
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'total_posts': len(enriched_posts),
                'platforms_included': validation_report['metadata']['platforms_included'],
                'content_types_included': validation_report['metadata']['content_types'],
                'date_range': validation_report['metadata']['date_range'],
                'total_media_items': validation_report['metadata']['total_media_items'],
                'format_version': '2.4.0',
                'compatible_with': ['Mark III v3.0+', 'Mark IV v4.0+'],
                'mission_context': mission_context or {}
            },
            'validation_report': validation_report,
            'posts': enriched_posts
        }
        
        # Write to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_payload, f, **self.json_config)
            
            logging.info(f"Successfully exported {len(enriched_posts)} posts to {filename}")
            logging.info(f"JSON validation status: {validation_report['status']}")
            
            if validation_report['issues']:
                logging.warning(f"Validation found {len(validation_report['issues'])} issues")
                for issue in validation_report['issues']:
                    logging.warning(f"  - {issue}")
            
            return filename
            
        except Exception as e:
            logging.error(f"Failed to export JSON file {filename}: {e}")
            raise
    
    def export_simple(self, posts: List[Dict[str, Any]], filename: str) -> str:
        """
        Export posts to a simple JSON file without metadata enrichment.
        
        Args:
            posts: List of posts to export
            filename: Output filename
            
        Returns:
            The filename of the exported JSON file
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, **self.json_config)
            
            logging.info(f"Successfully exported {len(posts)} posts to {filename} (simple format)")
            return filename
            
        except Exception as e:
            logging.error(f"Failed to export simple JSON file {filename}: {e}")
            raise
    
    def create_mission_summary(self, posts: List[Dict[str, Any]], mission_name: str, sources: List[str]) -> Dict[str, Any]:
        """
        Create a mission summary for inclusion in JSON exports.
        
        Args:
            posts: List of posts collected
            mission_name: Name of the mission executed
            sources: List of sources accessed
            
        Returns:
            Mission summary dictionary
        """
        return {
            'mission_name': mission_name,
            'sources_accessed': sources,
            'posts_collected': len(posts),
            'platforms_used': list(set(post.get('platform', 'unknown') for post in posts)),
            'execution_timestamp': datetime.utcnow().isoformat() + 'Z',
            'success_rate': len(posts) / len(sources) if sources else 0,
            'data_quality': 'high' if len(posts) > 0 else 'no_data'
        } 