import os
import re
import json
import shutil
from pathlib import Path


class FontService:
    """
    Service for managing curated Thai Game Fonts, PUA mappings,
    engine recommendations, and workspace deployments.
    """

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DEFAULT_FONTS_DIR = os.path.join(BASE_DIR, "tools", "fonts")
    EXTERNAL_FONTS_DIR = r"E:\Mod_Workspace\Tool\1_ThaiFont"

    def __init__(self, fonts_dir=None):
        self.fonts_dir = fonts_dir or self.DEFAULT_FONTS_DIR
        self.catalog = []
        self._load_catalog()

    def _load_catalog(self):
        catalog_path = os.path.join(self.fonts_dir, "catalog.json")
        if os.path.exists(catalog_path):
            try:
                with open(catalog_path, "r", encoding="utf-8") as f:
                    self.catalog = json.load(f)
            except Exception as e:
                print(f"[FontService] Failed to load catalog: {e}")
                self.catalog = []
        else:
            self.catalog = []

    def get_all_fonts(self):
        """Returns list of all font metadata entries."""
        return list(self.catalog)

    def get_font_by_id(self, font_id):
        """Finds font metadata by its ID."""
        for f in self.catalog:
            if f.get("id") == font_id:
                return f
        return None

    def get_fonts_for_engine(self, engine_name):
        """
        Sorts fonts by suitability score for the given game engine.
        Returns list of font dicts with an added 'score' and 'is_recommended' flag.
        """
        if not engine_name:
            return self.get_all_fonts()

        eng_lower = engine_name.lower().replace(" ", "").replace("_", "")

        scored = []
        for f in self.catalog:
            engines = f.get("engines", {})
            best_score = 70  # baseline suitability for any font

            for key, score in engines.items():
                k_clean = key.lower().replace(" ", "").replace("_", "")
                if k_clean in eng_lower or eng_lower in k_clean:
                    if score > best_score:
                        best_score = score

            # Specific engine aliases
            if "unreal" in eng_lower:
                best_score = max(best_score, engines.get("Unreal Engine", 80))
            elif "unity" in eng_lower:
                best_score = max(best_score, engines.get("Unity", 80))
            elif "reengine" in eng_lower or "capcom" in eng_lower:
                best_score = max(best_score, engines.get("RE Engine", 80))
            elif "godot" in eng_lower:
                best_score = max(best_score, engines.get("Godot Engine", 80))
            elif "cengine" in eng_lower:
                best_score = max(best_score, engines.get("C_Engine", 80))

            f_copy = dict(f)
            f_copy["engine_score"] = best_score
            f_copy["is_recommended"] = (best_score >= 90)
            scored.append(f_copy)

        # Sort descending by score
        scored.sort(key=lambda x: x.get("engine_score", 0), reverse=True)
        return scored

    def get_preview_path(self, font_id, variant_rel_path=None):
        """Returns the absolute file path to the font preview image (supports specific variant styles)."""
        font = self.get_font_by_id(font_id)
        if not font:
            return ""

        if variant_rel_path:
            v_fn = os.path.basename(variant_rel_path)
            v_clean = re.sub(r'[^a-zA-Z0-9_]', '_', os.path.splitext(v_fn)[0].lower())
            var_preview_fn = f"{font_id}_{v_clean}_preview.png"
            var_preview_path = os.path.join(self.fonts_dir, "previews", var_preview_fn)
            if os.path.exists(var_preview_path):
                return var_preview_path

        rel_img = font.get("preview_image", "")
        if not rel_img:
            rel_img = f"previews/{font_id}_preview.png"

        full_path = os.path.join(self.fonts_dir, rel_img)
        if os.path.exists(full_path):
            return full_path
        return ""

    def parse_variant_info(self, rel_path, filename):
        """Parses human-readable weight and style information from a font filename."""
        name = os.path.splitext(filename)[0]
        name_clean = re.sub(r'_PUA(_shifted)?$', '', name, flags=re.IGNORECASE)
        is_shifted = "_shifted" in name.lower()

        is_variable = "variablefont" in name_clean.lower() or "[" in name_clean or "wght" in name_clean.lower()
        is_italic = "italic" in name_clean.lower()
        is_17pt = "17pt" in name_clean.lower()

        # Width / Condensed check
        width_en = ""
        width_th = ""
        nl = name_clean.lower()
        if "extracondensed" in nl or "extra condensed" in nl:
            width_en = "ExtraCondensed"
            width_th = "แคบพิเศษ"
        elif "semicondensed" in nl or "semi condensed" in nl:
            width_en = "SemiCondensed"
            width_th = "กึ่งแคบ"
        elif "condensed" in nl:
            width_en = "Condensed"
            width_th = "แคบ"

        if "-" in name_clean:
            raw_style = name_clean.split("-", 1)[1]
        else:
            raw_style = "Regular"

        WEIGHT_PATTERNS = [
            ("ExtraBold", "ExtraBold (หนาพิเศษ)", 800),
            ("UltraBold", "ExtraBold (หนาพิเศษ)", 800),
            ("ExtraLight", "ExtraLight (บางพิเศษ)", 200),
            ("UltraLight", "ExtraLight (บางพิเศษ)", 200),
            ("SemiBold", "SemiBold (กึ่งหนา)", 600),
            ("DemiBold", "SemiBold (กึ่งหนา)", 600),
            ("GameBold", "GameBold (สำหรับเกม)", 750),
            ("Black", "Black (ดำ/หนาสุด)", 900),
            ("Heavy", "Heavy (หนามาก)", 850),
            ("Bold", "Bold (หนา)", 700),
            ("Medium", "Medium (ปานกลาง)", 500),
            ("Light", "Light (บาง)", 300),
            ("Thin", "Thin (บางเฉียบ)", 100),
            ("Regular", "Regular (ปกติ)", 400),
        ]

        matched_weight_en = "Regular"
        matched_weight_th = "Regular (ปกติ)"
        weight_val = 400

        for w_en, w_th, val in WEIGHT_PATTERNS:
            if w_en.lower() in raw_style.lower():
                matched_weight_en = w_en
                matched_weight_th = w_th
                weight_val = val
                break

        if is_variable:
            display_name = "Variable Font" + (" Italic" if is_italic else "")
            display_th = "ปรับน้ำหนักได้ (Variable Font)" + (" เอียง" if is_italic else "")
            weight_val = 400
        else:
            parts_en = [matched_weight_en]
            parts_th = [matched_weight_th]
            if width_en:
                parts_en.append(width_en)
                parts_th.append(f"[{width_th}]")
            if is_17pt:
                parts_en.append("(17pt)")
                parts_th.append("(17pt)")
            if is_italic:
                parts_en.append("Italic")
                parts_th.append("เอียง")
            if is_shifted:
                parts_en.append("(Shifted)")
                parts_th.append("(เลื่อนระดับสระ)")
            display_name = " ".join(parts_en)
            display_th = " ".join(parts_th)

        SORT_ORDER = {
            700: 1,   # Bold
            750: 2,   # GameBold
            400: 3,   # Regular
            600: 4,   # SemiBold
            500: 5,   # Medium
            800: 6,   # ExtraBold
            850: 7,   # Heavy
            900: 8,   # Black
            300: 9,   # Light
            200: 10,  # ExtraLight
            100: 11,  # Thin
        }
        order_score = (
            SORT_ORDER.get(weight_val, 50)
            + (100 if is_italic else 0)
            + (200 if width_en else 0)
            + (50 if is_17pt else 0)
            + (300 if is_variable else 0)
        )

        return {
            "file_name": filename,
            "rel_path": rel_path.replace("\\", "/"),
            "style_name": display_name,
            "display_th": display_th,
            "weight": weight_val,
            "is_italic": is_italic,
            "is_variable": is_variable,
            "order_score": order_score
        }

    def get_font_variants(self, font_id):
        """
        Scans and returns all available font style/weight files for the specified font family.
        Returns a sorted list of variant dicts.
        """
        font = self.get_font_by_id(font_id)
        if not font:
            return []

        folder = font.get("folder", "")
        folder_path = os.path.join(self.fonts_dir, "library", folder)
        if not os.path.exists(folder_path):
            return []

        primary_file = font.get("primary_file", "").replace("/", os.sep)
        variants = []

        for root, _, fnames in os.walk(folder_path):
            for fn in fnames:
                if fn.lower().endswith((".ttf", ".otf")):
                    if "_backup" in fn.lower() or ".bak" in fn.lower() or fn.startswith("."):
                        continue
                    full_p = os.path.join(root, fn)
                    rel = os.path.relpath(full_p, folder_path)
                    v_info = self.parse_variant_info(rel, fn)
                    v_info["full_path"] = full_p
                    v_info["is_default"] = (
                        rel.replace("\\", "/").lower() == primary_file.replace("\\", "/").lower()
                        or fn.lower() == os.path.basename(primary_file).lower()
                    )
                    variants.append(v_info)

        # Sort: default first if any, then by order_score, then style_name
        variants.sort(key=lambda x: (not x.get("is_default", False), x.get("order_score", 999), x.get("style_name", "")))
        return variants

    def get_font_file_path(self, font_id, variant_rel_path=None):
        """Returns the absolute path to the requested variant or primary TTF file."""
        font = self.get_font_by_id(font_id)
        if not font:
            return ""

        folder = font.get("folder", "")
        if variant_rel_path:
            specific_path = os.path.join(self.fonts_dir, "library", folder, variant_rel_path.replace("/", os.sep))
            if os.path.exists(specific_path):
                return specific_path

        p_file = font.get("primary_file", "").replace("/", os.sep)
        full_path = os.path.join(self.fonts_dir, "library", folder, p_file)
        if os.path.exists(full_path):
            return full_path

        r_file = font.get("regular_file", "").replace("/", os.sep)
        fallback_path = os.path.join(self.fonts_dir, "library", folder, r_file)
        if os.path.exists(fallback_path):
            return fallback_path

        return ""

    def deploy_font_to_project(self, font_id, project_path, selected_variant_rel_path=None):
        """
        Deploys the chosen font, Mapping.json, Char.txt, and thai_font_mapper.py
        into the project's 03_Font_and_UI/ directory.
        If selected_variant_rel_path is specified, records it as the primary chosen style.
        Returns a dict: {"success": bool, "message": str, "deployed_files": list, ...}
        """
        if not project_path or not os.path.exists(project_path):
            return {
                "success": False,
                "message": f"Workspace folder does not exist: {project_path}",
                "deployed_files": []
            }

        font = self.get_font_by_id(font_id)
        if not font:
            return {
                "success": False,
                "message": f"Font ID not found: {font_id}",
                "deployed_files": []
            }

        target_font_ui = os.path.join(project_path, "03_Font_and_UI")
        os.makedirs(target_font_ui, exist_ok=True)

        deployed_files = []

        # 1. Copy all Font TTF files in this family
        folder = font.get("folder", "")
        font_src_dir = os.path.join(self.fonts_dir, "library", folder)
        dest_font_dir = os.path.join(target_font_ui, folder)
        os.makedirs(dest_font_dir, exist_ok=True)

        if os.path.exists(font_src_dir):
            for item in os.listdir(font_src_dir):
                s_item = os.path.join(font_src_dir, item)
                d_item = os.path.join(dest_font_dir, item)
                if os.path.isfile(s_item) and s_item.lower().endswith((".ttf", ".otf")):
                    shutil.copy2(s_item, d_item)
                    deployed_files.append(os.path.relpath(d_item, project_path))
                elif os.path.isdir(s_item):
                    # For static folder e.g. in Google Sans or Noto Sans
                    shutil.copytree(s_item, d_item, dirs_exist_ok=True)
                    deployed_files.append(os.path.relpath(d_item, project_path))

        # Determine selected variant info
        variants = self.get_font_variants(font_id)
        selected_variant = None
        if selected_variant_rel_path:
            for v in variants:
                if v.get("rel_path") == selected_variant_rel_path or v.get("file_name") == selected_variant_rel_path:
                    selected_variant = v
                    break
        if not selected_variant and variants:
            selected_variant = variants[0]

        # 2. Copy Mapping.json, Char.txt, and thai_font_mapper.py into 03_Font_and_UI
        mapping_src_dir = os.path.join(self.fonts_dir, "mapping")
        essential_tools = ["Mapping.json", "Char.txt", "thai_font_mapper.py"]

        for tool_file in essential_tools:
            src_f = os.path.join(mapping_src_dir, tool_file)
            if not os.path.exists(src_f):
                src_f = os.path.join(self.EXTERNAL_FONTS_DIR, tool_file)

            if os.path.exists(src_f):
                dst_f = os.path.join(target_font_ui, tool_file)
                shutil.copy2(src_f, dst_f)
                deployed_files.append(os.path.relpath(dst_f, project_path))

        # Also copy thai_font_mapper.py to 05_Scripts_and_Tools if the folder exists
        scripts_dir = os.path.join(project_path, "05_Scripts_and_Tools")
        if os.path.exists(scripts_dir):
            src_mapper = os.path.join(mapping_src_dir, "thai_font_mapper.py")
            if os.path.exists(src_mapper):
                dst_mapper = os.path.join(scripts_dir, "thai_font_mapper.py")
                shutil.copy2(src_mapper, dst_mapper)
                deployed_files.append(os.path.relpath(dst_mapper, project_path))

        style_title = selected_variant.get("display_th", "") if selected_variant else ""
        return {
            "success": True,
            "message": f"Successfully deployed {font.get('name_en')} ({style_title}) and PUA Mapping kit to 03_Font_and_UI",
            "font_name": font.get("name_en"),
            "style_title": style_title,
            "selected_variant": selected_variant,
            "deployed_files": deployed_files
        }
