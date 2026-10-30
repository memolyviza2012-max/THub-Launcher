from dataclasses import dataclass
import re

_PROTECTED = re.compile(r'(<[^>]+>|\\n|\\r|\n|\r|\$\$[^\$]+\$\$|#[A-Za-z0-9_]+|~[A-Za-z0-9_]+|\{[^}\r\n]+\}|\[\[[^\]]+\]\]|\[(?!TAG_\d+\])[a-zA-Z0-9_.]+\]|%(?:[0-9.]*[a-zA-Z]+|[0-9]+)|@)')


def tags_match(source, target):
    return _PROTECTED.findall(source) == _PROTECTED.findall(target)


def apply_glossary_snapshot(text, glossary):
    for term, value in sorted(glossary.items(), key=lambda pair: len(str(pair[0])), reverse=True):
        term = str(term).strip()
        value = value[0] if isinstance(value, list) and value else value
        value = str(value or '').strip()
        if not term or not value:
            continue
        if term in text:
            text = text.replace(term, value)
        elif len(term) > 2 and term.lower() in text.lower():
            text = re.sub(re.escape(term), lambda _: value, text, flags=re.IGNORECASE)
    return text


class WebTransportError(Exception):
    """Terminal for automatic retry, especially after ambiguous browser delivery."""


@dataclass(frozen=True)
class RowTarget:
    model: object
    data: object
    item: object
    row: int
    path: str
    source: str
    original: str
    field: str
    row_id: str

    @classmethod
    def capture(cls, window, row, field='trans'):
        model = window.model
        item = model._data[row]
        return cls(model, model._data, item, row, str(getattr(window, 'csv_path', '')),
                   item.get('source', ''), item.get(field, ''), field, str(item.get('id', '')))

    def matches(self, window):
        return (not getattr(window, '_is_closing', False)
                and window.model is self.model and self.model._data is self.data
                and str(getattr(window, 'csv_path', '')) == self.path
                and 0 <= self.row < len(self.data) and self.data[self.row] is self.item
                and self.item.get('source', '') == self.source
                and str(self.item.get('id', '')) == self.row_id
                and self.item.get(self.field, '') == self.original)

