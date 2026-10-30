import os
import sys
import json
import threading
import copy
from core.safe_io import write_json_atomic

class ConfigManager:
    """Manages THub configuration safely with thread-locking and auto-defaults."""
    _instance = None
    _lock = threading.RLock()

    DEFAULT_CONFIG = {
        "active_theme": "Obsidian",
        "app_lang": "th",
        "card_view_mode": "Vertical",
        "auto_update": False,
        "default_author": "หน๊ด หนวด translator",
        "default_tools_dir": r"E:\Mod_Workspace\Tool",
        "default_workspace_dir": r"E:\Mod_Workspace",
        "game_library_paths": [],
        "projects": [],
        "tools": {},
        "steam_auto_capsule": True,
        "ai_cli_preset": "claude",
        "ai_cli_custom_cmd": "claude",
        "ai_cli_auto_copy": True,
        "dashboard_card_size": "normal"
    }

    def __new__(cls, config_path=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConfigManager, cls).__new__(cls)
                cls._instance._init(config_path)
        return cls._instance

    def _init(self, config_path=None):
        if config_path is None:
            config_path = os.environ.get("THUB_CONFIG_PATH")
        if config_path is None:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "hub_config.json")
        self.config_path = config_path
        self._data = {}
        self._load_error = None
        self.load()

    def load(self):
        with self._lock:
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, "r", encoding="utf-8-sig") as f:
                        loaded = json.load(f)
                    if (not isinstance(loaded, dict) or not isinstance(loaded.get("projects", []), list)
                            or any(not isinstance(project, dict) for project in loaded.get("projects", []))):
                        raise ValueError("Invalid THub configuration structure")
                    self._data = {**copy.deepcopy(self.DEFAULT_CONFIG), **loaded}
                    self._load_error = None
                except Exception as e:
                    self._load_error = str(e)
                    print(f"[ConfigManager] Error loading config: {e}. Using defaults without overwriting the original.")
                    self._data = copy.deepcopy(self.DEFAULT_CONFIG)
            else:
                self._data = copy.deepcopy(self.DEFAULT_CONFIG)
                self._load_error = None
                self.save()
            return self._data

    def save(self):
        with self._lock:
            try:
                if self._load_error:
                    raise OSError("Refusing to overwrite unreadable config: " + self._load_error)
                write_json_atomic(self.config_path, self._data)
                return True
            except Exception as e:
                print(f"[ConfigManager] Failed to save config: {e}")
                return False

    def get(self, key, default=None):
        with self._lock:
            return self._data.get(key, default)

    def set(self, key, value, auto_save=True):
        with self._lock:
            self._data[key] = value
            if auto_save and not self.save():
                raise OSError(f"Could not save THub config: {self.config_path}")
            return True

    def get_projects(self):
        with self._lock:
            return self._data.get("projects", [])

    def save_projects(self, projects):
        with self._lock:
            self._data["projects"] = projects
            if not self.save():
                raise OSError(f"Could not save THub projects: {self.config_path}")
            return True
