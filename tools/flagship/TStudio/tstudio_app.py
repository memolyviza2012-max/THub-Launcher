from tstudio_i18n import _
# -*- coding: utf-8 -*-
"""
Translation_Studio_Template.py
===============================
Universal Translation Studio Template
Adapted from the Studio Template to handle CSV and direct JSON deployment.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Core')))
import csv
import sys
csv.field_size_limit(2147483647)
import html
import json
import requests
import re
import shutil
import unicodedata
import file_converter

THAI_DEPENDENT_MARKS = set(
    '\u0e31'                          # ั (ไม้หันอากาศ)
    '\u0e33'                          # ำ (สระอำ)
    '\u0e34\u0e35\u0e36\u0e37'          # ิ ี ึ ื (สระบน)
    '\u0e38\u0e39\u0e3a'              # ุ ู ฺ (สระล่าง, พินทุ)
    '\u0e47'                          # ็ (ไม้ไต่คู้)
    '\u0e48\u0e49\u0e4a\u0e4b\u0e4c'  # ่ ้ ๊ ๋ ์ (วรรณยุกต์และทัณฑฆาต)
    '\u0e4d\u0e4e'                  # ํ ๎ (นิคหิต, ยามักการ)
)

def build_search_boundary_regex(query, match_case=False):
    """
    Builds a boundary regex for matching whole words or isolated Thai marks:
    1. If query is a Thai dependent mark (e.g. ำ, ่, ้, ิ, ์):
       Matches ONLY when it is an isolated / orphaned mark NOT attached to a preceding consonant.
    2. Otherwise:
       Uses standard word boundary (?<![A-Za-z0-9_ก-๙])query(?![A-Za-z0-9_ก-๙])
    """
    if not query:
        return None
    clean_q = unicodedata.normalize('NFC', query.strip())
    flags = 0 if match_case else re.IGNORECASE
    if clean_q and all(c in THAI_DEPENDENT_MARKS for c in clean_q):
        if clean_q in ('ำ', '\u0e4d\u0e32'):
            # Sara Am: isolated if NOT preceded by [ก-ฮ] or [ก-ฮ][่-๋]
            pat = r'(?<![\u0e01-\u0e2e])(?<![\u0e01-\u0e2e][\u0e48-\u0e4b])(?:\u0e33|\u0e4d\u0e32)'
        else:
            # Tone marks & vowels: isolated if NOT preceded by [ก-ฮ] or [ก-ฮ][ัิ-ืฺุู]
            pat = r'(?<![\u0e01-\u0e2e])(?<![\u0e01-\u0e2e][\u0e31\u0e34-\u0e3a])' + re.escape(clean_q)
        return re.compile(pat, flags)
    else:
        pat = r'(?<![A-Za-z0-9_ก-๙])' + re.escape(query) + r'(?![A-Za-z0-9_ก-๙])'
        return re.compile(pat, flags)

from tpua_engine import TPUAEngine
from tstudio_core import TStudioCore, CoreAI
from translation_transport import TranslationGateway, snapshot_config, is_web, RowTarget
from translation_transport.qt_controls import TranslationChannelWidget
from translation_transport.contracts import apply_glossary_snapshot, tags_match
from tstudio_telltale import TelltaleManager
from tstudio_ui_shared import SettingsDialog, PromptSettingsDialog, GlossaryWidget, ApiWorker, ThreadSafeWorkerSignalsForwarder
from tstudio_tlm_studio import (
    UNIVERSE_TONES_BY_CATEGORY, detect_game_universe_tone, detect_game_universe_tone_with_api,
    collect_stratified_dialogue_samples, apply_easy_mode,
    is_common_generic_english_word, is_engine_markup_tag, RE_VOCAL_SOUNDS
)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableView, QHeaderView, QLabel, QPushButton, QLineEdit,
    QSplitter, QGroupBox, QComboBox, QMessageBox, QTextEdit,
    QAbstractItemView, QDialog, QFormLayout, QTableWidget,
    QTableWidgetItem, QRadioButton, QButtonGroup, QScrollArea,
    QFileDialog, QMenu, QSpinBox, QProgressBar, QDockWidget, QMenuBar, QSizePolicy, QToolButton, QCheckBox,
    QStackedWidget, QFrame, QStyledItemDelegate, QStyle, QGraphicsDropShadowEffect, QTabWidget
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, QTimer, QRunnable, QThreadPool, pyqtSignal, pyqtSlot, QObject, QFileSystemWatcher, QRect, QRectF, QPoint, QSize
from PyQt6.QtGui import QColor, QKeySequence, QShortcut, QIcon, QPixmap, QAction, QPainter, QBrush, QPen, QFont
from flow_layout import FlowLayout

# ╔══════════════════════════════════════════════════════════════════╗
# ║           PROJECT CONFIGURATION — GOTG SPECIFIC                 ║
# ╚══════════════════════════════════════════════════════════════════╝
GAME_NAME    = "Your_Game_Name_Here"

if getattr(sys, 'frozen', False) and os.path.basename(sys.executable).lower() in ("tstudio.exe", "tstudio_app.exe"):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATH     = os.path.join(BASE_DIR, "translation.csv")
CSV_ENCODING = "utf-8-sig"
COL_ID       = 0
COL_SOURCE   = 1
COL_TRANS    = 2
COL_AI_REF   = 3
# ═══════════════════════════════════════════════════════════════════

CONFIG_PATH  = os.path.join(BASE_DIR, "config.json")
GLOSSARY_PATH = os.path.join(BASE_DIR, "glossary.json")
PROMPTS_PATH = os.path.join(BASE_DIR, "prompts.json")

TOP_BAR_SUBMODELS = {
    "DeepSeek": [
        ("deepseek-chat (DeepSeek-V3 แนะนำ/ประหยัดสุด)", "deepseek-chat"),
        ("deepseek-reasoner (DeepSeek-R1 ตรรกะ CoT)", "deepseek-reasoner"),
        ("✏️ กำหนดชื่อโมเดลเอง (Custom)...", "__custom__"),
    ],
    "Google Gemini": [
        ("gemini-2.0-flash (แนะนำ เร็ว/ประหยัดสุด เทียบเท่า DeepSeek)", "gemini-2.0-flash"),
        ("gemini-2.0-flash-lite (ประหยัดสูงสุด/เน้นความเร็วจัด)", "gemini-2.0-flash-lite"),
        ("gemini-2.0-flash-thinking-exp-01-21 (Reasoning ตรรกะ CoT)", "gemini-2.0-flash-thinking-exp-01-21"),
        ("gemini-2.0-pro-exp-02-05 (คุณภาพสูงสุด/บริบทซับซ้อน)", "gemini-2.0-pro-exp-02-05"),
        ("gemini-1.5-pro (2M Context มหาศาล)", "gemini-1.5-pro"),
        ("gemini-1.5-flash (เสถียร LTS)", "gemini-1.5-flash"),
        ("gemini-1.5-flash-8b (จิ๋ว/ประหยัด)", "gemini-1.5-flash-8b"),
        ("✏️ กำหนดชื่อโมเดลเอง (Custom)...", "__custom__"),
    ],
    "Anthropic Claude": [
        ("claude-3-5-haiku-20241022 (Claude 3.5 Haiku แนะนำ/เร็ว/ประหยัดสุด)", "claude-3-5-haiku-20241022"),
        ("claude-3-7-sonnet-20250219 (Claude 3.7 Sonnet ยอดนิยม/Hybrid Reasoning)", "claude-3-7-sonnet-20250219"),
        ("claude-3-5-sonnet-20241022 (Claude 3.5 Sonnet v2 คุณภาพการแปลยอดเยี่ยม)", "claude-3-5-sonnet-20241022"),
        ("claude-3-opus-20240229 (Claude 3 Opus โมเดลระดับพรีเมียม)", "claude-3-opus-20240229"),
        ("✏️ กำหนดชื่อโมเดลเอง (Custom)...", "__custom__"),
    ],
    "OpenAI": [
        ("gpt-4o-mini (GPT-4o Mini แนะนำ/ประหยัดสุด เทียบเท่า DeepSeek)", "gpt-4o-mini"),
        ("gpt-4o (Omni Flagship ฉลาดแม่นยำสูง)", "gpt-4o"),
        ("o3-mini (Reasoning ตรรกะ ความเร็วสูง)", "o3-mini"),
        ("o1 (Reasoning ตรรกะ Flagship)", "o1"),
        ("o1-mini (Reasoning ตรรกะ ประหยัด)", "o1-mini"),
        ("gpt-4.5-preview (Frontier โมเดลใหญ่สุด)", "gpt-4.5-preview"),
        ("chatgpt-4o-latest (อัปเดตล่าสุดเสมอ)", "chatgpt-4o-latest"),
        ("✏️ กำหนดชื่อโมเดลเอง (Custom)...", "__custom__"),
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
        ("✏️ กำหนดชื่อโมเดลเอง (Custom)...", "__custom__"),
    ],
    "Local LLM": [
        ("qwen2.5-coder-32b-instruct (Qwen 2.5 Coder 32B แนะนำ LM Studio)", "qwen2.5-coder-32b-instruct"),
        ("qwen2.5-14b-instruct (Qwen 2.5 14B LM Studio)", "qwen2.5-14b-instruct"),
        ("qwen2.5-7b-instruct (Qwen 2.5 7B LM Studio)", "qwen2.5-7b-instruct"),
        ("qwen2.5-32b-instruct (Qwen 2.5 32B LM Studio)", "qwen2.5-32b-instruct"),
        ("qwen2.5:14b (Qwen 2.5 14B Ollama)", "qwen2.5:14b"),
        ("qwen2.5:7b (Qwen 2.5 7B Ollama)", "qwen2.5:7b"),
        ("qwen2.5:32b (Qwen 2.5 32B Ollama)", "qwen2.5:32b"),
        ("qwen2.5-coder:32b (Qwen 2.5 Coder 32B Ollama)", "qwen2.5-coder:32b"),
        ("deepseek-r1:14b (DeepSeek R1 14B Local)", "deepseek-r1:14b"),
        ("deepseek-r1:8b (DeepSeek R1 8B Local)", "deepseek-r1:8b"),
        ("qwq:32b (QwQ 32B Reasoning Local)", "qwq:32b"),
        ("llama3.3:70b (Llama 3.3 70B Local)", "llama3.3:70b"),
        ("custom-local-llm (Custom Local Model)", "custom-local-llm"),
        ("✏️ กำหนดชื่อโมเดลเอง (Custom)...", "__custom__"),
    ]
}

def format_model_display_name(model_id, provider=""):
    if not model_id or model_id == "__custom__":
        return provider or "AI"
    m_clean = str(model_id).split("/")[-1].strip()
    mapping = {
        "deepseek-chat": "DeepSeek-V3",
        "deepseek-reasoner": "DeepSeek-R1",
        "gemini-2.0-flash": "Gemini 2.0 Flash",
        "gemini-2.0-flash-lite": "Gemini Flash-Lite",
        "gemini-2.0-flash-thinking-exp-01-21": "Gemini 2.0 Thinking",
        "gemini-2.0-pro-exp-02-05": "Gemini 2.0 Pro",
        "gemini-1.5-pro": "Gemini 1.5 Pro",
        "gemini-1.5-flash": "Gemini 1.5 Flash",
        "gemini-1.5-flash-8b": "Gemini 1.5 Flash-8B",
        "claude-3-5-haiku-20241022": "Claude 3.5 Haiku",
        "claude-3-7-sonnet-20250219": "Claude 3.7 Sonnet",
        "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
        "claude-3-opus-20240229": "Claude 3 Opus",
        "gpt-4o-mini": "GPT-4o Mini",
        "gpt-4o": "GPT-4o",
        "o3-mini": "o3-mini",
        "o1": "o1",
        "o1-mini": "o1-mini",
        "gpt-4.5-preview": "GPT-4.5",
        "chatgpt-4o-latest": "ChatGPT-4o",
        "qwen2.5-coder-32b-instruct": "Qwen 2.5 Coder 32B",
        "qwen2.5-14b-instruct": "Qwen 2.5 14B",
        "qwen2.5-7b-instruct": "Qwen 2.5 7B",
        "qwen2.5-32b-instruct": "Qwen 2.5 32B",
        "qwen2.5:14b": "Qwen 2.5 14B",
        "qwen2.5:7b": "Qwen 2.5 7B",
        "qwen2.5:32b": "Qwen 2.5 32B",
        "qwen2.5-coder:32b": "Qwen 2.5 Coder 32B",
        "deepseek-r1:14b": "DeepSeek R1 14B",
        "deepseek-r1:8b": "DeepSeek R1 8B",
        "qwq:32b": "QwQ 32B",
        "llama3.3:70b": "Llama 3.3 70B",
        "custom-local-llm": "Custom Local LLM",
        "local-model": "Local LLM",
    }
    if m_clean in mapping:
        return mapping[m_clean]
    if len(m_clean) > 22:
        return m_clean[:20] + "..."
    return m_clean


DEFAULT_SINGLE_PROMPT = f"""You are a Master-Level Video Game Localization Specialist for '{GAME_NAME}', translating the original source language into natural Thai.
Translate this line. ID: '{{id}}'. Return ONLY the pure Thai string, no quotes, no explanations.
[GLOSSARY TO USE]
- Character A = Name A
- Gamora = กาโมร่า
- Drax = แดร็กซ์
- Rocket = ร็อคเก็ต
- Groot = กรู้ท
- Mantis = แมนทิส
- Milano = ยานมิลาโน่
- Nova Corps = โนวาคอร์ปส
- Lady Hellbender = เลดี้เฮลเบนเดอร์
- Knowhere = โนว์แวร์
- Cosmo = คอสโม่
- Universal Church of Truth = คริสตจักรแห่งสัจธรรมสากล
- Grand Unifier Raker = แกรนด์ยูนิฟายเออร์เรกเกอร์
- Worldmind = เวิลด์มายด์
- Flark = ฟลาร์ก
- Scut = สคัท

STRICT LENGTH & CONTENT RULES (NON-NEGOTIABLE):
- Your translation MUST match the length and structure of the source text as closely as possible.
- If the source is a short UI label (e.g. 'ID:', 'Rank', 'Mass'), return ONLY its short Thai equivalent. Do NOT write a full sentence.
- If the source is 1-3 words, return 1-5 words maximum.
- Do NOT expand, elaborate, invent, or add any content that is not explicitly in the source text.
- Do NOT use your knowledge of the game's story or lore to add context or flavor text.
- Do NOT add colons, notes, parentheses, backstory, or any extra characters not present in the source.

Text: {{source_text}}"""

DEFAULT_OPTIONS_PROMPT = f"""You are a Master-Level Video Game Localization Specialist for '{GAME_NAME}', translating the original source language into natural Thai.
Translate this into 3 distinct styles:
1. Literal/Direct (แปลตรงตัว)
2. Casual/Slang (ภาษาพูด/สแลง)
3. Polite/Formal (สุภาพ/ทางการ)
ID: '{{id}}'.

[GLOSSARY TO USE]
- Character A = Name A
- Gamora = กาโมร่า
- Drax = แดร็กซ์
- Rocket = ร็อคเก็ต
- Groot = กรู้ท
- Mantis = แมนทิส
- Milano = ยานมิลาโน่
- Nova Corps = โนวาคอร์ปส
- Lady Hellbender = เลดี้เฮลเบนเดอร์
- Knowhere = โนว์แวร์
- Cosmo = คอสโม่
- Universal Church of Truth = คริสตจักรแห่งสัจธรรมสากล
- Grand Unifier Raker = แกรนด์ยูนิฟายเออร์เรกเกอร์
- Worldmind = เวิลด์มายด์
- Flark = ฟลาร์ก
- Scut = สคัท

Return ONLY a valid JSON array of 3 strings: ["option1", "option2", "option3"]
Text: {{source_text}}"""


MASTERPIECE_SS = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', 'Sarabun', sans-serif;
    font-size: 12px;
}

/* 1. TOP UNIFIED HEADER */
#header_hub {
    background-color: #14141e;
    border-bottom: 1px solid #313244;
    padding: 4px 12px;
}

#brand_badge {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #89b4fa, stop:1 #b4befe);
    color: #11111b;
    font-weight: 900;
    font-size: 13px;
    padding: 3px 8px;
    border-radius: 6px;
}

QMenuBar {
    background-color: transparent;
    color: #a6adc8;
    border: none;
    font-size: 12px;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
    border-radius: 5px;
}
QMenuBar::item:selected {
    background-color: #313244;
    color: #cdd6f4;
}

#breadcrumb_badge, #breadcrumb_btn {
    background-color: #181825;
    color: #89b4fa;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 12px;
    font-weight: 600;
}
#breadcrumb_badge:hover, #breadcrumb_btn:hover {
    background-color: #313244;
    border-color: #89b4fa;
    color: #cdd6f4;
}

#progress_capsule {
    background-color: #11111b;
    border: 1px solid #a6e3a1;
    border-radius: 12px;
    padding: 2px 10px;
}

#btn_quick_save {
    background-color: #a6e3a1;
    color: #11111b;
    font-weight: bold;
    border-radius: 6px;
    padding: 4px 12px;
    border: none;
}
#btn_quick_save:hover {
    background-color: #94e2d5;
}

/* 2. MODE SWITCHER BAR */
#mode_switcher_bar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
    padding: 5px 14px;
}

QPushButton#btn_mode_studio, QPushButton#btn_mode_trun {
    background-color: #313244;
    color: #a6adc8;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 5px 16px;
    font-weight: bold;
    font-size: 12px;
}
QPushButton#btn_mode_studio:checked {
    background-color: #89b4fa;
    color: #11111b;
    border: 1px solid #89b4fa;
}
QPushButton#btn_mode_trun:checked {
    background-color: #a6e3a1;
    color: #11111b;
    border: 1px solid #a6e3a1;
}

/* 3. COLUMN PANELS & CARDS */
.column-panel {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
}

.panel-header-title {
    font-size: 13px;
    font-weight: bold;
    color: #cdd6f4;
}

/* Quick Filter Chips */
QPushButton.filter-chip {
    background-color: #1e1e2e;
    color: #a6adc8;
    border: 1px solid #313244;
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
}
QPushButton.filter-chip:hover {
    background-color: #313244;
    color: #cdd6f4;
}
QPushButton.filter-chip:checked {
    background-color: #89b4fa;
    color: #11111b;
    border-color: #89b4fa;
}

/* Modern Tables */
QTableView, QTableWidget {
    background-color: #181825;
    alternate-background-color: #1e1e2e;
    gridline-color: #313244;
    border: 1px solid #313244;
    border-radius: 6px;
    selection-background-color: #2a2b3d;
    selection-color: #cdd6f4;
}
QHeaderView::section {
    background-color: #14141e;
    color: #a6adc8;
    font-weight: bold;
    border: none;
    border-bottom: 1px solid #313244;
    border-right: 1px solid #313244;
    padding: 6px 8px;
    font-size: 11px;
}

/* Editor Cards */
.editor-card {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
}

QTextEdit {
    background-color: #11111b;
    border: 1px solid #313244;
    border-radius: 6px;
    color: #cdd6f4;
    padding: 8px;
    font-size: 13px;
    line-height: 1.4;
}
QTextEdit:focus {
    border: 1px solid #89b4fa;
}

/* Inputs & Comboboxes */
QLineEdit, QComboBox {
    background-color: #11111b;
    border: 1px solid #313244;
    border-radius: 6px;
    color: #cdd6f4;
    padding: 4px 8px;
    font-size: 12px;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #89b4fa;
}
QComboBox::drop-down {
    border: none;
    width: 18px;
}


/* Enhanced Icon Buttons */
QPushButton.btn-icon {
    padding: 0px;
    font-size: 13px;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
    border-radius: 5px;
    text-align: center;
}

QPushButton.glossary-chip {
    background-color: #181825;
    color: #89b4fa;
    border: 1px solid #313244;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
}
QPushButton.glossary-chip:hover {
    background-color: #313244;
    border-color: #89b4fa;
    color: #cdd6f4;
}

QTableView {
    outline: none;
}

/* Action Buttons */

QPushButton.btn-icon {
    padding: 0px;
    font-size: 12px;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
    text-align: center;
}

QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 5px 12px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #45475a;
    border-color: #585b70;
}
QPushButton:pressed {
    background-color: #1e1e2e;
}

QPushButton.btn-primary {
    background-color: #89b4fa;
    color: #11111b;
    border: 1px solid #89b4fa;
    font-weight: bold;
}
QPushButton.btn-primary:hover {
    background-color: #b4befe;
}

QPushButton.btn-success {
    background-color: #a6e3a1;
    color: #11111b;
    border: 1px solid #a6e3a1;
    font-weight: bold;
}
QPushButton.btn-success:hover {
    background-color: #94e2d5;
}

QPushButton.btn-danger {
    background-color: #f38ba8;
    color: #11111b;
    border: 1px solid #f38ba8;
}
QPushButton.btn-danger:hover {
    background-color: #eba0ac;
}

/* Floating Bulk Bar */
#floating_bulk_bar {
    background-color: #11111b;
    border: 1px solid #89b4fa;
    border-radius: 8px;
    padding: 4px 12px;
}

/* In-Context Glossary Chips */
QPushButton.glossary-chip {
    background-color: #181825;
    color: #cba6f7;
    border: 1px solid #45475a;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: bold;
}
QPushButton.glossary-chip:hover {
    background-color: #cba6f7;
    color: #11111b;
    border-color: #cba6f7;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #181825;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #585b70;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #181825;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #45475a;
    min-width: 20px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #585b70;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""
DARK_SS = MASTERPIECE_SS


# Duplicates removed, now imported from tstudio_ui_shared.py

# =========================================================================
# Decoupled Modules (Item 4: Modular Refactor)
# =========================================================================
from tstudio_dialogs import (
    MergeTranslatedDialog,
    FindReplaceDialog,
    MilitaryTerminologyRetrofitDialog,
    GlossarySweeperDialog,
    ShortcutsCheatsheetDialog
)
from tstudio_delegates import (
    StatusPillDelegate,
    TagIconDelegate,
    HtmlDelegate
)
from tstudio_models import (
    CsvTableModel,
    FilterProxy,
    TransEditorEventFilter,
    SelectionTranslatePill,
    COL_AI_REF,
    reconstruct_lang_file,
    reconstruct_mesg_json_file,
    get_row_tag
)
# =========================================================================

def get_tstudio_icon():
    """Finds and loads the highest-quality TStudio icon (.ico or .png)."""
    tstudio_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(tstudio_dir, "TStudio.ico"),
        os.path.abspath(os.path.join(tstudio_dir, "..", "..", "..", "assets", "TStudio.ico")),
        os.path.join(tstudio_dir, "TStudioLOGO.png"),
        os.path.abspath(os.path.join(tstudio_dir, "..", "..", "..", "assets", "TStudio.png")),
    ]
    if hasattr(sys, '_MEIPASS'):
        candidates = [
            os.path.join(sys._MEIPASS, "assets", "TStudio.ico"),
            os.path.join(sys._MEIPASS, "tools", "flagship", "TStudio", "TStudio.ico"),
            os.path.join(sys._MEIPASS, "assets", "TStudio.png"),
            os.path.join(sys._MEIPASS, "tools", "flagship", "TStudio", "TStudioLOGO.png"),
        ] + candidates

    for p in candidates:
        if p and os.path.exists(p):
            ico = QIcon(p)
            if not ico.isNull():
                return ico
    return QIcon()

class TranslationStudio(QMainWindow):
    def __init__(self, project_path=None, profile_name=None, source_lang=None, target_lang=None, default_mode="studio"):
        super().__init__()
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.tstudio.app.1.0')
            except Exception:
                pass
        self.setWindowTitle(f'Translation Studio — {GAME_NAME}')
        self.resize(1440, 860)
        self.setMinimumSize(1200, 720)
        self.setStyleSheet(MASTERPIECE_SS)

        # Set Window and Taskbar Icon
        app_icon = get_tstudio_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        self.current_source_row = -1
        self.active_row_source_index = -1
        self.current_zoom = 0
        self.current_app_mode = default_mode or "studio"
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(100)
        self._workers = {}
        self.is_auto_save = True
        self.setAcceptDrops(True)

        # --- Live Sync Support ---
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.fileChanged.connect(self.on_external_csv_changed)
        self.last_csv_mtime = 0.0
        self.is_saving_csv = False
        self.csv_path, self.project_dir = self._resolve_initial_file(project_path)
        self.project_path = project_path or self.project_dir
        if self.project_dir:
            TStudioCore.set_project_path(self.project_dir)
        self.csv_encoding = CSV_ENCODING
        self.current_workspace_name = "Default (ค่าเริ่มต้น)"
        self.current_profile_name = "Default"

        # Models
        self.model = CsvTableModel(self)
        self.proxy = FilterProxy(self)
        self.proxy.setDynamicSortFilter(False)
        self.proxy.setSourceModel(self.model)

        # Batch Engine (TRun)
        from trun_batch_dock import TRunBatchDock
        self.batch_dock = TRunBatchDock(self)

        # Docks for backward compatibility with menus and plugins
        self.glossary_dock = QDockWidget(_("glossary_dock_title"), self)
        self.glossary_dock.setObjectName("glossary_dock")
        self.glossary_dock.hide()
        self.tlm_dock = QDockWidget(_("tlm_dock_title"), self)
        self.tlm_dock.setObjectName("tlm_dock")
        self.tlm_dock.hide()
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.tlm_dock)

        # Dummy compatibility docks
        self.dock_main = QDockWidget("Workspace", self)
        self.dock_main.hide()
        self.dock_source = QDockWidget("Source", self)
        self.dock_source.hide()
        self.dock_ai = QDockWidget("AI", self)
        self.dock_ai.hide()
        self.dock_trans = QDockWidget("Translation", self)
        self.dock_trans.hide()

        # Progress bar (compatibility)
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()

        # Load Profiles with Strict Project Isolation
        self._is_loading_profiles = True
        self._profiles_data = TStudioCore.load_profiles()
        self.current_profile_name = self._profiles_data.get("active_preset", "Default")
        if self.project_dir:
            proj_folder = os.path.basename(self.project_dir).strip().lower()
            p_clean = re.sub(r'[^a-zA-Z0-9]', '', proj_folder)
            found_key = None
            for pname in self._profiles_data.get("presets", {}).keys():
                pn_clean = re.sub(r'[^a-zA-Z0-9]', '', pname).lower()
                if pn_clean and (pn_clean == p_clean or pname.lower() == proj_folder or pname.lower().replace(" ", "_") == proj_folder.replace(" ", "_")):
                    found_key = pname
                    break
            if found_key:
                self.current_profile_name = found_key
            else:
                # Resolve proper display profile name from project metadata
                display_prof = os.path.basename(self.project_dir)
                thub_meta = os.path.join(self.project_dir, "thub_project.json")
                if os.path.exists(thub_meta):
                    try:
                        with open(thub_meta, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                        display_prof = meta.get("profile_name") or meta.get("project_name") or display_prof
                    except Exception:
                        pass
                if display_prof not in self._profiles_data.setdefault("presets", {}):
                    self._profiles_data["presets"][display_prof] = {"single": "", "opt": "", "batch": "", "glossary": {}, "max_bytes_limit": 63}
                self.current_profile_name = display_prof
        prof_data = self._profiles_data.get("presets", {}).get(self.current_profile_name, {})
        self.max_bytes_limit = prof_data.get("max_bytes_limit", 0)
        self._glossary_history = []
        self._glossary_redo_stack = []
        self._is_loading_profiles = False
        self._is_syncing_top_models = False

        # Build Masterpiece Central Layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. TOP UNIFIED HEADER BAR
        self._setup_unified_top_bar(main_layout)

        # 2. WORKSPACE MODE SWITCHER BAR
        self._setup_mode_switcher_bar(main_layout)
        self._init_top_universe_tone_combo()

        # 3. WORKSPACE STACK (CAT Studio vs TRun Dedicated Page)
        self.workspace_stack = QStackedWidget(self)

        # Page 0: CAT Studio (Horizontal 3-Column Splitter: Table, Glossary, 3-Tier Segment Stack)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)

        # Column 1: Translation Workspace (~36%)
        self.col1_workspace = self._build_col1_workspace()
        self.main_splitter.addWidget(self.col1_workspace)

        # Column 2: Glossary Window (~32%)
        self.col2_glossary = self._build_col2_glossary()
        self.main_splitter.addWidget(self.col2_glossary)

        # Column 3: 3-Tier Segment Stack (~32%)
        self.col3_editor_stack = self._build_col3_editor_stack()
        self.main_splitter.addWidget(self.col3_editor_stack)

        self.main_splitter.setSizes([500, 470, 470])
        self.workspace_stack.addWidget(self.main_splitter)

        # Page 1: TRun Dedicated Page (Batch AI Runner Full Workspace)
        self.workspace_stack.addWidget(self.batch_dock)

        main_layout.addWidget(self.workspace_stack, 1)

        # Status Bar
        self.statusBar().setStyleSheet("background-color: #11111b; color: #a6adc8; border-top: 1px solid #313244; font-size: 11px; padding: 4px 10px;")
        self.statusBar().showMessage("● พร้อมทำงาน  |  บันทึกอัตโนมัติ: เปิดใช้งาน  |  Ctrl+Enter เพื่อแปลและถัดไป")

        # Shortcuts & Auto-save
        self._init_masterpiece_shortcuts()
        self._csv_auto_save_timer = QTimer(self)
        self._csv_auto_save_timer.setSingleShot(True)
        self._csv_auto_save_timer.timeout.connect(self.silent_save_csv)
        self.model.dataChanged.connect(self.on_model_data_changed)
        
        self._stats_ui_timer = QTimer(self)
        self._stats_ui_timer.setSingleShot(True)
        self._stats_ui_timer.setInterval(60)  # Debounce stats UI updates to 60ms (~16fps)
        self._stats_ui_timer.timeout.connect(self._apply_stats_to_ui)

        self.setup_menu_bar()
        self.update_button_labels()
        self._setup_batch_progress_widget()

        # Load Glossary Data into Column 2
        self._load_glossary_data()

        # Restore modern layout state
        self.restore_layout_state()

        if self.csv_path and os.path.exists(self.csv_path):
            self._load_csv()
        elif project_path and os.path.isfile(project_path):
            if project_path.lower().endswith('.tproj'):
                self.load_project(project_path)
            elif project_path.lower().endswith('.ttarch2'):
                self.open_telltale_archive(project_path)
        else:
            prof = getattr(self, 'current_profile_name', 'Default')
            display_name = os.path.basename(self.project_dir) if getattr(self, 'project_dir', None) else prof
            if hasattr(self, 'btn_breadcrumb'):
                self.btn_breadcrumb.setText(f"📁 {display_name} › (คลิกเพื่อเลือกไฟล์)")
            self.setWindowTitle(f"Translation Studio — {display_name}")
            self.statusBar().showMessage("● พร้อมทำงาน  |  คลิก 📁 เพื่อเปิดไฟล์แปล หรือลากไฟล์มาวางในหน้าต่าง")

        if hasattr(self, 'current_app_mode') and self.current_app_mode != 'studio':
            self.switch_workspace_mode(self.current_app_mode)
        else:
            self._update_mode_buttons_ui()

    def _is_csv_owned_by_profile(self, csv_file, profile_name):
        """Strict verification that a CSV file belongs to the given profile/game project.
        Prevents cross-project contamination and glossary corruption."""
        if not csv_file or not profile_name:
            return False
        p_clean = str(profile_name).strip()
        if not p_clean or p_clean.lower() == 'default':
            return True  # Default profile is unconstrained

        try:
            csv_abs = os.path.normpath(os.path.abspath(csv_file))

            # 1. Check against profile workspace resolved by TStudioCore
            from tstudio_core import TStudioCore
            ws = TStudioCore.get_translation_workspace_dir(profile_name=p_clean, create_if_missing=False)
            if ws and os.path.isdir(ws):
                ws_abs = os.path.normpath(os.path.abspath(ws))
                try:
                    if os.path.commonpath([csv_abs, ws_abs]) == ws_abs:
                        return True
                except Exception:
                    pass
                # Check parent game root
                parent_root = os.path.dirname(ws_abs)
                try:
                    if os.path.commonpath([csv_abs, parent_root]) == parent_root:
                        return True
                except Exception:
                    pass

            # 2. Check against self.project_dir ONLY if self.project_dir matches profile_name
            p_dir = getattr(self, 'project_dir', None)
            if p_dir and os.path.isdir(p_dir):
                pn_clean = re.sub(r'[^a-zA-Z0-9]', '', p_clean).lower()
                p_dir_name = re.sub(r'[^a-zA-Z0-9]', '', os.path.basename(p_dir)).lower()
                if pn_clean and p_dir_name and (pn_clean == p_dir_name or pn_clean in p_dir_name or p_dir_name in pn_clean):
                    p_dir_abs = os.path.normpath(os.path.abspath(p_dir))
                    try:
                        if os.path.commonpath([csv_abs, p_dir_abs]) == p_dir_abs:
                            return True
                    except Exception:
                        pass

            # 3. Check filename vs profile tokens
            pn_clean = re.sub(r'[^a-zA-Z0-9]', '', p_clean).lower()
            f_clean = re.sub(r'[^a-zA-Z0-9]', '', os.path.basename(csv_file)).lower()
            if pn_clean and f_clean and (pn_clean in f_clean or f_clean in pn_clean):
                return True
        except Exception:
            pass

        return False

    def _find_csv_in_project_dir(self, target_dir):
        """Recursively search for the primary translation CSV in target_dir with priority folders."""
        if not target_dir or not os.path.isdir(target_dir):
            return None
        candidate_dirs = [
            os.path.join(target_dir, '02_Translation_Workspace'),
            os.path.join(target_dir, '02_Translation'),
            os.path.join(target_dir, '03_Translated_Text'),
            os.path.join(target_dir, '02_Extracted_Text'),
            target_dir
        ]
        all_found = []
        for d in candidate_dirs:
            if not os.path.isdir(d):
                continue
            for root, dirs, files in os.walk(d):
                dirs[:] = [sub for sub in dirs if not sub.startswith('.') and not any(bad in sub.lower() for bad in ['01_original', 'backup', 'tools', '__pycache__', '07_image', 'releases', 'packed'])]
                for f in files:
                    fl = f.lower()
                    if fl.endswith('.csv') and not fl.endswith('_meta.csv') and not fl.endswith('_backup.csv') and not fl.endswith('.bak') and not fl.endswith('.glossary.csv') and not fl.startswith('~$'):
                        all_found.append(os.path.join(root, f))
            if all_found:
                break
        if not all_found:
            return None
        primary = [c for c in all_found if not c.lower().endswith('_pua.csv') and 'readback' not in c.lower()]
        target_csvs = primary if primary else all_found
        target_csvs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return target_csvs[0]

    def _resolve_initial_file(self, project_path):
        """
        Intelligently resolves the initial CSV file and project directory to load on startup.
        Prioritizes:
        1. Direct file path passed in project_path (.csv)
        2. Primary/latest CSV inside target project directory
        3. (Standalone Only) Active preset's workspace resolved by TStudioCore
        4. (Standalone Only) Recently used origin_file or last_dir from config.json
        5. (Standalone Only) Default fallback CSV_PATH if it exists
        """
        resolved_csv = None
        resolved_project_dir = None

        if project_path:
            p_norm = os.path.normpath(os.path.abspath(str(project_path).strip()))
            if os.path.isfile(p_norm):
                if p_norm.lower().endswith('.csv'):
                    resolved_csv = p_norm
                resolved_project_dir = os.path.normpath(os.path.dirname(p_norm))
            elif os.path.isdir(p_norm):
                resolved_project_dir = p_norm

        # 1. If project_path was provided, search STRICTLY within that project directory!
        # NEVER fall back to foreign projects when a specific project was requested!
        if resolved_project_dir and os.path.isdir(resolved_project_dir):
            if not resolved_csv:
                resolved_csv = self._find_csv_in_project_dir(resolved_project_dir)
            return resolved_csv, resolved_project_dir

        # 2. Standalone launch: check active preset's workspace first
        try:
            from tstudio_core import TStudioCore
            prof_data = TStudioCore.load_profiles()
            active_preset = prof_data.get("active_preset", "Default")
            if active_preset and active_preset.strip().lower() != "default":
                ws_dir = TStudioCore.get_translation_workspace_dir(profile_name=active_preset, create_if_missing=False)
                if ws_dir and os.path.isdir(ws_dir):
                    cand_csv = self._find_csv_in_project_dir(ws_dir)
                    if cand_csv:
                        resolved_csv = cand_csv
                        resolved_project_dir = os.path.dirname(ws_dir) if os.path.basename(ws_dir).lower() in ['02_translation_workspace', '02_translation', '03_translated_text'] else ws_dir
                        return resolved_csv, resolved_project_dir
        except Exception:
            pass

        # 3. Standalone launch: check config.json origin_file or last_dir
        if not resolved_csv:
            cfg = TStudioCore.load_config() if hasattr(TStudioCore, 'load_config') else {}
            if isinstance(cfg, dict):
                orig = cfg.get("origin_file")
                if orig and isinstance(orig, str) and not TStudioCore.is_internal_path(orig):
                    orig_norm = os.path.normpath(orig)
                    if os.path.isfile(orig_norm) and orig_norm.lower().endswith('.csv'):
                        resolved_csv = orig_norm
                if not resolved_csv:
                    last_d = cfg.get("last_dir")
                    if last_d and isinstance(last_d, str) and not TStudioCore.is_internal_path(last_d):
                        last_norm = os.path.normpath(last_d)
                        if os.path.isdir(last_norm):
                            resolved_csv = self._find_csv_in_project_dir(last_norm)

        # 4. Fallback to local default translation.csv if present
        if not resolved_csv and os.path.exists(CSV_PATH):
            resolved_csv = CSV_PATH

        # Infer project_dir from resolved_csv if still missing
        if resolved_csv and not resolved_project_dir:
            p_dir = os.path.normpath(os.path.dirname(resolved_csv))
            for ws_token in ["02_translation_workspace", "03_translated_text", "02_translation", "02_extracted_text"]:
                if ws_token in p_dir.lower():
                    idx = p_dir.lower().find(ws_token)
                    game_dir = p_dir[:idx].rstrip(r"\/")
                    if game_dir and os.path.isdir(game_dir):
                        resolved_project_dir = os.path.normpath(game_dir)
                        break
            if not resolved_project_dir:
                resolved_project_dir = p_dir

        return resolved_csv, resolved_project_dir

    def get_active_translation_workspace(self, hint=None):
        from tstudio_core import TStudioCore
        if hint:
            return TStudioCore.get_translation_workspace_dir(hint_path=hint, profile_name=getattr(self, 'current_profile_name', None))
        prof_name = getattr(self, 'current_profile_name', None)
        if prof_name and prof_name.strip().lower() != 'default':
            ws = TStudioCore.get_translation_workspace_dir(profile_name=prof_name)
            if ws and os.path.basename(ws).lower() == '02_translation_workspace' and os.path.isdir(ws):
                return ws
        hint_val = getattr(self, 'csv_path', None) or getattr(self, 'project_dir', None) or getattr(self, 'project_path', None)
        return TStudioCore.get_translation_workspace_dir(hint_path=hint_val, profile_name=prof_name)

    def _setup_unified_top_bar(self, parent_layout):
        hub = QWidget()
        hub.setObjectName("header_hub")
        hub_layout = QHBoxLayout(hub)
        hub_layout.setContentsMargins(12, 4, 12, 4)
        hub_layout.setSpacing(10)

        # Brand Badge
        lbl_brand = QLabel("TS")
        lbl_brand.setObjectName("brand_badge")
        lbl_title = QLabel("<b>TStudio</b>")
        lbl_title.setStyleSheet("font-size: 14px; color: #cdd6f4; font-weight: bold; margin-right: 4px;")
        hub_layout.addWidget(lbl_brand)
        hub_layout.addWidget(lbl_title)

        # Unified Project & File Tab (Single-click directly opens file chooser dialog)
        display_name = os.path.basename(self.project_dir) if getattr(self, 'project_dir', None) else self.current_profile_name
        initial_file = os.path.basename(self.csv_path) if getattr(self, 'csv_path', None) else "(คลิกเลือกไฟล์)"
        self.btn_breadcrumb = QPushButton(f"📁 {display_name} › {initial_file}")
        self.btn_breadcrumb.setObjectName("breadcrumb_btn")
        self.btn_breadcrumb.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_breadcrumb.setToolTip("คลิกเพื่อเลือกไฟล์/เปิดโปรเจกต์ทันที (Ctrl+O) หรือลากไฟล์มาวางในหน้าต่าง")
        self.btn_breadcrumb.clicked.connect(self.new_project_from_file)
        self.btn_breadcrumb.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.btn_breadcrumb.customContextMenuRequested.connect(self._open_breadcrumb_menu)
        hub_layout.addWidget(self.btn_breadcrumb)

        # Integrated Top Menu Bar
        self.top_menu_bar = QMenuBar(self)
        hub_layout.addWidget(self.top_menu_bar)

        hub_layout.addStretch(1)

        self.translation_channel = TranslationChannelWidget(self)
        hub_layout.addWidget(self.translation_channel)

        # AI Provider Selector (ค่าย AI)
        self.cbo_top_provider = QComboBox()
        self.cbo_top_provider.setObjectName("cbo_top_provider")
        self.cbo_top_provider.setToolTip("เลือกค่าย AI ที่ต้องการใช้งาน")
        self.cbo_top_provider.setStyleSheet("""
            QComboBox#cbo_top_provider {
                background: #11111b;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 3px 8px;
                color: #89b4fa;
                font-weight: bold;
                font-size: 11px;
            }
            QComboBox#cbo_top_provider:hover {
                border-color: #89b4fa;
            }
        """)
        for p in ["DeepSeek", "Google Gemini", "Anthropic Claude", "OpenAI", "OpenRouter", "Local LLM"]:
            self.cbo_top_provider.addItem(p)
        self.cbo_top_provider.currentTextChanged.connect(self._on_top_provider_changed)
        hub_layout.addWidget(self.cbo_top_provider)

        # AI Sub-Model Selector (โมเดลย่อย)
        self.cbo_model = QComboBox()
        self.cbo_model.setObjectName("cbo_top_model")
        self.cbo_model.setToolTip("เลือกโมเดลย่อยของค่ายที่เลือก")
        self.cbo_model.setStyleSheet("""
            QComboBox#cbo_top_model {
                background: #181825;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 3px 8px;
                color: #a6e3a1;
                font-weight: bold;
                font-size: 11px;
            }
            QComboBox#cbo_top_model:hover {
                border-color: #a6e3a1;
            }
        """)
        self.cbo_model.view().setMinimumWidth(340)
        self.cbo_model.currentIndexChanged.connect(self._on_model_selector_changed)
        hub_layout.addWidget(self.cbo_model)

        # AI API Status & Config Capsule Button (Click to open Settings)
        self.btn_api_status = QPushButton()
        self.btn_api_status.setObjectName("btn_top_api_status")
        self.btn_api_status.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_api_status.clicked.connect(self.open_settings)
        hub_layout.addWidget(self.btn_api_status)

        self._sync_top_bar_model_selector()
        self._update_api_status_badge()

        # Single Progress Capsule
        self.lbl_progress_capsule = QLabel("0% (0 / 0)")
        self.lbl_progress_capsule.setObjectName("capsule_progress")
        hub_layout.addWidget(self.lbl_progress_capsule)

        # Quick Save Button
        self.btn_quick_save = QPushButton("💾 บันทึก")
        self.btn_quick_save.setObjectName("quick_save_btn")
        self.btn_quick_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_quick_save.clicked.connect(self.save_csv)
        hub_layout.addWidget(self.btn_quick_save)

        parent_layout.addWidget(hub)

    def _setup_mode_switcher_bar(self, parent_layout):
        mode_container = QWidget()
        mode_container.setObjectName("mode_switcher_hub")
        mode_container.setFixedHeight(34)
        mode_layout = QHBoxLayout(mode_container)
        mode_layout.setContentsMargins(12, 2, 12, 2)
        mode_layout.setSpacing(8)

        lbl_workspace = QLabel("WORKSPACE:")
        lbl_workspace.setStyleSheet("color: #6c7086; font-size: 11px; font-weight: bold; letter-spacing: 0.5px;")
        mode_layout.addWidget(lbl_workspace)

        self.btn_mode_studio = QPushButton("✍️ แปลภาษา (CAT Studio)")
        self.btn_mode_studio.setCheckable(True)
        self.btn_mode_studio.setChecked(True)
        self.btn_mode_studio.setProperty("class", "mode-tab")
        self.btn_mode_studio.setToolTip("โหมดสตูดิโอแปลภาษา สำหรับตรวจสอบและแก้ไขคำแปลทีละบรรทัด (F1)")

        self.btn_mode_trun = QPushButton("⚡ รันแปลอัตโนมัติ (Batch AI Runner)")
        self.btn_mode_trun.setCheckable(True)
        self.btn_mode_trun.setProperty("class", "mode-tab")
        self.btn_mode_trun.setToolTip("โหมดรันแปล AI อัตโนมัติ แปลทั้งไฟล์หรือคิวหลายไฟล์พร้อมกัน (F2)")

        self.mode_btn_group = QButtonGroup(self)
        self.mode_btn_group.addButton(self.btn_mode_studio)
        self.mode_btn_group.addButton(self.btn_mode_trun)

        self.btn_mode_studio.clicked.connect(lambda: self.switch_workspace_mode('studio'))
        self.btn_mode_trun.clicked.connect(lambda: self.switch_workspace_mode('trun'))

        mode_layout.addWidget(self.btn_mode_studio)
        mode_layout.addWidget(self.btn_mode_trun)

        # ── Universe Tone & Easy Mode Controls ──
        mode_layout.addSpacing(10)
        sep_tone = QFrame()
        sep_tone.setFrameShape(QFrame.Shape.VLine)
        sep_tone.setStyleSheet("color: #45475a; max-height: 18px;")
        mode_layout.addWidget(sep_tone)

        lbl_tone = QLabel("🎨 โทนจักรวาล:")
        lbl_tone.setStyleSheet("color: #fab387; font-size: 11px; font-weight: bold;")
        mode_layout.addWidget(lbl_tone)

        self.cbo_top_universe_tone = QComboBox()
        self.cbo_top_universe_tone.setToolTip("เลือกโทนจักรวาลของเกม เพื่อให้ AI เข้าใจบริบท อารมณ์ และสำนวนภาษา")
        self.cbo_top_universe_tone.setStyleSheet("""
            QComboBox {
                background: #181825;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 2px 8px;
                color: #cdd6f4;
                font-size: 11px;
                min-width: 220px;
                max-width: 320px;
            }
            QComboBox:hover {
                border-color: #fab387;
            }
        """)
        self.cbo_top_universe_tone.view().setMinimumWidth(380)
        mode_layout.addWidget(self.cbo_top_universe_tone)

        self.btn_top_detect_tone = QPushButton("🔍 ตรวจเช็คโทน")
        self.btn_top_detect_tone.setToolTip("วิเคราะห์แนวเกมจากโปรเจกต์และบทสนทนา เพื่อเลือกโทนจักรวาลที่เหมาะสมอัตโนมัติ")
        self.btn_top_detect_tone.setStyleSheet("""
            QPushButton {
                background: #313244;
                color: #89b4fa;
                border: 1px solid #45475a;
                border-radius: 5px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #89b4fa;
                color: #11111b;
            }
        """)
        self.btn_top_detect_tone.clicked.connect(self.auto_detect_game_tone_action)
        mode_layout.addWidget(self.btn_top_detect_tone)

        self.btn_top_easy_mode = QPushButton("⚡ Easy Mode")
        self.btn_top_easy_mode.setToolTip("คลิกเดียวครบ! วิเคราะห์เกม, เลือกโทน, ปรับสรรพนาม, ล็อกเพศ 100% และคอมไพล์ AI Prompts พร้อมใช้งานทันที")
        self.btn_top_easy_mode.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fab387, stop:1 #f38ba8);
                color: #11111b;
                border: none;
                border-radius: 5px;
                padding: 3px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.9;
                border: 1px solid #ffffff;
            }
        """)
        self.btn_top_easy_mode.clicked.connect(self.easy_mode_auto_setup_action)
        mode_layout.addWidget(self.btn_top_easy_mode)

        mode_layout.addStretch(1)

        parent_layout.addWidget(mode_container)

    def _init_top_universe_tone_combo(self):
        """Populates the top bar universe tone combo box with categorized options."""
        if not hasattr(self, 'cbo_top_universe_tone'):
            return
        self._is_syncing_top_tone = True
        self.cbo_top_universe_tone.blockSignals(True)
        self.cbo_top_universe_tone.clear()

        for cat_name, tones in UNIVERSE_TONES_BY_CATEGORY.items():
            self.cbo_top_universe_tone.addItem(f"── {cat_name} ──")
            model = self.cbo_top_universe_tone.model()
            item = model.item(self.cbo_top_universe_tone.count() - 1)
            if item:
                item.setEnabled(False)
                f = item.font()
                f.setBold(True)
                item.setFont(f)
            for t in tones:
                self.cbo_top_universe_tone.addItem(t)

        self.cbo_top_universe_tone.blockSignals(False)
        self._is_syncing_top_tone = False
        self.cbo_top_universe_tone.currentTextChanged.connect(self._on_top_universe_tone_changed)

        # Initial sync with active profile
        prof_name = getattr(self, 'current_profile_name', 'Default')
        prof = TStudioCore.get_current_profile_data(prof_name)
        tlm = prof.get("tlm", {})
        if not isinstance(tlm, dict):
            tlm = {"lore_notes": str(tlm)} if tlm else {}
        tone = tlm.get("universe_tone", "")
        self._sync_top_universe_tone(tone)

    def _sync_top_universe_tone(self, tone_text):
        """Synchronizes top bar tone combo with a given tone string."""
        if not hasattr(self, 'cbo_top_universe_tone'):
            return
        self._is_syncing_top_tone = True
        self.cbo_top_universe_tone.blockSignals(True)
        if tone_text:
            idx = self.cbo_top_universe_tone.findText(tone_text)
            if idx >= 0:
                self.cbo_top_universe_tone.setCurrentIndex(idx)
            else:
                self.cbo_top_universe_tone.setEditText(tone_text)
        else:
            gen_idx = self.cbo_top_universe_tone.findText("General / ทั่วไป มาตรฐานสากล (Universal Default)")
            if gen_idx >= 0:
                self.cbo_top_universe_tone.setCurrentIndex(gen_idx)
            else:
                self.cbo_top_universe_tone.setCurrentIndex(1 if self.cbo_top_universe_tone.count() > 1 else 0)
        self.cbo_top_universe_tone.blockSignals(False)
        self._is_syncing_top_tone = False

    def _on_top_universe_tone_changed(self, tone_text):
        """Handles user selecting a universe tone from top bar."""
        if getattr(self, '_is_syncing_top_tone', False) or not tone_text or tone_text.startswith("──"):
            return
        prof_name = getattr(self, 'current_profile_name', 'Default')
        prof = TStudioCore.get_current_profile_data(prof_name)
        if "tlm" not in prof or not isinstance(prof["tlm"], dict):
            prof["tlm"] = {}
        if "tlm_lore" in prof and isinstance(prof["tlm_lore"], dict):
            for k, v in prof.pop("tlm_lore", {}).items():
                if k not in prof["tlm"]:
                    prof["tlm"][k] = v
        prof["tlm"]["universe_tone"] = tone_text.strip()
        TStudioCore.save_profile_data(prof_name, prof)
        self.statusBar().showMessage(f"🎨 บันทึกโทนจักรวาล: {tone_text[:40]}...", 2500)

    def _collect_sample_texts_from_workspace(self, max_samples=100):
        """Collects stratified non-empty dialogue samples from active project table, avoiding UI noise."""
        try:
            if hasattr(self, 'model') and hasattr(self.model, '_data') and self.model._data:
                return collect_stratified_dialogue_samples(self.model._data, max_samples=max_samples)

            if hasattr(self, 'table') and self.table and self.table.model():
                model = self.table.model()
                row_count = model.rowCount()
                raw_rows = []
                for r in range(min(row_count, 600)):
                    idx = model.index(r, 2)
                    txt = model.data(idx, Qt.ItemDataRole.DisplayRole)
                    if txt and str(txt).strip():
                        raw_rows.append(str(txt).strip())
                return collect_stratified_dialogue_samples(raw_rows, max_samples=max_samples)
        except Exception as e:
            print(f"[TStudio] Warning collecting sample texts: {e}")
        return []

    def auto_detect_game_tone_action(self):
        """Auto-detects game genre & tone from project name/game title first, corroborated with dialogue samples and API."""
        self.statusBar().showMessage("🔍 กำลังตรวจวิเคราะห์จักรวาลและโทนเกม (Heuristic + AI Verification)...", 3000)
        samples = self._collect_sample_texts_from_workspace(100)
        file_path = getattr(self, 'csv_path', "") or getattr(self, 'project_dir', "") or getattr(self, 'project_path', "") or ""
        proj_dir = getattr(self, 'project_dir', "") or getattr(self, 'project_path', "") or ""
        if not proj_dir:
            try:
                proj_dir = TStudioCore.get_project_path() or ""
            except Exception:
                proj_dir = ""
        prof_name = getattr(self, 'current_profile_name', "Default")

        res = detect_game_universe_tone_with_api(prof_name, samples, file_path, project_dir=proj_dir)
        self._sync_top_universe_tone(res["tone"])

        # Persist to profile
        prof = TStudioCore.get_current_profile_data(prof_name)
        if "tlm" not in prof or not isinstance(prof["tlm"], dict):
            prof["tlm"] = {}
        if "tlm_lore" in prof and isinstance(prof["tlm_lore"], dict):
            for k, v in prof.pop("tlm_lore", {}).items():
                if k not in prof["tlm"]:
                    prof["tlm"][k] = v
        prof["tlm"]["tone_category"] = res["category"]
        prof["tlm"]["universe_tone"] = res["tone"]
        prof["tlm"]["pronoun_preset"] = res["pronoun"]
        TStudioCore.save_profile_data(prof_name, prof)

        stage_desc = "วิเคราะห์โดย AI ร่วมกับชื่อเกมและบทสนทนา (API-Assisted)" if res.get("stage") == "ai_api" else ("ระยะที่ 1: ตรวจพบจากชื่อโปรเจค/เกมโดยตรง" if res.get("stage") == "project_name" else "ระยะที่ 2: ตรวจพบจากเนื้อหาบทสนทนา")
        detected_name = res.get("inspected_name") or prof_name

        ac_info = res.get("ac_info")
        ac_extra_html = ""
        if ac_info and ac_info.get("is_ac"):
            ac_extra_html = (
                f"<br><br><div style='background: #181825; border-left: 4px solid #f38ba8; padding: 8px 10px; border-radius: 6px;'>"
                f"<b style='color: #f38ba8;'>🦅 ระบบวิเคราะห์ภาคและริยาบท (Assassin's Creed Franchise Engine):</b><br>"
                f"• <b>ภาคที่ตรวจพบ:</b> <span style='color: #a6e3a1; font-weight: bold;'>{ac_info['title']}</span><br>"
                f"• <b>ยุคสมัย/ฉากหลัง:</b> {ac_info['era']}<br>"
                f"• <b>ตัวละครหลัก:</b> <span style='color: #89b4fa; font-weight: bold;'>{ac_info['protagonist']}</span><br>"
                f"• <b>ริยาบทและมิติตัวละคร (Demeanor):</b> <span style='color: #fab387;'>{ac_info['demeanor']}</span><br>"
                f"• <b>มิติเวลา 2 ชั้น (Animus Dual-Layer):</b> ยุคอดีตใน Animus (ข้า-เจ้า / สหาย / ห้ามครับ-ค่ะ) ⚡ ยุคปัจจุบัน (ผม/ฉัน-คุณ)<br>"
                f"• <b>คติพจน์ประจำภาคี:</b> <i>'ไร้สิ่งใดจริงแท้ ทุกสิ่งล้วนทำได้'</i> (Nothing is true, everything is permitted)"
                f"</div>"
            )

        QMessageBox.information(
            self,
            "🔍 ตรวจเช็คโทนเกมอัตโนมัติ",
            f"<b>🎯 สรุปผลการวิเคราะห์จักรวาลและโทนเกม:</b><br><br>"
            f"• <b>ชื่อโปรเจค/เกมที่ตรวจพบ:</b> <span style='color: #89b4fa; font-weight: bold;'>{detected_name}</span> (ที่มา: {res.get('detected_from', 'N/A')})<br>"
            f"• <b>แนวเกม/โทนจักรวาล:</b> {res['tone']}<br>"
            f"• <b>หมวดหมู่:</b> {res['category']}<br>"
            f"• <b>ชุดสรรพนามที่แนะนำ:</b> {res['pronoun']}<br>"
            f"• <b>ระดับความเชื่อมั่น:</b> {res.get('confidence', 'มั่นใจ')} ({stage_desc})<br>"
            f"• <b>หลักฐาน/คีย์เวิร์ดที่พบ:</b> {res['reason']}"
            f"{ac_extra_html}<br><br>"
            f"<i>ระบบได้ปรับเปลี่ยนโทนจักรวาลของโปรไฟล์ '{prof_name}' ให้เรียบร้อยแล้ว</i>"
        )

    def easy_mode_auto_setup_action(self):
        """One-Click Easy Mode: Analyzes game, sets tone, pronouns, locks gender certainty 100%, and compiles AI prompts."""
        self.statusBar().showMessage("⚡ Easy Mode: กำลังวิเคราะห์และตั้งค่าโปรไฟล์อัตโนมัติ...", 3000)
        samples = self._collect_sample_texts_from_workspace(100)
        file_path = getattr(self, 'csv_path', "") or getattr(self, 'project_dir', "") or getattr(self, 'project_path', "") or ""
        proj_dir = getattr(self, 'project_dir', "") or getattr(self, 'project_path', "") or ""
        if not proj_dir:
            try:
                proj_dir = TStudioCore.get_project_path() or ""
            except Exception:
                proj_dir = ""
        prof_name = getattr(self, 'current_profile_name', "Default")

        prof = TStudioCore.get_current_profile_data(prof_name)
        updated_prof, res = apply_easy_mode(prof, prof_name, samples, file_path, project_dir=proj_dir, use_api=True)

        # Save updated profile
        TStudioCore.save_profile_data(prof_name, updated_prof)
        self._sync_top_universe_tone(res["tone"])

        stage_desc = "วิเคราะห์โดย AI ร่วมกับชื่อเกมและบทสนทนา (API-Assisted)" if res.get("stage") == "ai_api" else ("ระยะที่ 1: ตรวจพบจากชื่อโปรเจค/เกมโดยตรง" if res.get("stage") == "project_name" else "ระยะที่ 2: ตรวจพบจากเนื้อหาบทสนทนา")
        detected_name = res.get("inspected_name") or prof_name

        ac_info = res.get("ac_info")
        ac_extra_html = ""
        if ac_info and ac_info.get("is_ac"):
            ac_extra_html = (
                f"<br><br><div style='background: #181825; border-left: 4px solid #f38ba8; padding: 8px 10px; border-radius: 6px;'>"
                f"<b style='color: #f38ba8;'>🦅 ระบบวิเคราะห์ภาคและริยาบท (Assassin's Creed Franchise Engine):</b><br>"
                f"• <b>ภาคที่ตรวจพบ:</b> <span style='color: #a6e3a1; font-weight: bold;'>{ac_info['title']}</span><br>"
                f"• <b>ยุคสมัย/ฉากหลัง:</b> {ac_info['era']}<br>"
                f"• <b>ตัวละครหลัก:</b> <span style='color: #89b4fa; font-weight: bold;'>{ac_info['protagonist']}</span><br>"
                f"• <b>ริยาบทและมิติตัวละคร (Demeanor):</b> <span style='color: #fab387;'>{ac_info['demeanor']}</span><br>"
                f"• <b>มิติเวลา 2 ชั้น (Animus Dual-Layer):</b> ยุคอดีตใน Animus (ข้า-เจ้า / สหาย / ห้ามครับ-ค่ะ) ⚡ ยุคปัจจุบัน (ผม/ฉัน-คุณ)<br>"
                f"• <b>คติพจน์ประจำภาคี:</b> <i>'ไร้สิ่งใดจริงแท้ ทุกสิ่งล้วนทำได้'</i> (Nothing is true, everything is permitted)"
                f"</div>"
            )

        QMessageBox.information(
            self,
            "⚡ Easy Mode - วิเคราะห์และตั้งค่าเสร็จสมบูรณ์",
            f"<b>🚀 Easy Mode ดำเนินการเสร็จสิ้นในคลิกเดียว!</b><br><br>"
            f"• <b>ชื่อโปรเจค/เกมที่ตรวจพบ:</b> <span style='color: #a6e3a1; font-weight: bold;'>{detected_name}</span> (ที่มา: {res.get('detected_from', 'N/A')})<br>"
            f"• <b>แนวเกม/โทนจักรวาล:</b> {res['tone']}<br>"
            f"• <b>ชุดสรรพนามหลัก:</b> {res['pronoun']}<br>"
            f"• <b>ระดับความเชื่อมั่น:</b> {res.get('confidence', 'มั่นใจ')} ({stage_desc})<br>"
            f"• <b>ความปลอดภัยเรื่องเพศ:</b> 🛡️ มั่นใจ 100% ถึงระบุเพศ (ห้ามเดา ครับ/ค่ะ มั่ว)<br>"
            f"• <b>ปรัชญาการแปล:</b> ทับศัพท์ผสมแปลไทย (Hybrid)<br>"
            f"• <b>AI Prompts:</b> ✅ คอมไพล์เข้าโปรไฟล์ '{prof_name}' เรียบร้อยแล้ว พร้อมแปลได้ทันที!<br>"
            f"{ac_extra_html}<br>"
            f"<i>หลักฐานที่พบ: {res['reason']}</i>"
        )

    def _build_col1_workspace(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 8, 6, 8)
        layout.setSpacing(6)

        # Profile Switcher Row
        prof_row = QHBoxLayout()
        lbl_p = QLabel("📁")
        prof_row.addWidget(lbl_p)

        self.cbo_profile = QComboBox()
        self.cbo_profile.setMinimumWidth(140)
        self.cbo_profile.addItems(list(self._profiles_data["presets"].keys()))
        self.cbo_profile.setCurrentText(self.current_profile_name)
        self.cbo_profile.currentTextChanged.connect(self.on_profile_changed)
        prof_row.addWidget(self.cbo_profile, 1)

        btn_new_prof = QPushButton("+")
        btn_new_prof.setProperty("class", "btn-icon")
        btn_new_prof.setStyleSheet("padding:0px; font-size:14px; font-weight:bold;")
        btn_new_prof.setFixedSize(26, 26)
        btn_new_prof.setToolTip("สร้างโปรไฟล์ใหม่")
        btn_new_prof.clicked.connect(self.create_new_profile)
        prof_row.addWidget(btn_new_prof)

        btn_ren_prof = QPushButton("✏️")
        btn_ren_prof.setProperty("class", "btn-icon")
        btn_ren_prof.setStyleSheet("padding:0px; font-size:12px;")
        btn_ren_prof.setFixedSize(26, 26)
        btn_ren_prof.setToolTip("เปลี่ยนชื่อโปรไฟล์")
        btn_ren_prof.clicked.connect(self.rename_profile)
        prof_row.addWidget(btn_ren_prof)

        btn_del_prof = QPushButton("🗑️")
        btn_del_prof.setProperty("class", "btn-icon")
        btn_del_prof.setStyleSheet("padding:0px; font-size:12px;")
        btn_del_prof.setFixedSize(26, 26)
        btn_del_prof.setToolTip("ลบโปรไฟล์")
        btn_del_prof.clicked.connect(self.delete_profile)
        prof_row.addWidget(btn_del_prof)
        layout.addLayout(prof_row)

        # Search & Filter Row
        filter_row = QHBoxLayout()
        search_box_layout = QHBoxLayout()
        search_box_layout.setSpacing(3)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 ค้นหา (กด [=] ตรงเป๊ะๆ เช่น =e, [W] ตรงทั้งคำ หรือสระลอย เช่น \"ำ\", \"่\")...")
        self.search_input.setClearButtonEnabled(True)
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._on_search_timer_timeout)
        self.search_input.textChanged.connect(lambda: self._search_timer.start(250))
        search_box_layout.addWidget(self.search_input, 1)

        search_btn_style = """
            QToolButton {
                background: #181825; color: #a6adc8; border: 1px solid #313244;
                border-radius: 4px; font-weight: bold; font-size: 11px; padding: 2px 5px; min-width: 24px; min-height: 22px;
            }
            QToolButton:hover { background: #313244; color: #cdd6f4; }
            QToolButton:checked {
                background: #89b4fa; color: #11111b; border: 1px solid #89b4fa;
            }
        """

        self.btn_search_case = QToolButton()
        self.btn_search_case.setText("Aa")
        self.btn_search_case.setCheckable(True)
        self.btn_search_case.setToolTip("ตรงตามตัวพิมพ์ใหญ่-เล็ก (Match Case) [Alt+C]\nเปิดใช้งานเพื่อแยกแยะตัวพิมพ์เล็ก-ใหญ่ (เช่น 'e' กับ 'E')")
        self.btn_search_case.setStyleSheet(search_btn_style)
        self.btn_search_case.toggled.connect(self._on_search_mode_toggled)
        search_box_layout.addWidget(self.btn_search_case)

        self.btn_search_word = QToolButton()
        self.btn_search_word.setText("W")
        self.btn_search_word.setCheckable(True)
        self.btn_search_word.setToolTip("ตรงทั้งคำ / สระ-วรรณยุกต์เดี่ยวๆ (Match Whole Word / Lone Marks) [Alt+W]\n- สากล: ค้นหาคำเดี่ยวๆ (เช่น 'e' ไม่ปนกับ 'the', 'enter')\n- ภาษาไทย: ค้นหาสระลอยหรือวรรณยุกต์เดี่ยวๆ (เช่น ' ำ ', ' ่ ', '[่]') โดยไม่ปนกับคำปกติอย่าง 'ทำ' หรือ 'ที่'\n- ไวยากรณ์ด่วน: พิมพ์ \"e\" หรือ \"ำ\" หรือ \"่\" (ใส่เครื่องหมายคำพูด)")
        self.btn_search_word.setStyleSheet(search_btn_style)
        self.btn_search_word.toggled.connect(self._on_search_mode_toggled)
        search_box_layout.addWidget(self.btn_search_word)

        self.btn_search_exact = QToolButton()
        self.btn_search_exact.setText("=")
        self.btn_search_exact.setCheckable(True)
        self.btn_search_exact.setToolTip("ตรงทั้งประโยคเป๊ะๆ (Exact Match) [Alt+E]\nค้นหาเฉพาะแถวที่มีข้อความตรงเป๊ะๆ เช่น 'e' ตัวเดียวล้วนๆ (สามารถพิมพ์ =e ได้เช่นกัน)")
        self.btn_search_exact.setStyleSheet(search_btn_style)
        self.btn_search_exact.toggled.connect(self._on_search_mode_toggled)
        search_box_layout.addWidget(self.btn_search_exact)

        self.btn_search_regex = QToolButton()
        self.btn_search_regex.setText(".*")
        self.btn_search_regex.setCheckable(True)
        self.btn_search_regex.setToolTip("ใช้นิพจน์เรกูลาร์ (Regular Expression) [Alt+R]\nรองรับไวยากรณ์ Regex เช่น ^e$ หรือ \\b[eE]\\b")
        self.btn_search_regex.setStyleSheet(search_btn_style)
        self.btn_search_regex.toggled.connect(self._on_search_mode_toggled)
        search_box_layout.addWidget(self.btn_search_regex)

        filter_row.addLayout(search_box_layout, 2)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            _("filter_all_rows"), _("filter_untranslated"), _("filter_translated"),
            _("filter_ai_hallucinations"), _("filter_quotes_idioms"),
            _("filter_characters"), _("filter_locations"),
            _("filter_skills"), _("filter_items"), _("filter_items_skills"),
            _("filter_quests"), _("filter_system_ui"), _("filter_dialogues"),
            _("filter_mixed_lang"), _("filter_eng_leftovers"), _("filter_cjk_leaks")
        ])
        self.filter_combo.currentIndexChanged.connect(self._on_filter_mode_changed)
        filter_row.addWidget(self.filter_combo, 1)

        self.btn_analyze_file = QPushButton("📊 วิเคราะห์ทั้งไฟล์")
        self.btn_analyze_file.setToolTip("เปิดศูนย์วิเคราะห์อัจฉริยะ (สารบบตัวละคร, ชุดสกิล, ขุดคำศัพท์ Glossary, จับคำแปลขัดแย้ง) [Ctrl+Shift+A]")
        self.btn_analyze_file.setStyleSheet("background-color: #313244; color: #89b4fa; border: 1px solid #45475a; border-radius: 4px; padding: 4px 10px; font-weight: bold;")
        self.btn_analyze_file.clicked.connect(self.open_file_analyzer)
        filter_row.addWidget(self.btn_analyze_file)
        layout.addLayout(filter_row)

        # Quick Filter Chips
        chips_row = QHBoxLayout()
        chips_row.setSpacing(6)
        self.chip_all = QPushButton("ทั้งหมด (0)")
        self.chip_all.setProperty("class", "filter-chip")
        self.chip_all.setCheckable(True)
        self.chip_all.setChecked(True)
        self.chip_all.clicked.connect(lambda: self._set_quick_filter(0))

        self.chip_untrans = QPushButton("รอแปล (0)")
        self.chip_untrans.setProperty("class", "filter-chip")
        self.chip_untrans.setCheckable(True)
        self.chip_untrans.clicked.connect(lambda: self._set_quick_filter(1))

        self.chip_trans = QPushButton("แปลแล้ว (0)")
        self.chip_trans.setProperty("class", "filter-chip")
        self.chip_trans.setCheckable(True)
        self.chip_trans.clicked.connect(lambda: self._set_quick_filter(2))

        self.chip_mixed = QPushButton("🇬🇧 อังกฤษปน (0)")
        self.chip_mixed.setProperty("class", "filter-chip")
        self.chip_mixed.setCheckable(True)
        self.chip_mixed.setToolTip("กรองดูเฉพาะแถวที่มีภาษาอังกฤษปะปนในคำแปล (Mode 13)")
        self.chip_mixed.clicked.connect(lambda: self._set_quick_filter(13))

        self.chip_group = QButtonGroup(self)
        self.chip_group.setExclusive(False)
        self.chip_group.addButton(self.chip_all)
        self.chip_group.addButton(self.chip_untrans)
        self.chip_group.addButton(self.chip_trans)
        self.chip_group.addButton(self.chip_mixed)

        chips_row.addWidget(self.chip_all)
        chips_row.addWidget(self.chip_untrans)
        chips_row.addWidget(self.chip_trans)
        chips_row.addWidget(self.chip_mixed)
        chips_row.addStretch(1)
        layout.addLayout(chips_row)

        # Main Table View
        self.table = QTableView()
        self.table.setAcceptDrops(True)
        self.table.viewport().installEventFilter(self)
        self.table.installEventFilter(self)
        self.table.setModel(self.proxy)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setDefaultSectionSize(26)
        self.table.verticalHeader().setMinimumWidth(40)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_table_context_menu)

        # Delegates
        self.table.setItemDelegateForColumn(0, StatusPillDelegate(self.table))
        self.table.setItemDelegateForColumn(2, HtmlDelegate(self.table))
        self.table.setWordWrap(False)
        self.table.verticalHeader().setDefaultSectionSize(28)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 42)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 65)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(2, 175)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(3, 130)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.table.selectionModel().currentChanged.connect(self.on_row_selected)
        self.table.selectionModel().selectionChanged.connect(self._on_table_selection_changed)

        layout.addWidget(self.table, 1)

        # Floating Multi-Selection Action Bar
        self.floating_bulk_bar = QFrame()
        self.floating_bulk_bar.setStyleSheet("background: #181825; border: 1px solid #89b4fa; border-radius: 6px; padding: 4px;")
        bulk_layout = QHBoxLayout(self.floating_bulk_bar)
        bulk_layout.setContentsMargins(6, 2, 6, 2)
        bulk_layout.setSpacing(8)

        self.lbl_bulk_count = QLabel("● เลือก 0 แถว")
        self.lbl_bulk_count.setStyleSheet("color: #89b4fa; font-weight: bold; font-size: 11px;")
        bulk_layout.addWidget(self.lbl_bulk_count)

        btn_bulk_trans = QPushButton("⚡ แปลทีละบรรทัด (CAT)")
        btn_bulk_trans.setProperty("class", "btn-primary")
        btn_bulk_trans.setStyleSheet("background-color: #89b4fa; color: #11111b; font-weight: bold; border-radius: 4px; padding: 4px 10px; font-size: 11px;")
        btn_bulk_trans.setToolTip("แปลทีละบรรทัดในตารางโดยตรงด้วย AI (CAT Mode)")
        btn_bulk_trans.clicked.connect(lambda: self.retranslate_batch(force_cat=True))
        bulk_layout.addWidget(btn_bulk_trans)

        btn_bulk_trun = QPushButton("🚀 แปล Batch ด้วย TRun")
        btn_bulk_trun.setStyleSheet("background-color: #a6e3a1; color: #11111b; font-weight: bold; border-radius: 4px; padding: 4px 10px; font-size: 11px;")
        btn_bulk_trun.setToolTip("ส่งแถวที่เลือกไปรันแปลแบบ Batch ใน TRun ทันที (ประหยัด Token 80-90% + แปลทีละ 20-50 บรรทัดพร้อมกัน)")
        btn_bulk_trun.clicked.connect(lambda: self.send_selection_to_trun(auto_start=False))
        bulk_layout.addWidget(btn_bulk_trun)

        btn_bulk_cjk = QPushButton("🇨🇳 ล้างจีน")
        btn_bulk_cjk.clicked.connect(self.clean_selected_cjk)
        bulk_layout.addWidget(btn_bulk_cjk)

        btn_bulk_clear = QPushButton("🧹 ลบคำแปล")
        btn_bulk_clear.setToolTip("ลบคำแปลแถวที่เลือกกลับเป็นสถานะ 'รอแปล' (ไม่ลบแถว)")
        btn_bulk_clear.clicked.connect(lambda: self.clear_selected_translations(only_ai=False))
        bulk_layout.addWidget(btn_bulk_clear)

        btn_bulk_del = QPushButton("🗑️ ลบแถว (Shift+Del)")
        btn_bulk_del.setProperty("class", "btn-danger")
        btn_bulk_del.setToolTip("ลบแถวที่เลือกออกจากไฟล์อย่างถาวร")
        btn_bulk_del.clicked.connect(lambda: self.delete_selected_rows(confirm=True))
        bulk_layout.addWidget(btn_bulk_del)

        self.floating_bulk_bar.hide()
        layout.addWidget(self.floating_bulk_bar)

        return container

    def _build_col2_glossary(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(6, 8, 6, 8)
        layout.setSpacing(6)

        # Header: Title + Count + TLM toggle + Settings
        header_row = QHBoxLayout()
        lbl_g_title = QLabel("📖 <b>คลังคำศัพท์</b>"); lbl_g_title.setToolTip("คลังคำศัพท์ (Glossary)")
        lbl_g_title.setStyleSheet("color: #cdd6f4; font-size: 13px;")
        header_row.addWidget(lbl_g_title)

        self.lbl_glossary_count = QLabel("0 คำ")
        self.lbl_glossary_count.setStyleSheet("background: #181825; color: #89b4fa; padding: 2px 6px; border-radius: 10px; font-size: 11px; border: 1px solid #313244;")
        header_row.addWidget(self.lbl_glossary_count)
        header_row.addStretch(1)

        btn_tlm_studio = QPushButton("✨ TLM Studio")
        btn_tlm_studio.setStyleSheet("font-size: 11px; padding: 4px 10px; font-weight: bold; background: #cba6f7; color: #11111b; border-radius: 5px;")
        btn_tlm_studio.setToolTip("เปิด TLM Studio & AI Prompt: บัญญัติศัพท์, จัดการ Lore และตั้งค่า AI Prompts ครบวงจร")
        btn_tlm_studio.clicked.connect(lambda: self.open_tlm_studio(initial_tab=0))
        header_row.addWidget(btn_tlm_studio)
        layout.addLayout(header_row)

        # Search & Filter
        g_filter_row = QHBoxLayout()
        self.txt_g_search = QLineEdit()
        self.txt_g_search.setPlaceholderText("🔍 ค้นหาคำศัพท์...")
        self.txt_g_search.setClearButtonEnabled(True)
        self.txt_g_search.textChanged.connect(self._filter_glossary_table)
        g_filter_row.addWidget(self.txt_g_search, 2)

        self.cbo_g_cat = QComboBox()
        self.cbo_g_cat.addItems(["หมวดหมู่: ทั้งหมด", "บุคคล / ตัวละคร", "สถานที่ / โลก", "ฝ่าย / กิลด์", "อาวุธ / ไอเทม", "ไอเทม / วัตถุดิบ", "ทั่วไป"])
        self.cbo_g_cat.setItemData(0, "All")
        self.cbo_g_cat.setItemData(1, "Person")
        self.cbo_g_cat.setItemData(2, "Location")
        self.cbo_g_cat.setItemData(3, "Faction")
        self.cbo_g_cat.setItemData(4, "Weapon")
        self.cbo_g_cat.setItemData(5, "Item")
        self.cbo_g_cat.setItemData(6, "General")
        self.cbo_g_cat.currentIndexChanged.connect(self._filter_glossary_table)
        g_filter_row.addWidget(self.cbo_g_cat, 1)
        layout.addLayout(g_filter_row)

        # Glossary Table
        self.tbl_glossary = QTableWidget(0, 3)
        self.tbl_glossary.setHorizontalHeaderLabels(["คำต้นฉบับ (EN)", "คำแปลภาษาไทย (TH)", "🏷️"])
        self.tbl_glossary.setItemDelegateForColumn(2, TagIconDelegate(self.tbl_glossary))
        self.tbl_glossary.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_glossary.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tbl_glossary.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.tbl_glossary.setColumnWidth(2, 45)
        self.tbl_glossary.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_glossary.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tbl_glossary.cellDoubleClicked.connect(self._on_glossary_cell_double_clicked)
        self.tbl_glossary.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tbl_glossary.customContextMenuRequested.connect(self._show_glossary_context_menu)
        self.tbl_glossary.verticalHeader().setVisible(False)
        self.tbl_glossary.verticalHeader().setDefaultSectionSize(26)
        self.tbl_glossary.setWordWrap(False)

        # Hook Delete and Backspace key press on the glossary table
        orig_glossary_key_press = self.tbl_glossary.keyPressEvent
        def _glossary_key_press(event):
            if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
                if self.tbl_glossary.state() != QAbstractItemView.State.EditingState:
                    self._delete_selected_glossary_rows()
                    event.accept()
                    return
            orig_glossary_key_press(event)
        self.tbl_glossary.keyPressEvent = _glossary_key_press

        self._glossary_table_save_timer = QTimer(self)
        self._glossary_table_save_timer.setSingleShot(True)
        self._glossary_table_save_timer.timeout.connect(self._auto_save_glossary_from_table)
        self.tbl_glossary.itemChanged.connect(self._on_glossary_table_item_changed)

        layout.addWidget(self.tbl_glossary, 1)

        # ── Toolbar Row 1: จัดการคำศัพท์ (Term Operations) ──
        toolbar_row1 = QHBoxLayout()
        toolbar_row1.setSpacing(4)

        btn_add = QPushButton("➕ เพิ่มคำ")
        btn_add.setToolTip("เพิ่มคำศัพท์ใหม่ลงในคลังโปรไฟล์นี้")
        btn_add.clicked.connect(self._add_glossary_term_dialog)
        toolbar_row1.addWidget(btn_add)

        btn_edit = QPushButton("✏️ แก้ไข")
        btn_edit.setToolTip("แก้ไขคำศัพท์ที่เลือกในตาราง")
        btn_edit.clicked.connect(self._edit_selected_glossary_row)
        toolbar_row1.addWidget(btn_edit)

        btn_del = QPushButton("🗑️ ลบที่เลือก (Del)")
        btn_del.setStyleSheet("QPushButton:hover { background-color: #f38ba8; color: #11111b; }")
        btn_del.setToolTip("ลบคำศัพท์ที่เลือก (สามารถลากคลุมเลือกหลายแถวได้ หรือกดปุ่ม Delete บนคีย์บอร์ด)")
        btn_del.clicked.connect(self._delete_selected_glossary_rows)
        toolbar_row1.addWidget(btn_del)

        btn_undo = QPushButton("↩")
        btn_undo.setProperty("class", "btn-icon")
        btn_undo.setStyleSheet("padding:0px; font-size:12px;")
        btn_undo.setToolTip("เลิกทำ (Undo)")
        btn_undo.setFixedSize(28, 26)
        btn_undo.clicked.connect(self._undo_glossary)
        toolbar_row1.addWidget(btn_undo)

        btn_redo = QPushButton("↪")
        btn_redo.setProperty("class", "btn-icon")
        btn_redo.setStyleSheet("padding:0px; font-size:12px;")
        btn_redo.setToolTip("ทำซ้ำ (Redo)")
        btn_redo.setFixedSize(28, 26)
        btn_redo.clicked.connect(self._redo_glossary)
        toolbar_row1.addWidget(btn_redo)

        layout.addLayout(toolbar_row1)

        # ── Toolbar Row 2: เครื่องมือ AI (AI Intelligence) ──
        toolbar_row2 = QHBoxLayout()
        toolbar_row2.setSpacing(4)

        self.btn_g_retrans = QToolButton()
        self.btn_g_retrans.setText("🔄 แปลคำศัพท์ใหม่ (AI)  ▼")
        self.btn_g_retrans.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_g_retrans.setStyleSheet(
            "QToolButton { background-color: #f9e2af; color: #1e1e2e; font-weight: bold; border-radius: 4px; padding: 4px 8px; min-height: 24px; } "
            "QToolButton:hover { background-color: #f5c2e7; } "
            "QToolButton::menu-button { border: none; width: 14px; }"
        )
        self.btn_g_retrans.setToolTip("แปลคำศัพท์ในคลังด้วย AI (รองรับ 3 ทางเลือก, แปลด่วน, ทับศัพท์, สไตล์พิเศษ, หรือแปลยกชุด)")

        menu_retrans = QMenu(self)
        self.btn_g_retrans.setMenu(menu_retrans)

        def _update_retrans_menu():
            menu_retrans.clear()
            selected_indexes = self.tbl_glossary.selectedIndexes()
            selected_rows = sorted(list(set(idx.row() for idx in selected_indexes)))
            count = len(selected_rows)

            act_opt = menu_retrans.addAction("💡 แปล 3 ทางเลือก (3 Options Picker)...")
            act_opt.triggered.connect(self._retranslate_glossary_options)

            act_quick = menu_retrans.addAction("⚡ แปลด่วนทันที (Quick AI Translation)")
            act_quick.triggered.connect(lambda: self._retranslate_glossary_quick(mode=None))

            if count > 1:
                act_batch = menu_retrans.addAction(f"🌐 แปลคำศัพท์ที่เลือกทั้งหมด ({count} คำ)...")
                act_batch.triggered.connect(lambda: self._retranslate_glossary_batch())
            else:
                act_batch = menu_retrans.addAction("🌐 แปลคำศัพท์เป็นชุด (Batch Translate)...")
                act_batch.triggered.connect(lambda: self._retranslate_glossary_batch())

            menu_retrans.addSeparator()
            menu_styles = menu_retrans.addMenu("🎨 สไตล์ภาษาพิเศษ")
            menu_styles.addAction("🗣️ แปลทับศัพท์ (Transliteration)").triggered.connect(lambda: self._retranslate_glossary_quick("transliterate"))
            menu_styles.addAction("🏰 สไตล์แฟนตาซี / ย้อนยุค (Fantasy)").triggered.connect(lambda: self._retranslate_glossary_quick("fantasy"))
            menu_styles.addAction("👔 สไตล์ทางการ / สุภาพ (Formal)").triggered.connect(lambda: self._retranslate_glossary_quick("formal"))
            menu_styles.addAction("💬 ภาษาพูด / วัยรุ่น (Casual)").triggered.connect(lambda: self._retranslate_glossary_quick("casual"))
            menu_styles.addAction("🤖 ประกาศระบบ / AI (Robotic)").triggered.connect(lambda: self._retranslate_glossary_quick("robotic"))
            menu_styles.addAction("⚡ ดุดัน / แอ็กชัน (Mature)").triggered.connect(lambda: self._retranslate_glossary_quick("mature"))

            menu_retrans.addSeparator()
            act_custom = menu_retrans.addAction("✍️ กำหนด Prompt เอง (Custom Prompt)...")
            act_custom.triggered.connect(self._retranslate_glossary_custom)

        menu_retrans.aboutToShow.connect(_update_retrans_menu)
        _update_retrans_menu()
        toolbar_row2.addWidget(self.btn_g_retrans, 1)

        btn_auto_extract = QPushButton("✨ ดึงศัพท์อัตโนมัติ")
        btn_auto_extract.setStyleSheet("color: #cba6f7; font-weight: bold; padding: 4px 6px; min-height: 24px;")
        btn_auto_extract.setToolTip("ดึงคำศัพท์จากข้อความเกมอัตโนมัติด้วย TLM Studio")
        btn_auto_extract.clicked.connect(self._auto_extract_glossary_action)
        toolbar_row2.addWidget(btn_auto_extract, 1)

        btn_sweep = QPushButton("🧹 กวาดคำทั่วไป")
        btn_sweep.setStyleSheet("color: #fab387; font-weight: bold; padding: 4px 6px; min-height: 24px;")
        btn_sweep.setToolTip("ตรวจหาและกวาดล้างคำศัพท์ทั่วไป, เสียงคราง, แท็กเอนจิน, หรือคำที่ไม่ได้ใช้ในไฟล์เกมออก ให้เหลือเฉพาะชื่อ สถานที่ และศัพท์เฉพาะของเกม")
        btn_sweep.clicked.connect(self._clean_and_audit_glossary_dialog)
        toolbar_row2.addWidget(btn_sweep, 1)

        layout.addLayout(toolbar_row2)

        # ── Toolbar Row 3: โอนย้ายและโปรไฟล์ (Profile & Files) ──
        toolbar_row3 = QHBoxLayout()
        toolbar_row3.setSpacing(4)

        btn_import = QPushButton("📥 นำเข้า")
        btn_import.setToolTip("นำเข้าคำศัพท์จากไฟล์ CSV หรือ JSON")
        btn_import.clicked.connect(self._import_glossary_dialog)
        toolbar_row3.addWidget(btn_import)

        btn_export = QPushButton("📤 ส่งออก")
        btn_export.setToolTip("ส่งออกคลังคำศัพท์เป็นไฟล์ CSV หรือ JSON")
        btn_export.clicked.connect(self._export_glossary_dialog)
        toolbar_row3.addWidget(btn_export)

        btn_save = QPushButton("💾 บันทึกลงโปรไฟล์")
        btn_save.setProperty("class", "btn-primary")
        btn_save.setToolTip("บันทึกคลังคำศัพท์ทั้งหมดลงในโปรไฟล์เกมปัจจุบัน")
        btn_save.clicked.connect(self._save_glossary_profile)
        toolbar_row3.addWidget(btn_save)

        layout.addLayout(toolbar_row3)

        return container

    def _build_col3_editor_stack(self):
        from tstudio_editor import Column3EditorWidget
        self.col3_editor = Column3EditorWidget(self)

        # Backward-compatible attribute aliases
        self.txt_source = self.col3_editor.txt_source
        self.txt_ai = self.col3_editor.txt_ai
        self.txt_ai_ref = self.col3_editor.txt_ai
        self.txt_trans = self.col3_editor.txt_trans
        self.lbl_src_char_count = self.col3_editor.lbl_src_char_count
        self.lbl_trans_char_count = self.col3_editor.lbl_trans_char_count
        self.btn_trans_smart = self.col3_editor.btn_trans_smart
        self.btn_trans_special = self.col3_editor.btn_trans_special
        self.btn_patch_eng = self.col3_editor.btn_patch_eng
        self.btn_retrofit_mil = self.col3_editor.btn_retrofit_mil
        self.btn_polish_cinematic = self.col3_editor.btn_polish_cinematic
        self.btn_clear_trans = self.col3_editor.btn_clear_trans
        self.btn_delete_rows = self.col3_editor.btn_delete_rows
        self.chk_use_tlm = self.col3_editor.chk_use_tlm
        self.chk_guide_mode = self.col3_editor.chk_guide_mode
        self.glossary_chips_box = self.col3_editor.glossary_chips_box
        self.glossary_chips_layout = self.col3_editor.glossary_chips_layout
        self.special_menu = self.col3_editor.special_menu
        self.clear_menu = self.col3_editor.clear_menu
        self._trans_save_timer = self.col3_editor._trans_save_timer
        self.trans_filter = self.col3_editor.trans_filter
        self.ai_cards_container = None
        self.ai_style_cards = []

        if hasattr(self, 'model') and self.model:
            self.model.dataChanged.connect(self._on_table_data_changed)

        return self.col3_editor

    def focus_quick_search(self):
        """Focuses the quick search input box and selects its contents."""
        if hasattr(self, 'search_input') and self.search_input:
            self.search_input.setFocus()
            self.search_input.selectAll()

    def open_shortcuts_cheatsheet(self):
        """Displays the comprehensive keyboard shortcuts cheatsheet."""
        dlg = ShortcutsCheatsheetDialog(self)
        dlg.exec()

    def _init_masterpiece_shortcuts(self):
        self.shortcut_alt_up = QShortcut(QKeySequence("Alt+Up"), self, activated=self.select_prev_row)
        self.shortcut_alt_down = QShortcut(QKeySequence("Alt+Down"), self, activated=self.select_next_row)
        self.shortcut_ctrl_enter = QShortcut(QKeySequence("Ctrl+Return"), self, activated=self.confirm_and_next_row)
        self.shortcut_ctrl_enter2 = QShortcut(QKeySequence("Ctrl+Enter"), self, activated=self.confirm_and_next_row)
        self.shortcut_ctrl_1 = QShortcut(QKeySequence("Ctrl+1"), self, activated=lambda: self._apply_ai_style(0))
        self.shortcut_ctrl_2 = QShortcut(QKeySequence("Ctrl+2"), self, activated=lambda: self._apply_ai_style(1))
        self.shortcut_ctrl_3 = QShortcut(QKeySequence("Ctrl+3"), self, activated=lambda: self._apply_ai_style(2))
        self.shortcut_trans_sel = QShortcut(QKeySequence("Ctrl+Shift+T"), self, activated=self.translate_selected_snippet)
        self.shortcut_translit_sel = QShortcut(QKeySequence("Ctrl+Shift+Y"), self, activated=lambda: self.translate_selected_snippet(mode="transliterate"))
        self.shortcut_patch_eng = QShortcut(QKeySequence("Ctrl+Shift+E"), self, activated=self.patch_selected_english_leaks)
        self.shortcut_retrofit_mil = QShortcut(QKeySequence("Ctrl+Shift+M"), self, activated=self.open_military_retrofit_dialog)
        self.shortcut_polish_cinematic = QShortcut(QKeySequence("Ctrl+Shift+P"), self, activated=self.polish_selected_cinematic)
        
        # Search toggle shortcuts
        self.shortcut_search_case = QShortcut(QKeySequence("Alt+C"), self, activated=lambda: self.btn_search_case.toggle() if hasattr(self, 'btn_search_case') else None)
        self.shortcut_search_word = QShortcut(QKeySequence("Alt+W"), self, activated=lambda: self.btn_search_word.toggle() if hasattr(self, 'btn_search_word') else None)
        self.shortcut_search_exact = QShortcut(QKeySequence("Alt+E"), self, activated=lambda: self.btn_search_exact.toggle() if hasattr(self, 'btn_search_exact') else None)
        self.shortcut_search_regex = QShortcut(QKeySequence("Alt+R"), self, activated=lambda: self.btn_search_regex.toggle() if hasattr(self, 'btn_search_regex') else None)

        # Table management shortcuts scoped strictly to the table widget
        self.shortcut_shift_del = QShortcut(QKeySequence("Shift+Delete"), self.table, activated=lambda: self.delete_selected_rows(confirm=True))
        self.shortcut_shift_del.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.shortcut_del = QShortcut(QKeySequence(Qt.Key.Key_Delete), self.table, activated=self.on_delete_key_pressed)
        self.shortcut_del.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.shortcut_bsp = QShortcut(QKeySequence(Qt.Key.Key_Backspace), self.table, activated=self.clear_selected_translations)
        self.shortcut_bsp.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)

    def _set_quick_filter(self, mode):
        if hasattr(self, 'filter_combo'):
            self.filter_combo.blockSignals(True)
            self.filter_combo.setCurrentIndex(mode)
            self.filter_combo.blockSignals(False)
        self._on_filter_mode_changed(mode)

    def _sync_quick_filter_chips(self, mode):
        if hasattr(self, 'chip_all'):
            self.chip_all.blockSignals(True)
            self.chip_all.setChecked(mode == 0)
            self.chip_all.blockSignals(False)
        if hasattr(self, 'chip_untrans'):
            self.chip_untrans.blockSignals(True)
            self.chip_untrans.setChecked(mode == 1)
            self.chip_untrans.blockSignals(False)
        if hasattr(self, 'chip_trans'):
            self.chip_trans.blockSignals(True)
            self.chip_trans.setChecked(mode == 2)
            self.chip_trans.blockSignals(False)
        if hasattr(self, 'chip_mixed'):
            self.chip_mixed.blockSignals(True)
            self.chip_mixed.setChecked(mode == 13)
            self.chip_mixed.blockSignals(False)

    def _on_filter_mode_changed(self, mode):
        self.proxy.set_filter_mode(mode)
        self._sync_quick_filter_chips(mode)
        if self.proxy.rowCount() > 0:
            self.select_row_by_proxy(0)
        else:
            self.current_source_row = -1
            for w in [self.txt_source, self.txt_ai, self.txt_trans]:
                w.blockSignals(True)
                w.clear()
                w.blockSignals(False)

    def _on_search_mode_toggled(self):
        self._on_search_timer_timeout()

    def _on_search_timer_timeout(self):
        text = self.search_input.text()
        case_val = self.btn_search_case.isChecked() if hasattr(self, 'btn_search_case') else False
        word_val = self.btn_search_word.isChecked() if hasattr(self, 'btn_search_word') else False
        exact_val = self.btn_search_exact.isChecked() if hasattr(self, 'btn_search_exact') else False
        regex_val = self.btn_search_regex.isChecked() if hasattr(self, 'btn_search_regex') else False
        self.proxy.set_search(text, match_case=case_val, match_whole_word=word_val, match_exact=exact_val, match_regex=regex_val)
        if self.proxy.rowCount() > 0:
            self.select_row_by_proxy(0)
        else:
            self.current_source_row = -1
            for w in [self.txt_source, self.txt_ai, self.txt_trans]:
                w.blockSignals(True)
                w.clear()
                w.blockSignals(False)

    def _open_breadcrumb_menu(self, pos=None):
        from PyQt6.QtCore import QPoint
        menu = QMenu(self)
        
        # 1. Project & File Operations
        menu.addAction("📂 เปิดโปรเจกต์ / ไฟล์อื่น... (Ctrl+O)", self.new_project_from_file)
        menu.addAction("💾 บันทึกไฟล์ (Ctrl+S)", self.save_csv)
        menu.addAction("📑 บันทึกเป็น (Save As)... (Ctrl+Shift+S)", self.save_csv_as)
        menu.addSeparator()

        # 2. Deployment & Tools
        menu.addAction("🚀 ติดตั้งเข้าเกม (Deploy) (Ctrl+D)", self.deploy_to_game)
        menu.addAction("🔄 รวมไฟล์แปล (Merge CSV)...", self.open_merge_dialog)

        exp_menu = menu.addMenu("📤 ส่งออกไฟล์เฉพาะทาง (Export)")
        exp_menu.addAction("ส่งออก PUA CSV...", self.export_pua_csv)
        exp_menu.addAction("ส่งออกฟอร์แมตดั้งเดิม (Origin Format)...", self.export_origin_format)

        menu.addSeparator()

        # 3. Profile Submenu
        current_prof = getattr(self, 'current_profile_name', 'Default')
        prof_menu = menu.addMenu(f"👤 สลับโปรไฟล์เกม ({current_prof})")
        presets = self._profiles_data.get("presets", {}) if hasattr(self, '_profiles_data') else {}
        for p_name in sorted(presets.keys()):
            term_count = len(presets[p_name].get("glossary", {})) if isinstance(presets[p_name], dict) else 0
            label = f"✓ {p_name}  ({term_count} คำ)" if p_name == current_prof else f"   {p_name}  ({term_count} คำ)"
            act = prof_menu.addAction(label)
            act.triggered.connect(lambda checked, name=p_name: self.on_profile_changed(name))
            
        prof_menu.addSeparator()
        act_new_p = prof_menu.addAction("➕ สร้างโปรไฟล์ใหม่...")
        act_new_p.triggered.connect(self.create_new_profile)
        act_ren_p = prof_menu.addAction("✏️ เปลี่ยนชื่อโปรไฟล์...")
        act_ren_p.triggered.connect(self.rename_profile)
        act_del_p = prof_menu.addAction("🗑️ ลบโปรไฟล์...")
        act_del_p.triggered.connect(self.delete_profile)
        prof_menu.addSeparator()
        act_mgr_p = prof_menu.addAction("✨ TLM Studio & ตั้งค่า AI Prompt...")
        act_mgr_p.triggered.connect(lambda: self.open_prompt_settings(initial_tab=1))

        menu.addSeparator()
        menu.addAction("🚪 ออกจากโปรแกรม (Exit)", self.close)

        exec_pos = self.btn_breadcrumb.mapToGlobal(pos if pos is not None else QPoint(0, self.btn_breadcrumb.height()))
        menu.exec(exec_pos)

    def _on_top_provider_changed(self, new_provider):
        if not hasattr(self, 'cbo_model') or getattr(self, '_is_syncing_top_models', False):
            return
        self._is_syncing_top_models = True
        try:
            cfg = TStudioCore.load_config()
            cur_m = cfg.get("model", "")
            self.cbo_model.blockSignals(True)
            self.cbo_model.clear()
            submodels = TOP_BAR_SUBMODELS.get(new_provider, [])
            found_idx = -1
            for i, (label, model_id) in enumerate(submodels):
                self.cbo_model.addItem(label, model_id)
                if model_id == cur_m and model_id != "__custom__":
                    found_idx = i

            if found_idx != -1:
                self.cbo_model.setCurrentIndex(found_idx)
            elif cur_m and cur_m != "__custom__":
                matches_provider = (
                    (new_provider == "DeepSeek" and cur_m.startswith("deepseek")) or
                    (new_provider == "Google Gemini" and cur_m.startswith("gemini")) or
                    (new_provider == "Anthropic Claude" and cur_m.startswith("claude")) or
                    (new_provider == "OpenAI" and (cur_m.startswith("gpt") or cur_m.startswith("o1") or cur_m.startswith("o3") or cur_m.startswith("o4") or cur_m.startswith("chatgpt"))) or
                    (new_provider == "OpenRouter" and "/" in cur_m) or
                    (new_provider == "Local LLM" and (cur_m.startswith("qwen") or cur_m.startswith("llama") or cur_m.startswith("qwq") or "local" in cur_m))
                )
                if matches_provider:
                    insert_pos = max(0, self.cbo_model.count() - 1)
                    self.cbo_model.insertItem(insert_pos, f"{cur_m} (กำหนดเอง)", cur_m)
                    self.cbo_model.setCurrentIndex(insert_pos)
                elif submodels:
                    self.cbo_model.setCurrentIndex(0)
            elif submodels:
                self.cbo_model.setCurrentIndex(0)
            self.cbo_model.blockSignals(False)
        finally:
            self._is_syncing_top_models = False
        
        self._on_model_selector_changed(self.cbo_model.currentIndex())

    def _sync_top_bar_model_selector(self):
        if not hasattr(self, 'cbo_model') or not hasattr(self, 'cbo_top_provider'):
            return
        self._is_syncing_top_models = True
        try:
            cfg = TStudioCore.load_config()
            cur_m = cfg.get("model", "deepseek-chat")
            provider = cfg.get("provider", "")
            if not provider or provider not in TOP_BAR_SUBMODELS:
                if "/" in cur_m: provider = "OpenRouter"
                elif cur_m.startswith("gemini"): provider = "Google Gemini"
                elif cur_m.startswith("claude"): provider = "Anthropic Claude"
                elif cur_m.startswith("gpt") or cur_m.startswith("o1") or cur_m.startswith("o3") or cur_m.startswith("o4") or cur_m.startswith("chatgpt"): provider = "OpenAI"
                elif cur_m.startswith("qwen") or cur_m.startswith("llama") or cur_m.startswith("qwq") or cur_m in ("custom-local-llm", "local-llm"): provider = "Local LLM"
                else: provider = "DeepSeek"

            self.cbo_top_provider.blockSignals(True)
            p_idx = self.cbo_top_provider.findText(provider)
            if p_idx != -1:
                self.cbo_top_provider.setCurrentIndex(p_idx)
            self.cbo_top_provider.blockSignals(False)

            self.cbo_model.blockSignals(True)
            self.cbo_model.clear()
            submodels = TOP_BAR_SUBMODELS.get(provider, [])
            found_idx = -1
            for i, (label, model_id) in enumerate(submodels):
                self.cbo_model.addItem(label, model_id)
                if model_id == cur_m and model_id != "__custom__":
                    found_idx = i

            if found_idx != -1:
                self.cbo_model.setCurrentIndex(found_idx)
            else:
                insert_pos = max(0, self.cbo_model.count() - 1)
                self.cbo_model.insertItem(insert_pos, f"{cur_m} (กำหนดเอง)", cur_m)
                self.cbo_model.setCurrentIndex(insert_pos)
            self.cbo_model.blockSignals(False)
        finally:
            self._is_syncing_top_models = False

    def _update_api_status_badge(self):
        if not hasattr(self, 'btn_api_status'):
            return
        cfg = TStudioCore.load_config()
        model = cfg.get("model", "deepseek-chat")
        provider = cfg.get("provider", "")
        if not provider:
            if "/" in model: provider = "OpenRouter"
            elif model.startswith("gemini"): provider = "Google Gemini"
            elif model.startswith("claude"): provider = "Anthropic Claude"
            elif model.startswith("gpt") or model.startswith("o1") or model.startswith("o3") or model.startswith("o4"): provider = "OpenAI"
            elif model.startswith("qwen") or model.startswith("llama") or model.startswith("qwq") or model in ("custom-local-llm", "local-llm"): provider = "Local LLM"
            else: provider = "DeepSeek"

        has_key = False
        if provider == "DeepSeek":
            has_key = bool((cfg.get("deepseek_key") or cfg.get("api_key", "")).strip())
        elif provider == "Google Gemini":
            has_key = bool(cfg.get("google_key", "").strip())
        elif provider == "Anthropic Claude":
            has_key = bool(cfg.get("anthropic_key", "").strip())
        elif provider == "OpenAI":
            has_key = bool(cfg.get("openai_key", "").strip())
        elif provider == "OpenRouter":
            has_key = bool(cfg.get("openrouter_key", "").strip())
        elif provider == "Local LLM":
            has_key = True

        short_prov = provider.replace("Anthropic ", "").replace("Google ", "")
        model_disp = format_model_display_name(model, provider=provider)
        badge_title = f"{short_prov} › {model_disp}"
        if has_key:
            self.btn_api_status.setText(f"🟢 {badge_title} ⚙️")
            self.btn_api_status.setStyleSheet("""
                QPushButton#btn_top_api_status {
                    background: #181825;
                    border: 1px solid #a6e3a1;
                    border-radius: 6px;
                    padding: 3px 9px;
                    color: #a6e3a1;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton#btn_top_api_status:hover {
                    background: #313244;
                    border: 1px solid #89b4fa;
                    color: #cdd6f4;
                }
            """)
        else:
            self.btn_api_status.setText(f"⚠️ {badge_title} (ยังไม่มีคีย์) ⚙️")
            self.btn_api_status.setStyleSheet("""
                QPushButton#btn_top_api_status {
                    background: #2a1818;
                    border: 1px solid #fab387;
                    border-radius: 6px;
                    padding: 3px 9px;
                    color: #fab387;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton#btn_top_api_status:hover {
                    background: #3c2424;
                    border: 1px solid #f38ba8;
                    color: #f38ba8;
                }
            """)

        ds_ok = "🟢 พร้อมใช้งาน" if (cfg.get("deepseek_key") or cfg.get("api_key", "")).strip() else "⚪ ยังไม่ระบุ"
        gem_ok = "🟢 พร้อมใช้งาน" if cfg.get("google_key", "").strip() else "⚪ ยังไม่ระบุ"
        oai_ok = "🟢 พร้อมใช้งาน" if cfg.get("openai_key", "").strip() else "⚪ ยังไม่ระบุ"
        cla_ok = "🟢 พร้อมใช้งาน" if cfg.get("anthropic_key", "").strip() else "⚪ ยังไม่ระบุ"
        or_ok = "🟢 พร้อมใช้งาน" if cfg.get("openrouter_key", "").strip() else "⚪ ยังไม่ระบุ"
        loc_url = cfg.get("local_url") or "http://localhost:1234/v1/chat/completions"

        tooltip = (
            f"<b>⚡ สถานะการเชื่อมต่อ AI APIs:</b><br>"
            f"● <b>โมเดลที่ใช้งาน:</b> {model} ({provider})<br><br>"
            f"<b>🔑 สถานะ API Key แยกตามค่าย:</b><br>"
            f"● <b>DeepSeek:</b> {ds_ok}<br>"
            f"● <b>Google Gemini:</b> {gem_ok}<br>"
            f"● <b>OpenAI:</b> {oai_ok}<br>"
            f"● <b>Anthropic Claude:</b> {cla_ok}<br>"
            f"● <b>OpenRouter:</b> {or_ok}<br>"
            f"● <b>Local LLM:</b> {loc_url}<br><br>"
            f"<i>👉 คลิกปุ่มนี้เพื่อเปิดหน้าต่างตั้งค่า Multi-API Keys</i>"
        )
        self.btn_api_status.setToolTip(tooltip)
        if hasattr(self, 'cbo_model'):
            self.cbo_model.setToolTip(tooltip)
        if hasattr(self, 'cbo_top_provider'):
            self.cbo_top_provider.setToolTip(tooltip)

    def _on_model_selector_changed(self, idx_or_text=0):
        if getattr(self, '_is_syncing_top_models', False):
            return
        if hasattr(self, 'cbo_model') and self.cbo_model.count() > 0:
            chosen = self.cbo_model.currentData() or self.cbo_model.currentText()
            text = self.cbo_model.currentText()
        else:
            chosen = "deepseek-chat"
            text = "deepseek-chat (DeepSeek-V3)"

        # Custom model prompt handling
        if chosen == "__custom__":
            from PyQt6.QtWidgets import QInputDialog
            custom_name, ok = QInputDialog.getText(
                self, "✏️ กำหนดชื่อโมเดลเอง (Custom Model ID)",
                "กรุณาระบุชื่อ Model ID ของโมเดลที่คุณต้องการใช้งาน:\n(เช่น qwen2.5-coder-32b-instruct, gemma-2-27b-it, mistral-large)"
            )
            if ok and custom_name.strip():
                chosen = custom_name.strip()
                text = f"{chosen} (กำหนดเอง)"
                insert_pos = max(0, self.cbo_model.count() - 1)
                self._is_syncing_top_models = True
                try:
                    self.cbo_model.blockSignals(True)
                    self.cbo_model.insertItem(insert_pos, text, chosen)
                    self.cbo_model.setCurrentIndex(insert_pos)
                    self.cbo_model.blockSignals(False)
                finally:
                    self._is_syncing_top_models = False
            else:
                self._is_syncing_top_models = True
                try:
                    self.cbo_model.blockSignals(True)
                    self.cbo_model.setCurrentIndex(0)
                    chosen = self.cbo_model.currentData() or "deepseek-chat"
                    text = self.cbo_model.currentText()
                    self.cbo_model.blockSignals(False)
                finally:
                    self._is_syncing_top_models = False

        provider = self.cbo_top_provider.currentText() if hasattr(self, 'cbo_top_provider') else ""
        if not provider:
            if "/" in chosen: provider = "OpenRouter"
            elif chosen.startswith("gemini"): provider = "Google Gemini"
            elif chosen.startswith("claude"): provider = "Anthropic Claude"
            elif chosen.startswith("gpt") or chosen.startswith("o1") or chosen.startswith("o3") or chosen.startswith("o4") or chosen.startswith("chatgpt"): provider = "OpenAI"
            elif chosen.startswith("qwen") or chosen.startswith("llama") or chosen.startswith("qwq") or chosen in ("custom-local-llm", "local-llm"): provider = "Local LLM"
            else: provider = "DeepSeek"

        try:
            cfg = TStudioCore.load_config()
            cfg["model"] = chosen
            cfg["provider"] = provider
            TStudioCore.save_config(cfg)
            self._update_api_status_badge()
            self.update_button_labels()
            self.statusBar().showMessage(f"● สลับโมเดล AI เป็น: {text} (ค่าย: {provider})", 3000)
        except Exception as e:
            print(f"Error saving model config: {e}")

    # ── Drag & Drop Anywhere to Open Project / File ──
    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if event.type() in (QEvent.Type.DragEnter, QEvent.Type.DragMove):
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
                return True
        elif event.type() == QEvent.Type.Drop:
            if event.mimeData().hasUrls():
                self.dropEvent(event)
                return True
        return super().eventFilter(obj, event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.isLocalFile() for url in urls):
                event.acceptProposedAction()
                self.statusBar().showMessage("📥 ปล่อยไฟล์เพื่อเปิดโปรเจกต์ใน TStudio ทันที...", 3000)
                return
        event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.isLocalFile() for url in urls):
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    path = os.path.normpath(url.toLocalFile())
                    if path and os.path.exists(path):
                        event.acceptProposedAction()
                        self.new_project_from_file(path)
                        return
        event.ignore()

    def _load_glossary_data(self):
        prof_name = getattr(self, 'current_profile_name', None) or (self.cbo_profile.currentText() if hasattr(self, 'cbo_profile') else "Default")
        profile = TStudioCore.get_current_profile_data(prof_name)
        glossary = profile.get("glossary", {}) if isinstance(profile, dict) else {}
        self._populate_glossary_table(glossary)

    def _auto_load_companion_glossary(self):
        """Automatically load companion glossary (<csv_name>.glossary.json or glossary.json)
        when opening a CSV file or project on any computer ('แปลคอมอื่น')."""
        csv_file = getattr(self, 'csv_path', None)
        if not csv_file or not os.path.exists(csv_file):
            return

        try:
            import json
            csv_dir = os.path.dirname(os.path.abspath(csv_file))
            base_no_ext = os.path.splitext(os.path.basename(csv_file))[0]
            candidates = [
                os.path.join(csv_dir, f"{base_no_ext}.glossary.json"),
                os.path.join(csv_dir, "glossary.json")
            ]
            loaded_path = None
            comp_data = None
            for cand in candidates:
                if os.path.exists(cand):
                    with open(cand, 'r', encoding='utf-8') as f:
                        comp_data = json.load(f)
                    if isinstance(comp_data, dict) and comp_data:
                        loaded_path = cand
                        break

            if loaded_path and isinstance(comp_data, dict):
                prof_name = getattr(self, 'current_profile_name', None) or (self.cbo_profile.currentText() if hasattr(self, 'cbo_profile') else "Default")
                if not self._is_csv_owned_by_profile(csv_file, prof_name):
                    print(f"[Ownership Guard] Skipping auto-load companion glossary: '{os.path.basename(csv_file)}' does not belong to profile '{prof_name}'")
                    return

                prof = TStudioCore.get_current_profile_data(prof_name)
                current_glossary = prof.setdefault("glossary", {})
                
                # Merge companion glossary into profile glossary
                merged_count = 0
                for k, v in comp_data.items():
                    term = str(k).strip()
                    if not term: continue
                    if isinstance(v, list):
                        target = str(v[0]).strip() if len(v) > 0 else ""
                        tag = str(v[1]).strip() if len(v) > 1 else "General"
                    else:
                        target = str(v).strip()
                        tag = "General"
                    
                    if term not in current_glossary or current_glossary[term] != [target, tag]:
                        current_glossary[term] = [target, tag]
                        merged_count += 1

                if merged_count > 0:
                    TStudioCore.save_profile_data(prof_name, prof)
                    self._profiles_data = TStudioCore.load_profiles()
                    self._populate_glossary_table(prof["glossary"])
                    self.refresh_glossary_dependent_features()
                    self.statusBar().showMessage(f"● ซิงค์คลังคำศัพท์จาก '{os.path.basename(loaded_path)}' เข้าสู่โปรไฟล์ '{prof_name}' ({len(comp_data)} คำ) สำเร็จ", 4000)
        except Exception as e:
            print(f"[Warning] Failed to auto load companion glossary: {e}")

    def _populate_glossary_table(self, glossary_dict):
        self.tbl_glossary.blockSignals(True)
        try:
            self.tbl_glossary.setRowCount(0)
            if not isinstance(glossary_dict, dict):
                self.lbl_glossary_count.setText("0 คำ")
                return
            for term, val in glossary_dict.items():
                term_str = str(term).strip() if term is not None else ""
                if not term_str: continue
                target = val[0] if (isinstance(val, list) and len(val) > 0) else str(val or "")
                target_str = str(target) if target is not None else ""
                tag = val[1] if (isinstance(val, list) and len(val) > 1) else "General"
                tag_str = str(tag) if tag is not None else "General"
                curr_row = self.tbl_glossary.rowCount()
                self.tbl_glossary.insertRow(curr_row)
                self.tbl_glossary.setItem(curr_row, 0, QTableWidgetItem(term_str))
                self.tbl_glossary.setItem(curr_row, 1, QTableWidgetItem(target_str))
                self.tbl_glossary.setItem(curr_row, 2, QTableWidgetItem(tag_str))
            self.lbl_glossary_count.setText(f"{self.tbl_glossary.rowCount()} คำ")
            self._filter_glossary_table()
        finally:
            self.tbl_glossary.blockSignals(False)

    def _on_glossary_table_item_changed(self, item):
        if hasattr(self, '_glossary_table_save_timer'):
            self._glossary_table_save_timer.start(500)

    def _auto_save_glossary_from_table(self):
        new_glossary = {}
        for r in range(self.tbl_glossary.rowCount()):
            t_item = self.tbl_glossary.item(r, 0)
            tr_item = self.tbl_glossary.item(r, 1)
            tag_item = self.tbl_glossary.item(r, 2)
            if t_item and tr_item and t_item.text().strip():
                new_glossary[t_item.text().strip()] = [
                    tr_item.text().strip(),
                    tag_item.text().strip() if tag_item else "General"
                ]
        self._save_glossary_to_active_profile(new_glossary)
        self.statusBar().showMessage("● บันทึกการแก้ไขคำศัพท์ลงโปรไฟล์อัตโนมัติแล้ว", 2500)

    def _show_glossary_context_menu(self, pos):
        item = self.tbl_glossary.itemAt(pos)
        if not item: return
        row = item.row()

        selected_indexes = self.tbl_glossary.selectedIndexes()
        selected_rows = sorted(list(set(idx.row() for idx in selected_indexes)))
        if row not in selected_rows:
            self.tbl_glossary.selectRow(row)
            selected_rows = [row]

        count = len(selected_rows)
        menu = QMenu(self)

        act_insert = menu.addAction("➕ แทรกคำแปลลงช่องแปล")
        act_insert.triggered.connect(lambda: self._on_glossary_cell_double_clicked(row, 1))

        act_edit = menu.addAction("✏️ แก้ไขคำศัพท์...")
        act_edit.triggered.connect(self._edit_selected_glossary_row)

        menu.addSeparator()

        # AI Re-translate sub-menu
        menu_ai = menu.addMenu("🔄 แปลคำศัพท์ใหม่ (AI)")
        act_opt = menu_ai.addAction("💡 แปล 3 ทางเลือก (3 Options Picker)...")
        act_opt.triggered.connect(self._retranslate_glossary_options)

        act_quick = menu_ai.addAction("⚡ แปลด่วนทันที (Quick AI Translation)")
        act_quick.triggered.connect(lambda: self._retranslate_glossary_quick(mode=None))

        if count > 1:
            act_batch = menu_ai.addAction(f"🌐 แปลคำศัพท์ที่เลือกทั้งหมด ({count} คำ)...")
            act_batch.triggered.connect(lambda: self._retranslate_glossary_batch())
        else:
            act_batch = menu_ai.addAction("🌐 แปลคำศัพท์เป็นชุด (Batch Translate)...")
            act_batch.triggered.connect(lambda: self._retranslate_glossary_batch())

        menu_ai.addSeparator()
        menu_styles = menu_ai.addMenu("🎨 สไตล์ภาษาพิเศษ")
        menu_styles.addAction("🗣️ แปลทับศัพท์ (Transliteration)").triggered.connect(lambda: self._retranslate_glossary_quick("transliterate"))
        menu_styles.addAction("🏰 สไตล์แฟนตาซี / ย้อนยุค (Fantasy)").triggered.connect(lambda: self._retranslate_glossary_quick("fantasy"))
        menu_styles.addAction("👔 สไตล์ทางการ / สุภาพ (Formal)").triggered.connect(lambda: self._retranslate_glossary_quick("formal"))
        menu_styles.addAction("💬 ภาษาพูด / วัยรุ่น (Casual)").triggered.connect(lambda: self._retranslate_glossary_quick("casual"))
        menu_styles.addAction("🤖 ประกาศระบบ / AI (Robotic)").triggered.connect(lambda: self._retranslate_glossary_quick("robotic"))
        menu_styles.addAction("⚡ ดุดัน / แอ็กชัน (Mature)").triggered.connect(lambda: self._retranslate_glossary_quick("mature"))

        menu_ai.addSeparator()
        act_custom = menu_ai.addAction("✍️ กำหนด Prompt เอง (Custom Prompt)...")
        act_custom.triggered.connect(self._retranslate_glossary_custom)

        menu.addSeparator()

        del_label = f"🗑️ ลบคำศัพท์ที่เลือก ({count} คำ) (Del)" if count > 1 else "🗑️ ลบคำศัพท์ที่เลือก (Del)"
        act_del = menu.addAction(del_label)
        act_del.triggered.connect(self._delete_selected_glossary_rows)

        menu.addSeparator()
        act_clean = menu.addAction("🧹 กวาดล้างคำทั่วไปและคำที่ไม่ได้ใช้...")
        act_clean.triggered.connect(self._clean_and_audit_glossary_dialog)

        menu.exec(self.tbl_glossary.mapToGlobal(pos))

    def _filter_glossary_table(self):
        query = self.txt_g_search.text().lower().strip()
        cat = self.cbo_g_cat.currentData()
        for row in range(self.tbl_glossary.rowCount()):
            term_item = self.tbl_glossary.item(row, 0)
            target_item = self.tbl_glossary.item(row, 1)
            tag_item = self.tbl_glossary.item(row, 2)
            term = term_item.text().lower() if term_item else ""
            target = target_item.text().lower() if target_item else ""
            tag = tag_item.text() if tag_item else ""
            match_text = (query in term) or (query in target) if query else True
            match_cat = (cat == "All") or (tag == cat)
            self.tbl_glossary.setRowHidden(row, not (match_text and match_cat))

    def _on_glossary_cell_double_clicked(self, row, col):
        target_item = self.tbl_glossary.item(row, 1) or self.tbl_glossary.item(row, 0)
        if target_item and hasattr(self, 'txt_trans'):
            self.txt_trans.insertPlainText(target_item.text())
            self.txt_trans.setFocus()

    def _save_glossary_to_active_profile(self, glossary_dict=None):
        import copy
        try:
            prof_name = getattr(self, 'current_profile_name', None) or (self.cbo_profile.currentText() if hasattr(self, 'cbo_profile') else "Default")
            prof = TStudioCore.get_current_profile_data(prof_name)
            
            # Save undo snapshot
            current_glossary = copy.deepcopy(prof.get("glossary", {}))
            if not hasattr(self, '_glossary_history'): self._glossary_history = []
            if not hasattr(self, '_glossary_redo_stack'): self._glossary_redo_stack = []
            self._glossary_history.append(current_glossary)
            self._glossary_redo_stack.clear()
            if len(self._glossary_history) > 50:
                self._glossary_history.pop(0)

            if glossary_dict is not None:
                prof["glossary"] = glossary_dict
            else:
                new_glossary = {}
                for r in range(self.tbl_glossary.rowCount()):
                    t_item = self.tbl_glossary.item(r, 0)
                    tr_item = self.tbl_glossary.item(r, 1)
                    tag_item = self.tbl_glossary.item(r, 2)
                    if t_item and tr_item and t_item.text().strip():
                        new_glossary[t_item.text().strip()] = [tr_item.text().strip(), tag_item.text() if tag_item else "General"]
                prof["glossary"] = new_glossary

            TStudioCore.save_profile_data(prof_name, prof)
            self._profiles_data = TStudioCore.load_profiles()

            # Companion export alongside active CSV for cross-computer portability ("แปลคอมอื่น")
            csv_file = getattr(self, 'csv_path', None)
            if csv_file and os.path.exists(csv_file):
                if not self._is_csv_owned_by_profile(csv_file, prof_name):
                    print(f"[Ownership Guard] Skipping companion glossary export: '{os.path.basename(csv_file)}' does not belong to profile '{prof_name}'")
                else:
                    try:
                        csv_dir = os.path.dirname(os.path.abspath(csv_file))
                        base_no_ext = os.path.splitext(os.path.basename(csv_file))[0]
                        companion_path = os.path.join(csv_dir, f"{base_no_ext}.glossary.json")
                        with open(companion_path, 'w', encoding='utf-8') as gf:
                            json.dump(prof["glossary"], gf, ensure_ascii=False, indent=2)
                    except Exception as e:
                        print(f"[Warning] Failed to write companion glossary: {e}")

            if hasattr(self, '_glossary_table_save_timer') and self._glossary_table_save_timer.isActive():
                self._glossary_table_save_timer.stop()

            self._populate_glossary_table(prof["glossary"])
            self.refresh_glossary_dependent_features()
            return prof.get("glossary", {})
        except Exception as e:
            print(f"[Error] _save_glossary_to_active_profile failed: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _add_glossary_term_dialog(self):
        from PyQt6.QtWidgets import QInputDialog
        prof_name = getattr(self, 'current_profile_name', 'Default')
        term, ok1 = QInputDialog.getText(self, f"เพิ่มคำศัพท์ใหม่ [{prof_name}]", "คำต้นฉบับ (EN):")
        if ok1 and term and term.strip():
            term = term.strip()
            target, ok2 = QInputDialog.getText(self, f"เพิ่มคำศัพท์ใหม่ [{prof_name}]", f"คำแปลภาษาไทยสำหรับ '{term}':")
            if ok2 and target and target.strip():
                target = target.strip()
                cat, ok3 = QInputDialog.getItem(self, "หมวดหมู่คำศัพท์", "เลือกหมวดหมู่:", 
                                               ["Person", "Location", "Faction", "Weapon", "Item", "General"], 5, False)
                if ok3 and cat:
                    prof = TStudioCore.get_current_profile_data(prof_name)
                    glossary = prof.get("glossary", {})
                    glossary[term] = [target, cat]
                    self._save_glossary_to_active_profile(glossary)
                    self.statusBar().showMessage(f"● เพิ่มคำศัพท์ '{term}' ลงในโปรไฟล์ '{prof_name}' สำเร็จ", 3000)

    def _edit_selected_glossary_row(self):
        cur_row = self.tbl_glossary.currentRow()
        if cur_row < 0:
            QMessageBox.information(self, "แก้ไขคำศัพท์", "กรุณาเลือกแถวคำศัพท์ที่ต้องการแก้ไขในตารางก่อน")
            return
        t_item = self.tbl_glossary.item(cur_row, 0)
        tr_item = self.tbl_glossary.item(cur_row, 1)
        tag_item = self.tbl_glossary.item(cur_row, 2)
        old_term = t_item.text().strip() if t_item else ""
        old_trans = tr_item.text().strip() if tr_item else ""
        old_cat = tag_item.text().strip() if tag_item else "General"
        prof_name = getattr(self, 'current_profile_name', 'Default')

        from PyQt6.QtWidgets import QInputDialog
        new_term, ok1 = QInputDialog.getText(self, f"แก้ไขคำศัพท์ [{prof_name}]", "คำต้นฉบับ (EN):", text=old_term)
        if ok1 and new_term and new_term.strip():
            new_term = new_term.strip()
            new_trans, ok2 = QInputDialog.getText(self, f"แก้ไขคำศัพท์ [{prof_name}]", f"คำแปลภาษาไทยสำหรับ '{new_term}':", text=old_trans)
            if ok2 and new_trans and new_trans.strip():
                new_trans = new_trans.strip()
                cat_options = ["Person", "Location", "Faction", "Weapon", "Item", "General"]
                default_idx = cat_options.index(old_cat) if old_cat in cat_options else 5
                cat, ok3 = QInputDialog.getItem(self, "หมวดหมู่คำศัพท์", "เลือกหมวดหมู่:", cat_options, default_idx, False)
                if ok3 and cat:
                    prof = TStudioCore.get_current_profile_data(prof_name)
                    glossary = prof.get("glossary", {})
                    if old_term in glossary and old_term != new_term:
                        del glossary[old_term]
                    glossary[new_term] = [new_trans, cat]
                    self._save_glossary_to_active_profile(glossary)
                    self.statusBar().showMessage(f"● แก้ไขคำศัพท์ '{new_term}' ในโปรไฟล์ '{prof_name}' สำเร็จ", 3000)

                    # Prompt to batch-update existing translated rows that contain the old translation
                    if old_trans and old_trans != new_trans and hasattr(self, 'model') and self.model and self.model._data:
                        matching_rows = []
                        for idx, r_item in enumerate(self.model._data):
                            tr_t = str(r_item.get("trans") or "")
                            if old_trans in tr_t:
                                matching_rows.append(idx)
                        
                        if matching_rows:
                            reply = QMessageBox.question(
                                self,
                                "อัปเดตคำแปลในไฟล์",
                                f"พบแถวที่แปลไปแล้วจำนวน {len(matching_rows)} แถว ที่มีคำแปลเดิม ('{old_trans}')\n"
                                f"ต้องการแทนที่ด้วยคำแปลใหม่ ('{new_trans}') อัตโนมัติทั้งหมดหรือไม่?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                            )
                            if reply == QMessageBox.StandardButton.Yes:
                                for idx in matching_rows:
                                    r_item = self.model._data[idx]
                                    cur_tr = str(r_item.get("trans") or "")
                                    r_item["trans"] = cur_tr.replace(old_trans, new_trans)
                                self.model.is_dirty = True
                                self.model.layoutChanged.emit()
                                self.update_progress_stats()
                                self.statusBar().showMessage(f"● อัปเดตคำแปล '{old_trans}' ➔ '{new_trans}' ใน {len(matching_rows)} แถวเรียบร้อยแล้ว", 4000)

    def _get_selected_glossary_terms(self):
        selected_indexes = self.tbl_glossary.selectedIndexes()
        selected_rows = sorted(list(set(idx.row() for idx in selected_indexes)))
        if not selected_rows:
            cur = self.tbl_glossary.currentRow()
            if cur >= 0:
                selected_rows = [cur]
        
        items = []
        for r in selected_rows:
            t_item = self.tbl_glossary.item(r, 0)
            tr_item = self.tbl_glossary.item(r, 1)
            tag_item = self.tbl_glossary.item(r, 2)
            if t_item and t_item.text().strip():
                items.append((
                    r,
                    t_item.text().strip(),
                    tr_item.text().strip() if tr_item else "",
                    tag_item.text().strip() if tag_item else "General"
                ))
        return items

    def _delete_selected_glossary_rows(self):
        if getattr(self, '_is_deleting_glossary_row', False):
            return
        self._is_deleting_glossary_row = True
        try:
            selected_indexes = self.tbl_glossary.selectedIndexes()
            selected_rows = sorted(list(set(idx.row() for idx in selected_indexes)))
            if not selected_rows:
                cur_row = self.tbl_glossary.currentRow()
                if cur_row >= 0:
                    selected_rows = [cur_row]

            if not selected_rows:
                QMessageBox.information(self, "ลบคำศัพท์", "กรุณาเลือกแถวคำศัพท์ที่ต้องการลบในตารางก่อน")
                return

            terms_to_delete = []
            for r in selected_rows:
                term_item = self.tbl_glossary.item(r, 0)
                if term_item and term_item.text().strip():
                    t = term_item.text().strip()
                    if t not in terms_to_delete:
                        terms_to_delete.append(t)

            if not terms_to_delete:
                return

            prof_name = getattr(self, 'current_profile_name', 'Default')
            if len(terms_to_delete) == 1:
                msg = f"ต้องการลบคำศัพท์ '{terms_to_delete[0]}' ออกจากโปรไฟล์ '{prof_name}' ใช่หรือไม่?"
            else:
                sample = ", ".join(f"'{t}'" for t in terms_to_delete[:3])
                if len(terms_to_delete) > 3:
                    sample += f" ... และอีก {len(terms_to_delete) - 3} คำ"
                msg = f"ต้องการลบคำศัพท์ที่เลือกทั้งหมดจำนวน {len(terms_to_delete)} คำ ({sample})\nออกจากโปรไฟล์ '{prof_name}' ใช่หรือไม่?"

            reply = QMessageBox.question(
                self,
                "ยืนยันการลบคำศัพท์",
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            prof = TStudioCore.get_current_profile_data(prof_name)
            glossary = prof.get("glossary", {})
            deleted_count = 0
            for t in terms_to_delete:
                if t in glossary:
                    del glossary[t]
                    deleted_count += 1

            self._save_glossary_to_active_profile(glossary)
            self.statusBar().showMessage(f"● ลบคำศัพท์ {deleted_count} คำ ออกจากโปรไฟล์ '{prof_name}' เรียบร้อยแล้ว (กด ↩ เพื่อเลิกทำได้)", 3500)
        finally:
            self._is_deleting_glossary_row = False

    # Alias for single-row call compatibility
    def _delete_selected_glossary_row(self):
        self._delete_selected_glossary_rows()

    def _clean_and_audit_glossary_dialog(self):
        """Opens the Intelligent Glossary Sweeper & Lore Protector Dialog."""
        prof_name = getattr(self, 'current_profile_name', 'Default')
        prof = TStudioCore.get_current_profile_data(prof_name)
        glossary = prof.get("glossary", {})
        if not glossary or not isinstance(glossary, dict):
            QMessageBox.information(self, "คลังคำศัพท์ว่างเปล่า", f"โปรไฟล์ '{prof_name}' ยังไม่มีคำศัพท์ในคลัง")
            return
        dlg = GlossarySweeperDialog(self)
        dlg.exec()

    def _retranslate_glossary_options(self):
        items = self._get_selected_glossary_terms()
        if not items:
            QMessageBox.information(self, "แปลคำศัพท์ด้วย AI", "กรุณาเลือกคำศัพท์ในตารางก่อน")
            return
        row, term, old_trans, tag = items[0]
        cfg = TStudioCore.load_config()
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        self.statusBar().showMessage(f"💡 กำลังดึงตัวเลือกคำแปล 3 สไตล์สำหรับ '{term}' จาก AI...")

        prompt = (
            f"You are a professional video game localization expert.\n"
            f"Provide 3 different Thai translation options for the video game glossary term: '{term}'.\n"
            f"Output ONLY a JSON array of strings containing the 3 options. No markdown formatting."
        )

        def on_success(reply):
            options = TStudioCore.extract_translation_options(reply)
            if not options:
                QMessageBox.warning(self, "ข้อผิดพลาด", f"AI ส่งผลลัพธ์กลับมาไม่ถูกต้อง:\n{reply}")
                return
            dlg = TranslationOptionsDialog(self, options)
            if dlg.exec() and dlg.selected_text:
                chosen = dlg.selected_text.strip()
                prof_name = getattr(self, 'current_profile_name', 'Default')
                prof = TStudioCore.get_current_profile_data(prof_name)
                glossary = prof.get("glossary", {})
                curr = glossary.get(term, ["", "General"])
                tag_val = curr[1] if isinstance(curr, list) and len(curr) > 1 else tag
                glossary[term] = [chosen, tag_val]
                self._save_glossary_to_active_profile(glossary)
                self.statusBar().showMessage(f"● ปรับปรุงคำแปล '{term}' -> '{chosen}' สำเร็จ", 3500)

        def on_error(err):
            QMessageBox.critical(self, "การแปลล้มเหลว", f"เกิดข้อผิดพลาดในการเชื่อมต่อ AI:\n{err}")
            self.statusBar().showMessage("❌ การแปลคำศัพท์ล้มเหลว", 3000)

        worker = ApiWorker(CoreAI.generate_content, cfg, prompt, is_local=is_local)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _retranslate_glossary_quick(self, mode=None):
        items = self._get_selected_glossary_terms()
        if not items:
            QMessageBox.information(self, "แปลคำศัพท์ด้วย AI", "กรุณาเลือกคำศัพท์ในตารางก่อน")
            return

        if len(items) > 1:
            self._retranslate_glossary_batch(mode=mode)
            return

        row, term, old_trans, tag = items[0]
        cfg = TStudioCore.load_config()
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        self.statusBar().showMessage(f"⚡ กำลังแปลคำศัพท์ '{term}' ด้วย AI...")

        mode_text = ""
        if mode == "transliterate":
            mode_text = "TRANSLITERATE (แปลทับศัพท์) the English term into natural Thai pronunciation without translating its meaning."
        elif mode == "fantasy":
            mode_text = "Translate using fantasy, medieval, or archaic Thai vocabulary suitable for RPG lore/fantasy games."
        elif mode == "formal":
            mode_text = "Translate into polite, official, and formal Thai terminology."
        elif mode == "casual":
            mode_text = "Translate into natural, modern, casual Thai language."
        elif mode == "robotic":
            mode_text = "Translate into cold, systemic, robotic terminology."
        elif mode == "mature":
            mode_text = "Translate aggressively using gritty action vocabulary."
        else:
            mode_text = "Translate the video game glossary term into accurate, natural Thai."

        prompt = (
            f"You are a professional video game localization expert.\n"
            f"{mode_text}\n\n"
            f"Glossary Term: '{term}'\n\n"
            f"Output ONLY the translated Thai term without quotes, punctuation, or any explanation."
        )

        def on_success(res):
            import re
            clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)
            clean_res = re.sub(r'^["\']|["\']$', '', clean_res).strip()
            if not clean_res:
                return
            prof_name = getattr(self, 'current_profile_name', 'Default')
            prof = TStudioCore.get_current_profile_data(prof_name)
            glossary = prof.get("glossary", {})
            curr = glossary.get(term, ["", "General"])
            tag_val = curr[1] if isinstance(curr, list) and len(curr) > 1 else tag
            glossary[term] = [clean_res, tag_val]
            self._save_glossary_to_active_profile(glossary)
            self.statusBar().showMessage(f"● แปลคำศัพท์ '{term}' -> '{clean_res}' สำเร็จ", 3500)

        def on_error(err):
            QMessageBox.critical(self, "การแปลล้มเหลว", f"เกิดข้อผิดพลาดในการแปลคำศัพท์:\n{err}")
            self.statusBar().showMessage("❌ การแปลคำศัพท์ล้มเหลว", 3000)

        worker = ApiWorker(CoreAI.generate_content, cfg, prompt, is_local=is_local)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _retranslate_glossary_batch(self, mode=None):
        items = self._get_selected_glossary_terms()
        if not items:
            QMessageBox.information(self, "แปลคำศัพท์เป็นชุด", "กรุณาเลือกคำศัพท์ในตารางที่ต้องการแปลก่อน")
            return
        
        prof_name = getattr(self, 'current_profile_name', 'Default')
        reply = QMessageBox.question(
            self,
            "ยืนยันการแปลคำศัพท์เป็นชุด",
            f"ต้องการใช้ AI แปลคำศัพท์ที่เลือกจำนวน {len(items)} คำ ทั้งหมดใช่หรือไม่?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        cfg = TStudioCore.load_config()
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        self.statusBar().showMessage(f"⏳ กำลังแปลคำศัพท์ {len(items)} คำ ด้วย AI ในเบื้องหลัง...")

        terms_list = [it[1] for it in items]
        terms_json = json.dumps(terms_list, ensure_ascii=False)
        
        style_note = ""
        if mode == "transliterate":
            style_note = "TRANSLITERATE all terms into natural Thai pronunciation without translating meaning."
        elif mode == "fantasy":
            style_note = "Use archaic, fantasy, or medieval Thai terms appropriate for fantasy games."
        elif mode == "formal":
            style_note = "Use polite, formal Thai terms."
        elif mode == "casual":
            style_note = "Use natural, casual Thai language."
        elif mode == "robotic":
            style_note = "Use systemic, robotic terminology."
        elif mode == "mature":
            style_note = "Use gritty, action-styled Thai terms."

        prompt = (
            f"You are a professional video game localization expert.\n"
            f"{style_note}\n"
            f"Translate each of the following video game glossary terms into Thai:\n"
            f"{terms_json}\n\n"
            f"CRITICAL INSTRUCTIONS:\n"
            f"- Output ONLY a valid JSON object mapping each English term to its Thai translation.\n"
            f"- Example format: {{\"Sword\": \"ดาบ\", \"Shield\": \"โล่\"}}\n"
            f"- Do not include markdown codeblocks or any additional explanation."
        )

        def on_success(res):
            import re
            clean_match = re.search(r'\{.*\}', res, re.DOTALL)
            trans_dict = {}
            if clean_match:
                try:
                    trans_dict = json.loads(clean_match.group(0))
                except Exception:
                    pass
            if not trans_dict:
                clean_raw = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)
                try:
                    trans_dict = json.loads(clean_raw)
                except Exception as e:
                    QMessageBox.warning(self, "ข้อผิดพลาด", f"ไม่สามารถแยกข้อมูลคำแปลจาก AI ได้:\n{e}\n\n{res[:200]}")
                    return

            prof = TStudioCore.get_current_profile_data(prof_name)
            glossary = prof.get("glossary", {})
            lower_map = {str(k).lower(): str(v) for k, v in trans_dict.items()}
            updated_count = 0
            for it in items:
                orig_t = it[1]
                val = trans_dict.get(orig_t) or lower_map.get(orig_t.lower())
                if val and isinstance(val, str) and val.strip():
                    curr = glossary.get(orig_t, ["", it[3]])
                    tag = curr[1] if isinstance(curr, list) and len(curr) > 1 else it[3]
                    glossary[orig_t] = [val.strip(), tag]
                    updated_count += 1

            self._save_glossary_to_active_profile(glossary)
            self.statusBar().showMessage(f"● แปลคำศัพท์สำเร็จ {updated_count} คำ ในโปรไฟล์ '{prof_name}'", 4000)

        def on_error(err):
            QMessageBox.critical(self, "การแปลล้มเหลว", f"เกิดข้อผิดพลาดในการแปลคำศัพท์:\n{err}")
            self.statusBar().showMessage("❌ การแปลคำศัพท์ล้มเหลว", 3000)

        worker = ApiWorker(CoreAI.generate_content, cfg, prompt, is_local=is_local)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _retranslate_glossary_custom(self):
        items = self._get_selected_glossary_terms()
        if not items:
            QMessageBox.information(self, "แปลคำศัพท์ด้วย AI", "กรุณาเลือกคำศัพท์ในตารางก่อน")
            return
        row, term, old_trans, tag = items[0]
        from PyQt6.QtWidgets import QInputDialog
        custom_prompt, ok = QInputDialog.getMultiLineText(
            self,
            "กำหนด Prompt แปลคำศัพท์",
            "ระบุ Prompt สำหรับแปลคำศัพท์ (ใช้ {term} แทนคำศัพท์):",
            f"แปลคำศัพท์เกม: '{term}' เป็นภาษาไทย ให้กระชับ สละสลวย ตรงบริบทเกม ตอบเฉพาะคำแปลภาษาไทยเท่านั้น"
        )
        if not ok or not custom_prompt.strip():
            return
        
        cfg = TStudioCore.load_config()
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        self.statusBar().showMessage(f"⚡ กำลังแปลคำศัพท์ '{term}' ด้วย Custom Prompt...")

        prompt = custom_prompt.replace('{term}', term)

        def on_success(res):
            import re
            clean_res = re.sub(r'^```[^\n]*\n?|\n?```$', '', res.strip(), flags=re.MULTILINE)
            clean_res = re.sub(r'^["\']|["\']$', '', clean_res).strip()
            if not clean_res:
                return
            prof_name = getattr(self, 'current_profile_name', 'Default')
            prof = TStudioCore.get_current_profile_data(prof_name)
            glossary = prof.get("glossary", {})
            curr = glossary.get(term, ["", "General"])
            tag_val = curr[1] if isinstance(curr, list) and len(curr) > 1 else tag
            glossary[term] = [clean_res, tag_val]
            self._save_glossary_to_active_profile(glossary)
            self.statusBar().showMessage(f"● แปลคำศัพท์ '{term}' -> '{clean_res}' สำเร็จ", 3500)

        def on_error(err):
            QMessageBox.critical(self, "การแปลล้มเหลว", f"เกิดข้อผิดพลาดในการแปลคำศัพท์:\n{err}")
            self.statusBar().showMessage("❌ การแปลคำศัพท์ล้มเหลว", 3000)

        worker = ApiWorker(CoreAI.generate_content, cfg, prompt, is_local=is_local)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _save_glossary_profile(self):
        prof_name = getattr(self, 'current_profile_name', 'Default')
        saved_glossary = self._save_glossary_to_active_profile()
        QMessageBox.information(self, "บันทึกโปรไฟล์", f"บันทึกคลังคำศัพท์ {len(saved_glossary)} คำ ลงในโปรไฟล์เกม '{prof_name}' เรียบร้อยแล้ว!")

    def _auto_extract_glossary_action(self):
        self.toggle_tlm_dock()

    def _undo_glossary(self):
        if not hasattr(self, '_glossary_history') or not self._glossary_history:
            self.statusBar().showMessage("ไม่มีประวัติคำศัพท์ให้เลิกทำ", 2000)
            return
        import copy
        prof_name = getattr(self, 'current_profile_name', "Default")
        prof = TStudioCore.get_current_profile_data(prof_name)
        if not hasattr(self, '_glossary_redo_stack'): self._glossary_redo_stack = []
        self._glossary_redo_stack.append(copy.deepcopy(prof.get("glossary", {})))
        prev_glossary = self._glossary_history.pop()
        prof["glossary"] = prev_glossary
        TStudioCore.save_profile_data(prof_name, prof)
        self._populate_glossary_table(prev_glossary)
        self.refresh_glossary_dependent_features()
        if hasattr(self, 'current_source_row') and self.current_source_row >= 0:
            self.select_source_row(self.current_source_row)
        self.statusBar().showMessage(f"↩ เลิกทำคำศัพท์สำเร็จ (เหลือ {len(prev_glossary)} คำ)", 2500)

    def _redo_glossary(self):
        if not hasattr(self, '_glossary_redo_stack') or not self._glossary_redo_stack:
            self.statusBar().showMessage("ไม่มีประวัติคำศัพท์ให้ทำซ้ำ", 2000)
            return
        import copy
        prof_name = getattr(self, 'current_profile_name', "Default")
        prof = TStudioCore.get_current_profile_data(prof_name)
        if not hasattr(self, '_glossary_history'): self._glossary_history = []
        self._glossary_history.append(copy.deepcopy(prof.get("glossary", {})))
        next_glossary = self._glossary_redo_stack.pop()
        prof["glossary"] = next_glossary
        TStudioCore.save_profile_data(prof_name, prof)
        self._populate_glossary_table(next_glossary)
        self.refresh_glossary_dependent_features()
        if hasattr(self, 'current_source_row') and self.current_source_row >= 0:
            self.select_source_row(self.current_source_row)
        self.statusBar().showMessage(f"↪ ทำซ้ำคำศัพท์สำเร็จ (มี {len(next_glossary)} คำ)", 2500)

    def _import_glossary_dialog(self):
        target_dir = self.get_active_translation_workspace()
        file_path, _filter = QFileDialog.getOpenFileName(
            self, "นำเข้าคลังคำศัพท์", target_dir, "Glossary Files (*.csv *.json);;CSV Files (*.csv);;JSON Files (*.json);;All Files (*.*)"
        )
        if not file_path: return
        prof_name = getattr(self, 'current_profile_name', "Default")
        imported_terms = {}
        try:
            if file_path.lower().endswith(".json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    jdata = json.load(f)
                if isinstance(jdata, dict):
                    if "glossary" in jdata and isinstance(jdata["glossary"], dict):
                        jdata = jdata["glossary"]
                    for k, v in jdata.items():
                        if isinstance(v, list):
                            target = str(v[0]) if len(v) > 0 else ""
                            tag = str(v[1]) if len(v) > 1 else "General"
                            imported_terms[k.strip()] = [target, tag]
                        else:
                            imported_terms[k.strip()] = [str(v), "General"]
            else:
                import csv
                with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if not row: continue
                        if row[0].strip().lower() in ("original", "english", "en", "term", "source"):
                            continue
                        en = row[0].strip()
                        th = row[1].strip() if len(row) > 1 else ""
                        cat = row[2].strip() if len(row) > 2 else "General"
                        if en and th:
                            imported_terms[en] = [th, cat]

            if not imported_terms:
                QMessageBox.warning(self, "นำเข้าคำศัพท์", "ไม่พบคำศัพท์ที่สามารถนำเข้าได้ในไฟล์ที่เลือก")
                return

            reply = QMessageBox.question(
                self, "วิธีการนำเข้า",
                f"พบคำศัพท์ทั้งหมด {len(imported_terms)} คำ\n\nคุณต้องการ 'ผสาน (Merge)' เข้ากับคำศัพท์เดิม หรือ 'แทนที่ทั้งหมด (Overwrite)'?\n\nกด Yes = ผสาน (Merge)\nกด No = แทนที่ทั้งหมด (Overwrite)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return

            prof = TStudioCore.get_current_profile_data(prof_name)
            current_glossary = prof.get("glossary", {}).copy()
            if reply == QMessageBox.StandardButton.Yes:
                current_glossary.update(imported_terms)
                final_glossary = current_glossary
            else:
                final_glossary = imported_terms

            self._save_glossary_to_active_profile(final_glossary)
            QMessageBox.information(self, "นำเข้าสำเร็จ", f"นำเข้าคำศัพท์ลงในโปรไฟล์ '{prof_name}' เรียบร้อยแล้ว (รวมทั้งหมด {len(final_glossary)} คำ)")
        except Exception as e:
            QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ไม่สามารถนำเข้าไฟล์คำศัพท์ได้:\n{e}")

    def _export_glossary_dialog(self):
        prof_name = getattr(self, 'current_profile_name', "Default")
        prof = TStudioCore.get_current_profile_data(prof_name)
        glossary = prof.get("glossary", {})
        if not glossary:
            QMessageBox.warning(self, "ส่งออกคำศัพท์", f"โปรไฟล์ '{prof_name}' ยังไม่มีคำศัพท์ในคลัง")
            return
            
        target_dir = self.get_active_translation_workspace()
        file_path, _filter = QFileDialog.getSaveFileName(
            self, f"ส่งออกคำศัพท์โปรไฟล์ '{prof_name}'", os.path.join(target_dir, f"{prof_name}_glossary.csv"), "CSV Files (*.csv);;JSON Files (*.json)"
        )
        if not file_path: return
        try:
            if file_path.lower().endswith(".json"):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(glossary, f, ensure_ascii=False, indent=4)
            else:
                import csv
                with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Original", "Translation", "Category"])
                    for en, val in glossary.items():
                        th = val[0] if (isinstance(val, list) and len(val) > 0) else str(val or "")
                        cat = val[1] if (isinstance(val, list) and len(val) > 1) else "General"
                        writer.writerow([en, th, cat])
            self.statusBar().showMessage(f"● ส่งออกคลังคำศัพท์ {len(glossary)} คำ สำเร็จที่: {file_path}", 4000)
            QMessageBox.information(self, "ส่งออกสำเร็จ", f"ส่งออกคำศัพท์ {len(glossary)} คำ ไปยังไฟล์เรียบร้อยแล้ว!")
        except Exception as e:
            QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ไม่สามารถส่งออกไฟล์คำศัพท์ได้:\n{e}")

    def _apply_ai_ref_to_editor(self):
        if hasattr(self, 'col3_editor'):
            self.col3_editor.apply_ai_ref_to_editor()
        elif hasattr(self, 'txt_ai') and self.txt_ai.toPlainText():
            self.txt_trans.setPlainText(self.txt_ai.toPlainText())
            self.txt_trans.setFocus()

    def _toggle_ai_styles(self):
        self.retranslate_options(show_dialog=False)

    def _apply_ai_style(self, idx):
        if hasattr(self, 'ai_style_cards') and 0 <= idx < len(self.ai_style_cards):
            _, lbl = self.ai_style_cards[idx]
            txt = lbl.text().strip()
            if txt and not txt.startswith("—") and not txt.startswith("⏳") and not txt.startswith("❌"):
                row = getattr(self, 'current_source_row', -1)
                if getattr(self, 'chk_guide_mode', None) and self.chk_guide_mode.isChecked():
                    if row >= 0 and row < len(self.model._data):
                        self.model.update_ai_ref(row, txt)
                    self.txt_ai.setPlainText(txt)
                    self.statusBar().showMessage(f"● บันทึกสไตล์ที่ {idx+1} ลงช่อง AI Reference แล้ว", 3000)
                else:
                    self.txt_trans.setPlainText(txt)
                    self.txt_trans.setFocus()
                    if row >= 0 and row < len(self.model._data):
                        self.model.update_trans(row, txt)
                    self.statusBar().showMessage(f"● เลือกใช้สไตล์ที่ {idx+1} เรียบร้อยแล้ว", 3000)

    def _insert_chip_text(self, text):
        if hasattr(self, 'col3_editor'):
            self.col3_editor.insert_chip_text(text)
        elif hasattr(self, 'txt_trans'):
            self.txt_trans.insertPlainText(text)
            self.txt_trans.setFocus()

    def _copy_source_to_clipboard(self):
        if hasattr(self, 'col3_editor'):
            self.col3_editor.copy_source_to_clipboard()
        elif hasattr(self, 'txt_source'):
            txt = self.txt_source.toPlainText()
            if txt:
                QApplication.clipboard().setText(txt)

    def _on_table_selection_changed(self, selected, deselected):
        try:
            if not hasattr(self, 'table') or not self.table:
                return
            sel_model = self.table.selectionModel()
            if not sel_model:
                return
            indexes = sel_model.selectedRows()
            count = len(indexes)
            if hasattr(self, 'lbl_bulk_count') and hasattr(self, 'floating_bulk_bar'):
                if count > 1:
                    self.lbl_bulk_count.setText(f"● เลือก {count} แถว")
                    self.floating_bulk_bar.show()
                else:
                    self.floating_bulk_bar.hide()
            if hasattr(self, 'batch_dock') and self.batch_dock:
                try:
                    self.batch_dock.sync_active_file_info()
                except Exception:
                    pass
        except Exception as e:
            print(f"[Warning] _on_table_selection_changed suppressed: {e}")

    def _advance_filtered_row(self, direction=1):
        if hasattr(self, '_trans_save_timer') and self._trans_save_timer.isActive():
            self._trans_save_timer.stop()
            self.on_trans_changed()

        cur_idx = self.table.currentIndex()
        if not cur_idx.isValid():
            if self.proxy.rowCount() > 0:
                self.select_row_by_proxy(0)
            return

        cur_proxy_row = cur_idx.row()
        src_row = self.proxy.mapToSource(cur_idx).row()

        is_filtering = (self.proxy._mode != 0 or bool(self.proxy._search))
        row_released = is_filtering and (0 <= src_row < len(self.model._data)) and not self.proxy.filterAcceptsRow(src_row, QModelIndex())

        if row_released:
            self._is_releasing_filter_row = True
            try:
                self.proxy.invalidateFilter()
            finally:
                self._is_releasing_filter_row = False

            if cur_proxy_row < self.proxy.rowCount():
                self.select_row_by_proxy(cur_proxy_row)
            elif self.proxy.rowCount() > 0:
                self.select_row_by_proxy(self.proxy.rowCount() - 1)
            else:
                self.current_source_row = -1
                for w in [self.txt_source, self.txt_ai, self.txt_trans]:
                    w.blockSignals(True)
                    w.clear()
                    w.blockSignals(False)
                self.statusBar().showMessage("🎉 ตรวจสอบและแก้ไขครบทุกคำในตัวกรองเรียบร้อยแล้ว!", 4000)
        else:
            target_row = cur_proxy_row + direction
            if 0 <= target_row < self.proxy.rowCount():
                self.select_row_by_proxy(target_row)

    def confirm_and_next_row(self):
        self._advance_filtered_row(direction=1)

    def select_next_row(self):
        self._advance_filtered_row(direction=1)

    def select_prev_row(self):
        self._advance_filtered_row(direction=-1)

    def select_row_by_proxy(self, proxy_row):
        if 0 <= proxy_row < self.proxy.rowCount():
            idx = self.proxy.index(proxy_row, 0)
            if idx.isValid():
                self.table.selectRow(proxy_row)
                self.table.setCurrentIndex(idx)
                self.table.scrollTo(idx, QAbstractItemView.ScrollHint.EnsureVisible)
                self.on_row_selected(idx, idx)

    def select_source_row(self, row_idx):
        """Selects and scrolls to a row in the main table by its source model index."""
        if not hasattr(self, 'model') or not self.model or not getattr(self.model, '_data', None):
            return
        if row_idx < 0 or row_idx >= len(self.model._data):
            return
        if not hasattr(self, 'proxy') or not self.proxy or not hasattr(self, 'table') or not self.table:
            return
        try:
            src_index = self.model.index(row_idx, 0)
            proxy_index = self.proxy.mapFromSource(src_index)
            if proxy_index.isValid():
                p_row = proxy_index.row()
                if 0 <= p_row < self.proxy.rowCount():
                    sel_model = self.table.selectionModel()
                    if sel_model:
                        from PyQt6.QtCore import QItemSelectionModel
                        sel_model.blockSignals(True)
                        try:
                            sel_model.setCurrentIndex(proxy_index, QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows)
                        finally:
                            sel_model.blockSignals(False)
                    self.table.scrollTo(proxy_index, QAbstractItemView.ScrollHint.EnsureVisible)
                    self.on_row_selected(proxy_index, proxy_index)
        except Exception as e:
            print(f"[Warning] select_source_row suppressed exception: {e}")

    def setup_menu_bar(self):
        menubar = getattr(self, 'top_menu_bar', None) or self.menuBar()
        menubar.clear()
        
        # Clean up any previous global shortcut actions attached directly to self
        if hasattr(self, '_window_shortcut_actions'):
            for act in self._window_shortcut_actions:
                self.removeAction(act)
        self._window_shortcut_actions = []

        def _register_action(action):
            self.addAction(action)
            self._window_shortcut_actions.append(action)
            return action
        
        # Register global file & project shortcuts on window
        act_new_proj = QAction(_("act_start_translation"), self)
        act_new_proj.setShortcut('Ctrl+N')
        act_new_proj.triggered.connect(self.new_project_from_file)
        _register_action(act_new_proj)

        act_open_proj = QAction(_("act_open_project"), self)
        act_open_proj.setShortcut('Ctrl+O')
        act_open_proj.triggered.connect(self.new_project_from_file)
        _register_action(act_open_proj)

        act_save_proj = QAction(_("act_save_project"), self)
        act_save_proj.setShortcut('Ctrl+S')
        act_save_proj.triggered.connect(self.save_csv)
        _register_action(act_save_proj)

        act_save_csv = QAction(_("act_save_csv_as"), self)
        act_save_csv.setShortcut('Ctrl+Shift+S')
        act_save_csv.triggered.connect(self.save_csv_as)
        _register_action(act_save_csv)

        act_deploy = QAction(_("act_deploy"), self)
        act_deploy.setShortcut('Ctrl+D')
        act_deploy.triggered.connect(self.deploy_to_game)
        _register_action(act_deploy)

        # --- Edit Menu ---
        edit_menu = menubar.addMenu(_("menu_edit"))
        
        act_undo = QAction(_("act_undo"), self)
        act_undo.setToolTip(_("tooltip_act_undo"))
        act_undo.setShortcut("Ctrl+Z")
        act_undo.triggered.connect(lambda *args: QApplication.focusWidget().undo() if hasattr(QApplication.focusWidget(), 'undo') else None)
        edit_menu.addAction(act_undo)
        
        act_redo = QAction(_("act_redo"), self)
        act_redo.setToolTip(_("tooltip_act_redo"))
        act_redo.setShortcut("Ctrl+Y")
        act_redo.triggered.connect(lambda *args: QApplication.focusWidget().redo() if hasattr(QApplication.focusWidget(), 'redo') else None)
        edit_menu.addAction(act_redo)
        
        edit_menu.addSeparator()
        
        act_cut = QAction(_("act_cut"), self)
        act_cut.setToolTip(_("tooltip_act_cut"))
        act_cut.setShortcut("Ctrl+X")
        act_cut.triggered.connect(lambda *args: QApplication.focusWidget().cut() if hasattr(QApplication.focusWidget(), 'cut') else None)
        edit_menu.addAction(act_cut)
        
        act_copy = QAction(_("act_copy"), self)
        act_copy.setToolTip(_("tooltip_act_copy"))
        act_copy.setShortcut("Ctrl+C")
        act_copy.triggered.connect(lambda *args: QApplication.focusWidget().copy() if hasattr(QApplication.focusWidget(), 'copy') else None)
        edit_menu.addAction(act_copy)
        
        act_paste = QAction(_("act_paste"), self)
        act_paste.setToolTip(_("tooltip_act_paste"))
        act_paste.setShortcut("Ctrl+V")
        act_paste.triggered.connect(lambda *args: QApplication.focusWidget().paste() if hasattr(QApplication.focusWidget(), 'paste') else None)
        edit_menu.addAction(act_paste)
        
        edit_menu.addSeparator()
        
        act_quick_search = QAction("🔍 ค้นหาด่วน (Focus Quick Search)", self)
        act_quick_search.setToolTip("โฟกัสช่องค้นหาด่วนในแถบเครื่องมือ")
        act_quick_search.setShortcut(QKeySequence("Ctrl+F"))
        act_quick_search.triggered.connect(self.focus_quick_search)
        edit_menu.addAction(act_quick_search)
        _register_action(act_quick_search)

        act_fr = QAction(_("act_find_replace"), self)
        act_fr.setToolTip(_("tooltip_act_fr"))
        act_fr.setShortcut(QKeySequence("Ctrl+H"))
        act_fr.triggered.connect(lambda *args: FindReplaceDialog(self).exec())
        edit_menu.addAction(act_fr)
        _register_action(act_fr)
        
        edit_menu.addSeparator()
        
        self.act_trans_smart = QAction(_("act_trans_smart"), self)
        # Ctrl+T = Smart translate: single if 1 row, batch if multiple rows selected
        self.act_trans_smart.setShortcut(QKeySequence("Ctrl+T"))
        self.act_trans_smart.triggered.connect(self.retranslate_smart)
        edit_menu.addAction(self.act_trans_smart)
        
        self.act_trans_opt = QAction(_("act_trans_opt"), self)
        self.act_trans_opt.setShortcut("Ctrl+Shift+O")
        self.act_trans_opt.triggered.connect(lambda: self.retranslate_options(show_dialog=True))
        edit_menu.addAction(self.act_trans_opt)
        
        self.act_trans_special = QAction(_("act_trans_special"), self)
        # Ctrl+Shift+T = Batch translate all selected rows
        self.act_trans_special.setShortcut("Ctrl+Shift+T")
        self.act_trans_special.triggered.connect(self.show_special_translation_menu_at_cursor)
        edit_menu.addAction(self.act_trans_special)
        
        self.act_trans_batch = QAction("⚡ แปลทีละบรรทัดในตาราง (Batch CAT Mode)", self)
        self.act_trans_batch.triggered.connect(lambda: self.retranslate_batch(force_cat=True))
        edit_menu.addAction(self.act_trans_batch)

        self.act_trans_trun = QAction("🚀 แปลแถวที่เลือกด้วย TRun Batch (Ctrl+Shift+B)", self)
        self.act_trans_trun.setShortcut("Ctrl+Shift+B")
        self.act_trans_trun.triggered.connect(lambda: self.send_selection_to_trun(auto_start=False))
        edit_menu.addAction(self.act_trans_trun)

        edit_menu.addSeparator()

        act_clear_sel = QAction("🧹 ลบคำแปลแถวที่เลือก (Clear Selected)\tBackspace", self)
        act_clear_sel.triggered.connect(lambda: self.clear_selected_translations(only_ai=False))
        edit_menu.addAction(act_clear_sel)

        act_clear_ai_sel = QAction("🤖 ลบเฉพาะผลแปล AI แถวที่เลือก", self)
        act_clear_ai_sel.triggered.connect(lambda: self.clear_selected_translations(only_ai=True))
        edit_menu.addAction(act_clear_ai_sel)

        act_clear_all = QAction("💥 ลบคำแปลทั้งหมดในไฟล์ (Clear All Translations)...", self)
        act_clear_all.triggered.connect(lambda: self.clear_all_translations(only_ai=False))
        edit_menu.addAction(act_clear_all)

        act_clear_ai_all = QAction("🤖 ลบเฉพาะผลแปล AI ทั้งหมดในไฟล์...", self)
        act_clear_ai_all.triggered.connect(lambda: self.clear_all_translations(only_ai=True))
        edit_menu.addAction(act_clear_ai_all)
        
        # --- Tools Menu ---
        tools_menu = menubar.addMenu(_("menu_tools"))
        
        act_global = QAction(_("act_global_settings"), self)
        act_global.setToolTip(_("tooltip_act_global"))
        act_global.setShortcut("Ctrl+I")
        act_global.triggered.connect(self.open_settings)
        tools_menu.addAction(act_global)
        
        tools_menu.addSeparator()
        
        act_glossary = QAction(_("act_glossary_manager"), self)
        act_glossary.setToolTip(_("tooltip_act_glossary"))
        act_glossary.setShortcut("Ctrl+B")
        act_glossary.setStatusTip("Open or Focus the Glossary Manager")
        act_glossary.triggered.connect(self.open_glossary)
        tools_menu.addAction(act_glossary)

        act_sweep_glossary = QAction("🧹 กวาดล้างคำทั่วไปในคลังศัพท์ (Glossary Sweeper)...", self)
        act_sweep_glossary.setToolTip("ตรวจหาและกวาดล้างคำศัพท์ทั่วไป แท็กเอนจิน เสียงคราง และคำที่ไม่ได้ใช้ในโปรไฟล์")
        act_sweep_glossary.triggered.connect(self._clean_and_audit_glossary_dialog)
        tools_menu.addAction(act_sweep_glossary)
        
        self.act_toggle_qa = QAction(QIcon(), _("menu_qa_check"), self)
        self.act_toggle_qa.setCheckable(True)
        self.act_toggle_qa.setChecked(False)
        self.act_toggle_qa.setShortcut("Ctrl+Q")
        self.act_toggle_qa.setToolTip(_("tooltip_act_toggle_qa_status"))
        self.act_toggle_qa.triggered.connect(self.on_toggle_qa)
        tools_menu.addAction(self.act_toggle_qa)
        
        self.act_toggle_qa_marker = QAction(QIcon(), _("menu_qa_marker"), self)
        self.act_toggle_qa_marker.setCheckable(True)
        self.act_toggle_qa_marker.setChecked(True)
        self.act_toggle_qa_marker.setShortcut("Ctrl+M")
        self.act_toggle_qa_marker.setToolTip(_("tooltip_act_toggle_qa_marker_status"))
        self.act_toggle_qa_marker.triggered.connect(self.on_toggle_qa_marker)
        tools_menu.addAction(self.act_toggle_qa_marker)
        
        tools_menu.addSeparator()
        
        act_prompts = QAction("⚙️ ตั้งค่า AI Prompt (TLM Studio)", self)
        act_prompts.setToolTip(_("tooltip_act_prompts"))
        act_prompts.setShortcut("Ctrl+P")
        act_prompts.triggered.connect(lambda: self.open_prompt_settings(initial_tab=1))
        tools_menu.addAction(act_prompts)
        
        tools_menu.addSeparator()
        
        act_tlm = QAction("✨ TLM Studio (บริบทและคำศัพท์)", self)
        act_tlm.setToolTip(_("tooltip_act_tlm"))
        act_tlm.setShortcut("Ctrl+L")
        act_tlm.setStatusTip("Open TLM Studio (Lore Ingestion & Directives)")
        act_tlm.triggered.connect(lambda: self.open_tlm_studio(initial_tab=0))
        tools_menu.addAction(act_tlm)
        
        tools_menu.addSeparator()
        
        act_plugins = QAction(_("plugin_menu_action"), self)
        act_plugins.setToolTip(_("plugin_menu_tooltip"))
        act_plugins.triggered.connect(self.open_plugin_manager)
        tools_menu.addAction(act_plugins)
        
        tools_menu.addSeparator()
        
        act_refresh_tags = QAction("🔄 คำนวณหมวดหมู่แถวใหม่ทั้งหมด (Refresh Row Tags)", self)
        act_refresh_tags.setToolTip("วิเคราะห์และอัปเดตแท็กจัดหมวดหมู่ (ตัวละคร, สกิล, ไอเทม, บทสนทนา ฯลฯ) ใหม่ทั้งหมด")
        act_refresh_tags.setShortcut("F5")
        act_refresh_tags.triggered.connect(self.refresh_model_tags)
        tools_menu.addAction(act_refresh_tags)

        act_analyzer = QAction("📊 วิเคราะห์โครงสร้างและคำศัพท์ทั้งไฟล์ (Deep File Analyzer)", self)
        act_analyzer.setToolTip("เปิดศูนย์วิเคราะห์อัจฉริยะ (สารบบตัวละคร, ชุดสกิล, ขุดคำศัพท์ Glossary, จับคำแปลขัดแย้ง)")
        act_analyzer.setShortcut("Ctrl+Shift+A")
        act_analyzer.triggered.connect(self.open_file_analyzer)
        tools_menu.addAction(act_analyzer)
        
        # --- View Menu ---
        view_menu = menubar.addMenu(_("menu_view"))
        
        act_zoom_in = QAction(_("act_zoom_in"), self)
        act_zoom_in.setToolTip(_("tooltip_act_zoom_in"))
        act_zoom_in.setShortcut("Ctrl++")
        act_zoom_in.triggered.connect(self.zoom_in)
        view_menu.addAction(act_zoom_in)
        
        act_zoom_out = QAction(_("act_zoom_out"), self)
        act_zoom_out.setToolTip(_("tooltip_act_zoom_out"))
        act_zoom_out.setShortcut("Ctrl+-")
        act_zoom_out.triggered.connect(self.zoom_out)
        view_menu.addAction(act_zoom_out)
        
        act_zoom_reset = QAction(_("act_reset_zoom"), self)
        act_zoom_reset.setToolTip(_("tooltip_act_zoom_reset"))
        act_zoom_reset.setShortcut("Ctrl+0")
        act_zoom_reset.triggered.connect(self.zoom_reset)
        view_menu.addAction(act_zoom_reset)
        
        view_menu.addSeparator()
        
        act_wrap = QAction(_("act_word_wrap"), self)
        act_wrap.setToolTip(_("tooltip_act_wrap"))
        act_wrap.setShortcut("Alt+Z")
        act_wrap.setCheckable(True)
        act_wrap.setChecked(True)
        act_wrap.triggered.connect(self.toggle_word_wrap)
        view_menu.addAction(act_wrap)
        
        view_menu.addSeparator()

        # Workspace Modes Menu
        mode_menu = view_menu.addMenu("🚀 สลับโหมดการทำงาน (Workspace Mode)")
        act_mode_studio = QAction("✍️ แปลภาษา (CAT Studio)", self)
        act_mode_studio.setShortcut("F1")
        act_mode_studio.triggered.connect(lambda: self.switch_workspace_mode('studio'))
        mode_menu.addAction(act_mode_studio)

        act_mode_trun = QAction("⚡ รันแปลอัตโนมัติ (Batch AI Runner)", self)
        act_mode_trun.setShortcut("F2")
        act_mode_trun.triggered.connect(lambda: self.switch_workspace_mode('trun'))
        mode_menu.addAction(act_mode_trun)
        
        view_menu.addSeparator()
        
        self.panels_menu = view_menu.addMenu(_("menu_panels"))
        self.panels_menu.aboutToShow.connect(self.populate_panels_menu)
        
        self.float_menu = view_menu.addMenu(_("menu_float_dock"))
        self.float_menu.aboutToShow.connect(self.populate_float_menu)
        
        view_menu.addSeparator()
        
        # --- Layouts Menu ---
        self.layouts_menu = menubar.addMenu(_("menu_layouts"))
        self.layouts_menu.aboutToShow.connect(self.populate_layouts_menu)

        # --- Help Menu ---
        help_title = _("menu_help") if _("menu_help") != "menu_help" else "ความช่วยเหลือ (Help)"
        self.help_menu = menubar.addMenu(help_title)
        
        act_cheatsheet = QAction("⌨️ รายการคีย์ลัดทั้งหมด (Shortcuts Cheatsheet)", self)
        act_cheatsheet.setShortcut("F12")
        act_cheatsheet.setToolTip("เปิดหน้าต่างสรุปและแนะนำคีย์ลัดทั้งหมดใน TStudio")
        act_cheatsheet.triggered.connect(self.open_shortcuts_cheatsheet)
        self.help_menu.addAction(act_cheatsheet)
        _register_action(act_cheatsheet)

    def populate_panels_menu(self):
        self.panels_menu.clear()
        from PyQt6.QtGui import QAction

        # 1. Column 1: CAT Table
        act_c1 = QAction("ตารางคำแปล (CAT Table - คอลัมน์ 1)", self)
        act_c1.setCheckable(True)
        act_c1.setChecked(self.col1_workspace.isVisible())
        act_c1.triggered.connect(lambda checked: self.toggle_column_visibility(0, checked))
        self.panels_menu.addAction(act_c1)

        # 2. Column 2: Glossary Window
        act_c2 = QAction("คลังคำศัพท์ (Glossary Window - คอลัมน์ 2)", self)
        act_c2.setCheckable(True)
        act_c2.setChecked(self.col2_glossary.isVisible())
        act_c2.triggered.connect(lambda checked: self.toggle_column_visibility(1, checked))
        self.panels_menu.addAction(act_c2)

        # 3. Column 3: Translation Workspace
        act_c3 = QAction("พื้นที่แปลและ AI (Translation Workspace - คอลัมน์ 3)", self)
        act_c3.setCheckable(True)
        act_c3.setChecked(self.col3_editor_stack.isVisible())
        act_c3.triggered.connect(lambda checked: self.toggle_column_visibility(2, checked))
        self.panels_menu.addAction(act_c3)

        self.panels_menu.addSeparator()

        # 4. Optional Auxiliary Docks
        from PyQt6.QtWidgets import QDockWidget
        for dock in self.findChildren(QDockWidget):
            title = dock.windowTitle()
            if not title or title in ["Workspace", "Source", "AI", "Translation", _("glossary_dock_title")]:
                continue
            action = QAction(title, self)
            action.setCheckable(True)
            action.setChecked(dock.isVisible())
            action.triggered.connect(lambda checked, d=dock: d.setVisible(checked))
            self.panels_menu.addAction(action)

    def zoom_in(self):
        self.current_zoom += 1
        self.apply_zoom()
        
    def zoom_out(self):
        self.current_zoom -= 1
        self.apply_zoom()
        
    def zoom_reset(self):
        self.current_zoom = 0
        self.apply_zoom()
        
    def apply_zoom(self):
        font = self.table.font()
        font.setPointSize(max(6, 10 + self.current_zoom))
        self.table.setFont(font)
        self.table.resizeRowsToContents()
        
    def toggle_word_wrap(self, checked):
        self.table.setWordWrap(checked)
        self.table.resizeRowsToContents()

    def populate_float_menu(self):
        self.float_menu.clear()
        from PyQt6.QtWidgets import QDockWidget
        from PyQt6.QtGui import QAction
        for dock in self.findChildren(QDockWidget):
            prefix = _("act_dock") if dock.isFloating() else _("act_float")
            action = QAction(f"{prefix} {dock.windowTitle()}", self)
            action.triggered.connect(lambda checked, d=dock: d.setFloating(not d.isFloating()))
            self.float_menu.addAction(action)

    def _setup_batch_progress_widget(self):
        """Create a spinner + progress bar embedded in the status bar for batch translate feedback."""
        from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
        from PyQt6.QtCore import QTimer

        self._batch_sb_widget = QWidget()
        self._batch_sb_widget.setFixedHeight(22)
        sb_layout = QHBoxLayout(self._batch_sb_widget)
        sb_layout.setContentsMargins(6, 0, 10, 0)
        sb_layout.setSpacing(6)

        # Spinner label — cycles through unicode braille frames
        self._batch_spinner_label = QLabel("⠋")
        self._batch_spinner_label.setStyleSheet(
            "color: #89b4fa; font-size: 14px; font-weight: bold;"
        )
        sb_layout.addWidget(self._batch_spinner_label)

        # Status text
        self._batch_status_label = QLabel(_("batch_status_translating"))
        self._batch_status_label.setStyleSheet(
            "color: #cdd6f4; font-size: 12px;"
        )
        sb_layout.addWidget(self._batch_status_label)

        # Mini progress bar
        self._batch_mini_bar = QProgressBar()
        self._batch_mini_bar.setFixedWidth(140)
        self._batch_mini_bar.setFixedHeight(10)
        self._batch_mini_bar.setRange(0, 100)
        self._batch_mini_bar.setValue(0)
        self._batch_mini_bar.setTextVisible(False)
        self._batch_mini_bar.setStyleSheet(
            "QProgressBar {"
            "  border: 1px solid #45475a;"
            "  border-radius: 4px;"
            "  background: #313244;"
            "}"
            "QProgressBar::chunk {"
            "  background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "    stop:0 #89b4fa, stop:1 #a6e3a1);"
            "  border-radius: 3px;"
            "}"
        )
        sb_layout.addWidget(self._batch_mini_bar)

        # Row counter
        self._batch_count_label = QLabel("0 / 0")
        self._batch_count_label.setStyleSheet(
            "color: #a6adc8; font-size: 11px;"
        )
        sb_layout.addWidget(self._batch_count_label)

        # Embed into status bar (left side)
        self.statusBar().insertPermanentWidget(0, self._batch_sb_widget)
        self._batch_sb_widget.hide()

        # Spinner animation timer
        self._spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._spinner_idx = 0
        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(80)
        self._spinner_timer.timeout.connect(self._tick_spinner)

    def _tick_spinner(self):
        self._spinner_idx = (self._spinner_idx + 1) % len(self._spinner_frames)
        self._batch_spinner_label.setText(self._spinner_frames[self._spinner_idx])

    def _start_batch_progress(self, total: int):
        """Show the batch progress widget and start the spinner."""
        if not hasattr(self, '_batch_sb_widget'):
            return
        self._batch_mini_bar.setValue(0)
        self._batch_count_label.setText(f"0 / {total}")
        self._batch_status_label.setText(_("batch_status_translating"))
        self._batch_sb_widget.show()
        self._spinner_timer.start()

    def _finish_batch_progress(self, success_count: int, total: int):
        """Hide the batch progress widget and stop the spinner."""
        if hasattr(self, '_apply_stats_to_ui'):
            self._apply_stats_to_ui()
        if not hasattr(self, '_batch_sb_widget'):
            return
        self._spinner_timer.stop()
        # Flash 100% briefly before hiding
        self._batch_mini_bar.setValue(100)
        if success_count == total:
            self._batch_status_label.setText(_("batch_status_done").format(total=total))
            self._batch_spinner_label.setText("✓")
            self._batch_spinner_label.setStyleSheet("color: #a6e3a1; font-size: 13px; font-weight: bold;")
        else:
            self._batch_status_label.setText(_("batch_status_done_error").format(error=total - success_count))
            self._batch_spinner_label.setText("!")
            self._batch_spinner_label.setStyleSheet("color: #f38ba8; font-size: 13px; font-weight: bold;")
        # Hide after 2 seconds
        QTimer.singleShot(2000, lambda: (
            self._batch_sb_widget.hide(),
            self._batch_spinner_label.setText("⠋"),
            self._batch_spinner_label.setStyleSheet("color: #89b4fa; font-size: 14px; font-weight: bold;"),
        ))

    def refresh_model_tags(self):
        """Re-calculate tags for current model and update filters/stats."""
        if not hasattr(self, 'model') or not self.model or not self.model._data:
            return
        updated = self.model.refresh_tags()
        self.update_progress_stats()
        if hasattr(self, 'proxy') and self.proxy:
            self.proxy.invalidateFilter()
        if hasattr(self, 'statusBar') and self.statusBar():
            self.statusBar().showMessage(f"✅ รีเฟรชหมวดหมู่แถวเรียบร้อยแล้ว (อัปเดต {updated:,} แถว)", 4000)

    def update_progress_stats(self):

        if not hasattr(self, 'model') or not self.model or not self.model._data:
            self.progress_bar.setFormat(_("progress_no_file"))
            self.progress_bar.setValue(0)
            return
            
        total = len(self.model._data)
        if total == 0:
            return
            
        translated_count = 0
        counts = {i: 0 for i in range(16)}
        counts[0] = total

        for item in self.model._data:
            text = item["trans"]
            src = item["source"]
            tag = item.get("tag", "")
            
            # Progress bar count
            if item.get("is_th", False):
                translated_count += 1
                
            # Mode 1: Untranslated
            if not text.strip(): counts[1] += 1
            # Mode 2: Translated
            if text.strip(): counts[2] += 1
            # Mode 3: AI Hallucinations
            src_len, trans_len = len(src), len(text)
            if trans_len >= 200 and src_len > 0 and (trans_len / src_len) > 4:
                counts[3] += 1
            # Mode 4: Quotes/Idioms
            if item.get("is_idiom", False):
                counts[4] += 1
                
            # Modes 5-12: Smart Tags
            if "Char" in tag: counts[5] += 1
            if "Loc" in tag: counts[6] += 1
            if "Skill" in tag: counts[7] += 1
            if "Item" in tag: counts[8] += 1
            if "Item" in tag or "Skill" in tag: counts[9] += 1
            if "Quest" in tag: counts[10] += 1
            if "Sys" in tag: counts[11] += 1
            if "Talk" in tag: counts[12] += 1
            
            # Mode 13 & 14
            clean_text = re.sub(r'\{.*?\}|\[.*?\]|<.*?>', '', text)
            has_thai = bool(re.search(r'[\u0E00-\u0E7F]', clean_text))
            has_eng = bool(re.search(r'[a-zA-Z]', clean_text))
            if has_thai and has_eng: counts[13] += 1
            
            clean_ai = re.sub(r'\{.*?\}|\[.*?\]|<.*?>', '', str(item.get("ai_ref") or ""))
            has_eng_ai = bool(re.search(r'[a-zA-Z]', clean_ai))
            has_thai_ai = bool(re.search(r'[\u0E00-\u0E7F]', clean_ai))
            if has_eng and has_eng_ai and not has_thai and not has_thai_ai: counts[14] += 1

            # Mode 15: CJK
            if text.strip():
                if TStudioCore.has_cjk(text): counts[15] += 1
            else:
                if TStudioCore.has_cjk(str(item.get("ai_ref") or "")): counts[15] += 1
            
        # Cache for incremental updates
        self._stat_translated = translated_count
        self._stat_counts = counts

        # Update combo box texts
        labels = [
            _("filter_all_rows"), _("filter_untranslated"), _("filter_translated"), _("filter_ai_hallucinations"), _("filter_quotes_idioms"),
            _("filter_characters"), _("filter_locations"), _("filter_skills"), _("filter_items"), _("filter_items_skills"),
            _("filter_quests"), _("filter_system_ui"), _("filter_dialogues"),
            _("filter_mixed_lang"),
            _("filter_eng_leftovers"),
            _("filter_cjk_leaks")
        ]
        self.filter_combo.blockSignals(True)
        for i in range(16):
            if i < self.filter_combo.count():
                self.filter_combo.setItemText(i, f"{labels[i]} ({counts[i]:,})")
        self.filter_combo.blockSignals(False)
                
        percent = int((translated_count / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percent)
        if hasattr(self, 'lbl_progress_capsule'):
            self.lbl_progress_capsule.setText(f"{percent}% ({translated_count} / {total})")
        if hasattr(self, 'chip_all'):
            self.chip_all.setText(f"ทั้งหมด ({total})")
        if hasattr(self, 'chip_untrans'):
            self.chip_untrans.setText(f"รอแปล ({counts[1]})")
        if hasattr(self, 'chip_trans'):
            self.chip_trans.setText(f"แปลแล้ว ({counts[2]})")
        if hasattr(self, 'chip_mixed'):
            self.chip_mixed.setText(f"🇬🇧 อังกฤษปน ({counts[13]})")
            if counts[13] > 0:
                self.chip_mixed.setStyleSheet("color: #fab387; font-weight: bold;")
            else:
                self.chip_mixed.setStyleSheet("")
        if hasattr(self, 'btn_breadcrumb'):
            prof = getattr(self, 'current_profile_name', None) or (self.cbo_profile.currentText() if hasattr(self, 'cbo_profile') else "Default")
            pdata = TStudioCore.get_current_profile_data(prof) if hasattr(TStudioCore, 'get_current_profile_data') else {}
            game_title = pdata.get("game_title", "").strip() if isinstance(pdata, dict) else ""
            if not game_title and getattr(self, 'project_dir', None):
                game_title = os.path.basename(self.project_dir)
            display_name = game_title if game_title and game_title != "Default" else prof
            fname = os.path.basename(self.csv_path) if getattr(self, 'csv_path', None) else "(คลิกเลือกไฟล์)"
            self.btn_breadcrumb.setText(f"📁 {display_name} › {fname}")
            if self.csv_path:
                self.btn_breadcrumb.setToolTip(self.csv_path)
        self.progress_bar.setFormat(f"แปลแล้ว {percent}% ({translated_count:,} / {total:,})")

    def _apply_stats_to_ui(self):
        if not hasattr(self, '_stat_counts') or self._stat_counts is None:
            return
        labels = [
            _("filter_all_rows"), _("filter_untranslated"), _("filter_translated"), _("filter_ai_hallucinations"), _("filter_quotes_idioms"),
            _("filter_characters"), _("filter_locations"), _("filter_skills"), _("filter_items"), _("filter_items_skills"),
            _("filter_quests"), _("filter_system_ui"), _("filter_dialogues"),
            _("filter_mixed_lang"),
            _("filter_eng_leftovers"),
            _("filter_cjk_leaks")
        ]
        self.filter_combo.blockSignals(True)
        for i in [1, 2, 3, 13, 14, 15]:
            if i < self.filter_combo.count():
                self.filter_combo.setItemText(i, f"{labels[i]} ({self._stat_counts[i]:,})")
        self.filter_combo.blockSignals(False)
        
        total = self._stat_counts[0]
        percent = int((self._stat_translated / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percent)
        self.progress_bar.setFormat(f"แปลแล้ว {percent}% ({self._stat_translated:,} / {total:,})")

    def _update_stats_for_row(self, row, old_text, new_text):
        if not hasattr(self, '_stat_counts') or self._stat_counts is None:
            self.update_progress_stats()
            if not hasattr(self, '_stat_counts') or self._stat_counts is None:
                return
        
        # --- Live Sync: Hook file watcher once per file, not on every single translated row! ---
        if self.csv_path and os.path.exists(self.csv_path):
            current_watched = self.file_watcher.files()
            if not current_watched or self.csv_path not in current_watched:
                if current_watched:
                    self.file_watcher.removePaths(current_watched)
                self.file_watcher.addPath(self.csv_path)
                self.last_csv_mtime = os.path.getmtime(self.csv_path)

        if row < 0 or row >= len(self.model._data):
            return

        item = self.model._data[row]
        src = item["source"]
        
        # 1. Progress bar Thai count
        old_is_th = bool(re.search(r'[ก-๙เแไใโ]', old_text)) if old_text else False
        new_is_th = bool(re.search(r'[ก-๙เแไใโ]', new_text)) if new_text else False
        if old_is_th != new_is_th:
            self._stat_translated += (1 if new_is_th else -1)
            
        # 2. Mode 1: Untranslated
        old_untrans = not old_text.strip()
        new_untrans = not new_text.strip()
        if old_untrans != new_untrans:
            self._stat_counts[1] += (1 if new_untrans else -1)
            
        # 3. Mode 2: Translated
        old_trans = bool(old_text.strip())
        new_trans = bool(new_text.strip())
        if old_trans != new_trans:
            self._stat_counts[2] += (1 if new_trans else -1)
            
        # 4. Mode 3: AI Hallucinations
        src_len = len(src)
        old_len = len(old_text)
        new_len = len(new_text)
        
        old_halluc = (old_len >= 200 and src_len > 0 and (old_len / src_len) > 4)
        new_halluc = (new_len >= 200 and src_len > 0 and (new_len / src_len) > 4)
        if old_halluc != new_halluc:
            self._stat_counts[3] += (1 if new_halluc else -1)
            
        c_old = re.sub(r'\{.*?\}|\[.*?\]|<.*?>', '', old_text) if old_text else ""
        c_new = re.sub(r'\{.*?\}|\[.*?\]|<.*?>', '', new_text) if new_text else ""
        
        old_has_th = bool(re.search(r'[\u0E00-\u0E7F]', c_old))
        old_has_en = bool(re.search(r'[a-zA-Z]', c_old))
        new_has_th = bool(re.search(r'[\u0E00-\u0E7F]', c_new))
        new_has_en = bool(re.search(r'[a-zA-Z]', c_new))
        
        old_mixed = old_has_th and old_has_en
        new_mixed = new_has_th and new_has_en
        if old_mixed != new_mixed:
            self._stat_counts[13] += (1 if new_mixed else -1)
            
        c_ai = re.sub(r'\{.*?\}|\[.*?\]|<.*?>', '', str(item.get("ai_ref") or ""))
        ai_has_en = bool(re.search(r'[a-zA-Z]', c_ai))
        ai_has_th = bool(re.search(r'[\u0E00-\u0E7F]', c_ai))
        
        old_eng_left = old_has_en and ai_has_en and not old_has_th and not ai_has_th
        new_eng_left = new_has_en and ai_has_en and not new_has_th and not ai_has_th
        if old_eng_left != new_eng_left:
            self._stat_counts[14] += (1 if new_eng_left else -1)
            
        old_has_cjk = TStudioCore.has_cjk(old_text) if old_text.strip() else TStudioCore.has_cjk(str(item.get("ai_ref") or ""))
        new_has_cjk = TStudioCore.has_cjk(new_text) if new_text.strip() else TStudioCore.has_cjk(str(item.get("ai_ref") or ""))
        if old_has_cjk != new_has_cjk:
            self._stat_counts[15] += (1 if new_has_cjk else -1)

        # Debounce UI updates via QTimer so rapid row completions do not freeze the GUI thread
        if hasattr(self, '_stats_ui_timer'):
            if not self._stats_ui_timer.isActive():
                self._stats_ui_timer.start()
        else:
            self._apply_stats_to_ui()

    def changeEvent(self, event):
        if event.type() == event.Type.ActivationChange:
            if self.isActiveWindow():
                self._reload_profiles_silently()
            else:
                # Focus lost, save immediately if there are pending edits
                if hasattr(self, '_trans_save_timer') and self._trans_save_timer.isActive():
                    self._trans_save_timer.stop()
                    self.on_trans_changed()
                if hasattr(self, '_csv_auto_save_timer') and self._csv_auto_save_timer.isActive():
                    self._csv_auto_save_timer.stop()
                    self.silent_save_csv()
        super().changeEvent(event)

    def _reload_profiles_silently(self):
        if getattr(self, '_is_loading_profiles', False): return
        self._is_loading_profiles = True
        try:
            new_data = TStudioCore.load_profiles()
            current_text = self.cbo_profile.currentText()
            self.cbo_profile.blockSignals(True)
            self.cbo_profile.clear()
            self.cbo_profile.addItems(list(new_data["presets"].keys()))
            
            # Try to restore the previously selected active preset
            active = new_data.get("active_preset", "Default")
            if current_text in new_data["presets"]:
                self.cbo_profile.setCurrentText(current_text)
            elif active in new_data["presets"]:
                self.cbo_profile.setCurrentText(active)
            self.cbo_profile.blockSignals(False)
            self._profiles_data = new_data
        except Exception as e:
            print(f"Silent reload error: {e}")
        self._is_loading_profiles = False


    def populate_layouts_menu(self):
        self.layouts_menu.clear()
        from PyQt6.QtGui import QAction
        from tstudio_core import TStudioCore

        cfg = TStudioCore.load_config()
        user_layouts = cfg.get(self.layout_cfg_key, {})
        cur = getattr(self, 'current_workspace_name', 'Default (ค่าเริ่มต้น)')

        # Helper for checkable preset action
        def add_preset_action(name, display_name, func):
            act = QAction(display_name, self)
            act.setCheckable(True)
            if cur == name:
                act.setChecked(True)
            act.triggered.connect(func)
            self.layouts_menu.addAction(act)

        # 1. Built-in Purpose-Driven Presets
        add_preset_action("Default (ค่าเริ่มต้น)", "🌟 ค่าเริ่มต้นสมดุล (Standard Masterpiece)", self.layout_default)
        add_preset_action("Translator Focus", "✍️ มุ่งเน้นการแปล (Translator Focus)", self.layout_translator_focus)
        add_preset_action("Glossary Review", "📖 คลังคำศัพท์ & ตรวจทาน (Glossary & QA Review)", self.layout_glossary_review)
        add_preset_action("Full CAT Table", "📊 ตรวจสอบตารางรวม (Full CAT Table)", self.layout_full_table)

        # 2. Custom Layouts
        if user_layouts:
            self.layouts_menu.addSeparator()
            for name in user_layouts.keys():
                act = QAction(f"🪟 {name}", self)
                act.setCheckable(True)
                if cur == name:
                    act.setChecked(True)
                act.triggered.connect(lambda checked, n=name: self.load_custom_layout(n))
                self.layouts_menu.addAction(act)

        self.layouts_menu.addSeparator()

        # 3. Reset Layout
        act_reset = QAction("🔄 รีเซ็ตเลย์เอาต์กลับค่าเริ่มต้น (Reset Layout)", self)
        act_reset.setToolTip("คืนค่าสัดส่วนหน้าจอทั้ง 3 คอลัมน์สู่ค่ามาตรฐานเริ่มต้นที่สมบูรณ์")
        act_reset.triggered.connect(self.reset_layout_default)
        self.layouts_menu.addAction(act_reset)

        self.layouts_menu.addSeparator()

        # 4. Column Visibility Toggles
        act_col1 = QAction("☑️ แสดงตารางคำแปล (CAT Table - คอลัมน์ 1)", self)
        act_col1.setCheckable(True)
        act_col1.setChecked(self.col1_workspace.isVisible())
        act_col1.setShortcut("Alt+1")
        act_col1.triggered.connect(lambda checked: self.toggle_column_visibility(0, checked))
        self.layouts_menu.addAction(act_col1)

        act_col2 = QAction("☑️ แสดงคลังคำศัพท์ (Glossary Window - คอลัมน์ 2)", self)
        act_col2.setCheckable(True)
        act_col2.setChecked(self.col2_glossary.isVisible())
        act_col2.setShortcut("Alt+2")
        act_col2.triggered.connect(lambda checked: self.toggle_column_visibility(1, checked))
        self.layouts_menu.addAction(act_col2)

        act_col3 = QAction("☑️ แสดงพื้นที่แปลและ AI (Translation Workspace - คอลัมน์ 3)", self)
        act_col3.setCheckable(True)
        act_col3.setChecked(self.col3_editor_stack.isVisible())
        act_col3.setShortcut("Alt+3")
        act_col3.triggered.connect(lambda checked: self.toggle_column_visibility(2, checked))
        self.layouts_menu.addAction(act_col3)

        self.layouts_menu.addSeparator()

        # 5. Save / Delete Custom Presets
        if cur in user_layouts:
            act_save_cur = QAction(f"💾 บันทึกทับเลย์เอาต์ '{cur}'", self)
            act_save_cur.triggered.connect(self.save_current_custom_layout)
            self.layouts_menu.addAction(act_save_cur)

        act_save = QAction("💾 บันทึกเลย์เอาต์ปัจจุบันเป็นแบบใหม่...", self)
        act_save.triggered.connect(self.save_custom_layout)
        self.layouts_menu.addAction(act_save)

        act_del = QAction("🗑️ ลบเลย์เอาต์ส่วนตัว...", self)
        act_del.triggered.connect(self.delete_custom_layout)
        self.layouts_menu.addAction(act_del)

    def apply_splitter_proportions(self, ratios, visibilities=(True, True, True), layout_name=None):
        """
        Apply proportional widths to self.main_splitter and toggle column visibilities.
        ratios: tuple of 3 floats summing to 1.0 (e.g. (0.36, 0.30, 0.34))
        visibilities: tuple of 3 booleans (col1, col2, col3)
        """
        if layout_name:
            self.current_workspace_name = layout_name

        # 1. Update visibility
        self.col1_workspace.setVisible(visibilities[0])
        self.col2_glossary.setVisible(visibilities[1])
        self.col3_editor_stack.setVisible(visibilities[2])

        # 2. Calculate responsive pixel sizes
        total_w = self.main_splitter.width()
        if total_w < 600:
            total_w = self.width() if self.width() > 600 else 1400

        sizes = []
        for r, v in zip(ratios, visibilities):
            if v:
                sizes.append(max(80, int(total_w * r)))
            else:
                sizes.append(0)

        self.main_splitter.setSizes(sizes)

        # 3. Ensure auxiliary docks are hidden in studio mode
        if hasattr(self, 'batch_dock') and getattr(self, 'current_app_mode', 'studio') == 'studio':
            self.batch_dock.hide()
        if hasattr(self, 'tlm_dock'):
            self.tlm_dock.hide()

    def toggle_column_visibility(self, col_index, checked=None):
        """Toggle visibility of a specific column while preserving layout balance."""
        cols = [self.col1_workspace, self.col2_glossary, self.col3_editor_stack]
        if col_index < 0 or col_index >= len(cols):
            return

        target = cols[col_index]
        new_visible = checked if checked is not None else not target.isVisible()

        # Safety check: do not allow hiding all columns
        other_visible = [c.isVisible() for i, c in enumerate(cols) if i != col_index]
        if not new_visible and not any(other_visible):
            return

        target.setVisible(new_visible)

        cur_sizes = self.main_splitter.sizes()
        total_w = sum(cur_sizes) or self.main_splitter.width() or 1400
        vis_count = sum(1 for c in cols if c.isVisible())

        if vis_count > 0:
            new_sizes = []
            for i, c in enumerate(cols):
                if c.isVisible():
                    if cur_sizes[i] < 50:
                        new_sizes.append(int(total_w / vis_count))
                    else:
                        new_sizes.append(cur_sizes[i])
                else:
                    new_sizes.append(0)
            self.main_splitter.setSizes(new_sizes)

    def layout_default(self):
        """🌟 ค่าเริ่มต้นสมดุล (Standard Masterpiece: 36% / 30% / 34%)"""
        self.apply_splitter_proportions(
            ratios=(0.36, 0.30, 0.34),
            visibilities=(True, True, True),
            layout_name="Default (ค่าเริ่มต้น)"
        )
        self.statusBar().showMessage("● สลับสู่เลย์เอาต์: 🌟 ค่าเริ่มต้นสมดุล (Standard Masterpiece)", 3000)

    def layout_translator_focus(self):
        """✍️ มุ่งเน้นการแปล (Translator Focus: 28% / 0% / 72%)"""
        self.apply_splitter_proportions(
            ratios=(0.28, 0.0, 0.72),
            visibilities=(True, False, True),
            layout_name="Translator Focus"
        )
        self.statusBar().showMessage("● สลับสู่เลย์เอาต์: ✍️ มุ่งเน้นการแปล (ขยายพื้นที่แปลและ AI เต็มจอ)", 3000)

    def layout_glossary_review(self):
        """📖 คลังคำศัพท์ & ตรวจทาน (Glossary & Review: 35% / 42% / 23%)"""
        self.apply_splitter_proportions(
            ratios=(0.35, 0.42, 0.23),
            visibilities=(True, True, True),
            layout_name="Glossary Review"
        )
        self.statusBar().showMessage("● สลับสู่เลย์เอาต์: 📖 คลังคำศัพท์ & ตรวจทาน (ขยายคลังคำศัพท์กว้างพิเศษ)", 3000)

    def layout_full_table(self):
        """📊 ตรวจสอบตารางรวม (Full CAT Table: 75% / 0% / 25%)"""
        self.apply_splitter_proportions(
            ratios=(0.75, 0.0, 0.25),
            visibilities=(True, False, True),
            layout_name="Full CAT Table"
        )
        self.statusBar().showMessage("● สลับสู่เลย์เอาต์: 📊 ตรวจสอบตารางรวม (ขยายตารางคำแปลเต็มตา)", 3000)

    def reset_layout_default(self):
        """Reset layout completely to pristine state."""
        self.layout_default()

        if hasattr(self, 'batch_dock') and getattr(self, 'current_app_mode', 'studio') == 'studio':
            self.batch_dock.hide()
        if hasattr(self, 'tlm_dock'):
            self.tlm_dock.hide()

        try:
            from tstudio_core import TStudioCore
            cfg = TStudioCore.load_config()
            cfg['layout_state'] = ""
            cfg['current_workspace'] = "Default (ค่าเริ่มต้น)"
            cfg['modern_active_layout'] = "Default (ค่าเริ่มต้น)"
            cfg['modern_splitter_sizes'] = self.main_splitter.sizes()
            cfg['modern_columns_visible'] = [True, True, True]
            TStudioCore.save_config(cfg)
        except Exception as e:
            print(f"Error resetting layout in config: {e}")

        self.statusBar().showMessage("✓ รีเซ็ตเลย์เอาต์กลับสู่ค่าเริ่มต้นสมบูรณ์ เรียบร้อยแล้ว", 4000)

    @property
    def layout_cfg_key(self):
        return 'modern_user_layouts'

    def save_current_custom_layout(self):
        try:
            from tstudio_core import TStudioCore
            cfg = TStudioCore.load_config()
            layouts = cfg.get(self.layout_cfg_key, {})
            if self.current_workspace_name in layouts:
                layouts[self.current_workspace_name] = {
                    "sizes": self.main_splitter.sizes(),
                    "visible": [
                        self.col1_workspace.isVisible(),
                        self.col2_glossary.isVisible(),
                        self.col3_editor_stack.isVisible()
                    ]
                }
                cfg[self.layout_cfg_key] = layouts
                TStudioCore.save_config(cfg)
                self.statusBar().showMessage(f"✓ บันทึกทับเลย์เอาต์ '{self.current_workspace_name}' สำเร็จ", 3000)
        except Exception as e:
            self.statusBar().showMessage(f"⚠️ ไม่สามารถบันทึกเลย์เอาต์: {e}", 3000)

    def save_custom_layout(self):
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        name, ok = QInputDialog.getText(self, "บันทึกเลย์เอาต์ใหม่", "ตั้งชื่อเลย์เอาต์ของคุณ:")
        if ok and name.strip():
            name = name.strip()
            try:
                from tstudio_core import TStudioCore
                cfg = TStudioCore.load_config()
                layouts = cfg.get(self.layout_cfg_key, {})

                if name in layouts:
                    reply = QMessageBox.question(
                        self, "เขียนทับเลย์เอาต์",
                        f"มีเลย์เอาต์ '{name}' อยู่แล้วในระบบ ต้องการเขียนทับหรือไม่?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return

                layouts[name] = {
                    "sizes": self.main_splitter.sizes(),
                    "visible": [
                        self.col1_workspace.isVisible(),
                        self.col2_glossary.isVisible(),
                        self.col3_editor_stack.isVisible()
                    ]
                }
                cfg[self.layout_cfg_key] = layouts
                self.current_workspace_name = name
                cfg['modern_active_layout'] = name
                TStudioCore.save_config(cfg)
                self.statusBar().showMessage(f"✓ บันทึกเลย์เอาต์ '{name}' เรียบร้อยแล้ว", 3000)
            except Exception as e:
                self.statusBar().showMessage(f"⚠️ เกิดข้อผิดพลาดในการบันทึก: {e}", 3000)

    def load_custom_layout(self, name):
        try:
            from tstudio_core import TStudioCore
            cfg = TStudioCore.load_config()
            layouts = cfg.get(self.layout_cfg_key, {})
            if name in layouts:
                info = layouts[name]
                sizes = info.get("sizes", [500, 420, 480])
                visible = info.get("visible", [True, True, True])

                self.col1_workspace.setVisible(visible[0])
                self.col2_glossary.setVisible(visible[1])
                self.col3_editor_stack.setVisible(visible[2])
                self.main_splitter.setSizes(sizes)

                self.current_workspace_name = name
                self.statusBar().showMessage(f"● สลับสู่เลย์เอาต์ส่วนตัว: 🪟 {name}", 3000)
        except Exception as e:
            self.statusBar().showMessage(f"⚠️ โหลดเลย์เอาต์ไม่สำเร็จ: {e}", 3000)

    def delete_custom_layout(self):
        try:
            from tstudio_core import TStudioCore
            cfg = TStudioCore.load_config()
            layouts = cfg.get(self.layout_cfg_key, {})
            if not layouts:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "ลบเลย์เอาต์", "ไม่พบเลย์เอาต์ส่วนตัวที่สร้างไว้")
                return

            from PyQt6.QtWidgets import QInputDialog
            items = list(layouts.keys())
            name, ok = QInputDialog.getItem(self, "ลบเลย์เอาต์", "เลือกเลย์เอาต์ที่ต้องการลบ:", items, 0, False)
            if ok and name:
                del layouts[name]
                cfg[self.layout_cfg_key] = layouts
                if self.current_workspace_name == name:
                    self.layout_default()
                TStudioCore.save_config(cfg)
                self.statusBar().showMessage(f"✓ ลบเลย์เอาต์ '{name}' เรียบร้อยแล้ว", 3000)
        except Exception as e:
            self.statusBar().showMessage(f"⚠️ เกิดข้อผิดพลาดในการลบ: {e}", 3000)

    def save_layout_state(self):
        try:
            from tstudio_core import TStudioCore
            cfg = TStudioCore.load_config()
            cfg['modern_active_layout'] = getattr(self, 'current_workspace_name', 'Default (ค่าเริ่มต้น)')
            cfg['modern_splitter_sizes'] = self.main_splitter.sizes()
            cfg['modern_columns_visible'] = [
                self.col1_workspace.isVisible(),
                self.col2_glossary.isVisible(),
                self.col3_editor_stack.isVisible()
            ]
            TStudioCore.save_config(cfg)
        except Exception as e:
            print(f"Error saving modern layout state: {e}")

    def restore_layout_state(self):
        try:
            from tstudio_core import TStudioCore
            cfg = TStudioCore.load_config()
            active_layout = cfg.get('modern_active_layout', 'Default (ค่าเริ่มต้น)')
            self.current_workspace_name = active_layout

            user_layouts = cfg.get(self.layout_cfg_key, {})
            if active_layout in user_layouts:
                self.load_custom_layout(active_layout)
                return

            if active_layout == "Translator Focus":
                self.layout_translator_focus()
                return
            elif active_layout == "Glossary Review":
                self.layout_glossary_review()
                return
            elif active_layout == "Full CAT Table":
                self.layout_full_table()
                return
            elif active_layout == "Default (ค่าเริ่มต้น)":
                saved_sizes = cfg.get('modern_splitter_sizes')
                saved_vis = cfg.get('modern_columns_visible', [True, True, True])
                if saved_sizes and len(saved_sizes) == 3 and sum(saved_sizes) > 200:
                    self.col1_workspace.setVisible(saved_vis[0])
                    self.col2_glossary.setVisible(saved_vis[1])
                    self.col3_editor_stack.setVisible(saved_vis[2])
                    self.main_splitter.setSizes(saved_sizes)
                    return

            self.layout_default()
        except Exception as e:
            print(f"Error restoring layout state: {e}")
            self.layout_default()

    def switch_workspace_mode(self, mode):
        self.current_app_mode = mode
        self._update_mode_buttons_ui()

        if mode == 'studio':
            if hasattr(self, 'workspace_stack'):
                self.workspace_stack.setCurrentIndex(0)
            self.setWindowTitle(f'Translation Studio — {GAME_NAME} [✍️ โหมดแปลภาษา]')

        elif mode == 'trun':
            if hasattr(self, 'workspace_stack'):
                self.workspace_stack.setCurrentIndex(1)
            if hasattr(self, 'batch_dock'):
                self.batch_dock.sync_active_file_info()

            self.setWindowTitle(f'Translation Studio — {GAME_NAME} [⚡ โหมดรันแปลอัตโนมัติ (TRun)]')

    def _update_mode_buttons_ui(self):
        mode = getattr(self, 'current_app_mode', 'studio')
        active_ss_studio = "background: #89b4fa; color: #1e1e2e; font-weight: bold; padding: 5px 14px; border-radius: 4px;"
        active_ss_trun = "background: #a6e3a1; color: #1e1e2e; font-weight: bold; padding: 5px 14px; border-radius: 4px;"
        inactive_ss = "background: #313244; color: #a6adc8; border: 1px solid #45475a; padding: 5px 14px; border-radius: 4px;"

        if hasattr(self, 'btn_mode_studio'):
            self.btn_mode_studio.setStyleSheet(active_ss_studio if mode == 'studio' else inactive_ss)
            self.btn_mode_studio.setChecked(mode == 'studio')
        if hasattr(self, 'btn_mode_trun'):
            self.btn_mode_trun.setStyleSheet(active_ss_trun if mode == 'trun' else inactive_ss)
            self.btn_mode_trun.setChecked(mode == 'trun')

    def open_tlm_studio(self, initial_tab=0):
        """Open the advanced TLM Studio 2.0 modal dialog for lore ingestion, AI prompt studio & glossary extraction."""
        try:
            from tstudio_tlm_studio import TLMStudioDialog
            dlg = TLMStudioDialog(self, active_profile=getattr(self, 'current_profile_name', None), initial_tab=initial_tab)
            dlg.exec()
            self._profiles_data = TStudioCore.load_profiles()
            # Do NOT hijack the active profile or unload the current CSV workspace!
            # Safely refresh glossary data and top-bar sync without switching profile
            cur_prof = getattr(self, 'current_profile_name', None) or 'Default'
            if hasattr(self, 'refresh_glossary_dependent_features'):
                self.refresh_glossary_dependent_features()
            self._load_glossary_data()
            if hasattr(self, 'cbo_top_universe_tone'):
                cur_prof_data = self._profiles_data.get("presets", {}).get(cur_prof, {})
                tlm_cur = cur_prof_data.get("tlm") or cur_prof_data.get("tlm_lore") or {}
                if not isinstance(tlm_cur, dict):
                    tlm_cur = {"lore_notes": str(tlm_cur)} if tlm_cur else {}
                self._sync_top_universe_tone(tlm_cur.get("universe_tone", ""))
        except Exception as e:
            import traceback
            traceback.print_exc()
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, _("error_title"), f"Could not open TLM Studio 2.0:\n{e}")

    def toggle_tlm_dock(self):
        self.open_tlm_studio(initial_tab=0)

    def open_tlm_library(self):
        self.open_tlm_studio(initial_tab=0)

    def open_glossary(self):
        """Open or focus the Glossary Window (Column 2)."""
        if hasattr(self, 'col2_glossary') and not self.col2_glossary.isVisible():
            self.toggle_column_visibility(1, True)
        if hasattr(self, 'txt_g_search'):
            self.txt_g_search.setFocus()
            self.txt_g_search.selectAll()
        elif hasattr(self, 'txt_glossary_search'):
            self.txt_glossary_search.setFocus()
            self.txt_glossary_search.selectAll()

    def open_prompt_settings(self, initial_tab=1):
        self.open_tlm_studio(initial_tab=initial_tab)

    def open_plugin_manager(self):
        try:
            import plugin_manager_ui
            dlg = plugin_manager_ui.PluginManagerDialog(self)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, _("error_title"), _("plugin_err_open_manager", msg=str(e)))

    def open_settings(self):
        SettingsDialog(self).exec()
        self._sync_top_bar_model_selector()
        self._update_api_status_badge()
        self.setup_menu_bar()
        self.update_button_labels()

    def open_file_analyzer(self):
        """Open the Whole-File Localization Intelligence & Analytics Dashboard."""
        if not hasattr(self, 'model') or not self.model or not self.model._data:
            QMessageBox.information(self, "วิเคราะห์ไฟล์", "กรุณาเปิดไฟล์งานแปลก่อนทำการวิเคราะห์")
            return

        from tstudio_analyzer_dialog import LocalizationAnalyzerDialog

        prof = getattr(self, 'current_profile_name', None) or "Default"
        pdata = TStudioCore.get_current_profile_data(prof)
        game_title = pdata.get("game_title", "").strip() or prof
        glossary = pdata.get("glossary", {})

        dlg = LocalizationAnalyzerDialog(self.model._data, glossary=glossary, project_name=game_title, parent=self)
        dlg.jump_to_row_requested.connect(self._on_analyzer_jump_to_row)
        dlg.glossary_add_requested.connect(self._on_analyzer_add_glossary)
        dlg.exec()

    def _on_analyzer_jump_to_row(self, row_idx):
        """Jump to specific row in main table from analyzer."""
        if not hasattr(self, 'model') or not self.model or not self.model._data:
            return
        if 0 <= row_idx < len(self.model._data):
            if hasattr(self, 'filter_combo') and self.filter_combo.currentIndex() != 0:
                self.filter_combo.setCurrentIndex(0)

            src_idx = self.model.index(row_idx, 0)
            proxy_idx = self.proxy.mapFromSource(src_idx)
            if proxy_idx.isValid():
                self.table.selectRow(proxy_idx.row())
                self.table.scrollTo(proxy_idx)

    def _on_analyzer_add_glossary(self, term, trans, tag):
        """Add mined entity to project glossary."""
        prof = getattr(self, 'current_profile_name', None) or "Default"
        pdata = TStudioCore.get_current_profile_data(prof)
        if "glossary" not in pdata or not isinstance(pdata["glossary"], dict):
            pdata["glossary"] = {}
        pdata["glossary"][term] = [trans, tag or "General"]
        TStudioCore.save_profile_data(prof, pdata)
        if hasattr(self, 'refresh_glossary_dependent_features'):
            self.refresh_glossary_dependent_features()
        if hasattr(self, 'glossary_widget') and self.glossary_widget:
            self.glossary_widget.load_glossary(pdata["glossary"])

    def update_button_labels(self):
        cfg = TStudioCore.load_config()
        model = cfg.get("model", "")
        provider = cfg.get("provider", "")
        model_disp = format_model_display_name(model, provider=provider)

        icon = "💻" if (provider == "Local LLM" or model in ("custom-local-llm", "local-model") or model.startswith("qwen")) else "🤖"
        self.btn_trans_smart.setText(f"{icon} แปลด้วย {model_disp}")
        if hasattr(self, 'btn_trans_batch'):
            self.btn_trans_batch.setText(f"{icon} แปลกลุ่มด้วย {model_disp}")

        if model.startswith("gemini") or provider == "Google Gemini":
            style = "background:#a6e3a1; color:#1e1e2e; font-size:12px; padding:4px 8px; font-weight:bold;"
        elif model.startswith("claude") or provider == "Anthropic Claude":
            style = "background:#fab387; color:#1e1e2e; font-size:12px; padding:4px 8px; font-weight:bold;"
        elif model.startswith("deepseek") or provider == "DeepSeek":
            style = "background:#89b4fa; color:#1e1e2e; font-size:12px; padding:4px 8px; font-weight:bold;"
        elif provider == "Local LLM" or model.startswith("qwen") or model.startswith("llama") or model == "custom-local-llm":
            style = "background:#cba6f7; color:#1e1e2e; font-size:12px; padding:4px 8px; font-weight:bold;"
        else:
            style = "background:#89b4fa; color:#1e1e2e; font-size:12px; padding:4px 8px; font-weight:bold;"

        self.btn_trans_smart.setStyleSheet(style)
        if hasattr(self, 'btn_trans_batch'):
            self.btn_trans_batch.setStyleSheet(style)

        # Guide Mode overrides all button colors to purple
        if getattr(self, 'chk_guide_mode', None) and self.chk_guide_mode.isChecked():
            purple_style = "background:#cba6f7; color:#1e1e2e; font-size:12px; padding:4px 8px; font-weight:bold;"
            self.btn_trans_smart.setStyleSheet(purple_style)
            if hasattr(self, 'btn_trans_opt'):
                self.btn_trans_opt.setStyleSheet(purple_style)
            if hasattr(self, 'btn_trans_special'):
                self.btn_trans_special.setStyleSheet(purple_style)
            if hasattr(self, 'btn_trans_batch'):
                self.btn_trans_batch.setStyleSheet(purple_style)
        else:
            # Restore default colors for non-primary buttons
            if hasattr(self, 'btn_trans_opt'):
                self.btn_trans_opt.setStyleSheet("background:#f9e2af; color:#1e1e2e; font-size:12px; padding:4px 8px;")
            if hasattr(self, 'btn_trans_special'):
                self.btn_trans_special.setStyleSheet("background:#fab387; color:#1e1e2e; font-size:12px; padding:4px 8px;")


    def rename_profile(self):
        active = self.cbo_profile.currentText()
        if active == "Default":
            QMessageBox.warning(self, _("warning_title"), _("cannot_rename_default"))
            return
            
        from PyQt6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, _("rename_profile_title"), f"Enter new name for '{active}':", text=active)
        if ok and new_name.strip():
            new_name = new_name.strip()
            if new_name == active:
                return
            if new_name in self._profiles_data.get("presets", {}):
                QMessageBox.warning(self, _("warning_title"), f"Profile '{new_name}' already exists.")
                return
                
            self._profiles_data.setdefault("presets", {})[new_name] = self._profiles_data["presets"].pop(active)
            self._profiles_data["active_preset"] = new_name
            TStudioCore.save_profiles(self._profiles_data)
            
            self._is_loading_profiles = True
            idx = self.cbo_profile.currentIndex()
            self.cbo_profile.setItemText(idx, new_name)
            self.cbo_profile.setCurrentText(new_name)
            self._is_loading_profiles = False
            self.on_profile_changed(new_name)
            self.statusBar().showMessage(f"Profile renamed to '{new_name}'.", 3000)

    def delete_profile(self):
        active = self.cbo_profile.currentText()
        if active == "Default":
            QMessageBox.warning(self, _("warning_title"), _("cannot_delete_default"))
            return
            
        reply = QMessageBox.question(self, _("confirm_delete_title"), f"Are you sure you want to delete profile '{active}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._profiles_data.get("presets", {}).pop(active, None)
            self._profiles_data["active_preset"] = "Default"
            TStudioCore.save_profiles(self._profiles_data)
            self._is_loading_profiles = True
            self.cbo_profile.clear()
            self.cbo_profile.addItems(list(self._profiles_data.get("presets", {}).keys()))
            self.cbo_profile.setCurrentText("Default")
            self._is_loading_profiles = False
            
            self.on_profile_changed("Default")
            self.statusBar().showMessage(f"Profile '{active}' deleted.", 3000)

    def export_profile(self):
        active = self.cbo_profile.currentText()
        data = self._profiles_data["presets"].get(active)
        if data is None:
            QMessageBox.warning(self, _("warning_title"), f"Profile '{active}' not found.")
            return
        file_path, file_ext = QFileDialog.getSaveFileName(self, "Export Profile", f"{active}_profile.json", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                self.statusBar().showMessage(f"Profile exported to {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, _("error_title"), f"Failed to export profile:\n{e}")

    def import_profile(self):
        file_path, file_ext = QFileDialog.getOpenFileName(self, _("import_profile_title"), "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if "single" not in data or "opt" not in data or "glossary" not in data:
                    QMessageBox.warning(self, _("invalid_file_title"), _("invalid_profile_file"))
                    return
                    
                from PyQt6.QtWidgets import QInputDialog, QLineEdit
                import os
                base_name = os.path.basename(file_path)
                if base_name.lower().endswith(".json"):
                    base_name = base_name[:-5]
                if base_name.lower().endswith("_profile"):
                    base_name = base_name[:-8]
                
                name, ok = QInputDialog.getText(
                    self, 
                    _("import_profile_title"), 
                    _("import_profile_prompt"), 
                    QLineEdit.EchoMode.Normal, 
                    base_name
                )
                if ok and name.strip():
                    name = name.strip()
                    if name in self._profiles_data["presets"]:
                        reply = QMessageBox.question(
                            self,
                            _("import_profile_title"),
                            _("profile_overwrite_confirm").format(name=name),
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.No:
                            return
                    self._profiles_data["presets"][name] = data
                    self._profiles_data["active_preset"] = name
                    TStudioCore.save_profiles(self._profiles_data)
                    
                    self._is_loading_profiles = True
                    if self.cbo_profile.findText(name) == -1:
                        self.cbo_profile.addItem(name)
                    self.cbo_profile.setCurrentText(name)
                    self._is_loading_profiles = False
                    
                    self.on_profile_changed(name)
                    self.statusBar().showMessage(f"Profile '{name}' imported.", 3000)
            except Exception as e:
                QMessageBox.critical(self, _("error_title"), f"Failed to import profile:\n{e}")

    def unload_csv(self):
        """Cleanly unloads the active CSV file, resetting the table, editor, and stats."""
        if hasattr(self, 'file_watcher') and self.file_watcher and getattr(self, 'csv_path', None):
            try:
                self.file_watcher.removePath(self.csv_path)
            except Exception:
                pass
        self.csv_path = None
        self.project_path = None
        if hasattr(self, 'model') and self.model:
            self.model.clear()
        self.current_source_row = -1
        for attr in ('txt_source', 'txt_ai', 'txt_trans'):
            if hasattr(self, attr):
                widget = getattr(self, attr)
                widget.blockSignals(True)
                widget.clear()
                widget.blockSignals(False)
        self.update_progress_stats()
        if hasattr(self, 'batch_dock'):
            self.batch_dock.sync_active_file_info()

    def on_profile_changed(self, text):
        if not text: return

        # Check for unsaved changes in current CSV before switching profiles
        if hasattr(self, 'model') and getattr(self.model, 'is_dirty', False) and getattr(self, 'csv_path', None):
            reply = QMessageBox.question(
                self, _("unsaved_changes_title"),
                "คุณมีการแปลที่ยังไม่ได้บันทึกในไฟล์ปัจจุบัน ต้องการบันทึกก่อนเปลี่ยนโปรไฟล์หรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.save_csv()
            elif reply == QMessageBox.StandardButton.Cancel:
                if hasattr(self, 'cbo_profile') and getattr(self, 'current_profile_name', None):
                    self._is_loading_profiles = True
                    self.cbo_profile.setCurrentText(self.current_profile_name)
                    self._is_loading_profiles = False
                return

        self.current_profile_name = text

        # Sync cbo_profile safely if called programmatically
        if hasattr(self, 'cbo_profile') and not self._is_loading_profiles:
            if self.cbo_profile.currentText() != text:
                self._is_loading_profiles = True
                if self.cbo_profile.findText(text) == -1:
                    self.cbo_profile.addItem(text)
                self.cbo_profile.setCurrentText(text)
                self._is_loading_profiles = False

        # Load fresh data & persist active_preset
        fresh_data = TStudioCore.load_profiles()
        fresh_data["active_preset"] = text
        TStudioCore.save_profiles(fresh_data)
        self._profiles_data = fresh_data

        # Dynamically sync game project workspace to matching profile
        ws = None
        if text.strip().lower() != 'default':
            ws = TStudioCore.get_translation_workspace_dir(profile_name=text, create_if_missing=False)
            if ws and os.path.isdir(ws):
                game_root = os.path.dirname(ws) if os.path.basename(ws).lower() == '02_translation_workspace' else ws
                self.project_dir = game_root
                self.project_path = game_root
                TStudioCore.set_project_path(game_root)
            else:
                self.project_dir = None
                self.project_path = None
                TStudioCore.set_project_path(None)
        else:
            self.project_dir = None
            self.project_path = None
            TStudioCore.set_project_path(None)

        # File ownership verification: ensure loaded CSV actually belongs to this profile's workspace
        curr_csv = getattr(self, 'csv_path', None)
        curr_csv_valid_for_profile = False
        if curr_csv and os.path.exists(curr_csv):
            curr_csv_valid_for_profile = self._is_csv_owned_by_profile(curr_csv, text)

        if not curr_csv_valid_for_profile:
            # Need to switch or unload file
            found_csv = None
            if ws and os.path.isdir(ws):
                found_csv = self._find_csv_in_project_dir(ws)
            if not found_csv and self.project_dir and os.path.isdir(self.project_dir):
                found_csv = self._find_csv_in_project_dir(self.project_dir)

            if found_csv:
                self.csv_path = found_csv
                self._load_csv()
            else:
                self.unload_csv()
                mode_label = f"[{self.current_app_mode.upper()}]" if hasattr(self, 'current_app_mode') else ""
                title_str = f"Translation Studio — {text}"
                if mode_label:
                    title_str += f" {mode_label}"
                self.setWindowTitle(title_str)
                if hasattr(self, 'btn_breadcrumb'):
                    self.btn_breadcrumb.setText(f"📁 {text} › (คลิกเพื่อเลือกไฟล์)")
                    self.btn_breadcrumb.setToolTip("คลิกเพื่อเปิดไฟล์หรือโปรเจกต์แปล")
        else:
            # CSV belongs to this profile, update breadcrumb
            if hasattr(self, 'btn_breadcrumb'):
                self.btn_breadcrumb.setText(f"📁 {text} › {os.path.basename(self.csv_path)}")
                self.btn_breadcrumb.setToolTip(self.csv_path)

        # Update per-profile max_bytes_limit
        prof_data = fresh_data.get("presets", {}).get(text, {})
        self.max_bytes_limit = prof_data.get("max_bytes_limit", 0)

        # Sync top bar universe tone selector
        if hasattr(self, 'cbo_top_universe_tone'):
            tlm = prof_data.get("tlm") or prof_data.get("tlm_lore") or {}
            if not isinstance(tlm, dict):
                tlm = {"lore_notes": str(tlm)} if tlm else {}
            tone = tlm.get("universe_tone", "")
            self._sync_top_universe_tone(tone)

        # Clear undo/redo stacks on profile switch
        if hasattr(self, '_glossary_history'): self._glossary_history.clear()
        if hasattr(self, '_glossary_redo_stack'): self._glossary_redo_stack.clear()

        # Reload Column 2 Glossary Table
        self._load_glossary_data()

        # Refresh dependent features (QA highlights, in-context chips)
        self.refresh_glossary_dependent_features()
        if hasattr(self, 'current_source_row') and self.current_source_row >= 0:
            if hasattr(self, 'model') and self.model and getattr(self.model, '_data', None) and self.current_source_row < len(self.model._data):
                self.select_source_row(self.current_source_row)

        g_count = len(prof_data.get("glossary", {}))
        self.statusBar().showMessage(f"● สลับโปรไฟล์เป็น: '{text}' (คำศัพท์: {g_count} คำ | byte limit: {self.max_bytes_limit or 'ไม่จำกัด'})", 3500)

    def create_new_profile(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, _("new_profile_title"), _("new_profile_prompt"))
        if ok and name.strip():
            name = name.strip()
            self._profiles_data = TStudioCore.load_profiles()
            if name not in self._profiles_data.get("presets", {}):
                self._profiles_data.setdefault("presets", {})[name] = {
                    "single": DEFAULT_SINGLE_PROMPT,
                    "opt": DEFAULT_OPTIONS_PROMPT,
                    "batch": DEFAULT_SINGLE_PROMPT,
                    "glossary": {},
                    "max_bytes_limit": 0
                }
                self._profiles_data["active_preset"] = name
                TStudioCore.save_profiles(self._profiles_data)
                
                self._is_loading_profiles = True
                self.cbo_profile.addItem(name)
                self.cbo_profile.setCurrentText(name)
                self._is_loading_profiles = False
                
                self.on_profile_changed(name)
            else:
                self.cbo_profile.setCurrentText(name)

    def open_project_dialog(self):
        if hasattr(self, 'model') and getattr(self.model, 'is_dirty', False):
            reply = QMessageBox.question(self, _("unsaved_changes_title"), "You have unsaved translations. Do you want to save before opening a project?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                self.save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        target_dir = self.get_active_translation_workspace()
        file_path, file_ext = QFileDialog.getOpenFileName(self, "Open Project", target_dir, "TStudio Project (*.tproj);;All Files (*.*)")
        if file_path:
            self.load_project(file_path)

    def load_project(self, project_path):
        import json
        try:
            with open(project_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            csv_path = data.get("csv_file")
            if csv_path and os.path.exists(csv_path):
                self.project_path = project_path
                self.csv_path = csv_path
                self._load_csv()
                self.setWindowTitle(f"Translation Studio - {os.path.basename(project_path)}")
                
                active_profile = data.get("active_profile")
                if active_profile:
                    self.cbo_profile.setCurrentText(active_profile)
                    
                last_row = data.get("last_selected_row")
                if last_row is not None and last_row >= 0 and last_row < self.proxy.rowCount():
                    self.table.selectRow(last_row)
                    
            else:
                QMessageBox.warning(self, _("error_title"), f"CSV file not found:\n{csv_path}")
        except Exception as e:
            QMessageBox.critical(self, _("error_title"), f"Failed to load project:\n{str(e)}")

    def save_project(self):
        if not self.model or not self.model._data:
            QMessageBox.warning(self, _("error_title"), "No project loaded to save.")
            return
            
        if not self.project_path:
            target_dir = self.get_active_translation_workspace()
            file_path, file_ext = QFileDialog.getSaveFileName(self, "Save Project As", target_dir, "TStudio Project (*.tproj)")
            if not file_path:
                return
            if not file_path.endswith('.tproj'):
                file_path += '.tproj'
            self.project_path = file_path
            self.setWindowTitle(f"Translation Studio - {os.path.basename(file_path)}")

        self.save_csv()
        
        import json
        try:
            current_row = -1
            if self.table.selectionModel().hasSelection():
                current_row = self.table.selectionModel().selectedRows()[0].row()
                
            data = {
                "csv_file": self.csv_path,
                "active_profile": self._profiles_data.get("active_preset", "Default"),
                "last_selected_row": current_row
            }
            with open(self.project_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            self.statusBar().showMessage(f"Project saved to {os.path.basename(self.project_path)}", 5000)
            QMessageBox.information(self, _("save_success_title"), f"Project saved successfully to:\n{self.project_path}")
        except Exception as e:
            QMessageBox.critical(self, _("error_title"), f"Failed to save project:\n{str(e)}")

    def save_csv_as(self):
        if getattr(getattr(self, 'model', None), 'csv_read_error', None):
            return False
        if hasattr(self, '_trans_save_timer') and self._trans_save_timer.isActive():
            self._trans_save_timer.stop()
            self.on_trans_changed()

        if not self.model or not self.model._data:
            QMessageBox.warning(self, _("error_title"), _("no_data_save"))
            return
        from tstudio_core import TStudioCore
        target_dir = self.get_active_translation_workspace()
        file_path, file_ext = QFileDialog.getSaveFileName(self, _("save_csv_as_title"), self.csv_path or target_dir, "CSV Files (*.csv)")
        if file_path:
            TStudioCore.set_last_dir(file_path)
            import tempfile, shutil
            tmp_fd, tmp_path = tempfile.mkstemp(
                dir=os.path.dirname(os.path.abspath(file_path)),
                suffix='.tmp'
            )
            try:
                with os.fdopen(tmp_fd, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    headers = getattr(self.model, 'headers_row', None) or getattr(self.model, 'headers', None)
                    if headers:
                        writer.writerow(headers)
                    else:
                        writer.writerow([_("col_id"), _("col_source"), _("col_translation"), "AI Reference"])
                    col_id = getattr(self.model, 'col_id', COL_ID)
                    col_src = getattr(self.model, 'col_src', COL_SOURCE)
                    col_trans = getattr(self.model, 'col_trans', COL_TRANS)
                    col_ai = getattr(self.model, 'col_ai', COL_AI_REF)
                    target_len = len(headers) if headers else (max(col_id, col_src, col_trans, col_ai) + 1)

                    for item in self.model._data:
                        raw = item.get("raw_row")
                        if raw is not None:
                            row = list(raw)
                        else:
                            row = [''] * target_len
                        while len(row) < target_len:
                            row.append('')
                        if col_id < len(row): row[col_id] = item["id"]
                        if col_src < len(row): row[col_src] = item["source"]
                        if col_trans < len(row): row[col_trans] = item["trans"]
                        if 0 <= col_ai < len(row) and "ai_ref" in item:
                            row[col_ai] = str(item.get("ai_ref") or "")
                        writer.writerow(row)
                shutil.move(tmp_path, file_path)
                QMessageBox.information(self, _("success_title"), f"CSV saved successfully to:\n{os.path.basename(file_path)}")
            except Exception as e:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                QMessageBox.critical(self, _("error_title"), f"Failed to save CSV:\n{e}")

    def _load_csv(self):
        if not self.csv_path or not os.path.exists(self.csv_path):
            return
        count = self.model.load_csv(self.csv_path, self.csv_encoding, COL_ID, COL_SOURCE, COL_TRANS, COL_AI_REF)
        if getattr(self.model, 'csv_read_error', None):
            QMessageBox.warning(self, "CSV validation error", "รูปแบบ CSV หรือ encoding ไม่ผ่าน เปิดเพื่อดูเท่านั้น กรุณาตรวจไฟล์ต้นฉบับและ encoding ก่อนบันทึกหรือแปล")
        mode_label = f"[{self.current_app_mode.upper()}]" if hasattr(self, 'current_app_mode') else ""
        
        prof = getattr(self, 'current_profile_name', None) or "Default"
        pdata = TStudioCore.get_current_profile_data(prof) if hasattr(TStudioCore, 'get_current_profile_data') else {}
        game_title = pdata.get("game_title", "").strip() if isinstance(pdata, dict) else ""
        if not game_title and getattr(self, 'project_dir', None):
            game_title = os.path.basename(self.project_dir)
        game_display = game_title if game_title and game_title != "Default" else (prof if prof != "Default" else "TStudio")
        fname = os.path.basename(self.csv_path) if getattr(self, 'csv_path', None) else ""
        
        title_str = f"Translation Studio — {game_display}"
        if fname:
            title_str += f" ({fname})"
        if mode_label:
            title_str += f" {mode_label}"
        self.setWindowTitle(title_str)

        self.statusBar().showMessage(f'Loaded {count:,} entries from {fname}')
        self.update_progress_stats()
        self._auto_load_companion_glossary()
        if hasattr(self, 'batch_dock'):
            self.batch_dock.sync_active_file_info()

        if self.proxy.rowCount() > 0:
            self.select_row_by_proxy(0)
        else:
            self.current_source_row = -1
            for w in [self.txt_source, self.txt_ai, self.txt_trans]:
                w.blockSignals(True)
                w.clear()
                w.blockSignals(False)
            if hasattr(self, 'lbl_src_char_count'):
                self.lbl_src_char_count.setText("0 ตัวอักษร")
            if hasattr(self, 'lbl_trans_char_count'):
                self.lbl_trans_char_count.setText("0 ตัวอักษร")

    def open_merge_dialog(self):
        dlg = MergeTranslatedDialog(self)
        if dlg.exec():
            if dlg.merged_csv_path and os.path.exists(dlg.merged_csv_path):
                self.csv_path = dlg.merged_csv_path
                self._load_csv()
                self.model.set_ai_column_name("Merge Translation")
                self.statusBar().showMessage(f"Loaded merged file: {os.path.basename(self.csv_path)}", 5000)

    def new_project_from_file(self, file_path=None):
        if not isinstance(file_path, str) or not file_path:
            file_path = None

        if hasattr(self, 'model') and getattr(self.model, 'is_dirty', False):
            reply = QMessageBox.question(self, _("unsaved_changes_title"), _("unsaved_before_open"), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                self.save_csv()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        target_dir = self.get_active_translation_workspace()
        if not file_path:
            file_path, file_ext = QFileDialog.getOpenFileName(
                self,
                _("open_import_file_title"),
                target_dir,
                "Supported Files (*.csv *.tproj *.lor *.locres *.tex *.bundle *.ttarch2 *.win *.txt *.srt *.vtt *.json *.lang *.pak);;TStudio Projects (*.tproj);;CSV Files (*.csv);;Subtitle Files (*.srt *.vtt);;Locres Files (*.locres *.lor);;LANG Files (*.lang);;Texture Files (*.tex);;Unity Bundles (*.bundle *.txt *.json);;PAK Files (*.pak);;All Files (*.*)"
            )
        if file_path:
            file_path = os.path.normpath(file_path)
            from tstudio_core import TStudioCore
            TStudioCore.set_last_dir(file_path)
            if "02_translation_workspace" in file_path.lower():
                idx = file_path.lower().find("02_translation_workspace")
                game_dir = file_path[:idx].rstrip(r"\/")
                if game_dir and os.path.isdir(game_dir):
                    self.project_dir = os.path.normpath(game_dir)
                    TStudioCore.set_project_path(self.project_dir)
            if file_path.lower().endswith('.tproj'):
                self.load_project(file_path)
                return
            if file_path.lower().endswith('.ttarch2'):
                self.open_telltale_archive(file_path)
                return
            self.statusBar().showMessage(_("loading_file_status"))
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            def run_convert():
                try:
                    from tbundle_manager import TBundleManager
                    if TBundleManager.is_unity_bundle(file_path):
                        csv_out = TBundleManager.extract_text_to_csv(file_path)
                        if csv_out:
                            return csv_out
                except Exception as e:
                    print(f"Bundle extract error: {e}")
                    
                try:
                    if file_path.lower().endswith('.win'):
                        import sys
                        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Core"))
                        from utmt_handler import UTMTHandler
                        csv_out = UTMTHandler.extract_strings_to_csv(file_path)
                        if csv_out:
                            from tstudio_core import TStudioCore
                            cfg = TStudioCore.load_config()
                            cfg["origin_file"] = file_path
                            TStudioCore.save_config(cfg)
                            return csv_out
                except Exception as e:
                    print(f"UTMT extract error: {e}")
                    
                try:
                    if file_path.lower().endswith('.txt'):
                        import re, csv as _csv
                        with open(file_path, 'r', encoding='utf-8-sig', errors='replace') as f:
                            raw = f.readlines()
                        
                        # Detect TellTale format: lines starting with "N) " or "N) CHARACTER"
                        id_pattern = re.compile(r'^(\d+)\)\s*(.*)')
                        entries = []
                        i = 0
                        while i < len(raw):
                            m = id_pattern.match(raw[i].strip())
                            if m:
                                line_id = m.group(1)
                                character = m.group(2).strip()
                                text = ''
                                if i + 1 < len(raw):
                                    next_line = raw[i + 1].strip()
                                    if next_line and not id_pattern.match(next_line):
                                        text = next_line
                                        i += 1  # consume text line
                                entries.append((line_id, character, text))
                            i += 1
                        
                        # Need at least 10 entries to be confident it's TellTale format
                        if len(entries) >= 5:
                            import os as _os
                            base = _os.path.splitext(file_path)[0]
                            csv_out = base + '_telltale.csv'
                            with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
                                writer = _csv.writer(f)
                                writer.writerow([_("col_id"), _("col_source"), _("col_translation"), 'AI_Reference'])
                                for (lid, char, text) in entries:
                                    if text:  # skip empty lines
                                        row_id = f"{lid}"
                                        if char:
                                            row_id = f"{lid}_{char.replace(' ', '_')}"
                                        writer.writerow([row_id, text, '', char])
                            return csv_out
                except Exception as e:
                    print(f"TellTale txt parse error: {e}")

                # Hardcoded JSON parser removed to allow CustomParsers plugin system to handle .json
                    
                return file_converter.auto_convert_to_csv(file_path, None) # Don't pass UI to thread
                
            def on_success(converted_path):
                QApplication.restoreOverrideCursor()
                if converted_path:
                    self.project_path = None
                    self.setWindowTitle("Translation Studio - Unsaved Project")
                    from tstudio_core import TFormatManager
                    if not TFormatManager.is_standard_csv(converted_path):
                        headers = TFormatManager.get_headers(converted_path)
                        from tstudio_ui_shared import SmartImportDialog
                        dlg = SmartImportDialog(headers, self)
                        if dlg.exec() == QDialog.DialogCode.Accepted:
                            mapping = dlg.get_mapping()
                            try:
                                converted_path = TFormatManager.format_to_standard(converted_path, mapping)
                                QMessageBox.information(self, _("tformat_title"), _("tformat_formatted_msg"))
                            except Exception as e:
                                QMessageBox.critical(self, _("error_title"), f"Failed to format: {e}")
                                return
                        else:
                            return
                    self.csv_path = converted_path
                    
                    # Save origin_file in config!
                    from tstudio_core import TStudioCore
                    cfg = TStudioCore.load_config()
                    cfg["origin_file"] = file_path
                    TStudioCore.save_config(cfg)
                    
                    self._load_csv()
                    
            def on_error(err):
                QApplication.restoreOverrideCursor()
                QMessageBox.critical(self, _("file_error_title"), f"Failed to open or convert file:\n{err}")
                
            worker = ApiWorker(run_convert)
            forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
            worker.signals.finished.connect(forwarder.handle_finished)
            worker.signals.error.connect(forwarder.handle_error)
            self.threadpool.start(worker)


    def open_telltale_archive(self, file_path=None):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication
        import os
        
        if file_path is None:
            file_path, file_ext = QFileDialog.getOpenFileName(self, _("select_telltale_title"), BASE_DIR, "Telltale Archives (*.ttarch2);;All Files (*.*)")
        if not file_path:
            return
            
        manager = TelltaleManager()
        missing = manager.check_tools()
        if missing:
            QMessageBox.critical(self, _("telltale_tools_missing_title"), f"Cannot extract Telltale archives because the following tools are missing:\n{', '.join(missing)}\n\nPlease download them and place them in the 'telltale_tools' folder inside 'Core'.")
            return
            
        self.statusBar().showMessage(f"Extracting {os.path.basename(file_path)}...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        proj_dir = os.path.dirname(file_path)
        temp_dir = os.path.join(proj_dir, ".tstudio_temp", os.path.basename(file_path).replace('.', '_'))
        
        success, msg = manager.extract_ttarch2(file_path, temp_dir)
        QApplication.restoreOverrideCursor()
        
        if not success:
            QMessageBox.critical(self, _("extraction_error_title"), f"Failed to extract archive:\n{msg}")
            return
            
        # Auto-detect English .landb files
        import glob
        landb_files = glob.glob(os.path.join(temp_dir, "*english.landb"))
        if not landb_files:
            landb_files = glob.glob(os.path.join(temp_dir, "*.landb"))
            
        if not landb_files:
            QMessageBox.warning(self, _("no_landb_title"), f"No translation files found in the archive.\n{temp_dir}")
            return
            
        # We will merge ALL found .landb files into one CSV!
        csv_path = os.path.join(temp_dir, "combined_translation.landb.csv")
        try:
            manager.convert_landb_to_csv(landb_files, csv_path)
            self.csv_path = csv_path
            self._load_csv()
            QMessageBox.information(self, _("success_title"), _("loaded_telltale_success"))
        except Exception as e:
            QMessageBox.critical(self, _("error_title"), f"Failed to parse .landb:\n{str(e)}")
    def _compile_glossary_cache(self):
        """Pre-compiles glossary regex pattern and lookup dictionary into memory for ultra-fast matching."""
        try:
            prof_name = getattr(self, 'current_profile_name', None) or "Default"
            if hasattr(self, '_profiles_data') and isinstance(self._profiles_data, dict):
                profile = self._profiles_data.get("presets", {}).get(prof_name, {})
            else:
                from tstudio_core import TStudioCore
                profile = TStudioCore.get_current_profile_data(prof_name)
            glossary = profile.get("glossary", {}) if isinstance(profile, dict) else {}

            if not isinstance(glossary, dict) or not glossary:
                self._cached_glossary_pat = None
                self._cached_term_info = {}
                return

            sorted_glossary = sorted(glossary.items(), key=lambda x: len(str(x[0])), reverse=True)
            subpatterns = []
            term_info = {}
            for eng, val in sorted_glossary:
                eng_str = str(eng).strip()
                # Skip empty or 1-character terms to prevent matching every single character
                if not eng_str or len(eng_str) < 2:
                    continue
                target = val[0] if (isinstance(val, list) and len(val) > 0) else str(val or "")
                tag = val[1] if (isinstance(val, list) and len(val) > 1) else "General"
                icon = TagIconDelegate.TAG_MAP.get(tag, ("🏷️",))[0]
                term_info[eng_str.lower()] = (eng_str, target, tag, icon)

                esc = re.escape(html.escape(eng_str))
                pfx = r'\b' if re.match(r'^\w', eng_str) else r''
                sfx = r'\b' if re.search(r'\w$', eng_str) else r''
                sub = f"{pfx}{esc}{sfx}".strip()
                if sub:
                    subpatterns.append(sub)

            if subpatterns:
                combined = "|".join(subpatterns)
                self._cached_glossary_pat = re.compile(rf"({combined})", re.IGNORECASE)
                self._cached_term_info = term_info
            else:
                self._cached_glossary_pat = None
                self._cached_term_info = {}
        except Exception as e:
            print(f"[Warning] _compile_glossary_cache error: {e}")
            self._cached_glossary_pat = None
            self._cached_term_info = {}

    def update_html_sources(self):
        """
        O(1) Lazy Viewport Caching for Glossary Highlights:
        Bumps the cache generation version and triggers viewport repaint.
        Cells compute HTML highlights on-demand as they become visible,
        eliminating main-thread freezes on large 70,000+ row files.
        """
        try:
            self._compile_glossary_cache()
            self._html_cache_version = getattr(self, '_html_cache_version', 0) + 1
            if hasattr(self, 'table') and self.table:
                self.table.viewport().update()
        except Exception as e:
            print(f"[Warning] update_html_sources suppressed: {e}")

    def on_row_selected(self, current, previous):
        if getattr(self, '_is_selecting_row', False):
            return
        self._is_selecting_row = True
        try:
            # Flush any pending changes before changing the selected row
            if hasattr(self, '_trans_save_timer') and self._trans_save_timer.isActive():
                self._trans_save_timer.stop()
                self.on_trans_changed()

            # Save immediately on row change if there are unsaved changes
            if hasattr(self, '_csv_auto_save_timer') and self._csv_auto_save_timer.isActive():
                self._csv_auto_save_timer.stop()
                self.silent_save_csv()

            if not current.isValid():
                self.current_source_row = -1
                for w in [self.txt_source, self.txt_ai, self.txt_trans]:
                    w.blockSignals(True)
                    w.clear()
                    w.blockSignals(False)
                return
            if not hasattr(self, 'proxy') or not self.proxy:
                return
            if current.model() != self.proxy or current.row() < 0 or current.row() >= self.proxy.rowCount():
                return
            try:
                src = self.proxy.mapToSource(current)
            except Exception:
                return
            if not src.isValid():
                return
            row = src.row()
            # Guard: bounds check in case the model was reset (e.g. Find & Replace) between
            # the selection signal and this handler executing.
            if not hasattr(self, 'model') or not self.model or not getattr(self.model, '_data', None):
                return
            if row < 0 or row >= len(self.model._data):
                return
            self.current_source_row = row
            item = self.model._data[self.current_source_row]
            raw_source = item.get("source")
            source_text = str(raw_source) if raw_source is not None else ""
            
            # Fast-path: Set plain text immediately so user experiences instant responsiveness
            self.txt_source.blockSignals(True)
            self.txt_source.setPlainText(source_text)
            self.txt_source.blockSignals(False)

            # Debounce heavy in-context glossary highlights & chips to avoid freezing during rapid arrow-key navigation
            if not hasattr(self, '_editor_glossary_timer'):
                self._editor_glossary_timer = QTimer(self)
                self._editor_glossary_timer.setSingleShot(True)
                self._editor_glossary_timer.timeout.connect(self._refresh_current_row_editor_glossary)
            self._editor_glossary_timer.start(25)

            # Update AI and Trans boxes
            raw_trans = item.get("trans")
            trans_text = str(raw_trans) if raw_trans is not None else ""
            for w, val in [(self.txt_ai, str(item.get("ai_ref") or "")), (self.txt_trans, trans_text)]:
                w.blockSignals(True)
                w.setPlainText(val.replace('\r\n', '\n').replace('\r', '\n'))
                w.blockSignals(False)

            # Reset 3-style preview cards for newly selected row
            if hasattr(self, 'ai_style_cards'):
                for _, lbl_prev in self.ai_style_cards:
                    lbl_prev.setText("— กด '💡 3 สไตล์' เพื่อขอคำแปล —")

            # Update Masterpiece character counts
            if hasattr(self, 'lbl_src_char_count'):
                self.lbl_src_char_count.setText(f"{len(source_text)} ตัวอักษร")
            if hasattr(self, 'lbl_trans_char_count'):
                self.lbl_trans_char_count.setText(f"{len(trans_text)} ตัวอักษร")
        finally:
            self._is_selecting_row = False

    def _refresh_current_row_editor_glossary(self):
        """Safely refreshes txt_source highlights and glossary chips for active row without touching proxy or selection models."""
        try:
            if not hasattr(self, 'current_source_row') or self.current_source_row < 0:
                return
            if not hasattr(self, 'model') or not self.model or not getattr(self.model, '_data', None):
                return
            if self.current_source_row >= len(self.model._data):
                return

            item = self.model._data[self.current_source_row]
            raw_source = item.get("source")
            source_text = str(raw_source) if raw_source is not None else ""

            is_marker_enabled = True
            if hasattr(self, 'act_toggle_qa_marker') and not self.act_toggle_qa_marker.isChecked():
                is_marker_enabled = False

            if not hasattr(self, '_cached_glossary_pat'):
                self._compile_glossary_cache()

            pat = getattr(self, '_cached_glossary_pat', None)
            term_info = getattr(self, '_cached_term_info', {})

            matched_terms = []
            matched_chips = []

            if is_marker_enabled and pat and source_text and term_info:
                escaped_source = html.escape(source_text)
                found_keys = set()
                for m in pat.finditer(escaped_source):
                    matched_grp = m.group(1)
                    if not matched_grp:
                        continue
                    matched_lower = matched_grp.lower()
                    if matched_lower in term_info and matched_lower not in found_keys:
                        found_keys.add(matched_lower)
                        orig_en, orig_th, tag, icon = term_info[matched_lower]
                        matched_terms.append(f"{orig_en} ({orig_th})")
                        matched_chips.append((orig_en, orig_th, tag, icon))

                if matched_terms:
                    SPAN_TEMPLATE = r'<span style="background-color:#f9e2af; color:#11111b; font-weight:bold; padding:0 2px; border-radius:2px;">\1</span>'
                    highlighted_source = pat.sub(SPAN_TEMPLATE, escaped_source)
                    if hasattr(self, 'lbl_glossary_cheat'):
                        self.lbl_glossary_cheat.setText(_("glossary_cheat").format(terms=", ".join(matched_terms)))
                        self.lbl_glossary_cheat.show()
                    self.txt_source.blockSignals(True)
                    html_source = highlighted_source.replace('\n', '<br>')
                    self.txt_source.setHtml(f'<div style="font-family: inherit; font-size: inherit; white-space: pre-wrap;">{html_source}</div>')
                    self.txt_source.blockSignals(False)
                else:
                    if hasattr(self, 'lbl_glossary_cheat'):
                        self.lbl_glossary_cheat.hide()
                    self.txt_source.blockSignals(True)
                    self.txt_source.setPlainText(source_text)
                    self.txt_source.blockSignals(False)
            else:
                if hasattr(self, 'lbl_glossary_cheat'):
                    self.lbl_glossary_cheat.hide()
                self.txt_source.blockSignals(True)
                self.txt_source.setPlainText(source_text)
                self.txt_source.blockSignals(False)

            # Clear any dangling text selection pill
            if hasattr(self, '_clear_selection_pill'):
                self._clear_selection_pill()

            # Update Masterpiece in-context glossary chips safely
            if hasattr(self, 'glossary_chips_layout'):
                current_chip_keys = tuple((c[0], c[1]) for c in matched_chips)
                if getattr(self, '_rendered_chip_keys', None) != current_chip_keys:
                    self._rendered_chip_keys = current_chip_keys
                    while self.glossary_chips_layout.count() > 0:
                        child = self.glossary_chips_layout.takeAt(0)
                        if child:
                            w = child.widget()
                            if w:
                                w.setParent(None)
                                w.deleteLater()
                    for orig_en, target, tag, icon in matched_chips:
                        chip = QPushButton(f"{icon} {orig_en} ➔ {target} ➕")
                        chip.setProperty("class", "glossary-chip")
                        chip.clicked.connect(lambda _, t=target: self._insert_chip_text(t))
                        self.glossary_chips_layout.addWidget(chip)
        except Exception as e:
            print(f"[Warning] _refresh_current_row_editor_glossary error: {e}")

    def on_trans_changed(self):
        if self.current_source_row >= 0:
            # Guard: bounds check — model may have been reset (e.g. Find & Replace) while
            # the save-timer was pending, making current_source_row stale.
            if not hasattr(self, 'model') or not self.model or not getattr(self.model, '_data', None):
                return
            if self.current_source_row >= len(self.model._data):
                return
            raw_old = self.model._data[self.current_source_row].get("trans")
            old_text = str(raw_old) if raw_old is not None else ""
            new_text = self.txt_trans.toPlainText().replace('\r\n', '\n')
            if old_text != new_text:
                try:
                    self._is_internal_trans_sync = True
                    self.model.update_trans(self.current_source_row, new_text)
                    self._update_stats_for_row(self.current_source_row, old_text, new_text)
                finally:
                    self._is_internal_trans_sync = False

    def _on_table_data_changed(self, top_left, bottom_right, roles):
        # Ignore dataChanged triggered internally by typing inside txt_trans
        if getattr(self, '_is_internal_trans_sync', False):
            return
        if not roles or Qt.ItemDataRole.EditRole in roles:
            # Table cell was edited directly or from external action
            if self.current_source_row >= top_left.row() and self.current_source_row <= bottom_right.row():
                if top_left.column() <= 4 <= bottom_right.column():
                    # Update text box to match table only if text differs
                    item = self.model._data[self.current_source_row]
                    curr_trans = str(item.get("trans") or "")
                    if self.txt_trans.toPlainText() != curr_trans:
                        cursor = self.txt_trans.textCursor()
                        pos = cursor.position()
                        self.txt_trans.blockSignals(True)
                        self.txt_trans.setPlainText(curr_trans)
                        self.txt_trans.blockSignals(False)
                        if self.txt_trans.hasFocus():
                            cursor.setPosition(min(pos, len(curr_trans)))
                            self.txt_trans.setTextCursor(cursor)
                    self.update_progress_stats()

    def on_model_data_changed(self, topLeft, bottomRight, roles):
        if hasattr(self, '_csv_auto_save_timer'):
            self._csv_auto_save_timer.start(2000) # Save 2 seconds after data change

    def _load_api_config(self):
        try:
            return TStudioCore.load_config()
        except Exception as e:
            print(f"Error loading API config: {e}")
            return {
                "google_key": "", "anthropic_key": "", "deepseek_key": "", "openai_key": "",
                "model": "deepseek-v4-pro", "local_url": "http://localhost:1234/v1/chat/completions"
            }

    def _apply_glossary(self, text, source_text=None):
        if not text:
            return ""
        prof_name = getattr(self, 'current_profile_name', None)
        profile = TStudioCore.get_current_profile_data(prof_name)
        glossary = profile.get("glossary", {}) if isinstance(profile, dict) else {}
        if isinstance(glossary, dict):
            import re
            # Sort terms by length in descending order to avoid subterm collisions
            sorted_terms = sorted(glossary.items(), key=lambda x: len(str(x[0])), reverse=True)
            for wrong, val in sorted_terms:
                wrong_str = str(wrong).strip()
                if not wrong_str: continue
                right = val[0] if (isinstance(val, list) and len(val) > 0) else val
                right_str = str(right or "").strip()
                if not right_str: continue

                # 1. Replace raw untranslated source term if left in text
                if wrong_str in text:
                    text = text.replace(wrong_str, right_str)
                elif len(wrong_str) > 2 and wrong_str.lower() in text.lower():
                    text = re.sub(re.escape(wrong_str), right_str, text, flags=re.IGNORECASE)
        return text

    def _check_qa_bytes(self, text):
        if not text:
            return ""
        prof_name = getattr(self, 'current_profile_name', None)
        profile = TStudioCore.get_current_profile_data(prof_name)
        limit = profile.get("max_bytes_limit", 0) if isinstance(profile, dict) else 0
        try:
            limit = int(limit or 0)
        except Exception:
            limit = 0
        if limit > 0:
            encoded = text.encode('utf-8')
            if len(encoded) > limit:
                # truncate at character boundary
                truncated = b""
                for char in text:
                    char_bytes = char.encode('utf-8')
                    if len(truncated) + len(char_bytes) > limit:
                        break
                    truncated += char_bytes
                return truncated.decode('utf-8')
        return text

    def _get_dynamic_glossary(self, source_text):
        if hasattr(self, 'chk_use_tlm') and not self.chk_use_tlm.isChecked():
            return ""

        prof_name = getattr(self, 'current_profile_name', None)
        profile = TStudioCore.get_current_profile_data(prof_name)
        glossary = profile.get("glossary", {}) if isinstance(profile, dict) else {}
        if not isinstance(glossary, dict) or not glossary: return ""

        matched_terms = []
        source_lower = str(source_text or "").lower()

        import re
        # Sort terms by length descending to prioritize compound phrases first
        sorted_terms = sorted(glossary.items(), key=lambda x: len(str(x[0])), reverse=True)

        for eng, val in sorted_terms:
            eng_str = str(eng).strip()
            if not eng_str: continue

            thai = val[0] if (isinstance(val, list) and len(val) > 0) else val
            thai_str = str(thai or "").strip()
            if not thai_str: continue

            term_lower = eng_str.lower()
            # Fast substring pre-check: if the term substring does not exist in source_lower,
            # no word boundary regex could possibly match! This provides a >300x speedup.
            if term_lower not in source_lower:
                continue

            # Asian terms (Japanese Kana, Chinese Hanzi, Korean, Thai) do not have Latin word boundaries; use substring check
            if TStudioCore.has_cjk_or_kana(eng_str):
                is_matched = True
            else:
                prefix = r'\b' if re.match(r'^\w', eng_str) else r''
                suffix = r'(?:s|es|\'s)?\b' if re.search(r'\w$', eng_str) else r''
                pattern = prefix + re.escape(term_lower) + suffix
                is_matched = bool(re.search(pattern, source_lower))

            if is_matched:
                cat = val[1] if (isinstance(val, list) and len(val) > 1) else "Term"
                matched_terms.append(f"- \"{eng_str}\" ➔ \"{thai_str}\" ({cat})")

        if matched_terms:
            rules = (
                "CRITICAL TERMINOLOGY RULES (MANDATORY LOCALIZATION GLOSSARY):\n"
                "You MUST strictly translate the following recognized terms using their exact specified Thai translations:\n"
                + "\n".join(matched_terms)
                + "\n(DO NOT translate these terms into alternative synonyms. Follow the glossary strictly.)"
            )
            return rules
        return ""


    def retranslate_name(self):
        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        cfg = self.translation_channel.snapshot_config(TStudioCore.load_config())
        self.on_trans_changed()
        target = RowTarget.capture(self, self.current_source_row)
        self.statusBar().showMessage("Translating (Transliterate)...")
        self.btn_trans_smart.setEnabled(False)
        source_text = item["source"].replace('\n', '\n')
        
        prompt = f"You are a translator. The following text is a proper noun (e.g. character name, location). Your task is to TRANSLITERATE it into Thai pronunciation (แปลทับศัพท์) WITHOUT translating its meaning. For example: 'Weaver' -> 'วีเวอร์', 'Salvage Yard' -> 'ซัลเวจยาร์ด', 'John' -> 'จอห์น'. Return ONLY the transliterated Thai text.\n\nOriginal Text: {source_text}"
        
        safeguard = "\n\nCRITICAL RULES:\n- DO NOT translate or include the Context ID in your output.\n- Return ONLY the translation.\n- Preserve all UI/game tags like {...}, [...], <...> exactly as they appear."
        prompt += safeguard

        worker = ApiWorker(TranslationGateway.generate_content, cfg, prompt)
        forwarder = ThreadSafeWorkerSignalsForwarder(
            on_success=lambda reply, t=target, check=is_web(cfg): self._on_single_success(reply, t, {}, check),
            on_error=lambda err: self._on_retranslate_error(err, self.btn_trans_smart),
            parent=self
        )
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _on_name_success(self, reply):
        self.btn_trans_smart.setEnabled(True)
        translated = self._apply_glossary(re.sub(r'^"|"$', '', reply))
        self.txt_trans.setPlainText(translated)
        self.statusBar().showMessage(_("retranslated_status"), 3000)

    # -------------------------------------------------------------
    # Snippet / Selected Text Translation Methods (Delegated to Column3EditorWidget)
    # -------------------------------------------------------------
    def _on_text_selection_changed(self, editor_widget):
        """Monitors text selection in editor boxes and delegates to Column3EditorWidget."""
        if hasattr(self, 'col3_editor'):
            self.col3_editor.on_text_selection_changed(editor_widget)

    def _clear_selection_pill(self):
        """Hides floating pill and delegates to Column3EditorWidget."""
        if hasattr(self, 'col3_editor'):
            self.col3_editor.clear_selection_pill()

    def _show_trans_context_menu(self, pos):
        """Custom context menu for txt_trans delegated to Column3EditorWidget."""
        if hasattr(self, 'col3_editor'):
            self.col3_editor.show_trans_context_menu(pos)

    def _show_source_context_menu(self, pos):
        """Custom context menu for txt_source delegated to Column3EditorWidget."""
        if hasattr(self, 'col3_editor'):
            self.col3_editor.show_source_context_menu(pos)

    def _show_ai_context_menu(self, pos):
        """Custom context menu for txt_ai delegated to Column3EditorWidget."""
        if hasattr(self, 'col3_editor'):
            self.col3_editor.show_ai_context_menu(pos)

    def _quick_add_selection_to_glossary(self, term):
        """Quickly add highlighted text to glossary delegated to Column3EditorWidget."""
        if hasattr(self, 'col3_editor'):
            self.col3_editor.quick_add_selection_to_glossary(term)

    def translate_selected_snippet(self, source_widget=None, style_choice=False, mode=None):
        """Translates or transliterates selected snippet delegated to Column3EditorWidget."""
        if hasattr(self, 'col3_editor'):
            self.col3_editor.translate_selected_snippet(source_widget=source_widget, style_choice=style_choice, mode=mode)

    def _on_snippet_success(self, reply, sel_text, target_widget, sel_start, sel_end, style_choice, mode=None):
        """Handles snippet translation response delegated to Column3EditorWidget."""
        if hasattr(self, 'col3_editor'):
            self.col3_editor._on_snippet_success(reply, sel_text, target_widget, sel_start, sel_end, style_choice, mode=mode)

    def _apply_snippet_replacement(self, new_text, original_text, target_widget, sel_start, sel_end, apply_glossary=True):
        """Applies snippet replacement in editor delegated to Column3EditorWidget."""
        if hasattr(self, 'col3_editor'):
            self.col3_editor.apply_snippet_replacement(new_text, original_text, target_widget, sel_start, sel_end, apply_glossary=apply_glossary)

    def retranslate_smart(self):
        # 1. Check if user highlighted a snippet in txt_trans or txt_source
        if hasattr(self, 'txt_trans') and self.txt_trans.textCursor().hasSelection():
            sel = self.txt_trans.textCursor().selectedText().replace('\u2029', ' ').strip()
            if sel:
                self.translate_selected_snippet(source_widget=self.txt_trans)
                return
        if hasattr(self, 'txt_source') and self.txt_source.textCursor().hasSelection():
            sel = self.txt_source.textCursor().selectedText().replace('\u2029', ' ').strip()
            if sel:
                self.translate_selected_snippet(source_widget=self.txt_source)
                return
        selected_indexes = self.table.selectionModel().selectedRows()
        if not selected_indexes:
            # If nothing selected, try to translate current source row
            if self.current_source_row >= 0:
                self.retranslate_single()
            else:
                QMessageBox.information(self, _("no_selection_title"), _("no_selection_msg"))
            return
            
        rows = sorted(list(set(self.proxy.mapToSource(idx).row() for idx in selected_indexes)))
        rows_to_translate = [r for r in rows if self.model._data[r]["source"].strip()]
        
        if len(rows_to_translate) > 1:
            self.retranslate_batch()
        elif len(rows_to_translate) == 1:
            self.current_source_row = rows_to_translate[0]
            self.retranslate_single()
        else:
            QMessageBox.information(self, _("no_content_title"), _("no_content_msg"))

    def show_special_translation_menu_at_cursor(self):
        if hasattr(self, 'col3_editor'):
            self.col3_editor.show_special_translation_menu_at_cursor()
        elif hasattr(self, 'special_menu'):
            from PyQt6.QtGui import QCursor
            self.special_menu.exec(QCursor.pos())

    def retranslate_single(self):
        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        self.on_trans_changed()
        cfg = self.translation_channel.snapshot_config(TStudioCore.load_config())
        field = "ai_ref" if getattr(self, "chk_guide_mode", None) and self.chk_guide_mode.isChecked() else "trans"
        target = RowTarget.capture(self, self.current_source_row, field)
        source_text = item["source"].replace('\n', '\n')

        # --- SKIP CHECK: do not send purely symbolic/tag-only text to AI ---
        if CoreAI.should_skip_translation(source_text):
            self.statusBar().showMessage("Skipped — text is tags/symbols only.")
            self.btn_trans_smart.setEnabled(True)
            return

        self.statusBar().showMessage(_("translating_status_simple"))
        self.btn_trans_smart.setEnabled(False)
        
        prof_name = getattr(self, 'current_profile_name', None)
        profile = TStudioCore.get_current_profile_data(prof_name)
        s_prompt = profile.get('single') or DEFAULT_SINGLE_PROMPT
        dyn_glossary = self._get_dynamic_glossary(source_text)
        if '[GLOSSARY TO USE]' in s_prompt:
            s_prompt = s_prompt.replace('[GLOSSARY TO USE]', dyn_glossary if dyn_glossary else '')
            prompt = s_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)
        else:
            prompt = s_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)
            if dyn_glossary:
                prompt = dyn_glossary + "\n\n" + prompt
        
        # --- SAFEGUARD: Force rules if not explicitly present in the final prompt ---
        safeguard = (
            "\n\nCRITICAL RULES:\n"
            "- DO NOT translate or include the Context ID in your output.\n"
            "- Return ONLY the translation.\n"
            "- Preserve all UI/game tags like {...}, [...], <...> exactly as they appear.\n"
            "- Military & Weapon Nomenclature: Keep alphanumeric firearm models (e.g. 'M16' NEVER 'เอ็ม 16', 'AK-47', 'MP5', 'RPG-7', 'Glock 19'), weapon class acronyms ('SMG', 'AR', 'LMG', 'DMR', 'SR'), military vehicles ('Humvee', 'APC', 'VTOL', 'UAV', 'BTR-80'), and calibers ('9mm', '5.56mm') in original Latin/alphanumeric script."
        )
        if len(source_text.strip()) <= 15:
            safeguard += "\n- The text is VERY SHORT. DO NOT explain, DO NOT add markdown. Return ONLY the translation word(s)."
            safeguard += "\n- Example: 'On' -> 'เปิด', 'Yes' -> 'ใช่'"
        if "Context ID" not in prompt and "UI/game tags" not in prompt:
            prompt += safeguard

        worker = ApiWorker(TranslationGateway.generate_content, cfg, prompt)
        forwarder = ThreadSafeWorkerSignalsForwarder(
            on_success=lambda reply, t=target, g=dict(profile.get("glossary", {})), check=is_web(cfg): self._on_single_success(reply, t, g, check),
            on_error=lambda err: self._on_retranslate_error(err, self.btn_trans_smart),
            parent=self
        )
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _on_single_success(self, reply, target=None, glossary=None, check_tags=False):
        self.btn_trans_smart.setEnabled(True)
        if target is None:
            if not 0 <= self.current_source_row < len(self.model._data):
                return
            field = "ai_ref" if getattr(self, "chk_guide_mode", None) and self.chk_guide_mode.isChecked() else "trans"
            target = RowTarget.capture(self, self.current_source_row, field)
        # Flush a pending edit before checking the target revision.
        self.on_trans_changed()
        if not target.matches(self):
            self._retain_translation_conflict(target, reply)
            return
        translated = CoreAI.clean_ai_translation(target.source, reply)
        translated = re.sub(r'^"|"$', '', translated)
        translated = apply_glossary_snapshot(translated, glossary) if glossary is not None else self._apply_glossary(translated, source_text=target.source)
        if check_tags and not tags_match(target.source, translated):
            self._retain_translation_conflict(target, reply)
            self.statusBar().showMessage('Web ตอบกลับโดย Tags ไม่ตรง จึงเก็บผลแยกไว้ตรวจสอบ', 8000)
            return
        if target.field == 'ai_ref':
            self.model.update_ai_ref(target.row, translated)
        else:
            self.model.update_trans(target.row, translated)
            self._update_stats_for_row(target.row, target.original, translated)
        if target.row == self.current_source_row:
            editor = self.txt_ai if target.field == 'ai_ref' else self.txt_trans
            editor.blockSignals(True)
            editor.setPlainText(translated)
            editor.blockSignals(False)
        self.statusBar().showMessage(_("retranslated_status"), 3000)

    def _retain_translation_conflict(self, target, reply):
        # Keep late answers for recovery without overwriting a changed row or file.
        if not hasattr(self, '_translation_conflicts'):
            self._translation_conflicts = []
        record = {'path': target.path, 'id': target.row_id,
                  'source': target.source, 'reply': reply}
        self._translation_conflicts.append(record)
        try:
            import uuid
            from translation_transport.settings import atomic_json, state_dir
            recovery = state_dir() / 'results' / (uuid.uuid4().hex + '.json')
            atomic_json(recovery, record)
            message = 'เก็บคำตอบที่ยังนำเข้าไม่ได้ไว้ที่: ' + str(recovery)
        except Exception as error:
            message = 'เก็บคำตอบไว้ในหน่วยความจำแล้ว แต่บันทึกไฟล์กู้คืนไม่สำเร็จ: ' + str(error)
        self.statusBar().showMessage(message, 12000)

    def _on_retranslate_error(self, err_msg, btn):
        btn.setEnabled(True)
        QMessageBox.critical(self, _("failed_title"), str(err_msg))
        self.statusBar().showMessage(_("translation_failed_status"), 3000)

    def _on_guide_mode_toggled(self, checked: bool):
        """Visual feedback when Guide Mode is toggled on/off."""
        if checked:
            self.statusBar().showMessage(
                "🧭 Guide Mode เปิด — AI จะแปลไปยังช่อง AI Translation เพื่อเป็นไกด์", 4000
            )
            self.chk_guide_mode.setText("🧭 Guide Mode ✓")
        else:
            self.statusBar().showMessage(
                "Guide Mode ปิด — กลับสู่โหมดปกติ", 3000
            )
            self.chk_guide_mode.setText("🧭 Guide Mode")
            
        # Update buttons to reflect guide mode styling
        self.update_button_labels()

    def retranslate_special(self, mode):
        # 0. Check if user highlighted a snippet in txt_trans or txt_source
        if hasattr(self, 'txt_trans') and self.txt_trans.textCursor().hasSelection():
            sel = self.txt_trans.textCursor().selectedText().replace('\u2029', ' ').strip()
            if sel:
                self.translate_selected_snippet(source_widget=self.txt_trans, mode=mode)
                return
        if hasattr(self, 'txt_source') and self.txt_source.textCursor().hasSelection():
            sel = self.txt_source.textCursor().selectedText().replace('\u2029', ' ').strip()
            if sel:
                self.translate_selected_snippet(source_widget=self.txt_source, mode=mode)
                return

        # Check if multiple rows are selected for batch special translation
        selected_indexes = self.table.selectionModel().selectedRows()
        if len(selected_indexes) > 1:
            rows = sorted(list(set(self.proxy.mapToSource(idx).row() for idx in selected_indexes)))
            rows_to_translate = [r for r in rows if self.model._data[r]["source"].strip()]
            if len(rows_to_translate) > 1:
                reply = QMessageBox.question(
                    self, _("confirm_batch_title"),
                    f"ต้องการแปลภาษา {len(rows_to_translate)} บรรทัดที่เลือกด้วยโหมดแปลแบบพิเศษ '{mode}' ใช่หรือไม่?\n(การแปลจะทำงานแบบขนานในเบื้องหลัง)",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.retranslate_batch(mode=mode)
                return

        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        cfg = self.translation_channel.snapshot_config(TStudioCore.load_config())
        self.on_trans_changed()
        field = "ai_ref" if getattr(self, "chk_guide_mode", None) and self.chk_guide_mode.isChecked() else "trans"
        target = RowTarget.capture(self, self.current_source_row, field)
        self.statusBar().showMessage(f"Translating ({mode})...")
        self.btn_trans_special.setEnabled(False)
        source_text = item["source"].replace('\n', '\n')
        
        mode_text = ""
        length_constraint = "Keep your translation CONCISE. Match the length and structure of the original text as closely as possible. Do NOT write paragraphs if the original is a short sentence."
        
        if mode == "transliterate":
            mode_text = "TRANSLITERATE (แปลทับศัพท์) the original text into Thai pronunciation WITHOUT translating its meaning. Return ONLY the transliterated word."
        elif mode == "idiom":
            mode_text = f"Analyze the underlying meaning carefully. Translate into a natural, contextually appropriate Thai idiom or phrase (สำนวน/คำพังเพย). {length_constraint}"
        elif mode == "poem":
            mode_text = f"Translate into an elegant Thai poetic form (กลอน/บทกวี/คาถา) with appropriate rhyming. {length_constraint}"
        elif mode == "quote":
            mode_text = f"Translate into formal, philosophical, and impactful Thai language (คำคม/ปรัชญา), similar to a famous historical quote. {length_constraint}"
        elif mode == "mature":
            mode_text = f"Translate aggressively using mature, unfiltered, or profane Thai language (หยาบคาย/ดุดัน) appropriate for a gritty action game. {length_constraint}"
        elif mode == "fantasy":
            mode_text = f"Translate using medieval, fantasy, or archaic Thai language (ย้อนยุค/แฟนตาซี) (e.g., ข้า, เจ้า, ฝ่าบาท). {length_constraint}"
        elif mode == "robotic":
            mode_text = f"Translate into cold, systemic, robotic Thai language (ประกาศจากระบบ/AI) (e.g., ตรวจพบ, ระบบขัดข้อง). {length_constraint}"
        elif mode == "casual":
            mode_text = f"Translate into modern, casual, or sarcastic Thai slang (วัยรุ่น/กวนๆ) suitable for natural youth conversation. {length_constraint}"
            
        dyn_glossary = self._get_dynamic_glossary(source_text)
        prompt = f"You are a Master-Level Video Game Localization Specialist for '{GAME_NAME}', translating into natural Thai.\n{mode_text}\n\nCRITICAL LORE AWARENESS: You MUST strictly adhere to the Glossary/Terminology provided below for any recognized terms."
        if dyn_glossary:
            prompt += "\n\n" + dyn_glossary
        prompt += f"\nContext ID: '{item['id']}'.\n\nOriginal Text: {source_text}"
        
        safeguard = "\n\nCRITICAL RULES:\n- DO NOT translate or include the Context ID in your output.\n- Return ONLY the translation.\n- Preserve all UI/game tags like {...}, [...], <...> exactly as they appear."
        if len(source_text.strip()) <= 15:
            safeguard += "\n- The text is VERY SHORT. DO NOT explain, DO NOT add markdown. Return ONLY the translation word(s)."
            safeguard += "\n- Example: 'On' -> 'เปิด', 'Yes' -> 'ใช่'"
        if "Context ID" not in prompt and "UI/game tags" not in prompt:
            prompt += safeguard
        
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        worker = ApiWorker(TranslationGateway.generate_content, cfg, prompt, is_local=is_local)
        forwarder = ThreadSafeWorkerSignalsForwarder(
            on_success=lambda reply, t=target, check=is_web(cfg): self._on_special_success(reply, mode, t, check),
            on_error=lambda err: self._on_retranslate_error(err, self.btn_trans_special),
            parent=self
        )
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _on_special_success(self, reply, mode, target=None, check_tags=False):
        self.btn_trans_special.setEnabled(True)
        if target is not None:
            self._on_single_success(reply, target, check_tags=check_tags)
            return
        translated = self._apply_glossary(re.sub(r'^"|"$', '', reply))
        row = self.current_source_row
        
        if getattr(self, 'chk_guide_mode', None) and self.chk_guide_mode.isChecked():
            new_text = translated.replace('\n', '\n')
            self.model.update_ai_ref(row, new_text)
            self.txt_ai.setPlainText(translated.replace('\n', '\n'))
            self.statusBar().showMessage(f"[Guide] แปลเสร็จ ({mode}) — ดูได้ที่ช่อง AI Translation", 4000)
        else:
            self.txt_trans.setPlainText(translated)
            self.statusBar().showMessage(f"Re-translated as {mode}!", 3000)

    def retranslate_options(self, show_dialog=True):
        # 0. Check if user highlighted a snippet in txt_trans or txt_source
        if hasattr(self, 'txt_trans') and self.txt_trans.textCursor().hasSelection():
            sel = self.txt_trans.textCursor().selectedText().replace('\u2029', ' ').strip()
            if sel:
                self.translate_selected_snippet(source_widget=self.txt_trans, style_choice=True)
                return
        if hasattr(self, 'txt_source') and self.txt_source.textCursor().hasSelection():
            sel = self.txt_source.textCursor().selectedText().replace('\u2029', ' ').strip()
            if sel:
                self.translate_selected_snippet(source_widget=self.txt_source, style_choice=True)
                return

        # 1. Sync row selection if current_source_row is invalid
        if self.current_source_row < 0:
            selected_indexes = self.table.selectionModel().selectedRows()
            if selected_indexes:
                self.current_source_row = self.proxy.mapToSource(selected_indexes[0]).row()
            elif hasattr(self, 'table') and self.table.currentIndex().isValid():
                self.current_source_row = self.proxy.mapToSource(self.table.currentIndex()).row()

        if self.current_source_row < 0 or self.current_source_row >= len(self.model._data):
            QMessageBox.information(self, _("no_selection_title"), "กรุณาเลือกแถวที่ต้องการแปลในตาราง")
            return

        target_row = self.current_source_row
        item = self.model._data[target_row]
        source_text = item["source"].replace('\r\n', '\n').strip()
        if not source_text:
            return

        # 2. Skip check for pure numbers/symbols
        if CoreAI.should_skip_translation(source_text):
            self.statusBar().showMessage("⏭️ ข้ามการแปล: ข้อความไม่มีเนื้อหาที่ต้องแปล", 3000)
            return

        cfg = self.translation_channel.snapshot_config(TStudioCore.load_config())
        self.on_trans_changed()
        target = RowTarget.capture(self, target_row, "ai_ref")
        self.statusBar().showMessage("💡 กำลังดึงตัวเลือกคำแปล 3 สไตล์จาก AI...")
        
        # 3. UI visual feedback
        if getattr(self, 'btn_trans_opt', None):
            self.btn_trans_opt.setEnabled(False)
            self.btn_trans_opt.setText("⏳ กำลังแปล...")
        if getattr(self, 'ai_cards_container', None):
            self.ai_cards_container.show()
        if getattr(self, 'ai_style_cards', None):
            for _, lbl_prev in self.ai_style_cards:
                lbl_prev.setText("⏳ กำลังแปล...")

        prof_name = getattr(self, 'current_profile_name', None)
        profile = TStudioCore.get_current_profile_data(prof_name)
        o_prompt = profile.get('opt') or DEFAULT_OPTIONS_PROMPT
        dyn_glossary = self._get_dynamic_glossary(source_text)
        if '[GLOSSARY TO USE]' in o_prompt:
            o_prompt = o_prompt.replace('[GLOSSARY TO USE]', dyn_glossary if dyn_glossary else '')
            prompt = o_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)
        else:
            prompt = o_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)
            if dyn_glossary:
                prompt = dyn_glossary + "\n\n" + prompt
        
        # --- SAFEGUARD: Force rules if not explicitly present in the final prompt ---
        safeguard = "\n\nCRITICAL RULES:\n- DO NOT translate or include the Context ID in your output.\n- Return ONLY the JSON array.\n- Preserve all UI/game tags like {...}, [...], <...> exactly as they appear."
        if "Context ID" not in prompt and "UI/game tags" not in prompt:
            prompt += safeguard

        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
        worker = ApiWorker(TranslationGateway.generate_content, cfg, prompt, is_local=is_local)
        forwarder = ThreadSafeWorkerSignalsForwarder(
            on_success=lambda reply, r=target_row, sd=show_dialog, t=target: self._on_options_success(reply, r, sd, t),
            on_error=lambda err, r=target_row: self._on_options_error(err, r),
            parent=self
        )
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _on_options_error(self, err_msg, target_row):
        if getattr(self, 'btn_trans_opt', None):
            self.btn_trans_opt.setEnabled(True)
            self.btn_trans_opt.setText("💡 3 สไตล์")
        if getattr(self, 'ai_style_cards', None) and getattr(self, 'current_source_row', -1) == target_row:
            for btn_c, lbl_prev in self.ai_style_cards:
                lbl_prev.setText("❌ การแปลล้มเหลว")
        QMessageBox.critical(self, _("failed_title"), f"ไม่สามารถดึงตัวเลือก 3 สไตล์ได้:\n{err_msg}")
        self.statusBar().showMessage(_("translation_failed_status"), 3000)

    def _on_options_success(self, reply, target_row, show_dialog=True, target=None):
        if getattr(self, 'btn_trans_opt', None):
            self.btn_trans_opt.setEnabled(True)
            self.btn_trans_opt.setText("💡 3 สไตล์")
        
        if target is not None and not target.matches(self):
            self._retain_translation_conflict(target, reply)
            return

        from tstudio_core import TStudioCore
        options = TStudioCore.extract_translation_options(reply)
        if not options:
            QMessageBox.warning(self, _("parse_error_title"), f"AI ส่งกลับมาในรูปแบบที่ไม่ถูกต้อง:\n{reply}")
            if getattr(self, 'ai_style_cards', None) and getattr(self, 'current_source_row', -1) == target_row:
                for btn_c, lbl_prev in self.ai_style_cards:
                    lbl_prev.setText("— ไม่สามารถแยกแยะผลลัพธ์ได้ —")
            return

        source_text = self.model._data[target_row]["source"] if 0 <= target_row < len(self.model._data) else ""
        options = [self._apply_glossary(o, source_text=source_text) for o in options]
        primary_option = options[0] if options else ""

        # Update model for target_row (so it's safely saved even if user switched rows)
        if 0 <= target_row < len(self.model._data):
            self.model.update_ai_ref(target_row, primary_option)

        # If user is still viewing the target row, update txt_ai
        if getattr(self, 'current_source_row', -1) == target_row:
            if getattr(self, 'ai_cards_container', None):
                self.ai_cards_container.show()
            if getattr(self, 'ai_style_cards', None):
                for i, opt in enumerate(options[:3]):
                    if i < len(self.ai_style_cards):
                        btn_c, lbl_prev = self.ai_style_cards[i]
                        lbl_prev.setText(opt)
            self.txt_ai.setPlainText(primary_option)
            self.statusBar().showMessage("● แปล 3 สไตล์สำเร็จแล้ว", 4000)

        # Show modal dialog
        if show_dialog:
            dlg = TranslationOptionsDialog(self, options)
            if dlg.exec() and dlg.selected_text:
                if getattr(self, 'chk_guide_mode', None) and self.chk_guide_mode.isChecked():
                    self.model.update_ai_ref(target_row, dlg.selected_text)
                    if getattr(self, 'current_source_row', -1) == target_row:
                        self.txt_ai.setPlainText(dlg.selected_text)
                    self.statusBar().showMessage(_("guide_mode_translated"), 4000)
                else:
                    self.model.update_trans(target_row, dlg.selected_text)
                    if getattr(self, 'current_source_row', -1) == target_row:
                        self.txt_trans.setPlainText(dlg.selected_text)
                    self.statusBar().showMessage(_("done_status"), 3000)

    def retranslate_local(self):
        if self.current_source_row < 0: return
        item = self.model._data[self.current_source_row]
        if not item["source"].strip(): return
        cfg = TStudioCore.load_config()
        self.statusBar().showMessage("Translating with Local AI...")
        source_text = item["source"].replace('\n', '\n')
        
        prof_name = getattr(self, 'current_profile_name', None)
        profile = TStudioCore.get_current_profile_data(prof_name)
        s_prompt = profile.get('single') or DEFAULT_SINGLE_PROMPT
        prompt = s_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)

        worker = ApiWorker(CoreAI.generate_content, cfg, prompt, is_local=True)
        forwarder = ThreadSafeWorkerSignalsForwarder(
            on_success=lambda reply: self._on_local_success(reply),
            on_error=lambda err: self._on_local_error(err),
            parent=self
        )
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        wid = id(worker)
        worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
        self._workers[wid] = worker
        self.threadpool.start(worker)

    def _on_local_success(self, reply):
        translated = self._apply_glossary(re.sub(r'^"|"$', '', reply))
        row = self.current_source_row
        
        if getattr(self, 'chk_guide_mode', None) and self.chk_guide_mode.isChecked():
            new_text = translated.replace('\n', '\n')
            self.model.update_ai_ref(row, new_text)
            self.txt_ai.setPlainText(translated.replace('\n', '\n'))
            self.statusBar().showMessage("[Guide] แปลเสร็จ (Local AI) — ดูได้ที่ช่อง AI Translation", 4000)
        else:
            self.txt_trans.setPlainText(translated)
            self.statusBar().showMessage("Re-translated with Local AI!", 3000)

    def _on_local_error(self, err):
        QMessageBox.critical(self, _("failed_title"), f"Is your Local LLM running?\n\nError: {err}")

    def retranslate_batch(self, mode=None, force_cat=False):
        """Batch Translation engine: Translates selected rows line-by-line in CAT Mode (or prompts user / routes to TRun)."""
        self.on_trans_changed()
        if isinstance(mode, bool): mode = None
        source_rows = self._get_selected_source_rows()
        if not source_rows:
            QMessageBox.information(self, _("no_selection_title"), _("no_selection_msg"))
            return
            
        rows_to_translate = [r for r in source_rows if 0 <= r < len(self.model._data) and self.model._data[r]["source"].strip()]
        if not rows_to_translate:
            QMessageBox.information(self, _("no_content_title"), _("no_content_msg"))
            return

        # If exactly 1 row is selected, translate directly with single AI in CAT editor
        if len(rows_to_translate) == 1:
            self.current_source_row = rows_to_translate[0]
            if mode:
                self.retranslate_special(mode)
            else:
                self.retranslate_single()
            return

        # Confirm with user if they select many rows (> 5 rows) and force_cat is not set and no special mode
        if len(rows_to_translate) > 5 and not mode and not force_cat:
            box = QMessageBox(self)
            box.setWindowTitle("เลือกวิธีการแปลภาษา (Batch Translation)")
            box.setIcon(QMessageBox.Icon.Question)
            box.setText(
                f"คุณได้เลือกข้อความจำนวน <b>{len(rows_to_translate):,} บรรทัด</b><br><br>"
                f"💡 <b>คำแนะนำสำหรับการประหยัด Token และความเร็ว:</b><br>"
                f"• <b>TRun Batch Translation (แนะนำ):</b> รวมกลุ่ม 20-50 บรรทัด/API Call ช่วย<b>ประหยัด Token 80-90%</b> และแปลเร็วกว่ามาก<br>"
                f"• <b>CAT Mode (แปลทีละบรรทัด):</b> ส่ง 1 API Call ต่อ 1 บรรทัด เหมาะสำหรับการแปลจำนวนน้อย หรือตรวจงานทีละแถว<br><br>"
                f"ต้องการแปลด้วยวิธีใด?"
            )
            btn_trun = box.addButton("🚀 แปลด้วย TRun Batch (ประหยัด Token)", QMessageBox.ButtonRole.AcceptRole)
            btn_trun.setStyleSheet("background-color: #a6e3a1; color: #11111b; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
            btn_cat = box.addButton("⚡ แปลทีละบรรทัดในตาราง (CAT Mode)", QMessageBox.ButtonRole.ActionRole)
            btn_cancel = box.addButton("ยกเลิก (Cancel)", QMessageBox.ButtonRole.RejectRole)
            box.setDefaultButton(btn_trun)
            
            box.exec()
            clicked = box.clickedButton()
            if clicked == btn_cancel or clicked is None:
                return
            elif clicked == btn_trun:
                self.send_selection_to_trun(auto_start=True)
                return
        elif len(rows_to_translate) > 5 and mode:
            reply = QMessageBox.question(
                self, _("confirm_batch_title"),
                f"ต้องการแปลภาษา {len(rows_to_translate)} บรรทัดที่เลือกด้วยโหมดพิเศษ '{mode}' ใช่หรือไม่?\n(การแปลจะทำงานแบบขนานทีละบรรทัดในเบื้องหลัง)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Initialize batch state
        self._batch_total = len(rows_to_translate)
        self._batch_completed = 0
        self._batch_errors = []
        self._batch_done_shown = False  # Guard: prevent duplicate completion dialogs
        self._start_batch_progress(self._batch_total)
        
        # Disable all AI translation buttons during batch translation
        self.btn_trans_smart.setEnabled(False)
        if getattr(self, 'btn_trans_opt', None):
            self.btn_trans_opt.setEnabled(False)
        self.btn_trans_special.setEnabled(False)
        if hasattr(self, 'btn_trans_batch'):
            self.btn_trans_batch.setEnabled(False)
        
        self.statusBar().showMessage(_("batch_translating_status").format(current=0, total=self._batch_total))
        
        cfg = self.translation_channel.snapshot_config(TStudioCore.load_config())
        prof_name = getattr(self, 'current_profile_name', None)
        profile = TStudioCore.get_current_profile_data(prof_name)
        
        if mode:
            mode_text = ""
            length_constraint = "Keep your translation CONCISE. Match the length and structure of the original text as closely as possible. Do NOT write paragraphs if the original is a short sentence."
            
            if mode == "transliterate":
                mode_text = "TRANSLITERATE (แปลทับศัพท์) the original text into Thai pronunciation WITHOUT translating its meaning. Return ONLY the transliterated word."
            elif mode == "idiom":
                mode_text = f"Analyze the underlying meaning carefully. Translate into a natural, contextually appropriate Thai idiom or phrase (สำนวน/คำพังเพย). {length_constraint}"
            elif mode == "poem":
                mode_text = f"Translate into an elegant Thai poetic form (กลอน/บทกวี/คาถา) with appropriate rhyming. {length_constraint}"
            elif mode == "quote":
                mode_text = f"Translate into formal, philosophical, and impactful Thai language (คำคม/ปรัชญา), similar to a famous historical quote. {length_constraint}"
            elif mode == "mature":
                mode_text = f"Translate aggressively using mature, unfiltered, or profane Thai language (หยาบคาย/ดุดัน) appropriate for a gritty action game. {length_constraint}"
            elif mode == "fantasy":
                mode_text = f"Translate using medieval, fantasy, or archaic Thai language (ย้อนยุค/แฟนตาซี) (e.g., ข้า, เจ้า, ฝ่าบาท). {length_constraint}"
            elif mode == "robotic":
                mode_text = f"Translate into cold, systemic, robotic Thai language (ประกาศจากระบบ/AI) (e.g., ตรวจพบ, ระบบขัดข้อง). {length_constraint}"
            elif mode == "casual":
                mode_text = f"Translate into modern, casual, or sarcastic Thai slang (วัยรุ่น/กวนๆ) suitable for natural youth conversation. {length_constraint}"
                
            s_prompt = f"You are a Master-Level Video Game Localization Specialist for '{GAME_NAME}', translating into natural Thai.\n{mode_text}\n\nCRITICAL LORE AWARENESS: You MUST strictly adhere to the Glossary/Terminology provided below for any recognized terms.\nContext ID: '{{id}}'.\n\nOriginal Text: {{source_text}}"
        else:
            s_prompt = profile.get('single') or DEFAULT_SINGLE_PROMPT
        
        # Validate API settings once before running batch
        try:
            model = cfg.get("model", "")
            is_local = (cfg.get("provider", "") == "Local LLM" or model == "custom-local-llm")
            if not is_local and not is_web(cfg):
                if model.startswith("gemini") and not cfg.get("google_key"):
                    raise Exception("Google Gemini API Key is missing!")
                elif model.startswith("claude") and not cfg.get("anthropic_key"):
                    raise Exception("Anthropic Claude API Key is missing!")
                elif model.startswith("deepseek") and not cfg.get("deepseek_key"):
                    raise Exception("DeepSeek API Key is missing!")
                elif (model.startswith("gpt") or model.startswith("o1") or model.startswith("o3") or model.startswith("o4") or model.startswith("chatgpt")) and not cfg.get("openai_key"):
                    raise Exception("OpenAI API Key is missing!")
        except Exception as e:
            QMessageBox.critical(self, _("api_key_error_title"), f"ไม่สามารถเริ่มแปลได้:\n{e}\n\nกรุณาตั้งค่า API Key ใน Settings")
            self.btn_trans_smart.setEnabled(True)
            if getattr(self, 'btn_trans_opt', None):
                self.btn_trans_opt.setEnabled(True)
            self.btn_trans_special.setEnabled(True)
            if hasattr(self, 'btn_trans_batch'):
                self.btn_trans_batch.setEnabled(True)
            return

        # Determine safe batch concurrency based on user config or provider defaults
        user_concurrency = int(cfg.get("batch_concurrency", 0) or 0)
        if user_concurrency > 0:
            batch_concurrency = user_concurrency
        else:
            if is_local:
                batch_concurrency = 3
            elif model.startswith("deepseek"):
                batch_concurrency = 12  # DeepSeek tier limit is 25, 12 gives >50% safety buffer
            elif model.startswith("claude") or model.startswith("gemini"):
                batch_concurrency = 8
            else:
                batch_concurrency = 15

        if not hasattr(self, 'batch_threadpool'):
            self.batch_threadpool = QThreadPool(self)
        self.batch_threadpool.setMaxThreadCount(1 if is_web(cfg) else batch_concurrency)

        for idx_row, row in enumerate(rows_to_translate):
            if idx_row % 15 == 0:
                QApplication.processEvents()
            item = self.model._data[row]
            source_text = item["source"].replace('\n', '\n')
            
            from tstudio_core import CoreAI
            if CoreAI.should_skip_translation(source_text):
                # Skip API call for symbols/tags, just use the original text as success
                self._on_batch_row_success(source_text, row)
                continue
                
            dyn_glossary = self._get_dynamic_glossary(source_text)
            if '[GLOSSARY TO USE]' in s_prompt:
                row_s_prompt = s_prompt.replace('[GLOSSARY TO USE]', dyn_glossary if dyn_glossary else '')
                prompt = row_s_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)
            else:
                prompt = s_prompt.replace('{id}', item["id"]).replace('{source_text}', source_text)
                if dyn_glossary:
                    prompt = dyn_glossary + "\n\n" + prompt
                
            safeguard = (
                "\n\nCRITICAL RULES:\n"
                "- DO NOT translate or include the Context ID in your output.\n"
                "- Return ONLY the translation.\n"
                "- Preserve all UI/game tags like {...}, [...], <...> exactly as they appear.\n"
                "- Military & Weapon Nomenclature: Keep alphanumeric firearm models (e.g. 'M16' NEVER 'เอ็ม 16', 'AK-47', 'MP5', 'RPG-7', 'Glock 19'), weapon class acronyms ('SMG', 'AR', 'LMG', 'DMR', 'SR'), military vehicles ('Humvee', 'APC', 'VTOL', 'UAV', 'BTR-80'), and calibers ('9mm', '5.56mm') in original Latin/alphanumeric script."
            )
            if len(source_text.strip()) <= 15:
                safeguard += "\n- The text is VERY SHORT. DO NOT explain, DO NOT add markdown. Return ONLY the translation word(s)."
                safeguard += "\n- Example: 'On' -> 'เปิด', 'Yes' -> 'ใช่'"
            if "Context ID" not in prompt and "UI/game tags" not in prompt:
                prompt += safeguard
                
            field = "ai_ref" if getattr(self, "chk_guide_mode", None) and self.chk_guide_mode.isChecked() else "trans"
            target = RowTarget.capture(self, row, field)
            worker = ApiWorker(TranslationGateway.generate_content, cfg, prompt, is_local=is_local)
            
            forwarder = ThreadSafeWorkerSignalsForwarder(
                on_success=lambda reply, r=row, t=target, g=dict(profile.get("glossary", {})), check=is_web(cfg): self._on_batch_row_success(reply, r, t, g, check),
                on_error=lambda err, r=row: self._on_batch_row_error(err, r),
                parent=self
            )
            worker.signals.finished.connect(forwarder.handle_finished)
            worker.signals.error.connect(forwarder.handle_error)
            wid = id(worker)
            worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
            worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
            self._workers[wid] = worker
            self.batch_threadpool.start(worker)

    def _on_batch_row_success(self, reply, row, target=None, glossary=None, check_tags=False):
        # Guard against late-arriving callbacks after the window has been closed.
        if getattr(self, '_is_closing', False):
            return
        if target is not None:
            self.on_trans_changed()
        if target is not None and not target.matches(self):
            self._retain_translation_conflict(target, reply)
            self._batch_errors.append((row, "Target changed while translating"))
            self._batch_completed += 1
            self._update_batch_progress()
            return
        source_text = self.model._data[row]["source"] if 0 <= row < len(self.model._data) else ""
        try:
            from tstudio_core import CoreAI
            reply = CoreAI.clean_ai_translation(source_text, reply)
        except Exception as e:
            print(f"[Warning] clean_ai_translation error: {e}")
        translated = re.sub(r'^"|"$', '', reply)
        translated = apply_glossary_snapshot(translated, glossary) if glossary is not None else self._apply_glossary(translated, source_text=source_text)
        if check_tags and not tags_match(source_text, translated):
            self._retain_translation_conflict(target, reply)
            self._on_batch_row_error('Web Tags mismatch', row)
            return
        new_text = translated.replace('\n', '\n')

        guide_mode = (target.field == 'ai_ref') if target else (getattr(self, 'chk_guide_mode', None) and self.chk_guide_mode.isChecked())

        if guide_mode:
            # Guide Mode: write to ai_ref column only
            self.model.update_ai_ref(row, new_text)
            if row == self.current_source_row:
                self.txt_ai.blockSignals(True)
                self.txt_ai.setPlainText(translated.replace('\n', '\n'))
                self.txt_ai.blockSignals(False)
        else:
            old_text = self.model._data[row]["trans"]
            self.model.update_trans(row, new_text)
            self._update_stats_for_row(row, old_text, new_text)
            if row == self.current_source_row:
                self.txt_trans.blockSignals(True)
                self.txt_trans.setPlainText(translated.replace('\n', '\n'))
                self.txt_trans.blockSignals(False)

        self._batch_completed += 1
        self._update_batch_progress()

    def _on_batch_row_error(self, err, row):
        # FIX: Guard against late-arriving callbacks after the window has been closed.
        if getattr(self, '_is_closing', False):
            return
        self._batch_errors.append((row, str(err)))
        self._batch_completed += 1
        self._update_batch_progress()

    def _update_batch_progress(self):
        if getattr(self, '_is_closing', False):
            return
        if self._batch_completed < self._batch_total:
            # Update mini progress bar
            pct = int(self._batch_completed / self._batch_total * 100)
            if hasattr(self, '_batch_mini_bar'):
                self._batch_mini_bar.setValue(pct)
                self._batch_count_label.setText(f"{self._batch_completed} / {self._batch_total}")
            self.statusBar().showMessage(
                _("batch_translating_status").format(current=self._batch_completed, total=self._batch_total)
            )
        else:
            # Guard: multiple workers finishing simultaneously may each see
            # _batch_completed == _batch_total; only show the dialog once.
            if getattr(self, '_batch_done_shown', False):
                return
            self._batch_done_shown = True

            # Update progress to 100% and show finish state
            if hasattr(self, '_batch_mini_bar'):
                self._batch_mini_bar.setValue(100)
                self._batch_count_label.setText(f"{self._batch_total} / {self._batch_total}")
            success_count = self._batch_total - len(self._batch_errors)
            self._finish_batch_progress(success_count, self._batch_total)

            self.btn_trans_smart.setEnabled(True)
            if getattr(self, 'btn_trans_opt', None):
                self.btn_trans_opt.setEnabled(True)
            self.btn_trans_special.setEnabled(True)
            if hasattr(self, 'btn_trans_batch'):
                self.btn_trans_batch.setEnabled(True)
            if self._batch_errors:
                err_msgs = [f"แถวที่ {r+1}: {e}" for r, e in self._batch_errors[:5]]
                if len(self._batch_errors) > 5:
                    err_msgs.append(f"...และอีก {len(self._batch_errors) - 5} รายการ")
                QMessageBox.warning(
                    self, _("batch_complete_with_errors"),
                    f"แปลเสร็จสิ้นแล้ว แต่พบบั๊กหรือข้อผิดพลาดบางรายการ:\n\n" + "\n".join(err_msgs)
                )
                self.statusBar().showMessage(_("batch_translated_status").format(total=self._batch_total), 5000)
            else:
                self.statusBar().showMessage(_("batch_translated_status").format(total=self._batch_total), 5000)
                QMessageBox.information(self, _("success_title"), _("batch_translated_msg").format(total=self._batch_total))

    def patch_selected_english_leaks(self):
        """
        Detects untranslated English words/phrases inside the selected rows' Thai translations,
        and asks the AI to localize/patch ONLY those English parts in-context, preserving the
        surrounding Thai text, structure, and game tags.
        """
        source_rows = self._get_selected_source_rows()
        if not source_rows:
            if hasattr(self, 'current_source_row') and 0 <= self.current_source_row < len(self.model._data):
                source_rows = [self.current_source_row]
            else:
                QMessageBox.information(self, "แปลซ่อมคำอังกฤษเฉพาะจุด", "กรุณาเลือกบรรทัดในตารางที่ต้องการแปลซ่อม")
                return

        from tstudio_core import TStudioCore, CoreAI
        prof_name = getattr(self, 'current_profile_name', None)
        profile = TStudioCore.get_current_profile_data(prof_name)
        glossary_targets = []
        if profile and isinstance(profile.get("glossary"), dict):
            for v in profile["glossary"].values():
                val = v[0] if isinstance(v, list) and v else v
                if isinstance(val, str) and val.strip():
                    glossary_targets.append(val.strip())

        # Collect rows that actually contain untranslated English words
        rows_to_patch = []
        for r in source_rows:
            if 0 <= r < len(self.model._data):
                item = self.model._data[r]
                trans_text = str(item.get("trans") or "").strip()
                if not trans_text:
                    continue
                leaks = TStudioCore.extract_english_leaks(trans_text, allowed_words=glossary_targets)
                if leaks:
                    rows_to_patch.append((r, item, leaks))

        if not rows_to_patch:
            self.statusBar().showMessage("✅ แถวที่เลือกไม่มีคำภาษาอังกฤษหลุด (เป็นภาษาไทยสมบูรณ์แล้ว)", 4000)
            QMessageBox.information(self, "ผลการตรวจสอบ", "ไม่พบคำภาษาอังกฤษที่ต้องแปลซ่อมในแถวที่เลือก\n(ข้อความที่แปลแล้วเป็นภาษาไทยสมบูรณ์อยู่แล้ว)")
            return

        if len(rows_to_patch) > 5:
            reply = QMessageBox.question(
                self, "ยืนยันการแปลซ่อมคำอังกฤษเฉพาะจุด",
                f"ตรวจพบคำภาษาอังกฤษตกค้างใน {len(rows_to_patch)} แถว\nต้องการให้ AI แปลซ่อมเฉพาะคำอังกฤษเหล่านั้น โดยคงประโยคภาษาไทยเดิมไว้ใช่หรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        cfg = TStudioCore.load_config()
        self._patch_total = len(rows_to_patch)
        self._patch_completed = 0
        self._patch_errors = []
        self._patch_done_shown = False
        self._start_batch_progress(self._patch_total)

        self.statusBar().showMessage(f"🩹 กำลังแปลซ่อมคำอังกฤษเฉพาะจุด: 0/{self._patch_total} แถว...")

        # Disable translation buttons during patching
        if hasattr(self, 'btn_trans_smart'): self.btn_trans_smart.setEnabled(False)
        if hasattr(self, 'btn_trans_opt'): self.btn_trans_opt.setEnabled(False)
        if hasattr(self, 'btn_trans_special'): self.btn_trans_special.setEnabled(False)
        if hasattr(self, 'btn_patch_eng'): self.btn_patch_eng.setEnabled(False)
        if hasattr(self, 'btn_trans_batch'): self.btn_trans_batch.setEnabled(False)

        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")

        for idx_row, (r_idx, itm, leaks_list) in enumerate(rows_to_patch):
            if idx_row % 15 == 0:
                QApplication.processEvents()
            src_text = itm.get("source", "")
            curr_trans = itm.get("trans", "")
            dyn_glossary = self._get_dynamic_glossary(src_text)

            leaks_str = ", ".join(leaks_list)
            patch_prompt = (
                "You are an expert Video Game Localization Editor.\n"
                "Task: Fix and localize ONLY the untranslated English words inside this Thai game translation so they blend naturally into the sentence.\n\n"
                "CRITICAL RULES:\n"
                "1. DO NOT retranslate the whole sentence from scratch. PRESERVE the surrounding Thai phrasing, tone, and grammar.\n"
                f"2. Translate or phonetically transliterate ONLY the English words/phrases ({leaks_str}) into natural Thai that fits seamlessly into the sentence.\n"
                "   - EXCEPTION: Keep alphanumeric firearm models (M16, AK-47, MP5, RPG-7), weapon acronyms (SMG, AR, LMG), calibers (9mm, 5.56mm), and military vehicles (Humvee, APC, VTOL) in original English/Alphanumeric script.\n"
                "3. Strictly preserve all game tags, codes, and variables ({...}, <...>, %s, \\n, etc.) exactly as they appear.\n"
                "4. Return ONLY the final corrected Thai sentence. No quotes, no markdown, no conversational commentary.\n\n"
            )
            if dyn_glossary:
                patch_prompt += dyn_glossary + "\n\n"
            patch_prompt += (
                f"Original English: {src_text}\n"
                f"Current Thai with English: {curr_trans}\n"
                f"English words to fix: {leaks_str}\n\n"
                "Corrected Thai:"
            )

            worker = ApiWorker(CoreAI.generate_content, cfg, patch_prompt, is_local=is_local)
            forwarder = ThreadSafeWorkerSignalsForwarder(
                on_success=lambda rep, r=r_idx, it=itm: self._on_patch_row_success(rep, r, it),
                on_error=lambda err, r=r_idx, it=itm: self._on_patch_row_error(err, r, it),
                parent=self
            )
            worker.signals.finished.connect(forwarder.handle_finished)
            worker.signals.error.connect(forwarder.handle_error)
            wid = id(worker)
            worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
            worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
            self._workers[wid] = worker
            self.batch_threadpool.start(worker)

    def _on_patch_row_success(self, reply, row, itm):
        if getattr(self, '_is_closing', False):
            return
        cleaned = reply.strip()
        cleaned = re.sub(r'^```[a-zA-Z]*\n?|\n?```$', '', cleaned).strip()
        if cleaned.startswith('"') and cleaned.endswith('"') and len(cleaned) >= 2:
            cleaned = cleaned[1:-1].strip()

        old_text = self.model._data[row]["trans"] if 0 <= row < len(self.model._data) else ""
        if cleaned:
            self.model.update_trans(row, cleaned)
            self._update_stats_for_row(row, old_text, cleaned)
            if row == self.current_source_row:
                self.txt_trans.blockSignals(True)
                self.txt_trans.setPlainText(cleaned)
                self.txt_trans.blockSignals(False)

        self._patch_completed += 1
        self._update_patch_progress()

    def _on_patch_row_error(self, err, row, itm):
        if getattr(self, '_is_closing', False):
            return
        g_id = itm.get("id", f"Row {row+1}")
        self._patch_errors.append((row, g_id, str(err)))
        self._patch_completed += 1
        self._update_patch_progress()

    def _update_patch_progress(self):
        if getattr(self, '_is_closing', False):
            return
        if self._patch_completed < self._patch_total:
            pct = int(self._patch_completed / self._patch_total * 100)
            if hasattr(self, '_batch_mini_bar'):
                self._batch_mini_bar.setValue(pct)
                self._batch_count_label.setText(f"{self._patch_completed} / {self._patch_total}")
            self.statusBar().showMessage(f"🩹 แปลซ่อมคำอังกฤษเฉพาะจุด: {self._patch_completed}/{self._patch_total} แถว...")
        else:
            if getattr(self, '_patch_done_shown', False):
                return
            self._patch_done_shown = True

            if hasattr(self, '_batch_mini_bar'):
                self._batch_mini_bar.setValue(100)
                self._batch_count_label.setText(f"{self._patch_total} / {self._patch_total}")
            success_count = self._patch_total - len(self._patch_errors)
            self._finish_batch_progress(success_count, self._patch_total)

            if hasattr(self, 'btn_trans_smart'): self.btn_trans_smart.setEnabled(True)
            if hasattr(self, 'btn_trans_opt'): self.btn_trans_opt.setEnabled(True)
            if hasattr(self, 'btn_trans_special'): self.btn_trans_special.setEnabled(True)
            if hasattr(self, 'btn_patch_eng'): self.btn_patch_eng.setEnabled(True)
            if hasattr(self, 'btn_polish_cinematic'): self.btn_polish_cinematic.setEnabled(True)
            if hasattr(self, 'btn_trans_batch'): self.btn_trans_batch.setEnabled(True)

            self.update_progress_stats()
            self._is_releasing_filter_row = True
            try:
                self.proxy.invalidateFilter()
            finally:
                self._is_releasing_filter_row = False

            if self._patch_errors:
                err_msgs = [f"{gid}: {e}" for r, gid, e in self._patch_errors[:5]]
                self.statusBar().showMessage(f"⚠️ แปลซ่อมสำเร็จ {success_count}/{self._patch_total} แถว (พบข้อผิดพลาด {len(self._patch_errors)} รายการ)", 5000)
                QMessageBox.warning(self, "แปลซ่อมเสร็จสิ้น", f"แปลซ่อมสำเร็จ {success_count} แถว แต่พบข้อผิดพลาดบางรายการ:\n\n" + "\n".join(err_msgs))
            else:
                self.statusBar().showMessage(f"✅ แปลซ่อมคำอังกฤษเฉพาะจุดสำเร็จทั้งหมด {self._patch_total} แถว!", 5000)
                QMessageBox.information(self, "แปลซ่อมสำเร็จ", f"แปลซ่อมคำอังกฤษเฉพาะจุดสำเร็จทั้งหมด {self._patch_total} แถว!\nข้อความภาษาไทยเดิมยังคงอยู่ครบถ้วน")

    def polish_selected_cinematic(self):
        """
        Takes the selected rows (or current row) and asks the AI to polish and rewrite
        stiff, overly literal, or robotic Thai translations into natural, cinematic,
        and idiomatic Thai dialogue (eliminating translationese like 'ฉันจะถูกสาปถ้า...',
        'ยืนอยู่ที่ธรณีประตู', 'ทำการ...', 'ถูก...').
        """
        source_rows = self._get_selected_source_rows()
        if not source_rows:
            if hasattr(self, 'current_source_row') and 0 <= self.current_source_row < len(self.model._data):
                source_rows = [self.current_source_row]
            else:
                QMessageBox.information(self, "ขัดเกลาภาษาพูด (Cinematic Polish)", "กรุณาเลือกบรรทัดในตารางที่ต้องการขัดเกลา")
                return

        # Collect rows that actually have a non-empty translation to polish
        rows_to_polish = []
        for r in source_rows:
            if 0 <= r < len(self.model._data):
                item = self.model._data[r]
                trans_text = str(item.get("trans") or "").strip()
                if trans_text:
                    rows_to_polish.append((r, item))

        if not rows_to_polish:
            self.statusBar().showMessage("⚠️ ไม่พบข้อความแปลภาษาไทยในแถวที่เลือก", 4000)
            QMessageBox.information(self, "ขัดเกลาภาษาพูด", "ไม่พบข้อความแปลภาษาไทยในแถวที่เลือก\n(กรุณาแปลข้อความก่อน หรือกดปุ่ม แปล AI)")
            return

        if len(rows_to_polish) > 5:
            reply = QMessageBox.question(
                self, "ยืนยันการขัดเกลาภาษาพูด",
                f"คุณได้เลือก {len(rows_to_polish)} แถวสำหรับขัดเกลาสำนวนพากย์ไทยภาพยนตร์ (Cinematic Polish)\nต้องการให้ AI ขัดเกลาสำนวนภาษาพูดธรรมชาติ ขจัดสำนวนแปลตรงตัวใช่หรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        from tstudio_core import TStudioCore, CoreAI
        cfg = TStudioCore.load_config()
        self._polish_total = len(rows_to_polish)
        self._polish_completed = 0
        self._polish_errors = []
        self._polish_done_shown = False
        self._start_batch_progress(self._polish_total)

        self.statusBar().showMessage(f"🎬 กำลังขัดเกลาสำนวนภาษาพูด: 0/{self._polish_total} แถว...")

        # Disable buttons during processing
        if hasattr(self, 'btn_trans_smart'): self.btn_trans_smart.setEnabled(False)
        if hasattr(self, 'btn_trans_opt'): self.btn_trans_opt.setEnabled(False)
        if hasattr(self, 'btn_trans_special'): self.btn_trans_special.setEnabled(False)
        if hasattr(self, 'btn_patch_eng'): self.btn_patch_eng.setEnabled(False)
        if hasattr(self, 'btn_polish_cinematic'): self.btn_polish_cinematic.setEnabled(False)
        if hasattr(self, 'btn_trans_batch'): self.btn_trans_batch.setEnabled(False)

        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")

        prof_name = getattr(self, 'current_profile_name', None)
        profile = TStudioCore.get_current_profile_data(prof_name)
        tlm = (profile.get("tlm") or profile.get("tlm_lore") or {}) if profile else {}
        if not isinstance(tlm, dict):
            tlm = {"lore_notes": str(tlm)} if tlm else {}
        game_lore = tlm.get("lore_notes") or tlm.get("lore", "")

        for idx_row, (r_idx, itm) in enumerate(rows_to_polish):
            if idx_row % 15 == 0:
                QApplication.processEvents()
            src_text = itm.get("source", "")
            curr_trans = itm.get("trans", "")
            dyn_glossary = self._get_dynamic_glossary(src_text)

            polish_prompt = (
                "You are an Elite Hollywood Movie Thai Dubbing Scriptwriter and Video Game Localization Expert.\n"
                "Task: Polish and rewrite the stiff, robotic, or overly literal Thai translation into punchy, natural spoken Thai dialogue (พากย์ไทยภาพยนตร์ฮอลลีวูด/สงครามระดับมืออาชีพ).\n\n"
                "CRITICAL POLISHING RULES:\n"
                "1. ELIMINATE TRANSLATIONESE & LITERAL IDIOM TRANSLATIONS:\n"
                "   - Never translate English idioms or metaphors literally word-for-word.\n"
                "   - 'I'll be damned if...' -> 'ไม่มีทางยอมให้... / ฝันไปเถอะว่าฉันจะ...'\n"
                "   - 'at our doorstep' -> 'บุกมาถึงหน้าบ้านเรา / จ่อคอหอยเราอยู่'\n"
                "   - 'go to hell and back to kick them out' -> 'บุกน้ำลุยไฟพลิกแผ่นดินเพื่อไล่ตะเพิดพวกมัน'\n"
                "   - 'on their knees' -> 'ยอมสยบ / คลานเข่าเข้ามาขอร้อง / จนตรอก'\n"
                "   - 'Jerry / Kraut' -> 'พวกนาซี / พวกเยอรมัน'\n"
                "   - 'bite the bullet' -> 'กัดฟันสู้ / จำใจกลืนเลือด'\n"
                "2. NO ROBOTIC SYNTAX: Eliminate unnatural passive voice ('ถูกบังคับให้ถอย' -> 'ต้องล่าถอย') and bureaucratic words ('ทำการ...', 'มีการ...', 'ได้รับการ...'). Use active, spoken dialogue.\n"
                "3. WAR TONE & CURSING: Keep combat intensity, military grit, and profanity authentic (เวรเอ๊ย, ไอ้ระยำ, สารเลว, บัดซบ).\n"
                "4. WEAPONS & CODES: Keep weapon models (MP40, STG44, Flak 88, Panzerhund, RPG, SMG, AR) and calibers in original Latin/alphanumeric script.\n"
                "5. PRESERVE TAGS: Strictly preserve all variables, tags ({...}, <...>, %s, \\n), and punctuation codes.\n"
                "6. Return ONLY the polished Thai string. No commentary, no explanations, no quotes.\n\n"
            )
            if dyn_glossary:
                polish_prompt += dyn_glossary + "\n\n"
            if game_lore:
                polish_prompt += f"Game Lore & Context:\n{game_lore[:300]}\n\n"

            polish_prompt += (
                f"Original English: {src_text}\n"
                f"Current Literal/Stiff Thai: {curr_trans}\n\n"
                "Polished Cinematic Thai:"
            )

            worker = ApiWorker(CoreAI.generate_content, cfg, polish_prompt, is_local=is_local)
            forwarder = ThreadSafeWorkerSignalsForwarder(
                on_success=lambda rep, r=r_idx, it=itm: self._on_polish_row_success(rep, r, it),
                on_error=lambda err, r=r_idx, it=itm: self._on_polish_row_error(err, r, it),
                parent=self
            )
            worker.signals.finished.connect(forwarder.handle_finished)
            worker.signals.error.connect(forwarder.handle_error)
            wid = id(worker)
            worker.signals.finished.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
            worker.signals.error.connect(lambda _, w_id=wid: self._workers.pop(w_id, None))
            self._workers[wid] = worker
            self.batch_threadpool.start(worker)

    def _on_polish_row_success(self, reply, row, itm):
        if getattr(self, '_is_closing', False):
            return
        cleaned = reply.strip()
        cleaned = re.sub(r'^```[a-zA-Z]*\n?|\n?```$', '', cleaned).strip()
        if cleaned.startswith('"') and cleaned.endswith('"') and len(cleaned) >= 2:
            cleaned = cleaned[1:-1].strip()

        old_text = self.model._data[row]["trans"] if 0 <= row < len(self.model._data) else ""
        if cleaned:
            self.model.update_trans(row, cleaned)
            self._update_stats_for_row(row, old_text, cleaned)
            if row == self.current_source_row:
                self.txt_trans.blockSignals(True)
                self.txt_trans.setPlainText(cleaned)
                self.txt_trans.blockSignals(False)

        self._polish_completed += 1
        self._update_polish_progress()

    def _on_polish_row_error(self, err, row, itm):
        if getattr(self, '_is_closing', False):
            return
        g_id = itm.get("id", f"Row {row+1}")
        self._polish_errors.append((row, g_id, str(err)))
        self._polish_completed += 1
        self._update_polish_progress()

    def _update_polish_progress(self):
        if getattr(self, '_is_closing', False):
            return
        if self._polish_completed < self._polish_total:
            pct = int(self._polish_completed / self._polish_total * 100)
            if hasattr(self, '_batch_mini_bar'):
                self._batch_mini_bar.setValue(pct)
                self._batch_count_label.setText(f"{self._polish_completed} / {self._polish_total}")
            self.statusBar().showMessage(f"🎬 กำลังขัดเกลาสำนวนภาษาพูด: {self._polish_completed}/{self._polish_total} แถว...")
        else:
            if getattr(self, '_polish_done_shown', False):
                return
            self._polish_done_shown = True

            if hasattr(self, '_batch_mini_bar'):
                self._batch_mini_bar.setValue(100)
                self._batch_count_label.setText(f"{self._polish_total} / {self._polish_total}")
            success_count = self._polish_total - len(self._polish_errors)
            self._finish_batch_progress(success_count, self._polish_total)

            if hasattr(self, 'btn_trans_smart'): self.btn_trans_smart.setEnabled(True)
            if hasattr(self, 'btn_trans_opt'): self.btn_trans_opt.setEnabled(True)
            if hasattr(self, 'btn_trans_special'): self.btn_trans_special.setEnabled(True)
            if hasattr(self, 'btn_patch_eng'): self.btn_patch_eng.setEnabled(True)
            if hasattr(self, 'btn_polish_cinematic'): self.btn_polish_cinematic.setEnabled(True)
            if hasattr(self, 'btn_trans_batch'): self.btn_trans_batch.setEnabled(True)

            self.update_progress_stats()
            self._is_releasing_filter_row = True
            try:
                self.proxy.invalidateFilter()
            finally:
                self._is_releasing_filter_row = False

            if self._polish_errors:
                err_msgs = [f"{gid}: {e}" for r, gid, e in self._polish_errors[:5]]
                self.statusBar().showMessage(f"⚠️ ขัดเกลาสำเร็จ {success_count}/{self._polish_total} แถว (พบข้อผิดพลาด {len(self._polish_errors)} รายการ)", 5000)
                QMessageBox.warning(self, "ขัดเกลาเสร็จสิ้น", f"ขัดเกลาสำเร็จ {success_count} แถว แต่พบข้อผิดพลาดบางรายการ:\n\n" + "\n".join(err_msgs))
            else:
                self.statusBar().showMessage(f"✅ ขัดเกลาภาษาพูดภาพยนตร์สำเร็จทั้งหมด {self._polish_total} แถว!", 5000)
                QMessageBox.information(self, "ขัดเกลาสำเร็จ", f"ขัดเกลาภาษาพูดภาพยนตร์สำเร็จทั้งหมด {self._polish_total} แถว!\nสำนวนภาษาถูกปรับให้เป็นภาษาพูดธรรมชาติและได้อรรถรสเรียบร้อยแล้ว")

    def export_pua_csv(self):
        if getattr(getattr(self, 'model', None), 'csv_read_error', None):
            return False
        if not self.csv_path:
            QMessageBox.warning(self, _("error_title"), _("csv_path_not_configured"))
            return
            
        pua_path = self.csv_path.replace(".csv", "_PUA.csv")
        try:
            tpua = TPUAEngine()
            
            # Count PUA characters generated
            original_pua_count = 0
            final_pua_count = 0
            
            with open(pua_path, 'w', encoding=self.csv_encoding, newline='') as f:
                import csv
                writer = csv.writer(f)
                headers = getattr(self.model, 'headers_row', None) or getattr(self.model, 'headers', None)
                if headers:
                    writer.writerow(headers)
                col_id = getattr(self.model, 'col_id', COL_ID)
                col_src = getattr(self.model, 'col_src', COL_SOURCE)
                col_trans = getattr(self.model, 'col_trans', COL_TRANS)
                col_ai = getattr(self.model, 'col_ai', COL_AI_REF)
                target_len = len(headers) if headers else (max(col_id, col_src, col_trans, col_ai) + 1)

                for item in self.model._data:
                    raw = item.get("raw_row")
                    if raw is not None:
                        row = list(raw)
                    else:
                        row = [''] * target_len
                    while len(row) < target_len:
                        row.append('')
                    if col_id < len(row): row[col_id] = item["id"]
                    if col_src < len(row): row[col_src] = item["source"]
                    
                    orig_trans = item["trans"]
                    original_pua_count += sum(1 for c in orig_trans if 0xF000 <= ord(c) <= 0xF8FF)
                    
                    pua_trans = tpua.encode(orig_trans)
                    final_pua_count += sum(1 for c in pua_trans if 0xF000 <= ord(c) <= 0xF8FF)
                    
                    if col_trans < len(row): row[col_trans] = pua_trans
                    if 0 <= col_ai < len(row) and "ai_ref" in item:
                        row[col_ai] = str(item.get("ai_ref") or "")
                    writer.writerow(row)
            
            diff = final_pua_count - original_pua_count
            QMessageBox.information(self, _("export_pua_success_title"), f"Successfully exported to:\n{os.path.basename(pua_path)}\n\nReplaced +{diff} PUA characters.")
        except Exception as e:
            QMessageBox.critical(self, _("export_error_title"), str(e))

    def export_original(self):
        if not getattr(self, 'csv_path', None):
            QMessageBox.warning(self, "No File", _("please_open_file_first"))
            return
            
        # ── LANG Export logic ──
        meta_path = self.csv_path.replace(".csv", "_meta.json")
        if os.path.exists(meta_path):
            self.save_csv()
            out_lang, file_ext = QFileDialog.getSaveFileName(self, "Export to LANG File", BASE_DIR, "LANG Files (*.lang)")
            if not out_lang:
                return
            self.statusBar().showMessage("Exporting to LANG file...")
            try:
                reconstruct_lang_file(self.csv_path, meta_path, out_lang)
                self.statusBar().showMessage(f"Exported successfully to {os.path.basename(out_lang)}", 5000)
                QMessageBox.information(self, _("export_success_title"), f"Successfully exported LANG file at:\n{out_lang}")
            except Exception as e:
                QMessageBox.critical(self, _("export_error_title"), f"Failed to export LANG file:\n{e}")
            return

        try:
            from tbundle_manager import TBundleManager
            base_dir = os.path.dirname(self.csv_path)
            json_path = os.path.join(base_dir, f"{os.path.basename(self.csv_path).replace('.csv', '')}_meta.json")
            if os.path.exists(json_path):
                self.save_csv() # Auto save before deploy
                success, msg_or_path = TBundleManager.deploy_csv_to_bundle(self.csv_path)
                if success:
                    QMessageBox.information(self, _("deploy_success_title"), f"Deployed successfully back to Unity Bundle:\n{msg_or_path}")
                else:
                    QMessageBox.warning(self, "Deploy Failed", msg_or_path)
                return
        except Exception as e:
            pass

        from tstudio_core import TFormatManager
        success, msg_or_path = TFormatManager.export_original(self.csv_path)
        if success:
            QMessageBox.information(self, _("export_success_title"), f"Exported successfully to:\n{msg_or_path}")
        else:
            QMessageBox.warning(self, "Export Failed", msg_or_path)

    def save_csv(self):
        if getattr(getattr(self, 'model', None), 'csv_read_error', None):
            return False
        import tempfile, shutil
        if hasattr(self, '_trans_save_timer') and self._trans_save_timer.isActive():
            self._trans_save_timer.stop()
            self.on_trans_changed()

        if not self.csv_path:
            QMessageBox.warning(self, _("error_title"), _("csv_path_not_configured"))
            return
        self.is_saving_csv = True
        try:
            if self.csv_path and os.path.exists(self.csv_path):
                if os.path.getmtime(self.csv_path) > self.last_csv_mtime:
                    self._perform_delta_merge()
        except Exception: pass
        
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=os.path.dirname(os.path.abspath(self.csv_path)),
            suffix='.tmp'
        )
        try:
            with os.fdopen(tmp_fd, 'w', encoding=self.csv_encoding, newline='') as f:
                writer = csv.writer(f)
                headers = getattr(self.model, 'headers_row', None) or getattr(self.model, 'headers', None)
                if headers:
                    writer.writerow(headers)
                col_id = getattr(self.model, 'col_id', COL_ID)
                col_src = getattr(self.model, 'col_src', COL_SOURCE)
                col_trans = getattr(self.model, 'col_trans', COL_TRANS)
                col_ai = getattr(self.model, 'col_ai', COL_AI_REF)
                target_len = len(headers) if headers else (max(col_id, col_src, col_trans, col_ai) + 1)

                for item in self.model._data:
                    raw = item.get("raw_row")
                    if raw is not None:
                        row = list(raw)
                    else:
                        row = [''] * target_len
                    while len(row) < target_len:
                        row.append('')
                    if col_id < len(row): row[col_id] = item["id"]
                    if col_src < len(row): row[col_src] = item["source"]
                    if col_trans < len(row): row[col_trans] = item["trans"]
                    if 0 <= col_ai < len(row) and "ai_ref" in item:
                        row[col_ai] = str(item.get("ai_ref") or "")
                    writer.writerow(row)
            shutil.move(tmp_path, self.csv_path)
            self.model.is_dirty = False
            self.statusBar().showMessage('Saved!', 5000)
            QMessageBox.information(self, _("save_success_title"), f"Translations saved successfully to:\n{self.csv_path}")
            if os.path.exists(self.csv_path):
                self.last_csv_mtime = os.path.getmtime(self.csv_path)
            
            # Ensure companion glossary is synced alongside CSV for portability ("แปลคอมอื่น")
            try:
                prof_name = getattr(self, 'current_profile_name', None) or (self.cbo_profile.currentText() if hasattr(self, 'cbo_profile') else "Default")
                if not self._is_csv_owned_by_profile(self.csv_path, prof_name):
                    print(f"[Ownership Guard] Skipping companion glossary sync on save: '{os.path.basename(self.csv_path)}' does not belong to profile '{prof_name}'")
                else:
                    prof = TStudioCore.get_current_profile_data(prof_name)
                    if prof and "glossary" in prof and prof["glossary"]:
                        csv_dir = os.path.dirname(os.path.abspath(self.csv_path))
                        base_no_ext = os.path.splitext(os.path.basename(self.csv_path))[0]
                        comp_path = os.path.join(csv_dir, f"{base_no_ext}.glossary.json")
                        with open(comp_path, 'w', encoding='utf-8') as gf:
                            json.dump(prof["glossary"], gf, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[Warning] Failed to sync companion glossary on save: {e}")

            self.is_saving_csv = False
            return True
        except Exception as e:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            QMessageBox.critical(self, _("error_title"), f"Failed to save:\n{e}")
        finally:
            self.is_saving_csv = False

    def silent_save_csv(self):
        if getattr(getattr(self, 'model', None), 'csv_read_error', None):
            return False
        import tempfile, shutil
        if hasattr(self, '_trans_save_timer') and self._trans_save_timer.isActive():
            self._trans_save_timer.stop()
            self.on_trans_changed()

        if not self.csv_path or not self.model or not self.model._data:
            return False
            
        self.is_saving_csv = True
        try:
            if self.csv_path and os.path.exists(self.csv_path):
                if os.path.getmtime(self.csv_path) > self.last_csv_mtime:
                    self._perform_delta_merge()
        except Exception: pass
        
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=os.path.dirname(os.path.abspath(self.csv_path)),
            suffix='.tmp'
        )
        try:
            with os.fdopen(tmp_fd, 'w', encoding=self.csv_encoding, newline='') as f:
                writer = csv.writer(f)
                headers = getattr(self.model, 'headers_row', None) or getattr(self.model, 'headers', None)
                if headers:
                    writer.writerow(headers)
                col_id = getattr(self.model, 'col_id', COL_ID)
                col_src = getattr(self.model, 'col_src', COL_SOURCE)
                col_trans = getattr(self.model, 'col_trans', COL_TRANS)
                col_ai = getattr(self.model, 'col_ai', COL_AI_REF)
                target_len = len(headers) if headers else (max(col_id, col_src, col_trans, col_ai) + 1)

                for item in self.model._data:
                    raw = item.get("raw_row")
                    if raw is not None:
                        row = list(raw)
                    else:
                        row = [''] * target_len
                    while len(row) < target_len:
                        row.append('')
                    if col_id < len(row): row[col_id] = item["id"]
                    if col_src < len(row): row[col_src] = item["source"]
                    if col_trans < len(row): row[col_trans] = item["trans"]
                    if 0 <= col_ai < len(row) and "ai_ref" in item:
                        row[col_ai] = str(item.get("ai_ref") or "")
                    writer.writerow(row)
            shutil.move(tmp_path, self.csv_path)
            self.model.is_dirty = False
            if os.path.exists(self.csv_path):
                self.last_csv_mtime = os.path.getmtime(self.csv_path)
            self.statusBar().showMessage(_("status_auto_saved") if _("status_auto_saved") != "status_auto_saved" else "🟢 Auto-Saved", 3000)
            return True
        except Exception as e:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            print(f"Auto-save failed: {e}")
            return False

    def export_origin_format(self):
        if not self.model or not self.model._data:
            QMessageBox.warning(self, _("error_title"), _("export_no_data"))
            return
            
        file_path, filter_str = QFileDialog.getSaveFileName(
            self,
            _("export_origin_title"),
            BASE_DIR,
            "SubRip Subtitle (*.srt);;Web Video Text Tracks (*.vtt);;JSON Files (*.json);;All Files (*.*)"
        )
        
        if not file_path:
            return
            
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.json':
                import json
                export_data = {}
                part_buffers = {}
                
                for item in self.model._data:
                    uid = item["id"]
                    text = item["trans"].strip() if item["trans"].strip() else item["source"].strip()
                    
                    if "_part" in uid:
                        base_key, part_idx = uid.rsplit("_part", 1)
                        if base_key not in part_buffers:
                            part_buffers[base_key] = []
                        part_buffers[base_key].append((int(part_idx), text))
                    else:
                        export_data[uid] = text
                        
                # Merge part buffers
                for base_key, parts in part_buffers.items():
                    # Sort by part index
                    parts.sort(key=lambda x: x[0])
                    merged_text = "".join(p[1] for p in parts)
                    export_data[base_key] = merged_text
                    
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=4)
            else:
                with open(file_path, 'w', encoding='utf-8-sig') as f:
                    if ext == '.vtt':
                        f.write("WEBVTT\n\n")
                        
                    for item in self.model._data:
                        uid = item["id"]
                        text = item["trans"].strip() if item["trans"].strip() else item["source"].strip()
                        
                        parts = uid.split('|', 1)
                        if len(parts) == 2:
                            idx, timestamp = parts
                        else:
                            idx = ""
                            timestamp = uid
                            
                        if ext == '.srt':
                            if idx:
                                f.write(f"{idx}\n")
                            timestamp = timestamp.replace('.', ',')
                            f.write(f"{timestamp}\n")
                            f.write(f"{text}\n\n")
                        elif ext == '.vtt':
                            timestamp = timestamp.replace(',', '.')
                            if not re.search(r'\d{2}:\d{2}:\d{2}', timestamp):
                                pass
                            f.write(f"{timestamp}\n")
                            f.write(f"{text}\n\n")
                        else:
                            f.write(f"{text}\n")
                        
            QMessageBox.information(self, _("success_title"), f"Exported to {os.path.basename(file_path)} successfully!")
        except Exception as e:
            QMessageBox.critical(self, _("error_title"), f"Failed to export: {str(e)}")

    def deploy_to_game(self):
        if not hasattr(self, 'csv_path') or not self.csv_path:
            QMessageBox.warning(self, _("error_title"), _("no_file_loaded"))
            return

        try:
            from tstudio_core import TStudioCore
            cfg = TStudioCore.load_config()
            origin_file = cfg.get("origin_file", "")
            
            # ── JSON MESG Deploy logic ──
            if origin_file and origin_file.lower().endswith('.json'):
                try:
                    import json
                    with open(origin_file, 'r', encoding='utf-8') as f:
                        odata = json.load(f)
                    if isinstance(odata, dict) and "m_Script" in odata and isinstance(odata["m_Script"], str) and odata["m_Script"].startswith("MESG"):
                        self.save_csv()
                        reply = QMessageBox.question(self, "Deploy MESG JSON", 
                                                     f"Are you sure you want to overwrite the original JSON file at:\n{origin_file}?\n(Warning: Strings will be byte-padded/truncated to preserve pointers)",
                                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                        if reply == QMessageBox.StandardButton.Yes:
                            self.statusBar().showMessage("Deploying to MESG JSON...")
                            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                            try:
                                reconstruct_mesg_json_file(self.csv_path, origin_file)
                                QApplication.restoreOverrideCursor()
                                QMessageBox.information(self, "Success", f"Successfully deployed to MESG JSON at:\n{origin_file}")
                            except Exception as e:
                                QApplication.restoreOverrideCursor()
                                QMessageBox.critical(self, "Error", f"Failed to deploy MESG JSON:\n{str(e)}")
                        return
                except:
                    pass

            # ── LANG Deploy logic ──
            if origin_file and origin_file.lower().endswith('.lang'):
                meta_path = self.csv_path.replace(".csv", "_meta.json")
                if os.path.exists(meta_path):
                    self.save_csv()
                    reply = QMessageBox.question(self, _("deploy_lang_title"), 
                                                 f"Are you sure you want to overwrite the original LANG file at:\n{origin_file}?",
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        self.statusBar().showMessage("Deploying to LANG file...")
                        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                        try:
                            reconstruct_lang_file(self.csv_path, meta_path, origin_file)
                            QApplication.restoreOverrideCursor()
                            QMessageBox.information(self, _("deploy_success_title"), f"Successfully deployed to LANG file at:\n{origin_file}")
                        except Exception as e:
                            QApplication.restoreOverrideCursor()
                            QMessageBox.critical(self, _("deploy_error_title"), f"Failed to deploy LANG file:\n{str(e)}")
                    return

            if origin_file and origin_file.lower().endswith('.win') and "utmt" in self.csv_path.lower():
                self.save_csv()
                reply = QMessageBox.question(self, _("deploy_gamemaker_title"), 
                                             f"Are you sure you want to pack translations back into:\n{origin_file}?\n(This may take a few minutes)",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.statusBar().showMessage("Packing translations to data.win...")
                    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                    try:
                        import sys
                        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Core"))
                        from utmt_handler import UTMTHandler
                        out_win = UTMTHandler.repack_strings_from_csv(origin_file, self.csv_path)
                        QApplication.restoreOverrideCursor()
                        QMessageBox.information(self, _("deploy_success_title"), f"Successfully modded GameMaker archive at:\n{out_win}")
                    except Exception as e:
                        QApplication.restoreOverrideCursor()
                        QMessageBox.critical(self, _("deploy_error_title"), f"Failed to repack .win:\n{str(e)}")
                return

            if origin_file and origin_file.lower().endswith('.pak'):
                self.save_csv()
                reply = QMessageBox.question(self, "Deploy PAK File", 
                                             f"Are you sure you want to pack translations back into:\n{origin_file}?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.statusBar().showMessage("Packing translations to PAK file...")
                    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                    try:
                        from tstudio_core import TPakManager
                        TPakManager.reconstruct_pak_file(origin_file, self.csv_path, origin_file)
                        QApplication.restoreOverrideCursor()
                        QMessageBox.information(self, _("deploy_success_title"), f"Successfully deployed to PAK file at:\n{origin_file}")
                    except Exception as e:
                        QApplication.restoreOverrideCursor()
                        QMessageBox.critical(self, _("deploy_error_title"), f"Failed to deploy PAK file:\n{str(e)}")
                return
        except Exception as e:
            # Only restore cursor if we actually set it in the inner try block.
            # The outer except catches errors before setOverrideCursor is called
            # (e.g. user clicked 'No', or config load failed), so we must not
            # call restoreOverrideCursor unconditionally here — that would pop
            # an extra level and leave the cursor in WaitCursor permanently.
            # The inner try/except blocks each call restoreOverrideCursor already;
            # we just log here.
            print(f"Error checking win deploy: {e}")
            
        if self.csv_path.endswith('.landb.csv'):
            # Telltale Deploy logic
            self.save_csv()
            input_dir = os.path.dirname(self.csv_path)
            
            out_ttarch2, file_ext = QFileDialog.getSaveFileName(self, "Save Modded Telltale Archive", BASE_DIR, "Telltale Archives (*.ttarch2)")
            if not out_ttarch2:
                return
                
            self.statusBar().showMessage(_("deploy_telltale_msg"))
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            try:
                from tstudio_telltale import TelltaleManager
                manager = TelltaleManager()
                # Inject CSV into landb files in input_dir
                manager.convert_csv_to_landb(self.csv_path, input_dir)
                
                # Pack the directory
                success, msg = manager.pack_ttarch2(input_dir, out_ttarch2)
                
                QApplication.restoreOverrideCursor()
                if success:
                    QMessageBox.information(self, _("success_title"), f"Modded archive successfully created at:\n{out_ttarch2}")
                else:
                    QMessageBox.critical(self, _("error_title"), f"Failed to pack archive:\n{msg}")
            except Exception as e:
                QApplication.restoreOverrideCursor()
                QMessageBox.critical(self, _("error_title"), f"An error occurred during deployment:\n{str(e)}")
            return

        # Fallback for generic files: Use Template Replacement via Custom Dialog
        from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout
        dialog = QDialog(self)
        dialog.setWindowTitle(_("deploy_template_title"))
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()
        
        txt_template = QLineEdit()
        btn_template = QPushButton(_("browse_btn"))
        btn_template.setToolTip(_("tooltip_btn_template"))
        lay_template = QHBoxLayout()
        lay_template.addWidget(txt_template)
        lay_template.addWidget(btn_template)
        form_layout.addRow(_("original_template_file"), lay_template)
        
        txt_save = QLineEdit()
        btn_save = QPushButton(_("browse_btn"))
        btn_save.setToolTip(_("tooltip_btn_save"))
        lay_save = QHBoxLayout()
        lay_save.addWidget(txt_save)
        lay_save.addWidget(btn_save)
        form_layout.addRow(_("save_deployed_file"), lay_save)
        
        layout.addLayout(form_layout)
        
        btn_deploy = QPushButton(_("btn_deploy"))
        btn_deploy.setToolTip(_("tooltip_btn_deploy"))
        btn_deploy.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 8px;")
        layout.addWidget(btn_deploy)
        
        def browse_template():
            path, file_ext = QFileDialog.getOpenFileName(dialog, "Select Original Template File", BASE_DIR, "All Files (*.*)")
            if path:
                txt_template.setText(path)
                # Auto-fill save path
                import os
                base, ext = os.path.splitext(path)
                txt_save.setText(f"{base}_translated{ext}")
                
        def browse_save():
            path, file_ext = QFileDialog.getSaveFileName(dialog, "Select Save Location", txt_save.text() or BASE_DIR, "All Files (*.*)")
            if path:
                txt_save.setText(path)
                
        btn_template.clicked.connect(browse_template)
        btn_save.clicked.connect(browse_save)
        btn_deploy.clicked.connect(dialog.accept)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            template_path = txt_template.text()
            save_path = txt_save.text()
            
            if not template_path or not save_path:
                QMessageBox.warning(self, _("warning_title"), _("please_specify_both_paths"))
                return
                
            try:
                self.statusBar().showMessage("Deploying using template...")
                QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                
                # Auto-detect encoding
                encoding = 'utf-8'
                try:
                    import chardet
                    with open(template_path, 'rb') as f:
                        raw = f.read()
                        res = chardet.detect(raw)
                        if res and res.get('encoding'):
                            encoding = res['encoding']
                except Exception:
                    encoding = 'utf-8'
                    
                with open(template_path, 'r', encoding=encoding, errors='ignore') as f:
                    template_text = f.read()
                    
                replace_count = 0
                
                # Sort by length descending to prevent shorter strings from replacing parts of longer strings
                sorted_data = sorted(self.model._data, key=lambda x: len(x.get("source", "")), reverse=True)
                
                for item in sorted_data:
                    src = item.get("source", "").replace('\n', '\n')
                    trans = item.get("trans", "").replace('\n', '\n').strip()
                    if not trans:
                        trans = str(item.get("ai_ref") or "").replace('\n', '\n').strip()
                        
                    if trans and src and src != trans:
                        # Safeguard: Restore missing {Tags} and [Tags] at the beginning
                        tags_match = re.match(r'^((?:\[.*?\]|\{.*?\})\s*)+', src)
                        if tags_match:
                            tags = tags_match.group(0)
                            if not trans.startswith(tags.strip()):
                                # Strip any potentially mangled tags from trans before prepending original
                                trans_clean = re.sub(r'^((?:\[.*?\]|\{.*?\})\s*)+', '', trans)
                                trans = tags + trans_clean

                        if src in template_text:
                            template_text = template_text.replace(src, trans)
                            replace_count += 1
                            
                with open(save_path, 'w', encoding='utf-8-sig') as f:
                    f.write(template_text)
                    
                QApplication.restoreOverrideCursor()
                QMessageBox.information(self, _("deploy_success_title"), f"Successfully deployed {replace_count} translations to:\n{save_path}")
            except Exception as e:
                QApplication.restoreOverrideCursor()
                QMessageBox.critical(self, _("error_title"), f"Failed to deploy with template:\n{str(e)}")


    def on_external_csv_changed(self, path):
        if self.is_saving_csv or not self.csv_path or not os.path.exists(self.csv_path):
            return
        try:
            mtime = os.path.getmtime(self.csv_path)
            if mtime <= self.last_csv_mtime:
                return
            self.last_csv_mtime = mtime
            QTimer.singleShot(100, lambda: self._perform_delta_merge())
        except Exception as e:
            print(f"Live sync error: {e}")

    def _perform_delta_merge(self):
        if not self.csv_path or not os.path.exists(self.csv_path): return
        try:
            new_rows = []
            existing_ids = {str(item.get('id', '')) for item in self.model._data}
            import csv
            with open(self.csv_path, 'r', encoding=self.csv_encoding, errors='replace', newline='') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                for row in reader:
                    if not row: continue
                    row_id = str(row[COL_ID]) if len(row) > COL_ID else ""
                    if row_id and row_id not in existing_ids:
                        item = {
                            "id": row_id,
                            "source": row[COL_SOURCE] if len(row) > COL_SOURCE else "",
                            "trans": row[COL_TRANS] if len(row) > COL_TRANS else "",
                            "ai_ref": row[COL_AI_REF] if len(row) > COL_AI_REF else "",
                            "raw_row": list(row)
                        }
                        new_rows.append(item)
            if new_rows:
                self.model.beginInsertRows(QModelIndex(), len(self.model._data), len(self.model._data) + len(new_rows) - 1)
                self.model._data.extend(new_rows)
                self.model.endInsertRows()
                self.statusBar().showMessage(f"Live Sync: Loaded {len(new_rows)} new texts from game!", 5000)
                self.update_progress_stats()
        except Exception as e:
            print(f"Delta merge error: {e}")

    def closeEvent(self, event):
        if hasattr(self, '_trans_save_timer') and self._trans_save_timer.isActive():
            self._trans_save_timer.stop()
            self.on_trans_changed()

        if hasattr(self, 'model') and getattr(self.model, 'is_dirty', False):
            reply = QMessageBox.question(
                self, _("unsaved_changes_title"),
                _("unsaved_before_exit"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.save_csv()
                self.save_layout_state()
            elif reply == QMessageBox.StandardButton.No:
                self.save_layout_state()
            else:
                event.ignore()
                return

        else:
            self.save_layout_state()

        # FIX: Signal all in-flight batch workers to drop their callbacks, then
        # wait up to 3 s for the thread-pool to drain so no callback fires into
        # a half-destroyed window after this point.
        self._is_closing = True
        if hasattr(self, 'batch_threadpool') and self.batch_threadpool:
            try:
                self.batch_threadpool.clear()
            except Exception:
                pass
        # Clean up TRun batch runner
        if hasattr(self, 'batch_dock') and self.batch_dock:
            try:
                self.batch_dock.stop_translation()
            except Exception:
                pass

        event.accept()


    def on_toggle_qa_marker(self, checked):
        try:
            self._html_cache_version = getattr(self, '_html_cache_version', 0) + 1
            if checked:
                self._compile_glossary_cache()
            if hasattr(self, 'table') and self.table:
                self.table.viewport().update()
            self._refresh_current_row_editor_glossary()
        except Exception as e:
            print(f"[Warning] on_toggle_qa_marker suppressed: {e}")
            
    def recheck_qa_for_row(self, row_idx):
        if not hasattr(self, 'model') or not self.model or not getattr(self.model, 'is_qa_enabled', False):
            return False
        if not getattr(self.model, '_data', None):
            return False
        if row_idx < 0 or row_idx >= len(self.model._data):
            return False

        try:
            from tstudio_core import TStudioCore
            prof_name = getattr(self, 'current_profile_name', None) or "Default"
            if hasattr(self, '_profiles_data') and isinstance(self._profiles_data, dict):
                profile = self._profiles_data.get("presets", {}).get(prof_name, {})
            else:
                profile = TStudioCore.get_current_profile_data(prof_name)
            glossary = profile.get("glossary", {}) if isinstance(profile, dict) else {}
            if not isinstance(glossary, dict) or not glossary:
                return False

            item = self.model._data[row_idx]
            raw_src = item.get("source")
            source_text = str(raw_src) if raw_src is not None else ""
            raw_trans = item.get("trans")
            trans_text = str(raw_trans) if raw_trans is not None else ""

            has_error = False
            if trans_text.strip():
                if TStudioCore.has_cjk(trans_text):
                    has_error = True
                elif glossary:
                    if not hasattr(self, '_cached_glossary_pat'):
                        self._compile_glossary_cache()
                    pat = getattr(self, '_cached_glossary_pat', None)
                    term_info = getattr(self, '_cached_term_info', {})
                    if pat and term_info:
                        for m in pat.finditer(html.escape(source_text)):
                            k = m.group(1).lower()
                            if k in term_info:
                                target_th = term_info[k][1]
                                if target_th and target_th.lower() not in trans_text.lower():
                                    has_error = True
                                    break
                    else:
                        sorted_glossary = sorted(glossary.items(), key=lambda x: len(str(x[0])), reverse=True)
                        for eng, val in sorted_glossary:
                            eng_str = str(eng).strip()
                            if not eng_str: continue
                            _prefix = r'\b' if re.match(r'^\w', eng_str) else r''
                            _suffix = r'\b' if re.search(r'\w$', eng_str) else r''
                            pattern = _prefix + r'(' + re.escape(eng_str) + r')' + _suffix
                            if re.search(pattern, source_text, re.IGNORECASE):
                                thai = val[0] if (isinstance(val, list) and len(val) > 0) else val
                                thai_str = str(thai) if thai is not None else ""
                                if thai_str and thai_str.lower() not in trans_text.lower():
                                    has_error = True
                                    break

            if item.get("qa_failed") != has_error:
                item["qa_failed"] = has_error
                return True
            return False
        except Exception as e:
            print(f"[Warning] recheck_qa_for_row suppressed: {e}")
            return False
            
    def on_toggle_qa(self, checked):
        if getattr(self, '_qa_running', False):
            self.act_toggle_qa.blockSignals(True)
            self.act_toggle_qa.setChecked(not checked)  # revert
            self.act_toggle_qa.blockSignals(False)
            return
        self._qa_running = True
        try:
            self.model.is_qa_enabled = checked
            if not checked:
                # Clear QA flags
                for item in self.model._data:
                    item["qa_failed"] = False
                self.model.layoutChanged.emit()
                self.proxy.invalidateFilter()
                return

            # Run QA Check with precompiled single-pass regex (90x faster than double loop)
            if not hasattr(self, '_cached_glossary_pat'):
                self._compile_glossary_cache()
            pat = getattr(self, '_cached_glossary_pat', None)
            term_info = getattr(self, '_cached_term_info', {})

            failed_count = 0
            cjk_count = 0

            for item in self.model._data:
                item["qa_failed"] = False # Reset first
                trans_text = str(item.get("trans") or "")
                if not trans_text.strip():
                    continue

                has_error = False
                # Check 1: CJK character leak
                if TStudioCore.has_cjk(trans_text):
                    has_error = True
                    cjk_count += 1
                elif pat and term_info:
                    source_text = str(item.get("source") or "")
                    for m in pat.finditer(html.escape(source_text)):
                        grp = m.group(1)
                        if not grp: continue
                        k = grp.lower()
                        if k in term_info:
                            target_th = term_info[k][1]
                            if target_th and target_th.lower() not in trans_text.lower():
                                has_error = True
                                break

                if has_error:
                    item["qa_failed"] = True
                    failed_count += 1

            # Refresh the model
            self.model.layoutChanged.emit()
            if hasattr(self, 'proxy') and self.proxy:
                self.proxy.invalidateFilter()
            
            from PyQt6.QtWidgets import QMessageBox
            if failed_count > 0:
                extra_cjk_msg = f"\n(พบข้อความภาษาจีน/CJK หลุดมา {cjk_count} แถว)" if cjk_count > 0 else ""
                QMessageBox.warning(self, "QA Check", _("qa_failed_msg").format(failed=failed_count) + extra_cjk_msg)
            else:
                QMessageBox.information(self, "QA Check", _("qa_success_msg"))
        finally:
            self._qa_running = False

    def refresh_glossary_dependent_features(self):
        # 1. Reload profiles data in memory to ensure it is in sync with disk
        from tstudio_core import TStudioCore
        self._profiles_data = TStudioCore.load_profiles()
        self._compile_glossary_cache()
        
        # Guard: Ensure model exists and has data before running table-dependent updates
        if not hasattr(self, 'model') or not self.model or not getattr(self.model, '_data', None):
            return

        # 2. Update HTML sources for terms highlight (O(1) Lazy Viewport Update)
        self._html_cache_version = getattr(self, '_html_cache_version', 0) + 1
        if hasattr(self, 'table') and self.table:
            self.table.viewport().update()

        # 3. Re-run QA check if enabled (Single-Pass Precompiled Regex)
        if hasattr(self, 'model') and self.model and getattr(self.model, 'is_qa_enabled', False):
            pat = getattr(self, '_cached_glossary_pat', None)
            term_info = getattr(self, '_cached_term_info', {})

            for item in self.model._data:
                item["qa_failed"] = False # Reset
                trans_text = str(item.get("trans") or "")
                if not trans_text.strip():
                    continue

                has_error = False
                if TStudioCore.has_cjk(trans_text):
                    has_error = True
                elif pat and term_info:
                    source_text = str(item.get("source") or "")
                    for m in pat.finditer(html.escape(source_text)):
                        grp = m.group(1)
                        if not grp: continue
                        k = grp.lower()
                        if k in term_info:
                            target_th = term_info[k][1]
                            if target_th and target_th.lower() not in trans_text.lower():
                                has_error = True
                                break

                if has_error:
                    item["qa_failed"] = True

            if hasattr(self.model, 'layoutChanged'):
                (self.model.layoutChanged.emit() if hasattr(self.model.layoutChanged, 'emit') else self.model.layoutChanged())
            if hasattr(self, 'proxy') and self.proxy:
                self.proxy.invalidateFilter()
            
        # 4. Refresh the current selected row glossary markers in txt_source
        self._refresh_current_row_editor_glossary()

    def _get_selected_source_rows(self):
        """Returns sorted unique source model row indices currently selected in the table."""
        selected_indexes = self.table.selectionModel().selectedRows()
        if not selected_indexes:
            # Fallback if cells rather than entire rows were selected
            row_set = {idx.row() for idx in self.table.selectionModel().selectedIndexes()}
            selected_indexes = [self.proxy.index(r, 0) for r in row_set if self.proxy.index(r, 0).isValid()]
        if not selected_indexes:
            curr = self.table.currentIndex()
            if curr.isValid():
                selected_indexes = [curr]

        source_rows = set()
        for idx in selected_indexes:
            if idx.isValid():
                src_idx = self.proxy.mapToSource(idx)
                if src_idx.isValid() and 0 <= src_idx.row() < len(self.model._data):
                    source_rows.add(src_idx.row())
        return sorted(source_rows)

    def send_selection_to_trun(self, auto_start=False):
        """Send currently selected rows from CAT table directly to TRun Batch Runner."""
        source_rows = self._get_selected_source_rows()
        if not source_rows:
            QMessageBox.information(self, "ยังไม่ได้เลือกข้อความ", "กรุณาลากคลุมเลือกแถวที่ต้องการแปลในตารางก่อน")
            return

        rows_to_translate = [r for r in source_rows if 0 <= r < len(self.model._data) and self.model._data[r]["source"].strip()]
        if not rows_to_translate:
            QMessageBox.information(self, "ไม่มีข้อความต้นฉบับ", "แถวที่เลือกไม่มีข้อความต้นฉบับสำหรับแปล")
            return

        # Switch workspace mode to TRun
        self.switch_workspace_mode('trun')

        # Configure TRun dock for selected rows
        if hasattr(self, 'batch_dock') and self.batch_dock:
            self.batch_dock.radio_selected_rows.setChecked(True)
            self.batch_dock._on_target_mode_changed()
            self.batch_dock.sync_active_file_info()

            if auto_start:
                self.batch_dock.start_translation()
            else:
                self.batch_dock.log(
                    f"🎯 โอนย้าย {len(rows_to_translate):,} แถวที่เลือกจากตาราง CAT เรียบร้อยแล้ว! "
                    f"(ตรวจสอบการตั้งค่าแล้วกดปุ่ม '🚀 เริ่มรันแปล' ได้ทันที)", "#a6e3a1"
                )

    def clean_selected_cjk(self):
        source_rows = self._get_selected_source_rows()
        if not source_rows:
            QMessageBox.information(self, "Clean Chinese", "กรุณาเลือกแถวในตารางก่อน")
            return

        from tstudio_core import TStudioCore
        cleaned_count = 0
        for source_row in source_rows:
            if 0 <= source_row < len(self.model._data):
                item = self.model._data[source_row]
                current_trans = item.get("trans", "")
                changed = False
                if current_trans and TStudioCore.has_cjk(current_trans):
                    new_trans = TStudioCore.clean_cjk_leak(current_trans)
                    if new_trans != current_trans:
                        item["trans"] = new_trans
                        changed = True
                current_ai = str(item.get("ai_ref") or "")
                if current_ai and TStudioCore.has_cjk(current_ai):
                    new_ai = TStudioCore.clean_cjk_leak(current_ai)
                    if new_ai != current_ai:
                        item["ai_ref"] = new_ai
                        changed = True
                if changed:
                    self.model.update_trans(source_row, item["trans"])
                    cleaned_count += 1

        if cleaned_count > 0:
            self.statusBar().showMessage(f"ล้างคอมเมนต์ภาษาจีนสำเร็จ {cleaned_count} แถว!", 4000)
            if hasattr(self, 'current_source_row') and self.current_source_row in source_rows:
                curr_item = self.model._data[self.current_source_row]
                self.txt_trans.setPlainText(curr_item.get("trans", ""))
                if hasattr(self, 'txt_ai'):
                    self.txt_ai.setPlainText(str(curr_item.get("ai_ref") or ""))
            self._is_releasing_filter_row = True
            try:
                self.proxy.invalidateFilter()
            finally:
                self._is_releasing_filter_row = False
        else:
            self.statusBar().showMessage("ไม่พบคอมเมนต์ภาษาจีนที่ตัดได้ในแถวที่เลือก", 3000)

    def clear_selected_translations(self, only_ai=False):
        """Clears translations for selected rows (or current row).
        If only_ai is True, clears only the AI suggestion column (ai_ref).
        If only_ai is False, clears trans, ai_ref, is_th, and qa_failed back to 'รอแปล'."""
        source_rows = self._get_selected_source_rows()
        if not source_rows:
            if hasattr(self, 'current_source_row') and 0 <= self.current_source_row < len(self.model._data):
                source_rows = [self.current_source_row]
            else:
                self.statusBar().showMessage("กรุณาเลือกบรรทัดที่ต้องการลบคำแปล", 3000)
                return

        try:
            # Block dataChanged signal during batch update to avoid repeated auto-save triggers
            self.model.dataChanged.disconnect(self.on_model_data_changed)
        except Exception:
            pass

        try:
            for row in source_rows:
                if 0 <= row < len(self.model._data):
                    item = self.model._data[row]
                    if only_ai:
                        item["ai_ref"] = ""
                    else:
                        item["trans"] = ""
                        item["ai_ref"] = ""
                        item["is_th"] = False
                        item["qa_failed"] = False

            self.is_dirty = True
            self.model.is_dirty = True

            # Emit dataChanged for each cleared row individually (safe, no layoutChanged)
            for row in source_rows:
                idx_start = self.model.index(row, 0)
                idx_end = self.model.index(row, 4)
                self.model.dataChanged.emit(idx_start, idx_end, [
                    Qt.ItemDataRole.DisplayRole,
                    Qt.ItemDataRole.ForegroundRole,
                    Qt.ItemDataRole.UserRole
                ])

            # Update the editor text boxes if current row was cleared
            if hasattr(self, 'current_source_row') and self.current_source_row in source_rows:
                if not only_ai and hasattr(self, 'txt_trans'):
                    self.txt_trans.setPlainText("")
                if hasattr(self, 'txt_ai'):
                    self.txt_ai.setPlainText("")

            # Update stats & progress bar
            self.update_progress_stats()

            msg = f"ลบผลแปล AI {len(source_rows):,} บรรทัดเรียบร้อย" if only_ai else f"ลบคำแปล {len(source_rows):,} บรรทัดเรียบร้อย (สถานะกลับเป็นรอแปล)"
            self.statusBar().showMessage(msg, 3500)

            # Trigger one auto-save after batch is done
            if hasattr(self, '_csv_auto_save_timer'):
                self._csv_auto_save_timer.start(2000)

            self._is_releasing_filter_row = True
            try:
                self.proxy.invalidateFilter()
            finally:
                self._is_releasing_filter_row = False

            if hasattr(self, 'batch_dock') and self.batch_dock:
                try:
                    self.batch_dock.sync_active_file_info()
                except Exception:
                    pass

        finally:
            # Always reconnect the signal
            try:
                self.model.dataChanged.connect(self.on_model_data_changed)
            except Exception:
                pass

    def clear_all_translations(self, only_ai=False):
        """Clears all translations across the entire active file with a safety confirmation dialog.
        If only_ai is True, clears only the AI draft column.
        If only_ai is False, clears both trans and ai_ref, resetting all rows back to 'รอแปล'."""
        if not hasattr(self, 'model') or not self.model._data:
            QMessageBox.information(self, "ลบคำแปลทั้งหมด", "ไม่มีข้อมูลโปรเจกต์ที่เปิดอยู่")
            return

        total_rows = len(self.model._data)
        if only_ai:
            count = sum(1 for item in self.model._data if str(item.get("ai_ref", "")).strip())
            if count == 0:
                QMessageBox.information(self, "ลบผลแปล AI ทั้งหมด", f"ไม่มีผลแปล AI ที่บันทึกไว้ในไฟล์นี้\n(ทั้งหมด {total_rows:,} บรรทัดไม่มีข้อมูล AI)")
                return

            reply = QMessageBox.question(
                self,
                "🤖 ยืนยันการลบผลแปล AI ทั้งหมด (Clear All AI Drafts)",
                f"คุณต้องการลบเฉพาะผลแปล AI ทั้งหมดในไฟล์นี้ใช่หรือไม่?\n\n"
                f"📊 ข้อมูลที่จะถูกล้าง: {count:,} / {total_rows:,} บรรทัด\n\n"
                f"🛡️ ความปลอดภัยของข้อมูล:\n"
                f"✓ คำแปลภาษาไทยที่คุณตรวจหรือบันทึกแล้ว จะคงอยู่ปลอดภัยครบถ้วน\n"
                f"✓ ข้อความภาษาอังกฤษต้นฉบับและ ID จะคงอยู่ปลอดภัย 100%\n"
                f"✓ เฉพาะคอลัมน์ 'แปลโดย AI' เท่านั้นที่จะถูกล้างออก",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
        else:
            count = sum(
                1 for item in self.model._data
                if str(item.get("trans", "")).strip() or str(item.get("ai_ref", "")).strip() or item.get("is_th")
            )
            if count == 0:
                QMessageBox.information(
                    self, "ลบคำแปลทั้งหมด",
                    f"ไม่มีคำแปลที่ต้องลบในไฟล์นี้\n(ทั้งหมด {total_rows:,} บรรทัดมีสถานะ 'รอแปล' อยู่แล้ว)"
                )
                return

            reply = QMessageBox.question(
                self,
                "⚠️ ยืนยันการลบคำแปลทั้งหมด (Clear All Translations)",
                f"คุณต้องการลบคำแปลทั้งหมดในไฟล์นี้ใช่หรือไม่?\n\n"
                f"📊 สถิติคำแปลปัจจุบัน:\n"
                f"• บรรทัดที่มีคำแปล: {count:,} บรรทัด\n"
                f"• บรรทัดทั้งหมดในไฟล์: {total_rows:,} บรรทัด\n\n"
                f"🛡️ ความปลอดภัยของข้อมูล:\n"
                f"✓ ข้อความภาษาอังกฤษต้นฉบับ (Source) และ ID ทั้งหมดจะคงอยู่ปลอดภัย 100%\n"
                f"✓ ช่อง 'คำแปลภาษาไทย' และ 'แปลโดย AI' ทั้งหมดจะถูกล้างกลับเป็น 'รอแปล'\n\n"
                f"⚠️ คำเตือน: การดำเนินการนี้จะล้างคำแปลทั้งหมดของไฟล์ปัจจุบัน คุณแน่ใจหรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self.model.dataChanged.disconnect(self.on_model_data_changed)
        except Exception:
            pass

        try:
            for item in self.model._data:
                if only_ai:
                    item["ai_ref"] = ""
                else:
                    item["trans"] = ""
                    item["ai_ref"] = ""
                    item["is_th"] = False
                    item["qa_failed"] = False

            self.is_dirty = True
            self.model.is_dirty = True

            # Notify table model of total layout change
            self.model.layoutChanged.emit()

            if not only_ai and hasattr(self, 'txt_trans'):
                self.txt_trans.setPlainText("")
            if hasattr(self, 'txt_ai'):
                self.txt_ai.setPlainText("")

            self.update_progress_stats()

            done_msg = f"ลบผลแปล AI ทั้งหมด {count:,} บรรทัดเรียบร้อย" if only_ai else f"ลบคำแปลทั้งหมด {count:,} บรรทัดเรียบร้อย (สถานะกลับเป็นรอแปล)"
            self.statusBar().showMessage(done_msg, 4000)

            if hasattr(self, '_csv_auto_save_timer'):
                self._csv_auto_save_timer.start(1000)

            self._is_releasing_filter_row = True
            try:
                self.proxy.invalidateFilter()
            finally:
                self._is_releasing_filter_row = False

            if hasattr(self, 'batch_dock') and self.batch_dock:
                try:
                    self.batch_dock.sync_active_file_info()
                except Exception:
                    pass

            QMessageBox.information(
                self,
                "ลบคำแปลสำเร็จ",
                f"✅ ดำเนินการเรียบร้อยแล้ว!\n\n"
                f"• ล้างข้อมูล: {count:,} บรรทัด\n"
                f"• บรรทัดทั้งหมดในไฟล์: {total_rows:,} บรรทัด"
            )
        finally:
            try:
                self.model.dataChanged.connect(self.on_model_data_changed)
            except Exception:
                pass


    def delete_selected_rows(self, confirm=True):
        source_rows = self._get_selected_source_rows()
        if not source_rows:
            return

        count = len(source_rows)
        if confirm:
            reply = QMessageBox.question(
                self,
                "ยืนยันการลบบรรทัด (Confirm Delete Rows)",
                f"คุณแน่ใจหรือไม่ว่าต้องการลบแถวที่เลือกทั้งหมด {count} แถวออกจากโปรเจกต์/CSV นี้?\n\n⚠️ ข้อมูลจะถูกลบออกจากไฟล์เมื่อทำการบันทึก และไม่สามารถเลิกทำ (Undo) ได้",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            # Block dataChanged signal during delete to prevent premature auto-saves
            self.model.dataChanged.disconnect(self.on_model_data_changed)
        except Exception:
            pass

        try:
            deleted_count = self.model.delete_rows(source_rows)
            self.is_dirty = True

            # Clear selection and editors
            self.table.clearSelection()
            self.txt_source.setPlainText("")
            self.txt_trans.setPlainText("")
            if hasattr(self, 'current_source_row'):
                self.current_source_row = -1

            # Update stats & progress bar
            self.update_progress_stats()

            # Attempt to select a valid row near the deleted range
            if self.proxy.rowCount() > 0:
                first_del = min(source_rows)
                target_proxy_row = min(first_del, self.proxy.rowCount() - 1)
                new_idx = self.proxy.index(target_proxy_row, 0)
                if new_idx.isValid():
                    self.table.setCurrentIndex(new_idx)
                    self.table.selectRow(target_proxy_row)

            self.statusBar().showMessage(f"🗑️ ลบข้อมูลสำเร็จ {deleted_count} บรรทัด", 4000)

            if hasattr(self, '_csv_auto_save_timer'):
                self._csv_auto_save_timer.start(1000)
        finally:
            try:
                self.model.dataChanged.connect(self.on_model_data_changed)
            except Exception:
                pass

    def on_delete_key_pressed(self):
        source_rows = self._get_selected_source_rows()
        if not source_rows:
            return

        count = len(source_rows)
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("จัดการแถวที่เลือก (Manage Selected Rows)")
        msg_box.setText(f"คุณต้องการจัดการกับแถวที่เลือกไว้ ({count} แถว) อย่างไร?")
        msg_box.setIcon(QMessageBox.Icon.Question)

        btn_del_row = msg_box.addButton(f"🗑️ ลบแถวออกจากไฟล์ ({count} แถว)", QMessageBox.ButtonRole.DestructiveRole)
        btn_clear_trans = msg_box.addButton(f"🧹 ลบคำแปลแถวที่เลือก ({count} แถว)", QMessageBox.ButtonRole.ActionRole)
        btn_clear_ai = msg_box.addButton(f"🤖 ลบเฉพาะผลแปล AI ({count} แถว)", QMessageBox.ButtonRole.ActionRole)
        btn_cancel = msg_box.addButton("ยกเลิก (Cancel)", QMessageBox.ButtonRole.RejectRole)
        msg_box.setDefaultButton(btn_cancel)

        msg_box.exec()
        clicked_btn = msg_box.clickedButton()
        if clicked_btn == btn_del_row:
            self.delete_selected_rows(confirm=True)
        elif clicked_btn == btn_clear_trans:
            self.clear_selected_translations(only_ai=False)
        elif clicked_btn == btn_clear_ai:
            self.clear_selected_translations(only_ai=True)

    def show_table_context_menu(self, pos):
        source_rows = self._get_selected_source_rows()
        if not source_rows:
            idx_at_pos = self.table.indexAt(pos)
            if idx_at_pos.isValid():
                self.table.selectRow(idx_at_pos.row())
                source_rows = self._get_selected_source_rows()

        if not source_rows:
            return

        count = len(source_rows)
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { font-size: 13px; padding: 4px; }")

        act_clear = menu.addAction(f"🧹 ลบคำแปลแถวที่เลือก ({count} แถว)\tBackspace")
        act_clear.triggered.connect(lambda: self.clear_selected_translations(only_ai=False))

        act_clear_ai = menu.addAction(f"🤖 ลบเฉพาะผลแปล AI แถวที่เลือก ({count} แถว)")
        act_clear_ai.triggered.connect(lambda: self.clear_selected_translations(only_ai=True))

        act_clear_all = menu.addAction("💥 ลบคำแปลทั้งหมดในไฟล์ (Clear All)...")
        act_clear_all.triggered.connect(lambda: self.clear_all_translations(only_ai=False))

        menu.addSeparator()

        act_del = menu.addAction(f"🗑️ ลบแถวออกจากไฟล์ ({count} บรรทัด)\tShift+Del")
        act_del.triggered.connect(lambda: self.delete_selected_rows(confirm=True))

        menu.addSeparator()

        if count > 1:
            act_cat = menu.addAction(f"⚡ แปลทีละบรรทัดในตาราง ({count} แถว)\tCtrl+T")
            act_cat.triggered.connect(lambda: self.retranslate_batch(force_cat=True))

            act_trun = menu.addAction(f"🚀 แปล Batch ด้วย TRun ({count} แถว)\tCtrl+Shift+B")
            act_trun.triggered.connect(lambda: self.send_selection_to_trun(auto_start=False))
        else:
            act_ai = menu.addAction("⚡ แปลบรรทัดนี้ด้วย AI\tCtrl+Enter")
            act_ai.triggered.connect(self.retranslate_smart)

        act_opt = menu.addAction("💡 ขอคำแปล 3 สไตล์ (3 Styles)\tCtrl+Shift+O")
        act_opt.triggered.connect(lambda: self.retranslate_options(show_dialog=True))

        act_cjk = menu.addAction("🇨🇳 ล้างคอมเมนต์ภาษาจีน (Clean Chinese)")
        act_cjk.triggered.connect(self.clean_selected_cjk)

        act_patch_eng = menu.addAction(f"🩹 แปลซ่อมคำอังกฤษเฉพาะจุด ({count} แถว)\tCtrl+Shift+E")
        act_patch_eng.triggered.connect(self.patch_selected_english_leaks)

        act_retrofit = menu.addAction("🎖️ ซ่อมคำศัพท์อาวุธ & คีย์บอร์ดในไฟล์เดิม (0 Token)\tCtrl+Shift+M")
        act_retrofit.triggered.connect(self.open_military_retrofit_dialog)

        act_polish = menu.addAction(f"🎬 ขัดเกลาภาษาพูดภาพยนตร์ ({count} แถว)\tCtrl+Shift+P")
        act_polish.triggered.connect(self.polish_selected_cinematic)

        menu.addSeparator()

        act_copy_src = menu.addAction("📋 คัดลอกข้อความต้นฉบับ (Copy Source)")
        act_copy_src.triggered.connect(self.copy_selected_sources)

        act_copy_trans = menu.addAction("📋 คัดลอกคำแปล (Copy Translation)")
        act_copy_trans.triggered.connect(self.copy_selected_translations)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def open_military_retrofit_dialog(self):
        """Opens the zero-token military and firearm terminology retrofit dialog."""
        dlg = MilitaryTerminologyRetrofitDialog(self)
        dlg.exec()

    def copy_selected_sources(self):
        source_rows = self._get_selected_source_rows()
        if not source_rows:
            return
        sources = [self.model._data[r].get("source", "") for r in source_rows if 0 <= r < len(self.model._data)]
        text = "\n".join(sources)
        QApplication.clipboard().setText(text)
        self.statusBar().showMessage(f"📋 คัดลอกข้อความต้นฉบับ {len(sources)} บรรทัดแล้ว", 3000)

    def copy_selected_translations(self):
        source_rows = self._get_selected_source_rows()
        if not source_rows:
            return
        translations = [self.model._data[r].get("trans", "") for r in source_rows if 0 <= r < len(self.model._data)]
        text = "\n".join(translations)
        QApplication.clipboard().setText(text)
        self.statusBar().showMessage(f"📋 คัดลอกคำแปล {len(translations)} บรรทัดแล้ว", 3000)

if __name__ == '__main__':
    import argparse
    import traceback
    import sys
    from PyQt6.QtWidgets import QMessageBox

    def global_exception_handler(exc_type, exc_value, exc_traceback):
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        with open("crash.log", "w", encoding="utf-8") as f:
            f.write(error_msg)
        try:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Critical Error")
            msg.setText(_("msg_fatal_crash"))
            msg.setInformativeText(str(exc_value))
            msg.setDetailedText(error_msg)
            msg.exec()
        except:
            pass
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = global_exception_handler

    parser = argparse.ArgumentParser()
    parser.add_argument("project", nargs="?", type=str, help="Path to the THub project workspace", default=None)
    parser.add_argument("--mode", "-m", type=str, default="studio", choices=["studio", "trun"], help="Workspace mode: studio or trun")
    args, unknown = parser.parse_known_args()
    
    TStudioCore.set_project_path(args.project)
    
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.tstudio.app.1.0')
        except Exception:
            pass

    app = QApplication(sys.argv)
    app_icon = get_tstudio_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    from PyQt6.QtGui import QFont
    f = app.font()
    f.setFamily("Segoe UI")
    app.setFont(f)
    app.setStyle('Fusion')
    win = TranslationStudio(project_path=args.project, default_mode=args.mode)
    win.show()
    sys.exit(app.exec())

