import threading
import os
import glob
import re
from pathlib import Path

class KnowledgeService:
    """
    Multi-Tier Knowledge Base Service for Modding-Knowledge.
    Universal Deep Scanner and Dynamic Matcher:
      - Deep recursive scanner across all engines, subfolders, root bibles, and guides.
      - Dynamic engine discovery supporting 64+ engine directories without rigid static maps.
      - Version-aware title matching without false version mismatches.
      - Technical tag & file extension matching (Tier 1.5).
      - Multi-Tier recommendations:
          Tier 1: Exact Game Bible (⭐)
          Tier 1.5: Technical & Stack Guides (🛠️)
          Tier 2: Engine Guides (📘)
          Tier 3: Similar Game Bibles from same engine (🎮)
    """

    EXTERNAL_KB = r"E:\Mod_Workspace\Modding-Knowledge"
    LOCAL_KB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Modding-Knowledge")

    ROMAN_MAP = {
        'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5,
        'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9, 'x': 10
    }

    STOP_WORDS = {
        "the", "of", "and", "in", "on", "at", "to", "a", "an", "for",
        "edition", "remastered", "cut", "directors", "director"
    }

    # Core technical keywords for tagging and Tier 1.5 technical matching
    TECH_KEYWORDS = [
        "locres", "pk3", "msg", "tlk", "bif", "rpack", "pck", "asr", "bigfile",
        "bundle", "assets", "arc", "cpk", "iostore", "ucas", "utoc", "pak",
        "bitmap font", "fnt", "ufont", "sdf", "textmeshpro", "tmp", "pua",
        "repak", "fmodel", "unreallocres", "uabea", "unitypy", "bepinex",
        "reframework", "openjk", "quickbms", "flagrum", "wolvenkit", "kotor tool",
        "stringtable", "exb", "oodle", "zlib", "lz4", "aes"
    ]

    # Alias map for cross-engine synonyms and family groupings
    ALIAS_MAP = {
        "unreal": ["Unreal_Engine_5", "Unreal_Engine_4", "Unreal_Engine_3", "Unreal_Engine_2"],
        "unrealengine": ["Unreal_Engine_5", "Unreal_Engine_4", "Unreal_Engine_3", "Unreal_Engine_2"],
        "unrealengine5": ["Unreal_Engine_5"],
        "unrealengine4": ["Unreal_Engine_4"],
        "unrealengine3": ["Unreal_Engine_3"],
        "unrealengine2": ["Unreal_Engine_2"],
        "idtech": ["id_Tech", "id_Tech_6", "id_Tech_7"],
        "idtech6": ["id_Tech_6"],
        "idtech7": ["id_Tech_7"],
        "odyssey": ["Aurora_Engine"],
        "odysseyengine": ["Aurora_Engine"],
        "aurora": ["Aurora_Engine"],
        "auroraengine": ["Aurora_Engine"],
        "katana": ["Gust_Engine"],
        "gust": ["Gust_Engine"],
        "katanagust": ["Gust_Engine"],
        "gustengine": ["Gust_Engine"],
        "cengine": ["C_Engine"],
        "reengine": ["RE_Engine"],
        "mtframework": ["MT_Framework"],
        "cdc": ["Crystal Dynamics Foundation Engine"],
        "cdcengine": ["Crystal Dynamics Foundation Engine"],
        "crystaldynamics": ["Crystal Dynamics Foundation Engine"],
        "foundationengine": ["Crystal Dynamics Foundation Engine"],
        "fledge": ["Fledge", "FLEDGE_Engine"],
        "fledgeengine": ["Fledge", "FLEDGE_Engine"],
        "custom": ["Custom_Engine", "Paradox_Custom", "RemedyCustom", "Despair Engine", "SGE_Engine"],
        "customengine": ["Custom_Engine", "Paradox_Custom", "RemedyCustom", "Despair Engine", "SGE_Engine"],
        "10tons": ["10tons_Engine"],
        "10tonsengine": ["10tons_Engine"],
        "dawn": ["Dawn_Engine"],
        "dawnengine": ["Dawn_Engine"],
        "unity": ["Unity"],
    }

    _instance = None
    _instance_lock = threading.RLock()

    @classmethod
    def get_instance(cls):
        """Thread-safe singleton instance for high-performance shared access."""
        with cls._instance_lock:
            if getattr(cls, "_instance", None) is None:
                cls._instance = cls()
            return cls._instance

    @classmethod
    def instance(cls):
        """Convenience alias for get_instance()."""
        return cls.get_instance()

    def __init__(self):
        if os.path.exists(self.EXTERNAL_KB):
            self.root_kb = self.EXTERNAL_KB
        elif os.path.exists(self.LOCAL_KB):
            self.root_kb = self.LOCAL_KB
        else:
            self.root_kb = None

        # Readers use a published catalog while a replacement is built in isolation.
        # The tuple swap publishes all three collections and their cache atomically.
        self._catalog = ([], {}, {}, {}, 0)
        self._reindex_lock = threading.Lock()
        self.reindex()

    @property
    def _index(self):
        return self._catalog[0]

    @property
    def _engines(self):
        return self._catalog[1]

    @property
    def _categories(self):
        return self._catalog[2]

    @property
    def _title_cache(self):
        return self._catalog[3]

    @property
    def generation(self):
        """Revision of the published catalog, used by dependent detection caches."""
        return self._catalog[4]

    @classmethod
    def _extract_tags(cls, file_path, title="", filename=""):
        """Extracts technical keyword tags using word-boundary safe patterns."""
        tags = set()
        search_blob = f"{filename} {title}".lower()

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                search_blob += " " + f.read(4000).lower()
        except Exception:
            pass

        for kw in cls.TECH_KEYWORDS:
            if len(kw) <= 4:
                if re.search(r'(?:\b|\.)' + re.escape(kw) + r'\b', search_blob):
                    tags.add(kw)
            else:
                if kw in search_blob:
                    tags.add(kw)

        return tags

    @classmethod
    def _extract_file_metadata(cls, file_path):
        """Extracts header metadata (Engine, Game ID, Titles) from markdown."""
        engine = None
        game = None
        h1 = None
        h2 = None

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                head = f.read(3000)

            m_eng = re.search(r'>\s*\*\*Engine:\*\*\s*([^\n\r]+)', head, re.IGNORECASE)
            if m_eng:
                engine = m_eng.group(1).strip()

            m_game = re.search(r'>\s*\*\*Game(?:\s*ID|\s*/\s*Version)?:\*\*\s*([^\n\r]+)', head, re.IGNORECASE)
            if m_game:
                game = m_game.group(1).strip()

            m_h1 = re.search(r'^#\s+(?:📖\s*)?([^\n\r]+)', head, re.MULTILINE)
            if m_h1:
                h1 = m_h1.group(1).strip()

            m_h2 = re.search(r'^##\s+([^\n\r]+)', head, re.MULTILINE)
            if m_h2:
                h2 = m_h2.group(1).strip()
        except Exception:
            pass

        return {"engine": engine, "game": game, "h1": h1, "h2": h2}

    def reindex(self):
        """
        Universal Deep Recursive Scanner for Modding-Knowledge:
        Scans all markdown files across Engines, Games, Techniques, Tools, Skills,
        as well as root-level markdown files, building complete index without gaps.
        """
        with self._reindex_lock:
            # Do not clear the live catalog: UI searches must remain available
            # throughout I/O, and a failed refresh must leave the prior data usable.
            builder = object.__new__(type(self))
            builder.__dict__ = self.__dict__.copy()
            builder._catalog = ([], {}, {}, {}, 0)
            builder._build_index()
            self._catalog = builder._catalog[:4] + (self.generation + 1,)
            # Engine detection attaches Bible metadata, so invalidate its cached
            # results after a successful knowledge refresh without importing it.
            import sys
            scanner = sys.modules.get("core.engine_scanner")
            if scanner is not None:
                scanner.EngineScanner._cache.clear()

    def _build_index(self):
        """Populate a private replacement catalog; reindex() owns publication."""
        self._index.clear()
        self._engines.clear()
        self._categories.clear()

        if not self.root_kb:
            return
        if not os.path.isdir(self.root_kb):
            raise FileNotFoundError(f"Knowledge directory is unavailable: {self.root_kb}")

        kb_path = Path(self.root_kb)
        seen_paths = set()

        # 1. Scan Engines folder recursively
        engines_dir = kb_path / "Engines"
        if engines_dir.is_dir():
            for eng_folder in sorted(engines_dir.iterdir()):
                if not eng_folder.is_dir():
                    continue

                folder_name = eng_folder.name
                display_name = folder_name.replace("_", " ")

                games_dict = {}
                eng_guides = []

                for md_file in sorted(eng_folder.rglob("*.md")):
                    if md_file.name.lower() == "readme.md":
                        continue

                    file_abs = str(md_file)
                    if file_abs in seen_paths:
                        continue
                    seen_paths.add(file_abs)

                    rel = md_file.relative_to(kb_path).as_posix()
                    rel_to_eng = md_file.relative_to(eng_folder)
                    parts = rel_to_eng.parts

                    g_folder = None
                    g_display = None
                    cat = "Engines"

                    if len(parts) == 1:
                        # Engines/<Engine>/<Guide.md>
                        pass
                    elif parts[0].lower() == "games" and len(parts) >= 2:
                        # Engines/<Engine>/Games/<GameFolder>/...
                        g_folder = parts[1]
                        g_display = g_folder.replace("_", " ")
                    elif parts[0].lower() in ("techniques", "tools", "docs"):
                        # Engines/<Engine>/Techniques/...
                        cat = parts[0].capitalize()
                    else:
                        # Direct game folder under engine (e.g. Frostbite/DeadSpaceRemake)
                        g_folder = parts[0]
                        g_display = g_folder.replace("_", " ")

                    tags = self._extract_tags(md_file, title=md_file.stem, filename=md_file.name)
                    item = {
                        "title": md_file.stem.replace("_", " "),
                        "filename": md_file.name,
                        "path": file_abs,
                        "rel_path": rel,
                        "engine": display_name,
                        "engine_folder": folder_name,
                        "game": g_display,
                        "game_folder": g_folder,
                        "category": cat,
                        "tags": tags
                    }

                    self._index.append(item)

                    if g_folder:
                        if g_folder not in games_dict:
                            games_dict[g_folder] = {
                                "name": g_display,
                                "folder": g_folder,
                                "path": str(eng_folder / parts[0] if parts[0].lower() != "games" else eng_folder / "Games" / g_folder),
                                "bibles": []
                            }
                        games_dict[g_folder]["bibles"].append(item)
                    else:
                        eng_guides.append(item)

                games_list = sorted(games_dict.values(), key=lambda g: g["name"])
                self._engines[folder_name] = {
                    "name": display_name,
                    "folder": folder_name,
                    "path": str(eng_folder),
                    "games": games_list,
                    "engine_guides": eng_guides,
                    "total_games": len(games_list),
                    "total_guides": len(eng_guides)
                }

            # 1.2 Scan direct markdown files in Engines/*.md (e.g. C-Engine.md, GameMaker_Studio.md)
            for md_file in sorted(engines_dir.glob("*.md")):
                if md_file.name.lower() == "readme.md":
                    continue

                file_abs = str(md_file)
                if file_abs in seen_paths:
                    continue
                seen_paths.add(file_abs)

                rel = md_file.relative_to(kb_path).as_posix()
                stem = md_file.stem
                stem_clean = re.sub(r'[^a-z0-9]', '', stem.lower())
                matched_folder = None
                for ef in self._engines.keys():
                    if stem_clean == re.sub(r'[^a-z0-9]', '', ef.lower()):
                        matched_folder = ef
                        break

                display_name = matched_folder.replace("_", " ") if matched_folder else stem.replace("_", " ")
                tags = self._extract_tags(md_file, title=stem, filename=md_file.name)
                guide_item = {
                    "title": stem.replace("_", " "),
                    "filename": md_file.name,
                    "path": file_abs,
                    "rel_path": rel,
                    "engine": display_name,
                    "engine_folder": matched_folder or stem,
                    "game": None,
                    "game_folder": None,
                    "category": "Engines",
                    "tags": tags
                }
                self._index.append(guide_item)
                if matched_folder and matched_folder in self._engines:
                    self._engines[matched_folder]["engine_guides"].append(guide_item)
                    self._engines[matched_folder]["total_guides"] += 1
                elif not matched_folder:
                    self._engines[stem] = {
                        "name": display_name,
                        "folder": stem,
                        "path": str(md_file),
                        "games": [],
                        "engine_guides": [guide_item],
                        "total_games": 0,
                        "total_guides": 1
                    }

        # 2. Scan other top-level categories: Techniques, Tools, Skills, Games (root)
        for cat_dir in sorted(kb_path.iterdir()):
            if not cat_dir.is_dir() or cat_dir.name in ("Engines", ".git", "_Index"):
                continue

            cat_name = cat_dir.name.replace("_", " ")
            cat_items = []

            for md_file in sorted(cat_dir.rglob("*.md")):
                if md_file.name.lower() == "readme.md":
                    continue

                file_abs = str(md_file)
                if file_abs in seen_paths:
                    continue
                seen_paths.add(file_abs)

                rel = md_file.relative_to(kb_path).as_posix()
                meta = self._extract_file_metadata(md_file)
                tags = self._extract_tags(md_file, title=md_file.stem, filename=md_file.name)

                game_name = meta.get("game") or (md_file.parent.name if md_file.parent != cat_dir else None)
                engine_name = meta.get("engine") or cat_name

                item = {
                    "title": md_file.stem.replace("_", " "),
                    "filename": md_file.name,
                    "path": file_abs,
                    "rel_path": rel,
                    "engine": engine_name,
                    "engine_folder": cat_dir.name,
                    "game": game_name,
                    "game_folder": md_file.parent.name if md_file.parent != cat_dir else None,
                    "category": cat_name,
                    "tags": tags
                }
                cat_items.append(item)
                self._index.append(item)

            if cat_items:
                self._categories[cat_name] = cat_items

        # 3. Scan Root-level Markdown Files (e.g. STAR_WARS_Jedi_Academy_Thai_Localization_Bible_v1.0.md)
        for md_file in sorted(kb_path.glob("*.md")):
            if md_file.name.lower() == "readme.md":
                continue

            file_abs = str(md_file)
            if file_abs in seen_paths:
                continue
            seen_paths.add(file_abs)

            rel = md_file.relative_to(kb_path).as_posix()
            meta = self._extract_file_metadata(md_file)
            tags = self._extract_tags(md_file, title=md_file.stem, filename=md_file.name)

            inferred_engine = meta.get("engine")
            inferred_game = meta.get("game")

            if not inferred_game:
                clean_title = md_file.stem.replace("_", " ")
                clean_title = re.sub(r'\b(?:Thai\s+Localization\s+Bible|Bible)\b.*', '', clean_title, flags=re.IGNORECASE).strip()
                inferred_game = clean_title or md_file.stem

            resolved_ef = None
            if inferred_engine:
                matched_folders = self._resolve_engine_folders(inferred_engine)
                if matched_folders:
                    resolved_ef = matched_folders[0]

            item = {
                "title": md_file.stem.replace("_", " "),
                "filename": md_file.name,
                "path": file_abs,
                "rel_path": rel,
                "engine": inferred_engine or "General",
                "engine_folder": resolved_ef or "General",
                "game": inferred_game,
                "game_folder": inferred_game.replace(" ", "_") if inferred_game else None,
                "category": "Root",
                "tags": tags
            }
            self._index.append(item)

            if resolved_ef and resolved_ef in self._engines:
                self._engines[resolved_ef]["games"].append({
                    "name": inferred_game,
                    "folder": inferred_game.replace(" ", "_"),
                    "path": file_abs,
                    "bibles": [item]
                })

    def get_engines(self):
        """Returns all indexed engines, sorted with highest game count first."""
        return sorted(
            self._engines.values(),
            key=lambda e: (-e["total_games"], -e["total_guides"], e["name"])
        )

    def get_engine(self, engine_folder_or_name):
        """Finds engine by folder name or display name."""
        if not engine_folder_or_name:
            return None
        target = re.sub(r'[^a-z0-9]', '', engine_folder_or_name.lower())
        for folder, data in self._engines.items():
            if re.sub(r'[^a-z0-9]', '', folder.lower()) == target or re.sub(r'[^a-z0-9]', '', data["name"].lower()) == target:
                return data
        return None

    def get_games_for_engine(self, engine_folder_or_name):
        """Returns all games under a specified engine."""
        eng = self.get_engine(engine_folder_or_name)
        if eng:
            return eng.get("games", [])
        return []

    def get_categories(self):
        """Returns non-engine category items (e.g. Techniques, Tools)."""
        return self._categories

    def search(self, query, engine_folder=None):
        """
        Instant search across all guides and bibles by title, rel_path, engine, game, or tags.
        Optionally filter within a specific engine.
        """
        pool = self._index
        if engine_folder:
            pool = [item for item in pool if item.get("engine_folder") == engine_folder]

        if not query:
            return pool

        q = query.lower().strip()
        results = []
        for item in pool:
            title = item["title"].lower()
            rel = item["rel_path"].lower()
            engine = (item.get("engine") or "").lower()
            game = (item.get("game") or "").lower()
            tags = item.get("tags") or set()
            if q in title or q in rel or q in engine or q in game or any(q in t for t in tags):
                results.append(item)
        return results

    @classmethod
    def _clean_text(cls, s):
        if not s:
            return ""
        s = re.sub(r'[\ufffd\x80-\xff]', '', str(s))
        s = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', s)
        s = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', s)
        return s

    @classmethod
    def _extract_versions(cls, text):
        """
        Extracts game sequel/version numbers (e.g. '2' from 'Helldivers 2' or 'II' from 'DOOM II').
        Carefully strips document version notations ('v1.0', 'version 2.0') to avoid
        false mismatches between game title and bible revision.
        """
        if not text:
            return set()

        text_clean = re.sub(r'\bv\s*\d+(?:\.\d+)*\b', '', str(text), flags=re.IGNORECASE)
        text_clean = re.sub(r'\bversion\s*\d+(?:\.\d+)*\b', '', text_clean, flags=re.IGNORECASE)
        text_clean = re.sub(r'thai\s+localization\s+bible', '', text_clean, flags=re.IGNORECASE)
        text_clean = re.sub(r'thai\s+mod\s+production\s+bible', '', text_clean, flags=re.IGNORECASE)
        text_clean = cls._clean_text(text_clean).lower()

        versions = set()
        for m in re.finditer(r'\b([1-9]|1[0-9])\b', text_clean):
            versions.add(int(m.group(1)))
        for m in re.finditer(r'\b(ii|iii|iv|v|vi|vii|viii|ix|x)\b', text_clean):
            val = cls.ROMAN_MAP.get(m.group(1))
            if val:
                versions.add(val)
        for m in re.finditer(r'\b(\w+)\s+i\b', text_clean):
            if m.group(1) not in ("and", "or", "if", "as", "is"):
                versions.add(1)
        return versions

    @classmethod
    def _tokenize(cls, s):
        if not s:
            return []
        s = cls._clean_text(s)
        tokens = [w.lower() for w in re.split(r'[^a-zA-Z0-9]+', s) if len(w) >= 2]
        return [t for t in tokens if t not in cls.STOP_WORDS]

    @staticmethod
    def _get_canonical_engine(name):
        if not name:
            return ""
        clean = re.sub(r'[^a-z0-9]', '', str(name).lower())
        if "cdc" in clean or "crystaldynamics" in clean or "foundation" in clean:
            return "crystal_dynamics"
        if clean in ("cengine", "c"):
            return "c_engine"
        if "unreal" in clean:
            return "unreal"
        if "aurora" in clean or "odyssey" in clean:
            return "aurora"
        if "gust" in clean or "katana" in clean:
            return "gust"
        if "marvelous" in clean:
            return "marvelous"
        if "10tons" in clean:
            return "10tons"
        if "dawn" in clean:
            return "dawn"
        if "idtech" in clean:
            return "idtech"
        if "reengine" in clean or "residentevil" in clean:
            return "re_engine"
        if "mtframework" in clean:
            return "mt_framework"
        if "asura" in clean:
            return "asura"
        if "void" in clean:
            return "void"
        if "unity" in clean:
            return "unity"
        if "frostbite" in clean:
            return "frostbite"
        if "custom" in clean or "sge" in clean or "despair" in clean or "paradox" in clean or "remedy" in clean:
            return "custom"
        return clean

    @classmethod
    def _are_engines_compatible(cls, proj_eng, item_eng_folder):
        if not proj_eng or not item_eng_folder:
            return True
        c_proj = cls._get_canonical_engine(proj_eng)
        c_item = cls._get_canonical_engine(item_eng_folder)
        if not c_proj or not c_item:
            return True
        return c_proj == c_item

    def _resolve_engine_folders(self, engine_name):
        """
        Dynamically resolves an engine name into matching engine folders from self._engines.
        Uses aliases, clean normalization, and safe word-boundary matching.
        """
        clean = re.sub(r'[^a-z0-9]', '', (engine_name or "").lower())
        clean_root = clean.replace("engine", "")
        targets = []

        # 1. Alias lookup
        if clean in self.ALIAS_MAP:
            for ef in self.ALIAS_MAP[clean]:
                if ef in self._engines and ef not in targets:
                    targets.append(ef)

        # 2. Dynamic matching across all 64+ indexed engines
        for ef in self._engines.keys():
            if ef in targets:
                continue
            c_ef = re.sub(r'[^a-z0-9]', '', ef.lower())
            c_ef_root = c_ef.replace("engine", "")

            # Exact or root match
            if clean == c_ef or (clean_root and clean_root == c_ef_root):
                targets.append(ef)
            # Safe substring match (both sides require at least 4 chars)
            elif len(clean_root) >= 4 and len(c_ef_root) >= 4 and (clean_root in c_ef_root or c_ef_root in clean_root):
                targets.append(ef)

        return targets

    def _score_game_match(self, project_title, item, project_engine=None):
        if not project_title:
            return 0

        p_clean_str = re.sub(r'[^a-z0-9]', '', self._clean_text(project_title).lower())
        g_clean_str = re.sub(r'[^a-z0-9]', '', self._clean_text(item.get("game") or "").lower())
        f_clean_str = re.sub(r'[^a-z0-9]', '', self._clean_text(item.get("game_folder") or "").lower())

        # Check KKND alias
        if "krushkill" in p_clean_str and "destroy" in p_clean_str:
            p_clean_str = p_clean_str.replace("krushkillndestroy", "kknd").replace("krushkilldestroy", "kknd")
        if "krushkill" in g_clean_str and "destroy" in g_clean_str:
            g_clean_str = g_clean_str.replace("krushkillndestroy", "kknd").replace("krushkilldestroy", "kknd")
        if "krushkill" in f_clean_str and "destroy" in f_clean_str:
            f_clean_str = f_clean_str.replace("krushkillndestroy", "kknd").replace("krushkilldestroy", "kknd")

        # Check version / sequel alignment
        p_vers = self._extract_versions(project_title)
        i_vers = self._extract_versions(f"{item.get('game_folder', '')} {item.get('game', '')} {item.get('title', '')}")

        # Sequel mismatch checks
        if p_vers and i_vers:
            if p_vers != i_vers:
                return 0
        elif i_vers and not p_vers:
            if any(v > 1 for v in i_vers):
                return 0
        elif p_vers and not i_vers:
            if any(v > 1 for v in p_vers):
                return 0

        # Engine compatibility
        eng_compat = self._are_engines_compatible(project_engine, item.get("engine_folder") or item.get("engine"))
        if not eng_compat:
            return 0

        # Exact clean string match
        if p_clean_str and (p_clean_str == f_clean_str or p_clean_str == g_clean_str):
            score = 120
        else:
            p_tokens = set(self._tokenize(project_title))
            if "krush" in p_tokens and "destroy" in p_tokens:
                p_tokens.add("kknd")

            g_tokens = set(self._tokenize(item.get("game") or item.get("game_folder") or ""))
            if "kknd" in g_tokens:
                g_tokens.update(["krush", "kill", "destroy"])

            t_tokens = set(self._tokenize(item.get("title") or ""))
            target_tokens = g_tokens | t_tokens

            if not p_tokens or not target_tokens:
                return 0

            intersection_g = p_tokens & g_tokens
            intersection_all = p_tokens & target_tokens

            if not intersection_all:
                return 0

            # Franchise Sibling check
            if g_tokens:
                unshared_p = p_tokens - g_tokens
                unshared_g = g_tokens - p_tokens
                unshared_p_words = {w for w in unshared_p if not w.isdigit()}
                unshared_g_words = {w for w in unshared_g if not w.isdigit()}
                if len(unshared_p_words) >= 1 and len(unshared_g_words) >= 1:
                    return 0

                if g_tokens.issubset(p_tokens) and len(g_tokens) >= 1:
                    score = 100
                elif len(intersection_g) >= 2:
                    overlap = len(intersection_g) / max(len(p_tokens), len(g_tokens))
                    score = int(overlap * 80) + 20
                else:
                    overlap = len(intersection_all) / len(p_tokens)
                    if overlap < 0.5:
                        return 0
                    score = int(overlap * 80)
            else:
                overlap = len(intersection_all) / len(p_tokens)
                if overlap < 0.5:
                    return 0
                score = int(overlap * 80)

        # Number equality bonus
        if p_vers and i_vers and p_vers == i_vers:
            score += 20

        # File type priority
        fn_lower = item.get("filename", "").lower()
        if "thai_localization_bible" in fn_lower or "thai_bible" in fn_lower:
            score += 20
        elif "bible" in fn_lower:
            score += 10
        if "tracker" in fn_lower or "log" in fn_lower:
            score -= 40

        return score

    def find_guides_for_engine(self, engine_name, game_title=None, tech_keywords=None, max_results=5):
        """
        Multi-Tier High-Precision Guide Finder:
        Tier 1: Exact Game Bible for this project (⭐)
        Tier 1.5: Technical & Stack Guides matching file extensions or tools (🛠️)
        Tier 2: Technical & Font Guides for this exact engine (📘)
        Tier 3: Exemplar Game Bibles from the same engine (🎮)
        """
        results = []
        seen_paths = set()

        clean_engine = re.sub(r'[^a-z0-9]', '', (engine_name or "").lower())

        # 1. Tier 1: Search for Exact Game Bible
        candidate_game_matches = []
        if game_title:
            for item in self._index:
                score = self._score_game_match(game_title, item, engine_name)
                if score >= 60:
                    candidate_game_matches.append((score, item))

            candidate_game_matches.sort(key=lambda x: -x[0])

            # If we have an exact/high match (score >= 100), suppress loose matches
            if candidate_game_matches and candidate_game_matches[0][0] >= 100:
                candidate_game_matches = [m for m in candidate_game_matches if m[0] >= 90]

            for score, item in candidate_game_matches:
                if item["path"] not in seen_paths:
                    seen_paths.add(item["path"])
                    item_copy = dict(item)
                    item_copy["match_type"] = "game_bible"
                    item_copy["score"] = score
                    results.append(item_copy)

        # Resolve Target Engine Folders dynamically
        target_folders = []
        if clean_engine in ("unrealengine", "unreal") and results:
            for r in results:
                ef = r.get("engine_folder")
                if ef and ef.startswith("Unreal_Engine_") and ef not in target_folders:
                    target_folders.append(ef)

        if not target_folders:
            target_folders = self._resolve_engine_folders(engine_name)

        # 2. Tier 1.5: Technical & Stack Guides (Matching detected file extensions or keywords)
        clean_tech = []
        if tech_keywords:
            for tk in tech_keywords:
                tk_clean = str(tk).lower().strip().lstrip(".")
                if tk_clean and len(tk_clean) >= 2:
                    clean_tech.append(tk_clean)

        if clean_tech and len(results) < max_results:
            tech_matches = []
            for item in self._index:
                if item["path"] in seen_paths:
                    continue

                item_tags = item.get("tags") or set()
                item_title = item.get("title", "").lower()
                item_rel = item.get("rel_path", "").lower()

                match_count = 0
                for tk in clean_tech:
                    if tk in item_tags or tk in item_title or tk in item_rel:
                        match_count += 1

                if match_count > 0:
                    eng_bonus = 2 if (item.get("engine_folder") in target_folders) else 0
                    tech_matches.append((match_count + eng_bonus, item))

            tech_matches.sort(key=lambda x: -x[0])
            for score, item in tech_matches:
                if item["path"] not in seen_paths:
                    seen_paths.add(item["path"])
                    item_copy = dict(item)
                    item_copy["match_type"] = "tech_guide"
                    results.append(item_copy)
                    if len(results) >= max_results:
                        break

        # 3. Tier 2: Engine Guides
        for tf in target_folders:
            eng_data = self.get_engine(tf)
            if not eng_data:
                continue
            for g in eng_data.get("engine_guides", []):
                if g["path"] not in seen_paths:
                    seen_paths.add(g["path"])
                    g_copy = dict(g)
                    g_copy["match_type"] = "engine_guide"
                    results.append(g_copy)
                    if len(results) >= max_results:
                        break
            if len(results) >= max_results:
                break

        # 4. Tier 3: Exemplar Game Bibles from same engine
        for tf in target_folders:
            eng_data = self.get_engine(tf)
            if not eng_data:
                continue
            for gm in eng_data.get("games", []):
                for b in gm.get("bibles", []):
                    if b["path"] not in seen_paths:
                        seen_paths.add(b["path"])
                        b_copy = dict(b)
                        b_copy["match_type"] = "similar_game"
                        results.append(b_copy)
                        if len(results) >= max_results:
                            break
                if len(results) >= max_results:
                    break
            if len(results) >= max_results:
                break

        return results[:max_results]

    def read_markdown(self, file_path):
        """Reads markdown content safely across multiple encodings."""
        if not os.path.exists(file_path):
            return ""
        for enc in ['utf-8', 'utf-8-sig', 'cp874', 'cp1252']:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    return f.read()
            except Exception:
                continue
        return ""

    CANONICAL_ENGINE_NAMES = {
        'Unreal_Engine_5': 'Unreal Engine 5',
        'Unreal_Engine_4': 'Unreal Engine 4',
        'Unreal_Engine_3': 'Unreal Engine 3',
        'Unreal_Engine_2': 'Unreal Engine 2',
        'CryEngine': 'CryEngine',
        'Decima_Engine': 'Decima Engine',
        'Northlight_Engine': 'Northlight Engine',
        'Northlight': 'Northlight Engine',
        '4A_Engine': '4A Engine',
        'C_Engine': 'C-Engine',
        'Disrupt_Engine': 'Disrupt Engine',
        'Disrupt': 'Disrupt Engine',
        'Dunia_Engine': 'Dunia Engine',
        'Scimitar_Engine': 'Scimitar Engine',
        'AnvilNext': 'AnvilNext',
        'Frostbite': 'Frostbite',
        'RE_Engine': 'RE Engine',
        'MT_Framework': 'MT Framework',
        'REDengine': 'REDengine',
        'Crate_Engine': 'Crate Engine',
        'Aurora_Engine': 'Aurora Engine',
        'Odyssey_Engine': 'Odyssey Engine',
        'id_Tech_7': 'id Tech 7',
        'id_Tech_6': 'id Tech 6',
        'id_Tech_3': 'id Tech 3',
        'id_Tech': 'id Tech',
        'Gust_Engine': 'Katana / Gust',
        'PlatinumGames_Engine': 'PlatinumGames',
        'Crystal_Dynamics_Foundation_Engine': 'Crystal Dynamics Foundation Engine',
        'Crystal Dynamics Foundation Engine': 'Crystal Dynamics Foundation Engine',
        'Asura_Engine': 'Asura Engine',
        'Marvelous_Engine': 'Marvelous Engine',
        'Visceral_Engine': 'Visceral Engine',
        'Dawn_Engine': 'Dawn Engine',
        'STEM_Engine': 'STEM Engine',
        'Evolution_Engine': 'Evolution Engine',
        'FLEDGE_Engine': 'FLEDGE Engine',
        'Glacier_Engine': 'Glacier Engine',
        'Source_Engine': 'Source Engine',
        'RAGE_Engine': 'RAGE Engine',
        'Snowdrop': 'Snowdrop',
        'Quantic Dream Engine': 'Quantic Dream Engine',
        'Godot': 'Godot',
        'GameMaker_Studio': 'GameMaker',
        'Void Engine': 'Void Engine',
        'Unity': 'Unity',
        '10tons_Engine': '10tons Engine',
        'Asobo_Engine': 'Asobo Engine',
        'Blizzard_Engine': 'Blizzard Engine',
        'Classic_RE': 'Classic RE',
        'Essence_Engine': 'Essence Engine',
        'FalcomEngine': 'Falcom Engine',
        'Gamebryo': 'Gamebryo',
        'Genome_Engine': 'Genome Engine',
        'Illusion_Engine': 'Illusion Engine',
        'KT_Engine': 'KT Engine',
        'LEAD_Engine': 'LEAD Engine',
        'Luminous_Engine': 'Luminous Engine',
        'RenPy': 'RenPy',
        'Custom_Engine': 'Custom Engine'
    }

    @classmethod
    def get_canonical_engine_name(cls, folder_or_name):
        """Translates an engine folder or dirty string into its canonical display badge."""
        if not folder_or_name:
            return "Custom Engine"
        try:
            from core.engine_database import EngineDatabase
            res = EngineDatabase.normalize_name(folder_or_name)
            if res and res != "Custom Engine":
                return res
        except Exception:
            pass
        name_str = str(folder_or_name).strip()
        if name_str in cls.CANONICAL_ENGINE_NAMES:
            return cls.CANONICAL_ENGINE_NAMES[name_str]
        clean_key = name_str.replace(" ", "_")
        if clean_key in cls.CANONICAL_ENGINE_NAMES:
            return cls.CANONICAL_ENGINE_NAMES[clean_key]
        for k, v in cls.CANONICAL_ENGINE_NAMES.items():
            if k.lower() == clean_key.lower() or v.lower() == name_str.lower():
                return v
        return name_str.replace("_Engine", " Engine").replace("_", " ")

    def find_exact_bible_by_title(self, title, engine_name=None):
        """
        High-precision matcher that finds the exact Game Bible for a given game title.
        Returns a rich metadata dict with bible path, recommended tools, and file formats,
        or None if no confident match exists.
        """
        if not title or len(str(title).strip()) < 2:
            return None

        catalog = self._catalog
        title_cache, index = catalog[3], catalog[0]
        clean_query = str(title).strip()
        cache_key = (clean_query.lower(), (engine_name or "").lower())
        if cache_key in title_cache:
            return title_cache[cache_key]

        candidates = []
        for item in index:
            score = self._score_game_match(clean_query, item, engine_name)
            if score >= 60:
                candidates.append((score, item))

        if not candidates:
            clean_str = re.sub(r'[^a-z0-9]', '', self._clean_text(clean_query).lower())
            if len(clean_str) >= 4:
                for item in index:
                    g_clean = re.sub(r'[^a-z0-9]', '', self._clean_text(item.get("game") or "").lower())
                    f_clean = re.sub(r'[^a-z0-9]', '', self._clean_text(item.get("game_folder") or "").lower())
                    t_clean = re.sub(r'[^a-z0-9]', '', self._clean_text(item.get("title") or "").lower())
                    if clean_str == g_clean or clean_str == f_clean or (len(g_clean) >= 4 and clean_str in g_clean):
                        candidates.append((85, item))
                    elif len(t_clean) >= 6 and clean_str in t_clean and "bible" in t_clean:
                        candidates.append((70, item))

        if not candidates:
            if title_cache is not None:
                title_cache[cache_key] = None
            return None

        candidates.sort(key=lambda x: -x[0])
        best_score, best_item = candidates[0]

        # Extract tools and extensions
        tags = best_item.get("tags") or set()
        tools = [t for t in [
            "QuickBMS", "repak", "FModel", "UnrealLocres", "UABEA", "AssetStudio", "UnityPy",
            "REFramework", "REE.PAK.Tool", "WolvenKit", "Kotor Tool", "TLK Editor", "OpenJK",
            "UndertaleModTool", "CriPakTools", "Frosty Editor", "AnvilToolkit", "Gibbed",
            "Asura Extractor", "ARC Tool", "GDRE Tools", "Flagrum", "TStudio", "TRun"
        ] if t.lower() in tags or any(t.lower() in str(x).lower() for x in tags)]
        if not tools:
            tools = ["TStudio", "TRun"]

        valid_exts = [f".{t}" for t in tags if t in (
            "pak", "locres", "upk", "bundle", "assets", "arc", "cpk", "rpack", "pck", "asr",
            "bigfile", "bif", "tlk", "msg", "pk3", "vpk", "forge", "fat", "dat", "bin", "ucas", "utoc", "rpkg", "rpf"
        )]

        eng_folder = best_item.get("engine_folder", "")
        eng_display = best_item.get("engine", "")
        canonical_engine = self.get_canonical_engine_name(eng_folder or eng_display)

        # Ensure raw_item is JSON serializable
        clean_raw_item = {k: (sorted(list(v)) if isinstance(v, set) else v) for k, v in best_item.items()}

        result = {
            "found": True,
            "bible_title": best_item["title"],
            "bible_path": best_item["path"],
            "rel_path": best_item["rel_path"],
            "game_name": best_item.get("game") or best_item.get("game_folder") or clean_query,
            "engine_name": canonical_engine,
            "engine_badge": canonical_engine,
            "recommended_tools": tools,
            "file_extensions": valid_exts,
            "confidence": best_score,
            "raw_item": clean_raw_item
        }

        if title_cache is not None:
            title_cache[cache_key] = result
        return result

    def get_all_engine_names(self):
        """Returns all registered canonical engine names, ordered by game count."""
        engine_counts = {}
        for eng in self.get_engines():
            c_name = self.get_canonical_engine_name(eng["folder"])
            engine_counts[c_name] = engine_counts.get(c_name, 0) + eng["total_games"]
        # Add remaining known canonical names
        try:
            from core.engine_database import EngineDatabase
            for c_name in EngineDatabase.get_known_engine_names():
                if c_name not in engine_counts:
                    engine_counts[c_name] = 0
        except Exception:
            for c_name in self.CANONICAL_ENGINE_NAMES.values():
                if c_name not in engine_counts:
                    engine_counts[c_name] = 0
        return [e[0] for e in sorted(engine_counts.items(), key=lambda x: (-x[1], x[0]))]

    def find_matching_bible(self, game_title, engine_name=None):
        """Instance alias for find_exact_bible_by_title."""
        return self.find_exact_bible_by_title(game_title, engine_name=engine_name)

    @classmethod
    def find_matching_bible_class(cls, game_title, engine_name=None):
        """Classmethod helper to find matching bible using singleton instance."""
        return cls.get_instance().find_exact_bible_by_title(game_title, engine_name=engine_name)

    # Class-level alias
    find_matching_bible = find_matching_bible_class
