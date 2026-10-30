# คัมภีร์: การดัดแปลงและฝังฟอนต์ภายนอก (Harvest Moon: Light of Hope)

## 1. บทนำและปัญหาที่พบ
เกม Harvest Moon: Light of Hope พัฒนาด้วยเอนจิน Unity การแสดงผลข้อความในเกมใช้ฟอนต์ที่ถูกฝัง (Hardcoded) ไว้ในไฟล์ `resources.assets` ได้แก่:
- `FOT-GrecoStd-B`
- `FOT-PopHappinessStd-EB`
- `FOT-SeuratPro-B`

**ปัญหาคือ:** 
1. เกมไม่มีระบบรองรับการเปลี่ยนฟอนต์จากภายนอก
2. เมื่อเราพยายามเขียนสคริปต์ (BepInEx Plugin) โหลดฟอนต์แบบ Dynamic (เช่นดึงจากโฟลเดอร์) ตัวเกมและเอนจิน Freetype ของ Unity ปฏิเสธหรือไม่ยอมเรนเดอร์ตัวอักษร 
3. มีสคริปต์ภายในเกมชื่อ `FontAttach` ที่คอยบังคับเซ็ตฟอนต์ของ UI กลับไปเป็นฟอนต์ดั้งเดิมตลอดเวลา ทำให้ UI บางส่วนไม่ยอมเปลี่ยนฟอนต์

## 2. วิธีแก้ปัญหา (The Solution)
เราใช้วิธีโจมตี 3 ประสาน (Triple-Threat Method) เพื่อให้ฟอนต์ไทย PUA ภายนอกสามารถทำงานในเกมได้อย่างสมบูรณ์:

### ขั้นที่ 1: การฝังฟอนต์ตรงเข้า Bundle (Direct Asset Injection & Padding)
เนื่องจาก Unity ตรวจสอบขนาดของไฟล์ Asset การที่เราจะยัดฟอนต์ `.ttf` ใหม่เข้าไปแทนที่ของเดิม เราไม่สามารถทำให้ไฟล์มีขนาดใหญ่หรือเล็กกว่าเดิมได้ (มิฉะนั้นโครงสร้าง Byte offset จะพังและเกมเด้ง)

**เทคนิคที่ใช้:** 
1. อ่านไฟล์ `.ttf` ฟอนต์ภาษาไทย (เช่น `GoogleSans-Regular_Adjusted.ttf`)
2. เทียบขนาดไฟล์กับฟอนต์ดั้งเดิมใน `resources.assets`
3. ทำการ **Padding (ยัดไส้)** โดยเติม `\x00` (Null bytes) ต่อท้ายไฟล์ฟอนต์ไทย จนกว่าขนาดจะ **เท่ากับ** ไฟล์ฟอนต์ต้นฉบับเป๊ะๆ
4. นำก้อน Byte ที่เท่ากันนี้ เขียนทับลงไปใน `resources.assets` โดยใช้ไลบรารีอย่าง `UnityPy`

*(หมายเหตุ: ไฟล์ฟอนต์ไทยต้องมีขนาด "น้อยกว่าหรือเท่ากับ" ฟอนต์ดั้งเดิมเสมอ)*

### ขั้นที่ 2: ปราบสคริปต์กวนใจ (Hook Neutralization)
แม้เราจะฝังฟอนต์ในทรัพยากรเกมสำเร็จ แต่เกมมีคลาส `FontAttach` ใน `Assembly-CSharp.dll` ที่คอยขัดขวาง

**เทคนิคที่ใช้:**
เราสร้าง BepInEx Plugin (`WorkingFontFixPlugin.dll`) เพื่อเข้าไป Hook คลาส `FontAttach` โดยใช้ **Harmony Patching** 
```csharp
MethodInfo updateMethod = fontAttachType.GetMethod("Update", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
harmony.Patch(updateMethod, new HarmonyMethod(prefixMethod));
...
public static bool FontAttachPrefix(Component __instance) {
    return false; // สั่งหยุดการทำงานของฟังก์ชันทันที (Skip original method)
}
```
การคืนค่า `false` ใน Prefix Patch ทำให้ฟังก์ชัน `Start()`, `Update()`, และ `FontSet()` ของ `FontAttach` เป็นอัมพาต เกมจึงยอมจำนนและปล่อยให้ UI แสดงผลฟอนต์ที่เราฝังไว้ใน `resources.assets` ได้อย่างอิสระ

### ขั้นที่ 3: การใช้ข้อความแบบ PUA (Private Use Area)
Unity มักจะมีปัญหาการเรนเดอร์สระบน-ล่างและวรรณยุกต์ไทย (สระลอย/จม/เหลื่อมทับตัวอักษรมีหาง)

**เทคนิคที่ใช้:**
1. ใช้ฟอนต์ที่ผ่านการปรับจูนตารางอักขระ PUA (เช่น โยกสระหลบหางป.ปลา ไปไว้ในรหัส F700+)
2. นำไฟล์แปลภาษา (`THub_Input_translated.csv`) มารันผ่านสคริปต์แปลง PUA (`pua_converter.py`) เพื่อเปลี่ยนข้อความไทยปกติ ให้สระและวรรณยุกต์พิเศษถูกแปลงเป็นรหัส PUA 
3. นำข้อความที่รหัสถูกต้องแล้ว แพ็กกลับเข้าไปทับไฟล์ TextAsset (`locale/us`) ในเกม

## สรุปขั้นตอน (Summary Workflow)
1. **เตรียมฟอนต์:** ใช้ฟอนต์ที่จูน PUA แล้ว และขนาดต้องไม่เกินฟอนต์ดั้งเดิม
2. **ฉีดฟอนต์ (Inject):** ใช้สคริปต์ UnityPy ยัด `\x00` ต่อท้ายให้ขนาดเป๊ะ แล้วยัดทับลงไปใน `resources.assets`
3. **ฉีดข้อความ (Text Pack):** นำคำแปลไปแปลงเป็น PUA แล้วแพ็กลงไฟล์แปลใน `StreamingAssets`
4. **วางยา (Plugin):** โยน `WorkingFontFixPlugin.dll` ลงในโฟลเดอร์ BepInEx เพื่อปิดระบบ `FontAttach` ของเกม

ด้วยวิธีการนี้ เราจึงสามารถใช้ฟอนต์ภายนอกได้อย่างสมบูรณ์ สวยงาม และไม่ต้องกลัวเกมเด้งครับ!
