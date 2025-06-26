import html
from datetime import datetime
import logging
import re

# Conditional import for the markdown library
try:
    import markdown
    # The presence of pymdown-extensions is implicitly required by the code now.
    # A requirements.txt file should list: markdown, pymdown-extensions
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    logging.warning("Libraries 'markdown' or 'pymdown-extensions' not available. Install with: pip install markdown pymdown-extensions")


class HTMLOutput:
    """
    A dedicated module for rendering I.N.S.I.G.H.T. reports and briefings
    into a clean, self-contained HTML file.
    
    v2.5 (Corrected): Relies exclusively on the standard `markdown` library and its extensions
    for all content conversion, removing legacy regex-based parsers to ensure
    robust and valid HTML generation.
    """

    def __init__(self, report_title="I.N.S.I.G.H.T. Report"):
        self.title = html.escape(report_title)
        self.body_content = ""
        
        if MARKDOWN_AVAILABLE:
            self.markdown_processor = markdown.Markdown(
                extensions=[
                    'pymdownx.magiclink',            # Auto-converts URLs to links correctly.
                    'markdown.extensions.fenced_code', # Support for ```code``` blocks.
                    'markdown.extensions.codehilite',  # Syntax highlighting for code.
                    'markdown.extensions.tables',      # Support for Markdown tables.
                    'markdown.extensions.sane_lists',  # Improved list parsing.
                ],
                extension_configs={
                    'codehilite': {'use_pygments': False}
                }
            )

    def _convert_markdown_to_html(self, text: str) -> str:
        """
        Convert markdown to HTML using the standard markdown library.
        If the library is not available, it safely escapes the text.
        """
        if not text:
            return ""
        
        if MARKDOWN_AVAILABLE:
            # Reset is good practice to avoid state carry-over between calls
            self.markdown_processor.reset()
            return self.markdown_processor.convert(text)
        else:
            # Fallback if markdown library isn't installed:
            # Safely escape the content and wrap in a paragraph tag.
            # The CSS 'white-space: pre-wrap' will handle line breaks.
            return f"<p>{html.escape(text)}</p>"

    def _get_html_template(self):
        """Returns the basic structure of the HTML document with embedded CSS."""
        # CSS now includes 'white-space: pre-wrap' to handle newlines correctly,
        # removing the need for the problematic 'nl2br' extension.
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            background-color: #121212;
            color: #e0e0e0;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 900px;
            margin: 20px auto;
            padding: 20px;
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 8px;
        }}
        header {{
            text-align: center;
            border-bottom: 2px solid #00aaff;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        header h1 {{
            color: #00aaff;
            margin: 0;
        }}
        .post-block {{
            background-color: #2a2a2a;
            border: 1px solid #444;
            border-left: 5px solid #00aaff;
            padding: 15px;
            margin-bottom: 25px;
            border-radius: 5px;
        }}
        .post-block.rss {{
            border-left: 5px solid #ff6b35;
        }}
        .post-block.atom {{
            border-left: 5px solid #ff9500;
        }}
        .post-header {{
            font-size: 0.9em;
            color: #aaa;
            margin-bottom: 10px;
            border-bottom: 1px solid #444;
            padding-bottom: 5px;
        }}
        .post-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 8px;
        }}
        .post-content p {{
            margin: 0 0 1em 0;
            white-space: pre-wrap; /* THIS IS CRITICAL: It preserves newlines without needing <br> tags. */
        }}
        .post-content a {{
            color: #00aaff;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s;
        }}
        .post-content a:hover {{
            border-bottom-color: #00aaff;
        }}
        .post-content strong {{
            color: #ffffff;
            font-weight: 600;
        }}
        .post-content em {{
            color: #ffcc00;
            font-style: italic;
        }}
        .post-content code {{
            background-color: #333;
            color: #ff6b6b;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
        }}
        .post-content del {{
            color: #888;
            text-decoration: line-through;
        }}
        .post-content h1, .post-content h2, .post-content h3 {{
            color: #00aaff;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }}
        .post-content h1 {{
            font-size: 1.4em;
            border-bottom: 2px solid #00aaff;
            padding-bottom: 5px;
        }}
        .post-content h2 {{
            font-size: 1.2em;
            border-bottom: 1px solid #555;
            padding-bottom: 3px;
        }}
        .post-content h3 {{
            font-size: 1.1em;
        }}
        .categories {{
            margin: 10px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }}
        .category-tag {{
            background-color: #444;
            color: #00aaff;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            border: 1px solid #555;
        }}
        .feed-type-badge {{
            display: inline-block;
            background-color: #333;
            color: #fff;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7em;
            text-transform: uppercase;
            margin-left: 5px;
        }}
        .feed-type-badge.rss {{
            background-color: #ff6b35;
        }}
        .feed-type-badge.atom {{
            background-color: #ff9500;
        }}
        .media-gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .media-item {{
            position: relative;
            background-color: #333;
            border-radius: 8px;
            overflow: hidden;
            border: 2px solid #555;
            transition: border-color 0.3s;
        }}
        .media-item:hover {{
            border-color: #00aaff;
        }}
        .media-item img {{
            width: 100%;
            height: auto;
            max-height: 400px;
            object-fit: cover;
            display: block;
        }}
        .media-item video {{
            width: 100%;
            height: auto;
            max-height: 400px;
            display: block;
        }}
        .media-item audio {{
            width: 100%;
            height: 60px;
            background-color: #2a2a2a;
        }}
        .media-overlay {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(transparent, rgba(0,0,0,0.8));
            padding: 10px;
            opacity: 0;
            transition: opacity 0.3s;
        }}
        .media-item:hover .media-overlay {{
            opacity: 1;
        }}
        .media-link {{
            color: #00aaff;
            text-decoration: none;
            font-size: 0.9em;
            display: inline-block;
        }}
        .media-link:hover {{
            text-decoration: underline;
        }}
        .document-item {{
            padding: 20px;
            text-align: center;
            background-color: #2a2a2a;
        }}
        .document-preview {{
            margin-bottom: 15px;
        }}
        .document-icon {{
            font-size: 3em;
            margin-bottom: 10px;
        }}
        .document-name {{
            color: #e0e0e0;
            font-size: 0.9em;
            word-break: break-all;
            margin-bottom: 10px;
        }}
        .document-link {{
            background-color: #00aaff;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            text-decoration: none;
            display: inline-block;
            transition: background-color 0.3s;
        }}
        .document-link:hover {{
            background-color: #0088cc;
        }}
        .audio-item {{
            padding: 15px;
            background-color: #2a2a2a;
        }}
        .post-footer {{
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid #444;
        }}
        .post-footer a {{
            color: #00aaff;
            text-decoration: none;
        }}
        .post-footer a:hover {{
            text-decoration: underline;
        }}
        .channel-header, .date-header {{
            margin-top: 40px;
            color: #00aaff;
            border-bottom: 1px solid #555;
            padding-bottom: 5px;
        }}
        .source-info {{
            font-size: 0.9em;
            color: #999;
            margin-bottom: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header><h1>{self.title}</h1></header>
        <main>
            {self.body_content}
        </main>
    </div>
</body>
</html>
        """

    def _format_categories(self, categories: list) -> str:
        """Format categories as styled tags."""
        if not categories:
            return ""
        
        category_html = '<div class="categories">'
        for category in categories:
            category_html += f'<span class="category-tag">{html.escape(category)}</span>'
        category_html += '</div>'
        return category_html

    def _get_feed_type_badge(self, feed_type: str) -> str:
        """Generate a badge for the feed type."""
        if not feed_type or feed_type == "unknown":
            return ""
        return f'<span class="feed-type-badge {feed_type.lower()}">{feed_type.upper()}</span>'

    def _is_image_url(self, url: str) -> bool:
        """Check if URL points to an image file."""
        if not url:
            return False
        clean_url = url.split('?')[0].lower()
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.ico')
        return any(clean_url.endswith(ext) for ext in image_extensions)

    def _is_video_url(self, url: str) -> bool:
        """Check if URL points to a video file."""
        if not url:
            return False
        clean_url = url.split('?')[0].lower()
        video_extensions = ('.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv', '.m4v')
        return any(clean_url.endswith(ext) for ext in video_extensions)

    def _is_audio_url(self, url: str) -> bool:
        """Check if URL points to an audio file."""
        if not url:
            return False
        clean_url = url.split('?')[0].lower()
        audio_extensions = ('.mp3', '.wav', '.ogg', '.aac', '.flac', '.m4a')
        return any(clean_url.endswith(ext) for ext in audio_extensions)

    def _is_telegram_media_url(self, url: str) -> bool:
        """Check if URL is a Telegram media URL that should be treated as an image."""
        if not url:
            return False
        return 't.me/' in url and ('?single' in url or any(x in url for x in ['/photo/', '/video/']))

    def _create_media_html(self, url: str) -> str:
        """Create appropriate HTML for different media types."""
        if not url:
            return ""
            
        url_escaped = html.escape(url)
        
        if self._is_telegram_media_url(url):
            filename = url.split('/')[-1].split('?')[0]
            return f'''
            <div class="media-item document-item">
                <div class="document-preview">
                    <div class="document-icon">📄</div>
                    <div class="document-name">{html.escape(filename)}</div>
                </div>
                <a href="{url_escaped}" target="_blank" class="document-link">📥 Download / View</a>
            </div>
            '''
        elif self._is_image_url(url):
            return f'''
            <div class="media-item image-item">
                <img src="{url_escaped}" alt="Image Content" loading="lazy">
                <div class="media-overlay">
                    <a href="{url_escaped}" target="_blank" class="media-link">🔗 Open Full Size</a>
                </div>
            </div>
            '''
        elif self._is_video_url(url):
            return f'''
            <div class="media-item video-item">
                <video controls preload="metadata">
                    <source src="{url_escaped}">
                    Your browser does not support the video tag.
                </video>
            </div>
            '''
        elif self._is_audio_url(url):
            return f'''
            <div class="media-item audio-item">
                <audio controls preload="metadata">
                    <source src="{url_escaped}">
                    Your browser does not support the audio element.
                </audio>
            </div>
            '''
        else:
            filename = url.split('/')[-1].split('?')[0] if '/' in url else url
            return f'''
            <div class="media-item document-item">
                <div class="document-preview">
                    <div class="document-icon">📄</div>
                    <div class="document-name">{html.escape(filename)}</div>
                </div>
                <a href="{url_escaped}" target="_blank" class="document-link">📥 Download / View</a>
            </div>
            '''

    def _format_post(self, post_data: dict, show_channel=False):
        """Converts a single post dictionary into an HTML block."""
        media_count = len(post_data.get('media_urls', []))
        media_indicator = f"| {media_count} Media Item(s)" if media_count > 0 else ""
        
        source_platform = post_data.get('platform', 'unknown')
        feed_type = post_data.get('feed_type', 'unknown')
        post_class = f"post-block {feed_type}" if feed_type != 'unknown' else "post-block"
        
        if source_platform == 'rss':
            feed_title = post_data.get('feed_title', 'RSS Feed')
            post_title = post_data.get('title', 'No title')
            feed_badge = self._get_feed_type_badge(feed_type)
            header_html = f"""
            <div class="source-info">From: {html.escape(feed_title)} {feed_badge}</div>
            <div class="post-title">{html.escape(post_title)}</div>
            <div class="post-header">
                <strong>Published:</strong> {post_data['date'].strftime('%Y-%m-%d %H:%M:%S')}
                {media_indicator}
            </div>
            """
        else:
            source_info = f"<strong>From:</strong> {post_data['source']} | " if show_channel and post_data.get('source') else ""
            header_html = f"""
            <div class="post-header">
                {source_info}
                <strong>URL:</strong> {post_data.get('url', 'No URL')} | 
                <strong>Date:</strong> {post_data['date'].strftime('%Y-%m-%d %H:%M:%S')}
                {media_indicator}
            </div>
            """

        categories_html = self._format_categories(post_data.get('categories', []))

        # Simplified content processing
        if source_platform == 'rss' and post_data.get('content_html'):
            post_text_html = post_data['content_html']
        else:
            raw_content = post_data.get('content', 'No content')
            # Always use the reliable markdown converter
            post_text_html = self._convert_markdown_to_html(raw_content)
        
        media_gallery_html = ""
        if post_data.get('media_urls'):
            media_gallery_html += '<div class="media-gallery">'
            for url in post_data['media_urls']:
                if url and url.strip():
                    media_gallery_html += self._create_media_html(url)
            media_gallery_html += '</div>'

        return f"""
        <div class="{post_class}">
            {header_html}
            {categories_html}
            <div class="post-content">
                {post_text_html}
                {media_gallery_html}
            </div>
            <div class="post-footer">
                <a href="{post_data.get('url', '#')}" target="_blank">View Original</a>
            </div>
        </div>
        """

    def render_report(self, posts: list):
        """Renders a simple list of posts."""
        for post in posts:
            self.body_content += self._format_post(post)

    def render_briefing(self, briefing_data: dict, days: int):
        """Renders a full daily briefing, organized by channel/feed and date."""
        self.title = f"I.N.S.I.G.H.T. Briefing - Last {days} Days"
        for source, posts in briefing_data.items():
            if not posts: continue
            
            first_post = posts[0]
            source_platform = first_post.get('platform', 'telegram')
            
            if source_platform == 'rss':
                feed_title = first_post.get('feed_title', source)
                feed_type = first_post.get('feed_type', 'rss')
                feed_badge = self._get_feed_type_badge(feed_type)
                self.body_content += f'<h2 class="channel-header">Intel From: {html.escape(feed_title)} {feed_badge}</h2>'
            else:
                self.body_content += f'<h2 class="channel-header">Intel From: @{source.upper()}</h2>'
            
            posts_by_day = {}
            for post in posts:
                day_str = post['date'].strftime('%Y-%m-%d, %A')
                if day_str not in posts_by_day:
                    posts_by_day[day_str] = []
                posts_by_day[day_str].append(post)
            
            for day, day_posts in sorted(posts_by_day.items(), key=lambda item: datetime.strptime(item[0].split(',')[0], '%Y-%m-%d'), reverse=True):
                self.body_content += f'<h3 class="date-header">{day}</h3>'
                for post_data in day_posts:
                    self.body_content += self._format_post(post_data)

    def render_rss_briefing(self, posts: list, title: str):
        """Render RSS-specific briefing with category analytics."""
        self.title = title
        if not posts:
            self.body_content += "<p>No RSS posts found for this briefing.</p>"
            return
            
        all_categories = set()
        feed_types = set()
        for post in posts:
            all_categories.update(post.get('categories', []))
            feed_types.add(post.get('feed_type', 'unknown'))
        
        analytics_html = f"""
        <div class="post-block">
            <div class="post-header">📊 Briefing Analytics</div>
            <div class="post-content">
                <p><strong>Total Posts:</strong> {len(posts)}</p>
                <p><strong>Feed Types:</strong> {', '.join(sorted(feed_types)) if feed_types else 'Unknown'}</p>
                <p><strong>Unique Categories:</strong> {len(all_categories)}</p>
                {self._format_categories(sorted(list(all_categories)))}
            </div>
        </div>
        """
        self.body_content += analytics_html
        
        for post in posts:
            self.body_content += self._format_post(post)

    def save_to_file(self, filename="insight_report.html"):
        """Generates the final HTML and saves it to a file."""
        final_html = self._get_html_template()
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(final_html)
            logging.info(f"Successfully generated HTML dossier: {filename}")
        except Exception as e:
            logging.error(f"Failed to save HTML file: {e}")