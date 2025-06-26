#!/usr/bin/env python3
"""
INSIGHT Express - Enhanced MVP with Source Quotations
Transparent intelligence analysis with source preservation
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from google import genai
from google.genai import types

# Fix Windows console encoding issues
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    os.system("chcp 65001 >nul")

# Import your existing Mark II infrastructure  
from main import InsightOperator
from config.config_manager import ConfigManager

class InsightExpressEnhanced:
    """
    Enhanced MVP Core Intelligence Engine with Source Preservation
    """
    
    def __init__(self):
        """Initialize the enhanced intelligence engine"""
        print("🚀 INSIGHT Express Enhanced - Initializing...")
        
        # Initialize Gemini
        self.gemini_client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )
        
        # Initialize your existing Mark II infrastructure
        self.insight_operator = InsightOperator(debug_mode=False)
        self.config_manager = ConfigManager()
        
        print("✅ Enhanced intelligence engine ready")
    
    async def collect_today_intelligence(self) -> Dict[str, List[Dict]]:
        """
        Collect intelligence from all enabled sources with enhanced metadata
        """
        print("📡 Collecting intelligence from sources...")
        
        await self.insight_operator.connect_all()
        
        intelligence_data = {
            'telegram': [],
            'rss': [],
            'collection_time': datetime.now().isoformat(),
            'collection_stats': {}
        }
        
        config = self.config_manager.load_config()
        sources_config = config.get('sources', {})
        
        # Enhanced Telegram collection
        telegram_config = sources_config.get('telegram', {})
        if telegram_config.get('enabled', False) and 'telegram' in self.insight_operator.connectors:
            telegram_channels = telegram_config.get('channels', [])
            print(f"📱 Collecting from {len(telegram_channels)} Telegram channels...")
            
            for channel in telegram_channels:
                try:
                    posts = await self.insight_operator.get_n_posts(channel, 15)  # Get more posts
                    if posts:
                        recent_posts = self._filter_recent_posts(posts, hours=24)
                        # Add enhanced metadata
                        for post in recent_posts:
                            post['collection_source'] = 'telegram'
                            post['collection_channel'] = channel
                        intelligence_data['telegram'].extend(recent_posts)
                        print(f"  📋 {channel}: {len(recent_posts)} recent posts")
                except Exception as e:
                    print(f"  ❌ {channel}: Failed - {e}")
        
        # Enhanced RSS collection  
        rss_config = sources_config.get('rss', {})
        if rss_config.get('enabled', False) and 'rss' in self.insight_operator.connectors:
            rss_feeds = rss_config.get('feeds', [])
            print(f"📰 Collecting from {len(rss_feeds)} RSS feeds...")
            
            for feed_url in rss_feeds:
                try:
                    posts = await self.insight_operator.get_rss_posts(feed_url, 25)  # Get more posts
                    if posts:
                        recent_posts = self._filter_recent_posts(posts, hours=24)
                        # Add enhanced metadata
                        feed_name = self._extract_feed_name(feed_url)
                        for post in recent_posts:
                            post['collection_source'] = 'rss'
                            post['collection_feed'] = feed_name
                            post['collection_feed_url'] = feed_url
                        intelligence_data['rss'].extend(recent_posts)
                        print(f"  📋 {feed_name}: {len(recent_posts)} recent posts")
                except Exception as e:
                    print(f"  ❌ {feed_url}: Failed - {e}")
        
        await self.insight_operator.disconnect_all()
        
        # Collection statistics
        total_posts = len(intelligence_data['telegram']) + len(intelligence_data['rss'])
        intelligence_data['collection_stats'] = {
            'total_posts': total_posts,
            'telegram_posts': len(intelligence_data['telegram']),
            'rss_posts': len(intelligence_data['rss']),
            'collection_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"✅ Collection complete: {total_posts} total posts")
        return intelligence_data
    
    def _filter_recent_posts(self, posts: List[Dict], hours: int = 24) -> List[Dict]:
        """Filter posts to only include recent ones"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_posts = []
        
        for post in posts:
            post_time = post.get('timestamp')
            if post_time:
                try:
                    if isinstance(post_time, str):
                        if post_time.endswith('Z'):
                            post_time = post_time[:-1] + '+00:00'
                        post_datetime = datetime.fromisoformat(post_time)
                        if post_datetime.tzinfo:
                            post_datetime = post_datetime.replace(tzinfo=None)
                        if post_datetime > cutoff_time:
                            recent_posts.append(post)
                except Exception:
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
    
    def process_with_gemini_enhanced(self, intelligence_data: Dict[str, List[Dict]]) -> str:
        """
        Enhanced processing with source preservation and reasoning transparency
        """
        print("🧠 Processing intelligence with Enhanced Gemini analysis...")
        
        telegram_count = len(intelligence_data['telegram'])
        rss_count = len(intelligence_data['rss'])
        total_count = telegram_count + rss_count
        
        if total_count == 0:
            print("📭 No recent content found")
            return self._generate_empty_briefing()
        
        # Enhanced formatting with source preservation
        formatted_content = self._format_for_gemini_enhanced(intelligence_data)
        
        prompt = f"""
You are an expert intelligence analyst creating a transparent daily briefing. I've collected {total_count} posts from my sources in the last 24 hours.

CRITICAL REQUIREMENTS:
1. **PRESERVE SOURCE QUOTATIONS**: For every analysis point, include the exact quote that supports it
2. **SHOW YOUR REASONING**: Explain why you classified something as important 
3. **TRACK DUPLICATES**: When combining stories, list all sources that covered it
4. **RATE WITH JUSTIFICATION**: Explain your 1-10 importance scoring

ANALYSIS TASKS:
1. **Duplicate Detection**: Find stories covered by multiple sources
2. **Importance Scoring**: Rate each story 1-10 with reasoning
3. **Categorization**: Group by topic with source attribution
4. **Key Insights**: Extract actionable intelligence

OUTPUT FORMAT - Enhanced HTML with Source Transparency:
```html
<div class="daily-briefing">
    <h1>📰 Enhanced Daily Intelligence Briefing</h1>
    <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Sources: {total_count} posts analyzed | Transparency Mode: ON</p>
    
    <div class="collection-stats">
        <h2>📊 Collection Statistics</h2>
        <ul>
            <li>Telegram Posts: {telegram_count}</li>
            <li>RSS Posts: {rss_count}</li>
            <li>Analysis Method: Source-Preserved Intelligence</li>
        </ul>
    </div>
    
    <div class="top-stories">
        <h2>🔥 Top Stories (Importance: 8-10)</h2>
        
        <div class="story">
            <h3>Story Title (Importance: X/10)</h3>
            <p class="reasoning"><strong>Why Important:</strong> [Your reasoning for the score]</p>
            <p class="summary">[2-3 sentence summary]</p>
            <div class="sources">
                <h4>📋 Source Evidence:</h4>
                <blockquote class="source-quote">
                    <p>"[Exact quote from source]"</p>
                    <cite>— Source Name, Platform</cite>
                </blockquote>
                <!-- Repeat for multiple sources if story appeared multiple times -->
            </div>
        </div>
        <!-- Repeat for each top story -->
    </div>
    
    <div class="by-category">
        <h2>📂 Stories by Category</h2>
        
        <div class="category">
            <h3>🤖 AI & Technology</h3>
            <div class="story">
                <h4>Story Title (Importance: X/10)</h4>
                <p>[Summary with reasoning]</p>
                <blockquote class="source-quote">
                    <p>"[Supporting quote]"</p>
                    <cite>— Source, Platform</cite>
                </blockquote>
            </div>
        </div>
        
        <div class="category">
            <h3>💻 Programming & Development</h3>
            <!-- Similar structure -->
        </div>
        
        <!-- Add other categories as needed -->
    </div>
    
    <div class="duplicate-analysis">
        <h2>🔄 Duplicate Story Analysis</h2>
        <div class="duplicate-group">
            <h3>Story: [Common Topic]</h3>
            <p><strong>Coverage Count:</strong> X sources</p>
            <ul>
                <li><strong>Source 1:</strong> "[Quote]"</li>
                <li><strong>Source 2:</strong> "[Quote]"</li>
            </ul>
            <p><strong>Analysis:</strong> [What's unique vs redundant]</p>
        </div>
    </div>
    
    <div class="insights">
        <h2>💡 Key Intelligence Takeaways</h2>
        <div class="insight">
            <h3>Insight: [Key Point]</h3>
            <p>[Why this matters]</p>
            <blockquote class="source-quote">
                <p>"[Supporting evidence]"</p>
                <cite>— Source Evidence</cite>
            </blockquote>
        </div>
    </div>
    
    <div class="reasoning-transparency">
        <h2>🔍 Analysis Methodology</h2>
        <ul>
            <li><strong>Duplicate Detection:</strong> [How you found duplicates]</li>
            <li><strong>Importance Scoring:</strong> [Your criteria]</li>
            <li><strong>Source Quality:</strong> [Assessment of source reliability]</li>
        </ul>
    </div>
</div>
```

CONTENT TO ANALYZE:
{formatted_content}

Remember: EVERY analysis point must include the source quote that supports it. Show your reasoning process completely.

Generate the enhanced HTML briefing now:
"""

        try:
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

            print("  🔄 Enhanced analysis in progress...")
            print("  📋 Preserving source quotations...")
            print("  🧮 Analyzing reasoning patterns...")
            
            response_text = ""
            for chunk in self.gemini_client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                response_text += chunk.text
            
            print("✅ Enhanced Gemini processing complete")
            return response_text
            
        except Exception as e:
            print(f"❌ Enhanced processing failed: {e}")
            return self._generate_error_briefing(str(e))
    
    def _format_for_gemini_enhanced(self, intelligence_data: Dict[str, List[Dict]]) -> str:
        """Enhanced formatting with complete source preservation"""
        formatted = []
        
        # Enhanced Telegram formatting
        for i, post in enumerate(intelligence_data['telegram']):
            source = post.get('collection_channel', 'Unknown')
            content = post.get('content', '')
            title = post.get('title', 'No Title')
            timestamp = post.get('timestamp', '')
            post_url = post.get('post_url', '')
            
            # Preserve more content for analysis
            content_preview = content[:800] + "..." if len(content) > 800 else content
            
            formatted.append(f"""
[TELEGRAM POST #{i+1}]
Channel: @{source}
Timestamp: {timestamp}
URL: {post_url}
Title: {title}
Content: "{content_preview}"
Full Length: {len(content)} characters
""")
        
        # Enhanced RSS formatting
        for i, post in enumerate(intelligence_data['rss']):
            source = post.get('collection_feed', 'Unknown')
            title = post.get('title', 'No Title')
            content = post.get('content', '')
            timestamp = post.get('timestamp', '')
            post_url = post.get('post_url', '')
            categories = post.get('categories', [])
            
            content_preview = content[:800] + "..." if len(content) > 800 else content
            
            formatted.append(f"""
[RSS POST #{i+1}]
Feed: {source}
Title: "{title}"
Timestamp: {timestamp}
URL: {post_url}
Categories: {', '.join(categories) if categories else 'None'}
Content: "{content_preview}"
Full Length: {len(content)} characters
""")
        
        return "\n" + "="*80 + "\n".join(formatted) + "\n" + "="*80
    
    def _generate_empty_briefing(self) -> str:
        """Generate enhanced empty briefing"""
        return f"""
<div class="daily-briefing">
    <h1>📰 Enhanced Daily Intelligence Briefing</h1>
    <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | No new content found</p>
    
    <div class="no-content">
        <h2>😴 All Quiet on the Intelligence Front</h2>
        <p>No new posts found in the last 24 hours from your configured sources.</p>
        <div class="suggestions">
            <h3>💡 Suggestions:</h3>
            <ul>
                <li>Check your source configuration in config/sources.json</li>
                <li>Try expanding the time window to 48 hours</li>
                <li>Add more RSS feeds or Telegram channels</li>
                <li>Verify your API credentials are working</li>
            </ul>
        </div>
    </div>
</div>
"""
    
    def _generate_error_briefing(self, error: str) -> str:
        """Generate enhanced error briefing"""
        return f"""
<div class="daily-briefing">
    <h1>📰 Enhanced Daily Intelligence Briefing</h1>
    <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Error occurred</p>
    
    <div class="error">
        <h2>❌ Analysis Error</h2>
        <p>Failed to process intelligence data: {error}</p>
        <div class="troubleshooting">
            <h3>🔧 Troubleshooting:</h3>
            <ul>
                <li>Check your GEMINI_API_KEY environment variable</li>
                <li>Verify your API quota and billing</li>
                <li>Check your network connection</li>
                <li>Review the console output for detailed error messages</li>
            </ul>
        </div>
    </div>
</div>
"""

    async def run_enhanced_briefing(self) -> str:
        """Main entry point for enhanced briefing"""
        print("🎯 Starting Enhanced Daily Intelligence Briefing...")
        
        try:
            # Step 1: Enhanced collection
            intelligence_data = await self.collect_today_intelligence()
            
            # Step 2: Enhanced processing
            briefing_html = self.process_with_gemini_enhanced(intelligence_data)
            
            # Step 3: Save with enhanced naming
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
            filename = f"briefing_enhanced_{timestamp}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self._wrap_enhanced_html(briefing_html))
            
            print(f"✅ Enhanced briefing saved: {filename}")
            return briefing_html
            
        except Exception as e:
            print(f"❌ Enhanced briefing failed: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_error_briefing(str(e))
    
    def _wrap_enhanced_html(self, content: str) -> str:
        """Enhanced HTML wrapper with better styling"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>INSIGHT Express Enhanced - Daily Briefing</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            max-width: 900px; 
            margin: 0 auto; 
            padding: 20px; 
            line-height: 1.6; 
            background: #f8f9fa;
        }}
        .daily-briefing {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 30px; font-style: italic; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 15px; }}
        h3 {{ color: #7f8c8d; }}
        h4 {{ color: #95a5a6; }}
        
        .collection-stats {{ background: #e8f4f8; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .top-stories {{ background: #fff5f5; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #e74c3c; }}
        .by-category {{ margin: 30px 0; }}
        .category {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
        .story {{ margin: 15px 0; padding: 15px; background: white; border-radius: 6px; border-left: 3px solid #3498db; }}
        
        .source-quote {{ 
            background: #f7f7f7; 
            border-left: 4px solid #34495e; 
            padding: 15px; 
            margin: 10px 0; 
            font-style: italic; 
        }}
        .source-quote cite {{ 
            font-size: 0.9em; 
            color: #7f8c8d; 
            font-weight: bold; 
        }}
        
        .reasoning {{ 
            background: #e8f5e8; 
            padding: 10px; 
            border-radius: 6px; 
            margin: 10px 0; 
        }}
        
        .duplicate-analysis {{ 
            background: #fff9e6; 
            padding: 20px; 
            border-radius: 8px; 
            margin: 20px 0; 
            border-left: 4px solid #f39c12; 
        }}
        .duplicate-group {{ 
            margin: 15px 0; 
            padding: 15px; 
            background: white; 
            border-radius: 6px; 
        }}
        
        .insights {{ 
            background: #e8f5e8; 
            padding: 20px; 
            border-radius: 8px; 
            margin: 20px 0; 
            border-left: 4px solid #27ae60; 
        }}
        .insight {{ 
            margin: 15px 0; 
            padding: 15px; 
            background: white; 
            border-radius: 6px; 
        }}
        
        .reasoning-transparency {{ 
            background: #f0f0f0; 
            padding: 20px; 
            border-radius: 8px; 
            margin: 20px 0; 
            border-left: 4px solid #95a5a6; 
        }}
        
        .no-content, .error {{ 
            text-align: center; 
            padding: 40px; 
            background: #f8f9fa; 
            border-radius: 8px; 
        }}
        .suggestions, .troubleshooting {{ 
            text-align: left; 
            margin-top: 20px; 
            background: white; 
            padding: 20px; 
            border-radius: 6px; 
        }}
        
        ul {{ margin: 10px 0; padding-left: 20px; }}
        li {{ margin: 5px 0; }}
        
        @media (max-width: 600px) {{
            body {{ padding: 10px; }}
            .daily-briefing {{ padding: 15px; }}
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""

# Main execution
async def main():
    """Enhanced main entry point"""
    print("🚀 INSIGHT Express Enhanced - Source-Transparent Intelligence")
    print("=" * 60)
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("   PowerShell: $env:GEMINI_API_KEY='your_api_key'")
        return
    
    try:
        express = InsightExpressEnhanced()
        briefing_html = await express.run_enhanced_briefing()
        
        print("\n" + "=" * 60)
        print("🎉 Enhanced briefing generated successfully!")
        print("📂 Check the generated HTML file for transparent intelligence analysis")
        print("🔍 Now includes source quotations and reasoning transparency")
        
    except Exception as e:
        print(f"💥 Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())