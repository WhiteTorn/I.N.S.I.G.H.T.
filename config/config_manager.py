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
    
    def validate_config(self):
        """Validates the loaded configuration dictionary."""
        errors = []

        # Check if the config is a dictionary
        if not isinstance(self.config, dict):
            errors.append("the config is not a valid dictionary.")
            return False, errors
        
        # Check required keys
        required_keys = ['metadata', 'sources']
        for key in required_keys:
            if key not in self.config:
                errors.append(f"The key '{key}' is missing from the config.")

        # Check data types
        if "metadata" in self.config:
            if not isinstance(self.config['metadata'], dict):
                errors.append("The metadata key must be a dictionary.")
            else:
                # Check metadata fields
                metadata = self.config['metadata']
                required_metadata_fields = ['name', 'description', 'version']
                for field in required_metadata_fields:
                    if field not in metadata:
                        errors.append(f"The field '{field}' is missing from the metadata.")
                    # also check the data types of fields
                    
        if "sources" in self.config:
            if not isinstance(self.config['sources'], list):
                errors.append("The sources key must be a list.")
            # check data types of each source in the list

        # Return validation result
        if len(errors) > 0:
            return False, errors
        
        return True, "The config is valid."


config_manager = ConfigManager()

config_manager.load_config()
config_manager.print_config()
print(config_manager.validate_config())

