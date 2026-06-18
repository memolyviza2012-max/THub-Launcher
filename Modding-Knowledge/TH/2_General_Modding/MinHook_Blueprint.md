# พิมพ์เขียว MinHook สำหรับ Dawn Engine (และเอนจินอื่นๆ)

เอกสารนี้รวบรวมโครงสร้างและแนวทางการเขียน Hook ฟังก์ชันของเกมอย่างปลอดภัยโดยใช้ไลบรารี MinHook

## 1. การตั้งค่า MinHook (Setup MinHook)
ทำการเริ่มต้นระบบ (Initialize) ของ MinHook ในระหว่างกระบวนการ `DLL_PROCESS_ATTACH` หลังจากที่เราดึงที่อยู่เริ่มต้น (Base address) ของเกมมาได้แล้วและมั่นใจว่าสภาพแวดล้อมพร้อมทำงาน

```cpp
MH_Initialize();
```

## 2. การค้นหาฟังก์ชัน (Locate Functions)
ใช้ระบบค้นหารูปแบบไบต์ (Pattern Scanner) ในการค้นหาที่อยู่ของฟังก์ชัน แทนที่จะใช้ที่อยู่แบบตายตัว (Hardcoded addresses) เพื่อป้องกันการพังเมื่อเกมอัปเดต
*ตัวอย่าง: กิจวัตรการจองหน่วยความจำสตริง (String Allocation), การตรวจสอบสตริง, หรือฟังก์ชันวาดผล UI (UI Render routines)*

## 3. การสร้างฟังก์ชันสวมรอย (Create Detour Functions)
ต้องรักษาโครงสร้างพารามิเตอร์ (Signature) ให้เหมือนกับฟังก์ชันเป้าหมายเป๊ะๆ เสมอ และอย่าลืมใช้ `__thiscall` หากมันเป็น member function ของคลาส

```cpp
typedef const char* (__thiscall* StringAlloc_t)(void* mem_mgr, const char* original_str);
StringAlloc_t g_orig_StringAlloc = nullptr;

const char* detour_string_alloc(void* mem_mgr, const char* original_str) {
    if (!original_str) {
        if (g_orig_StringAlloc) return g_orig_StringAlloc(mem_mgr, original_str);
        return original_str;
    }

    // แทรกระบบแปลภาษาตรงนี้...
    const char* translated = lookup_translation(original_str);
    
    if (g_orig_StringAlloc) return g_orig_StringAlloc(mem_mgr, translated);
    return translated;
}
```

## 4. การติดตั้ง Hook (Install Hooks)
ห่อหุ้มคำสั่งสร้าง Hook ไว้ด้วยการเช็ก Error และบันทึกสถานะการทำงานเสมอ

```cpp
MH_STATUS status = MH_CreateHook(
    (LPVOID)target_func_addr,
    &detour_string_alloc,
    reinterpret_cast<LPVOID*>(&g_orig_StringAlloc)
);

if (status == MH_OK) {
    MH_EnableHook((LPVOID)target_func_addr);
} else {
    // บันทึก Error (ตัวอย่างเช่น MH_STATUS_MESSAGE(status))
}
```

## 5. การล้างข้อมูล (Cleanup)
ต้องทำการยกเลิกและปิดระบบ MinHook ทุกครั้งเมื่อ DLL ถูกถอดออก (`DLL_PROCESS_DETACH`) เพื่อไม่ให้เกมแครช

```cpp
MH_Uninitialize();
```


---
**จัดทำโดย:** [หน๊ด หนวด translator](https://www.facebook.com/NodNuatTranslator/)
