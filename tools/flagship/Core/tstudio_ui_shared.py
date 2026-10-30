
try:
    from tstudio_i18n import _
except ImportError:
    try:
        from trun_i18n import _
    except ImportError:
        try:
            from i18n_helper import _
        except ImportError:
            _ = lambda x: x


import os
import json
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QLabel, QComboBox, 
    QLineEdit, QFileDialog, QDialog, QScrollArea, QButtonGroup, QRadioButton,
    QFormLayout, QTextEdit, QGroupBox, QSpinBox, QDoubleSpinBox, QApplication,
    QAbstractItemView, QTabWidget
)
from PyQt6.QtCore import Qt, QLocale, QThreadPool, QRunnable, pyqtSignal, QObject, pyqtSlot
from tstudio_core import TStudioCore, CoreAI, DEFAULT_SINGLE_PROMPT, DEFAULT_OPTIONS_PROMPT

class TranslationOptionsDialog(QDialog):
    def __init__(self, parent, options):
        super().__init__(parent)
        self.setWindowTitle("🎯 Select Translation Style")
        self.setMinimumSize(500, 280)
        self.selected_text = ""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("เลือกสไตล์คำแปลที่ต้องการ:"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        cl = QVBoxLayout(content)
        self.bg = QButtonGroup(self)
        labels = ["1️⃣ ตรงตัว (Literal)", "2️⃣ ภาษาพูด/สแลง (Casual)", "3️⃣ สุภาพ/ทางการ (Formal)"]
        for i, opt in enumerate(options):
            label = labels[i] if i < len(labels) else f"Option {i+1}"
            rb = QRadioButton(f"{label}:\n{opt}")
            rb.setStyleSheet("font-size: 13px; padding: 6px;")
            if i == 0: rb.setChecked(True)
            self.bg.addButton(rb, i)
            cl.addWidget(rb)
        self.options = options
        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        btn_ok = QPushButton(_("btn_use_selected"))
        btn_ok.setToolTip(_("tooltip_btn_ok"))
        btn_ok.clicked.connect(self.on_ok)
        btn_ok.setStyleSheet("background: #a6e3a1; color: #1e1e2e;")
        layout.addWidget(btn_ok)

    def on_ok(self):
        idx = self.bg.checkedId()
        if 0 <= idx < len(self.options):
            self.selected_text = self.options[idx]
        self.accept()

class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

class ThreadSafeWorkerSignalsForwarder(QObject):
    def __init__(self, on_success=None, on_error=None, parent=None):
        super().__init__(parent)
        self.on_success = on_success
        self.on_error = on_error

    @pyqtSlot(object)
    def handle_finished(self, val):
        try:
            if self.on_success:
                self.on_success(val)
        finally:
            self.deleteLater()

    @pyqtSlot(str)
    def handle_error(self, err_msg):
        try:
            if self.on_error:
                self.on_error(err_msg)
        finally:
            self.deleteLater()


class ApiWorker(QRunnable):
    _active_signals = set()
    
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        # Prevent premature garbage collection of signals
        ApiWorker._active_signals.add(self.signals)
        self.signals.finished.connect(self._cleanup)
        self.signals.error.connect(self._cleanup)

    def _cleanup(self, *args):
        try:
            ApiWorker._active_signals.remove(self.signals)
        except KeyError:
            pass

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))

def test_api_connection(provider, api_key="", base_url="", model=""):
    """
    Tests connectivity and API key validity for a given provider.
    Returns (success: bool, message: str)
    """
    import requests
    provider = str(provider or "").strip()
    api_key = str(api_key or "").strip()
    base_url = str(base_url or "").strip()

    if provider == "Local LLM":
        url = base_url or "http://localhost:1234/v1/chat/completions"
        test_urls = []
        if "1234" in url or "localhost" in url:
            test_urls.append("http://localhost:1234/v1/models")
        if "11434" in url or "localhost" in url:
            test_urls.append("http://localhost:11434/api/tags")
        base_clean = url.split("/chat")[0].rstrip("/")
        if not base_clean.endswith("/v1"):
            base_clean += "/v1"
        test_urls.append(f"{base_clean}/models")
        test_urls.append(url)
        
        last_err = ""
        for u in test_urls:
            try:
                r = requests.get(u, timeout=3)
                if r.status_code in (200, 404, 405):
                    return True, "เชื่อมต่อ Local LLM สำเร็จ (เซิร์ฟเวอร์พร้อมใช้งาน)"
            except Exception as e:
                last_err = str(e)
        return False, f"ไม่สามารถเชื่อมต่อ Local LLM ได้ ({last_err or 'Connection refused'})"

    if not api_key:
        return False, "กรุณากรอก API Key ก่อนกดทดสอบ"

    try:
        if provider == "DeepSeek":
            url = base_url if base_url else "https://api.deepseek.com/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            r = requests.get(url, headers=headers, timeout=6)
            if r.status_code == 200:
                models = [m.get("id") for m in r.json().get("data", [])]
                m_txt = f" (พบโมเดล {', '.join(models)})" if models else ""
                return True, f"เชื่อมต่อสำเร็จ! DeepSeek API Key ถูกต้อง{m_txt}"
            elif r.status_code == 401:
                return False, "API Key ไม่ถูกต้อง (401 Unauthorized)"
            elif r.status_code == 402:
                return False, "ยอดเงินคงเหลือในบัญชีไม่พอ (402 Insufficient Balance)"
            else:
                return False, f"เชื่อมต่อไม่สำเร็จ (HTTP {r.status_code}): {r.text[:100]}"

        elif provider == "Google Gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            r = requests.get(url, timeout=6)
            if r.status_code == 200:
                models = [m.get("name", "").split("/")[-1] for m in r.json().get("models", [])]
                m_cnt = f" (พบ {len(models)} โมเดล)" if models else ""
                return True, f"เชื่อมต่อสำเร็จ! Google Gemini API Key พร้อมใช้งาน{m_cnt}"
            elif r.status_code in (400, 403):
                return False, f"API Key ไม่ถูกต้อง หรือไม่มีสิทธิ์เข้าถึง ({r.status_code})"
            else:
                return False, f"เชื่อมต่อไม่สำเร็จ (HTTP {r.status_code}): {r.text[:100]}"

        elif provider == "OpenAI":
            url = base_url if base_url else "https://api.openai.com/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            r = requests.get(url, headers=headers, timeout=6)
            if r.status_code == 200:
                return True, "เชื่อมต่อสำเร็จ! OpenAI API Key พร้อมใช้งาน"
            elif r.status_code == 401:
                return False, "OpenAI API Key ไม่ถูกต้อง (401 Unauthorized)"
            elif r.status_code == 429:
                return False, "คำขอเกินโควตา/ติด Rate Limit หรือเครดิตหมด (429)"
            else:
                return False, f"เชื่อมต่อไม่สำเร็จ (HTTP {r.status_code}): {r.text[:100]}"

        elif provider == "Anthropic Claude":
            url = base_url if base_url else "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "ping"}]
            }
            r = requests.post(url, headers=headers, json=payload, timeout=8)
            if r.status_code == 200:
                return True, "เชื่อมต่อสำเร็จ! Anthropic Claude API พร้อมใช้งาน"
            elif r.status_code == 401:
                return False, "Anthropic API Key ไม่ถูกต้อง (401 Unauthorized)"
            elif r.status_code == 429:
                return False, "คำขอเกินโควตาหรือเครดิตหมด (429 Rate Limit)"
            else:
                return False, f"เชื่อมต่อไม่สำเร็จ (HTTP {r.status_code}): {r.text[:100]}"

        elif provider == "OpenRouter":
            url = "https://openrouter.ai/api/v1/auth/key"
            headers = {"Authorization": f"Bearer {api_key}"}
            r = requests.get(url, headers=headers, timeout=6)
            if r.status_code == 200:
                j = r.json().get("data", {})
                label = j.get("label", "Key")
                limit = j.get("limit")
                lim_txt = f", Limit: ${limit}" if limit else ""
                return True, f"เชื่อมต่อสำเร็จ! OpenRouter ({label}{lim_txt})"
            elif r.status_code == 401:
                return False, "OpenRouter API Key ไม่ถูกต้อง (401 Unauthorized)"
            else:
                return False, f"เชื่อมต่อไม่สำเร็จ (HTTP {r.status_code}): {r.text[:100]}"

        else:
            return False, f"ไม่รู้จักผู้ให้บริการ: {provider}"

    except requests.exceptions.Timeout:
        return False, "การเชื่อมต่อหมดเวลา (Timeout 6s) กรุณาตรวจสอบอินเทอร์เน็ต"
    except Exception as ex:
        return False, f"เกิดข้อผิดพลาด: {str(ex)[:100]}"

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ การตั้งค่า AI Model & Multi-API Keys")
        self.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.setMinimumSize(620, 540)
        self.resize(660, 560)
        
        self.api_keys = {
            "DeepSeek": "",
            "Google Gemini": "",
            "OpenAI": "",
            "Anthropic Claude": "",
            "OpenRouter": ""
        }
        self.models_by_provider = {
            "DeepSeek": [
                ("deepseek-chat (DeepSeek-V3 แนะนำ/ประหยัดสุด)", "deepseek-chat"),
                ("deepseek-reasoner (DeepSeek-R1 ตรรกะ CoT)", "deepseek-reasoner"),
                ("✏️ กำหนดชื่อโมเดลเอง (Custom)...", "__custom__")
            ],
            "Google Gemini": [
                ("gemini-2.0-flash (แนะนำ เร็ว/ประหยัดสุด เทียบเท่า DeepSeek)", "gemini-2.0-flash"),
                ("gemini-2.0-flash-lite (ประหยัดสูงสุด/เน้นความเร็วจัด)", "gemini-2.0-flash-lite"),
                ("gemini-2.0-flash-thinking-exp-01-21 (Reasoning ตรรกะ CoT)", "gemini-2.0-flash-thinking-exp-01-21"),
                ("gemini-2.0-pro-exp-02-05 (คุณภาพสูงสุด/บริบทซับซ้อน)", "gemini-2.0-pro-exp-02-05"),
                ("gemini-1.5-pro (2M Context มหาศาล)", "gemini-1.5-pro"),
                ("gemini-1.5-flash (เสถียร LTS)", "gemini-1.5-flash"),
                ("gemini-1.5-flash-8b (จิ๋ว/ประหยัด)", "gemini-1.5-flash-8b"),
                ("✏️ กำหนดชื่อโมเดลเอง (Custom)...", "__custom__")
            ],
            "OpenAI": [
                ("gpt-4o-mini (GPT-4o Mini แนะนำ/ประหยัดสุด เทียบเท่า DeepSeek)", "gpt-4o-mini"),
                ("gpt-4o (Omni Flagship ฉลาดแม่นยำสูง)", "gpt-4o"),
                ("o3-mini (Reasoning ตรรกะ ความเร็วสูง)", "o3-mini"),
                ("o1 (Reasoning ตรรกะ Flagship)", "o1"),
                ("o1-mini (Reasoning ตรรกะ ประหยัด)", "o1-mini"),
                ("gpt-4.5-preview (Frontier โมเดลใหญ่สุด)", "gpt-4.5-preview"),
                ("chatgpt-4o-latest (อัปเดตล่าสุดเสมอ)", "chatgpt-4o-latest"),
                ("✏️ กำหนดชื่อโมเดลเอง (Custom)...", "__custom__")
            ],
            "Anthropic Claude": [
                ("claude-3-5-haiku-20241022 (Claude 3.5 Haiku แนะนำ/เร็ว/ประหยัดสุด)", "claude-3-5-haiku-20241022"),
                ("claude-3-7-sonnet-20250219 (Claude 3.7 Sonnet ยอดนิยม/Hybrid Reasoning)", "claude-3-7-sonnet-20250219"),
                ("claude-3-5-sonnet-20241022 (Claude 3.5 Sonnet v2 คุณภาพการแปลยอดเยี่ยม)", "claude-3-5-sonnet-20241022"),
                ("claude-3-opus-20240229 (Claude 3 Opus โมเดลระดับพรีเมียม)", "claude-3-opus-20240229"),
                ("✏️ กำหนดชื่อโมเดลเอง (Custom)...", "__custom__")
            ],
            "OpenRouter": [
                ("deepseek/deepseek-chat (DeepSeek-V3 แนะนำ/ประหยัดสุด OpenRouter)", "deepseek/deepseek-chat"),
                ("google/gemini-2.0-flash-001 (Gemini 2.0 Flash คุ้มค่า/เร็วสูง)", "google/gemini-2.0-flash-001"),
                ("openai/gpt-4o-mini (GPT-4o Mini ประหยัด/เสถียร)", "openai/gpt-4o-mini"),
                ("deepseek/deepseek-r1 (DeepSeek R1 Reasoning ตรรกะ)", "deepseek/deepseek-r1"),
                ("anthropic/claude-3.7-sonnet (Claude 3.7 Sonnet คุณภาพสูง)", "anthropic/claude-3.7-sonnet"),
                ("anthropic/claude-3.5-sonnet (Claude 3.5 Sonnet v2)", "anthropic/claude-3.5-sonnet"),
                ("openai/gpt-4o (GPT-4o Omni)", "openai/gpt-4o"),
                ("openai/o3-mini (o3-mini Reasoning)", "openai/o3-mini"),
                ("qwen/qwen-2.5-72b-instruct (Qwen 2.5 72B)", "qwen/qwen-2.5-72b-instruct"),
                ("meta-llama/llama-3.3-70b-instruct (Llama 3.3 70B)", "meta-llama/llama-3.3-70b-instruct"),
                ("✏️ กำหนดชื่อโมเดลเอง (Custom)...", "__custom__")
            ],
            "Local LLM": [
                ("qwen2.5-coder-32b-instruct (Qwen 2.5 Coder 32B แนะนำ LM Studio)", "qwen2.5-coder-32b-instruct"),
                ("qwen2.5-14b-instruct (Qwen 2.5 14B LM Studio)", "qwen2.5-14b-instruct"),
                ("qwen2.5-7b-instruct (Qwen 2.5 7B LM Studio)", "qwen2.5-7b-instruct"),
                ("qwen2.5-32b-instruct (Qwen 2.5 32B LM Studio)", "qwen2.5-32b-instruct"),
                ("qwen2.5:14b (Qwen 2.5 14B แนะนำ/แปลดีเยี่ยม/VRAM 10-12GB)", "qwen2.5:14b"),
                ("qwen2.5:7b (Qwen 2.5 7B ประหยัดสเปกสุด/เร็ว/VRAM 6GB)", "qwen2.5:7b"),
                ("qwen2.5:32b (Qwen 2.5 32B คุณภาพสูง/ต้องการ VRAM 20GB+)", "qwen2.5:32b"),
                ("qwen2.5-coder:32b (Qwen 2.5 Coder 32B)", "qwen2.5-coder:32b"),
                ("deepseek-r1:14b (DeepSeek R1 14B Reasoning Local)", "deepseek-r1:14b"),
                ("deepseek-r1:8b (DeepSeek R1 8B Local ประหยัดสเปก)", "deepseek-r1:8b"),
                ("qwq:32b (QwQ 32B Reasoning Local)", "qwq:32b"),
                ("llama3.3:70b (Llama 3.3 70B Local)", "llama3.3:70b"),
                ("custom-local-llm (Custom Local Model)", "custom-local-llm"),
                ("✏️ กำหนดชื่อโมเดลเอง (Custom)...", "__custom__")
            ]
        }
        self.current_provider = "DeepSeek"
        self.key_inputs = {}
        self.key_status_labels = {}
        self.test_result_labels = {}
        self._is_loading_models = False
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #313244; background: #181825; border-radius: 8px; }
            QTabBar::tab { background: #11111b; color: #a6adc8; padding: 8px 16px; border: 1px solid #313244; border-bottom: none; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 4px; font-weight: bold; }
            QTabBar::tab:selected { background: #1e1e2e; color: #cdd6f4; border-bottom: 2px solid #89b4fa; }
        """)

        # ── TAB 1: Active Model & Parameters ──
        tab_active = QWidget()
        tab_active_layout = QVBoxLayout(tab_active)
        tab_active_layout.setContentsMargins(16, 16, 16, 16)
        tab_active_layout.setSpacing(12)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.cbo_provider = QComboBox()
        self.cbo_provider.addItems(["DeepSeek", "Google Gemini", "Anthropic Claude", "OpenAI", "OpenRouter", "Local LLM"])
        self.cbo_provider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cbo_provider.setStyleSheet("""
            QComboBox {
                background: #181825;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 5px 10px;
                color: #89b4fa;
                font-weight: bold;
                font-size: 12px;
            }
            QComboBox:hover {
                border-color: #89b4fa;
            }
            QComboBox QAbstractItemView {
                background-color: #181825;
                color: #cdd6f4;
                border: 1px solid #45475a;
                selection-background-color: #313244;
                selection-color: #89b4fa;
                padding: 4px;
                outline: none;
            }
        """)
        self.cbo_provider.currentTextChanged.connect(self.on_provider_changed)
        form_layout.addRow("1. 🏢 AI Provider (ผู้ให้บริการ):", self.cbo_provider)

        model_row = QHBoxLayout()
        model_row.setSpacing(6)

        self.cbo_model = QComboBox()
        self.cbo_model.setEditable(False)
        self.cbo_model.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cbo_model.setMaxVisibleItems(15)
        self.cbo_model.view().setMinimumWidth(420)
        self.cbo_model.setStyleSheet("""
            QComboBox {
                background: #181825;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 5px 10px;
                color: #a6e3a1;
                font-weight: bold;
                font-size: 12px;
            }
            QComboBox:hover {
                border-color: #a6e3a1;
            }
            QComboBox QAbstractItemView {
                background-color: #181825;
                color: #cdd6f4;
                border: 1px solid #45475a;
                selection-background-color: #313244;
                selection-color: #a6e3a1;
                padding: 4px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                min-height: 26px;
                padding: 4px 8px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #313244;
                color: #89b4fa;
            }
        """)
        self.cbo_model.currentIndexChanged.connect(self._on_model_combo_changed)

        btn_custom_model = QPushButton("✏️ พิมพ์เอง")
        btn_custom_model.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_custom_model.setStyleSheet("background: #313244; border-radius: 4px; padding: 4px 10px; color: #89b4fa; font-size: 11px; font-weight: bold;")
        btn_custom_model.setToolTip("พิมพ์ชื่อโมเดลเอง (Model ID) หากไม่มีในรายการ")
        btn_custom_model.clicked.connect(self._prompt_custom_model)

        model_row.addWidget(self.cbo_model, 1)
        model_row.addWidget(btn_custom_model)
        form_layout.addRow("2. 🤖 Model Name (ชื่อโมเดลย่อย):", model_row)

        self.txt_base_url = QLineEdit()
        self.txt_base_url.setPlaceholderText("ไม่จำเป็น (สำหรับ Custom Proxy, Gateway หรือ OpenRouter URL)")
        self.txt_base_url.setStyleSheet("background: #181825; border: 1px solid #313244; border-radius: 6px; padding: 4px 8px; color: #cdd6f4;")
        form_layout.addRow("3. 🌐 Base API URL (ถ้ามี):", self.txt_base_url)

        self.spn_temp = QDoubleSpinBox()
        self.spn_temp.setRange(0.0, 2.0)
        self.spn_temp.setSingleStep(0.05)
        self.spn_temp.setStyleSheet("background: #181825; border: 1px solid #313244; border-radius: 6px; padding: 4px 8px; color: #cdd6f4;")
        form_layout.addRow("4. 🌡️ Temperature (ความสร้างสรรค์):", self.spn_temp)

        self.spn_max_tokens = QSpinBox()
        self.spn_max_tokens.setRange(256, 128000)
        self.spn_max_tokens.setSingleStep(1024)
        self.spn_max_tokens.setStyleSheet("background: #181825; border: 1px solid #313244; border-radius: 6px; padding: 4px 8px; color: #cdd6f4;")
        form_layout.addRow("5. 📦 Max Tokens (ความยาวคำตอบสูงสุด):", self.spn_max_tokens)

        self.spn_timeout = QSpinBox()
        self.spn_timeout.setRange(10, 600)
        self.spn_timeout.setSuffix(" วินาที")
        self.spn_timeout.setStyleSheet("background: #181825; border: 1px solid #313244; border-radius: 6px; padding: 4px 8px; color: #cdd6f4;")
        form_layout.addRow("6. ⏱️ Timeout (เวลารอตัดจบ):", self.spn_timeout)

        self.spn_concurrency = QSpinBox()
        self.spn_concurrency.setRange(1, 50)
        self.spn_concurrency.setValue(10)
        self.spn_concurrency.setSuffix(" เธรด (Threads)")
        self.spn_concurrency.setToolTip(
            "จำนวนการเรียก API พร้อมกันสูงสุดเมื่อแปลหลายแถว (Batch Concurrency)\n"
            "- แนะนำ 10-12 สำหรับ DeepSeek (เพื่อไม่ให้เกินโควตา Concurrency 25 ของเซิร์ฟเวอร์)\n"
            "- แนะนำ 5-10 สำหรับ Gemini / Claude\n"
            "- แนะนำ 2-4 สำหรับ Local LLM (Ollama / LM Studio)"
        )
        self.spn_concurrency.setStyleSheet("background: #181825; border: 1px solid #313244; border-radius: 6px; padding: 4px 8px; color: #cdd6f4;")
        form_layout.addRow("7. ⚡ Batch Concurrency (เธรดแปลพร้อมกัน):", self.spn_concurrency)

        tab_active_layout.addLayout(form_layout)

        # Active provider key status banner
        self.card_key_status = QWidget()
        self.card_key_status.setStyleSheet("background: #11111b; border: 1px solid #313244; border-radius: 8px; padding: 10px;")
        card_l = QVBoxLayout(self.card_key_status)
        card_l.setContentsMargins(10, 8, 10, 8)
        card_l.setSpacing(6)
        
        card_top = QHBoxLayout()
        self.lbl_active_key_notice = QLabel("🔑 สถานะคีย์: กำลังตรวจสอบ...")
        self.lbl_active_key_notice.setStyleSheet("font-size: 12px; font-weight: bold;")
        
        self.btn_test_active = QPushButton("⚡ ทดสอบโมเดลนี้")
        self.btn_test_active.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_test_active.setStyleSheet("background: #313244; border-radius: 4px; padding: 4px 10px; color: #a6e3a1; font-size: 11px; font-weight: bold;")
        self.btn_test_active.setToolTip("ทดสอบการเชื่อมต่อโมเดลและ API Key ที่เลือกอยู่ในแท็บนี้ทันที")
        self.btn_test_active.clicked.connect(self.test_active_model_connection)

        btn_jump_keys = QPushButton("👉 จัดการคีย์ในแท็บ API Keys")
        btn_jump_keys.setStyleSheet("background: #313244; border-radius: 4px; padding: 4px 8px; color: #89b4fa; font-size: 11px;")
        btn_jump_keys.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_jump_keys.clicked.connect(lambda: self.tab_widget.setCurrentIndex(1))

        card_top.addWidget(self.lbl_active_key_notice, 1)
        card_top.addWidget(self.btn_test_active)
        card_top.addWidget(btn_jump_keys)
        card_l.addLayout(card_top)

        self.lbl_active_test_res = QLabel("")
        self.lbl_active_test_res.setWordWrap(True)
        self.lbl_active_test_res.setStyleSheet("font-size: 11px;")
        self.lbl_active_test_res.setVisible(False)
        card_l.addWidget(self.lbl_active_test_res)

        tab_active_layout.addWidget(self.card_key_status)

        tab_active_layout.addStretch(1)
        self.tab_widget.addTab(tab_active, "🎯 โมเดลหลัก & พารามิเตอร์")

        # ── TAB 2: Multi-Provider API Keys ──
        tab_keys = QWidget()
        tab_keys_layout = QVBoxLayout(tab_keys)
        tab_keys_layout.setContentsMargins(16, 16, 16, 16)
        tab_keys_layout.setSpacing(10)

        hint_lbl = QLabel("คุณสามารถกรอกและบันทึก API Key ของผู้ให้บริการหลายค่ายพร้อมกันได้ที่นี่ เมื่อคุณสลับโมเดลในหน้าต่างหลัก ระบบจะใช้คีย์ที่ถูกต้องให้อัตโนมัติ โดยคุณสามารถกดปุ่ม '⚡ ทดสอบ API' เพื่อตรวจเช็กการเชื่อมต่อได้ทันทีก่อนเริ่มแปล")
        hint_lbl.setWordWrap(True)
        hint_lbl.setStyleSheet("color: #a6adc8; font-size: 11px; margin-bottom: 4px;")
        tab_keys_layout.addWidget(hint_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)

        providers_spec = [
            ("DeepSeek", "DeepSeek API Key (sk-...):", "sk-..."),
            ("Google Gemini", "Google Gemini API Key (AIzaSy...):", "AIzaSy..."),
            ("OpenAI", "OpenAI API Key (sk-proj-...):", "sk-proj-..."),
            ("Anthropic Claude", "Anthropic Claude Key (sk-ant-...):", "sk-ant-..."),
            ("OpenRouter", "OpenRouter API Key (sk-or-...):", "sk-or-...")
        ]

        for p_name, label_text, placeholder in providers_spec:
            grp = QWidget()
            grp.setStyleSheet("background: #11111b; border: 1px solid #313244; border-radius: 8px; padding: 6px;")
            gl = QVBoxLayout(grp)
            gl.setContentsMargins(8, 6, 8, 6)
            gl.setSpacing(4)

            top_row = QHBoxLayout()
            lbl_title = QLabel(f"<b>{p_name}</b>")
            lbl_title.setStyleSheet("color: #cdd6f4; font-size: 12px;")
            lbl_status = QLabel("⚪ ยังไม่ระบุ")
            lbl_status.setStyleSheet("color: #6c7086; font-size: 11px;")
            self.key_status_labels[p_name] = lbl_status
            top_row.addWidget(lbl_title)
            top_row.addStretch(1)
            top_row.addWidget(lbl_status)
            gl.addLayout(top_row)

            inp_row = QHBoxLayout()
            inp_row.setSpacing(6)
            txt = QLineEdit()
            txt.setEchoMode(QLineEdit.EchoMode.Password)
            txt.setPlaceholderText(placeholder)
            txt.setStyleSheet("background: #181825; border: 1px solid #313244; border-radius: 4px; padding: 4px 8px; color: #cdd6f4;")
            self.key_inputs[p_name] = txt

            btn_toggle = QPushButton("👁️")
            btn_toggle.setFixedWidth(36)
            btn_toggle.setToolTip("แสดง/ซ่อน API Key")
            btn_toggle.setStyleSheet("background: #313244; border-radius: 4px; padding: 4px; color: #cdd6f4;")
            def make_toggle(edit_field):
                return lambda: edit_field.setEchoMode(
                    QLineEdit.EchoMode.Normal if edit_field.echoMode() == QLineEdit.EchoMode.Password else QLineEdit.EchoMode.Password
                )
            btn_toggle.clicked.connect(make_toggle(txt))

            btn_test = QPushButton("⚡ ทดสอบ API")
            btn_test.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_test.setStyleSheet("background: #313244; color: #89b4fa; font-weight: bold; border-radius: 4px; padding: 4px 10px; font-size: 11px;")
            btn_test.setToolTip(f"ทดสอบการเชื่อมต่อและตรวจสอบความถูกต้องของ {p_name} API Key")

            lbl_test_res = QLabel("")
            lbl_test_res.setWordWrap(True)
            lbl_test_res.setStyleSheet("font-size: 11px; margin-top: 2px;")
            lbl_test_res.setVisible(False)
            self.test_result_labels[p_name] = lbl_test_res

            btn_test.clicked.connect(self.make_tester(p_name, txt, btn_test, lbl_test_res))

            def make_status_updater(provider_name, edit_field, status_label):
                def updater():
                    val = edit_field.text().strip()
                    if val:
                        status_label.setText("🟢 มีคีย์แล้ว (พร้อมใช้งาน)")
                        status_label.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 11px;")
                    else:
                        status_label.setText("⚪ ยังไม่ระบุ")
                        status_label.setStyleSheet("color: #6c7086; font-size: 11px;")
                    self._update_active_tab_notice()
                return updater

            txt.textChanged.connect(make_status_updater(p_name, txt, lbl_status))

            inp_row.addWidget(txt, 1)
            inp_row.addWidget(btn_toggle)
            inp_row.addWidget(btn_test)
            gl.addLayout(inp_row)
            gl.addWidget(lbl_test_res)
            scroll_layout.addWidget(grp)

        # Local LLM section
        grp_local = QWidget()
        grp_local.setStyleSheet("background: #11111b; border: 1px solid #313244; border-radius: 8px; padding: 6px;")
        gl_local = QVBoxLayout(grp_local)
        gl_local.setContentsMargins(8, 6, 8, 6)
        gl_local.setSpacing(4)
        top_local = QHBoxLayout()
        lbl_local_title = QLabel("<b>💻 Local LLM (Ollama / LM Studio)</b>")
        lbl_local_title.setStyleSheet("color: #cdd6f4; font-size: 12px;")
        lbl_local_status = QLabel("💻 ออฟไลน์ในเครื่อง (ไม่ต้องใช้คีย์)")
        lbl_local_status.setStyleSheet("color: #89b4fa; font-size: 11px;")
        top_local.addWidget(lbl_local_title)
        top_local.addStretch(1)
        top_local.addWidget(lbl_local_status)
        gl_local.addLayout(top_local)

        self.txt_local_url = QLineEdit()
        self.txt_local_url.setPlaceholderText("http://localhost:11434/v1/chat/completions (Ollama) หรือ :1234 (LM Studio)")
        self.txt_local_url.setStyleSheet("background: #181825; border: 1px solid #313244; border-radius: 4px; padding: 4px 8px; color: #cdd6f4;")
        gl_local.addWidget(self.txt_local_url)

        local_btn_row = QHBoxLayout()
        local_btn_row.setSpacing(8)
        btn_ollama = QPushButton("⚡ Ollama (:11434)")
        btn_ollama.setStyleSheet("background: #313244; border-radius: 4px; padding: 3px 8px; color: #cdd6f4; font-size: 11px;")
        btn_ollama.clicked.connect(lambda: self.txt_local_url.setText("http://localhost:11434/v1/chat/completions"))
        btn_lmstudio = QPushButton("⚡ LM Studio (:1234)")
        btn_lmstudio.setStyleSheet("background: #313244; border-radius: 4px; padding: 3px 8px; color: #cdd6f4; font-size: 11px;")
        btn_lmstudio.clicked.connect(lambda: self.txt_local_url.setText("http://localhost:1234/v1/chat/completions"))
        
        btn_test_local = QPushButton("⚡ ทดสอบเชื่อมต่อ")
        btn_test_local.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_test_local.setStyleSheet("background: #313244; border-radius: 4px; padding: 3px 10px; color: #89b4fa; font-weight: bold; font-size: 11px;")

        lbl_test_local_res = QLabel("")
        lbl_test_local_res.setWordWrap(True)
        lbl_test_local_res.setStyleSheet("font-size: 11px; margin-top: 2px;")
        lbl_test_local_res.setVisible(False)
        self.test_result_labels["Local LLM"] = lbl_test_local_res

        btn_test_local.clicked.connect(self.make_tester("Local LLM", self.txt_local_url, btn_test_local, lbl_test_local_res))

        local_btn_row.addWidget(btn_ollama)
        local_btn_row.addWidget(btn_lmstudio)
        local_btn_row.addWidget(btn_test_local)
        local_btn_row.addStretch(1)
        gl_local.addLayout(local_btn_row)
        gl_local.addWidget(lbl_test_local_res)

        scroll_layout.addWidget(grp_local)
        scroll_layout.addStretch(1)
        scroll.setWidget(scroll_content)
        tab_keys_layout.addWidget(scroll)

        self.tab_widget.addTab(tab_keys, "🔑 จัดการ API Keys หลายค่าย")
        main_layout.addWidget(self.tab_widget, 1)

        # Bottom Buttons
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(10)
        btn_bar.addStretch(1)

        btn_cancel = QPushButton("ยกเลิก (Cancel)")
        btn_cancel.setStyleSheet("background: #313244; color: #cdd6f4; border-radius: 6px; padding: 6px 16px;")
        btn_cancel.clicked.connect(self.reject)
        btn_bar.addWidget(btn_cancel)

        btn_save = QPushButton("💾 บันทึกการตั้งค่าทั้งหมด (Save All)")
        btn_save.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-weight: bold; border-radius: 6px; padding: 6px 20px;")
        btn_save.clicked.connect(self.save_config)
        btn_bar.addWidget(btn_save)

        main_layout.addLayout(btn_bar)

        self.load_config()

    def _infer_provider(self, model):
        if "/" in model: return "OpenRouter"
        if model.startswith("gemini"): return "Google Gemini"
        if model.startswith("claude"): return "Anthropic Claude"
        if model.startswith("gpt") or model.startswith("o1") or model.startswith("o3") or model.startswith("o4") or model.startswith("chatgpt"): return "OpenAI"
        if model.startswith("qwen") or model.startswith("llama") or model.startswith("qwq") or model in ("custom-local-llm", "local-model"): return "Local LLM"
        return "DeepSeek"

    def _update_active_tab_notice(self):
        p = self.cbo_provider.currentText()
        if p == "Local LLM":
            self.lbl_active_key_notice.setText("💻 สถานะคีย์: Local LLM ทำงานในเครื่อง (ไม่ต้องใช้ API Key)")
            self.lbl_active_key_notice.setStyleSheet("color: #89b4fa; font-weight: bold; font-size: 12px;")
            return
        inp = self.key_inputs.get(p)
        has_key = bool(inp and inp.text().strip())
        if has_key:
            self.lbl_active_key_notice.setText(f"🔑 สถานะคีย์ ({p}): 🟢 มีคีย์แล้ว (พร้อมใช้งาน)")
            self.lbl_active_key_notice.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 12px;")
        else:
            self.lbl_active_key_notice.setText(f"⚠️ สถานะคีย์ ({p}): ยังไม่ระบุคีย์ (กรุณากรอกในแท็บ 'จัดการ API Keys')")
            self.lbl_active_key_notice.setStyleSheet("color: #fab387; font-weight: bold; font-size: 12px;")

    def test_active_model_connection(self):
        p = self.cbo_provider.currentText()
        m = self.cbo_model.currentData() or self.cbo_model.currentText().strip()
        if m == "__custom__":
            m = "deepseek-chat"
        base_url = self.txt_base_url.text().strip()
        
        if p == "Local LLM":
            key_val = ""
            base_val = base_url or self.txt_local_url.text().strip()
        else:
            inp = self.key_inputs.get(p)
            key_val = inp.text().strip() if inp else ""
            base_val = base_url
            if not key_val:
                self.lbl_active_test_res.setText(f"⚠️ กรุณากรอก API Key สำหรับ {p} ในแท็บ 'จัดการ API Keys' ก่อนกดทดสอบ")
                self.lbl_active_test_res.setStyleSheet("color: #fab387; font-weight: bold; font-size: 11px;")
                self.lbl_active_test_res.setVisible(True)
                return

        self.btn_test_active.setEnabled(False)
        orig_text = self.btn_test_active.text()
        self.btn_test_active.setText("⏳ กำลังทดสอบ...")
        self.lbl_active_test_res.setText(f"⏳ กำลังส่งคำขอตรวจสอบการเชื่อมต่อไปยัง {p} ({m})...")
        self.lbl_active_test_res.setStyleSheet("color: #89b4fa; font-size: 11px;")
        self.lbl_active_test_res.setVisible(True)

        def test_task():
            return test_api_connection(p, api_key=key_val, base_url=base_val, model=m)

        worker = ApiWorker(test_task)
        def on_finished(res):
            self.btn_test_active.setEnabled(True)
            self.btn_test_active.setText(orig_text)
            ok, msg = res
            if ok:
                self.lbl_active_test_res.setText(f"✅ {msg}")
                self.lbl_active_test_res.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 11px;")
            else:
                self.lbl_active_test_res.setText(f"❌ {msg}")
                self.lbl_active_test_res.setStyleSheet("color: #f38ba8; font-weight: bold; font-size: 11px;")

        def on_error(err_msg):
            self.btn_test_active.setEnabled(True)
            self.btn_test_active.setText(orig_text)
            self.lbl_active_test_res.setText(f"❌ เกิดข้อผิดพลาด: {err_msg}")
            self.lbl_active_test_res.setStyleSheet("color: #f38ba8; font-weight: bold; font-size: 11px;")

        worker.signals.finished.connect(on_finished)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

    def make_tester(self, provider_name, edit_field, button, result_label):
        def on_click():
            key_val = edit_field.text().strip() if edit_field else ""
            base_val = self.txt_base_url.text().strip() if hasattr(self, 'txt_base_url') else ""
            if provider_name == "Local LLM":
                base_val = edit_field.text().strip() if edit_field else ""
                key_val = ""

            if provider_name != "Local LLM" and not key_val:
                result_label.setText("⚠️ กรุณากรอก API Key ก่อนกดทดสอบ")
                result_label.setStyleSheet("color: #fab387; font-weight: bold; font-size: 11px;")
                result_label.setVisible(True)
                return

            button.setEnabled(False)
            orig_text = button.text()
            button.setText("⏳ กำลังทดสอบ...")
            result_label.setText(f"⏳ กำลังส่งคำขอตรวจสอบการเชื่อมต่อไปยัง {provider_name}...")
            result_label.setStyleSheet("color: #89b4fa; font-size: 11px;")
            result_label.setVisible(True)

            def test_task():
                return test_api_connection(provider_name, api_key=key_val, base_url=base_val)

            worker = ApiWorker(test_task)
            def on_finished(res):
                button.setEnabled(True)
                button.setText(orig_text)
                ok, msg = res
                if ok:
                    result_label.setText(f"✅ {msg}")
                    result_label.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 11px;")
                else:
                    result_label.setText(f"❌ {msg}")
                    result_label.setStyleSheet("color: #f38ba8; font-weight: bold; font-size: 11px;")

            def on_error(err_msg):
                button.setEnabled(True)
                button.setText(orig_text)
                result_label.setText(f"❌ เกิดข้อผิดพลาด: {err_msg}")
                result_label.setStyleSheet("color: #f38ba8; font-weight: bold; font-size: 11px;")

            worker.signals.finished.connect(on_finished)
            worker.signals.error.connect(on_error)
            QThreadPool.globalInstance().start(worker)

        return on_click

    def _on_model_combo_changed(self, idx):
        if getattr(self, '_is_loading_models', False):
            return
        if self.cbo_model.currentData() == "__custom__":
            self._prompt_custom_model()

    def _prompt_custom_model(self):
        from PyQt6.QtWidgets import QInputDialog
        cur_id = self.cbo_model.currentData() or ""
        if cur_id == "__custom__":
            cur_id = ""
        val, ok = QInputDialog.getText(
            self,
            "✏️ กำหนดชื่อโมเดล AI เอง",
            "ระบุชื่อโมเดล (Model ID) ที่ต้องการใช้งาน เช่น deepseek-chat, gpt-4o, claude-3-5-sonnet:",
            text=cur_id
        )
        if ok and val.strip():
            model_id = val.strip()
            label = f"{model_id} (กำหนดเอง)"
            self._is_loading_models = True
            insert_pos = max(0, self.cbo_model.count() - 1)
            self.cbo_model.insertItem(insert_pos, label, model_id)
            self.cbo_model.setCurrentIndex(insert_pos)
            self._is_loading_models = False
        elif not cur_id or cur_id == "__custom__":
            if self.cbo_model.count() > 0:
                self.cbo_model.setCurrentIndex(0)

    def on_provider_changed(self, new_provider):
        self.current_provider = new_provider
        self._is_loading_models = True
        current_model_data = self.cbo_model.currentData()
        self.cbo_model.clear()
        models = self.models_by_provider.get(new_provider, [])
        found_idx = -1
        for i, item in enumerate(models):
            if isinstance(item, tuple):
                label, model_id = item
            else:
                label, model_id = item, item
            self.cbo_model.addItem(label, model_id)
            if model_id == current_model_data:
                found_idx = i

        if found_idx != -1:
            self.cbo_model.setCurrentIndex(found_idx)
        elif self.cbo_model.count() > 0:
            self.cbo_model.setCurrentIndex(0)

        self._is_loading_models = False

        # Clear localhost url if switching away from Local LLM
        if new_provider != "Local LLM":
            cur_base = self.txt_base_url.text().strip().lower()
            if "localhost" in cur_base or "127.0.0.1" in cur_base:
                self.txt_base_url.clear()

    def _infer_provider(self, model_name):
        m = (model_name or "").lower()
        if "/" in m:
            return "OpenRouter"
        elif m.startswith("gemini"):
            return "Google Gemini"
        elif m.startswith("claude"):
            return "Anthropic Claude"
        elif m.startswith("gpt") or m.startswith("o1") or m.startswith("o3") or m.startswith("o4") or m.startswith("chatgpt"):
            return "OpenAI"
        elif m.startswith("qwen") or m.startswith("llama") or m.startswith("qwq") or "local" in m:
            return "Local LLM"
        return "DeepSeek"

    def load_config(self):
        try:
            data = TStudioCore.load_config()
            self.api_keys["DeepSeek"] = data.get("deepseek_key") or data.get("api_key", "")
            self.api_keys["Google Gemini"] = data.get("google_key", "")
            self.api_keys["OpenAI"] = data.get("openai_key", "")
            self.api_keys["Anthropic Claude"] = data.get("anthropic_key", "")
            self.api_keys["OpenRouter"] = data.get("openrouter_key", "")
            
            for p_name, txt in self.key_inputs.items():
                val = self.api_keys.get(p_name, "")
                txt.setText(val)
                lbl = self.key_status_labels.get(p_name)
                if lbl:
                    if val.strip():
                        lbl.setText("🟢 มีคีย์แล้ว (พร้อมใช้งาน)")
                        lbl.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 11px;")
                    else:
                        lbl.setText("⚪ ยังไม่ระบุ")
                        lbl.setStyleSheet("color: #6c7086; font-size: 11px;")

            local_url = data.get("local_url") or "http://localhost:11434/v1/chat/completions"
            self.txt_local_url.setText(local_url)

            saved_model = data.get("model", "deepseek-chat")
            provider = data.get("provider", self._infer_provider(saved_model))
            if provider not in self.models_by_provider:
                provider = "DeepSeek"

            self.cbo_provider.blockSignals(True)
            self.cbo_provider.setCurrentText(provider)
            self.cbo_provider.blockSignals(False)

            self._is_loading_models = True
            models = self.models_by_provider.get(provider, [])
            self.cbo_model.clear()
            found_idx = -1
            for i, item in enumerate(models):
                if isinstance(item, tuple):
                    label, model_id = item
                else:
                    label, model_id = item, item
                self.cbo_model.addItem(label, model_id)
                if model_id == saved_model:
                    found_idx = i

            if found_idx != -1:
                self.cbo_model.setCurrentIndex(found_idx)
            else:
                insert_pos = max(0, self.cbo_model.count() - 1)
                self.cbo_model.insertItem(insert_pos, f"{saved_model} (กำหนดเอง)", saved_model)
                self.cbo_model.setCurrentIndex(insert_pos)
            self._is_loading_models = False

            base_url = data.get("base_url", "")
            self.txt_base_url.setText(base_url)
            self.spn_temp.setValue(float(data.get("temperature", 0.3)))
            self.spn_max_tokens.setValue(int(data.get("max_tokens", 4096)))
            self.spn_timeout.setValue(int(data.get("timeout", 30)))
            self.spn_concurrency.setValue(int(data.get("batch_concurrency", 10)))

            self._update_active_tab_notice()
        except Exception as e:
            print(f"UI load_config error: {e}")

    def save_config(self):
        data = TStudioCore.load_config()
        
        deepseek_val = self.key_inputs.get("DeepSeek", QLineEdit()).text().strip()
        data["deepseek_key"] = deepseek_val
        data["api_key"] = deepseek_val # Backwards compatibility
        data["google_key"] = self.key_inputs.get("Google Gemini", QLineEdit()).text().strip()
        data["openai_key"] = self.key_inputs.get("OpenAI", QLineEdit()).text().strip()
        data["anthropic_key"] = self.key_inputs.get("Anthropic Claude", QLineEdit()).text().strip()
        data["openrouter_key"] = self.key_inputs.get("OpenRouter", QLineEdit()).text().strip()
        data["local_url"] = self.txt_local_url.text().strip()
        
        chosen_provider = self.cbo_provider.currentText()
        chosen_model = self.cbo_model.currentData() or self.cbo_model.currentText().strip()
        if chosen_model == "__custom__":
            chosen_model = "deepseek-chat"
        data["provider"] = chosen_provider
        data["model"] = chosen_model
        
        entered_base_url = self.txt_base_url.text().strip()
        data["base_url"] = entered_base_url
        data["temperature"] = self.spn_temp.value()
        data["max_tokens"] = self.spn_max_tokens.value()
        data["timeout"] = self.spn_timeout.value()
        data["batch_concurrency"] = self.spn_concurrency.value()

        TStudioCore.save_config(data)
        QMessageBox.information(self, "บันทึกสำเร็จ", "บันทึกการตั้งค่า AI Models และ Multi-API Keys เรียบร้อยแล้ว!")
        super().accept()

    def accept(self):
        self.save_config()

class PromptSettingsDialog(QDialog):
    """Unified PromptSettingsDialog wrapper pointing directly to TLMStudioDialog Tab 2 (Prompt Studio).
    Maintains 100% backward compatibility with all legacy callers and external tools."""
    def __init__(self, parent=None, active_profile=None):
        super().__init__(parent)
        from tstudio_tlm_studio import TLMStudioDialog
        self._inner = TLMStudioDialog(parent=parent, active_profile=active_profile, initial_tab=1)
        self.active_profile = self._inner.active_profile
        self.txt_single = getattr(self._inner, 'txt_p_single', None)
        self.txt_opt = getattr(self._inner, 'txt_p_opt', None)
        self.txt_batch = getattr(self._inner, 'txt_p_batch', None)

    def exec(self):
        return self._inner.exec()

    def show(self):
        return self._inner.show()

    def save_current_preset(self, close_dialog=True):
        return self._inner._save_profile_prompts(show_msg=close_dialog)

    def __getattr__(self, name):
        return getattr(self._inner, name)

GLOSSARY_TAGS = ['General', 'Person', 'Location', 'Weapon', 'Item', 'Faction', 'Quest', 'Other']

from PyQt6.QtWidgets import QStyledItemDelegate

class TagColumnDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(GLOSSARY_TAGS)
        return combo

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.ItemDataRole.EditRole) or ""
        if text in GLOSSARY_TAGS:
            editor.setCurrentText(text)
        else:
            editor.setCurrentText("General")

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)

    def paint(self, painter, option, index):
        # Draw standard item background (selection highlight, hover states, etc.)
        self.parent().style().drawControl(
            self.parent().style().ControlElement.CE_ItemViewItem,
            option, painter, self.parent()
        )
        
        text = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        if not text:
            return
            
        painter.save()
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        
        # Color mapping for tags
        tag_colors = {
            "Weapon": ("#f38ba8", "#11111b"),
            "Faction": ("#cba6f7", "#11111b"),
            "Person": ("#fab387", "#11111b"),
            "Location": ("#a6e3a1", "#11111b"),
            "Item": ("#89b4fa", "#11111b"),
            "Quest": ("#f9e2af", "#11111b"),
            "General": ("#45475a", "#cdd6f4"),
            "Other": ("#585b70", "#cdd6f4")
        }
        
        bg_color_str, text_color_str = tag_colors.get(text, ("#585b70", "#cdd6f4"))
        
        from PyQt6.QtGui import QColor, QBrush, QPen
        bg_color = QColor(bg_color_str)
        text_color = QColor(text_color_str)
        
        # Calculate badge bounds inside the cell
        rect = option.rect
        margin_h = 10
        margin_v = 4
        
        badge_width = min(80, rect.width() - (margin_h * 2))
        badge_height = rect.height() - (margin_v * 2)
        badge_x = rect.x() + (rect.width() - badge_width) // 2
        badge_y = rect.y() + margin_v
        
        from PyQt6.QtCore import QRect
        badge_rect = QRect(badge_x, badge_y, badge_width, badge_height)
        
        # Draw pill background
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(badge_rect, 8, 8)
        
        # Draw tag text
        painter.setPen(QPen(text_color))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()

class GlossaryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_profile = TStudioCore.load_profiles()["active_preset"]
        self.profile_data = TStudioCore.get_current_profile_data()
        
        self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)

        ctx_group = QGroupBox("TLM Context & Glossary Extraction")
        ctx_group.setCheckable(True)
        ctx_group.setChecked(False) # Collapsed by default as requested
        
        ctx_main_layout = QVBoxLayout(ctx_group)
        ctx_main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.ctx_container = QWidget()
        ctx_layout = QVBoxLayout(self.ctx_container)
        ctx_layout.setContentsMargins(5, 5, 5, 5)
        
        from PyQt6.QtWidgets import QSizePolicy
        ctx_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        from PyQt6.QtWidgets import QGridLayout
        grid = QGridLayout()
        grid.setSpacing(6)
        
        self.txt_game_name = QLineEdit()
        self.txt_game_name.setPlaceholderText("Game Name")
        
        self.txt_source_lang = QLineEdit()
        self.txt_source_lang.setPlaceholderText("Source (e.g. English)")
        
        self.txt_target_lang = QLineEdit()
        self.txt_target_lang.setPlaceholderText("Target (e.g. Thai)")
        _preset_name = self.profile_data.get("game_title", self.active_profile)
        if _preset_name and _preset_name != "Default":
            self.txt_game_name.setText(_preset_name)
            
        self.cbo_category = QComboBox()
        self.cbo_category.setEditable(True)
        self.cbo_category.addItems(["General", "Characters & NPCs", "Locations & World", "Items & Weapons", "Factions & Lore", "UI & Menus"])
        
        self.spin_amount = QSpinBox()
        self.spin_amount.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.spin_amount.setRange(1, 100)
        self.spin_amount.setValue(30)
        self.spin_amount.setMinimumWidth(60)
        
        self.btn_gen = QPushButton(_("btn_extract"))
        self.btn_gen.setToolTip(_("tooltip_btn_extract"))
        self.btn_gen.setStyleSheet("background-color: #cba6f7; color: #1e1e2e; font-weight: bold; border-radius: 4px; padding: 4px 12px; min-height: 22px;")
        self.btn_gen.clicked.connect(self.auto_generate_glossary)
        self.btn_gen.setToolTip("สกัดคำศัพท์ที่พบบ่อยจากเกมนี้ และแปลอัตโนมัติด้วย AI")
        
        # Game Title Column
        grid.addWidget(QLabel("Game Title"), 0, 0)
        grid.addWidget(self.txt_game_name, 1, 0)
        
        # Category Column
        grid.addWidget(QLabel("Category"), 0, 1)
        grid.addWidget(self.cbo_category, 1, 1)
        
        # Amount Column
        grid.addWidget(QLabel("Amount"), 0, 2)
        grid.addWidget(self.spin_amount, 1, 2)
        
        # Extract Button
        grid.addWidget(self.btn_gen, 1, 3)
        
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        
        self.txt_tlm_context = QTextEdit()
        self.txt_tlm_context.setPlaceholderText("Paste game lore, wiki, or dialog text here... (Optional)")
        self.txt_tlm_context.setMaximumHeight(50)
        
        ctx_layout.addLayout(grid)
        ctx_layout.addWidget(self.txt_tlm_context)
        
        ctx_main_layout.addWidget(self.ctx_container)
        ctx_group.toggled.connect(self.ctx_container.setVisible)
        self.ctx_container.setVisible(ctx_group.isChecked())
        
        layout.addWidget(ctx_group)

        # Search & Filter Bar
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.setToolTip("พิมพ์คำศัพท์เพื่อค้นหา")
        self.search_box.textChanged.connect(self.filter_glossary)
        search_layout.addWidget(self.search_box, 3)
        
        search_layout.addWidget(QLabel("Tag:"))
        self.combo_filter_tag = QComboBox()
        self.combo_filter_tag.addItems(["All"] + GLOSSARY_TAGS)
        self.combo_filter_tag.currentTextChanged.connect(self.filter_glossary)
        search_layout.addWidget(self.combo_filter_tag, 1)
        
        btn_settings = QPushButton("⚙️")
        btn_settings.clicked.connect(lambda: SettingsDialog(self).exec())
        btn_settings.setToolTip(_("tooltip_btn_ai_settings"))
        btn_settings.setStyleSheet("background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; min-height: 22px; font-size: 14px;")
        search_layout.addWidget(btn_settings)
        
        layout.addLayout(search_layout)

        self.table = QTableWidget(0, 3)
        self.table.setItemDelegateForColumn(2, TagColumnDelegate(self))
        self.table.setHorizontalHeaderLabels([_("glossary_col_word"), _("glossary_col_thai"), _("glossary_col_tag")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(self.table)
        
        self._history = []
        self._history_index = -1
        self._is_pushing_history = False

        btn_add = QPushButton(_("btn_add_row"))
        btn_add.setToolTip(_("tooltip_btn_add"))
        btn_add.clicked.connect(lambda: self.add_row())
        btn_add.setStyleSheet("background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        
        btn_auto_tag = QPushButton(_("btn_auto_tag"))
        btn_auto_tag.setStyleSheet("background-color: #89b4fa; color: #1e1e2e; font-weight: bold; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        btn_auto_tag.setToolTip(_("tooltip_btn_auto_tag"))
        btn_auto_tag.clicked.connect(self.auto_tag_general_rows)
        btn_auto_tag.setToolTip("ใช้ AI ช่วยจัดหมวดหมู่ (Tag) คำศัพท์อัตโนมัติ")
        
        from PyQt6.QtWidgets import QToolButton, QMenu
        self.btn_retrans = QToolButton()
        self.btn_retrans.setText(_("btn_retranslate"))
        self.btn_retrans.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_retrans.setStyleSheet("QToolButton { background-color: #f9e2af; color: #1e1e2e; font-weight: bold; border-radius: 4px; padding: 4px 8px; min-height: 22px; } QToolButton::menu-button { border: none; }")
        menu_retrans = QMenu(self)
        act_opt = menu_retrans.addAction(_("menu_gen_3_options"))
        act_opt.triggered.connect(self.retranslate_options)
        act_custom = menu_retrans.addAction(_("menu_custom_trans"))
        act_custom.triggered.connect(self.retranslate_custom)
        
        menu_retrans.addSeparator()
        menu_retrans.addAction(_("menu_transliterate")).triggered.connect(lambda: self.retranslate_special("transliterate"))
        menu_retrans.addAction(_("menu_idiom")).triggered.connect(lambda: self.retranslate_special("idiom"))
        menu_retrans.addAction(_("menu_poem")).triggered.connect(lambda: self.retranslate_special("poem"))
        menu_retrans.addAction(_("menu_quote")).triggered.connect(lambda: self.retranslate_special("quote"))
        menu_retrans.addSeparator()
        menu_retrans.addAction(_("menu_mature")).triggered.connect(lambda: self.retranslate_special("mature"))
        menu_retrans.addAction(_("menu_fantasy")).triggered.connect(lambda: self.retranslate_special("fantasy"))
        menu_retrans.addAction(_("menu_robotic")).triggered.connect(lambda: self.retranslate_special("robotic"))
        menu_retrans.addAction(_("menu_casual")).triggered.connect(lambda: self.retranslate_special("casual"))
        self.btn_retrans.setMenu(menu_retrans)
        self.btn_retrans.setToolTip(_("tooltip_btn_retranslate"))
        
        btn_del = QPushButton(_("btn_delete_row"))
        btn_del.clicked.connect(self.del_row)
        btn_del.setToolTip(_("tooltip_btn_delete_row"))
        btn_del.setStyleSheet("background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        
        self.btn_undo = QPushButton("↩️ Undo")
        self.btn_undo.setToolTip("ย้อนกลับ (Ctrl+Z)")
        self.btn_undo.clicked.connect(self.undo)
        self.btn_undo.setStyleSheet("background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        self.btn_undo.setEnabled(False)
        
        self.btn_redo = QPushButton("↪️ Redo")
        self.btn_redo.setToolTip("ทำซ้ำ (Ctrl+Y)")
        self.btn_redo.clicked.connect(self.redo)
        self.btn_redo.setStyleSheet("background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        self.btn_redo.setEnabled(False)
        
        from PyQt6.QtGui import QKeySequence, QShortcut
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.redo)
        QShortcut(QKeySequence("Delete"), self.table).activated.connect(self.del_row)
        
        btn_save = QPushButton(_("btn_save_to_profile"))
        btn_save.clicked.connect(lambda: self.save_glossary(True))
        btn_save.setToolTip(_("tooltip_btn_save_glossary"))
        btn_save.setStyleSheet("background-color: #a6e3a1; color: #1e1e2e; font-weight: bold; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        
        btn_export = QPushButton(_("btn_export"))
        btn_export.clicked.connect(self.export_glossary)
        btn_export.setToolTip(_("tooltip_btn_export_glossary"))
        btn_export.setStyleSheet("background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        
        btn_import = QPushButton("📥 Import")
        btn_import.clicked.connect(self.import_glossary)
        btn_import.setToolTip("นำเข้า Glossary จากไฟล์ JSON (รวมเข้ากับของเดิม)")
        btn_import.setStyleSheet("background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px 8px; min-height: 22px;")
        
        btn_layout_top = QHBoxLayout()
        btn_layout_top.setSpacing(6)
        btn_layout_top.addWidget(btn_add)
        btn_layout_top.addWidget(btn_auto_tag)
        btn_layout_top.addWidget(self.btn_undo)
        btn_layout_top.addWidget(self.btn_redo)
        btn_layout_top.addWidget(btn_del)
        
        btn_layout_bottom = QHBoxLayout()
        btn_layout_bottom.setSpacing(6)
        btn_layout_bottom.addWidget(btn_import)
        btn_layout_bottom.addWidget(btn_export)
        btn_layout_bottom.addWidget(self.btn_retrans)
        btn_layout_bottom.addWidget(btn_save)
        
        btn_container = QVBoxLayout()
        btn_container.setSpacing(4)
        btn_container.addLayout(btn_layout_top)
        btn_container.addLayout(btn_layout_bottom)
        layout.addLayout(btn_container)
        
        self._is_modified = False
        
        # Setup auto-save timer
        from PyQt6.QtCore import QTimer
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(lambda: self.save_glossary(show_msg=False))
        
        self.table.itemChanged.connect(self.mark_modified)
        self.load_glossary()


    def mark_modified(self):
        self._is_modified = True
        if not getattr(self, '_is_pushing_history', False):
            self.push_history()
        if hasattr(self, 'save_timer'):
            self.save_timer.start(500) # Auto-save 500ms after user stops typing

    def update_history_buttons(self):
        if hasattr(self, 'btn_undo') and hasattr(self, 'btn_redo'):
            self.btn_undo.setEnabled(self._history_index > 0)
            self.btn_redo.setEnabled(self._history_index < len(self._history) - 1)

    def push_history(self):
        if getattr(self, '_is_pushing_history', False):
            return
            
        snapshot = []
        for r in range(self.table.rowCount()):
            w_item = self.table.item(r, 0)
            c_item = self.table.item(r, 1)
            t_item = self.table.item(r, 2)
            if w_item and c_item:
                w = w_item.text()
                c = c_item.text()
                t = t_item.text() if t_item else "General"
                snapshot.append((w, c, t))
                
        if self._history and 0 <= self._history_index < len(self._history):
            if self._history[self._history_index] == snapshot:
                return # No change
                
        self._history = self._history[:self._history_index + 1]
        self._history.append(snapshot)
        self._history_index += 1
        self.update_history_buttons()

    def undo(self):
        if self._history_index > 0:
            self._history_index -= 1
            self.restore_history_snapshot()
            
    def redo(self):
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self.restore_history_snapshot()
            
    def restore_history_snapshot(self):
        if self._history_index < 0 or self._history_index >= len(self._history):
            return
            
        self._is_pushing_history = True
        old_state = self.table.blockSignals(True)
        self.table.setRowCount(0)
        
        snapshot = self._history[self._history_index]
        for (w, c, t) in snapshot:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(w))
            self.table.setItem(row, 1, QTableWidgetItem(c))
            tag_item = QTableWidgetItem(t)
            tag_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, tag_item)
            
        self.table.blockSignals(old_state)
        self._is_pushing_history = False
        
        self.update_history_buttons()
        self._is_modified = True
        if hasattr(self, 'save_timer'):
            self.save_timer.start(0)

    def filter_glossary(self, *args, **kwargs):
        search_text = self.search_box.text().lower()
            
        filter_tag = self.combo_filter_tag.currentText()
        
        for row in range(self.table.rowCount()):
            item_en = self.table.item(row, 0)
            item_th = self.table.item(row, 1)
            en_text = item_en.text().lower() if item_en else ""
            th_text = item_th.text().lower() if item_th else ""
            
            item_tag = self.table.item(row, 2)
            row_tag = item_tag.text() if item_tag else "General"
            
            match_text = search_text in en_text or search_text in th_text
            match_tag = (filter_tag == "All") or (filter_tag == row_tag)
            
            self.table.setRowHidden(row, not (match_text and match_tag))

    def auto_generate_glossary(self):
        import json, re
        game_name = self.txt_game_name.text().strip()
        if not game_name:
            QMessageBox.warning(self, "Warning", "Please enter a game name first!")
            return
            
        data = TStudioCore.load_profiles()
        if self.active_profile in data["presets"]:
            data["presets"][self.active_profile]["game_title"] = game_name
            data["presets"][self.active_profile]["source_language"] = self.txt_source_lang.text().strip()
            data["presets"][self.active_profile]["target_language"] = self.txt_target_lang.text().strip()
            TStudioCore.save_profiles(data)
            self.profile_data = data["presets"][self.active_profile]

        cfg = TStudioCore.load_config()
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.btn_gen.setText("⏳ Generating...")
        self.btn_gen.setEnabled(False)
        self.setWindowTitle("🧠 TLM Extractor - Generating... Please wait...")
        QApplication.processEvents()
        
        amount = self.spin_amount.value()
        category_text = self.cbo_category.currentText().strip()
        cat_prompt_part = f"specifically in the category of '{category_text}'" if category_text and category_text.lower() != "general" else "including terminology, items, factions, or character names"
        
        existing_words = []
        for r in range(self.table.rowCount()):
            item_en = self.table.item(r, 0)
            if item_en and item_en.text().strip():
                existing_words.append(item_en.text().strip())
                
        anti_dup_prompt = ""
        if existing_words:
            anti_dup_prompt = f"\nCRITICAL: Do NOT extract any of the following terminology, as they already exist in the glossary:\n{json.dumps(existing_words, ensure_ascii=False)}\n"
            
        source_lang = self.txt_source_lang.text().strip() or "English"
        target_lang = self.txt_target_lang.text().strip() or "Thai"
        
        tlm_text = self.txt_tlm_context.toPlainText().strip()
        if tlm_text:
            prompt = f"You are a video game localization expert. Your task is to extract exactly {amount} key terminology (names, places, items) from the following context for the game '{game_name}'.\n\n--- CONTEXT ---\n{tlm_text[:8000]}\n---------------\n\n" \
                     f"{anti_dup_prompt}" \
                     "You MUST output ONLY a valid JSON array. Do not use any nested objects. Each object in the array must have exactly three string keys: 'source', 'target', and 'tag'.\n" \
                     f"- 'source': The original word/term in {source_lang}.\n" \
                     f"- 'target': The translated word/term in {target_lang}.\n" \
                     "- 'tag': MUST be exactly one of the following words: General, Person, Location, Weapon, Item, Faction, Quest, Other.\n" \
                     "Output ONLY the JSON array. Do NOT output markdown formatting like ```json."
        else:
            prompt = f"You are a video game localization expert. Your task is to extract exactly {amount} most common terminology for the game '{game_name}', {cat_prompt_part}.\n" \
                     f"The source language is {source_lang} and the target language is {target_lang}.\n" \
                     f"{anti_dup_prompt}" \
                     "You MUST output ONLY a valid JSON array. Do not use any nested objects. Each object in the array must have exactly three string keys: 'source', 'target', and 'tag'.\n" \
                     f"- 'source': The original word/term in {source_lang}.\n" \
                     f"- 'target': The translated word/term in {target_lang}.\n" \
                     "- 'tag': MUST be exactly one of the following words: General, Person, Location, Weapon, Item, Faction, Quest, Other.\n" \
                     "Example of expected output:\n" \
                     '[\n  {"source": "Health Potion", "target": "ยาฟื้นฟูพลังชีวิต", "tag": "Item"},\n  {"source": "Sword", "target": "ดาบ", "tag": "Weapon"}\n]\n' \
                     "Output ONLY the JSON array. Do NOT output markdown formatting like ```json."
                 
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        
        def do_gen():
            from tstudio_core import CoreAI
            return CoreAI.generate_content(cfg, prompt, is_local=is_local)
            
        def on_error(err):
            try:
                self.isVisible()  # Guard: raises RuntimeError if C++ object is deleted
            except RuntimeError:
                QApplication.restoreOverrideCursor()
                return
            self.btn_gen.setText("🧠 Extract from TLM")
            self.btn_gen.setEnabled(True)
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(f"🧠 TLM Extractor")
            QMessageBox.critical(self, "Failed", f"Error generating glossary:\n{err}")

        def on_success(res):
            try:
                self.isVisible()  # Guard: raises RuntimeError if C++ object is deleted
            except RuntimeError:
                QApplication.restoreOverrideCursor()
                return
            try:
                import re, json
                match = re.search(r'\[.*\]', res, re.DOTALL)
                if match:
                    clean_res = match.group(0)
                else:
                    clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)
                    
                new_terms = json.loads(clean_res)
                
                if isinstance(new_terms, dict):
                    raise Exception("AI returned a JSON Dictionary instead of an Array.")
                if not isinstance(new_terms, list):
                    raise Exception("AI did not return a JSON Array.")
                
                self.merge_new_terms(new_terms, game_name)
                
                self.btn_gen.setText("🧠 Extract from TLM")
                self.btn_gen.setEnabled(True)
                QApplication.restoreOverrideCursor()
                self.setWindowTitle(f"🧠 TLM Extractor")
            except Exception as e:
                on_error(f"Data parsing error: {e}\n\nRaw Response:\n{res[:200]}...")
            
        worker = ApiWorker(do_gen)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)

    def merge_new_terms(self, new_terms, game_name=""):
        added_count = 0
        merged_count = 0
        
        self._is_pushing_history = True
        
        # Pre-fetch existing glossary items for deduplication
        existing_terms = {}
        for r in range(self.table.rowCount()):
            item_en = self.table.item(r, 0)
            item_th = self.table.item(r, 1)
            if item_en and item_th:
                existing_terms[item_en.text().strip().lower()] = (r, item_th.text().strip())
                
        for item in new_terms:
            if not isinstance(item, dict): continue
            # Support both new ('source'/'target') and legacy ('en'/'th') JSON keys
            en = (item.get("source") or item.get("en", "")).strip()
            th = (item.get("target") or item.get("th", "")).strip()
            tag = item.get("tag", "General")
            if not en or not th: continue
            
            en_lower = en.lower()
            if en_lower in existing_terms:
                # Collision! Check if Thai translation is different
                row_idx, old_th = existing_terms[en_lower]
                if old_th != th and th not in old_th:
                    new_th = f"{old_th} / {th}"
                    self.table.item(row_idx, 1).setText(new_th)
                    existing_terms[en_lower] = (row_idx, new_th) # update cache
                    self.mark_modified()
                    merged_count += 1
            else:
                self.add_row(en, th, tag)
                existing_terms[en_lower] = (self.table.rowCount() - 1, th)
                added_count += 1
        
        if added_count == 0 and merged_count == 0:
            self._is_pushing_history = False
            raise Exception("AI returned valid JSON, but no new or unique terms were extracted.")
            
        self._is_pushing_history = False
        self.push_history()
        self.save_glossary(show_msg=False)
        QMessageBox.information(self, "Success", f"Glossary terms updated!\nAdded: {added_count} terms\nMerged: {merged_count} duplicates")

    def load_glossary(self):
        self._is_pushing_history = True
        old_state = self.table.blockSignals(True)
        self.table.setRowCount(0)
        
        target_lang = self.profile_data.get("target_language", "Target") if self.profile_data else "Target"
        if not target_lang:
            target_lang = "Target"
            
        ui_lang = os.environ.get("THUB_LANG", "th")
        if target_lang.lower() in ["thai", "th", "ไทย"]:
            target_header = _("glossary_col_thai")
        else:
            if ui_lang == "th":
                target_header = f"คำแปลภาษา {target_lang} (จำเป็น)"
            else:
                target_header = f"{target_lang} Translation (Required)"
        
        self.table.setHorizontalHeaderLabels([_("glossary_col_word"), target_header, _("glossary_col_tag")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        for wrong, val in self.profile_data.get("glossary", {}).items():
            if isinstance(val, list):
                right = val[0]
                tag = val[1] if len(val) > 1 else "General"
            else:
                right = val
                tag = "General"
            self.add_row(wrong, right, tag)
        self.table.blockSignals(old_state)
        self._is_modified = False
        self._is_pushing_history = False
        
        self._history = []
        self._history_index = -1
        self.push_history()

    def add_row(self, wrong="", right="", tag="General"):
        old_state = self.table.blockSignals(True)
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(wrong))
        self.table.setItem(row, 1, QTableWidgetItem(right))
        
        tag_item = QTableWidgetItem(tag)
        tag_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 2, tag_item)
        
        self.table.blockSignals(old_state)
        self._is_modified = True
        if not getattr(self, '_is_pushing_history', False):
            self.push_history()

    def export_glossary(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import json
        
        path, _ext = QFileDialog.getSaveFileName(self, "Export Glossary", "", "JSON Files (*.json)")
        if not path:
            return
            
        data = TStudioCore.load_profiles()
        glossary_data = data["presets"][self.active_profile].get("glossary", {})
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(glossary_data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Success", f"Glossary exported successfully to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export glossary:\n{str(e)}")
            
    def import_glossary(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import json
        
        path, _ext = QFileDialog.getOpenFileName(self, "Import Glossary", "", "JSON Files (*.json)")
        if not path:
            return
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
                
            if not isinstance(imported_data, dict):
                QMessageBox.warning(self, "Error", "Invalid JSON format. Expected a dictionary.")
                return
                
            data = TStudioCore.load_profiles()
            current_glossary = data["presets"][self.active_profile].get("glossary", {})
            
            # Merge imported data
            for eng, val in imported_data.items():
                if isinstance(val, list) and len(val) >= 2:
                    current_glossary[eng] = val
                elif isinstance(val, str):
                    current_glossary[eng] = [val, "General"]
            
            data["presets"][self.active_profile]["glossary"] = current_glossary
            TStudioCore.save_profiles(data)
            
            self.profile_data = data["presets"][self.active_profile]
            self.load_glossary()  # Fixed: was self.load_data() which doesn't exist
            QMessageBox.information(self, "Success", "Glossary imported successfully!")
            
            # Notify TranslationStudio main window to refresh QA checks and markers
            p = self.parent()
            while p:
                if p.__class__.__name__ == 'TranslationStudio' and hasattr(p, 'refresh_glossary_dependent_features'):
                    p.refresh_glossary_dependent_features()
                    break
                p = p.parent()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import glossary:\n{str(e)}")



    def del_row(self):
        rows = set()
        for item in self.table.selectedItems():
            rows.add(item.row())
            
        if not rows:
            row = self.table.currentRow()
            if row >= 0:
                rows.add(row)
                
        if not rows:
            return
            
        old_state = self.table.blockSignals(True)
        for row in sorted(list(rows), reverse=True):
            self.table.removeRow(row)
        self.table.blockSignals(old_state)
        
        self.push_history()
        self._is_modified = True
        if hasattr(self, 'save_timer'):
            self.save_timer.start(0) # Save deletion immediately

    def save_glossary(self, show_msg=True):
        data = TStudioCore.load_profiles()
        if self.active_profile in data["presets"]:
            new_glossary = {}
            for r in range(self.table.rowCount()):
                w, c = self.table.item(r, 0), self.table.item(r, 1)
                tag_item = self.table.item(r, 2)
                if w and c and w.text().strip():
                    tag = tag_item.text() if tag_item else "General"
                    new_glossary[w.text().strip()] = [c.text().strip(), tag]
            data["presets"][self.active_profile]["glossary"] = new_glossary
            TStudioCore.save_profiles(data)
            self._is_modified = False
            if show_msg:
                QMessageBox.information(self, "Saved", f"Glossary saved to profile '{self.active_profile}'!")
            
            # Notify TranslationStudio main window to refresh QA checks and markers
            p = self.parent()
            while p:
                if p.__class__.__name__ == 'TranslationStudio' and hasattr(p, 'refresh_glossary_dependent_features'):
                    p.refresh_glossary_dependent_features()
                    break
                p = p.parent()

    def closeEvent(self, event):
        if getattr(self, '_is_modified', False):
            if hasattr(self, 'save_timer') and self.save_timer.isActive():
                self.save_timer.stop()
            self.save_glossary(show_msg=False)
        event.accept()


    def auto_tag_general_rows(self):
        rows_to_tag = []
        terms_to_tag = []
        for r in range(self.table.rowCount()):
            tag_item = self.table.item(r, 2)
            w = self.table.item(r, 0)
            c = self.table.item(r, 1)
            row_tag = tag_item.text() if tag_item else "General"
            if w and c and row_tag == "General":
                if w.text().strip() and c.text().strip():
                    rows_to_tag.append(r)
                    terms_to_tag.append({"en": w.text().strip(), "th": c.text().strip()})
        
        if not terms_to_tag:
            QMessageBox.information(self, "Auto-Tag", "No 'General' items to tag!")
            return
            
        cfg = TStudioCore.load_config()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.setWindowTitle("📖 Glossary Editor - Auto-Tagging... Please wait...")
        QApplication.processEvents()
        
        prompt = "You are a video game localization expert.\n" \
                 "Categorize the following glossary terms into exactly one of these tags: General, Person, Location, Weapon, Item, Faction, Quest, Other.\n" \
                 "Input terms:\n" + json.dumps(terms_to_tag, ensure_ascii=False) + "\n\n" \
                 "You MUST output ONLY a valid JSON array matching the exact same order. Do not use nested objects. Each object must have a 'tag' string key.\n" \
                 "Example of expected output:\n" \
                 '[\n  {"tag": "Item"},\n  {"tag": "Person"}\n]\n' \
                 "Output ONLY the JSON array. Do NOT output markdown formatting like ```json."
                 
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        
        def do_tag():
            return CoreAI.generate_content(cfg, prompt, is_local=is_local)
            
        def on_error(err):
            try:
                self.isVisible()  # Guard: raises RuntimeError if C++ object is deleted
            except RuntimeError:
                QApplication.restoreOverrideCursor()
                return
            self.btn_gen.setText("🧠 Extract from TLM")
            self.btn_gen.setEnabled(True)
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
            QMessageBox.critical(self, "Failed", f"Error auto-tagging:\n{err}")

        def on_success(res):
            try:
                self.isVisible()  # Guard: raises RuntimeError if C++ object is deleted
            except RuntimeError:
                QApplication.restoreOverrideCursor()
                return
            try:
                match = re.search(r'\[.*\]', res, re.DOTALL)
                if match:
                    clean_res = match.group(0)
                else:
                    clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)
                    
                new_tags = json.loads(clean_res)
                
                if not isinstance(new_tags, list):
                    raise Exception("AI did not return a JSON Array.")
                if len(new_tags) != len(rows_to_tag):
                    raise Exception(f"AI returned {len(new_tags)} tags but expected {len(rows_to_tag)}.")
                
                self._is_pushing_history = True
                for idx, item in enumerate(new_tags):
                    tag = item.get("tag", "General")
                    if tag in GLOSSARY_TAGS:
                        row = rows_to_tag[idx]
                        tag_item = self.table.item(row, 2)
                        if tag_item:
                            tag_item.setText(tag)
                        else:
                            tag_item = QTableWidgetItem(tag)
                            tag_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.table.setItem(row, 2, tag_item)
                            
                self._is_pushing_history = False
                self.push_history()
                self.save_glossary(show_msg=False)
                self.btn_gen.setText("🧠 Extract from TLM")
                self.btn_gen.setEnabled(True)
                QApplication.restoreOverrideCursor()
                self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
                QMessageBox.information(self, "Success", f"Successfully auto-tagged {len(rows_to_tag)} items and saved to profile!")
            except Exception as e:
                on_error(f"Data parsing error: {e}\n\nRaw Response:\n{res[:200]}...")

        worker = ApiWorker(do_tag)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)




    def retranslate_options(self):
        row = self.table.currentRow()
        if row < 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please select a row first!")
            return

        item_en = self.table.item(row, 0)
        if not item_en or not item_en.text().strip():
            return

        # CO-C2: capture item identity instead of stale integer row
        anchor_item = self.table.item(row, 0)

        cfg = TStudioCore.load_config()
        self.setWindowTitle("📖 Glossary Editor - Translating... Please wait...")
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QApplication.processEvents()

        source_text = item_en.text().strip()
        prompt = f"You are a professional video game localization expert.\n" \
                 f"Provide 3 different Thai translation options for the glossary term: '{source_text}'.\n" \
                 f"Output ONLY a JSON array of strings containing the 3 options. No markdown formatting."

        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")

        def do_opt():
            return CoreAI.generate_content(cfg, prompt, is_local=is_local)

        def on_error(err):
            from PyQt6.QtWidgets import QMessageBox
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
            QMessageBox.critical(self, "Failed", f"Error generating options:\n{err}")

        def on_success(res):
            try:
                import re
                match = re.search(r'\[.*\]', res, re.DOTALL)
                if match:
                    clean_res = match.group(0)
                else:
                    clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)

                import json
                options = json.loads(clean_res)

                if not isinstance(options, list) or len(options) == 0:
                    raise Exception("Invalid JSON Array format from AI.")

                QApplication.restoreOverrideCursor()
                self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")

                dlg = TranslationOptionsDialog(self, options)
                if dlg.exec() and dlg.selected_text:
                    # CO-C2: resolve current row from anchor_item to avoid stale index
                    if anchor_item is None:
                        return
                    target_row = None
                    for r in range(self.table.rowCount()):
                        if self.table.item(r, 0) is anchor_item:
                            target_row = r
                            break
                    if target_row is None:
                        return
                    item_th = self.table.item(target_row, 1)
                    if not item_th:
                        from PyQt6.QtWidgets import QTableWidgetItem
                        item_th = QTableWidgetItem()
                        self.table.setItem(target_row, 1, item_th)
                    item_th.setText(dlg.selected_text)
                    self.mark_modified()

            except Exception as e:
                on_error(f"Data parsing error: {e}\n\nRaw Response:\n{res[:200]}...")

        worker = ApiWorker(do_opt)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)


    def retranslate_custom(self):
        row = self.table.currentRow()
        if row < 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please select a row first!")
            return

        item_en = self.table.item(row, 0)
        if not item_en or not item_en.text().strip():
            return

        # CO-C2: capture item identity instead of stale integer row
        anchor_item = self.table.item(row, 0)

        from PyQt6.QtWidgets import QInputDialog, QApplication
        from PyQt6.QtCore import Qt
        custom_prompt, ok = QInputDialog.getMultiLineText(self, "Custom Translation", "Enter your custom prompt for this term (use {term} for the English word):", "Translate the glossary term: '{term}' to Thai. Output only the translated word.")
        if ok and custom_prompt.strip():
            cfg = TStudioCore.load_config()
            self.setWindowTitle("📖 Glossary Editor - Translating... Please wait...")
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            QApplication.processEvents()

            source_text = item_en.text().strip()
            prompt = custom_prompt.replace('{term}', source_text)

            is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")

            def do_cus():
                return CoreAI.generate_content(cfg, prompt, is_local=is_local)

            def on_success(res):
                import re
                clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)

                QApplication.restoreOverrideCursor()
                self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")

                # CO-C2: resolve current row from anchor_item to avoid stale index
                if anchor_item is None:
                    return
                target_row = None
                for r in range(self.table.rowCount()):
                    if self.table.item(r, 0) is anchor_item:
                        target_row = r
                        break
                if target_row is None:
                    return
                item_th = self.table.item(target_row, 1)
                if not item_th:
                    from PyQt6.QtWidgets import QTableWidgetItem
                    item_th = QTableWidgetItem()
                    self.table.setItem(target_row, 1, item_th)
                item_th.setText(clean_res)
                self.mark_modified()

            def on_error(err):
                from PyQt6.QtWidgets import QMessageBox
                QApplication.restoreOverrideCursor()
                self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
                QMessageBox.critical(self, "Failed", f"Error translating:\n{err}")

            worker = ApiWorker(do_cus)
            forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
            worker.signals.finished.connect(forwarder.handle_finished)
            worker.signals.error.connect(forwarder.handle_error)
            QThreadPool.globalInstance().start(worker)

    def retranslate_special(self, mode):
        row = self.table.currentRow()
        if row < 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please select a row first!")
            return
            
        item_en = self.table.item(row, 0)
        if not item_en or not item_en.text().strip():
            return
            
        anchor_item = self.table.item(row, 0)
        cfg = TStudioCore.load_config()
        self.setWindowTitle(f"📖 Glossary Editor - Translating ({mode})...")
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QApplication.processEvents()

        source_text = item_en.text().strip()
        
        mode_text = ""
        length_constraint = "Keep your translation CONCISE. Match the length and structure of the original text as closely as possible."
        
        if mode == "transliterate":
            mode_text = "TRANSLITERATE (แปลทับศัพท์) the original text into Thai pronunciation WITHOUT translating its meaning. Return ONLY the transliterated word."
        elif mode == "idiom":
            mode_text = f"Analyze the underlying meaning carefully. Translate into a natural, contextually appropriate Thai idiom or phrase (สำนวน/คำพังเพย). {length_constraint}"
        elif mode == "poem":
            mode_text = f"Translate into an elegant Thai poetic form (กลอน/บทกวี/คาถา) with appropriate rhyming. {length_constraint}"
        elif mode == "quote":
            mode_text = f"Translate into formal, philosophical, and impactful Thai language (คำคม/ปรัชญา). {length_constraint}"
        elif mode == "mature":
            mode_text = f"Translate aggressively using mature, unfiltered, or profane Thai language (หยาบคาย/ดุดัน) appropriate for a gritty action game. {length_constraint}"
        elif mode == "fantasy":
            mode_text = f"Translate using medieval, fantasy, or archaic Thai language (ย้อนยุค/แฟนตาซี) (e.g., ข้า, เจ้า, ฝ่าบาท). {length_constraint}"
        elif mode == "robotic":
            mode_text = f"Translate into cold, systemic, robotic Thai language (ประกาศจากระบบ/AI). {length_constraint}"
        elif mode == "casual":
            mode_text = f"Translate into modern, casual, or sarcastic Thai slang (วัยรุ่น/กวนๆ) suitable for natural youth conversation. {length_constraint}"
            
        prompt = f"You are a professional video game localization expert.\n{mode_text}\n\nOriginal Text: '{source_text}'\n\nOutput ONLY the translated term without quotes or formatting."

        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        
        def do_special():
            return CoreAI.generate_content(cfg, prompt, is_local=is_local)
            
        def on_error(err):
            from PyQt6.QtWidgets import QMessageBox
            QApplication.restoreOverrideCursor()
            self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")
            QMessageBox.critical(self, "API Error", f"Failed to connect to API:\n{err}")

        def on_success(res):
            try:
                import re
                clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)
                clean_res = re.sub(r'^"|"$', '', clean_res).strip()
                
                if anchor_item is None: return
                target_row = None
                for r in range(self.table.rowCount()):
                    if self.table.item(r, 0) is anchor_item:
                        target_row = r
                        break
                if target_row is None: return
                
                item_th = self.table.item(target_row, 1)
                if not item_th:
                    from PyQt6.QtWidgets import QTableWidgetItem
                    item_th = QTableWidgetItem()
                    self.table.setItem(target_row, 1, item_th)
                item_th.setText(clean_res)
                self.mark_modified()
            except Exception as e:
                on_error(f"Data parsing error: {e}")
            finally:
                QApplication.restoreOverrideCursor()
                self.setWindowTitle(f"📖 Glossary Editor (Editing: {self.active_profile})")

        worker = ApiWorker(do_special)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success=on_success, on_error=on_error, parent=self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)

    # --- duplicate retranslate_options (blocking/wrong import) and duplicate retranslate_custom (bare signals) removed ---

class SmartImportDialog(QDialog):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TFormat - Smart Import")
        self.resize(450, 300)
        self.headers = headers
        self.mapping = {}
        
        layout = QVBoxLayout(self)
        lbl_info = QLabel("⚠️ พบคอลัมน์ที่ไม่ตรงตามมาตรฐาน!\nโปรดจับคู่คอลัมน์ด้านล่างเพื่อให้ TFormat จัดระเบียบไฟล์ให้คุณ:")
        lbl_info.setStyleSheet("font-weight: bold; color: #f9e2af; font-size: 14px;")
        layout.addWidget(lbl_info)
        layout.addSpacing(10)
        
        form = QFormLayout()
        
        self.cbo_id = QComboBox()
        self.cbo_id.addItems(headers)
        
        self.cbo_src = QComboBox()
        self.cbo_src.addItems(headers)
        
        self.cbo_trans = QComboBox()
        self.cbo_trans.addItem("-- สร้างคอลัมน์แปลใหม่ (ว่างเปล่า) --")
        self.cbo_trans.addItems(headers)
        
        # Auto-guess logic
        for idx, h in enumerate(headers):
            hl = str(h).lower()
            if 'id' in hl or 'key' in hl: self.cbo_id.setCurrentIndex(idx)
            elif 'source' in hl or 'en' in hl or 'text' in hl or 'orig' in hl: self.cbo_src.setCurrentIndex(idx)
            elif 'trans' in hl or 'th' in hl or 'target' in hl: self.cbo_trans.setCurrentIndex(idx + 1)
            
        form.addRow("🔑 ID Column:", self.cbo_id)
        form.addRow("📄 Source Text:", self.cbo_src)
        form.addRow("🇹🇭 Translation (Optional):", self.cbo_trans)
        
        layout.addLayout(form)
        layout.addStretch()
        
        btn_box = QHBoxLayout()
        btn_ok = QPushButton(_("btn_format_file"))
        btn_ok.setToolTip(_("tooltip_btn_ok"))
        btn_ok.setStyleSheet("background: #a6e3a1; color: #1e1e2e; font-weight: bold; padding: 6px;")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton(_("btn_cancel"))
        btn_cancel.setToolTip(_("tooltip_btn_cancel"))
        btn_cancel.clicked.connect(self.reject)
        
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_ok)
        layout.addLayout(btn_box)

    def get_mapping(self):
        trans_col = self.cbo_trans.currentText()
        if trans_col == "-- สร้างคอลัมน์แปลใหม่ (ว่างเปล่า) --":
            trans_col = None
            
        return {
            "id": self.cbo_id.currentText(),
            "source": self.cbo_src.currentText(),
            "trans": trans_col
        }


