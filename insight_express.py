#!/usr/bin/env python3
"""
INSIGHT Express - MVP Core Intelligence Engine
Simple, fast personal news assistant powered by Gemini 2.5 Flash
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from google import genai
from google.genai import types

# Import your existing Mark II infrastructure  
from main import InsightOperator
from config.config_manager import ConfigManager

class InsightExpress:
    """
    MVP Core Intelligence Engine
    
    Takes your existing connectors, processes with Gemini, outputs intelligent briefings
    """
    
    def __init__(self):
        """Initialize the intelligence engine"""
        print("🚀 INSIGHT Express - Initializing...")
        
        # Initialize Gemini
        self.gemini_client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )
        
        # Initialize your existing Mark II infrastructure
        self.insight_operator = InsightOperator(debug_mode=False)
        self.config_manager = ConfigManager()
        
        print("✅ Intelligence engine ready")
    
    async def collect_today_intelligence(self) -> Dict[str, List[Dict]]:
        """
        Collect intelligence from all enabled sources
        
        Returns:
            Dict with 'telegram' and 'rss' data
        """
        print("📡 Collecting intelligence from sources...")
        
        # Connect to all available platforms
        await self.insight_operator.connect_all()
        
        intelligence_data = {
            'telegram': [],
            'rss': [],
            'collection_time': datetime.now().isoformat()
        }
        
        # Get enabled sources from config
        config = self.config_manager.load_config()
        enabled_sources = self.config_manager.get_enabled_sources(config)
        
        # Collect Telegram posts (last 24 hours)
        if 'telegram' in enabled_sources:
            telegram_channels = enabled_sources['telegram'].get('channels', [])
            print(f"📱 Collecting from {len(telegram_channels)} Telegram channels...")
            
            for channel in telegram_channels:
                try:
                    # Get last 10 posts from each channel
                    posts = await self.insight_operator.get_n_posts(channel, 10)
                    if posts:
                        # Filter posts from last 24 hours
                        recent_posts = self._filter_recent_posts(posts, hours=24)
                        intelligence_data['telegram'].extend(recent_posts)
                        print(f"  📋 {channel}: {len(recent_posts)} recent posts")
                except Exception as e:
                    print(f"  ❌ {channel}: Failed - {e}")
        
        # Collect RSS posts (last 24 hours)  
        if 'rss' in enabled_sources:
            rss_feeds = enabled_sources['rss'].get('feeds', [])
            print(f"📰 Collecting from {len(rss_feeds)} RSS feeds...")
            
            for feed_url in rss_feeds:
                try:
                    # Get last 20 posts from each feed
                    posts = await self.insight_operator.get_rss_posts(feed_url, 20)
                    if posts:
                        # Filter posts from last 24 hours
                        recent_posts = self._filter_recent_posts(posts, hours=24)
                        intelligence_data['rss'].extend(recent_posts)
                        feed_name = self._extract_feed_name(feed_url)
                        print(f"  📋 {feed_name}: {len(recent_posts)} recent posts")
                except Exception as e:
                    print(f"  ❌ {feed_url}: Failed - {e}")
        
        await self.insight_operator.disconnect_all()
        
        total_posts = len(intelligence_data['telegram']) + len(intelligence_data['rss'])
        print(f"✅ Collection complete: {total_posts} total posts")
        
        return intelligence_data
    
    def _filter_recent_posts(self, posts: List[Dict], hours: int = 24) -> List[Dict]:
        """Filter posts to only include recent ones"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_posts = []
        
        for post in posts:
            post_time = post.get('timestamp')
            if post_time:
                # Handle different timestamp formats
                if isinstance(post_time, str):
                    try:
                        post_datetime = datetime.fromisoformat(post_time.replace('Z', '+00:00'))
                        if post_datetime.replace(tzinfo=None) > cutoff_time:
                            recent_posts.append(post)
                    except:
                        # If parsing fails, include the post to be safe
                        recent_posts.append(post)
                else:
                    recent_posts.append(post)
        
        return recent_posts
    
    def _extract_feed_name(self, feed_url: str) -> str:
        """Extract a readable name from feed URL"""
        if 'simonwillison' in feed_url:
            return "Simon Willison's Weblog"
        elif 'localllama' in feed_url:
            return "LocalLLaMA Newsletter"
        elif 'reddit.com/r/LocalLLaMA' in feed_url:
            return "r/LocalLLaMA"
        else:
            return feed_url.split('/')[2] if '/' in feed_url else feed_url
    
    def process_with_gemini(self, intelligence_data: Dict[str, List[Dict]]) -> str:
        """
        Send collected intelligence to Gemini for processing
        
        Returns:
            HTML-formatted intelligent briefing
        """
        print("🧠 Processing intelligence with Gemini...")
        
        # Prepare the prompt
        telegram_count = len(intelligence_data['telegram'])
        rss_count = len(intelligence_data['rss'])
        total_count = telegram_count + rss_count
        
        if total_count == 0:
            return self._generate_empty_briefing()
        
        # Format data for Gemini
        formatted_content = self._format_for_gemini(intelligence_data)
        
        prompt = f"""
You are an expert intelligence analyst. I've collected {total_count} posts from my news sources in the last 24 hours ({telegram_count} from Telegram, {rss_count} from RSS feeds).

Your task: Create a smart daily briefing that saves me time and highlights what matters.

RULES:
1. **Remove duplicates**: If multiple sources cover the same story, combine them into one entry
2. **Score importance**: Rate each story 1-10 based on significance 
3. **Categorize**: Group by topics (AI/Tech, Programming, Business, etc.)
4. **Summarize**: 2-3 sentences max per story
5. **Highlight key insights**: What should I actually know/remember?

OUTPUT FORMAT (HTML):
```html
<div class="daily-briefing">
    <h1>📰 Daily Intelligence Briefing</h1>
    <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Sources: {total_count} posts processed</p>
    
    <div class="top-stories">
        <h2>🔥 Top Stories (Importance: 8-10)</h2>
        <!-- List top 3-5 most important stories -->
    </div>
    
    <div class="by-category">
        <h2>📊 By Category</h2>
        
        <h3>🤖 AI & Technology</h3>
        <!-- AI-related stories -->
        
        <h3>💻 Programming & Development</h3>
        <!-- Dev-related stories -->
        
        <h3>📈 Business & Industry</h3>
        <!-- Business stories -->
        
        <!-- Add other categories as needed -->
    </div>
    
    <div class="quick-insights">
        <h2>💡 Key Takeaways</h2>
        <!-- 3-5 bullet points of what I should remember -->
    </div>
</div>
```

CONTENT TO PROCESS:
{formatted_content}

Generate the HTML briefing now:
"""

        try:
            # Send to Gemini
            model = "gemini-2.5-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=-1,
                ),
                response_mime_type="text/plain",
            )

            print("  🔄 Analyzing content...")
            response_text = ""
            
            for chunk in self.gemini_client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                response_text += chunk.text
            
            print("✅ Gemini processing complete")
            return response_text
            
        except Exception as e:
            print(f"❌ Gemini processing failed: {e}")
            return self._generate_error_briefing(str(e))
    
    def _format_for_gemini(self, intelligence_data: Dict[str, List[Dict]]) -> str:
        """Format collected data for Gemini processing"""
        formatted = []
        
        # Format Telegram posts
        for post in intelligence_data['telegram']:
            source = post.get('source_id', 'Unknown')
            content = post.get('content', '')[:500]  # Limit content length
            timestamp = post.get('timestamp', '')
            
            formatted.append(f"[TELEGRAM] {source} | {timestamp}\n{content}\n")
        
        # Format RSS posts  
        for post in intelligence_data['rss']:
            source = post.get('source_id', 'Unknown')
            title = post.get('title', 'No Title')
            content = post.get('content', '')[:500]  # Limit content length
            timestamp = post.get('timestamp', '')
            
            formatted.append(f"[RSS] {source} | {timestamp}\n{title}\n{content}\n")
        
        return "\n---\n".join(formatted)
    
    def _generate_empty_briefing(self) -> str:
        """Generate briefing when no content is available"""
        return f"""
<div class="daily-briefing">
    <h1>📰 Daily Intelligence Briefing</h1>
    <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | No new content found</p>
    
    <div class="no-content">
        <h2>😴 All Quiet</h2>
        <p>No new posts found in the last 24 hours from your configured sources.</p>
        <p>Check your source configuration or try expanding the time window.</p>
    </div>
</div>
"""
    
    def _generate_error_briefing(self, error: str) -> str:
        """Generate briefing when Gemini processing fails"""
        return f"""
<div class="daily-briefing">
    <h1>📰 Daily Intelligence Briefing</h1>
    <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Error occurred</p>
    
    <div class="error">
        <h2>❌ Processing Error</h2>
        <p>Failed to process intelligence data: {error}</p>
        <p>Check your Gemini API configuration and try again.</p>
    </div>
</div>
"""

    async def run_daily_briefing(self) -> str:
        """
        Main entry point: Collect intelligence and generate briefing
        
        Returns:
            HTML briefing content
        """
        print("🎯 Starting daily intelligence briefing...")
        
        try:
            # Step 1: Collect intelligence
            intelligence_data = await self.collect_today_intelligence()
            
            # Step 2: Process with Gemini
            briefing_html = self.process_with_gemini(intelligence_data)
            
            # Step 3: Save briefing
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
            filename = f"briefing_express_{timestamp}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self._wrap_html(briefing_html))
            
            print(f"✅ Briefing saved: {filename}")
            return briefing_html
            
        except Exception as e:
            print(f"❌ Briefing generation failed: {e}")
            return self._generate_error_briefing(str(e))
    
    def _wrap_html(self, content: str) -> str:
        """Wrap briefing content in full HTML document"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>INSIGHT Express - Daily Briefing</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 30px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .top-stories {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .by-category {{ margin: 30px 0; }}
        .quick-insights {{ background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .no-content, .error {{ text-align: center; padding: 40px; background: #f8f9fa; border-radius: 8px; }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""

# Main execution
async def main():
    """Main entry point for INSIGHT Express"""
    print("🚀 INSIGHT Express - MVP Intelligence Engine")
    print("=" * 50)
    
    # Check environment
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("   Set it with: export GEMINI_API_KEY=your_api_key")
        return
    
    # Initialize and run
    try:
        express = InsightExpress()
        briefing_html = await express.run_daily_briefing()
        
        print("\n" + "=" * 50)
        print("🎉 Daily briefing generated successfully!")
        print("📂 Check the generated HTML file for your intelligent briefing")
        
    except Exception as e:
        print(f"💥 Critical error: {e}")

if __name__ == "__main__":
    asyncio.run(main())