from ..connectors import create_connector
from ..processors.ai.gemini_processor import GeminiProcessor
from ..processors.utils.post_utils import PostSorter
from datetime import datetime

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
                        connector_config = self.config_manager.get_platform_config(self.config, platform)
                        sources = connector_config.get('sources', [])
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
                    return {"error": "Failed to setup connector"}
                
            except Exception as e:
                return {"error": f"Briefing Generation Error: {e}"}
        
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

