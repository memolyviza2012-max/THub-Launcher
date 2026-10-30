# -*- coding: utf-8 -*-
"""
tstudio_tlm_studio.py
======================
TLM Studio 2.0 (Translation Lore Master)
Advanced Game Lore Reference Ingestion, Directive Matrix & Interactive Staging Grid
"""

import os
import sys
import re
import csv
import json
import copy
import urllib.request
import urllib.error

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QCheckBox, QSpinBox, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QGroupBox,
    QSplitter, QMessageBox, QFileDialog, QMenu, QApplication, QStyledItemDelegate,
    QStyle, QFormLayout, QFrame, QSizePolicy, QScrollArea, QToolButton
)
from PyQt6.QtCore import Qt, QThreadPool, pyqtSignal, pyqtSlot, QSize, QRect, QObject, QRunnable
from PyQt6.QtGui import QColor, QFont, QPainter, QBrush, QPen

from tstudio_core import TStudioCore, CoreAI, BASE_DIR, DEFAULT_SINGLE_PROMPT, DEFAULT_OPTIONS_PROMPT
from tstudio_ui_shared import ApiWorker, ThreadSafeWorkerSignalsForwarder

class MiningWorkerSignals(QObject):
    progress = pyqtSignal(int, int, str)
    batch_done = pyqtSignal(list)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

class MiningWorker(QRunnable):
    _active_signals = set()

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = MiningWorkerSignals()
        MiningWorker._active_signals.add(self.signals)
        self.signals.finished.connect(self._cleanup)
        self.signals.error.connect(self._cleanup)

    def _cleanup(self, *args):
        try:
            MiningWorker._active_signals.remove(self.signals)
        except KeyError:
            pass

    @pyqtSlot()
    def run(self):
        try:
            self.fn(self.signals, *self.args, **self.kwargs)
        except Exception as e:
            self.signals.error.emit(str(e))


try:
    from tstudio_i18n import _
except ImportError:
    try:
        from trun_i18n import _
    except ImportError:
        def _(key): return key


TAG_COLORS = {
    "Person": ("#f38ba8", "#11111b"),      # Soft Red / Dark
    "Location": ("#a6e3a1", "#11111b"),    # Green / Dark
    "Faction": ("#cba6f7", "#11111b"),     # Mauve / Dark
    "Weapon": ("#fab387", "#11111b"),      # Peach / Dark
    "Item": ("#f9e2af", "#11111b"),        # Yellow / Dark
    "General": ("#89b4fa", "#11111b"),     # Blue / Dark
    "Quest": ("#94e2d5", "#11111b"),       # Teal / Dark
    "Other": ("#6c7086", "#cdd6f4"),       # Muted Grey / Light
}

VALID_TAGS = ["General", "Person", "Location", "Faction", "Weapon", "Item", "Quest", "Other"]

UNIVERSE_TONES_BY_CATEGORY = {
    "🚀 ไซไฟ เทคโนโลยี และอวกาศ (Sci-Fi & Space)": [
        "Star Wars & Space Opera / ลิเกอวกาศ มหากาพย์สงครามดวงดาว เจไดและซิธ (Star Wars, Mass Effect, KotOR, Jedi Survivor)",
        "Cyberpunk & High-Tech Dystopia / ไซเบอร์พังก์ โลกอนาคตมืดมน ดิจิทัลใต้ดิน (Cyberpunk 2077, Deus Ex, Ghostrunner, Stray)",
        "Grimdark Sci-Fi / สงครามโกธิกอวกาศมืดมน ลัทธิจักรวรรดิ (Warhammer 40,000: Space Marine/Rogue Trader/Boltgun)",
        "Hard Sci-Fi & Space Engineering / ไซไฟสมจริง กู้ซากและวิศวกรรมอวกาศ (Hardspace: Shipbreaker, Elite Dangerous, Star Citizen)",
        "Space Exploration & Colonization / สำรวจดวงดาว บุกเบิกอาณานิคมอวกาศ (Starfield, No Man's Sky, The Outer Worlds, Deliver Us Mars)",
        "Cosmic & Deep Space Horror / สยองขวัญอวกาศลึกลับ สิ่งมีชีวิตต่างดาว (Dead Space, Prey, Returnal, Alien: Isolation, System Shock)",
        "Mecha & Heavy Armor Warfare / หุ่นรบไซไฟ สงครามหุ้มเกราะไฮเทค (Armored Core, Titanfall, MechWarrior, Battletech)",
        "Steampunk & Victorian Industrial / จักรกลไอน้ำวิกตอเรียน เรโทรอนาคต (Dishonored, Bioshock Infinite, Lies of P, Frostpunk)",
        "Dieselpunk & Alternate History / ดีเซลพังก์ สงครามโลกสมมติ (Wolfenstein, Iron Harvest, The Order: 1886)",
        "Biopunk & Deep Sea Subterranean / ชีวกลายพันธุ์ ใต้สมุทรลึก (Bioshock 1/2, SOMA, Subnautica, Barotrauma)",
        "Retro Sci-Fi & 80s Synthwave / ไซไฟย้อนยุค ซินธ์เวฟนีออน (Far Cry 3: Blood Dragon, Katana Zero, Hotline Miami)"
    ],
    "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)": [
        "High & Epic Fantasy / แฟนตาซีมหากาพย์ เวทมนตร์และการผจญภัย (Baldur's Gate 3, The Witcher 3, Skyrim, Dragon Age)",
        "Dark Fantasy & Soulslike / ดาร์กแฟนตาซี สิ้นหวัง ลึกลับ ทรงพลัง (Elden Ring, Dark Souls, Bloodborne, Diablo)",
        "Eastern Wuxia & Xianxia / จีนกำลังภายใน เทพเซียน ยุทธภพ (Black Myth: Wukong, Wo Long, Gujian, Dynasty Warriors)",
        "Feudal Japan & Samurai / ซามูไร-นินจายุคศักดินา เกียรติยศนักรบ (Ghost of Tsushima, Sekiro, Nioh, Like a Dragon: Ishin, AC Shadows)",
        "Medieval Historical / ประวัติศาสตร์ยุคกลาง ยุโรปสมจริง ไร้เวทมนตร์ (Kingdom Come: Deliverance, Mount & Blade, Crusader Kings)",
        "Crusades & Holy Land / สงครามครูเสด ภาคีมือสังหารศักดิ์สิทธิ์ (Assassin's Creed 1)",
        "Italian Renaissance & Brotherhood / เรเนซองส์อิตาลี ภราดรภาพมือสังหารและล้างแค้น (Assassin's Creed 2, Brotherhood, Revelations)",
        "Colonial American Revolution / ปฏิวัติอเมริกาและสงครามเจ็ดปี มือสังหารกับเทมพลาร์ (Assassin's Creed III, AC Rogue)",
        "French Revolution / การปฏิวัติฝรั่งเศส ปารีสเลือดและชนชั้นขุนนาง (Assassin's Creed Unity)",
        "Victorian Industrial London / ลอนดอนวิกตอเรียน ปฏิวัติอุตสาหกรรมและแก๊งอันธพาล (Assassin's Creed Syndicate)",
        "Ancient Egyptian Antiquity / อียิปต์โบราณ เมดไจและกำเนิดภาคีเร้นกาย (Assassin's Creed Origins)",
        "Islamic Golden Age Baghdad / แบกแดดยุคทอง ภาคีผู้เร้นกายพันหนึ่งราตรี (Assassin's Creed Mirage)",
        "Greco-Roman Antiquity / อารยธรรมกรีก-โรมันโบราณ ทวยเทพและวีรชน (Assassin's Creed Odyssey, God of War ภาคกรีก, Titan Quest)",
        "Norse & Viking Saga / ตำนานนอร์ส ชนเผ่าไวกิ้ง รังนาร็อก (God of War Ragnarok, Valheim, Assassin's Creed Valhalla)",
        "Age of Sail & Piracy / ยุคเดินเรือ โจรสลัด ทะเลแคริบเบียน (Sea of Thieves, Assassin's Creed IV: Black Flag, Skull and Bones)",
        "Gothic Vampire & Occult / กอทิก ผีดูดเลือด ปราสาทมืดมนและไสยศาสตร์ (Castlevania, Vampire: The Masquerade, V Rising)",
        "Mythology & Folk Legends / เทพปกรณัม นิทานพื้นบ้าน มนตร์เสน่ห์ (Hades, Okami, Cult of the Lamb, Bramble)"
    ],
    "🧟 เอาชีวิตรอด สยองขวัญ และโลกล่มสลาย (Survival & Horror)": [
        "Post-Apocalyptic Wasteland / แดนรกร้างโลกล่มสลาย กัมมันตรังสี (Fallout, Metro, S.T.A.L.K.E.R., Wasteland, Mad Max)",
        "Zombie & Viral Outbreak / ไวรัสระบาด เอาชีวิตรอดจากซอมบี้ (Resident Evil, The Last of Us, Dying Light, Days Gone, Project Zomboid)",
        "Lovecraftian & Eldritch Horror / สยองขวัญคอสมิกเลิฟคราฟต์ ความวิปลาสโบราณ (Call of Cthulhu, Dredge, Darkest Dungeon, Alan Wake)",
        "Psychological & Paranormal / หลอนประสาท ลี้ลับเหนือธรรมชาติ (Silent Hill, Outlast, Fatal Frame, Control)",
        "Wilderness Survival & Crafting / เอาชีวิตรอดในพงไพรธรรมชาติ สร้างฐาน (The Forest, Green Hell, Rust, The Long Dark, Ark)"
    ],
    "🔫 แอ็กชัน ยุคปัจจุบัน และการทหาร (Action & Military)": [
        "Military Tactical & Spec-Ops / ยุทธวิธีทหาร หน่วยรบพิเศษ สมจริง (Call of Duty, Battlefield, Rainbow Six, Ghost Recon, ARMA)",
        "Urban Crime & Underworld / อาชญากรรมใต้ดิน แก๊งมาเฟีย เมืองใหญ่ (GTA, Mafia, Saints Row, Payday, Yakuza/Like a Dragon)",
        "Espionage & Secret Agent / สายลับจารกรรม ลอบเร้น ชิงไหวชิงพริบ (Metal Gear Solid, Splinter Cell, Hitman, Deathloop)",
        "Western & Frontier Outlaw / คาวบอยคาวเลือด แดนเถื่อนตะวันตก ดวลปืน (Red Dead Redemption, Desperados, Weird West)",
        "Superhero & Comic Universe / ซูเปอร์ฮีโร่และคอมิกส์ พิทักษ์เมือง (Marvel's Spider-Man, Batman Arkham, Injustice)"
    ],
    "🌸 อนิเมะ JRPG และแฟนตาซีเอเชีย (Anime & Asian Fantasy)": [
        "Anime JRPG & High-School Fantasy / อนิเมะโรงเรียน ผจญภัยวัยรุ่น (Persona, Genshin Impact, Honkai: Star Rail, Final Fantasy)",
        "Shonen Battle & High Action / อนิเมะต่อสู้ปล่อยพลัง มิตรภาพลูกผู้ชาย (Monster Hunter, Dragon Ball, Tales of Arise, Granblue Fantasy)",
        "Cozy, Slice of Life & Farming / จำลองชีวิต อบอุ่นหัวใจและทำฟาร์ม (Stardew Valley, Animal Crossing, Rune Factory)"
    ],
    "🎭 เสียดสี ตลกร้าย ปรัชญา และทั่วไป (Comedy, Satire & General)": [
        "Satirical & Dark Comedy / เสียดสีการเมือง ตลกร้ายฮาจัด กวนประสาท (Helldivers 2, The Outer Worlds, Borderlands, Portal, South Park)",
        "Absurdist Bureaucracy & Dystopian / รัฐข้าราชการอำนาจนิยม ตลกร้าย (Papers Please, Beholder, The Stanley Parable)",
        "Philosophical Detective & Surreal Noir / สืบสวนปรัชญา เหนือจริง ลุ่มลึก (Disco Elysium, Death Stranding, Kentucky Route Zero)",
        "General / ทั่วไป มาตรฐานสากล (Universal Default)"
    ]
}

# Flattened list for backward compatibility
UNIVERSE_TONES = []
for _cat_tones in UNIVERSE_TONES_BY_CATEGORY.values():
    UNIVERSE_TONES.extend(_cat_tones)

PRONOUN_PRESETS = {
    "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)": {
        "1st": "ข้า, เรา",
        "2nd": "เจ้า, สหาย, ท่าน, นายท่าน",
        "3rd": "เขา, นาง, พวกมัน",
        "neutral": "ข้า (แทนตนเอง), เจ้า หรือ ท่าน (แทนผู้ฟัง)",
        "summary": "1st: ข้า, เรา | 2nd: เจ้า, สหาย, ท่าน, นายท่าน | ห้ามครับ/ค่ะ เด็ดขาดในยุคอดีต",
        "rules": (
            "- ยุคอดีตใน Animus: บังคับใช้ 'ข้า - เจ้า / ข้า - ท่าน / สหาย' (ห้ามหลุด ผม/คุณ/ครับ/ค่ะ เด็ดขาด)\n"
            "- มิติโลกปัจจุบัน (นอก Animus): ให้ใช้ 'ผม/ฉัน - คุณ/นาย' ตามปกติ (บริบทแฮกเกอร์/วิทยุสื่อสาร)\n"
            "- สหายร่วมภาคี (Brotherhood): เรียกกันว่า 'สหาย' หรือ 'พี่น้องร่วมภาคี'\n"
            "- ผู้อาวุโส/อาจารย์/ผู้ว่าจ้าง: ใช้ 'ท่าน' หรือ 'นายท่าน'\n"
            "- คำลงท้าย: ตัด ครับ/ค่ะ ออกทั้งหมด ให้ใช้น้ำเสียงสุขุม เด็ดขาด หนักแน่นแบบวรรณกรรมอิงประวัติศาสตร์"
        )
    },
    "🌌 มหากาพย์อวกาศ / Star Wars / แฟนตาซี (ข้า - เจ้า / ข้า - ท่าน)": {
        "1st": "ข้า, ข้าพเจ้า, เรา",
        "2nd": "เจ้า, ท่าน, พวกเจ้า",
        "3rd": "เขา, นาง, มัน, พวกเขา",
        "neutral": "ข้า (แทนตนเอง), เจ้า หรือ ท่าน (แทนผู้ฟัง)",
        "summary": "1st: ข้า | 2nd: เจ้า, ท่าน | กลาง: ข้า, เจ้า, ท่าน (ห้ามครับ/ค่ะ เด็ดขาด)",
        "rules": (
            "- 1st Person ('I'): ใช้ 'ข้า' หรือ 'ข้าพเจ้า' (หรือละสรรพนามอย่างเป็นธรรมชาติ) ห้ามใช้ 'ผม' หรือ 'ฉัน/ดิฉัน'\n"
            "- 2nd Person ('You'): ใช้ 'เจ้า' (ระดับเดียวกันหรือต่ำกว่า) หรือ 'ท่าน' (ผู้อาวุโส/เจได/ผู้สูงศักดิ์)\n"
            "- ห้ามสุ่มเดาคำลงท้าย ครับ/ค่ะ เด็ดขาด ให้ใช้ 'ขอรับ' หรือละคำลงท้าย"
        )
    },
    "🏰 แฟนตาซียุคกลาง / อัศวิน / เวทมนตร์ (ข้า - เจ้า / ข้า - ท่าน / ท่านลอร์ด)": {
        "1st": "ข้า, ข้าพเจ้า",
        "2nd": "เจ้า, ท่าน, นายท่าน, ท่านลอร์ด",
        "3rd": "เขา, นาง, พวกมัน",
        "neutral": "ข้า, เจ้า, ท่าน",
        "summary": "1st: ข้า | 2nd: เจ้า, ท่าน, นายท่าน | กลาง: ข้า, เจ้า, ท่าน",
        "rules": (
            "- 1st Person: ใช้ 'ข้า' เป็นหลัก\n"
            "- 2nd Person: ใช้ 'เจ้า' (สามัญชน) หรือ 'ท่าน / นายท่าน' (ขุนนาง/อัศวิน)\n"
            "- ห้ามใช้ ผม/คุณ/ครับ/ค่ะ ในยุคกลาง"
        )
    },
    "⚔️ จีนกำลังภายใน / ยุทธภพ (ข้า - เจ้า / จอมยุทธ / แม่นาง / ศิษย์พี่)": {
        "1st": "ข้า, ข้าพเจ้า, ข้าน้อย",
        "2nd": "เจ้า, ท่าน, จอมยุทธ, แม่นาง, ศิษย์พี่/น้อง",
        "3rd": "เขา, นาง, พวกเขา",
        "neutral": "ข้า, ท่าน, จอมยุทธ",
        "summary": "1st: ข้า, ข้าน้อย | 2nd: เจ้า, ท่าน, จอมยุทธ | กลาง: ข้า, ท่าน",
        "rules": (
            "- สรรพนามยุทธภพ: ข้า/เจ้า/ท่าน/ข้าน้อย\n"
            "- หากไม่แน่ใจเพศ ห้ามเดา แม่นาง หรือ แม่ทัพ ให้ใช้ 'ท่าน' หรือ 'จอมยุทธ'"
        )
    },
    "🏯 ญี่ปุ่นยุคซามูไร / นินจา (ข้า - เจ้า / นายท่าน / ท่านหญิง)": {
        "1st": "ข้า, ตัวข้า",
        "2nd": "เจ้า, ท่าน, นายท่าน, ท่านผู้นำ",
        "3rd": "เขา, นาง, ผู้นั้น",
        "neutral": "ข้า, เจ้า, ท่าน",
        "summary": "1st: ข้า | 2nd: เจ้า, ท่าน, นายท่าน | กลาง: ข้า, เจ้า, ท่าน",
        "rules": (
            "- ยึดถือเกียรติยศซามูไร ใช้ ข้า/เจ้า/ท่าน เป็นหลัก\n"
            "- คำลงท้าย: ขอรับ, ท่าน"
        )
    },
    "🪖 การทหาร / หน่วยรบพิเศษ (ผม - คุณ / ผู้การ / หมวด)": {
        "1st": "ผม (ชาย), ฉัน/ดิฉัน (หญิง), ข้าพเจ้า",
        "2nd": "คุณ, นาย, พวกนาย, ผู้การ, หมวด, จ่า, สารวัตร",
        "3rd": "เขา, เจ้าหมอนั่น, เป้าหมาย",
        "neutral": "คุณ, ท่าน, หรือละประธาน",
        "summary": "1st: ผม (ชาย) / ฉัน (หญิง) | 2nd: คุณ, นาย, ผู้การ | ไม่สุ่มเดาเพศ",
        "rules": (
            "- โทนทหารรบจริงจัง หนักแน่น กระชับ ปราศจากความเยิ่นเย้อ\n"
            "- ผู้พูดชาย: ใช้ 'ผม' เป็นหลัก\n"
            "- ผู้พูดหญิง (Female Soldier/Officer/Agent): ห้ามใช้ 'ผม' หรือลงท้าย 'ครับ' เด็ดขาด! ให้ใช้ 'ฉัน' (กับเพื่อนทหาร/ระดับเดียวกัน) หรือ 'ดิฉัน' (รายงานผู้บังคับบัญชา) หรือเรียกยศ/ละประธาน\n"
            "- คำเรียกผู้ฟัง: ใช้ คุณ / นาย / พวกนาย หรือเรียกตามยศทหาร (ผู้การ, หมวด, จ่า)\n"
            "- การละประธาน (Subject Dropping): ในคำสั่ง/รายงานยุทธวิธี สามารถละประธานได้อย่างเป็นธรรมชาติ เช่น 'รับทราบ', 'เห็นเป้าหมายแล้ว', 'กำลังเข้าเคลียร์พื้นที่'\n"
            "- คำลงท้าย: ห้ามสุ่มเดา ครับ/ค่ะ หากไม่มั่นใจเพศ ให้ลงท้ายด้วยน้ำเสียงทหารเด็ดขาด (เช่น 'รับทราบ', 'เข้าใจแล้ว')"
        )
    },
    "🪖 ทหารยุทธวิธี / สายลุย / ตำรวจ (ผม/ฉัน - นาย/พวกนาย/ผู้หมวด)": {
        "1st": "ผม (ชาย), ฉัน/ดิฉัน (หญิง), ข้าพเจ้า",
        "2nd": "นาย, พวกนาย, คุณ, ผู้การ, หมวด, จ่า",
        "3rd": "เขา, เจ้าหมอนั่น, เป้าหมาย, พวกมัน",
        "neutral": "นาย, คุณ, หรือละประธาน",
        "summary": "1st: ผม (ชาย) / ฉัน (หญิง) | 2nd: นาย, พวกนาย, หมวด | ไม่สุ่มเดาเพศ",
        "rules": (
            "- สไตล์สายลุย/ทหารภาคสนาม/ตำรวจ: ลุย ดุดัน ตรงไปตรงมา กระชับฉับไว\n"
            "- ผู้พูดชาย: แทนตนเองว่า 'ผม' เรียกสหายร่วมรบว่า 'นาย / พวกนาย'\n"
            "- ผู้พูดหญิง (Female Operator): แทนตนเองว่า 'ฉัน' เรียกเพื่อนร่วมรบว่า 'นาย / พวกนาย' (ห้ามตัวละครหญิงใช้ 'ผม' หรือ 'ครับ' เด็ดขาด)\n"
            "- ยุทธวิธีรบ: ละประธานเมื่อรายงาน/ออกคำสั่ง ('รับทราบ', 'เห็นตัวแล้ว', 'ยิงคุ้มกันด้วย!')\n"
            "- ปราศจากคำลงท้ายหวานแหลม (หลีกเลี่ยง ครับ/ค่ะ ในภาวะสงคราม)"
        )
    },
    "🏙️ โลกปัจจุบัน / สากลทั่วไป (ผม/ฉัน - คุณ / เขา - เธอ)": {
        "1st": "ผม (ชาย) / ฉัน (หญิงหรือเป็นกันเอง)",
        "2nd": "คุณ",
        "3rd": "เขา / เธอ",
        "neutral": "ฉัน, คุณ",
        "summary": "1st: ผม/ฉัน | 2nd: คุณ | กลาง: คุณ (หากไม่แน่ใจเพศ ห้ามเดา ครับ/ค่ะ)",
        "rules": (
            "- มาตรฐานสากล: ผม (ชาย) / ฉัน (หญิง) - คุณ\n"
            "- หากไม่แน่ใจเพศตัวละคร ให้ใช้ 'คุณ' หรือละประธาน และหลีกเลี่ยงการเดา ครับ/ค่ะ"
        )
    },
    "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)": {
        "1st": "ผม (ชาย) / ฉัน (หญิงหรือเป็นกันเอง)",
        "2nd": "คุณ",
        "3rd": "เขา / เธอ",
        "neutral": "คุณ, หรือละประธาน",
        "summary": "1st: ผม/ฉัน | 2nd: คุณ | กลาง: คุณ (หากไม่แน่ใจเพศ ห้ามเดา ครับ/ค่ะ)",
        "rules": (
            "- มาตรฐานสากล: ชายใช้ 'ผม' หญิงใช้ 'ฉัน' - คุณ\n"
            "- หากไม่แน่ใจเพศตัวละคร ให้ใช้ 'คุณ' หรือละประธาน และหลีกเลี่ยงการเดา ครับ/ค่ะ"
        )
    },
    "🔥 เพื่อนสนิท / วัยรุ่น / แก๊งสเตอร์ดิบเถื่อน (ฉัน - แก / นาย - เอ็ง)": {
        "1st": "ฉัน, ข้า, กู",
        "2nd": "แก, นาย, เอ็ง, มึง",
        "3rd": "มัน, พวกมัน",
        "neutral": "ฉัน, แก, นาย",
        "summary": "1st: ฉัน, ข้า | 2nd: แก, นาย, เอ็ง | กลาง: ฉัน, แก",
        "rules": (
            "- ภาษาพูดปากเปล่า สนิทสนมหรือดิบเถื่อนตามบริบท\n"
            "- ไม่ใช้คำสุภาพทางการ"
        )
    },
    "🔥 สตรีท / นอกกฎหมาย / ปากจัด (กู - มึง / ฉัน - แก / ไอ้เวร)": {
        "1st": "ฉัน, ข้า, กู",
        "2nd": "แก, นาย, เอ็ง, มึง",
        "3rd": "มัน, พวกมัน, ไอ้เวรนั่น",
        "neutral": "ฉัน, แก, นาย",
        "summary": "1st: กู/ฉัน | 2nd: มึง/แก/นาย | สตรีท ปากจัด ดิบเถื่อน",
        "rules": (
            "- สไตล์ดิบเถื่อน สตรีท นอกกฎหมาย ใช้ กู-มึง หรือ ฉัน-แก ตามระดับความสนิทและความเดือด\n"
            "- ผู้หญิงสายห้าว: ใช้ ฉัน-แก หรือ กู-มึง ได้ตามสถานการณ์"
        )
    },
    "👔 สุภาพทางการ / ราชการ / พิธีการ (กระผม/ดิฉัน - ท่าน / ใต้เท้า)": {
        "1st": "กระผม, ดิฉัน, ข้าพเจ้า",
        "2nd": "ท่าน, ใต้เท้า, คุณ",
        "3rd": "ท่าน, เขา",
        "neutral": "ข้าพเจ้า, ท่าน",
        "summary": "1st: กระผม/ดิฉัน | 2nd: ท่าน, ใต้เท้า | กลาง: ข้าพเจ้า, ท่าน",
        "rules": (
            "- เน้นความสุภาพสูงสุด ใช้ กระผม/ดิฉัน และ ท่าน"
        )
    },
    "⚙️ กำหนดเอง (Custom Pronouns)": {
        "1st": "กำหนดเอง",
        "2nd": "กำหนดเอง",
        "3rd": "กำหนดเอง",
        "neutral": "กำหนดเอง",
        "summary": "ผู้ใช้กำหนดสรรพนามและกฎระบุเพศเองในช่องกฎเฉพาะ",
        "rules": "- ปฏิบัติตามกฎสรรพนามเฉพาะที่ระบุไว้ในช่องกฎเฉพาะด้านล่าง"
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# ASSASSIN'S CREED INSTALLMENTS & DEMEANOR (ริยาบท) SPECIALIZED DATABASE
# ─────────────────────────────────────────────────────────────────────────────

ASSASSINS_CREED_INSTALLMENTS = {
    "ac1": {
        "title": "Assassin's Creed (2007)",
        "era": "สงครามครูเสดครั้งที่ 3 (ดินแดนศักดิ์สิทธิ์ ดามัสกัส/เยรูซาเล็ม ค.ศ. 1191)",
        "tone": "Crusades & Holy Land / สงครามครูเสด ภาคีมือสังหารศักดิ์สิทธิ์ (Assassin's Creed 1)",
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "protagonist": "อัลตาอีร์ (Altaïr Ibn-La'Ahad)",
        "demeanor": (
            "สุขุม เยือกเย็น เคร่งครัดในวินัยและคติพจน์ภาคี (Creed) "
            "พูดจาคมคาย หนักแน่น นอบน้อมต่อผู้นำ (อัลมูอัลลิม) แต่มั่นคงในเสรีภาพ ห้ามใช้คำสมัยใหม่หรือ ครับ/ค่ะ เด็ดขาด"
        ),
        "keywords": [
            "altair", "altaïr", "masyaf", "al mualim", "crusade", "crusader", "saracen",
            "robert de sable", "holy land", "ac1", "ac 1", "assassin's creed 1", "assassins creed 1"
        ]
    },
    "ac2_ezio": {
        "title": "Assassin's Creed II / Brotherhood / Revelations (Ezio Trilogy)",
        "era": "เรเนซองส์ อิตาลี (ฟลอเรนซ์, เวนิส, โรม) & คอนสแตนติโนเปิล (ค.ศ. 1476–1511)",
        "tone": "Italian Renaissance & Brotherhood / เรเนซองส์อิตาลี ภราดรภาพมือสังหารและล้างแค้น (Assassin's Creed 2, Brotherhood, Revelations)",
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "protagonist": "เอ็ตซีโอ ออดิตอเร (Ezio Auditore da Firenze)",
        "demeanor": (
            "สง่างาม มีเสน่ห์แบบสุภาพบุรุษอิตาเลียน สุภาพต่อสตรีและผู้สูงศักดิ์ ('ท่าน/นายท่าน') "
            "ให้เกียรติมิตรสหาย ('สหาย/ภราดา') เด็ดขาดต่อศัตรูตระกูลบอร์เจีย "
            "คำส่งวิญญาณวาระสุดท้าย: 'Requiescat in pace (จงสู่สุคติ)' ด้วยน้ำเสียงสงบและเคารพ"
        ),
        "keywords": [
            "ezio", "auditore", "ac2", "ac 2", "brotherhood", "revelations", "florence",
            "venice", "monteriggioni", "borgia", "cesare", "rodrigo", "da vinci", "leonardo",
            "machiavelli", "forli", "tuscany", "assassin's creed 2", "assassins creed 2", "assassin's creed ii"
        ]
    },
    "ac3_rogue": {
        "title": "Assassin's Creed III / AC Rogue",
        "era": "สงครามปฏิวัติอเมริกา & สงครามเจ็ดปี (ค.ศ. 1752–1783)",
        "tone": "Colonial American Revolution / ปฏิวัติอเมริกาและสงครามเจ็ดปี มือสังหารกับเทมพลาร์ (Assassin's Creed III, AC Rogue)",
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "protagonist": "คอนเนอร์ (Connor / Ratonhnhaké:ton) / เชย์ คอร์แมก (Shay Cormac)",
        "demeanor": (
            "คอนเนอร์: ซื่อสัตย์ หนักแน่น ตรงไปตรงมา มุ่งมั่นเพื่อชนเผ่าและอิสรภาพ / "
            "เชย์ คอร์แมก: สุขุม เด็ดเดี่ยว ยอมแบกรับตราบาปเพื่อความสงบสุข ('I make my own luck') "
            "ภาษาทหารยุคอาณานิคมผสานชนเผ่า หนักแน่น ไร้คำลงท้ายอ่อนหวาน"
        ),
        "keywords": [
            "connor", "ratonhnhake", "shay cormac", "haytham", "ac3", "ac 3", "ac rogue",
            "rogue", "colonial", "boston tea", "frontier", "george washington", "seven years war",
            "assassin's creed 3", "assassins creed 3", "assassin's creed iii", "assassin's creed rogue"
        ]
    },
    "ac4_black_flag": {
        "title": "Assassin's Creed IV: Black Flag",
        "era": "ยุคทองแห่งโจรสลัด ทะเลแคริบเบียน (ค.ศ. 1715–1722)",
        "tone": "Age of Sail & Piracy / ยุคเดินเรือ โจรสลัด ทะเลแคริบเบียน (Sea of Thieves, Assassin's Creed IV: Black Flag, Skull and Bones)",
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "pronoun": "🔥 สตรีท / นอกกฎหมาย / ปากจัด (กู - มึง / ฉัน - แก / ไอ้เวร)",
        "protagonist": "เอ็ดเวิร์ด เคนเวย์ (Edward Kenway)",
        "demeanor": (
            "กวนประสาท รักอิสระ ดิบเถื่อน เถลไถล สำนวนคนเรือโจรสลัด (เหล้า รัม เรือรบ ทองคำ) "
            "กับลูกเรือใช้ ฉัน-แก หรือ ข้า-เอ็ง อย่างเป็นกันเอง เมื่อเข้าสู่ความขัดแย้งของภาคีจึงสุขุมและตื่นรู้ในอุดมการณ์"
        ),
        "keywords": [
            "black flag", "edward kenway", "jackdaw", "blackbeard", "nassau", "havana",
            "kingston", "buccaneer", "privateer", "ac4", "ac 4", "assassin's creed 4",
            "assassins creed 4", "assassin's creed iv"
        ]
    },
    "ac_unity": {
        "title": "Assassin's Creed Unity",
        "era": "การปฏิวัติฝรั่งเศส ปารีส (ค.ศ. 1789–1794)",
        "tone": "French Revolution / การปฏิวัติฝรั่งเศส ปารีสเลือดและชนชั้นขุนนาง (Assassin's Creed Unity)",
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "protagonist": "อาร์โน ดอเรียน (Arno Dorian)",
        "demeanor": (
            "ชาญฉลาด คมคาย สุภาพกึ่งประชดประชัน มีกลิ่นอายผู้ดีฝรั่งเศสท่ามกลางความบ้าคลั่งของม็อบปฏิวัติและกิโยติน "
            "สรรพนามในราชสำนักใช้ 'ท่าน/ใต้เท้า' ในภาคีใช้ 'สหาย' น้ำเสียงกับเอลีสจะอ่อนโยนและจริงใจ"
        ),
        "keywords": [
            "unity", "ac unity", "arno dorian", "arno", "elise de la serre", "robespierre",
            "bastille", "guillotine", "versailles", "notre-dame", "assassin's creed unity", "assassins creed unity"
        ]
    },
    "ac_syndicate": {
        "title": "Assassin's Creed Syndicate",
        "era": "ลอนดอน ยุควิกตอเรียน ปฏิวัติอุตสาหกรรม (ค.ศ. 1868)",
        "tone": "Victorian Industrial London / ลอนดอนวิกตอเรียน ปฏิวัติอุตสาหกรรมและแก๊งอันธพาล (Assassin's Creed Syndicate)",
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "protagonist": "จาค็อบ & อีวี่ ฟราย (Jacob & Evie Frye)",
        "demeanor": (
            "จาค็อบ: ยียวน มั่นใจ สายลุยคุมแก๊งอันธพาล (The Rooks) / "
            "อีวี่: สุภาพสตรีมือสังหาร สุขุม รอบคอบ ยึดถือกฎระเบียบภาคี "
            "ใช้ภาษาอังกฤษค็อกนีย์ผสมผู้ดีวิกตอเรียน สรรพนาม ฉัน-คุณ หรือ ฉัน-แก ในหมู่นักเลง"
        ),
        "keywords": [
            "syndicate", "ac syndicate", "jacob frye", "evie frye", "rooks", "starrick",
            "blighters", "whitechapel", "big ben", "thames", "assassin's creed syndicate", "assassins creed syndicate"
        ]
    },
    "ac_origins": {
        "title": "Assassin's Creed Origins",
        "era": "อียิปต์โบราณ ยุคราชวงศ์ปโตเลมี (49–43 ปีก่อน ค.ศ.)",
        "tone": "Ancient Egyptian Antiquity / อียิปต์โบราณ เมดไจและกำเนิดภาคีเร้นกาย (Assassin's Creed Origins)",
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "protagonist": "บาเยกแห่งซีวา (Bayek of Siwa) & อายา (Aya / Amunet)",
        "demeanor": (
            "เมดไจผู้พิทักษ์: ดุดัน ทรงพลัง เกรี้ยวกราดต่อศัตรู แต่อ่อนโยน เปี่ยมเมตตาต่อเด็กและคนยากไร้ "
            "พูดจาหนักแน่น เคารพต่อทวยเทพแห่งไอยคุปต์ (อามุน, อนูบิส) สรรพนาม 'ข้า-เจ้า / ข้า-ท่าน'"
        ),
        "keywords": [
            "origins", "ac origins", "bayek", "siwa", "aya of alexandria", "medjay",
            "amunet", "cleopatra", "ptolemy", "pharaoh", "anubis", "order of the ancients",
            "assassin's creed origins", "assassins creed origins"
        ]
    },
    "ac_odyssey": {
        "title": "Assassin's Creed Odyssey",
        "era": "กรีกโบราณ สงครามเพโลพอนนีเซียน (431 ปีก่อน ค.ศ.)",
        "tone": "Greco-Roman Antiquity / อารยธรรมกรีก-โรมันโบราณ ทวยเทพและวีรชน (Assassin's Creed Odyssey, God of War ภาคกรีก, Titan Quest)",
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "protagonist": "คาสซานดรา / อเล็กซิออส (Kassandra / Alexios - Misthios)",
        "demeanor": (
            "ทหารรับจ้างมิสธิออสแห่งสปาร์ตา: ทะนงองอาจ ตรงไปตรงมา มั่นใจในฝีมือ มีอารมณ์ขันแบบทหารกรีกโบราณ "
            "สบถคำกรีก ('Malaka!') เมื่อถูกกวนใจ ยึดมั่นในเกียรติยศและสัญญาว่าจ้าง สรรพนาม 'ข้า-เจ้า / ข้า-ท่าน'"
        ),
        "keywords": [
            "odyssey", "ac odyssey", "kassandra", "alexios", "misthios", "spartan",
            "athenian", "cult of kosmos", "leonidas", "malaka", "adrestia", "spear of leonidas",
            "assassin's creed odyssey", "assassins creed odyssey"
        ]
    },
    "ac_valhalla": {
        "title": "Assassin's Creed Valhalla",
        "era": "อังกฤษยุคมืด & ตำนานไวกิ้ง (ค.ศ. 873)",
        "tone": "Norse & Viking Saga / ตำนานนอร์ส ชนเผ่าไวกิ้ง รังนาร็อก (God of War Ragnarok, Valheim, Assassin's Creed Valhalla)",
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "protagonist": "เอวอร์ จุมพิตหมาป่า (Eivor Wolf-Kissed)",
        "demeanor": (
            "นักรบไวกิ้งแดนเหนือ: ห้าวหาญแต่สุขุม เปี่ยมคารมกวี (Flyting) รักเกียรติยศ ชนเผ่าเรเวน และพี่น้องร่วมสาบาน "
            "ดุดันในสนามรบแต่สุขุมยามเจรจา สรรพนาม 'ข้า-เจ้า / ท่าน / พี่น้อง' คำทักทายและชนแก้ว 'Skál!'"
        ),
        "keywords": [
            "valhalla", "ac valhalla", "eivor", "raven clan", "sigurd", "ragnarsson",
            "drengr", "skal", "odins eye", "assassin's creed valhalla", "assassins creed valhalla"
        ]
    },
    "ac_mirage": {
        "title": "Assassin's Creed Mirage",
        "era": "แบกแดดยุคทอง ยุคเคาะลีฟะฮ์อับบาซียะฮ์ (ค.ศ. 861)",
        "tone": "Islamic Golden Age Baghdad / แบกแดดยุคทอง ภาคีผู้เร้นกายพันหนึ่งราตรี (Assassin's Creed Mirage)",
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "protagonist": "บาซิม อิบน์ อิสฮาก (Basim Ibn Ishaq) & โรชาน (Roshan)",
        "demeanor": (
            "ภาคีผู้เร้นกาย (Hidden Ones): ลอบเร้น นอบน้อมต่อครูบาอาจารย์ (โรชาน) ดั่งศิษย์กับอาจารย์ "
            "พูดจาสุภาพ คมคาย แฝงปรัชญาและคำสอนแห่งอะลามูต สรรพนาม 'ข้า-เจ้า / สหาย / นายท่าน'"
        ),
        "keywords": [
            "mirage", "ac mirage", "basim", "basim ibn ishaq", "roshan", "alamut",
            "hidden ones", "baghdad", "caliphate", "round city", "assassin's creed mirage", "assassins creed mirage"
        ]
    },
    "ac_shadows": {
        "title": "Assassin's Creed Shadows",
        "era": "ญี่ปุ่น ยุคอาซูจิ-โมโมยามะ / เซ็นโกคุ (ค.ศ. 1579)",
        "tone": "Feudal Japan & Samurai / ซามูไร-นินจายุคศักดินา เกียรติยศนักรบ (Ghost of Tsushima, Sekiro, Nioh, Like a Dragon: Ishin, AC Shadows)",
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "pronoun": "🏯 ญี่ปุ่นยุคซามูไร / นินจา (ข้า - เจ้า / นายท่าน / ท่านหญิง)",
        "protagonist": "นาโอเอะ ฟูจิบายาชิ (Naoe) & ยาสึเกะ (Yasuke)",
        "demeanor": (
            "สองวิถีแห่งแดนอาทิตย์อุทัย: นาโอเอะ = ชิโนบิสาว ว่องไว เด็ดเดี่ยว เร้นกายในเงามืด / "
            "ยาสึเกะ = ซามูไรผู้เปี่ยมเกียรติยศ หนักแน่น ภักดีต่อโนบูนางะ "
            "ยึดถือบูชิโด ลงท้าย 'ขอรับ / ท่าน' สรรพนาม 'ข้า-เจ้า / นายท่าน'"
        ),
        "keywords": [
            "shadows", "ac shadows", "yasuke", "naoe", "fujibayashi", "oda nobunaga",
            "shinobi", "shinba", "assassin's creed shadows", "assassins creed shadows"
        ]
    },
    "ac_general": {
        "title": "Assassin's Creed Series (แฟรนไชส์ภาคีมือสังหาร)",
        "era": "มหากาพย์ประวัติศาสตร์ สงครามระหว่างภาคีมือสังหารกับเทมพลาร์",
        "tone": "Italian Renaissance & Brotherhood / เรเนซองส์อิตาลี ภราดรภาพมือสังหารและล้างแค้น (Assassin's Creed 2, Brotherhood, Revelations)",
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "protagonist": "มือสังหารแห่งภราดรภาพ (Assassin of the Brotherhood)",
        "demeanor": (
            "สุขุม เยือกเย็น นอบน้อมต่อมิตรสหายและผู้อาวุโส ('สหาย/นายท่าน') "
            "มุ่งมั่นในเสรีภาพและเจตจำนงอิสระ เคารพในความตาย ('Requiescat in pace') สลับกับมิติไซไฟโลกปัจจุบัน (Animus/Abstergo)"
        ),
        "keywords": [
            "assassin's creed", "assassins creed", "animus", "hidden blade", "eagle vision",
            "pieces of eden", "leap of faith", "brotherhood", "templar order", "abstergo"
        ]
    }
}

def resolve_assassins_creed_installment(target_name="", sample_text_buf=""):
    """
    Analyzes game title, folder paths, and dialogue excerpts to identify
    the exact Assassin's Creed installment, era, setting, and character demeanors (ริยาบท).
    """
    clean_target = re.sub(r'[\_\-\+\.]+', ' ', str(target_name)).lower()
    sample_lower = str(sample_text_buf).lower()
    text_to_check = f"{clean_target} {sample_lower}"

    # Franchise anchors, iconic characters, mantras and installments
    has_ac_mention = any(k in text_to_check for k in [
        "assassin's creed", "assassins creed", "animus", "hidden blade",
        "eagle vision", "pieces of eden", "leap of faith", "abstergo",
        "requiescat in pace", "nothing is true, everything is permitted", "hidden ones",
        "brotherhood", "revelations", "black flag",
        # Protagonists & iconic lore
        "altair", "altaïr", "ezio", "auditore", "edward kenway", "jackdaw",
        "arno dorian", "jacob frye", "evie frye", "bayek", "medjay",
        "kassandra", "alexios", "misthios", "eivor", "raven clan",
        "basim", "basim ibn ishaq", "shay cormac", "haytham", "ratonhnhake",
        "ac1", "ac2", "ac3", "ac4"
    ])

    if not has_ac_mention:
        if re.search(r'\b(ac\s*([0-9]+|iv|ii|iii|unity|rogue|syndicate|origins|odyssey|valhalla|mirage|shadows|brotherhood|revelations|black\s*flag))\b', clean_target):
            has_ac_mention = True
        elif "assassin" in clean_target and any(k in text_to_check for k in ["creed", "blade", "animus", "order", "brotherhood"]):
            has_ac_mention = True

    if not has_ac_mention:
        return {"is_ac": False}

    best_key = None
    best_score = 0

    for key, data in ASSASSINS_CREED_INSTALLMENTS.items():
        if key == "ac_general":
            continue
        score = 0
        for kw in data["keywords"]:
            kw_lower = kw.lower()
            if len(kw_lower) <= 3:
                if re.search(r'\b' + re.escape(kw_lower) + r'\b', clean_target):
                    score += 60
                elif sample_lower and re.search(r'\b' + re.escape(kw_lower) + r'\b', sample_lower):
                    score += 15
            else:
                if kw_lower in clean_target:
                    score += 45
                elif sample_lower and kw_lower in sample_lower:
                    score += 20
        if score > best_score:
            best_score = score
            best_key = key

    if not best_key or best_score < 10:
        best_key = "ac_general"

    meta = dict(ASSASSINS_CREED_INSTALLMENTS[best_key])
    meta["is_ac"] = True
    meta["installment_key"] = best_key
    meta["score"] = best_score
    return meta

# ─────────────────────────────────────────────────────────────────────────────
# GAME UNIVERSE TONE DETECTION ENGINE & ONE-CLICK EASY MODE
# ─────────────────────────────────────────────────────────────────────────────

TONE_DETECTION_RULES = [
    # ── 1. ไซไฟ เทคโนโลยี และอวกาศ (Sci-Fi & Space) ──
    {
        "category": "🚀 ไซไฟ เทคโนโลยี และอวกาศ (Sci-Fi & Space)",
        "tone": "Star Wars & Space Opera / ลิเกอวกาศ มหากาพย์สงครามดวงดาว เจไดและซิธ (Star Wars, Mass Effect, KotOR, Jedi Survivor)",
        "pronoun": "🌌 มหากาพย์อวกาศ / Star Wars / แฟนตาซี (ข้า - เจ้า / ข้า - ท่าน)",
        "keywords": [
            "star wars", "jedi", "sith", "lightsaber", "force", "kotor", "skywalker", "padawan",
            "vader", "mandalorian", "coruscant", "tatooine", "droid", "stormtrooper", "galactic empire",
            "rebel alliance", "starship", "hyperspace", "mass effect", "normandy", "spectre", "shepard",
            "asari", "turian", "krogan", "lightsabers", "midichlorian", "tarkin", "kenobi", "cal kestis",
            "zero company", "jedi knight", "jedi academy", "republic commando", "rogue squadron"
        ],
        "label": "Star Wars & Space Opera (มหากาพย์อวกาศ/เจได/ซิธ)"
    },
    {
        "category": "🚀 ไซไฟ เทคโนโลยี และอวกาศ (Sci-Fi & Space)",
        "tone": "Cyberpunk & High-Tech Dystopia / ไซเบอร์พังก์ โลกอนาคตมืดมน ดิจิทัลใต้ดิน (Cyberpunk 2077, Deus Ex, Ghostrunner, Stray)",
        "pronoun": "🔥 สตรีท / นอกกฎหมาย / ปากจัด (กู - มึง / ฉัน - แก / ไอ้เวร)",
        "keywords": [
            "cyberpunk", "night city", "netrunner", "corpo", "arasaka", "militech", "braindance",
            "edgerunner", "deus ex", "cyberware", "implant", "augmented", "ghostrunner", "stray",
            "dystopia", "hacker", "ripperdoc", "sandevistan", "deck", "cyberdeck", "human revolution",
            "mankind divided", "cloudpunk", "the ascent", "ruiner", "shadowrun", "citizen sleeper"
        ],
        "label": "Cyberpunk & Dystopia (ไซเบอร์พังก์)"
    },
    {
        "category": "🚀 ไซไฟ เทคโนโลยี และอวกาศ (Sci-Fi & Space)",
        "tone": "Grimdark Sci-Fi / สงครามโกธิกอวกาศมืดมน ลัทธิจักรวรรดิ (Warhammer 40,000: Space Marine/Rogue Trader/Boltgun)",
        "pronoun": "🌌 มหากาพย์อวกาศ / Star Wars / แฟนตาซี (ข้า - เจ้า / ข้า - ท่าน)",
        "keywords": [
            "warhammer", "40000", "40k", "astartes", "space marine", "space marines",
            "imperium of man", "god-emperor", "heretic astartes", "adeptus astartes",
            "adeptus mechanicus", "inquisition", "inquisitor", "bolter", "boltgun",
            "necron", "necrons", "greenskins", "tyranid", "tyranids", "rogue trader",
            "omnissiah", "adeptus", "mechanicus", "ultramarine", "ultramarines",
            "darktide", "dawn of war", "chaos gate", "necromunda", "gladius",
            "battlefleet gothic", "horus heresy", "black legion", "servitor", "psykers"
        ],
        "label": "Warhammer 40K / Grimdark (สงครามโกธิกอวกาศมืดมน)"
    },
    {
        "category": "🚀 ไซไฟ เทคโนโลยี และอวกาศ (Sci-Fi & Space)",
        "tone": "Hard Sci-Fi & Space Engineering / ไซไฟสมจริง กู้ซากและวิศวกรรมอวกาศ (Hardspace: Shipbreaker, Elite Dangerous, Star Citizen)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "hardspace", "shipbreaker", "elite dangerous", "star citizen", "space engineers",
            "kerbal", "stationeers", "salvage", "thruster", "reactor", "tethers", "airlock", "lynx"
        ],
        "label": "Hard Sci-Fi & Space Engineering (วิศวกรรมอวกาศสมจริง)"
    },
    {
        "category": "🚀 ไซไฟ เทคโนโลยี และอวกาศ (Sci-Fi & Space)",
        "tone": "Space Exploration & Colonization / สำรวจดวงดาว บุกเบิกอาณานิคมอวกาศ (Starfield, No Man's Sky, The Outer Worlds, Deliver Us Mars)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "starfield", "no man's sky", "nomanssky", "outer worlds", "deliver us mars",
            "deliver us the moon", "astroneer", "everspace", "constellation", "colonization", "exoplanet"
        ],
        "label": "Space Exploration & Colonization (สำรวจดวงดาว/อาณานิคม)"
    },
    {
        "category": "🚀 ไซไฟ เทคโนโลยี และอวกาศ (Sci-Fi & Space)",
        "tone": "Cosmic & Deep Space Horror / สยองขวัญอวกาศลึกลับ สิ่งมีชีวิตต่างดาว (Dead Space, Prey, Returnal, Alien: Isolation, System Shock)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "dead space", "callisto protocol", "alien isolation", "aliens", "prey", "returnal",
            "system shock", "signalis", "necromorph", "ishimura", "xenomorph", "marker"
        ],
        "label": "Cosmic & Deep Space Horror (สยองขวัญอวกาศลึก)"
    },
    {
        "category": "🚀 ไซไฟ เทคโนโลยี และอวกาศ (Sci-Fi & Space)",
        "tone": "Mecha & Heavy Armor Warfare / หุ่นรบไซไฟ สงครามหุ้มเกราะไฮเทค (Armored Core, Titanfall, MechWarrior, Battletech)",
        "pronoun": "🪖 ทหารยุทธวิธี / สายลุย / ตำรวจ (ผม/ฉัน - นาย/พวกนาย/ผู้หมวด)",
        "keywords": [
            "armored core", "titanfall", "mechwarrior", "battletech", "front mission", "daemon x machina",
            "gundam", "mecha", "pilot", "rubicon", "coral", "mech", "chassis", "exosuit"
        ],
        "label": "Mecha & Heavy Armor Warfare (หุ่นรบหุ้มเกราะ)"
    },
    {
        "category": "🚀 ไซไฟ เทคโนโลยี และอวกาศ (Sci-Fi & Space)",
        "tone": "Steampunk & Victorian Industrial / จักรกลไอน้ำวิกตอเรียน เรโทรอนาคต (Dishonored, Bioshock Infinite, Lies of P, Frostpunk)",
        "pronoun": "🏰 แฟนตาซียุคกลาง / อัศวิน / เวทมนตร์ (ข้า - เจ้า / ข้า - ท่าน / ท่านลอร์ด)",
        "keywords": [
            "dishonored", "corvo", "emily", "dunwall", "karnaca", "outsider", "whale oil",
            "bioshock infinite", "columbia", "lies of p", "geppetto", "krat", "frostpunk",
            "steampunk", "victorian", "automaton", "clockwork", "steam engine"
        ],
        "label": "Steampunk & Victorian Industrial (จักรกลไอน้ำวิกตอเรียน)"
    },
    {
        "category": "🚀 ไซไฟ เทคโนโลยี และอวกาศ (Sci-Fi & Space)",
        "tone": "Dieselpunk & Alternate History / ดีเซลพังก์ สงครามโลกสมมติ (Wolfenstein, Iron Harvest, The Order: 1886)",
        "pronoun": "🪖 ทหารยุทธวิธี / สายลุย / ตำรวจ (ผม/ฉัน - นาย/พวกนาย/ผู้หมวด)",
        "keywords": [
            "wolfenstein", "blazkowicz", "iron harvest", "the order 1886", "dieselpunk",
            "reich", "panzer", "alternate history", "trench"
        ],
        "label": "Dieselpunk & Alternate History (ดีเซลพังก์/ประวัติศาสตร์สมมติ)"
    },
    {
        "category": "🚀 ไซไฟ เทคโนโลยี และอวกาศ (Sci-Fi & Space)",
        "tone": "Biopunk & Deep Sea Subterranean / ชีวกลายพันธุ์ ใต้สมุทรลึก (Bioshock 1/2, SOMA, Subnautica, Barotrauma)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "bioshock", "rapture", "big daddy", "little sister", "adam", "eve", "plasmid",
            "soma", "subnautica", "barotrauma", "under the waves", "deep sea", "underwater", "leviathan"
        ],
        "label": "Biopunk & Deep Sea (ชีวกลายพันธุ์/ใต้สมุทรลึก)"
    },
    {
        "category": "🚀 ไซไฟ เทคโนโลยี และอวกาศ (Sci-Fi & Space)",
        "tone": "Retro Sci-Fi & 80s Synthwave / ไซไฟย้อนยุค ซินธ์เวฟนีออน (Far Cry 3: Blood Dragon, Katana Zero, Hotline Miami)",
        "pronoun": "🔥 สตรีท / นอกกฎหมาย / ปากจัด (กู - มึง / ฉัน - แก / ไอ้เวร)",
        "keywords": [
            "blood dragon", "katana zero", "hotline miami", "synthwave", "retrowave", "neon", "cyber samurai"
        ],
        "label": "Retro Sci-Fi & Synthwave (ไซไฟเรโทร/ซินธ์เวฟ)"
    },

    # ── 2. แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical) ──
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "High & Epic Fantasy / แฟนตาซีมหากาพย์ เวทมนตร์และการผจญภัย (Baldur's Gate 3, The Witcher 3, Skyrim, Dragon Age)",
        "pronoun": "🏰 แฟนตาซียุคกลาง / อัศวิน / เวทมนตร์ (ข้า - เจ้า / ข้า - ท่าน / ท่านลอร์ด)",
        "keywords": [
            "baldur", "bg3", "witcher", "skyrim", "dragon age", "elder scrolls", "dungeons & dragons",
            "d&d", "faerun", "geralt", "rivia", "dragonborn", "tamriel", "spell", "cantrip",
            "wizard", "sorcerer", "cleric", "paladin", "goblin", "tavern", "illithid", "mind flayer",
            "dragon's dogma", "dragons dogma", "fable", "kingdoms of amalur", "divinity", "avowed"
        ],
        "label": "High & Epic Fantasy (แฟนตาซีมหากาพย์/เวทมนตร์)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Dark Fantasy & Soulslike / ดาร์กแฟนตาซี สิ้นหวัง ลึกลับ ทรงพลัง (Elden Ring, Dark Souls, Bloodborne, Diablo)",
        "pronoun": "🏰 แฟนตาซียุคกลาง / อัศวิน / เวทมนตร์ (ข้า - เจ้า / ข้า - ท่าน / ท่านลอร์ด)",
        "keywords": [
            "elden ring", "dark souls", "bloodborne", "demons souls", "demon's souls", "sekiro", "lies of p",
            "lords of the fallen", "tarnished", "grace", "erdtree", "bonfire", "estus", "ashen",
            "undead", "hollow", "great rune", "finger maiden", "soulsborne", "diablo", "sanctuary",
            "nephalem", "marika", "radagon", "malenia", "ranni", "yharnam", "mortal shell", "blasphemous",
            "grim dawn", "path of exile", "dawnwalker"
        ],
        "label": "Dark Fantasy & Soulslike (ดาร์กแฟนตาซี/วิญญาณ)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Eastern Wuxia & Xianxia / จีนกำลังภายใน เทพเซียน ยุทธภพ (Black Myth: Wukong, Wo Long, Gujian, Dynasty Warriors)",
        "pronoun": "⚔️ จีนกำลังภายใน / ยุทธภพ (ข้า - เจ้า / จอมยุทธ / แม่นาง / ศิษย์พี่)",
        "keywords": [
            "wukong", "black myth", "wo long", "dynasty warriors", "gujian", "xuan yuan", "xuan-yuan",
            "sword and fairy", "wuxia", "xianxia", "cultivation", "sect", "qi", "dantian",
            "meridian", "immortal", "dao", "shaolin", "wudang", "destined one", "sun wukong",
            "three kingdoms", "heroines through my lens", "fate seeker", "tale of immortal"
        ],
        "label": "Eastern Wuxia & Xianxia (จีนกำลังภายใน/เทพเซียน)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Feudal Japan & Samurai / ซามูไร-นินจายุคศักดินา เกียรติยศนักรบ (Ghost of Tsushima, Sekiro, Nioh, Like a Dragon: Ishin, AC Shadows)",
        "pronoun": "🏯 ญี่ปุ่นยุคซามูไร / นินจา (ข้า - เจ้า / นายท่าน / ท่านหญิง)",
        "keywords": [
            "tsushima", "ghost of tsushima", "sekiro", "nioh", "ishin", "ronin", "shogun",
            "samurai", "ninja", "shinobi", "katana", "bushido", "sengoku", "daimyo", "jin sakai",
            "kuro", "ashina", "lord sakai", "mongol", "rise of the ronin", "shadow tactics",
            "assassin's creed shadows", "assassins creed shadows", "ac shadows", "yasuke", "naoe"
        ],
        "label": "Feudal Japan & Samurai (ซามูไร/นินจา)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Medieval Historical / ประวัติศาสตร์ยุคกลาง ยุโรปสมจริง ไร้เวทมนตร์ (Kingdom Come: Deliverance, Mount & Blade, Crusader Kings)",
        "pronoun": "🏰 แฟนตาซียุคกลาง / อัศวิน / เวทมนตร์ (ข้า - เจ้า / ข้า - ท่าน / ท่านลอร์ด)",
        "keywords": [
            "kingdom come", "kcd", "deliverance", "mount & blade", "mount and blade", "bannerlord",
            "crusader kings", "chivalry", "manor lords", "henry", "bohemia", "feudal", "knight",
            "rattay", "skalitz", "medieval dynasty", "warband"
        ],
        "label": "Medieval Historical (ประวัติศาสตร์ยุคกลางสมจริง)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Crusades & Holy Land / สงครามครูเสด ภาคีมือสังหารศักดิ์สิทธิ์ (Assassin's Creed 1)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "keywords": [
            "assassin's creed 1", "assassins creed 1", "altair", "altaïr", "masyaf", "al mualim",
            "crusade", "crusader", "saracen", "robert de sable", "holy land", "ac1"
        ],
        "label": "Crusades & Holy Land (สงครามครูเสด/ภาคีมือสังหารศักดิ์สิทธิ์)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Italian Renaissance & Brotherhood / เรเนซองส์อิตาลี ภราดรภาพมือสังหารและล้างแค้น (Assassin's Creed 2, Brotherhood, Revelations)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "keywords": [
            "assassin's creed 2", "assassins creed 2", "ac2", "ac 2", "brotherhood", "revelations",
            "ezio", "auditore", "florence", "venice", "monteriggioni", "borgia", "cesare",
            "rodrigo", "da vinci", "leonardo", "machiavelli", "forli", "tuscany"
        ],
        "label": "Italian Renaissance & Brotherhood (เรเนซองส์อิตาลี/ภราดรภาพมือสังหาร)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Colonial American Revolution / ปฏิวัติอเมริกาและสงครามเจ็ดปี มือสังหารกับเทมพลาร์ (Assassin's Creed III, AC Rogue)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "keywords": [
            "assassin's creed 3", "assassins creed 3", "ac3", "ac 3", "ac rogue", "assassin's creed rogue",
            "assassins creed rogue", "connor", "ratonhnhake", "shay cormac", "haytham", "colonial",
            "boston tea party", "frontier", "george washington", "seven years war"
        ],
        "label": "Colonial American Revolution (ปฏิวัติอเมริกา/เทมพลาร์)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "French Revolution / การปฏิวัติฝรั่งเศส ปารีสเลือดและชนชั้นขุนนาง (Assassin's Creed Unity)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "keywords": [
            "assassin's creed unity", "assassins creed unity", "ac unity", "arno", "arno dorian",
            "elise de la serre", "robespierre", "bastille", "guillotine", "versailles", "notre-dame"
        ],
        "label": "French Revolution (การปฏิวัติฝรั่งเศส/ปารีส)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Victorian Industrial London / ลอนดอนวิกตอเรียน ปฏิวัติอุตสาหกรรมและแก๊งอันธพาล (Assassin's Creed Syndicate)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "assassin's creed syndicate", "assassins creed syndicate", "ac syndicate", "jacob frye",
            "evie frye", "rooks", "starrick", "blighters", "whitechapel", "big ben", "industrial revolution"
        ],
        "label": "Victorian Industrial London (ลอนดอนวิกตอเรียน/แก๊งอันธพาล)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Ancient Egyptian Antiquity / อียิปต์โบราณ เมดไจและกำเนิดภาคีเร้นกาย (Assassin's Creed Origins)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "keywords": [
            "assassin's creed origins", "assassins creed origins", "ac origins", "bayek", "siwa",
            "aya of alexandria", "medjay", "amunet", "cleopatra", "ptolemy", "pharaoh", "anubis"
        ],
        "label": "Ancient Egyptian Antiquity (อียิปต์โบราณ/เมดไจ)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Islamic Golden Age Baghdad / แบกแดดยุคทอง ภาคีผู้เร้นกายพันหนึ่งราตรี (Assassin's Creed Mirage)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "keywords": [
            "assassin's creed mirage", "assassins creed mirage", "ac mirage", "basim", "basim ibn ishaq",
            "roshan", "alamut", "hidden ones", "baghdad", "caliphate", "round city"
        ],
        "label": "Islamic Golden Age Baghdad (แบกแดดยุคทอง/ผู้เร้นกาย)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Greco-Roman Antiquity / อารยธรรมกรีก-โรมันโบราณ ทวยเทพและวีรชน (Assassin's Creed Odyssey, God of War ภาคกรีก, Titan Quest)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "keywords": [
            "expeditions rome", "rome", "odyssey", "ac odyssey", "spartan", "gladiator", "titan quest",
            "ryse", "son of rome", "roman", "greek", "olympus", "zeus", "caesar", "centurion", "legion",
            "assassin's creed odyssey", "assassins creed odyssey", "kassandra", "alexios", "misthios", "malaka"
        ],
        "label": "Greco-Roman Antiquity (กรีก-โรมันโบราณ)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Norse & Viking Saga / ตำนานนอร์ส ชนเผ่าไวกิ้ง รังนาร็อก (God of War Ragnarok, Valheim, Assassin's Creed Valhalla)",
        "pronoun": "🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)",
        "keywords": [
            "ragnarok", "valhalla", "valheim", "viking", "norse", "odin", "thor", "midgard",
            "asgard", "hellblade", "senua", "northgard", "jarl",
            "assassin's creed valhalla", "assassins creed valhalla", "ac valhalla", "eivor", "raven clan", "sigurd"
        ],
        "label": "Norse & Viking Saga (ตำนานนอร์ส/ไวกิ้ง)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Age of Sail & Piracy / ยุคเดินเรือ โจรสลัด ทะเลแคริบเบียน (Sea of Thieves, Assassin's Creed IV: Black Flag, Skull and Bones)",
        "pronoun": "🔥 สตรีท / นอกกฎหมาย / ปากจัด (กู - มึง / ฉัน - แก / ไอ้เวร)",
        "keywords": [
            "sea of thieves", "black flag", "skull and bones", "pirate", "caribbean", "galleon",
            "buccaneer", "corsair", "port royale", "risen", "edward kenway", "jackdaw",
            "assassin's creed 4", "assassins creed 4", "assassin's creed iv", "ac4", "ac 4"
        ],
        "label": "Age of Sail & Piracy (ยุคเดินเรือ/โจรสลัด)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Gothic Vampire & Occult / กอทิก ผีดูดเลือด ปราสาทมืดมนและไสยศาสตร์ (Castlevania, Vampire: The Masquerade, V Rising)",
        "pronoun": "🏰 แฟนตาซียุคกลาง / อัศวิน / เวทมนตร์ (ข้า - เจ้า / ข้า - ท่าน / ท่านลอร์ด)",
        "keywords": [
            "vampyr", "v rising", "vampire", "masquerade", "bloodlines", "castlevania", "dracula",
            "nosferatu", "occult", "gothic", "bloodlust", "coffin", "jonathan reid"
        ],
        "label": "Gothic Vampire & Occult (กอทิก/ผีดูดเลือด)"
    },
    {
        "category": "🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)",
        "tone": "Mythology & Folk Legends / เทพปกรณัม นิทานพื้นบ้าน มนตร์เสน่ห์ (Hades, Okami, Cult of the Lamb, Bramble)",
        "pronoun": "🏰 แฟนตาซียุคกลาง / อัศวิน / เวทมนตร์ (ข้า - เจ้า / ข้า - ท่าน / ท่านลอร์ด)",
        "keywords": [
            "hades", "zagreus", "okami", "cult of the lamb", "bramble", "folk legend", "mythology",
            "underworld", "persephone", "nyx", "charon", "ori and the"
        ],
        "label": "Mythology & Folk Legends (เทพปกรณัม/นิทานพื้นบ้าน)"
    },

    # ── 3. เอาชีวิตรอด สยองขวัญ และโลกล่มสลาย (Survival & Horror) ──
    {
        "category": "🧟 เอาชีวิตรอด สยองขวัญ และโลกล่มสลาย (Survival & Horror)",
        "tone": "Post-Apocalyptic Wasteland / แดนรกร้างโลกล่มสลาย กัมมันตรังสี (Fallout, Metro, S.T.A.L.K.E.R., Wasteland, Mad Max)",
        "pronoun": "🔥 สตรีท / นอกกฎหมาย / ปากจัด (กู - มึง / ฉัน - แก / ไอ้เวร)",
        "keywords": [
            "fallout", "metro", "stalker", "s.t.a.l.k.e.r.", "wasteland", "mad max", "vault-tec", "vault tec",
            "radiation", "rads", "pip boy", "pip-boy", "chornobyl", "chernobyl", "mutant", "scavenger",
            "ghoul", "artefact", "apocalypse", "krush kill", "remnant"
        ],
        "label": "Post-Apocalyptic Wasteland (โลกล่มสลาย/แดนรกร้าง)"
    },
    {
        "category": "🧟 เอาชีวิตรอด สยองขวัญ และโลกล่มสลาย (Survival & Horror)",
        "tone": "Zombie & Viral Outbreak / ไวรัสระบาด เอาชีวิตรอดจากซอมบี้ (Resident Evil, The Last of Us, Dying Light, Days Gone, Project Zomboid)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "resident evil", "biohazard", "last of us", "dying light", "days gone", "project zomboid",
            "left 4 dead", "dead island", "zombie", "infected", "cordyceps", "t virus", "t-virus",
            "raccoon city", "clicker", "umbrella corporation", "joel", "ellie", "the last stand",
            "bio inc", "outbreak", "undead"
        ],
        "label": "Zombie & Viral Outbreak (ซอมบี้/ไวรัสระบาด)"
    },
    {
        "category": "🧟 เอาชีวิตรอด สยองขวัญ และโลกล่มสลาย (Survival & Horror)",
        "tone": "Lovecraftian & Eldritch Horror / สยองขวัญคอสมิกเลิฟคราฟต์ ความวิปลาสโบราณ (Call of Cthulhu, Dredge, Darkest Dungeon, Alan Wake)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "cthulhu", "dredge", "darkest dungeon", "alan wake", "sinking city", "lovecraft",
            "eldritch", "madness", "sanity", "old ones", "insanity"
        ],
        "label": "Lovecraftian & Eldritch Horror (สยองขวัญคอสมิก/วิปลาส)"
    },
    {
        "category": "🧟 เอาชีวิตรอด สยองขวัญ และโลกล่มสลาย (Survival & Horror)",
        "tone": "Psychological & Paranormal / หลอนประสาท ลี้ลับเหนือธรรมชาติ (Silent Hill, Outlast, Fatal Frame, Control)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "silent hill", "outlast", "fatal frame", "control", "f.e.a.r.", "fear", "amnesia",
            "layers of fear", "paranormal", "psychological", "asylum", "pyramid head",
            "little goody two shoes", "visage", "medium"
        ],
        "label": "Psychological & Paranormal (หลอนประสาท/เหนือธรรมชาติ)"
    },
    {
        "category": "🧟 เอาชีวิตรอด สยองขวัญ และโลกล่มสลาย (Survival & Horror)",
        "tone": "Wilderness Survival & Crafting / เอาชีวิตรอดในพงไพรธรรมชาติ สร้างฐาน (The Forest, Green Hell, Rust, The Long Dark, Ark)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "the forest", "sons of the forest", "green hell", "rust", "the long dark", "ark",
            "raft", "crafting", "survival", "shelter", "campfire", "starvation"
        ],
        "label": "Wilderness Survival & Crafting (เอาชีวิตรอดในพงไพร)"
    },

    # ── 4. แอ็กชัน ยุคปัจจุบัน และการทหาร (Action & Military) ──
    {
        "category": "🔫 แอ็กชัน ยุคปัจจุบัน และการทหาร (Action & Military)",
        "tone": "Military Tactical & Spec-Ops / ยุทธวิธีทหาร หน่วยรบพิเศษ สมจริง (Call of Duty, Battlefield, Rainbow Six, Ghost Recon, ARMA)",
        "pronoun": "🪖 ทหารยุทธวิธี / สายลุย / ตำรวจ (ผม/ฉัน - นาย/พวกนาย/ผู้หมวด)",
        "keywords": [
            "call of duty", "cod", "modern warfare", "black ops", "battlefield", "rainbow six",
            "ghost recon", "arma", "spec ops", "spec-ops", "tactical", "delta force", "cqb",
            "squadron", "hostile", "extract", "air support", "recon", "captain price", "soap",
            "outpost infinity siege", "sniper elite"
        ],
        "label": "Military Tactical & Spec-Ops (การทหารยุทธวิธี)"
    },
    {
        "category": "🔫 แอ็กชัน ยุคปัจจุบัน และการทหาร (Action & Military)",
        "tone": "Urban Crime & Underworld / อาชญากรรมใต้ดิน แก๊งมาเฟีย เมืองใหญ่ (GTA, Mafia, Saints Row, Payday, Yakuza/Like a Dragon)",
        "pronoun": "🔥 สตรีท / นอกกฎหมาย / ปากจัด (กู - มึง / ฉัน - แก / ไอ้เวร)",
        "keywords": [
            "gta", "grand theft auto", "mafia", "saints row", "payday", "yakuza", "like a dragon",
            "sleeping dogs", "judgment", "heist", "mobster", "gangster", "underworld", "cartel", "cop"
        ],
        "label": "Urban Crime & Underworld (อาชญากรรมใต้ดิน/มาเฟีย)"
    },
    {
        "category": "🔫 แอ็กชัน ยุคปัจจุบัน และการทหาร (Action & Military)",
        "tone": "Espionage & Secret Agent / สายลับจารกรรม ลอบเร้น ชิงไหวชิงพริบ (Metal Gear Solid, Splinter Cell, Hitman, Deathloop)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "metal gear", "snake", "big boss", "splinter cell", "sam fisher", "hitman",
            "agent 47", "deathloop", "espionage", "secret agent", "stealth", "infiltrate",
            "evil genius", "covert"
        ],
        "label": "Espionage & Secret Agent (สายลับจารกรรม/ลอบเร้น)"
    },
    {
        "category": "🔫 แอ็กชัน ยุคปัจจุบัน และการทหาร (Action & Military)",
        "tone": "Western & Frontier Outlaw / คาวบอยคาวเลือด แดนเถื่อนตะวันตก ดวลปืน (Red Dead Redemption, Desperados, Weird West)",
        "pronoun": "🔥 สตรีท / นอกกฎหมาย / ปากจัด (กู - มึง / ฉัน - แก / ไอ้เวร)",
        "keywords": [
            "red dead", "rdr", "redemption", "arthur morgan", "van der linde", "desperados",
            "weird west", "cowboy", "outlaw", "sheriff", "saloon", "revolver", "gunslinger", "bounty hunter"
        ],
        "label": "Western & Frontier Outlaw (คาวบอยแดนเถื่อน)"
    },
    {
        "category": "🔫 แอ็กชัน ยุคปัจจุบัน และการทหาร (Action & Military)",
        "tone": "Superhero & Comic Universe / ซูเปอร์ฮีโร่และคอมิกส์ พิทักษ์เมือง (Marvel's Spider-Man, Batman Arkham, Injustice)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "spider-man", "spiderman", "batman", "arkham", "injustice", "guardians of the galaxy",
            "avengers", "suicide squad", "gotham", "marvel", "dc", "superhero", "villain"
        ],
        "label": "Superhero & Comic Universe (ซูเปอร์ฮีโร่และคอมิกส์)"
    },

    # ── 5. อนิเมะ JRPG และแฟนตาซีเอเชีย (Anime & Asian Fantasy) ──
    {
        "category": "🌸 อนิเมะ JRPG และแฟนตาซีเอเชีย (Anime & Asian Fantasy)",
        "tone": "Anime JRPG & High-School Fantasy / อนิเมะโรงเรียน ผจญภัยวัยรุ่น (Persona, Genshin Impact, Honkai: Star Rail, Final Fantasy)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "persona", "genshin", "honkai", "star rail", "final fantasy", "ff7", "ffxvi",
            "tales of", "granblue", "anime", "jrpg", "p5r", "phantom thief", "astral express",
            "atelier", "ryza", "yumia", "natsunee", "danganronpa", "trails of", "ys", "ni no kuni",
            "octopath", "fire emblem", "disgaea", "xenoblade", "fairy fencer", "neptunia",
            "lost epic", "sword art online", "sao", "fate/stay", "fate grand order", "fgo",
            "blue archive", "azur lane", "arknights", "zenless", "zenless zone zero", "wuthering waves",
            "valkyrie", "etrian", "shin megami tensei", "smt", "senran", "senran kagura", "peach beach",
            "sengoku rance", "rance", "eiyuden", "triangle strategy", "star ocean", "ender lilies",
            "ender magnolia", "little goody two shoes", "witch's apocalyptic journey", "witchs apocalyptic journey",
            "edge of eternity", "gnosia", "visual novel", "visualnovel",
            "senpai", "sensei", "kouhai", "chan", "kun", "san", "sama", "dono",
            "onii-chan", "onee-san", "waifu", "tsundere", "nakama", "arigato", "gomen", "kawaii",
            "classmate", "student council", "homeroom", "bento", "gacha", "maid",
            "isekai", "demon king", "maou", "adventurer", "adventurers guild", "potion", "potions",
            "mana", "alchemy", "alchemist", "slime", "chocobo", "magic circle"
        ],
        "label": "Anime JRPG & Asian Fantasy (อนิเมะ/JRPG)"
    },
    {
        "category": "🌸 อนิเมะ JRPG และแฟนตาซีเอเชีย (Anime & Asian Fantasy)",
        "tone": "Shonen Battle & High Action / อนิเมะต่อสู้ปล่อยพลัง มิตรภาพลูกผู้ชาย (Monster Hunter, Dragon Ball, Tales of Arise, Granblue Fantasy)",
        "pronoun": "🔥 สตรีท / นอกกฎหมาย / ปากจัด (กู - มึง / ฉัน - แก / ไอ้เวร)",
        "keywords": [
            "monster hunter", "dragon ball", "naruto", "one piece", "bleach", "tales of arise",
            "god eater", "scarlet nexus", "code vein", "mega man", "rockman", "guilty gear", "blazblue",
            "hunter", "palico", "saiyan", "chakra", "bankai", "haki", "super saiyan", "kamehameha"
        ],
        "label": "Shonen Battle & High Action (อนิเมะต่อสู้ปล่อยพลัง)"
    },
    {
        "category": "🌸 อนิเมะ JRPG และแฟนตาซีเอเชีย (Anime & Asian Fantasy)",
        "tone": "Cozy, Slice of Life & Farming / จำลองชีวิต อบอุ่นหัวใจและทำฟาร์ม (Stardew Valley, Animal Crossing, Rune Factory)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "doraemon", "story of seasons", "harvest moon", "stardew valley", "animal crossing",
            "rune factory", "slime rancher", "sandrock", "portia", "coral island", "fae farm", "farming",
            "crops", "watering can", "fertilizer", "barn", "coop", "harvest", "seeds"
        ],
        "label": "Cozy & Farming (จำลองชีวิต/ทำฟาร์มอบอุ่น)"
    },

    # ── 6. เสียดสี ตลกร้าย ปรัชญา และทั่วไป (Comedy, Satire & General) ──
    {
        "category": "🎭 เสียดสี ตลกร้าย ปรัชญา และทั่วไป (Comedy, Satire & General)",
        "tone": "Satirical & Dark Comedy / เสียดสีการเมือง ตลกร้ายฮาจัด กวนประสาท (Helldivers 2, The Outer Worlds, Borderlands, Portal, South Park)",
        "pronoun": "🔥 สตรีท / นอกกฎหมาย / ปากจัด (กู - มึง / ฉัน - แก / ไอ้เวร)",
        "keywords": [
            "helldivers", "borderlands", "tiny tina", "portal", "south park", "high on life",
            "destroy all humans", "tropico", "goat simulator", "satire", "comedy"
        ],
        "label": "Satirical & Dark Comedy (เสียดสีตลกร้าย)"
    },
    {
        "category": "🎭 เสียดสี ตลกร้าย ปรัชญา และทั่วไป (Comedy, Satire & General)",
        "tone": "Absurdist Bureaucracy & Dystopian / รัฐข้าราชการอำนาจนิยม ตลกร้าย (Papers Please, Beholder, The Stanley Parable)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "papers please", "beholder", "the stanley parable", "not tonight", "orwell", "bureaucracy", "ministry"
        ],
        "label": "Absurdist Bureaucracy (รัฐข้าราชการ/อำนาจนิยม)"
    },
    {
        "category": "🎭 เสียดสี ตลกร้าย ปรัชญา และทั่วไป (Comedy, Satire & General)",
        "tone": "Philosophical Detective & Surreal Noir / สืบสวนปรัชญา เหนือจริง ลุ่มลึก (Disco Elysium, Death Stranding, Kentucky Route Zero)",
        "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
        "keywords": [
            "disco elysium", "revachol", "death stranding", "kentucky route zero", "obra dinn",
            "pentiment", "gnosia", "detective", "philosophical", "noir"
        ],
        "label": "Philosophical Detective & Surreal Noir (สืบสวนปรัชญา/ลุ่มลึก)"
    }
]

def is_ui_or_junk_text(text):
    """Identifies short UI menu options, button labels, numbers, and technical tags."""
    if not text or not isinstance(text, str):
        return True
    s = text.strip()
    if len(s) < 4 or len(s) > 1000:
        return True
    if re.match(r'^[0-9\.\,\:\;\-\_\+\*\#\/\s\(\)\[\]\{\}\%\$\@\!\?\|\\]+$', s):
        return True
    ui_blacklist = {
        "ok", "cancel", "options", "apply", "back", "settings", "graphics", "audio",
        "display", "resolution", "volume", "vsync", "exit", "quit", "save", "load",
        "new game", "continue", "yes", "no", "on", "off", "controls", "confirm",
        "gameplay", "video", "language", "subtitles", "default", "brightness",
        "gamma", "contrast", "music", "sfx", "voice", "master volume", "windowed",
        "fullscreen", "borderless", "pause", "resume", "retry", "restart", "main menu"
    }
    if s.lower() in ui_blacklist:
        return True
    return False

def collect_stratified_dialogue_samples(data_source, max_samples=80):
    """
    Extracts stratified dialogue and narrative samples from a list of strings,
    dict records, or table model, intentionally filtering out UI menu noise and
    sampling evenly across the full progression of the dataset.
    """
    if not data_source:
        return []

    raw_lines = []
    if isinstance(data_source, list):
        for item in data_source:
            if isinstance(item, dict):
                src = item.get("source") or item.get("text") or item.get("src") or ""
            else:
                src = str(item)
            if src and str(src).strip():
                raw_lines.append(str(src).strip())
    else:
        raw_lines = [str(data_source).strip()]

    if not raw_lines:
        return []

    meaningful = [txt for txt in raw_lines if not is_ui_or_junk_text(txt)]
    if not meaningful:
        meaningful = [txt for txt in raw_lines if len(txt) > 3]

    total = len(meaningful)
    if total <= max_samples:
        return meaningful

    samples = []
    bucket_count = 5
    bucket_size = total // bucket_count
    per_bucket = max_samples // bucket_count

    for b in range(bucket_count):
        start = b * bucket_size
        end = (b + 1) * bucket_size if b < bucket_count - 1 else total
        slice_items = meaningful[start:end]
        if not slice_items:
            continue
        ranked = sorted(slice_items, key=lambda x: ((' ' in x), len(x) > 15, len(x)), reverse=True)
        step = max(1, len(ranked) // per_bucket)
        picked = [ranked[i] for i in range(0, min(len(ranked), per_bucket * step), step)][:per_bucket]
        samples.extend(picked)

    return samples[:max_samples]

# -------------------------------------------------------------
# INTELLIGENT GAME ENTITY & TERMINOLOGY EXTRACTION ENGINE
# -------------------------------------------------------------
GAME_LOCALIZATION_STOPWORDS = {
    "a", "about", "above", "across", "actually", "after", "again", "against", "all", "almost", "alone", "along",
    "already", "also", "although", "always", "am", "among", "an", "and", "another", "any", "anybody", "anyone",
    "anything", "anywhere", "are", "aren't", "around", "as", "ask", "asked", "asking", "at", "away", "back", "bad",
    "be", "because", "been", "before", "behind", "being", "believe", "below", "beside", "besides", "best", "better",
    "between", "beyond", "both", "bring", "brought", "but", "by", "call", "called", "came", "can", "can't", "cannot",
    "cause", "certain", "certainly", "clear", "clearly", "close", "come", "comes", "coming", "could", "couldn't",
    "course", "damn", "did", "didn't", "do", "does", "doesn't", "doing", "done", "don't", "down", "during", "each",
    "either", "else", "enough", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere",
    "except", "far", "fast", "feel", "few", "finally", "find", "fine", "first", "five", "for", "from", "get", "gets",
    "getting", "give", "given", "giving", "go", "goes", "going", "gone", "good", "got", "great", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "hear", "heard", "hello", "help",
    "her", "here", "here's", "hers", "herself", "hey", "him", "himself", "his", "hold", "home", "hope", "how",
    "however", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it'd", "it'll", "it's",
    "its", "itself", "just", "keep", "kept", "knew", "know", "known", "last", "late", "later", "least", "leave",
    "left", "less", "let", "let's", "like", "likely", "listen", "little", "live", "look", "looked", "looking", "looks",
    "lose", "lost", "lot", "lots", "made", "make", "makes", "making", "many", "matter", "may", "maybe", "me", "mean",
    "meanwhile", "might", "mind", "mine", "miss", "more", "moreover", "most", "mostly", "move", "moved", "much",
    "must", "my", "myself", "near", "need", "needed", "needs", "never", "new", "next", "nice", "no", "nobody", "none",
    "noone", "nope", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "oh", "ok", "okay", "on",
    "once", "one", "ones", "only", "onto", "open", "or", "other", "others", "our", "ours", "ourselves", "out",
    "outside", "over", "own", "part", "perhaps", "please", "point", "probably", "put", "quite", "rather", "ready",
    "really", "remember", "right", "run", "said", "same", "saw", "say", "saying", "says", "second", "see", "seeing",
    "seem", "seemed", "seems", "seen", "several", "shall", "she", "she'd", "she'll", "she's", "should", "shouldn't",
    "show", "side", "since", "so", "some", "somebody", "someone", "something", "sometimes", "somewhere", "soon",
    "sorry", "still", "stop", "such", "sure", "take", "taken", "taking", "tell", "telling", "than", "thank", "thanks",
    "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they",
    "they'd", "they'll", "they're", "they've", "thing", "things", "think", "thinking", "this", "those", "though",
    "thought", "three", "through", "time", "to", "today", "together", "told", "tomorrow", "too", "took", "top",
    "toward", "towards", "true", "truly", "try", "trying", "turn", "turned", "two", "under", "until", "up", "upon",
    "us", "use", "used", "using", "very", "wait", "waiting", "want", "wanted", "wants", "was", "wasn't", "watch",
    "way", "we", "we'd", "we'll", "we're", "we've", "well", "went", "were", "weren't", "what", "whatever", "what's",
    "when", "where", "where's", "whether", "which", "while", "who", "who's", "whole", "whom", "whose", "why", "will",
    "with", "within", "without", "won't", "work", "world", "worse", "worst", "would", "wouldn't", "wrong", "yeah",
    "year", "yes", "yet", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    "end", "user", "tap", "cal", "force"
}

GAME_LEGAL_STOPWORDS = {
    "privacy policy", "terms of service", "user agreement", "eula", "activision", "activision publishing",
    "facebook", "twitter", "youtube", "discord", "all rights reserved", "copyright", "trademarks", "license",
    "subscriber", "end user license", "end user license agreement", "privacy", "policy", "inc", "llc",
    "corporation", "publisher", "publishing", "developed by", "published by", "customer service",
    "technical support", "service provided content", "service provided", "online services",
    "united states", "content", "agreement", "party", "trademark", "warranties", "disclaimer"
}

TITLE_PREFIXES = {
    "captain", "general", "sergeant", "major", "colonel", "lieutenant", "commander", "admiral", "doctor", "dr",
    "mr", "mrs", "ms", "lord", "sir", "lady"
}

_COMMON_ENGLISH_WORDS_CACHE = None

def get_common_english_words():
    global _COMMON_ENGLISH_WORDS_CACHE
    if _COMMON_ENGLISH_WORDS_CACHE is not None:
        return _COMMON_ENGLISH_WORDS_CACHE

    words_set = set()
    res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "common_english_words.json")
    if os.path.exists(res_path):
        try:
            with open(res_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    words_set = set(w.lower().strip() for w in data if w)
        except Exception as e:
            print(f"[TLM Studio] Warning reading common_english_words.json: {e}")

    if not words_set:
        words_set = set(GAME_LOCALIZATION_STOPWORDS)

    _COMMON_ENGLISH_WORDS_CACHE = words_set
    return _COMMON_ENGLISH_WORDS_CACHE

RE_VOCAL_SOUNDS = re.compile(
    r'^(?:'
    # Any repeating letters 3 or more (e.g. Aaaah, Nnnn, Haaah)
    r'.*([a-zA-Z])\1{2,}.*|'
    # Standard vocal interjections and moans (strictly NOT matching normal double-letter words like Woods, Reed, Quinn, Green, Rook)
    r'[Aa]h+n*|[Hh][aeou]+[hng]*|[Oo]h+|[Uu]h+|[Ee]h+|[Mm]m+h*|[Nn]n+h*|[Uu]m+|[Hh]m+|[Gg][ua]h+|[Uu]gh+|'
    r'[Kk][ua]h+|[Nn]gh+|[Mm]nh+|[Hh]gh+|[Ww]h[aouei]{2,}|[Ww]hew|[Ee]ek|[Kk]yaa+|[Uu]waa+|[Ff]ufu(?:fu)?|'
    r'[Ee]hehe+|[Nn]yaa+|[Aa]ra|[Bb]wah|[Aa]hem|[Ss]igh|[Gg]asp|[Tt][sc]k|[Pp]fft|[Hh]mph|[Hh]rm|'
    r'[Yy]ay|[Yy]uck|[Oo]uch|[Oo]w+|[Oo]of|[Oo]ops|[Pp]shew|[Bb]am|[Bb]oom|[Cc]lap|[Gg]ulp|'
    r'[Ss]plurt|[Ss]quirt|[Gg]ush|[Tt]witch|[Cc]ough|[Ss]lurp|[Bb]lurt|[Bb]lub|[Gg]ob|[Ss]hh+'
    r')$',
    re.IGNORECASE
)

GENERIC_ROLE_NOUNS = {
    "man", "men", "woman", "women", "boy", "boys", "girl", "girls", "child", "children",
    "guy", "guys", "person", "people", "staff", "folk", "folks",
    "gramps", "granny", "servant", "servants", "maid", "maids", "soldier", "soldiers",
    "guard", "guards", "butler", "butlers", "villager", "villagers", "citizen", "citizens"
}

STRICT_GENERIC_SINGLE_NOUNS = {
    "base", "flight", "island", "white", "black", "fleet", "wings", "unit", "valley",
    "number", "attack", "door", "key", "zone", "ground", "crew", "fighter", "missile",
    "operation", "endurance", "potion", "demon", "sword", "shield", "armor", "monster",
    "cavern", "slime", "goblin", "rifle", "pistol", "shotgun", "grenade", "room", "house",
    "tree", "water", "fire", "wind", "earth", "gold", "silver", "iron", "steel", "stone",
    "wood", "cloth", "leather", "meat", "bread", "apple", "herb", "flower", "book", "note",
    "letter", "map", "chest", "box", "bag", "ring", "necklace", "boots", "gloves", "helmet",
    "hat", "shirt", "pants", "shoes", " weapon", "item", "quest", "skill", "level", "rank"
}

GENERIC_MULTIWORD_BLACKLIST = {
    "standing art", "boob divination", "peerless middle", "thank you", "thanks a lot",
    "good morning", "good afternoon", "good evening", "good night", "see you", "excuse me",
    "new game", "load game", "save game", "main menu", "title screen", "game over",
    "press start", "press any key", "high quality", "medium quality", "low quality",
    "sound effect", "sound effects", "background music", "voice volume", "master volume",
    "full screen", "windowed mode", "borderless window", "frame rate", "vertical sync",
    "motion blur", "depth of field", "shadow quality", "texture quality", "anti aliasing",
    "the player", "climate change", "third cold war", "super soldier", "virtual simulation",
    "combat androids", "lore dossier", "key technologies", "world setting", "story premise",
    "core conflict", "major factions", "thai localization", "pronoun guide", "tone & register",
    "combat dialogue", "pronoun system",
    # UI headers, prompt directives & controller tokens (Zero Self-Ingestion)
    "all categories", "master lore", "glossary dossier", "zero hallucination",
    "key characters", "proper-noun locations", "master glossary table", "default",
    "candidate entities", "universe tone", "tone category", "pronoun preset",
    "strict gender", "custom rules", "extract mode", "term count", "target categories",
    "day length", "atmospheric composition", "distance from sun", "year length",
    "mission type", "breaking news", "mini boss",
    "left_stick_forward", "right_stick_forward", "left_stick_back", "right_stick_back",
    "button_a", "button_b", "button_x", "button_y",
    "dpad_up", "dpad_down", "dpad_left", "dpad_right"
}

LORE_ENTITY_NOUNS = {
    # Hierarchy & Titles
    "lord", "lady", "king", "queen", "prince", "princess", "emperor", "empress",
    "captain", "commander", "admiral", "general", "major", "colonel", "lieutenant", "sergeant",
    "master", "chief", "overlord", "baron", "count", "duke", "archbishop", "pope",
    # Factions, Organizations & Military Units
    "company", "force", "task force", "squad", "unit", "team", "flight", "corps", "regiment",
    "battalion", "platoon", "division", "fleet", "clan", "guild", "cult", "sect", "covenant",
    "alliance", "federation", "republic", "empire", "syndicate", "cartel", "guard", "vanguard",
    "sentinel", "knights", "brotherhood", "legion", "order", "dominion", "accord", "pact",
    "coalition", "corporation", "immortals", "initiative", "agency", "bureau", "ministry",
    # Gear, Weapons & Combat
    "sword", "shield", "armor", "blade", "spear", "staff", "wand", "rod", "bow", "axe",
    "hammer", "mace", "dagger", "cannon", "gun", "rifle", "carbine", "shotgun", "grenade",
    "mine", "turret", "missile", "torpedo", "bomb", "collar", "ring", "crown", "helm",
    "helmet", "boots", "gauntlets", "cloak", "robe", "cybercore", "interface", "implant",
    "module", "protocol", "system", "network", "virus", "gas", "serum", "drop", "card", "tag",
    # Lore Items, Artifacts & Alchemy
    "down", "feather", "tail", "wing", "fang", "horn", "tome", "scroll", "grimoire", "shard",
    "crystal", "core", "gem", "stone", "orb", "relic", "artifact", "rune", "sigil", "crest",
    "badge", "medal", "insignia", "emblem", "potion", "elixir", "amulet", "talisman", "chalice",
    "grail", "flare", "seed", "tear", "ash", "ember", "soul", "essence", "key", "cryptokey",
    # Places & Architecture
    "citadel", "kingdom", "dynasty", "realm", "sanctuary", "forest", "plains", "cavern",
    "caverns", "dungeon", "tower", "ruins", "shrine", "temple", "outpost", "bunker", "sector",
    "zone", "district", "bastion", "fortress", "keep", "haven", "colosseum", "arena", "valley",
    "mountain", "peak", "abyss", "trench", "grove", "oasis", "vault", "station", "hill",
    "city", "island", "safehouse", "facility", "laboratory", "lab", "base", "complex"
}

NUMBERED_STRUCTURAL_PATTERN = re.compile(
    r'^(?:Quest|Chapter|Episode|Stage|Level|Map|Area|Floor|Part|Act|Vol|Volume|Day|Night|Step|Rank|Phase|No|Page)\s+[0-9]+$',
    re.IGNORECASE
)

THAI_TITLE_PREFIXES = (
    "ผู้บังคับการ", "ผู้บัญชาการ", "ผบ.", "กัปตัน", "นายพล", "พลเอก", "พลโท", "พลตรี",
    "จ่า", "สิบเอก", "พันตรี", "พันเอก", "พันโท", "ร้อยโท", "ร้อยเอก", "ผู้การ",
    "ดร.", "ดอกเตอร์", "หมอ", "ศาสตราจารย์", "ลอร์ด", "เลดี้", "เซอร์",
    "ราชา", "กษัตริย์", "ราชินี", "เจ้าชาย", "เจ้าหญิง", "จักรพรรดิ", "อาจารย์",
    "มาสเตอร์", "หลวงพ่อ", "บาทหลวง", "เจ้าหน้าที่", "สายลับ", "นักสืบ", "สารวัตร", "หัวหน้า"
)

RE_THAI_CHAR = re.compile(r'[\u0E00-\u0E7F]')
RE_LATIN_CHAR = re.compile(r'[A-Za-z]')

def normalize_category_tag(raw_tag, en_term="", context="", default_tag="General"):
    t = f"{raw_tag or ''} {en_term or ''} {context or ''}".lower()
    if raw_tag:
        rt = str(raw_tag).strip().lower()
        for vt in VALID_TAGS:
            if vt.lower() == rt:
                return vt
        if any(k in rt for k in ("person", "character", "char", "npc", "ตัวละคร", "บุคคล")):
            return "Person"
        if any(k in rt for k in ("location", "place", "city", "world", "region", "สถานที่", "เมือง", "ดินแดน", "ฐาน")):
            return "Location"
        if any(k in rt for k in ("faction", "org", "group", "company", "ฝ่าย", "องค์กร", "กลุ่ม", "บริษัท", "กองกำลัง")):
            return "Faction"
        if any(k in rt for k in ("weapon", "gun", "sword", "arm", "อาวุธ", "ปืน", "ดาบ")):
            return "Weapon"
        if any(k in rt for k in ("item", "artifact", "relic", "tech", "gear", "ไอเทม", "สิ่งของ", "อุปกรณ์", "เทคโนโลยี")):
            return "Item"
        if any(k in rt for k in ("quest", "mission", "mode", "เควสต์", "ภารกิจ", "โหมด")):
            return "Quest"

    if any(k in t for k in ("contract", "deathmatch", "mission", "quest", "ภารกิจ", "สัญญาจ้าง", "โหมดการเล่น")):
        return "Quest"
    if any(k in t for k in ("corporation", "accord", "pact", "coalition", "immortals", "cia", "fbi", "faction", "พันธมิตร", "สนธิสัญญา", "องค์กร", "บรรษัท", "บริษัท", "กองกำลัง", "มาเฟีย")):
        return "Faction"
    if any(k in t for k in ("station", "forest", "city", "tower", "island", "valley", "zone", "citadel", "safehouse", "เมือง", "สถานี", "ป่า", "ฐานปฏิบัติการ", "เขตกักกัน", "ไคโร", "ซูริก", "สิงคโปร์", "อียิปต์")):
        return "Location"
    if any(k in t for k in ("interface", "dni", "cybercore", "cybernetic", "nova", "divinium", "cryptokey", "supply drop", "calling card", "clan tag", "ชิป", "โมดูล", "ก๊าซ", "อาวุธชีวภาพ", "กล่องเสบียง", "สกุลเงิน", "การ์ด", "ป้าย")):
        return "Item"
    if any(k in t for k in ("rifle", "pistol", "launcher", "weapon", "gun", "sword", "blade", "turret", "sentry", "ปืน", "อาวุธ", "ดาบ")):
        return "Weapon"
    return default_tag

def strip_thai_title_prefix(th_str):
    s = th_str.strip()
    for pfx in THAI_TITLE_PREFIXES:
        if s.startswith(pfx):
            rest = s[len(pfx):].strip()
            if rest:
                return rest
    return s

def expand_entity_variants(en_raw, th_raw, tag, context=""):
    """
    Expands a Glossary entity into essential spoken/written variants:
    - Parenthetical abbreviations/aliases: 'Direct Neural Interface (DNI)' -> 'Direct Neural Interface' + 'DNI'
    - Slash pairs: 'Winslow Accord / WA' -> 'Winslow Accord' + 'WA'
    - 'The ...' proper nouns: 'The Frozen Forest' -> 'The Frozen Forest' + 'Frozen Forest'
    - Character Full Names (Person): 'Commander John Taylor' -> 'Commander John Taylor' + 'John Taylor' + 'Taylor' + 'John'
    """
    results = []
    en_clean = re.sub(r'^\*\*|\*\*$', '', str(en_raw or '').strip()).strip(' "\'•*-`')
    th_clean = re.sub(r'^\*\*|\*\*$', '', str(th_raw or '').strip()).strip(' "\'`')
    if not en_clean or not th_clean:
        return results
    if en_clean.lower() in GENERIC_MULTIWORD_BLACKLIST:
        return results

    alt_th = ""
    if " / " in th_clean and "/" not in en_clean:
        th_parts = [p.strip() for p in th_clean.split(" / ") if p.strip()]
        if len(th_parts) >= 2:
            th_clean = th_parts[0]
            alt_th = th_parts[1]

    m_paren_en = re.match(r'^([A-Za-z0-9\s\'\-\.]+?)\s*\(([A-Za-z0-9\-\s\'\.]{2,40})\)$', en_clean)
    m_paren_th = re.match(r'^(.+?)\s*\((.+?)\)$', th_clean)
    if m_paren_en:
        part1_en = m_paren_en.group(1).strip()
        part2_en = m_paren_en.group(2).strip()
        if m_paren_th:
            main_th = m_paren_th.group(1).strip()
            alias_th = m_paren_th.group(2).strip()
            results.append((part1_en, main_th, tag, context, alt_th))
            results.append((part2_en, alias_th, tag, f"ชื่อย่อ/ชื่อเต็มของ {part1_en}" if not context else context, ""))
        else:
            results.append((part1_en, th_clean, tag, context, alt_th))
            p2_th = alt_th if (alt_th and part2_en in alt_th) else (part2_en if part2_en.isupper() and len(part2_en) <= 5 else th_clean)
            results.append((part2_en, p2_th, tag, f"ชื่อย่อ/ชื่อเต็มของ {part1_en}" if not context else context, ""))
        en_clean = part1_en
        th_clean = m_paren_th.group(1).strip() if m_paren_th else th_clean
    elif "/" in en_clean and len(en_clean.split("/")) == 2:
        p1, p2 = [p.strip() for p in en_clean.split("/")]
        if " / " in th_raw and len(th_raw.split(" / ")) == 2:
            t1, t2 = [t.strip() for t in th_raw.split(" / ")]
            results.append((p1, t1, tag, context, ""))
            results.append((p2, t2, tag, context, ""))
        else:
            results.append((p1, th_clean, tag, context, alt_th))
            results.append((p2, alt_th or th_clean, tag, context, ""))
        en_clean = p1
    else:
        if m_paren_th and re.match(r'^[A-Za-z0-9\s\'\-\.]+$', m_paren_th.group(2).strip()):
            th_clean = m_paren_th.group(1).strip()
        results.append((en_clean, th_clean, tag, context, alt_th))

    if en_clean.lower().startswith("the ") and len(en_clean) > 6 and tag in ("Location", "Item", "Faction", "Weapon", "General"):
        no_the = en_clean[4:].strip()
        results.append((no_the, th_clean, tag, context, alt_th))

    if tag == "Person":
        en_no_nick = re.sub(r'\s*["\'“‘][^"\'”’]+["\'”’]\s*', ' ', en_clean).strip()
        th_no_nick = re.sub(r'\s*["\'“‘][^"\'”’]+["\'”’]\s*', ' ', th_clean).strip()
        en_tokens = en_no_nick.split()

        if len(en_tokens) >= 2 and en_tokens[0].lower().strip(".,") in TITLE_PREFIXES:
            en_stripped = " ".join(en_tokens[1:]).strip()
            th_stripped = strip_thai_title_prefix(th_no_nick)
            results.append((en_stripped, th_stripped, "Person", f"ชื่อของ {en_clean}", ""))
            en_tokens = en_stripped.split()
            th_no_nick = th_stripped

        th_tokens = th_no_nick.split()
        if len(en_tokens) == 2 and len(th_tokens) == 2:
            w1_en, w2_en = en_tokens[0].strip(".,"), en_tokens[1].strip(".,")
            w1_th, w2_th = th_tokens[0].strip(), th_tokens[1].strip()
            if len(w2_en) >= 2 and not w2_en.isdigit():
                results.append((w2_en, w2_th, "Person", f"นามสกุล/ชื่อเรียกในบทสนทนาของ {en_clean}", ""))
            if len(w1_en) >= 3 and not w1_en.isdigit():
                results.append((w1_en, w1_th, "Person", f"ชื่อต้นของ {en_clean}", ""))

    return results

def parse_lore_glossary_and_entities(lore_text):
    """
    Parses a Lore Summary (from Gemini Web, AI Lore Scout, or Markdown/Text file) and extracts:
    1. Structured Glossary Items: [{'en', 'th', 'tag', 'context', 'alt'}, ...] covering:
       - All Main & Key Characters (with automatic full name + spoken short name/surname expansion)
       - All Proper-Noun Locations & Factions
       - All Unique Proper-Noun Items & Weapons
       - Master Glossary Tables (both Markdown pipe tables and Gemini Web copied stacked tables)
    2. Candidate English Entities list for any untagged/untranslated proper nouns.
    """
    if not lore_text or not isinstance(lore_text, str):
        return [], []

    glossary_items = []
    seen_en_lower = set()
    candidate_entities = []
    seen_cand_lower = set()

    def add_candidate_entity(en_str):
        en_c = re.sub(r'^\*\*|\*\*$', '', str(en_str).strip()).strip(' "\'•*-`')
        if not en_c or len(en_c) < 2 or len(en_c) > 55:
            return
        low = en_c.lower()
        if low in GENERIC_MULTIWORD_BLACKLIST or low in ("ai", "we", "i", "english", "english term", "original", "term", "category", "context", "note", "notes", "none", "n/a"):
            return
        if RE_THAI_CHAR.search(en_c) or not RE_LATIN_CHAR.search(en_c):
            return
        if low not in seen_cand_lower:
            seen_cand_lower.add(low)
            candidate_entities.append(en_c)

    def add_glossary_pair(en_raw, th_raw, raw_tag, context=""):
        tag = normalize_category_tag(raw_tag, en_raw, context, default_tag="General")
        variants = expand_entity_variants(en_raw, th_raw, tag, context)
        for v_en, v_th, v_tag, v_ctx, v_alt in variants:
            if not v_en or not v_th:
                continue
            if not RE_LATIN_CHAR.search(v_en):
                continue
            low = v_en.lower()
            if low in ("english", "english term", "original", "term", "source", "---", ":---", "ai", "we", "i") or low in GENERIC_MULTIWORD_BLACKLIST:
                continue
            if is_common_generic_english_word(v_en, tag=v_tag, from_lore=True):
                continue
            add_candidate_entity(v_en)
            if low not in seen_en_lower:
                seen_en_lower.add(low)
                glossary_items.append({
                    "en": v_en,
                    "th": v_th,
                    "tag": v_tag,
                    "context": v_ctx,
                    "alt": v_alt
                })

    lines = [ln.strip() for ln in lore_text.splitlines() if ln.strip()]
    current_section_tag = "General"
    section_blacklist = False
    inline_candidates = []

    i = 0
    while i < len(lines):
        s = lines[i]

        # 1. Stacked Gemini Web table rows (when HTML tables are copied from Gemini Web without pipes)
        if s in ("ภาษาอังกฤษ", "English Term", "English", "คำศัพท์ (English)", "คำศัพท์เฉพาะ (English)") and i + 2 < len(lines):
            if "คำแปล" in lines[i+1] or "Thai" in lines[i+1]:
                has_cat_col = ("Category" in lines[i+2] or "หมวดหมู่" in lines[i+2])
                step = 4 if (has_cat_col and i + 3 < len(lines) and ("คำอธิบาย" in lines[i+3] or "Context" in lines[i+3] or "บทบาท" in lines[i+3])) else 3
                i += step
                while i + (step - 1) < len(lines):
                    row_en = lines[i]
                    if re.match(r'^(?:\*\*)?[0-9]+\.\s+', row_en) or row_en.startswith("#"):
                        break
                    if step == 4:
                        row_th, row_cat, row_ctx = lines[i+1], lines[i+2], lines[i+3]
                    else:
                        row_th, row_cat, row_ctx = lines[i+1], "", lines[i+2]
                    if RE_LATIN_CHAR.search(row_en) and not RE_THAI_CHAR.search(row_en) and RE_THAI_CHAR.search(row_th):
                        add_glossary_pair(row_en, row_th, row_cat, row_ctx)
                        i += step
                    else:
                        break
                continue

        # 2. Detect section headers
        if s.startswith("#") or re.match(r'^(?:\*\*)?[0-9]+\.\s+', s) or s in ("ตัวละครหลัก (Characters)", "องค์กรและฝ่ายมหาอำนาจ (Major Factions)", "ทีมของเทย์เลอร์ (Taylor's Squad):"):
            h_low = s.lower()
            if any(k in h_low for k in ("สรรพนาม", "pronoun", "style guide", "ทิศทางการแปล", "ตัวอย่างการปรับสำนวน")):
                section_blacklist = True
            else:
                section_blacklist = False
                if any(k in h_low for k in ("ตัวละคร", "character", "person", "squad", "cast", "protagonist", "npc")):
                    current_section_tag = "Person"
                elif any(k in h_low for k in ("สถานที่", "เมือง", "ดินแดน", "location", "place", "region", "world")):
                    current_section_tag = "Location"
                elif any(k in h_low for k in ("ไอเทม", "สิ่งของ", "อุปกรณ์", "เทคโนโลยี", "ศัพท์เฉพาะ", "item", "artifact", "tech", "terminology")):
                    current_section_tag = "Item"
                elif any(k in h_low for k in ("อาวุธ", "weapon")):
                    current_section_tag = "Weapon"
                elif any(k in h_low for k in ("ฝ่าย", "องค์กร", "มหาอำนาจ", "faction", "organization")):
                    current_section_tag = "Faction"
                else:
                    current_section_tag = "General"
            i += 1
            continue

        # 3. Markdown Pipe Table Row
        if s.startswith("|") and s.count("|") >= 3:
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) >= 2:
                c0 = re.sub(r'\*\*|`', '', cells[0]).strip()
                c1 = re.sub(r'\*\*|`', '', cells[1]).strip()
                if c0 and c1 and not c0.startswith("-") and not c1.startswith("-"):
                    if c0.lower() not in ("english", "english term", "term", "คำศัพท์", "ชื่อภาษาอังกฤษ", "ต้นฉบับ"):
                        row_tag = cells[2].strip() if len(cells) >= 3 else current_section_tag
                        row_ctx = cells[3].strip() if len(cells) >= 4 else ""
                        if RE_THAI_CHAR.search(c0) and not RE_THAI_CHAR.search(c1) and RE_LATIN_CHAR.search(c1):
                            c0, c1 = c1, c0
                        add_glossary_pair(c0, c1, row_tag, row_ctx)
            i += 1
            continue

        # 4. Definition lines (with or without bullets, since Gemini Web copy strips bullets)
        if not section_blacklist:
            b_body = re.sub(r'^(?:[-*•]|\d+\.)\s+', '', s).strip()
            parts_desc = re.split(r'\s*(?:[:：]|(?:\s+[-–—]\s+))\s*', b_body, maxsplit=1)
            if len(parts_desc) == 2 and parts_desc[1].strip():
                head_clean = re.sub(r'\*\*|`', '', parts_desc[0]).strip()
                desc_part = parts_desc[1].strip()

                m_en_th = re.match(r'^([A-Za-z0-9][A-Za-z0-9\s\'\-\./\(\)]{1,55}?)\s*\(([^()]*(?:\([^()]*\)[^()]*)*[\u0E00-\u0E7F][^()]*(?:\([^()]*\)[^()]*)*)\)$', head_clean)
                if m_en_th:
                    en_p = m_en_th.group(1).strip()
                    th_p = re.sub(r'^(?:อ่านว่า|ทับศัพท์ว่า|แปลว่า|คือ)\s*', '', m_en_th.group(2).strip()).strip(' "\'')
                    add_glossary_pair(en_p, th_p, current_section_tag, desc_part)
                elif re.match(r'^([\u0E00-\u0E7F][^()]{1,50}?)\s*\(([A-Za-z0-9][A-Za-z0-9\s\'\-\./]{1,50})\)$', head_clean):
                    m_th_en = re.match(r'^([\u0E00-\u0E7F][^()]{1,50}?)\s*\(([A-Za-z0-9][A-Za-z0-9\s\'\-\./]{1,50})\)$', head_clean)
                    add_glossary_pair(m_th_en.group(2).strip(), m_th_en.group(1).strip(), current_section_tag, desc_part)
                elif RE_LATIN_CHAR.search(head_clean) and not RE_THAI_CHAR.search(head_clean) and len(head_clean.split()) <= 6:
                    add_candidate_entity(head_clean)
                    m_lead_th = re.match(r'^([\u0E00-\u0E7F][^\s,.;:()]{2,35})(?:\s+|$)', desc_part)
                    if m_lead_th and current_section_tag in ("Faction", "Location", "Person", "Item", "Weapon"):
                        lead_th = m_lead_th.group(1).strip()
                        if not any(lead_th.startswith(w) for w in ("การ", "ความ", "เป็น", "คือ", "มี", "ใช้", "ทำ", "เกิด", "ตั้งอยู่", "อาวุธ", "เทคโนโลยี", "บรรษัท", "องค์กร", "กองกำลัง")):
                            add_glossary_pair(head_clean, lead_th, current_section_tag, desc_part)

            if ":" in s or len(s) > 40:
                inline_candidates.append((s, current_section_tag))

        i += 1

    # Pass 2: Inline narrative mentions e.g. "ของราอูล เมเนนเดซ (Raul Menendez)" or "แดนนี่ ลี (Danny Li)"
    for s, sec_tag in inline_candidates:
        for m_inline in re.finditer(r'([\u0E00-\u0E7F][\u0E00-\u0E7F\.\s]{1,40}?)\s*\(([A-Z][A-Za-z0-9\'\-]+(?:\s+[A-Z][A-Za-z0-9\'\-]+){0,3})\)', s):
            raw_th_chunk = m_inline.group(1).strip()
            en_inline = m_inline.group(2).strip()
            if en_inline.lower() in GENERIC_MULTIWORD_BLACKLIST or en_inline.lower() in seen_en_lower:
                continue
            raw_th_chunk = re.split(r'(?:ของ|โดยสองพี่น้อง|โดย|กับ|และ|หรือปล่อย|หรือ|คือ|ชื่อว่า|ชื่อ|อย่าง|ผู้บังคับการ|ผบ\.)\s*', raw_th_chunk)[-1].strip()
            en_w_count = len(en_inline.split())
            th_words = raw_th_chunk.split()
            clean_th_words = th_words[-min(len(th_words), max(en_w_count, 2)):]
            th_inline = " ".join(w for w in clean_th_words if w and len(w) <= 18).strip(' "\'')
            if th_inline and len(th_inline) >= 2:
                # Do NOT guess 'Person' purely based on 2-word count; preserve section context tag
                inferred_tag = sec_tag if sec_tag and sec_tag in VALID_TAGS else "General"
                add_glossary_pair(en_inline, th_inline, inferred_tag, "สกัดจากเนื้อเรื่อง Lore")

    return glossary_items, candidate_entities

def is_common_generic_english_word(word, tag=None, from_lore=False):
    """
    Returns True if word is a generic common English dictionary word, conversational phrase,
    vocal noise/moan, generic NPC role description (e.g. 'Old Man', 'Dubious Gramps'),
    or structural numbered heading (e.g. 'Quest 1').
    Returns False for genuine game entities, character names (even if first/last names exist in common_english_words.json),
    proper locations, unique items, lore terminology, and hardware models.
    """
    if not word or not isinstance(word, str):
        return True
    w = word.strip()
    if len(w) <= 1:
        return True
    if "\n" in w or "\r" in w or "\t" in w:
        return True
    if w.isdigit() or re.match(r'^[0-9\.,\-/\s#]+$', w):
        return True
    if NUMBERED_STRUCTURAL_PATTERN.match(w):
        return True
    if RE_VOCAL_SOUNDS.match(w):
        return True

    # Engine variable / developer codes / markup tags
    if is_engine_markup_tag(w):
        return True
    w_low = w.lower()
    if w_low in ("ccg", "cg", "bg", "se", "me", "bgm", "ev", "tachie") or w_low.startswith(('alist', 'tmpdb', 'systemfile', 'q0', 'e0', 'f0')):
        return True
    if re.match(r'^[A-Za-z][0-9]{2,}$', w):
        return True
    if w_low in GENERIC_MULTIWORD_BLACKLIST:
        return True

    tokens = w.split()
    if len(tokens) >= 2 and all(tok.lower() == tokens[0].lower() for tok in tokens):
        return True

    tokens_low = [tok.lower().strip(",.!?\"'") for tok in tokens]

    # Erotic / Adult scene phrases (e.g. "Sprite Sex", "Prostitution Sex")
    if any(tok in ("sex", "cum", "cumming", "prostitution", "rape") for tok in tokens_low):
        return True

    # If explicitly tagged as a Person/Location/Faction/Weapon/Item/Quest or extracted from Lore Summary:
    # Do NOT reject character names (e.g., Taylor, Hall, Woods, Mason, John Taylor) or proper items/places
    # just because they appear in the 10,261-word common_english_words.json!
    if from_lore or tag in ("Person", "Location", "Faction", "Weapon", "Item", "Quest"):
        if len(tokens) == 1:
            if w_low in GAME_LOCALIZATION_STOPWORDS or w_low in GENERIC_ROLE_NOUNS:
                return True
            if tag != "Person" and not from_lore and w_low in STRICT_GENERIC_SINGLE_NOUNS:
                return True
            return False
        else:
            if tokens_low[-1] in GENERIC_ROLE_NOUNS and all(tok in GAME_LOCALIZATION_STOPWORDS for tok in tokens_low[:-1]):
                return True
            return False

    common_set = get_common_english_words()

    if len(tokens) == 1:
        # Military / hardware alphanumeric models (e.g. F-15C, Su-35S, M4A1, RPG-7) or ALL-CAPS acronyms (DNI, Wraith, NRC) are NOT generic
        if (re.search(r'[0-9]', w) and re.search(r'[A-Za-z]', w)) or (w.isupper() and 2 <= len(w) <= 6):
            return False

        if w_low in common_set or w_low in GAME_LOCALIZATION_STOPWORDS or w_low in STRICT_GENERIC_SINGLE_NOUNS:
            return True
        if w_low.endswith('s') and (w_low[:-1] in common_set or w_low[:-1] in GAME_LOCALIZATION_STOPWORDS):
            return True
        if w_low.endswith('es') and (w_low[:-2] in common_set or w_low[:-2] in GAME_LOCALIZATION_STOPWORDS):
            return True
        if w_low.endswith('ing') and (w_low[:-3] in common_set or w_low[:-3] in GAME_LOCALIZATION_STOPWORDS):
            return True
        if w_low.endswith('ed') and (w_low[:-2] in common_set or w_low[:-2] in GAME_LOCALIZATION_STOPWORDS):
            return True
        if w_low.endswith('ly') and (w_low[:-2] in common_set or w_low[:-2] in GAME_LOCALIZATION_STOPWORDS):
            return True
        if any(w_low.endswith(rn) and len(w_low) > len(rn) for rn in ("man", "woman", "boy", "girl")):
            return True
        return False
    else:
        # Check if phrase starts with a title prefix followed by a name/entity (e.g. "Captain Price", "Lady Sylvia")
        if tokens_low[0] in TITLE_PREFIXES and len(tokens_low) >= 2 and tokens_low[-1] not in GENERIC_ROLE_NOUNS:
            return False

        # Phrases ending in generic role nouns where ALL preceding tokens are generic
        # e.g. "Hospitalized Gramps", "Dubious Old Man", "Fat Servant", "Horny Old Man"
        if tokens_low[-1] in GENERIC_ROLE_NOUNS:
            if all(tok in common_set or tok in GAME_LOCALIZATION_STOPWORDS for tok in tokens_low[:-1]):
                return True

        # Reject conversational starters (e.g. "Thank You", "Let's Go", "Don't Shoot")
        conversational_head = {
            "i", "you", "we", "they", "he", "she", "it", "this", "that", "there", "here",
            "what", "where", "when", "why", "how", "who", "which", "don't", "dont",
            "please", "thank", "thanks", "hello", "hi", "hey", "let's", "lets"
        }
        if tokens_low[0] in conversational_head:
            return True

        # Check if every single token in the phrase is a common dictionary word
        all_common = all(
            (tok in common_set or tok in GAME_LOCALIZATION_STOPWORDS or
             (tok.endswith('s') and tok[:-1] in common_set) or
             (tok.endswith('es') and tok[:-2] in common_set) or
             (tok.endswith('ing') and tok[:-3] in common_set) or
             (tok.endswith('ed') and tok[:-2] in common_set))
            for tok in tokens_low
        )
        if all_common:
            # Keep if it contains a recognised lore/entity noun OR if it is a 2-3 word Title Case proper noun
            # (such as Character Full Names "John Taylor", "Sarah Hall", or Unique Items/Places "Silent Hill", "Golden Seed", "Supply Drop")
            has_lore_noun = any(tok in LORE_ENTITY_NOUNS for tok in tokens_low)
            is_title_proper_name = (
                2 <= len(tokens) <= 3
                and all(t[0].isupper() for t in tokens if t)
                and not any(tok in GAME_LOCALIZATION_STOPWORDS for tok in tokens_low)
                and tokens_low[-1] not in GENERIC_ROLE_NOUNS
            )
            if not has_lore_noun and not is_title_proper_name:
                return True

        return False

ENGINE_TAG_PREFIXES = {"wait_", "color_", "speed_", "size_", "font_", "align_", "alpha_", "lspace_", "cwait_"}
ENGINE_TAG_NAMES = {
    "wait", "pause", "speed", "size", "color", "font", "align", "alpha", "lspace", "cwait",
    "sprite", "quad", "icon", "ruby", "rb", "rt", "pos", "line-height", "line-indent",
    "margin", "voffset", "nobr", "page", "br", "b", "i", "u", "s", "sub", "sup"
}

def is_engine_markup_tag(tag_str):
    if not tag_str or not isinstance(tag_str, str):
        return False
    t = tag_str.strip().lower()
    if t.startswith(("/", "\\")):
        return True
    t_clean = t.strip("<>[]{}【】〔〕《》『』「」\"' ")
    if not t_clean:
        return True
    if re.match(r'^(?:var|arg|val|param)[0-9]*$', t_clean):
        return True
    if any(t_clean.startswith(p) for p in ENGINE_TAG_PREFIXES):
        return True
    if t_clean in ENGINE_TAG_NAMES:
        return True
    if any(k in t_clean for k in ("skip", "click", "icon", "advance", "nobr", "hidewin", "autonext", "sound", "voice")):
        return True
    parts = re.split(r'[_:=-]', t_clean)
    if any(p in ENGINE_TAG_NAMES for p in parts):
        return True
    return False

def is_legal_or_boilerplate(text_lower):
    if text_lower in GAME_LEGAL_STOPWORDS:
        return True
    for phrase in ["privacy policy", "terms of service", "user agreement", "license agreement", "end user", "all rights reserved"]:
        if phrase in text_lower:
            return True
    return False

def extract_game_entity_candidates(source_texts, existing_terms=None, max_candidates=50, lore_text=""):
    """
    Intelligent Game Entity Discovery Engine:
    Exhaustively scans dialogue, lore, and text corpus to identify high-value game terminology:
    - Structured Lore Summary entities (Main Characters, Proper Locations, Unique Items, Factions)
    - Speaker Prefixes & Vocative Direct-Address Character Names (e.g. 'Taylor:', 'Hey, Hendricks!')
    - Real UI bracketed & tagged terms ([Potion], <Gold>, {Quest_Item}, 【Skill】)
    - Short Quoted Proper Nouns (e.g. 'Alexandria Crest', 'Eye of Agamotto') - strictly excluding spoken dialogue sentences
    - Military models, weapon codes & calibers (M4A1, AK-47, RPG-7, AC-130, 9mm, .50 Cal, etc.)
    - Multi-word Title Case proper nouns (Task Force 141, Captain Price, Shadow Company, John Taylor, Frozen Forest)
    - Game mechanics & domain keyword combinations (Perk, Skill, Attachment, Citadel, Cybercore, etc.)
    - High-frequency mid-sentence proper nouns (Price, Ghost, Soap, Makarov, Taylor, Hendricks) appearing multiple times
    """
    if not source_texts and not lore_text:
        return []

    existing_set = set()
    if existing_terms:
        for t in existing_terms:
            t_str = str(t).strip().lower()
            if t_str:
                existing_set.add(t_str)

    scores = {}
    lore_protected_lower = set()

    # 0. Extract directly from Lore Text if provided
    if lore_text and isinstance(lore_text, str) and lore_text.strip():
        lore_g_items, lore_c_ents = parse_lore_glossary_and_entities(lore_text)
        for g_item in lore_g_items:
            en_val = g_item.get("en", "").strip()
            if en_val and en_val.lower() not in existing_set:
                scores[en_val] = scores.get(en_val, 0) + 25
                lore_protected_lower.add(en_val.lower())
        for c_ent in lore_c_ents:
            if c_ent and c_ent.lower() not in existing_set:
                scores[c_ent] = scores.get(c_ent, 0) + 18
                lore_protected_lower.add(c_ent.lower())

    # Real game UI tags & brackets (Square brackets, Angle brackets, Braces, Japanese brackets)
    re_brackets = re.compile(r'(?:\[|<|\{|\【|\〔|\《|\『|\「)([A-Za-z0-9\s\'\-_/.#]{2,45})(?:\]|>|\}|\】|\〕|\》|\』|\」)')
    # Quoted terms: ONLY 1-3 Title Case capitalized words inside quotes, never entire sentences
    re_quoted_title = re.compile(r'["“\'‘]([A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*){0,3})["”\'’]')
    re_sentence_punct = re.compile(r'[,.?!;:]')
    # Speaker prefix: e.g. "Taylor: Move up!" or "Sarah Hall: Hold your fire!"
    re_speaker_prefix = re.compile(r'^([A-Z][a-zA-Z0-9\'\-]+(?:\s+[A-Z][a-zA-Z0-9\'\-]+){0,2})\s*:\s+\S')
    # Vocative direct address: e.g. "Listen, Taylor!" or "Hey Hendricks,"
    re_vocative = re.compile(r'(?:,\s*|\b(?:Hey|Listen|Wait|Dammit|Damn it|Sorry|Thanks|Captain|Commander|General|Doctor|Lord|Lady|Master|Agent|Sergeant|Lieutenant)\s+)([A-Z][a-z]{2,20})(?=[,!?\.\s]|$)')
    # Parenthetical English proper nouns inside Lore/Notes: e.g. (John Taylor), (The Frozen Forest)
    re_paren_proper = re.compile(r'\(([A-Z][A-Za-z0-9\'\-\.]+(?:\s+[A-Za-z0-9\'\-\.]+){0,4})\)')

    conversational_starters = {
        "i", "you", "we", "they", "he", "she", "it", "this", "that", "there", "here",
        "what", "where", "when", "why", "how", "who", "which",
        "don't", "dont", "do", "did", "does", "is", "are", "was", "were", "be", "been",
        "have", "has", "had", "can", "could", "will", "would", "shall", "should", "may", "might",
        "please", "thank", "thanks", "hello", "hi", "hey", "look", "wait", "listen", "come", "go",
        "get", "kill", "attack", "take", "no", "yes", "oh", "ah", "let's", "lets", "good", "well"
    }

    # Military Hardware: Alphanumeric models (F-15C, Su-35S), Weapon IDs (M4A1, MP5, RPG-7), Calibers (9mm, .50 Cal)
    re_military = re.compile(
        r'(?:\b|\.)(?:'
        r'[A-Za-z]{1,6}-[0-9]{1,4}[A-Za-z0-9]*|'
        r'[A-Z]{1,4}[0-9]{1,4}[A-Z0-9]*|'
        r'[0-9]{1,3}(?:\.[0-9]{1,3})?\s*(?:mm|Cal|Gauge)'
        r')\b'
    )
    re_titlecase = re.compile(r'\b[A-Z][a-zA-Z0-9]+(?:\s+(?:[A-Z][a-zA-Z0-9]+|[0-9]{1,4}(?:-[0-9]{1,4})?)){1,3}\b')
    re_mid_cap = re.compile(r'(?<=[a-z0-9,;!?]\s)\b([A-Z][a-z]{2,})\b')

    game_keywords = {
        "perk", "skill", "spell", "artifact", "relic", "rune", "potion", "shield", "armor", "rifle",
        "pistol", "launcher", "grenade", "turret", "drone", "mine", "strike", "ammo", "loadout",
        "blueprint", "attachment", "optic", "muzzle", "barrel", "grip", "stock", "laser", "magazine",
        "camo", "rank", "level", "class", "faction", "guild", "clan", "legion", "citadel", "outpost",
        "bunker", "sector", "zone", "dungeon", "vault", "shrine", "temple", "boss", "squad", "unit",
        "regiment", "division", "battalion", "corps", "fleet", "vanguard", "sentinel", "guardian",
        "cybercore", "interface", "protocol", "accord", "pact", "coalition", "corporation", "forest",
        "station", "safehouse"
    }

    for text in (source_texts or []):
        if not text or not isinstance(text, str):
            continue
        text_str = text.strip()
        if not text_str:
            continue

        # 0A. Speaker Prefix Detection (Character Names)
        m_spk = re_speaker_prefix.match(text_str)
        if m_spk:
            spk_c = m_spk.group(1).strip()
            spk_low = spk_c.lower()
            if len(spk_c) > 2 and spk_low not in GAME_LOCALIZATION_STOPWORDS and not is_common_generic_english_word(spk_c, tag="Person") and spk_low not in existing_set:
                scores[spk_c] = scores.get(spk_c, 0) + 8
                lore_protected_lower.add(spk_low)

        # 0B. Vocative Direct Address Detection (Character Names in Dialogue)
        for m_voc in re_vocative.findall(text_str):
            voc_c = m_voc.strip()
            voc_low = voc_c.lower()
            if len(voc_c) > 2 and voc_low not in conversational_starters and voc_low not in GAME_LOCALIZATION_STOPWORDS and not is_common_generic_english_word(voc_c, tag="Person") and voc_low not in existing_set:
                scores[voc_c] = scores.get(voc_c, 0) + 4
                lore_protected_lower.add(voc_low)

        # 0C. Parenthetical English Proper Nouns (from Lore / Codex lines)
        if RE_THAI_CHAR.search(text_str):
            for m_p in re_paren_proper.findall(text_str):
                p_c = m_p.strip()
                p_low = p_c.lower()
                if len(p_c) > 2 and not is_common_generic_english_word(p_c, from_lore=True) and p_low not in existing_set:
                    scores[p_c] = scores.get(p_c, 0) + 10
                    lore_protected_lower.add(p_low)

        # 1. Bracketed UI terms ([Item], <Var>, 【Skill】)
        for m in re_brackets.findall(text_str):
            m_c = m.strip()
            if len(m_c) <= 2 or re_sentence_punct.search(m_c) or is_engine_markup_tag(m_c):
                continue
            words = m_c.split()
            if len(words) > 4 or words[0].lower() in conversational_starters:
                continue
            m_low = m_c.lower()
            if not is_common_generic_english_word(m_c) and not is_legal_or_boilerplate(m_low) and m_low not in existing_set:
                scores[m_c] = scores.get(m_c, 0) + 5

        # 2. Quoted Proper Nouns (Title Case only, strictly excluding conversational dialogue)
        for m in re_quoted_title.findall(text_str):
            m_c = m.strip()
            if len(m_c) <= 2 or re_sentence_punct.search(m_c) or is_engine_markup_tag(m_c):
                continue
            words = m_c.split()
            if len(words) > 3 or words[0].lower() in conversational_starters:
                continue
            m_low = m_c.lower()
            if not is_common_generic_english_word(m_c) and not is_legal_or_boilerplate(m_low) and m_low not in existing_set:
                scores[m_c] = scores.get(m_c, 0) + 3

        # 3. Military Hardware, Firearms & Alphanumerics
        for m in re_military.findall(text_str):
            m_c = m.strip().lstrip(".")
            if len(m_c) < 3 or (len(m_c) == 2 and m_c[0].isalpha() and m_c[1].isdigit()):
                continue
            m_low = m_c.lower()
            if not is_common_generic_english_word(m_c) and not is_legal_or_boilerplate(m_low) and m_low not in existing_set:
                scores[m_c] = scores.get(m_c, 0) + 4

        # 4. Multi-word Title Case Proper Nouns
        for m in re_titlecase.findall(text_str):
            m_c = m.strip()
            words = m_c.split()
            if words[0].lower() in GAME_LOCALIZATION_STOPWORDS and len(words) > 1 and words[0].lower() != "the":
                m_c = " ".join(words[1:])
            m_low = m_c.lower()
            if len(m_c) > 3 and not is_common_generic_english_word(m_c) and not is_legal_or_boilerplate(m_low) and m_low not in existing_set:
                bonus = 3 if any(kw in m_low.split() for kw in game_keywords) else 0
                scores[m_c] = scores.get(m_c, 0) + 3 + bonus

        # 5. Mid-sentence capitalized proper nouns (Price, Soap, Ghost, Makarov, Alexandria, etc.)
        for m in re_mid_cap.findall(text_str):
            m_c = m.strip()
            m_low = m_c.lower()
            is_prot = m_low in lore_protected_lower
            if not is_prot and is_common_generic_english_word(m_c):
                continue
            if len(m_c) > 2 and m_low not in GAME_LOCALIZATION_STOPWORDS and not is_legal_or_boilerplate(m_low) and m_low not in TITLE_PREFIXES and m_low not in existing_set:
                scores[m_c] = scores.get(m_c, 0) + 2

    # High-Yield Qualification Filter:
    qualified = []
    for term, score in scores.items():
        t_low = term.lower()
        if " " not in term:
            if score >= 4 or t_low in game_keywords or t_low in lore_protected_lower:
                qualified.append((term, score))
        else:
            if score >= 3 or t_low in lore_protected_lower:
                qualified.append((term, score))

    # Collect all tokens from multi-word compounds
    all_multi_tokens = set()
    for item in qualified:
        if " " in item[0]:
            for token in item[0].lower().split():
                all_multi_tokens.add(token)

    pruned = []
    for term, score in qualified:
        t_low = term.lower()
        is_prot = t_low in lore_protected_lower
        if not is_prot and is_common_generic_english_word(term):
            continue
        if " " not in term:
            # Only prune a single-word token if it is NOT lore-protected AND has a weak score (< 4)
            # Never delete frequent character surnames/callsigns (e.g. 'Taylor', 'Hendricks', 'Price') just because 'John Taylor' or 'Captain Price' exists!
            if t_low in all_multi_tokens and not is_prot and score < 4:
                continue
        pruned.append((term, score))

    # Sort by score descending
    sorted_candidates = sorted(pruned, key=lambda x: x[1], reverse=True)
    return [term for term, score in sorted_candidates[:max_candidates]]

IGNORED_FOLDER_NAMES = {
    "mod_workspace", "workspace", "workspaces", "modder_project", "project", "projects",
    "games", "translation", "localization", "data", "text", "content", "assets", "raw",
    "src", "target", "default", "tool", "tools", "release", "scratch", "scripts",
    "01_original", "02_translation_workspace", "03_staging", "04_packed_mod", "05_scripts_and_tools"
}

def detect_game_universe_tone(title="", sample_texts=None, file_path="", project_dir=""):
    """
    Two-Stage Game Universe & Tone Detection Engine:
    Stage 1: Primary Discovery and Check from Project Name & Game Title (from thub_project.json, folders, title, profile)
    Stage 2: Secondary Corroboration from Dialogue & Text Corpus
    Stage 3: Synthesis & Structured Conclusion
    """
    candidates = []
    seen = set()

    def add_candidate(raw, source, priority):
        if not raw or not str(raw).strip():
            return
        s_clean = str(raw).strip()
        norm = re.sub(r'[\_\-\+\.\~]+', ' ', s_clean)
        norm = re.sub(r'\s+', ' ', norm).strip().lower()
        if not norm or norm in ("default", "none"):
            return
        norm_slug = norm.replace(" ", "_")
        if norm_slug in IGNORED_FOLDER_NAMES or norm in IGNORED_FOLDER_NAMES:
            return

        norm_no_mod = re.sub(r'\b(workspace|mod|th|thai|en|english|translation|patch|demo)\b', '', norm).strip()
        norm_no_mod = re.sub(r'\s+', ' ', norm_no_mod).strip()

        key = norm
        if key and key not in seen:
            seen.add(key)
            candidates.append({
                "norm": norm,
                "norm_no_mod": norm_no_mod,
                "raw": s_clean,
                "source": source,
                "priority": priority
            })

    # Discover paths from project_dir, file_path, and TStudioCore
    paths_to_check = []
    if project_dir and os.path.exists(project_dir):
        paths_to_check.append(project_dir if os.path.isdir(project_dir) else os.path.dirname(project_dir))
    
    # Check TStudioCore active project path
    core_proj = TStudioCore.get_project_path()
    if core_proj and os.path.exists(core_proj) and core_proj not in paths_to_check:
        paths_to_check.append(core_proj)

    if file_path:
        norm_fp = os.path.normpath(file_path).replace('\\', '/')
        parts = norm_fp.split('/')
        for part in reversed(parts):
            p_lower = part.lower().strip()
            if part and not p_lower.endswith(('.csv', '.json', '.txt', '.tsv', '.xlsx')):
                p_slug = p_lower.replace(" ", "_")
                if p_slug not in IGNORED_FOLDER_NAMES and p_lower not in IGNORED_FOLDER_NAMES:
                    add_candidate(part, f"โฟลเดอร์ไฟล์ ({part})", 80)
                    break

        if os.path.exists(file_path):
            cur = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
            for _ in range(3):
                if cur and cur not in paths_to_check:
                    base_c = os.path.basename(os.path.normpath(cur)).lower()
                    if base_c not in IGNORED_FOLDER_NAMES:
                        paths_to_check.append(cur)
                parent = os.path.dirname(cur)
                if parent == cur:
                    break
                cur = parent

    for p in paths_to_check:
        meta_file = os.path.join(p, "thub_project.json")
        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                p_name = meta.get("project_name", "")
                if p_name:
                    add_candidate(p_name, "thub_project.json (Project Name)", 100)
                g_path = meta.get("game_path", "")
                if g_path:
                    g_base = os.path.basename(os.path.normpath(g_path))
                    add_candidate(g_base, "thub_project.json (Game Path)", 95)
            except Exception:
                pass
        folder_base = os.path.basename(os.path.normpath(p))
        if folder_base:
            fb_lower = folder_base.lower()
            if fb_lower not in IGNORED_FOLDER_NAMES and fb_lower.replace(" ", "_") not in IGNORED_FOLDER_NAMES:
                add_candidate(folder_base, f"โฟลเดอร์โปรเจกต์ ({folder_base})", 85)

    if title and title.lower() not in ("default", "none", ""):
        add_candidate(title, f"ชื่อที่ระบุ ({title})", 90)

    candidates.sort(key=lambda x: x["priority"], reverse=True)

    # Collect stratified samples
    samples = collect_stratified_dialogue_samples(sample_texts, max_samples=100)
    sample_buf = " ".join([str(s).lower() for s in samples[:150]])

    # ─────────────────────────────────────────────────────────────
    # STAGE 1: Check from Project Name & Game Title FIRST (Strict Word Boundary)
    # ─────────────────────────────────────────────────────────────
    stage1_best = None
    stage1_max_score = 0
    stage1_candidate = None
    stage1_kw = ""

    for cand in candidates:
        name_targets = [cand["norm"]]
        if cand["norm_no_mod"] and cand["norm_no_mod"] != cand["norm"]:
            name_targets.append(cand["norm_no_mod"])
        for rule in TONE_DETECTION_RULES:
            for kw in rule["keywords"]:
                kw_lower = kw.lower()
                for target in name_targets:
                    matched = False
                    if len(kw_lower) >= 2:
                        if re.search(r'\b' + re.escape(kw_lower) + r'\b', target) or target == kw_lower:
                            matched = True
                    if matched:
                        score = cand["priority"] + len(kw_lower) * 2
                        if score > stage1_max_score:
                            stage1_max_score = score
                            stage1_best = rule
                            stage1_candidate = cand
                            stage1_kw = kw

    # ─────────────────────────────────────────────────────────────
    # STAGE 2: Corroboration / Fallback from Dialogue Samples (Word Boundary)
    # ─────────────────────────────────────────────────────────────
    dialogue_hits = []
    stage2_best = None
    stage2_max_score = 0

    for rule in TONE_DETECTION_RULES:
        d_score = 0
        rule_hits = []
        if sample_buf:
            for kw in rule["keywords"]:
                kw_lower = kw.lower()
                matches = re.findall(r'\b' + re.escape(kw_lower) + r'\b', sample_buf)
                occ = min(len(matches), 5)
                if occ > 0:
                    if len(kw_lower) <= 3 and occ < 2:
                        continue
                    d_score += occ * 4
                    rule_hits.append(f"'{kw}' x{occ}")
        if d_score > stage2_max_score:
            stage2_max_score = d_score
            stage2_best = rule
            dialogue_hits = rule_hits

    # ─────────────────────────────────────────────────────────────
    # STAGE 3: Conclusion & Synthesis
    # ─────────────────────────────────────────────────────────────
    if stage1_best:
        chosen_rule = stage1_best
        inspected_name = stage1_candidate["raw"]
        source_desc = stage1_candidate["source"]
        
        corrob_str = ""
        confidence = "มั่นใจสูงมาก (99% จากชื่อเกมและโปรเจกต์)"
        if stage2_best and stage2_best["tone"] == stage1_best["tone"] and dialogue_hits:
            corrob_str = f" พร้อมบทสนทนายืนยัน ({', '.join(dialogue_hits[:3])})"
            confidence = "มั่นใจสูงสุด (100% ชื่อเกมและบทสนทนาตรงกัน)"

        evidence = f"ตรวจพบชื่อแฟรนไชส์ '{stage1_kw}' ใน {source_desc} ('{inspected_name}'){corrob_str}"
        summary_conclusion = (
            f"🎮 ชื่อเกม/โปรเจกต์ที่ตรวจสอบ: '{inspected_name}' ({source_desc})\n"
            f"✅ สรุปโทนจักรวาล: {chosen_rule['tone']}\n"
            f"👥 สรุปสรรพนาม: {chosen_rule['pronoun']}\n"
            f"📊 ระดับความเชื่อมั่น: {confidence}\n"
            f"💡 หลักฐาน: {evidence}"
        )
        res = {
            "category": chosen_rule["category"],
            "tone": chosen_rule["tone"],
            "pronoun": chosen_rule["pronoun"],
            "label": chosen_rule["label"],
            "inspected_name": inspected_name,
            "detected_from": source_desc,
            "matched_keyword": stage1_kw,
            "confidence": confidence,
            "stage": "project_name",
            "score": stage1_max_score + stage2_max_score,
            "reason": evidence,
            "summary_conclusion": summary_conclusion,
            "is_confident": True
        }
        return enrich_result_with_ac_if_applicable(res, candidates, title, sample_buf)
    elif stage2_best and stage2_max_score >= 8:
        chosen_rule = stage2_best
        inspected_name = candidates[0]["raw"] if candidates else (title or "ไม่ระบุชื่อ")
        confidence = "มั่นใจปานกลาง (ตรวจวิเคราะห์จากเนื้อหาและบทสนทนาในเกม)"
        evidence = f"ตรวจพบคีย์เวิร์ดในบทสนทนาเกม: {', '.join(dialogue_hits[:4])}"
        summary_conclusion = (
            f"🎮 ชื่อโปรเจกต์: '{inspected_name}' (ชื่อทั่วไป)\n"
            f"✅ สรุปโทนจักรวาล: {chosen_rule['tone']}\n"
            f"👥 สรุปสรรพนาม: {chosen_rule['pronoun']}\n"
            f"📊 ระดับความเชื่อมั่น: {confidence}\n"
            f"💡 หลักฐาน: {evidence}"
        )
        res = {
            "category": chosen_rule["category"],
            "tone": chosen_rule["tone"],
            "pronoun": chosen_rule["pronoun"],
            "label": chosen_rule["label"],
            "inspected_name": inspected_name,
            "detected_from": "บทสนทนาในเกม (Dialogue Analysis)",
            "matched_keyword": dialogue_hits[0] if dialogue_hits else "",
            "confidence": confidence,
            "stage": "dialogue",
            "score": stage2_max_score,
            "reason": evidence,
            "summary_conclusion": summary_conclusion,
            "is_confident": True
        }
        return enrich_result_with_ac_if_applicable(res, candidates, title, sample_buf)
    else:
        inspected_name = candidates[0]["raw"] if candidates else (title or "ไม่ระบุชื่อ")
        res = {
            "category": "🎭 เสียดสี ตลกร้าย ปรัชญา และทั่วไป (Comedy, Satire & General)",
            "tone": "General / ทั่วไป มาตรฐานสากล (Universal Default)",
            "pronoun": "👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)",
            "label": "General / ทั่วไป มาตรฐานสากล",
            "inspected_name": inspected_name,
            "detected_from": "ค่าเริ่มต้นสากล",
            "matched_keyword": "",
            "confidence": "ค่ากลางมาตรฐาน",
            "stage": "default",
            "score": 0,
            "reason": "ไม่พบชื่อแฟรนไชส์เฉพาะเจาะจง จึงใช้ค่ากลางมาตรฐานสากล",
            "summary_conclusion": (
                f"🎮 ชื่อเกม/โปรเจกต์: '{inspected_name}'\n"
                f"✅ สรุปโทนจักรวาล: General / ทั่วไป มาตรฐานสากล\n"
                f"👥 สรุปสรรพนาม: 👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)"
            ),
            "is_confident": False
        }
        return enrich_result_with_ac_if_applicable(res, candidates, title, sample_buf)

def enrich_result_with_ac_if_applicable(res, candidates=None, title="", sample_buf=""):
    """
    Enriches tone detection result with specific Assassin's Creed installment,
    era, setting, and character demeanor (ริยาบท) if the game belongs to the franchise.
    """
    names = [c["norm"] for c in candidates] if candidates else []
    if title:
        names.append(title.lower())
    if res.get("inspected_name"):
        names.append(str(res.get("inspected_name")).lower())
    names_str = " ".join(names)
    ac_meta = resolve_assassins_creed_installment(names_str, sample_buf)
    if ac_meta and ac_meta.get("is_ac"):
        res["ac_info"] = ac_meta
        res["era"] = ac_meta["era"]
        res["demeanor"] = ac_meta["demeanor"]
        res["protagonist"] = ac_meta["protagonist"]

        # Align category/tone/pronoun if not already installment-specific
        if ("Crusades" not in res["tone"] and "Renaissance" not in res["tone"] and
            "American Revolution" not in res["tone"] and "French Revolution" not in res["tone"] and
            "Victorian" not in res["tone"] and "Egyptian" not in res["tone"] and
            "Baghdad" not in res["tone"] and "Odyssey" not in res["tone"] and
            "Valhalla" not in res["tone"] and "Black Flag" not in res["tone"] and
            "Shadows" not in res["tone"]):
            res["category"] = ac_meta["category"]
            res["tone"] = ac_meta["tone"]
            res["pronoun"] = ac_meta["pronoun"]
            res["label"] = ac_meta["title"]
        else:
            if "สากล" in res["pronoun"] or "แฟนตาซียุคกลาง" in res["pronoun"]:
                res["pronoun"] = ac_meta["pronoun"]

        inspected_name = res.get("inspected_name") or title or ac_meta["title"]
        source_desc = res.get("detected_from") or "Assassin's Creed Engine"
        conf = res.get("confidence", "มั่นใจสูง")
        res["summary_conclusion"] = (
            f"🎮 ชื่อเกม/โปรเจกต์: '{inspected_name}' ({source_desc})\n"
            f"🦅 แฟรนไชส์: Assassin's Creed — {ac_meta['title']}\n"
            f"⏳ ยุคสมัยและฉากหลัง: {ac_meta['era']} (ตัวละครหลัก: {ac_meta['protagonist']})\n"
            f"🎭 ริยาบทและบุคลิกตัวละคร: {ac_meta['demeanor']}\n"
            f"✅ สรุปโทนจักรวาล: {res['tone']}\n"
            f"👥 สรุปสรรพนาม: {res['pronoun']}\n"
            f"🛡️ มิติเวลา 2 ชั้น: อดีตใน Animus (ข้า-เจ้า / สหาย / ห้ามครับ-ค่ะ) ⚡ ปัจจุบัน (ผม/ฉัน-คุณ)\n"
            f"📊 ระดับความเชื่อมั่น: {conf}\n"
            f"💡 หลักฐาน: {res.get('reason', '')} | ตรวจพบภาค: {ac_meta['title']}"
        )
    return res

def detect_game_universe_tone_with_api(title="", sample_texts=None, file_path="", project_dir="", cfg=None):
    """
    API-Assisted Two-Stage Game Universe & Tone Detection Engine:
    1. Runs enhanced heuristic detection first (with specialized AC installment & demeanor resolver).
    2. If an API key is available (OpenAI, DeepSeek, Google, Claude, or Local LLM),
       queries the model with representative dialogue lines and candidate clues.
    3. Guarantees 0% false positive Warhammer 40k on Anime/JRPG games.
    4. Accurately identifies Assassin's Creed installments and character demeanors.
    5. Seamlessly falls back to heuristic engine if API is not configured or times out.
    """
    heuristic_res = detect_game_universe_tone(title, sample_texts, file_path, project_dir)
    
    if cfg is None:
        try:
            cfg = TStudioCore.load_config()
        except Exception:
            cfg = {}

    has_api = bool(
        cfg.get("openai_key") or cfg.get("deepseek_key") or cfg.get("google_key") or
        cfg.get("anthropic_key") or cfg.get("openrouter_key") or cfg.get("api_key") or
        (cfg.get("provider") == "Local LLM") or (cfg.get("model") == "custom-local-llm")
    )
    if not has_api:
        return heuristic_res

    clean_samples = collect_stratified_dialogue_samples(sample_texts, max_samples=15)
    sample_block = "\n".join([f"- {s[:160]}" for s in clean_samples[:10]]) if clean_samples else "(No dialogue lines provided)"

    detected_name = heuristic_res.get("inspected_name") or title or "Video Game"

    cat_list_str = "\n".join([f"- {cat}:\n  " + "\n  ".join(tones[:3]) for cat, tones in UNIVERSE_TONES_BY_CATEGORY.items()])

    prompt = (
        f"You are a Master Video Game Localization & Narrative Specialist.\n"
        f"Analyze this game project and determine its exact universe category, tone, and appropriate Thai pronoun system:\n\n"
        f"Game Title / Folder: '{detected_name}'\n"
        f"Heuristic Suggestion: {heuristic_res.get('tone')}\n\n"
        f"Sample Dialogue Excerpts from Game Files:\n"
        f"{sample_block}\n\n"
        f"CRITICAL DISAMBIGUATION RULES:\n"
        f"1. NEVER classify a game as 'Warhammer 40,000 / Grimdark Sci-Fi' unless it explicitly belongs to the Warhammer 40k franchise (Space Marines, Astartes, Imperium of Man, Bolter, Adeptus Mechanicus).\n"
        f"2. If the game features anime art style, JRPG mechanics, school life, cute/isekai fantasy, swords & magic, or Asian aesthetics (e.g. Senran Kagura, Lost Epic, Atelier, Persona, Genshin, Witch's Apocalyptic Journey), you MUST choose category '🌸 อนิเมะ JRPG และแฟนตาซีเอเชีย (Anime & Asian Fantasy)' or '🏰 แฟนตาซี ย้อนยุค และประวัติศาสตร์ (Fantasy & Historical)'.\n"
        f"3. If the game belongs to the 'Assassin's Creed' franchise, you MUST identify the exact installment (e.g. AC 1, AC 2/Brotherhood/Revelations, AC 3/Rogue, AC IV Black Flag, Unity, Syndicate, Origins, Odyssey, Valhalla, Mirage, Shadows) and its historical era, matching the appropriate tone and character demeanor (ริยาบท).\n\n"
        f"Allowed Categories & Tone Presets:\n{cat_list_str}\n\n"
        f"Allowed Pronoun Presets:\n"
        f"- 🦅 ภาคีมือสังหาร / อิงประวัติศาสตร์ (ข้า - เจ้า / สหาย / ข้า - ท่าน)\n"
        f"- 👔 สากล / ยุคปัจจุบัน / มาตรฐาน (ผม / ฉัน - คุณ)\n"
        f"- 🔥 สตรีท / นอกกฎหมาย / ปากจัด (กู - มึง / ฉัน - แก / ไอ้เวร)\n"
        f"- 🏰 แฟนตาซียุคกลาง / อัศวิน / เวทมนตร์ (ข้า - เจ้า / ข้า - ท่าน / ท่านลอร์ด)\n"
        f"- 🏯 ญี่ปุ่นยุคซามูไร / นินจา (ข้า - เจ้า / นายท่าน / ท่านหญิง)\n"
        f"- ⚔️ จีนกำลังภายใน / ยุทธภพ (ข้า - เจ้า / จอมยุทธ / แม่นาง / ศิษย์พี่)\n"
        f"- 🪖 ทหารยุทธวิธี / สายลุย / ตำรวจ (ผม/ฉัน - นาย/พวกนาย/ผู้หมวด)\n"
        f"- 🌌 มหากาพย์อวกาศ / Star Wars / แฟนตาซี (ข้า - เจ้า / ข้า - ท่าน)\n\n"
        f"Respond ONLY in valid JSON format matching this schema:\n"
        f"{{\n"
        f'  "category": "<Exact category from the list>",\n'
        f'  "tone": "<Exact tone from the list>",\n'
        f'  "pronoun": "<Exact pronoun preset from the list>",\n'
        f'  "reason": "<Brief explanation in Thai of why this tone and pronoun were selected>"\n'
        f"}}"
    )

    try:
        is_local = (cfg.get("provider") == "Local LLM" or cfg.get("model") == "custom-local-llm")
        fast_cfg = dict(cfg)
        fast_cfg["timeout"] = 12
        fast_cfg["max_tokens"] = 512
        raw_res = CoreAI.generate_content(fast_cfg, prompt, is_local=is_local)
        
        clean_res = re.sub(r'<think>.*?</think>', '', raw_res, flags=re.DOTALL).strip()
        m = re.search(r'\{[\s\S]*\}', clean_res)
        if m:
            ai_data = json.loads(m.group(0))
            ai_cat = ai_data.get("category", "").strip()
            ai_tone = ai_data.get("tone", "").strip()
            ai_pronoun = ai_data.get("pronoun", "").strip()
            ai_reason = ai_data.get("reason", "").strip()

            matched_rule = None
            for rule in TONE_DETECTION_RULES:
                if rule["tone"] == ai_tone or (ai_cat and rule["category"] == ai_cat and ai_tone in rule["tone"]):
                    matched_rule = rule
                    break

            if matched_rule:
                confidence = "มั่นใจสูงสุด (ตรวจวิเคราะห์ด้วย AI ร่วมกับชื่อเกมและบทสนทนา)"
                summary_conclusion = (
                    f"🎮 ชื่อเกม/โปรเจกต์: '{detected_name}'\n"
                    f"🤖 ผลวิเคราะห์ AI: {matched_rule['tone']}\n"
                    f"📂 หมวดหมู่: {matched_rule['category']}\n"
                    f"👥 สรุปสรรพนาม: {ai_pronoun or matched_rule['pronoun']}\n"
                    f"📊 ระดับความเชื่อมั่น: {confidence}\n"
                    f"💡 เหตุผล AI: {ai_reason}"
                )
                ai_res = {
                    "category": matched_rule["category"],
                    "tone": matched_rule["tone"],
                    "pronoun": ai_pronoun or matched_rule["pronoun"],
                    "label": matched_rule["label"],
                    "inspected_name": detected_name,
                    "detected_from": f"AI ตรวจวิเคราะห์ ({cfg.get('model', 'LLM')})",
                    "matched_keyword": "AI Verification",
                    "confidence": confidence,
                    "stage": "ai_api",
                    "score": 250,
                    "reason": f"AI ตรวจวิเคราะห์: {ai_reason}",
                    "summary_conclusion": summary_conclusion,
                    "is_confident": True,
                    "ai_verified": True
                }
                return enrich_result_with_ac_if_applicable(ai_res, [], detected_name, sample_block)
    except Exception as e:
        print(f"[detect_game_universe_tone_with_api] API verification fallback: {e}")

    return heuristic_res

def apply_easy_mode(profile_data, title="", sample_texts=None, file_path="", project_dir="", use_api=True):
    """
    One-Click Easy Mode:
    1. Analyzes Project Name and Game Title FIRST, with API assistance if available.
    2. Detects the best Category, Universe Tone, and Pronouns.
    3. Enables 100% Strict Gender Certainty.
    4. Sets Hybrid Translation philosophy.
    5. Compiles Single, Options, and Batch Prompts directly into the profile.
    Returns: (updated_profile_data, detection_result)
    """
    if use_api:
        res = detect_game_universe_tone_with_api(title, sample_texts, file_path, project_dir)
    else:
        res = detect_game_universe_tone(title, sample_texts, file_path, project_dir)
    
    if "tlm" not in profile_data or not isinstance(profile_data["tlm"], dict):
        profile_data["tlm"] = {}
        
    tlm = profile_data["tlm"]
    tlm["tone_category"] = res["category"]
    tlm["universe_tone"] = res["tone"]
    tlm["pronoun_preset"] = res["pronoun"]
    tlm["strict_gender"] = True

    tone_lower = res["tone"].lower()
    title_lower = title.lower()
    is_cinematic_auto = any(k in tone_lower or k in title_lower for k in [
        "wolfenstein", "dishonored", "dieselpunk", "warfare", "tactical", "shooter", "steampunk", "cyberpunk"
    ])
    if is_cinematic_auto:
        tlm["trans_philosophy"] = "🎬 พากย์ไทยภาพยนตร์ & ขจัดสำนวนฝรั่ง (Cinematic War Dub - ไม่แปลตรงตัว แปลเอาอารมณ์ ภาษาพูดธรรมชาติ)"
    else:
        tlm["trans_philosophy"] = "ทับศัพท์ผสมแปลไทย (Hybrid - ชื่อเฉพาะทับศัพท์ คำขยายแปลไทยสละสลวย)"
    
    # Pronoun & Gender Certainty directives
    p_name = res["pronoun"]
    preset = PRONOUN_PRESETS.get(p_name, {})
    p_rules = preset.get("rules", "")
    p_neutral = preset.get("neutral", "คุณ / เจ้า / ท่าน")
    
    pronoun_section = (
        f"\n### PRONOUN & CHARACTER ADDRESSING MATRIX:\n"
        f"- Pronoun Style: {p_name}\n"
        f"{p_rules}\n"
        f"- STRICT GENDER CERTAINTY (NON-NEGOTIABLE):\n"
        f"  1. ONLY use gender-specific pronouns/particles (ผม, ฉัน, ดิฉัน, ครับ, ค่ะ, นาย, เธอ, หล่อน, แม่นาง) "
        f"when 100% CERTAIN of character gender from Context ID (e.g. '_female', '_male', 'queen_', 'caroline', 'anya', 'engel'), explicit source clues ('she said', 'madam', 'sir'), or established lore.\n"
        f"  2. IF UNCERTAIN OR AMBIGUOUS: NEVER guess or gamble on gender! MUST use neutral pronouns ({p_neutral}) or naturally omit the subject, and NEVER gamble on polite gender particles ('ครับ' vs 'ค่ะ').\n"
        f"  3. FEMALE OPERATOR / CHARACTER RULE: When a female character (identified via Context ID, female name e.g. Caroline, Anya, Frau Engel, Sarah, Jill, or context) speaks in first person, NEVER use 'ผม' or 'ครับ'! Use 'ฉัน' (peers/informal) or 'ดิฉัน' (formal report), or naturally drop the subject.\n"
        f"  4. SUBJECT DROPPING IN COMBAT/ACTION: In tactical commands or reports, drop pronouns naturally (e.g. 'รับทราบ', 'เห็นเป้าหมายแล้ว', 'กำลังเข้าเคลียร์') instead of forcing 'ผม/ฉัน'.\n"
    )

    lore = (tlm.get("lore_notes") or tlm.get("lore") or "").strip()
    custom_rules = tlm.get("custom_rules", "").strip()
    lore_section = f"\n### GAME LORE & SETTING:\n{lore}\n" if lore else ""
    rules_section = f"\n### IRONCLAD PROJECT & VARIABLE RULES:\n{custom_rules}\n" if custom_rules else ""
    
    game_name = res.get("inspected_name") or (title if title and title.lower() != "default" else "Game")
    tone = res["tone"]
    philosophy = tlm["trans_philosophy"]

    anti_literal_section = ""
    if is_cinematic_auto or "Cinematic" in philosophy or "ไม่แปลตรงตัว" in philosophy:
        anti_literal_section = (
            "\n### ANTI-LITERAL & CINEMATIC ACTION-DUB DIRECTIVES (CRITICAL):\n"
            "1. BAN WORD-FOR-WORD TRANSLATION & RIGID TRANSLATIONESE:\n"
            "   - NEVER translate English idioms or slangs literally word-for-word.\n"
            "   - 'I'll be damned if...' ➔ 'ไม่มีทางยอมให้... / ฝันไปเถอะว่าฉันจะ...' (ห้ามแปล 'ฉันจะถูกสาปถ้า...')\n"
            "   - 'at our doorstep' ➔ 'บุกมาถึงหน้าบ้านเรา / จ่อคอหอยเราอยู่' (ห้ามแปล 'อยู่ที่ธรณีประตู')\n"
            "   - 'go to hell and back to kick them out' ➔ 'บุกน้ำลุยไฟพลิกแผ่นดินเพื่อไล่ตะเพิดพวกมัน' (ห้ามแปล 'ไปนรกและกลับมาเพื่อเตะ...')\n"
            "   - 'on their knees' ➔ 'ยอมสยบ / คลานเข่าเข้ามาขอร้อง / จนตรอก' (ห้ามแปล 'คุกเข่าอยู่')\n"
            "   - 'Jerry / Kraut' ➔ 'พวกนาซี / พวกเยอรมัน / พวกไอ้กบฏ' (ห้ามแปล 'เจอร์รี่')\n"
            "   - 'bite the bullet' ➔ 'กัดฟันสู้ / จำใจกลืนเลือด' (ห้ามแปล 'กัดกระสุน')\n"
            "2. NATURAL SPOKEN THAI SYNTAX & COMBAT TONE:\n"
            "   - Eliminate rigid passive voice: ห้ามใช้ 'ถูกบังคับให้ถอยหลัง', ให้ใช้ 'ต้องล่าถอย' (ในภาษาไทย 'ถูก' ใช้กับเคราะห์ร้ายเท่านั้น และห้ามใช้โครงสร้าง 'ได้รับการ/ทำการ/มีการ')\n"
            "   - Dialogue must flow like a blockbuster movie Thai dub (พันธมิตร/ทีมพากย์ฮอลลีวูดมืออาชีพ): ใช้ภาษาพูดที่มีพลัง ดุดัน สมจริงตามสถานการณ์สงคราม\n"
            "   - Profanity & Combat Exclamations (Damn, Bastard, Hell, Shit, Fuck): ถ่ายทอดอารมณ์ด่าและสบถตามสถานการณ์เดือด (เช่น 'เวรเอ๊ย', 'ไอ้ระยำ', 'สารเลว', 'บัดซบ') ห้ามแปลสุภาพจนเสียอรรถรส\n"
            "3. WEAPONS & TACTICAL VEHICLES EXCEPTION:\n"
            "   - Keep firearm models (MP40, STG44, Flak 88, Luger, Panzerhund, RPG, SMG, AR), calibers, and vehicles in original Latin/alphanumeric script.\n"
            "4. KEYBOARD KEYS, MOUSE & CONTROLLER INPUTS EXCEPTION:\n"
            "   - Keep PC keyboard keys and controls in original Latin script (e.g. 'Spacebar'/'Space' NEVER 'สเปคบรา'/'เว้นวรรค', 'Enter' NEVER 'เอ็นเทอ'/'ป้อน', 'Shift', 'Ctrl', 'Alt', 'Tab', 'Esc', 'Backspace', 'Delete', 'Insert', 'Num Lock', 'Page Up', 'Page Down', 'WASD', 'LMB', 'RMB').\n"
        )
    
    # Assassin's Creed Specialized Demeanor & Franchise Directives
    ac_directives_section = ""
    ac_info = res.get("ac_info")
    if not ac_info and any(k in tone_lower or k in title_lower for k in ["assassin", "creed", "animus", "hidden ones"]):
        ac_sample_str = " ".join([str(s).lower() for s in (sample_texts or [])[:50]])
        ac_info = resolve_assassins_creed_installment(f"{title} {res.get('tone', '')}", ac_sample_str)

    if ac_info and ac_info.get("is_ac"):
        ac_directives_section = (
            f"\n### ASSASSIN'S CREED UNIVERSE & CHARACTER DEMEANOR DIRECTIVES (ริยาบทและมิติตัวละคร):\n"
            f"- INSTALLMENT & ERA: {ac_info['title']} — {ac_info['era']} (ตัวละครหลัก: {ac_info['protagonist']})\n"
            f"- CHARACTER DEMEANOR & MANNERS (ริยาบทและบุคลิกภาพตัวละคร):\n"
            f"  {ac_info['demeanor']}\n"
            f"- DUAL-LAYER TIME DIRECTIVE (CRITICAL - มิติเวลา 2 ชั้น):\n"
            f"  1. Animus Layer (ยุคอดีตในประวัติศาสตร์): ใช้ภาษาอิงประวัติศาสตร์ วรรณกรรมโบราณ สุภาพแต่หนักแน่น สรรพนาม 'ข้า - เจ้า / สหาย / ข้า - ท่าน' ห้ามใช้ 'ครับ/ค่ะ' หรือ 'ผม/คุณ' ในยุคอดีตเด็ดขาด!\n"
            f"  2. Modern Day Layer (โลกปัจจุบัน / นอก Animus / วิทยุสื่อสาร / แฮกเกอร์ Abstergo): ใช้ภาษาคนยุคปัจจุบัน 'ผม/ฉัน - คุณ/นาย' อย่างเป็นธรรมชาติ\n"
            f"- BROTHERHOOD RELATIONSHIPS & ADDRESSING:\n"
            f"  - สหายร่วมภาคี (Fellow Assassins): เรียกกันว่า 'สหาย' (Brother/Sister) หรือ 'พี่น้องร่วมภาคี' ด้วยความเคารพซึ่งกันและกัน\n"
            f"  - ผู้อาวุโส / อาจารย์ / ชนชั้นสูง (Mentors, Masters, Nobility): เรียก 'ท่าน', 'นายท่าน', 'ท่านอาจารย์', 'ท่านลอร์ด'\n"
            f"  - ช่วงเวลาสังหารและวาระสุดท้าย (Memory Corridor / Assassination Confession): น้ำเสียงสุขุม เยือกเย็น ลุ่มลึก เคารพในความตาย คำส่งวิญญาณ 'Requiescat in pace' ➔ 'จงสู่สุคติ'\n"
            f"- SACRED CREED & MANTRAS (คติพจน์ประจำภาคี):\n"
            f"  - 'Nothing is true, everything is permitted.' ➔ 'ไร้สิ่งใดจริงแท้ ทุกสิ่งล้วนทำได้' (หรือ 'ไม่มีสิ่งใดจริงแท้ ทุกสิ่งล้วนเป็นไปได้')\n"
            f"  - 'We work in the dark to serve the light.' ➔ 'เราทำงานในเงามืด เพื่อรับใช้แสงสว่าง'\n"
            f"- CORE FRANCHISE TERMINOLOGY (ศัพท์เฉพาะประจำจักรวาล):\n"
            f"  - Assassin Brotherhood ➔ ภาคีมือสังหาร\n"
            f"  - Templar Order ➔ ภาคีเทมพลาร์\n"
            f"  - Hidden Blade ➔ มีดลับ / ใบมีดเร้น\n"
            f"  - Eagle Vision ➔ เนตรอินทรี\n"
            f"  - Pieces of Eden ➔ ชิ้นส่วนแห่งอีเดน\n"
            f"  - Leap of Faith ➔ ทะยานศรัทธา / ดิ่งศรัทธา\n"
            f"  - Desynchronized ➔ การประสานคลื่นล้มเหลว / สัญญาณหลุด\n"
        )

    single_prompt = (
        f"You are a Master-Level Video Game Localization Specialist for the game '{game_name}', translating the source language into natural Thai.\n"
        f"Your mission is to provide an authentic, natural, and culturally resonant Thai localization crafted for gamers.\n\n"
        f"### GAME UNIVERSE & TONE:\n"
        f"- Universe & Tone: {tone}\n"
        f"- Translation Philosophy: {philosophy}\n"
        f"{pronoun_section}"
        f"{lore_section}"
        f"{anti_literal_section}"
        f"{ac_directives_section}"
        f"### LOCALIZATION DIRECTIVES:\n"
        f"1. Context ID ({{id}}) is provided solely for reference. NEVER include {{id}} in your output.\n"
        f"2. Return ONLY the pure Thai translation string for {{source_text}}. Do NOT include quotes, markdown, or explanations.\n"
        f"3. STRICT ZERO-ENGLISH RESIDUAL: Translate or phonetically transliterate general English words into Thai. Proper nouns with no glossary entry MUST be phonetically transliterated into Thai script. No Thai-English code-switching.\n"
        f"   - EXCEPTION FOR KEYBOARD KEYS & CONTROLS: Keep PC keyboard keys ('Spacebar', 'Enter', 'Shift', 'Ctrl', 'Alt', 'Tab', 'Esc', 'Backspace', 'WASD', 'LMB', 'RMB') and firearm models ('M16', 'AK-47', 'SMG', 'Humvee', '9mm') in original Latin script.\n"
        f"4. Strictly preserve all game variables, tags ({{...}}, [...], <...>), and formatting tokens exactly as they appear."
        f"{rules_section}"
    )

    opt_prompt = (
        f"You are a Master-Level Video Game Localization Specialist for the game '{game_name}', translating the source language into natural Thai.\n"
        f"Generate exactly 3 context-fitting Thai translation options for: {{source_text}}.\n\n"
        f"### GAME UNIVERSE & TONE:\n"
        f"- Universe & Tone: {tone}\n"
        f"- Translation Philosophy: {philosophy}\n"
        f"{pronoun_section}"
        f"{lore_section}"
        f"{anti_literal_section}"
        f"{ac_directives_section}"
        f"### OUTPUT FORMAT DIRECTIVES:\n"
        f"1. Context ID ({{id}}) is provided solely for reference. NEVER include {{id}} in your output.\n"
        f"2. You MUST return ONLY a valid JSON array containing exactly 3 distinct Thai strings: [\"Option 1\", \"Option 2\", \"Option 3\"].\n"
        f"3. STRICT ZERO-ENGLISH RESIDUAL: Translate or phonetically transliterate general English words into Thai across all 3 options. Proper nouns with no glossary entry MUST be phonetically transliterated into Thai script. No Thai-English code-switching. (EXCEPTION: Keep alphanumeric firearm models like 'M16', 'AK-47', 'SMG', 'Humvee', and keyboard keys like 'Spacebar', 'Enter', 'Shift', 'Ctrl', 'Alt', 'Esc' in original Latin script).\n"
        f"4. Strictly preserve all game variables and tags identically across all 3 options."
        f"{rules_section}"
    )

    batch_prompt = (
        f"You are a Master-Level Video Game Localization Specialist for the game '{game_name}', translating the source language into natural Thai.\n"
        f"Perform high-accuracy bulk localization into Thai.\n\n"
        f"### GAME UNIVERSE & TONE:\n"
        f"- Universe & Tone: {tone}\n"
        f"- Translation Philosophy: {philosophy}\n"
        f"{pronoun_section}"
        f"{lore_section}"
        f"{anti_literal_section}"
        f"{ac_directives_section}"
        f"### LOCALIZATION DIRECTIVES:\n"
        f"1. Translate each line preserving line-by-line 1:1 mapping.\n"
        f"2. STRICT ZERO-ENGLISH RESIDUAL: Translate or phonetically transliterate general English words into Thai. (EXCEPTION: Keep alphanumeric firearm models and keyboard keys 'Spacebar', 'Enter', 'Shift', 'Ctrl', 'Alt', 'Esc' in original Latin script).\n"
        f"3. Maintain line count and strictly preserve all variables, codes, and tags identically.\n"
        f"4. Do NOT output explanations, introductory text, or markdown codeblocks."
        f"{rules_section}"
    )
    
    profile_data["single"] = single_prompt
    profile_data["options"] = opt_prompt
    profile_data["batch"] = batch_prompt
    if "prompts" not in profile_data or not isinstance(profile_data["prompts"], dict):
        profile_data["prompts"] = {}
    profile_data["prompts"]["single"] = single_prompt
    profile_data["prompts"]["options"] = opt_prompt
    profile_data["prompts"]["batch"] = batch_prompt
    if "tlm" in profile_data and isinstance(profile_data["tlm"], dict):
        if "prompts" not in profile_data["tlm"] or not isinstance(profile_data["tlm"]["prompts"], dict):
            profile_data["tlm"]["prompts"] = {}
        profile_data["tlm"]["prompts"]["single"] = single_prompt
        profile_data["tlm"]["prompts"]["options"] = opt_prompt
        profile_data["tlm"]["prompts"]["batch"] = batch_prompt

    return profile_data, res


class StagingTagDelegate(QStyledItemDelegate):
    """Renders category tags as clean badges and allows quick combo-box editing."""
    def paint(self, painter, option, index):
        tag = index.data() or "General"
        bg_hex, fg_hex = TAG_COLORS.get(tag, ("#585b70", "#cdd6f4"))

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Selection background
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, QColor("#313244"))

        # Badge pill rect
        rect = option.rect
        pill_w = min(rect.width() - 8, max(54, len(tag) * 8 + 14))
        pill_h = 20
        pill_x = rect.x() + (rect.width() - pill_w) // 2
        pill_y = rect.y() + (rect.height() - pill_h) // 2

        pill_rect = QRect(pill_x, pill_y, pill_w, pill_h)
        painter.setBrush(QBrush(QColor(bg_hex)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(pill_rect, 6, 6)

        # Badge text
        painter.setPen(QPen(QColor(fg_hex)))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pill_rect, Qt.AlignmentFlag.AlignCenter, tag)
        painter.restore()

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(VALID_TAGS)
        combo.setStyleSheet("background: #181825; color: #cdd6f4; border: 1px solid #89b4fa;")
        return combo

    def setEditorData(self, editor, index):
        tag = index.data() or "General"
        idx = editor.findText(tag)
        if idx >= 0:
            editor.setCurrentIndex(idx)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)


class TLMStudioDialog(QDialog):
    """
    TLM Studio 2.0: Deep Game Lore Ingestion, Directives Matrix & Interactive Staging Grid.
    Seamlessly synchronizes with active game profiles and TStudio Column 2 Glossary.
    """
    def __init__(self, parent=None, active_profile=None, initial_tab=0):
        super().__init__(parent)
        self.main_app = parent
        self.profiles = TStudioCore.load_profiles()

        if parent and hasattr(parent, 'current_profile_name') and parent.current_profile_name:
            self.active_profile = active_profile or parent.current_profile_name
        else:
            self.active_profile = active_profile or self.profiles.get("active_preset", "Default")

        self.setWindowTitle(f"🧠 TLM Studio 2.0 — คลังปัญญาและสตูดิโอ AI Prompt (Profile: {self.active_profile})")
        self.resize(1080, 860)
        self.setMinimumSize(900, 720)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI', 'Tahoma', sans-serif; }
            QGroupBox { font-weight: bold; border: 1px solid #313244; border-radius: 8px; margin-top: 8px; padding-top: 14px; color: #89b4fa; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 12px; padding: 0 4px; }
            QLineEdit, QTextEdit, QComboBox, QSpinBox { background: #181825; border: 1px solid #313244; border-radius: 6px; padding: 5px; color: #cdd6f4; }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #89b4fa; }
            QTabWidget::pane { border: 1px solid #313244; background: #181825; border-radius: 6px; }
            QTabBar::tab { background: #313244; color: #a6adc8; padding: 8px 18px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; font-weight: bold; }
            QTabBar::tab:selected { background: #181825; color: #89b4fa; border-top: 2px solid #89b4fa; }
            QTableWidget { background: #181825; alternate-background-color: #1e1e2e; gridline-color: #313244; border: 1px solid #313244; border-radius: 6px; }
            QHeaderView::section { background: #11111b; color: #a6adc8; font-weight: bold; border: none; padding: 4px; }
        """)

        # Data container for staged terms
        # list of dict: {"en": ..., "th": ..., "tag": ..., "context": ..., "alt": ...}
        self.staged_terms = []
        self._prompts_modified = False

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # 1. Top Profile Switcher & Stats Bar
        self._setup_profile_header(main_layout)

        # 2. Main Tab Widget (Tab 1: Directives, Tab 2: AI Prompt Studio, Tab 3: Staging Review)
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget, 1)

        self._build_tab1_directives()
        self._build_tab2_prompt_studio()
        self._build_tab3_staging()

        # 3. Bottom Global Status Bar & Loading Progress
        self._setup_bottom_status(main_layout)

        # Load saved profile lore configuration & prompts
        self._load_profile_lore_data(self.active_profile)
        self._load_profile_prompts(self.active_profile)

        if 0 <= initial_tab < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(initial_tab)

    # -------------------------------------------------------------
    # 1. PROFILE HEADER
    # -------------------------------------------------------------
    def _setup_profile_header(self, layout):
        header_card = QFrame()
        header_card.setStyleSheet("background: #11111b; border: 1px solid #313244; border-radius: 8px;")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(12, 8, 12, 8)
        h_layout.setSpacing(12)

        lbl_icon = QLabel("👤")
        lbl_icon.setStyleSheet("font-size: 16px;")
        h_layout.addWidget(lbl_icon)

        lbl_title = QLabel("โปรไฟล์เกมที่ใช้งาน:")
        lbl_title.setStyleSheet("font-weight: bold; color: #cdd6f4; font-size: 13px;")
        h_layout.addWidget(lbl_title)

        self.cbo_profile = QComboBox()
        self.cbo_profile.setStyleSheet("background: #181825; border: 1px solid #45475a; border-radius: 6px; padding: 4px 10px; color: #a6e3a1; font-weight: bold; min-width: 170px;")
        all_presets = list(self.profiles.get("presets", {}).keys())
        self.cbo_profile.addItems(all_presets)
        if self.active_profile in all_presets:
            self.cbo_profile.setCurrentText(self.active_profile)
        self.cbo_profile.currentTextChanged.connect(self._on_profile_selector_changed)
        h_layout.addWidget(self.cbo_profile)

        self.lbl_profile_stat = QLabel()
        self.lbl_profile_stat.setStyleSheet("background: #313244; color: #89b4fa; border-radius: 5px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        h_layout.addWidget(self.lbl_profile_stat)
        self._refresh_profile_stat_badge()

        h_layout.addStretch(1)

        btn_clean_profile = QPushButton("🧹 ล้างคำทั่วไปออกจากโปรไฟล์")
        btn_clean_profile.setStyleSheet("background: #fab387; color: #11111b; font-weight: bold; padding: 5px 12px; border-radius: 6px; font-size: 11px;")
        btn_clean_profile.setToolTip("ตรวจหาและลบคำศัพท์ภาษาอังกฤษทั่วไป (เช่น Base, Island, White, Flight) ออกจากคลังโปรไฟล์ เพื่อประหยัด Token และค่าใช้จ่ายในการแปลใน TRun")
        btn_clean_profile.clicked.connect(self._clean_common_words_from_profile)
        h_layout.addWidget(btn_clean_profile)

        btn_quick_save = QPushButton("💾 บันทึกทั้งหมดเข้าโปรไฟล์")
        btn_quick_save.setStyleSheet("background: #a6e3a1; color: #11111b; font-weight: bold; padding: 5px 14px; border-radius: 6px;")
        btn_quick_save.setToolTip("บันทึกทั้งการตั้งค่าบริบท Lore และ AI Prompts ทั้งหมดลงในโปรไฟล์นี้ทันที")
        btn_quick_save.clicked.connect(self._save_all_profile_data)
        h_layout.addWidget(btn_quick_save)

        layout.addWidget(header_card)

    def _refresh_profile_stat_badge(self):
        prof = TStudioCore.get_current_profile_data(self.active_profile)
        count = len(prof.get("glossary", {}))
        self.lbl_profile_stat.setText(f"📚 คลังศัพท์ในโปรไฟล์: {count} คำ")

    def _clean_common_words_from_profile(self):
        """Audits active profile glossary and removes single-word common English vocabulary to prevent TRun token bloat."""
        if self.main_app and hasattr(self.main_app, '_clean_and_audit_glossary_dialog'):
            self.main_app._clean_and_audit_glossary_dialog()
            self._refresh_profile_stat_badge()
            return

        prof = TStudioCore.get_current_profile_data(self.active_profile)
        glossary = prof.get("glossary", {})
        if not glossary or not isinstance(glossary, dict):
            QMessageBox.information(self, "คลังศัพท์ว่างเปล่า", f"โปรไฟล์ '{self.active_profile}' ยังไม่มีคำศัพท์ในคลัง")
            return

        generic_found = [term for term in glossary.keys() if is_common_generic_english_word(term)]
        if not generic_found:
            QMessageBox.information(
                self, "คลังศัพท์สะอาดเรียบร้อย",
                f"ยินดีด้วย! คลังศัพท์ในโปรไฟล์ '{self.active_profile}' (ทั้งหมด {len(glossary)} คำ)\n"
                f"ไม่มีคำศัพท์ภาษาอังกฤษทั่วไปปะปนอยู่เลย ทุกคำเป็นคำเฉพาะทางแล้ว!"
            )
            return

        preview_str = ", ".join(generic_found[:20])
        if len(generic_found) > 20:
            preview_str += f" ... และอีก {len(generic_found) - 20} คำ"

        res = QMessageBox.question(
            self, "ยืนยันการล้างคำศัพท์ทั่วไป",
            f"ตรวจพบคำศัพท์ภาษาอังกฤษทั่วไป {len(generic_found)} คำในโปรไฟล์ '{self.active_profile}':\n\n"
            f"ตัวอย่างคำที่พบ: {preview_str}\n\n"
            f"⚠️ คำทั่วไปเหล่านี้ทำให้ TRun แทรกคำศัพท์เข้าไปในทุกบรรทัดบทสนทนา ทำให้เปลือง Token และค่าใช้จ่าย API มหาศาล\n\n"
            f"คุณต้องการลบคำทั่วไป {len(generic_found)} คำออกจากคลังศัพท์ของโปรไฟล์นี้ทันทีหรือไม่?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if res == QMessageBox.StandardButton.Yes:
            for term in generic_found:
                glossary.pop(term, None)
            prof["glossary"] = glossary
            TStudioCore.save_profile_data(self.active_profile, prof)
            self._refresh_profile_stat_badge()
            if self.main_app and hasattr(self.main_app, 'refresh_glossary_dependent_features'):
                self.main_app.refresh_glossary_dependent_features()
            QMessageBox.information(
                self, "ล้างคำศัพท์สำเร็จ",
                f"ลบคำศัพท์ทั่วไป {len(generic_found)} คำออกจากโปรไฟล์ '{self.active_profile}' เรียบร้อยแล้ว!\n"
                f"เหลือคำเฉพาะทางคุณภาพสูง {len(glossary)} คำ ช่วยประหยัดค่าใช้จ่ายใน TRun อย่างมาก!"
            )
            self.lbl_status.setText(f"ล้างคำศัพท์ทั่วไป {len(generic_found)} คำออกจากคลังโปรไฟล์เรียบร้อย")

    def _on_profile_selector_changed(self, new_profile):
        if not new_profile or new_profile == self.active_profile:
            return

        if getattr(self, '_prompts_modified', False):
            reply = QMessageBox.question(
                self, "บันทึกการเปลี่ยนแปลง?",
                f"คุณมีการแก้ไข AI Prompt ในโปรไฟล์ '{self.active_profile}' ที่ยังไม่ได้บันทึก\nต้องการบันทึกก่อนเปลี่ยนไปโปรไฟล์ '{new_profile}' หรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._save_profile_prompts(show_msg=False)
            elif reply == QMessageBox.StandardButton.Cancel:
                self.cbo_profile.blockSignals(True)
                self.cbo_profile.setCurrentText(self.active_profile)
                self.cbo_profile.blockSignals(False)
                return

        # Save previous profile data
        self._save_profile_lore_data(silent=True)
        self.active_profile = new_profile
        self.setWindowTitle(f"🧠 TLM Studio 2.0 — คลังปัญญาและสตูดิโอ AI Prompt (Profile: {self.active_profile})")
        self._refresh_profile_stat_badge()
        self._load_profile_lore_data(self.active_profile)
        self._load_profile_prompts(self.active_profile)

        # Notify main_app to stay in sync
        if hasattr(self, 'main_app') and self.main_app and hasattr(self.main_app, 'on_profile_changed'):
            try:
                if getattr(self.main_app, 'current_profile_name', None) != new_profile:
                    self.main_app.on_profile_changed(new_profile)
            except Exception as e:
                print(f"[TLM Studio] Error notifying main_app of profile change: {e}")

    # -------------------------------------------------------------
    # 2. TAB 1: KNOWLEDGE INGESTION & DIRECTIVES MATRIX
    # -------------------------------------------------------------
    def _build_tab1_directives(self):
        tab1 = QWidget()
        layout = QVBoxLayout(tab1)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # ----------------- SECTION A: REFERENCE KNOWLEDGE INGESTION -----------------
        grp_ingest = QGroupBox("📚 1. แหล่งข้อมูลอ้างอิงและเนื้อเรื่อง (Reference Knowledge Ingestion)")
        ingest_layout = QVBoxLayout(grp_ingest)
        ingest_layout.setSpacing(8)

        # Row A1: Internal CSV Entity Scanner
        csv_scan_row = QHBoxLayout()
        self.lbl_csv_status = QLabel("📄 สแกนคำนามเฉพาะจากตารางงานแปล (Dialogue / CSV Entity Scanner):")
        self.lbl_csv_status.setStyleSheet("color: #a6adc8; font-size: 12px;")
        csv_scan_row.addWidget(self.lbl_csv_status)

        self.btn_scan_csv = QPushButton("⚡ สแกนคำนามเฉพาะจากไฟล์ CSV ในโปรเจกต์")
        self.btn_scan_csv.setStyleSheet("background: #89b4fa; color: #11111b; font-weight: bold; padding: 5px 12px; border-radius: 6px;")
        self.btn_scan_csv.setToolTip("สแกนหาคำนามเฉพาะ, คำขึ้นต้นพิมพ์ใหญ่, วงเล็บ [XYZ] ในไฟล์ตารางแปลเพื่อป้อนเข้า AI")
        self.btn_scan_csv.clicked.connect(self._scan_entities_from_csv)
        csv_scan_row.addWidget(self.btn_scan_csv)
        csv_scan_row.addStretch(1)
        ingest_layout.addLayout(csv_scan_row)

        # Row A2: Web / Wiki Fetcher
        fetch_row = QHBoxLayout()
        lbl_url = QLabel("🌐 วาง URL วิกิ/สารานุกรม:")
        lbl_url.setStyleSheet("color: #a6adc8; font-size: 12px;")
        fetch_row.addWidget(lbl_url)

        self.txt_url = QLineEdit()
        self.txt_url.setPlaceholderText("https://warhammer40k.fandom.com/wiki/... หรือ URL ข้อมูลเกม/Lore")
        fetch_row.addWidget(self.txt_url, 1)

        self.btn_fetch_url = QPushButton("🌐 Fetch via Jina Reader")
        self.btn_fetch_url.setStyleSheet("background: #fab387; color: #11111b; font-weight: bold; padding: 5px 12px; border-radius: 6px;")
        self.btn_fetch_url.setToolTip("ดึงเนื้อหาบริบทจากหน้าเว็บอัตโนมัติผ่าน Jina Reader API")
        self.btn_fetch_url.clicked.connect(self._fetch_wiki_url)
        fetch_row.addWidget(self.btn_fetch_url)
        ingest_layout.addLayout(fetch_row)

        # Row A3: Lore Text Area & Candidate Entities Box
        lore_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Lore Notes
        lore_box = QWidget()
        l_layout = QVBoxLayout(lore_box)
        l_layout.setContentsMargins(0, 0, 0, 0)
        l_layout.setSpacing(4)

        lore_head_row = QHBoxLayout()
        lore_head_row.addWidget(QLabel("📖 ข้อมูลเนื้อเรื่อง / โลกของเกม (Lore Notes):"))
        lore_head_row.addStretch(1)

        self.btn_gemini_web_lore = QPushButton("🌐 สรุปผ่าน Gemini Web")
        self.btn_gemini_web_lore.setStyleSheet("background: #89b4fa; color: #11111b; font-weight: bold; padding: 3px 8px; border-radius: 4px; font-size: 11px;")
        self.btn_gemini_web_lore.setToolTip("สร้าง Prompt ที่อ้างอิงข้อมูลจริงจาก Google Search คัดลอกลงคลิปบอร์ด และเปิด Gemini Web อัตโนมัติ เพื่อป้องกัน AI เขียนเพ้อเจ้อ/หลอนข้อมูล")
        self.btn_gemini_web_lore.clicked.connect(self._launch_gemini_web_lore_workflow)
        lore_head_row.addWidget(self.btn_gemini_web_lore)

        self.btn_import_gemini = QPushButton("📥 วางจาก Gemini Web")
        self.btn_import_gemini.setStyleSheet("background: #a6e3a1; color: #11111b; font-weight: bold; padding: 3px 8px; border-radius: 4px; font-size: 11px;")
        self.btn_import_gemini.setToolTip("นำเข้าข้อความสรุปเนื้อเรื่องที่คัดลอกจาก Gemini Web ลงในช่องนี้ทันที")
        self.btn_import_gemini.clicked.connect(self._import_gemini_web_lore)
        lore_head_row.addWidget(self.btn_import_gemini)

        self.btn_ai_scout_lore = QPushButton("🤖 AI สรุปเนื้อเรื่องอัตโนมัติ")
        self.btn_ai_scout_lore.setStyleSheet("background: #cba6f7; color: #11111b; font-weight: bold; padding: 3px 8px; border-radius: 4px; font-size: 11px;")
        self.btn_ai_scout_lore.setToolTip("ให้ AI ค้นคว้าและสรุปเนื้อเรื่อง ตัวละครหลัก สถานที่เฉพาะ และไอเท็มพิเศษของเกมนี้ พร้อมสกัดเข้า Glossary อัตโนมัติ")
        self.btn_ai_scout_lore.clicked.connect(self._generate_ai_lore)
        lore_head_row.addWidget(self.btn_ai_scout_lore)

        self.btn_extract_lore_glossary = QPushButton("📚 สกัดคำจากบทสรุปเข้า Glossary")
        self.btn_extract_lore_glossary.setStyleSheet("background: #f9e2af; color: #11111b; font-weight: bold; padding: 3px 8px; border-radius: 4px; font-size: 11px;")
        self.btn_extract_lore_glossary.setToolTip("สกัดชื่อตัวละครหลักทั้งหมด (ทั้งชื่อเต็มและชื่อเรียกสั้น), สถานที่ชื่อเฉพาะ, ฝ่าย และไอเท็มพิเศษจากบทสรุป Lore เข้าสู่ Glossary และตะกร้าตรวจสอบทันที (ไม่ต้องเสีย API ซ้ำ)")
        self.btn_extract_lore_glossary.clicked.connect(lambda: self._extract_lore_to_glossary(silent=False))
        lore_head_row.addWidget(self.btn_extract_lore_glossary)

        btn_import_lore = QPushButton("📂 นำเข้า")
        btn_import_lore.setStyleSheet("background: #313244; color: #cdd6f4; padding: 3px 6px; border-radius: 4px; font-size: 11px;")
        btn_import_lore.setToolTip("นำเข้าไฟล์เนื้อเรื่องจากภายนอก (.txt / .md / .json)")
        btn_import_lore.clicked.connect(self._import_lore_file)
        lore_head_row.addWidget(btn_import_lore)

        btn_export_lore = QPushButton("💾 บันทึก")
        btn_export_lore.setStyleSheet("background: #313244; color: #cdd6f4; padding: 3px 6px; border-radius: 4px; font-size: 11px;")
        btn_export_lore.setToolTip("บันทึกเนื้อเรื่องลงไฟล์ .txt")
        btn_export_lore.clicked.connect(self._export_lore_file)
        lore_head_row.addWidget(btn_export_lore)

        btn_clear_lore = QPushButton("🧹 ล้าง")
        btn_clear_lore.setStyleSheet("background: #313244; color: #f38ba8; padding: 3px 6px; border-radius: 4px; font-size: 11px;")
        btn_clear_lore.setToolTip("ล้างข้อความเนื้อเรื่อง")
        btn_clear_lore.clicked.connect(self._clear_lore_content)
        lore_head_row.addWidget(btn_clear_lore)

        l_layout.addLayout(lore_head_row)

        self.txt_lore_content = QTextEdit()
        self.txt_lore_content.setPlaceholderText(
            "วางเนื้อเรื่องย่อ, ภูมิหลังตัวละคร, ชื่อเมือง, เผ่าพันธุ์ หรือข้อมูลจากเกมที่นี่ หรือกดปุ่ม '🤖 AI สรุปเนื้อเรื่องอัตโนมัติ' ด้านบน..."
        )
        l_layout.addWidget(self.txt_lore_content)
        lore_splitter.addWidget(lore_box)

        # Right: Candidate Entities Scanned
        ent_box = QWidget()
        e_layout = QVBoxLayout(ent_box)
        e_layout.setContentsMargins(0, 0, 0, 0)
        e_layout.addWidget(QLabel("🔍 คำนามเฉพาะที่สแกนพบ (Candidate Entities from Game Data):"))
        self.txt_candidate_entities = QTextEdit()
        self.txt_candidate_entities.setPlaceholderText("กดปุ่ม '⚡ สแกนคำนามเฉพาะ' ด้านบนเพื่อดึงคำนามจากไฟล์แปลมาแสดงที่นี่...")
        e_layout.addWidget(self.txt_candidate_entities)
        lore_splitter.addWidget(ent_box)

        lore_splitter.setSizes([540, 360])
        ingest_layout.addWidget(lore_splitter, 1)

        splitter.addWidget(grp_ingest)

        # ----------------- SECTION B: TERMINOLOGY DIRECTIVE MATRIX -----------------
        grp_matrix = QGroupBox("🎯 2. เมทริกซ์กำหนดทิศทางการบัญญัติศัพท์ (Terminology Directive Matrix)")
        matrix_layout = QVBoxLayout(grp_matrix)
        matrix_layout.setSpacing(8)

        # Row B1: Game Tone Category & Tone Selector
        row_b1 = QHBoxLayout()
        lbl_cat = QLabel("📂 หมวดหมู่เกม:")
        lbl_cat.setStyleSheet("color: #fab387; font-weight: bold;")
        row_b1.addWidget(lbl_cat)
        
        self.cbo_tone_category = QComboBox()
        self.cbo_tone_category.setStyleSheet("background: #181825; color: #fab387; font-weight: bold; border: 1px solid #45475a; border-radius: 6px; padding: 4px;")
        self.cbo_tone_category.addItem("✨ แสดงทุกหมวดหมู่ (All Categories)")
        for cat in UNIVERSE_TONES_BY_CATEGORY.keys():
            self.cbo_tone_category.addItem(cat)
        row_b1.addWidget(self.cbo_tone_category, 1)

        lbl_tone = QLabel("🎨 โทน/จักรวาลเกม:")
        lbl_tone.setStyleSheet("color: #89b4fa; font-weight: bold;")
        row_b1.addWidget(lbl_tone)
        
        self.cbo_universe_tone = QComboBox()
        self.cbo_universe_tone.setEditable(True)
        self.cbo_universe_tone.setStyleSheet("background: #181825; color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; padding: 4px;")
        row_b1.addWidget(self.cbo_universe_tone, 2)

        self.btn_auto_detect_tone = QPushButton("🔍 ตรวจเช็คโทน")
        self.btn_auto_detect_tone.setStyleSheet("background: #89b4fa; color: #11111b; font-weight: bold; border-radius: 6px; padding: 4px 8px; font-size: 11px;")
        self.btn_auto_detect_tone.setToolTip("วิเคราะห์แนวเกมจากชื่อโปรไฟล์/ไฟล์งานแปล และสลับหมวดหมู่+โทนจักรวาลให้อัตโนมัติ")
        self.btn_auto_detect_tone.clicked.connect(self._on_auto_detect_tone_clicked)
        row_b1.addWidget(self.btn_auto_detect_tone)

        self.btn_easy_mode = QPushButton("⚡ Easy Mode")
        self.btn_easy_mode.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fab387, stop:1 #f38ba8); color: #11111b; font-weight: bold; border-radius: 6px; padding: 4px 10px; font-size: 11px;")
        self.btn_easy_mode.setToolTip("ปุ่มมหัศจรรย์คลิกเดียวจบ! วิเคราะห์เกม, ปรับโทน, ล็อกสรรพนาม, เปิดเซฟตี้เพศ 100% และคอมไพล์ AI Prompts ให้พร้อมใช้งานทันที")
        self.btn_easy_mode.clicked.connect(self._on_easy_mode_clicked)
        row_b1.addWidget(self.btn_easy_mode)

        matrix_layout.addLayout(row_b1)

        # Connect category & tone selector
        self.cbo_tone_category.currentTextChanged.connect(self._on_tone_category_changed)
        self.cbo_universe_tone.currentTextChanged.connect(self._on_universe_tone_selected)
        self._populate_tones_combo("✨ แสดงทุกหมวดหมู่ (All Categories)")

        # Row B2: Pronoun System Preset & Summary Preview
        row_b2 = QHBoxLayout()
        lbl_pronoun = QLabel("👥 สรรพนามหลัก:")
        lbl_pronoun.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        row_b2.addWidget(lbl_pronoun)

        self.cbo_pronouns = QComboBox()
        self.cbo_pronouns.setStyleSheet("background: #181825; color: #a6e3a1; font-weight: bold; border: 1px solid #45475a; border-radius: 6px; padding: 4px; min-width: 260px;")
        for p_name in PRONOUN_PRESETS.keys():
            self.cbo_pronouns.addItem(p_name)
        self.cbo_pronouns.currentTextChanged.connect(self._on_pronoun_preset_changed)
        row_b2.addWidget(self.cbo_pronouns, 1)

        self.txt_pronoun_preview = QLineEdit()
        self.txt_pronoun_preview.setReadOnly(True)
        self.txt_pronoun_preview.setStyleSheet("background: #11111b; color: #a6adc8; border: 1px dashed #45475a; border-radius: 4px; padding: 3px 8px; font-size: 11px;")
        self.txt_pronoun_preview.setToolTip("ตัวอย่างสรรพนามและแนวทางคำลงท้ายที่จะนำไปใส่ใน AI Prompt")
        row_b2.addWidget(self.txt_pronoun_preview, 2)
        matrix_layout.addLayout(row_b2)
        self._on_pronoun_preset_changed(self.cbo_pronouns.currentText())

        # Row B3: Gender Confidence & Translation Philosophy
        row_b3 = QHBoxLayout()
        self.chk_strict_gender = QCheckBox("🛡️ มั่นใจเพศ 100% ถึงระบุเพศ (ไม่มั่นใจให้ใช้คำกลาง คุณ/เจ้า/ท่าน ห้ามเดาครับ/ค่ะ)")
        self.chk_strict_gender.setChecked(True)
        self.chk_strict_gender.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 11px;")
        self.chk_strict_gender.setToolTip("หาก AI ไม่แน่ใจเพศตัวละคร 100% จาก Context ID หรือเนื้อเรื่อง จะบังคับใช้สรรพนามกลาง (คุณ/เจ้า/ท่าน) และห้ามสุ่มเดา ครับ/ค่ะ โดยเด็ดขาด")
        row_b3.addWidget(self.chk_strict_gender, 2)

        row_b3.addWidget(QLabel("⚖️ ปรัชญาการแปล:"))
        self.cbo_philosophy = QComboBox()
        self.cbo_philosophy.addItems([
            "🎬 พากย์ไทยภาพยนตร์ & ขจัดสำนวนฝรั่ง (Cinematic War Dub - ไม่แปลตรงตัว แปลเอาอารมณ์ ภาษาพูดธรรมชาติ)",
            "ทับศัพท์ผสมแปลไทย (Hybrid - ชื่อเฉพาะทับศัพท์ คำขยายแปลไทยสละสลวย)",
            "เน้นทับศัพท์แม่นยำ (Phonetic Transliteration - ถอดเสียงอิงความคุ้นเคยเกมเมอร์)",
            "เน้นความหมายไทยแท้ (Deep Localization - แปลความหมายครบทุกคำ)"
        ])
        row_b3.addWidget(self.cbo_philosophy, 1)
        matrix_layout.addLayout(row_b3)

        # Row B4: Target Categories to Mine & Term Count
        cat_box = QHBoxLayout()
        cat_box.addWidget(QLabel("🏷️ หมวดหมู่คำที่ต้องการ:"))
        self.chk_cats = {}
        for cat in ["Person", "Location", "Faction", "Weapon", "Item", "General"]:
            chk = QCheckBox(cat)
            chk.setChecked(True)
            chk.setStyleSheet("color: #cdd6f4; font-size: 11px;")
            self.chk_cats[cat] = chk
            cat_box.addWidget(chk)
        cat_box.addStretch(1)

        cat_box.addWidget(QLabel("⚡ โหมดการสกัด:"))
        self.cbo_extract_mode = QComboBox()
        self.cbo_extract_mode.addItem("🎯 สกัดคำสำคัญหลัก (Essential Lore - 35-50 คำ)", "essential")
        self.cbo_extract_mode.addItem("⚡ กำหนดจำนวนเอง (Custom Target)", "custom")
        self.cbo_extract_mode.addItem("📦 สกัดครอบคลุมระดับลึก (Deep Lore - 100 คำ)", "deep")
        self.cbo_extract_mode.addItem("🌐 สกัดสูงสุดอัตโนมัติ (Auto Max - 350 คำ)", "auto")
        self.cbo_extract_mode.setStyleSheet("background: #181825; color: #a6e3a1; font-weight: bold; border-radius: 4px; padding: 2px 8px; font-size: 11px;")
        self.cbo_extract_mode.setToolTip(
            "Essential Lore: สกัดเฉพาะคำสำคัญ/ชื่อเฉพาะหลัก 35-50 คำที่คุ้มค่าสูงสุด ช่วยประหยัด Token เวลาแปลอย่างมาก (แนะนำ)\n"
            "Custom Target: กำหนดจำนวนคำที่ต้องการสกัดด้วยตัวเองผ่านช่องตัวเลข\n"
            "Deep Lore: สกัดครอบคลุมระดับลึก 100 คำ สำหรับเกม RPG ขนาดใหญ่\n"
            "Auto Max: สกัดเต็มพิกัดสูงสุด 350 คำ"
        )
        cat_box.addWidget(self.cbo_extract_mode)

        self.lbl_spn_count = QLabel("จำนวนคำ:")
        self.lbl_spn_count.setVisible(True)
        cat_box.addWidget(self.lbl_spn_count)

        self.spn_term_count = QSpinBox()
        self.spn_term_count.setRange(10, 500)
        self.spn_term_count.setValue(35)
        self.spn_term_count.setStyleSheet("min-width: 60px;")
        self.spn_term_count.setVisible(True)
        cat_box.addWidget(self.spn_term_count)

        def _on_extract_mode_toggle(idx):
            mode = self.cbo_extract_mode.currentData()
            self.lbl_spn_count.setVisible(True)
            self.spn_term_count.setVisible(True)
            if mode == "essential":
                self.spn_term_count.setValue(35)
            elif mode == "deep":
                self.spn_term_count.setValue(100)
            elif mode == "auto":
                self.spn_term_count.setValue(350)

        self.cbo_extract_mode.currentIndexChanged.connect(_on_extract_mode_toggle)
        matrix_layout.addLayout(cat_box)

        # Row B5: Custom Constraints / Forbidden rules & Quick Rules Toolbar
        rule_head_row = QHBoxLayout()
        rule_head_row.addWidget(QLabel("⚠️ กฎเฉพาะ / กฎคุ้มครองตัวแปร (Custom & Variable Rules):"))
        rule_head_row.addStretch(1)

        btn_rule_csv_vars = QPushButton("🛡️ สแกนตัวแปรจาก CSV")
        btn_rule_csv_vars.setStyleSheet("background: #89b4fa; color: #11111b; font-weight: bold; padding: 3px 8px; border-radius: 4px; font-size: 11px;")
        btn_rule_csv_vars.setToolTip("สแกนหาตัวแปร {...}, [...], <...>, %s ใน CSV แล้วสร้างกฎห้ามแปลทับตัวแปร")
        btn_rule_csv_vars.clicked.connect(self._scan_csv_variables_and_build_rules)
        rule_head_row.addWidget(btn_rule_csv_vars)

        btn_rule_pronouns = QPushButton("🚻 เพิ่มกฎสรรพนาม & เพศ")
        btn_rule_pronouns.setStyleSheet("background: #a6e3a1; color: #11111b; font-weight: bold; padding: 3px 8px; border-radius: 4px; font-size: 11px;")
        btn_rule_pronouns.setToolTip("เพิ่มกฎสรรพนาม (เช่น Star Wars: ข้า/เจ้า/ท่าน) และกฎห้ามเดาเพศลงในช่องกฎเฉพาะทันที")
        btn_rule_pronouns.clicked.connect(self._insert_pronoun_rules)
        rule_head_row.addWidget(btn_rule_pronouns)

        btn_rule_anti_literal = QPushButton("🎬 ไม่แปลตรงตัว / พากย์ไทยภาพยนตร์")
        btn_rule_anti_literal.setStyleSheet("background: #f9e2af; color: #11111b; font-weight: bold; padding: 3px 8px; border-radius: 4px; font-size: 11px;")
        btn_rule_anti_literal.setToolTip("ฉีดกฎเหล็กแปลเอาอรรถรส ขจัดสำนวนฝรั่ง (I'll be damned -> ไม่มีทางยอม, at doorstep -> จ่อหน้าบ้าน) ปรับไวยากรณ์เป็นภาษาพูดธรรมชาติสไตล์พากย์ไทยภาพยนตร์ฮอลลีวูด และคงชื่ออาวุธ/ยานพาหนะสากล")
        btn_rule_anti_literal.clicked.connect(self._insert_anti_literal_rule)
        rule_head_row.addWidget(btn_rule_anti_literal)

        btn_rule_no_cjk = QPushButton("🇹🇭 แปลไทย 100% ไร้จีน")
        btn_rule_no_cjk.setStyleSheet("background: #313244; color: #cdd6f4; padding: 3px 6px; border-radius: 4px; font-size: 11px;")
        btn_rule_no_cjk.setToolTip("เพิ่มกฎห้ามมีตัวอักษรจีน/ญี่ปุ่น/เกาหลีหลุดรอด และแปลเป็นไทยสละสลวย 100%")
        btn_rule_no_cjk.clicked.connect(self._insert_no_cjk_rule)
        rule_head_row.addWidget(btn_rule_no_cjk)

        btn_rule_proper_noun = QPushButton("🧠 วิเคราะห์คำเฉพาะ")
        btn_rule_proper_noun.setStyleSheet("background: #fab387; color: #11111b; font-weight: bold; padding: 3px 8px; border-radius: 4px; font-size: 11px;")
        btn_rule_proper_noun.setToolTip("เพิ่มกฎให้ AI แยกแยะคำเฉพาะเพื่อทับศัพท์ตามขนบเกมเมอร์ แทนการแปลตรงตัว")
        btn_rule_proper_noun.clicked.connect(self._insert_smart_proper_noun_rule)
        rule_head_row.addWidget(btn_rule_proper_noun)

        btn_rule_hybrid = QPushButton("⚖️ สไตล์ไฮบริด")
        btn_rule_hybrid.setStyleSheet("background: #313244; color: #cdd6f4; padding: 3px 6px; border-radius: 4px; font-size: 11px;")
        btn_rule_hybrid.setToolTip("เพิ่มกฎสไตล์ผสม: คำเฉพาะทับศัพท์ + คำคุณศัพท์/คำบรรยายแปลไทย")
        btn_rule_hybrid.clicked.connect(self._insert_hybrid_rule)
        rule_head_row.addWidget(btn_rule_hybrid)

        btn_sync_profile_prompts = QPushButton("🔗 ซิงค์เข้า AI Prompt โปรไฟล์")
        btn_sync_profile_prompts.setStyleSheet("background: #f5c2e7; color: #11111b; font-weight: bold; padding: 3px 8px; border-radius: 4px; font-size: 11px;")
        btn_sync_profile_prompts.setToolTip("นำกฎจักรวาล, สรรพนาม, และกฎคุ้มครองตัวแปรนี้ไปใส่ใน AI Prompt หลักของการแปลเดี่ยวและแปลชุดในโปรไฟล์")
        btn_sync_profile_prompts.clicked.connect(self._sync_rules_to_main_prompts)
        rule_head_row.addWidget(btn_sync_profile_prompts)

        btn_clear_rules = QPushButton("🧹 ล้างกฎ")
        btn_clear_rules.setStyleSheet("background: #313244; color: #f38ba8; padding: 3px 6px; border-radius: 4px; font-size: 11px;")
        btn_clear_rules.setToolTip("ล้างกฎเฉพาะ")
        btn_clear_rules.clicked.connect(self._clear_custom_rules)
        rule_head_row.addWidget(btn_clear_rules)

        matrix_layout.addLayout(rule_head_row)

        self.txt_custom_rules = QTextEdit()
        self.txt_custom_rules.setMaximumHeight(105)
        self.txt_custom_rules.setPlaceholderText(
            "กฎเฉพาะ เช่น: ห้ามแปล Space Marine ให้ทับศัพท์ สเปซมารีน, ห้ามแก้ไขตัวแปร {...} หรือกดปุ่ม '🛡️ สแกนตัวแปรจาก CSV' ด้านบนเพื่อสร้างกฎอัตโนมัติ..."
        )
        self.txt_custom_rules.text = self.txt_custom_rules.toPlainText
        matrix_layout.addWidget(self.txt_custom_rules)

        splitter.addWidget(grp_matrix)
        splitter.setSizes([430, 290])
        layout.addWidget(splitter, 1)

        # ----------------- SECTION C: ACTION TRIGGER BAR -----------------
        trigger_bar = QHBoxLayout()
        trigger_bar.setSpacing(8)

        self.btn_start_mining = QPushButton("🚀 เริ่ม AI สกัดและบัญญัติศัพท์เชิงลึก (Start Deep AI Mining)")
        self.btn_start_mining.setStyleSheet("""
            QPushButton { background: #cba6f7; color: #11111b; font-size: 13px; font-weight: bold; padding: 8px 16px; border-radius: 6px; }
            QPushButton:hover { background: #f5c2e7; }
        """)
        self.btn_start_mining.clicked.connect(self._start_deep_ai_mining)
        trigger_bar.addWidget(self.btn_start_mining, 1)

        self.btn_web_chat_mine = QPushButton("🌐 สกัดศัพท์ผ่าน Web Chat (ฟรี)")
        self.btn_web_chat_mine.setStyleSheet("""
            QPushButton { background: #a6e3a1; color: #11111b; font-size: 12px; font-weight: bold; padding: 8px 12px; border-radius: 6px; }
            QPushButton:hover { background: #94e2d5; }
        """)
        self.btn_web_chat_mine.setToolTip("บายพาส API: สร้าง Prompt สกัดคำศัพท์ครบชุด (ตัวละครหลัก, สถานที่เฉพาะ, ไอเท็มพิเศษ) คัดลอกลงคลิปบอร์ดเพื่อนำไปวางใน Gemini Web / ChatGPT / Codex Chat ฟรี")
        self.btn_web_chat_mine.clicked.connect(self._launch_web_chat_mining_workflow)
        trigger_bar.addWidget(self.btn_web_chat_mine)

        self.btn_import_web_chat_mine = QPushButton("📥 วางผลสกัดเข้า Glossary")
        self.btn_import_web_chat_mine.setStyleSheet("""
            QPushButton { background: #f9e2af; color: #11111b; font-size: 12px; font-weight: bold; padding: 8px 12px; border-radius: 6px; }
            QPushButton:hover { background: #fab387; }
        """)
        self.btn_import_web_chat_mine.setToolTip("วางผลลัพธ์ JSON หรือตารางคำศัพท์ที่คัดลอกมาจาก Gemini Web / ChatGPT เข้าสู่ตะกร้าตรวจสอบและผสานเข้า Glossary ทันที")
        self.btn_import_web_chat_mine.clicked.connect(self._import_web_chat_mining_result)
        trigger_bar.addWidget(self.btn_import_web_chat_mine)

        self.btn_compile_prompts = QPushButton("🪄 คอมไพล์เข้า AI Prompts (Tab 2)")
        self.btn_compile_prompts.setStyleSheet("""
            QPushButton { background: #89b4fa; color: #11111b; font-size: 13px; font-weight: bold; padding: 8px 14px; border-radius: 6px; }
            QPushButton:hover { background: #b4befe; }
        """)
        self.btn_compile_prompts.setToolTip("นำเนื้อเรื่อง Lore, จักรวาลเกม, และกฎคุ้มครองตัวแปรทั้งหมดไปสร้างเป็น AI Prompts แล้วสลับไปหน้า AI Prompt Studio ทันที")
        self.btn_compile_prompts.clicked.connect(self._compile_directives_to_prompts)
        trigger_bar.addWidget(self.btn_compile_prompts)

        layout.addLayout(trigger_bar)
        self.tab_widget.addTab(tab1, "🧭 บริบทและทิศทางการสกัด (Lore & Directives)")

    # -------------------------------------------------------------
    # 3. TAB 2: AI PROMPT STUDIO & LIVE TESTER
    # -------------------------------------------------------------
    def _build_tab2_prompt_studio(self):
        tab2 = QWidget()
        layout = QVBoxLayout(tab2)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 1. Top Action Toolbar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        btn_auto_compile = QPushButton("🪄 ประกอบ Prompt จากบริบทแท็บ 1 (Auto-Synthesize)")
        btn_auto_compile.setStyleSheet("background: #89b4fa; color: #11111b; font-weight: bold; padding: 5px 12px; border-radius: 5px; font-size: 11px;")
        btn_auto_compile.setToolTip("นำเนื้อเรื่อง Lore, จักรวาลเกม, และกฎเหล็กคุ้มครองตัวแปรจากแท็บ 1 มาประกอบเป็น Single, Options และ Batch Prompts อัตโนมัติ")
        btn_auto_compile.clicked.connect(self._compile_directives_to_prompts)
        top_bar.addWidget(btn_auto_compile)

        self.btn_prompt_tpl = QToolButton()
        self.btn_prompt_tpl.setText("📚 โหลดแม่แบบ (Templates)...")
        self.btn_prompt_tpl.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_prompt_tpl.setStyleSheet("background: #cba6f7; color: #11111b; font-weight: bold; padding: 5px 12px; border-radius: 5px; font-size: 11px;")

        menu_tpl = QMenu(self)
        menu_tpl.addAction("1. Default Base (มาตรฐาน TStudio)", lambda: self._load_prompt_template("default"))
        menu_tpl.addAction("2. 🎬 Cinematic War Dub & Anti-Literal (พากย์ไทยภาพยนตร์ ขจัดสำนวนฝรั่ง)", lambda: self._load_prompt_template("cinematic_war"))
        menu_tpl.addAction("3. Story & Dialogue (สละสลวย เข้าถึงอารมณ์)", lambda: self._load_prompt_template("story"))
        menu_tpl.addAction("4. UI & Menus (สั้น กระชับ ตรงปุ่ม)", lambda: self._load_prompt_template("ui"))
        menu_tpl.addAction("5. Strict / Direct (แปลตรงตัว เคร่งครัด)", lambda: self._load_prompt_template("strict"))
        self.btn_prompt_tpl.setMenu(menu_tpl)
        top_bar.addWidget(self.btn_prompt_tpl)

        top_bar.addStretch(1)

        self.lbl_prompts_saved_status = QLabel("● พร้อมใช้งาน")
        self.lbl_prompts_saved_status.setStyleSheet("color: #a6adc8; font-size: 11px;")
        top_bar.addWidget(self.lbl_prompts_saved_status)

        btn_save_prompts = QPushButton("💾 บันทึก Prompt เข้าโปรไฟล์")
        btn_save_prompts.setStyleSheet("background: #a6e3a1; color: #11111b; font-weight: bold; padding: 5px 14px; border-radius: 5px; font-size: 11px;")
        btn_save_prompts.setToolTip("บันทึกการตั้งค่า Prompts ทั้งหมดลงในโปรไฟล์ปัจจุบัน")
        btn_save_prompts.clicked.connect(lambda: self._save_profile_prompts(show_msg=True))
        top_bar.addWidget(btn_save_prompts)

        layout.addLayout(top_bar)

        # 2. Main Scrollable Area for Prompts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        s_layout = QVBoxLayout(scroll_content)
        s_layout.setContentsMargins(0, 4, 0, 4)
        s_layout.setSpacing(10)

        # Helper to create insert toolbar
        def make_tag_bar(target_widget, tags):
            tb = QHBoxLayout()
            tb.setContentsMargins(0, 0, 0, 0)
            tb.setSpacing(6)
            lbl = QLabel("แทรกแท็ก:")
            lbl.setStyleSheet("color: #6c7086; font-size: 11px;")
            tb.addWidget(lbl)
            for tag in tags:
                btn = QPushButton(tag)
                btn.setStyleSheet("padding: 2px 7px; font-size: 11px; background: #313244; color: #89b4fa; border-radius: 3px;")
                btn.clicked.connect(lambda checked, t=tag, w=target_widget: w.insertPlainText(t))
                tb.addWidget(btn)
            tb.addStretch(1)
            return tb

        # 1. Single Translation Prompt
        grp_single = QGroupBox("1. Single Translation Prompt (การแปลเดี่ยว / TStudio)")
        l_s = QVBoxLayout(grp_single)
        l_s.setSpacing(4)
        self.txt_p_single = QTextEdit()
        self.txt_p_single.setMinimumHeight(130)
        self.txt_p_single.textChanged.connect(self._mark_prompts_modified)
        l_s.addLayout(make_tag_bar(self.txt_p_single, ["{source_text}", "{id}"]))
        l_s.addWidget(self.txt_p_single)
        s_layout.addWidget(grp_single)

        # 2. Three Options Prompt
        grp_opt = QGroupBox("2. Three Options Prompt (ตัวเลือกแปล 3 รูปแบบ / TStudio)")
        l_o = QVBoxLayout(grp_opt)
        l_o.setSpacing(4)
        lbl_opt_hint = QLabel("AI ต้องส่งผลลัพธ์เป็น JSON Array ของสตริง 3 ตัวเสมอ: [\"ตัวเลือก 1\", \"ตัวเลือก 2\", \"ตัวเลือก 3\"]")
        lbl_opt_hint.setStyleSheet("color: #fab387; font-size: 11px;")
        l_o.addWidget(lbl_opt_hint)
        self.txt_p_opt = QTextEdit()
        self.txt_p_opt.setMinimumHeight(110)
        self.txt_p_opt.textChanged.connect(self._mark_prompts_modified)
        l_o.addLayout(make_tag_bar(self.txt_p_opt, ["{source_text}", "{id}"]))
        l_o.addWidget(self.txt_p_opt)
        s_layout.addWidget(grp_opt)

        # 3. Batch Translation Prompt
        grp_batch = QGroupBox("3. Batch Translation Prompt (การแปลชุดจำนวนมาก / TRun)")
        l_b = QVBoxLayout(grp_batch)
        l_b.setSpacing(4)
        self.txt_p_batch = QTextEdit()
        self.txt_p_batch.setMinimumHeight(110)
        self.txt_p_batch.textChanged.connect(self._mark_prompts_modified)
        l_b.addLayout(make_tag_bar(self.txt_p_batch, ["{source_text}"]))
        l_b.addWidget(self.txt_p_batch)
        s_layout.addWidget(grp_batch)

        # 4. QA Checker Settings
        grp_qa = QGroupBox("✅ การตั้งค่าตรวจสอบคุณภาพ (QA Checker Settings)")
        l_qa = QHBoxLayout(grp_qa)
        lbl_qa = QLabel("จำกัดขนาดไบต์ภาษาไทยสูงสุด (Max Byte Limit):")
        lbl_qa.setStyleSheet("color: #cdd6f4; font-size: 12px;")
        l_qa.addWidget(lbl_qa)

        self.spin_qa_bytes = QSpinBox()
        self.spin_qa_bytes.setRange(0, 9999)
        self.spin_qa_bytes.setValue(63)
        self.spin_qa_bytes.setToolTip("ตั้งค่าขีดจำกัดไบต์สำหรับภาษาไทย เช่น 21/63 ไบต์ เพื่อป้องกันเกมที่บัฟเฟอร์หน่วยความจำจำกัดไม่ให้แครช (0 = ไม่จำกัด)")
        self.spin_qa_bytes.valueChanged.connect(self._mark_prompts_modified)
        l_qa.addWidget(self.spin_qa_bytes)

        lbl_qa_tip = QLabel("(ช่วยป้องกันฟอนต์ล้นบัฟเฟอร์และเกมแครช เช่น สำหรับเอนจินเกมรุ่นเก่า)")
        lbl_qa_tip.setStyleSheet("color: #6c7086; font-size: 11px;")
        l_qa.addWidget(lbl_qa_tip)
        l_qa.addStretch(1)
        s_layout.addWidget(grp_qa)

        # 5. Live Prompt Tester
        grp_tester = QGroupBox("🧪 ทดสอบ AI Prompt สด (Live Prompt Tester)")
        l_t = QVBoxLayout(grp_tester)
        l_t.setSpacing(6)

        t_row1 = QHBoxLayout()
        t_row1.addWidget(QLabel("ข้อความทดสอบ:"))
        self.txt_test_input = QLineEdit()
        self.txt_test_input.setText("Hello wanderer, welcome to the shop. What can I get for you today?")
        t_row1.addWidget(self.txt_test_input, 1)

        self.btn_test_single = QPushButton("▶️ ทดสอบแปลเดี่ยว (Single)")
        self.btn_test_single.setStyleSheet("background: #89b4fa; color: #11111b; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 11px;")
        self.btn_test_single.clicked.connect(lambda: self._run_live_prompt_test("single"))
        t_row1.addWidget(self.btn_test_single)

        self.btn_test_opt = QPushButton("▶️ ทดสอบ 3 ตัวเลือก (Options)")
        self.btn_test_opt.setStyleSheet("background: #fab387; color: #11111b; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 11px;")
        self.btn_test_opt.clicked.connect(lambda: self._run_live_prompt_test("opt"))
        t_row1.addWidget(self.btn_test_opt)

        l_t.addLayout(t_row1)

        self.txt_test_result = QTextEdit()
        self.txt_test_result.setReadOnly(True)
        self.txt_test_result.setFixedHeight(75)
        self.txt_test_result.setPlaceholderText("ผลการแปลจากโมเดล AI จะปรากฏที่นี่...")
        l_t.addWidget(self.txt_test_result)
        s_layout.addWidget(grp_tester)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)

        self.tab_widget.addTab(tab2, "⚙️ สตูดิโอ AI Prompt & ทดสอบสด (AI Prompt Studio & Live Tester)")

    # -------------------------------------------------------------
    # 4. TAB 3: INTERACTIVE STAGING REVIEW GRID
    # -------------------------------------------------------------
    def _build_tab3_staging(self):
        tab3 = QWidget()
        layout = QVBoxLayout(tab3)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Toolbar
        tb_layout = QHBoxLayout()
        tb_layout.setSpacing(8)

        lbl_s = QLabel("🔍 กรอง:")
        tb_layout.addWidget(lbl_s)

        self.txt_stage_filter = QLineEdit()
        self.txt_stage_filter.setPlaceholderText("ค้นหาในรายการคำศัพท์ที่สกัดได้...")
        self.txt_stage_filter.textChanged.connect(self._filter_staging_table)
        tb_layout.addWidget(self.txt_stage_filter, 1)

        self.cbo_stage_cat_filter = QComboBox()
        self.cbo_stage_cat_filter.addItem("ทั้งหมด (All)", "All")
        for tag in VALID_TAGS:
            self.cbo_stage_cat_filter.addItem(tag, tag)
        self.cbo_stage_cat_filter.currentIndexChanged.connect(self._filter_staging_table)
        tb_layout.addWidget(self.cbo_stage_cat_filter)

        self.lbl_stage_stat = QLabel("พบ 0 คำ (เลือกไว้ 0 คำ)")
        self.lbl_stage_stat.setStyleSheet("color: #a6adc8; font-weight: bold; font-size: 11px; padding: 0 6px;")
        tb_layout.addWidget(self.lbl_stage_stat)

        btn_sel_all = QPushButton("☑️ เลือกทั้งหมด")
        btn_sel_all.clicked.connect(lambda: self._set_all_staged_checked(True))
        tb_layout.addWidget(btn_sel_all)

        btn_desel_all = QPushButton("◻️ ปลดทั้งหมด")
        btn_desel_all.clicked.connect(lambda: self._set_all_staged_checked(False))
        tb_layout.addWidget(btn_desel_all)

        btn_del_row = QPushButton("🗑️ ลบแถว")
        btn_del_row.setStyleSheet("color: #f38ba8;")
        btn_del_row.clicked.connect(self._delete_selected_staged_rows)
        tb_layout.addWidget(btn_del_row)

        btn_filter_generic = QPushButton("🧹 กรองคำทั่วไปออก")
        btn_filter_generic.setStyleSheet("background: #313244; color: #fab387; font-weight: bold; padding: 4px 8px; border-radius: 4px; font-size: 11px;")
        btn_filter_generic.setToolTip("คัดกรองคำศัพท์ภาษาอังกฤษทั่วไป (เช่น Base, Flight, Island, White) ออกจากตะกร้าตรวจสอบอัตโนมัติ")
        btn_filter_generic.clicked.connect(self._purge_common_words_from_staged)
        tb_layout.addWidget(btn_filter_generic)

        btn_add_manual = QPushButton("➕ เพิ่มคำใหม่")
        btn_add_manual.clicked.connect(self._add_manual_staged_row)
        tb_layout.addWidget(btn_add_manual)

        layout.addLayout(tb_layout)

        # Staging Table Widget
        self.tbl_staging = QTableWidget()
        self.tbl_staging.setColumnCount(6)
        self.tbl_staging.setHorizontalHeaderLabels([
            "เลือก", "คำศัพท์ต้นฉบับ (EN)", "คำแปลไทย (TH)", "หมวดหมู่ (Tag)", "บริบท / เหตุผลรองรับ (Context)", "คำแปลทางเลือก (Alt)"
        ])
        self.tbl_staging.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.tbl_staging.setColumnWidth(0, 48)
        self.tbl_staging.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tbl_staging.setColumnWidth(1, 160)
        self.tbl_staging.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tbl_staging.setColumnWidth(2, 180)
        self.tbl_staging.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tbl_staging.setColumnWidth(3, 110)
        self.tbl_staging.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tbl_staging.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        self.tbl_staging.setColumnWidth(5, 160)

        self.tbl_staging.setAlternatingRowColors(True)
        self.tbl_staging.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_staging.setItemDelegateForColumn(3, StagingTagDelegate(self))
        self.tbl_staging.cellDoubleClicked.connect(self._on_staging_cell_double_clicked)
        self.tbl_staging.itemChanged.connect(self._on_staging_item_changed)
        layout.addWidget(self.tbl_staging, 1)

        # Import Actions Row
        import_bar = QHBoxLayout()
        import_bar.setSpacing(10)

        self.btn_export_staged = QPushButton("📤 ส่งออกรายการคำศัพท์ (CSV/JSON)")
        self.btn_export_staged.clicked.connect(self._export_staged_terms)
        import_bar.addWidget(self.btn_export_staged)

        import_bar.addStretch(1)

        self.btn_overwrite_glossary = QPushButton("⚠️ แทนที่คลังคำศัพท์ทั้งหมดในโปรไฟล์ (Overwrite)")
        self.btn_overwrite_glossary.setStyleSheet("""
            QPushButton { background: #f38ba8; color: #11111b; font-weight: bold; padding: 7px 16px; border-radius: 6px; }
            QPushButton:hover { background: #eba0ac; }
        """)
        self.btn_overwrite_glossary.setToolTip("ล้างคำศัพท์เดิมในโปรไฟล์นี้ออก แล้วแทนที่ด้วยคำศัพท์ที่เลือกไว้ทั้งหมด")
        self.btn_overwrite_glossary.clicked.connect(lambda: self._execute_import_to_profile(overwrite=True))
        import_bar.addWidget(self.btn_overwrite_glossary)

        self.btn_merge_glossary = QPushButton("📥 ผสานเข้าคลังคำศัพท์โปรไฟล์ (Merge into Profile)")
        self.btn_merge_glossary.setStyleSheet("""
            QPushButton { background: #a6e3a1; color: #11111b; font-size: 12px; font-weight: bold; padding: 7px 20px; border-radius: 6px; }
            QPushButton:hover { background: #94e2d5; }
        """)
        self.btn_merge_glossary.setToolTip("รวมคำศัพท์ที่เลือกเข้ากับคลังคำศัพท์เดิมในโปรไฟล์นี้ทันที")
        self.btn_merge_glossary.clicked.connect(lambda: self._execute_import_to_profile(overwrite=False))
        import_bar.addWidget(self.btn_merge_glossary)

        layout.addLayout(import_bar)
        self.tab_widget.addTab(tab3, "📋 ตะกร้าตรวจสอบคำศัพท์ (Staging Review & Import Grid)")

    def _build_tab2_staging(self):
        # Backward compatibility alias
        self._build_tab3_staging()

    # -------------------------------------------------------------
    # 4. BOTTOM STATUS BAR
    # -------------------------------------------------------------
    def _setup_bottom_status(self, layout):
        status_row = QHBoxLayout()
        status_row.setContentsMargins(4, 0, 4, 0)
        self.lbl_status = QLabel("พร้อมทำงาน (Ready)")
        self.lbl_status.setStyleSheet("color: #a6adc8; font-size: 11px;")
        status_row.addWidget(self.lbl_status, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #313244; border-radius: 5px; background: #11111b; } QProgressBar::chunk { background: #cba6f7; }")
        self.progress_bar.hide()
        status_row.addWidget(self.progress_bar)

        layout.addLayout(status_row)

    # -------------------------------------------------------------
    # LOGIC: PROFILE DATA PERSISTENCE
    # -------------------------------------------------------------
    def _load_profile_lore_data(self, profile_name):
        prof = TStudioCore.get_current_profile_data(profile_name)
        tlm_data = prof.get("tlm") or prof.get("tlm_lore") or {}
        if not isinstance(tlm_data, dict):
            tlm_data = {"lore_notes": str(tlm_data)} if tlm_data else {}

        self.txt_url.setText(str(tlm_data.get("wiki_url") or ""))
        self.txt_lore_content.setText(str(tlm_data.get("lore_notes") or ""))
        self.txt_candidate_entities.setText(str(tlm_data.get("candidate_entities") or ""))

        tone = str(tlm_data.get("universe_tone") or "")
        found_cat = None
        for cat_name, tones in UNIVERSE_TONES_BY_CATEGORY.items():
            if tone in tones:
                found_cat = cat_name
                break

        if found_cat:
            idx = self.cbo_tone_category.findText(found_cat)
            if idx >= 0:
                self.cbo_tone_category.blockSignals(True)
                self.cbo_tone_category.setCurrentIndex(idx)
                self._populate_tones_combo(found_cat)
                self.cbo_tone_category.blockSignals(False)
        else:
            self.cbo_tone_category.blockSignals(True)
            self.cbo_tone_category.setCurrentIndex(0)
            self._populate_tones_combo("✨ แสดงทุกหมวดหมู่ (All Categories)")
            self.cbo_tone_category.blockSignals(False)

        if tone:
            idx = self.cbo_universe_tone.findText(tone)
            if idx >= 0:
                self.cbo_universe_tone.setCurrentIndex(idx)
            else:
                self.cbo_universe_tone.setEditText(tone)

        p_preset = str(tlm_data.get("pronoun_preset") or "")
        if p_preset:
            idx = self.cbo_pronouns.findText(p_preset)
            if idx >= 0:
                self.cbo_pronouns.setCurrentIndex(idx)
            else:
                self._on_universe_tone_selected(tone)
        else:
            self._on_universe_tone_selected(tone)

        if "strict_gender" in tlm_data:
            self.chk_strict_gender.setChecked(bool(tlm_data.get("strict_gender")))
        else:
            self.chk_strict_gender.setChecked(True)

        philosophy = str(tlm_data.get("philosophy") or tlm_data.get("trans_philosophy") or "")
        if philosophy:
            idx = self.cbo_philosophy.findText(philosophy)
            if idx >= 0:
                self.cbo_philosophy.setCurrentIndex(idx)

        self.txt_custom_rules.setText(str(tlm_data.get("custom_rules") or ""))
        extract_mode = tlm_data.get("extract_mode", "essential")
        idx_m = self.cbo_extract_mode.findData(extract_mode)
        if idx_m >= 0:
            self.cbo_extract_mode.setCurrentIndex(idx_m)
        else:
            self.cbo_extract_mode.setCurrentIndex(0)

        term_cnt = tlm_data.get("term_count")
        try:
            self.spn_term_count.setValue(int(term_cnt) if term_cnt is not None else 35)
        except Exception:
            self.spn_term_count.setValue(35)

        checked_cats = tlm_data.get("target_categories")
        if not isinstance(checked_cats, list):
            checked_cats = ["Person", "Location", "Faction", "Weapon", "Item", "General"]
        for cat, chk in self.chk_cats.items():
            chk.setChecked(cat in checked_cats)

    def _save_profile_lore_data(self, silent=False):
        prof_name = self.active_profile
        prof = TStudioCore.get_current_profile_data(prof_name)

        if "tlm" not in prof or not isinstance(prof["tlm"], dict):
            prof["tlm"] = {}
        # Remove deprecated tlm_lore
        prof.pop("tlm_lore", None)

        checked_cats = [cat for cat, chk in self.chk_cats.items() if chk.isChecked()]
        prof["tlm"].update({
            "wiki_url": self.txt_url.text().strip(),
            "lore_notes": self.txt_lore_content.toPlainText().strip(),
            "candidate_entities": self.txt_candidate_entities.toPlainText().strip(),
            "universe_tone": self.cbo_universe_tone.currentText().strip(),
            "tone_category": self.cbo_tone_category.currentText().strip(),
            "pronoun_preset": self.cbo_pronouns.currentText().strip(),
            "strict_gender": self.chk_strict_gender.isChecked(),
            "philosophy": self.cbo_philosophy.currentText().strip(),
            "trans_philosophy": self.cbo_philosophy.currentText().strip(),
            "custom_rules": self.txt_custom_rules.toPlainText().strip(),
            "extract_mode": self.cbo_extract_mode.currentData(),
            "term_count": self.spn_term_count.value(),
            "target_categories": checked_cats
        })

        TStudioCore.save_profile_data(prof_name, prof)
        if not silent:
            QMessageBox.information(
                self, "บันทึกข้อมูลสำเร็จ",
                f"บันทึกข้อมูลบริบทและทิศทางคำศัพท์ลงในโปรไฟล์ '{prof_name}' เรียบร้อยแล้ว!"
            )

    # -------------------------------------------------------------
    # LOGIC: PROMPT STUDIO PERSISTENCE & COMPILER
    # -------------------------------------------------------------
    def _mark_prompts_modified(self):
        self._prompts_modified = True
        if hasattr(self, 'lbl_prompts_saved_status'):
            self.lbl_prompts_saved_status.setText("● มีการแก้ไขที่ยังไม่ได้บันทึก")
            self.lbl_prompts_saved_status.setStyleSheet("color: #fab387; font-size: 11px; font-weight: bold;")

    def _load_profile_prompts(self, profile_name):
        if not hasattr(self, 'txt_p_single'):
            return
        prof = TStudioCore.get_current_profile_data(profile_name)

        self.txt_p_single.blockSignals(True)
        self.txt_p_opt.blockSignals(True)
        self.txt_p_batch.blockSignals(True)
        self.spin_qa_bytes.blockSignals(True)

        self.txt_p_single.setPlainText(str(prof.get("single") or DEFAULT_SINGLE_PROMPT))
        self.txt_p_opt.setPlainText(str(prof.get("opt") or DEFAULT_OPTIONS_PROMPT))
        self.txt_p_batch.setPlainText(str(prof.get("batch") or prof.get("single") or DEFAULT_SINGLE_PROMPT))
        val_limit = prof.get("max_bytes_limit")
        try:
            self.spin_qa_bytes.setValue(int(val_limit) if val_limit is not None else 63)
        except Exception:
            self.spin_qa_bytes.setValue(63)

        self.txt_p_single.blockSignals(False)
        self.txt_p_opt.blockSignals(False)
        self.txt_p_batch.blockSignals(False)
        self.spin_qa_bytes.blockSignals(False)

        self._prompts_modified = False
        if hasattr(self, 'lbl_prompts_saved_status'):
            self.lbl_prompts_saved_status.setText("● พร้อมใช้งาน")
            self.lbl_prompts_saved_status.setStyleSheet("color: #a6adc8; font-size: 11px;")

    def _save_profile_prompts(self, show_msg=True):
        if not hasattr(self, 'txt_p_single'):
            return False
        s1 = self.txt_p_single.toPlainText()
        s2 = self.txt_p_opt.toPlainText()

        if "{source_text}" not in s1 or "{source_text}" not in s2:
            reply = QMessageBox.warning(
                self, "ไม่มีแท็ก {source_text}",
                "Prompt ของคุณไม่มีแท็ก '{source_text}' ซึ่งจะทำให้ AI ไม่ได้รับข้อความที่จะแปล\n\nต้องการบันทึกต่อไปหรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return False

        data = TStudioCore.load_profiles()
        if self.active_profile in data.get("presets", {}):
            data["presets"][self.active_profile]["single"] = s1
            data["presets"][self.active_profile]["opt"] = s2
            data["presets"][self.active_profile]["batch"] = self.txt_p_batch.toPlainText()
            data["presets"][self.active_profile]["max_bytes_limit"] = self.spin_qa_bytes.value()
            data["active_preset"] = self.active_profile
            TStudioCore.save_profiles(data)

            self._prompts_modified = False
            if hasattr(self, 'lbl_prompts_saved_status'):
                self.lbl_prompts_saved_status.setText("● บันทึกแล้ว")
                self.lbl_prompts_saved_status.setStyleSheet("color: #a6e3a1; font-size: 11px;")

            parent = self.parent() or self.main_app
            if parent and hasattr(parent, 'on_profile_changed'):
                parent._profiles_data = data
                if hasattr(parent, 'cbo_profile'):
                    parent.cbo_profile.blockSignals(True)
                    parent.cbo_profile.setCurrentText(self.active_profile)
                    parent.cbo_profile.blockSignals(False)
                parent.on_profile_changed(self.active_profile)

            if show_msg:
                QMessageBox.information(self, "บันทึกสำเร็จ", f"บันทึก AI Prompts ลงในโปรไฟล์ '{self.active_profile}' เรียบร้อยแล้ว!")
                self.lbl_status.setText(f"บันทึก AI Prompts ลงโปรไฟล์ '{self.active_profile}' สำเร็จ")
            return True
        return False

    def _save_all_profile_data(self):
        self._save_profile_lore_data(silent=True)
        self._save_profile_prompts(show_msg=False)
        QMessageBox.information(
            self, "บันทึกข้อมูลทั้งหมดสำเร็จ",
            f"บันทึกทั้งบริบทเนื้อเรื่อง Lore, กฎจักรวาล และ AI Prompts ทั้งหมดเข้าโปรไฟล์ '{self.active_profile}' เรียบร้อยแล้ว!"
        )
        self.lbl_status.setText(f"บันทึกบริบทและ AI Prompts ลงในโปรไฟล์ '{self.active_profile}' สำเร็จ")

    def _compile_directives_to_prompts(self):
        """Compiles Game Lore, Universe Tone, Translation Philosophy, Pronouns, and Ironclad Rules
        from Tab 1 into professional Single, Options, and Batch Prompts in Tab 2."""
        game_name = getattr(self, '_detected_game_name', '') or (self.active_profile if self.active_profile and self.active_profile.lower() != "default" else "Game")
        tone = self.cbo_universe_tone.currentText().strip()
        philosophy = self.cbo_philosophy.currentText().strip()
        lore = self.txt_lore_content.toPlainText().strip()
        custom_rules = self.txt_custom_rules.toPlainText().strip()

        # Pronoun & Gender Certainty Directives
        p_name = self.cbo_pronouns.currentText().strip()
        preset = PRONOUN_PRESETS.get(p_name, {})
        p_rules = preset.get("rules", "")
        p_neutral = preset.get("neutral", "คุณ / เจ้า / ท่าน")
        strict_gender = self.chk_strict_gender.isChecked()

        pronoun_section = (
            f"\n### PRONOUN & CHARACTER ADDRESSING MATRIX:\n"
            f"- Pronoun Style: {p_name}\n"
            f"{p_rules}\n"
        )
        if strict_gender:
            pronoun_section += (
                f"- STRICT GENDER CERTAINTY (NON-NEGOTIABLE):\n"
                f"  1. ONLY use gender-specific pronouns/particles (ผม, ฉัน, ดิฉัน, ครับ, ค่ะ, นาย, เธอ, หล่อน, แม่นาง) "
                f"when 100% CERTAIN of character gender from Context ID (e.g. '_female', '_male', 'queen_', 'caroline', 'anya', 'engel'), explicit source clues ('she said', 'madam', 'sir'), or established lore.\n"
                f"  2. IF UNCERTAIN OR AMBIGUOUS: NEVER guess or gamble on gender! MUST use neutral pronouns ({p_neutral}) or naturally omit the subject, and NEVER gamble on polite gender particles ('ครับ' vs 'ค่ะ').\n"
                f"  3. FEMALE OPERATOR / CHARACTER RULE: When a female character (identified via Context ID, female name e.g. Caroline, Anya, Frau Engel, Sarah, Jill, or context) speaks in first person, NEVER use 'ผม' or 'ครับ'! Use 'ฉัน' (peers/informal) or 'ดิฉัน' (formal report), or naturally drop the subject.\n"
                f"  4. SUBJECT DROPPING IN COMBAT/ACTION: In tactical commands or reports, drop pronouns naturally (e.g. 'รับทราบ', 'เห็นเป้าหมายแล้ว', 'กำลังเข้าเคลียร์') instead of forcing 'ผม/ฉัน'.\n"
            )

        lore_section = f"\n### GAME LORE & SETTING:\n{lore}\n" if lore else ""
        rules_section = f"\n### IRONCLAD PROJECT & VARIABLE RULES:\n{custom_rules}\n" if custom_rules else ""

        is_anti_literal = (
            "Cinematic" in philosophy or
            "ไม่แปลตรงตัว" in philosophy or
            "พากย์ไทยภาพยนตร์" in philosophy or
            "ขจัดสำนวนฝรั่ง" in philosophy or
            "ANTI-LITERAL" in custom_rules.upper() or
            "ไม่แปลตรงตัว" in custom_rules
        )
        anti_literal_section = ""
        if is_anti_literal:
            anti_literal_section = (
                "\n### ANTI-LITERAL & CINEMATIC ACTION-DUB DIRECTIVES (CRITICAL):\n"
                "1. BAN WORD-FOR-WORD TRANSLATION & RIGID TRANSLATIONESE:\n"
                "   - NEVER translate English idioms or slangs literally word-for-word.\n"
                "   - 'I'll be damned if...' ➔ 'ไม่มีทางยอมให้... / ฝันไปเถอะว่าฉันจะ...' (ห้ามแปล 'ฉันจะถูกสาปถ้า...')\n"
                "   - 'at our doorstep' ➔ 'บุกมาถึงหน้าบ้านเรา / จ่อคอหอยเราอยู่' (ห้ามแปล 'อยู่ที่ธรณีประตู')\n"
                "   - 'go to hell and back to kick them out' ➔ 'บุกน้ำลุยไฟพลิกแผ่นดินเพื่อไล่ตะเพิดพวกมัน' (ห้ามแปล 'ไปนรกและกลับมาเพื่อเตะ...')\n"
                "   - 'on their knees' ➔ 'ยอมสยบ / คลานเข่าเข้ามาขอร้อง / จนตรอก' (ห้ามแปล 'คุกเข่าอยู่')\n"
                "   - 'Jerry / Kraut' ➔ 'พวกนาซี / พวกเยอรมัน / พวกไอ้กบฏ' (ห้ามแปล 'เจอร์รี่')\n"
                "   - 'bite the bullet' ➔ 'กัดฟันสู้ / จำใจกลืนเลือด' (ห้ามแปล 'กัดกระสุน')\n"
                "2. NATURAL SPOKEN THAI SYNTAX & COMBAT TONE:\n"
                "   - Eliminate rigid passive voice: ห้ามใช้ 'ถูกบังคับให้ถอยหลัง', ให้ใช้ 'ต้องล่าถอย' (ในภาษาไทย 'ถูก' ใช้กับเคราะห์ร้ายเท่านั้น และห้ามใช้โครงสร้าง 'ได้รับการ/ทำการ/มีการ')\n"
                "   - Dialogue must flow like a blockbuster movie Thai dub (พันธมิตร/ทีมพากย์ฮอลลีวูดมืออาชีพ): ใช้ภาษาพูดที่มีพลัง ดุดัน สมจริงตามสถานการณ์สงคราม\n"
                "   - Profanity & Combat Exclamations (Damn, Bastard, Hell, Shit, Fuck): ถ่ายทอดอารมณ์ด่าและสบถตามสถานการณ์เดือด (เช่น 'เวรเอ๊ย', 'ไอ้ระยำ', 'สารเลว', 'บัดซบ') ห้ามแปลสุภาพจนเสียอรรถรส\n"
                "3. WEAPONS & TACTICAL VEHICLES EXCEPTION:\n"
                "   - Keep firearm models (MP40, STG44, Flak 88, Luger, Panzerhund, RPG, SMG, AR), calibers, and vehicles in original Latin/alphanumeric script.\n"
                "4. KEYBOARD KEYS, MOUSE & CONTROLLER INPUTS EXCEPTION:\n"
                "   - Keep PC keyboard keys and controls in original Latin script (e.g. 'Spacebar'/'Space' NEVER 'สเปคบรา'/'เว้นวรรค', 'Enter' NEVER 'เอ็นเทอ'/'ป้อน', 'Shift', 'Ctrl', 'Alt', 'Tab', 'Esc', 'Backspace', 'Delete', 'Insert', 'Num Lock', 'Page Up', 'Page Down', 'WASD', 'LMB', 'RMB').\n"
            )

        # Assassin's Creed Specialized Demeanor & Franchise Directives
        ac_info = getattr(self, '_detected_ac_info', None)
        if not ac_info and any(k in tone.lower() or k in game_name.lower() or k in lore.lower() for k in ["assassin", "creed", "animus", "hidden ones"]):
            ac_info = resolve_assassins_creed_installment(f"{game_name} {tone}", lore)

        ac_directives_section = ""
        if ac_info and ac_info.get("is_ac"):
            ac_directives_section = (
                f"\n### ASSASSIN'S CREED UNIVERSE & CHARACTER DEMEANOR DIRECTIVES (ริยาบทและมิติตัวละคร):\n"
                f"- INSTALLMENT & ERA: {ac_info['title']} — {ac_info['era']} (ตัวละครหลัก: {ac_info['protagonist']})\n"
                f"- CHARACTER DEMEANOR & MANNERS (ริยาบทและบุคลิกภาพตัวละคร):\n"
                f"  {ac_info['demeanor']}\n"
                f"- DUAL-LAYER TIME DIRECTIVE (CRITICAL - มิติเวลา 2 ชั้น):\n"
                f"  1. Animus Layer (ยุคอดีตในประวัติศาสตร์): ใช้ภาษาอิงประวัติศาสตร์ วรรณกรรมโบราณ สุภาพแต่หนักแน่น สรรพนาม 'ข้า - เจ้า / สหาย / ข้า - ท่าน' ห้ามใช้ 'ครับ/ค่ะ' หรือ 'ผม/คุณ' ในยุคอดีตเด็ดขาด!\n"
                f"  2. Modern Day Layer (โลกปัจจุบัน / นอก Animus / วิทยุสื่อสาร / แฮกเกอร์ Abstergo): ใช้ภาษาคนยุคปัจจุบัน 'ผม/ฉัน - คุณ/นาย' อย่างเป็นธรรมชาติ\n"
                f"- BROTHERHOOD RELATIONSHIPS & ADDRESSING:\n"
                f"  - สหายร่วมภาคี (Fellow Assassins): เรียกกันว่า 'สหาย' (Brother/Sister) หรือ 'พี่น้องร่วมภาคี' ด้วยความเคารพซึ่งกันและกัน\n"
                f"  - ผู้อาวุโส / อาจารย์ / ชนชั้นสูง (Mentors, Masters, Nobility): เรียก 'ท่าน', 'นายท่าน', 'ท่านอาจารย์', 'ท่านลอร์ด'\n"
                f"  - ช่วงเวลาสังหารและวาระสุดท้าย (Memory Corridor / Assassination Confession): น้ำเสียงสุขุม เยือกเย็น ลุ่มลึก เคารพในความตาย คำส่งวิญญาณ 'Requiescat in pace' ➔ 'จงสู่สุคติ'\n"
                f"- SACRED CREED & MANTRAS (คติพจน์ประจำภาคี):\n"
                f"  - 'Nothing is true, everything is permitted.' ➔ 'ไร้สิ่งใดจริงแท้ ทุกสิ่งล้วนทำได้' (หรือ 'ไม่มีสิ่งใดจริงแท้ ทุกสิ่งล้วนเป็นไปได้')\n"
                f"  - 'We work in the dark to serve the light.' ➔ 'เราทำงานในเงามืด เพื่อรับใช้แสงสว่าง'\n"
                f"- CORE FRANCHISE TERMINOLOGY (ศัพท์เฉพาะประจำจักรวาล):\n"
                f"  - Assassin Brotherhood ➔ ภาคีมือสังหาร\n"
                f"  - Templar Order ➔ ภาคีเทมพลาร์\n"
                f"  - Hidden Blade ➔ มีดลับ / ใบมีดเร้น\n"
                f"  - Eagle Vision ➔ เนตรอินทรี\n"
                f"  - Pieces of Eden ➔ ชิ้นส่วนแห่งอีเดน\n"
                f"  - Leap of Faith ➔ ทะยานศรัทธา / ดิ่งศรัทธา\n"
                f"  - Desynchronized ➔ การประสานคลื่นล้มเหลว / สัญญาณหลุด\n"
            )

        single_prompt = (
            f"You are a Master-Level Video Game Localization Specialist for the game '{game_name}', translating the source language into natural Thai.\n"
            f"Your mission is to provide an authentic, natural, and culturally resonant Thai localization crafted for gamers.\n\n"
            f"### GAME UNIVERSE & TONE:\n"
            f"- Universe & Tone: {tone}\n"
            f"- Translation Philosophy: {philosophy}\n"
            f"{pronoun_section}"
            f"{lore_section}"
            f"{anti_literal_section}"
            f"{ac_directives_section}"
            f"### LOCALIZATION DIRECTIVES:\n"
            f"1. Context ID ({{id}}) is provided solely for reference. NEVER include {{id}} in your output.\n"
            f"2. Return ONLY the pure Thai translation string for {{source_text}}. Do NOT include quotes, markdown, or explanations.\n"
            f"3. STRICT ZERO-ENGLISH RESIDUAL: Translate or phonetically transliterate general English words into Thai (e.g. 'Quest' ➔ 'เควสต์', 'Inventory' ➔ 'ช่องเก็บของ', 'Attack' ➔ 'โจมตี'). Proper nouns with no glossary entry MUST be phonetically transliterated into Thai script. No Thai-English code-switching.\n"
            f"   - EXCEPTION FOR MILITARY & WEAPONS: Keep alphanumeric firearm models (e.g. 'M16' NEVER 'เอ็ม 16', 'AK-47', 'MP5', 'RPG-7', 'Glock 19'), weapon class acronyms ('SMG', 'AR', 'LMG', 'DMR', 'SR'), military vehicles ('Humvee', 'APC', 'VTOL', 'UAV', 'BTR-80'), and calibers ('9mm', '5.56mm') in original Latin/alphanumeric script.\n"
            f"   - EXCEPTION FOR KEYBOARD KEYS & CONTROLS: Keep PC keyboard keys and controls in original Latin script ('Spacebar'/'Space' NEVER 'สเปคบรา'/'เว้นวรรค', 'Enter' NEVER 'เอ็นเทอ'/'ป้อน', 'Shift', 'Ctrl', 'Alt', 'Tab', 'Esc', 'Backspace', 'Delete', 'Insert', 'Num Lock', 'Page Up', 'Page Down', 'WASD', 'LMB', 'RMB').\n"
            f"4. Strictly preserve all game variables, tags ({{...}}, [...], <...>), and formatting tokens exactly as they appear."
            f"{rules_section}"
        )

        opt_prompt = (
            f"You are a Master-Level Video Game Localization Specialist for the game '{game_name}', translating the source language into natural Thai.\n"
            f"Generate exactly 3 context-fitting Thai translation options for: {{source_text}}.\n\n"
            f"### GAME UNIVERSE & TONE:\n"
            f"- Universe & Tone: {tone}\n"
            f"- Translation Philosophy: {philosophy}\n"
            f"{pronoun_section}"
            f"{lore_section}"
            f"{anti_literal_section}"
            f"{ac_directives_section}"
            f"### OUTPUT FORMAT DIRECTIVES:\n"
            f"1. Context ID ({{id}}) is provided solely for reference. NEVER include {{id}} in your output.\n"
            f"2. You MUST return ONLY a valid JSON array containing exactly 3 distinct Thai strings: [\"Option 1\", \"Option 2\", \"Option 3\"].\n"
            f"3. STRICT ZERO-ENGLISH RESIDUAL: Translate or phonetically transliterate general English words into Thai across all 3 options. Proper nouns with no glossary entry MUST be phonetically transliterated into Thai script. No Thai-English code-switching. (EXCEPTION: Keep alphanumeric firearm models like 'M16', 'AK-47', 'SMG', 'Humvee', and keyboard keys like 'Spacebar', 'Enter', 'Shift', 'Ctrl', 'Alt', 'Esc' in original Latin script).\n"
            f"4. Strictly preserve all game variables and tags identically across all 3 options."
            f"{rules_section}"
        )

        batch_prompt = (
            f"You are a Master-Level Video Game Localization Specialist for the game '{game_name}', translating the source language into natural Thai.\n"
            f"Perform high-accuracy bulk localization into Thai.\n\n"
            f"### GAME UNIVERSE & TONE:\n"
            f"- Universe & Tone: {tone}\n"
            f"- Translation Philosophy: {philosophy}\n"
            f"{pronoun_section}"
            f"{lore_section}"
            f"{anti_literal_section}"
            f"{ac_directives_section}"
            f"### LOCALIZATION DIRECTIVES:\n"
            f"1. Translate each line preserving line-by-line 1:1 mapping.\n"
            f"2. STRICT ZERO-ENGLISH RESIDUAL: Translate or phonetically transliterate general English words into Thai. (EXCEPTION: Keep alphanumeric firearm models and keyboard keys 'Spacebar', 'Enter', 'Shift', 'Ctrl', 'Alt', 'Esc' in original Latin script).\n"
            f"3. Maintain line count and strictly preserve all variables, codes, and tags identically.\n"
            f"4. Do NOT output explanations, introductory text, or markdown codeblocks."
            f"{rules_section}"
        )

        self.txt_p_single.setPlainText(single_prompt)
        self.txt_p_opt.setPlainText(opt_prompt)
        self.txt_p_batch.setPlainText(batch_prompt)
        self._mark_prompts_modified()

        # Switch to Tab 2 (AI Prompt Studio)
        self.tab_widget.setCurrentIndex(1)
        self.lbl_status.setText(f"ประกอบ AI Prompts จากบริบท, สรรพนาม และกฎของ '{game_name}' เรียบร้อยแล้ว (ตรวจสอบและทดสอบสดได้ทันที)")

    def _load_prompt_template(self, tpl_type):
        msg = QMessageBox(self)
        msg.setWindowTitle("โหลดแม่แบบ Prompt")
        msg.setText("การโหลดแม่แบบจะแทนที่เนื้อหา Prompt ปัจจุบันในหน้านี้ ต้องการดำเนินการต่อหรือไม่?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() != QMessageBox.StandardButton.Yes:
            return

        if tpl_type == "default":
            self.txt_p_single.setPlainText(DEFAULT_SINGLE_PROMPT)
            self.txt_p_opt.setPlainText(DEFAULT_OPTIONS_PROMPT)
            self.txt_p_batch.setPlainText(DEFAULT_SINGLE_PROMPT)
        elif tpl_type == "cinematic_war":
            sys_p = (
                "You are an Elite Hollywood Action & War Movie Dubbing Scriptwriter and Master Game Localizer.\n"
                "Translate the dialogue/subtitles for {source_text} into natural, punchy spoken Thai (พากย์ไทยภาพยนตร์แอ็กชัน/สงครามระดับบล็อกบัสเตอร์).\n\n"
                "CRITICAL ANTI-LITERAL DIRECTIVES:\n"
                "1. NEVER translate idioms, slangs, or metaphors literally word-for-word (e.g. 'I'll be damned if...' -> 'ไม่มีทางยอมให้... / ฝันไปเถอะ', 'at our doorstep' -> 'บุกมาถึงหน้าบ้านเรา / จ่อคอหอยเราอยู่', 'go to hell and back' -> 'บุกน้ำลุยไฟพลิกแผ่นดินเพื่อไล่ตะเพิดพวกมัน', 'on their knees' -> 'ยอมสยบ / คลานเข่าเข้ามาขอร้อง / จนตรอก', 'Jerry / Kraut' -> 'พวกนาซี / พวกเยอรมัน').\n"
                "2. NO ROBOTIC TRANSLATIONESE: Ban rigid passive voice ('ถูกบังคับให้ถอย' -> 'ต้องล่าถอย') and bureaucratic words ('ทำการ...', 'มีการ...', 'ได้รับการ...'). Use natural spoken Thai syntax.\n"
                "3. TONE & COMBAT SWEARING: Translate military slang, battle shouts, and curse words (Damn, Bastard, Hell, Shit, Fuck) with authentic grit and raw emotion (เช่น 'เวรเอ๊ย', 'ไอ้ระยำ', 'สารเลว', 'บัดซบ').\n"
                "4. MILITARY & WEAPONS EXCEPTION: Keep firearm models (MP40, STG44, Flak 88, Luger, Panzerhund, RPG, SMG, AR), calibers, and tactical vehicle names in original Latin/alphanumeric script.\n"
                "5. Strictly preserve all game variables and tags ({...}, <...>, %s) exactly as they appear."
            )
            self.txt_p_single.setPlainText(sys_p + "\n\n- Return ONLY the pure Thai dubbing string for {source_text}. No markdown, no quotes, no commentary.")
            self.txt_p_opt.setPlainText(sys_p + "\n\n- Return exactly 3 distinct, emotionally intense Thai dubbing options as a valid JSON array of strings: [\"Option 1\", \"Option 2\", \"Option 3\"].")
            self.txt_p_batch.setPlainText(sys_p + "\n\n- Return ONLY the pure Thai string for each line. Maintain line count identically.")
        elif tpl_type == "story":
            sys_p = "You are a creative writer and game localization expert. Translate the following video game dialogue/story text into Thai.\nFocus on natural flow, emotional resonance, and fitting character voices.\nUse {id} and {source_text}."
            self.txt_p_single.setPlainText(sys_p + "\n\n- Return ONLY the Thai string.")
            self.txt_p_opt.setPlainText(sys_p + "\n\n- Return exactly 3 slightly different emotional/creative options as a JSON array of strings.")
            self.txt_p_batch.setPlainText(sys_p + "\n\n- Return ONLY the Thai string.")
        elif tpl_type == "ui":
            sys_p = "You are a UI/UX localization expert. Translate the following game interface text into Thai.\nKeep the translation as short, concise, and literal as possible to fit UI buttons.\nUse {id} and {source_text}."
            self.txt_p_single.setPlainText(sys_p + "\n\n- Return ONLY the Thai string.")
            self.txt_p_opt.setPlainText(sys_p + "\n\n- Return exactly 3 concise options as a JSON array of strings.")
            self.txt_p_batch.setPlainText(sys_p + "\n\n- Return ONLY the Thai string.")
        elif tpl_type == "strict":
            sys_p = "Translate the following {source_text} into Thai directly and literally.\nDo not adapt, localize, or add creative flair.\nReturn ONLY the pure Thai string."
            self.txt_p_single.setPlainText(sys_p)
            self.txt_p_opt.setPlainText("Translate {source_text} into Thai.\nReturn exactly 3 literal translation options as a JSON array of strings.")
            self.txt_p_batch.setPlainText(sys_p)

        self._mark_prompts_modified()
        self.lbl_status.setText(f"โหลดแม่แบบ '{tpl_type}' เข้าสู่สตูดิโอเรียบร้อย")

    def _run_live_prompt_test(self, mode):
        test_text = self.txt_test_input.text().strip()
        if not test_text:
            QMessageBox.warning(self, "คำเตือน", "กรุณาใส่ข้อความทดสอบก่อน")
            return

        prompt_template = self.txt_p_single.toPlainText() if mode == "single" else self.txt_p_opt.toPlainText()
        if "{source_text}" not in prompt_template:
            QMessageBox.warning(self, "คำเตือน", "Prompt ของคุณไม่มีแท็ก '{source_text}' AI จะไม่ได้รับข้อความทดสอบ!")
            return

        final_prompt = prompt_template.replace("{source_text}", test_text).replace("{id}", "TEST_001")

        self.txt_test_result.setPlainText("⏳ กำลังส่งคำสั่งไปยังโมเดล AI เพื่อแปลผลสด... กรุณารอสักครู่")
        cfg = TStudioCore.load_config()
        is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")

        def do_translate():
            return CoreAI.generate_content(cfg, final_prompt, is_local=is_local)

        def on_success(res):
            try:
                if self.isVisible():
                    self.txt_test_result.setPlainText(res.strip())
                    self.lbl_status.setText("ทดสอบ AI Prompt สำเร็จ")
            except RuntimeError:
                pass

        def on_error(err):
            try:
                if self.isVisible():
                    self.txt_test_result.setPlainText(f"❌ เกิดข้อผิดพลาดในการทดสอบ:\n{err}")
                    self.lbl_status.setText("เกิดข้อผิดพลาดในการทดสอบ AI Prompt")
            except RuntimeError:
                pass

        worker = ApiWorker(do_translate)
        worker.signals.finished.connect(on_success)
        worker.signals.error.connect(on_error)
        QThreadPool.globalInstance().start(worker)

    def closeEvent(self, event):
        if getattr(self, '_prompts_modified', False):
            reply = QMessageBox.question(
                self, 'บันทึกการเปลี่ยนแปลง?',
                "คุณมีการแก้ไขใน AI Prompt Studio ที่ยังไม่ได้บันทึก ต้องการบันทึกก่อนปิดหรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._save_profile_prompts(show_msg=False)
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    # -------------------------------------------------------------
    # LOGIC: INTERNAL CSV ENTITY SCANNER
    # -------------------------------------------------------------
    def _scan_entities_from_csv(self, silent=False):
        """Scans the active translation workspace, project data, and loaded CSV for candidate game entities."""
        source_sentences = []

        # 1. Try to read from main_app table model if present
        if self.main_app and hasattr(self.main_app, 'model') and hasattr(self.main_app.model, '_data'):
            for item in self.main_app.model._data:
                if isinstance(item, dict):
                    src = item.get("source") or item.get("Source") or item.get("English") or ""
                    if src:
                        source_sentences.append(str(src))

        # 2. If table is empty, try current CSV file
        if not source_sentences:
            curr_csv = getattr(self.main_app, 'csv_path', None) or getattr(self.main_app, 'current_csv_file', None)
            if curr_csv and os.path.exists(curr_csv):
                try:
                    with open(curr_csv, 'r', encoding='utf-8', errors='ignore') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if len(row) > 1:
                                # Standard TStudio CSV: row[0]=ID, row[1]=COL_SOURCE
                                source_sentences.append(row[1])
                except Exception:
                    pass

        # 3. Include Lore Notes if available
        lore_txt = self.txt_lore_content.toPlainText().strip()
        if lore_txt:
            source_sentences.extend(lore_txt.splitlines())

        # 4. If still empty, prompt file dialog (unless silent mode)
        if not source_sentences and not silent:
            target_dir = TStudioCore.get_translation_workspace_dir(
                hint_path=getattr(self.main_app, 'csv_path', None) if self.main_app else None,
                profile_name=getattr(self, 'active_profile', None)
            )
            file_path, _filter = QFileDialog.getOpenFileName(
                self, "เลือกไฟล์ CSV สำหรับสแกนคำเฉพาะ", target_dir, "CSV Files (*.csv);;All Files (*.*)"
            )
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if len(row) > 1:
                                source_sentences.append(row[1])
                except Exception as e:
                    QMessageBox.warning(self, "ข้อผิดพลาด", f"ไม่สามารถเปิดไฟล์ CSV: {e}")
                    return

        if not source_sentences:
            if not silent:
                QMessageBox.information(self, "ไม่พบข้อมูล", "ไม่พบข้อมูลบทสนทนาหรือไฟล์ CSV สำหรับการสแกน")
            return

        # Query existing glossary terms to exclude from candidates
        prof = TStudioCore.get_current_profile_data(self.active_profile)
        curr_glossary = prof.get("glossary", {}) if isinstance(prof.get("glossary"), dict) else {}
        existing_terms = list(curr_glossary.keys()) + [item.get("en", "") for item in self.staged_terms if item.get("en")]

        mode = self.cbo_extract_mode.currentData() if hasattr(self, 'cbo_extract_mode') else "essential"
        if mode == "essential":
            max_limit = min(max(self.spn_term_count.value(), 10), 50)
        elif mode == "deep":
            max_limit = 100
        elif mode == "auto":
            max_limit = 350
        else:  # custom
            max_limit = self.spn_term_count.value()

        top_candidates = extract_game_entity_candidates(
            source_sentences,
            existing_terms=existing_terms,
            max_candidates=max_limit,
            lore_text=lore_txt
        )

        formatted_entities = "\n".join(f"- {term}" for term in top_candidates)
        self.txt_candidate_entities.setText(formatted_entities)
        self.lbl_csv_status.setText(f"📄 สแกนสำเร็จ: พบคำเฉพาะทางและชื่อเฉพาะ {len(top_candidates)} คำ จากข้อความ {len(source_sentences)} แถว")
        if not silent:
            QMessageBox.information(
                self, "สแกนสำเร็จ",
                f"สแกนพบคำเฉพาะทาง ตัวละคร สถานที่ และไอเท็มเฉพาะ {len(top_candidates)} คำ!\n"
                f"(ผ่านการกรองคำทั่วไปและ EULA ออกเรียบร้อยแล้ว)\n\n"
                f"ข้อมูลถูกนำไปใส่ในช่อง 'คำนามเฉพาะที่สแกนพบ' เรียบร้อยแล้ว พร้อมสำหรับการสกัดด้วย AI"
            )

    # -------------------------------------------------------------
    # LOGIC: WEB / WIKI FETCHER
    # -------------------------------------------------------------
    def _fetch_wiki_url(self):
        url = self.txt_url.text().strip()
        if not url:
            QMessageBox.warning(self, "แจ้งเตือน", "กรุณาวาง URL ของวิกิหรือหน้าเว็บที่ต้องการดึงข้อมูลก่อน")
            return

        self.btn_fetch_url.setEnabled(False)
        self.btn_fetch_url.setText("⏳ กำลังดึง...")
        self.progress_bar.show()
        self.lbl_status.setText("กำลังเชื่อมต่อดึงข้อมูลผ่าน Jina Reader...")

        def do_fetch():
            jina_url = "https://r.jina.ai/" + url
            req = urllib.request.Request(jina_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw_text = resp.read().decode('utf-8', errors='replace')
                return raw_text

        def on_success(content):
            self.btn_fetch_url.setEnabled(True)
            self.btn_fetch_url.setText("🌐 Fetch via Jina Reader")
            self.progress_bar.hide()
            self.lbl_status.setText("ดึงข้อมูลหน้าเว็บสำเร็จ")

            # Clean and truncate if excessively large
            cleaned = content[:20000]
            current_lore = self.txt_lore_content.toPlainText().strip()
            if current_lore:
                self.txt_lore_content.setText(current_lore + "\n\n--- WIKI CONTENT ---\n" + cleaned)
            else:
                self.txt_lore_content.setText(cleaned)

            QMessageBox.information(self, "ดึงข้อมูลสำเร็จ", f"ดึงข้อมูลบริบทจากหน้าเว็บเรียบร้อย ({len(cleaned)} ตัวอักษร)!")

        def on_error(err):
            self.btn_fetch_url.setEnabled(True)
            self.btn_fetch_url.setText("🌐 Fetch via Jina Reader")
            self.progress_bar.hide()
            self.lbl_status.setText("เกิดข้อผิดพลาดในการดึงหน้าเว็บ")
            QMessageBox.warning(self, "ข้อผิดพลาด", f"ไม่สามารถดึงข้อมูลจาก URL:\n{err}")

        worker = ApiWorker(do_fetch)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)

    # -------------------------------------------------------------
    # LOGIC: GEMINI WEB LIVE RESEARCH & AI LORE SCOUT
    # -------------------------------------------------------------
    def _launch_gemini_web_lore_workflow(self):
        """
        Gemini Web Live Lore Research Bridge:
        Generates a Google Search-grounded prompt, copies it to the clipboard,
        and launches https://gemini.google.com/app in the default web browser.
        Eliminates hallucination ('เขียนไปเรื่อย') by grounding research in Google Search facts,
        and forces an exhaustive breakdown of Main Characters, Proper Locations, and Unique Items + Master Glossary Table.
        """
        game_title = self.active_profile
        if game_title.lower() in ("default", "none", ""):
            from PyQt6.QtWidgets import QInputDialog
            text, ok = QInputDialog.getText(self, "ระบุชื่อเกม", "กรุณาระบุชื่อเกมที่ต้องการให้ Gemini Web ค้นคว้าและเขียนบทสรุป:")
            if not ok or not text.strip():
                return
            game_title = text.strip()

        tone = self.cbo_universe_tone.currentText().strip()
        category = self.cbo_tone_category.currentText().strip()
        pronoun = self.cbo_pronouns.currentText().strip()

        sample_texts, file_path, proj_dir = self._collect_detection_sample_texts()
        dialogue_samples = collect_stratified_dialogue_samples(sample_texts, max_samples=12)
        sample_str = "\n".join([f"- \"{s}\"" for s in dialogue_samples[:10]]) if dialogue_samples else "(ไม่มีตัวอย่างบทสนทนาในเวิร์กสเปซ)"

        prompt = (
            f"คุณคือผู้เชี่ยวชาญด้าน Video Game Lore, Worldbuilding และ Narrative Localization มือหนึ่ง\n"
            f"ช่วยค้นคว้าข้อมูลจริงจากอินเทอร์เน็ต (ผ่าน Google Search) และจัดทำ 'สารบบสรุปเนื้อเรื่อง ภูมิหลังโลก และคลังศัพท์เฉพาะครบวงจร (Master Lore & Glossary Dossier)' สำหรับเกมนี้:\n\n"
            f"🎮 **ชื่อเกม:** \"{game_title}\"\n"
            f"📂 **หมวดหมู่เกม:** {category}\n"
            f"🎨 **โทนจักรวาลที่คาดหวัง:** {tone}\n"
            f"👥 **แนวทางสรรพนาม:** {pronoun}\n\n"
            f"📜 **ตัวอย่างข้อความ / บทสนทนาจริงจากไฟล์เกม:**\n"
            f"{sample_str}\n\n"
            f"═══════════════════════════════════════════════════════════════════════════\n"
            f"🛡️ **กฎเหล็กป้องกันการหลอนข้อมูล & ความครบถ้วนสมบูรณ์ (Zero Hallucination & Exhaustive Entity Directive):**\n"
            f"1. กรุณาใช้ Google Search ค้นคว้าข้อมูลจริงจาก Wiki / Fandom / Steam Store / บทสรุปทางการของเกมนี้\n"
            f"2. ห้ามแต่งเรื่องเองเด็ดขาด ห้ามเดา ห้ามเขียนไปเรื่อย หากข้อมูลส่วนไหนไม่มีให้ระบุตรงๆ\n"
            f"3. **สำคัญมาก:** ต้องรวบรวม **ชื่อตัวละครหลักและตัวละครสำคัญทั้งหมด**, **สถานที่ที่เป็นชื่อเฉพาะทั้งหมด**, และ **ไอเท็ม/เทคโนโลยี/อาวุธชื่อเฉพาะที่มีในเกม (ชื่อไม่เหมือนของทั่วไป)** มาให้ครบถ้วน เพื่อที่ระบบ TLM จะนำไปสกัดทำเป็น Glossary ทันที!\n"
            f"═══════════════════════════════════════════════════════════════════════════\n\n"
            f"กรุณาจัดทำสรุปเป็นภาษาไทยที่กระชับ ลุ่มลึก และถูกต้อง โดยครอบคลุม 7 หัวข้อหลักดังนี้:\n\n"
            f"1. **เซตติ้งและยุคสมัยของโลก (World Setting & Era):**\n"
            f"   - บรรยากาศ ประวัติศาสตร์ย่อ และเทคโนโลยี/เวทมนตร์หลักของโลกในเกมนี้\n\n"
            f"2. **เนื้อเรื่องย่อและปมขัดแย้งหลัก (Story Premise & Core Conflict):**\n"
            f"   - จุดเริ่มต้นของเรื่อง ชะตากรรมของตัวเอก และศัตรู/วิกฤตการณ์หลัก\n\n"
            f"3. **รายชื่อตัวละครหลักและตัวละครสำคัญทั้งหมด (All Main & Key Characters - หมวด Person):**\n"
            f"   - ลิสต์ตัวละครหลัก ตัวละครในทีม บอส และ NPC สำคัญทั้งหมดในรูปแบบ: `English Name (คำทับศัพท์ไทย): เพศ, บทบาท, ลักษณะนิสัย และสรรพนามที่ใช้`\n"
            f"   - หากตัวละครมีทั้งชื่อเต็มและชื่อเรียกสั้น/ฉายาในบทสนทนา (เช่น `John Taylor` และ `Taylor`) ให้ระบุทั้งคู่\n\n"
            f"4. **สถานที่ที่เป็นชื่อเฉพาะและฝ่าย/องค์กรสำคัญ (Proper-Noun Locations & Major Factions - หมวด Location / Faction):**\n"
            f"   - ลิสต์ชื่อเมือง ฐานทัพ สถานี ดันเจี้ยน ดินแดน และองค์กร/ฝ่ายทั้งหมดในรูปแบบ: `English Name (คำแปล/ทับศัพท์ไทย): คำอธิบายสั้นๆ`\n\n"
            f"5. **ไอเท็มชื่อเฉพาะ เทคโนโลยีพิเศษ และอาวุธเอกลักษณ์ (Unique Proper-Noun Items, Tech & Signature Weapons - หมวด Item / Weapon):**\n"
            f"   - ลิสต์เฉพาะไอเท็มที่มีชื่อเฉพาะในเกม (ชื่อไม่เหมือนของปกติทั่วไป), อุปกรณ์พิเศษ, ชิป/ไซเบอร์เนติกส์, วัตถุโบราณ, สกุลเงินเฉพาะ, และอาวุธชื่อเฉพาะ ในรูปแบบ: `English Name (คำแปล/ทับศัพท์ไทย): คำอธิบายสั้นๆ` (ห้ามเอาคำนามทั่วไป เช่น Sword, Rifle, Potion, Door)\n\n"
            f"6. **ทิศทางการแปลภาษาไทยและระบบสรรพนาม (Thai Localization & Pronoun Guide):**\n"
            f"   - สรรพนามที่ควรใช้ระหว่างตัวละคร ระดับภาษา (ทางการ/สแลง/กวน/โบราณ) และข้อควรระวังสำคัญ\n\n"
            f"7. **ตารางคลังคำศัพท์หลักพร้อมนำเข้า Glossary (Master Glossary Table - บังคับต้องมี!):**\n"
            f"   - สรุปรวมคำศัพท์จากข้อ 3, 4, 5 ทั้งหมดลงในตาราง Markdown ที่มี 4 คอลัมน์เป๊ะๆ ดังนี้:\n"
            f"   `| English Term | คำแปลไทย | Category | คำอธิบายสั้นๆ |`\n"
            f"   - โดยช่อง `Category` ให้ระบุค่าใดค่าหนึ่งจาก: `Person`, `Location`, `Faction`, `Item`, `Weapon`, `Quest`, `General`\n"
            f"   - สำหรับตัวละครหลักที่มีชื่อ-นามสกุล (เช่น `John Taylor`) ให้แยกแถวชื่อเรียกสั้นที่ใช้คุยกันในเกม (เช่น `Taylor`) มาให้ด้วย เพื่อให้ระบบจับคู่คำในบทสนทนาได้ครบ 100%!\n"
        )

        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(prompt)

        gemini_url = "https://gemini.google.com/app"
        try:
            import webbrowser
            webbrowser.open(gemini_url)
        except Exception as e:
            print(f"[Gemini Web Bridge] Error opening browser: {e}")

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("🌐 เชื่อมต่อ Gemini Web สำเร็จ!")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(
            f"<b>🚀 คัดลอก Prompt สรุปเนื้อเรื่อง + สกัดตัวละคร/สถานที่/ไอเท็มเฉพาะ ลงคลิปบอร์ดแล้ว!</b><br><br>"
            f"<b>ขั้นตอนการใช้งาน:</b><br>"
            f"1. สลับไปที่หน้าต่างเบราว์เซอร์ <b>Gemini Web</b> ที่เพิ่งเปิดขึ้นมา<br>"
            f"2. กด <b>[Ctrl + V]</b> เพื่อวาง Prompt และกดส่งให้ Gemini ค้นคว้าด้วย Google Search<br>"
            f"3. เมื่อ Gemini เขียนสรุปและสร้างตาราง Glossary เสร็จ ให้กดปุ่ม <b>'Copy'</b> ในหน้าเว็บ<br>"
            f"4. กลับมากดปุ่ม <b>'📥 นำเข้าข้อความจากคลิปบอร์ดทันที'</b> ด้านล่างนี้ ระบบจะวางบทสรุปและ<b>สกัดตัวละคร สถานที่ และไอเท็มเฉพาะเข้า Glossary ให้อัตโนมัติ!</b><br>"
        )
        btn_paste_now = msg_box.addButton("📥 นำเข้าข้อความจากคลิปบอร์ดทันที", QMessageBox.ButtonRole.AcceptRole)
        btn_reopen = msg_box.addButton("🌐 เปิด Gemini Web อีกครั้ง", QMessageBox.ButtonRole.ActionRole)
        btn_copy_again = msg_box.addButton("📋 คัดลอก Prompt อีกครั้ง", QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton("ปิดหน้าต่างนี้", QMessageBox.ButtonRole.RejectRole)

        while True:
            msg_box.exec()
            clicked_btn = msg_box.clickedButton()
            if clicked_btn == btn_paste_now:
                self._import_gemini_web_lore()
                break
            elif clicked_btn == btn_reopen:
                import webbrowser
                webbrowser.open(gemini_url)
            elif clicked_btn == btn_copy_again:
                if clipboard:
                    clipboard.setText(prompt)
                self.lbl_status.setText("📋 คัดลอก Prompt ลงคลิปบอร์ดอีกครั้งเรียบร้อย")
            else:
                break

    def _extract_lore_to_glossary(self, silent=False):
        """
        Parses self.txt_lore_content to extract all Main Characters (Full + Short Callsigns),
        Proper-Noun Locations, Factions, and Unique Items, then:
        1. Populates self.txt_candidate_entities with discovered English proper nouns.
        2. Stages all extracted (EN, TH, Tag, Context) entries into self.staged_terms (Tab 3).
        3. Automatically merges new terms into the active profile's Glossary (prof['glossary']) so no term is left behind!
        """
        lore_text = self.txt_lore_content.toPlainText().strip()
        if not lore_text:
            if not silent:
                QMessageBox.warning(self, "ไม่มีข้อมูลเนื้อเรื่อง", "กรุณาวางหรือสร้างบทสรุปเนื้อเรื่อง (Lore Notes) ก่อนสกัดคำศัพท์เข้า Glossary")
            return 0, 0

        glossary_items, candidate_entities = parse_lore_glossary_and_entities(lore_text)

        # Update Candidate Entities box (merge with existing lines without duplicates)
        existing_cand_lines = []
        seen_c = set()
        cur_cand_txt = self.txt_candidate_entities.toPlainText().strip()
        if cur_cand_txt:
            for ln in cur_cand_txt.splitlines():
                c_clean = re.sub(r'^(?:[-*•]|\d+\.)\s*', '', ln.strip()).strip()
                if c_clean and c_clean.lower() not in seen_c:
                    seen_c.add(c_clean.lower())
                    existing_cand_lines.append(c_clean)

        for c_ent in candidate_entities:
            if c_ent.lower() not in seen_c:
                seen_c.add(c_ent.lower())
                existing_cand_lines.append(c_ent)

        if existing_cand_lines:
            self.txt_candidate_entities.setText("\n".join(f"- {c}" for c in existing_cand_lines))

        if not glossary_items:
            if not silent:
                QMessageBox.information(
                    self, "ผลการสกัดจากบทสรุป",
                    f"สแกนพบคำนามเฉพาะภาษาอังกฤษ {len(candidate_entities)} คำ และนำเข้าช่อง Candidate Entities แล้ว\n"
                    f"(ไม่พบคู่คำแปลไทยในวงเล็บหรือตาราง คุณสามารถกดปุ่ม '🚀 เริ่ม AI สกัดและบัญญัติศัพท์เชิงลึก' เพื่อแปลต่อได้ทันที)"
                )
            return 0, len(candidate_entities)

        prof_name = self.active_profile
        prof = TStudioCore.get_current_profile_data(prof_name)
        curr_glossary = copy.deepcopy(prof.get("glossary", {})) if isinstance(prof.get("glossary"), dict) else {}
        existing_lower = {str(k).strip().lower(): str(k).strip() for k in curr_glossary.keys() if str(k).strip()}
        staged_lower = {str(item.get("en", "")).strip().lower() for item in self.staged_terms if str(item.get("en", "")).strip()}

        added_to_staged = 0
        cat_counts = {}

        for g_item in glossary_items:
            en = g_item["en"].strip()
            th = g_item["th"].strip()
            tag = g_item.get("tag", "General")
            ctx = g_item.get("context", "")
            alt = g_item.get("alt", "")
            en_low = en.lower()

            if en_low in GENERIC_MULTIWORD_BLACKLIST:
                continue

            cat_counts[tag] = cat_counts.get(tag, 0) + 1

            if en_low not in staged_lower:
                staged_lower.add(en_low)
                self.staged_terms.append({
                    "en": en,
                    "th": th,
                    "tag": tag,
                    "context": ctx,
                    "alt": alt,
                    "checked": True
                })
                added_to_staged += 1

        self._save_profile_lore_data(silent=True)
        self._render_staging_table()
        self._refresh_profile_stat_badge()

        # Switch to Tab 3 (Staging Review Grid) so user can review and approve
        if hasattr(self, 'tab_widget'):
            self.tab_widget.setCurrentIndex(2)

        cat_summary = ", ".join(f"{k}: {v}" for k, v in sorted(cat_counts.items(), key=lambda x: -x[1]))
        self.lbl_status.setText(
            f"📥 สกัดคำเข้าตะกร้าตรวจสอบ (Tab 3) สำเร็จ {len(glossary_items)} คำ ({cat_summary}) — รอการตรวจสอบและผสานเข้า Glossary"
        )

        if not silent:
            QMessageBox.information(
                self, "📚 สกัดคำศัพท์เข้าตะกร้าตรวจสอบสำเร็จ!",
                f"<b>✅ สกัดชื่อตัวละคร สถานที่เฉพาะ และไอเท็มพิเศษเข้าตะกร้าตรวจสอบ (Tab 3) แล้ว!</b><br><br>"
                f"• <b>สกัดคำศัพท์ได้ทั้งหมด:</b> {len(glossary_items)} คำ ({cat_summary})<br>"
                f"• <b>เพิ่มในตะกร้าตรวจสอบ:</b> +{added_to_staged} คำใหม่<br><br>"
                f"<i>กรุณาตรวจสอบความถูกต้องในหน้าต่างนี้ แล้วกดปุ่ม <b>'📥 ผสานเข้าคลังคำศัพท์โปรไฟล์'</b> ด้านล่าง เพื่อยืนยันและนำคำศัพท์เข้าใช้งานจริง</i>"
            )

        return len(glossary_items), added_to_staged

    def _import_gemini_web_lore(self):
        """Pastes lore synopsis copied from Gemini Web directly into txt_lore_content and extracts entities into Tab 3 staging review."""
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip() if clipboard else ""

        if not text:
            QMessageBox.warning(self, "คลิปบอร์ดว่างเปล่า", "ไม่พบข้อความในคลิปบอร์ด กรุณากด Copy จาก Gemini Web ก่อนนำเข้า")
            return

        # Anti-Self-Ingestion Guard: Block user from pasting the research prompt template back into lore
        prompt_signals = [
            "คุณคือผู้เชี่ยวชาญ",
            "Master Lore & Glossary Dossier",
            "Zero Hallucination & Exhaustive Entity Directive",
            "สารบบสรุปเนื้อเรื่อง ภูมิหลังโลก",
            "ตารางคลังคำศัพท์หลักพร้อมนำเข้า Glossary",
            "### DIRECTIVES MATRIX:",
            "### CANDIDATE TERMS TO PROCESS:"
        ]
        if any(sig in text for sig in prompt_signals):
            QMessageBox.warning(
                self, "ตรวจพบ Prompt แม่แบบ (ไม่ใช่ผลลัพธ์)",
                "⚠️ <b>ข้อความในคลิปบอร์ดคือ 'Prompt แม่แบบสำหรับค้นคว้า' ไม่ใช่คำตอบจาก Gemini!</b><br><br>"
                "<b>วิธีแก้ไขที่ถูกต้อง:</b><br>"
                "1. นำ Prompt นี้ไปวางและกดส่งในหน้าต่าง <b>Gemini Web</b> (หรือ ChatGPT)<br>"
                "2. รอให้ AI ค้นคว้าและเขียนบทสรุปเนื้อเรื่องจนเสร็จสมบูรณ์<br>"
                "3. กด <b>Copy (คัดลอก)</b> เฉพาะ <u>คำตอบที่ AI ตอบกลับมา</u><br>"
                "4. กลับมากดปุ่ม <b>'📥 วางจาก Gemini Web'</b> อีกครั้ง"
            )
            return

        if len(text) < 30:
            res = QMessageBox.question(
                self, "ข้อความสั้นเกินไป",
                f"ข้อความในคลิปบอร์ดมีเพียง {len(text)} ตัวอักษร:\n'{text}'\nต้องการนำเข้าหรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if res != QMessageBox.StandardButton.Yes:
                return

        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        cleaned = re.sub(r'^```markdown\s*|^```\s*|```$', '', cleaned, flags=re.MULTILINE).strip()

        cur = self.txt_lore_content.toPlainText().strip()
        if cur:
            res = QMessageBox.question(
                self, "เลือกรูปแบบการนำเข้า",
                "มีข้อความเนื้อเรื่องเดิมอยู่ในช่องแล้ว ต้องการนำเข้าแบบใด?\n\n"
                "- กด 'Yes' เพื่อต่อท้ายข้อความเดิม (Append)\n"
                "- กด 'No' เพื่อแทนที่ข้อความเดิมทั้งหมด (Replace)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if res == QMessageBox.StandardButton.Cancel:
                return
            elif res == QMessageBox.StandardButton.Yes:
                self.txt_lore_content.setPlainText(cur + f"\n\n--- 🌐 GEMINI WEB LORE DOSSIER: {self.active_profile} ---\n" + cleaned)
            else:
                self.txt_lore_content.setPlainText(cleaned)
        else:
            self.txt_lore_content.setPlainText(cleaned)

        extracted_total, added_staged = self._extract_lore_to_glossary(silent=True)
        self.lbl_status.setText(f"📥 นำเข้าเนื้อเรื่องจาก Gemini Web ({len(cleaned)} ตัวอักษร) และส่งคำศัพท์เข้าตะกร้าตรวจสอบ {extracted_total} คำ (+{added_staged} คำใหม่)")
        QMessageBox.information(
            self, "นำเข้าและเตรียมคำศัพท์ในตะกร้าตรวจสอบแล้ว",
            f"<b>✅ นำเข้าข้อมูล Lore จาก Gemini Web และส่งคำศัพท์เข้าตะกร้าตรวจสอบ (Tab 3) แล้ว!</b><br><br>"
            f"• <b>จำนวนตัวอักษรบทสรุป:</b> {len(cleaned):,} ตัวอักษร<br>"
            f"• <b>สกัดตัวละคร/สถานที่/ไอเท็มเฉพาะ:</b> {extracted_total} คำ<br>"
            f"• <b>เพิ่มในตะกร้าตรวจสอบ (Tab 3):</b> +{added_staged} คำใหม่<br><br>"
            f"<i>ระบบเปิดหน้า <b>ตะกร้าตรวจสอบคำศัพท์ (Tab 3)</b> ให้คุณเรียบร้อยแล้ว กรุณาตรวจสอบคำศัพท์และกดปุ่ม '📥 ผสานเข้าคลังคำศัพท์โปรไฟล์' เพื่อบันทึกคำศัพท์ที่ผ่านการตรวจเข้าสู่ Glossary</i>"
        )

    def _generate_ai_lore(self):
        """Uses AI to automatically research and draft a comprehensive lore synopsis + Master Glossary Table for the active game profile."""
        game_title = self.active_profile
        if game_title.lower() in ("default", "none", ""):
            from PyQt6.QtWidgets import QInputDialog
            text, ok = QInputDialog.getText(self, "ระบุชื่อเกม", "กรุณาระบุชื่อเกมที่ต้องการให้ AI สรุปเนื้อเรื่อง:")
            if not ok or not text.strip():
                return
            game_title = text.strip()

        cfg = TStudioCore.load_config()
        if not cfg.get("api_key") and not (cfg.get("provider") == "Local LLM" or cfg.get("model") == "custom-local-llm") and not cfg.get("google_key") and not cfg.get("openai_key") and not cfg.get("deepseek_key"):
            QMessageBox.warning(self, "ยังไม่ได้ตั้งค่า API Key", "กรุณาตั้งค่า API Key ใน Settings ก่อนเริ่มเจนเนื้อเรื่อง")
            return

        tone = self.cbo_universe_tone.currentText().strip()
        self.btn_ai_scout_lore.setEnabled(False)
        self.btn_ai_scout_lore.setText("⏳ กำลังวิเคราะห์และสรุปเนื้อเรื่อง...")
        self.progress_bar.show()
        self.lbl_status.setText(f"AI กำลังค้นคว้าและสรุปภูมิหลัง + ตัวละคร/สถานที่/ไอเท็มเฉพาะของเกม '{game_title}'...")

        scout_prompt = (
            f"You are a master video game lore archivist, narrative designer, and Thai localization director.\n"
            f"Please conduct an in-depth lore briefing, entity catalog, and worldbuilding synthesis for the video game: '{game_title}'.\n"
            f"Tone/Universe Preference: {tone}\n\n"
            f"CRITICAL: Ground your research in factual canonical lore from official wiki or game sources. Do NOT hallucinate.\n"
            f"You MUST exhaustively list ALL main & key characters, ALL proper-noun locations & factions, and ALL unique proper-noun items/weapons so our system can automatically build a complete Localization Glossary.\n\n"
            f"Please format your output in clean, readable Thai (with English proper nouns in parentheses) covering these 7 sections:\n"
            f"1. **เซตติ้งและยุคสมัยของโลก (World Setting & Era)**: บรรยากาศ ประวัติศาสตร์ย่อ และเทคโนโลยี/เวทมนตร์หลัก\n"
            f"2. **เนื้อเรื่องย่อและปมขัดแย้งหลัก (Story Premise & Core Conflict)**: จุดเริ่มต้นของเรื่อง ชะตากรรมของตัวเอก และศัตรู\n"
            f"3. **รายชื่อตัวละครหลักและตัวละครสำคัญทั้งหมด (All Main & Key Characters - Person)**: ลิสต์ตัวละครหลัก ทีมตัวเอก บอส และ NPC สำคัญทั้งหมดในรูปแบบ `- English Name (คำทับศัพท์ไทย): บทบาท เพศ และสรรพนามที่ใช้` (ระบุทั้งชื่อเต็มและชื่อสั้นที่ใช้เรียกในบทสนทนา)\n"
            f"4. **สถานที่ที่เป็นชื่อเฉพาะและฝ่าย/องค์กรสำคัญ (Proper-Noun Locations & Factions - Location / Faction)**: ลิสต์ชื่อเมือง ฐานทัพ สถานี ดินแดน ดันเจี้ยน และองค์กรทั้งหมดในรูปแบบ `- English Name (คำแปล/ทับศัพท์ไทย): คำอธิบาย`\n"
            f"5. **ไอเท็มชื่อเฉพาะ เทคโนโลยีพิเศษ และอาวุธเอกลักษณ์ (Unique Proper-Noun Items & Weapons - Item / Weapon)**: ลิสต์เฉพาะไอเท็มที่มีชื่อเฉพาะในเกม (ชื่อไม่เหมือนของปกติทั่วไป) ชิป/อุปกรณ์พิเศษ วัตถุโบราณ สกุลเงิน และอาวุธชื่อเฉพาะ ในรูปแบบ `- English Name (คำแปล/ทับศัพท์ไทย): คำอธิบาย`\n"
            f"6. **ทิศทางการแปลภาษาไทย (Localization Tone & Pronoun Guide)**: คำแนะนำเรื่องระดับภาษาและระบบสรรพนามระหว่างตัวละคร\n"
            f"7. **ตารางคลังคำศัพท์หลัก (Master Glossary Table)**: สรุปรวมคำศัพท์จากข้อ 3, 4, 5 ทั้งหมดลงในตาราง Markdown 4 คอลัมน์:\n"
            f"   `| English Term | คำแปลไทย | Category | คำอธิบายสั้นๆ |`\n"
            f"   (โดย Category คือ Person, Location, Faction, Item, Weapon, Quest, หรือ General)\n\n"
            f"Provide rich, concrete, accurate details without fluff. Return clean Markdown."
        )

        def do_scout():
            is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")
            # Enable search grounding for Gemini models to prevent hallucination
            return CoreAI.generate_content(cfg, scout_prompt, is_local=is_local, use_search_grounding=True)

        def on_success(res):
            self.btn_ai_scout_lore.setEnabled(True)
            self.btn_ai_scout_lore.setText("🤖 AI สรุปเนื้อเรื่องอัตโนมัติ")
            self.progress_bar.hide()

            clean_res = re.sub(r'<think>.*?</think>', '', res, flags=re.DOTALL).strip()
            clean_res = re.sub(r'^```markdown\s*|^```\s*|```$', '', clean_res, flags=re.MULTILINE).strip()

            cur = self.txt_lore_content.toPlainText().strip()
            if cur:
                self.txt_lore_content.setPlainText(cur + f"\n\n--- AI LORE BRIEFING: {game_title} ---\n" + clean_res)
            else:
                self.txt_lore_content.setPlainText(clean_res)

            extracted_total, added_new = self._extract_lore_to_glossary(silent=True)
            self.lbl_status.setText(f"สร้างสรุปเนื้อเรื่อง '{game_title}' สำเร็จ และสกัดคำศัพท์เข้า Glossary {extracted_total} คำ (+{added_new} คำใหม่)!")
            QMessageBox.information(
                self, "สำเร็จ",
                f"<b>✅ AI สรุปเนื้อเรื่องและสกัดคำศัพท์ของ '{game_title}' เรียบร้อยแล้ว!</b><br><br>"
                f"• <b>ความยาวบทสรุป:</b> {len(clean_res):,} ตัวอักษร<br>"
                f"• <b>สกัดตัวละคร/สถานที่/ไอเท็มเฉพาะเข้า Glossary:</b> {extracted_total} คำ (+{added_new} คำใหม่ในโปรไฟล์)"
            )

        def on_error(err):
            self.btn_ai_scout_lore.setEnabled(True)
            self.btn_ai_scout_lore.setText("🤖 AI สรุปเนื้อเรื่องอัตโนมัติ")
            self.progress_bar.hide()
            self.lbl_status.setText("เกิดข้อผิดพลาดในการสรุปเนื้อเรื่อง")
            QMessageBox.critical(self, "AI Error", f"ไม่สามารถสรุปเนื้อเรื่องจาก AI ได้:\n{err}")

        worker = ApiWorker(do_scout)
        forwarder = ThreadSafeWorkerSignalsForwarder(on_success, on_error, self)
        worker.signals.finished.connect(forwarder.handle_finished)
        worker.signals.error.connect(forwarder.handle_error)
        QThreadPool.globalInstance().start(worker)

    def _import_lore_file(self):
        target_dir = TStudioCore.get_translation_workspace_dir(
            hint_path=getattr(self.main_app, 'csv_path', None) if self.main_app else None,
            profile_name=getattr(self, 'active_profile', None)
        )
        file_path, _ = QFileDialog.getOpenFileName(
            self, "นำเข้าไฟล์เนื้อเรื่อง", target_dir, "Text Files (*.txt *.md *.json);;All Files (*.*)"
        )
        if not file_path: return
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            cur = self.txt_lore_content.toPlainText().strip()
            if cur:
                self.txt_lore_content.setPlainText(cur + "\n\n--- IMPORTED FILE: " + os.path.basename(file_path) + " ---\n" + content)
            else:
                self.txt_lore_content.setPlainText(content)
            extracted_total, added_new = self._extract_lore_to_glossary(silent=True)
            self.lbl_status.setText(f"นำเข้าไฟล์ '{os.path.basename(file_path)}' สำเร็จ (สกัดคำเข้า Glossary {extracted_total} คำ, ใหม่ +{added_new} คำ)")
        except Exception as e:
            QMessageBox.warning(self, "ข้อผิดพลาด", f"ไม่สามารถอ่านไฟล์ได้: {e}")

    def _export_lore_file(self):
        text = self.txt_lore_content.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "ไม่มีข้อมูล", "ยังไม่มีเนื้อหาเนื้อเรื่องให้บันทึก")
            return
        target_dir = TStudioCore.get_translation_workspace_dir(
            hint_path=getattr(self.main_app, 'csv_path', None) if self.main_app else None,
            profile_name=getattr(self, 'active_profile', None)
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self, "บันทึกเนื้อเรื่องลงไฟล์", os.path.join(target_dir, f"{self.active_profile}_Lore.txt"), "Text Files (*.txt);;Markdown (*.md);;All Files (*.*)"
        )
        if not file_path: return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            self.lbl_status.setText(f"บันทึกไฟล์เรียบร้อย: {os.path.basename(file_path)}")
            QMessageBox.information(self, "บันทึกสำเร็จ", f"บันทึกเนื้อเรื่องลงในไฟล์ {file_path} เรียบร้อยแล้ว")
        except Exception as e:
            QMessageBox.warning(self, "ข้อผิดพลาด", f"ไม่สามารถบันทึกไฟล์ได้: {e}")

    def _clear_lore_content(self):
        if not self.txt_lore_content.toPlainText().strip(): return
        res = QMessageBox.question(self, "ยืนยันการล้างข้อมูล", "คุณแน่ใจหรือไม่ว่าต้องการล้างข้อความเนื้อเรื่องทั้งหมด?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if res == QMessageBox.StandardButton.Yes:
            self.txt_lore_content.clear()
            self.lbl_status.setText("ล้างข้อมูลเนื้อเรื่องเรียบร้อย")

    # -------------------------------------------------------------
    # LOGIC: CUSTOM RULES & CSV VARIABLE GUARDS
    # -------------------------------------------------------------
    def _scan_csv_variables_and_build_rules(self):
        """Scans project dialogue/CSV data, catalogs all variable placeholders & formatting tags,
        and synthesizes ironclad variable protection rules into txt_custom_rules."""
        source_sentences = []
        if self.main_app and hasattr(self.main_app, 'model') and self.main_app.model:
            source_sentences = [row.get("source", "") for row in self.main_app.model._data if row.get("source")]

        if not source_sentences:
            csv_path = getattr(self.main_app, 'csv_path', None) if self.main_app else None
            if not csv_path or not os.path.exists(csv_path):
                try:
                    from tstudio_app import CSV_PATH
                    csv_path = CSV_PATH
                except Exception:
                    csv_path = None
            if csv_path and os.path.exists(csv_path):
                try:
                    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            src = row.get("source") or row.get("Source") or row.get("English") or ""
                            if src: source_sentences.append(src)
                except Exception:
                    pass

        if not source_sentences:
            QMessageBox.warning(self, "ไม่พบข้อมูล CSV", "ไม่พบไฟล์ CSV หรือตารางแปลในโปรเจกต์ กรุณาเปิดไฟล์งานแปลก่อนทำการสแกนตัวแปร")
            return

        curly_vars = set()
        bracket_tags = set()
        xml_tags = set()
        printf_tags = set()
        escape_tags = set()
        script_vars = set()

        re_curly = re.compile(r'\{[A-Za-z0-9_.:\-]+\}')
        re_bracket = re.compile(r'\[[A-Za-z0-9_:=#/\s\-]+\]')
        re_xml = re.compile(r'<[/A-Za-z0-9_:=#"\'.\s\-]+>')
        re_printf = re.compile(r'%[0-9$]*[-+ 0#]*[0-9]*\.?[0-9]*[cdieEfgGosuxXpn%]')
        re_escape = re.compile(r'\\[nrt]')
        re_script = re.compile(r'[$@][A-Za-z0-9_]+')

        for s in source_sentences:
            for m in re_curly.findall(s): curly_vars.add(m)
            for m in re_bracket.findall(s): bracket_tags.add(m)
            for m in re_xml.findall(s): xml_tags.add(m)
            for m in re_printf.findall(s): printf_tags.add(m)
            for m in re_escape.findall(s): escape_tags.add(m)
            for m in re_script.findall(s): script_vars.add(m)

        found_types = []
        if curly_vars: found_types.append(f"วงเล็บปีกกา ({len(curly_vars)} แบบ): {', '.join(sorted(list(curly_vars))[:15])}")
        if bracket_tags: found_types.append(f"วงเล็บก้ามปู/แท็กเกม ({len(bracket_tags)} แบบ): {', '.join(sorted(list(bracket_tags))[:15])}")
        if xml_tags: found_types.append(f"แท็ก XML/สี ({len(xml_tags)} แบบ): {', '.join(sorted(list(xml_tags))[:10])}")
        if printf_tags: found_types.append(f"Printf Specifiers ({len(printf_tags)} แบบ): {', '.join(sorted(list(printf_tags))[:10])}")
        if escape_tags: found_types.append(f"Escape Codes ({len(escape_tags)} แบบ): {', '.join(sorted(list(escape_tags)))}")
        if script_vars: found_types.append(f"Script Tokens ({len(script_vars)} แบบ): {', '.join(sorted(list(script_vars))[:10])}")

        rule_lines = [
            "### กฎคุ้มครองตัวแปรและแท็กจากไฟล์ CSV (IRONCLAD VARIABLE & CODE PROTECTION):",
            "1. ห้ามแก้ไข ดัดแปลง แปลข้างใน ย้ายตำแหน่ง หรือลบตัวแปรและแท็กโค้ดต่อไปนี้เด็ดขาด ให้คงไว้ตรงตามต้นฉบับ 100%:"
        ]
        all_samples = []
        for cat_list in [curly_vars, bracket_tags, xml_tags, printf_tags, escape_tags, script_vars]:
            all_samples.extend(sorted(list(cat_list))[:8])
        if all_samples:
            rule_lines.append(f"   - ตัวแปรที่ตรวจพบในโปรเจกต์: {', '.join(all_samples[:25])}")
        rule_lines.append("2. ในกรณีที่เป็นแท็กเปิด-ปิด เช่น <color=red>...</color> หรือ <b>...</b> ให้แปลเฉพาะข้อความภายในแท็ก ห้ามเปลี่ยนชื่อแท็กเด็ดขาด")
        rule_lines.append("3. สัญลักษณ์ขึ้นบรรทัดใหม่ \\n ต้องคงไว้อย่างถูกต้อง ห้ามลบเป็นวรรคตอนเด็ดขาด")

        synthesized_rule = "\n".join(rule_lines)

        current_rules = self.txt_custom_rules.toPlainText().strip()
        if current_rules:
            self.txt_custom_rules.setPlainText(current_rules + "\n\n" + synthesized_rule)
        else:
            self.txt_custom_rules.setPlainText(synthesized_rule)

        summary_msg = f"สแกนสำเร็จจาก {len(source_sentences)} บรรทัด!\n\nตรวจพบตัวแปร:\n" + ("\n".join(found_types) if found_types else "ไม่พบตัวแปรพิเศษในไฟล์นี้")
        QMessageBox.information(self, "สร้างกฎคุ้มครองตัวแปรสำเร็จ", summary_msg)
        self.lbl_status.setText("สร้างกฎคุ้มครองตัวแปรจาก CSV สำเร็จ")

    def _populate_tones_combo(self, category=None):
        """Populates self.cbo_universe_tone with tones, optionally filtered by category."""
        prev_tone = self.cbo_universe_tone.currentText().strip()
        self.cbo_universe_tone.blockSignals(True)
        self.cbo_universe_tone.clear()

        if not category or category.startswith("✨"):
            # Show all tones grouped by category with headers
            for cat_name, tones in UNIVERSE_TONES_BY_CATEGORY.items():
                self.cbo_universe_tone.addItem(f"── {cat_name} ──")
                model = self.cbo_universe_tone.model()
                item = model.item(self.cbo_universe_tone.count() - 1)
                if item:
                    item.setEnabled(False)
                    item.setForeground(QBrush(QColor("#fab387")))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                for t in tones:
                    self.cbo_universe_tone.addItem(t)
        else:
            tones = UNIVERSE_TONES_BY_CATEGORY.get(category, [])
            for t in tones:
                self.cbo_universe_tone.addItem(t)

        # Restore previous tone if still present or select first real item
        if prev_tone:
            idx = self.cbo_universe_tone.findText(prev_tone)
            if idx >= 0:
                self.cbo_universe_tone.setCurrentIndex(idx)
            else:
                self.cbo_universe_tone.setEditText(prev_tone)
        else:
            for i in range(self.cbo_universe_tone.count()):
                model = self.cbo_universe_tone.model()
                item = model.item(i)
                if item and item.isEnabled():
                    self.cbo_universe_tone.setCurrentIndex(i)
                    break

        self.cbo_universe_tone.blockSignals(False)

    def _on_tone_category_changed(self, category_name):
        self._populate_tones_combo(category_name)
        self._on_universe_tone_selected(self.cbo_universe_tone.currentText())

    def _on_universe_tone_selected(self, tone_text):
        if not tone_text:
            return
        t_lower = tone_text.lower()
        if "star wars" in t_lower or "space opera" in t_lower:
            self._set_pronoun_preset_by_prefix("🌌 มหากาพย์อวกาศ / Star Wars")
        elif "wuxia" in t_lower or "xianxia" in t_lower or "จีนกำลังภายใน" in t_lower:
            self._set_pronoun_preset_by_prefix("⚔️ จีนกำลังภายใน")
        elif "samurai" in t_lower or "feudal japan" in t_lower or "ซามูไร" in t_lower:
            self._set_pronoun_preset_by_prefix("🏯 ญี่ปุ่นยุคซามูไร")
        elif "tactical" in t_lower or "military" in t_lower or "ทหาร" in t_lower:
            self._set_pronoun_preset_by_prefix("🪖 การทหาร")
        elif "assassin" in t_lower or "creed" in t_lower or "ภาคีมือสังหาร" in t_lower:
            self._set_pronoun_preset_by_prefix("🦅 ภาคีมือสังหาร")
        elif "high & epic fantasy" in t_lower or "medieval historical" in t_lower or "dark fantasy" in t_lower:
            self._set_pronoun_preset_by_prefix("🏰 แฟนตาซียุคกลาง")

    def _set_pronoun_preset_by_prefix(self, prefix):
        if not hasattr(self, 'cbo_pronouns'):
            return
        for i in range(self.cbo_pronouns.count()):
            text = self.cbo_pronouns.itemText(i)
            if text.startswith(prefix):
                if self.cbo_pronouns.currentIndex() == i:
                    self._on_pronoun_preset_changed(text)
                else:
                    self.cbo_pronouns.setCurrentIndex(i)
                break

    def _on_pronoun_preset_changed(self, preset_name):
        if not hasattr(self, 'txt_pronoun_preview'):
            return
        preset = PRONOUN_PRESETS.get(preset_name, {})
        summary = preset.get("summary", "")
        self.txt_pronoun_preview.setText(summary)

    def _insert_pronoun_rules(self):
        """Inserts the current pronoun system and strict gender certainty rules into custom rules box."""
        p_name = self.cbo_pronouns.currentText()
        preset = PRONOUN_PRESETS.get(p_name, {})
        rules_text = preset.get("rules", "")
        neutral = preset.get("neutral", "คุณ / เจ้า / ท่าน")
        strict = self.chk_strict_gender.isChecked()

        rule_block = f"### [กฎสรรพนามและการระบุเพศ - {p_name}]\n{rules_text}\n"
        if strict:
            rule_block += (
                "- กฎเหล็กความมั่นใจทางเพศ (Strict Gender Certainty):\n"
                "  1. ต้องมั่นใจเพศ 100% เท่านั้นจาก Context ID (เช่น _male, _female, caroline, anya, engel), ข้อความอังกฤษ (she/he/madam/sir) หรือ Lore จึงจะใช้สรรพนามระบุเพศได้\n"
                f"  2. หากไม่มั่นใจเพศตัวละคร 100% ห้ามเดาเพศเด็ดขาด! ให้ใช้สรรพนามกลาง ({neutral}) หรือละประธานอย่างเป็นธรรมชาติ\n"
                "  3. ตัวละครหญิง (Female Characters/Soldiers): ห้ามแทนตนเองว่า 'ผม' หรือลงท้าย 'ครับ' เด็ดขาด! ให้ใช้ 'ฉัน' (สหาย/ระดับเดียวกัน), 'ดิฉัน' (รายงานผู้บังคับบัญชา) หรือละประธาน\n"
                "  4. ยุทธวิธีรบ (Subject Dropping): ในคำสั่ง/รายงานยุทธวิธี สามารถละประธาน 'ผม/ฉัน' ได้อย่างเป็นธรรมชาติ (เช่น 'รับทราบ', 'เห็นเป้าหมายแล้ว', 'กำลังเข้าเคลียร์')\n"
                "  5. ห้ามสุ่มเดาคำลงท้าย ครับ/ค่ะ มั่วเด็ดขาด หากไม่แน่ใจให้ละคำลงท้ายหรือใช้น้ำเสียงเด็ดขาดกระชับ"
            )

        cur = self.txt_custom_rules.toPlainText().strip()
        self.txt_custom_rules.setPlainText(cur + "\n\n" + rule_block if cur else rule_block)
        self.lbl_status.setText(f"เพิ่มกฎสรรพนาม ({p_name}) และกฎระบุเพศ เรียบร้อย")

    def _collect_detection_sample_texts(self):
        sample_texts = []
        try:
            if hasattr(self, 'txt_candidate_entities') and self.txt_candidate_entities.toPlainText().strip():
                sample_texts.extend(self.txt_candidate_entities.toPlainText().splitlines()[:50])
            if hasattr(self, 'txt_lore_content') and self.txt_lore_content.toPlainText().strip():
                sample_texts.append(self.txt_lore_content.toPlainText().strip())
        except Exception:
            pass

        parent = self.parent()
        file_path = getattr(parent, 'csv_path', "") or getattr(parent, 'project_dir', "") or getattr(parent, 'project_path', "") or ""
        proj_dir = getattr(parent, 'project_dir', "") or getattr(parent, 'project_path', "") or ""
        if not proj_dir:
            try:
                proj_dir = TStudioCore.get_project_path() or ""
            except Exception:
                proj_dir = ""

        if parent:
            try:
                parent_prof = getattr(parent, 'current_profile_name', None)
                if not parent_prof or parent_prof == self.active_profile:
                    if hasattr(parent, '_collect_sample_texts_from_workspace'):
                        sample_texts.extend(parent._collect_sample_texts_from_workspace(100))
                    elif hasattr(parent, 'model') and hasattr(parent.model, '_data') and parent.model._data:
                        sample_texts.extend(collect_stratified_dialogue_samples(parent.model._data, max_samples=100))
                    elif hasattr(parent, 'table') and parent.table and parent.table.model():
                        m = parent.table.model()
                        rows_data = []
                        for r in range(min(500, m.rowCount())):
                            idx = m.index(r, 2)
                            val = m.data(idx, Qt.ItemDataRole.DisplayRole)
                            if val and str(val).strip():
                                rows_data.append(str(val).strip())
                        sample_texts.extend(collect_stratified_dialogue_samples(rows_data, max_samples=100))
            except Exception as e:
                print(f"[TLM Studio] Warning collecting samples from parent: {e}")

        return sample_texts, file_path, proj_dir

    def _on_auto_detect_tone_clicked(self):
        sample_texts, file_path, proj_dir = self._collect_detection_sample_texts()
        self.lbl_status.setText("🔍 กำลังวิเคราะห์โทนจักรวาล (Heuristic + AI Verification)...")
        QApplication.processEvents()

        res = detect_game_universe_tone_with_api(self.active_profile, sample_texts, file_path, project_dir=proj_dir)

        if res.get("inspected_name"):
            self._detected_game_name = res["inspected_name"]

        ac_info = res.get("ac_info")
        if ac_info and ac_info.get("is_ac"):
            self._detected_ac_info = ac_info
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
        else:
            self._detected_ac_info = None
            ac_extra_html = ""

        # Apply category
        cat_idx = self.cbo_tone_category.findText(res["category"])
        if cat_idx >= 0:
            self.cbo_tone_category.setCurrentIndex(cat_idx)
        else:
            self.cbo_tone_category.setCurrentIndex(0)

        # Apply tone
        tone_idx = self.cbo_universe_tone.findText(res["tone"])
        if tone_idx >= 0:
            self.cbo_universe_tone.setCurrentIndex(tone_idx)
        else:
            self.cbo_universe_tone.setEditText(res["tone"])

        # Apply pronoun
        p_idx = self.cbo_pronouns.findText(res["pronoun"])
        if p_idx >= 0:
            self.cbo_pronouns.setCurrentIndex(p_idx)

        stage_desc = "วิเคราะห์โดย AI ร่วมกับชื่อเกมและบทสนทนา (API-Assisted)" if res.get("stage") == "ai_api" else ("ระยะที่ 1: ตรวจพบจากชื่อโปรเจค/เกมโดยตรง" if res.get("stage") == "project_name" else "ระยะที่ 2: ตรวจพบจากเนื้อหาบทสนทนา")
        detected_name = res.get("inspected_name") or self.active_profile

        self.lbl_status.setText(f"🔍 ตรวจพบ: {res['label']} ({detected_name})")
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
            f"<i>ระบบได้ปรับหมวดหมู่และเลือกโทนจักรวาลให้เรียบร้อยแล้ว</i>"
        )

    def _on_easy_mode_clicked(self):
        sample_texts, file_path, proj_dir = self._collect_detection_sample_texts()
        self.lbl_status.setText("⚡ Easy Mode: กำลังวิเคราะห์และคอมไพล์โปรไฟล์อัตโนมัติ...")
        QApplication.processEvents()

        res = detect_game_universe_tone_with_api(self.active_profile, sample_texts, file_path, project_dir=proj_dir)

        if res.get("inspected_name"):
            self._detected_game_name = res["inspected_name"]

        ac_info = res.get("ac_info")
        if ac_info and ac_info.get("is_ac"):
            self._detected_ac_info = ac_info
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
        else:
            self._detected_ac_info = None
            ac_extra_html = ""

        # 1. Category & Tone
        cat_idx = self.cbo_tone_category.findText(res["category"])
        if cat_idx >= 0:
            self.cbo_tone_category.setCurrentIndex(cat_idx)
        else:
            self.cbo_tone_category.setCurrentIndex(0)

        tone_idx = self.cbo_universe_tone.findText(res["tone"])
        if tone_idx >= 0:
            self.cbo_universe_tone.setCurrentIndex(tone_idx)
        else:
            self.cbo_universe_tone.setEditText(res["tone"])

        # 2. Pronoun Matrix
        p_idx = self.cbo_pronouns.findText(res["pronoun"])
        if p_idx >= 0:
            self.cbo_pronouns.setCurrentIndex(p_idx)

        # 3. Strict Gender Certainty
        self.chk_strict_gender.setChecked(True)

        # 4. Translation Philosophy
        self.cbo_philosophy.setCurrentIndex(0)

        # 5. Auto-extract Characters, Proper Locations & Unique Items from Lore Notes into Glossary if present!
        lore_ext_total, lore_ext_new = 0, 0
        if self.txt_lore_content.toPlainText().strip():
            lore_ext_total, lore_ext_new = self._extract_lore_to_glossary(silent=True)

        # 6. Compile to Prompts immediately!
        self._compile_directives_to_prompts()

        # 7. Save Profile Data
        self._save_profile_lore_data()

        stage_desc = "วิเคราะห์โดย AI ร่วมกับชื่อเกมและบทสนทนา (API-Assisted)" if res.get("stage") == "ai_api" else ("ระยะที่ 1: ตรวจพบจากชื่อโปรเจค/เกมโดยตรง" if res.get("stage") == "project_name" else "ระยะที่ 2: ตรวจพบจากเนื้อหาบทสนทนา")
        detected_name = res.get("inspected_name") or self.active_profile
        lore_ext_line = f"• <b>คลังคำศัพท์จาก Lore:</b> 📚 สกัดตัวละคร/สถานที่/ไอเท็มเฉพาะ {lore_ext_total} คำ (+{lore_ext_new} คำใหม่เข้า Glossary)<br>" if lore_ext_total > 0 else ""

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
            f"{lore_ext_line}"
            f"• <b>AI Prompts:</b> ✅ คอมไพล์เข้าโปรไฟล์ '{self.active_profile}' เรียบร้อยแล้ว พร้อมใช้งานทันที!<br>"
            f"{ac_extra_html}<br>"
            f"<i>หลักฐานที่พบ: {res['reason']}</i>"
        )

    def _insert_no_cjk_rule(self):
        rule = (
            "### กฎการแปลไทยบริสุทธิ์ 100% (STRICT ZERO-FOREIGN / NO-CJK LEAK RULE):\n"
            "- ผลลัพธ์การแปลต้องเป็นภาษาไทยที่เป็นธรรมชาติ สละสลวย 100%\n"
            r"- ห้ามมีตัวอักษรจีน (CJK: [\u4e00-\u9fff]), ญี่ปุ่น (Hiragana/Katakana), หรือเกาหลี (Hangul) หลุดรอดมาในคำแปลเด็ดขาด" "\n"
            "- ห้ามทิ้งคำศัพท์ภาษาอังกฤษหรือภาษาต้นทางไว้โดยไม่ได้แปล ยกเว้นกรณีที่เป็นชื่อเฉพาะ รหัสรุ่นทางเทคนิค หรือตัวแปรที่ถูกระบุไว้เท่านั้น"
        )
        cur = self.txt_custom_rules.toPlainText().strip()
        self.txt_custom_rules.setPlainText(cur + "\n\n" + rule if cur else rule)
        self.lbl_status.setText("เพิ่มกฎแปลไทย 100% ไร้ภาษาจีน เรียบร้อย")

    def _insert_smart_proper_noun_rule(self):
        rule = (
            "### กฎการวิเคราะห์และถอดเสียงคำเฉพาะอัจฉริยะ (SMART PROPER NOUN DISCRIMINATION):\n"
            "1. แยกแยะความแตกต่างระหว่าง 'คำนามเฉพาะ (Proper Nouns)' กับ 'คำบรรยายทั่วไป (Descriptive Terms)' อย่างแม่นยำ\n"
            "2. สำหรับชื่อเฉพาะ (ชื่อตัวละคร, เผ่าพันธุ์, ฝ่าย/องค์กร, ชื่อเมือง/ดาว, อาวุธในตำนาน): ห้ามแปลตรงตัวตามพจนานุกรมจนเพี้ยน (เช่น 'Bolter' ห้ามแปลเป็น 'ปืนสลักเกลียว') แต่ให้ 'ทับศัพท์' (Transliterate) ออกเสียงภาษาไทยอย่างถูกต้องตามความคุ้นเคยของเกมเมอร์ ('โบลต์เตอร์')\n"
            "3. สำหรับรหัสเฉพาะทางเทคนิคหรือโมเดล (เช่น 'MK-IV', 'STC-09', 'Unit 734'): ให้คงตัวอักษรภาษาอังกฤษและตัวเลขไว้ตามเดิม\n"
            "4. สำหรับคำอธิบายประเภท อุปกรณ์ทั่วไป สถานะ คำสั่ง UI: ให้แปลเป็นความหมายภาษาไทยที่ชัดเจน ตรงบริบทเกม"
        )
        cur = self.txt_custom_rules.toPlainText().strip()
        self.txt_custom_rules.setPlainText(cur + "\n\n" + rule if cur else rule)
        self.lbl_status.setText("เพิ่มกฎวิเคราะห์คำเฉพาะ/ทับศัพท์อัจฉริยะ เรียบร้อย")

    def _insert_hybrid_rule(self):
        rule = (
            "### กฎการแปลสไตล์ไฮบริดเกมเมอร์ (HYBRID GAMER LOCALIZATION):\n"
            "- ใช้รูปแบบผสมผสาน: คำนามเฉพาะทับศัพท์ชัดเจน + คำคุณศัพท์/คำกริยา/คำอธิบายแปลไทยสละสลวย\n"
            "- สำนวนภาษาต้องเข้ากับโทนจักรวาลเกม ไม่แปลแข็งเป็นหุ่นยนต์ รักษาอารมณ์ความรู้สึกต้นฉบับอย่างสมบูรณ์"
        )
        cur = self.txt_custom_rules.toPlainText().strip()
        self.txt_custom_rules.setPlainText(cur + "\n\n" + rule if cur else rule)
        self.lbl_status.setText("เพิ่มกฎสไตล์ไฮบริดเกมเมอร์ เรียบร้อย")

    def _insert_anti_literal_rule(self):
        rule = (
            "### กฎเหล็กพากย์ไทยภาพยนตร์ & ขจัดสำนวนฝรั่ง (ANTI-LITERAL & CINEMATIC ACTION-DUB):\n"
            "1. ห้ามแปลตรงตัวคำต่อคำ (Word-for-Word) หรือใช้สำนวนแปลฝรั่งแข็งกระด้างโดยเด็ดขาด\n"
            "2. ถอดความสำนวน คำอุปมาอุปไมย และคำสแลง ให้เป็นภาษาพูดไทยที่เห็นภาพและได้อารมณ์:\n"
            "   - 'I'll be damned if...' ➔ 'ไม่มีทางยอมให้... / ฝันไปเถอะว่าฉันจะ...' (ห้ามแปล 'ฉันจะถูกสาปถ้า...')\n"
            "   - 'at our doorstep' ➔ 'บุกมาถึงหน้าบ้านเรา / จ่อคอหอยเราอยู่' (ห้ามแปล 'อยู่ที่ธรณีประตู')\n"
            "   - 'go to hell and back to kick them out' ➔ 'บุกน้ำลุยไฟพลิกแผ่นดินเพื่อไล่ตะเพิดพวกมัน' (ห้ามแปล 'ไปนรกและกลับมาเพื่อเตะ...')\n"
            "   - 'on their knees' ➔ 'ยอมสยบ / คลานเข่าเข้ามาขอร้อง / จนตรอก' (ห้ามแปล 'คุกเข่าอยู่')\n"
            "   - 'Jerry / Kraut' ➔ 'พวกนาซี / พวกเยอรมัน / พวกไอ้กบฏ' (ห้ามแปล 'เจอร์รี่')\n"
            "   - 'bite the bullet' ➔ 'กัดฟันสู้ / จำใจกลืนเลือด' (ห้ามแปล 'กัดกระสุน')\n"
            "3. กำจัดไวยากรณ์หุ่นยนต์: ไม่ใช้คำว่า 'ถูก' พร่ำเพรื่อ (เช่น 'ถูกบังคับให้ถอย' ให้แก้เป็น 'ต้องล่าถอย') และตัดคำฟุ่มเฟือยแบบ 'ทำการ...', 'มีการ...', 'ได้รับการ...' ออกทั้งหมด\n"
            "4. น้ำเสียงพากย์ไทยภาพยนตร์ฮอลลีวูด (Cinematic Dubbing): ถ่ายทอดอารมณ์ดุดัน สมจริงตามสถานการณ์สงคราม คำสบถ (Damn, Shit, Bastard, Fuck) แปลให้ได้อารมณ์เดือดดาลตามเนื้อเรื่อง (เช่น 'เวรเอ๊ย', 'ไอ้ระยำ', 'สารเลว', 'บัดซบ')\n"
            "5. ข้อยกเว้นชื่ออาวุธ/ยานพาหนะ: รหัสปืน ยุทโธปกรณ์ ยานเกราะ (เช่น MP40, STG44, Luger, Panzerhund, Flak 88, RPG, SMG, AR) ให้คงอักษรภาษาอังกฤษและตัวเลขไว้ตามเดิม"
        )
        cur = self.txt_custom_rules.toPlainText().strip()
        self.txt_custom_rules.setPlainText(cur + "\n\n" + rule if cur else rule)
        self.lbl_status.setText("เพิ่มกฎพากย์ไทยภาพยนตร์ & ขจัดสำนวนฝรั่ง เรียบร้อย")

    def _clear_custom_rules(self):
        if not self.txt_custom_rules.toPlainText().strip(): return
        res = QMessageBox.question(self, "ยืนยันการล้างกฎ", "คุณแน่ใจหรือไม่ว่าต้องการล้างกฎเฉพาะทั้งหมด?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if res == QMessageBox.StandardButton.Yes:
            self.txt_custom_rules.clear()
            self.lbl_status.setText("ล้างกฎเฉพาะเรียบร้อย")

    def _sync_rules_to_main_prompts(self):
        """Synchronizes current Universe Tone, Pronouns, Lore Context, and Custom/Variable Guard Rules
        directly into the active profile's AI Single & Batch translation prompts."""
        prof_name = self.active_profile
        prof = TStudioCore.get_current_profile_data(prof_name)
        
        tone = self.cbo_universe_tone.currentText().strip()
        philosophy = self.cbo_philosophy.currentText().strip()
        rules = self.txt_custom_rules.toPlainText().strip()
        
        p_name = self.cbo_pronouns.currentText().strip()
        preset = PRONOUN_PRESETS.get(p_name, {})
        p_rules = preset.get("rules", "")
        p_neutral = preset.get("neutral", "คุณ / เจ้า / ท่าน")
        strict_gender = self.chk_strict_gender.isChecked()

        directives_block = (
            f"\n[UNIVERSE & LOCALIZATION DIRECTIVES]\n"
            f"- Universe & Tone: {tone}\n"
            f"- Philosophy: {philosophy}\n"
            f"- Pronoun Style: {p_name}\n"
            f"{p_rules}\n"
        )
        if strict_gender:
            directives_block += (
                f"[STRICT GENDER CERTAINTY DIRECTIVE]\n"
                f"- Must be 100% certain of character gender to use gendered pronouns/particles (ผม/ฉัน/ครับ/ค่ะ).\n"
                f"- If ambiguous or unconfirmed: MUST use neutral terms ({p_neutral}) or naturally drop subject, and NEVER guess 'ครับ/ค่ะ'.\n"
                f"- Female Characters / Combatants: NEVER use 'ผม' or 'ครับ'! Use 'ฉัน' (peers), 'ดิฉัน' (formal), or drop the subject.\n"
                f"- Tactical Subject Dropping: In combat commands/reports, drop pronouns naturally (e.g. 'รับทราบ', 'เห็นเป้าหมายแล้ว', 'กำลังเข้าเคลียร์') instead of forcing 'ผม/ฉัน'.\n"
            )
        if rules:
            directives_block += f"[PROJECT CUSTOM & VARIABLE RULES]\n{rules}\n"

        base_single = f"""You are a Master-Level Video Game Localization Specialist for '{prof_name}', translating the source language into natural Thai.
Translate this line. ID: '{{id}}'. Return ONLY the pure Thai string, no quotes, no explanations.
{directives_block}
STRICT LENGTH & CONTENT RULES (NON-NEGOTIABLE):
- Your translation MUST match the length and structure of the source text as closely as possible.
- If the source is a short UI label (e.g. 'ID:', 'Rank', 'Mass'), return ONLY its short Thai equivalent.
- Preserve all game tags like {{...}}, [...], <...> exactly.
- Strictly ZERO leftover Chinese/CJK characters or foreign text leaks.
Text: {{source_text}}"""

        base_batch = f"""You are a Master-Level Video Game Localization Specialist for '{prof_name}', translating the source language into natural Thai.
Perform high-accuracy bulk localization into Thai.
{directives_block}
STRICT BATCH TRANSLATION RULES (NON-NEGOTIABLE):
- Translate each line preserving line-by-line 1:1 mapping.
- Match the length and tone of the original context.
- Preserve all game tags like {{...}}, [...], <...> exactly.
- Strictly ZERO leftover Chinese/CJK characters or foreign text leaks.
- Do NOT output explanations, introductory text, or markdown codeblocks."""

        prof['single'] = base_single
        prof['batch'] = base_batch
        if "prompts" not in prof or not isinstance(prof["prompts"], dict):
            prof["prompts"] = {}
        prof["prompts"]["single"] = base_single
        prof["prompts"]["batch"] = base_batch
        if "tlm" in prof and isinstance(prof["tlm"], dict):
            if "prompts" not in prof["tlm"] or not isinstance(prof["tlm"]["prompts"], dict):
                prof["tlm"]["prompts"] = {}
            prof["tlm"]["prompts"]["single"] = base_single
            prof["tlm"]["prompts"]["batch"] = base_batch
        self._save_profile_lore_data(silent=True)
        TStudioCore.save_profile_data(prof_name, prof)
        self._load_profile_prompts(prof_name)

        if self.main_app and hasattr(self.main_app, 'refresh_glossary_dependent_features'):
            self.main_app.refresh_glossary_dependent_features()

        QMessageBox.information(
            self, "ซิงค์สำเร็จ",
            f"ซิงค์โทนจักรวาลเกม, ระบบสรรพนาม, กฎความมั่นใจเรื่องเพศ, และกฎคุ้มครองตัวแปรเข้าสู่ AI Translation Prompt ของโปรไฟล์ '{prof_name}' เรียบร้อยแล้ว!\n\n"
            f"การแปลในหน้าต่างหลักจะปฏิบัติตามกฎนี้โดยอัตโนมัติ"
        )
        self.lbl_status.setText("ซิงค์กฎและระบบสรรพนามเข้าสู่ AI Prompt หลักของโปรไฟล์สำเร็จ")

    # -------------------------------------------------------------
    # LOGIC: DEEP AI MINING & WEB CHAT BYPASS MINING
    # -------------------------------------------------------------
    def _build_batch_mining_prompt(self, batch_terms, game_title, tone, philosophy, target_cats, custom_rules, anti_dup_block, lore_text):
        batch_candidates_text = "\n".join(f"- {t}" for t in batch_terms)
        return (
            f"You are a master video game localization director and terminologist specializing in video game adaptation into natural Thai.\n"
            f"Your mission is to establish Thai localization and glossary definitions for the following {len(batch_terms)} specific game terms for '{game_title}':\n\n"
            f"### CANDIDATE TERMS TO PROCESS:\n"
            f"{batch_candidates_text}\n\n"
            f"### DIRECTIVES MATRIX:\n"
            f"- Universe & Tone Style: {tone}\n"
            f"- Localization Philosophy: {philosophy}\n"
            f"- Target Categories to Focus on: {', '.join(target_cats)}\n\n"
            f"### CRITICAL LOCALIZATION RULES:\n"
            f"1. MANDATORY COVERAGE OF CHARACTERS, PROPER LOCATIONS, AND UNIQUE ITEMS:\n"
            f"   - **Main & Key Characters (`Person`)**: You MUST include ALL character names, callsigns, and titles (e.g. 'John Taylor', 'Taylor', 'Sarah Hall', 'Hall', 'Jacob Hendricks', 'Hendricks', 'Rachel Kane', 'Kane', 'Raul Menendez'). NEVER skip a character's first name, surname, or callsign even if it resembles a common English word!\n"
            f"   - **Proper-Noun Locations & Factions (`Location`, `Faction`)**: Include all named cities, stations, bases, regions, dungeons, and organizations (e.g. 'The Frozen Forest', 'Black Station', 'Winslow Accord', 'Common Defense Pact', 'Coalescence Corporation').\n"
            f"   - **Unique Proper-Noun Items & Weapons (`Item`, `Weapon`)**: Include all items, technologies, cybernetics, currencies, and weapons that have unique proper names in the game (e.g. 'Direct Neural Interface', 'DNI', 'Cybercore', 'Nova 6', 'Divinium', 'Cryptokey', 'Supply Drop', 'Calling Card', 'M4A1').\n"
            f"2. FILTER OUT ONLY GENERIC NON-ENTITY WORDS:\n"
            f"   - Skip purely generic everyday objects that are NOT proper nouns (e.g. bare 'Door', 'Room', 'Tree', 'Water', 'Table', 'Old Man', 'Young Woman', 'Quest 1') and vocal sound effects ('Aah', 'Ugh', 'Gasp').\n"
            f"3. STRICT ZERO-FOREIGN / NO-CJK LEAK: The Thai translation must be pure, natural Thai. Absolutely NO Chinese characters ([\\u4e00-\\u9fff]), Japanese, or Korean characters permitted.\n"
            f"4. SMART PROPER NOUN INTELLIGENCE: For character names and proper places, TRANSLITERATE (ทับศัพท์) into natural Thai phonetics based on gaming community standards. For unique items/factions, use either established Thai translation or natural hybrid localization.\n"
            f"5. CUSTOM & VARIABLE CONSTRAINTS:\n{custom_rules if custom_rules else 'None'}\n\n"
            f"{anti_dup_block}"
            f"### LORE & STORY CONTEXT:\n"
            f"{lore_text[:8000] if lore_text else 'None'}\n\n"
            f"### OUTPUT FORMAT INSTRUCTIONS:\n"
            f"You MUST output ONLY a valid JSON array of objects starting directly with '['. Do not include markdown code block backticks, intro text, or reasoning commentary.\n"
            f"Each object MUST contain exactly these 5 keys:\n"
            f"1. 'en': (string) The original English term.\n"
            f"2. 'th': (string) The refined Thai translation following the tone and philosophy directives.\n"
            f"3. 'tag': (string) Exactly one of: General, Person, Location, Faction, Weapon, Item, Quest, Other.\n"
            f"4. 'context': (string) Short explanation (in Thai or English) of what this entity is and why it was translated this way.\n"
            f"5. 'alt': (string) An alternative acceptable Thai translation, or empty string.\n\n"
            f"Example:\n"
            f"[\n"
            f'  {{"en": "John Taylor", "th": "จอห์น เทย์เลอร์", "tag": "Person", "context": "ผู้บังคับการทีม Black Ops ตัวละครหลัก", "alt": "เทย์เลอร์"}},\n'
            f'  {{"en": "The Frozen Forest", "th": "ป่าเหมันต์", "tag": "Location", "context": "สถานที่จำลองในจิตใต้สำนึก DNI", "alt": "ฟโรเซนฟอเรสต์"}}\n'
            f"]"
        )

    def _build_generative_mining_prompt(self, target_count, game_title, tone, philosophy, target_cats, custom_rules, anti_dup_block, lore_text):
        return (
            f"You are a master video game localization director and terminologist specializing in video game adaptation into natural Thai.\n"
            f"Your mission is to extract and establish a comprehensive, professional glossary of {target_count} crucial terms for the game '{game_title}'.\n\n"
            f"### DIRECTIVES MATRIX:\n"
            f"- Universe & Tone Style: {tone}\n"
            f"- Localization Philosophy: {philosophy}\n"
            f"- Target Categories to Focus on: {', '.join(target_cats)}\n\n"
            f"### CRITICAL LOCALIZATION RULES:\n"
            f"1. MANDATORY EXHAUSTIVE EXTRACTION OF 3 CORE PILLARS:\n"
            f"   - **Pillar 1 — All Main & Key Characters (`Person`)**: Extract ALL main characters, squadmates, antagonists, and key NPCs from the Lore Context and your canonical knowledge of '{game_title}'. Include BOTH their full names (e.g. 'John Taylor', 'Sarah Hall') AND their spoken short names/callsigns ('Taylor', 'Hall', 'Hendricks', 'Kane').\n"
            f"   - **Pillar 2 — All Proper-Noun Locations & Factions (`Location`, `Faction`)**: Extract all named cities, facilities, stations, regions, realms, and organizations/factions.\n"
            f"   - **Pillar 3 — All Unique Proper-Noun Items, Tech & Signature Weapons (`Item`, `Weapon`)**: Extract all items with unique/non-generic names in the game, special technologies/implants, artifacts, currencies, and signature weapons.\n"
            f"2. ZERO GENERIC NOISE: Do NOT output generic everyday nouns ('Door', 'Key', 'Room', 'Old Man') or vocal moans ('Aah', 'Ugh').\n"
            f"3. STRICT ZERO-FOREIGN / NO-CJK LEAK: The Thai translation must be pure, natural Thai. Absolutely NO Chinese characters ([\\u4e00-\\u9fff]), Japanese, or Korean characters permitted.\n"
            f"4. SMART PROPER NOUN INTELLIGENCE: Distinguish proper nouns from descriptive words. Transliterate character names accurately into natural Thai phonetics.\n"
            f"5. CUSTOM & VARIABLE CONSTRAINTS:\n{custom_rules if custom_rules else 'None'}\n\n"
            f"{anti_dup_block}"
            f"### LORE & STORY CONTEXT:\n"
            f"{lore_text[:12000] if lore_text else 'None'}\n\n"
            f"### OUTPUT FORMAT INSTRUCTIONS:\n"
            f"You MUST output ONLY a valid JSON array of objects starting directly with '['. Do not include markdown code block backticks, intro text, or reasoning commentary.\n"
            f"Each object MUST contain exactly these 5 keys:\n"
            f"1. 'en': (string) The original English term (Character name, proper location, faction, unique item, or weapon).\n"
            f"2. 'th': (string) The refined Thai translation following the tone and philosophy directives.\n"
            f"3. 'tag': (string) Exactly one of: General, Person, Location, Faction, Weapon, Item, Quest, Other.\n"
            f"4. 'context': (string) Short explanation (in Thai or English) of what this entity is and why it was translated this way.\n"
            f"5. 'alt': (string) An alternative acceptable Thai translation, or empty string.\n\n"
            f"Example:\n"
            f"[\n"
            f'  {{"en": "John Taylor", "th": "จอห์น เทย์เลอร์", "tag": "Person", "context": "ผู้บังคับการทีมไซเบอร์เนติกส์หลักของเรื่อง", "alt": "เทย์เลอร์"}},\n'
            f'  {{"en": "Direct Neural Interface", "th": "ระบบเชื่อมต่อประสาทโดยตรง", "tag": "Item", "context": "เทคโนโลยีชิป DNI เชื่อมสมองทหาร", "alt": "ดีเอ็นไอ"}}\n'
            f"]"
        )

    def _launch_web_chat_mining_workflow(self):
        """
        Zero-Cost Web Chat Bypass for TLM Terminology Mining:
        First extracts any pre-translated terms from Lore Notes into Glossary, then builds a rich JSON mining prompt
        combining Lore + CSV Candidate Entities, copies it to the clipboard, and opens Gemini Web / ChatGPT.
        """
        lore_text = self.txt_lore_content.toPlainText().strip()
        if lore_text:
            self._extract_lore_to_glossary(silent=True)

        entities_text = self.txt_candidate_entities.toPlainText().strip()
        if not entities_text:
            self._scan_entities_from_csv(silent=True)
            entities_text = self.txt_candidate_entities.toPlainText().strip()

        game_title = self.active_profile
        tone = self.cbo_universe_tone.currentText().strip()
        philosophy = self.cbo_philosophy.currentText().strip()
        custom_rules = self.txt_custom_rules.toPlainText().strip()
        target_cats = [cat for cat, chk in self.chk_cats.items() if chk.isChecked()] or ["Person", "Location", "Faction", "Weapon", "Item", "General"]

        candidate_list = []
        if entities_text:
            for line in entities_text.splitlines():
                line = re.sub(r'^(?:[-*•]|\d+\.)\s*', '', line.strip()).strip()
                if line and line not in candidate_list:
                    candidate_list.append(line)

        prof = TStudioCore.get_current_profile_data(self.active_profile)
        existing_glossary = prof.get("glossary", {}) if isinstance(prof.get("glossary"), dict) else {}
        existing_terms = [str(k).strip() for k in existing_glossary.keys() if str(k).strip()]
        anti_dup_block = ""
        if existing_terms:
            anti_dup_block = (
                f"\n### EXISTING GLOSSARY TERMS (Skip these if already covered, or refine if needed):\n"
                f"{json.dumps(existing_terms[:120], ensure_ascii=False)}\n\n"
            )

        target_limit = max(self.spn_term_count.value(), 50)
        if candidate_list:
            prompt = self._build_batch_mining_prompt(
                batch_terms=candidate_list[:target_limit],
                game_title=game_title,
                tone=tone,
                philosophy=philosophy,
                target_cats=target_cats,
                custom_rules=custom_rules,
                anti_dup_block=anti_dup_block,
                lore_text=lore_text
            )
        else:
            prompt = self._build_generative_mining_prompt(
                target_count=target_limit,
                game_title=game_title,
                tone=tone,
                philosophy=philosophy,
                target_cats=target_cats,
                custom_rules=custom_rules,
                anti_dup_block=anti_dup_block,
                lore_text=lore_text
            )

        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(prompt)

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("🌐 บายพาสสกัดคำศัพท์ผ่าน Web Chat (Gemini / ChatGPT / Codex)")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(
            f"<b>🚀 คัดลอก Prompt สกัดคำศัพท์เชิงลึก (JSON) ลงคลิปบอร์ดเรียบร้อยแล้ว!</b><br><br>"
            f"• <b>โปรไฟล์เกม:</b> {game_title}<br>"
            f"• <b>คำนามเฉพาะที่ส่งไปวิเคราะห์:</b> {len(candidate_list[:target_limit]) if candidate_list else target_limit} คำ<br><br>"
            f"<b>ขั้นตอนการใช้งาน (ฟรี ไม่เสียค่า API):</b><br>"
            f"1. เลือกเปิดเว็บ <b>Gemini Web</b> หรือ <b>ChatGPT / Codex Chat</b> ด้านล่าง (หรือสลับไปหน้าแชทที่คุณเปิดไว้)<br>"
            f"2. กด <b>[Ctrl + V]</b> เพื่อวาง Prompt แล้วกดส่ง<br>"
            f"3. เมื่อ AI สร้างรายการ JSON เสร็จ ให้กด <b>Copy</b> ข้อความทั้งหมดมา<br>"
            f"4. กดปุ่ม <b>'📥 วางผลลัพธ์จากคลิปบอร์ดเข้า Glossary ทันที'</b> ด้านล่างนี้!"
        )
        btn_paste_now = msg_box.addButton("📥 วางผลลัพธ์จากคลิปบอร์ดเข้า Glossary ทันที", QMessageBox.ButtonRole.AcceptRole)
        btn_open_gemini = msg_box.addButton("🌐 เปิด Gemini Web", QMessageBox.ButtonRole.ActionRole)
        btn_open_chatgpt = msg_box.addButton("🤖 เปิด ChatGPT Web", QMessageBox.ButtonRole.ActionRole)
        btn_copy_again = msg_box.addButton("📋 คัดลอก Prompt อีกครั้ง", QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton("ปิดหน้าต่างนี้", QMessageBox.ButtonRole.RejectRole)

        while True:
            msg_box.exec()
            clicked = msg_box.clickedButton()
            if clicked == btn_paste_now:
                self._import_web_chat_mining_result()
                break
            elif clicked == btn_open_gemini:
                import webbrowser
                webbrowser.open("https://gemini.google.com/app")
            elif clicked == btn_open_chatgpt:
                import webbrowser
                webbrowser.open("https://chatgpt.com/")
            elif clicked == btn_copy_again:
                if clipboard:
                    clipboard.setText(prompt)
                self.lbl_status.setText("📋 คัดลอก Prompt สกัดคำศัพท์ลงคลิปบอร์ดอีกครั้งเรียบร้อย")
            else:
                break

    def _import_web_chat_mining_result(self):
        """Imports JSON or Markdown table terminology output copied from Gemini Web / ChatGPT / Codex Chat."""
        clipboard = QApplication.clipboard()
        raw_text = clipboard.text().strip() if clipboard else ""
        if not raw_text:
            QMessageBox.warning(self, "คลิปบอร์ดว่างเปล่า", "ไม่พบข้อความในคลิปบอร์ด กรุณาคัดลอกผลลัพธ์จากหน้าเว็บแชทก่อนนำเข้า")
            return

        parsed_terms = self._parse_ai_terms_json(raw_text)
        if not parsed_terms:
            # Also try parsing via parse_lore_glossary_and_entities in case user copied a Lore summary or stacked table
            g_items, _ = parse_lore_glossary_and_entities(raw_text)
            if g_items:
                parsed_terms = g_items

        if not parsed_terms:
            QMessageBox.warning(
                self, "ไม่พบรายการคำศัพท์",
                "ไม่พบรูปแบบ JSON Array หรือตารางคำศัพท์ในคลิปบอร์ด\n"
                "(หากคุณคัดลอกบทสรุปเนื้อเรื่องมา ให้วางในช่อง Lore Notes แล้วกดปุ่ม '📚 สกัดคำจากบทสรุปเข้า Glossary')"
            )
            return

        self._handle_ai_mining_result(parsed_terms, auto_merge_to_profile=True)

    def _parse_ai_terms_json(self, raw_res):
        """Robust multi-strategy parser and stream healer for AI terminology output."""
        if not raw_res or not str(raw_res).strip():
            return []

        # Strip reasoning tags (DeepSeek-R1, Qwen, etc.)
        clean_text = re.sub(r'<think>.*?</think>', '', str(raw_res), flags=re.DOTALL).strip()
        if not clean_text:
            clean_text = str(raw_res).strip()

        new_terms = None

        # 1. Try markdown JSON codeblock: ```json ... ``` or unclosed ```json ...
        md_match = re.search(r'```(?:json)?\s*(.*?)(?:```|$)', clean_text, re.DOTALL)
        candidate_texts = []
        if md_match and md_match.group(1).strip():
            candidate_texts.append(md_match.group(1).strip())
        candidate_texts.append(clean_text)

        # Strategy 1: Attempt JSON parse on candidate texts with Stream Healing
        for c_text in candidate_texts:
            # A. Try direct parse
            try:
                cleaned_c = re.sub(r',\s*([\]}])', r'\1', c_text)
                parsed = json.loads(cleaned_c)
                if isinstance(parsed, (list, dict)):
                    new_terms = parsed
                    break
            except Exception:
                pass

            # B. Try outermost array [...]
            s = c_text.find('[')
            e = c_text.rfind(']')
            if s != -1 and e != -1 and e > s:
                try:
                    sub_arr = c_text[s:e+1]
                    sub_arr = re.sub(r',\s*([\]}])', r'\1', sub_arr)
                    parsed = json.loads(sub_arr)
                    if isinstance(parsed, list):
                        new_terms = parsed
                        break
                except Exception:
                    pass

            # C. Stream Healing: Truncated JSON array starting with [ but missing closing ]
            if s != -1 and (e == -1 or e <= s):
                last_brace = c_text.rfind('}')
                if last_brace > s:
                    try:
                        healed_arr = c_text[s:last_brace+1] + "\n]"
                        healed_arr = re.sub(r',\s*([\]}])', r'\1', healed_arr)
                        parsed = json.loads(healed_arr)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            new_terms = parsed
                            break
                    except Exception:
                        pass

            # D. Try outermost object {...}
            s2 = c_text.find('{')
            e2 = c_text.rfind('}')
            if s2 != -1 and e2 != -1 and e2 > s2:
                try:
                    sub_obj = c_text[s2:e2+1]
                    sub_obj = re.sub(r',\s*([\]}])', r'\1', sub_obj)
                    parsed = json.loads(sub_obj)
                    if isinstance(parsed, dict):
                        new_terms = parsed
                        break
                except Exception:
                    pass

            # E. Wrap sequence of comma-separated {...}, {...} in [ ... ]
            if s2 != -1 and e2 != -1 and e2 > s2:
                try:
                    wrapped = "[" + c_text[s2:e2+1] + "]"
                    wrapped = re.sub(r',\s*([\]}])', r'\1', wrapped)
                    parsed = json.loads(wrapped)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        new_terms = parsed
                        break
                except Exception:
                    pass

        # Strategy 2: Fallback to regex object extraction: find all {"en": ...} objects
        if new_terms is None:
            obj_matches = re.findall(r'\{[^{}]*?"en"\s*:\s*".*?\}', clean_text, re.DOTALL)
            if not obj_matches:
                obj_matches = re.findall(r'\{[^{}]*\}', clean_text)
            fallback_list = []
            for om in obj_matches:
                try:
                    clean_om = re.sub(r',\s*\}', '}', om)
                    po = json.loads(clean_om)
                    if isinstance(po, dict) and ("en" in po or "th" in po or "term" in po):
                        fallback_list.append(po)
                except Exception:
                    m_en = re.search(r'"(?:en|term|source)"\s*:\s*"([^"]+)"', om)
                    m_th = re.search(r'"(?:th|target|translation)"\s*:\s*"([^"]+)"', om)
                    m_tag = re.search(r'"tag"\s*:\s*"([^"]+)"', om)
                    if m_en and m_th:
                        fallback_list.append({
                            "en": m_en.group(1),
                            "th": m_th.group(1),
                            "tag": m_tag.group(1) if m_tag else "General"
                        })
            if fallback_list:
                new_terms = fallback_list

        # Strategy 3: Fallback to Markdown Table or Bullet / Numbered Lists
        if new_terms is None:
            lines = [ln.strip() for ln in clean_text.splitlines() if ln.strip()]
            text_terms = []
            for ln in lines:
                if ln.startswith('|') and '|' in ln[1:]:
                    parts = [p.strip() for p in ln.split('|') if p.strip()]
                    if len(parts) >= 2 and not any(h in parts[0].lower() for h in ['english', 'en', 'original', '---']):
                        text_terms.append({
                            "en": parts[0],
                            "th": parts[1],
                            "tag": parts[2] if len(parts) > 2 and parts[2] in VALID_TAGS else "General",
                            "context": parts[3] if len(parts) > 3 else "",
                            "alt": parts[4] if len(parts) > 4 else ""
                        })
                elif re.match(r'^(?:[-*•]|\d+\.)\s+', ln):
                    ln_clean = re.sub(r'^(?:[-*•]|\d+\.)\s+', '', ln)
                    m_pair = re.split(r'\s*[:=\->➔]\s*', ln_clean, maxsplit=1)
                    if len(m_pair) == 2 and m_pair[0] and m_pair[1]:
                        en_part = m_pair[0].strip()
                        th_part = m_pair[1].strip()
                        tag_part = "General"
                        tag_m = re.search(r'\((General|Person|Location|Faction|Weapon|Item|Quest|Other)\)', th_part, re.IGNORECASE)
                        if tag_m:
                            tag_part = tag_m.group(1).capitalize()
                            th_part = re.sub(r'\s*\([^)]*\)', '', th_part).strip()
                        text_terms.append({
                            "en": en_part,
                            "th": th_part,
                            "tag": tag_part if tag_part in VALID_TAGS else "General",
                            "context": "",
                            "alt": ""
                        })
            if text_terms:
                new_terms = text_terms

        if new_terms is None:
            return []

        # If AI returned a dictionary (e.g. {"terms": [...]})
        if isinstance(new_terms, dict):
            found_list = None
            for candidate_key in ["terms", "glossary", "data", "items", "results", "vocabulary", "words"]:
                if candidate_key in new_terms and isinstance(new_terms[candidate_key], list):
                    found_list = new_terms[candidate_key]
                    break
            if found_list is not None:
                new_terms = found_list
            else:
                converted = []
                for k, v in new_terms.items():
                    if isinstance(v, dict):
                        converted.append({
                            "en": str(k),
                            "th": str(v.get("th") or v.get("target") or v.get("translation") or ""),
                            "tag": str(v.get("tag", "General")),
                            "context": str(v.get("context", "")),
                            "alt": str(v.get("alt", ""))
                        })
                    elif isinstance(v, str):
                        converted.append({
                            "en": str(k),
                            "th": str(v),
                            "tag": "General",
                            "context": "",
                            "alt": ""
                        })
                new_terms = converted

        if not isinstance(new_terms, list):
            return []

        return new_terms

    def _start_deep_ai_mining(self):
        lore_text = self.txt_lore_content.toPlainText().strip()
        # Step 0: Always extract pre-translated Characters, Locations, Factions & Unique Items from Lore Summary first!
        lore_pre_extracted_count = 0
        if lore_text:
            lore_pre_extracted_count, _ = self._extract_lore_to_glossary(silent=True)

        entities_text = self.txt_candidate_entities.toPlainText().strip()

        # If both lore and candidate entities are empty, try auto-scanning from loaded project data
        if not lore_text and not entities_text:
            has_project_data = False
            if self.main_app and hasattr(self.main_app, 'model') and self.main_app.model and getattr(self.main_app.model, '_data', None):
                has_project_data = True
            elif self.main_app and getattr(self.main_app, 'csv_path', None) and os.path.exists(self.main_app.csv_path):
                has_project_data = True

            if has_project_data:
                self.lbl_status.setText("⚡ กำลังสแกนคำเฉพาะทางจากไฟล์งานแปลอัตโนมัติ...")
                self._scan_entities_from_csv(silent=True)
                entities_text = self.txt_candidate_entities.toPlainText().strip()

        if not lore_text and not entities_text:
            # Check if active profile has existing glossary terms to use as reference
            prof_tmp = TStudioCore.get_current_profile_data(self.active_profile)
            g_keys = list(prof_tmp.get("glossary", {}).keys()) if isinstance(prof_tmp.get("glossary"), dict) else []
            if g_keys:
                entities_text = "\n".join(f"- {k}" for k in g_keys[:50])
                self.txt_candidate_entities.setText(entities_text)
            else:
                QMessageBox.warning(
                    self, "ไม่มีข้อมูลอ้างอิง",
                    "กรุณาใส่ข้อมูลเนื้อเรื่อง (Lore Notes), เปิดไฟล์งานแปลในโปรแกรม, หรือกด '⚡ สแกนคำนามเฉพาะ' เพื่อให้ AI มีบริบทในการวิเคราะห์"
                )
                return

        cfg = TStudioCore.load_config()
        if not cfg.get("api_key") and not (cfg.get("provider") == "Local LLM" or cfg.get("model") == "custom-local-llm") and not cfg.get("google_key") and not cfg.get("openai_key") and not cfg.get("deepseek_key"):
            if lore_pre_extracted_count > 0:
                self.tab_widget.setCurrentIndex(2)
                QMessageBox.information(
                    self, "สกัดจากบทสรุป Lore สำเร็จ (โหมดไร้ API)",
                    f"สกัดตัวละคร สถานที่ และไอเท็มเฉพาะจากบทสรุป Lore ได้ {lore_pre_extracted_count} คำ และนำเข้า Glossary เรียบร้อยแล้ว!\n"
                    f"(หากต้องการให้ AI สกัดเพิ่มเติมนอกเหนือจากบทสรุป กรุณาตั้งค่า API Key หรือใช้ปุ่ม '🌐 สกัดศัพท์ผ่าน Web Chat')"
                )
                return
            QMessageBox.warning(self, "ยังไม่ได้ตั้งค่า API Key", "กรุณาตั้งค่า API Key ใน Settings หรือใช้ปุ่ม '🌐 สกัดศัพท์ผ่าน Web Chat (ฟรี)'")
            return

        game_title = self.active_profile
        tone = self.cbo_universe_tone.currentText().strip()
        philosophy = self.cbo_philosophy.currentText().strip()
        custom_rules = self.txt_custom_rules.toPlainText().strip()
        target_cats = [cat for cat, chk in self.chk_cats.items() if chk.isChecked()]
        if not target_cats:
            target_cats = ["General", "Person", "Location", "Faction", "Weapon", "Item"]

        # Deduplication against existing profile glossary & existing staged terms
        prof = TStudioCore.get_current_profile_data(self.active_profile)
        existing_glossary = prof.get("glossary", {}) if isinstance(prof.get("glossary"), dict) else {}
        existing_terms = [str(k).strip() for k in existing_glossary.keys() if str(k).strip()]
        staged_existing = [str(item.get("en", "")).strip() for item in self.staged_terms if str(item.get("en", "")).strip()]
        all_existing = list(dict.fromkeys(existing_terms + staged_existing))
        all_existing_lower = {k.lower() for k in all_existing}

        # Parse candidate entities (preferring untranslated candidates not yet in glossary)
        candidate_list = []
        if entities_text:
            for line in entities_text.splitlines():
                line = line.strip()
                if not line: continue
                line = re.sub(r'^(?:[-*•]|\d+\.)\s*', '', line).strip()
                if line and line not in candidate_list and line.lower() not in all_existing_lower:
                    candidate_list.append(line)

        mode = self.cbo_extract_mode.currentData() if hasattr(self, 'cbo_extract_mode') else "essential"
        if mode == "essential":
            target_limit = min(max(self.spn_term_count.value(), 10), 50)
        elif mode == "deep":
            target_limit = 100
        elif mode == "auto":
            target_limit = 350
        else:  # custom
            target_limit = self.spn_term_count.value()

        if candidate_list:
            terms_to_process = candidate_list[:target_limit]
        else:
            terms_to_process = []

        anti_dup_block = ""
        if all_existing:
            sample_terms = all_existing[:150]
            anti_dup_block = (
                f"\n### STRICT DEDUPLICATION DIRECTIVE (CRITICAL):\n"
                f"The following {len(all_existing)} terms ALREADY EXIST in the established glossary. Do NOT re-extract, translate, or output any of these:\n"
                f"{json.dumps(sample_terms, ensure_ascii=False)}\n"
                f"Focus exclusively on discovering and establishing NEW, unlisted terminology (especially any remaining main characters, proper-noun locations, and unique items)!\n\n"
            )

        # Multi-batch chunking strategy (35 terms per batch to avoid LLM token truncation)
        CHUNK_SIZE = 35
        if terms_to_process:
            batches = [terms_to_process[i:i + CHUNK_SIZE] for i in range(0, len(terms_to_process), CHUNK_SIZE)]
        else:
            target_count = target_limit
            batches = [None]  # Single generative batch

        total_batches = len(batches)
        self.btn_start_mining.setEnabled(False)
        self.btn_start_mining.setText("🧠 กำลังสกัดคำศัพท์...")
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.lbl_status.setText(f"AI กำลังเริ่มกระบวนการสกัดคำศัพท์ ({len(terms_to_process) if terms_to_process else 'เชิงสังเคราะห์'} คำ)...")

        def run_mining(signals):
            all_extracted_terms = []
            is_local = (cfg.get("provider", "") == "Local LLM" or cfg.get("model", "") == "custom-local-llm")

            for b_idx, batch in enumerate(batches):
                try:
                    if batch is not None:
                        current_count = len(batch)
                        start_n = b_idx * CHUNK_SIZE + 1
                        end_n = b_idx * CHUNK_SIZE + current_count
                        signals.progress.emit(
                            b_idx + 1, total_batches,
                            f"🔄 AI กำลังสกัดและบัญญัติศัพท์ ชุดที่ {b_idx + 1}/{total_batches} ({start_n}-{end_n} / {len(terms_to_process)} คำ)..."
                        )
                        prompt = self._build_batch_mining_prompt(
                            batch_terms=batch,
                            game_title=game_title,
                            tone=tone,
                            philosophy=philosophy,
                            target_cats=target_cats,
                            custom_rules=custom_rules,
                            anti_dup_block=anti_dup_block,
                            lore_text=lore_text
                        )
                    else:
                        signals.progress.emit(
                            1, 1,
                            "🔄 AI กำลังค้นหาและสกัดคำศัพท์จากเนื้อเรื่อง (Generative Extraction)..."
                        )
                        prompt = self._build_generative_mining_prompt(
                            target_count=target_count,
                            game_title=game_title,
                            tone=tone,
                            philosophy=philosophy,
                            target_cats=target_cats,
                            custom_rules=custom_rules,
                            anti_dup_block=anti_dup_block,
                            lore_text=lore_text
                        )

                    raw_res = CoreAI.generate_content(cfg, prompt, is_local=is_local)
                    batch_terms = self._parse_ai_terms_json(raw_res)
                    if batch_terms:
                        all_extracted_terms.extend(batch_terms)
                        signals.batch_done.emit(batch_terms)
                except Exception as e:
                    print(f"[TLM Studio] Warning during mining batch {b_idx + 1}: {e}")

            if not all_extracted_terms:
                if lore_pre_extracted_count > 0:
                    signals.finished.emit([])
                else:
                    signals.error.emit("ไม่สามารถสกัดหรือแปลงข้อมูลคำศัพท์จาก AI ได้ กรุณาลองใหม่อีกครั้ง")
            else:
                signals.finished.emit(all_extracted_terms)

        worker = MiningWorker(run_mining)
        worker.signals.progress.connect(self._on_mining_progress)
        worker.signals.batch_done.connect(self._on_mining_batch_done)
        worker.signals.finished.connect(self._on_mining_finished)
        worker.signals.error.connect(self._on_mining_error)
        QThreadPool.globalInstance().start(worker)

    def _on_mining_progress(self, current, total, text):
        pct = int(((current - 1) / max(total, 1)) * 100)
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(text)
        self.btn_start_mining.setText(f"🧠 กำลังสกัดชุดที่ {current}/{total}...")

    def _on_mining_batch_done(self, batch_terms):
        self.lbl_status.setText(f"⚡ สกัดชุดสำเร็จ ({len(batch_terms)} คำ)... กำลังดำเนินการต่อ")

    def _on_mining_finished(self, all_terms):
        self.progress_bar.setValue(100)
        self.progress_bar.hide()
        self.btn_start_mining.setEnabled(True)
        self.btn_start_mining.setText("🚀 เริ่ม AI สกัดและบัญญัติศัพท์เชิงลึก (Start Deep AI Mining)")
        if not all_terms and self.staged_terms:
            self.tab_widget.setCurrentIndex(2)
            self.lbl_status.setText(f"✅ สกัดคำศัพท์จากบทสรุป Lore เรียบร้อยแล้ว ({len(self.staged_terms)} คำในตะกร้า)")
            return
        self.lbl_status.setText(f"✅ สกัดคำศัพท์เสร็จสมบูรณ์ รวม {len(all_terms)} คำ")
        self._handle_ai_mining_result(all_terms, auto_merge_to_profile=True)

    def _on_mining_error(self, err_msg):
        self.progress_bar.hide()
        self.btn_start_mining.setEnabled(True)
        self.btn_start_mining.setText("🚀 เริ่ม AI สกัดและบัญญัติศัพท์เชิงลึก (Start Deep AI Mining)")
        self.lbl_status.setText("เกิดข้อผิดพลาดในการสกัดคำศัพท์")
        QMessageBox.critical(self, "AI Error", f"เกิดข้อผิดพลาดจาก AI:\n{err_msg}")

    def _handle_ai_mining_result(self, res_data, auto_merge_to_profile=True):
        try:
            if isinstance(res_data, list):
                new_terms = res_data
            else:
                new_terms = self._parse_ai_terms_json(res_data)

            if not new_terms or not isinstance(new_terms, list):
                raise ValueError("ไม่พบรายการคำศัพท์ที่ถูกต้องจากการตอบกลับของ AI")

            # Query existing glossary terms for duplicate detection
            prof_name = self.active_profile
            prof = TStudioCore.get_current_profile_data(prof_name)
            curr_glossary = copy.deepcopy(prof.get("glossary", {})) if isinstance(prof.get("glossary"), dict) else {}
            existing_lower = {str(k).strip().lower(): str(k).strip() for k in curr_glossary.keys() if str(k).strip()}
            staged_lower = {str(item.get("en", "")).strip().lower() for item in self.staged_terms if str(item.get("en", "")).strip()}

            valid_extracted = []
            dup_count = 0
            auto_merged_count = 0

            for item in new_terms:
                if not isinstance(item, dict): continue
                raw_en = str(item.get("en") or item.get("source") or item.get("term") or "").strip()
                raw_th = str(item.get("th") or item.get("target") or item.get("translation") or "").strip()
                if not raw_en or not raw_th: continue

                raw_tag = str(item.get("tag", "General")).strip()
                ctx = str(item.get("context", "")).strip()
                raw_alt = str(item.get("alt", "")).strip()
                tag = normalize_category_tag(raw_tag, raw_en, ctx, default_tag="General")

                # Expand variants (e.g. 'John Taylor' -> 'John Taylor' + 'Taylor' + 'John', 'Direct Neural Interface (DNI)' -> both)
                variants = expand_entity_variants(raw_en, raw_th, tag, ctx)
                if not variants:
                    variants = [(raw_en, raw_th, tag, ctx, raw_alt)]

                for en, th, v_tag, v_ctx, v_alt in variants:
                    if not en or not th:
                        continue
                    alt_final = v_alt or (raw_alt if en == raw_en else "")

                    # Tag-aware filter: protects Person names ('John Taylor', 'Taylor', 'Hall'), Locations ('The Frozen Forest'), and Unique Items!
                    if is_common_generic_english_word(en, tag=v_tag):
                        print(f"[TLM Studio] Filtered out generic common dictionary word: '{en}' (tag={v_tag})")
                        continue

                    en_low = en.lower()
                    is_dup_prof = en_low in existing_lower
                    is_dup_staged = en_low in staged_lower
                    is_dup = is_dup_prof or is_dup_staged

                    if is_dup_prof:
                        dup_count += 1
                        orig_key = existing_lower.get(en_low, en)
                        dup_note = f"(มีคำศัพท์ '{orig_key}' ในคลังเดิมแล้ว)"
                        v_ctx = f"{dup_note} {v_ctx}".strip() if v_ctx else dup_note
                    elif auto_merge_to_profile:
                        curr_glossary[en] = [th, v_tag]
                        existing_lower[en_low] = en
                        auto_merged_count += 1

                    if not is_dup_staged:
                        staged_lower.add(en_low)
                        valid_extracted.append({
                            "en": en,
                            "th": th,
                            "tag": v_tag,
                            "context": v_ctx,
                            "alt": alt_final,
                            "checked": not is_dup_prof
                        })

            if not valid_extracted and auto_merged_count == 0:
                raise ValueError("ไม่พบคำศัพท์ใหม่ที่สามารถนำเข้าตารางตรวจสอบได้")

            if auto_merge_to_profile and auto_merged_count > 0:
                if self.main_app and hasattr(self.main_app, '_save_glossary_to_active_profile'):
                    main_current = getattr(self.main_app, 'current_profile_name', 'Default')
                    if main_current == prof_name:
                        self.main_app._save_glossary_to_active_profile(curr_glossary)
                    else:
                        prof["glossary"] = curr_glossary
                        TStudioCore.save_profile_data(prof_name, prof)
                else:
                    prof["glossary"] = curr_glossary
                    TStudioCore.save_profile_data(prof_name, prof)

            # Append to staged terms
            self.staged_terms.extend(valid_extracted)
            self._render_staging_table()
            self._refresh_profile_stat_badge()

            # Switch to Tab 3 (Staging Grid) automatically
            self.tab_widget.setCurrentIndex(2)

            dup_info = f"\n• พบคำที่ซ้ำกับคลังเดิม: {dup_count} คำ (คงคำแปลเดิมไว้)" if dup_count > 0 else ""
            merge_info = f"\n• ผสานคำใหม่เข้าสู่ Glossary ของโปรไฟล์ '{prof_name}' อัตโนมัติแล้ว: +{auto_merged_count} คำ (รวมในคลัง {len(curr_glossary)} คำ)" if auto_merged_count > 0 else ""
            QMessageBox.information(
                self, "สกัดและบันทึกคำศัพท์สำเร็จ",
                f"สกัดและบัญญัติศัพท์ได้สำเร็จ {len(valid_extracted)} รายการ!{merge_info}{dup_info}\n\n"
                f"ระบบได้นำคำศัพท์เข้าสู่ทั้ง Glossary ของโปรไฟล์ และ 'ตะกร้าตรวจสอบคำศัพท์ (Staging Grid)' เรียบร้อยแล้ว!"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Parsing Error",
                f"ไม่สามารถแปลงผลลัพธ์จาก AI เป็นรายการคำศัพท์ได้: {e}"
            )

    # -------------------------------------------------------------
    # LOGIC: TAB 2 STAGING GRID ACTIONS
    # -------------------------------------------------------------
    def _render_staging_table(self):
        self.tbl_staging.blockSignals(True)
        self.tbl_staging.setRowCount(0)

        for row_idx, item in enumerate(self.staged_terms):
            self.tbl_staging.insertRow(row_idx)

            # Col 0: Checkbox
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_item.setCheckState(Qt.CheckState.Checked if item.get("checked", True) else Qt.CheckState.Unchecked)
            self.tbl_staging.setItem(row_idx, 0, chk_item)

            # Col 1: EN
            en_item = QTableWidgetItem(item.get("en", ""))
            en_item.setForeground(QBrush(QColor("#cdd6f4")))
            self.tbl_staging.setItem(row_idx, 1, en_item)

            # Col 2: TH
            th_item = QTableWidgetItem(item.get("th", ""))
            th_item.setForeground(QBrush(QColor("#a6e3a1")))
            font = th_item.font()
            font.setBold(True)
            th_item.setFont(font)
            self.tbl_staging.setItem(row_idx, 2, th_item)

            # Col 3: Tag
            tag_item = QTableWidgetItem(item.get("tag", "General"))
            self.tbl_staging.setItem(row_idx, 3, tag_item)

            # Col 4: Context
            ctx_item = QTableWidgetItem(item.get("context", ""))
            ctx_item.setForeground(QBrush(QColor("#a6adc8")))
            ctx_item.setToolTip(item.get("context", ""))
            self.tbl_staging.setItem(row_idx, 4, ctx_item)

            # Col 5: Alt
            alt_item = QTableWidgetItem(item.get("alt", ""))
            alt_item.setForeground(QBrush(QColor("#fab387")))
            alt_item.setToolTip("ดับเบิลคลิกเพื่อสลับคำนี้ไปเป็นคำแปลหลัก (TH)")
            self.tbl_staging.setItem(row_idx, 5, alt_item)

        self.tbl_staging.blockSignals(False)
        self._filter_staging_table()
        self._update_staging_stats()

    def _filter_staging_table(self):
        query = self.txt_stage_filter.text().lower().strip()
        cat = self.cbo_stage_cat_filter.currentData()

        visible_count = 0
        for r in range(self.tbl_staging.rowCount()):
            en_item = self.tbl_staging.item(r, 1)
            th_item = self.tbl_staging.item(r, 2)
            tag_item = self.tbl_staging.item(r, 3)

            en = en_item.text().lower() if en_item else ""
            th = th_item.text().lower() if th_item else ""
            tag = tag_item.text() if tag_item else ""

            match_text = (query in en or query in th) if query else True
            match_cat = (cat == "All") or (tag == cat)
            visible = match_text and match_cat
            self.tbl_staging.setRowHidden(r, not visible)
            if visible:
                visible_count += 1

        self._update_staging_stats(visible_count)

    def _update_staging_stats(self, visible_count=None):
        if visible_count is None:
            visible_count = sum(1 for r in range(self.tbl_staging.rowCount()) if not self.tbl_staging.isRowHidden(r))
        checked_count = 0
        for r in range(self.tbl_staging.rowCount()):
            chk = self.tbl_staging.item(r, 0)
            if chk and chk.checkState() == Qt.CheckState.Checked:
                checked_count += 1
        self.lbl_stage_stat.setText(f"แสดง {visible_count} คำ (เลือกไว้ {checked_count} คำ)")

    def _set_all_staged_checked(self, checked):
        self.tbl_staging.blockSignals(True)
        for r in range(self.tbl_staging.rowCount()):
            if not self.tbl_staging.isRowHidden(r):
                item = self.tbl_staging.item(r, 0)
                if item:
                    item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        self.tbl_staging.blockSignals(False)
        self._update_staging_stats()

    def _on_staging_item_changed(self, item):
        self._update_staging_stats()

    def _on_staging_cell_double_clicked(self, row, col):
        # If user double clicks on Alt column (col 5), swap Alt with TH (col 2)
        if col == 5:
            alt_item = self.tbl_staging.item(row, 5)
            th_item = self.tbl_staging.item(row, 2)
            if alt_item and th_item and alt_item.text().strip():
                old_th = th_item.text()
                th_item.setText(alt_item.text())
                alt_item.setText(old_th)
                self.lbl_status.setText(f"สลับคำแปลสำหรับแถวที่ {row+1} เรียบร้อย")

    def _delete_selected_staged_rows(self):
        selected_rows = sorted(set(index.row() for index in self.tbl_staging.selectedIndexes()), reverse=True)
        if not selected_rows:
            QMessageBox.information(self, "แจ้งเตือน", "กรุณาคลิกเลือกแถวที่ต้องการลบในตารางก่อน")
            return
        self.tbl_staging.blockSignals(True)
        for r in selected_rows:
            self.tbl_staging.removeRow(r)
        self.tbl_staging.blockSignals(False)
        self._update_staging_stats()

    def _purge_common_words_from_staged(self):
        """Audits self.staged_terms and purges single-word common English dictionary terms while preserving tagged entities."""
        if not self.staged_terms:
            QMessageBox.information(self, "ตะกร้าว่างเปล่า", "ยังไม่มีคำศัพท์ในตะกร้าตรวจสอบ")
            return
        initial_len = len(self.staged_terms)
        purged = [item for item in self.staged_terms if not is_common_generic_english_word(item.get("en", ""), tag=item.get("tag"))]
        removed_count = initial_len - len(purged)
        if removed_count == 0:
            QMessageBox.information(self, "สะอาดเรียบร้อย", "ไม่พบคำศัพท์ภาษาอังกฤษทั่วไปในตะกร้าตรวจสอบ ทุกคำเป็นคำเฉพาะทางแล้ว!")
            return
        self.staged_terms = purged
        self._render_staging_table()
        QMessageBox.information(
            self, "กรองคำสำเร็จ",
            f"กรองคำศัพท์ภาษาอังกฤษทั่วไปออกทั้งหมด {removed_count} คำ เรียบร้อยแล้ว!\n"
            f"เหลือคำเฉพาะทางคุณภาพสูง {len(self.staged_terms)} คำ"
        )
        self.lbl_status.setText(f"กรองคำศัพท์ทั่วไปออก {removed_count} คำ จากตะกร้าตรวจสอบเรียบร้อย")

    def _add_manual_staged_row(self):
        r = self.tbl_staging.rowCount()
        self.tbl_staging.blockSignals(True)
        self.tbl_staging.insertRow(r)

        chk_item = QTableWidgetItem()
        chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        chk_item.setCheckState(Qt.CheckState.Checked)
        self.tbl_staging.setItem(r, 0, chk_item)

        self.tbl_staging.setItem(r, 1, QTableWidgetItem("New Term"))
        self.tbl_staging.setItem(r, 2, QTableWidgetItem("คำแปลใหม่"))
        self.tbl_staging.setItem(r, 3, QTableWidgetItem("General"))
        self.tbl_staging.setItem(r, 4, QTableWidgetItem("เพิ่มด้วยตนเอง"))
        self.tbl_staging.setItem(r, 5, QTableWidgetItem(""))
        self.tbl_staging.blockSignals(False)

        self.tbl_staging.selectRow(r)
        self._update_staging_stats()

    # -------------------------------------------------------------
    # LOGIC: IMPORT & SYNC TO ACTIVE PROFILE
    # -------------------------------------------------------------
    def _execute_import_to_profile(self, overwrite=False):
        """Merges or overwrites staged terms into the active profile's glossary and syncs Column 2."""
        try:
            checked_terms = {}
            for r in range(self.tbl_staging.rowCount()):
                chk = self.tbl_staging.item(r, 0)
                if chk and chk.checkState() == Qt.CheckState.Checked:
                    en_item = self.tbl_staging.item(r, 1)
                    th_item = self.tbl_staging.item(r, 2)
                    tag_item = self.tbl_staging.item(r, 3)
                    if en_item and th_item and en_item.text().strip():
                        en = en_item.text().strip()
                        th = th_item.text().strip()
                        tag = tag_item.text().strip() if tag_item else "General"
                        checked_terms[en] = [th, tag]

            if not checked_terms:
                QMessageBox.warning(self, "ไม่มีคำศัพท์ที่เลือก", "กรุณาทำเครื่องหมายเลือกคำศัพท์ในช่อง 'เลือก' อย่างน้อย 1 คำ")
                return

            prof_name = self.active_profile
            prof = TStudioCore.get_current_profile_data(prof_name)
            current_glossary = copy.deepcopy(prof.get("glossary", {})) if isinstance(prof.get("glossary"), dict) else {}

            if overwrite:
                reply = QMessageBox.question(
                    self, "ยืนยันการแทนที่คำศัพท์",
                    f"คุณต้องการ 'แทนที่' คลังคำศัพท์ทั้งหมดของโปรไฟล์ '{prof_name}' ด้วยคำศัพท์ที่เลือกจำนวน {len(checked_terms)} คำ ใช่หรือไม่?\n"
                    f"(คำศัพท์เดิมทั้งหมดในโปรไฟล์จะถูกเขียนทับ)",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
                final_glossary = checked_terms
            else:
                # Merge
                final_glossary = current_glossary
                for en, val in checked_terms.items():
                    final_glossary[en] = val

            # Normalize final_glossary so every key is a valid non-empty string and every value is [target_str, tag_str]
            normalized_glossary = {}
            for k, v in final_glossary.items():
                k_str = str(k).strip()
                if not k_str: continue
                if k_str.lower() in GENERIC_MULTIWORD_BLACKLIST:
                    continue
                if isinstance(v, list):
                    t_str = str(v[0]) if len(v) > 0 and v[0] is not None else ""
                    tag_str = str(v[1]) if len(v) > 1 and v[1] in VALID_TAGS else "General"
                else:
                    t_str = str(v) if v is not None else ""
                    tag_str = "General"
                normalized_glossary[k_str] = [t_str, tag_str]
            final_glossary = normalized_glossary

            # Save to active profile
            if self.main_app and hasattr(self.main_app, '_save_glossary_to_active_profile'):
                # If dialog active_profile is the one currently loaded in main_app
                main_current = getattr(self.main_app, 'current_profile_name', 'Default')
                if main_current == prof_name:
                    self.main_app._save_glossary_to_active_profile(final_glossary)
                else:
                    prof["glossary"] = final_glossary
                    TStudioCore.save_profile_data(prof_name, prof)
            else:
                prof["glossary"] = final_glossary
                TStudioCore.save_profile_data(prof_name, prof)

            self._refresh_profile_stat_badge()
            action_name = "แทนที่" if overwrite else "ผสาน"
            QMessageBox.information(
                self, "นำเข้าสำเร็จ",
                f"ดำเนินการ {action_name} คำศัพท์จำนวน {len(checked_terms)} คำ เข้าสู่โปรไฟล์ '{prof_name}' เรียบร้อยแล้ว!\n"
                f"ยอดคำศัพท์รวมในโปรไฟล์ขณะนี้: {len(final_glossary)} คำ"
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "เกิดข้อผิดพลาดในการนำเข้า", f"ไม่สามารถนำเข้าคำศัพท์ได้:\n{str(e)}")

    def _export_staged_terms(self):
        target_dir = TStudioCore.get_translation_workspace_dir(
            hint_path=getattr(self.main_app, 'csv_path', None) if self.main_app else None,
            profile_name=getattr(self, 'active_profile', None)
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self, "ส่งออกคำศัพท์ในตะกร้า", os.path.join(target_dir, f"TLM_Glossary_{self.active_profile}.csv"),
            "CSV Files (*.csv);;JSON Files (*.json)"
        )
        if not file_path: return

        data = []
        for r in range(self.tbl_staging.rowCount()):
            en_item = self.tbl_staging.item(r, 1)
            th_item = self.tbl_staging.item(r, 2)
            tag_item = self.tbl_staging.item(r, 3)
            ctx_item = self.tbl_staging.item(r, 4)
            alt_item = self.tbl_staging.item(r, 5)
            if en_item and th_item and en_item.text().strip():
                data.append({
                    "en": en_item.text().strip(),
                    "th": th_item.text().strip(),
                    "tag": tag_item.text().strip() if tag_item else "General",
                    "context": ctx_item.text().strip() if ctx_item else "",
                    "alt": alt_item.text().strip() if alt_item else ""
                })

        try:
            if file_path.lower().endswith(".json"):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["English", "Thai", "Tag", "Context", "Alternative"])
                    for row in data:
                        writer.writerow([row["en"], row["th"], row["tag"], row["context"], row["alt"]])

            QMessageBox.information(self, "ส่งออกสำเร็จ", f"ส่งออกคำศัพท์จำนวน {len(data)} คำ เรียบร้อยแล้ว:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"ไม่สามารถส่งออกไฟล์ได้: {e}")
