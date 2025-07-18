from insight_core.config.config_manager import ConfigManager
from insight_core.engines.mark_i_foundation_engine import MarkIFoundationEngine

class InsightBridge:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config_manager.load_config()
        self.engine = MarkIFoundationEngine(self.config_manager)

    def get_sources(self):
        return self.config_manager.config
    # self.config_manager.get_config
    
    def get_enabled_sources(self):
        return self.config_manager.get_enabled_sources(self.config_manager.config)

    def update_config(self, new_config):
        return self.config_manager.update_config(new_config)
    
    async def daily_briefing(self, day):
        return await self.engine.get_daily_briefing(day)

