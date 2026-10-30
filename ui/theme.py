"""
THub Modern Theme - Inspired by DLSS Swapper (Obsidian & Fluent Dark)
"""

class Theme:
    # Canvas & Backgrounds
    BG_CANVAS      = "#0b0e14" # Deep Obsidian Canvas
    BG_SIDEBAR     = "#11141d" # Dark Slate Sidebar
    BG_HEADER      = "#141824" # Header Bar Surface
    BG_CARD        = "#171c2a" # Card Background
    BG_CARD_HOVER  = "#1e2436" # Card Hover Background
    BG_PILL        = "#1e2436" # Status Pill Background

    # Borders & Dividers
    BORDER_SUBTLE  = "#23293d" # Crisp Card Outline
    BORDER_HOVER   = "#3b4463" # Focused Outline
    BORDER_ACCENT  = "#38bdf8" # Cyan Glow

    # Accents & Brand Colors
    CYAN_TSTUDIO   = "#38bdf8" # TStudio Cyan
    CYAN_HOVER     = "#0284c7"
    VIOLET_AI      = "#a855f7" # AI Helper Violet
    VIOLET_HOVER   = "#9333ea"
    GREEN_SUCCESS  = "#22c55e" # Engine & Completed Green
    GREEN_HOVER    = "#16a34a"
    AMBER_WARN     = "#f59e0b" # In-progress Amber
    RED_ROSE       = "#f43f5e" # TVox & Error Red

    # Typography
    TEXT_PRIMARY   = "#f8fafc" # Bright Slate 50
    TEXT_SECONDARY = "#94a3b8" # Slate 400
    TEXT_MUTED     = "#64748b" # Slate 500
    TEXT_INVERT    = "#0f172a" # Dark text on light button

    # Font Families
    FONT_FAMILY    = "Segoe UI"
    FONT_FALLBACK  = "Prompt"

    @classmethod
    def get_engine_color(cls, engine_name):
        e = (engine_name or "").lower()
        if "unreal" in e:
            return "#38bdf8" # Cyan Blue
        elif "unity" in e:
            return "#22c55e" # Green
        elif "re engine" in e:
            return "#f43f5e" # Red
        elif "frostbite" in e:
            return "#fb923c" # Orange
        elif "redengine" in e:
            return "#c084fc" # Purple
        elif "directx 12" in e:
            return "#22c55e"
        elif "directx 11" in e:
            return "#38bdf8"
        elif "vulkan" in e:
            return "#ef4444"
        return "#94a3b8"
