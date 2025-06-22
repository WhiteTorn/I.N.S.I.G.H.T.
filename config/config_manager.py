import os
import json

class ConfigManager:
    def __init__(self):
        self.config = {}
        self.config_path = os.path.join(os.path.dirname(__file__), 'sources.json')
        # if config_path can't be found, how __init__ should manage it?
        # is not it is better to have config_path in the load config method and assign from the load_config to init?
        # because load_config has error handling and everything needed?
        # what you think about it?

    def load_config(self):
        """
        Loads the config from the config file.
        If the file does not exist, error will be raised.
        If the file is not a valid JSON file, error will be raised.
        """
        try:
            with open(self.config_path, 'r') as file:
                self.config = json.load(file)
        except FileNotFoundError:
            print(f"Error: The file {self.config_path} does not exist.")
            self.config = {}
        except json.JSONDecodeError:
            print(f"Error: The file {self.config_path} is not a valid JSON file.")
            self.config = {}
        except Exception as e:
            print(f"Error: An unexpected error occurred while loading the config file: {e}")
            self.config = {}
            
    def print_config(self):
        try:
            with open(self.config_path, 'r') as file:
                self.config = json.load(file) # you can't print the config pretty because it has no indent.
                pretty = json.dumps(self.config, indent=4)
                print(pretty)
        except FileNotFoundError:
            print(f"Error: The file {self.config_path} does not exist.")
            self.config = {}
        except json.JSONDecodeError:
            print(f"Error: The file {self.config_path} is not a valid JSON file.")
            self.config = {}
        except Exception as e:
            print(f"Error: An unexpected error occurred while printing the config file: {e}")
            self.config = {}

    def get_config(self):
        """Returns the loaded configuration dictionary."""
        return self.config


config_manager = ConfigManager()
config_manager.print_config()

