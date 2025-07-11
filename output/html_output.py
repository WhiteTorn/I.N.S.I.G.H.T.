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
    I.N.S.I.G.H.T. Daily Briefing HTML Renderer
    
    v3.1: Simplified daily briefing format with light mode theme
    Renders daily briefings with AI-generated summaries and chronologically sorted posts
    """

    def __init__(self, report_title="I.N.S.I.G.H.T. Daily Briefing"):
        self.title = html.escape(report_title)
        self.body_content = ""
        
        if MARKDOWN_AVAILABLE:
            self.markdown_processor = markdown.Markdown(
                extensions=[
                    'pymdownx.magiclink',
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.codehilite',
                    'markdown.extensions.tables',
                    'markdown.extensions.sane_lists',
                ],
                extension_configs={
                    'codehilite': {'use_pygments': False}
                }
            )

    def _convert_markdown_to_html(self, text: str) -> str:
        """Convert markdown to HTML using the standard markdown library."""
        if not text:
            return ""
        
        if MARKDOWN_AVAILABLE:
            self.markdown_processor.reset()
            return self.markdown_processor.convert(text)
        else:
            return f"<p>{html.escape(text)}</p>"

    def _get_html_template(self):
        """Returns the light mode HTML template optimized for daily briefings."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            background-color: #f8f9fa;
            color: #2c3e50;
            margin: 0;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        .main-content {{
            padding: 0;
        }}
        
        .day-section {{
            margin-bottom: 40px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .day-header {{
            background-color: #f8f9fa;
            padding: 20px 30px;
            border-left: 5px solid #667eea;
            margin-bottom: 0;
        }}
        
        .day-title {{
            font-size: 1.8em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .day-meta {{
            color: #6c757d;
            font-size: 0.95em;
        }}
        
        .briefing-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            margin: 0 30px 30px 30px;
            border-radius: 12px;
            border: 1px solid #dee2e6;
            overflow: hidden;
        }}
        
        .briefing-header {{
            background-color: #ffffff;
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            align-items: center;
        }}
        
        .briefing-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .briefing-icon {{
            font-size: 1.2em;
        }}
        
        .briefing-content {{
            padding: 25px;
            background-color: #ffffff;
        }}
        
        .briefing-summary {{
            font-size: 1.05em;
            line-height: 1.7;
            color: #495057;
            margin-bottom: 20px;
        }}
        
        .briefing-full-content {{
            color: #495057;
            line-height: 1.6;
        }}
        
        .briefing-full-content h1,
        .briefing-full-content h2,
        .briefing-full-content h3 {{
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        
        .briefing-full-content h1 {{
            font-size: 1.4em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 5px;
        }}
        
        .briefing-full-content h2 {{
            font-size: 1.2em;
            color: #667eea;
        }}
        
        .briefing-full-content h3 {{
            font-size: 1.1em;
            color: #6c757d;
        }}
        
        .briefing-full-content p {{
            margin-bottom: 1em;
        }}
        
        .briefing-full-content strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        
        .briefing-full-content em {{
            color: #667eea;
            font-style: italic;
        }}
        
        .briefing-full-content ul,
        .briefing-full-content ol {{
            margin-left: 20px;
            margin-bottom: 1em;
        }}
        
        .briefing-full-content li {{
            margin-bottom: 0.5em;
        }}
        
        .posts-section {{
            padding: 0 30px 30px 30px;
        }}
        
        .posts-header {{
            font-size: 1.4em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #dee2e6;
        }}
        
        .post-card {{
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .post-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        .post-header {{
            background-color: #f8f9fa;
            padding: 15px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .post-meta {{
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 8px;
        }}
        
        .post-title {{
            font-size: 1.2em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .post-content {{
            padding: 20px;
        }}
        
        .post-text {{
            color: #495057;
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        
        .post-text p {{
            margin-bottom: 1em;
        }}
        
        .post-text a {{
            color: #667eea;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s;
        }}
        
        .post-text a:hover {{
            border-bottom-color: #667eea;
        }}
        
        .post-footer {{
            padding: 15px;
            background-color: #f8f9fa;
            border-top: 1px solid #dee2e6;
        }}
        
        .post-actions {{
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        
        .action-btn {{
            background: none;
            border: none;
            color: #667eea;
            font-size: 0.9em;
            cursor: pointer;
            padding: 5px 10px;
            border-radius: 5px;
            transition: background-color 0.2s;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .action-btn:hover {{
            background-color: #e9ecef;
        }}
        
        .media-gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }}
        
        .media-item {{
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid #dee2e6;
        }}
        
        .media-item img {{
            width: 100%;
            height: auto;
            max-height: 200px;
            object-fit: cover;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 8px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .day-header, .briefing-content, .posts-section {{
                padding: 15px 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>📊 {self.title}</h1>
            <div class="subtitle">Intelligence Analysis & Strategic Insights</div>
        </header>
        <main class="main-content">
            {self.body_content}
        </main>
    </div>
</body>
</html>
        """

    def _format_briefing_content(self, briefing_text: str) -> str:
        """Format the AI-generated briefing content into HTML without categorization."""
        if not briefing_text:
            return "<p>No briefing available for this day.</p>"
        
        # Convert the full markdown to HTML without any categorization
        briefing_html = self._convert_markdown_to_html(briefing_text)
        
        return f'<div class="briefing-full-content">{briefing_html}</div>'

    def _format_post(self, post_data: dict) -> str:
        """Format a single post for the daily briefing layout."""
        # Handle post title
        if post_data.get('platform') == 'rss':
            post_title = post_data.get('title', 'RSS Post')
        else:
            # For Telegram posts, create a title from content
            content = post_data.get('content', '')
            post_title = content[:50] + "..." if len(content) > 50 else content
            if not post_title.strip():
                post_title = "Telegram Post"
        
        # Format date
        post_date = post_data.get('date', datetime.now())
        formatted_date = post_date.strftime('%H:%M')
        
        # Source information
        source = post_data.get('source', 'Unknown')
        if post_data.get('platform') == 'rss':
            source_info = f"📡 {post_data.get('feed_title', source)}"
        else:
            source_info = f"📱 @{source}"
        
        # Content
        content = post_data.get('content', '')
        if post_data.get('platform') == 'rss' and post_data.get('content_html'):
            content_html = self._sanitize_rss_html(post_data['content_html'])
        else:
            content_html = self._convert_markdown_to_html(content)
        
        # Media handling
        media_html = ""
        media_urls = post_data.get('media_urls', [])
        if media_urls:
            media_html = '<div class="media-gallery">'
            for url in media_urls[:3]:  # Limit to 3 media items
                if self._is_image_url(url):
                    media_html += f'<div class="media-item"><img src="{html.escape(url)}" alt="Media content" loading="lazy"></div>'
            media_html += '</div>'
        
        return f'''
        <div class="post-card">
            <div class="post-header">
                <div class="post-meta">{formatted_date} • {source_info}</div>
                <div class="post-title">{html.escape(post_title)}</div>
            </div>
            <div class="post-content">
                <div class="post-text">{content_html}</div>
                {media_html}
            </div>
            <div class="post-footer">
                <div class="post-actions">
                    <a href="{post_data.get('url', '#')}" target="_blank" class="action-btn">
                        🔗 View Original
                    </a>
                    <button class="action-btn">💾 Process</button>
                    <button class="action-btn">💬 Discuss</button>
                </div>
            </div>
        </div>
        '''

    def _sanitize_rss_html(self, raw_html: str) -> str:
        """Basic HTML sanitization for RSS content."""
        if not raw_html:
            return ""
        
        # Remove dangerous elements
        dangerous_elements = ['script', 'iframe', 'object', 'embed', 'style']
        for element in dangerous_elements:
            raw_html = re.sub(f'<{element}[^>]*>.*?</{element}>', '', raw_html, flags=re.IGNORECASE | re.DOTALL)
            raw_html = re.sub(f'<{element}[^>]*/?>', '', raw_html, flags=re.IGNORECASE)
        
        return raw_html

    def _is_image_url(self, url: str) -> bool:
        """Check if URL points to an image file."""
        if not url:
            return False
        clean_url = url.split('?')[0].lower()
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg')
        return any(clean_url.endswith(ext) for ext in image_extensions)

    def render_daily_briefing(self, day: datetime, briefing_text: str, posts: list):
        """Render a complete daily briefing with AI summary and sorted posts."""
        # Sort posts by date (newest first)
        sorted_posts = sorted(
            posts,
            key=lambda post: post.get('date', datetime.min),
            reverse=True
        )
        
        # Format day header
        day_formatted = day.strftime('%B %d, %Y')
        day_weekday = day.strftime('%A')
        
        # Build the HTML
        self.body_content += f'''
        <div class="day-section">
            <div class="day-header">
                <div class="day-title">📅 {day_formatted}</div>
                <div class="day-meta">{day_weekday} • {len(sorted_posts)} intelligence items</div>
            </div>
            
            <div class="briefing-card">
                <div class="briefing-header">
                    <div class="briefing-title">
                        <span class="briefing-icon">📊</span>
                        Full Daily Briefing
                    </div>
                </div>
                <div class="briefing-content">
                    {self._format_briefing_content(briefing_text)}
                </div>
            </div>
            
            <div class="posts-section">
                <div class="posts-header">Intelligence Items</div>
                {''.join(self._format_post(post) for post in sorted_posts)}
            </div>
        </div>
        '''

    def save_to_file(self, filename="insight_daily_briefing.html"):
        """Generate and save the final HTML file."""
        final_html = self._get_html_template()
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(final_html)
            logging.info(f"Successfully generated daily briefing: {filename}")
            return filename
        except Exception as e:
            logging.error(f"Failed to save HTML file: {e}")
            return None

    def render_topic_based_daily_briefing(self, day: datetime, enhanced_briefing: dict, posts: list):
        """
        Render a topic-based daily briefing with AI summary, ToC, and topic deep-dives.
        
        Args:
            day: Date for the briefing
            enhanced_briefing: Dict with daily_briefing, table_of_contents, and topics
            posts: List of all posts for reference
        """
        # Create post lookup by URL/ID for quick reference
        posts_by_id = {}
        for post in posts:
            post_id = post.get('url', f"post_{posts.index(post)}")
            posts_by_id[post_id] = post
        
        # Format day header
        day_formatted = day.strftime('%B %d, %Y')
        day_weekday = day.strftime('%A')
        
        # Extract data from enhanced briefing
        daily_briefing = enhanced_briefing.get('daily_briefing', 'No briefing available')
        table_of_contents = enhanced_briefing.get('table_of_contents', [])
        topics = enhanced_briefing.get('topics', [])
        
        # Build the HTML
        self.body_content += f'''
        <div class="day-section">
            <div class="day-header">
                <div class="day-title">📅 {day_formatted}</div>
                <div class="day-meta">{day_weekday} • {len(posts)} intelligence items • {len(topics)} topics</div>
            </div>
            
            <!-- Daily Briefing Section -->
            <div class="briefing-card">
                <div class="briefing-header">
                    <div class="briefing-title">
                        <span class="briefing-icon">📊</span>
                        Daily Briefing
                    </div>
                </div>
                <div class="briefing-content">
                    {self._format_briefing_content(daily_briefing)}
                </div>
            </div>
            
            <!-- Table of Contents Section -->
            <div class="toc-section">
                <div class="toc-header">
                    <div class="toc-title">
                        <span class="toc-icon">📋</span>
                        Topics Overview
                    </div>
                </div>
                <div class="toc-content">
                    <ol class="toc-list">
                        {''.join(f'<li><a href="#{topic["id"]}" class="toc-link">{topic["title"]}</a></li>' for topic in table_of_contents)}
                    </ol>
                </div>
            </div>
            
            <!-- Topics Deep Dive Section -->
            <div class="topics-section">
                <div class="topics-header">Deep Dive Analysis</div>
                {''.join(self._format_topic(topic, posts_by_id) for topic in topics)}
            </div>
        </div>
        '''

    def _format_topic(self, topic: dict, posts_by_id: dict) -> str:
        """Format a single topic with its deep-dive summary and referenced posts."""
        topic_id = topic.get('id', 'unknown-topic')
        topic_title = topic.get('title', 'Unknown Topic')
        topic_summary = topic.get('summary', 'No summary available')
        post_references = topic.get('post_references', [])
        
        # Convert summary to HTML
        summary_html = self._convert_markdown_to_html(topic_summary)
        
        # Build referenced posts HTML
        referenced_posts_html = ""
        for post_ref in post_references:
            if post_ref in posts_by_id:
                post = posts_by_id[post_ref]
                referenced_posts_html += self._format_referenced_post(post)
        
        return f'''
        <div class="topic-section" id="{topic_id}">
            <div class="topic-header">
                <div class="topic-title">
                    <span class="topic-icon">🔍</span>
                    {html.escape(topic_title)}
                </div>
            </div>
            <div class="topic-content">
                <div class="topic-summary">
                    {summary_html}
                </div>
                <div class="topic-sources">
                    <div class="sources-header">Referenced Intelligence Sources</div>
                    {referenced_posts_html}
                </div>
            </div>
        </div>
        '''

    def _format_referenced_post(self, post_data: dict) -> str:
        """Format a post that's referenced by a topic."""
        # Handle post title
        if post_data.get('platform') == 'rss':
            post_title = post_data.get('title', 'RSS Post')
        else:
            content = post_data.get('content', '')
            post_title = content[:50] + "..." if len(content) > 50 else content
            if not post_title.strip():
                post_title = "Telegram Post"
        
        # Format date
        post_date = post_data.get('date', datetime.now())
        formatted_date = post_date.strftime('%H:%M')
        
        # Source information
        source = post_data.get('source', 'Unknown')
        if post_data.get('platform') == 'rss':
            source_info = f"📡 {post_data.get('feed_title', source)}"
        else:
            source_info = f"📱 @{source}"
        
        # Content preview
        content = post_data.get('content', '')
        content_preview = content[:200] + "..." if len(content) > 200 else content
        content_html = self._convert_markdown_to_html(content_preview)
        
        return f'''
        <div class="referenced-post">
            <div class="referenced-post-header">
                <div class="referenced-post-meta">{formatted_date} • {source_info}</div>
                <div class="referenced-post-title">{html.escape(post_title)}</div>
            </div>
            <div class="referenced-post-content">
                {content_html}
            </div>
            <div class="referenced-post-footer">
                <a href="{post_data.get('url', '#')}" target="_blank" class="reference-link">
                    🔗 View Full Post
                </a>
            </div>
        </div>
        '''

    def _get_enhanced_html_template(self):
        """Returns the enhanced HTML template with topic-based styling."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        /* Existing styles from _get_html_template() */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            background-color: #f8f9fa;
            color: #2c3e50;
            margin: 0;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        .main-content {{
            padding: 0;
        }}
        
        /* Enhanced styles for topic-based layout */
        .day-section {{
            margin-bottom: 40px;
        }}
        
        .day-header {{
            background-color: #f8f9fa;
            padding: 20px 30px;
            border-left: 5px solid #667eea;
            margin-bottom: 0;
        }}
        
        .day-title {{
            font-size: 1.8em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .day-meta {{
            color: #6c757d;
            font-size: 0.95em;
        }}
        
        /* Table of Contents Styles */
        .toc-section {{
            background: linear-gradient(135deg, #e8f4f8 0%, #d6eaf8 100%);
            margin: 0 30px 30px 30px;
            border-radius: 12px;
            border: 1px solid #bee5eb;
            overflow: hidden;
        }}
        
        .toc-header {{
            background-color: #d1ecf1;
            padding: 20px;
            border-bottom: 1px solid #bee5eb;
            display: flex;
            align-items: center;
        }}
        
        .toc-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #0c5460;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .toc-icon {{
            font-size: 1.2em;
        }}
        
        .toc-content {{
            padding: 25px;
            background-color: #ffffff;
        }}
        
        .toc-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .toc-list li {{
            margin-bottom: 10px;
            padding: 12px 15px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 3px solid #17a2b8;
            transition: all 0.2s ease;
        }}
        
        .toc-list li:hover {{
            background: #e2e6ea;
            transform: translateX(5px);
        }}
        
        .toc-link {{
            color: #495057;
            text-decoration: none;
            font-weight: 500;
            font-size: 1.05em;
            display: block;
        }}
        
        .toc-link:hover {{
            color: #0c5460;
        }}
        
        /* Topics Section Styles */
        .topics-section {{
            padding: 0 30px 30px 30px;
        }}
        
        .topics-header {{
            font-size: 1.4em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #dee2e6;
        }}
        
        /* Individual Topic Styles */
        .topic-section {{
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 12px;
            margin-bottom: 30px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .topic-header {{
            background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
            padding: 20px;
            border-bottom: 1px solid #f39c12;
        }}
        
        .topic-title {{
            font-size: 1.4em;
            font-weight: 600;
            color: #8b4513;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .topic-icon {{
            font-size: 1.2em;
        }}
        
        .topic-content {{
            padding: 25px;
        }}
        
        .topic-summary {{
            font-size: 1.05em;
            line-height: 1.7;
            color: #495057;
            margin-bottom: 25px;
        }}
        
        .topic-summary h1,
        .topic-summary h2,
        .topic-summary h3 {{
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        
        .topic-summary h1 {{
            font-size: 1.3em;
            border-bottom: 2px solid #f39c12;
            padding-bottom: 5px;
        }}
        
        .topic-summary h2 {{
            font-size: 1.15em;
            color: #e67e22;
        }}
        
        .topic-summary h3 {{
            font-size: 1.05em;
            color: #6c757d;
        }}
        
        .topic-summary strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        
        .topic-summary em {{
            color: #e67e22;
            font-style: italic;
        }}
        
        /* Topic Sources Styles */
        .topic-sources {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }}
        
        .sources-header {{
            font-size: 1.1em;
            font-weight: 600;
            color: #155724;
            margin-bottom: 15px;
        }}
        
        /* Referenced Post Styles */
        .referenced-post {{
            background: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 15px;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .referenced-post:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        .referenced-post-header {{
            background-color: #f8f9fa;
            padding: 12px 15px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .referenced-post-meta {{
            font-size: 0.85em;
            color: #6c757d;
            margin-bottom: 5px;
        }}
        
        .referenced-post-title {{
            font-size: 1em;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .referenced-post-content {{
            padding: 15px;
            color: #495057;
            line-height: 1.5;
        }}
        
        .referenced-post-footer {{
            padding: 12px 15px;
            background-color: #f8f9fa;
            border-top: 1px solid #dee2e6;
            text-align: right;
        }}
        
        .reference-link {{
            color: #28a745;
            text-decoration: none;
            font-size: 0.9em;
            font-weight: 500;
        }}
        
        .reference-link:hover {{
            color: #1e7e34;
            text-decoration: underline;
        }}
        
        /* Existing briefing styles */
        .briefing-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            margin: 0 30px 30px 30px;
            border-radius: 12px;
            border: 1px solid #dee2e6;
            overflow: hidden;
        }}
        
        .briefing-header {{
            background-color: #ffffff;
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            align-items: center;
        }}
        
        .briefing-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .briefing-icon {{
            font-size: 1.2em;
        }}
        
        .briefing-content {{
            padding: 25px;
            background-color: #ffffff;
        }}
        
        .briefing-full-content {{
            color: #495057;
            line-height: 1.6;
        }}
        
        .briefing-full-content h1,
        .briefing-full-content h2,
        .briefing-full-content h3 {{
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        
        .briefing-full-content h1 {{
            font-size: 1.4em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 5px;
        }}
        
        .briefing-full-content h2 {{
            font-size: 1.2em;
            color: #667eea;
        }}
        
        .briefing-full-content h3 {{
            font-size: 1.1em;
            color: #6c757d;
        }}
        
        .briefing-full-content p {{
            margin-bottom: 1em;
        }}
        
        .briefing-full-content strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        
        .briefing-full-content em {{
            color: #667eea;
            font-style: italic;
        }}
        
        .briefing-full-content ul,
        .briefing-full-content ol {{
            margin-left: 20px;
            margin-bottom: 1em;
        }}
        
        .briefing-full-content li {{
            margin-bottom: 0.5em;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 8px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .day-header, .briefing-content, .toc-content, .topic-content, .topics-section {{
                padding: 15px 20px;
            }}
            
            .topic-title {{
                font-size: 1.2em;
            }}
            
            .toc-list li {{
                padding: 10px 12px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>📊 {self.title}</h1>
            <div class="subtitle">Enhanced Intelligence Analysis & Strategic Insights</div>
        </header>
        <main class="main-content">
            {self.body_content}
        </main>
    </div>
</body>
</html>
        """
    
