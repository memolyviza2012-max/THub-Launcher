# The Alters — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
เอกสารนี้วิเคราะห์กลไกม็อดภาษาไทยของเกม **The Alters** ซึ่งพัฒนาด้วย **Unreal Engine 5** ตัวม็อดถูกแพ็กอยู่ในฟอร์แมต `.pak` แบบมาตรฐาน (ไม่ได้ใช้ `.ucas`/`.utoc` ของ IoStore) ทำให้ง่ายต่อการแกะและการดัดแปลง 

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | Unreal Engine 5 |
| **Archive Format** | Standard `.pak` (No IoStore) |
| **Font System** | FontFace (`.ufont`) ภายในบรรจุฟอนต์ TrueType (.ttf) แบบ Raw |
| **Text System** | Unreal Localization (`.locres`) |
| **Mod Complexity** | ★★☆☆☆ (แกะง่าย, จัดการฟอนต์แบบ 1:1 ได้เลย) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
เมื่อทำการ Unpack ไฟล์ `TheAlters-Windows_P_999.pak` (ขนาด 2.2 MB) ด้วยเครื่องมือ `repak_cli` พบโครงสร้างดังนี้:
```
TheAlters/
└── Content/
    ├── Localization/
    │   └── P9Playable/
    │       └── en/
    │           └── P9Playable.locres (4.3 MB - ไฟล์ข้อความภาษาไทย)
    └── P9Playable/
        └── UI/
            └── Fonts/
                ├── Inter/
                │   ├── Inter-Bold.ufont
                │   ├── Inter-ExtraBold.ufont
                │   ├── Inter-Medium.ufont
                │   ├── Inter-Regular.ufont
                │   └── Inter-SemiBold.ufont
                ├── Inter_ExplorationMAp/
                │   └── Inter-Medium-Exp.ufont
                └── NotoSans/
                    ├── NotoSans-Black.ufont
                    └── NotoSans-SemiBold.ufont
```

---

## 4. Text & Font Analysis

### 4.1 ระบบข้อความ (Text / .locres)
- ม็อดเดอร์ทำการแปลภาษาไทยทับไฟล์ `P9Playable.locres` ในโฟลเดอร์ `en` โดยตรง
- สามารถใช้เครื่องมือมาตรฐานอย่าง **UnrealLocres** ในการสกัดข้อความออกมาเป็น `.csv` และนำเข้ากลับเพื่อแพ็กคืนได้ง่ายมาก

### 4.2 ระบบฟอนต์ (.ufont / .ttf)
- **การค้นพบที่น่าสนใจ:** ไฟล์ `.ufont` ทั้ง 8 ไฟล์ในม็อดนี้ **มีขนาดเท่ากันเป๊ะที่ 101,752 Bytes**
- นี่คือการใช้เทคนิค **"Font Replacement" แบบง่าย**: ม็อดเดอร์ใช้ไฟล์ฟอนต์ภาษาไทยเพียงไฟล์เดียว ก๊อปปี้และเปลี่ยนชื่อเพื่อไปแทนที่ฟอนต์ดั้งเดิมทุกรูปแบบ (Bold, Regular, Medium, NotoSans ฯลฯ) เพื่อให้แน่ใจว่าเกมจะดึงฟอนต์ไทยไปแสดงผลในทุกสถานการณ์โดยไม่ต้องสนใจความหนาของตัวอักษร
- **ผลการสกัดฟอนต์ (Font Extraction):**
  - ด้วยการสแกนหา Header แบบ TrueType (`00 01 00 00`) พบว่าไฟล์ `.ufont` บรรจุไฟล์ `.ttf` ไว้ในสภาพสมบูรณ์ (ไม่มีการใส่ Header ของ Unreal ไว้ด้านหน้า)
  - ฟอนต์ที่ถูกสกัดออกมาได้คือ **Noto Sans Thai Looped Regular** ซึ่งเป็นฟอนต์โอเพนซอร์สของ Google ที่อ่านง่ายและมีหัว

> ✅ **ผลการดึง Asset:**
> สกัดไฟล์ฟอนต์ `NotoSansThaiLooped-Regular.ttf` สำเร็จ! สามารถเข้าไปดูและติดตั้งได้ในโฟลเดอร์ `Assets/Fonts/` ของคลัง Modding Knowledge (The_Alters)

---

## 5. Required Tools
สำหรับผู้ที่ต้องการดัดแปลงม็อดตัวนี้เพิ่มเติม:
| เครื่องมือ | หน้าที่ |
|---|---|
| **repak_cli** (Rust-based) | แตกไฟล์ `.pak` (Unpack) และแพ็กไฟล์กลับ (Pack) |
| **UnrealLocres** | แก้ไขข้อความใน `.locres` เป็น `.csv` |
| **Hex Editor / Script** | ใช้ในการดึงไฟล์ `.ttf` ออกจาก `.ufont` |

---

## 6. Conclusion
The Alters เป็นเกม Unreal Engine 5 ที่เป็นมิตรกับนักทำม็อดภาษาไทยมากที่สุดเกมหนึ่ง เนื่องจากไม่ได้ใช้งาน IoStore และไม่มีระบบล็อกรหัสผ่าน (AES) บนตัวไฟล์ม็อด การเปลี่ยนฟอนต์ใช้วิธียัดไฟล์ Raw `.ttf` เข้าไปแทนที่ `.ufont` ได้เลย ทำให้ประหยัดเวลาอย่างมากในการพัฒนาและทดสอบ
