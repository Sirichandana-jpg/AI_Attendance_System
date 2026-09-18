import yaml
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "configs", "config.yaml")

def load_config():
    with open(CONFIG_FILE, "r") as file:
        return yaml.safe_load(file)

def get_config_value(section, key, default=None):
    config = load_config()
    return config.get(section, {}).get(key, default)
