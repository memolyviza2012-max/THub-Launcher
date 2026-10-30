"""Small channel controls on existing screens; remote checks always run in workers."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QComboBox, QPushButton, QDialog,
                            QFormLayout, QLineEdit, QSpinBox, QLabel, QDialogButtonBox,
                            QMessageBox)

from .settings import load_settings, save_settings, state_dir


# Automatic routes in the installed codex-chatgpt-web 6.1.9 catalog.
# These are Bridge choices, not a claim of model access on the signed-in account.
WEB_MODEL_CHOICES = {
    'chatgpt-web/gpt-6-sol': ('medium', 'high', 'xhigh'),
    'chatgpt-web/gpt-6-sol-instant': ('low',),
    'chatgpt-web/gpt-6-pro': ('max',),
    'chatgpt-web/gpt-5.6-sol': ('medium', 'high', 'xhigh'),
    'chatgpt-web/gpt-5.6-sol-instant': ('low',),
    'chatgpt-web/gpt-5.6-pro': ('max',),
    'chatgpt-web/gpt-5.6-luna': ('low', 'medium'),
}


class WebSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('ChatGPT Web — การแปลเบื้องหลัง')
        self.setMinimumWidth(540)
        layout = QFormLayout(self)
        try:
            self.settings = load_settings()
        except Exception:
            from .settings import defaults
            self.settings = defaults()
        self.endpoint = QLineEdit(self.settings['endpoint'])
        self.model = QComboBox()
        self.model.setEditable(False)
        self.model.setToolTip('เลือกโมเดลจากรายการ ระบบใส่รหัส Web Model ให้เอง')
        self.populate_models([], self.settings['model'])
        self.effort = QComboBox()
        self.effort.addItems(['', 'low', 'medium', 'high', 'xhigh', 'max'])
        self.effort.setCurrentText(self.settings['effort'])
        self.model.currentIndexChanged.connect(self.model_changed)
        self.model_changed()
        self.timeout = QSpinBox()
        self.timeout.setRange(15, 3600)
        self.timeout.setValue(self.settings['timeout'])
        layout.addRow('Web Model', self.model)
        model_hint = QLabel('รายการจาก Bridge 6.1.9 — ใช้ได้ตามสิทธิ์บัญชี ChatGPT ของคุณ\n'
                            'เลือกชื่อโมเดลจากรายการ แล้วกด Save ได้เลย')
        model_hint.setWordWrap(True)
        layout.addRow(model_hint)
        # Routine use only needs a model and Save; diagnostics stay available on demand.
        advanced = QWidget(self)
        advanced_layout = QFormLayout(advanced)
        advanced_layout.setContentsMargins(0, 0, 0, 0)
        advanced_button = QPushButton('ตั้งค่าขั้นสูง / ตรวจการเชื่อมต่อ')
        advanced_button.setCheckable(True)
        advanced_button.toggled.connect(advanced.setVisible)
        layout.addRow(advanced_button)
        layout.addRow(advanced)
        advanced.hide()
        advanced_layout.addRow('Bridge URL', self.endpoint)
        advanced_layout.addRow('Effort', self.effort)
        advanced_layout.addRow('Timeout (วินาที)', self.timeout)
        notice = QLabel('เปิด codex-chatgpt-web และล็อกอินในโหมด browser-only ก่อน\n'
                        'ปุ่มแปลและ Run TRun ใช้งานเหมือนเดิม ค่าของ API แยกจากหน้านี้')
        notice.setWordWrap(True)
        advanced_layout.addRow(notice)
        self.status = QLabel('กดแปลหรือ Run TRun ได้เลย ระบบตรวจและเปิด Bridge ให้เบื้องหลัง')
        self.status.setWordWrap(True)
        from .web_client import pending_details
        pending = pending_details(self.settings['endpoint'])
        if pending:
            self.status.setText('ระบบจะตรวจงานเดิมและจัดการสถานะค้างให้อัตโนมัติเมื่อกดแปล')
        self.check = QPushButton('ตรวจ Bridge / อ่าน Web Models')
        self.check.clicked.connect(self.check_bridge)
        advanced_layout.addRow(self.check)
        layout.addRow(self.status)
        acknowledge = QPushButton('ตรวจหน้า ChatGPT แล้ว — รับทราบคำขอที่ไม่ทราบผล')
        acknowledge.clicked.connect(self.acknowledge)
        advanced_layout.addRow(acknowledge)
        recovery = QPushButton('เปิดโฟลเดอร์คำตอบที่เก็บไว้ตรวจสอบ')
        recovery.clicked.connect(self.open_recovery)
        advanced_layout.addRow(recovery)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def values(self):
        return dict(self.settings, endpoint=self.endpoint.text().strip(),
                    model=self.model.currentData() or '', effort=self.effort.currentText(),
                    timeout=self.timeout.value())

    def populate_models(self, models, selected):
        self.model.blockSignals(True)
        try:
            self.model.clear()
            for model in dict.fromkeys([*WEB_MODEL_CHOICES, selected, *models]):
                if not isinstance(model, str) or not model.startswith('chatgpt-web/'):
                    continue
                label = model.removeprefix('chatgpt-web/')
                if model in WEB_MODEL_CHOICES:
                    label = label.replace('gpt-', 'GPT-', 1)
                    for suffix in ('sol', 'instant', 'pro', 'luna'):
                        label = label.replace('-' + suffix, ' ' + suffix.title())
                self.model.addItem(label, model)
                self.model.setItemData(self.model.count() - 1, model, Qt.ItemDataRole.ToolTipRole)
            index = self.model.findData(selected)
            self.model.setCurrentIndex(index if index >= 0 else 0)
        finally:
            self.model.blockSignals(False)

    def model_changed(self, *_):
        efforts = WEB_MODEL_CHOICES.get(self.model.currentData())
        if efforts and self.effort.currentText() not in efforts:
            self.effort.setCurrentText(efforts[0])

    def check_bridge(self):
        from tstudio_ui_shared import ApiWorker, ThreadSafeWorkerSignalsForwarder
        from PyQt6.QtCore import QThreadPool
        from .web_client import WebClient
        try:
            client = WebClient(self.values())
        except Exception as error:
            self.status.setText(str(error))
            return
        self.check.setEnabled(False)
        self._check_client = client
        self.status.setText('กำลังตรวจ Bridge…')
        self._worker = ApiWorker(client.models)
        self._forwarder = ThreadSafeWorkerSignalsForwarder(self.checked, self.check_error, parent=self)
        self._worker.signals.finished.connect(self._forwarder.handle_finished)
        self._worker.signals.error.connect(self._forwarder.handle_error)
        QThreadPool.globalInstance().start(self._worker)

    def checked(self, models):
        selected = self.model.currentData()
        self.populate_models(models, selected)
        if self._check_client.catalog_source == 'configured':
            self.status.setText('Bridge พร้อม — มีรายการโมเดลให้เลือก ยังไม่ได้ยืนยันสิทธิ์แต่ละโมเดล')
        else:
            self.status.setText('พบ %d Web Models (ยังไม่ยืนยันการส่งข้อความจริง)' % len(models))
        self.check.setEnabled(True)

    def check_error(self, error):
        self.status.setText(error)
        self.check.setEnabled(True)

    def acknowledge(self):
        if QMessageBox.question(self, 'คำขอ Web ที่ไม่ทราบผล',
                                'ยืนยันว่าตรวจหน้า ChatGPT และไม่มีคำขอเดิมกำลังทำงานแล้ว?\n'
                                'การรับทราบนี้อนุญาตให้ส่งงานใหม่ แต่ไม่กู้หรือส่งคำขอเก่าซ้ำ') != QMessageBox.StandardButton.Yes:
            return
        from .settings import validate
        from .web_client import acknowledge_pending
        try:
            endpoint = validate(self.values())['endpoint']
            # Nonblocking acknowledgement: do not wait behind an active browser call on Qt.
            from tstudio_ui_shared import ApiWorker, ThreadSafeWorkerSignalsForwarder
            from PyQt6.QtCore import QThreadPool
            self._ack_worker = ApiWorker(lambda: acknowledge_pending(endpoint))
            self._ack_forwarder = ThreadSafeWorkerSignalsForwarder(
                lambda _: self.status.setText('รับทราบแล้ว สามารถเริ่มงานใหม่ได้'),
                lambda err: self.status.setText(err), parent=self)
            self._ack_worker.signals.finished.connect(self._ack_forwarder.handle_finished)
            self._ack_worker.signals.error.connect(self._ack_forwarder.handle_error)
            QThreadPool.globalInstance().start(self._ack_worker)
        except Exception as error:
            self.status.setText(str(error))

    def save(self):
        try:
            if not self.model.currentData():
                raise ValueError('กรุณาเลือก Web Model ก่อนบันทึก')
            save_settings(self.values())
        except Exception as error:
            QMessageBox.warning(self, 'Web Settings', str(error))
            return
        self.accept()

    def open_recovery(self):
        from PyQt6.QtCore import QUrl
        from PyQt6.QtGui import QDesktopServices
        from .settings import state_dir
        folder = state_dir() / 'results'
        folder.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))


class TranslationChannelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.combo = QComboBox()
        self.combo.addItem('API', 'api')
        self.combo.addItem('ChatGPT Web', 'web')
        self.combo.setToolTip('ช่องทางสำหรับปุ่มแปลและ Run TRun — ไม่เปลี่ยน API Model')
        self.settings_button = QPushButton('Web ⚙')
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.combo)
        layout.addWidget(self.settings_button)
        self.refresh()
        self.combo.currentIndexChanged.connect(self.changed)

    def refresh(self):
        self.combo.blockSignals(True)
        try:
            cfg = load_settings()
            self.combo.setCurrentIndex(1 if cfg['channel'] == 'web' else 0)
            self.combo.setItemText(1, 'Web · ' + cfg['model'].removeprefix('chatgpt-web/') if cfg['model'] else 'Web · ยังไม่เลือกโมเดล')
            self.settings_button.setToolTip('Web Model: ' + (cfg['model'] or '(ยังไม่เลือก)') + '\n' + str(state_dir() / 'settings.json'))
        except Exception:
            self.combo.setCurrentIndex(-1)
            self.combo.setToolTip('การตั้งค่าช่องทางเสียหาย กรุณาเปิด Web Settings')
        finally:
            self.combo.blockSignals(False)

    def showEvent(self, event):
        self.refresh()
        super().showEvent(event)

    def changed(self):
        try:
            cfg = load_settings()
            cfg['channel'] = self.combo.currentData()
            if cfg['channel'] == 'web' and not cfg['model']:
                cfg['model'] = 'chatgpt-web/gpt-6-sol'
                cfg['effort'] = 'medium'
            save_settings(cfg)
        except Exception as error:
            QMessageBox.warning(self, 'Translation channel', str(error))
            self.refresh()

    def route(self):
        from .settings import validate
        settings = load_settings()
        # Another window may have changed the shared preference. The visible choice in
        # THIS window is authoritative for a new job; never switch its transport invisibly.
        settings['channel'] = self.combo.currentData()
        return validate(settings)

    def snapshot_config(self, config):
        from .gateway import snapshot_config
        return snapshot_config(config, self.route())

    def open_settings(self):
        WebSettingsDialog(self).exec()
        self.refresh()
