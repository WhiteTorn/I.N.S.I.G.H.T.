#!/usr/bin/env python3
"""
I.N.S.I.G.H.T. Mark III Preview - Database Integration Demo

This script demonstrates how Mark III "The Scribe" will process the standardized
JSON files produced by Mark II "The Inquisitor". It showcases the clean separation
of concerns and data pipeline architecture.

This is NOT the actual Mark III implementation, but a preview of how the
JSON consumption will work in the full Mark III system.
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

class MarkIIIPreview:
    """
    Preview implementation of Mark III "The Scribe" capabilities.
    
    Demonstrates:
    - JSON file processing
    - Database schema mapping
    - Data validation and cleaning
    - Duplicate detection
    - Metadata preservation
    """
    
    def __init__(self, db_path: str = "insight_preview.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize database schema
        self._initialize_database()
        
    def _initialize_database(self):
        """Create the database schema for Mark III preview."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Core posts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_platform TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    post_id TEXT NOT NULL,
                    author TEXT,
                    content TEXT,
                    timestamp DATETIME NOT NULL,
                    post_url TEXT,
                    content_type TEXT,
                    processing_metadata TEXT,
                    platform_specific_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    
                    UNIQUE(source_platform, source_id, post_id)
                )
            """)
            
            # Media URLs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS post_media (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER,
                    media_url TEXT NOT NULL,
                    media_order INTEGER DEFAULT 0,
                    FOREIGN KEY (post_id) REFERENCES posts (id)
                )
            """)
            
            # Processing logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_posts INTEGER,
                    successful_inserts INTEGER,
                    duplicates_skipped INTEGER,
                    errors INTEGER,
                    validation_status TEXT,
                    processing_notes TEXT
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_timestamp ON posts(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(source_platform)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_content_type ON posts(content_type)")
            
            conn.commit()
            
        self.logger.info(f"Mark III Preview database initialized: {self.db_path}")
    
    def process_json_file(self, json_file_path: str) -> Dict[str, Any]:
        """
        Process a JSON file produced by Mark II Inquisitor.
        
        This demonstrates the core Mark III functionality of consuming
        standardized JSON payloads and storing them in the database.
        
        Args:
            json_file_path: Path to the JSON file
            
        Returns:
            Processing report with statistics and any issues
        """
        processing_report = {
            'filename': Path(json_file_path).name,
            'status': 'success',
            'total_posts': 0,
            'successful_inserts': 0,
            'duplicates_skipped': 0,
            'errors': 0,
            'validation_issues': [],
            'processing_notes': []
        }
        
        try:
            # Load and validate JSON file
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate file structure
            if not self._validate_json_structure(data):
                processing_report['status'] = 'error'
                processing_report['validation_issues'].append('Invalid JSON structure')
                return processing_report
            
            # Extract posts and metadata
            posts = data.get('posts', [])
            report_metadata = data.get('report_metadata', {})
            validation_report = data.get('validation_report', {})
            
            processing_report['total_posts'] = len(posts)
            
            # Log the source file information
            format_version = report_metadata.get('format_version', 'unknown')
            generated_by = report_metadata.get('generated_by', 'unknown')
            self.logger.info(f"Processing {len(posts)} posts from {generated_by} (format v{format_version})")
            
            # Process each post
            with sqlite3.connect(self.db_path) as conn:
                for post in posts:
                    try:
                        if self._insert_post(conn, post):
                            processing_report['successful_inserts'] += 1
                        else:
                            processing_report['duplicates_skipped'] += 1
                            
                    except Exception as e:
                        processing_report['errors'] += 1
                        processing_report['validation_issues'].append(f"Error processing post {post.get('post_id', 'unknown')}: {str(e)}")
                        self.logger.error(f"Error processing post: {e}")
                
                conn.commit()
            
            # Log processing summary
            self._log_processing_result(processing_report, validation_report)
            
            self.logger.info(f"Processing complete: {processing_report['successful_inserts']} inserted, "
                           f"{processing_report['duplicates_skipped']} duplicates skipped, "
                           f"{processing_report['errors']} errors")
            
        except Exception as e:
            processing_report['status'] = 'error'
            processing_report['validation_issues'].append(f"File processing error: {str(e)}")
            self.logger.error(f"Failed to process JSON file {json_file_path}: {e}")
        
        return processing_report
    
    def _validate_json_structure(self, data: Dict[str, Any]) -> bool:
        """Validate that the JSON file has the expected Mark II v2.4 structure."""
        required_keys = ['report_metadata', 'validation_report', 'posts']
        return all(key in data for key in required_keys)
    
    def _insert_post(self, conn: sqlite3.Connection, post: Dict[str, Any]) -> bool:
        """
        Insert a single post into the database.
        
        Returns True if inserted, False if duplicate (skipped).
        """
        cursor = conn.cursor()
        
        # Extract core fields
        source_platform = post.get('source_platform')
        source_id = post.get('source_id')
        post_id = post.get('post_id')
        
        # Check for duplicate
        cursor.execute("""
            SELECT id FROM posts 
            WHERE source_platform = ? AND source_id = ? AND post_id = ?
        """, (source_platform, source_id, post_id))
        
        if cursor.fetchone():
            return False  # Duplicate, skip
        
        # Parse timestamp
        timestamp_str = post.get('timestamp')
        if isinstance(timestamp_str, str):
            # Convert ISO format to datetime
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            timestamp = datetime.utcnow()
        
        # Prepare platform-specific data
        platform_data = {}
        processing_metadata = post.get('processing_metadata', {})
        
        # Store platform-specific fields
        if source_platform == 'telegram':
            platform_data = {
                'channel': post.get('channel'),
                'id': post.get('id'),
                'date': post.get('date'),
                'text': post.get('text'),
                'link': post.get('link')
            }
        elif source_platform == 'rss':
            platform_data = {
                'title': post.get('title'),
                'feed_title': post.get('feed_title'),
                'feed_type': post.get('feed_type'),
                'categories': post.get('categories', []),
                'content_html': post.get('content_html')
            }
        
        # Insert post
        cursor.execute("""
            INSERT INTO posts (
                source_platform, source_id, post_id, author, content,
                timestamp, post_url, content_type, processing_metadata,
                platform_specific_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source_platform,
            source_id,
            post_id,
            post.get('author'),
            post.get('content'),
            timestamp,
            post.get('post_url'),
            post.get('content_analysis_hints', {}).get('content_type'),
            json.dumps(processing_metadata),
            json.dumps(platform_data)
        ))
        
        # Get the inserted post ID
        new_post_id = cursor.lastrowid
        
        # Insert media URLs
        media_urls = post.get('media_urls', [])
        for order, media_url in enumerate(media_urls):
            cursor.execute("""
                INSERT INTO post_media (post_id, media_url, media_order)
                VALUES (?, ?, ?)
            """, (new_post_id, media_url, order))
        
        return True  # Successfully inserted
    
    def _log_processing_result(self, processing_report: Dict[str, Any], validation_report: Dict[str, Any]):
        """Log the processing result to the processing_logs table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processing_logs (
                    filename, total_posts, successful_inserts, duplicates_skipped,
                    errors, validation_status, processing_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                processing_report['filename'],
                processing_report['total_posts'],
                processing_report['successful_inserts'],
                processing_report['duplicates_skipped'],
                processing_report['errors'],
                validation_report.get('status', 'unknown'),
                json.dumps(processing_report['validation_issues'])
            ))
            conn.commit()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the current database state."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get total posts
            cursor.execute("SELECT COUNT(*) FROM posts")
            total_posts = cursor.fetchone()[0]
            
            # Get posts by platform
            cursor.execute("""
                SELECT source_platform, COUNT(*) 
                FROM posts 
                GROUP BY source_platform
            """)
            posts_by_platform = dict(cursor.fetchall())
            
            # Get recent processing activity
            cursor.execute("""
                SELECT COUNT(*) FROM processing_logs
                WHERE processed_at >= datetime('now', '-24 hours')
            """)
            recent_files_processed = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM posts")
            date_range = cursor.fetchone()
            
            return {
                'total_posts': total_posts,
                'posts_by_platform': posts_by_platform,
                'recent_files_processed': recent_files_processed,
                'date_range': {
                    'earliest': date_range[0],
                    'latest': date_range[1]
                }
            }
    
    def query_posts_for_llm(self, keywords: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """
        Query posts for Mark IV LLM processing.
        
        This demonstrates how Mark IV will retrieve data from Mark III.
        """
        with sqlite3.connect(self.db_path) as conn:
            # Build search query
            keyword_conditions = []
            params = []
            
            for keyword in keywords:
                keyword_conditions.append("content LIKE ?")
                params.append(f"%{keyword}%")
            
            where_clause = " OR ".join(keyword_conditions) if keyword_conditions else "1=1"
            
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT source_platform, source_id, author, content, timestamp, 
                       content_type, post_url, processing_metadata
                FROM posts 
                WHERE {where_clause}
                ORDER BY timestamp DESC 
                LIMIT ?
            """, params + [limit])
            
            results = []
            for row in cursor.fetchall():
                post_data = {
                    'source_platform': row[0],
                    'source_id': row[1],
                    'author': row[2],
                    'content': row[3],
                    'timestamp': row[4],
                    'content_type': row[5],
                    'post_url': row[6],
                    'processing_metadata': json.loads(row[7]) if row[7] else {}
                }
                results.append(post_data)
            
            return results


def demo_mark_iii_processing():
    """
    Demonstration of Mark III preview functionality.
    
    This shows how Mark III will process JSON files from Mark II.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize Mark III preview
    mark_iii = MarkIIIPreview("demo_insight.db")
    
    print("="*60)
    print("I.N.S.I.G.H.T. Mark III Preview - Database Integration Demo")
    print("="*60)
    
    # Look for JSON files to process
    json_files = list(Path(".").glob("*.json"))
    
    if not json_files:
        print("\n❌ No JSON files found in current directory.")
        print("Run Mark II first to generate some JSON files, then run this demo.")
        return
    
    print(f"\n📁 Found {len(json_files)} JSON file(s) to process:")
    for file in json_files:
        print(f"  • {file.name}")
    
    # Process each JSON file
    for json_file in json_files:
        print(f"\n🔄 Processing {json_file.name}...")
        result = mark_iii.process_json_file(str(json_file))
        
        if result['status'] == 'success':
            print(f"✅ Success: {result['successful_inserts']} posts inserted, "
                  f"{result['duplicates_skipped']} duplicates skipped")
        else:
            print(f"❌ Error processing file")
            for issue in result['validation_issues']:
                print(f"   - {issue}")
    
    # Show database statistics
    print("\n📊 Database Statistics:")
    stats = mark_iii.get_database_stats()
    print(f"  • Total posts: {stats['total_posts']}")
    print(f"  • Posts by platform: {stats['posts_by_platform']}")
    print(f"  • Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
    
    # Demonstrate Mark IV query capability
    print("\n🤖 Mark IV Query Demo (searching for 'news'):")
    llm_posts = mark_iii.query_posts_for_llm(['news'], limit=3)
    
    for i, post in enumerate(llm_posts, 1):
        print(f"\n  Post {i}:")
        print(f"    Platform: {post['source_platform']}")
        print(f"    Author: {post['author']}")
        print(f"    Content: {post['content'][:100]}...")
        print(f"    Type: {post['content_type']}")
    
    print("\n🎯 Mark III Preview Demo Complete!")
    print(f"Database saved to: demo_insight.db")
    print("\nThis demonstrates the clean data pipeline from Mark II → Mark III → Mark IV")


if __name__ == "__main__":
    demo_mark_iii_processing() 