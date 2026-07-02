# unity_tmp_exporter.py
"""
Export Profile: Unity TextMeshPro JSON Metrics
Compatible with: Unity 2020+ with TextMeshPro package.

This module generates a JSON file containing glyph metrics in the format
that TextMeshPro uses internally. Modders can use tools like UABEA or
UnityEX to inject these metrics into an existing .asset file.

Coordinate System Note
----------------------
Unity / TextMeshPro stores glyph rects with a **bottom-left (0, 0) origin**,
which is the opposite of TGlyph's top-left atlas origin.  The Y coordinate
must therefore be flipped before writing:

    tmp_y = atlas_h - rect.y - rect.h

This ensures that a glyph at the very top of the atlas (rect.y = 0) maps to
the bottom of Unity's coordinate space (tmp_y = atlas_h - rect.h).
"""

import json
from pathlib import Path


def export(
    rects: list,          # list of AtlasRect objects from atlas_packer
    metrics: dict,        # dict[codepoint:int -> dict{'ox','oy','adv'}]
    atlas_w: int,
    atlas_h: int,
    font_name: str,
    line_height: int,
    png_path: str,        # absolute path to the atlas .png already saved
    out_dir: str,
) -> str:
    """Generate Unity TextMeshPro JSON metrics file.

    The output file is written to ``<out_dir>/<font_name>_tmp.json``.
    The JSON structure mirrors the glyph table layout used by TMP's internal
    asset format so it can be parsed and re-injected with asset editing tools
    such as UABEA or UnityEX.

    Y-Axis Flip
    -----------
    TGlyph uses a **top-left origin** (y increases downward).  Unity TMP uses
    a **bottom-left origin** (y increases upward).  The conversion applied to
    every glyph rect is::

        tmp_y = atlas_h - rect.y - rect.h

    Parameters
    ----------
    rects : list[AtlasRect]
        Placed glyph rectangles as returned by ``AtlasPacker.pack()``.
        Each object must expose: ``.codepoint`` (int), ``.x``, ``.y``,
        ``.w``, ``.h`` (int).
    metrics : dict[int, dict]
        Mapping from codepoint to glyph metric dict with keys:
        ``'ox'`` (int) – horizontal bearing X (``horizontalBearingX``),
        ``'oy'`` (int) – horizontal bearing Y (ignored; rect.h is used instead),
        ``'adv'`` (int) – horizontal advance (``horizontalAdvance``).
        Missing codepoints fall back to ``ox=0, adv=rect.w``.
    atlas_w : int
        Total atlas image width in pixels.
    atlas_h : int
        Total atlas image height in pixels.
    font_name : str
        Logical font name written into the ``font_name`` field and used as
        the stem of the output file (``<font_name>_tmp.json``).
    line_height : int
        Pixel distance from one line baseline to the next.
    png_path : str
        Absolute path to the already-saved atlas PNG (stored for reference
        only; TMP resolves the texture via the .asset file).
    out_dir : str
        Directory where the JSON file will be written.  Created if absent.

    Returns
    -------
    str
        Absolute path to the generated JSON file.
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    json_path = out_path / f"{font_name}_tmp.json"

    glyphs: list[dict] = []

    for r in rects:
        cp = r.codepoint
        m = metrics.get(cp, {})

        bearing_x: int = m.get("ox", 0)
        # horizontalBearingY approximation: how far the glyph top extends
        # above the baseline. TMP expects a positive value; using glyph
        # cell height is a safe default when proper FreeType metrics are
        # unavailable.
        bearing_y: int = r.h
        advance: int = m.get("adv", r.w)

        # Flip Y from top-left to bottom-left origin.
        flipped_y: int = atlas_h - r.y - r.h

        glyphs.append(
            {
                "unicode": cp,
                "glyphRect": {
                    "x": r.x,
                    "y": flipped_y,
                    "width": r.w,
                    "height": r.h,
                },
                "metrics": {
                    "horizontalBearingX": bearing_x,
                    "horizontalBearingY": bearing_y,
                    "horizontalAdvance": advance,
                },
            }
        )

    payload: dict = {
        "font_name": font_name,
        "line_height": line_height,
        "atlas_width": atlas_w,
        "atlas_height": atlas_h,
        "glyphs": glyphs,
    }

    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return str(json_path.resolve())
