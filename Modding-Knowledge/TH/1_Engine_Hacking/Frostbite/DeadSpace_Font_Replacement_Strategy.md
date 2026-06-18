# Knowledge Base: In-Memory Font Replacement (Dead Space Case Study)

## ภาพรวม (Overview)
เทคนิคนี้เป็นอีกหนึ่งรูปแบบของการทำ Mod ภาษาไทย โดยโฟกัสไปที่การ **"แทนที่ข้อมูลฟอนต์ในหน่วยความจำ (In-Memory Font Replacement)"** แบบไดนามิก เพื่อแก้ปัญหาเกมที่ไม่รองรับฟอนต์ภาษาไทย และมีโครงสร้างไฟล์ฟอนต์ที่ยากต่อการดัดแปลงตรงๆ

ต่างจากการทำ Translation Hooking (เช่นในโปรเจกต์ GOTG) ที่ดักจับและเปลี่ยนข้อความก่อนแสดงผล วิธีนี้พุ่งเป้าไปที่ **ตัวสินทรัพย์ฟอนต์ (Font Asset)** ที่โหลดอยู่ใน RAM โดยตรง

## กลไกการทำงาน (The Mechanism)
เทคนิคนี้อาศัยสถาปัตยกรรม Proxy DLL และ Inline Hooking (MinHook) 

1. **Proxy DLL Loading:** 
   สร้าง DLL ปลอม (เช่น `dxgi.dll`) ให้เกมโหลดก่อนตัวจริง เมื่อเกมเรียกใช้ ระบบจะทำ Forwarding ฟังก์ชันทั้งหมดกลับไปที่ System DLL ตัวจริง
2. **Asset Preparation:** 
   อ่านไฟล์ฟอนต์ภาษาไทย (เช่น ฟอนต์ Jura `System.App.Control.dll`) จากดิสก์เข้าไปพักไว้ในตัวแปรบนหน่วยความจำ 
3. **Module Scanning:** 
   หา Base Address และขนาดของ Game Executable (`GetModuleHandleA` + `K32GetModuleInformation`)
4. **Safe Environment Setup:** 
   แช่แข็งการทำงานของ Thread อื่นในเกมทั้งหมด (`SuspendThread`) เพื่อป้องกันเกมแครชระหว่างที่เรากำลังแก้ไขหน่วยความจำ
5. **Memory Patching:** 
   เปลี่ยนสิทธิ์การเข้าถึงหน่วยความจำ (`VirtualProtect` เป็น RWX) ตรงตำแหน่งเป้าหมาย จากนั้นก๊อปปี้ (memcpy) ข้อมูลฟอนต์ภาษาไทย ไปวางทับฟอนต์เดิมของเกม
6. **Cleanup & Resume:** 
   เคลียร์แคชคำสั่งของ CPU (`FlushInstructionCache`) และปลุก Thread ทั้งหมดให้ทำงานต่อ (`ResumeThread`)

## การเปรียบเทียบ: Dead Space (Font Hook) vs GOTG (Translation Hook)

ทั้งสองเทคนิคมีความเหมือนและความแตกต่างที่สามารถนำมาบูรณาการร่วมกันได้:

### สิ่งที่ควรรวมกัน (Shared Core Architecture)
ฐานความรู้ทั้งสองสามารถ **ใช้โครงสร้าง (Boilerplate) ตัวเดียวกันได้**:
* **Proxy DLL Wrapper**: โค้ดสำหรับทำ `dxgi.dll` หรือ `dinput8.dll` ปลอม และการโหลดฟังก์ชันตัวจริง
* **MinHook Implementation**: โค้ดสำหรับการทำ Inline Hook และเทคนิคการ Suspend/Resume Thread อย่างปลอดภัย
* **Memory Management**: การใช้ `VirtualProtect` และ `FlushInstructionCache`

### สิ่งที่ควรแยก (Different Execution Targets)
* **Dead Space (Font Replacement)**
  * **เป้าหมาย:** ข้อมูลไบนารี (Binary Asset)
  * **วิธีการ:** ระบุ Memory Offset ของฟอนต์เดิม แล้วก๊อปปี้ฟอนต์ตัวใหม่ไปทับตรงๆ (มักจะต้องแก้ขนาด/โครงสร้าง Header ให้ตรงกัน หรืออาศัยความยืดหยุ่นของเกม)
  * **ความท้าทาย:** ตำแหน่ง Offset มักจะเลื่อนทุกครั้งที่มีการอัปเดตเกม (Hardcoded offsets)

* **GOTG (Translation Hook)**
  * **เป้าหมาย:** โค้ดฟังก์ชันเรนเดอร์ หรือฟังก์ชันโหลดข้อความ
  * **วิธีการ:** ค้นหา Pattern (AOB Scan) ของฟังก์ชัน, ดัก (Detour) เพื่อแทรกแซงพารามิเตอร์ข้อความ, จับคู่ภาษาเดิมกับภาษาไทยใน Dictionary, แล้วโยนกลับให้เกม
  * **ความท้าทาย:** ต้องค้นหาโครงสร้าง String object ให้เจอ และบางครั้งต้องจัดการกับ memory allocation ของข้อความที่ยาวขึ้น

## ข้อควรระวังและการต่อยอด
1. **การหา Offset:** เทคนิคแบบ Dead Space ใช้ตาราง Offset แบบตายตัว (Hardcoded) ซึ่งจะแตกทันทีเมื่อเกมอัปเดต ควรต่อยอดด้วยการทำ **AOB Pattern Scanning** เพื่อหาตำแหน่งฟอนต์โดยอัตโนมัติ
2. **การทำ Text Shaping:** เทคนิคนี้ **ไม่ได้** ทำ Text Shaping (การจัดรูปสระ/วรรณยุกต์ซ้อน) ถ้าใช้กับเกมที่เอนจิ้นไม่มีตัวจัดการตรงนี้ (เช่นไม่มี HarfBuzz) จะเกิดปัญหาสระลอย จำเป็นต้องรวมพลังกับเทคนิค Hook ไปที่ฟังก์ชันวาดตัวอักษรเพื่อจัดตำแหน่งแกน X/Y ของแต่ละ Glyph เอง


---
**จัดทำโดย:** [หน๊ด หนวด translator](https://www.facebook.com/NodNuatTranslator/)
