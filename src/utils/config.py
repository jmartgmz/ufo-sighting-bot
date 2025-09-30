"""
Configuration management utilities for the UFO Sighting Bot.
"""
import json
import os

CONFIG_FILE = "data/config.json"
REACTIONS_FILE = "data/reactions.json"

def load_config():
    """Load server configuration from JSON file."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    """Save server configuration to JSON file."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def load_reactions():
    """Load reaction tracking data from JSON file."""
    if not os.path.exists(REACTIONS_FILE):
        return {}
    with open(REACTIONS_FILE, "r") as f:
        return json.load(f)

def save_reactions(data):
    """Save reaction tracking data to JSON file."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(REACTIONS_FILE), exist_ok=True)
    with open(REACTIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_log_channel_id(guild_id):
    """Get the logging channel ID for a guild."""
    config = load_config()
    guild_config = config.get(str(guild_id), {})
    
    # Handle both old format (integer) and new format (dictionary)
    if isinstance(guild_config, dict):
        return guild_config.get("log_channel_id")
    else:
        # Old format - guild_config is just the channel ID integer
        return None

def set_log_channel_id(guild_id, channel_id):
    """Set the logging channel ID for a guild."""
    config = load_config()
    guild_id_str = str(guild_id)
    
    if guild_id_str not in config:
        config[guild_id_str] = {}
    
    config[guild_id_str]["log_channel_id"] = channel_id
    save_config(config)