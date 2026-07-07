from fontTools.ttLib import TTFont
from fontTools.pens.qtPen import QtPen
from PyQt6.QtGui import QPainterPath, QTransform

class VisualFontEngine:
    def __init__(self, font_path):
        self.font_path = font_path
        self.font = TTFont(font_path)
        self.glyf = self.font['glyf']
        self.cmap = self.font.getBestCmap()
        self.hmtx = self.font['hmtx']
        self.upm = self.font['head'].unitsPerEm

    def get_glyph_path_and_width(self, unicode_char):
        """Returns (QPainterPath, advance_width) for a given unicode character."""
        g_name = self.cmap.get(ord(unicode_char))
        if not g_name or g_name not in self.glyf:
            return QPainterPath(), 0

        # Create a PyQt6 QPainterPath and pass it to QtPen to avoid PyQt5/PyQt6 conflicts
        path = QPainterPath()
        pen = QtPen(self.glyf, path=path)
        self.glyf[g_name].draw(pen, self.glyf)

        # Get width
        width = self.hmtx.metrics[g_name][0]
        return path, width

    def get_f700_type(self, unicode_char):
        """
        Categorizes the character based on MacThai F700 rules to determine which offsets apply.
        Returns: 'base', 'upper_vowel', 'tone_mark', 'lower_vowel'
        """
        cp = ord(unicode_char)
        if cp in [0x0E34, 0x0E35, 0x0E36, 0x0E37, 0x0E31, 0x0E4D, 0x0E47]:
            return 'upper_vowel'
        if cp in [0x0E48, 0x0E49, 0x0E4A, 0x0E4B, 0x0E4C]:
            return 'tone_mark'
        if cp in [0x0E38, 0x0E39, 0x0E3A]:
            return 'lower_vowel'
        return 'base'

    def close(self):
        self.font.close()
