# 🎨 Media Kit & Branding Retrofit Guide (07_Image_Resources)
**Category:** Techniques / Branding & Community Publishing  
**Author:** NodNuatTranslator / TStudio & THub Ecosystem  
**Last Updated:** 2026-09-28 (v2.1 High-Resolution Multi-Size Logo Suite Edition)

---

## 1. วัตถุประสงค์ (Purpose)
คู่มือมาตรฐานสำหรับการยกระดับและจัดระเบียบสื่อประชาสัมพันธ์ (Media Kit & Branding) ในโปรเจกต์ม็อดแปลเกมทุกโปรเจกต์ เพื่อสร้างความน่าเชื่อถือ สวยงาม ดึงดูดผู้เล่น และเข้ากันได้กับระบบ **THub**, **ModderHub**, และหน้าเพจโซเชียลมีเดีย

---

## 2. โครงสร้างโฟลเดอร์มาตรฐาน (Standard Folder Structure)

```text
<Game_Workspace>/
├── thub_cover.jpg                  # ภาพปกขนาด 16:9 แนวนอนสำหรับแสดงในการ์ด THub
└── 07_Image_Resources/
    ├── cover 16-9.psd              # เทมเพลตภาพหน้าปกแนวนอน 16:9 (1920x1080)
    ├── Cover_Post facebook.psd     # เทมเพลตโพสต์เพจ Facebook
    ├── Header copy.psd             # เทมเพลตส่วนหัวม็อด
    ├── Header_facebook.psd         # เทมเพลตแบนเนอร์ปก Facebook Page
    ├── Official_Art/               # ภาพทางการความละเอียดสูงจาก CDN
    │   ├── banner_hero_1920x620.jpg    # Hero Banner อัตราส่วน 1920x620
    │   ├── cover_landscape_616x353.jpg # Capsule แนวนอน 616x353
    │   ├── cover_portrait_600x900.jpg  # Library Capsule แนวตั้ง 2:3 (600x900)
    │   ├── cover_header_460x215.jpg    # Header Store 460x215
    │   ├── official_logo.png           # โลโก้เกมต้นฉบับโปร่งใสขนาดใหญ่ (1280px+)
    │   └── Logos/                      # ชุดไฟล์โลโก้ครบทุกขนาดมาตรฐาน
    │       ├── logo_master_original.png    # ความละเอียดสูงสุดดั้งเดิม คมชัด 100%
    │       ├── logo_ultra_4k_2048px.png    # กว้าง 2048px สำหรับสิ่งพิมพ์/แบนเนอร์ยักษ์
    │       ├── logo_large_1280px.png       # กว้าง 1280px สำหรับ Cover 16:9 / 1080p
    │       ├── logo_medium_800px.png       # กว้าง 800px สำหรับภาพโพสต์ Facebook
    │       ├── logo_standard_512px.png     # กว้าง 512px สำหรับ Store / การ์ด THub
    │       ├── logo_small_256px.png        # กว้าง 256px สำหรับ UI Dialog
    │       ├── logo_icon_128px.png         # กว้าง 128px สำหรับ Badge / Icon
    │       └── candidate_*.png             # ภาพต้นฉบับดิบจากแต่ละแหล่ง (Steam/Wiki/Local)
    ├── Generated_Logo/
    │   └── AI_Logo_Prompt.md       # สคริปต์คำสั่งสร้างโลโก้ 3D จาก AI
    └── Final_Exports/              # ภาพผลงานสำเร็จพร้อมเผยแพร่
```

---

## 3. การค้นหาและสกัดโลโก้ความละเอียดสูง 4 ลำดับชั้น (Multi-Tier High-Res Logo Discovery Protocol)

เพื่อให้ได้ภาพโลโก้ของเกมที่มีขนาดใหญ่ที่สุด คมชัดที่สุด และมีหลากหลายขนาดสำหรับงานออกแบบ THub และ AI Helper จะทำงานร่วมกันตาม 4 ลำดับชั้น:

### ลำดับที่ 1 (Steam Retina 2X Assets)
- ดึงภาพ `logo_2x.png` จาก Steam Akamai & Fastly CDN โดยตรง (ความละเอียดระดับ Retina กว้าง 1280px+ พื้นหลังโปร่งใส Alpha)
- หากไม่มี `logo_2x.png` จะใช้ `logo.png` เป็นตัวเลือกรอง

### ลำดับที่ 2 (Wikimedia Commons Vector SVG & High-Res Master)
- ค้นหาผ่าน Wikimedia Commons MediaWiki API ด้วยคำค้น `{game_name} logo`
- หากเป็นไฟล์ Vector (`.svg`) จะเรนเดอร์ขนาดความคมชัดสูงสุดระดับ Master (`2048px` หรือ `3840px` PNG)
- หากเป็นไฟล์ภาพถ่ายหรือ PNG ต้นฉบับ จะสกัดไฟล์ความละเอียดดั้งเดิมออกมา

### ลำดับที่ 3 (Local Game Installation & Workspace Deep Scan)
- สแกนหาไฟล์ภาพโลโก้หรือ Splash Screen ต้นฉบับจากโฟลเดอร์เกมหรือ `01_Original_Backup` (เช่น `*splash*.bmp`, `*splash*.png`, `*logo*.png`, `*title*.png`, `*title_atlas*.png`) ซึ่งเกมจำนวนมากมีภาพความละเอียด 1080p, 1440p, หรือ 4K บรรจุอยู่ในตัวเกม

### ลำดับที่ 4 (Resolution Comparator & Multi-Size Lanczos Resampler)
- นำภาพจากทุกแหล่งมาเปรียบเทียบพิกเซลรวม (width $\times$ height) และเลือกภาพที่ดีที่สุดเป็น **`Master Logo`**
- ประมวลผลย่อ/ขยายด้วยอัลกอริทึม **Lanczos Resampling** คุณภาพสูง เพื่อสร้างชุดไฟล์ภาพครบทุกขนาดมาตรฐาน (2048px, 1280px, 800px, 512px, 256px, 128px)

---

## 4. กฎความปลอดภัย (Safety Rule)
- **ห้ามเขียนทับ (No Overwrite):** หากในโฟลเดอร์ `07_Image_Resources` มีไฟล์ PSD หรือรูปภาพที่ผู้ใช้จัดทำไว้ก่อนหน้า ให้คงไฟล์เดิมไว้ 100% ห้ามลบหรือเขียนทับ

---

## 5. มาตรฐาน AI Logo Prompt Engineering

เมื่อสร้าง Prompt สำหรับเจนเนอเรตโลโก้เกมด้วย Midjourney, FLUX.1, SDXL, หรือ DALL-E 3:
- **คีย์เวิร์ดบังคับ:**  
  `3D extruded lettering, completely isolated on pure solid flat black background`
- **ประโยชน์ของคีย์เวิร์ดนี้:**  
  ทำให้พื้นหลังของภาพเป็นสีดำสนิท (#000000) 100% ปราศจากแสงสะท้อนที่พื้นหรือดวงดาว ทำให้สามารถนำเข้า Photoshop แล้วไดคัทได้ใน 1 คลิก

---

## 6. เทคนิค Photoshop 1-Click Compositing

1. **Screen Blending Mode (เร็วที่สุดใน 1 วินาที):**
   - วางภาพฉากหลัง (Official Art) ไว้เลเยอร์ล่าง
   - วางภาพโลโก้ AI (พื้นหลังดำ) ไว้เลเยอร์บน
   - เปลี่ยน Blending Mode ของเลเยอร์โลโก้เป็น **`Screen`**
   - พิกเซลสีดำจะถูกหักล้างออกหมดทันที เหลือเฉพาะแสงเรือง แสงสะท้อน และตัวอักษร 3 มิติ

2. **Select Subject Masking (สำหรับงานไดคัทเนี๊ยบ):**
   - ไปที่ `Select` > `Subject` หรือ `Color Range`
   - เลือกสีดำสนิท กด Invert และเพิ่ม Layer Mask

3. **Exporting:**
   - ส่งออกผลงานความละเอียดสูงบันทึกไว้ในโฟลเดอร์ `Final_Exports/`
