from ..connectors import create_connector
from ..processors.ai.gemini_processor import GeminiProcessor
from ..processors.utils.post_utils import PostSorter
from datetime import datetime
from typing import Dict, Any, List

class MarkIFoundationEngine:
    """
    I.N.S.I.G.H.T. Mark I - Foundation Engine
    
    Purpose: Basic briefing generation
    
    Capabilities:
    - Fetch posts from Multi Source
    - Sort posts by date
    - Generate simple briefing

    FSG - Foundate Solid Ground.
    
    Upgrade Path: Mark II Synthesis Engine
    """
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.config = self.config_manager.config
        self.gemini = GeminiProcessor()
        

    async def get_daily_briefing(self, day):
        "Generate Daily Briefing"
        try:

            all_posts = []
            # Step 1: Get Target Date
            try:
                target_date = datetime.strptime(day, "%Y-%m-%d")
            except ValueError:
                return {"Error": f"invalid date format {type(day)}"}
            except Exception as e:
                return {"Error": f"{e}"}
            
            # Step 2: Get Enabled Platforms
            try:
                enabled = self.config_manager.get_enabled_sources(self.config)
                platforms = list(enabled.keys())

                for platform in platforms:
                    print(platform) # rss
                    # Let's print name of the connector file.
                    # print(f"{platform}_connector.py")
                    connector = create_connector(platform)
                    if connector:
                        print(f"✅ {platform} connector ready")
                        # connector_config = self.config_manager.get_platform_config(self.config, platform)
                        sources = self.config_manager.get_active_sources(self.config, platform)
                        connector.setup_connector()
                        await connector.connect()

                        for source in sources:
                            posts = await connector.fetch_posts(source, 10)
                            all_posts.extend(posts)
                            
                        await connector.disconnect()
                        
                    else:
                        print(f"❌ Failed to create {platform} connector")
                    # Get Sources
                    # Connect Connectors
            except Exception as e:
                return {"Error": f"{e}"}
                
            # Step 3: Filter by day
            if not all_posts:
                return {"error": "No posts fetched from any source"}
            
            try:
                sorted_posts = PostSorter.sort_posts_by_date(all_posts)

                day_posts = PostSorter.get_posts_for_specific_day(sorted_posts, target_date)

                if not day_posts:
                    return {"error": f"No posts found for date {day}"}
                
            except Exception as e:
                return {"error": f"Date filtering error: {e}"}

            # Step 4: Generate briefing
            try:
                if self.gemini.setup_processor():
                    await self.gemini.connect()
                    brief = await self.gemini.daily_briefing(day_posts)
                    await self.gemini.disconnect()

                    return {
                        "success": True,
                        "briefing": brief,
                        "date": day,
                        "posts_processed": len(day_posts),
                        "total_posts_fetched": len(day_posts),
                        "posts": day_posts  # Add the actual posts for the specific day
                    }
                else:
                    return {
                        "error": "AI processor setup failed: GEMINI_API_KEY missing or invalid. Set GEMINI_API_KEY in your environment (.env) and restart the server."
                    }
                
            except Exception as e:
                return {"error": f"Briefing Generation Error: {e}"}
        
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

    async def get_daily_briefing_with_topics(self, day: str, include_unreferenced: bool = True) -> Dict[str, Any]:
        """
        Generate Topic-based Briefing.
        - LLM returns only numeric post IDs per topic (1-based as Post 1, Post 2, ...), we map them to posts.
        - Always produce a topic-based briefing when possible; fallback to standard briefing if enhanced fails.
        - No token cost returned.
        """
        try:
            all_posts: List[Dict[str, Any]] = []
            try:
                target_date = datetime.strptime(day, "%Y-%m-%d")
            except ValueError:
                return {"error": f"invalid date format {type(day)}"}
            except Exception as e:
                return {"error": f"{e}"}

            try:
                enabled = self.config_manager.get_enabled_sources(self.config)
                platforms = list(enabled.keys())

                for platform in platforms:
                    connector = create_connector(platform)
                    if connector:
                        connector_config = self.config_manager.get_platform_config(self.config, platform)
                        sources = self.config_manager.get_active_sources(self.config, platform)
                        print(sources)
                        connector.setup_connector()
                        await connector.connect()
                        for source in sources:
                            posts = await connector.fetch_posts(source, 10)
                            all_posts.extend(posts)
                        await connector.disconnect()
            except Exception as e:
                return {"error": f"{e}"}

            if not all_posts:
                return {"error": "No posts fetched from any source"}

            try:
                sorted_posts = PostSorter.sort_posts_by_date(all_posts)
                day_posts = PostSorter.get_posts_for_specific_day(sorted_posts, target_date)
                if not day_posts:
                    return {"error": f"No posts found for date {day}"}
            except Exception as e:
                return {"error": f"Date filtering error: {e}"}

            # Build numeric ID mapping: Post 1, Post 2, ... in chronological order
            indexed_posts: Dict[str, Dict[str, Any]] = {}
            for idx, post in enumerate(day_posts, start=1):
                post_id = str(idx)  # numeric ID as string for transport simplicity
                # attach post_id into the post copy
                post_copy = dict(post)
                post_copy["post_id"] = post_id
                indexed_posts[post_id] = post_copy

            try:
                if self.gemini.setup_processor():
                    await self.gemini.connect()
                    enhanced = await self.gemini.topic_briefing_with_numeric_ids(day_posts)
                    await self.gemini.disconnect()

                    if isinstance(enhanced, dict) and "error" not in enhanced:
                        # topics: [{ id, title, summary, post_ids: ["1","2",...] }]
                        topics = enhanced.get("topics", [])

                        # Validate post_ids and collect unreferenced
                        referenced = set()
                        for t in topics:
                            ids = [pid for pid in t.get("post_ids", []) if pid in indexed_posts]
                            t["post_ids"] = ids
                            referenced.update(ids)

                        unreferenced_ids = []
                        if include_unreferenced:
                            all_ids = set(indexed_posts.keys())
                            unreferenced_ids = sorted(all_ids - referenced, key=lambda x: int(x))

                        return {
                            "success": True,
                            "enhanced": True,
                            # For topic-based flow, we expose topics; the overall daily briefing text is optional here
                            "briefing": enhanced.get("daily_briefing", ""),
                            "topics": topics,
                            "unreferenced_posts": unreferenced_ids,
                            "posts": indexed_posts,
                            "date": day,
                            "posts_processed": len(day_posts),
                            "total_posts_fetched": len(day_posts)
                        }
                    else:
                        # Fallback to standard briefing
                        if self.gemini.setup_processor():
                            await self.gemini.connect()
                            brief = await self.gemini.daily_briefing(day_posts)
                            await self.gemini.disconnect()
                        else:
                            return {"error": "AI processor setup failed"}
                        return {
                            "success": True,
                            "enhanced": False,
                            "briefing": brief,
                            "topics": [],
                            "unreferenced_posts": list(indexed_posts.keys()) if include_unreferenced else [],
                            "posts": indexed_posts,
                            "date": day,
                            "posts_processed": len(day_posts),
                            "total_posts_fetched": len(day_posts)
                        }
                else:
                    return {"error": "AI processor setup failed: GEMINI_API_KEY missing or invalid. Set GEMINI_API_KEY in your environment (.env) and restart the server."}
            except Exception as e:
                return {"error": f"Briefing Generation Error: {e}"}

        except Exception as e:
            return {"error": f"Unexpected error: {e}"}


