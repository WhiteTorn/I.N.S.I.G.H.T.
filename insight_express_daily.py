#!/usr/bin/env python3
"""
INSIGHT Express - Multi-Day Daily Briefings Engine (Fixed)
Direct connector approach with robust error handling
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta, date, timezone
from typing import List, Dict, Any, Tuple
from google import genai
from google.genai import types

# Fix Windows console encoding issues
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    os.system("chcp 65001 >nul")

# Direct connector imports (no InsightOperator)
from connectors.telegram_connector import TelegramConnector
from connectors.rss_connector import RssConnector
from config.config_manager import ConfigManager
from logs.core.logger_config import get_component_logger

class InsightExpressDailyFixed:
    """
    Direct connector approach for multi-day intelligence briefings with robust error handling
    """
    
    def __init__(self):
        """Initialize the daily briefings engine"""
        print("🚀 INSIGHT Express Daily - Fixed Direct Connector Engine")
        
        # Initialize Gemini
        self.gemini_client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )
        
        # Initialize config and logger
        self.config_manager = ConfigManager()
        self.logger = get_component_logger('daily_briefings')
        
        # Direct connector instances
        self.telegram_connector = None
        self.rss_connector = None
        
        print("✅ Daily briefings engine ready")
    
    async def setup_connectors(self) -> bool:
        """Setup connectors directly using the test file approach"""
        print("🔧 Setting up connectors directly...")
        
        config = self.config_manager.load_config()
        telegram_setup = False
        rss_setup = False
        
        # Setup Telegram connector
        try:
            telegram_config = self.config_manager.get_platform_config(config, 'telegram')
            if telegram_config and telegram_config.get('enabled', False):
                channels = telegram_config.get('channels', [])
                if channels:
                    print(f"📱 Setting up Telegram ({len(channels)} channels)...")
                    self.telegram_connector = TelegramConnector()
                    
                    if self.telegram_connector.setup_connector():
                        await self.telegram_connector.connect()
                        telegram_setup = True
                        print("  ✅ Telegram connector ready")
                    else:
                        print("  ❌ Telegram setup failed")
                else:
                    print("  ⚠️ No Telegram channels configured")
            else:
                print("  ⚠️ Telegram not enabled")
        except Exception as e:
            print(f"  ❌ Telegram setup error: {e}")
        
        # Setup RSS connector
        try:
            rss_config = self.config_manager.get_platform_config(config, 'rss')
            if rss_config and rss_config.get('enabled', False):
                feeds = rss_config.get('feeds', [])
                if feeds:
                    print(f"📰 Setting up RSS ({len(feeds)} feeds)...")
                    self.rss_connector = RssConnector()
                    
                    if self.rss_connector.setup_connector():
                        await self.rss_connector.connect()
                        rss_setup = True
                        print("  ✅ RSS connector ready")
                    else:
                        print("  ❌ RSS setup failed")
                else:
                    print("  ⚠️ No RSS feeds configured")
            else:
                print("  ⚠️ RSS not enabled")
        except Exception as e:
            print(f"  ❌ RSS setup error: {e}")
        
        overall_success = telegram_setup or rss_setup
        if overall_success:
            connectors = []
            if telegram_setup: connectors.append("Telegram")
            if rss_setup: connectors.append("RSS")
            print(f"✅ Connectors ready: {', '.join(connectors)}")
        else:
            print("❌ No connectors available")
        
        return overall_success
    
    def generate_date_range(self, days_back: int) -> List[date]:
        """Generate date range: N days back + today"""
        today = date.today()
        dates = []
        
        # Add historical days
        for i in range(days_back, 0, -1):
            dates.append(today - timedelta(days=i))
        
        # Add today
        dates.append(today)
        
        return dates
    
    def _safe_str(self, value: any, default: str = "Unknown") -> str:
        """Safely convert any value to string, handling None cases"""
        if value is None:
            return default
        if isinstance(value, str):
            return value
        try:
            return str(value)
        except:
            return default
    
    def _safe_content_preview(self, content: any, max_length: int = 600) -> str:
        """Safely create content preview, handling None and various types"""
        if content is None:
            return "No content available"
        
        content_str = self._safe_str(content, "No content available")
        
        if len(content_str) > max_length:
            return content_str[:max_length] + "..."
        return content_str
    
    def _safe_timestamp(self, date_obj: any) -> str:
        """Safely format timestamp, handling None and various date formats"""
        if date_obj is None:
            return "Unknown time"
        
        try:
            if isinstance(date_obj, datetime):
                return date_obj.strftime('%H:%M')
            elif isinstance(date_obj, str):
                # Try to parse string date
                parsed_date = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
                return parsed_date.strftime('%H:%M')
            else:
                return "Unknown time"
        except:
            return "Unknown time"
    
    async def collect_daily_posts(self, target_date: date) -> List[Dict[str, Any]]:
        """
        Collect posts for a specific date using direct connector approach
        """
        print(f"📡 Collecting posts for {target_date.strftime('%Y-%m-%d')}...")
        
        all_posts = []
        config = self.config_manager.load_config()
        
        # Calculate date boundaries for filtering
        start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = start_of_day + timedelta(days=1)
        
        # Collect Telegram posts
        if self.telegram_connector:
            telegram_config = self.config_manager.get_platform_config(config, 'telegram')
            channels = telegram_config.get('channels', [])
            print(f"  📱 Scanning {len(channels)} Telegram channels...")
            
            for channel in channels:
                try:
                    # Fetch posts (limit 10 as requested)
                    posts = await self.telegram_connector.fetch_posts(channel, 10)
                    
                    # Filter by target date
                    daily_posts = []
                    for post in posts:
                        post_date = post.get('date')
                        if post_date and isinstance(post_date, datetime):
                            # Ensure timezone awareness
                            if post_date.tzinfo is None:
                                post_date = post_date.replace(tzinfo=timezone.utc)
                            
                            # Check if post is from target date
                            if start_of_day <= post_date < end_of_day:
                                # Add metadata for daily processing with safe defaults
                                post['collection_source'] = 'telegram'
                                post['collection_channel'] = self._safe_str(channel)
                                post['target_date'] = target_date.isoformat()
                                # Ensure essential fields are not None
                                post['content'] = self._safe_str(post.get('content'), "No content")
                                post['title'] = self._safe_str(post.get('title'), "No title")
                                daily_posts.append(post)
                    
                    all_posts.extend(daily_posts)
                    print(f"    📋 @{channel}: {len(daily_posts)} posts")
                    
                except Exception as e:
                    print(f"    ❌ @{channel}: Failed - {e}")
        
        # Collect RSS posts
        if self.rss_connector:
            rss_config = self.config_manager.get_platform_config(config, 'rss')
            feeds = rss_config.get('feeds', [])
            print(f"  📰 Scanning {len(feeds)} RSS feeds...")
            
            for feed_url in feeds:
                try:
                    # Fetch posts (limit 20 as requested)
                    posts = await self.rss_connector.fetch_posts(feed_url, 20)
                    
                    # Filter by target date
                    daily_posts = []
                    for post in posts:
                        post_date = post.get('date')
                        if post_date and isinstance(post_date, datetime):
                            # Ensure timezone awareness
                            if post_date.tzinfo is None:
                                post_date = post_date.replace(tzinfo=timezone.utc)
                            
                            # Check if post is from target date
                            if start_of_day <= post_date < end_of_day:
                                # Add metadata for daily processing with safe defaults
                                post['collection_source'] = 'rss'
                                post['collection_feed'] = self._extract_feed_name(feed_url)
                                post['collection_feed_url'] = self._safe_str(feed_url)
                                post['target_date'] = target_date.isoformat()
                                # Ensure essential fields are not None
                                post['content'] = self._safe_str(post.get('content'), "No content")
                                post['title'] = self._safe_str(post.get('title'), "No title")
                                daily_posts.append(post)
                    
                    all_posts.extend(daily_posts)
                    feed_name = self._extract_feed_name(feed_url)
                    print(f"    📋 {feed_name}: {len(daily_posts)} posts")
                    
                except Exception as e:
                    print(f"    ❌ {feed_url}: Failed - {e}")
        
        total_posts = len(all_posts)
        print(f"  ✅ {target_date.strftime('%Y-%m-%d')}: {total_posts} posts collected")
        
        return all_posts
    
    def _extract_feed_name(self, feed_url: str) -> str:
        """Extract readable name from feed URL"""
        if not feed_url:
            return "Unknown Feed"
        
        if 'simonwillison' in feed_url:
            return "Simon Willison's Weblog"
        elif 'localllama' in feed_url:
            return "LocalLLaMA Newsletter"
        elif 'reddit.com/r/LocalLLaMA' in feed_url:
            return "r/LocalLLaMA"
        else:
            try:
                return feed_url.split('/')[2] if '/' in feed_url else feed_url
            except:
                return "Unknown Feed"
    
    async def process_daily_with_gemini(self, posts: List[Dict[str, Any]], target_date: date) -> str:
        """
        Process daily posts with Gemini AI with robust error handling
        """
        date_formatted = target_date.strftime('%B %d, %Y')
        total_count = len(posts)
        
        print(f"  🧠 Processing {date_formatted} with Gemini ({total_count} posts)...")
        
        if total_count == 0:
            return self._generate_empty_daily_briefing(date_formatted)
        
        try:
            # Count by source
            telegram_posts = [p for p in posts if p.get('collection_source') == 'telegram']
            rss_posts = [p for p in posts if p.get('collection_source') == 'rss']
            
            formatted_content = self._format_posts_for_gemini(posts, date_formatted)
            
            prompt = f"""
You are an expert intelligence analyst creating a focused daily briefing for {date_formatted}.
You have {total_count} posts from this specific day ({len(telegram_posts)} Telegram, {len(rss_posts)} RSS).

DAILY ANALYSIS MISSION:
Create a comprehensive single-day intelligence briefing that captures what happened on {date_formatted}.

ANALYSIS REQUIREMENTS:
1. **Daily Focus**: What specifically happened on {date_formatted}?
2. **Source Attribution**: Include exact quotes with source attribution
3. **Importance Ranking**: Rate stories 1-10 for their significance
4. **Key Insights**: What should someone know about this day?
5. **Timeline Context**: Note any connections to broader trends

OUTPUT FORMAT - Daily Intelligence Briefing:
```html
<div class="daily-briefing">
    <h1>📅 Daily Intelligence Briefing</h1>
    <h2>{date_formatted}</h2>
    <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Posts Analyzed: {total_count} | Focus: Single Day Analysis</p>
    
    <div class="day-summary">
        <h2>📋 Day Overview</h2>
        <p><strong>Intelligence Summary:</strong> [1-2 sentences about what defined this day]</p>
        <ul>
            <li><strong>Total Activity:</strong> {total_count} posts</li>
            <li><strong>Telegram Posts:</strong> {len(telegram_posts)}</li>
            <li><strong>RSS Posts:</strong> {len(rss_posts)}</li>
            <li><strong>Primary Topics:</strong> [List main topics of the day]</li>
        </ul>
    </div>
    
    <div class="top-stories">
        <h2>🔥 Top Stories of {date_formatted}</h2>
        
        <div class="story">
            <h3>Story Title (Importance: X/10)</h3>
            <p class="story-context"><strong>Why This Mattered Today:</strong> [Explain significance for this specific day]</p>
            <p class="summary">[Brief summary]</p>
            <div class="sources">
                <h4>📋 Source Evidence:</h4>
                <blockquote class="source-quote">
                    <p>"[Exact quote from source]"</p>
                    <cite>— Source Name, {date_formatted}</cite>
                </blockquote>
            </div>
        </div>
    </div>
    
    <div class="by-category">
        <h2>📂 Categories for {date_formatted}</h2>
        
        <div class="category">
            <h3>🤖 AI & Technology</h3>
            <div class="story">
                <h4>Story Title (Importance: X/10)</h4>
                <p>[Summary with daily context]</p>
                <blockquote class="source-quote">
                    <p>"[Supporting quote]"</p>
                    <cite>— Source, {date_formatted}</cite>
                </blockquote>
            </div>
        </div>
        
        <!-- Add other relevant categories -->
    </div>
    
    <div class="daily-insights">
        <h2>💡 Key Takeaways from {date_formatted}</h2>
        <div class="insight">
            <h3>Main Insight: [Key Point]</h3>
            <p>[Why this was important specifically on {date_formatted}]</p>
            <blockquote class="source-quote">
                <p>"[Supporting evidence]"</p>
                <cite>— Source Evidence from {date_formatted}</cite>
            </blockquote>
        </div>
    </div>
    
    <div class="daily-analysis">
        <h2>🔍 Analysis Notes</h2>
        <ul>
            <li><strong>Source Quality:</strong> [Assessment of sources for this day]</li>
            <li><strong>Coverage Patterns:</strong> [What topics dominated]</li>
            <li><strong>Notable Developments:</strong> [Significant announcements/events]</li>
            <li><strong>Forward Indicators:</strong> [Stories that might develop]</li>
        </ul>
    </div>
</div>
```

DAILY CONTENT FOR {date_formatted}:
{formatted_content}

Focus on what made {date_formatted} unique and significant. Generate the daily briefing now:
"""

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

            response_text = ""
            for chunk in self.gemini_client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                response_text += chunk.text
            
            print(f"  ✅ {date_formatted} analysis complete")
            return response_text
            
        except Exception as e:
            print(f"  ❌ {date_formatted} processing failed: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_error_daily_briefing(date_formatted, str(e))
    
    def _format_posts_for_gemini(self, posts: List[Dict[str, Any]], date_formatted: str) -> str:
        """Format posts for Gemini processing with robust error handling"""
        formatted = []
        
        for i, post in enumerate(posts):
            try:
                source_type = self._safe_str(post.get('collection_source'), 'unknown')
                
                if source_type == 'telegram':
                    channel = self._safe_str(post.get('collection_channel'), 'Unknown')
                    content = self._safe_str(post.get('content'), 'No content')
                    timestamp = self._safe_timestamp(post.get('date'))
                    
                    content_preview = self._safe_content_preview(content, 600)
                    
                    formatted.append(f"""
[TELEGRAM POST #{i+1} - {date_formatted}]
Channel: @{channel}
Time: {timestamp}
Content: "{content_preview}"
""")
                
                elif source_type == 'rss':
                    feed_name = self._safe_str(post.get('collection_feed'), 'Unknown')
                    title = self._safe_str(post.get('title'), 'No Title')
                    content = self._safe_str(post.get('content'), 'No content')
                    timestamp = self._safe_timestamp(post.get('date'))
                    
                    content_preview = self._safe_content_preview(content, 600)
                    
                    formatted.append(f"""
[RSS POST #{i+1} - {date_formatted}]
Feed: {feed_name}
Title: "{title}"
Time: {timestamp}
Content: "{content_preview}"
""")
                
                else:
                    # Handle unknown source types
                    content = self._safe_str(post.get('content'), 'No content')
                    content_preview = self._safe_content_preview(content, 600)
                    
                    formatted.append(f"""
[UNKNOWN POST #{i+1} - {date_formatted}]
Source: {source_type}
Content: "{content_preview}"
""")
                    
            except Exception as e:
                print(f"    ⚠️ Error formatting post #{i+1}: {e}")
                # Add a safe fallback for problematic posts
                formatted.append(f"""
[ERROR POST #{i+1} - {date_formatted}]
Error: Failed to format this post - {str(e)}
""")
        
        header = f"\n{'='*60}\nDAILY INTELLIGENCE FOR {date_formatted}\n{'='*60}\n"
        return header + "\n".join(formatted)
    
    def _generate_empty_daily_briefing(self, date_formatted: str) -> str:
        """Generate briefing for days with no content"""
        return f"""
<div class="daily-briefing">
    <h1>📅 Daily Intelligence Briefing</h1>
    <h2>{date_formatted}</h2>
    <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | No content found for this day</p>
    
    <div class="no-content">
        <h2>😴 Quiet Day</h2>
        <p>No posts found for {date_formatted} from your configured sources.</p>
        <div class="possible-reasons">
            <h3>Possible reasons:</h3>
            <ul>
                <li>Light activity on this day</li>
                <li>Weekend or holiday</li>
                <li>Sources were inactive</li>
                <li>Content fell outside the 24-hour window</li>
                <li>Network connectivity issues during collection</li>
            </ul>
        </div>
    </div>
</div>
"""
    
    def _generate_error_daily_briefing(self, date_formatted: str, error: str) -> str:
        """Generate error briefing for failed days"""
        return f"""
<div class="daily-briefing">
    <h1>📅 Daily Intelligence Briefing</h1>
    <h2>{date_formatted}</h2>
    <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Processing error</p>
    
    <div class="error">
        <h2>❌ Analysis Error for {date_formatted}</h2>
        <p>Failed to process intelligence for this day: {error}</p>
        <div class="troubleshooting">
            <h3>Troubleshooting:</h3>
            <ul>
                <li>Check Gemini API key and quota</li>
                <li>Verify network connectivity</li>
                <li>Review source configuration</li>
                <li>Check console output for detailed errors</li>
            </ul>
        </div>
    </div>
</div>
"""
    
    async def run_multi_day_briefings(self, days_back: int = 1) -> Dict[str, str]:
        """
        Main entry point: Generate daily briefings for multiple days
        """
        print(f"🎯 Starting Multi-Day Intelligence Briefings ({days_back} days + today)")
        print("=" * 70)
        
        # Setup connectors first
        if not await self.setup_connectors():
            print("❌ No connectors available. Exiting.")
            return {}
        
        # Generate date range
        dates_to_process = self.generate_date_range(days_back)
        print(f"📅 Processing dates: {[d.strftime('%Y-%m-%d') for d in dates_to_process]}")
        print("=" * 70)
        
        daily_briefings = {}
        
        for i, target_date in enumerate(dates_to_process):
            date_str = target_date.strftime('%Y-%m-%d')
            date_formatted = target_date.strftime('%B %d, %Y')
            
            print(f"\n[{i+1}/{len(dates_to_process)}] Processing {date_formatted}...")
            
            try:
                # Step 1: Collect daily posts
                daily_posts = await self.collect_daily_posts(target_date)
                
                # Step 2: Process with Gemini
                briefing_html = await self.process_daily_with_gemini(daily_posts, target_date)
                
                # Step 3: Save daily briefing
                filename = f"daily_briefing_{date_str}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self._wrap_daily_html(briefing_html, date_formatted))
                
                daily_briefings[date_str] = briefing_html
                print(f"  ✅ Saved: {filename}")
                
            except Exception as e:
                print(f"  ❌ Failed to process {date_formatted}: {e}")
                import traceback
                traceback.print_exc()
                error_briefing = self._generate_error_daily_briefing(date_formatted, str(e))
                daily_briefings[date_str] = error_briefing
        
        # Generate master index
        self._generate_master_index(dates_to_process, daily_briefings)
        
        # Cleanup connectors
        await self.cleanup_connectors()
        
        print("\n" + "=" * 70)
        print(f"🎉 Multi-Day Briefings Complete!")
        print(f"📂 Generated {len(daily_briefings)} daily briefings")
        print("📋 Check 'briefings_index.html' for navigation")
        
        return daily_briefings
    
    async def cleanup_connectors(self):
        """Cleanup connector resources"""
        if self.telegram_connector:
            try:
                await self.telegram_connector.disconnect()
                print("✅ Telegram connector disconnected")
            except Exception as e:
                print(f"❌ Telegram cleanup error: {e}")
        
        if self.rss_connector:
            try:
                await self.rss_connector.disconnect()
                print("✅ RSS connector disconnected")
            except Exception as e:
                print(f"❌ RSS cleanup error: {e}")
    
    def _generate_master_index(self, dates: List[date], briefings: Dict[str, str]):
        """Generate master index HTML file"""
        index_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>INSIGHT Express - Daily Briefings Index</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .briefing-list {{ list-style: none; padding: 0; }}
        .briefing-item {{ margin: 15px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db; }}
        .briefing-link {{ text-decoration: none; color: #2c3e50; font-weight: bold; }}
        .briefing-link:hover {{ color: #3498db; }}
        .date {{ font-size: 1.2em; margin-bottom: 5px; }}
        .meta {{ color: #666; font-size: 0.9em; }}
        .stats {{ background: #e8f4f8; padding: 15px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📅 INSIGHT Express - Daily Briefings</h1>
        <p>Multi-Day Intelligence Analysis Dashboard</p>
        <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Fixed Error Handling</p>
    </div>
    
    <div class="stats">
        <h2>📊 Briefing Statistics</h2>
        <ul>
            <li><strong>Total Days:</strong> {len(dates)}</li>
            <li><strong>Date Range:</strong> {dates[0].strftime('%B %d')} - {dates[-1].strftime('%B %d, %Y')}</li>
            <li><strong>Briefings Generated:</strong> {len(briefings)}</li>
            <li><strong>Collection Limits:</strong> Telegram: 10 posts/channel, RSS: 20 posts/feed</li>
            <li><strong>Error Handling:</strong> Robust None-safe processing</li>
        </ul>
    </div>
    
    <h2>📋 Daily Briefings</h2>
    <ul class="briefing-list">
"""
        
        for target_date in reversed(dates):  # Most recent first
            date_str = target_date.strftime('%Y-%m-%d')
            date_formatted = target_date.strftime('%B %d, %Y')
            is_today = target_date == date.today()
            
            status = "✅" if date_str in briefings else "❌"
            today_indicator = " (Today)" if is_today else ""
            
            index_html += f"""
        <li class="briefing-item">
            <div class="date">
                <a href="daily_briefing_{date_str}.html" class="briefing-link">
                    {status} {date_formatted}{today_indicator}
                </a>
            </div>
            <div class="meta">Click to view detailed daily intelligence briefing</div>
        </li>
"""
        
        index_html += """
    </ul>
    
    <div class="footer" style="text-align: center; margin-top: 40px; color: #666;">
        <p>INSIGHT Express - Fixed Error Handling Engine</p>
    </div>
</body>
</html>
"""
        
        with open("briefings_index.html", 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        print("📋 Master index saved: briefings_index.html")
    
    def _wrap_daily_html(self, content: str, date_formatted: str) -> str:
        """Wrap daily briefing in HTML"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Briefing - {date_formatted}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f8f9fa; }}
        .daily-briefing {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 30px; font-style: italic; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 15px; }}
        h3 {{ color: #7f8c8d; }}
        
        .day-summary {{ background: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .top-stories {{ background: #fff5f5; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #e74c3c; }}
        .story {{ margin: 15px 0; padding: 15px; background: white; border-radius: 6px; border-left: 3px solid #3498db; }}
        .source-quote {{ background: #f7f7f7; border-left: 4px solid #34495e; padding: 15px; margin: 10px 0; font-style: italic; }}
        .source-quote cite {{ font-size: 0.9em; color: #7f8c8d; font-weight: bold; }}
        .story-context {{ background: #e8f5e8; padding: 10px; border-radius: 6px; margin: 10px 0; }}
        .daily-insights {{ background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #27ae60; }}
        .daily-analysis {{ background: #f0f0f0; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #95a5a6; }}
        .no-content, .error {{ text-align: center; padding: 40px; background: #f8f9fa; border-radius: 8px; }}
        .possible-reasons, .troubleshooting {{ text-align: left; margin-top: 15px; }}
        
        .nav-links {{ text-align: center; margin: 20px 0; }}
        .nav-links a {{ display: inline-block; margin: 0 10px; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 6px; }}
        .nav-links a:hover {{ background: #2980b9; }}
    </style>
</head>
<body>
    <div class="nav-links">
        <a href="briefings_index.html">← Back to Index</a>
    </div>
    
    {content}
    
    <div class="nav-links">
        <a href="briefings_index.html">← Back to Index</a>
    </div>
</body>
</html>
"""

# Main execution
async def main():
    """Main entry point for fixed multi-day briefings"""
    print("🚀 INSIGHT Express Daily - Fixed Error Handling Engine")
    print("=" * 70)
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("   PowerShell: $env:GEMINI_API_KEY='your_api_key'")
        return
    
    # Get user input for number of days
    try:
        days_input = input("Enter number of historical days (default 1): ").strip()
        days_back = int(days_input) if days_input else 1
    except ValueError:
        days_back = 1
    
    try:
        engine = InsightExpressDailyFixed()
        briefings = await engine.run_multi_day_briefings(days_back)
        
        print(f"\n🎉 Complete! Generated briefings for {len(briefings)} days")
        print("📂 Files created:")
        print("   • briefings_index.html (master navigation)")
        for date_str in briefings.keys():
            print(f"   • daily_briefing_{date_str}.html")
        
        print(f"\n📊 Collection Settings:")
        print("   • Telegram: 10 posts per channel")
        print("   • RSS: 20 posts per feed")
        print("   • Method: Direct connector approach")
        print("   • Error Handling: Robust None-safe processing")
        
    except Exception as e:
        print(f"💥 Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())