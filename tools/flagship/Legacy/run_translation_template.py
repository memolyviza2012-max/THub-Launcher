# -*- coding: utf-8 -*-
"""
run_translation_template.py
============================
สคริปต์แปลภาษาอัจฉริยะ (Context-Aware Batch Engine) — Template Version
ใช้คู่กับ Translation_Studio_Template.py

อ่าน TEMPLATE_README.md ก่อนใช้งาน!
"""

import csv
import time
import requests
import os
import re
import json
import warnings
import sys

sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings("ignore")

# ╔══════════════════════════════════════════════════════════════════╗
# ║           PROJECT CONFIGURATION — แก้ตรงนี้เท่านั้น!            ║
# ║   AI: อ่าน TEMPLATE_README.md ก่อนแก้ไขส่วนนี้ทุกครั้ง         ║
# ╚══════════════════════════════════════════════════════════════════╝
GAME_NAME          = "Game Name"         # ชื่อเกม (ใช้ใน AI Prompt และหัวหน้าต่าง)
CSV_FILEPATH       = r""                 # Path ไปยังไฟล์ CSV หลัก
CSV_ENCODING       = "utf-8"             # Encoding: "utf-8", "utf-8-sig", "utf-16-le"
COL_ID             = 0                   # คอลัมน์ที่เก็บ ID
COL_SOURCE         = 1                   # คอลัมน์ที่เก็บข้อความต้นฉบับ
COL_TRANS          = 2                   # คอลัมน์ที่เก็บคำแปล
BATCH_TARGET_CHARS = 3000                # ขนาดของแต่ละ Batch (ตัวอักษร) — แก้ได้ถ้าต้องการ
# ═══════════════════════════════════════════════════════════════════

# ==============================================================================
# [ส่วนที่ 1: ตั้งค่าระบบ — อ่านค่าจาก config.json และ glossary.json]
# ==============================================================================
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH   = os.path.join(BASE_DIR, "config.json")
GLOSSARY_PATH = os.path.join(BASE_DIR, "glossary.json")

try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        _cfg   = json.load(f)
        API_KEY = _cfg.get("api_key", "")
        MODEL   = _cfg.get("model", "deepseek-chat")
except:
    API_KEY = ""
    MODEL   = "deepseek-chat"

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
TEMPERATURE  = 0.3
MAX_TOKENS   = 8192
MAX_RETRIES  = 5
RETRY_BASE_S = 5

# ==============================================================================
# [ส่วนที่ 2: Hard Glossary Enforcer — อ่านจาก glossary.json ที่ใช้ร่วมกับ Studio]
# ==============================================================================
try:
    with open(GLOSSARY_PATH, 'r', encoding='utf-8') as f:
        HARD_GLOSSARY_FIXES = json.load(f)
except:
    HARD_GLOSSARY_FIXES = {}

# ==============================================================================
# [ส่วนที่ 3: Master System Prompt]
# ==============================================================================
# ⚠️ AI: ปรับ SYSTEM_PROMPT ให้เหมาะกับโปรเจคใหม่
# - เปลี่ยนชื่อเกม, ประเภทข้อความ, สไตล์การแปล
# - เพิ่ม/ลด Context Awareness ตาม ID Pattern ของเกมนั้นๆ
SYSTEM_PROMPT = f"""I want you to act as a Master-Level English-to-Thai Video Game Localization Specialist for '{GAME_NAME}'.

=== 1. GENERAL RULES ===
- Translate naturally into Thai. Do NOT use overly formal or robotic language.
- Preserve the tone and emotion of the original text.
- For spoken dialogue: use natural conversational Thai (ฉัน, แก, คุณ, มึง, กู depending on character).
- For UI/quest text: use clear, concise instructions.

=== 2. OFFICIAL GLOSSARY (EXACT MATCH) ===
Respect these terms exactly as listed. Do NOT translate them differently.
(Terms will be enforced by the script automatically from glossary.json)

=== 3. FORMATTING (ABSOLUTE LAWS) ===
1. PRESERVE VARIABLES: Keep [TAG_0], [TAG_1], {{0}}, {{1}} exactly intact.
2. EXACT OUTPUT FORMAT: Return ONLY tab-separated lines:
"ID_XXXXX" [TAB] "THAI_TRANSLATION"
"""

# ==============================================================================
# [ส่วนที่ 4: ฟังก์ชันจัดการข้อความและแปลภาษา (Helper Functions)]
# ==============================================================================
def is_translated(text):
    """ตรวจว่าข้อความนี้ถูกแปลแล้วหรือยัง (ตรวจสอบว่ามีอักษรไทยหรือไม่)"""
    if not text or not isinstance(text, str): return False
    return bool(re.search(r'[\u0E00-\u0E7F]', text))

def mask_tags(text):
    """ซ่อน Tags/Variables ชั่วคราวก่อนส่งให้ AI เพื่อป้องกันการแปลผิดพลาด"""
    tag_pattern = r'(<[^>]+>|\\n|\\r|\n|\r|%[sdiefg]|\{\d+\}|\[\[[^\]]+\]\])'
    tags = re.findall(tag_pattern, text)
    masked_text = text
    placeholders = {}
    for idx, tag in enumerate(tags):
        placeholder = f"[TAG_{idx}]"
        if placeholder not in placeholders:
            placeholders[placeholder] = tag
        masked_text = masked_text.replace(tag, placeholder, 1)
    return masked_text, placeholders

def unmask_tags(translated_text, placeholders):
    """คืน Tags/Variables กลับมาหลังจาก AI แปลเสร็จแล้ว"""
    unmasked = translated_text
    for placeholder, original_tag in placeholders.items():
        unmasked = unmasked.replace(placeholder, original_tag)
    return unmasked

def enforce_glossary(text):
    """บังคับแก้คำแปลที่ AI หลุด Glossary — อ่านจากไฟล์ glossary.json เดียวกับ Studio"""
    for wrong_word, correct_word in HARD_GLOSSARY_FIXES.items():
        text = text.replace(wrong_word, correct_word)
    return text

def translate_batch(batch_tasks, batch_num, total_batches):
    """ส่งข้อความทั้ง Batch ไปให้ AI แปลในครั้งเดียว"""
    lines = [f'"{task["game_id"]}"\t"{task["masked_text"]}"' for task in batch_tasks]
    user_prompt = f"Translate these {len(batch_tasks)} entries:\n" + "\n".join(lines)

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user",   "content": user_prompt.strip()}
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=120)
            if response.status_code == 429:
                sleep_time = RETRY_BASE_S * (2 ** (attempt - 1))
                print(f"  [429] Rate Limit ชน! นอนรอ {sleep_time} วินาที... (รอบที่ {attempt}/{MAX_RETRIES})")
                time.sleep(sleep_time)
                continue
            if response.status_code == 401:
                print("  [401] API Key ไม่ถูกต้องหรือหมดอายุ กรุณาตรวจสอบใน Settings ของ Studio")
                return None
            if response.status_code != 200:
                print(f"  [HTTP {response.status_code}] เกิดข้อผิดพลาด: {response.text[:100]}")
                time.sleep(RETRY_BASE_S)
                continue

            reply = response.json()['choices'][0]['message']['content'].strip()
            reply = re.sub(r'^```[^\n]*\n?', '', reply, flags=re.MULTILINE)
            reply = re.sub(r'\n?```$', '', reply, flags=re.MULTILINE)

            results = {}
            for line in reply.split('\n'):
                line = line.strip()
                if '\t' not in line: continue
                parts = line.split('\t', 1)
                results[parts[0].strip().strip('"')] = parts[1].strip().strip('"')
            return results

        except Exception as e:
            print(f"  [ERROR] {e} — รอ {RETRY_BASE_S} วินาที...")
            time.sleep(RETRY_BASE_S)
    return None

def save_csv_checkpoint(headers, rows, filepath):
    """บันทึก CSV แบบ Atomic (เซฟ .tmp ก่อน แล้วค่อย rename เพื่อป้องกันไฟล์เสีย)"""
    tmp_file = filepath + ".tmp"
    try:
        with open(tmp_file, 'w', encoding=CSV_ENCODING, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        os.replace(tmp_file, filepath)
    except Exception as e:
        print(f"  [ERROR] บันทึกไฟล์ไม่สำเร็จ: {e}")
        if os.path.exists(tmp_file): os.remove(tmp_file)

# ==============================================================================
# [ส่วนที่ 5: ฟังก์ชันหลักการทำงาน (Main Control Flow)]
# ==============================================================================
def main():
    print("=" * 60)
    print(f"  {GAME_NAME} - Context-Aware Translation Engine")
    print(f"  Template Version — คู่กับ Translation_Studio_Template.py")
    print("=" * 60)

    if not API_KEY:
        print("[CRITICAL] ยังไม่ได้ตั้งค่า API_KEY!")
        print("           กรุณาเปิด Translation_Studio_Template.py > Settings > ใส่ API Key")
        return

    if not CSV_FILEPATH:
        print("[CRITICAL] ยังไม่ได้ตั้งค่า CSV_FILEPATH!")
        print("           กรุณาแก้ไข CSV_FILEPATH ในส่วน PROJECT CONFIGURATION")
        return

    if not os.path.exists(CSV_FILEPATH):
        print(f"[ERROR] ไม่พบไฟล์ CSV ที่: {CSV_FILEPATH}")
        return

    print(f"[1/4] กำลังอ่านไฟล์ CSV: {CSV_FILEPATH}")
    csv_rows = []
    csv_headers = []
    try:
        with open(CSV_FILEPATH, 'r', encoding=CSV_ENCODING, newline='') as f:
            reader = csv.reader(f)
            csv_headers = next(reader)
            for row in reader:
                while len(row) <= max(COL_ID, COL_SOURCE, COL_TRANS): row.append("")
                csv_rows.append(row)
    except Exception as e:
        print(f"[ERROR] เปิดไฟล์ไม่สำเร็จ: {e}")
        return
    print(f"[2/4] โหลดข้อมูลเสร็จสิ้น: จำนวนทั้งสิ้น {len(csv_rows):,} รายการ")

    pending_tasks = []
    for row_idx, row in enumerate(csv_rows):
        game_id        = row[COL_ID]
        source_text    = row[COL_SOURCE]
        current_trans  = row[COL_TRANS]
        if is_translated(current_trans): continue
        if not source_text.strip(): continue
        masked_text, placeholders = mask_tags(source_text)
        pending_tasks.append({
            "row_idx": row_idx, "game_id": game_id,
            "raw_text": source_text, "masked_text": masked_text,
            "placeholders": placeholders
        })
    print(f"[3/4] ตรวจสอบเสร็จสิ้น: มีข้อความรอแปลทั้งสิ้น {len(pending_tasks):,} รายการ")

    if not pending_tasks:
        print("      ยินดีด้วยครับ! แปลครบ 100% เรียบร้อยแล้ว!")
        return

    batches, current_batch, current_chars = [], [], 0
    for task in pending_tasks:
        current_batch.append(task)
        current_chars += len(task["masked_text"])
        if current_chars >= BATCH_TARGET_CHARS:
            batches.append(current_batch)
            current_batch, current_chars = [], 0
    if current_batch: batches.append(current_batch)
    print(f"      แบ่งกลุ่มทำงาน (Batches): {len(batches)} กลุ่ม (~{BATCH_TARGET_CHARS} ตัวอักษรต่อกลุ่ม)")

    print("\n[4/4] เริ่มเดินเครื่องแปลภาษาไทยด้วย DeepSeek...")
    translated_count, failed_count = 0, 0
    start_time = time.time()

    for idx, batch in enumerate(batches, 1):
        elapsed = time.time() - start_time
        print(f"\n  --- กำลังรันกลุ่มที่ {idx}/{len(batches)} (มีทั้งหมด {len(batch)} ข้อความ) ---")
        print(f"  เวลาที่ใช้ไปแล้ว: {int(elapsed // 60)} นาที {int(elapsed % 60)} วินาที")

        api_results = translate_batch(batch, idx, len(batches))
        if not api_results:
            print(f"  [FAIL] กลุ่มที่ {idx} แปลไม่สำเร็จ ยกยอดไปรอบหน้า")
            failed_count += len(batch)
            continue

        for task in batch:
            tid = task["game_id"]
            if tid in api_results:
                final_thai = unmask_tags(api_results[tid], task["placeholders"])
                final_thai = enforce_glossary(final_thai)
                print(f"    [แปล] {task['raw_text'][:40]}... -> {final_thai[:40]}...")
                csv_rows[task["row_idx"]][COL_TRANS] = final_thai
                translated_count += 1
            else:
                print(f"  [WARN] ไม่พบผลลัพธ์สำหรับ {tid}")
                failed_count += 1

        save_csv_checkpoint(csv_headers, csv_rows, CSV_FILEPATH)
        print(f"  สำเร็จสะสม: {translated_count} ข้อความ  |  ตกหล่น: {failed_count} ข้อความ")

    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("      ปฏิบัติการแปลไทยสำเร็จเสร็จสิ้น!")
    print("=" * 60)
    print(f"  - แปลเสร็จสิ้นทั้งหมด  : {translated_count:,} ข้อความ")
    print(f"  - ข้อความที่ข้าม/ตกหล่น: {failed_count:,} ข้อความ")
    print(f"  - เวลารวม               : {int(total_time // 60)} นาที {int(total_time % 60)} วินาที")
    print(f"  - อัปเดตคลังแสงที่      : {CSV_FILEPATH}")
    print("=" * 60)

if __name__ == "__main__":
    main()
