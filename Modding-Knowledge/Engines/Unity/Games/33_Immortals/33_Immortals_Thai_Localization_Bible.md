# 33 Immortals — Thai Localization Modding Bible
### Advanced Deep Analysis Edition

---

## 1. Overview
เอกสารนี้อธิบายกลไกการม็อดภาษาไทยของเกม **33 Immortals** อย่างละเอียดที่สุด เกมนี้สร้างด้วย **Unity Engine** แต่ใช้ระบบ Localization แบบ **Custom Plaintext** ที่ไม่พึ่ง Unity's built-in localization system ม็อดนี้มีความพิเศษตรงที่เป็นระบบ localization ที่ **ง่ายที่สุดและโปร่งใสที่สุด** ในบรรดาเกมทั้งหมดที่วิเคราะห์มา — ไม่มีการบีบอัด, ไม่มี binary, ไม่มี archive ทุกอย่างเป็น plaintext `.txt`

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unity Engine |
| **Localization System** | Custom Plaintext Key-Value (ไม่ใช่ Unity Localization Package) |
| **Text Format** | `.txt` plaintext — UTF-8 without BOM |
| **Text Encoding** | UTF-8 (ยืนยัน: พบ Thai UTF-8 sequences `E0 B8/B9 xx`, ไม่มี BOM `EF BB BF`) |
| **Config Format** | `.json` (info.json — ระบุชื่อภาษา) |
| **UI Rich Text** | Unity TextMeshPro Rich Text Tags (`<style>`, `<sprite>`, `<voffset>`, `<size>`) |
| **Localization Approach** | **Direct File Override** — วาง `.txt` ทับ locale เดิม |
| **Mod Complexity** | ★☆☆☆☆ (ง่ายที่สุด — แก้ text file แล้ววาง) |

---

## 3. Localization Architecture — โครงสร้างระบบ

### 3.1 โครงสร้างโฟลเดอร์
```
33Immortals_Data/
  └── StreamingAssets/
      └── locale/
          └── en-us/                     ←── Language Folder (ทับ English โดยตรง)
              ├── info.json              ←── {"displayName":"English"}
              ├── beatrice/              ←── NPC: Beatrice dialogues
              ├── coemstics/             ←── Cosmetics descriptions
              ├── collectibles/          ←── Collectible items text
              ├── compendium/            ←── Compendium entries
              ├── dailyevents/           ←── Daily events text
              ├── demo/                  ←── Demo content
              ├── levels/                ←── Level descriptions
              ├── mastery/               ←── Mastery system
              ├── npc/                   ←── NPC dialogues (Virgil, etc.)
              ├── player/                ←── Player-related text
              ├── popup/                 ←── Popup messages
              ├── tutorials/             ←── Tutorial text
              ├── ui/                    ←── UI strings (menus, HUD, etc.)
              ├── update/                ←── Post-launch update text
              ├── update8/               ←── Update 8 specific content
              └── weapon/                ←── Weapon descriptions (7 sins + virtues)
```

### 3.2 สถิติ

| ข้อมูล | จำนวน |
|---|---|
| **ไฟล์ทั้งหมด** | 147 ไฟล์ |
| **ไฟล์ `.txt`** | 146 ไฟล์ |
| **ไฟล์ `.json`** | 1 ไฟล์ (`info.json`) |
| **ขนาดรวม** | 1.49 MB |
| **หมวดหมู่** | 23 โฟลเดอร์ |

---

## 4. Text Format — รูปแบบไฟล์ข้อความ

### 4.1 Key-Value Format
ทุกไฟล์ `.txt` ใช้รูปแบบเดียวกัน — **สลับระหว่างบรรทัด Key และบรรทัด Value**:

```
key: {category}/{key_name} {hash_id} {version} {status}
{translated_text}

key: {category}/{key_name} {hash_id} {version} {status}
{translated_text}
```

### 4.2 ตัวอย่างจริง

```
key: ui/boot.epilepsy.description -6821087917699882751 v1 Rush
เกมนี้มีเนื้อหาที่อาจทำให้เกิดอาการชักในผู้ที่มีความไวต่อแสง กรุณาใช้ความระมัดระวัง

key: ui/boot.epilepsy.title 3867464437270152814 v1 Rush
คำเตือนเรื่องแสงกระพริบ
```

### 4.3 วิเคราะห์ฟิลด์ใน Key Line

| ฟิลด์ | ตัวอย่าง | ความหมาย |
|---|---|---|
| `key:` | `key:` | Keyword prefix (คงที่) |
| Category/Key | `ui/boot.epilepsy.title` | Path-style key identifier (ตรงกับโฟลเดอร์และชื่อไฟล์) |
| Hash ID | `3867464437270152814` | Internal hash สำหรับ lookup ในเกม (signed 64-bit integer) |
| Version | `v1` | เวอร์ชันของ string นี้ |
| Status | `Rush` / `Placeholder` / `ReadyForRevision` | สถานะการแปล |

### 4.4 Translation Status ที่พบ

| Status | ความหมาย |
|---|---|
| `Rush` | แปลเสร็จแล้ว (ส่วนใหญ่) |
| `Placeholder` | ยังเป็น placeholder (บางส่วน) |
| `ReadyForRevision` | แปลแล้วรอตรวจทาน |

### 4.5 Unity Rich Text Tags ที่ใช้
ข้อความรองรับ **TextMeshPro Rich Text** ดังนี้:

| Tag | ตัวอย่าง | หน้าที่ |
|---|---|---|
| `<style=...>` | `<style=BenneTitle26>บทบาท:</style>` | กำหนดสไตล์ตัวอักษร |
| `<sprite=...>` | `<sprite="RPGIcons" name="Sinful">` | แสดงไอคอนแบบ inline |
| `<voffset=...>` | `<voffset=0.24em>ส</voffset>` | ปรับตำแหน่งแนวตั้ง (ใช้แก้ปัญหาสระลอย) |
| `<size=...>` | `<size=160%>` | ปรับขนาดตัวอักษร |

> **สำคัญ:** พบการใช้ `<voffset=0.24em>` ครอบสระลอยภาษาไทยบ่อยมาก — นี่คือเทคนิคแก้ปัญหา **สระไทยลอยสูง/ต่ำไม่ตรง** ใน TextMeshPro ที่ฟอนต์ไม่ได้ถูกออกแบบมาสำหรับภาษาไทยโดยเฉพาะ

---

## 5. Language Slot Strategy

### 5.1 กลยุทธ์: ทับ `en-us` โดยตรง
ม็อดนี้วางไฟล์ข้อความภาษาไทยทับ **โฟลเดอร์ภาษาอังกฤษ (`en-us`)** โดยตรง

- `info.json` ยังคงแสดงเป็น `{"displayName":"English"}` 
- เมื่อเปิดเกมด้วยการตั้งค่าภาษาอังกฤษ → จะแสดงเป็นภาษาไทยทันที
- **ข้อเสีย:** ผู้เล่นไม่สามารถสลับกลับไปภาษาอังกฤษได้ (ต้องลบม็อดออก)

### 5.2 ทางเลือกที่ดีกว่า (สำหรับการพัฒนาต่อ)
สามารถสร้างโฟลเดอร์ `th-th/` ใหม่ แล้วเปลี่ยน `info.json` เป็น `{"displayName":"ไทย"}` — แต่ต้องแก้โค้ดเกมด้วยเพื่อให้รู้จัก locale ใหม่

---

## 6. เนื้อหาแยกตามหมวดหมู่

### 6.1 NPC Dialogues (`npc/`)
| ไฟล์ | ขนาด | เนื้อหา |
|---|---|---|
| `virgil_story.txt` | 80 KB | บทสนทนาหลักของ Virgil (ตัวละครนำ) |
| `beatrice_canto_*.txt` | หลายไฟล์ | บทสนทนาของ Beatrice แยกตาม Canto |
| `virgil_tutorial.txt` | 177 bytes | บทสนทนา tutorial |

### 6.2 UI Strings (`ui/`)
| ไฟล์ | ขนาด | เนื้อหา |
|---|---|---|
| `main_menu.txt` | 45 KB | **ไฟล์ใหญ่สุด** — เมนูหลักทุกรายการ |
| `celebration.txt` | 47 KB | ข้อความฉลองชัยชนะ |
| `quest_board.txt` | 16 KB | กระดานเควส |
| `loading_screen.txt` | 15 KB | ข้อความหน้าโหลด |
| `input_rebinding.txt` | 10 KB | การตั้งค่าปุ่มกด |
| `achievements.txt` | 10 KB | ความสำเร็จ |

### 6.3 Weapon Descriptions (`weapon/`)
อาวุธตั้งชื่อตาม **7 บาป + คุณธรรม** จาก Divine Comedy:

| ไฟล์ | ขนาด | อาวุธ |
|---|---|---|
| `charity.txt` | 4.3 KB | อาวุธแห่งการกุศล |
| `gluttony.txt` | 4.1 KB | อาวุธแห่งความตะกละ |
| `greed.txt` | 4.9 KB | อาวุธแห่งความโลภ |
| `hope.txt` | 4.3 KB | อาวุธแห่งความหวัง |
| `justice.txt` | 4.2 KB | อาวุธแห่งความยุติธรรม |
| `pride.txt` | 3.8 KB | อาวุธแห่งความทะนง |
| `sloth.txt` | 4.9 KB | อาวุธแห่งความเกียจคร้าน |
| `temperance.txt` | 3.5 KB | อาวุธแห่งการควบคุมตน |

### 6.4 Tutorials & Updates
- `tutorials/` — คู่มือสอนเล่น (basic, advanced, weapon mastery)
- `update/` & `update8/` — เนื้อหาที่เพิ่มหลังวันวางจำหน่าย

---

## 7. Complete Pipeline — ขั้นตอนสร้างม็อด

```
ขั้นตอนที่ 1: คัดลอกโฟลเดอร์ locale/en-us/ จากเกม
    (หรือภาษาอื่นที่ต้องการทับ)
        ↓
ขั้นตอนที่ 2: แปลไฟล์ .txt ทุกไฟล์
    - เปิดด้วย Text Editor ที่รองรับ UTF-8
    - แปลเฉพาะบรรทัดที่ 2 ของแต่ละคู่ (Value line)
    - ห้ามแก้ไขบรรทัดที่ 1 (Key line) — เป็น identifier ของเกม
    - ระวังไม่ลบ Rich Text tags (<style>, <sprite>, <voffset>)
        ↓
ขั้นตอนที่ 3: แก้ปัญหาสระไทยลอย (ถ้าจำเป็น)
    - ใช้ <voffset=0.24em>สระ</voffset> เพื่อปรับตำแหน่ง
    - ใช้กับสระที่ลอยสูงเกินไป เช่น สระอิ สระี สระือ ฯลฯ
        ↓
ขั้นตอนที่ 4: วางโฟลเดอร์ที่แปลแล้วทับ locale/en-us/ ในเกม
    33Immortals_Data/StreamingAssets/locale/en-us/ ← วางทับ
        ↓
เสร็จสิ้น! เปิดเกมได้เลย
```

---

## 8. Required Tools

| เครื่องมือ | หน้าที่ | ระดับความจำเป็น |
|---|---|---|
| **Text Editor** (VSCode, Notepad++) | แก้ไขไฟล์ `.txt` | ✅ จำเป็น |
| **UTF-8 Support** | บันทึกไฟล์เป็น UTF-8 without BOM | ✅ จำเป็น |
| **AI Translation** (Gemini, DeepSeek) | แปลข้อความจำนวนมาก | ⚡ แนะนำ |
| **Unity/AssetStudio** | ไม่จำเป็น — ไม่ต้องแตก asset | ❌ ไม่ต้องใช้ |
| **Hex Editor** | ไม่จำเป็น — ไม่มี binary format | ❌ ไม่ต้องใช้ |

---

## 9. เปรียบเทียบความซับซ้อนกับเกมอื่น

| เกม | Engine | วิธีม็อด | ความซับซ้อน |
|---|---|---|---|
| **33 Immortals** | Unity | **วาง .txt ทับ** | ★☆☆☆☆ |
| FRONT MISSION 1st | Unity (IL2CPP) | BepInEx + Harmony hook + JSON | ★★★☆☆ |
| Metro 2033 | 4A Engine | VFS Index + Archive | ★★★☆☆ |
| Ghost Recon Wildlands | Scimitar | QuickBMS + Forge reimport | ★★★★☆ |
| The Evil Within 2 | STEM Engine | PKR/PTR repack + padding | ★★★★★ |
| Deathloop | Void Engine | Full resource repack + OodleLZ | ★★★★★ |

---

## 10. Conclusion
ม็อดภาษาไทยของ **33 Immortals** เป็นตัวอย่างที่สมบูรณ์แบบของ **"Developer-Friendly Localization System"**:

1. **ไม่มี Binary Format** — ทุกอย่างเป็น plaintext `.txt` อ่านได้ด้วย text editor
2. **ไม่มี Archive/Compression** — ไม่ต้อง unpack, decompress, หรือ repack อะไรเลย
3. **Key-Value แบบ Flat File** — format ชัดเจน (key line + value line สลับกัน)
4. **Unity StreamingAssets** — เกมโหลดไฟล์จาก filesystem โดยตรง ไม่ต้อง rebuild asset bundle
5. **เทคนิค `<voffset>`** — วิธีแก้ปัญหาสระไทยลอยใน TextMeshPro ที่น่าสนใจมาก
6. **Hash ID 64-bit** — แม้ format จะง่าย แต่เกมใช้ hash ในการ lookup ทำให้ประสิทธิภาพดี
7. **Translation Status Tracking** — มีระบบติดตามสถานะการแปลในตัว (Rush/Placeholder/ReadyForRevision)

นี่คือ **เกมที่ง่ายที่สุดในการทำ mod ภาษาไทย** จากทั้งหมดที่วิเคราะห์ในคอลเลกชัน Rivet Engineer
