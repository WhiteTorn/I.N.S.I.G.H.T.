from insight_core.config.config_manager import ConfigManager

class InsightBridge:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()

    def get_sources(self):
        return self.config
    
    def get_enabled_sources(self):
        return self.config_manager.get_enabled_sources(self.config)
