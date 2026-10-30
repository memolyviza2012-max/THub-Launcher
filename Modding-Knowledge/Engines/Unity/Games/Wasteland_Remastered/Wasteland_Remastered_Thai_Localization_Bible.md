# Wasteland Remastered - Thai Localization Bible

## 1. Overview
Wasteland Remastered เป็นเกมที่รันบน **Unity Engine (IL2CPP)** และใช้ระบบแสดงผลข้อความด้วย **TextMeshPro (TMP) เวอร์ชันเก่า (v1.3.x สำหรับ Unity 2018)**. 
การแปลภาษาในเกมนี้แบ่งออกเป็น 2 ส่วนหลัก: 
1. การแปลข้อความในไฟล์ XML (ง่ายมาก)
2. การทำ Font Injection (ยากระดับปานกลาง-สูง) เนื่องจากบั๊กของเกมที่ทำให้ฟอนต์ล่องหน (Invisible Text) อันเกิดจาก Shader Mismatch

---

## 2. Text Translation (การแปลข้อความ)
ข้อความของเกมส่วนใหญ่อยู่ในโฟลเดอร์:
`Wasteland Remastered/WL_Data/StreamingAssets/Localization/`

ภายในโฟลเดอร์จะมีไฟล์ XML เช่น `wr_localization.xml` ซึ่งเก็บข้อความทุกอย่างในเกมไว้
- **Format:** เป็น XML มาตรฐาน สามารถเปิดแก้ด้วย Notepad++ หรือเครื่องมือแปลภาษาใด ๆ ได้เลย
- **Encoding:** ต้องบันทึกเป็น UTF-8 เสมอ
- ข้อดีคือไม่ต้องทำ Asset Unpacking/Repacking สามารถแก้ไขไฟล์และเห็นผลในเกมได้ทันที!

---

## 3. Font Injection & Shader Fix (หัวใจสำคัญ)

การแสดงผลภาษาไทยในเกมนี้ **ไม่สามารถยัดไฟล์ TTF ดิบๆ เข้าไปได้** เนื่องจากเกมใช้ TextMeshPro. และเราไม่สามารถใช้เทคนิค Runtime OS Font Injection (เสกฟอนต์จาก Windows สดๆ) แบบเกมยุคใหม่ได้ เพราะ Unity 2018 ยังไม่มีคำสั่ง `TMP_FontAsset.CreateFontAsset`.

ดังนั้น **วิธีที่สมบูรณ์ที่สุดคือ การใช้ BepInEx IL2CPP โหลด AssetBundle ที่มี TMP_FontAsset ภาษาไทยเข้าไปสวมทับแบบ Runtime.**

### 3.1 การเตรียม AssetBundle
1. ใช้ Unity Editor (เวอร์ชันใกล้เคียง 2018) สร้าง `TMP_FontAsset` ที่ใส่ภาษาไทย (U+0E00-U+0E7F)
2. แพ็กเป็น AssetBundle (เช่นไฟล์ `arialuni_sdf_u2018`)

### 3.2 ปัญหา Invisible Text (Shader Mismatch)
เมื่อเราใช้ `AssetBundle.LoadAsset` ดึงฟอนต์เข้ามาใน IL2CPP และยัดใส่ `TMP_Settings.fallbackFontAssets` ตัวหนังสือจะโปร่งใส (มองไม่เห็น) ทันที
**สาเหตุ:** Material ที่ติดมากับ AssetBundle ใช้ Shader คนละเวอร์ชันกับที่เอนจินของเกมใน Memory รู้จัก

### 3.3 การแก้ไข (The BepInEx Plugin + Harmony Hook)
เราต้องเขียนปลั๊กอิน (C#) เพื่อแก้ปัญหานี้โดยเฉพาะ โดยใช้ `Harmony` เข้าไปจัดการ:
1. โหลด `TMP_FontAsset` จาก AssetBundle
2. สั่งหา Shader ดั้งเดิมของเกม: `Shader.Find("TextMeshPro/Distance Field")`
3. สร้าง Material ใหม่จาก Shader นี้ แล้วนำ Texture ของฟอนต์ไทยมาใส่
4. ใช้ Harmony ดักจับฟังก์ชัน `OnEnable` ของ `TextMeshProUGUI` และ `TextMeshPro`
5. ทันทีที่ UI แสดงผล โค้ดจะเข้าไปเปลี่ยน `font` และ `fontSharedMaterial` เป็นภาษาไทยทันที

**Source Code สำหรับ FontInjectorPlugin.cs:**
```csharp
using System.IO;
using System.Reflection;
using BepInEx;
using BepInEx.Unity.IL2CPP;
using UnityEngine;
using TMPro;
using HarmonyLib;
using Il2CppInterop.Runtime.Injection;
using Il2CppInterop.Runtime;
using Il2CppInterop.Runtime.InteropTypes.Arrays;

namespace DynamicFontInjector
{
    [BepInPlugin("com.modder.dynamicfontinjector", "Dynamic TMP Font Injector", "1.0.0")]
    public class FontInjectorPlugin : BasePlugin
    {
        public static TMP_FontAsset ThaiFontAsset = null;
        public static Material ThaiMaterial = null;

        public override void Load()
        {
            string pluginDir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            string abPath = Path.Combine(pluginDir, "arialuni_sdf_u2018");
            
            AssetBundle bundle = AssetBundle.LoadFromFile(abPath);
            var allAssets = bundle.LoadAllAssets(Il2CppType.Of<TMP_FontAsset>());
            ThaiFontAsset = allAssets[0].TryCast<TMP_FontAsset>();
            
            UnityEngine.Object.DontDestroyOnLoad(ThaiFontAsset);
            
            // Fix Shader Mismatch for IL2CPP
            Shader nativeShader = Shader.Find("TextMeshPro/Distance Field");
            if (nativeShader != null)
            {
                ThaiMaterial = new Material(nativeShader);
                ThaiMaterial.mainTexture = ThaiFontAsset.material.mainTexture;
                ThaiFontAsset.material = ThaiMaterial;
                UnityEngine.Object.DontDestroyOnLoad(ThaiMaterial);
            }

            // Apply Harmony Patches
            var harmony = new Harmony("com.modder.dynamicfontinjector");
            var methodUGUI = AccessTools.Method(typeof(TextMeshProUGUI), "OnEnable");
            harmony.Patch(methodUGUI, postfix: new HarmonyMethod(typeof(FontInjectorPlugin).GetMethod(nameof(OnEnablePostfix), BindingFlags.Static | BindingFlags.NonPublic)));
        }

        // Postfix for UI Text
        static void OnEnablePostfix(TextMeshProUGUI __instance)
        {
            if (ThaiFontAsset != null && __instance != null)
            {
                __instance.font = ThaiFontAsset;
                if (ThaiMaterial != null) __instance.fontSharedMaterial = ThaiMaterial;
            }
        }
    }
}
```

---

## 4. สรุปขั้นตอนการติดตั้ง Mod
1. ติดตั้ง **BepInEx 6 (IL2CPP)** ลงในโฟลเดอร์เกม
2. รันเกม 1 ครั้งเพื่อให้ BepInEx สร้างไฟล์ Interop Assemblies (Unhollowing)
3. นำ `FontInjectorPlugin.dll` และไฟล์ฟอนต์ `arialuni_sdf_u2018` วางใน `BepInEx/plugins/`
4. วางไฟล์ `wr_localization.xml` ที่แปลแล้วทับของเดิมใน `StreamingAssets/Localization/`
5. รันเกมและสนุกกับภาษาไทย!
