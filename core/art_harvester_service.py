import os
import re
import json
import shutil
import urllib.request
import urllib.parse
import subprocess
import difflib
import threading
import tempfile
from core.config_manager import ConfigManager
from PIL import Image

from core.steam_service import SteamService


class ArtHarvesterService:
    """
    Intelligent Multi-Source Artwork & Background Harvester:
    1. Sony PlayStation Store (PS5 4K / PS4 1080p official textless key art & backgrounds)
    2. Steam Store Official CDN (Hero 1920x620, Capsule, Screenshots, Wallpapers)
    3. Auto-Ranks and Sets the best 16:9 textless artwork as project cover (thub_cover.jpg)
    4. Saves all high-res assets to {workspace}/07_Image_Resources/Official_Art/
    """

    _harvest_lock = threading.Lock()
    _active_harvests = set()

    @staticmethod
    def _cancelled():
        """Honor owned Qt worker cancellation; ordinary Python callers remain supported."""
        try:
            from PyQt6.QtCore import QThread
            return QThread.currentThread().isInterruptionRequested()
        except (ImportError, RuntimeError):
            return False

    @classmethod
    def clean_game_title(cls, game_name: str) -> str:
        """Strips mod tags, edition suffixes, and bracketed noise to improve search matching."""
        if not game_name:
            return ""
        clean = re.sub(r'\[.*?\]|\(.*?\)|<.*?>|\{.*?\}|~.*?~', '', game_name)
        for term in [
            'Thai Mod', 'Thai Version', 'ม็อดภาษาไทย', 'ภาษาไทย', 'ม็อด', 'Mod',
            'Definitive Edition', 'Remastered', 'Remaster', 'GOTY', 'Game of the Year',
            'Enhanced Edition', 'Director\'s Cut'
        ]:
            clean = re.sub(rf'(?i)\b{re.escape(term)}\b', '', clean)
        clean = re.sub(r'[_\-]+', ' ', clean)
        clean = ' '.join(clean.split()).strip()
        return clean or game_name.strip()

    @classmethod
    def _find_browser_exe(cls) -> str:
        """Finds Microsoft Edge or Google Chrome executable for headless web queries."""
        candidates = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return ""

    # =========================================================================
    # 1. Sony PlayStation Store (PS5 / PS4) Harvester
    # =========================================================================
    @classmethod
    def harvest_sony_playstation_assets(cls, game_name: str, target_dir: str) -> list:
        """
        Extracts pristine, official 4K/1080p textless key art and backgrounds from
        Sony's official CDN (image.api.playstation.com) via PlayStation Store GraphQL API.
        """
        if not game_name or not target_dir or cls._cancelled():
            return []

        os.makedirs(target_dir, exist_ok=True)
        clean_q = cls.clean_game_title(game_name)
        browser_exe = cls._find_browser_exe()
        if not browser_exe:
            print("[ArtHarvester] Headless browser not found, skipping PS Store search.")
            return []

        # 1. Search PlayStation Store
        encoded = urllib.parse.quote(clean_q)
        url = f"https://store.playstation.com/en-us/search/{encoded}"
        cmd = [
            browser_exe,
            "--headless=new",
            "--disable-gpu",
            "--virtual-time-budget=4000",
            "--dump-dom",
            url
        ]
        try:
            if cls._cancelled():
                return []
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=14,
                                  creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            html = proc.stdout or ""
        except Exception as e:
            print(f"[ArtHarvester] PS Store search failed: {e}")
            return []

        if cls._cancelled():
            return []

        # 2. Extract product IDs and fuzzy-rank matches
        items = re.findall(r'<a[^>]+href="(/en-us/product/([^"]+))"[^>]*>(.*?)</a>', html, re.DOTALL)
        candidates = []
        seen = set()
        for _, prod_id, content in items:
            if prod_id in seen:
                continue
            seen.add(prod_id)
            text = re.sub(r'<[^>]+>', ' ', content)
            text = ' '.join(text.split()).strip()
            if text:
                clean_t = text.replace('®', '').replace('™', '').strip()
                score = difflib.SequenceMatcher(None, clean_q.lower(), clean_t.lower()).ratio()
                candidates.append((score, prod_id, clean_t))

        if not candidates:
            return []

        candidates.sort(key=lambda x: x[0], reverse=True)
        best_match = candidates[0]
        if best_match[0] < 0.45:
            # Fallback check: see if query words are in title
            q_words = [w for w in clean_q.lower().split() if len(w) > 2]
            best_match = None
            for s, pid, ct in candidates:
                if any(w in ct.lower() for w in q_words):
                    best_match = (s, pid, ct)
                    break
            if not best_match:
                return []

        best_prod_id = best_match[1]
        print(f"[ArtHarvester] Matched Sony PS Store: '{best_match[2]}' -> {best_prod_id}")

        # 3. Query Sony GraphQL for official high-resolution media
        base_url = 'https://web.np.playstation.com/api/graphql/v1/op'
        params = {
            'operationName': 'metGetProductById',
            'variables': json.dumps({'productId': best_prod_id}),
            'extensions': json.dumps({
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': 'a128042177bd93dd831164103d53b73ef790d56f51dae647064cb8f9d9fc9d1a'
                }
            })
        }
        api_url = base_url + '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(api_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'x-psn-store-locale-override': 'en-US',
            'content-type': 'application/json'
        })

        saved_files = []
        if cls._cancelled():
            return saved_files
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                prod = data.get('data', {}).get('productRetrieve', {})
                media_list = prod.get('media', [])
                concept_id = prod.get('concept', {}).get('id')

                # Download media
                for m in media_list:
                    if cls._cancelled():
                        return saved_files
                    role = m.get('role', '')
                    murl = m.get('url', '')
                    if not murl or m.get('type') != 'IMAGE':
                        continue

                    target_name = None
                    source_label = "Sony PlayStation"
                    score = 50

                    if role == 'GAMEHUB_COVER_ART':
                        target_name = 'ps5_gamehub_cover_art_3840x2160.jpg'
                        source_label = 'Sony PS5 (4K Key Art)'
                        score = 110
                    elif role == 'BACKGROUND':
                        target_name = 'ps4_ps5_background_1920x1080.jpg'
                        source_label = 'Sony PS4/PS5 (Background)'
                        score = 105
                    elif role == 'SIXTEEN_BY_NINE_BANNER':
                        target_name = 'ps5_16x9_banner.jpg'
                        source_label = 'Sony PS5 (16:9 Banner)'
                        score = 100
                    elif role == 'EDITION_KEY_ART':
                        target_name = 'ps5_edition_key_art.jpg'
                        source_label = 'Sony PS5 (Edition Art)'
                        score = 90
                    elif role == 'LOGO':
                        target_name = 'official_ps_logo.png'
                        source_label = 'Sony Official Logo (PNG)'
                        score = 40

                    if target_name:
                        dest = os.path.join(target_dir, target_name)
                        if not os.path.exists(dest) or os.path.getsize(dest) < 1000:
                            cls._download_file(murl, dest)
                        if os.path.exists(dest) and os.path.getsize(dest) > 1000:
                            w, h = cls._get_image_dims(dest)
                            saved_files.append({
                                "path": dest,
                                "filename": target_name,
                                "source": source_label,
                                "role": role,
                                "width": w,
                                "height": h,
                                "score": score
                            })

                # If concept_id exists, fetch screenshots
                if concept_id and not cls._cancelled():
                    c_params = {
                        'operationName': 'conceptRetrieveForMedia',
                        'variables': json.dumps({'conceptId': str(concept_id)}),
                        'extensions': json.dumps({
                            'persistedQuery': {
                                'version': 1,
                                'sha256Hash': '615a2c4618229aa2f11c10fe497eaf4fdc151e4dcc0b6b82e154aeacb0123c2d'
                            }
                        })
                    }
                    c_url = base_url + '?' + urllib.parse.urlencode(c_params)
                    c_req = urllib.request.Request(c_url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                        'x-psn-store-locale-override': 'en-US',
                        'content-type': 'application/json'
                    })
                    try:
                        with urllib.request.urlopen(c_req, timeout=10) as c_resp:
                            c_data = json.loads(c_resp.read().decode('utf-8'))
                            dp = c_data.get('data', {}).get('conceptRetrieve', {}).get('defaultProduct', {})
                            ss_idx = 1
                            for cm in dp.get('media', []):
                                if cls._cancelled():
                                    return saved_files
                                if cm.get('role') == 'SCREENSHOT' and cm.get('type') == 'IMAGE':
                                    ss_url = cm.get('url', '')
                                    ss_name = f'ps5_screenshot_{ss_idx}.jpg'
                                    ss_dest = os.path.join(target_dir, ss_name)
                                    if not os.path.exists(ss_dest) or os.path.getsize(ss_dest) < 1000:
                                        cls._download_file(ss_url, ss_dest)
                                    if os.path.exists(ss_dest) and os.path.getsize(ss_dest) > 1000:
                                        w, h = cls._get_image_dims(ss_dest)
                                        saved_files.append({
                                            "path": ss_dest,
                                            "filename": ss_name,
                                            "source": "Sony PS5 (Official Screenshot)",
                                            "role": "SCREENSHOT",
                                            "width": w,
                                            "height": h,
                                            "score": 75
                                        })
                                    ss_idx += 1
                                    if ss_idx > 6:
                                        break
                    except Exception as ce:
                        print(f"[ArtHarvester] PS concept screenshots notice: {ce}")

        except Exception as e:
            print(f"[ArtHarvester] PS GraphQL query error: {e}")

        return saved_files

    # =========================================================================
    # 2. Steam Official CDN Harvester
    # =========================================================================
    @classmethod
    def harvest_steam_assets(cls, game_name: str, target_dir: str) -> list:
        """
        Discovers and downloads Steam Store official high-resolution assets:
        - banner_hero_1920x620.jpg
        - cover_landscape_616x353.jpg
        - cover_portrait_600x900.jpg
        - cover_header_460x215.jpg
        - official_logo.png
        """
        if not game_name or not target_dir or cls._cancelled():
            return []

        os.makedirs(target_dir, exist_ok=True)
        appid, actual_name = SteamService.search_game_appid(game_name)
        if not appid or cls._cancelled():
            return []

        print(f"[ArtHarvester] Matched Steam Store: '{actual_name}' (AppID: {appid})")
        saved_files = []

        targets = [
            ("banner_hero_1920x620.jpg", [f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/library_hero.jpg"], "Steam (Hero 1080p)", "HERO", 95),
            ("cover_landscape_616x353.jpg", [f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg", f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"], "Steam (Capsule)", "CAPSULE", 85),
            ("cover_portrait_600x900.jpg", [f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/library_600x900_2x.jpg", f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/library_600x900.jpg"], "Steam (Portrait Poster)", "POSTER", 70),
            ("cover_header_460x215.jpg", [f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"], "Steam (Header)", "HEADER", 65),
            ("official_logo.png", [
                f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/logo_2x.png",
                f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{appid}/logo_2x.png",
                f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/logo_2x.png",
                f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/logo.png",
                f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{appid}/logo.png",
            ], "Steam Official Logo (PNG)", "LOGO", 40),
        ]

        for fname, urls, source, role, score in targets:
            if cls._cancelled():
                return saved_files
            dest = os.path.join(target_dir, fname)
            if not os.path.exists(dest) or os.path.getsize(dest) < 500:
                for url in urls:
                    if cls._cancelled():
                        return saved_files
                    try:
                        cls._download_file(url, dest)
                        if os.path.exists(dest) and os.path.getsize(dest) > 500:
                            break
                    except Exception:
                        continue
            if os.path.exists(dest) and os.path.getsize(dest) > 500:
                w, h = cls._get_image_dims(dest)
                saved_files.append({
                    "path": dest,
                    "filename": fname,
                    "source": source,
                    "role": role,
                    "width": w,
                    "height": h,
                    "score": score
                })

        return saved_files

    # =========================================================================
    # 3. Master Multi-Source Harvester & Auto-Cover Setter
    # =========================================================================
    @classmethod
    def harvest_all_artworks(cls, game_name: str, workspace_path: str = None, automatic=False) -> dict:
        """Deduplicate downloads per destination while preserving explicit user requests."""
        empty = {"success": False, "game_name": game_name, "primary_cover": None,
                 "sony_count": 0, "steam_count": 0, "total_images": 0, "images": []}
        if not game_name or cls._cancelled():
            return dict(empty, cancelled=cls._cancelled())
        if automatic and not ConfigManager().get("steam_auto_capsule", True):
            return dict(empty, skipped=True)
        identity = ("workspace", os.path.normcase(os.path.realpath(workspace_path))) if workspace_path else ("cache", SteamService._get_safe_slug(game_name))
        with cls._harvest_lock:
            if identity in cls._active_harvests:
                return dict(empty, busy=True)
            cls._active_harvests.add(identity)
        try:
            return cls._harvest_all_artworks_impl(game_name, workspace_path)
        finally:
            with cls._harvest_lock:
                cls._active_harvests.discard(identity)

    @classmethod
    def _harvest_all_artworks_impl(cls, game_name: str, workspace_path: str = None) -> dict:
        """
        Executes complete multi-source art harvest:
        1. Harvests Sony PlayStation Store (PS5 4K / PS4 1080p key art)
        2. Harvests Steam Official CDN (Hero 1920x620, Capsule 616x353, Header)
        3. Collects local images in 07_Image_Resources/Official_Art/
        4. Ranks candidates and sets the best 16:9 textless artwork as thub_cover.jpg
        """
        result = {
            "success": False,
            "game_name": game_name,
            "primary_cover": None,
            "sony_count": 0,
            "steam_count": 0,
            "total_images": 0,
            "images": []
        }
        if not game_name:
            return result

        # Determine target directory
        if workspace_path and os.path.exists(workspace_path):
            art_dir = os.path.join(workspace_path, "07_Image_Resources", "Official_Art")
            cover_dest = os.path.join(workspace_path, "thub_cover.jpg")
        else:
            slug = SteamService._get_safe_slug(game_name)
            art_dir = os.path.join(SteamService.get_central_cache_dir(), slug)
            cover_dest = os.path.join(SteamService.get_central_cache_dir(), f"{slug}.jpg")

        os.makedirs(art_dir, exist_ok=True)

        all_collected = []
        seen_paths = set()

        # 1. Harvest Sony PlayStation Store
        try:
            sony_files = cls.harvest_sony_playstation_assets(game_name, art_dir)
            result["sony_count"] = len(sony_files)
            for item in sony_files:
                if item["path"] not in seen_paths:
                    seen_paths.add(item["path"])
                    all_collected.append(item)
        except Exception as e:
            print(f"[ArtHarvester] Sony harvest error: {e}")

        if cls._cancelled():
            return dict(result, cancelled=True)

        # 2. Harvest Steam Store
        try:
            steam_files = cls.harvest_steam_assets(game_name, art_dir)
            result["steam_count"] = len(steam_files)
            for item in steam_files:
                if item["path"] not in seen_paths:
                    seen_paths.add(item["path"])
                    all_collected.append(item)
        except Exception as e:
            print(f"[ArtHarvester] Steam harvest error: {e}")

        if cls._cancelled():
            return dict(result, cancelled=True)

        # 3. Check any existing local files in art_dir that might not have been recorded
        try:
            for f in os.listdir(art_dir):
                if cls._cancelled():
                    return dict(result, cancelled=True)
                fp = os.path.join(art_dir, f)
                if fp not in seen_paths and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    if os.path.isfile(fp) and os.path.getsize(fp) > 1000:
                        seen_paths.add(fp)
                        w, h = cls._get_image_dims(fp)
                        all_collected.append({
                            "path": fp,
                            "filename": f,
                            "source": "Local Official Art",
                            "role": "LOCAL",
                            "width": w,
                            "height": h,
                            "score": 60
                        })
        except Exception:
            pass

        # 4. Rank candidates to pick the best 16:9 cover
        # Priority: 4K PS5 GameHub > PS4/PS5 Background > Steam Hero > 16:9 Banner > Capsule > Screenshots
        for c in all_collected:
            w, h = c["width"], c["height"]
            ratio = w / max(1, h)
            # Bonus for near 16:9 aspect ratio (~1.6 to 1.85)
            if 1.55 <= ratio <= 1.85:
                c["score"] += 20
            elif 2.8 <= ratio <= 3.2: # Steam hero (1920x620)
                c["score"] += 15

            # Resolution bonus
            if w >= 3840 and h >= 2160:
                c["score"] += 25
            elif w >= 1920 and h >= 1080:
                c["score"] += 15

        all_collected.sort(key=lambda x: (x["score"], x["width"] * x["height"]), reverse=True)

        if cls._cancelled():
            return dict(result, cancelled=True)

        # 5. Set primary cover
        primary = None
        for cand in all_collected:
            if cand["role"] != "LOGO":  # Don't pick logo as background cover
                primary = cand
                break

        if primary and primary["path"] and os.path.exists(primary["path"]):
            try:
                if os.path.abspath(primary["path"]) != os.path.abspath(cover_dest):
                    shutil.copy2(primary["path"], cover_dest)
                SteamService.save_to_central_cover(game_name, cover_dest)
                result["primary_cover"] = cover_dest
                primary["is_primary"] = True
                result["success"] = True
            except Exception as e:
                print(f"[ArtHarvester] Error setting primary cover: {e}")


        result["total_images"] = len(all_collected)
        result["images"] = all_collected
        return result

    @classmethod
    def get_existing_artworks(cls, workspace_path: str = None, game_name: str = "") -> list:
        """
        Scans for existing harvested official artworks in:
        1. {workspace}/07_Image_Resources/Official_Art/
        2. Central cache dir for this game
        Returns a sorted list of image candidate metadata dicts.
        """
        collected = []
        seen = set()
        dirs_to_check = []

        if workspace_path and os.path.exists(workspace_path):
            cover_path = os.path.join(workspace_path, "thub_cover.jpg")
            if os.path.exists(cover_path) and cover_path not in seen:
                w, h = cls._get_image_dims(cover_path)
                seen.add(os.path.abspath(cover_path))
                collected.append({
                    "path": cover_path,
                    "filename": "thub_cover.jpg",
                    "source": "Current Cover",
                    "role": "CURRENT_COVER",
                    "label": "ภาพปกปัจจุบัน (Active Cover)",
                    "width": w,
                    "height": h,
                    "score": 200,
                    "is_primary": True
                })

            art_dir = os.path.join(workspace_path, "07_Image_Resources", "Official_Art")
            if os.path.exists(art_dir):
                dirs_to_check.append(art_dir)

        if game_name:
            slug = SteamService._get_safe_slug(game_name)
            central_art = os.path.join(SteamService.get_central_cache_dir(), slug)
            if os.path.exists(central_art) and central_art not in dirs_to_check:
                dirs_to_check.append(central_art)

        for d in dirs_to_check:
            if cls._cancelled():
                return collected
            try:
                for f in os.listdir(d):
                    if cls._cancelled():
                        return collected
                    fp = os.path.join(d, f)
                    norm_p = os.path.abspath(fp)
                    if norm_p in seen or not os.path.isfile(fp):
                        continue
                    if not f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        continue
                    if os.path.getsize(fp) < 400:
                        continue
                    seen.add(norm_p)
                    w, h = cls._get_image_dims(fp)
                    lower_f = f.lower()

                    source = "Local Official Art"
                    role = "WALLPAPER"
                    label = f
                    score = 70

                    if "official_ps_logo" in lower_f or ("sony" in lower_f and "logo" in lower_f):
                        source = "Sony PlayStation"
                        role = "LOGO"
                        label = "Sony Official Transparent Logo (PNG)"
                        score = 250
                    elif "logo" in lower_f:
                        source = "Steam CDN"
                        role = "LOGO"
                        label = "Steam Official Transparent Logo (PNG)"
                        score = 250
                    elif "cover_portrait" in lower_f or "library_600x900" in lower_f or (h > w * 1.2 and "portrait" in lower_f):
                        source = "Steam CDN"
                        role = "PORTRAIT"
                        label = "Steam Library Grid Poster (600x900)"
                        score = 90
                    elif "cover_header" in lower_f:
                        source = "Steam CDN"
                        role = "HEADER"
                        label = "Steam Store Header Capsule (460x215)"
                        score = 80
                    elif "sony_ps5_gamehub" in lower_f or "gamehub" in lower_f:
                        source = "Sony PlayStation"
                        role = "GAMEHUB_COVER_ART"
                        label = "Sony PS5 4K GameHub Key Art"
                        score = 120
                    elif "sony_bg" in lower_f or "background" in lower_f:
                        source = "Sony PlayStation"
                        role = "BACKGROUND"
                        label = "Sony PlayStation Background (1080p)"
                        score = 110
                    elif "steam_hero" in lower_f or "banner_hero" in lower_f:
                        source = "Steam CDN"
                        role = "STEAM_HERO"
                        label = "Steam Official Hero Banner (1920x620)"
                        score = 95
                    elif "sony_banner" in lower_f or "banner" in lower_f:
                        source = "Sony PlayStation"
                        role = "SIXTEEN_BY_NINE_BANNER"
                        label = "Sony PlayStation 16:9 Banner"
                        score = 100
                    elif "sony_screenshot" in lower_f:
                        source = "Sony PlayStation"
                        role = "SCREENSHOT"
                        label = "Sony PlayStation Official Screenshot"
                        score = 80
                    elif "steam_capsule" in lower_f or "cover_landscape" in lower_f:
                        source = "Steam CDN"
                        role = "STEAM_CAPSULE"
                        label = "Steam Official Landscape Capsule"
                        score = 85
                    elif "steam_screenshot" in lower_f:
                        source = "Steam CDN"
                        role = "STEAM_SCREENSHOT"
                        label = "Steam Official Screenshot"
                        score = 75

                    ratio = w / max(1, h)
                    if 1.55 <= ratio <= 1.85:
                        score += 20
                    elif 2.8 <= ratio <= 3.2:
                        score += 15

                    if w >= 3840 and h >= 2160:
                        score += 25
                    elif w >= 1920 and h >= 1080:
                        score += 15

                    collected.append({
                        "path": fp,
                        "filename": f,
                        "source": source,
                        "role": role,
                        "label": label,
                        "width": w,
                        "height": h,
                        "score": score,
                        "is_primary": False
                    })
            except Exception as e:
                print(f"[ArtHarvester] Error scanning directory {d}: {e}")

        collected.sort(key=lambda x: (1 if x.get("role") == "CURRENT_COVER" else 0, x["score"], x["width"] * x["height"]), reverse=True)
        return collected

    @classmethod
    def set_as_project_cover(cls, workspace_path: str, image_path: str, game_name: str = "") -> bool:
        """Copies any selected image to {workspace}/thub_cover.jpg and updates SteamService central cover."""
        if not image_path or not os.path.exists(image_path):
            return False
        try:
            if workspace_path and os.path.exists(workspace_path):
                cover_dest = os.path.join(workspace_path, "thub_cover.jpg")
                if os.path.abspath(image_path) != os.path.abspath(cover_dest):
                    shutil.copy2(image_path, cover_dest)
            if game_name:
                SteamService.save_to_central_cover(game_name, image_path)

            return True
        except Exception as e:
            print(f"[ArtHarvester] Error setting project cover: {e}")
            return False

    @classmethod
    def get_or_harvest_dimension(cls, game_name: str, workspace_path: str = None, dim_key: str = "widescreen") -> dict:
        """
        Finds or on-demand downloads a specific dimension asset:
          - 'widescreen' / 'landscape': 16:9 4K / 1080p / Capsule 616x353
          - 'portrait': 2:3 vertical poster 600x900 (Steam Library Poster)
          - 'hero': wide banner 1920x620 (Steam Hero Banner)
          - 'header': store header 460x215
          - 'logo': official transparent PNG logo (Steam or Sony)
        Returns:
          {
             "success": bool,
             "path": str or None,
             "dim_key": str,
             "filename": str,
             "label": str,
             "width": int,
             "height": int,
             "is_logo": bool
          }
        """
        if not game_name or cls._cancelled():
            return {"success": False, "dim_key": dim_key, "error": "No game name provided or operation cancelled"}

        if workspace_path and os.path.exists(workspace_path):
            art_dir = os.path.join(workspace_path, "07_Image_Resources", "Official_Art")
        else:
            slug = SteamService._get_safe_slug(game_name)
            art_dir = os.path.join(SteamService.get_central_cache_dir(), slug)

        os.makedirs(art_dir, exist_ok=True)

        def _scan_candidate():
            if not os.path.exists(art_dir):
                return None
            try:
                files = os.listdir(art_dir)
            except Exception:
                return None
            files_lower = {f.lower(): f for f in files}

            if dim_key == "logo":
                for target in ["official_logo.png", "official_ps_logo.png", "logo.png"]:
                    if target in files_lower:
                        real_f = files_lower[target]
                        fp = os.path.join(art_dir, real_f)
                        if os.path.isfile(fp) and os.path.getsize(fp) > 300:
                            w, h = cls._get_image_dims(fp)
                            return {
                                "success": True,
                                "path": fp,
                                "dim_key": dim_key,
                                "filename": real_f,
                                "label": "โลโก้เกมโปร่งใส (Official Transparent Logo)",
                                "width": w,
                                "height": h,
                                "is_logo": True
                            }
                # Fallback: any PNG containing logo
                for fl, rf in files_lower.items():
                    if "logo" in fl and fl.endswith(".png"):
                        fp = os.path.join(art_dir, rf)
                        if os.path.isfile(fp) and os.path.getsize(fp) > 300:
                            w, h = cls._get_image_dims(fp)
                            return {
                                "success": True,
                                "path": fp,
                                "dim_key": dim_key,
                                "filename": rf,
                                "label": "โลโก้เกมโปร่งใส (Official Transparent Logo)",
                                "width": w,
                                "height": h,
                                "is_logo": True
                            }

            elif dim_key in ("widescreen", "landscape"):
                for target in [
                    "ps5_gamehub_cover_art_3840x2160.jpg",
                    "ps4_ps5_background_1920x1080.jpg",
                    "cover_landscape_616x353.jpg",
                    "ps5_16x9_banner.jpg"
                ]:
                    if target in files_lower:
                        real_f = files_lower[target]
                        fp = os.path.join(art_dir, real_f)
                        if os.path.isfile(fp) and os.path.getsize(fp) > 1000:
                            w, h = cls._get_image_dims(fp)
                            return {
                                "success": True,
                                "path": fp,
                                "dim_key": dim_key,
                                "filename": real_f,
                                "label": "ภาพแนวนอน 16:9 (Landscape Cover)",
                                "width": w,
                                "height": h,
                                "is_logo": False
                            }

            elif dim_key == "portrait":
                for target in ["cover_portrait_600x900.jpg"]:
                    if target in files_lower:
                        real_f = files_lower[target]
                        fp = os.path.join(art_dir, real_f)
                        if os.path.isfile(fp) and os.path.getsize(fp) > 1000:
                            w, h = cls._get_image_dims(fp)
                            return {
                                "success": True,
                                "path": fp,
                                "dim_key": dim_key,
                                "filename": real_f,
                                "label": "ภาพแนวตั้งโปสเตอร์ 600x900 (Portrait Poster)",
                                "width": w,
                                "height": h,
                                "is_logo": False
                            }

            elif dim_key == "hero":
                for target in ["banner_hero_1920x620.jpg", "ps5_16x9_banner.jpg"]:
                    if target in files_lower:
                        real_f = files_lower[target]
                        fp = os.path.join(art_dir, real_f)
                        if os.path.isfile(fp) and os.path.getsize(fp) > 1000:
                            w, h = cls._get_image_dims(fp)
                            return {
                                "success": True,
                                "path": fp,
                                "dim_key": dim_key,
                                "filename": real_f,
                                "label": "ภาพแบนเนอร์กว้าง 1920x620 (Hero Banner)",
                                "width": w,
                                "height": h,
                                "is_logo": False
                            }

            elif dim_key == "header":
                for target in ["cover_header_460x215.jpg"]:
                    if target in files_lower:
                        real_f = files_lower[target]
                        fp = os.path.join(art_dir, real_f)
                        if os.path.isfile(fp) and os.path.getsize(fp) > 1000:
                            w, h = cls._get_image_dims(fp)
                            return {
                                "success": True,
                                "path": fp,
                                "dim_key": dim_key,
                                "filename": real_f,
                                "label": "ภาพปกส่วนหัว 460x215 (Store Header)",
                                "width": w,
                                "height": h,
                                "is_logo": False
                            }

            return None

        # 1. Quick local check
        local_cand = _scan_candidate()
        if local_cand:
            return local_cand

        # 2. Not found locally, trigger harvest
        try:
            cls.harvest_all_artworks(game_name, workspace_path)
        except Exception as e:
            print(f"[ArtHarvester] Harvest error during get_or_harvest_dimension: {e}")

        if cls._cancelled():
            return {"success": False, "dim_key": dim_key, "cancelled": True}

        # 3. Re-scan after harvest
        post_cand = _scan_candidate()
        if post_cand:
            return post_cand

        return {
            "success": False,
            "dim_key": dim_key,
            "error": f"Asset for dimension '{dim_key}' not found on Sony or Steam Store"
        }

    # =========================================================================
    # Helpers
    # =========================================================================
    @classmethod
    def _download_file(cls, url: str, dest_path: str):
        temporary = None
        try:
            if cls._cancelled():
                return False
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=12) as resp:
                fd, temporary = tempfile.mkstemp(prefix='.thub-art-', dir=os.path.dirname(os.path.abspath(dest_path)))
                size = 0
                with os.fdopen(fd, 'wb') as handle:
                    while not cls._cancelled():
                        block = resp.read(64 * 1024)
                        if not block:
                            break
                        handle.write(block)
                        size += len(block)
                if size > 1000 and not cls._cancelled():
                    os.replace(temporary, dest_path)
                    return True
        except Exception:
            pass
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
        return False

    @classmethod
    def _get_image_dims(cls, img_path: str):
        try:
            with Image.open(img_path) as im:
                return im.width, im.height
        except Exception:
            return 0, 0

