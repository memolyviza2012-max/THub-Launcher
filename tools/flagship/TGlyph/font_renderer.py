# -*- coding: utf-8 -*-
"""font_renderer.py – Render individual font glyphs via Pillow + numpy.

This module provides:
- Supersampled glyph rendering  (render at N×, downscale with LANCZOS)
- Thai combining-mark compositing (above / below marks on consonants)
- Glyph metric measurement
- Game-engine–style text-line preview using per-glyph metrics

All pixel arrays are **uint8 grayscale (0-255)** numpy ndarrays.
Font objects (Pillow ``ImageFont``) are LRU-cached for performance.
Supports ``.ttf`` and ``.otf`` font files.
"""

from __future__ import annotations

import functools
import logging
from typing import Dict, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Thai Unicode ranges for combining-mark classification
# ---------------------------------------------------------------------------
# Above vowels / tone marks: U+0E31, U+0E34-0E3A, U+0E47-0E4E
_THAI_ABOVE_MARKS: set[int] = (
    {0x0E31}
    | set(range(0x0E34, 0x0E3B))   # sara i, sara ii, sara ue, etc.
    | set(range(0x0E47, 0x0E4F))   # mai tai khu, mai ek, mai tho, …
)

# Below vowels: U+0E38-0E3A  (sara u, sara uu, phinthu)
_THAI_BELOW_MARKS: set[int] = set(range(0x0E38, 0x0E3B))

# ---------------------------------------------------------------------------
# Font cache
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=32)
def _load_font(font_path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load and cache a TrueType / OpenType font at the requested pixel size.

    Parameters
    ----------
    font_path : str
        Absolute path to a ``.ttf`` or ``.otf`` file.
    size : int
        Desired font size in pixels.

    Returns
    -------
    ImageFont.FreeTypeFont
        Cached Pillow font object.
    """
    return ImageFont.truetype(font_path, size)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _render_text_to_array(
    font: ImageFont.FreeTypeFont,
    text: str,
    canvas_size: int = 512,
) -> np.ndarray:
    """Render *text* onto a grayscale canvas and return the raw pixel array.

    The canvas is square with side length *canvas_size*.  Text is drawn
    centred so that combining marks stay in the correct relative position.

    Returns
    -------
    np.ndarray
        2-D ``uint8`` array of shape ``(canvas_size, canvas_size)``.
    """
    img = Image.new("L", (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(img)

    # Measure the full text bounding box so we can centre it
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    # Draw position: centre on canvas, offset by bbox origin
    x = (canvas_size - tw) // 2 - bbox[0]
    y = (canvas_size - th) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=255)

    return np.asarray(img, dtype=np.uint8)


def _trim_whitespace(arr: np.ndarray, padding: int = 2) -> np.ndarray:
    """Crop a 2-D grayscale array to the bounding box of non-zero pixels.

    A small *padding* (in pixels) is kept around the content to avoid
    clipping anti-aliased edges.

    Returns
    -------
    np.ndarray
        Trimmed sub-array (still ``uint8``).  If the image is entirely
        blank, a 1×1 zero array is returned.
    """
    rows = np.any(arr > 0, axis=1)
    cols = np.any(arr > 0, axis=0)
    if not rows.any():
        return np.zeros((1, 1), dtype=np.uint8)

    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    # Apply padding while clamping to array bounds
    rmin = max(rmin - padding, 0)
    rmax = min(rmax + padding, arr.shape[0] - 1)
    cmin = max(cmin - padding, 0)
    cmax = min(cmax + padding, arr.shape[1] - 1)

    return arr[rmin : rmax + 1, cmin : cmax + 1]


def _resize_array(
    arr: np.ndarray,
    target_w: int,
    target_h: int,
) -> np.ndarray:
    """Resize a 2-D ``uint8`` array to ``(target_h, target_w)`` using LANCZOS.

    The glyph is fitted inside the target rectangle while preserving aspect
    ratio.  Remaining pixels stay black (0).

    Returns
    -------
    np.ndarray
        Array of shape ``(target_h, target_w)``, dtype ``uint8``.
    """
    src_h, src_w = arr.shape
    if src_h == 0 or src_w == 0:
        return np.zeros((target_h, target_w), dtype=np.uint8)

    # Determine scale to fit glyph into target rectangle
    scale = min(target_w / src_w, target_h / src_h)
    new_w = max(int(src_w * scale), 1)
    new_h = max(int(src_h * scale), 1)

    img = Image.fromarray(arr, mode="L")
    img_resized = img.resize((new_w, new_h), Image.LANCZOS)

    # Centre the resized glyph on a blank canvas
    canvas = np.zeros((target_h, target_w), dtype=np.uint8)
    y_off = (target_h - new_h) // 2
    x_off = (target_w - new_w) // 2
    canvas[y_off : y_off + new_h, x_off : x_off + new_w] = np.asarray(
        img_resized, dtype=np.uint8
    )
    return canvas


def _classify_thai_modifiers(modifiers: str) -> Tuple[str, str]:
    """Split a modifier string into above-marks and below-marks.

    Characters that are neither above nor below Thai marks are treated as
    above marks by default (safe fallback for PUA combining glyphs).

    Returns
    -------
    tuple[str, str]
        ``(above_marks, below_marks)``
    """
    above: list[str] = []
    below: list[str] = []
    for ch in modifiers:
        cp = ord(ch)
        if cp in _THAI_BELOW_MARKS:
            below.append(ch)
        else:
            above.append(ch)
    return "".join(above), "".join(below)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_glyph(
    font_path: str,
    char: str,
    target_w: int,
    target_h: int,
    ss_factor: int = 3,
) -> np.ndarray:
    """Render a single character to a grayscale numpy array.

    The glyph is rendered at ``ss_factor`` × the target size (supersampling),
    trimmed of surrounding whitespace, then downscaled with LANCZOS for
    high-quality anti-aliasing.

    Parameters
    ----------
    font_path : str
        Path to a ``.ttf`` or ``.otf`` font file.
    char : str
        The character to render (single codepoint).
    target_w : int
        Desired output width in pixels.
    target_h : int
        Desired output height in pixels.
    ss_factor : int, optional
        Supersampling multiplier (default ``3``).

    Returns
    -------
    np.ndarray
        ``uint8`` array of shape ``(target_h, target_w)``.
    """
    ss_factor = max(ss_factor, 1)

    # Canvas large enough for the supersampled render
    render_size = max(target_w, target_h) * ss_factor
    font_size = int(render_size * 0.7)  # ~70 % of canvas = comfortable glyph
    font = _load_font(font_path, font_size)

    raw = _render_text_to_array(font, char, canvas_size=render_size)
    trimmed = _trim_whitespace(raw)
    result = _resize_array(trimmed, target_w, target_h)

    logger.debug(
        "render_glyph: char=U+%04X  ss=%d  trimmed=%s  target=(%d,%d)",
        ord(char), ss_factor, trimmed.shape, target_w, target_h,
    )
    return result


def render_composite(
    font_path: str,
    consonant: str,
    modifiers: str,
    target_w: int,
    target_h: int,
    ss_factor: int = 3,
) -> np.ndarray:
    """Render a PUA composite glyph (consonant + combining marks).

    The consonant and its modifiers are drawn together as a single string
    so that the font's own GPOS/mark-attachment tables handle positioning.
    The combined image is then trimmed and resized to the target dimensions.

    Thai combining marks are classified into above-marks and below-marks to
    ensure the correct stacking order when the string is assembled.

    Parameters
    ----------
    font_path : str
        Path to a ``.ttf`` or ``.otf`` font file.
    consonant : str
        Base consonant character.
    modifiers : str
        One or more combining marks (above / below vowels, tone marks, etc.).
    target_w : int
        Desired output width in pixels.
    target_h : int
        Desired output height in pixels.
    ss_factor : int, optional
        Supersampling multiplier (default ``3``).

    Returns
    -------
    np.ndarray
        ``uint8`` array of shape ``(target_h, target_w)``.
    """
    ss_factor = max(ss_factor, 1)

    # Classify and reorder modifiers: below marks come after the consonant
    # in Thai text order, then above marks / tone marks.
    
    # Replace Sara Am (U+0E33) with Nikhahit (U+0E4D) so that PUA glyphs 
    # don't incorrectly include the Sara Aa (cane) part, which is handled separately.
    modifiers_fixed = modifiers.replace("\u0e33", "\u0e4d")
    
    above, below = _classify_thai_modifiers(modifiers_fixed)

    # Assemble composite string in canonical Thai order:
    #   consonant  +  below vowels  +  above vowels / tone marks
    composite_text = consonant + below + above

    render_size = max(target_w, target_h) * ss_factor
    # Use a slightly larger font proportion to give marks room
    font_size = int(render_size * 0.6)
    font = _load_font(font_path, font_size)

    raw = _render_text_to_array(font, composite_text, canvas_size=render_size)
    trimmed = _trim_whitespace(raw, padding=4)
    result = _resize_array(trimmed, target_w, target_h)

    logger.debug(
        "render_composite: consonant=U+%04X  mods=%r  ss=%d  "
        "trimmed=%s  target=(%d,%d)",
        ord(consonant), modifiers, ss_factor, trimmed.shape,
        target_w, target_h,
    )
    return result


def measure_glyph(
    font_path: str,
    char: str,
    font_size: int = 200,
) -> Dict[str, object]:
    """Measure the metrics of a single glyph.

    Parameters
    ----------
    font_path : str
        Path to a ``.ttf`` or ``.otf`` font file.
    char : str
        The character to measure.
    font_size : int, optional
        Font size in pixels for measurement (default ``200``).

    Returns
    -------
    dict
        ``{'width': int, 'height': int, 'bbox': tuple,
          'ascent': int, 'descent': int}``

        - **width / height** – bounding-box dimensions of the rendered glyph.
        - **bbox** – ``(x_min, y_min, x_max, y_max)`` as returned by Pillow.
        - **ascent / descent** – font-level metrics (positive upward).
    """
    font = _load_font(font_path, font_size)
    ascent, descent = font.getmetrics()

    # Draw on a temporary surface to get the precise bbox
    tmp = Image.new("L", (1, 1), 0)
    draw = ImageDraw.Draw(tmp)
    bbox = draw.textbbox((0, 0), char, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    return {
        "width": width,
        "height": height,
        "bbox": bbox,
        "ascent": ascent,
        "descent": descent,
    }


def render_text_preview(
    font_path: str,
    text: str,
    glyph_metrics: Dict[str, dict],
    glyph_images: Dict[str, np.ndarray],
    canvas_width: int = 3200,
) -> Image.Image:
    """Simulate game-engine text rendering using pre-computed glyph data.

    Each entry in *glyph_metrics* is expected to contain at least::

        {
            "ox": int,   # x-offset (bearing-X): shift glyph right
            "oy": int,   # y-offset (bearing-Y): shift glyph down from baseline
            "adv": int,  # advance width: cursor moves right after drawing
            "w": int,    # glyph image width
            "h": int,    # glyph image height
        }

    Parameters
    ----------
    font_path : str
        Path to the font file (used only for fallback rendering of glyphs
        missing from *glyph_images*).
    text : str
        The Unicode string to render.
    glyph_metrics : dict[str, dict]
        Per-character metric dictionaries keyed by the character itself.
    glyph_images : dict[str, np.ndarray]
        Pre-rendered ``uint8`` grayscale glyph arrays keyed by character.
    canvas_width : int, optional
        Width of the output canvas in pixels (default ``3200``).

    Returns
    -------
    PIL.Image.Image
        RGB image of the rendered text line on a dark background.
    """
    # Determine line height from the first available glyph's height, or a
    # sensible default derived from the font metrics.
    line_height = 64  # default
    if glyph_metrics:
        sample = next(iter(glyph_metrics.values()))
        line_height = max(sample.get("h", 64), line_height)

    canvas_height = line_height * 3  # generous vertical room
    canvas = Image.new("RGB", (canvas_width, canvas_height), (30, 30, 30))

    baseline_y = canvas_height // 2  # baseline roughly centred

    cursor_x = 20  # left margin

    for ch in text:
        metrics = glyph_metrics.get(ch)
        glyph_arr = glyph_images.get(ch)

        if metrics is None or glyph_arr is None:
            # Fallback: render on the fly at a reasonable size
            try:
                fallback_h = line_height
                fallback_w = max(int(fallback_h * 0.6), 1)
                glyph_arr = render_glyph(
                    font_path, ch, fallback_w, fallback_h, ss_factor=2
                )
                metrics = {
                    "ox": 0,
                    "oy": 0,
                    "adv": fallback_w,
                    "w": fallback_w,
                    "h": fallback_h,
                }
            except Exception:
                logger.warning("Cannot render fallback glyph for U+%04X", ord(ch))
                cursor_x += line_height // 2  # skip
                continue

        ox = metrics.get("ox", 0)
        oy = metrics.get("oy", 0)
        adv = metrics.get("adv", metrics.get("w", 0))
        gh, gw = glyph_arr.shape[:2]

        # Place glyph: x = cursor + ox,  y = baseline - glyph_height + oy
        draw_x = cursor_x + ox
        draw_y = baseline_y - gh + oy

        # Clamp to canvas
        if draw_x < 0:
            draw_x = 0
        if draw_y < 0:
            draw_y = 0

        # Paste glyph onto canvas (alpha-blend via grayscale → RGB mask)
        glyph_img = Image.fromarray(glyph_arr, mode="L")
        # Create a white glyph image to composite with the grayscale as mask
        white = Image.new("RGB", (gw, gh), (255, 255, 255))

        # Ensure paste region fits within canvas
        paste_w = min(gw, canvas_width - draw_x)
        paste_h = min(gh, canvas_height - draw_y)
        if paste_w <= 0 or paste_h <= 0:
            cursor_x += adv
            continue

        if paste_w < gw or paste_h < gh:
            white = white.crop((0, 0, paste_w, paste_h))
            glyph_img = glyph_img.crop((0, 0, paste_w, paste_h))

        canvas.paste(white, (draw_x, draw_y), mask=glyph_img)

        cursor_x += adv

        # Stop if we exceed canvas
        if cursor_x >= canvas_width - 20:
            logger.info("Text preview truncated at canvas width %d", canvas_width)
            break

    return canvas


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

def clear_font_cache() -> None:
    """Clear the internal LRU font cache.

    Useful when font files are regenerated on disk and stale objects
    should be evicted.
    """
    _load_font.cache_clear()
    logger.info("Font cache cleared.")


if __name__ == "__main__":
    # Quick smoke test
    import sys

    if len(sys.argv) < 2:
        print("Usage: python font_renderer.py <font_path> [char]")
        sys.exit(1)

    _font = sys.argv[1]
    _char = sys.argv[2] if len(sys.argv) > 2 else "A"

    arr = render_glyph(_font, _char, 64, 64)
    print(f"render_glyph  → shape={arr.shape}, dtype={arr.dtype}, "
          f"min={arr.min()}, max={arr.max()}")

    info = measure_glyph(_font, _char)
    print(f"measure_glyph → {info}")

    print("OK – font_renderer smoke test passed.")
