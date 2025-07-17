from insight_core.config.config_manager import ConfigManager

class InsightBridge:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config_manager.load_config()

    def get_sources(self):
        return self.config_manager.config
    # self.config_manager.get_config
    
    def get_enabled_sources(self):
        return self.config_manager.get_enabled_sources(self.config_manager.config)

    def update_config(self, new_config):
        return self.config_manager.update_config(new_config)
    
    async def generate_daily_briefing(self, date_str: str, limit: int = 20) -> Dict[str, Any]:
        # Send Limit Data to post fetchers
        # They will fetch data from the enabled sources
        # They will sort by days and we will get briefing by day we have inputed.
        pass

