# html_renderer.py
import html
from datetime import datetime
import logging

class HTMLRenderer:
    """
    A dedicated module for rendering I.N.S.I.G.H.T. reports and briefings
    into a clean, self-contained HTML file.
    """

    def __init__(self, report_title="I.N.S.I.G.H.T. Report"):
        self.title = html.escape(report_title)
        self.body_content = ""

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
            max-width: 800px;
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
        .post-header {{
            font-size: 0.9em;
            color: #aaa;
            margin-bottom: 10px;
            border-bottom: 1px solid #444;
            padding-bottom: 5px;
        }}
        .post-content p {{
            margin: 0 0 1em 0;
            white-space: pre-wrap; /* Preserve line breaks from Telegram */
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
        .post-footer a {{
            color: #00aaff;
            text-decoration: none;
        }}
        .channel-header, .date-header {{
            margin-top: 40px;
            color: #00aaff;
            border-bottom: 1px solid #555;
            padding-bottom: 5px;
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

    # html_renderer.py (Updated _format_post method)

# ... inside the HTMLRenderer class ...

    def _format_post(self, post_data: dict, show_channel=False):
        """Converts a single post dictionary into an HTML block."""
        media_count = len(post_data['media_urls'])
        media_indicator = f"| {media_count} Media Item(s)" if media_count > 0 else ""
        
        # NEW: Conditionally add the channel name to the header
        channel_info = ""
        if show_channel and post_data.get('channel'):
            channel_info = f"<strong>From:</strong> @{post_data['channel']} | "

        # Sanitize text for HTML and preserve line breaks
        post_text_html = f"<p>{html.escape(post_data['text'])}</p>"
        
        # Create the media gallery
        media_gallery_html = ""
        if post_data['media_urls']:
            media_gallery_html += '<div class="media-gallery">'
            for url in post_data['media_urls']:
                media_gallery_html += f'<a href="{url}" target="_blank"><img src="{url}" alt="Telegram Media"></a>'
            media_gallery_html += '</div>'

        return f"""
        <div class="post-block">
            <div class="post-header">
                {channel_info}
                <strong>ID:</strong> {post_data['id']} | 
                <strong>Date:</strong> {post_data['date'].strftime('%Y-%m-%d %H:%M:%S')}
                {media_indicator}
            </div>
            <div class="post-content">
                {post_text_html}
                {media_gallery_html}
            </div>
            <div class="post-footer">
                <a href="{post_data['link']}" target="_blank">View on Telegram</a>
            </div>
        </div>
        """

    def render_report(self, posts: list):
        """Renders a simple list of posts."""
        for post in posts:
            self.body_content += self._format_post(post)

    def render_briefing(self, briefing_data: dict, days: int):
        """Renders a full daily briefing, organized by channel and date."""
        self.title = f"I.N.S.I.G.H.T. Briefing - Last {days} Days"
        for channel, posts in briefing_data.items():
            if not posts: continue
            
            self.body_content += f'<h2 class="channel-header">Intel From: @{channel.upper()}</h2>'
            
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

    def save_to_file(self, filename="insight_report.html"):
        """Generates the final HTML and saves it to a file."""
        final_html = self._get_html_template()
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(final_html)
            logging.info(f"Successfully generated HTML dossier: {filename}")
        except Exception as e:
            logging.error(f"Failed to save HTML file: {e}")