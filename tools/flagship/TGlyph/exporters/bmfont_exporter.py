# bmfont_exporter.py
"""
Export Profile: BMFont Standard (.fnt + .png)
Compatible with: Godot Engine, RPG Maker, Unreal Engine 4/5 (import via plugin),
and hundreds of indie game engines.

Format Spec: http://www.angelcode.com/products/bmfont/doc/file_format.html

The BMFont text format uses top-left (0, 0) as the image origin, which matches
TGlyph's atlas coordinate system directly — no Y-axis flip is required.
"""

from pathlib import Path
from typing import Any


def export(
    rects: list,          # list of AtlasRect objects from atlas_packer
    metrics: dict,        # dict[codepoint:int -> dict{'ox','oy','adv'}]
    atlas_w: int,
    atlas_h: int,
    font_name: str,
    line_height: int,
    png_path: str,        # absolute path to the atlas .png already saved
    out_dir: str,
    base: int = 32,       # baseline offset from top of line (pixels)
) -> str:
    """Generate a .fnt file (BMFont text format) for the given atlas.

    The output file is written to ``<out_dir>/<font_name>.fnt``.  The atlas
    PNG referenced inside the file is stored as a bare basename so that the
    .fnt and .png can be moved together without path breakage.

    Parameters
    ----------
    rects : list[AtlasRect]
        Placed glyph rectangles as returned by ``AtlasPacker.pack()``.
        Each object must expose: ``.codepoint`` (int), ``.x``, ``.y``,
        ``.w``, ``.h`` (int).
    metrics : dict[int, dict]
        Mapping from codepoint to glyph metric dict with keys:
        ``'ox'`` (int) – horizontal bearing / x-offset,
        ``'oy'`` (int) – vertical bearing / y-offset,
        ``'adv'`` (int) – horizontal advance width.
        Missing codepoints fall back to ``ox=0, oy=0, adv=rect.w``.
    atlas_w : int
        Total atlas image width in pixels (``scaleW``).
    atlas_h : int
        Total atlas image height in pixels (``scaleH``).
    font_name : str
        Logical font name embedded in the ``info`` line and used as the
        stem of the output file (``<font_name>.fnt``).
    line_height : int
        Pixel distance from one line baseline to the next (``lineHeight``).
    png_path : str
        Absolute path to the already-saved atlas PNG.  Only the basename is
        written into the .fnt file.
    out_dir : str
        Directory where the .fnt file will be written.  Created if absent.
    base : int, optional
        Pixel offset from the top of a line to the baseline (``base``).
        Defaults to 32.

    Returns
    -------
    str
        Absolute path to the generated .fnt file.
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    fnt_path = out_path / f"{font_name}.fnt"
    png_basename = Path(png_path).name

    lines: list[str] = []

    # ------------------------------------------------------------------
    # info line
    # ------------------------------------------------------------------
    lines.append(
        f'info face="{font_name}" size={line_height} bold=0 italic=0 '
        f'charset="" unicode=1 stretchH=100 smooth=1 aa=1 '
        f'padding=0,0,0,0 spacing=1,1'
    )

    # ------------------------------------------------------------------
    # common line
    # ------------------------------------------------------------------
    lines.append(
        f"common lineHeight={line_height} base={base} "
        f"scaleW={atlas_w} scaleH={atlas_h} pages=1 packed=0"
    )

    # ------------------------------------------------------------------
    # page line
    # ------------------------------------------------------------------
    lines.append(f'page id=0 file="{png_basename}"')

    # ------------------------------------------------------------------
    # chars block
    # ------------------------------------------------------------------
    lines.append(f"chars count={len(rects)}")

    for r in rects:
        cp = r.codepoint
        m = metrics.get(cp, {})

        ox: int = m.get("ox", 0)
        oy: int = m.get("oy", 0)
        adv: int = m.get("adv", r.w)  # fallback: advance = glyph cell width

        lines.append(
            f"char id={cp:<6d}"
            f"  x={r.x:<6d}"
            f"  y={r.y:<6d}"
            f"  width={r.w:<6d}"
            f"  height={r.h:<6d}"
            f"  xoffset={ox:<6d}"
            f"  yoffset={oy:<6d}"
            f"  xadvance={adv:<6d}"
            f"  page=0"
            f"  chnl=15"
        )

    # ------------------------------------------------------------------
    # Write file (Unix line endings for maximum cross-engine compatibility)
    # ------------------------------------------------------------------
    content = "\n".join(lines) + "\n"
    fnt_path.write_text(content, encoding="utf-8")

    return str(fnt_path.resolve())
