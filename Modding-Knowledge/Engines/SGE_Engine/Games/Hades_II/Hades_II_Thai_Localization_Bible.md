# Hades II — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Hades II is a roguelike action game developed by **Supergiant Games** using their proprietary **SGE (Supergiant Engine)** built on **FNA/MonoGame**. The Thai localization mod uses the simplest and most elegant architecture in our entire knowledge base: **Pure Lua Script Replacement**. The game's entire text and logic system is driven by plaintext `.lua` files that sit in `Content/Scripts/`, and the modder simply translated every string in-place across all 226 scripts. No binary patching, no archive repacking, no DLL injection — just text editing.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | SGE (Supergiant Engine) / FNA / MonoGame |
| **Developer** | Supergiant Games |
| **Mod Author** | ไม่ระบุ |
| **Archive Format** | None — **Loose Lua scripts** (ไม่มีการแพ็คไฟล์!) |
| **Font System** | Engine-managed (P22UndergroundSCMedium + custom) |
| **Thai Font** | **Chakra Petch** (Google Fonts, OFL license — ไม่ได้แนบ TTF มา) |
| **Text System** | Lua string literals ภายในไฟล์ `.lua` |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★☆☆☆ (Simplest possible — pure text replacement) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

```text
Hades II/
├── Content/
│   └── Scripts/                        (226 ไฟล์ Lua, 19.1 MB รวม)
│       ├── NPCData_Odysseus.lua        (582 KB — 82,853 Thai chars 🥇)
│       ├── NPCData_Hecate.lua          (513 KB — 81,986 Thai chars)
│       ├── NPCData_Moros.lua           (483 KB — 76,278 Thai chars)
│       ├── NPCData_Nemesis.lua         (604 KB — 72,575 Thai chars)
│       ├── NPCData.lua                 (533 KB — 71,441 Thai chars)
│       ├── HeroData.lua                (533 KB — 52,278 Thai chars)
│       ├── QuestData.lua               (162 KB)
│       ├── PatchLogic.lua              (66 KB)
│       ├── RoomLogic.lua               (217 KB)
│       ├── SpellLogic.lua              (118 KB)
│       ├── ... และอีก 216 ไฟล์
│       └── [Total: 226 Lua files]
│
└── licenses/
    └── ChakraPetch-OFL.txt             (4 KB — SIL Open Font License)
```

### สถาปัตยกรรม "Zero Packaging"
ม็อดนี้ไม่มีการแพ็คไฟล์ใดๆ เลย! Supergiant Games ออกแบบ SGE ให้โหลด Lua scripts ดิบๆ จากโฟลเดอร์ `Content/Scripts/` ทำให้ม็อดเดอร์แค่แก้ไฟล์ `.lua` แล้ววางทับได้เลย — เป็นสถาปัตยกรรมม็อดที่เรียบง่ายที่สุดในคลังเกมทั้งหมดของเรา

---

## 4. Font Analysis

### 4.1 Chakra Petch — ฟอนต์ไทยของม็อด
- **ที่มา:** Google Fonts (Chakra Petch Project by Cadson Demak)
- **License:** SIL Open Font License 1.1 (แนบใบอนุญาตมาด้วย)
- **หมายเหตุ:** ม็อดไม่ได้แนบไฟล์ `.ttf` มาในแพ็คเกจ — ฟอนต์ถูกติดตั้งแยกต่างหาก หรือถูกฝังไว้ในเกมฝั่ง engine assets ที่อยู่นอกโฟลเดอร์ม็อด
- **Font Extraction:** ❌ ไม่มีไฟล์ TTF ในม็อด (สามารถดาวน์โหลดได้จาก [Google Fonts](https://fonts.google.com/specimen/Chakra+Petch))

### 4.2 P22UndergroundSCMedium — ฟอนต์ต้นฉบับ
- พบการอ้างอิงในไฟล์ `BountyData.lua`: `Font = "P22UndergroundSCMedium"`
- เป็นฟอนต์ต้นฉบับของเกม (ไม่ใช่ฟอนต์ไทย)

---

## 5. Text Analysis

### 5.1 สถิติอันยิ่งใหญ่ 🏆
- **ไฟล์ทั้งหมด:** 226 Lua scripts
- **ขนาดรวม:** 19.1 MB
- **Thai Characters:** **1,871,111 ตัวอักษร**
- **ไฟล์ที่มีภาษาไทย:** 226/226 (**ทุกไฟล์!**)

### Thai Character Ranking (All-Time KB):
| อันดับ | เกม | Thai Chars | ระบบ |
|---|---|---|---|
| 🥇 1 | KCD2 | 5,170,838 | CryEngine (XML) |
| 🥈 2 | KCD1 | 3,314,378 | CryEngine (XML) |
| 🥉 3 | Rune Factory 5 | 2,298,835 | Unity (Injection) |
| 4 | **Hades II** | **1,871,111** | **SGE (Lua Scripts)** |
| 5 | Midnight Suns | 1,792,657 | UE4 (Locres) |

*Hades II ครองอันดับ 4 ตลอดกาล!*

### 5.2 ตัวอย่างข้อความไทย
```lua
{ Cue = "/VO/Melinoe_1707", Text = "โครนอสต้องตายค่ะ ท่าน" }
{ Cue = "/VO/Odysseus_0216", Text = "ขอคารวะ เทพธิดา" }
{ Cue = "/VO/Odysseus_0217", Text = "สักวันท่านต้องจัดการเขาได้" }
{ Cue = "/VO/Odysseus_0224", Text = "เขาต้องได้รับผลกรรม" }
```

---

## 6. Cross-Engine Comparison

| Feature | Hades II | Sea of Stars | Rune Factory 5 |
|---|---|---|---|
| **Engine** | SGE (FNA) | Unity | Unity (IL2CPP) |
| **Text Format** | Lua scripts (.lua) | Addressable Bundle | BepInEx Injection |
| **Packaging** | **None** (loose files!) | UnityFS Bundle | translations.txt |
| **Text Encoding** | UTF-8 | UTF-8 | UTF-8 |
| **Thai Chars** | 1.87M | ~150K | 2.29M |
| **Mod Files** | 226 | 19 | 7 |
| **Complexity** | ★★☆☆☆ | ★★★★☆ | ★★★★☆ |

**จุดเด่น:** เรียบง่ายที่สุด! ไม่ต้องแตกไฟล์ ไม่ต้อง compile อะไรทั้งนั้น แค่แก้ Lua แล้ววางทับ
**จุดอ่อน:** เกมอัปเดตทีเดียวม็อดอาจพังทั้ง 226 ไฟล์ เพราะ Supergiant อาจเปลี่ยน logic ในไฟล์

---

## 7. Pipeline — ขั้นตอนสร้างม็อด

1. **ก๊อป Lua ทั้งโฟลเดอร์:** คัดลอก `Content/Scripts/` ทั้งหมดจากเกมต้นฉบับ
2. **แปล Text:** ค้นหาบรรทัดที่มี `Text = "..."` แล้วแปลเป็นไทย (UTF-8)
3. **ติดตั้งฟอนต์:** ติดตั้ง Chakra Petch ลงในระบบเกม (ขึ้นอยู่กับว่า SGE โหลดฟอนต์จากที่ไหน)
4. **วางทับ:** ก๊อปไฟล์ `.lua` ทั้งหมดไปทับในโฟลเดอร์เกม
5. **ทดสอบ:** เล่นเกม ตรวจสอบว่าข้อความไทยแสดงผลถูกต้อง

```bash
# Pipeline ง่ายมาก — แค่ copy!
cp -r Content/Scripts/ "<game_folder>/Content/Scripts/"
```

---

## 8. Troubleshooting
- **ข้อความยังเป็นอังกฤษ:** ไฟล์ Lua ไม่ได้ถูกวางทับ ตรวจสอบว่าอยู่ใน `Content/Scripts/` ของเกม
- **เกมแครช/Lua Error:** ม็อดเวอร์ชันไม่ตรงกับเกม (Supergiant อัปเดตบ่อย)
- **สระลอย/ฟอนต์ผิด:** ฟอนต์ Chakra Petch ไม่ได้ถูกติดตั้ง/โหลดอย่างถูกต้อง
- **อัปเดตเกมแล้วม็อดพัง:** ต้องรอม็อดเดอร์ merge Lua ใหม่ (อาจใช้ diff/merge tool)

---

## 9. Required Tools
| Tool Name | Purpose | Source |
|---|---|---|
| Text Editor (VS Code) | แก้ไข Lua scripts (UTF-8) | [code.visualstudio.com] |
| diff/merge tool | เปรียบเทียบ Lua เมื่อเกมอัปเดต | [meld / WinMerge] |

---

## 10. Extracted Assets
- **Font:** ❌ ไม่มีไฟล์ TTF ในม็อด
  - ม็อดระบุใช้ **Chakra Petch** (ดาวน์โหลดได้ฟรีจาก Google Fonts)
  - License: [ChakraPetch-OFL.txt](file:///D:/Mods%20games/Thai%20Mods/0_Rivet%20Engineer/Hades%20II/licenses/ChakraPetch-OFL.txt)

---

## 11. M2M Protocol
**(สำหรับ AI Agent ที่ต้องการนำคัมภีร์ไปรันสร้างม็อดอัตโนมัติ)**

### AI Automation Score: ★★★★★ (สมบูรณ์แบบ!)
- **Text Translation:** ✅ AI ทำได้ 100% — แค่อ่าน/เขียนไฟล์ `.lua` ที่เป็น UTF-8 plaintext!
- **Pattern:** ค้นหา `Text = "..."` ด้วย regex แล้วแปลข้อความฝั่งขวา
- **Font:** ⚠️ ต้องดาวน์โหลด Chakra Petch จาก Google Fonts แยก
- **Deployment:** ✅ AI สามารถก๊อปไฟล์ `.lua` ไปวางในโฟลเดอร์เกมได้ทันที
- **Merge on Update:** ✅ AI สามารถใช้ diff/merge เปรียบเทียบ Lua เมื่อเกมอัปเดต

**นี่คือเกมที่เหมาะที่สุดสำหรับ AI-Automated Translation Pipeline!**
