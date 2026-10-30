import os
import re
import queue
import shutil
import json
import threading

class SteamService:
    """Fetches Steam header / landscape images (16:9) and handles fast in-memory caching."""
    _cache = {}
    _lock = threading.Lock()

    # Throttled background auto-fetch queue
    _fetch_queue = queue.Queue()
    _queued_keys = set()
    _fetch_listeners = {}
    _queue_lock = threading.Lock()
    _worker_thread = None

    @staticmethod
    def _cancelled():
        """Stop subsequent network attempts when an owned Qt task is cancelled."""
        try:
            from PyQt6.QtCore import QThread
            return QThread.currentThread().isInterruptionRequested()
        except (ImportError, RuntimeError):
            return False

    @classmethod
    def get_central_cache_dir(cls):
        """Returns the centralized cover cache directory inside assets/cover_cache."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cache_dir = os.path.join(base_dir, "assets", "cover_cache")
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    @classmethod
    def _get_safe_slug(cls, name):
        return re.sub(r'[^a-zA-Z0-9_\-]+', '_', name.strip().lower()).strip('_') or 'game'

    @classmethod
    def get_central_cover_path(cls, game_name):
        """Returns existing cached cover path from central cache if available."""
        if not game_name:
            return None
        slug = cls._get_safe_slug(game_name)
        central_dir = cls.get_central_cache_dir()
        for ext in ('.jpg', '.png', '.webp'):
            candidate = os.path.join(central_dir, f"{slug}{ext}")
            if os.path.exists(candidate) and os.path.getsize(candidate) > 500:
                return candidate
        return None

    @classmethod
    def save_to_central_cover(cls, game_name, src_file):
        """Copies an image to central cache as backup."""
        if not game_name or not src_file or not os.path.exists(src_file):
            return None
        try:
            slug = cls._get_safe_slug(game_name)
            ext = os.path.splitext(src_file)[1].lower() or '.jpg'
            dest = os.path.join(cls.get_central_cache_dir(), f"{slug}{ext}")
            shutil.copy2(src_file, dest)
            return dest
        except Exception:
            return None

    @classmethod
    def search_game_appid(cls, game_name):
        """Searches Steam Store API for the game's AppID using multi-stage smart sanitization."""
        if not game_name or not game_name.strip():
            return None, None
        if cls._cancelled():
            return None, None
        # Cover-cache lookups are part of startup; load HTTP only for a search.
        import urllib.parse
        import urllib.request

        raw = game_name.strip()
        candidates = [raw]

        # 1. Strip brackets e.g. [Thai Mod], (GOTY), ~Boku~
        c_no_brackets = re.sub(r'\[.*?\]|\(.*?\)|<.*?>|\{.*?\}|~.*?~', '', raw).strip()
        if c_no_brackets and c_no_brackets not in candidates:
            candidates.append(c_no_brackets)

        # 2. Replace underscores and hyphens with spaces
        c_spaces = re.sub(r'[_\-]+', ' ', raw).strip()
        c_spaces = re.sub(r'\s+', ' ', c_spaces)
        if c_spaces and c_spaces not in candidates:
            candidates.append(c_spaces)

        # 3. Strip mod / version / edition noise words
        c_noise = re.sub(r'(?i)\b(thai|mod|thai mod|modding|translation|patch|remastered|definitive|edition|v\d+.*)\b', '', raw).strip()
        c_noise = re.sub(r'\s+', ' ', c_noise)
        if c_noise and c_noise not in candidates:
            candidates.append(c_noise)

        # 4. Text before colon or dash or tilde
        c_prefix = re.split(r'[:\-–—~]', raw)[0].strip()
        if c_prefix and len(c_prefix) >= 3 and c_prefix not in candidates:
            candidates.append(c_prefix)

        # 5. Trailing digits (e.g. Dead Island 1 -> Dead Island)
        c_num = re.sub(r'\s+\d+$', '', raw).strip()
        if c_num and len(c_num) >= 3 and c_num not in candidates:
            candidates.append(c_num)

        for q in candidates:
            if cls._cancelled():
                return None, None
            if not q or len(q) < 2:
                continue
            try:
                query = urllib.parse.quote(q)
                url = f"https://store.steampowered.com/api/storesearch/?term={query}&l=english&cc=US"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    if data.get("total", 0) > 0:
                        item = data["items"][0]
                        return item.get("id"), item.get("name")
            except Exception:
                continue

        return None, None

    @classmethod
    def queue_auto_cover_fetch(cls, game_name, workspace_path, on_complete=None):
        """Queues an automatic cover fetch in the background with rate limiting and deduplication."""
        if not game_name:
            return

        norm_path = os.path.normpath(workspace_path) if workspace_path else ""
        key = (game_name.lower().strip(), norm_path)

        with cls._queue_lock:
            if on_complete:
                if key not in cls._fetch_listeners:
                    cls._fetch_listeners[key] = []
                if on_complete not in cls._fetch_listeners[key]:
                    cls._fetch_listeners[key].append(on_complete)

            if key in cls._queued_keys:
                return
            cls._queued_keys.add(key)
            cls._fetch_queue.put((game_name, workspace_path, key))

            if cls._worker_thread is None or not cls._worker_thread.is_alive():
                cls._worker_thread = threading.Thread(target=cls._process_fetch_queue, daemon=True)
                cls._worker_thread.start()

    @classmethod
    def _process_fetch_queue(cls):
        import time
        while True:
            # Queue-empty observation and worker retirement share the same lock
            # as enqueue/start. A request arriving during shutdown cannot strand.
            with cls._queue_lock:
                try:
                    game_name, workspace_path, key = cls._fetch_queue.get_nowait()
                except queue.Empty:
                    cls._worker_thread = None
                    return

            best = None
            try:
                cover_dest = None
                if workspace_path:
                    try:
                        os.makedirs(workspace_path, exist_ok=True)
                        cover_dest = os.path.join(workspace_path, "thub_cover.jpg")
                    except Exception:
                        pass

                if not cover_dest:
                    central_dir = cls.get_central_cache_dir()
                    slug = cls._get_safe_slug(game_name)
                    cover_dest = os.path.join(central_dir, f"{slug}.jpg")

                # Fast direct cover download (<1 second)
                ok, res_path = cls.download_steam_cover_sync(game_name, cover_dest)
                if ok and os.path.exists(res_path) and os.path.getsize(res_path) > 500:
                    best = res_path
                    # Also copy to Official_Art/cover_landscape_616x353.jpg if workspace exists
                    if workspace_path and os.path.exists(workspace_path):
                        try:
                            art_dir = os.path.join(workspace_path, "07_Image_Resources", "Official_Art")
                            os.makedirs(art_dir, exist_ok=True)
                            art_cover = os.path.join(art_dir, "cover_landscape_616x353.jpg")
                            shutil.copy2(best, art_cover)
                        except Exception:
                            pass
                else:
                    best = cls.get_central_cover_path(game_name)

                if best:
                    cls.save_to_central_cover(game_name, best)

            except Exception as e:
                print(f"[SteamService] Auto-fetch error for '{game_name}': {e}")
            finally:
                # Release deduplication state on success AND failure, including
                # exceptions. Failed jobs can be retried and callbacks do not leak.
                with cls._queue_lock:
                    listeners = cls._fetch_listeners.pop(key, [])
                    cls._queued_keys.discard(key)
                cls._fetch_queue.task_done()

            if best:
                for cb in listeners:
                    try:
                        cb(best)
                    except Exception as e:
                        print(f"[SteamService] Listener callback error: {e}")

            time.sleep(0.15)

    @classmethod
    def fetch_landscape_cover(cls, game_name, dest_path, on_complete=None):
        """Asynchronously downloads 16:9 Steam header/capsule to dest_path."""
        def _worker():
            import urllib.request
            success = False
            try:
                appid, _ = cls.search_game_appid(game_name)
                if appid:
                    # Preferred: 16:9 landscape headers with CDN fallbacks
                    header_urls = [
                        f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg",
                        f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg",
                        f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{appid}/capsule_616x353.jpg",
                        f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{appid}/capsule_616x353.jpg",
                        f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg",
                        f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/library_hero.jpg",
                        f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{appid}/library_hero.jpg"
                    ]

                    for url in header_urls:
                        try:
                            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req, timeout=6) as resp:
                                if resp.status == 200:
                                    img_bytes = resp.read()
                                    if len(img_bytes) > 500:
                                        os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
                                        with open(dest_path, "wb") as f:
                                            f.write(img_bytes)
                                        success = True
                                        cls.save_to_central_cover(game_name, dest_path)
                                        break
                        except Exception:
                            continue
            except Exception as e:
                print(f"[SteamService] Download error: {e}")

            if on_complete:
                try:
                    on_complete(success, dest_path)
                except Exception as e:
                    print(f"[SteamService] Callback error: {e}")

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    @classmethod
    def fetch_all_game_capsules_sync(cls, game_name, dest_dir, root_cover_dest=None):
        """Synchronously downloads multiple cover dimensions to dest_dir:
        - cover_landscape_616x353.jpg (Steam Capsule)
        - cover_portrait_600x900.jpg (Steam Library 2:3 Poster)
        - banner_hero_1920x620.jpg (Steam Library Hero)
        - cover_header_460x215.jpg (Steam Header)
        - official_logo.png (Transparent Logo)
        Optionally copies the best landscape cover to root_cover_dest.
        Returns a dict of {key: downloaded_file_path or None}.
        """
        import urllib.request
        results = {}
        appid, _ = cls.search_game_appid(game_name)
        if not appid:
            return results

        os.makedirs(dest_dir, exist_ok=True)

        asset_specs = [
            ("cover_landscape_616x353.jpg", [
                f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg",
                f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"
            ]),
            ("cover_portrait_600x900.jpg", [
                f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/library_600x900_2x.jpg",
                f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/library_600x900.jpg"
            ]),
            ("banner_hero_1920x620.jpg", [
                f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/library_hero.jpg"
            ]),
            ("cover_header_460x215.jpg", [
                f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"
            ]),
            ("official_logo.png", [
                f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/logo_2x.png",
                f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{appid}/logo_2x.png",
                f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/logo_2x.png",
                f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/logo.png",
                f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{appid}/logo.png",
            ]),
        ]

        for filename, urls in asset_specs:
            if cls._cancelled():
                return results
            file_path = os.path.join(dest_dir, filename)
            downloaded = False
            for url in urls:
                if cls._cancelled():
                    return results
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=6) as resp:
                        if resp.status == 200:
                            data = resp.read()
                            if len(data) > 500: # ensure valid image payload
                                with open(file_path, "wb") as f:
                                    f.write(data)
                                results[filename] = file_path
                                downloaded = True
                                break
                except Exception:
                    continue
            if not downloaded:
                results[filename] = None

        if root_cover_dest:
            best_cover = results.get("cover_landscape_616x353.jpg") or results.get("cover_header_460x215.jpg") or results.get("banner_hero_1920x620.jpg") or results.get("cover_portrait_600x900.jpg")
            if best_cover and os.path.exists(best_cover):
                try:
                    import shutil
                    os.makedirs(os.path.dirname(os.path.abspath(root_cover_dest)), exist_ok=True)
                    shutil.copy2(best_cover, root_cover_dest)
                    cls.save_to_central_cover(game_name, root_cover_dest)
                except Exception as e:
                    print(f"[SteamService] Copy root cover failed: {e}")

        return results

    @classmethod
    def fetch_all_game_capsules(cls, game_name, dest_dir, root_cover_dest=None, on_complete=None):
        """Asynchronously downloads all game cover dimensions to dest_dir."""
        def _worker():
            results = cls.fetch_all_game_capsules_sync(game_name, dest_dir, root_cover_dest=root_cover_dest)
            if on_complete:
                try:
                    on_complete(results)
                except Exception as e:
                    print(f"[SteamService] All capsules callback error: {e}")

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    @classmethod
    def download_steam_cover_sync(cls, game_name, dest_path):
        """Synchronously downloads 16:9 Steam header/capsule to dest_path with CDN fallbacks."""
        import urllib.request
        appid, _ = cls.search_game_appid(game_name)
        if not appid:
            return False, "ไม่พบเกมนี้บน Steam Store"

        header_urls = [
            f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg",
            f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg",
            f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{appid}/capsule_616x353.jpg",
            f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{appid}/capsule_616x353.jpg",
            f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg",
            f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/library_hero.jpg",
            f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{appid}/library_hero.jpg"
        ]

        for url in header_urls:
            if cls._cancelled():
                return False, "ยกเลิกการดาวน์โหลด"
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    if resp.status == 200:
                        img_bytes = resp.read()
                        if len(img_bytes) > 500:
                            os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
                            with open(dest_path, "wb") as f:
                                f.write(img_bytes)
                            cls.save_to_central_cover(game_name, dest_path)
                            return True, dest_path
            except Exception:
                continue
        return False, "ดาวน์โหลดภาพจาก Steam ไม่สำเร็จ"

    @classmethod
    def download_image_from_url(cls, url, dest_path):
        """Downloads an image from a direct URL to dest_path."""
        import urllib.request
        try:
            req = urllib.request.Request(url.strip(), headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    img_bytes = resp.read()
                    os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
                    with open(dest_path, "wb") as f:
                        f.write(img_bytes)
                    return True, dest_path
        except Exception as e:
            return False, str(e)
        return False, "URL ไม่ถูกต้องหรือไม่สามารถเข้าถึงได้"

    @classmethod
    def get_rounded_card_image(cls, image_path, size=(276, 155), corner_radius=8):
        """Loads and crops an image to a 16:9 landscape ratio with rounded corners. Highly cached."""
        from PIL import Image, ImageDraw
        cache_key = (image_path, size, corner_radius)
        with cls._lock:
            if cache_key in cls._cache:
                return cls._cache[cache_key]

        if not image_path or not os.path.exists(image_path):
            img = cls._create_placeholder_poster(size, corner_radius)
        else:
            try:
                with Image.open(image_path) as raw_img:
                    raw_img = raw_img.convert("RGBA")
                    target_w, target_h = size
                    orig_w, orig_h = raw_img.size

                    scale = max(target_w / orig_w, target_h / orig_h)
                    new_w = int(orig_w * scale)
                    new_h = int(orig_h * scale)
                    # Use BILINEAR for super fast startup rendering
                    resized = raw_img.resize((new_w, new_h), Image.Resampling.BILINEAR)

                    left = (new_w - target_w) // 2
                    top = (new_h - target_h) // 2
                    cropped = resized.crop((left, top, left + target_w, top + target_h))

                    # Apply rounded corners
                    mask = Image.new('L', size, 0)
                    draw = ImageDraw.Draw(mask)
                    draw.rounded_rectangle([(0, 0), size], radius=corner_radius, fill=255)

                    rounded = Image.new('RGBA', size, (0, 0, 0, 0))
                    rounded.paste(cropped, (0, 0), mask=mask)
                    img = rounded
            except Exception as e:
                print(f"[SteamService] Failed to process image {image_path}: {e}")
                img = cls._create_placeholder_poster(size, corner_radius)

        with cls._lock:
            cls._cache[cache_key] = img
        return img

    @classmethod
    def _create_placeholder_poster(cls, size, corner_radius=8):
        from PIL import Image, ImageDraw
        img = Image.new('RGBA', size, (24, 28, 40, 255))
        mask = Image.new('L', size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle([(0, 0), size], radius=corner_radius, fill=255)

        res = Image.new('RGBA', size, (0, 0, 0, 0))
        res.paste(img, (0, 0), mask=mask)
        return res
