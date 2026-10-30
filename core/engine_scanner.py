# -*- coding: utf-8 -*-
import os
import re
import threading
class _LazyEngineDatabaseProxy:
    """Transparent lazy proxy so EngineDatabase.* works everywhere without startup overhead."""
    _target = None

    @classmethod
    def _get_target(cls):
        if cls._target is None:
            from core.engine_database import EngineDatabase
            cls._target = EngineDatabase
        return cls._target

    def __getattr__(self, name):
        return getattr(self._get_target(), name)

EngineDatabase = _LazyEngineDatabaseProxy()

def _get_engine_db():
    return EngineDatabase

class _LazyDict(dict):
    """Defers loading heavy engine dictionary data until first access."""
    def __init__(self, loader):
        super().__init__()
        self._loader = loader
        self._loaded = False
        self._load_lock = threading.RLock()

    def _ensure(self):
        if not self._loaded:
            with self._load_lock:
                if not self._loaded:
                    super().update(self._loader())
                    self._loaded = True

    def __getitem__(self, item):
        self._ensure()
        return super().__getitem__(item)

    def get(self, item, default=None):
        self._ensure()
        return super().get(item, default)

    def __contains__(self, item):
        self._ensure()
        return super().__contains__(item)

    def items(self):
        self._ensure()
        return super().items()

    def keys(self):
        self._ensure()
        return super().keys()

    def values(self):
        self._ensure()
        return super().values()

    def __iter__(self):
        self._ensure()
        return super().__iter__()

    def __len__(self):
        self._ensure()
        return super().__len__()

    def __repr__(self):
        self._ensure()
        return super().__repr__()

class _LazyList(list):
    """Defers loading heavy engine list data until first access."""
    def __init__(self, loader):
        super().__init__()
        self._loader = loader
        self._loaded = False
        self._load_lock = threading.RLock()

    def _ensure(self):
        if not self._loaded:
            with self._load_lock:
                if not self._loaded:
                    super().extend(self._loader())
                    self._loaded = True

    def __iter__(self):
        self._ensure()
        return super().__iter__()

    def __getitem__(self, item):
        self._ensure()
        return super().__getitem__(item)

    def __len__(self):
        self._ensure()
        return super().__len__()

    def __contains__(self, item):
        self._ensure()
        return super().__contains__(item)

    def __repr__(self):
        self._ensure()
        return super().__repr__()

class EngineScanner:
    """
    Multi-Tier High-Performance Game Engine Scanner (Master World Edition).
    Accurately identifies and analyzes 130+ game engines across the world.
    Seamlessly synchronizes with Modding-Knowledge and EngineDatabase (Lazy Loaded).
    """

    _cache = {}

    ENGINE_COLORS = _LazyDict(lambda: _get_engine_db().get_all_colors())
    ENGINE_DEFAULT_TOOLS = _LazyDict(lambda: _get_engine_db().get_all_tools())
    ENGINE_DEFAULT_EXTS = _LazyDict(lambda: _get_engine_db().get_all_exts())
    KNOWN_ENGINES = _LazyList(lambda: _get_engine_db().get_known_engine_names())

    @classmethod
    def normalize_engine_name(cls, name):
        """Converts any engine name or alias into its canonical clean name."""
        return _get_engine_db().normalize_name(name)

    @classmethod
    def get_engine_info(cls, name):
        """Retrieves full rich metadata dictionary for the specified engine."""
        return _get_engine_db().get_engine(name)

    @classmethod
    def get_known_engines(cls):
        """Dynamically merges known canonical engines with any discovered in Modding-Knowledge."""
        try:
            from core.knowledge_service import KnowledgeService
            dynamic = KnowledgeService.get_instance().get_all_engine_names()
            merged = []
            for n in cls.KNOWN_ENGINES:
                c = cls.normalize_engine_name(n)
                if c not in merged:
                    merged.append(c)
            for n in dynamic:
                c = cls.normalize_engine_name(n)
                if c not in merged:
                    merged.append(c)
            return merged
        except Exception:
            return cls.KNOWN_ENGINES

    TITLE_HEURISTICS = [
        # 1. FromSoftware / Soulsborne
        (["elden ring", "shadow of the erdtree", "dark souls", "bloodborne", "sekiro", "armored core", "demon's souls", "demons souls"], "FromSoftware Proprietary"),
        # 2. Bethesda Game Studios
        (["starfield"], "Creation Engine 2"),
        (["skyrim", "fallout 4", "fallout 76"], "Creation Engine"),
        (["fallout 3", "fallout new vegas", "new vegas", "oblivion", "morrowind"], "Gamebryo"),
        # 3. Larian Studios
        (["baldur's gate 3", "baldurs gate 3", "bg3", "divinity original sin", "original sin 2"], "Divinity Engine"),
        # 4. Paradox Grand Strategy
        (["crusader kings", "hearts of iron", "stellaris", "europa universalis", "victoria 3", "imperator rome"], "Clausewitz Engine"),
        # 5. Valve Corporation
        (["counter-strike 2", "cs2", "half-life: alyx", "dota 2"], "Source 2"),
        (["half-life 2", "portal 2", "portal 1", "left 4 dead", "team fortress 2", "cs:go", "counter-strike: global offensive", "titanfall", "apex legends"], "Source Engine"),
        (["half-life 1", "counter-strike 1.6", "day of defeat"], "GoldSrc"),
        # 6. Sony First-Party PC Ports
        (["spider-man", "spiderman", "miles morales", "ratchet & clank", "rift apart"], "Insomniac Engine"),
        (["last of us", "tlou", "uncharted"], "Naughty Dog Proprietary"),
        (["ghost of tsushima", "ghost of yotei"], "Sucker Punch Engine"),
        (["god of war", "ragnarok"], "Santa Monica Engine"),
        (["death stranding", "horizon zero dawn", "horizon forbidden west", "killzone"], "Decima Engine"),
        (["gran turismo"], "Polyphony Digital Engine"),
        # 7. Sega / Ryu Ga Gotoku Studio
        (["like a dragon", "judgment", "lost judgment", "yakuza 6", "yakuza: like a dragon", "infinite wealth", "the man who erased his name"], "Dragon Engine"),
        (["yakuza 0", "yakuza kiwami", "yakuza 3", "yakuza 4", "yakuza 5"], "Old Yakuza Engine"),
        (["total war", "warhammer 3", "three kingdoms"], "TW Engine"),
        # 8. Koei Tecmo / Team Ninja / Omega Force / Gust
        (["nioh", "wo long", "rise of the ronin", "ninja gaiden", "stranger of paradise"], "Team Ninja Engine"),
        (["dynasty warriors", "samurai warriors", "warriors orochi", "fate/samurai remnant", "persona 5 strikers"], "KT Engine"),
        (["atelier ryza", "atelier sophie", "atelier yumia", "atelier", "blue reflection", "nights of azure"], "Katana / Gust"),
        # 9. Nihon Falcom
        (["trails of cold steel", "trails from zero", "trails to azure", "trails into reverie", "trails through daybreak", "ys viii", "ys ix", "ys x", "ys origin", "ys: the oath"], "Falcom Engine"),
        # 10. Square Enix
        (["final fantasy xv", "ffxv", "forspoken"], "Luminous Engine"),
        (["final fantasy xiii", "ffxiii", "lightning returns"], "Crystal Tools"),
        (["final fantasy vii remake", "ff7r", "ffvii remake", "kingdom hearts 3"], "Unreal Engine 4"),
        (["nier replicant"], "Toylogic Engine"),
        (["nier automata", "bayonetta", "metal gear rising"], "PlatinumGames"),
        (["bravely default"], "Silicon Studio Engine"),
        # 11. Bandai Namco / CyberConnect2
        (["naruto shippuden", "ultimate ninja storm", "dragon ball z: kakarot", "demon slayer"], "NuLibrary"),
        # 12. Capcom
        (["resident evil 2", "resident evil 3", "resident evil 4", "resident evil 7", "resident evil 8", "resident evil village", "monster hunter rise", "monster hunter wilds", "dragons dogma 2", "dragon's dogma 2", "devil may cry 5", "street fighter 6", "kunitsu-gami"], "RE Engine"),
        (["monster hunter world", "dragon's dogma", "dragons dogma", "ddda", "resident evil 5", "resident evil 6", "devil may cry 4", "mega man x", "dead rising"], "MT Framework"),
        (["resident evil 1", "biohazard 2", "biohazard 3"], "Classic RE"),
        # 13. CD Projekt RED
        (["witcher 3", "cyberpunk", "witcher 2"], "REDengine"),
        (["the witcher: enhanced", "the witcher 1", "witcher enhanced", "neverwinter nights 1"], "Aurora Engine"),
        (["neverwinter nights 2", "nwn2"], "Electron Engine"),
        (["knights of the old republic", "swkotor", "kotor"], "Odyssey Engine"),
        (["baldurs gate 1", "baldur's gate 2", "icewind dale", "planescape torment"], "Infinity Engine"),
        # 14. Techland
        (["dying light 2"], "C-Engine"),
        (["dying light", "call of juarez", "dead island"], "Chrome Engine"),
        # 15. 4A Games
        (["metro 2033", "metro last light", "metro exodus", "metro redux"], "4A Engine"),
        # 16. Remedy Entertainment
        (["alan wake 2", "control", "quantum break"], "Northlight Engine"),
        (["alan wake", "max payne"], "Remedy Engine"),
        # 17. Ubisoft
        (["assassin's creed", "assassins creed", "rainbow six siege", "immortals fenyx rising", "for honor"], "Ubisoft Anvil"),
        (["far cry"], "Dunia Engine"),
        (["watch dogs", "watch_dogs"], "Disrupt Engine"),
        (["the division", "avatar: frontiers of pandora", "star wars outlaws", "south park: the fractured"], "Snowdrop"),
        (["beyond good & evil", "beyond good and evil", "prince of persia"], "Jade Engine"),
        (["splinter cell: conviction", "splinter cell: blacklist"], "LEAD Engine"),
        # 18. Rockstar Games
        (["grand theft auto v", "gta v", "gta 5", "red dead redemption", "rdr2", "rdr 2", "max payne 3"], "RAGE Engine"),
        (["gta san andreas", "gta vice city", "gta iii", "burnout"], "RenderWare"),
        # 19. EA DICE / Frostbite / Visceral
        (["dead space remake", "battlefield", "dragon age: inquisition", "dragon age inquisition", "mass effect: andromeda"], "Frostbite"),
        (["dead space 1", "dead space 2", "dead space 3", "dante's inferno"], "Visceral Engine"),
        # 20. IO Interactive
        (["hitman", "kane & lynch", "freedom fighters"], "Glacier Engine"),
        # 21. Rebellion Developments
        (["sniper elite", "zombie army", "evil genius 2"], "Asura Engine"),
        # 22. Crystal Dynamics / Eidos
        (["tomb raider", "rise of the tomb raider", "shadow of the tomb raider", "deus ex human revolution"], "Foundation Engine"),
        (["deus ex mankind divided"], "Dawn Engine"),
        # 23. Crytek
        (["crysis", "kingdom come", "hunt showdown", "sniper ghost warrior contracts"], "CryEngine"),
        # 24. Activision / Infinity Ward
        (["call of duty", "modern warfare", "warzone", "black ops"], "IW Engine"),
        # 25. Saber Interactive
        (["space marine 2", "spacemarine 2", "world war z", "snowrunner", "mudrunner"], "Saber Engine"),
        # 26. Asobo Studio
        (["a plague tale", "plague tale", "flight simulator"], "Asobo Engine"),
        # 27. Crate Entertainment
        (["grim dawn", "titan quest"], "Crate Engine"),
        # 28. 10tons Ltd
        (["dysmantle", "tesla vs lovecraft", "undead horde"], "10tons Engine"),
        # 29. Deck13
        (["the surge", "atlas fallen", "lords of the fallen"], "FLEDGE Engine"),
        # 30. Piranha Bytes
        (["elex", "risen", "gothic 3"], "Genome Engine"),
        (["gothic 1", "gothic 2"], "ZenGin"),
        # 31. Monolith Productions
        (["f.e.a.r.", "fear 1", "fear 2", "condemned"], "LithTech"),
        (["shadow of mordor", "shadow of war"], "Firefly Engine"),
        # 32. Spiders
        (["greedfall", "steelrising", "the technomancer"], "Silk Engine"),
        # 33. Volition
        (["saints row", "red faction guerrila"], "Iron Engine"),
        # 34. Bungie / 343 Industries
        (["halo combat evolved", "halo 2", "halo 3", "halo reach"], "Blam Engine"),
        (["destiny 2", "destiny 1"], "Tiger Engine"),
        (["halo infinite"], "Slipspace Engine"),
        # 35. Telltale Games
        (["walking dead", "wolf among us", "tales from the borderlands", "batman the telltale"], "Telltale Tool"),
        # 36. Overkill Software
        (["payday 2", "payday: the heist"], "Diesel Engine"),
        # 37. Hello Games
        (["no man's sky", "no mans sky"], "Hello Games Engine"),
        # 38. Blizzard Entertainment
        (["warcraft 3", "warcraft iii", "starcraft 2", "overwatch", "diablo iv", "diablo 4"], "Blizzard Engine"),
        # 39. Visual Novels / Adventure / Indie
        (["doki doki literature club", "ddlc", "slay the princess"], "RenPy"),
        (["omori", "to the moon", "fear & hunger", "lisa the painful"], "RPG Maker"),
        (["mad father", "misao", "witch's house"], "Wolf RPG Editor"),
        (["fate/stay night", "tsukihime", "witch on the holy night"], "Kirikiri"),
        (["higurashi", "umineko"], "NScripter"),
        (["clannad", "summer pockets", "little busters", "angel beats"], "SiglusEngine"),
        (["grisaia no kajitsu", "fruit of grisaia"], "CatSystem2"),
        (["gemini rue", "kathy rain", "blackwell"], "Adventure Game Studio"),
        (["monkey island", "day of the tentacle"], "SCUMM"),
        (["duke nukem 3d", "blood", "ion fury"], "Build Engine"),
        (["stardew valley", "terraria", "celeste", "bastion", "transistor"], "MonoGame / XNA"),
        (["balatro"], "Love2D"),
        (["slay the spire"], "Java / LibGDX"),
        (["plants vs zombies", "plants vs. zombies", "peggle"], "PopCap Framework"),
        (["shovel knight"], "Yacht Club Engine"),
        (["eastward"], "Pixpil Engine"),
        (["battle realms"], "Liquid Engine"),
        (["hades"], "Custom Engine"),
        (["noita"], "Custom Engine"),
        (["undertale", "deltarune", "katana zero", "hotline miami", "pizza tower"], "GameMaker"),
        (["brotato", "buckshot roulette", "halls of torment", "cassette beasts"], "Godot"),
        (["black myth wukong", "black myth: wukong", "stalker 2", "silent hill 2 remake", "tekken 8"], "Unreal Engine 5"),
        (["hollow knight", "cuphead", "valheim", "subnautica", "genshin impact", "dave the diver", "sea of stars", "cult of the lamb", "tunic"], "Unity"),
    ]

    @classmethod
    def get_engine_color(cls, engine_name):
        """Returns standard hex color for the specified engine."""
        norm = cls.normalize_engine_name(engine_name)
        if norm in cls.ENGINE_COLORS:
            return cls.ENGINE_COLORS[norm]
        info = _get_engine_db().get_engine(engine_name)
        return info.get("color", "#38bdf8")

    @classmethod
    def detect_engine(cls, game_dir="", workspace_dir="", title="", saved_engine=None):
        """
        Multi-tier detection pipeline:
        1. Saved/Explicit engine
        2. Game directory scan (depth 0, 1, 2)
        3. Workspace directory scan
        4. Modding-Knowledge Bible match (checks 355+ bibles & 130+ engines)
        5. Title heuristics lookup
        6. Fallback to 'Custom Engine' (guaranteed non-empty badge)
        """
        candidate_title = title.strip() if title else ""
        if not candidate_title and game_dir:
            candidate_title = os.path.basename(os.path.normpath(game_dir))

        from core.knowledge_service import KnowledgeService
        knowledge = KnowledgeService._instance
        generation = knowledge.generation if knowledge is not None else 0
        cache_key = (game_dir, workspace_dir, candidate_title, saved_engine, generation)
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        # Tier 1: Saved Engine
        if saved_engine and saved_engine.strip():
            eng = cls.normalize_engine_name(saved_engine.strip())
            info = _get_engine_db().get_engine(eng)
            res = {
                "detected": True,
                "engine_name": eng,
                "badge": eng,
                "badge_color": cls.get_engine_color(eng),
                "tier": "saved",
                "tools": info.get("recommended_tools") or cls.ENGINE_DEFAULT_TOOLS.get(eng, ["TStudio", "TRun"]),
                "detected_exts": info.get("text_formats") or cls.ENGINE_DEFAULT_EXTS.get(eng, []),
                "info": info
            }
            if candidate_title:
                try:
                    from core.knowledge_service import KnowledgeService
                    b_match = KnowledgeService.get_instance().find_exact_bible_by_title(candidate_title, engine_name=eng)
                    if b_match:
                        res["bible"] = b_match
                except Exception:
                    pass
            cls._cache[cache_key] = res
            return res

        res = None

        # Tier 2: Game Directory Deep Scan
        if game_dir and os.path.exists(game_dir):
            res = cls._scan_game_dir(game_dir)

        # Tier 3: Workspace Directory Inspection
        if not res and workspace_dir and os.path.exists(workspace_dir):
            res = cls._scan_workspace(workspace_dir)

        # Tier 4: Modding-Knowledge Bible Match
        bible_match = None
        if candidate_title:
            try:
                from core.knowledge_service import KnowledgeService
                scan_engine = res.get("engine_name") if res else None
                bible_match = KnowledgeService.get_instance().find_exact_bible_by_title(candidate_title, engine_name=scan_engine)
            except Exception:
                pass

        if not res and bible_match:
            b_engine = cls.normalize_engine_name(bible_match["engine_name"])
            info = EngineDatabase.get_engine(b_engine)
            res = {
                "detected": True,
                "engine_name": b_engine,
                "badge": b_engine,
                "badge_color": cls.get_engine_color(b_engine),
                "tier": "bible_knowledge",
                "bible": bible_match,
                "tools": bible_match.get("recommended_tools") or info.get("recommended_tools", ["TStudio", "TRun"]),
                "detected_exts": bible_match.get("file_extensions") or info.get("text_formats", []),
                "info": info
            }

        # Tier 5: Known Title Heuristics
        if not res and candidate_title:
            title_lower = candidate_title.lower()
            for keywords, raw_eng in cls.TITLE_HEURISTICS:
                if any(kw in title_lower for kw in keywords):
                    eng = cls.normalize_engine_name(raw_eng)
                    info = EngineDatabase.get_engine(eng)
                    res = {
                        "detected": True,
                        "engine_name": eng,
                        "badge": eng,
                        "badge_color": cls.get_engine_color(eng),
                        "tier": "heuristic",
                        "tools": info.get("recommended_tools", ["TStudio", "TRun"]),
                        "detected_exts": info.get("text_formats", []),
                        "info": info
                    }
                    break

        # Tier 6: Clean Fallback
        if not res:
            custom_info = EngineDatabase.get_engine("Custom Engine")
            res = {
                "detected": False,
                "engine_name": "Custom Engine",
                "badge": "Custom Engine",
                "badge_color": cls.ENGINE_COLORS.get("Custom Engine", "#94a3b8"),
                "tier": "fallback",
                "tools": custom_info.get("recommended_tools", ["TStudio", "TRun"]),
                "detected_exts": custom_info.get("text_formats", []),
                "info": custom_info
            }

        # If res exists without bible attached, attach bible if available
        if "bible" not in res and bible_match:
            res["bible"] = bible_match
        elif "bible" not in res and candidate_title:
            try:
                from core.knowledge_service import KnowledgeService
                b_match = KnowledgeService.get_instance().find_exact_bible_by_title(candidate_title, engine_name=res.get("engine_name"))
                if b_match:
                    res["bible"] = b_match
            except Exception:
                pass

        eng_name = res.get("engine_name", "Custom Engine")
        info = res.get("info") or EngineDatabase.get_engine(eng_name)
        res["info"] = info
        res.setdefault("tools", info.get("recommended_tools", ["TStudio", "TRun"]))
        res.setdefault("detected_exts", info.get("text_formats", []))

        cls._cache[cache_key] = res
        return res

    @classmethod
    def scan_directory(cls, game_dir):
        """Backwards compatibility wrapper for scan_directory."""
        return cls.detect_engine(game_dir=game_dir)

    @classmethod
    def _scan_game_dir(cls, game_dir):
        try:
            top_entries = set(os.listdir(game_dir))
            top_lower = {e.lower() for e in top_entries}

            # Immediate signatures in root
            # Unity
            if "unityplayer.dll" in top_lower or any(e.endswith("_data") for e in top_lower) or "gameassembly.dll" in top_lower:
                return {"detected": True, "engine_name": "Unity", "badge": "Unity", "badge_color": cls.get_engine_color("Unity"), "tier": "game_dir_root"}

            # Techland C-Engine
            if "ph" in top_lower or any("rwdi.dll" in e for e in top_lower):
                return {"detected": True, "engine_name": "C-Engine", "badge": "C-Engine", "badge_color": cls.get_engine_color("C-Engine"), "tier": "game_dir_root"}

            # CryEngine
            if "system.cfg" in top_lower or "crysystem.dll" in top_lower or "cryengine.dll" in top_lower or "engine.pak" in top_lower:
                return {"detected": True, "engine_name": "CryEngine", "badge": "CryEngine", "badge_color": cls.get_engine_color("CryEngine"), "tier": "game_dir_root"}

            # FromSoftware (Dantelion / Souls)
            if any(e.endswith(".bdt") for e in top_lower) or "gamepath.txt" in top_lower or any(e in top_lower for e in ("eldenring.exe", "darksoulsiii.exe", "sekiro.exe", "armoredcore6.exe")):
                return {"detected": True, "engine_name": "FromSoftware Proprietary", "badge": "FromSoftware Proprietary", "badge_color": cls.get_engine_color("FromSoftware Proprietary"), "tier": "game_dir_root"}

            # Bethesda Creation Engine 2 (Starfield)
            if "starfield.exe" in top_lower or any(e.endswith(".ba2") and "starfield" in e for e in top_lower):
                return {"detected": True, "engine_name": "Creation Engine 2", "badge": "Creation Engine 2", "badge_color": cls.get_engine_color("Creation Engine 2"), "tier": "game_dir_root"}

            # Bethesda Creation Engine (Skyrim / Fallout 4)
            if any(e.endswith(".ba2") for e in top_lower) or any(e in top_lower for e in ("skyrimse.exe", "skyrim.exe", "fallout4.exe", "fallout76.exe")):
                return {"detected": True, "engine_name": "Creation Engine", "badge": "Creation Engine", "badge_color": cls.get_engine_color("Creation Engine"), "tier": "game_dir_root"}

            # Larian Divinity Engine (Baldur's Gate 3)
            if any(e in top_lower for e in ("bg3.exe", "bg3_dx11.exe", "eocapp.exe")):
                return {"detected": True, "engine_name": "Divinity Engine", "badge": "Divinity Engine", "badge_color": cls.get_engine_color("Divinity Engine"), "tier": "game_dir_root"}

            # Valve Source 2
            if "cs2.exe" in top_lower or "hlvr.exe" in top_lower or ("tier0.dll" in top_lower and "engine2.dll" in top_lower):
                return {"detected": True, "engine_name": "Source 2", "badge": "Source 2", "badge_color": cls.get_engine_color("Source 2"), "tier": "game_dir_root"}

            # Valve Source Engine
            if "hl2.exe" in top_lower or "tier0.dll" in top_lower or "vstdlib.dll" in top_lower:
                return {"detected": True, "engine_name": "Source Engine", "badge": "Source Engine", "badge_color": cls.get_engine_color("Source Engine"), "tier": "game_dir_root"}

            # Scimitar / AnvilNext (Assassin's Creed, etc.)
            if any(e.endswith(".forge") for e in top_lower):
                return {"detected": True, "engine_name": "Ubisoft Anvil", "badge": "Ubisoft Anvil", "badge_color": cls.get_engine_color("Ubisoft Anvil"), "tier": "game_dir_root"}

            # 4A Engine (Metro series)
            if "content.vfs0" in top_lower or "4a.dll" in top_lower or any("metro" in e and e.endswith(".exe") for e in top_lower):
                return {"detected": True, "engine_name": "4A Engine", "badge": "4A Engine", "badge_color": cls.get_engine_color("4A Engine"), "tier": "game_dir_root"}

            # Crate Engine (Grim Dawn)
            if "database.arz" in top_lower or any(e == "grim dawn.exe" for e in top_lower):
                return {"detected": True, "engine_name": "Crate Engine", "badge": "Crate Engine", "badge_color": cls.get_engine_color("Crate Engine"), "tier": "game_dir_root"}

            # Glacier Engine (Hitman)
            if any(e.endswith(".rpkg") for e in top_lower) or any("hitman" in e and e.endswith(".exe") for e in top_lower):
                return {"detected": True, "engine_name": "Glacier Engine", "badge": "Glacier Engine", "badge_color": cls.get_engine_color("Glacier Engine"), "tier": "game_dir_root"}

            # RAGE Engine (Rockstar)
            if any(e.endswith(".rpf") for e in top_lower) or any(e in top_lower for e in ("gta5.exe", "rdr2.exe", "playrdr.exe", "maxpayne3.exe")):
                return {"detected": True, "engine_name": "RAGE Engine", "badge": "RAGE Engine", "badge_color": cls.get_engine_color("RAGE Engine"), "tier": "game_dir_root"}

            # Frostbite
            if any(e.endswith(".cas") for e in top_lower) or any(e.endswith(".toc") for e in top_lower) or "initfs_win32" in top_lower:
                return {"detected": True, "engine_name": "Frostbite", "badge": "Frostbite", "badge_color": cls.get_engine_color("Frostbite"), "tier": "game_dir_root"}

            # GameMaker
            if "data.win" in top_lower:
                return {"detected": True, "engine_name": "GameMaker", "badge": "GameMaker", "badge_color": cls.get_engine_color("GameMaker"), "tier": "game_dir_root"}

            # Ren'Py
            if "renpy" in top_lower or any(e.endswith(".rpa") for e in top_lower):
                return {"detected": True, "engine_name": "RenPy", "badge": "RenPy", "badge_color": cls.get_engine_color("RenPy"), "tier": "game_dir_root"}

            # Gust / Koei Tecmo
            if any(e.startswith("atelier_") for e in top_lower) or "motor" in top_lower:
                return {"detected": True, "engine_name": "Katana / Gust", "badge": "Katana / Gust", "badge_color": cls.get_engine_color("Katana / Gust"), "tier": "game_dir_root"}

            # id Tech
            if any(e.endswith(".pk3") for e in top_lower) or ("gamedata" in top_lower and "base" in top_lower):
                return {"detected": True, "engine_name": "id Tech 3", "badge": "id Tech 3", "badge_color": cls.get_engine_color("id Tech 3"), "tier": "game_dir_root"}

            # RE Engine
            if any(e.startswith("re_chunk_") for e in top_lower) or "reframework" in top_lower or any(e.endswith(".msg.22") or e.endswith(".msg") for e in top_lower):
                return {"detected": True, "engine_name": "RE Engine", "badge": "RE Engine", "badge_color": cls.get_engine_color("RE Engine"), "tier": "game_dir_root"}

            # MT Framework
            if "nativepc" in top_lower or "nativedx10" in top_lower:
                return {"detected": True, "engine_name": "MT Framework", "badge": "MT Framework", "badge_color": cls.get_engine_color("MT Framework"), "tier": "game_dir_root"}

            # Unreal Engine 3 (UPK / UDK)
            if any(e.endswith(".upk") for e in top_lower) or "cookedpcconsole" in top_lower or "cookedpc" in top_lower or "udkgame" in top_lower:
                return {"detected": True, "engine_name": "Unreal Engine 3", "badge": "Unreal Engine 3", "sub_engine": "UE3", "is_ue3": True, "badge_color": cls.get_engine_color("Unreal Engine 3"), "tier": "game_dir_root", "tools": ["TStudio", "TRun", "UDK MCP", "FModel"]}

            # Unreal Engine 5 / 4
            if any(e.endswith(".ucas") for e in top_lower) or any(e.endswith(".utoc") for e in top_lower):
                return {"detected": True, "engine_name": "Unreal Engine 5", "badge": "Unreal Engine 5", "badge_color": cls.get_engine_color("Unreal Engine 5"), "tier": "game_dir_root"}

            if "engine" in top_lower or any(e.startswith("pakchunk") for e in top_lower):
                return {"detected": True, "engine_name": "Unreal Engine 4", "badge": "Unreal Engine 4", "badge_color": cls.get_engine_color("Unreal Engine 4"), "tier": "game_dir_root"}

            # Godot
            if any(e.endswith(".pck") for e in top_lower):
                return {"detected": True, "engine_name": "Godot", "badge": "Godot", "badge_color": cls.get_engine_color("Godot"), "tier": "game_dir_root"}

            # Asura Engine
            if any(e.endswith(".asr") for e in top_lower):
                return {"detected": True, "engine_name": "Asura Engine", "badge": "Asura Engine", "badge_color": cls.get_engine_color("Asura Engine"), "tier": "game_dir_root"}

            # Foundation Engine / CDC
            if any(e.startswith("bigfile.") for e in top_lower):
                return {"detected": True, "engine_name": "Foundation Engine", "badge": "Foundation Engine", "badge_color": cls.get_engine_color("Foundation Engine"), "tier": "game_dir_root"}

            # Odyssey / Aurora
            if "chitin.key" in top_lower and "dialog.tlk" in top_lower:
                return {"detected": True, "engine_name": "Odyssey Engine", "badge": "Odyssey Engine", "badge_color": cls.get_engine_color("Odyssey Engine"), "tier": "game_dir_root"}

            # REDengine
            if "witcher3.exe" in top_lower or "cyberpunk2077.exe" in top_lower or "r6" in top_lower:
                return {"detected": True, "engine_name": "REDengine", "badge": "REDengine", "badge_color": cls.get_engine_color("REDengine"), "tier": "game_dir_root"}

            # PopCap
            if "main.pak" in top_lower and any("zombies" in e or "peggle" in e for e in top_lower):
                return {"detected": True, "engine_name": "PopCap Framework", "badge": "PopCap Framework", "badge_color": cls.get_engine_color("PopCap Framework"), "tier": "game_dir_root"}

            # Love2D
            if "love.dll" in top_lower or any(e.endswith(".love") for e in top_lower) or "balatro.exe" in top_lower:
                return {"detected": True, "engine_name": "Love2D", "badge": "Love2D", "badge_color": cls.get_engine_color("Love2D"), "tier": "game_dir_root"}

            # MonoGame / XNA
            if any(e.endswith(".xnb") for e in top_lower) or any(e in top_lower for e in ("stardew valley.exe", "terraria.exe", "celeste.exe")):
                return {"detected": True, "engine_name": "MonoGame / XNA", "badge": "MonoGame / XNA", "badge_color": cls.get_engine_color("MonoGame / XNA"), "tier": "game_dir_root"}

            # Level 1/2 subfolder check
            subdirs_to_check = [d for d in top_entries if os.path.isdir(os.path.join(game_dir, d))]
            for sub in subdirs_to_check[:25]:
                sub_path = os.path.join(game_dir, sub)
                sub_name_lower = sub.lower()

                if sub_name_lower in ("build", "bin", "binaries", "content", "data", "base", "motor", "disc", "ph", "gamedata", "nativepc", "database", "worlds", "data_win64", "package", "game", "assets", "r6"):
                    try:
                        sub_entries = {e.lower() for e in os.listdir(sub_path)}

                        # Sub C-Engine
                        if sub_name_lower == "ph" or any("rwdi.dll" in e for e in sub_entries):
                            return {"detected": True, "engine_name": "C-Engine", "badge": "C-Engine", "badge_color": cls.get_engine_color("C-Engine"), "tier": "game_dir_sub"}

                        # Sub Gust
                        if "root.rdb" in sub_entries or any(e.endswith(".fdata") for e in sub_entries) or any(e.startswith("pack0") for e in sub_entries):
                            return {"detected": True, "engine_name": "Katana / Gust", "badge": "Katana / Gust", "badge_color": cls.get_engine_color("Katana / Gust"), "tier": "game_dir_sub"}

                        # Sub Unity
                        if any(e.endswith("_data") for e in sub_entries) or "unityplayer.dll" in sub_entries:
                            return {"detected": True, "engine_name": "Unity", "badge": "Unity", "badge_color": cls.get_engine_color("Unity"), "tier": "game_dir_sub"}

                        # Sub CryEngine
                        if "system.cfg" in sub_entries or "engine.pak" in sub_entries or "crysystem.dll" in sub_entries:
                            return {"detected": True, "engine_name": "CryEngine", "badge": "CryEngine", "badge_color": cls.get_engine_color("CryEngine"), "tier": "game_dir_sub"}

                        # Sub FromSoftware
                        if any(e.endswith(".bdt") for e in sub_entries) or any(e.endswith(".msgbnd.dcx") for e in sub_entries):
                            return {"detected": True, "engine_name": "FromSoftware Proprietary", "badge": "FromSoftware Proprietary", "badge_color": cls.get_engine_color("FromSoftware Proprietary"), "tier": "game_dir_sub"}

                        # Sub Crate Engine
                        if "database.arz" in sub_entries:
                            return {"detected": True, "engine_name": "Crate Engine", "badge": "Crate Engine", "badge_color": cls.get_engine_color("Crate Engine"), "tier": "game_dir_sub"}

                        # Sub Scimitar / AnvilNext
                        if any(e.endswith(".forge") for e in sub_entries):
                            return {"detected": True, "engine_name": "Ubisoft Anvil", "badge": "Ubisoft Anvil", "badge_color": cls.get_engine_color("Ubisoft Anvil"), "tier": "game_dir_sub"}

                        # Sub Disrupt / Dunia Engine
                        if any(e.endswith(".fat") for e in sub_entries) and any(e.endswith(".dat") for e in sub_entries):
                            return {"detected": True, "engine_name": "Disrupt Engine", "badge": "Disrupt Engine", "badge_color": cls.get_engine_color("Disrupt Engine"), "tier": "game_dir_sub"}

                        # Sub 4A Engine
                        if "content.vfs0" in sub_entries:
                            return {"detected": True, "engine_name": "4A Engine", "badge": "4A Engine", "badge_color": cls.get_engine_color("4A Engine"), "tier": "game_dir_sub"}

                        # Sub Void Engine
                        if any(e.endswith(".sharedresources") for e in sub_entries):
                            return {"detected": True, "engine_name": "Void Engine", "badge": "Void Engine", "badge_color": cls.get_engine_color("Void Engine"), "tier": "game_dir_sub"}

                        # Sub id Tech
                        if any(e.endswith(".pk3") for e in sub_entries):
                            return {"detected": True, "engine_name": "id Tech 3", "badge": "id Tech 3", "badge_color": cls.get_engine_color("id Tech 3"), "tier": "game_dir_sub"}

                        # Sub Aurora
                        if any(e.endswith(".bif") for e in sub_entries) and any(e.endswith(".tlk") for e in sub_entries):
                            return {"detected": True, "engine_name": "Aurora Engine", "badge": "Aurora Engine", "badge_color": cls.get_engine_color("Aurora Engine"), "tier": "game_dir_sub"}

                        # Sub Asura
                        if any(e.endswith(".asr") for e in sub_entries):
                            return {"detected": True, "engine_name": "Asura Engine", "badge": "Asura Engine", "badge_color": cls.get_engine_color("Asura Engine"), "tier": "game_dir_sub"}

                        # Sub Marvelous
                        if any(e.endswith(".lzs") for e in sub_entries):
                            return {"detected": True, "engine_name": "Marvelous Engine", "badge": "Marvelous Engine", "badge_color": cls.get_engine_color("Marvelous Engine"), "tier": "game_dir_sub"}

                        # Sub Unreal (UE3 vs UE4 vs UE5)
                        if any(e.endswith(".upk") for e in sub_entries) or "cookedpcconsole" in sub_name_lower or "cookedpc" in sub_name_lower:
                            return {"detected": True, "engine_name": "Unreal Engine 3", "badge": "Unreal Engine 3", "sub_engine": "UE3", "is_ue3": True, "badge_color": cls.get_engine_color("Unreal Engine 3"), "tier": "game_dir_sub", "tools": ["TStudio", "TRun", "UDK MCP", "FModel"]}
                        if any(e.endswith(".ucas") for e in sub_entries) or any(e.endswith(".utoc") for e in sub_entries):
                            return {"detected": True, "engine_name": "Unreal Engine 5", "badge": "Unreal Engine 5", "badge_color": cls.get_engine_color("Unreal Engine 5"), "tier": "game_dir_sub"}
                        if any(e.endswith(".locres") for e in sub_entries) or "paks" in sub_entries or "win64" in sub_entries:
                            return {"detected": True, "engine_name": "Unreal Engine 4", "badge": "Unreal Engine 4", "badge_color": cls.get_engine_color("Unreal Engine 4"), "tier": "game_dir_sub"}
                    except Exception:
                        pass
        except Exception:
            pass
        return None

    @classmethod
    def _scan_workspace(cls, workspace_dir):
        try:
            check_dirs = ["00_Original", "01_Original_Backup", "02_Translation_Workspace", "05_Scripts_and_Tools", "06_Releases"]
            for cd in check_dirs:
                target = os.path.join(workspace_dir, cd)
                if not os.path.exists(target):
                    continue
                for root, dirs, files in os.walk(target):
                    rel = os.path.relpath(root, target)
                    depth = 0 if rel == "." else len(rel.split(os.sep))
                    dirs_lower = {d.lower() for d in dirs}
                    # Prune traversal at the supported depth, rather than enumerating
                    # the entire tree and discarding each deeper directory afterwards.
                    if depth >= 2:
                        dirs[:] = []
                    if depth > 2:
                        continue
                    files_lower = {f.lower() for f in files}

                    # C-Engine in workspace
                    if "ph" in dirs_lower or any(f.endswith(".rpack") for f in files_lower) or any("dyinglight" in f or "dl2" in f for f in files_lower):
                        return {"detected": True, "engine_name": "C-Engine", "badge": "C-Engine", "badge_color": cls.get_engine_color("C-Engine"), "tier": "workspace"}

                    # Unity in workspace
                    if "unityplayer.dll" in files_lower or any(f.endswith(".bundle") or f.endswith(".assets") for f in files_lower) or any(d.endswith("_data") for d in dirs_lower) or "bepinex" in dirs_lower or "xunity" in dirs_lower:
                        return {"detected": True, "engine_name": "Unity", "badge": "Unity", "badge_color": cls.get_engine_color("Unity"), "tier": "workspace"}

                    # CryEngine in workspace
                    if "system.cfg" in files_lower or "engine.pak" in files_lower:
                        return {"detected": True, "engine_name": "CryEngine", "badge": "CryEngine", "badge_color": cls.get_engine_color("CryEngine"), "tier": "workspace"}

                    # FromSoftware in workspace
                    if any(f.endswith(".bdt") or f.endswith(".fmg") or f.endswith(".msgbnd.dcx") for f in files_lower):
                        return {"detected": True, "engine_name": "FromSoftware Proprietary", "badge": "FromSoftware Proprietary", "badge_color": cls.get_engine_color("FromSoftware Proprietary"), "tier": "workspace"}

                    # Unreal Engine in workspace (UE3 vs UE4 vs UE5)
                    if any(f.endswith(".upk") for f in files_lower) or "cookedpcconsole" in dirs_lower:
                        return {"detected": True, "engine_name": "Unreal Engine 3", "badge": "Unreal Engine 3", "sub_engine": "UE3", "is_ue3": True, "badge_color": cls.get_engine_color("Unreal Engine 3"), "tier": "workspace", "tools": ["TStudio", "TRun", "UDK MCP", "FModel"]}
                    if any(f.endswith(".ucas") for f in files_lower) or any(f.endswith(".utoc") for f in files_lower):
                        return {"detected": True, "engine_name": "Unreal Engine 5", "badge": "Unreal Engine 5", "badge_color": cls.get_engine_color("Unreal Engine 5"), "tier": "workspace"}
                    if any(f.endswith(".locres") for f in files_lower) or "ue4ss" in dirs_lower or any(f.startswith("pakchunk") for f in files_lower):
                        return {"detected": True, "engine_name": "Unreal Engine 4", "badge": "Unreal Engine 4", "badge_color": cls.get_engine_color("Unreal Engine 4"), "tier": "workspace"}

                    # Scimitar / AnvilNext
                    if any(f.endswith(".forge") for f in files_lower):
                        return {"detected": True, "engine_name": "Ubisoft Anvil", "badge": "Ubisoft Anvil", "badge_color": cls.get_engine_color("Ubisoft Anvil"), "tier": "workspace"}

                    # Disrupt / Dunia
                    if any(f.endswith(".fat") for f in files_lower) and any(f.endswith(".dat") for f in files_lower):
                        return {"detected": True, "engine_name": "Disrupt Engine", "badge": "Disrupt Engine", "badge_color": cls.get_engine_color("Disrupt Engine"), "tier": "workspace"}

                    # 4A Engine
                    if any(f.endswith(".vfs0") for f in files_lower):
                        return {"detected": True, "engine_name": "4A Engine", "badge": "4A Engine", "badge_color": cls.get_engine_color("4A Engine"), "tier": "workspace"}

                    # Crate Engine
                    if any(f.endswith(".arz") for f in files_lower) or any(f.endswith(".arc") for f in files_lower):
                        return {"detected": True, "engine_name": "Crate Engine", "badge": "Crate Engine", "badge_color": cls.get_engine_color("Crate Engine"), "tier": "workspace"}

                    # Glacier Engine
                    if any(f.endswith(".rpkg") for f in files_lower):
                        return {"detected": True, "engine_name": "Glacier Engine", "badge": "Glacier Engine", "badge_color": cls.get_engine_color("Glacier Engine"), "tier": "workspace"}

                    # RAGE Engine
                    if any(f.endswith(".rpf") for f in files_lower):
                        return {"detected": True, "engine_name": "RAGE Engine", "badge": "RAGE Engine", "badge_color": cls.get_engine_color("RAGE Engine"), "tier": "workspace"}

                    # GameMaker
                    if "data.win" in files_lower:
                        return {"detected": True, "engine_name": "GameMaker", "badge": "GameMaker", "badge_color": cls.get_engine_color("GameMaker"), "tier": "workspace"}

                    # MT Framework in workspace
                    if any(f.endswith(".arc") for f in files_lower):
                        return {"detected": True, "engine_name": "MT Framework", "badge": "MT Framework", "badge_color": cls.get_engine_color("MT Framework"), "tier": "workspace"}

                    # Aurora in workspace
                    if any(f.endswith(".bif") for f in files_lower):
                        return {"detected": True, "engine_name": "Aurora Engine", "badge": "Aurora Engine", "badge_color": cls.get_engine_color("Aurora Engine"), "tier": "workspace"}

                    # Asura in workspace
                    if any(f.endswith(".asr") for f in files_lower):
                        return {"detected": True, "engine_name": "Asura Engine", "badge": "Asura Engine", "badge_color": cls.get_engine_color("Asura Engine"), "tier": "workspace"}

                    # CDC in workspace
                    if any(f.startswith("bigfile.") for f in files_lower):
                        return {"detected": True, "engine_name": "Foundation Engine", "badge": "Foundation Engine", "badge_color": cls.get_engine_color("Foundation Engine"), "tier": "workspace"}

                    # Marvelous in workspace
                    if any(f.endswith(".lzs") for f in files_lower):
                        return {"detected": True, "engine_name": "Marvelous Engine", "badge": "Marvelous Engine", "badge_color": cls.get_engine_color("Marvelous Engine"), "tier": "workspace"}
        except Exception:
            pass
        return None
