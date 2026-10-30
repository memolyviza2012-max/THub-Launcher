import os
import re
import threading
from core.config_manager import ConfigManager

class GameScanner:
    """
    High-speed scanner for installed games across Steam, Xbox, GOG, and custom directories.
    Caches results in-memory and provides smart search & auto-fill for new projects.
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self, config_manager=None):
        self.cfg = config_manager or ConfigManager()
        self._installed_games = []
        self._last_scanned_libs = []
        self._is_initialized = False

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def get_steam_libraries(self):
        """Discovers all Steam library folders by parsing libraryfolders.vdf and drive roots."""
        discovered = set()

        # 1. Standard Steam installation VDF locations
        candidate_vdfs = [
            r"C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf",
            r"C:\Program Files\Steam\steamapps\libraryfolders.vdf",
            r"C:\Steam\steamapps\libraryfolders.vdf",
            r"D:\Steam\steamapps\libraryfolders.vdf",
            r"E:\Steam\steamapps\libraryfolders.vdf",
            r"F:\Steam\steamapps\libraryfolders.vdf",
        ]

        for vdf_path in candidate_vdfs:
            if os.path.exists(vdf_path):
                try:
                    with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if '"path"' in line:
                                parts = line.split('"path"')
                                if len(parts) > 1:
                                    raw_p = parts[1].strip().strip('"').replace('\\\\', '\\')
                                    common_dir = os.path.join(raw_p, "steamapps", "common")
                                    if os.path.exists(common_dir):
                                        discovered.add(os.path.normpath(common_dir))
                except Exception as e:
                    print(f"[GameScanner] Error reading VDF {vdf_path}: {e}")

        # 2. Drive root auto-scan across all available drives
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            drive_root = f"{letter}:\\"
            if os.path.exists(drive_root):
                candidates = [
                    os.path.join(drive_root, "SteamLibrary", "steamapps", "common"),
                    os.path.join(drive_root, "Steam", "steamapps", "common"),
                    os.path.join(drive_root, "Program Files (x86)", "Steam", "steamapps", "common"),
                    os.path.join(drive_root, "Program Files", "Steam", "steamapps", "common"),
                ]
                for c in candidates:
                    if os.path.exists(c):
                        discovered.add(os.path.normpath(c))

        return sorted(list(discovered))

    def get_common_libraries(self):
        """Scans for other common game store folders (Xbox, GOG, Epic, etc.)."""
        common = set()
        for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            drive_root = f"{letter}:\\"
            if os.path.exists(drive_root):
                candidates = [
                    os.path.join(drive_root, "XboxGames"),
                    os.path.join(drive_root, "GOG Games"),
                    os.path.join(drive_root, "Epic Games"),
                    os.path.join(drive_root, "Games"),
                    os.path.join(drive_root, "Game"),
                    os.path.join(drive_root, "Program Files (x86)", "GOG Galaxy", "Games"),
                    os.path.join(drive_root, "Program Files", "Epic Games"),
                ]
                for c in candidates:
                    if os.path.exists(c):
                        common.add(os.path.normpath(c))
        return sorted(list(common))

    def get_all_library_folders(self):
        """Combines Steam libraries, common game stores, and user-configured custom paths."""
        all_libs = []
        seen = set()

        # Steam
        for s in self.get_steam_libraries():
            norm = os.path.normpath(s)
            if norm not in seen:
                seen.add(norm)
                all_libs.append({"path": norm, "source": "Steam"})

        # Common
        for c in self.get_common_libraries():
            norm = os.path.normpath(c)
            if norm not in seen:
                seen.add(norm)
                all_libs.append({"path": norm, "source": "System"})

        # Custom paths from config
        custom_paths = self.cfg.get("game_library_paths", []) or []
        for cp in custom_paths:
            if os.path.exists(cp):
                norm = os.path.normpath(cp)
                if norm not in seen:
                    seen.add(norm)
                    all_libs.append({"path": norm, "source": "Custom"})

        return all_libs

    def scan_installed_games(self, force_refresh=False):
        """
        Scans all discovered libraries and indexes installed games.
        Returns a list of game records: [{"name": ..., "path": ..., "source": ...}].
        """
        with self._lock:
            if self._is_initialized and not force_refresh:
                return self._installed_games

            libs = self.get_all_library_folders()
            games = []
            seen_paths = set()

            for lib_entry in libs:
                lib_path = lib_entry["path"]
                source = lib_entry["source"]
                if not os.path.exists(lib_path):
                    continue

                try:
                    for item in os.listdir(lib_path):
                        full_path = os.path.normpath(os.path.join(lib_path, item))
                        if not os.path.isdir(full_path):
                            continue
                        if full_path in seen_paths:
                            continue

                        # Check if directory actually has content (skip empty folders)
                        try:
                            sub_contents = os.listdir(full_path)
                            if not sub_contents:
                                continue
                        except Exception:
                            continue

                        seen_paths.add(full_path)
                        games.append({
                            "name": item,
                            "clean_name": self._clean_game_name(item),
                            "path": full_path,
                            "library": lib_path,
                            "source": source
                        })
                except Exception as e:
                    print(f"[GameScanner] Error scanning {lib_path}: {e}")

            # Sort alphabetically by name
            games.sort(key=lambda g: g["name"].lower())
            self._installed_games = games
            self._last_scanned_libs = libs
            self._is_initialized = True
            return self._installed_games

    @staticmethod
    def _clean_game_name(name):
        """Normalizes a game directory name for fuzzy matching."""
        # Replace underscores, hyphens with spaces and remove special edition suffixes for matching
        cleaned = re.sub(r'[_+\-]', ' ', name)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def find_installed_games(self, query, limit=10):
        """
        Finds matching installed games for a query string.
        Ranks results using exact, token, and substring similarity.
        """
        if not query or not query.strip():
            return []

        games = self.scan_installed_games()
        q_raw = query.strip()
        q_clean = self._clean_game_name(q_raw).lower()
        q_tokens = [t for t in re.split(r'[^a-zA-Z0-9\u0E00-\u0E7F]+', q_clean) if t]

        scored = []
        for g in games:
            score = self._score_match(q_clean, q_tokens, g)
            if score > 20:
                scored.append((score, g))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [g for _, g in scored[:limit]]

    def get_best_match(self, query, min_score=60):
        """Returns the single best matching game if confidence is high enough."""
        matches = self.find_installed_games(query, limit=1)
        if not matches:
            return None

        # Re-score the first match
        q_clean = self._clean_game_name(query.strip()).lower()
        q_tokens = [t for t in re.split(r'[^a-zA-Z0-9\u0E00-\u0E7F]+', q_clean) if t]
        score = self._score_match(q_clean, q_tokens, matches[0])
        if score >= min_score:
            return matches[0]
        return None

    def _score_match(self, q_clean, q_tokens, game):
        g_name_raw = game["name"].lower()
        g_clean = game["clean_name"].lower()
        g_tokens = [t for t in re.split(r'[^a-zA-Z0-9\u0E00-\u0E7F]+', g_clean) if t]

        # 1. Exact match
        if q_clean == g_clean or q_clean == g_name_raw:
            return 100

        # 2. Query is prefix or contains full name
        if g_clean.startswith(q_clean):
            return 95
        if q_clean.startswith(g_clean):
            return 92

        # 3. Substring match
        if q_clean in g_clean or q_clean in g_name_raw:
            ratio = len(q_clean) / max(len(g_clean), 1)
            return int(75 + 15 * ratio)

        # 4. Token overlap
        if q_tokens and g_tokens:
            q_set = set(q_tokens)
            g_set = set(g_tokens)
            overlap = q_set.intersection(g_set)
            if overlap:
                match_ratio = len(overlap) / len(q_set)
                base = 50 * match_ratio

                # Bonus if order of tokens matches
                if len(overlap) == len(q_set):
                    base += 25
                return int(base)

        return 0
