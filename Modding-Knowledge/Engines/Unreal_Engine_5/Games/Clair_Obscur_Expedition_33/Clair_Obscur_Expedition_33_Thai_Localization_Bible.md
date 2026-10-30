# Clair Obscur: Expedition 33 — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
เอกสารนี้วิเคราะห์กลไกม็อดภาษาไทยของ **Clair Obscur: Expedition 33** อย่างละเอียดที่สุด เกมนี้สร้างด้วย **Unreal Engine 5** (internal codename: **Sandfall**) และใช้ระบบ localization มาตรฐาน **LocRes** ม็อดนี้มาในรูปแบบ **PAK v11** ไฟล์เดียว (5.53 MB) ที่บรรจุ **37 entries** — รวมถึง **EB Garamond** (9 weights), **Bai Jamjuree / ใบจามจุรี** (12 weights, ฟอนต์ไทย!), ฟอนต์ display อีก 9 ตัว, Roboto Condensed (5 ตัว Slate), และ Game.locres — โดดเด่นด้วยชุดฟอนต์ที่ครบถ้วนและหลากหลายที่สุดในคลังความรู้

---

## 2. Technical Stack

| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 (Codename: **Sandfall**) |
| **Developer** | Sandfall Interactive |
| **Asset System** | PAK v11 (single file, mixed compression) |
| **Localization System** | **LocRes** (UE standard) |
| **LocRes Locale Slot** | `en/` (English slot override) |
| **Font System** | `.ufont` (embedded raw TTF) + `.ttf` (Slate raw) |
| **Mod Strategy** | PAK Patch (`_P` suffix) ใน Paks folder |
| **Mod Complexity** | ★★★☆☆ (มาตรฐาน UE5 แต่มีฟอนต์เยอะ) |

---

## 3. โครงสร้างไฟล์ (File Architecture)

### 3.1 ภาพรวม
```
Content/Sandfall/Content/Paks/
└── PlaeWaiLenEng-Windows_P.pak    ← 5.53 MB  ★ ไฟล์ม็อดเดียว (PAK v11)
```

> **PlaeWaiLenEng** = "แปลว่าเล่นอิง" — ชื่อที่ผู้สร้างม็อดไทยตั้งให้ (Thai modder naming style)

### 3.2 Install Path
```
{GameInstall}/Sandfall/Content/Paks/PlaeWaiLenEng-Windows_P.pak
```

---

## 4. PAK Analysis

### 4.1 PAK Header
| ฟิลด์ | ค่า |
|---|---|
| **Format** | UE PAK v11 |
| **Magic** | `E1 12 6F 5A` at offset 5,798,917 |
| **Mount Point** | `../../../Sandfall/Content/` |
| **Entry Count** | **37** |
| **Index Offset** | 5,795,742 |
| **Index Size** | 575 bytes |
| **Encrypted** | ❌ No |
| **Entropy** | Mixed: ~3.9–4.1 (raw font data) to ~5.9 (metadata) |

### 4.2 Entropy Profile
```
0-528KB:    ent ~5.8-6.0  ← UAsset metadata + LocRes
528-1152KB: ent ~3.9-4.1  ← RAW FONT DATA (Bai Jamjuree/Sarabun)  ★
1168-1600KB: ent ~4.2-4.6 ← More font data
1600-5500KB: ent ~4.5-5.9 ← Mixed fonts + remaining assets
5500-5800KB: ent ~3.8-5.2 ← Index + footer
```

> **Entropy 3.9–4.1** ใน PAK v11 = ข้อมูลฟอนต์ **ไม่ถูก compress** — ทำให้สามารถดึง TTF ออกมาจาก binary ได้โดยตรง!

---

## 5. LocRes — ระบบข้อความ

| ฟิลด์ | ค่า |
|---|---|
| **ไฟล์** | `Game.locres` |
| **Path** | `Sandfall/Content/Localization/.../en/` |
| **Locale** | `en` (English slot override) |
| **Format** | UE LocRes binary (standard) |

---

## 6. Font System — 37 Entries, 4 Categories

### 6.1 ฟอนต์ไทย: Bai Jamjuree / ใบจามจุรี (12 weights)
| ฟอนต์ | Weight | Italic |
|---|---|---|
| FF_BaiJamjuree-ExtraLight | ExtraLight | ✓ |
| FF_BaiJamjuree-Light | Light | ✓ |
| FF_BaiJamjuree-Regular | Regular | ✓ |
| FF_BaiJamjuree-Medium | Medium | ✓ |
| FF_BaiJamjuree-SemiBold | SemiBold | ✓ |
| FF_BaiJamjuree-Bold | Bold | ✓ |

> **Bai Jamjuree (ใบจามจุรี)** = ฟอนต์ไทย-อังกฤษจาก **Cadson Demak** (Google Fonts) — ออกแบบมาสำหรับจอ, อ่านง่าย, มีทั้ง Upright + Italic ครบ 12 weights — ชื่อ "ใบจามจุรี" (ใบของต้นจามจุรี) สื่อถึงความเรียบง่ายแต่สง่างาม

### 6.2 ฟอนต์เกม: EB Garamond (9 weights)
| ฟอนต์ | Weight |
|---|---|
| EBGaramond-Regular | Regular |
| EBGaramond-Medium | Medium |
| EBGaramond-SemiBold | SemiBold |
| EBGaramond-Bold | Bold |
| EBGaramond-ExtraBold | ExtraBold |
| + Italic variants | (Bold, ExtraBold, Medium) |

> **EB Garamond** = ฟอนต์ Serif สไตล์ Claude Garamond (ศตวรรษที่ 16) เหมาะกับธีม Art Deco / Belle Époque ของเกม

### 6.3 ฟอนต์ Display/Decorative
| ฟอนต์ | ลักษณะ |
|---|---|
| **IM FELL Double Pica** (2 weights) | 18th century typography |
| **IM FELL DW Pica** | Historical display |
| **Libre Baskerville** (3 weights) | Transitional serif (reading) |
| **Portmanteau Regular** | Decorative display |
| **Sherlock Vintage** | Victorian/detective style ★ |
| **Trajan Pro** (2 weights) | Roman monumental inscriptions |

### 6.4 Slate UI: Roboto Condensed (5 variants)
| ฟอนต์ | Weight |
|---|---|
| RobotoCondensed-Bold | Bold |
| RobotoCondensed-BoldItalic | Bold Italic |
| RobotoCondensed-Light | Light |
| RobotoCondensed-LightItalic | Light Italic |
| RobotoCondensed-Regular | Regular |

---

## 7. Extracted Fonts — Real TTF Files

ฟอนต์ **16 ตัว** ดึงออกมาเป็น **ไฟล์ TTF จริง** สำเร็จจาก PAK v11:

### 🇹🇭 Thai Fonts (Sarabun Family — 14 weights)
> **.ufont** ที่ชื่อ **Bai Jamjuree** เก็บ **Sarabun** ข้างใน — อาจเป็นเพราะ mod patcher เปลี่ยนฟอนต์ภายใน .ufont wrapper

| ไฟล์ TTF | ขนาด | Weight |
|---|---|---|
| Sarabun_Regular.ttf | 81 KB | Regular |
| Sarabun_Italic.ttf | 84 KB | Italic |
| Sarabun_Light.ttf | 81 KB | Light |
| Sarabun_Light_Italic.ttf | 84 KB | Light Italic |
| Sarabun_ExtraLight.ttf | 81 KB | ExtraLight |
| Sarabun_ExtraLight_Italic.ttf | 84 KB | ExtraLight Italic |
| Sarabun_Medium.ttf | 81 KB | Medium |
| Sarabun_Medium_Italic.ttf | 84 KB | Medium Italic |
| Sarabun_SemiBold.ttf | 81 KB | SemiBold |
| Sarabun_SemiBold_Italic.ttf | 84 KB | SemiBold Italic |
| Sarabun_Bold.ttf | 81 KB | Bold |
| Sarabun_Bold_Italic.ttf | 84 KB | Bold Italic |
| Sarabun_ExtraBold.ttf | 81 KB | ExtraBold |
| Sarabun_ExtraBold_Italic.ttf | 83 KB | ExtraBold Italic |

### 🇹🇭 Thai Supplement
| ไฟล์ TTF | ขนาด | หน้าที่ |
|---|---|---|
| **Noto_Sans_Thai_Looped_Regular.ttf** | 270 KB | Thai Looped glyphs (มีหัว) |

> **Noto Sans Thai Looped** = variant ของ Noto Sans Thai ที่มี **หัวตัวอักษร** (looped glyphs) — traditional Thai style

### 🎭 Game Display Font
| ไฟล์ TTF | ขนาด | หน้าที่ |
|---|---|---|
| **Sherlock_Vintage.ttf** | 1,014 KB | Victorian detective-style display |

---

## 8. Font Architecture Deep Dive

### 8.1 Bai Jamjuree ≠ Sarabun — Font Swapping
ม็อดนี้ใช้เทคนิค **Font Swapping** ที่น่าสนใจ:

```
.ufont wrapper:  FF_BaiJamjuree-Bold.ufont
↓ ภายใน .ufont:  Sarabun Bold (TTF data)
```

> **กลยุทธ์:** แทนที่จะเปลี่ยน font asset path ทั้งหมด (ซึ่งต้องแก้ UAsset references) ม็อดเดอร์ **ใส่ Sarabun ลงใน .ufont wrapper ของ Bai Jamjuree** — เกมเรียก Bai Jamjuree แต่จริงๆ ได้ Sarabun

> ทั้ง **Sarabun** และ **Bai Jamjuree** เป็นฟอนต์จาก **Cadson Demak** (ดีไซเนอร์ไทย) มี metrics คล้ายกัน ทำให้ swap ได้อย่างราบรื่น

### 8.2 EB Garamond + Sarabun — Font Pairing
เกมออกแบบด้วย **EB Garamond** (Serif, ยุโรป) ม็อดเพิ่ม **Sarabun** (Sans-serif, ไทย) — เป็น font pairing ที่ contrast กันแต่ทำงานร่วมกันได้ดี:
- **EB Garamond** → หัวข้อ, ชื่อเกม, quote (Serif elegance)
- **Sarabun** → body text ไทย, UI elements (Sans-serif clarity)

---

## 9. Pipeline — ขั้นตอนสร้างม็อด

```
ขั้นตอนที่ 1: สกัด PAK ของเกม
    UnrealPak.exe -Extract pakchunk0-Windows.pak
    → ได้ .ufont + Game.locres ต้นฉบับ
        ↓
ขั้นตอนที่ 2: แปลข้อความ
    แก้ไข Game.locres ด้วย LocRes Editor
        ↓
ขั้นตอนที่ 3: Font Swap
    - ดาวน์โหลด Sarabun (Google Fonts, 14 weights)
    - ดาวน์โหลด Noto Sans Thai Looped (Google Fonts)
    - Wrap Sarabun เข้าไปใน .ufont ของ Bai Jamjuree (swap)
        ↓
ขั้นตอนที่ 4: Pack PAK v11
    UnrealPak.exe -Create PlaeWaiLenEng-Windows_P.pak
        ↓
ขั้นตอนที่ 5: ติดตั้ง
    วาง PAK ไปที่: {GameInstall}/Sandfall/Content/Paks/
        ↓
เสร็จสิ้น!
```

---

## 10. สถิติม็อด

| ข้อมูล | จำนวน |
|---|---|
| **ไฟล์ม็อด** | 1 ไฟล์ (PAK v11) |
| **ขนาด** | 5.53 MB |
| **PAK Version** | 11 |
| **PAK Entries** | 37 |
| **LocRes** | 1 (Game.locres) |
| **Font entries (.ufont)** | 26 |
| **Font entries (.ttf Slate)** | 5 |
| **ฟอนต์จริงที่ดึงออกมา** | 16 TTF (14 Sarabun + 1 Noto Thai Looped + 1 Sherlock Vintage) |
| **Font families (PAK)** | EB Garamond (9) + Bai Jamjuree (12) + Display (5) + Roboto (5) + misc (6) |

---

## 11. ความพิเศษของม็อดนี้

### 11.1 Font Swapping (Bai Jamjuree → Sarabun)
ม็อดเดอร์ใช้เทคนิค **Font Swap** — ใส่ Sarabun ลงใน .ufont wrapper ของ Bai Jamjuree เพื่อเลี่ยงการแก้ UAsset references

### 11.2 ครบทุก Weight (14/14)
Sarabun ถูก extract ออกมาได้ **ครบทั้ง 14 weights** (7 upright + 7 italic) จาก ExtraLight ถึง ExtraBold — ครบถ้วนที่สุดในคลังความรู้

### 11.3 Noto Sans Thai Looped
ใช้ **Looped variant** ของ Noto Sans Thai (มีหัวตัวอักษร) เป็น fallback

### 11.4 PAK v11 Raw Font Storage
ถึงแม้ PAK v11 ปกติ compress ด้วย Oodle แต่ font data ใน PAK นี้ถูกเก็บ **raw** (entropy ~3.9-4.1) ทำให้ดึงได้โดยตรง

### 11.5 Historical Font Collection
เกม Clair Obscur มีชุดฟอนต์ที่สื่อถึง **ยุค Belle Époque / Art Deco** — EB Garamond, IM FELL, Libre Baskerville, Trajan Pro, Sherlock Vintage — ทุกตัวสะท้อนธีม "ยุคเก่า" ของเกม

---

## 12. เปรียบเทียบ

| เกม | Engine | PAK Ver | LocRes | Fonts Extracted | Thai Font | Complexity |
|---|---|---|---|---|---|---|
| **Clair Obscur** | UE5 | 11 | 1 | 16 TTF | Sarabun (14w) + Noto Looped | ★★★☆☆ |
| **Cronos** | UE5 | 4 | 2 | 11 TTF | 5 families (11 files) | ★★★☆☆ |
| **Code Vein II** | UE5 | 3 + IoStore | 1 | 12 (TTF+OTF) | Sarabun (1w) | ★★★★☆ |
| **Lords of the Fallen** | UE5 | 11 | 1 | 0 (need UnrealPak) | NotoSansThai Variable | ★★★☆☆ |

---

## 13. Conclusion

ม็อดภาษาไทยของ **Clair Obscur: Expedition 33** โดดเด่นด้วย:

1. **Sarabun ครบ 14 weights** — จาก ExtraLight ถึง ExtraBold ทั้ง Upright + Italic — ชุดฟอนต์ไทยที่สมบูรณ์ที่สุดในคลังความรู้
2. **Font Swapping** — ใส่ Sarabun ลงใน .ufont wrapper ของ Bai Jamjuree (ทั้งสองจาก Cadson Demak)
3. **Noto Sans Thai Looped** — fallback font ที่มีหัวตัวอักษร (traditional style)
4. **PAK v11 Raw Storage** — ฟอนต์ไม่ถูก compress (entropy ~3.9) ดึง TTF จริงได้โดยตรง
5. **Historical Font Collection** — EB Garamond, IM FELL, Trajan Pro, Sherlock Vintage ทั้งหมดสะท้อนธีม Belle Époque ของเกม
6. **Single File** — ทุกอย่างใน PAK ไฟล์เดียว 5.53 MB — ลบไฟล์เดียว = เกมกลับปกติ

---

## 14. Extracted Assets

- **Fonts (16 ไฟล์จริง TTF):** [Assets/Fonts/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Clair_Obscur_Expedition_33/Assets/Fonts)
  - **Sarabun** (14 weights) ★ ไทย
  - **Noto_Sans_Thai_Looped_Regular.ttf** (270 KB) ★ ไทย Looped
  - **Sherlock_Vintage.ttf** (1,014 KB) — Game display

- **Texts:** [Assets/Texts/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Clair_Obscur_Expedition_33/Assets/Texts)
  - *Game.locres อยู่ใน PAK — ต้องใช้ UnrealPak*

- **Configs:** [Assets/Configs/](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Clair_Obscur_Expedition_33/Assets/Configs)
  - [PAK_Content_Listing.txt](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/Unreal_Engine_5/Games/Clair_Obscur_Expedition_33/Assets/Configs/PAK_Content_Listing.txt) — 37 entries
