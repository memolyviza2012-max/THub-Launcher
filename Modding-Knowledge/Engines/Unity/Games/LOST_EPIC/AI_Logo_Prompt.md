# AI Logo Prompt Kit — LOST EPIC Thai Mod

ผู้จัดทำ: **หน๊ด หนวด translator** (NodNuatTranslator)  
เกม: **LOST EPIC**  
เอนจิน: **Unity**  
วัตถุประสงค์: สร้างชุดคำสั่ง AI Prompt คุณภาพสูงสำหรับเจนเนอเรตโลโก้ภาษาไทย/ชื่อม็อด และคู่มือการประกอบงานกราฟิก 1-Click ใน Photoshop

---

## กฎร่วมของทุก Prompt (Core Rules)

ให้คงวลีสำคัญระดับ Golden Keyword ต่อไปนี้ไว้ในทุก Prompt เสมอ:

> **`3D extruded lettering, completely isolated on pure solid flat black background`**

### ข้อกำหนดด้านการออกแบบ (Design Specifications):
- **สไตล์ศิลปะ (Art Direction)**: อิงตามธีม Dark Fantasy ผสม Anime Aesthetics ของ *Namie* (ผู้ออกแบบตัวละคร LOST EPIC) โดดเด่นด้วยโทนสีน้ำเงินคอสมิก/แซงค์ทัม (Sanctum Azure Blue), สีทองเปล่งประกายแห่งทวยเทพ (Divine Radiant Gold), และประกายดาบผลึกรูน (Crystalline Rune Blade Glow)
- **อัตราส่วนภาพ (Aspect Ratio)**: แนวนอน 16:9 หรือ 21:9 เหมาะสำหรับวางเป็นไตเติลหน้าปกเกมและแบนเนอร์
- **การจัดวางองค์ประกอบ (Composition)**: จัดวางกึ่งกลาง (Centered Horizontal Lockup) เว้นขอบปลอดภัย (Safe Margins) รอบทิศทางอย่างน้อย 15% เพื่อไม่ให้ปลายตัวอักษรหรือเอฟเฟกต์แสงถูกตัดขอบ
- **พื้นหลัง (Background)**: บังคับให้เป็นสีดำสนิทแบนเรียบแบบเพียวสีเดียว (`pure solid flat black #000000`) ห้ามมีหมอก, ลวดลาย, ควัน, หรือการเกลี่ยสี (Vignette/Gradient) เพื่อให้สามารถไดคัทใน Photoshop หรือใช้โหมด Screen ได้ใน 1 วินาที
- **ความละเอียด (Resolution)**: บันทึกและดึงไฟล์ความละเอียดสูงสุด (High-Resolution / Lossless PNG)

---

## Negative Prompt กลาง (Universal Negative Prompt)

```text
busy background, scenery, landscape, realistic human face, full anime body, character illustration,
complex scenery, floating particles, smoke, fire, messy background, gradient background,
transparent checkerboard, checkered background, watermark, signature, artist name, copyright notice,
extra text, random gibberish letters, misspelled Thai, distorted glyphs, broken fonts,
unreadable typography, cropped letters, cut-off edges, duplicated logo, UI mockup, frame,
border, photo frame, bevel border, low resolution, blurry, artifacts, compression noise, flat 2D unextruded text
```

> **คำแนะนำสำหรับฟอนต์ไทย**: โดยธรรมชาติของ AI Image Generator ปัจจุบัน (Midjourney, Flux, SDXL, DALL-E 3) อาจสะกดตัวอักษรภาษาไทยที่ซับซ้อน (สระ/วรรณยุกต์) เพี้ยนได้ แนะนำให้ใช้ภาพจาก AI เป็น "Base Graphic & Texture / 3D Bevel Element" แล้วใช้ Photoshop ซ้อนเลเยอร์ตัวอักษรภาษาไทยจริง (เช่น ฟอนต์ Prompt หรือฟอนต์แฟนตาซีมีสไตล์) ทับอีกชั้น เพื่อความประณีตระดับมืออาชีพสูงสุด

---

## 1. Prompt สำหรับ Midjourney v6.1

```text
A prestigious anime dark fantasy game localization logo for "LOST EPIC Thai Mod".
Featuring heroic celestial anime aesthetics, stylized sharp 3D extruded lettering,
carved sanctum crystal bevels, polished obsidian metal base with glowing holy gold trim,
and ethereal celestial azure blue rim lighting inspired by divine God Slayer blades.
Centered horizontal title lockup with a sleek subtitle reading "Thai Edition - NodNuatTranslator".
3D extruded lettering, completely isolated on pure solid flat black background.
Generous safe padding margins, crisp silhouette edges, masterpiece typography,
clean contrast, studio game logo design, no characters, no scenery, no background clutter.
--ar 16:9 --v 6.1 --style raw --s 180 --c 5
```

---

## 2. Prompt สำหรับ FLUX.1 (Dev / Schnell)

```text
A pristine horizontal localization title logo for the game LOST EPIC, created for a Thai translation mod.
The logo features monumental 3D extruded lettering crafted from dark celestial titanium and sanctum white gold,
embellished with subtle glowing azure-blue holy runes and sharp beveled edges evoking a god-slaying anime fantasy sword.
A sleek sub-heading beneath the main title indicates "Thai Mod by NodNuatTranslator".
The typography is sharp, legible, and balanced in a clean centered horizontal layout.
3D extruded lettering, completely isolated on pure solid flat black background.
Perfect clean vector-like silhouette, absolute pitch black backdrop with zero ambient lighting,
no smoke, no fire, no particles, no characters, no scenery, no watermark, generous negative space around borders.
```

---

## 3. Prompt สำหรับ SDXL (Stable Diffusion XL)

**Positive Prompt:**
```text
(masterpiece:1.3), (highest quality:1.2), ultra-detailed game logo,
LOST EPIC Thai Mod, anime fantasy action RPG title typography,
heroic 3D extruded lettering, celestial azure energy accents, radiant holy gold trim,
polished dark metal bevels, sanctum divine aesthetic, God Slayer motif,
centered horizontal lockup, crisp defined edges, professional localization branding,
3D extruded lettering, completely isolated on pure solid flat black background,
pure solid flat black keying background, high contrast, generous safe margin
```

**Negative Prompt:**
```text
(worst quality:2.0), (low quality:2.0), (blurry:1.5), noisy, character, person, anime girl,
scenery, landscape, forest, mountains, glowing background, smoke, flames, dust, sparks,
gradient, checkerboard, vignette, watermark, label, signature, username, cropped,
cut-off typography, duplicate logo, lowres, jpeg artifacts, flat 2d text
```

---

## 4. Prompt สำหรับ DALL·E 3

```text
Create a clean and striking 3D localization video game logo for "LOST EPIC: Thai Translation Mod".
The design features sharp, faceted 3D extruded typography in a horizontal layout, combining celestial deep blue crystals,
polished silver-chrome metal, and radiant gold divine accents fitting a fast-paced anime god-slaying fantasy RPG.
Include a small neat subtitle reading "NodNuatTranslator".
The entire logo must be 3D extruded lettering, completely isolated on pure solid flat black background.
Do not include any background scenes, characters, or decorative frames.
Ensure wide empty space around all sides of the logo for easy graphic cutout.
```

---

## ระดมสมอง: ไอเดียชื่อเกมภาษาไทย (Thai Title Concepts)

| ลำดับ | ชื่อภาษาไทย | สไตล์/แนวทาง | เหตุผลและจุดเด่น |
| :--- | :--- | :--- | :--- |
| **แบบที่ 1** | **ลอสท์ เอพิก: ศึกสังหารเทพ** | ทับศัพท์โมเดิร์น + คำขยายความมันส์ | คงชื่อแบรนด์สากล "LOST EPIC" ที่เกมเมอร์คุ้นเคย แล้วเสริมสร้อย "ศึกสังหารเทพ" ซึ่งตรงกับภารกิจหลักของตัวเอก (God Slayer) ผู้บุก Sanctum ไปโค่นล้ม 6 ทวยเทพ |
| **แบบที่ 2** | **มหากาพย์สูญสลาย: อัศวินล่าทวยเทพ** | แปลความหมายแฟนตาซีมหากาพย์ (Lore-accurate) | สื่อความหมายของคำว่า "LOST" (สูญสลาย) และ "EPIC" (มหากาพย์) ถ่ายทอดอารมณ์ดาร์กแฟนตาซีระดับตำนาน เหมาะกับโปสเตอร์และคัตซีนเนื้อเรื่อง |
| **แบบที่ 3** | **มหากาพย์ล่าเทพ** | สั้น กระชับ ติดหู (Punchy Action) | สั้นเพียง 4 พยางค์ จดจำง่าย ทรงพลัง เข้ากับเกมเพลย์ 2D Action ฟันดาบความเร็วสูง เหมาะสำหรับทำตราสัญลักษณ์บนหน้าปกขนาดเล็กและไอคอน |
| **แบบที่ 4** | **ลอสท์ เอพิก: มหากาพย์แดนเทวาสูญ** | แฟนตาซีลึกลับ กลิ่นอายอนิเมะ | เน้นบรรยากาศของดินแดนศักดิ์สิทธิ์ Sanctum ที่บิดเบี้ยวและสูญสลาย มอบความรู้สึกขลังและน่าค้นหา |
| **แบบที่ 5** | **LOST EPIC ภาษาไทย — โดย หน๊ด หนวด translator** | คอมมิวนิตี้ / บิลด์ทางการ | เหมาะสำหรับแบนเนอร์แจกม็อด, ชื่อไฟล์อัปเดต, ปกการ์ด THub และสื่อ Social Media |

> **ข้อแนะนำในการเลือก**:  
> • ใช้ **แบบที่ 1 (ลอสท์ เอพิก: ศึกสังหารเทพ)** สำหรับหน้าปกโปรโมตหลักและวิดีโอตัวอย่าง  
> • ใช้ **แบบที่ 3 (มหากาพย์ล่าเทพ)** หรือ **แบบที่ 5** บนไอคอนย่อยและการ์ดเกมในระบบ THub

---

## คู่มือประกอบงานใน Photoshop (1-Click Workflow Guide)

เมื่อได้ภาพโลโก้พื้นหลังดำจาก AI หรือไฟล์ภาพ Official Art แล้ว ให้ทำตามขั้นตอนการประกอบงานอย่างรวดเร็วดังนี้:

### วิธีที่ 1: เทคนิค Screen Blending Mode (เร็วที่สุด — 1 วินาที ไม่ต้องตัดต่อ)
1. เปิดไฟล์เทมเพลต PSD ที่ต้องการ เช่น `cover 16-9.psd` หรือ `Cover_Post facebook.psd`
2. ลากไฟล์ภาพโลโก้พื้นหลังดำจากโฟลเดอร์ `Generated_Logo/` เข้ามาวางในเลเยอร์เหนือฉากหลัง
3. ที่กล่อง **Layer Blending Mode** เปลี่ยนจาก **Normal** ➔ **Screen**
4. **ผลลัพธ์**: พื้นหลังสีดำจะโปร่งใสหายไป 100% ทันที เหลือเพียงตัวอักษร 3D และประกายแสงเรืองรองอย่างสมบูรณ์แบบ
5. *(ทางเลือกเสริม)*: หากมีฝุ่นดำบาง ๆ หลงเหลือ ให้กด `Ctrl + L` (Levels) แล้วดึงแถบเลื่อนสีดำด้านซ้ายเข้าหาตรงกลางเล็กน้อยเพื่อตัดค่าดำส่วนเกิน

### วิธีที่ 2: เทคนิค 1-Click Select Subject / Remove Background (ได้ไฟล์ไดคัทโปร่งใสแท้)
1. เปิดภาพโลโก้ใน Photoshop
2. ไปที่เมนูคำสั่ง **Select ➔ Subject** หรือกดปุ่ม **Remove Background** ในหน้าต่าง Properties
3. ด้วยการที่พื้นหลังเป็น Pure Flat Black AI จะตรวจจับขอบตัวอักษร 3D ได้คมกริบ 100%
4. กดสร้าง **Layer Mask** แล้วลากไปวางในเทมเพลต PSD ได้ทันที

### การวางองค์ประกอบภาพ (Layout Assembly):
1. **ฉากหลัง (Background Art)**: นำภาพจาก `Official_Art/` เช่น:
   - `banner_hero_1920x620.jpg` (สำหรับแบนเนอร์แนวนอนกว้าง)
   - `cover_portrait_600x900.jpg` (สำหรับโปสเตอร์หน้าปกแนวตั้ง)
   - `cover_landscape_616x353.jpg` (สำหรับภาพปก 16:9)
2. **โลโก้ (Logo Placement)**: ปรับขนาดโลโก้ภาษาไทยให้อยู่ในระยะปลอดภัย ไม่ทับใบหน้าตัวละครหลัก และเว้นช่องไฟให้สบายตา
3. **เครดิตผู้พัฒนา (Credits & Branding)**: ปรับแต่งข้อความเครดิต *"แปลไทยโดย หน๊ด หนวด translator"* ตามเลเยอร์ข้อความในเทมเพลต
4. **ส่งออกผลงาน (Export)**:
   - สั่ง `File ➔ Export ➔ Quick Export as PNG` หรือ `Save As JPEG` (Quality: 10-12)
   - บันทึกไฟล์ที่เสร็จสมบูรณ์ลงในโฟลเดอร์: **`E:\Mod_Workspace\LOST_EPIC\07_Image_Resources\Final_Exports\`**
