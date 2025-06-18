"""
I.N.S.I.G.H.T. Console Renderer

This module handles all console/terminal output for the I.N.S.I.G.H.T. platform.
It provides clean, formatted console output for reports, briefings, and feed analysis.

Supports rendering for:
- Telegram posts
- RSS/Atom feeds 
- YouTube transcripts
- Reddit posts and comments
- Feed analysis information
"""

from datetime import datetime


class ConsoleRenderer:
    """
    Console renderer for I.N.S.I.G.H.T. intelligence reports.
    
    Provides formatted terminal output for all platform data types
    with enhanced support for RSS/Atom feeds, YouTube transcripts,
    and Reddit content.
    """
    
    @staticmethod
    def render_report_to_console(posts: list, title: str):
        """A generic renderer for a list of posts, supporting Telegram, RSS, and YouTube content."""
        print("\n" + "#"*25 + f" I.N.S.I.G.H.T. REPORT: {title.upper()} " + "#"*25)
        if not posts:
            print("\nNo displayable posts found for this report.")
        
        for i, post_data in enumerate(posts):
            media_count = len(post_data.get('media_urls', []))
            media_indicator = f"[+{media_count} MEDIA]" if media_count > 0 else ""
            
            # Handle platform-specific fields
            if post_data.get('platform') == 'youtube':
                video_title = post_data.get('title', 'Unknown Video')
                channel_name = post_data.get('author', 'Unknown Channel')
                view_count = post_data.get('view_count', 0)
                
                print(f"\n--- Video {i+1}/{len(posts)} | {video_title} ---")
                print(f"📺 Channel: {channel_name} | 📅 Date: {post_data.get('date', 'Unknown').strftime('%Y-%m-%d %H:%M:%S') if post_data.get('date') else 'Unknown'}")
                print(f"👀 Views: {view_count:,} | Video ID: {post_data.get('url', 'Unknown')} {media_indicator}")
                print(f"\n🎬 TRANSCRIPT:")
                
            elif post_data.get('platform') == 'rss':
                title_field = post_data.get('title', 'No title')
                feed_title = post_data.get('feed_title', 'Unknown Feed')
                feed_type = post_data.get('feed_type', 'rss').upper()
                categories = post_data.get('categories', [])
                
                print(f"\n--- Post {i+1}/{len(posts)} | {title_field} ---")
                print(f"Feed: {feed_title} ({feed_type}) | Date: {post_data.get('date', post_data.get('date', 'Unknown')).strftime('%Y-%m-%d %H:%M:%S') if post_data.get('date') or post_data.get('date') else 'Unknown'} {media_indicator}")
                if categories:
                    print(f"Categories: {', '.join(categories)}")
            else:
                # Telegram and other platforms
                print(f"\n--- Post {i+1}/{len(posts)} | ID: {post_data.get('id', post_data.get('url', 'Unknown'))} | Date: {post_data.get('date', post_data.get('date', 'Unknown')).strftime('%Y-%m-%d %H:%M:%S') if post_data.get('date') or post_data.get('date') else 'Unknown'} {media_indicator} ---")
            
            # Display content (text or transcript)
            content = post_data.get('content', post_data.get('text', 'No content available'))
            print(content)
            
            # Display link
            link = post_data.get('url', post_data.get('link', 'No link available'))
            print(f"🔗 Link: {link}")

            if post_data.get('media_urls'):
                print("📎 Media Links:")
                for url in post_data['media_urls']:
                    print(f"  - {url}")
            print("-" * 60)
        print("\n" + "#"*30 + " END OF REPORT " + "#"*30)

    @staticmethod
    def render_briefing_to_console(posts: list, title: str):
        """Renders a chronologically sorted briefing, supporting both platforms with categories."""
        print("\n" + "#"*25 + f" I.N.S.I.G.H.T. BRIEFING: {title.upper()} " + "#"*25)
        if not posts:
            print("\nNo intelligence gathered for this period.")
            print("\n" + "#"*30 + " END OF BRIEFING " + "#"*30)
            return

        posts_by_day = {}
        for post in posts:
            day_str = post['date'].strftime('%Y-%m-%d, %A')
            if day_str not in posts_by_day:
                posts_by_day[day_str] = []
            posts_by_day[day_str].append(post)
        
        for day, day_posts in sorted(posts_by_day.items()):
            print(f"\n\n{'='*25} INTEL FOR: {day} {'='*25}")
            for i, post_data in enumerate(day_posts):
                media_count = len(post_data.get('media_urls', []))
                media_indicator = f"[+{media_count} MEDIA]" if media_count > 0 else ""
                
                # Handle different source types
                if post_data.get('platform') == 'rss':
                    feed_title = post_data.get('feed_title', 'RSS Feed')
                    feed_type = post_data.get('feed_type', 'rss').upper()
                    categories = post_data.get('categories', [])
                    
                    print(f"\n--- [{post_data['date'].strftime('%H:%M:%S')}] From: {feed_title} ({feed_type}) {media_indicator} ---")
                    if categories:
                        print(f"Categories: {', '.join(categories)}")
                else:
                    print(f"\n--- [{post_data['date'].strftime('%H:%M:%S')}] From: @{post_data['source']} {media_indicator} ---")
                
                print(post_data['content'])
                print(f"Link: {post_data['url']}")

                if post_data.get('media_urls'):
                    print("Media Links:")
                    for url in post_data['media_urls']:
                        print(f"  - {url}")
                print("-" * 60)

        print("\n" + "#"*30 + " END OF BRIEFING " + "#"*30)

    @staticmethod
    def render_feed_info(feed_info: dict):
        """Render RSS/Atom feed analysis information with category insights."""
        print("\n" + "#"*25 + " RSS/ATOM FEED ANALYSIS " + "#"*25)
        
        if feed_info['status'] == 'error':
            print(f"❌ Error analyzing feed: {feed_info['error']}")
            return
        
        print(f"📰 Feed Title: {feed_info['title']}")
        print(f"🌐 URL: {feed_info['url']}")
        print(f"📝 Description: {feed_info['description']}")
        print(f"🔗 Website: {feed_info['link']}")
        print(f"🌍 Language: {feed_info['language']}")
        print(f"📊 Total Entries Available: {feed_info['total_entries']}")
        print(f"🔄 Feed Type: {feed_info['feed_type'].upper()}")
        print(f"🏷️  Categories Found: {feed_info['category_count']}")
        
        if feed_info.get('common_categories'):
            print(f"📂 Common Categories: {', '.join(feed_info['common_categories'][:10])}")  # Show first 10
            if len(feed_info['common_categories']) > 10:
                print(f"   ... and {len(feed_info['common_categories']) - 10} more")
        
        print(f"🕒 Last Updated: {feed_info['last_updated']}")
        print("\n" + "#"*30 + " END OF ANALYSIS " + "#"*30)

    @staticmethod
    def report_mission_outcome(posts_collected: int, sources_attempted: int, mission_name: str):
        """Report mission outcome with Citadel-enhanced feedback."""
        if posts_collected > 0:
            print(f"\n✅ Mission '{mission_name}' completed successfully!")
            print(f"   📊 Intelligence gathered: {posts_collected} posts")
            if sources_attempted > 1:
                print(f"   🎯 Sources processed: {sources_attempted}")
        elif sources_attempted > 0:
            print(f"\n⚠️  Mission '{mission_name}' completed with no intelligence gathered.")
            print(f"   🔍 This may indicate:")
            print(f"      • Sources are currently inaccessible")
            print(f"      • No content available in the specified timeframe")
            print(f"      • Network connectivity issues")
            print(f"   🛡️  Citadel Protection: System remained stable despite source failures")
        else:
            print(f"\n❌ Mission '{mission_name}' failed to initiate.")
            print(f"   🛡️  Citadel Protection: System protected from cascading failures")

    @staticmethod
    def display_mission_menu():
        """Display the mission selection menu."""
        print("\nChoose your mission:")
        print("\n--- TELEGRAM MISSIONS ---")
        print("1. Deep Scan (Get last N posts from one Telegram channel)")
        print("2. Historical Briefing (Get posts from the last N days from multiple Telegram channels)")
        print("3. End of Day Briefing (Get all of today's posts from multiple Telegram channels)")
        print("\n--- RSS/ATOM MISSIONS ---")
        print("4. RSS Feed Analysis (Analyze a single RSS/Atom feed)")
        print("5. RSS Single Feed Scan (Get N posts from a single RSS/Atom feed)")
        print("6. RSS Multi-Feed Scan (Get N posts from multiple RSS/Atom feeds)")
        print("\n--- YOUTUBE MISSIONS ---")
        print("7. YouTube Transcript (Get transcript from a single YouTube video)")
        print("8. YouTube Channel Transcripts (Get transcripts from the latest N videos in a YouTube channel)")
        print("9. YouTube Playlist Transcripts (Get transcripts from a YouTube playlist)")
        print("10. YouTube Search (Search for YouTube videos and extract their transcripts)")
        print("\n--- REDDIT MISSIONS ---")
        print("12. Reddit Post Analysis (Get single Reddit post with comments by URL)")
        print("13. Reddit Subreddit Explorer (Browse and select posts from subreddit)")
        print("14. Reddit Multi-Source Briefing (Get posts from multiple subreddits/URLs)")
        print("\n--- UNIFIED OUTPUT MISSIONS ---")
        print("11. JSON Export Test (Export sample data to test Mark III compatibility)")

    @staticmethod
    def display_output_format_menu():
        """Display the output format selection menu."""
        print("\nChoose your output format:")
        print("1. Console Only")
        print("2. HTML Dossier Only")
        print("3. JSON Export Only")
        print("4. Console + HTML")
        print("5. Console + JSON")
        print("6. HTML + JSON")
        print("7. All Formats (Console + HTML + JSON)")

    @staticmethod
    def display_startup_banner(available_connectors: list, global_timeout: int):
        """Display the I.N.S.I.G.H.T. startup banner."""
        print(f"\nI.N.S.I.G.H.T. Mark II (v2.4) - The Inquisitor - Citadel Edition - Operator Online.")
        print(f"Available connectors: {', '.join(available_connectors)}")
        print(f"🛡️  Citadel Protection: {global_timeout}s global timeout, bulletproof error handling") 