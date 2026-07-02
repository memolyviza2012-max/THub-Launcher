"""TGlyph Export Profile Plugins."""
from . import bmfont_exporter, unity_tmp_exporter

PROFILES = {
    "bmfont": bmfont_exporter.export,
    "unity_tmp": unity_tmp_exporter.export,
}
