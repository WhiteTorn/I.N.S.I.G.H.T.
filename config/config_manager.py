import os
import json

class ConfigManager:
    def __init__(self):
        self.config = {}
        self.config_path = os.path.join(os.path.dirname(__file__), 'sources.json')

    def load_config(self):
        with open(self.config_path, 'r') as file:
            self.config = json.load(file)
            
    def print_config(self):
        with open(self.config_path, 'r') as file:
            self.config = json.load(file)
            pretty = json.dumps(self.config, indent=4)
            print(pretty)

config_manager = ConfigManager()
config_manager.print_config()

