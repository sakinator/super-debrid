import json
import os
from pathlib import Path
from typing import Dict, Any

CONFIG_FILE = Path(__file__).parent / "data" / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "host": "0.0.0.0",
    "port": 7070,
    # The 9 Debrid Services (All Supported with Optional Paid / Free API Keys)
    "torbox_api_key": "",
    "realdebrid_api_key": "",
    "alldebrid_api_key": "",
    "premiumize_api_key": "",
    "debridlink_api_key": "",
    "linksnappy_api_key": "",
    "linksnappy_username": "",
    "linksnappy_password": "",
    "megadebrid_api_key": "",
    "deepbrid_token": "",
    "highway_token": "",
    "seedr_token": "",
    "seedr_username": "",
    "seedr_password": "",
    # Free resolvers toggles
    "terabox_enabled": True,
    "pixeldrain_bypass_enabled": True,
    "get4all_enabled": True,
    "anything_rip_enabled": True,
    "deepbrid_free_enabled": True,
    "highway_free_enabled": True,
    "ytdlp_enabled": True,
}

def load_config() -> Dict[str, Any]:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(data)
            return merged
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
