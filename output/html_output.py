# html_output.py
import html
from datetime import datetime
import logging
import re

class HTMLOutput:
    """
    A dedicated module for rendering I.N.S.I.G.H.T. reports and briefings
    into a clean, self-contained HTML file.
    
    Enhanced in v2.3 with RSS/Atom feed support, category display,
    and adaptive rendering for different content types.
    Enhanced in v2.4 with markdown-to-HTML conversion support.
    """

    def __init__(self, report_title="I.N.S.I.G.H.T. Report"):
        self.title = html.escape(report_title)
        self.body_content = ""

    def _convert_markdown_to_html(self, text: str) -> str:
        """
        Convert basic markdown to HTML.
        Supports: links, bold, italic, code, strikethrough, auto-linking, and line breaks.
        """
        if not text:
            return ""
        
        # Step 1: Protect and convert plain URLs to links FIRST (before other markdown processing)
        # This prevents URLs with underscores from being treated as italic markdown
        url_pattern = r'https?://[^\s<>"\']+(?:[^\s<>"\'.,;!?])'
        
        # Find all URLs and replace them with placeholder tokens
        urls = re.findall(url_pattern, text)
        url_placeholders = {}
        
        for i, url in enumerate(urls):
            placeholder = f"__URL_PLACEHOLDER_{i}__"
            url_placeholders[placeholder] = f'<a href="{url}" target="_blank">{url}</a>'
            text = text.replace(url, placeholder, 1)  # Replace only first occurrence
        
        # Step 2: Convert markdown links [text](url) to HTML
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
        
        # Step 3: Convert other markdown patterns (now URLs are protected)
        # Convert strikethrough ~~text~~ to <del>
        text = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', text)
        
        # Convert bold **text** or __text__ to <strong>
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)
        
        # Convert italic *text* or _text_ to <em> (but not if surrounded by **)
        text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', text)
        text = re.sub(r'(?<!_)_([^_\n]+)_(?!_)', r'<em>\1</em>', text)
        
        # Convert inline code `text` to <code>
        text = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', text)
        
        # Convert headers ### text to <h3>
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        
        # Step 4: Restore URL placeholders with actual HTML links
        for placeholder, html_link in url_placeholders.items():
            text = text.replace(placeholder, html_link)
        
        # Step 5: Convert line breaks to <br> tags
        text = text.replace('\n', '<br>')
        
        # Step 6: Escape remaining HTML while preserving our converted markdown
        html_tag_pattern = r'(<a[^>]*>.*?</a>|<strong>.*?</strong>|<em>.*?</em>|<code>.*?</code>|<del>.*?</del>|<h[1-6]>.*?</h[1-6]>|<br>)'
        parts = re.split(html_tag_pattern, text)
        
        escaped_parts = []
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Even indices are plain text that should be escaped
                escaped_parts.append(html.escape(part))
            else:  # Odd indices are our HTML tags that should be preserved
                escaped_parts.append(part)
        
        return ''.join(escaped_parts)

    def _is_likely_markdown(self, text: str) -> bool:
        """
        Detect if text contains markdown patterns or plain URLs.
        """
        if not text:
            return False
            
        markdown_patterns = [
            r'\[.+\]\(.+\)',          # Links [text](url)
            r'\*\*.+\*\*',            # Bold **text**
            r'__.+__',                # Bold __text__
            r'(?<!\*)\*.+\*(?!\*)',   # Italic *text*
            r'(?<!_)_.+_(?!_)',       # Italic _text_
            r'`.+`',                  # Code `text`
            r'~~.+~~',                # Strikethrough ~~text~~
            r'^#{1,6} .+$',           # Headers # text
            r'https?://[^\s<>"\']+',  # Plain URLs (auto-link these)
        ]
        
        return any(re.search(pattern, text, re.MULTILINE) for pattern in markdown_patterns)

    def _get_html_template(self):
        """Returns the basic structure of the HTML document with embedded CSS."""
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
            white-space: pre-wrap; /* Preserve line breaks */
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
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }}
        .media-gallery a {{
            display: block;
        }}
        .media-gallery img {{
            max-width: 150px;
            max-height: 150px;
            border-radius: 4px;
            border: 2px solid #555;
            transition: transform 0.2s;
        }}
        .media-gallery img:hover {{
            transform: scale(1.05);
            border-color: #00aaff;
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

    def _format_post(self, post_data: dict, show_channel=False):
        """Converts a single post dictionary into an HTML block with enhanced RSS/Atom support."""
        media_count = len(post_data.get('media_urls', []))
        media_indicator = f"| {media_count} Media Item(s)" if media_count > 0 else ""
        
        # Determine post type and styling using NEW field names
        source_platform = post_data.get('platform', 'unknown')
        feed_type = post_data.get('feed_type', 'unknown')
        post_class = f"post-block {feed_type}" if feed_type != 'unknown' else "post-block"
        
        # Build header based on source type
        if source_platform == 'rss':
            # RSS/Atom post
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
            # Telegram post - use URL instead of legacy id field
            source_info = ""
            if show_channel and post_data.get('source'):
                source_info = f"<strong>From:</strong> {post_data['source']} | "
            
            header_html = f"""
            <div class="post-header">
                {source_info}
                <strong>URL:</strong> {post_data.get('url', 'No URL')} | 
                <strong>Date:</strong> {post_data['date'].strftime('%Y-%m-%d %H:%M:%S')}
                {media_indicator}
            </div>
            """

        # Format categories if available
        categories_html = ""
        if post_data.get('categories'):
            categories_html = self._format_categories(post_data['categories'])

        # Choose content based on source and available data with markdown support
        if source_platform == 'rss' and post_data.get('content_html'):
            # Use rich HTML content for RSS/Atom feeds if available
            content_html = post_data['content_html']
            # Ensure content is properly wrapped and safe
            if not content_html.strip().startswith('<'):
                post_text_html = f"<p>{content_html}</p>"
            else:
                post_text_html = content_html
        else:
            # Use content and convert markdown to HTML if detected
            raw_content = post_data.get('content', 'No content')
            
            if self._is_likely_markdown(raw_content):
                # Convert markdown to HTML
                converted_content = self._convert_markdown_to_html(raw_content)
                post_text_html = f"<p>{converted_content}</p>"
            else:
                # Fallback to escaped HTML for plain text
                post_text_html = f"<p>{html.escape(raw_content)}</p>"
        
        # Create the media gallery
        media_gallery_html = ""
        if post_data.get('media_urls'):
            media_gallery_html += '<div class="media-gallery">'
            for url in post_data['media_urls']:
                media_gallery_html += f'<a href="{url}" target="_blank"><img src="{url}" alt="Media Content"></a>'
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
        """Renders a simple list of posts with enhanced support for RSS/Atom feeds."""
        for post in posts:
            self.body_content += self._format_post(post)

    def render_briefing(self, briefing_data: dict, days: int):
        """Renders a full daily briefing, organized by channel/feed and date."""
        self.title = f"I.N.S.I.G.H.T. Briefing - Last {days} Days"
        for source, posts in briefing_data.items():
            if not posts: continue
            
            # Determine source type for header styling
            first_post = posts[0] if posts else {}
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
            
            for day, day_posts in sorted(posts_by_day.items()):
                self.body_content += f'<h3 class="date-header">{day}</h3>'
                for post_data in day_posts:
                    self.body_content += self._format_post(post_data)

    def render_rss_briefing(self, posts: list, title: str):
        """Render RSS-specific briefing with category analytics."""
        self.title = title
        
        if not posts:
            self.body_content += "<p>No RSS posts found for this briefing.</p>"
            return
        
        # Category analytics
        all_categories = set()
        feed_types = set()
        for post in posts:
            if post.get('categories'):
                all_categories.update(post['categories'])
            if post.get('feed_type'):
                feed_types.add(post['feed_type'])
        
        # Analytics header
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
        
        # Render posts
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