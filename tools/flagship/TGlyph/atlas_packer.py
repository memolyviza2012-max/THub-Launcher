"""atlas_packer.py – Pack multiple glyph images into a texture atlas.

Implements a **Shelf Packing Algorithm**:
    1. Sort glyphs by height (tallest first).
    2. Place glyphs left-to-right in rows ("shelves").
    3. When a row is full, start a new shelf below.

Supports *reserved areas* – rectangles that must not be overwritten (e.g.
existing Latin characters already present on the base atlas image).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class AtlasRect:
    """Axis-aligned rectangle placed on the atlas, tied to a codepoint."""

    x: int
    y: int
    w: int
    h: int
    codepoint: int


@dataclass
class _Shelf:
    """Internal representation of a single horizontal shelf."""

    y: int          # top-edge y of this shelf
    height: int     # tallest item placed so far (shelf height)
    cursor_x: int   # next free x position on this shelf


# ---------------------------------------------------------------------------
# Packer
# ---------------------------------------------------------------------------

class AtlasPacker:
    """Shelf-based 2-D rectangle packer with reserved-area support.

    Parameters
    ----------
    width : int
        Atlas width in pixels (default 4096).
    height : int
        Atlas height in pixels (default 4096).
    padding : int
        Gap in pixels inserted between every glyph and between glyphs and
        reserved areas (default 2).
    """

    def __init__(self, width: int = 4096, height: int = 4096, padding: int = 2) -> None:
        self.width: int = width
        self.height: int = height
        self.padding: int = padding
        self._reserved: list[tuple[int, int, int, int]] = []  # (x, y, w, h)

    # -- Reserved areas -----------------------------------------------------

    def add_reserved(self, x: int, y: int, w: int, h: int) -> None:
        """Mark a rectangle as reserved (will not be overwritten).

        Parameters
        ----------
        x, y : int
            Top-left corner of the reserved area.
        w, h : int
            Width and height of the reserved area.
        """
        self._reserved.append((x, y, w, h))

    # -- Collision helpers --------------------------------------------------

    def _overlaps_reserved(self, rx: int, ry: int, rw: int, rh: int) -> bool:
        """Return *True* if the candidate rectangle overlaps any reserved area.

        A padding-expanded zone around each reserved area is also considered
        occupied so that glyphs never touch reserved content.
        """
        pad = self.padding
        for (ax, ay, aw, ah) in self._reserved:
            # Expand reserved area by padding on each side.
            if (rx + rw > ax - pad and rx < ax + aw + pad and
                    ry + rh > ay - pad and ry < ay + ah + pad):
                return True
        return False

    # -- Core packing -------------------------------------------------------

    def pack(self, glyphs: list[tuple[int, int, int]]) -> list[AtlasRect]:
        """Pack a list of glyphs into the atlas.

        Parameters
        ----------
        glyphs : list[tuple[int, int, int]]
            Each element is ``(codepoint, width, height)``.

        Returns
        -------
        list[AtlasRect]
            Assigned positions for every glyph that has a positive size.

        Raises
        ------
        ValueError
            If any glyph cannot fit inside the atlas.
        """
        pad = self.padding

        # Filter out zero-size glyphs and sort remaining by height descending.
        valid = [(cp, w, h) for cp, w, h in glyphs if w > 0 and h > 0]
        valid.sort(key=lambda g: g[2], reverse=True)

        shelves: list[_Shelf] = []
        results: list[AtlasRect] = []

        for codepoint, gw, gh in valid:
            placed = False

            # Try existing shelves first.
            for shelf in shelves:
                candidate_x = shelf.cursor_x
                candidate_y = shelf.y

                # Check atlas right boundary.
                if candidate_x + gw + pad > self.width:
                    continue

                # Check atlas bottom boundary.
                if candidate_y + gh > self.height:
                    continue

                # Ensure no overlap with reserved areas.
                if self._overlaps_reserved(candidate_x, candidate_y, gw, gh):
                    # Try advancing past reserved areas on this shelf.
                    candidate_x = self._find_free_x_on_shelf(
                        shelf, gw, gh, candidate_x,
                    )
                    if candidate_x is None:
                        continue

                # Place the glyph.
                results.append(AtlasRect(
                    x=candidate_x,
                    y=candidate_y,
                    w=gw,
                    h=gh,
                    codepoint=codepoint,
                ))
                shelf.cursor_x = candidate_x + gw + pad
                shelf.height = max(shelf.height, gh)
                placed = True
                break

            if not placed:
                # Open a new shelf below the last one.
                new_y = 0 if not shelves else (
                    shelves[-1].y + shelves[-1].height + pad
                )

                # Check that the new shelf fits vertically.
                if new_y + gh > self.height:
                    raise ValueError(
                        f"Atlas overflow: cannot place glyph U+{codepoint:04X} "
                        f"({gw}×{gh}) — atlas {self.width}×{self.height} is full."
                    )

                start_x = pad
                # Skip reserved areas on the brand-new shelf.
                if self._overlaps_reserved(start_x, new_y, gw, gh):
                    maybe_x = self._find_free_x_on_shelf_raw(
                        new_y, gh, gw, start_x,
                    )
                    if maybe_x is None:
                        raise ValueError(
                            f"Atlas overflow: cannot place glyph U+{codepoint:04X} "
                            f"({gw}×{gh}) on a new shelf at y={new_y}."
                        )
                    start_x = maybe_x

                new_shelf = _Shelf(y=new_y, height=gh, cursor_x=start_x + gw + pad)
                shelves.append(new_shelf)

                results.append(AtlasRect(
                    x=start_x,
                    y=new_y,
                    w=gw,
                    h=gh,
                    codepoint=codepoint,
                ))

        return results

    # -- Internal scan helpers ----------------------------------------------

    def _find_free_x_on_shelf(
        self,
        shelf: _Shelf,
        gw: int,
        gh: int,
        start_x: int,
    ) -> Optional[int]:
        """Scan rightward on *shelf* for the first x where the glyph fits."""
        return self._find_free_x_on_shelf_raw(shelf.y, gh, gw, start_x)

    def _find_free_x_on_shelf_raw(
        self,
        shelf_y: int,
        shelf_gh: int,
        gw: int,
        start_x: int,
    ) -> Optional[int]:
        """Low-level scan: advance *start_x* rightward to dodge reserved areas.

        Returns the first valid x, or *None* if the glyph cannot fit on this
        row without exceeding the atlas width.
        """
        pad = self.padding
        x = start_x

        # Safety limit to avoid infinite loops on degenerate reserved layouts.
        max_iter = self.width
        for _ in range(max_iter):
            if x + gw + pad > self.width:
                return None

            if not self._overlaps_reserved(x, shelf_y, gw, shelf_gh):
                return x

            # Jump past the blocking reserved area.
            advanced = False
            for (ax, ay, aw, ah) in self._reserved:
                # Check if this reserved area actually blocks us.
                if (x + gw > ax - pad and x < ax + aw + pad and
                        shelf_y + shelf_gh > ay - pad and shelf_y < ay + ah + pad):
                    x = ax + aw + pad
                    advanced = True
                    break
            if not advanced:
                # Should not happen, but guard against infinite loop.
                x += 1
        return None

    # -- Image compositing --------------------------------------------------

    def get_atlas_image(
        self,
        rects: list[AtlasRect],
        glyph_images: dict[int, np.ndarray],
        base_image: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Composite glyph images onto an atlas canvas.

        Parameters
        ----------
        rects : list[AtlasRect]
            Positioned rectangles returned by :meth:`pack`.
        glyph_images : dict[int, np.ndarray]
            Mapping from codepoint to glyph pixel data (H×W or H×W×C).
        base_image : np.ndarray, optional
            If provided, draw on top of a copy of this image (preserving any
            reserved / pre-existing content).  Otherwise a blank (zeros)
            canvas is created.

        Returns
        -------
        np.ndarray
            The composited atlas image.
        """
        if base_image is not None:
            atlas = base_image.copy()
        else:
            # Create RGBA by default if no base image, so background is transparent
            atlas = np.zeros((self.height, self.width, 4), dtype=np.uint8)

        is_rgba = (atlas.ndim == 3 and atlas.shape[2] == 4)

        for rect in rects:
            img = glyph_images.get(rect.codepoint)
            if img is None:
                continue

            # Crop the source image to the declared rect size so we never
            # write out-of-bounds even if the caller provides oversized data.
            src = img[: rect.h, : rect.w]
            sh, sw = src.shape[:2]

            # Ensure we do not exceed atlas boundaries.
            dst_h = min(sh, self.height - rect.y)
            dst_w = min(sw, self.width - rect.x)
            if dst_h <= 0 or dst_w <= 0:
                continue
                
            src_cropped = src[:dst_h, :dst_w]

            if is_rgba:
                # Convert grayscale src to RGBA (White text, alpha = src value)
                rgba_src = np.zeros((dst_h, dst_w, 4), dtype=np.uint8)
                rgba_src[..., 0] = 255
                rgba_src[..., 1] = 255
                rgba_src[..., 2] = 255
                rgba_src[..., 3] = src_cropped
                atlas[rect.y : rect.y + dst_h, rect.x : rect.x + dst_w] = rgba_src
            else:
                atlas[rect.y : rect.y + dst_h, rect.x : rect.x + dst_w] = src_cropped

        return atlas


# ---------------------------------------------------------------------------
# Coordinate export
# ---------------------------------------------------------------------------

def generate_coords_json(rects: list[AtlasRect]) -> dict:
    """Convert a list of placed rectangles into a JSON-friendly dictionary.

    Returns
    -------
    dict
        ``{codepoint_hex_str: {'x': int, 'y': int, 'w': int, 'h': int}}``
        where the key is the uppercase hex codepoint, e.g. ``"F000"``.
    """
    coords: dict[str, dict[str, int]] = {}
    for r in rects:
        key = f"{r.codepoint:04X}"
        coords[key] = {"x": r.x, "y": r.y, "w": r.w, "h": r.h}
    return coords
