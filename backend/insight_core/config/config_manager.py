import os
import json
from typing import Dict, List, Tuple

class ConfigManager:
    def __init__(self):
        self.config = {}
        self.config_path = os.path.join(os.path.dirname(__file__), 'sources.json')
        # if config_path can't be found, how __init__ should manage it?
        # is not it is better to have config_path in the load config method and assign from the load_config to init?
        # because load_config has error handling and everything needed?
        # what you think about it?

    def load_config(self) -> Dict:
        """
        Loads the config from the config file.
        If the file does not exist, error will be raised.
        If the file is not a valid JSON file, error will be raised.
        """
        try:
            with open(self.config_path, 'r') as file:
                self.config = json.load(file)
                return self.config
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
    
    def validate_config(self, config: Dict) -> Tuple[bool, List[str]]:
        """Validates the loaded configuration dictionary."""
        errors = []

        # Check if the config is a dictionary
        if not isinstance(config, dict):
            errors.append("the config is not a valid dictionary.")
            return False, errors
        
        # Check required keys
        required_keys = ['metadata', 'platforms']
        for key in required_keys:
            if key not in config:
                errors.append(f"The key '{key}' is missing from the config.")

        # Check data types
        if "metadata" in config:
            if not isinstance(config['metadata'], dict):
                errors.append("The metadata key must be a dictionary.")
            else:
                # Check metadata fields
                metadata = config['metadata']
                required_metadata_fields = ['name', 'description', 'version']
                for field in required_metadata_fields:
                    if field not in metadata:
                        errors.append(f"The field '{field}' is missing from the metadata.")
                    # also check the data types of fields
                    
        if "platforms" in config:
            if not isinstance(config['platforms'], dict):
                errors.append("The platforms key must be a dictionary.")
            # check data types of each source in the list

        # Return validation result
        if len(errors) > 0:
            return False, errors
        
        return True, "The config is valid."

    def get_enabled_sources(self, config: Dict) -> Dict:
        """Returns a list of enabled sources from the config."""
        enabled_sources = {}
        for source in config['platforms']:
            if config['platforms'][source]['enabled']:
                # enabled_sources.append({f"{source}": config['platforms'][source]['sources']})
                enabled_sources[source] = config['platforms'][source]['sources']

        return enabled_sources

    def get_platform_config(self, config: Dict, platform: str) -> Dict:
        """Returns the config for a specific platform from the config."""
        try:
            return config['platforms'][platform]
        except KeyError as e:
            print(f"Error: The platform '{platform}' is not defined in the config: {e}")
            return None

    def _get_default_config(self) -> Dict:
        """Returns the default config."""
        return {
            "metadata": {
                "name": "Default Config",
                "description": "Default config description",
                "version": "1.0.0"
            },
            "platforms": {
                "telegram": {
                    "enabled": True,
                    "sources": ["durov"]
                },
                "rss": {
                    "enabled": True,
                    "sources": ["https://simonwillison.net/atom/everything/"]
                },
                "youtube": {
                    "enabled": True,
                    "sources": ["UCoryWpk4QVYKFCJul9KBdyw"]
                },
                "reddit": {
                    "enabled": True,
                    "sources": ["LocalLLaMA"]
                }
            }
        }

    def update_config(self, new_config: Dict) -> Dict:
        is_valid, errors = self.validate_config(new_config)
        if is_valid:
            try:
                self.config.update(new_config)
                self._save_config()
                return self.config
            except Exception as e:
                print(f"Can't update config, exception {e}")
                return None
        else:
            print(f"new config {new_config} is not valid configuration.")
            print(f"Validation errors: {errors}")
            return None

    def _save_config(self):
        with open(self.config_path, 'w') as file:
            json.dump(self.config, file, indent = 4)