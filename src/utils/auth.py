"""
Authorization utilities for the UFO Sighting Bot.
"""
import json
import os

AUTH_FILE = "data/authorized_users.json"

def load_authorized_users():
    """Load authorized users configuration."""
    if not os.path.exists(AUTH_FILE):
        # Default authorized users (you can modify this list)
        default_auth = {
            "admin_users": [
                543568562145722417  # Bot owner - replace with actual ID
            ]
        }
        save_authorized_users(default_auth)
        return default_auth
    
    with open(AUTH_FILE, "r") as f:
        return json.load(f)

def save_authorized_users(auth_data):
    """Save authorized users configuration."""
    os.makedirs(os.path.dirname(AUTH_FILE), exist_ok=True)
    with open(AUTH_FILE, "w") as f:
        json.dump(auth_data, f, indent=4)

def is_admin_user(user_id):
    """Check if user is an admin (has access to all admin commands)."""
    auth_data = load_authorized_users()
    return user_id in auth_data.get("admin_users", [])

def add_admin_user(user_id):
    """Add a user to the admin list."""
    auth_data = load_authorized_users()
    if user_id not in auth_data.get("admin_users", []):
        auth_data.setdefault("admin_users", []).append(user_id)
        save_authorized_users(auth_data)
        return True
    return False

def remove_admin_user(user_id):
    """Remove a user from the admin list."""
    auth_data = load_authorized_users()
    if user_id in auth_data.get("admin_users", []):
        auth_data["admin_users"].remove(user_id)
        save_authorized_users(auth_data)
        return True
    return False

def get_admin_users():
    """Get list of admin users."""
    auth_data = load_authorized_users()
    return auth_data.get("admin_users", [])