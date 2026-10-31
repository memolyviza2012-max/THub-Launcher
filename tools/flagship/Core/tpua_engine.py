import json
import os

# Default mapping path: look in the same directory as this engine file (Core/mapping.json)
DEFAULT_MAPPING_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapping.json")

class TPUAEngine:
    def __init__(self, mapping_path=None):
        self.standard = {}
        self.contextual = {}
        self.reverse = {}
        self.ctx_reverse = {}
        self.load_mapping(mapping_path)

    @staticmethod
    def _to_codepoint(v):
        """Normalize a mapping value to a unicode codepoint int.
        Accepts hex strings ('f000') and literal characters (U+F000),
        because mapping files from different generators use either format."""
        if isinstance(v, int):
            return v
        s = str(v).strip()
        if not s:
            return None
        try:
            return int(s, 16)
        except ValueError:
            pass
        if len(s) == 1:
            return ord(s)
        return None

    def load_mapping(self, mapping_path=None):
        path_to_use = mapping_path
        if not path_to_use or not os.path.exists(mapping_path):
            # Fallback to default mapping in Core directory
            path_to_use = DEFAULT_MAPPING_PATH

        if not os.path.exists(path_to_use):
            print(f"TPUAEngine Warning: Mapping file not found at {path_to_use}. PUA operations will do nothing.")
            return

        with open(path_to_use, "r", encoding="utf-8") as f:
            raw = json.load(f)

        for k, v in raw.items():
            if k.startswith("_"): continue
            if isinstance(v, list):
                cps = [self._to_codepoint(h) for h in v[:2]]
                if len(cps) == 2 and all(c is not None for c in cps):
                    self.contextual[k] = cps
            else:
                cp = self._to_codepoint(v)
                if cp is not None:
                    self.standard[k] = cp

        # Build reverse maps
        for thai, cp in self.standard.items():
            if cp not in self.reverse or len(thai) > len(self.reverse[cp]):
                self.reverse[cp] = thai

        for thai, (pua_cp, vowel_cp) in self.contextual.items():
            self.ctx_reverse[(pua_cp, vowel_cp)] = thai

    def encode(self, text: str) -> str:
        """Replace Thai words with PUA chars. Contextual first, longest match first."""
        if not text: return text
        result = text

        for word in sorted(self.contextual.keys(), key=len, reverse=True):
            pua_cp, vowel_cp = self.contextual[word]
            result = result.replace(word, chr(pua_cp) + chr(vowel_cp))

        for word in sorted(self.standard.keys(), key=len, reverse=True):
            result = result.replace(word, chr(self.standard[word]))

        return result

    def decode(self, text: str) -> str:
        """Replace PUA characters back to Thai text. Longest match first."""
        if not text: return text
        result = text

        for (pua_cp, vowel_cp), thai in sorted(self.ctx_reverse.items(), key=lambda x: -len(x[1])):
            pua_char = chr(pua_cp)
            vowel_char = chr(vowel_cp)
            pattern = pua_char + vowel_char
            result = result.replace(pattern, thai)

        for cp in sorted(self.reverse.keys(), key=lambda x: -len(self.reverse[x])):
            thai = self.reverse[cp]
            result = result.replace(chr(cp), thai)

        result = result.replace('ำา', 'ำ')
        return result
