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

    def load_mapping(self, mapping_path=None):
        path_to_use = mapping_path
        if not path_to_use or not os.path.exists(path_to_use):
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
                self.contextual[k] = v
            else:
                self.standard[k] = v.upper()

        # Build reverse maps
        for thai, hex_code in self.standard.items():
            try:
                if len(hex_code) == 1:
                    cp = ord(hex_code)
                else:
                    cp = int(hex_code, 16)
                if cp not in self.reverse or len(thai) > len(self.reverse[cp]):
                    self.reverse[cp] = thai
            except (ValueError, OverflowError):
                pass

        for thai, hex_list in self.contextual.items():
            try:
                pua_cp = ord(hex_list[0]) if len(hex_list[0]) == 1 else int(hex_list[0], 16)
                vowel_cp = ord(hex_list[1]) if len(hex_list[1]) == 1 else int(hex_list[1], 16)
                self.ctx_reverse[(pua_cp, vowel_cp)] = thai
            except (ValueError, OverflowError, IndexError):
                pass

    def encode(self, text: str) -> str:
        """Replace Thai words with PUA chars. Contextual first, longest match first."""
        if not text: return text
        result = text

        for word in sorted(self.contextual.keys(), key=len, reverse=True):
            try:
                out_chars = []
                for h in self.contextual[word]:
                    if len(h) == 1:
                        out_chars.append(h)
                    else:
                        out_chars.append(chr(int(h, 16)))
                out = "".join(out_chars)
            except (ValueError, OverflowError):
                continue
            result = result.replace(word, out)

        for word in sorted(self.standard.keys(), key=len, reverse=True):
            hex_code = self.standard[word]
            try:
                if len(hex_code) == 1:
                    pua_char = hex_code
                else:
                    pua_char = chr(int(hex_code, 16))
            except (ValueError, OverflowError):
                continue
            result = result.replace(word, pua_char)

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
