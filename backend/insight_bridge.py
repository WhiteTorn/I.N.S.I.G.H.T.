from insight_core.config.config_manager import ConfigManager

class InsightBridge:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config_manager.load_config()

    def get_sources(self):
        return self.config_manager.config
    
    def get_enabled_sources(self):
        return self.config_manager.get_enabled_sources(self.config_manager.config)

    def update_config(self, new_config):
        return self.config_manager.update_config(new_config)