import json
import os

SETTINGS_FILE = "server_settings.json"
SUPERUSERS = {1380365019153432596, 1245296006338445339}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_admin_or_superuser(user_id: int, guild_owner_id: int) -> bool:
    return (user_id in SUPERUSERS) or (user_id == guild_owner_id)

def get_server_thought_setting(guild_id: int) -> bool:
    data = load_settings()
    return data.get(str(guild_id), {}).get("show_thoughts", True)

def set_server_thought_setting(guild_id: int, enabled: bool):
    data = load_settings()
    guild_str = str(guild_id)
    if guild_str not in data:
        data[guild_str] = {}
    data[guild_str]["show_thoughts"] = enabled
    save_settings(data)
