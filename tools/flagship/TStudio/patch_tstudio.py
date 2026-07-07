import sys
import re

file_path = 'e:/Mod_Workspace/Modder_project/modder-hub/tools/flagship/TStudio/tstudio_app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Bug 1: Change self._workers = [] to {}
content = content.replace('self._workers = []  # Keep references', 'self._workers = {}  # Keep references')

# Replace lambda _ worker.signals
pattern1 = r'worker\.signals\.finished\.connect\(lambda _: self\._workers\.remove\(worker\) if worker in self\._workers else None\)\n\s*worker\.signals\.error\.connect\(lambda _: self\._workers\.remove\(worker\) if worker in self\._workers else None\)\n\s*self\._workers\.append\(worker\)'
repl1 = r'''wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker'''
content = re.sub(pattern1, repl1, content)

# Replace lambda _, w=worker worker.signals
pattern2 = r'worker\.signals\.finished\.connect\(lambda _, w=worker: self\._workers\.remove\(w\) if w in self\._workers else None\)\n\s*worker\.signals\.error\.connect\(lambda _, w=worker: self\._workers\.remove\(w\) if w in self\._workers else None\)\n\s*self\._workers\.append\(worker\)'
repl2 = r'''wid = id(worker)
            worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
            worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
            self._workers[wid] = worker'''
content = re.sub(pattern2, repl2, content)

# Bug 2: Optimize HtmlDelegate
html_delegate_old = '''class HtmlDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        from PyQt6.QtWidgets import QStyleOptionViewItem
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        painter.save()
        
        # Draw background
        bg = index.data(Qt.ItemDataRole.BackgroundRole)
        if bg:
            painter.fillRect(option.rect, bg)
            
        # Draw selection
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        doc = QTextDocument()
        doc.setDefaultStyleSheet("body { color: #cdd6f4; font-family: inherit; font-size: 13px; }")
        
        text = options.text
        # if text does not contain HTML tags, escape it to avoid parsing issues?
        # In our case, the html_source has tags. If not, it's plain text.
        if "<span" not in text:
            # simple escape
            text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
        doc.setHtml(f"<body>{text}</body>")
        doc.setDocumentMargin(4)

        painter.translate(option.rect.left(), option.rect.top())
        clip = option.rect.translated(-option.rect.left(), -option.rect.top())
        painter.setClipRect(clip)

        ctx = QAbstractTextDocumentLayout.PaintContext()
        ctx.palette = option.palette
        doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        options = option
        self.initStyleOption(options, index)
        doc = QTextDocument()
        text = options.text
        if "<span" not in text:
            text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        doc.setHtml(text)
        doc.setDocumentMargin(4)
        return QSize(int(doc.idealWidth()), 30)'''

html_delegate_new = '''class HtmlDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = QTextDocument()
        self.doc.setDefaultStyleSheet("body { color: #cdd6f4; font-family: inherit; font-size: 13px; }")
        self.doc.setDocumentMargin(4)

    def paint(self, painter, option, index):
        from PyQt6.QtWidgets import QStyleOptionViewItem
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        painter.save()
        
        # Draw background
        bg = index.data(Qt.ItemDataRole.BackgroundRole)
        if bg:
            painter.fillRect(option.rect, bg)
            
        # Draw selection
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        text = options.text
        # if text does not contain HTML tags, escape it to avoid parsing issues?
        # In our case, the html_source has tags. If not, it's plain text.
        if "<span" not in text:
            # simple escape
            text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
        self.doc.setHtml(f"<body>{text}</body>")

        painter.translate(option.rect.left(), option.rect.top())
        clip = option.rect.translated(-option.rect.left(), -option.rect.top())
        painter.setClipRect(clip)

        ctx = QAbstractTextDocumentLayout.PaintContext()
        ctx.palette = option.palette
        self.doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        options = option
        self.initStyleOption(options, index)
        text = options.text
        if "<span" not in text:
            text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.doc.setHtml(text)
        return QSize(int(self.doc.idealWidth()), 30)'''

if html_delegate_old in content:
    content = content.replace(html_delegate_old, html_delegate_new)
else:
    print("WARNING: HtmlDelegate old content not found!")

# Bug 3: Add tlm_dock to addDockWidget before restoreState
tlm_dock_old = '''        self.tlm_dock.hide()

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.glossary_dock)'''
tlm_dock_new = '''        self.tlm_dock.hide()
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.tlm_dock)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.glossary_dock)'''

if tlm_dock_old in content:
    content = content.replace(tlm_dock_old, tlm_dock_new)
else:
    print("WARNING: tlm_dock old content not found!")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Patched successfully.')
