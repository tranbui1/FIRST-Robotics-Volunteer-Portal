import json
import os

CONFIG_FILE = "config.json"

def load_config():
    """
    Load configuration data from JSON file.
    
    Reads the application configuration from config.json file if it exists,
    otherwise returns an empty dictionary for default initialization.
    
    Returns:
        - dict: Configuration dictionary with stored settings, or empty dict
               if config file doesn't exist or is invalid
               
    Usage:
        # Load existing config
        config = load_config()
        main_data_path = config.get('main_data_path', 'default/path.csv')
        
        # First run (no config file exists)
        config = load_config()  # Returns {}
        
        # Example config structure:
        # {
        #     "main_data_path": "/path/to/matching_data.csv",
        #     "role_link_path": "/path/to/role_links.csv"
        # }
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    """
    Save configuration data to JSON file.
    
    Writes the provided configuration dictionary to config.json file
    with pretty-printing (4-space indentation) for readability.
    
    Args:
        - config (dict): Configuration dictionary to persist to disk
        
    Usage:
        # Update and save config
        config = load_config()
        config['main_data_path'] = '/new/path/data.csv'
        config['role_link_path'] = '/new/path/links.csv'
        save_config(config)
        
        # Save new config from scratch
        new_config = {
            'main_data_path': '/uploads/match_data_abc123.csv',
            'role_link_path': '/uploads/role_links_def456.csv'
        }
        save_config(new_config)
    """
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)