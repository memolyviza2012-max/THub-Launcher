# -*- coding: utf-8 -*-
"""
Master Game Engines Database (สารานุกรมเอนจิ้นเกมทั่วโลกสำหรับระบบ Modder Hub).
Contains comprehensive metadata for 132 game engines across the entire world:
  - Canonical names, developer, origin, category, color badges
  - Typical games, text & localization formats, font subsystems (PUA/SDF/Bitmap)
  - Recommended modding tools, complexity rating, detection signatures
"""

import re

ENGINE_DATABASE = {
    "Unreal Engine 5": {
        "canonical_name": "Unreal Engine 5",
        "aliases": [
            "unreal engine 5",
            "unreal_engine_5",
            "unrealengine5",
            "ue5",
            "unreal 5"
],
        "developer": "Epic Games",
        "origin_country": "USA",
        "category": "Commercial AAA 3D",
        "color": "#00bcff",
        "typical_games": [
            "Black Myth: Wukong",
            "S.T.A.L.K.E.R. 2: Heart of Chornobyl",
            "Silent Hill 2 Remake",
            "Tekken 8",
            "Senua's Saga: Hellblade II",
            "Lords of the Fallen (2023)",
            "Remnant II",
            "RoboCop: Rogue City",
            "The Matrix Awakens",
            "The First Descendant",
            "Fortnite (UE5 era)"
],
        "text_formats": [
            ".locres",
            ".pak",
            ".ucas",
            ".utoc",
            ".uasset"
],
        "font_tech": "Slate Font / Distance Field SDF / Offline TTF/OTF. รองรับ Dynamic Font และ PUA สมบูรณ์แบบ",
        "recommended_tools": [
            "repak",
            "FModel",
            "UnrealLocres",
            "UAssetGUI",
            "TStudio",
            "TRun",
            "ZenTools"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นยุคเน็กซ์เจนเรือธงระดับโลกจาก Epic Games โดดเด่นด้วยระบบ Nanite และ Lumen ข้อความภาษาในเกมจัดเก็บในระบบ Zen Store (.utoc / .ucas) และ .pak โดยไฟล์แปลหลักคือ .locres สามารถแกะและแพ็กกลับได้ด้วย repak และแก้ไขข้อความผ่าน TStudio อย่างรวดเร็ว",
        "description_en": "Next-gen flagship engine by Epic Games featuring Nanite and Lumen. Localization uses Zen Store (.utoc/.ucas) and .pak with .locres binary string tables.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "engine",
                        "paks",
                        "content"
            ],
            "extensions": [
                        ".ucas",
                        ".utoc",
                        ".locres"
            ],
            "exe_patterns": [
                        "-win64-shipping.exe"
            ]
},
    },
    "Unreal Engine 4": {
        "canonical_name": "Unreal Engine 4",
        "aliases": [
            "unreal engine 4",
            "unreal_engine_4",
            "unrealengine4",
            "ue4",
            "unreal 4"
],
        "developer": "Epic Games",
        "origin_country": "USA",
        "category": "Commercial AAA 3D",
        "color": "#38bdf8",
        "typical_games": [
            "Final Fantasy VII Remake",
            "Star Wars Jedi: Fallen Order",
            "Star Wars Jedi: Survivor",
            "Hogwarts Legacy",
            "Hi-Fi Rush",
            "Tales of Arise",
            "Shin Megami Tensei V: Vengeance",
            "Dragon Quest XI S",
            "Octopath Traveler 1 & 2",
            "Stray",
            "Psychonauts 2",
            "Lies of P",
            "Hellblade: Senua's Sacrifice",
            "Life is Strange 2",
            "Ghostrunner"
],
        "text_formats": [
            ".locres",
            ".pak",
            ".uasset",
            ".uexp"
],
        "font_tech": "Slate Font / Font Face (.uasset) / Distance Field Font / TTF/OTF PUA Injection",
        "recommended_tools": [
            "repak",
            "FModel",
            "UnrealLocres",
            "UAssetGUI",
            "UE4SS",
            "TStudio",
            "TRun"
],
        "complexity": "Easy to Medium",
        "description_th": "หนึ่งในเอนจิ้นที่มีเกมสร้างมากที่สุดในโลก จัดเก็บไฟล์เกมใน .pak ข้อความแปลหลักอยู่ในไฟล์ .locres (UTF-16) และ .uasset มีเครื่องมือซัพพอร์ตล้นหลาม สามารถใช้ repak ดึง/แพ็กกลับ และสร้างม็อดใส่โฟลเดอร์ ~mods ได้ทันที",
        "description_en": "Widely adopted commercial engine by Epic Games. Localization relies on .locres and .uasset in standard .pak containers.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "paks",
                        "binaries/win64"
            ],
            "extensions": [
                        ".pak",
                        ".locres"
            ],
            "exe_patterns": [
                        "-win64-shipping.exe"
            ]
},
    },
    "Unreal Engine 3": {
        "canonical_name": "Unreal Engine 3",
        "aliases": [
            "unreal engine 3",
            "unreal_engine_3",
            "unrealengine3",
            "ue3",
            "unreal 3",
            "udk"
],
        "developer": "Epic Games",
        "origin_country": "USA",
        "category": "Commercial AAA 3D (Classic)",
        "color": "#0284c7",
        "typical_games": [
            "Batman: Arkham Asylum / City / Origins",
            "BioShock Infinite",
            "Mass Effect 1, 2, 3",
            "Borderlands 1, 2, The Pre-Sequel",
            "Dishonored 1",
            "XCOM: Enemy Unknown",
            "Gears of War 1, 2, 3",
            "DmC: Devil May Cry",
            "Life is Strange 1",
            "Outlast 1",
            "Alice: Madness Returns",
            "Remember Me",
            "The Vanishing of Ethan Carter"
],
        "text_formats": [
            ".upk",
            ".txt",
            ".int",
            ".fra",
            ".deu",
            ".locres"
],
        "font_tech": "Bitmap Font Texture (Font'Package.FontName') / MultiFont / Scaleform GFx",
        "recommended_tools": [
            "UDK MCP",
            "TStudio",
            "TRun",
            "UE Viewer (UModel)",
            "QuickBMS",
            "Scaleform Tools"
],
        "complexity": "High",
        "description_th": "เอนจิ้นยอดนิยมยุค PS3/Xbox 360 บรรจุเนื้อหาในแพ็กเกจ .upk ข้อความส่วนใหญ่อยู่ในโฟลเดอร์ Localization (.int, .txt) หรือฝังใน UPK ฟอนต์เป็น Bitmap Texture ต้องแทนที่ Glyph หรือฉีดฟอนต์ผ่าน Scaleform GFx",
        "description_en": "Iconic generation engine using .upk packages and localized text files (.int/.txt). Fonts are typically texture-based bitmap atlases or Scaleform GFx.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "cookedpcconsole",
                        "cookedpc",
                        "udkgame"
            ],
            "extensions": [
                        ".upk",
                        ".int"
            ],
            "exe_patterns": []
},
    },
    "Unreal Engine 2": {
        "canonical_name": "Unreal Engine 2",
        "aliases": [
            "unreal engine 2",
            "unreal_engine_2",
            "unrealengine2",
            "ue2",
            "unreal 2",
            "ue2.5"
],
        "developer": "Epic Games",
        "origin_country": "USA",
        "category": "Classic 3D Commercial",
        "color": "#0369a1",
        "typical_games": [
            "Tom Clancy's Splinter Cell 1, Pandora Tomorrow, Chaos Theory",
            "BioShock 1 & 2 (Custom UE2.5)",
            "Unreal Tournament 2003 / 2004",
            "Postal 2",
            "Lineage II",
            "Star Wars Republic Commando",
            "Deus Ex: Invisible War",
            "Thief: Deadly Shadows"
],
        "text_formats": [
            ".u",
            ".int",
            ".ini",
            ".txt"
],
        "font_tech": "Texture-based TrueType Bitmap rasterizer / Native Font packages",
        "recommended_tools": [
            "TStudio",
            "TRun",
            "UnrealEd",
            "Wotgreal",
            "DragonUnPACKer"
],
        "complexity": "High",
        "description_th": "เอนจิ้นคลาสสิกยุค 2002-2006 ข้อความและภาษาถูกเก็บเป็นไฟล์ข้อความธรรมดาตามรหัสภาษา เช่น .int, .ini หรือฝังในสคริปต์ .u ฟอนต์แปลงเป็น Texture แผ่นบิตแมปในไฟล์แพ็กเกจ",
        "description_en": "Classic engine era using .int/.ini text files and .u packages with bitmap texture fonts.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "system",
                        "maps",
                        "textures"
            ],
            "extensions": [
                        ".u",
                        ".int",
                        ".utx"
            ],
            "exe_patterns": [
                        "ut2004.exe",
                        "postal2.exe"
            ]
},
    },
    "Unreal Engine 1": {
        "canonical_name": "Unreal Engine 1",
        "aliases": [
            "unreal engine 1",
            "unreal_engine_1",
            "ue1",
            "unreal 1"
],
        "developer": "Epic Games",
        "origin_country": "USA",
        "category": "Retro 3D Commercial",
        "color": "#0c4a6e",
        "typical_games": [
            "Unreal (1998)",
            "Unreal Tournament (1999)",
            "Deus Ex (2000)",
            "Rune",
            "Clive Barker's Undying",
            "Wheel of Time"
],
        "text_formats": [
            ".int",
            ".ini",
            ".u"
],
        "font_tech": "Monochrome / 8-bit Font Texture Sheets",
        "recommended_tools": [
            "UnrealEd",
            "TStudio",
            "Hex Editor"
],
        "complexity": "Medium",
        "description_th": "ต้นกำเนิดตระกูล Unreal Engine ยุคปี 1998 การแปลเกมทำได้โดยการแปลไฟล์ข้อความภาษา .int และแก้ไขฟอนต์บิตแมปในเท็กซ์เจอร์ .utx",
        "description_en": "The original Unreal Engine (1998) with .int text files and .utx texture sheets.",
        "detection": {
            "root_files": [
                        "unreal.exe"
            ],
            "root_dlls": [
                        "engine.dll",
                        "core.dll"
            ],
            "sub_dirs": [
                        "system"
            ],
            "extensions": [
                        ".u",
                        ".int",
                        ".uax"
            ],
            "exe_patterns": [
                        "unreal.exe",
                        "deusex.exe"
            ]
},
    },
    "Unreal Engine": {
        "canonical_name": "Unreal Engine",
        "aliases": [
            "unreal engine",
            "unreal",
            "unrealengine",
            "ue"
],
        "developer": "Epic Games",
        "origin_country": "USA",
        "category": "Commercial AAA 3D",
        "color": "#38bdf8",
        "typical_games": [
            "General Unreal Engine Titles"
],
        "text_formats": [
            ".locres",
            ".pak",
            ".ucas",
            ".utoc"
],
        "font_tech": "Slate / SDF / TrueType",
        "recommended_tools": [
            "repak",
            "FModel",
            "UnrealLocres",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "หมวดหมู่ทั่วไปสำหรับเกมตระกูล Unreal Engine ทุกรุ่น",
        "description_en": "General category for Unreal Engine family titles.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "engine"
            ],
            "extensions": [
                        ".pak",
                        ".locres"
            ],
            "exe_patterns": []
},
    },
    "Unity": {
        "canonical_name": "Unity",
        "aliases": [
            "unity",
            "unity engine",
            "unity3d",
            "unity mono",
            "unity il2cpp"
],
        "developer": "Unity Technologies",
        "origin_country": "USA / Denmark",
        "category": "Commercial Multi-Platform 2D/3D",
        "color": "#22c55e",
        "typical_games": [
            "Hollow Knight",
            "Ori and the Blind Forest / Will of the Wisps",
            "Cuphead",
            "Genshin Impact",
            "Subnautica 1 & Below Zero",
            "Valheim",
            "Escape from Tarkov",
            "Cities: Skylines",
            "Outer Wilds",
            "Risk of Rain 2",
            "Cult of the Lamb",
            "Sea of Stars",
            "Sons of the Forest",
            "Rust",
            "Tunic",
            "Dredge",
            "Dave the Diver"
],
        "text_formats": [
            ".assets",
            ".bundle",
            ".json",
            ".csv",
            ".txt",
            ".bytes"
],
        "font_tech": "TextMeshPro (TMP_FontAsset / SDF Font), Bitmap Font, Dynamic TrueType Font",
        "recommended_tools": [
            "UnityPy",
            "UABEA",
            "AssetStudio",
            "BepInEx",
            "MelonLoader",
            "XUnity.AutoTranslator",
            "TStudio",
            "TRun"
],
        "complexity": "Easy to Medium",
        "description_th": "เอนจิ้นยอดนิยมอันดับ 1 ของวงการเกมอินดี้และเกมมือถือ มีโครงสร้างแบบ Mono หรือ IL2CPP ไฟล์เกมจัดเก็บใน .assets หรือ AssetBundle (.bundle) ข้อความมักเป็น TextAsset/JSON และแสดงผลด้วย TextMeshPro ซึ่งม็อดไทยนิยมสร้าง Font Asset SDF บรรจุ PUA หรือฉีดฟอนต์ผ่าน BepInEx Hook",
        "description_en": "Top commercial multi-platform engine. Employs TextMeshPro SDF fonts and serialized AssetBundles. Moddable via BepInEx and AssetStudio/UABEA.",
        "detection": {
            "root_files": [
                        "unityplayer.dll",
                        "gameassembly.dll"
            ],
            "root_dlls": [
                        "unityplayer.dll"
            ],
            "sub_dirs": [
                        "_data",
                        "mono",
                        "il2cpp_data"
            ],
            "extensions": [
                        ".assets",
                        ".bundle"
            ],
            "exe_patterns": []
},
    },
    "CryEngine": {
        "canonical_name": "CryEngine",
        "aliases": [
            "cryengine",
            "cryengine 3",
            "cryengine v",
            "cry engine",
            "cryengine 2",
            "cryengine 1"
],
        "developer": "Crytek",
        "origin_country": "Germany",
        "category": "Commercial AAA 3D",
        "color": "#06b6d4",
        "typical_games": [
            "Crysis 1, 2, 3 (Original & Remastered)",
            "Kingdom Come: Deliverance (KCD1 & KCD2)",
            "Hunt: Showdown",
            "Sniper Ghost Warrior Contracts 1 & 2",
            "Prey (2017)",
            "Homefront: The Revolution",
            "Far Cry 1 (CryEngine 1)"
],
        "text_formats": [
            ".pak",
            ".xml",
            ".gfx",
            ".tbl",
            ".csv"
],
        "font_tech": "Scaleform GFx Font Library (gfxfontlib.gfx), TrueType via Flash, Bitmap Font",
        "recommended_tools": [
            "QuickBMS",
            "CryPak",
            "JPEXS Free Flash Decompiler",
            "TStudio",
            "TRun"
],
        "complexity": "Medium to High",
        "description_th": "เอนจิ้นกราฟิกสมจริงขั้นสุดยอดจากเยอรมนี จัดเก็บไฟล์ทั้งหมดในแพ็กเกจ .pak ข้อความแปลมักเป็นไฟล์ XML บรรจุใน Localization pak และ UI ใช้ Autodesk Scaleform GFx สำหรับเรนเดอร์ข้อความและฟอนต์ สามารถแก้ไขฟอนต์ไทยผ่าน JPEXS ได้อย่างแม่นยำ",
        "description_en": "Cutting-edge visual engine by Crytek. Uses .pak archives, XML text databases, and Scaleform GFx Flash font libraries.",
        "detection": {
            "root_files": [
                        "system.cfg",
                        "engine.pak",
                        "crysystem.dll",
                        "cryengine.dll"
            ],
            "root_dlls": [
                        "crysystem.dll",
                        "cryengine.dll"
            ],
            "sub_dirs": [
                        "localized",
                        "engine"
            ],
            "extensions": [
                        ".pak",
                        ".gfx"
            ],
            "exe_patterns": [
                        "kingdomcome.exe",
                        "crysis.exe"
            ]
},
    },
    "Amazon Lumberyard / O3DE": {
        "canonical_name": "Amazon Lumberyard / O3DE",
        "aliases": [
            "lumberyard",
            "amazon lumberyard",
            "o3de",
            "open 3d engine"
],
        "developer": "Amazon Game Tech / Linux Foundation",
        "origin_country": "USA",
        "category": "Open-Source / Commercial AAA 3D",
        "color": "#0ea5e9",
        "typical_games": [
            "New World",
            "Deadhaus Sonata",
            "Star Citizen (StarEngine - modified Lumberyard)"
],
        "text_formats": [
            ".pak",
            ".xml",
            ".json"
],
        "font_tech": "FreeType 2 / OpenType Native / Scaleform GFx",
        "recommended_tools": [
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นที่แยกสายการพัฒนามาจาก CryEngine โดย Amazon พัฒนาต่อเป็น Open 3D Engine (O3DE) รองรับโครงสร้างไฟล์คล้าย CryEngine (.pak) แต่ปรับปรุงระบบเน็ตเวิร์กและเอนทิตี UI สมัยใหม่",
        "description_en": "CryEngine fork by Amazon evolved into O3DE open source, using .pak archives and modernized UI systems.",
        "detection": {
            "root_files": [
                        "system.cfg"
            ],
            "root_dlls": [
                        "crysystem.dll",
                        "lyengine.dll"
            ],
            "sub_dirs": [],
            "extensions": [
                        ".pak"
            ],
            "exe_patterns": []
},
    },
    "Godot Engine": {
        "canonical_name": "Godot",
        "aliases": [
            "godot",
            "godot engine",
            "godot 4",
            "godot 3",
            "godotengine"
],
        "developer": "Godot Engine Community",
        "origin_country": "International / Argentina",
        "category": "Open-Source 2D/3D",
        "color": "#74c7ec",
        "typical_games": [
            "Brotato",
            "Cassette Beasts",
            "Buckshot Roulette",
            "Halls of Torment",
            "Sonic Colors: Ultimate (Blind Squirrel engine port)",
            "Dome Keeper",
            "Rogue State Revolution",
            "Ex-Zodiac"
],
        "text_formats": [
            ".pck",
            ".tscn",
            ".po",
            ".csv",
            ".json"
],
        "font_tech": "Native Dynamic Font (.ttf / .otf) via FreeType / TextServer HarfBuzz (Godot 4 รองรับสระไทยสมบูรณ์แบบ)",
        "recommended_tools": [
            "GDRE Tools",
            "Godot PCK Explorer",
            "poedit",
            "TStudio",
            "TRun"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นโอเพนซอร์สยอดนิยมอันดับ 1 ของโลก ตัวเกมรวมไฟล์แพ็กเกจเป็น .pck ไฟล์แปลนิยมใช้รูปแบบมาตรฐานสากล gettext (.po) หรือ .csv และใน Godot 4 มี TextServer HarfBuzz ในตัว ทำให้รองรับการจัดวางสระวรรณยุกต์ไทยได้อย่างถูกต้อง 100% โดยไม่ต้องแก้ฟอนต์",
        "description_en": "Leading free open-source engine. Uses .pck archives and standard gettext .po files. Godot 4 features native HarfBuzz text shaping with flawless Thai support.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".pck"
            ],
            "exe_patterns": []
},
    },
    "GameMaker": {
        "canonical_name": "GameMaker",
        "aliases": [
            "gamemaker",
            "gamemaker studio",
            "gamemaker: studio",
            "gms2",
            "gms",
            "gamemaker studio 2",
            "undertale engine"
],
        "developer": "YoYo Games / Opera",
        "origin_country": "UK",
        "category": "Commercial 2D",
        "color": "#10b981",
        "typical_games": [
            "Undertale",
            "Deltarune",
            "Hotline Miami 1 & 2",
            "Katana ZERO",
            "Pizza Tower",
            "Risk of Rain (Original)",
            "Nuclear Throne",
            "VA-11 Hall-A",
            "Hyper Light Drifter",
            "Forager",
            "Gunpoint"
],
        "text_formats": [
            "data.win",
            ".csv",
            ".json"
],
        "font_tech": "Embedded Sprite Font / Font Texture Glyphs in data.win",
        "recommended_tools": [
            "UndertaleModTool",
            "UTMT Bleeding Edge",
            "TStudio",
            "TRun"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้น 2D ชื่อดัง ตัวเกมคอมไพล์รวมทุกอย่างไว้ในไฟล์เดียว data.win (หรือ game.unx/game.ios) สามารถใช้ UndertaleModTool (UTMT) เปิดดู แก้ไขข้อความใน Strings Table และเพิ่มสระวรรณยุกต์หรือ PUA ใน Sprite Fonts ได้ง่ายดาย",
        "description_en": "Leading 2D engine packaging assets into a single data.win file. Fully editable via UndertaleModTool for string tables and font sprites.",
        "detection": {
            "root_files": [
                        "data.win"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        "data.win"
            ],
            "exe_patterns": []
},
    },
    "Construct": {
        "canonical_name": "Construct",
        "aliases": [
            "construct",
            "construct 2",
            "construct 3",
            "scirra construct"
],
        "developer": "Scirra",
        "origin_country": "UK",
        "category": "HTML5 / WebGL 2D Commercial",
        "color": "#f97316",
        "typical_games": [
            "There Is No Game: Wrong Dimension",
            "Iconoclasts (prototype era)",
            "The Next Penelope",
            "Airscape: The Fall of Gravity"
],
        "text_formats": [
            ".json",
            "package.nw",
            "c2runtime.js",
            "c3runtime.js"
],
        "font_tech": "CSS Web Fonts / Canvas Text / SpriteFont",
        "recommended_tools": [
            "7-Zip",
            "TStudio",
            "Text Editor"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นสร้างเกม HTML5 รันบน NW.js หรือ Electron ใน Windows ไฟล์เกมถูกรวมใน package.nw (เปิดได้ด้วย 7-Zip) ข้อความมักเป็น JSON หรือตัวแปรใน JS แก้ไขง่ายมาก",
        "description_en": "HTML5-based game creator wrapped in NW.js/Electron. Modded by opening package.nw with 7-Zip and editing JSON/JS files.",
        "detection": {
            "root_files": [
                        "package.nw",
                        "nw.exe"
            ],
            "root_dlls": [
                        "nw.dll",
                        "ffmpeg.dll"
            ],
            "sub_dirs": [],
            "extensions": [
                        ".nw"
            ],
            "exe_patterns": []
},
    },
    "Cocos2d-x / Cocos Creator": {
        "canonical_name": "Cocos2d-x",
        "aliases": [
            "cocos2d-x",
            "cocos",
            "cocos creator",
            "cocos2d"
],
        "developer": "Cocos / Chukong Technologies",
        "origin_country": "China",
        "category": "Open-Source 2D/3D Multi-Platform",
        "color": "#06b6d4",
        "typical_games": [
            "Geometry Dash",
            "Badland 1 & 2",
            "Fire Emblem Heroes",
            "Dragon Ball Z Dokkan Battle",
            "Kingdom Rush (Mobile ports)"
],
        "text_formats": [
            ".json",
            ".plist",
            ".lua",
            ".csv"
],
        "font_tech": "Bitmap Font (.fnt / .png), FreeType TrueType",
        "recommended_tools": [
            "TStudio",
            "Plist Editor",
            "TexturePacker"
],
        "complexity": "Medium",
        "description_th": "เฟรมเวิร์กยอดนิยมสำหรับเกม 2D ข้ามแพลตฟอร์ม ข้อความมักเก็บใน .plist, .json หรือสคริปต์ Lua นิยมใช้ฟอนต์บิตแมป BMFont (.fnt) ร่วมกับ FreeType",
        "description_en": "Open-source multi-platform framework using BMFont (.fnt), FreeType, and plist/json/lua data files.",
        "detection": {
            "root_files": [],
            "root_dlls": [
                        "cocos2d.dll",
                        "libcocos2d.dll"
            ],
            "sub_dirs": [
                        "resources"
            ],
            "extensions": [
                        ".plist"
            ],
            "exe_patterns": [
                        "geometrydash.exe"
            ]
},
    },
    "Defold": {
        "canonical_name": "Defold",
        "aliases": [
            "defold",
            "defold engine"
],
        "developer": "Defold Foundation / King",
        "origin_country": "Sweden",
        "category": "Lightweight 2D/3D Commercial",
        "color": "#f59e0b",
        "typical_games": [
            "Blossom Tales II",
            "Fates of Ort",
            "Void Scrappers"
],
        "text_formats": [
            ".dmanifest",
            ".arcd",
            ".json",
            ".lua"
],
        "font_tech": "Bitmap Font Generator / Distance Field Fonts",
        "recommended_tools": [
            "Defold Toolsuite",
            "QuickBMS",
            "TStudio"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นขนาดเล็กกินแรมน้อยพัฒนาโดย King ข้อความถูกคอมไพล์ในคลังข้อมูล Defold (.arcd) หรือเขียนผ่านสคริปต์ Lua",
        "description_en": "Ultra-lightweight game engine originally from King, utilizing Lua and packed archive files (.arcd).",
        "detection": {
            "root_files": [
                        "game.projectc",
                        "game.arcd"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".arcd"
            ],
            "exe_patterns": []
},
    },
    "Unigine": {
        "canonical_name": "Unigine",
        "aliases": [
            "unigine",
            "unigine 2",
            "unigine engine"
],
        "developer": "Unigine Corp",
        "origin_country": "Cyprus / Russia",
        "category": "Enterprise / High-End 3D Simulation",
        "color": "#8b5cf6",
        "typical_games": [
            "Oil Rush",
            "Cradle",
            "Valley Benchmark",
            "Superposition Benchmark"
],
        "text_formats": [
            ".ung",
            ".xml",
            ".json"
],
        "font_tech": "Native TrueType / TrueType Atlas Cache",
        "recommended_tools": [
            "ung_extract",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นสำหรับงานจำลองเสมือนจริงและกราฟิกสมจริง ไฟล์ทั้งหมดถูกบรรจุในคลัง .ung ข้อความใช้ XML/JSON",
        "description_en": "High-fidelity simulation and visual engine using .ung archive packages and standard XML text formatting.",
        "detection": {
            "root_files": [],
            "root_dlls": [
                        "unigine_x64.dll"
            ],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".ung"
            ],
            "exe_patterns": []
},
    },
    "Flax Engine": {
        "canonical_name": "Flax Engine",
        "aliases": [
            "flax",
            "flax engine"
],
        "developer": "Flax Engine",
        "origin_country": "Poland",
        "category": "Modern Commercial 3D Open-Source",
        "color": "#06b6d4",
        "typical_games": [
            "Indie titles and commercial tech demos"
],
        "text_formats": [
            ".flx",
            ".json",
            ".flaxpackage"
],
        "font_tech": "SDF Font Asset / FreeType Native",
        "recommended_tools": [
            "Flax Editor",
            "TStudio"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นยุคใหม่สไตล์ C++ และ C# โครงสร้างคล้าย Unreal Engine ผสมผสาน Unity ทำงานรวดเร็ว",
        "description_en": "Modern lightweight C++/C# engine with Unreal-inspired workflow and modular packaging.",
        "detection": {
            "root_files": [],
            "root_dlls": [
                        "flaxengine.dll"
            ],
            "sub_dirs": [
                        "content"
            ],
            "extensions": [
                        ".flx"
            ],
            "exe_patterns": []
},
    },
    "RE Engine": {
        "canonical_name": "RE Engine",
        "aliases": [
            "re engine",
            "reengine",
            "re_engine",
            "reach for the moon engine"
],
        "developer": "Capcom",
        "origin_country": "Japan",
        "category": "Proprietary AAA Action/Survival",
        "color": "#f43f5e",
        "typical_games": [
            "Resident Evil 7: Biohazard",
            "Resident Evil 2 Remake",
            "Resident Evil 3 Remake",
            "Resident Evil Village (RE8)",
            "Resident Evil 4 Remake",
            "Devil May Cry 5",
            "Monster Hunter Rise & Sunbreak",
            "Monster Hunter Wilds",
            "Dragon's Dogma 2",
            "Street Fighter 6",
            "Kunitsu-Gami: Path of the Goddess",
            "Dead Rising Deluxe Remaster",
            "Apollo Justice: Ace Attorney Trilogy"
],
        "text_formats": [
            ".msg.XX",
            ".msg",
            ".pak"
],
        "font_tech": "SDF Font Texture Atlas (.otf / .ttf embedded in GFX / DirectDraw via REFramework PUA hook)",
        "recommended_tools": [
            "REFramework",
            "REE.PAK.Tool",
            "TStudio",
            "TRun",
            "GMR",
            "Kuriimu"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นเรือธงที่ดีที่สุดของ Capcom โดดเด่นเรื่องโฟโตเรียลลิสติกและการโหลดฉากไร้รอยต่อ ไฟล์เกมถูกบีบอัดเป็น re_chunk_xxx.pak ข้อความภาษาเก็บในฟอร์แมต .msg (เช่น .msg.22 หรือ .msg.5391) มีระบบ REFramework ที่เปิดทางให้ฉีดฟอนต์ไทยและระบบแปลเข้าไปได้แบบเรียลไทม์",
        "description_en": "Capcom's flagship engine powering Resident Evil, DMC5, and Monster Hunter Wilds. Uses .msg inside re_chunk_xxx.pak with native REFramework modding support.",
        "detection": {
            "root_files": [
                        "re_chunk_000.pak",
                        "reframework"
            ],
            "root_dlls": [
                        "dinput8.dll"
            ],
            "sub_dirs": [],
            "extensions": [
                        ".msg",
                        ".pak"
            ],
            "exe_patterns": [
                        "re7.exe",
                        "re2.exe",
                        "re3.exe",
                        "re4.exe",
                        "re8.exe",
                        "dmc5.exe",
                        "mhrise.exe",
                        "dd2.exe",
                        "sf6.exe"
            ]
},
    },
    "MT Framework": {
        "canonical_name": "MT Framework",
        "aliases": [
            "mt framework",
            "mtframework",
            "mt_framework"
],
        "developer": "Capcom",
        "origin_country": "Japan",
        "category": "Proprietary AAA Action",
        "color": "#eab308",
        "typical_games": [
            "Monster Hunter: World & Iceborne",
            "Dragon's Dogma: Dark Arisen",
            "Resident Evil 5 & 6",
            "Resident Evil: Revelations 1 & 2",
            "Devil May Cry 4 & Special Edition",
            "Dead Rising 1 & 2",
            "Marvel vs. Capcom 3",
            "Mega Man 11",
            "Lost Planet 1 & 2",
            "DuckTales: Remastered"
],
        "text_formats": [
            ".arc",
            ".bin",
            ".gmd",
            ".msg"
],
        "font_tech": "Bitmap Font Sheets (.gfd / .tex / .dds) / MultiFont",
        "recommended_tools": [
            "ARC Tool",
            "Fluffy Mod Manager",
            "GMD Tool",
            "TStudio",
            "TRun"
],
        "complexity": "Medium to High",
        "description_th": "เอนจิ้นคลาสสิกผู้สร้างตำนานให้ Capcom ตลอดยุค PS3/PS4 ไฟล์บรรจุในแพ็กเกจ .arc ข้อความภาษาถูกเก็บในโครงสร้าง .gmd (Game Message Data) ฟอนต์เป็นแผ่น Texture บิตแมป ต้องขยายขนาดชีตและจัดเรียง Glyph ใหม่สำหรับภาษาไทย",
        "description_en": "Capcom's legendary previous-gen engine. Assets packed in .arc archives with text stored in .gmd binary files. Font rendering uses bitmap textures.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "nativepc",
                        "nativedx10",
                        "nativedx11"
            ],
            "extensions": [
                        ".arc",
                        ".gmd"
            ],
            "exe_patterns": [
                        "monsterhunterworld.exe",
                        "ddda.exe",
                        "re5dx9.exe",
                        "re6.exe",
                        "dmc4.exe"
            ]
},
    },
    "Classic RE Engine": {
        "canonical_name": "Classic RE",
        "aliases": [
            "classic re",
            "classic_re",
            "biohazard engine",
            "classic resident evil"
],
        "developer": "Capcom",
        "origin_country": "Japan",
        "category": "Retro Survival Horror (PS1 Era)",
        "color": "#dc2626",
        "typical_games": [
            "Resident Evil (1996)",
            "Resident Evil 2 (1998)",
            "Resident Evil 3: Nemesis (1999)"
],
        "text_formats": [
            ".bin",
            ".adt",
            ".pvd",
            ".rofs"
],
        "font_tech": "16-color 4-bit / 8-bit TIM / VRAM Texture Bitmaps",
        "recommended_tools": [
            "REtool",
            "Hex Editor",
            "TIM2Viewer",
            "TStudio"
],
        "complexity": "High",
        "description_th": "เอนจิ้น Resident Evil ยุคดั้งเดิมบน PS1/PC ยุค 90 ข้อความฝังในไบนารีและสคริปต์ห้อง (Room data) ฟอนต์เป็นรูปภาพ TIM ขนาดเล็ก",
        "description_en": "Classic 90s survival horror engine storing text within room data and rendering fonts from small TIM textures.",
        "detection": {
            "root_files": [
                        "bio2.exe",
                        "bio3.exe",
                        "residentevil.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "pl0",
                        "pl1"
            ],
            "extensions": [
                        ".adt",
                        ".pvd"
            ],
            "exe_patterns": [
                        "bio2.exe",
                        "bio3.exe"
            ]
},
    },
    "REDengine": {
        "canonical_name": "REDengine",
        "aliases": [
            "redengine",
            "redengine 3",
            "redengine 4",
            "red engine",
            "red_engine",
            "redengine 2"
],
        "developer": "CD Projekt RED",
        "origin_country": "Poland",
        "category": "Proprietary AAA Open-World RPG",
        "color": "#c084fc",
        "typical_games": [
            "The Witcher 2: Assassins of Kings (REDengine 1/2)",
            "The Witcher 3: Wild Hunt (REDengine 3)",
            "Cyberpunk 2077 & Phantom Liberty (REDengine 4)"
],
        "text_formats": [
            ".w2strings",
            ".archive",
            ".json",
            ".w3strings"
],
        "font_tech": "FreeType Vector Font Package / Cyberpunk inkHUD Font (.inkfont)",
        "recommended_tools": [
            "WolvenKit",
            "w3strings encoder/decoder",
            "CyberCAT",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นโลกเปิดคุณภาพสูงจากโปแลนด์ ใน The Witcher 3 ข้อความอยู่ในไฟล์ .w3strings / .w2strings บรรจุใน .bundle และใน Cyberpunk 2077 อยู่ใน .archive แก้ไขข้อความได้ผ่าน WolvenKit และ w3strings tool ฟอนต์รองรับ TTF/OTF ผ่านระบบ inkUI",
        "description_en": "CD Projekt RED's world-class RPG engine. Localization uses .w3strings (Witcher 3) and JSON inside .archive (Cyberpunk 2077), modded via WolvenKit.",
        "detection": {
            "root_files": [
                        "witcher3.exe",
                        "cyberpunk2077.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "r6",
                        "content/content0"
            ],
            "extensions": [
                        ".w2strings",
                        ".w3strings",
                        ".archive"
            ],
            "exe_patterns": [
                        "witcher3.exe",
                        "cyberpunk2077.exe"
            ]
},
    },
    "C-Engine": {
        "canonical_name": "C-Engine",
        "aliases": [
            "c-engine",
            "cengine",
            "c_engine",
            "techland c-engine"
],
        "developer": "Techland",
        "origin_country": "Poland",
        "category": "Proprietary AAA First-Person Open-World",
        "color": "#84cc16",
        "typical_games": [
            "Dying Light 2: Stay Human",
            "Dying Light: The Beast"
],
        "text_formats": [
            ".rpack",
            ".scr",
            ".csv",
            ".json"
],
        "font_tech": "Dynamic TrueType Font Atlas (.ttf) embedded in rpack packages",
        "recommended_tools": [
            "QuickBMS",
            "Dying Light 2 Mod Tools",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นยุคล่าสุดของ Techland พัฒนาต่อยอดจาก Chrome Engine เพื่อรองรับโลกเปิดขนาดใหญ่ของ Dying Light 2 ไฟล์บรรจุใน .rpack ในโฟลเดอร์ ph ข้อความอยู่ในสคริปต์ .scr และไฟล์แปลภาษา รองรับฟอนต์ TTF ภาษาไทยได้ดีเยี่ยม",
        "description_en": "Techland's cutting-edge open world engine powering Dying Light 2. Packages assets into .rpack archives under the 'ph' directory.",
        "detection": {
            "root_files": [],
            "root_dlls": [
                        "rwdi.dll"
            ],
            "sub_dirs": [
                        "ph",
                        "ph/source"
            ],
            "extensions": [
                        ".rpack"
            ],
            "exe_patterns": [
                        "dyinglightgame_x64_rwdi.exe"
            ]
},
    },
    "Chrome Engine": {
        "canonical_name": "Chrome Engine",
        "aliases": [
            "chrome engine",
            "chrome_engine",
            "chrome engine 4",
            "chrome engine 5",
            "chrome engine 6"
],
        "developer": "Techland",
        "origin_country": "Poland",
        "category": "Proprietary 3D Action",
        "color": "#a3e635",
        "typical_games": [
            "Dying Light 1",
            "Call of Juarez 1 (2006)",
            "Call of Juarez: Bound in Blood",
            "Call of Juarez: Gunslinger",
            "Dead Island (2011)",
            "Dead Island: Riptide",
            "Nail'd",
            "Sniper: Ghost Warrior 1"
],
        "text_formats": [
            ".pak",
            ".scr",
            ".txt"
],
        "font_tech": "Bitmap Font Generator (.fnt / .dds) / TrueType",
        "recommended_tools": [
            "7-Zip",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นสร้างชื่อของ Techland ไฟล์ .pak ของ Chrome Engine เป็นมาตรฐาน ZIP สามารถใช้ 7-Zip หรือ WinRAR เปิดแตกไฟล์และแพ็กกลับได้ทันที ข้อความอยู่ในไฟล์ .scr หรือ .txt ใน Data0.pak แก้ไขสะดวกมาก",
        "description_en": "Classic Techland engine whose .pak archives are standard ZIP containers, making text editing in .scr and .txt extremely straightforward.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".pak"
            ],
            "exe_patterns": [
                        "coj.exe",
                        "coj2.exe",
                        "cojgunslinger.exe",
                        "dyinglightgame.exe"
            ]
},
    },
    "4A Engine": {
        "canonical_name": "4A Engine",
        "aliases": [
            "4a engine",
            "4a_engine",
            "4a"
],
        "developer": "4A Games",
        "origin_country": "Ukraine / Malta",
        "category": "Proprietary AAA Post-Apocalyptic FPS",
        "color": "#e11d48",
        "typical_games": [
            "Metro 2033 (Original & Redux)",
            "Metro: Last Light (Original & Redux)",
            "Metro Exodus & Enhanced Edition",
            "Arktika.1"
],
        "text_formats": [
            ".vfs0",
            ".bin",
            ".txt"
],
        "font_tech": "DDS Bitmap Font Sheets / Texture Font Mapping",
        "recommended_tools": [
            "4A Games Unpacker",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นที่มีระบบแสงเงาและบรรยากาศอันดับต้นๆ ของวงการ พัฒนาโดยอดีตทีมงาน S.T.A.L.K.E.R. บรรจุไฟล์เกมใน content.vfs0 ข้อความถูกเก็บเป็นโครงสร้างไบนารี .bin ฟอนต์เป็นแผ่นเท็กซ์เจอร์บิตแมป",
        "description_en": "Atmospheric high-fidelity FPS engine powering the Metro series. Packs assets in .vfs0 containers with binary text databases.",
        "detection": {
            "root_files": [
                        "content.vfs0"
            ],
            "root_dlls": [
                        "4a.dll"
            ],
            "sub_dirs": [],
            "extensions": [
                        ".vfs0"
            ],
            "exe_patterns": [
                        "metro.exe",
                        "metroexodus.exe"
            ]
},
    },
    "Decima Engine": {
        "canonical_name": "Decima Engine",
        "aliases": [
            "decima engine",
            "decima",
            "decima_engine"
],
        "developer": "Guerrilla Games",
        "origin_country": "Netherlands",
        "category": "Proprietary AAA Open-World",
        "color": "#8b5cf6",
        "typical_games": [
            "Horizon Zero Dawn & Remastered",
            "Horizon Forbidden West",
            "Death Stranding & Director's Cut",
            "Death Stranding 2: On the Beach",
            "Killzone: Shadow Fall",
            "Until Dawn (PS4 Original)"
],
        "text_formats": [
            ".bin",
            ".core",
            ".stream"
],
        "font_tech": "Vector Distance Field SDF Font / TrueType Core Assets",
        "recommended_tools": [
            "Decima Explorer",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High to Very High",
        "description_th": "เอนจิ้นโอเพนเวิลด์ชั้นนำระดับโลกของ Guerrilla Games ร่วมพัฒนากับ Kojima Productions ไฟล์เกมบรรจุในแพ็กเกจ .bin มีระบบ Core Assets ที่มีโครงสร้างซับซ้อน ตัวอักษรและฟอนต์ใช้ระบบเวกเตอร์ความละเอียดสูง",
        "description_en": "Premier open-world engine by Guerrilla Games used for Horizon and Death Stranding. Uses .bin packages and structured .core binary formats.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".core",
                        ".bin"
            ],
            "exe_patterns": [
                        "horizonzerodawn.exe",
                        "ds.exe"
            ]
},
    },
    "Naughty Dog Engine": {
        "canonical_name": "Naughty Dog Proprietary",
        "aliases": [
            "naughty dog",
            "naughty dog engine",
            "naughty_dog"
],
        "developer": "Naughty Dog",
        "origin_country": "USA",
        "category": "Proprietary AAA Cinematic Action",
        "color": "#dc2626",
        "typical_games": [
            "The Last of Us Part I (PC/PS5)",
            "The Last of Us Part II Remastered",
            "Uncharted: Legacy of Thieves Collection (Uncharted 4 & Lost Legacy)",
            "The Last of Us (PS3/PS4 Original)",
            "Uncharted 1, 2, 3"
],
        "text_formats": [
            ".psarc",
            ".bin",
            ".dcx",
            ".txt"
],
        "font_tech": "TrueType Embedded / High-Res Distance Field Font",
        "recommended_tools": [
            "PSARC Tool",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นภาพยนตร์เกมที่ทรงพลังที่สุดของ Sony ข้อความและไฟล์เกมจัดเก็บในระบบคลัง .psarc มีการจัดการสคริปต์ภาษาอย่างเป็นระบบ ฟอนต์รองรับ Unicode",
        "description_en": "Naughty Dog's cinematic powerhouse engine. Uses .psarc archive packages with embedded string tables.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".psarc"
            ],
            "exe_patterns": [
                        "tlou-i.exe",
                        "u4.exe"
            ]
},
    },
    "Insomniac Games Engine": {
        "canonical_name": "Insomniac Engine",
        "aliases": [
            "insomniac engine",
            "insomniac",
            "insomniac games engine"
],
        "developer": "Insomniac Games",
        "origin_country": "USA",
        "category": "Proprietary AAA Open-World Action",
        "color": "#0284c7",
        "typical_games": [
            "Marvel's Spider-Man Remastered (PC)",
            "Marvel's Spider-Man: Miles Morales (PC)",
            "Marvel's Spider-Man 2",
            "Ratchet & Clank: Rift Apart (PC)",
            "Sunset Overdrive"
],
        "text_formats": [
            ".toc",
            ".archive",
            ".stage",
            ".mod"
],
        "font_tech": "Direct TrueType / OTF Font Asset with Custom Shaping",
        "recommended_tools": [
            "SMPC Mod Tool",
            "Insomniac Archive Tool",
            "TStudio",
            "TRun"
],
        "complexity": "Medium to High",
        "description_th": "เอนจิ้นที่ขึ้นชื่อเรื่องความเร็วในการสตรีมฉากและกราฟิกที่ลื่นไหล ในเวอร์ชัน PC บรรจุไฟล์เกมใน .archive และมีสารบัญ .toc มีเครื่องมือ SMPC Mod Tool รองรับการแก้ไขและติดตั้งม็อดอย่างเป็นระบบ",
        "description_en": "High-velocity streaming open-world engine. Employs .archive/.toc formats, moddable on PC via SMPC Tool.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "asset_archive"
            ],
            "extensions": [
                        ".archive",
                        ".toc"
            ],
            "exe_patterns": [
                        "spider-man.exe",
                        "milesmorales.exe",
                        "riftapart.exe"
            ]
},
    },
    "Sucker Punch Engine": {
        "canonical_name": "Sucker Punch Engine",
        "aliases": [
            "sucker punch",
            "sucker punch engine"
],
        "developer": "Sucker Punch Productions",
        "origin_country": "USA",
        "category": "Proprietary AAA Open-World",
        "color": "#ef4444",
        "typical_games": [
            "Ghost of Tsushima Director's Cut (PC/PS5)",
            "Ghost of Yotei",
            "inFAMOUS: Second Son & First Light"
],
        "text_formats": [
            ".psarc",
            ".bin",
            ".spk"
],
        "font_tech": "Unicode Vector Font Rendering / TrueType",
        "recommended_tools": [
            "PSARC Tool",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นโอเพนเวิลด์ความงามวิจิตรของ Ghost of Tsushima จัดเก็บไฟล์เกมหลักในคลัง .psarc",
        "description_en": "Visually stunning open world engine behind Ghost of Tsushima, packaging data in .psarc containers.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".psarc"
            ],
            "exe_patterns": [
                        "ghost.exe",
                        "ghostoftsushima.exe"
            ]
},
    },
    "Santa Monica Engine": {
        "canonical_name": "Santa Monica Engine",
        "aliases": [
            "santa monica",
            "proprietary_santa_monica",
            "santa monica engine",
            "god of war engine"
],
        "developer": "Santa Monica Studio",
        "origin_country": "USA",
        "category": "Proprietary AAA Action/Adventure",
        "color": "#b91c1c",
        "typical_games": [
            "God of War (2018 / PC)",
            "God of War Ragnarok (PC/PS5)",
            "God of War III & Remastered"
],
        "text_formats": [
            ".wad",
            ".pkg",
            ".bin"
],
        "font_tech": "TrueType Vector SDF / Glyphs atlas",
        "recommended_tools": [
            "GOW WAD Extractor",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นสำหรับมหากาพย์ God of War โดยเฉพาะ จัดเก็บไฟล์ในรูปแบบแพ็กเกจ .wad และ .pkg",
        "description_en": "Proprietary powerhouse engine designed specifically for the God of War Norse saga.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".wad",
                        ".pkg"
            ],
            "exe_patterns": [
                        "gow.exe",
                        "godofwar.exe",
                        "gowragnarok.exe"
            ]
},
    },
    "Northlight Engine": {
        "canonical_name": "Northlight Engine",
        "aliases": [
            "northlight engine",
            "northlight",
            "northlight_engine"
],
        "developer": "Remedy Entertainment",
        "origin_country": "Finland",
        "category": "Proprietary AAA Narrative/Cinematic",
        "color": "#6366f1",
        "typical_games": [
            "Alan Wake 2",
            "Control & Ultimate Edition",
            "Quantum Break",
            "CrossfireX (Campaign)"
],
        "text_formats": [
            ".bin",
            ".rmd",
            ".package"
],
        "font_tech": "Distance Field SDF Font / TrueType Vector",
        "recommended_tools": [
            "Northlight Tool",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นแห่งยุคจากฟินแลนด์ โดดเด่นด้วยระบบแสง Ray Tracing / Path Tracing และการผสมผสานวิดีโอ Live-Action ไร้รอยต่อ ไฟล์เกมบรรจุใน .bin หรือ .rmd ข้อความและสคริปต์อยู่ในรูปแบบไบนารี",
        "description_en": "Remedy's state-of-the-art engine featuring path-tracing and live-action integration. Uses .bin and .rmd packages.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".bin",
                        ".rmd"
            ],
            "exe_patterns": [
                        "alanwake2.exe",
                        "control.exe",
                        "quantumbreak.exe"
            ]
},
    },
    "Remedy Engine": {
        "canonical_name": "Remedy Engine",
        "aliases": [
            "remedy engine",
            "max payne engine",
            "alan wake engine",
            "remedycustom"
],
        "developer": "Remedy Entertainment",
        "origin_country": "Finland",
        "category": "Classic 3D Action",
        "color": "#4f46e5",
        "typical_games": [
            "Alan Wake (2010)",
            "Alan Wake's American Nightmare",
            "Max Payne 1 (2001)",
            "Max Payne 2: The Fall of Max Payne (2003)"
],
        "text_formats": [
            ".bin",
            ".ras",
            ".mpm",
            ".txt"
],
        "font_tech": "Bitmap Font Sheet / TrueType",
        "recommended_tools": [
            "Max Payne Toolset",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นยุคคลาสสิกของ Remedy ใน Max Payne ใช้ไฟล์ .ras และใน Alan Wake 1 ใช้ไฟล์ .bin",
        "description_en": "Remedy's classic generation engine used for Max Payne 1-2 (.ras) and Alan Wake 1 (.bin).",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".ras"
            ],
            "exe_patterns": [
                        "maxpayne.exe",
                        "maxpayne2.exe",
                        "alanwake.exe"
            ]
},
    },
    "Ubisoft Anvil": {
        "canonical_name": "Ubisoft Anvil",
        "aliases": [
            "anvil",
            "anvilnext",
            "anvilnext 2.0",
            "scimitar",
            "scimitar engine",
            "scimitar_engine",
            "ubisoft anvil"
],
        "developer": "Ubisoft Montreal",
        "origin_country": "Canada / France",
        "category": "Proprietary AAA Open-World",
        "color": "#ca8a04",
        "typical_games": [
            "Assassin's Creed (All: Mirage, Valhalla, Odyssey, Origins, Unity, Black Flag, etc.)",
            "Prince of Persia: The Forgotten Sands",
            "Tom Clancy's Rainbow Six Siege",
            "Immortals Fenyx Rising",
            "For Honor",
            "Ghost Recon Breakpoint",
            "Ghost Recon Wildlands"
],
        "text_formats": [
            ".forge",
            ".pck",
            ".bin"
],
        "font_tech": "Scaleform GFx / Distance Field Vector / TrueType embedded in Forge",
        "recommended_tools": [
            "AnvilToolkit",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นหลักของตระกูล Assassin's Creed เดิมชื่อ Scimitar และพัฒนาเป็น AnvilNext ไฟล์เกมทั้งหมดบรรจุในแพ็กเกจ .forge ขนาดใหญ่ ข้อความถูกบีบอัดเป็นไบนารี สามารถเปิดและแก้ไขผ่าน AnvilToolkit",
        "description_en": "Ubisoft's primary open-world engine for Assassin's Creed and Rainbow Six. Packs assets into massive .forge containers, modded via AnvilToolkit.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".forge"
            ],
            "exe_patterns": [
                        "acvalhalla.exe",
                        "acodyssey.exe",
                        "acorigins.exe",
                        "rainbowsix.exe"
            ]
},
    },
    "Dunia Engine": {
        "canonical_name": "Dunia Engine",
        "aliases": [
            "dunia engine",
            "dunia",
            "dunia_engine",
            "dunia 2"
],
        "developer": "Ubisoft Montreal",
        "origin_country": "Canada",
        "category": "Proprietary AAA Open-World FPS",
        "color": "#d97706",
        "typical_games": [
            "Far Cry 2",
            "Far Cry 3 & Blood Dragon",
            "Far Cry 4",
            "Far Cry Primal",
            "Far Cry 5 & New Dawn",
            "Far Cry 6",
            "Avatar: The Game (2009)"
],
        "text_formats": [
            ".dat",
            ".fat",
            ".xml",
            ".oasis"
],
        "font_tech": "Direct TrueType / OASIS Font Database / Scaleform GFx",
        "recommended_tools": [
            "Gibbed Dunia Tools",
            "Far Cry Mod Installer",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นสร้างสรรค์หมู่เกาะและทุ่งกว้างของ Far Cry ต่อยอดมาจาก CryEngine บรรจุไฟล์คู่ .dat และ .fat แก้ไขง่ายผ่าน Gibbed Dunia Tools ข้อความภาษาอยู่ในไฟล์ XML/Oasis strings",
        "description_en": "Ubisoft's Far Cry engine derived from CryEngine. Packages data in matching .dat/.fat archives with XML text databases.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "data_win32"
            ],
            "extensions": [
                        ".dat",
                        ".fat"
            ],
            "exe_patterns": [
                        "farcry3.exe",
                        "farcry4.exe",
                        "farcry5.exe",
                        "farcry6.exe"
            ]
},
    },
    "Disrupt Engine": {
        "canonical_name": "Disrupt Engine",
        "aliases": [
            "disrupt engine",
            "disrupt",
            "disrupt_engine"
],
        "developer": "Ubisoft Montreal",
        "origin_country": "Canada",
        "category": "Proprietary AAA Modern Urban Open-World",
        "color": "#3b82f6",
        "typical_games": [
            "Watch Dogs 1",
            "Watch Dogs 2",
            "Watch Dogs: Legion"
],
        "text_formats": [
            ".dat",
            ".fat",
            ".xml",
            ".bin"
],
        "font_tech": "Distance Field Font / Scaleform GFx",
        "recommended_tools": [
            "Gibbed Disrupt Tools",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นจำลองเมืองใหญ่และระบบแฮกของตระกูล Watch Dogs ใช้โครงสร้างไฟล์คู่ .dat/.fat คล้าย Dunia แต่ปรับแต่งสำหรับจำลองประชากรเมืองและการจราจร",
        "description_en": "Urban open-world engine for Watch Dogs, using .dat/.fat container archives and XML text structures.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "data_win64"
            ],
            "extensions": [
                        ".dat",
                        ".fat"
            ],
            "exe_patterns": [
                        "watch_dogs.exe",
                        "watchdogs2.exe",
                        "watchdogslegion.exe"
            ]
},
    },
    "Snowdrop": {
        "canonical_name": "Snowdrop",
        "aliases": [
            "snowdrop",
            "snowdrop engine",
            "snowdrop_engine"
],
        "developer": "Massive Entertainment / Ubisoft",
        "origin_country": "Sweden",
        "category": "Proprietary AAA Dynamic 3D",
        "color": "#0ea5e9",
        "typical_games": [
            "Tom Clancy's The Division 1 & 2",
            "Avatar: Frontiers of Pandora",
            "Star Wars Outlaws",
            "South Park: The Fractured But Whole",
            "Mario + Rabbids Kingdom Battle / Sparks of Hope",
            "The Settlers: New Allies"
],
        "text_formats": [
            ".sdf",
            ".dat",
            ".bin"
],
        "font_tech": "Direct SDF Font (Signed Distance Field) / TrueType Embedded",
        "recommended_tools": [
            "Snowdrop Extractor",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "Very High",
        "description_th": "เอนจิ้นยุคใหม่ของ Ubisoft พัฒนาโดย Massive โดดเด่นด้านระบบ Node Scripting กราฟิก และระบบสภาพอากาศ ไฟล์ถูกบีบอัดสูงมากในคลัง .sdf",
        "description_en": "Massive Entertainment's powerhouse engine powering The Division and Star Wars Outlaws. High compression .sdf packages.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".sdf"
            ],
            "exe_patterns": [
                        "thedivision.exe",
                        "thedivision2.exe",
                        "outlaws.exe"
            ]
},
    },
    "Jade Engine": {
        "canonical_name": "Jade Engine",
        "aliases": [
            "jade engine",
            "jade",
            "jade_engine"
],
        "developer": "Ubisoft Montpellier",
        "origin_country": "France",
        "category": "Classic 3D Action/Adventure",
        "color": "#14b8a6",
        "typical_games": [
            "Beyond Good & Evil (Original & 20th Anniversary)",
            "Prince of Persia: The Sands of Time (2003)",
            "Prince of Persia: Warrior Within (2004)",
            "Prince of Persia: The Two Thrones (2005)",
            "Peter Jackson's King Kong",
            "Rayman Raving Rabbids"
],
        "text_formats": [
            ".bf",
            ".bin"
],
        "font_tech": "Bitmap Font Textures / TrueType Rasterized Sheets",
        "recommended_tools": [
            "Jade BF Ripper",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นระดับตำนานของผู้สร้าง Michel Ancel บรรจุเนื้อหาทั้งหมดในไฟล์ BigFile (.bf) ขนาดใหญ่เพียงไฟล์เดียว ฟอนต์เป็นแผ่นบิตแมปความละเอียดต่ำ",
        "description_en": "Legendary Ubisoft engine by Michel Ancel. Encapsulates all game data inside a single BigFile (.bf) container.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".bf"
            ],
            "exe_patterns": [
                        "bge.exe",
                        "pop.exe",
                        "pop2.exe",
                        "pop3.exe"
            ]
},
    },
    "Creation Engine 2": {
        "canonical_name": "Creation Engine 2",
        "aliases": [
            "creation engine 2",
            "creation 2",
            "creationengine2"
],
        "developer": "Bethesda Game Studios",
        "origin_country": "USA",
        "category": "Proprietary AAA Open-World RPG",
        "color": "#f59e0b",
        "typical_games": [
            "Starfield",
            "The Elder Scrolls VI (Upcoming)"
],
        "text_formats": [
            ".ba2",
            ".strings",
            ".dlstrings",
            ".ilstrings",
            ".esm"
],
        "font_tech": "Scaleform GFx / SWF Flash Fonts / Direct TTF Injection",
        "recommended_tools": [
            "Creation Kit 2",
            "xEdit (SF1Edit)",
            "BA2 Manager",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "วิวัฒนาการล่าสุดของเอนจิ้น Bethesda สำหรับ Starfield ใช้ระบบคลังข้อมูล .ba2 และไฟล์ข้อความ .strings มีระบบ Creation Kit รองรับม็อดเต็มรูปแบบ",
        "description_en": "Next-generation Bethesda engine powering Starfield, featuring updated .ba2 archives and .strings localization tables.",
        "detection": {
            "root_files": [
                        "starfield.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".ba2",
                        ".esm"
            ],
            "exe_patterns": [
                        "starfield.exe"
            ]
},
    },
    "Creation Engine": {
        "canonical_name": "Creation Engine",
        "aliases": [
            "creation engine",
            "creation",
            "creationengine"
],
        "developer": "Bethesda Game Studios",
        "origin_country": "USA",
        "category": "Proprietary AAA Open-World RPG",
        "color": "#fbbf24",
        "typical_games": [
            "The Elder Scrolls V: Skyrim (Legendary, Special, Anniversary Editions)",
            "Fallout 4",
            "Fallout 76"
],
        "text_formats": [
            ".ba2",
            ".bsa",
            ".strings",
            ".dlstrings",
            ".ilstrings",
            ".esp",
            ".esm"
],
        "font_tech": "Flash SWF (fontconfig.txt / fonts_en.swf) / Direct TrueType",
        "recommended_tools": [
            "Creation Kit",
            "xEdit (TES5Edit / FO4Edit)",
            "BSA Browser",
            "TStudio",
            "TRun"
],
        "complexity": "Easy to Medium",
        "description_th": "หนึ่งในเอนจิ้นที่มีคอมมูนิตี้ม็อดใหญ่ที่สุดในโลก ไฟล์บรรจุใน .bsa หรือ .ba2 ข้อความภาษาแยกเป็นไฟล์ .strings (.dlstrings/.ilstrings) และฟอนต์ควบคุมผ่าน fontconfig.txt ในโฟลเดอร์ Interface สามารถใส่ฟอนต์ไทย TTF ได้ง่ายมาก",
        "description_en": "Immense modding ecosystem engine. Uses .bsa/.ba2 archives with .strings tables and fontconfig.txt pointing to TrueType SWF fonts.",
        "detection": {
            "root_files": [
                        "skyrim.exe",
                        "skyrimse.exe",
                        "fallout4.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "data/interface",
                        "data/strings"
            ],
            "extensions": [
                        ".bsa",
                        ".ba2",
                        ".strings"
            ],
            "exe_patterns": [
                        "tesv.exe",
                        "skyrimse.exe",
                        "fallout4.exe",
                        "fallout76.exe"
            ]
},
    },
    "Gamebryo": {
        "canonical_name": "Gamebryo",
        "aliases": [
            "gamebryo",
            "netimmerse"
],
        "developer": "Gamebase / Numerical Design Limited (NDL)",
        "origin_country": "USA",
        "category": "Commercial / Classic 3D RPG",
        "color": "#78716c",
        "typical_games": [
            "The Elder Scrolls IV: Oblivion",
            "Fallout 3",
            "Fallout: New Vegas",
            "The Elder Scrolls III: Morrowind (NetImmerse)",
            "Catherine (Atlus)",
            "Epic Mickey",
            "Civilization IV",
            "Bully: Scholarship Edition (NetImmerse)"
],
        "text_formats": [
            ".bsa",
            ".esp",
            ".esm",
            ".txt",
            ".xml"
],
        "font_tech": "FNT / TEX Bitmap Fonts (.fnt) in Fonts directory",
        "recommended_tools": [
            "FOMM",
            "BSA Commander",
            "FNVEdit",
            "FO3Edit",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "รากฐานของเอนจิ้น RPG ชื่อดังยุค 2000 บรรจุไฟล์ใน .bsa ฟอนต์เป็นไฟล์บิตแมปคู่ .fnt และ .tex สามารถสร้างฟอนต์ไทยด้วย BMFont และแทนที่เข้าไปได้โดยตรง",
        "description_en": "Predecessor to Creation Engine powering Oblivion and Fallout New Vegas. Uses .bsa archives and .fnt bitmap fonts.",
        "detection": {
            "root_files": [
                        "fallout3.exe",
                        "falloutnv.exe",
                        "oblivion.exe",
                        "morrowind.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "data/fonts"
            ],
            "extensions": [
                        ".bsa",
                        ".esp"
            ],
            "exe_patterns": [
                        "falloutnv.exe",
                        "fallout3.exe",
                        "oblivion.exe"
            ]
},
    },
    "id Tech 7": {
        "canonical_name": "id Tech 7",
        "aliases": [
            "id tech 7",
            "id_tech_7",
            "idtech7"
],
        "developer": "id Software",
        "origin_country": "USA",
        "category": "Proprietary AAA Ultra-Fast FPS",
        "color": "#f43f5e",
        "typical_games": [
            "DOOM Eternal & The Ancient Gods Part 1 & 2"
],
        "text_formats": [
            ".package",
            ".resources",
            ".json"
],
        "font_tech": "Signed Distance Field (SDF) Font Atlas / Vulkan Native",
        "recommended_tools": [
            "id-tech-7-extractor",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นความเร็วสูงระดับตำนาน รันด้วย Vulkan 100% จัดเก็บไฟล์ใน .package และ .resources ข้อความภาษาและสตริงถูกเข้ารหัสเฉพาะ",
        "description_en": "Vulkan-exclusive high-velocity FPS engine behind DOOM Eternal. Packaged in .package and .resources files.",
        "detection": {
            "root_files": [
                        "doometernal.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "base"
            ],
            "extensions": [
                        ".package",
                        ".resources"
            ],
            "exe_patterns": [
                        "doometernal.exe"
            ]
},
    },
    "id Tech 6": {
        "canonical_name": "id Tech 6",
        "aliases": [
            "id tech 6",
            "id_tech_6",
            "idtech6"
],
        "developer": "id Software",
        "origin_country": "USA",
        "category": "Proprietary AAA FPS",
        "color": "#ec4899",
        "typical_games": [
            "DOOM (2016)",
            "Wolfenstein II: The New Colossus",
            "Wolfenstein: Youngblood"
],
        "text_formats": [
            ".resources",
            ".package",
            ".json"
],
        "font_tech": "TrueType Vector SDF / MegaTexture Font",
        "recommended_tools": [
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นที่ฟื้นคืนชีพซีรีส์ DOOM ในปี 2016 จัดเก็บเนื้อหาใน .resources และ .package",
        "description_en": "Reboot engine for DOOM 2016 and Wolfenstein II, utilizing .resources packages.",
        "detection": {
            "root_files": [
                        "doomx64.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "base"
            ],
            "extensions": [
                        ".resources"
            ],
            "exe_patterns": [
                        "doomx64.exe",
                        "newcolossus_x64.exe"
            ]
},
    },
    "id Tech 5": {
        "canonical_name": "id Tech 5",
        "aliases": [
            "id tech 5",
            "id_tech_5",
            "idtech5"
],
        "developer": "id Software",
        "origin_country": "USA",
        "category": "Proprietary 3D Action",
        "color": "#db2777",
        "typical_games": [
            "Rage (2011)",
            "Wolfenstein: The New Order",
            "Wolfenstein: The Old Blood",
            "The Evil Within 1"
],
        "text_formats": [
            ".streamed",
            ".resources",
            ".bimage"
],
        "font_tech": "MegaTexture Virtual Texturing / TrueType TTF",
        "recommended_tools": [
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "Very High",
        "description_th": "เอนจิ้นที่มีเทคโนโลยี MegaTexture อันเป็นเอกลักษณ์ บรรจุไฟล์ลงใน .resources",
        "description_en": "Famous for MegaTexture virtual texturing, storing assets in .streamed/.resources containers.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "virtualtextures",
                        "base"
            ],
            "extensions": [
                        ".streamed"
            ],
            "exe_patterns": [
                        "rage.exe",
                        "wolfneworder_x64.exe",
                        "theevilwithin.exe"
            ]
},
    },
    "id Tech 3": {
        "canonical_name": "id Tech 3",
        "aliases": [
            "id tech 3",
            "id_tech_3",
            "idtech3",
            "quake 3 engine"
],
        "developer": "id Software",
        "origin_country": "USA",
        "category": "Classic 3D Action",
        "color": "#be185d",
        "typical_games": [
            "Quake III Arena",
            "Star Wars Jedi Knight II: Jedi Outcast",
            "Star Wars Jedi Knight: Jedi Academy",
            "Return to Castle Wolfenstein",
            "Call of Duty 1 & 2 (Original IW Engine based on id Tech 3)",
            "Medal of Honor: Allied Assault",
            "Soldier of Fortune II"
],
        "text_formats": [
            ".pk3",
            ".str",
            ".cfg",
            ".menu"
],
        "font_tech": "Bitmap Font Glyphs (.dat / .tga) in fonts/ folder",
        "recommended_tools": [
            "Pakscape",
            "7-Zip",
            "OpenJK",
            "TStudio",
            "TRun"
],
        "complexity": "Easy to Medium",
        "description_th": "เอนจิ้นยอดนิยมยุค 2000 ไฟล์ .pk3 เป็นมาตรฐานไฟล์ ZIP สามารถเปิดดูด้วย 7-Zip ได้ทันที ข้อความอยู่ในไฟล์ .str และฟอนต์เป็นไฟล์บิตแมป",
        "description_en": "Legendary engine packaging assets into standard ZIP-based .pk3 archives with .str localization files.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "base",
                        "gamedata"
            ],
            "extensions": [
                        ".pk3"
            ],
            "exe_patterns": [
                        "jamp.exe",
                        "jasp.exe",
                        "quake3.exe",
                        "wolfsp.exe"
            ]
},
    },
    "id Tech": {
        "canonical_name": "id Tech",
        "aliases": [
            "id tech",
            "idtech",
            "id_tech",
            "id software engine"
],
        "developer": "id Software",
        "origin_country": "USA",
        "category": "Proprietary FPS",
        "color": "#ec4899",
        "typical_games": [
            "General id Tech titles"
],
        "text_formats": [
            ".pk3",
            ".pk4",
            ".wad",
            ".resources"
],
        "font_tech": "Bitmap Font / TrueType",
        "recommended_tools": [
            "Pakscape",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "หมวดหมู่ทั่วไปสำหรับเอนจิ้นตระกูล id Tech",
        "description_en": "General category for id Software's id Tech engine lineage.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "base"
            ],
            "extensions": [
                        ".pk3",
                        ".pk4"
            ],
            "exe_patterns": []
},
    },
    "Void Engine": {
        "canonical_name": "Void Engine",
        "aliases": [
            "void engine",
            "void",
            "void_engine",
            "arkane void"
],
        "developer": "Arkane Studios",
        "origin_country": "France",
        "category": "Proprietary AAA Immersive Sim",
        "color": "#a855f7",
        "typical_games": [
            "Dishonored 2",
            "Dishonored: Death of the Outsider"
],
        "text_formats": [
            ".sharedresources",
            ".resources",
            ".bimage"
],
        "font_tech": "Distance Field Font / TTF embedded in resources",
        "recommended_tools": [
            "QuickBMS",
            "Dishonored 2 Tool",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นที่ Arkane Studios นำ id Tech 5 มาปรับแต่งขนานใหญ่เพื่อสร้างระบบ Immersive Sim ที่สมบูรณ์แบบ จัดเก็บไฟล์ใน .sharedresources",
        "description_en": "Customized id Tech 5 fork built by Arkane for Dishonored 2, packaging assets in .sharedresources.",
        "detection": {
            "root_files": [
                        "dishonored2.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "base"
            ],
            "extensions": [
                        ".sharedresources"
            ],
            "exe_patterns": [
                        "dishonored2.exe",
                        "dishonoreddot_o.exe"
            ]
},
    },
    "STEM Engine": {
        "canonical_name": "STEM Engine",
        "aliases": [
            "stem engine",
            "stem",
            "stem_engine",
            "tango stem"
],
        "developer": "Tango Gameworks",
        "origin_country": "Japan",
        "category": "Proprietary AAA Survival Horror",
        "color": "#b91c1c",
        "typical_games": [
            "The Evil Within 2"
],
        "text_formats": [
            ".sharedresources",
            ".resources"
],
        "font_tech": "TrueType Vector Font / SDF",
        "recommended_tools": [
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นเฉพาะตัวของ Tango Gameworks ที่พัฒนาต่อจาก id Tech เพื่อสร้างบรรยากาศหลอนใน The Evil Within 2",
        "description_en": "Tango Gameworks' id Tech-based customized engine powering The Evil Within 2.",
        "detection": {
            "root_files": [
                        "teiw2.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "base"
            ],
            "extensions": [
                        ".sharedresources"
            ],
            "exe_patterns": [
                        "theevilwithin2.exe",
                        "teiw2.exe"
            ]
},
    },
    "RAGE Engine": {
        "canonical_name": "RAGE Engine",
        "aliases": [
            "rage engine",
            "rage",
            "rage_engine",
            "rockstar advanced game engine",
            "rockstar"
],
        "developer": "Rockstar Games",
        "origin_country": "USA / UK",
        "category": "Proprietary AAA Open-World Action",
        "color": "#e11d48",
        "typical_games": [
            "Grand Theft Auto V & Online",
            "Grand Theft Auto IV & Episodes from Liberty City",
            "Red Dead Redemption 1 (PC)",
            "Red Dead Redemption 2",
            "Max Payne 3",
            "Midnight Club: Los Angeles",
            "Rockstar Games Presents Table Tennis"
],
        "text_formats": [
            ".rpf",
            ".gxt2",
            ".gxt",
            ".oiv"
],
        "font_tech": "Scaleform GFx / Texture Font Dictionary (.wtd / .ytd) / Direct TrueType",
        "recommended_tools": [
            "OpenIV",
            "CodeWalker",
            "GXT2 Editor",
            "TStudio",
            "TRun"
],
        "complexity": "Medium to High",
        "description_th": "เอนจิ้นโลกเปิดระดับตำนานของ Rockstar Games บรรจุไฟล์เกมทั้งหมดในแพ็กเกจ .rpf สามารถใช้ OpenIV หรือ CodeWalker เปิดแก้ไขได้ ข้อความภาษาอยู่ในไฟล์ตารางข้อความ .gxt2 มีระบบม็อดที่กว้างขวาง",
        "description_en": "Rockstar Advanced Game Engine powering GTA and Red Dead. Data resides in .rpf archives with text stored in .gxt2 tables.",
        "detection": {
            "root_files": [
                        "gta5.exe",
                        "rdr2.exe",
                        "playrdr.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".rpf"
            ],
            "exe_patterns": [
                        "gta5.exe",
                        "gtaiv.exe",
                        "rdr2.exe",
                        "maxpayne3.exe"
            ]
},
    },
    "RenderWare": {
        "canonical_name": "RenderWare",
        "aliases": [
            "renderware",
            "criterion renderware"
],
        "developer": "Criterion Games",
        "origin_country": "UK",
        "category": "Classic 3D Multi-Platform",
        "color": "#ea580c",
        "typical_games": [
            "Grand Theft Auto III",
            "Grand Theft Auto: Vice City",
            "Grand Theft Auto: San Andreas",
            "Burnout 3: Takedown / Revenge / Paradise",
            "Sonic Heroes",
            "Bully (Original PS2 era)",
            "Tony Hawk's Pro Skater 3 & 4"
],
        "text_formats": [
            ".img",
            ".txd",
            ".dff",
            ".gxt"
],
        "font_tech": "fonts.txd (Texture Dictionary Bitmap Glyph Sheets)",
        "recommended_tools": [
            "IMG Tool",
            "TXD Workshop",
            "GXT Editor",
            "TStudio",
            "TRun"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นยุคทอง PS2 ผู้สร้างความสำเร็จให้ GTA ภาค 3, Vice City และ San Andreas ไฟล์เก็บใน gta3.img ข้อความอยู่ใน american.gxt และฟอนต์เป็นไฟล์เท็กซ์เจอร์ fonts.txd",
        "description_en": "The iconic PS2-era engine behind classic GTA trilogy, storing assets in .img and fonts in fonts.txd.",
        "detection": {
            "root_files": [
                        "gta-sa.exe",
                        "gta-vc.exe",
                        "gta3.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "models",
                        "text"
            ],
            "extensions": [
                        ".img",
                        ".txd",
                        ".gxt"
            ],
            "exe_patterns": [
                        "gta-sa.exe",
                        "gta-vc.exe",
                        "gta3.exe"
            ]
},
    },
    "Source 2": {
        "canonical_name": "Source 2",
        "aliases": [
            "source 2",
            "source2",
            "source_2"
],
        "developer": "Valve Corporation",
        "origin_country": "USA",
        "category": "Proprietary AAA Next-Gen 3D",
        "color": "#ea580c",
        "typical_games": [
            "Half-Life: Alyx",
            "Counter-Strike 2 (CS2)",
            "Dota 2",
            "Deadlock",
            "Aperture Desk Job"
],
        "text_formats": [
            ".vpk",
            ".vdata",
            ".txt",
            ".json"
],
        "font_tech": "Panorama UI / FreeType Native TrueType / TrueType Vector",
        "recommended_tools": [
            "VRF (Source 2 Viewer)",
            "GCFScape",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นรุ่นใหม่ล่าสุดจาก Valve ปรับปรุงจาก Source Engine เดิม ใช้ระบบ Panorama UI ที่เขียนด้วย HTML/CSS/JS ข้อความอยู่ในคลัง .vpk และรองรับฟอนต์ TTF ภาษาไทยได้ง่ายผ่าน CSS styling",
        "description_en": "Valve's next-gen engine powered by Panorama UI (HTML/CSS/JS). Content packed in .vpk with excellent modern typography support.",
        "detection": {
            "root_files": [
                        "cs2.exe",
                        "hlvr.exe"
            ],
            "root_dlls": [
                        "tier0.dll",
                        "engine2.dll"
            ],
            "sub_dirs": [
                        "game/csgo",
                        "game/hlvr"
            ],
            "extensions": [
                        ".vpk"
            ],
            "exe_patterns": [
                        "cs2.exe",
                        "hlvr.exe"
            ]
},
    },
    "Source Engine": {
        "canonical_name": "Source Engine",
        "aliases": [
            "source engine",
            "source",
            "source_engine"
],
        "developer": "Valve Corporation",
        "origin_country": "USA",
        "category": "Proprietary AAA 3D Classic",
        "color": "#f97316",
        "typical_games": [
            "Half-Life 2 (Episodes 1 & 2)",
            "Portal 1 & 2",
            "Left 4 Dead 1 & 2",
            "Team Fortress 2",
            "Counter-Strike: Global Offensive (CS:GO)",
            "Counter-Strike: Source",
            "Garry's Mod",
            "Titanfall 1 & 2 (Customized Source)",
            "Apex Legends (Customized Source)",
            "The Stanley Parable",
            "Vampire: The Masquerade - Bloodlines"
],
        "text_formats": [
            ".vpk",
            ".txt",
            ".res",
            ".pcf"
],
        "font_tech": "VGUI Font Mapping / TrueType System Fonts via ClientScheme.res",
        "recommended_tools": [
            "GCFScape",
            "VTFEdit",
            "Crowbar",
            "TStudio",
            "TRun"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นยอดนิยมตลอดกาลจาก Valve บรรจุไฟล์เกมใน .vpk ข้อความแปลอยู่ในโฟลเดอร์ resource (เช่น closecaption_english.txt หรือ basemodui_english.txt) ในรูปแบบ KeyValues และฟอนต์ควบคุมผ่าน ClientScheme.res สามารถใช้ฟอนต์ TTF จาก Windows ได้ทันที",
        "description_en": "Iconic Valve engine packing content in .vpk files. Localization uses KeyValues text in resource/ folder and ClientScheme.res for system font mapping.",
        "detection": {
            "root_files": [
                        "hl2.exe"
            ],
            "root_dlls": [
                        "tier0.dll",
                        "vstdlib.dll"
            ],
            "sub_dirs": [
                        "hl2",
                        "portal2",
                        "left4dead2",
                        "csgo"
            ],
            "extensions": [
                        ".vpk"
            ],
            "exe_patterns": [
                        "hl2.exe",
                        "portal2.exe",
                        "left4dead2.exe",
                        "csgo.exe"
            ]
},
    },
    "GoldSrc": {
        "canonical_name": "GoldSrc",
        "aliases": [
            "goldsrc",
            "goldsource",
            "half-life 1 engine"
],
        "developer": "Valve Corporation",
        "origin_country": "USA",
        "category": "Retro 3D (Modified Quake)",
        "color": "#c2410c",
        "typical_games": [
            "Half-Life 1 (1998)",
            "Counter-Strike 1.6",
            "Day of Defeat",
            "Team Fortress Classic",
            "Sven Co-op"
],
        "text_formats": [
            ".pak",
            ".wad",
            ".txt",
            ".titles"
],
        "font_tech": "VGUI Bitmap Font Glyphs / TrueType in Steam era",
        "recommended_tools": [
            "Wally",
            "PakExplorer",
            "TStudio"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นแรกของ Valve ที่นำเอนจิ้น Quake มาพัฒนาต่อ บรรจุเท็กซ์เจอร์ใน .wad และแพ็กเกจ .pak",
        "description_en": "Valve's debut engine based on modified Quake engine, utilizing .wad and .pak archives.",
        "detection": {
            "root_files": [
                        "hl.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "valve",
                        "cstrike"
            ],
            "extensions": [
                        ".wad"
            ],
            "exe_patterns": [
                        "hl.exe"
            ]
},
    },
    "FromSoftware Proprietary": {
        "canonical_name": "FromSoftware Proprietary",
        "aliases": [
            "fromsoftware",
            "fromsoftware engine",
            "dantelion",
            "fromsoftware proprietary",
            "souls engine"
],
        "developer": "FromSoftware",
        "origin_country": "Japan",
        "category": "Proprietary AAA Action RPG",
        "color": "#475569",
        "typical_games": [
            "Elden Ring & Shadow of the Erdtree",
            "Dark Souls: Remastered",
            "Dark Souls II: Scholar of the First Sin",
            "Dark Souls III",
            "Bloodborne",
            "Sekiro: Shadows Die Twice",
            "Armored Core VI: Fires of Rubicon",
            "Demon's Souls (Original PS3)"
],
        "text_formats": [
            ".bdt",
            ".bhd",
            ".msgbnd.dcx",
            ".fmg",
            ".param"
],
        "font_tech": "Scaleform GFx / Font Sheet Atlas (.gfxfontlib) / TrueType Embedded in Layouts",
        "recommended_tools": [
            "WitchyBND",
            "Yabber",
            "FMG Editor",
            "UXM Selective Unpacker",
            "TStudio",
            "TRun"
],
        "complexity": "Medium to High",
        "description_th": "เอนจิ้นเฉพาะตัวของ FromSoftware ที่สร้างความประทับใจให้เกมเมอร์ทั่วโลก บรรจุไฟล์ในคลังข้อมูล Data0.bdt/bhd ข้อความอยู่ในไฟล์ .fmg ภายในแพ็กเกจ .msgbnd.dcx แก้ไขได้ง่ายด้วย WitchyBND หรือ FMG Editor ฟอนต์เชื่อมโยงผ่าน Scaleform GFx",
        "description_en": "FromSoftware's renowned Soulsborne engine. Uses .bdt/.bhd archives with text stored in .fmg files inside .msgbnd.dcx packages.",
        "detection": {
            "root_files": [
                        "eldenring.exe",
                        "darksoulsiii.exe",
                        "sekiro.exe",
                        "armoredcore6.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "msg",
                        "param"
            ],
            "extensions": [
                        ".bdt",
                        ".bhd",
                        ".fmg"
            ],
            "exe_patterns": [
                        "eldenring.exe",
                        "darksoulsiii.exe",
                        "darksoulsii.exe",
                        "darksoulsremastered.exe",
                        "sekiro.exe",
                        "armoredcore6.exe"
            ]
},
    },
    "Dragon Engine": {
        "canonical_name": "Dragon Engine",
        "aliases": [
            "dragon engine",
            "dragon_engine",
            "rgg dragon engine",
            "yakuza dragon engine"
],
        "developer": "Ryu Ga Gotoku Studio / Sega",
        "origin_country": "Japan",
        "category": "Proprietary AAA Action/Adventure",
        "color": "#dc2626",
        "typical_games": [
            "Yakuza 6: The Song of Life",
            "Yakuza: Kiwami 2",
            "Judgment (Judge Eyes)",
            "Lost Judgment",
            "Yakuza: Like a Dragon (Yakuza 7)",
            "Like a Dragon: Infinite Wealth (Yakuza 8)",
            "Like a Dragon Gaiden: The Man Who Erased His Name",
            "Virtua Fighter 5 Ultimate Showdown"
],
        "text_formats": [
            ".par",
            ".bin",
            ".po",
            ".csv"
],
        "font_tech": "TrueType Vector Font / Font Sheet Texture (.gfd / .dds)",
        "recommended_tools": [
            "PAR Tool",
            "Ryu Mod Manager (RMM)",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นยุคใหม่ของสตูดิโอ Ryu Ga Gotoku โดดเด่นด้วยระบบฟิสิกส์สมจริงและกราฟิกแสงไฟนีออนยามค่ำคืน ไฟล์เกมบรรจุในคลัง .par สามารถแกะและแพ็กกลับได้ด้วย PAR Tool และจัดการม็อดผ่าน Ryu Mod Manager",
        "description_en": "RGG Studio's modern flagship engine powering Yakuza 6-8 and Judgment series. Packs assets in .par archives, moddable via Ryu Mod Manager.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".par"
            ],
            "exe_patterns": [
                        "yakuza6.exe",
                        "yakuzakiwami2.exe",
                        "judgment.exe",
                        "lostjudgment.exe",
                        "likeadragon.exe"
            ]
},
    },
    "Old Yakuza Engine": {
        "canonical_name": "Old Yakuza Engine",
        "aliases": [
            "old yakuza engine",
            "rgg old engine",
            "yakuza 0 engine"
],
        "developer": "Ryu Ga Gotoku Studio / Sega",
        "origin_country": "Japan",
        "category": "Proprietary Action (Previous-Gen)",
        "color": "#ef4444",
        "typical_games": [
            "Yakuza 0",
            "Yakuza Kiwami 1",
            "Yakuza 3, 4, 5 Remastered",
            "Fist of the North Star: Lost Paradise"
],
        "text_formats": [
            ".par",
            ".bin"
],
        "font_tech": "Bitmap Font Glyphs in font.par / TrueType",
        "recommended_tools": [
            "PAR Tool",
            "Ryu Mod Manager",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นคลาสสิกของซีรีส์ Yakuza ก่อนยุค Dragon Engine บรรจุไฟล์ใน .par",
        "description_en": "Pre-Dragon Engine era powering Yakuza 0 and Kiwami 1, utilizing .par archives.",
        "detection": {
            "root_files": [
                        "yakuza0.exe",
                        "yakuzakiwami.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "media/data"
            ],
            "extensions": [
                        ".par"
            ],
            "exe_patterns": [
                        "yakuza0.exe",
                        "yakuzakiwami.exe"
            ]
},
    },
    "Luminous Engine": {
        "canonical_name": "Luminous Engine",
        "aliases": [
            "luminous engine",
            "luminous",
            "luminous_engine",
            "luminous productions"
],
        "developer": "Square Enix / Luminous Productions",
        "origin_country": "Japan",
        "category": "Proprietary AAA Open-World Action RPG",
        "color": "#a855f7",
        "typical_games": [
            "Final Fantasy XV (Windows Edition)",
            "Forspoken"
],
        "text_formats": [
            ".earc",
            ".bin",
            ".json"
],
        "font_tech": "Distance Field TrueType / Vector SDF",
        "recommended_tools": [
            "Flagrum",
            "Luminous Tool",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นกราฟิกสุดอลังการของ Square Enix จัดเก็บไฟล์ในแพ็กเกจ .earc มีโปรแกรม Flagrum ที่ทำให้การม็อดข้อความและสกินใน FFXV ทำได้อย่างสะดวก",
        "description_en": "Square Enix's graphical powerhouse engine behind FFXV and Forspoken. Modded using Flagrum tool for .earc packages.",
        "detection": {
            "root_files": [
                        "ffxv.exe",
                        "forspoken.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "datas"
            ],
            "extensions": [
                        ".earc"
            ],
            "exe_patterns": [
                        "ffxv.exe",
                        "forspoken.exe"
            ]
},
    },
    "Crystal Tools": {
        "canonical_name": "Crystal Tools",
        "aliases": [
            "crystal tools",
            "crystal_tools",
            "white engine"
],
        "developer": "Square Enix",
        "origin_country": "Japan",
        "category": "Proprietary AAA RPG (PS3 Era)",
        "color": "#c084fc",
        "typical_games": [
            "Final Fantasy XIII",
            "Final Fantasy XIII-2",
            "Lightning Returns: Final Fantasy XIII",
            "Final Fantasy XIV (1.0 Original)"
],
        "text_formats": [
            ".bin",
            ".win32.bin",
            ".xwb"
],
        "font_tech": "Bitmap Font Glyphs in .win32.bin",
        "recommended_tools": [
            "FF13 Tool",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นสำหรับ Final Fantasy ยุค PS3 เดิมมีชื่อว่า White Engine บรรจุไฟล์เกมใน .bin",
        "description_en": "Square Enix's PS3-generation RPG engine behind the FFXIII trilogy.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "white_data"
            ],
            "extensions": [
                        ".win32.bin"
            ],
            "exe_patterns": [
                        "ffxiiiimg.exe",
                        "ffxiii2img.exe"
            ]
},
    },
    "Katana / Gust": {
        "canonical_name": "Katana / Gust",
        "aliases": [
            "katana / gust",
            "gust engine",
            "gust_engine",
            "katana",
            "gust"
],
        "developer": "Gust / Koei Tecmo",
        "origin_country": "Japan",
        "category": "Proprietary JRPG",
        "color": "#06b6d4",
        "typical_games": [
            "Atelier Ryza 1, 2, 3",
            "Atelier Sophie 1 & 2",
            "Atelier Yumia",
            "Atelier Mysterious Trilogy",
            "Nights of Azure 1 & 2",
            "Blue Reflection & Second Light",
            "Fairy Tail (Gust)"
],
        "text_formats": [
            ".rdb",
            ".fdata",
            ".ebm",
            ".bin"
],
        "font_tech": "TrueType Vector Font / Bitmap Texture Sheets",
        "recommended_tools": [
            "Gust Tools",
            "Gust_Pak",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นประจำค่าย Gust ผู้สร้างซีรีส์ Atelier ปรุงยา จัดเก็บไฟล์ในแพ็กเกจ PACK00_01.DAT หรือ root.rdb ข้อความภาษาถูกจัดระเบียบในตารางไบนารี สามารถสกัดและแปลงเป็นข้อความได้ผ่าน Gust Tools",
        "description_en": "Engine used for the Atelier and Blue Reflection series by Gust. Uses .rdb and PACK files, moddable with Gust Tools.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "data",
                        "motor"
            ],
            "extensions": [
                        ".rdb",
                        ".fdata"
            ],
            "exe_patterns": [
                        "atelier_ryza.exe",
                        "atelier_ryza2.exe",
                        "atelier_ryza3.exe"
            ]
},
    },
    "KT Engine": {
        "canonical_name": "KT Engine",
        "aliases": [
            "kt engine",
            "kt_engine",
            "tecmo_engine",
            "omega_engine",
            "despair engine"
],
        "developer": "Koei Tecmo / Omega Force",
        "origin_country": "Japan",
        "category": "Proprietary Musou / Action",
        "color": "#0284c7",
        "typical_games": [
            "Dynasty Warriors 7, 8, 9",
            "Samurai Warriors 4 & 5",
            "Warriors Orochi 3 & 4 Ultimate",
            "Fate/Samurai Remnant",
            "Persona 5 Strikers",
            "Dragon Quest Heroes 1 & 2",
            "One Piece: Pirate Warriors 3 & 4",
            "Attack on Titan 1 & 2"
],
        "text_formats": [
            ".bin",
            ".idx",
            "linkdata"
],
        "font_tech": "Bitmap Font Glyphs in LINKDATA / TrueType",
        "recommended_tools": [
            "Linkdata Tool",
            "Koei Tecmo Tool",
            "TStudio",
            "TRun"
],
        "complexity": "Medium to High",
        "description_th": "เอนจิ้นเกมฟันแหลกแนว Musou ของ Omega Force บรรจุไฟล์เกมใน LINKDATA.BIN และไฟล์ดัชนี .IDX",
        "description_en": "Koei Tecmo's Musou engine behind Dynasty Warriors and Warriors Orochi. Packages data into LINKDATA.BIN and .IDX tables.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".idx"
            ],
            "exe_patterns": [
                        "dw8.exe",
                        "dw9.exe",
                        "wo4.exe"
            ]
},
    },
    "Team Ninja Engine": {
        "canonical_name": "Team Ninja Engine",
        "aliases": [
            "team ninja engine",
            "team_ninja_engine",
            "team ninja",
            "katana team ninja"
],
        "developer": "Team Ninja / Koei Tecmo",
        "origin_country": "Japan",
        "category": "Proprietary Hardcore Action RPG",
        "color": "#0369a1",
        "typical_games": [
            "Nioh 1: Complete Edition",
            "Nioh 2: Complete Edition",
            "Wo Long: Fallen Dynasty",
            "Stranger of Paradise: Final Fantasy Origin",
            "Ninja Gaiden: Master Collection (Sigma 1, 2, 3 Razor's Edge)",
            "Rise of the Ronin (Ronin Engine)"
],
        "text_formats": [
            ".bin",
            ".cpk",
            ".idx"
],
        "font_tech": "FreeType TrueType / TrueType SDF Font",
        "recommended_tools": [
            "QuickBMS",
            "CriPakTools",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นเกมต่อสู้แอ็กชันดุดันของ Team Ninja โครงสร้างจัดเก็บข้อมูลใช้แพ็กเกจไบนารีความเร็วสูง",
        "description_en": "High-intensity combat engine powering Nioh and Wo Long.",
        "detection": {
            "root_files": [
                        "nioh.exe",
                        "nioh2.exe",
                        "wolong.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".bin"
            ],
            "exe_patterns": [
                        "nioh.exe",
                        "nioh2.exe",
                        "wolong.exe"
            ]
},
    },
    "Falcom Engine": {
        "canonical_name": "Falcom Engine",
        "aliases": [
            "falcom engine",
            "falcomengine",
            "napishtim_engine",
            "falcom",
            "yeti engine"
],
        "developer": "Nihon Falcom",
        "origin_country": "Japan",
        "category": "Proprietary JRPG",
        "color": "#ec4899",
        "typical_games": [
            "The Legend of Heroes: Trails of Cold Steel 1, 2, 3, 4",
            "The Legend of Heroes: Trails from Zero & Trails to Azure",
            "The Legend of Heroes: Trails into Reverie",
            "The Legend of Heroes: Trails through Daybreak (Kuro no Kiseki)",
            "Ys VIII: Lacrimosa of DANA",
            "Ys IX: Monstrum Nox",
            "Ys X: Nordics",
            "Ys: Memories of Celceta",
            "Ys Origin",
            "Ys: The Oath in Felghana"
],
        "text_formats": [
            ".tbl",
            ".dat",
            ".pkg",
            ".t_text",
            ".json"
],
        "font_tech": "Direct TrueType (.ttf/.otf) mapped in ED8 font tables / SenPatcher",
        "recommended_tools": [
            "SenPatcher",
            "ED8 Decompiler",
            "Falcom TBL Tool",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นประจำค่าย Nihon Falcom ผู้สร้างตำนาน Trails (Kiseki) และ Ys ในเกมยุค Cold Steel และ Daybreak มีการจัดเก็บข้อความในตาราง .tbl และแพ็กเกจ .pkg รองรับฟอนต์ TTF ภาษาไทยได้สมบูรณ์แบบด้วย SenPatcher",
        "description_en": "Nihon Falcom's engine behind Trails and Ys series. Text resides in .tbl tables and .pkg archives, with full TTF support via SenPatcher.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "data/text",
                        "text"
            ],
            "extensions": [
                        ".tbl",
                        ".pkg"
            ],
            "exe_patterns": [
                        "ed8.exe",
                        "ed8_2.exe",
                        "ed8_3.exe",
                        "ed8_4.exe",
                        "ys8.exe",
                        "ys9.exe"
            ]
},
    },
    "PlatinumGames": {
        "canonical_name": "PlatinumGames",
        "aliases": [
            "platinumgames",
            "platinumgames engine",
            "platinumgames_engine"
],
        "developer": "PlatinumGames",
        "origin_country": "Japan",
        "category": "Proprietary High-Speed Action",
        "color": "#64748b",
        "typical_games": [
            "NieR: Automata",
            "Bayonetta 1, 2, 3",
            "Metal Gear Rising: Revengeance",
            "Astral Chain",
            "Vanquish",
            "The Wonderful 101: Remastered"
],
        "text_formats": [
            ".dat",
            ".dtt",
            ".cpk",
            ".wta",
            ".wtp"
],
        "font_tech": "Direct TrueType Font / Texture Bitmap Font in .dat",
        "recommended_tools": [
            "DAT Tool",
            "CriPakTools",
            "NieR Mod Tool",
            "TStudio",
            "TRun"
],
        "complexity": "Medium to High",
        "description_th": "เอนจิ้นแอ็กชันความเร็ว 60fps อันลือชื่อ ไฟล์เกมบรรจุในแพ็กเกจ .dat และ .dtt ข้อความใน NieR: Automata ถูกบีบอัดในไฟล์แพ็กเกจ มีเครื่องมือ DAT Tool ช่วยแกะและแพ็กกลับได้",
        "description_en": "High-octane action engine behind NieR: Automata and Bayonetta, using .dat and .dtt containers.",
        "detection": {
            "root_files": [
                        "nierautomata.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".dat",
                        ".dtt"
            ],
            "exe_patterns": [
                        "nierautomata.exe",
                        "metalgearrising.exe",
                        "bayonetta.exe"
            ]
},
    },
    "FOX Engine": {
        "canonical_name": "FOX Engine",
        "aliases": [
            "fox engine",
            "fox",
            "fox_engine",
            "kojima fox engine"
],
        "developer": "Kojima Productions / Konami",
        "origin_country": "Japan",
        "category": "Proprietary AAA Photorealistic Stealth/Action",
        "color": "#eab308",
        "typical_games": [
            "Metal Gear Solid V: The Phantom Pain",
            "Metal Gear Solid V: Ground Zeroes",
            "P.T. (Playable Teaser)",
            "eFootball PES 2014 through PES 2021",
            "Metal Gear Survive"
],
        "text_formats": [
            ".dat",
            ".fpk",
            ".fpkd",
            ".lng"
],
        "font_tech": "Vector SDF Font Sheets / Scaleform GFx",
        "recommended_tools": [
            "GzsTool",
            "FtexTool",
            "TStudio",
            "TRun"
],
        "complexity": "Medium to High",
        "description_th": "เอนจิ้นชิ้นเอกของ Hideo Kojima ก่อนแยกตัวจาก Konami โดดเด่นด้านระบบฟิสิกส์ การจัดแสงเสมือนจริง และการเรนเดอร์ระดับสูง บรรจุไฟล์เกมใน .dat และ .fpk สามารถแตกไฟล์ด้วย GzsTool",
        "description_en": "Hideo Kojima's masterpiece engine featuring stunning lighting and physics in MGSV, modded using GzsTool.",
        "detection": {
            "root_files": [
                        "mgsvtpp.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "master"
            ],
            "extensions": [
                        ".dat",
                        ".fpk"
            ],
            "exe_patterns": [
                        "mgsvtpp.exe",
                        "mgsvgz.exe",
                        "pes2021.exe"
            ]
},
    },
    "Asura Engine": {
        "canonical_name": "Asura Engine",
        "aliases": [
            "asura engine",
            "asura",
            "asura_engine"
],
        "developer": "Rebellion Developments",
        "origin_country": "UK",
        "category": "Proprietary AAA Tactical Stealth/Action",
        "color": "#14b8a6",
        "typical_games": [
            "Sniper Elite 3",
            "Sniper Elite 4",
            "Sniper Elite 5",
            "Zombie Army Trilogy",
            "Zombie Army 4: Dead War",
            "Evil Genius 2: World Domination",
            "Strange Brigade",
            "Aliens vs. Predator (2010)",
            "Rogue Trooper Redux"
],
        "text_formats": [
            ".asr",
            ".asr_en",
            ".pc_en",
            ".zip"
],
        "font_tech": "Compressed Font Glyph Archive (.asr.zip / .asr) / TrueType",
        "recommended_tools": [
            "Asura Extractor",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นประจำค่าย Rebellion ผู้สร้างซีรีส์ Sniper Elite และ Zombie Army ไฟล์เกมทั้งหมดถูกบรรจุเป็นคลัง .asr และ .asr_en ข้อความอยู่ในสตรีมไบนารี สามารถสกัดและแพ็กกลับได้ด้วย Asura Extractor",
        "description_en": "Rebellion's proprietary engine powering Sniper Elite and Zombie Army series, utilizing .asr and .asr_en packages.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".asr",
                        ".asr_en"
            ],
            "exe_patterns": [
                        "sniperelite4.exe",
                        "sniperelite5.exe",
                        "za4.exe"
            ]
},
    },
    "Foundation Engine": {
        "canonical_name": "Foundation Engine",
        "aliases": [
            "foundation engine",
            "cdc engine",
            "cdc",
            "crystal dynamics foundation engine",
            "crystal_dynamics_engine"
],
        "developer": "Crystal Dynamics / Eidos",
        "origin_country": "USA",
        "category": "Proprietary AAA Cinematic Action/Adventure",
        "color": "#6366f1",
        "typical_games": [
            "Tomb Raider (2013)",
            "Rise of the Tomb Raider (2015)",
            "Shadow of the Tomb Raider (2018)",
            "Deus Ex: Human Revolution",
            "Marvel's Avengers"
],
        "text_formats": [
            "bigfile.000",
            "bigfile.update.000",
            ".bin",
            ".pak"
],
        "font_tech": "Scaleform GFx / Texture Glyph Atlases / Distance Field Font",
        "recommended_tools": [
            "Gibbed Tomb Raider Tools",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นภาพยนตร์ผจญภัยของ Tomb Raider ยุค Reboot บรรจุไฟล์เกมทั้งหมดในไฟล์ขนาดใหญ่ bigfile.000 และ bigfile.update.xxx จัดการและแตกไฟล์ด้วยเครื่องมือ Gibbed Tools",
        "description_en": "Crystal Dynamics' engine powering the modern Tomb Raider reboot trilogy. Encapsulates assets inside bigfile.000 packages.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".bin"
            ],
            "exe_patterns": [
                        "tombraider.exe",
                        "rottr.exe",
                        "sottr.exe",
                        "dxhr.exe"
            ]
},
    },
    "Dawn Engine": {
        "canonical_name": "Dawn Engine",
        "aliases": [
            "dawn engine",
            "dawn",
            "dawn_engine"
],
        "developer": "Eidos-Montréal",
        "origin_country": "Canada",
        "category": "Proprietary AAA Immersive Cyberpunk RPG",
        "color": "#f59e0b",
        "typical_games": [
            "Deus Ex: Mankind Divided"
],
        "text_formats": [
            ".dat",
            ".bin",
            ".archive"
],
        "font_tech": "Vector SDF Font Asset / DirectDraw",
        "recommended_tools": [
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นที่ต่อยอดมาจาก Glacier 2 เพื่อสร้างโลกไซเบอร์พังก์อันละเอียดอ่อนใน Deus Ex: Mankind Divided",
        "description_en": "Eidos-Montreal's tailored engine evolved from Glacier 2 for Deus Ex: Mankind Divided.",
        "detection": {
            "root_files": [
                        "dxmd.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".dat"
            ],
            "exe_patterns": [
                        "dxmd.exe"
            ]
},
    },
    "Glacier Engine": {
        "canonical_name": "Glacier Engine",
        "aliases": [
            "glacier engine",
            "glacier",
            "glacier_engine",
            "glacier 2",
            "glacier_2"
],
        "developer": "IO Interactive",
        "origin_country": "Denmark",
        "category": "Proprietary AAA Stealth/Action",
        "color": "#0284c7",
        "typical_games": [
            "Hitman: World of Assassination (Hitman 1, 2, 3)",
            "Hitman: Absolution",
            "Kane & Lynch: Dead Men / Dog Days",
            "Freedom Fighters",
            "Project 007 (Upcoming)"
],
        "text_formats": [
            ".rpkg",
            ".locr",
            ".json"
],
        "font_tech": "Signed Distance Field (SDF) Font in RPKG / Vector TrueType",
        "recommended_tools": [
            "RPKG Tool",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "Medium to High",
        "description_th": "เอนจิ้นจำลองฝูงชน AI และระบบลอบเร้นระดับโลกของ IO Interactive บรรจุไฟล์เกมใน .rpkg ข้อความภาษาอยู่ในไฟล์ .locr สามารถแกะ แปล และแพ็กกลับได้อย่างแม่นยำด้วย RPKG Tool",
        "description_en": "IO Interactive's sophisticated crowd AI engine for the Hitman World of Assassination. Data packaged in .rpkg with .locr string databases.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "runtime"
            ],
            "extensions": [
                        ".rpkg"
            ],
            "exe_patterns": [
                        "hitman.exe",
                        "hitman2.exe",
                        "hitman3.exe"
            ]
},
    },
    "Frostbite": {
        "canonical_name": "Frostbite",
        "aliases": [
            "frostbite",
            "frostbite 2",
            "frostbite 3",
            "frostbite engine"
],
        "developer": "EA DICE",
        "origin_country": "Sweden",
        "category": "Proprietary AAA Dynamic 3D",
        "color": "#fb923c",
        "typical_games": [
            "Battlefield (All: 3, 4, 1, V, 2042, Bad Company 2)",
            "Dead Space Remake (2023)",
            "Dragon Age: Inquisition",
            "Dragon Age: The Veilguard",
            "Mass Effect: Andromeda",
            "Need for Speed (Heat, Unbound, Rivals)",
            "Star Wars Battlefront 1 & 2",
            "Star Wars: Squadrons",
            "EA Sports FC (FIFA series)",
            "Mirror's Edge Catalyst"
],
        "text_formats": [
            ".cas",
            ".toc",
            ".res",
            ".sb"
],
        "font_tech": "Distance Field TrueType / TrueType vector embedded in initfs_win32",
        "recommended_tools": [
            "Frosty Toolsuite (Frosty Editor / Mod Manager)",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นกราฟิกระดับพระกาฬของ EA DICE โดดเด่นเรื่องการทำลายสิ่งแวดล้อม ไฟล์เกมจัดเก็บในระบบ .cas และ .toc แก้ไขและสร้างม็อดผ่าน Frosty Editor",
        "description_en": "EA DICE's visual powerhouse featuring destructible environments. Modded via the Frosty Toolsuite for .cas/.toc databases.",
        "detection": {
            "root_files": [
                        "initfs_win32"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "data/win32"
            ],
            "extensions": [
                        ".cas",
                        ".toc"
            ],
            "exe_patterns": [
                        "bf4.exe",
                        "bf1.exe",
                        "bf2042.exe",
                        "deadspace.exe",
                        "dai.exe"
            ]
},
    },
    "Visceral Engine": {
        "canonical_name": "Visceral Engine",
        "aliases": [
            "visceral engine",
            "visceral",
            "visceral_engine",
            "godfather engine"
],
        "developer": "Visceral Games / EA",
        "origin_country": "USA",
        "category": "Proprietary Survival Horror / Action",
        "color": "#991b1b",
        "typical_games": [
            "Dead Space (2008 Original)",
            "Dead Space 2",
            "Dead Space 3",
            "Dante's Inferno",
            "The Godfather 1 & 2",
            "The Simpsons Game"
],
        "text_formats": [
            ".str",
            ".big",
            ".dat",
            ".bin"
],
        "font_tech": "Texture Glyph Atlas / TrueType",
        "recommended_tools": [
            "Gibbed Dead Space Tools",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นอวกาศสยองขวัญของ Dead Space ไตรภาคดั้งเดิม บรรจุไฟล์เกมใน .str และ .big",
        "description_en": "Visceral Games' survival horror engine behind the original Dead Space trilogy.",
        "detection": {
            "root_files": [
                        "deadspace.exe",
                        "deadspace2.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".str",
                        ".big"
            ],
            "exe_patterns": [
                        "deadspace.exe",
                        "deadspace2.exe",
                        "deadspace3.exe"
            ]
},
    },
    "Aurora Engine": {
        "canonical_name": "Aurora Engine",
        "aliases": [
            "aurora engine",
            "aurora",
            "aurora_engine"
],
        "developer": "BioWare",
        "origin_country": "Canada",
        "category": "Classic 3D RPG",
        "color": "#f97316",
        "typical_games": [
            "The Witcher: Enhanced Edition (Witcher 1)",
            "Neverwinter Nights (Original & Enhanced Edition)"
],
        "text_formats": [
            ".tlk",
            ".bif",
            ".key",
            ".erf"
],
        "font_tech": "TrueType Font / Bitmap Texture Sheets in bif",
        "recommended_tools": [
            "TLK Editor",
            "Kotor Tool",
            "NWN Explorer",
            "TStudio",
            "TRun"
],
        "complexity": "Easy to Medium",
        "description_th": "เอนจิ้น RPG คลาสสิกของ BioWare ข้อความทั้งหมดจัดเก็บในไฟล์ตารางข้อความ dialog.tlk และคลังข้อมูล .bif มีเครื่องมือ TLK Editor แก้ไขภาษาไทยได้อย่างตรงไปตรงมา",
        "description_en": "BioWare's classic RPG engine. All dialog strings reside in dialog.tlk, easily modified via TLK Editor.",
        "detection": {
            "root_files": [
                        "dialog.tlk",
                        "chitin.key"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".tlk",
                        ".bif"
            ],
            "exe_patterns": [
                        "witcher.exe",
                        "nwmain.exe"
            ]
},
    },
    "Odyssey Engine": {
        "canonical_name": "Odyssey Engine",
        "aliases": [
            "odyssey engine",
            "odyssey",
            "odyssey_engine"
],
        "developer": "BioWare",
        "origin_country": "Canada",
        "category": "Classic 3D RPG",
        "color": "#ea580c",
        "typical_games": [
            "Star Wars: Knights of the Old Republic (KOTOR)",
            "Star Wars: Knights of the Old Republic II - The Sith Lords"
],
        "text_formats": [
            ".tlk",
            ".bif",
            ".rim",
            ".erf"
],
        "font_tech": "TXI / TGA Font Texture Glyphs (fnt_*.tga)",
        "recommended_tools": [
            "Kotor Tool",
            "TLK Editor",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นตระกูล Aurora ที่พัฒนาต่อเพื่อจักรวาล Star Wars ข้อความอยู่ใน dialog.tlk และฟอนต์เป็นไฟล์เท็กซ์เจอร์ TGA พร้อมเมตริก TXI",
        "description_en": "BioWare's Aurora-derived Star Wars engine. Uses dialog.tlk and TGA/TXI font texture pairs.",
        "detection": {
            "root_files": [
                        "chitin.key",
                        "dialog.tlk"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "override"
            ],
            "extensions": [
                        ".tlk",
                        ".rim"
            ],
            "exe_patterns": [
                        "swkotor.exe",
                        "swkotor2.exe"
            ]
},
    },
    "Eclipse Engine": {
        "canonical_name": "Eclipse Engine",
        "aliases": [
            "eclipse engine",
            "eclipse",
            "eclipse_engine"
],
        "developer": "BioWare",
        "origin_country": "Canada",
        "category": "Proprietary 3D RPG",
        "color": "#c2410c",
        "typical_games": [
            "Dragon Age: Origins",
            "Dragon Age II"
],
        "text_formats": [
            ".erf",
            ".gda",
            ".tlk"
],
        "font_tech": "Scaleform GFx Flash Fonts / TrueType",
        "recommended_tools": [
            "DA Toolset",
            "gdapp",
            "talkhelper",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นสร้างชื่อของซีรีส์ Dragon Age ยุคคลาสสิก บรรจุไฟล์ใน .erf และข้อความอยู่ในตาราง .tlk และ .gda",
        "description_en": "BioWare's engine for Dragon Age: Origins and DA2. Uses .erf packages and .tlk string tables.",
        "detection": {
            "root_files": [
                        "daorigins.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "packages/core"
            ],
            "extensions": [
                        ".erf",
                        ".gda"
            ],
            "exe_patterns": [
                        "daorigins.exe",
                        "dragonage2.exe"
            ]
},
    },
    "Infinity Engine": {
        "canonical_name": "Infinity Engine",
        "aliases": [
            "infinity engine",
            "infinity",
            "infinity_engine"
],
        "developer": "BioWare / Black Isle Studios",
        "origin_country": "Canada",
        "category": "Retro Isometric 2D RPG",
        "color": "#9a3412",
        "typical_games": [
            "Baldur's Gate 1 & 2 (Original & Enhanced Edition)",
            "Icewind Dale 1 & 2",
            "Planescape: Torment"
],
        "text_formats": [
            ".tlk",
            ".bif",
            ".key"
],
        "font_tech": "BAM Font Glyphs / TrueType in EE editions",
        "recommended_tools": [
            "NearInfinity",
            "WeiDU",
            "TStudio"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นไอโซเมตริก RPG คลาสสิกยอดเยี่ยมตลอดกาล ข้อความอยู่ใน dialog.tlk รองรับม็อดภาษาไทยอย่างดีในเวอร์ชัน Enhanced Edition",
        "description_en": "Classic isometric D&D engine. Uses dialog.tlk with robust WeiDU modding community.",
        "detection": {
            "root_files": [
                        "chitin.key",
                        "dialog.tlk"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".tlk"
            ],
            "exe_patterns": [
                        "baldur.exe",
                        "bg2main.exe",
                        "torment.exe"
            ]
},
    },
    "Divinity Engine": {
        "canonical_name": "Divinity Engine",
        "aliases": [
            "divinity engine",
            "divinityengine",
            "divinity",
            "larian engine",
            "divinity 4.0"
],
        "developer": "Larian Studios",
        "origin_country": "Belgium",
        "category": "Proprietary AAA Isometric/Cinematic RPG",
        "color": "#d97706",
        "typical_games": [
            "Baldur's Gate 3",
            "Divinity: Original Sin 1 & Enhanced Edition",
            "Divinity: Original Sin 2 & Definitive Edition",
            "Divinity II: Developer's Cut"
],
        "text_formats": [
            ".pak",
            ".loca",
            ".xml",
            ".lsf",
            ".lsx"
],
        "font_tech": "TrueType Vector Font / OTF embedded in Virtual Textures",
        "recommended_tools": [
            "LSLib (Divine Tool)",
            "BG3 Mod Manager",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นยอดเยี่ยมแห่งยุคของ Baldur's Gate 3 บรรจุเนื้อหาในแพ็กเกจ .pak สามารถแกะและสร้างใหม่ด้วย LSLib (Divine Tool) ข้อความภาษาถูกจัดระเบียบในไฟล์ .loca / .xml มีระบบรองรับม็อดในเกมอย่างเป็นทางการ",
        "description_en": "Larian's award-winning RPG engine behind Baldur's Gate 3. Packages data in .pak archives with .loca localization tables, moddable with LSLib.",
        "detection": {
            "root_files": [
                        "bg3.exe",
                        "bg3_dx11.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "data/localization"
            ],
            "extensions": [
                        ".pak",
                        ".loca"
            ],
            "exe_patterns": [
                        "bg3.exe",
                        "bg3_dx11.exe",
                        "eocapp.exe"
            ]
},
    },
    "Clausewitz Engine": {
        "canonical_name": "Clausewitz Engine",
        "aliases": [
            "clausewitz engine",
            "clausewitz",
            "jomini",
            "paradox_custom",
            "paradox clausewitz"
],
        "developer": "Paradox Interactive",
        "origin_country": "Sweden",
        "category": "Proprietary Grand Strategy",
        "color": "#0284c7",
        "typical_games": [
            "Crusader Kings III & II",
            "Hearts of Iron IV",
            "Stellaris",
            "Europa Universalis IV",
            "Victoria 3",
            "Imperator: Rome",
            "Age of Wonders 4 (Triumph)"
],
        "text_formats": [
            ".yml",
            ".csv",
            ".txt",
            ".gui"
],
        "font_tech": "OpenType / TrueType (.otf/.ttf) defined in gui/fonts.gui",
        "recommended_tools": [
            "VS Code",
            "Paradox Launcher",
            "TStudio",
            "TRun"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นสำหรับเกมวางแผนมหภาคอันดับ 1 ของโลก ข้อความและภาษาอยู่ในไฟล์ข้อความ YAML (.yml) รูปแบบ UTF-8 with BOM ฟอนต์กำหนดค่าผ่านไฟล์ gui/fonts.gui ใส่ฟอนต์ไทย TTF ได้สะดวกง่ายดาย",
        "description_en": "Paradox's grand strategy engine. Localization is plain-text UTF-8-BOM YAML (.yml), making Thai translation and font modding very accessible.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "game/localization",
                        "localization"
            ],
            "extensions": [
                        ".yml",
                        ".gui"
            ],
            "exe_patterns": [
                        "ck3.exe",
                        "hoi4.exe",
                        "stellaris.exe",
                        "eu4.exe",
                        "victoria3.exe"
            ]
},
    },
    "Apex Engine": {
        "canonical_name": "Apex Engine",
        "aliases": [
            "apex engine",
            "apex",
            "apex_engine",
            "avalanche_engine",
            "avalanche engine"
],
        "developer": "Avalanche Studios",
        "origin_country": "Sweden",
        "category": "Proprietary AAA Open-World Action",
        "color": "#ea580c",
        "typical_games": [
            "Just Cause 2, 3, 4",
            "Mad Max (2015)",
            "Generation Zero",
            "theHunter: Call of the Wild",
            "Rage 2 (co-developed with id Software)",
            "Contraband"
],
        "text_formats": [
            ".tab",
            ".arc",
            ".bin"
],
        "font_tech": "Texture Glyph Atlas / Distance Field Font",
        "recommended_tools": [
            "Gibbed Avalanche Tools",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "Medium to High",
        "description_th": "เอนจิ้นระเบิดภูเขาเผากระท่อมโลกเปิดของ Just Cause และ Mad Max ไฟล์เกมบรรจุในแพ็กเกจ .tab และ .arc แก้ไขได้ด้วย Gibbed Avalanche Tools",
        "description_en": "Open world destruction engine powering Just Cause and Mad Max. Uses .tab/.arc container archives.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "archives_win64"
            ],
            "extensions": [
                        ".tab",
                        ".arc"
            ],
            "exe_patterns": [
                        "justcause3.exe",
                        "justcause4.exe",
                        "madmax.exe",
                        "generationzero.exe"
            ]
},
    },
    "Saber Engine": {
        "canonical_name": "Saber Engine",
        "aliases": [
            "saber engine",
            "saber",
            "swarm engine",
            "saber swarm"
],
        "developer": "Saber Interactive",
        "origin_country": "USA",
        "category": "Proprietary AAA Swarm/Physics",
        "color": "#059669",
        "typical_games": [
            "Warhammer 40,000: Space Marine 2",
            "World War Z & Aftermath",
            "SnowRunner",
            "MudRunner",
            "Expeditions: A MudRunner Game",
            "Halo: Combat Evolved Anniversary (Campaign)",
            "Halo 2: Anniversary"
],
        "text_formats": [
            ".pak",
            ".pct",
            ".xml",
            ".json"
],
        "font_tech": "TrueType Vector Font / Swarm UI",
        "recommended_tools": [
            "QuickBMS",
            "SnowRunner Editor",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นที่เก่งกาจด้านการจำลองฝูงศัตรูนับพันตัว (Swarm) และระบบฟิสิกส์โคลนน้ำสมจริง ใน Space Marine 2 และ SnowRunner ไฟล์ถูกบีบอัดใน .pak",
        "description_en": "Proprietary swarm AI and terrain deformation engine behind Space Marine 2 and SnowRunner.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "client/packaged",
                        "en_us"
            ],
            "extensions": [
                        ".pak",
                        ".pct"
            ],
            "exe_patterns": [
                        "spacemarine2.exe",
                        "snowrunner.exe",
                        "wwz.exe"
            ]
},
    },
    "Asobo Engine": {
        "canonical_name": "Asobo Engine",
        "aliases": [
            "asobo engine",
            "asobo",
            "asobo_engine",
            "silas engine"
],
        "developer": "Asobo Studio",
        "origin_country": "France",
        "category": "Proprietary AAA Cinematic/Flight Sim",
        "color": "#0284c7",
        "typical_games": [
            "A Plague Tale: Innocence",
            "A Plague Tale: Requiem",
            "Microsoft Flight Simulator (2020 & 2024)"
],
        "text_formats": [
            ".bin",
            ".pck",
            ".fsarchive"
],
        "font_tech": "Direct TrueType / OTF Font Asset with high-DPI scaling",
        "recommended_tools": [
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นที่มีคุณภาพกราฟิกและระบบจำลองฝูงหนูอันน่าทึ่งใน A Plague Tale และระบบโลกเสมือนจริงใน MSFS",
        "description_en": "Asobo's in-house engine for A Plague Tale and Microsoft Flight Simulator.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".bin"
            ],
            "exe_patterns": [
                        "aplaguetaleinnocence.exe",
                        "aplaguetalerequiem.exe",
                        "flightsimulator.exe"
            ]
},
    },
    "Crate Engine": {
        "canonical_name": "Crate Engine",
        "aliases": [
            "crate engine",
            "crate",
            "crate_engine"
],
        "developer": "Crate Entertainment",
        "origin_country": "USA",
        "category": "Proprietary ARPG (Iron Lore Titan Quest evolution)",
        "color": "#d97706",
        "typical_games": [
            "Grim Dawn & Expansions (Ashes of Malmouth, Forgotten Gods, Fangs of Asterkarn)",
            "Titan Quest (Original Iron Lore engine)"
],
        "text_formats": [
            ".arz",
            ".arc",
            ".txt"
],
        "font_tech": "Direct TrueType Font mapped in font replacement files",
        "recommended_tools": [
            "ARC Tool",
            "Grim Dawn Asset Manager",
            "TStudio",
            "TRun"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นสร้างสรรค์ Grim Dawn ต่อยอดมาจาก Titan Quest ไฟล์เกมถูกบีบอัดใน .arc และฐานข้อมูล .arz ข้อความอยู่ในไฟล์ .txt ในคลัง ZIP ภาษา รองรับภาษาไทยได้ง่ายดาย",
        "description_en": "Iron Lore engine evolution for Grim Dawn. Text resides in simple text files inside language archives, easily modded.",
        "detection": {
            "root_files": [
                        "database.arz",
                        "grim dawn.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "resources"
            ],
            "extensions": [
                        ".arz",
                        ".arc"
            ],
            "exe_patterns": [
                        "grim dawn.exe"
            ]
},
    },
    "10tons Engine": {
        "canonical_name": "10tons Engine",
        "aliases": [
            "10tons engine",
            "10tons",
            "10tons_engine"
],
        "developer": "10tons Ltd",
        "origin_country": "Finland",
        "category": "Proprietary 2D/3D Indie",
        "color": "#10b981",
        "typical_games": [
            "DYSMANTLE",
            "Tesla vs Lovecraft",
            "Undead Horde 1 & 2",
            "JYDGE",
            "Neon Chrome",
            "Crimsonland"
],
        "text_formats": [
            ".pak",
            ".csv",
            ".json"
],
        "font_tech": "Embedded TrueType / Custom font atlas",
        "recommended_tools": [
            "QuickBMS",
            "10tons Extractor",
            "TStudio",
            "TRun"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นสร้างเกมแนวเอาชีวิตรอดและ Twin-stick shooter ของ 10tons ไฟล์เกมจัดเก็บใน .pak ข้อความจัดเก็บเป็นตาราง CSV หรือ JSON",
        "description_en": "Proprietary lightweight engine powering DYSMANTLE and Tesla vs Lovecraft, packaging CSV/JSON into .pak archives.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".pak"
            ],
            "exe_patterns": [
                        "dysmantle.exe",
                        "teslavslovecraft.exe"
            ]
},
    },
    "FLEDGE Engine": {
        "canonical_name": "FLEDGE Engine",
        "aliases": [
            "fledge engine",
            "fledge",
            "fledge_engine"
],
        "developer": "Deck13",
        "origin_country": "Germany",
        "category": "Proprietary Action RPG",
        "color": "#f59e0b",
        "typical_games": [
            "The Surge 1",
            "The Surge 2",
            "Atlas Fallen",
            "Lords of the Fallen (2014)"
],
        "text_formats": [
            ".ff",
            ".bin"
],
        "font_tech": "TrueType Vector SDF / DirectDraw",
        "recommended_tools": [
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นของค่าย Deck13 จากเยอรมนี โดดเด่นด้านระบบฟิสิกส์การตัดชิ้นส่วนในซีรีส์ The Surge",
        "description_en": "Deck13's proprietary action RPG engine for The Surge and Atlas Fallen.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".ff"
            ],
            "exe_patterns": [
                        "thesurge.exe",
                        "thesurge2.exe",
                        "atlasfallen.exe"
            ]
},
    },
    "Genome Engine": {
        "canonical_name": "Genome Engine",
        "aliases": [
            "genome engine",
            "genome",
            "genome_engine"
],
        "developer": "Piranha Bytes",
        "origin_country": "Germany",
        "category": "Proprietary Action RPG",
        "color": "#65a30d",
        "typical_games": [
            "ELEX 1 & 2",
            "Risen 1, 2, 3",
            "Gothic 3"
],
        "text_formats": [
            ".pak",
            ".hdr",
            ".csv"
],
        "font_tech": "FNT Bitmap Font / TrueType",
        "recommended_tools": [
            "ELEX Resource Manager",
            "Risen Tool",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นสวมบทบาทโลกเปิดที่มีเอกลักษณ์เฉพาะตัวสูงของ Piranha Bytes บรรจุไฟล์ใน .pak",
        "description_en": "Piranha Bytes' open world RPG engine powering Gothic 3, Risen, and ELEX.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "data/ini"
            ],
            "extensions": [
                        ".pak"
            ],
            "exe_patterns": [
                        "elex.exe",
                        "elex2.exe",
                        "risen.exe"
            ]
},
    },
    "Essence Engine": {
        "canonical_name": "Essence Engine",
        "aliases": [
            "essence engine",
            "essence",
            "essence_engine",
            "essence 5"
],
        "developer": "Relic Entertainment",
        "origin_country": "Canada",
        "category": "Proprietary AAA Real-Time Strategy",
        "color": "#2563eb",
        "typical_games": [
            "Company of Heroes 1, 2, 3",
            "Warhammer 40,000: Dawn of War 1, 2, 3",
            "Age of Empires IV"
],
        "text_formats": [
            ".sga",
            ".ucs",
            ".txt"
],
        "font_tech": "TrueType Vector / Scaleform GFx",
        "recommended_tools": [
            "SGA Reader",
            "Relic Modding Tool",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นเกม RTS แนวหน้าของโลก บรรจุไฟล์เกมในคลัง .sga ข้อความภาษาอยู่ในไฟล์ข้อความ .ucs (Unicode String)",
        "description_en": "Relic's premier strategy engine for Company of Heroes and AoE4. Uses .sga archives and .ucs string files.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".sga",
                        ".ucs"
            ],
            "exe_patterns": [
                        "reliccoh.exe",
                        "reliccoh2.exe",
                        "coh3.exe",
                        "relicdow2.exe",
                        "relcardinal.exe"
            ]
},
    },
    "RenPy": {
        "canonical_name": "RenPy",
        "aliases": [
            "renpy",
            "ren'py",
            "ren_py"
],
        "developer": "PyTom / Ren'Py Community",
        "origin_country": "USA",
        "category": "Visual Novel Open-Source",
        "color": "#f472b6",
        "typical_games": [
            "Doki Doki Literature Club! (DDLC)",
            "Slay the Princess",
            "Katawa Shoujo",
            "Being a DIK",
            "Scarlet Hollow",
            "Needy Streamer Overload (partly)"
],
        "text_formats": [
            ".rpa",
            ".rpy",
            ".rpyc"
],
        "font_tech": "Native TrueType / OpenType (.ttf/.otf) with custom word-wrap and full Thai Unicode support",
        "recommended_tools": [
            "UnRPA",
            "rpyc decrypter",
            "TStudio",
            "TRun"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นนิยายภาพ (Visual Novel) ยอดนิยมอันดับ 1 ของโลก ไฟล์รวมในแพ็กเกจ .rpa สคริปต์ภาษา Python/RenPy (.rpy) มีระบบ Localization ในตัว รองรับฟอนต์ TTF ภาษาไทยได้ง่ายที่สุดในบรรดาทุกเอนจิ้น",
        "description_en": "World-leading visual novel engine using Python and .rpa packages. Features built-in translation system and flawless TrueType Thai font support.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "game",
                        "renpy"
            ],
            "extensions": [
                        ".rpa",
                        ".rpy",
                        ".rpyc"
            ],
            "exe_patterns": []
},
    },
    "RPG Maker": {
        "canonical_name": "RPG Maker",
        "aliases": [
            "rpg maker",
            "rpgmaker",
            "rpg maker mv",
            "rpg maker mz",
            "rpg maker vx ace",
            "rpg maker xp"
],
        "developer": "Gotcha Gotcha Games / Enterbrain",
        "origin_country": "Japan",
        "category": "2D JRPG Creation Software",
        "color": "#10b981",
        "typical_games": [
            "OMORI (RPG Maker MV)",
            "To the Moon (RPG Maker XP)",
            "Fear & Hunger 1 & 2 (RPG Maker MV)",
            "LISA: The Painful (VX Ace)",
            "Ib (Original)",
            "The Witch's House",
            "Mad Father (Original)",
            "Pocket Mirror",
            "Corpse Party (Original)",
            "Space Funeral"
],
        "text_formats": [
            ".json",
            ".rvdata2",
            ".rxdata",
            ".rgssad"
],
        "font_tech": "Canvas Web Font (MV/MZ) / TrueType Embedded in Game.ini (XP/VX/VX Ace)",
        "recommended_tools": [
            "RPG Maker Decrypter",
            "RPGMakerMV-Extract",
            "TStudio",
            "TRun"
],
        "complexity": "Easy",
        "description_th": "เครื่องมือสร้างเกม RPG สไตล์ญี่ปุ่น 16-bit ที่ได้รับความนิยมสูงสุด รุ่นใหม่ (MV, MZ) ใช้ JavaScript และ HTML5 ข้อความอยู่ในไฟล์ .json ในโฟลเดอร์ data รุ่นเก่า (XP, VX Ace) ใช้ Ruby RGSS",
        "description_en": "Iconic JRPG creation engine. Modern versions (MV/MZ) store text in JSON, older versions (XP/VX Ace) in Ruby data files.",
        "detection": {
            "root_files": [
                        "game.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "data",
                        "js/plugins",
                        "www/data"
            ],
            "extensions": [
                        ".rgssad",
                        ".rvdata2",
                        ".rxdata"
            ],
            "exe_patterns": [
                        "game.exe"
            ]
},
    },
    "Wolf RPG Editor": {
        "canonical_name": "Wolf RPG Editor",
        "aliases": [
            "wolf rpg",
            "wolf rpg editor",
            "wolfrpg"
],
        "developer": "SmokingWOLF",
        "origin_country": "Japan",
        "category": "2D Indie RPG/Adventure",
        "color": "#34d399",
        "typical_games": [
            "Mad Father (Remake)",
            "Misao",
            "The Witch's House MV",
            "LiEat",
            "1BitHeart"
],
        "text_formats": [
            ".wolf",
            ".dat"
],
        "font_tech": "Windows GDI TrueType / Font mapped in Game.dat",
        "recommended_tools": [
            "Wolf Decryptor",
            "WolfTrans",
            "TStudio"
],
        "complexity": "Medium",
        "description_th": "โปรแกรมสร้างเกมอินดี้สยองขวัญและผจญภัยชื่อดังจากญี่ปุ่น ข้อความถูกเข้ารหัสในไฟล์แพ็กเกจ .wolf แตกไฟล์ด้วย Wolf Decryptor หรือ WolfTrans",
        "description_en": "Popular Japanese indie adventure engine powering Mad Father and Misao. Encrypted inside .wolf archives.",
        "detection": {
            "root_files": [
                        "game.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "data/basicdata"
            ],
            "extensions": [
                        ".wolf"
            ],
            "exe_patterns": [
                        "game.exe"
            ]
},
    },
    "Kirikiri": {
        "canonical_name": "Kirikiri",
        "aliases": [
            "kirikiri",
            "kirikiri2",
            "kirikiri z",
            "krkr",
            "tvp"
],
        "developer": "WXP / Kazuki Ohta",
        "origin_country": "Japan",
        "category": "Visual Novel Engine",
        "color": "#f472b6",
        "typical_games": [
            "Fate/stay night",
            "Fate/hollow ataraxia",
            "Tsukihime (Original & Plus-Disc)",
            "Witch on the Holy Night (Mahoyo PC)",
            "G-senjou no Maou",
            "Sabbat of the Witch (Yuzusoft)",
            "Senren*Banka"
],
        "text_formats": [
            ".xp3",
            ".ks",
            ".tjs"
],
        "font_tech": "TrueType Rendering via FreeType/GDI",
        "recommended_tools": [
            "XP3Viewer",
            "KrkrExtract",
            "TStudio",
            "TRun"
],
        "complexity": "Easy to Medium",
        "description_th": "เอนจิ้นวิชวลโนเวลระดับตำนานของญี่ปุ่น ผู้สร้างความสำเร็จให้ Type-Moon และ Yuzusoft ไฟล์เกมบรรจุใน .xp3 สคริปต์เขียนด้วย KAG/TJS (.ks) แตกไฟล์ง่ายด้วย KrkrExtract",
        "description_en": "Legendary Japanese visual novel engine powering Type-Moon classics. Uses .xp3 packages and .ks scripts.",
        "detection": {
            "root_files": [
                        "tvpwin32.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".xp3"
            ],
            "exe_patterns": [
                        "fate.exe",
                        "tvpwin32.exe"
            ]
},
    },
    "NScripter / ONScripter": {
        "canonical_name": "NScripter",
        "aliases": [
            "nscripter",
            "onscripter",
            "ponscripter"
],
        "developer": "Naoki Takahashi",
        "origin_country": "Japan",
        "category": "Classic Visual Novel Engine",
        "color": "#fb7185",
        "typical_games": [
            "Higurashi When They Cry (Original)",
            "Umineko When They Cry (Original)",
            "Tsukihime (Original NScripter port)",
            "Narcissu"
],
        "text_formats": [
            "nscript.dat",
            "0.txt",
            "arc.nsa",
            ".sar"
],
        "font_tech": "TrueType (default.ttf in root)",
        "recommended_tools": [
            "NSDEC",
            "NSA Extractor",
            "TStudio"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นนิยายภาพยุคคลาสสิกที่สร้างประวัติศาสตร์ให้ซีรีส์ 'แว่วเสียงเรไร' Higurashi ข้อความอ่านง่ายจาก 0.txt หรือ nscript.dat",
        "description_en": "Classic Japanese VN engine behind Higurashi and Umineko, using nscript.dat and .nsa archives.",
        "detection": {
            "root_files": [
                        "nscript.dat",
                        "0.txt"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".nsa",
                        ".sar"
            ],
            "exe_patterns": [
                        "onscripter.exe"
            ]
},
    },
    "SiglusEngine": {
        "canonical_name": "SiglusEngine",
        "aliases": [
            "siglusengine",
            "siglus",
            "reallive"
],
        "developer": "Visual Arts / Key",
        "origin_country": "Japan",
        "category": "Proprietary Visual Novel Engine",
        "color": "#ec4899",
        "typical_games": [
            "CLANNAD (HD Edition)",
            "Little Busters! (English Edition)",
            "Summer Pockets & Reflection Blue",
            "Angel Beats! 1st beat",
            "Rewrite & Harvest festa!",
            "Kanon",
            "AIR"
],
        "text_formats": [
            "Gameexe.dat",
            ".pck",
            ".g00",
            ".dxf"
],
        "font_tech": "TrueType Font via GDI/DirectWrite",
        "recommended_tools": [
            "SiglusExtract",
            "RealLiveMax",
            "TStudio"
],
        "complexity": "High",
        "description_th": "เอนจิ้นประจำค่าย Key (Visual Arts) ผู้สร้างเกมบ่อน้ำตาแตกอย่าง CLANNAD และ Summer Pockets ไฟล์เกมหลักบรรจุใน Gameexe.dat และ Scene.pck",
        "description_en": "Visual Arts/Key's proprietary engine for CLANNAD and Summer Pockets, using Gameexe.dat and Scene.pck.",
        "detection": {
            "root_files": [
                        "siglusengine.exe",
                        "gameexe.dat"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".pck",
                        ".g00"
            ],
            "exe_patterns": [
                        "siglusengine.exe"
            ]
},
    },
    "CatSystem2": {
        "canonical_name": "CatSystem2",
        "aliases": [
            "catsystem2",
            "cs2",
            "catsystem"
],
        "developer": "Windmill",
        "origin_country": "Japan",
        "category": "Proprietary Visual Novel Engine",
        "color": "#f472b6",
        "typical_games": [
            "The Fruit of Grisaia (Grisaia no Kajitsu)",
            "The Labyrinth of Grisaia",
            "The Eden of Grisaia",
            "Chrono Clock",
            "Hatsuyuki Sakura"
],
        "text_formats": [
            ".int",
            ".cst",
            ".fes"
],
        "font_tech": "TrueType with FreeType renderer",
        "recommended_tools": [
            "cs2_decompiler",
            "intExtract",
            "TStudio"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นวิชวลโนเวลที่ใช้สร้างซีรีส์ Grisaia อันเลื่องชื่อ ไฟล์เกมบรรจุในคลัง .int ข้อความอยู่ในสคริปต์ .cst",
        "description_en": "Visual novel engine behind the Grisaia trilogy, using .int archives and .cst script files.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".int",
                        ".cst"
            ],
            "exe_patterns": [
                        "grisaia.exe"
            ]
},
    },
    "BGI / Ethornell": {
        "canonical_name": "BGI / Ethornell",
        "aliases": [
            "bgi",
            "ethornell",
            "bgi / ethornell",
            "buriko general interpreter"
],
        "developer": "Buriko General Interpreter",
        "origin_country": "Japan",
        "category": "Proprietary Visual Novel Engine",
        "color": "#fb7185",
        "typical_games": [
            "Daitoshokan no Hitsujikai",
            "August titles",
            "Steins;Gate (PSP/PC ports)"
],
        "text_formats": [
            ".arc",
            "._bp"
],
        "font_tech": "TrueType via FreeType",
        "recommended_tools": [
            "BGI Tool",
            "Sys4 Editor",
            "TStudio"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นสำหรับเกมวิชวลโนเวลชื่อดังในญี่ปุ่น ไฟล์ถูกรวมใน .arc",
        "description_en": "Widely used Japanese VN engine for August titles and others, using .arc archives.",
        "detection": {
            "root_files": [
                        "bgi.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".arc"
            ],
            "exe_patterns": [
                        "bgi.exe"
            ]
},
    },
    "Adventure Game Studio": {
        "canonical_name": "Adventure Game Studio",
        "aliases": [
            "adventure game studio",
            "ags",
            "ags engine"
],
        "developer": "Chris Jones / AGS Community",
        "origin_country": "UK",
        "category": "Point & Click 2D Adventure",
        "color": "#d97706",
        "typical_games": [
            "Gemini Rue",
            "Blackwell series",
            "Kathy Rain",
            "Whispers of a Machine",
            "Resonance",
            "Primordia"
],
        "text_formats": [
            ".ags",
            "ac2game.dta",
            ".tra"
],
        "font_tech": "WFN / TrueType Fonts (.ttf) embedded in AGS package",
        "recommended_tools": [
            "AGS Editor",
            "AGS Unpacker",
            "TStudio"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นสร้างเกมผจญภัย Point & Click แนวสืบสวนยอดนิยม ไฟล์เกมบรรจุใน ac2game.dta หรือ .ags รองรับไฟล์แปลภาษา .tra",
        "description_en": "Leading point-and-click retro adventure engine. Uses ac2game.dta and .tra translation files.",
        "detection": {
            "root_files": [
                        "ac2game.dta"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".ags"
            ],
            "exe_patterns": [
                        "geminirue.exe",
                        "kathyrain.exe"
            ]
},
    },
    "SCUMM": {
        "canonical_name": "SCUMM",
        "aliases": [
            "scumm",
            "scummvm",
            "lucasarts scumm"
],
        "developer": "LucasArts (Ron Gilbert & Aric Wilmunder)",
        "origin_country": "USA",
        "category": "Retro Point & Click Adventure",
        "color": "#b45309",
        "typical_games": [
            "The Secret of Monkey Island 1 & 2",
            "Maniac Mansion & Day of the Tentacle",
            "Indiana Jones and the Fate of Atlantis",
            "Full Throttle",
            "Sam & Max Hit the Road"
],
        "text_formats": [
            ".000",
            ".001",
            ".sou"
],
        "font_tech": "8-bit Bitmap Character Glyphs",
        "recommended_tools": [
            "ScummVM Tools",
            "SCUMM Revisited",
            "TStudio"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นสร้างประวัติศาสตร์เกมผจญภัยของ LucasArts รันได้อย่างสมบูรณ์แบบบน ScummVM",
        "description_en": "LucasArts' legendary adventure engine running natively on ScummVM.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".000",
                        ".001"
            ],
            "exe_patterns": [
                        "scummvm.exe"
            ]
},
    },
    "Build Engine": {
        "canonical_name": "Build Engine",
        "aliases": [
            "build engine",
            "build",
            "ken silverman build"
],
        "developer": "Ken Silverman / 3D Realms",
        "origin_country": "USA",
        "category": "Retro 2.5D FPS",
        "color": "#ea580c",
        "typical_games": [
            "Duke Nukem 3D",
            "Blood (Monolith)",
            "Shadow Warrior (1997)",
            "Ion Fury (Modern Build engine)",
            "Redneck Rampage"
],
        "text_formats": [
            ".grp",
            ".con",
            ".def"
],
        "font_tech": "Sprite Glyphs in TILES000.ART",
        "recommended_tools": [
            "eDuke32",
            "GRP Explorer",
            "TStudio"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้น 2.5D ระดับตำนานผู้ให้กำเนิด Duke Nukem 3D ไฟล์บรรจุใน .grp ข้อความอยู่ในสคริปต์ .con",
        "description_en": "Ken Silverman's classic 2.5D engine powering Duke Nukem 3D and Ion Fury.",
        "detection": {
            "root_files": [
                        "duke3d.grp"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".grp"
            ],
            "exe_patterns": [
                        "eduke32.exe",
                        "duke3d.exe"
            ]
},
    },
    "MonoGame / XNA": {
        "canonical_name": "MonoGame / XNA",
        "aliases": [
            "monogame",
            "xna",
            "fna",
            "monogame / xna"
],
        "developer": "Microsoft / MonoGame Team",
        "origin_country": "USA",
        "category": "C# .NET Indie Game Framework",
        "color": "#8b5cf6",
        "typical_games": [
            "Stardew Valley",
            "Terraria",
            "Celeste",
            "Bastion",
            "Transistor",
            "Fez",
            "Rogue Legacy",
            "Axiom Verge"
],
        "text_formats": [
            ".xnb",
            ".json",
            ".yaml",
            ".csv"
],
        "font_tech": "SpriteFont (.xnb) / TrueType via BMFont or Dynamic SpriteFont",
        "recommended_tools": [
            "XNB Extract",
            "SMAPI (Stardew)",
            "tModLoader (Terraria)",
            "TStudio",
            "TRun"
],
        "complexity": "Easy",
        "description_th": "เฟรมเวิร์กภาษา C# ยอดนิยมสูงสุดของวงการเกมอินดี้ บรรจุเนื้อหาใน .xnb มีคอมมูนิตี้ม็อดขนาดใหญ่ยักษ์ เช่น SMAPI ใน Stardew Valley และ tModLoader ใน Terraria ข้อความมักเป็น JSON",
        "description_en": "C# .NET framework behind Stardew Valley and Celeste. Uses .xnb assets and JSON text with strong mod API support.",
        "detection": {
            "root_files": [
                        "stardew valley.exe",
                        "terraria.exe",
                        "celeste.exe"
            ],
            "root_dlls": [
                        "monogame.framework.dll",
                        "fna.dll"
            ],
            "sub_dirs": [
                        "content"
            ],
            "extensions": [
                        ".xnb"
            ],
            "exe_patterns": [
                        "stardew valley.exe",
                        "terraria.exe",
                        "celeste.exe"
            ]
},
    },
    "Love2D": {
        "canonical_name": "Love2D",
        "aliases": [
            "love2d",
            "love",
            "löve",
            "love 2d"
],
        "developer": "LÖVE Development Team",
        "origin_country": "International",
        "category": "Lua 2D Game Framework",
        "color": "#ec4899",
        "typical_games": [
            "Balatro",
            "Move or Die",
            "Mari0",
            "Kingdom Rush (PC Port)",
            "SNKRX",
            "BABA IS YOU (custom engine using Lua/Love concept)"
],
        "text_formats": [
            ".love",
            ".lua",
            ".json"
],
        "font_tech": "Embedded TrueType (.ttf/.otf) with native FreeType rendering",
        "recommended_tools": [
            "7-Zip",
            "Lovely (Balatro Mod Loader)",
            "TStudio",
            "TRun"
],
        "complexity": "Easy",
        "description_th": "เฟรมเวิร์ก 2D ภาษา Lua ยอดฮิต ตัวเกมคือไฟล์ ZIP ที่เปลี่ยนนามสกุลเป็น .love (หรือรวมใน .exe) เปิดแตกไฟล์ด้วย 7-Zip ได้ทันที และในเกมฟีเวอร์อย่าง Balatro มี Lovely Mod Loader ช่วยฉีดข้อความและฟอนต์ไทยได้อย่างสมบูรณ์",
        "description_en": "Lua 2D framework powering smash-hits like Balatro. Moddable by opening the .exe or .love archive with 7-Zip.",
        "detection": {
            "root_files": [
                        "love.dll"
            ],
            "root_dlls": [
                        "love.dll",
                        "lua51.dll"
            ],
            "sub_dirs": [],
            "extensions": [
                        ".love"
            ],
            "exe_patterns": [
                        "balatro.exe"
            ]
},
    },
    "Java / LibGDX": {
        "canonical_name": "Java / LibGDX",
        "aliases": [
            "java / libgdx",
            "libgdx",
            "java",
            "java_libgdx"
],
        "developer": "Badlogic Games / Mojang",
        "origin_country": "International",
        "category": "Java Multi-Platform Game Framework",
        "color": "#ea580c",
        "typical_games": [
            "Slay the Spire",
            "Minecraft (Java Edition)",
            "Delver",
            "Mindy"
],
        "text_formats": [
            ".jar",
            ".zip",
            ".json",
            ".properties",
            ".csv"
],
        "font_tech": "FreeTypeFontGenerator / TrueType (.ttf) embedded in JAR",
        "recommended_tools": [
            "ModTheSpire",
            "7-Zip",
            "TStudio",
            "TRun"
],
        "complexity": "Easy",
        "description_th": "เฟรมเวิร์กภาษา Java สำหรับเกมข้ามแพลตฟอร์ม ไฟล์เกมบรรจุใน .jar (มาตรฐาน ZIP) ข้อความมักเป็นไฟล์ JSON หรือ Properties รองรับฟอนต์ TTF ภาษาไทยได้ทันที",
        "description_en": "Java-based game framework behind Slay the Spire and Minecraft Java, using standard .jar ZIP packaging and JSON/Properties.",
        "detection": {
            "root_files": [
                        "slaythespire.exe",
                        "slaythespire.jar"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "jre"
            ],
            "extensions": [
                        ".jar"
            ],
            "exe_patterns": [
                        "slaythespire.exe",
                        "javaw.exe"
            ]
},
    },
    "PICO-8": {
        "canonical_name": "PICO-8",
        "aliases": [
            "pico-8",
            "pico8",
            "tic-80"
],
        "developer": "Lexaloffle Games",
        "origin_country": "International",
        "category": "Fantasy Console 8-bit",
        "color": "#eab308",
        "typical_games": [
            "Celeste Classic",
            "Slipways (Pico-8 edition)",
            "Dusk Child"
],
        "text_formats": [
            ".p8",
            ".p8.png"
],
        "font_tech": "4x6 Pixel Fixed Bitmap Font",
        "recommended_tools": [
            "PICO-8 Console",
            "Text Editor"
],
        "complexity": "Medium",
        "description_th": "คอนโซลจำลองยุค 8-bit ข้อความอยู่ในตลับสคริปต์ Lua .p8",
        "description_en": "Fantasy console running Lua cartridges (.p8) with fixed 4x6 pixel fonts.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".p8",
                        ".p8.png"
            ],
            "exe_patterns": [
                        "pico8.exe"
            ]
},
    },
    "PopCap Framework": {
        "canonical_name": "PopCap Framework",
        "aliases": [
            "popcap",
            "popcap framework",
            "sexyappframework"
],
        "developer": "PopCap Games",
        "origin_country": "USA",
        "category": "Casual 2D Framework",
        "color": "#10b981",
        "typical_games": [
            "Plants vs. Zombies (PvZ)",
            "Peggle & Peggle Nights",
            "Bejeweled 2 & 3",
            "Zuma & Zuma's Revenge",
            "Bookworm"
],
        "text_formats": [
            ".pak",
            ".txt",
            ".xml"
],
        "font_tech": "Bitmap Font Image (.png/.xml pair)",
        "recommended_tools": [
            "PopCap PAK Extractor",
            "QuickBMS",
            "TStudio"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นสำหรับเกมแคชชวลอันดับ 1 ของโลกอย่าง Plants vs. Zombies ไฟล์รวมอยู่ใน main.pak แตกและแพ็กกลับได้ง่ายมาก",
        "description_en": "Casual framework powering Plants vs. Zombies, storing assets in main.pak.",
        "detection": {
            "root_files": [
                        "main.pak",
                        "plantsvszombies.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".pak"
            ],
            "exe_patterns": [
                        "plantsvszombies.exe",
                        "peggle.exe"
            ]
},
    },
    "IW Engine": {
        "canonical_name": "IW Engine",
        "aliases": [
            "iw engine",
            "iw",
            "iw_engine",
            "call of duty engine"
],
        "developer": "Infinity Ward / Activision",
        "origin_country": "USA",
        "category": "Proprietary AAA FPS",
        "color": "#16a34a",
        "typical_games": [
            "Call of Duty: Modern Warfare (2019) & MWII/MWIII",
            "Call of Duty: Warzone",
            "Call of Duty: Black Ops Cold War",
            "Call of Duty 4: Modern Warfare (Original)",
            "Call of Duty: Modern Warfare 2 (2009)",
            "Call of Duty: Black Ops (1, 2, 3, 4)"
],
        "text_formats": [
            ".iwd",
            ".ff",
            ".zone",
            ".txt",
            ".csv"
],
        "font_tech": "TrueType Texture Atlas in Fastfile (.ff) / Distance Field Font",
        "recommended_tools": [
            "Greyhound",
            "Cordycep",
            "FFXtract",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นเรือธงที่ขับเคลื่อนมหากาพย์ Call of Duty มายาวนาน พัฒนาต่อยอดมาจาก id Tech 3 บรรจุไฟล์ใน Fastfile (.ff) หรือ .iwd",
        "description_en": "Activision and Infinity Ward flagship engine powering the Call of Duty franchise, using Fastfile (.ff) containers.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "main",
                        "zone"
            ],
            "extensions": [
                        ".iwd",
                        ".ff"
            ],
            "exe_patterns": [
                        "cod.exe",
                        "iw3sp.exe",
                        "iw4sp.exe",
                        "iw5sp.exe",
                        "blackops.exe",
                        "modernwarfare.exe"
            ]
},
    },
    "Evolution Engine": {
        "canonical_name": "Evolution Engine",
        "aliases": [
            "evolution engine",
            "evolution",
            "evolution_engine"
],
        "developer": "Digital Extremes",
        "origin_country": "Canada",
        "category": "Proprietary AAA Live-Service Action",
        "color": "#8b5cf6",
        "typical_games": [
            "Warframe",
            "The Darkness II",
            "Dark Sector",
            "Soulframe (Upcoming)"
],
        "text_formats": [
            ".toc",
            ".pkg",
            ".cache",
            ".txt"
],
        "font_tech": "TrueType Vector Font / Flash UI Cache",
        "recommended_tools": [
            "QuickBMS",
            "Evolution Engine Tool",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นขับเคลื่อนเกมออนไลน์ยอดนิยม Warframe บรรจุไฟล์ใน .toc และ .pkg",
        "description_en": "Digital Extremes in-house engine powering Warframe, using .toc and .pkg packages.",
        "detection": {
            "root_files": [
                        "warframe.x64.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "cache.windows"
            ],
            "extensions": [
                        ".toc",
                        ".pkg"
            ],
            "exe_patterns": [
                        "warframe.x64.exe",
                        "thedarknessii.exe"
            ]
},
    },
    "Quantic Dream Engine": {
        "canonical_name": "Quantic Dream Engine",
        "aliases": [
            "quantic dream engine",
            "quantic dream",
            "quantic_dream_engine"
],
        "developer": "Quantic Dream",
        "origin_country": "France",
        "category": "Proprietary Interactive Narrative/Cinematic",
        "color": "#3b82f6",
        "typical_games": [
            "Detroit: Become Human",
            "Beyond: Two Souls",
            "Heavy Rain",
            "Fahrenheit (Indigo Prophecy)"
],
        "text_formats": [
            ".dax",
            ".idx",
            ".bin",
            ".xml"
],
        "font_tech": "TrueType Vector SDF / FreeType Embedded",
        "recommended_tools": [
            "QuickBMS",
            "Detroit Localization Tool",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นภาพยนตร์แบบโต้ตอบชั้นนำของ Quantic Dream บรรจุไฟล์ใน BigFile .dax และ .idx",
        "description_en": "Interactive drama engine behind Detroit: Become Human, packaging data into .dax and .idx files.",
        "detection": {
            "root_files": [
                        "detroitbecomehuman.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".dax",
                        ".idx"
            ],
            "exe_patterns": [
                        "detroitbecomehuman.exe",
                        "beyondtwosouls.exe",
                        "heavyrain.exe"
            ]
},
    },
    "Silk Engine": {
        "canonical_name": "Silk Engine",
        "aliases": [
            "silk engine",
            "silk",
            "silk_engine",
            "spiders engine"
],
        "developer": "Spiders",
        "origin_country": "France",
        "category": "Proprietary Action RPG",
        "color": "#06b6d4",
        "typical_games": [
            "GreedFall 1 & 2",
            "Steelrising",
            "The Technomancer",
            "Bound by Flame"
],
        "text_formats": [
            ".spk",
            ".bin",
            ".xml"
],
        "font_tech": "TrueType Vector Font / Bitmap Texture Atlas",
        "recommended_tools": [
            "QuickBMS",
            "Spiders SPK Extractor",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นประจำค่าย Spiders จากฝรั่งเศส บรรจุไฟล์เกมใน .spk ข้อความจัดเก็บเป็น XML ในแพ็กเกจ",
        "description_en": "Spiders in-house RPG engine powering GreedFall and Steelrising, packaging content in .spk archives.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "datalocal"
            ],
            "extensions": [
                        ".spk"
            ],
            "exe_patterns": [
                        "greedfall.exe",
                        "steelrising.exe",
                        "thetechnomancer.exe"
            ]
},
    },
    "Iron Engine": {
        "canonical_name": "Iron Engine",
        "aliases": [
            "iron engine",
            "iron_engine",
            "ctg engine",
            "volition iron engine"
],
        "developer": "Volition",
        "origin_country": "USA",
        "category": "Proprietary Open-World Destruction/Action",
        "color": "#9333ea",
        "typical_games": [
            "Saints Row 2, 3, 4 & Gat out of Hell",
            "Saints Row (2022 Reboot)",
            "Red Faction: Guerrilla (Geo-Mod 2.0 / Iron Engine)",
            "Agents of Mayhem"
],
        "text_formats": [
            ".vpp_pc",
            ".str2_pc",
            ".le_strings",
            ".xml"
],
        "font_tech": "TrueType Vector / Scaleform GFx",
        "recommended_tools": [
            "Gibbed Saints Row Tools",
            "ThomasJepp Tools",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นของค่าย Volition ผู้สร้าง Saints Row และ Red Faction บรรจุไฟล์ใน .vpp_pc และ .str2_pc ข้อความอยู่ใน .le_strings",
        "description_en": "Volition engine behind Saints Row and Red Faction Guerrilla, using .vpp_pc and .str2_pc packages.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "packfiles/pc"
            ],
            "extensions": [
                        ".vpp_pc",
                        ".str2_pc"
            ],
            "exe_patterns": [
                        "saintsrowthethird.exe",
                        "saintsrowiv.exe",
                        "saintsrow.exe"
            ]
},
    },
    "TW Engine": {
        "canonical_name": "TW Engine",
        "aliases": [
            "tw engine",
            "tw_engine",
            "warscape",
            "total war engine"
],
        "developer": "Creative Assembly",
        "origin_country": "UK",
        "category": "Proprietary Grand Tactical/RTS",
        "color": "#b45309",
        "typical_games": [
            "Total War: Warhammer 1, 2, 3",
            "Total War: Three Kingdoms",
            "Total War: Rome II",
            "Total War: Medieval II",
            "Total War: Shogun 2",
            "Total War: Pharaoh",
            "Total War: Attila"
],
        "text_formats": [
            ".pack",
            ".loc",
            ".tsv",
            ".xml"
],
        "font_tech": "TrueType Font (.ttf) mapped in db/fonts table",
        "recommended_tools": [
            "RPFM (Rusted PackFile Manager)",
            "Pack File Manager (PFM)",
            "TStudio",
            "TRun"
],
        "complexity": "Easy to Medium",
        "description_th": "เอนจิ้นสงครามยุทธการจำลองทหารนับหมื่นนายของ Total War บรรจุไฟล์เกมใน .pack ข้อความภาษาจัดเก็บในตาราง .loc ใน db/ สามารถแก้ด้วย RPFM ได้อย่างเป็นมืออาชีพ",
        "description_en": "Creative Assembly strategic battle engine. Localization is stored in .loc tables within .pack files, modded with RPFM.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".pack",
                        ".loc"
            ],
            "exe_patterns": [
                        "warhammer3.exe",
                        "threekingdoms.exe",
                        "rome2.exe",
                        "shogun2.exe"
            ]
},
    },
    "LithTech": {
        "canonical_name": "LithTech",
        "aliases": [
            "lithtech",
            "lithtech jupiter",
            "jupiter ex",
            "talon"
],
        "developer": "Monolith Productions",
        "origin_country": "USA",
        "category": "Classic FPS / Horror",
        "color": "#475569",
        "typical_games": [
            "F.E.A.R. 1 (Jupiter EX)",
            "F.E.A.R. 2: Project Origin",
            "Condemned: Criminal Origins",
            "No One Lives Forever 1 & 2",
            "Shogo: Mobile Armor Division",
            "Aliens versus Predator 2 (2001)"
],
        "text_formats": [
            ".arch00",
            ".rez",
            ".str"
],
        "font_tech": "Bitmap Font Sheets / TrueType",
        "recommended_tools": [
            "FEAR Extractor",
            "RezExtract",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นยิงสยองขวัญระดับตำนานของ F.E.A.R. บรรจุไฟล์ใน .arch00 หรือ .rez ข้อความอยู่ในตาราง .str",
        "description_en": "Monolith Productions classic engine powering F.E.A.R. and Condemned, using .arch00 archives.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".arch00",
                        ".rez"
            ],
            "exe_patterns": [
                        "fear.exe",
                        "fear2.exe",
                        "condemned.exe"
            ]
},
    },
    "Firefly Engine": {
        "canonical_name": "Firefly Engine",
        "aliases": [
            "firefly engine",
            "firefly",
            "nemesis engine",
            "monolith firefly"
],
        "developer": "Monolith Productions",
        "origin_country": "USA",
        "category": "Proprietary AAA Action/Adventure",
        "color": "#ca8a04",
        "typical_games": [
            "Middle-earth: Shadow of Mordor",
            "Middle-earth: Shadow of War",
            "Wonder Woman (Upcoming)"
],
        "text_formats": [
            ".arch06",
            ".bin",
            ".bnd"
],
        "font_tech": "TrueType Vector Font / Scaleform GFx",
        "recommended_tools": [
            "QuickBMS",
            "Shadow of Mordor Tools",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นที่มีระบบ Nemesis System อันโด่งดัง บรรจุไฟล์ใน .arch06",
        "description_en": "Monolith engine powering Shadow of Mordor and Shadow of War, utilizing .arch06 archives.",
        "detection": {
            "root_files": [
                        "shadowofmordor.exe",
                        "shadowofwar.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".arch06"
            ],
            "exe_patterns": [
                        "shadowofmordor.exe",
                        "shadowofwar.exe"
            ]
},
    },
    "Hello Games Engine": {
        "canonical_name": "Hello Games Engine",
        "aliases": [
            "hello games engine",
            "in-house (hello games)",
            "no man's sky engine",
            "hello games"
],
        "developer": "Hello Games",
        "origin_country": "UK",
        "category": "Proprietary Procedural Infinite Universe",
        "color": "#06b6d4",
        "typical_games": [
            "No Man's Sky",
            "Light No Fire (Upcoming)",
            "The Last Campfire"
],
        "text_formats": [
            ".pak",
            ".mbin",
            ".exml"
],
        "font_tech": "DDS Texture Font Atlas / FreeType TrueType",
        "recommended_tools": [
            "MBINCompiler",
            "PSArcTool",
            "NMS Modding Tools",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นสร้างจักรวาลแบบ Procedural Generation ระดับมหากาพย์ บรรจุไฟล์เกมใน .pak ข้อความอยู่ในไฟล์ .mbin ซึ่งสามารถแปลงเป็น XML (.exml) ได้ผ่าน MBINCompiler",
        "description_en": "Procedural universe engine powering No Man's Sky. Localized text sits inside .mbin files, convertible with MBINCompiler.",
        "detection": {
            "root_files": [
                        "nms.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "gamedata/pcbanks"
            ],
            "extensions": [
                        ".mbin"
            ],
            "exe_patterns": [
                        "nms.exe"
            ]
},
    },
    "Blizzard Proprietary": {
        "canonical_name": "Blizzard Engine",
        "aliases": [
            "blizzard engine",
            "blizzard proprietary",
            "blizzard_engine",
            "blizzard"
],
        "developer": "Blizzard Entertainment",
        "origin_country": "USA",
        "category": "Proprietary AAA Strategy / Action RPG / Hero Shooter",
        "color": "#0284c7",
        "typical_games": [
            "Warcraft III: Reforged & The Frozen Throne",
            "StarCraft II: Wings of Liberty / Heart of the Swarm / Legacy of the Void",
            "Overwatch 1 & 2 (Tank Engine)",
            "Diablo III & Diablo IV",
            "Heroes of the Storm",
            "World of Warcraft"
],
        "text_formats": [
            ".mpq",
            ".casc",
            ".txt",
            ".json",
            ".srt"
],
        "font_tech": "Embedded TrueType (.ttf/.otf) with custom shaping engine",
        "recommended_tools": [
            "CascView",
            "MPQEditor",
            "CASC Explorer",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นระดับตำนานของ Blizzard ในยุคใหม่ใช้ระบบคลังเก็บข้อมูล CASC (Content Addressable Storage Container) ข้อความอยู่ในไฟล์ String tables ฟอนต์รองรับ TTF ในคลังข้อมูล",
        "description_en": "Blizzard's flagship proprietary technology using CASC and MPQ storage containers with embedded TrueType fonts.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "data/data",
                        "warcraft iii"
            ],
            "extensions": [
                        ".mpq",
                        ".idx"
            ],
            "exe_patterns": [
                        "warcraft iii.exe",
                        "sc2_x64.exe",
                        "overwatch.exe",
                        "diablo iv.exe"
            ]
},
    },
    "Blam Engine": {
        "canonical_name": "Blam Engine",
        "aliases": [
            "blam engine",
            "blam",
            "bungie blam",
            "halo engine"
],
        "developer": "Bungie",
        "origin_country": "USA",
        "category": "Proprietary Sci-Fi FPS",
        "color": "#059669",
        "typical_games": [
            "Halo: Combat Evolved",
            "Halo 2",
            "Halo 3 & ODST",
            "Halo: Reach",
            "Halo 4 (343 modified Blam)"
],
        "text_formats": [
            ".map",
            ".unic",
            ".txt"
],
        "font_tech": "Bitmap Font Glyphs in .map tags",
        "recommended_tools": [
            "Assembly",
            "Halo Editing Kit (HEK)",
            "TStudio"
],
        "complexity": "High",
        "description_th": "เอนจิ้นต้นกำเนิดตำนาน Master Chief ข้อมูลทั้งหมดถูกรวมอยู่ในไฟล์ .map",
        "description_en": "Bungie's classic FPS engine behind Halo 1 through Reach, packaging assets in .map files.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "maps"
            ],
            "extensions": [
                        ".map"
            ],
            "exe_patterns": [
                        "halo.exe",
                        "halo2.exe"
            ]
},
    },
    "Tiger Engine": {
        "canonical_name": "Tiger Engine",
        "aliases": [
            "tiger engine",
            "tiger",
            "bungie tiger"
],
        "developer": "Bungie",
        "origin_country": "USA",
        "category": "Proprietary AAA MMO-FPS",
        "color": "#0284c7",
        "typical_games": [
            "Destiny 1",
            "Destiny 2 & Expansions"
],
        "text_formats": [
            ".pkg",
            ".bin"
],
        "font_tech": "TrueType Vector Font in PKG / Scaleform",
        "recommended_tools": [
            "Destiny PKG Tool",
            "TStudio"
],
        "complexity": "Very High",
        "description_th": "เอนจิ้นของเกม Destiny 2 พัฒนาต่อยอดจาก Blam เพื่อรองรับเกมยิงออนไลน์ขนาดยักษ์",
        "description_en": "Bungie's evolved engine powering Destiny 2, using .pkg archives.",
        "detection": {
            "root_files": [
                        "destiny2.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "packages"
            ],
            "extensions": [
                        ".pkg"
            ],
            "exe_patterns": [
                        "destiny2.exe"
            ]
},
    },
    "Slipspace Engine": {
        "canonical_name": "Slipspace Engine",
        "aliases": [
            "slipspace engine",
            "slipspace",
            "halo infinite engine"
],
        "developer": "343 Industries",
        "origin_country": "USA",
        "category": "Proprietary AAA FPS",
        "color": "#0369a1",
        "typical_games": [
            "Halo Infinite"
],
        "text_formats": [
            ".module",
            ".bin"
],
        "font_tech": "Signed Distance Field Vector / TrueType",
        "recommended_tools": [
            "Slipspace Extractor",
            "TStudio"
],
        "complexity": "Very High",
        "description_th": "เอนจิ้นยุคใหม่ของแฟรนไชส์ Halo สร้างขึ้นสำหรับ Halo Infinite บรรจุไฟล์ใน .module",
        "description_en": "Modern 343 Industries engine designed for Halo Infinite, utilizing .module containers.",
        "detection": {
            "root_files": [
                        "haloinfinite.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".module"
            ],
            "exe_patterns": [
                        "haloinfinite.exe"
            ]
},
    },
    "Telltale Tool": {
        "canonical_name": "Telltale Tool",
        "aliases": [
            "telltale tool",
            "telltale",
            "telltale engine"
],
        "developer": "Telltale Games",
        "origin_country": "USA",
        "category": "Proprietary Episodic Narrative Adventure",
        "color": "#f97316",
        "typical_games": [
            "The Walking Dead (Seasons 1, 2, A New Frontier, The Final Season)",
            "The Wolf Among Us",
            "Tales from the Borderlands",
            "Batman: The Telltale Series & The Enemy Within",
            "Game of Thrones: A Telltale Games Series",
            "Minecraft: Story Mode"
],
        "text_formats": [
            ".ttarch",
            ".ttarch2",
            ".landb",
            ".prop"
],
        "font_tech": "TrueType Font (.ttf) embedded in TTARCH packages / Font metadata .prop",
        "recommended_tools": [
            "TTG Tools",
            "Telltale Inspector",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นเกมผจญภัยแบบแบ่งตอนยอดนิยม บรรจุไฟล์ทั้งหมดใน .ttarch หรือ .ttarch2 ข้อความอยู่ในไฟล์ฐานข้อมูลภาษา .landb สามารถแตกและแพ็กกลับได้ด้วย TTG Tools",
        "description_en": "Episodic story engine behind The Walking Dead and The Wolf Among Us. Assets packed in .ttarch/.ttarch2 with .landb string tables.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "archives"
            ],
            "extensions": [
                        ".ttarch",
                        ".ttarch2"
            ],
            "exe_patterns": [
                        "walkingdead.exe",
                        "walkingdead2.exe",
                        "wwau.exe",
                        "batman.exe"
            ]
},
    },
    "Diesel Engine": {
        "canonical_name": "Diesel Engine",
        "aliases": [
            "diesel engine",
            "diesel",
            "overkill diesel"
],
        "developer": "GRIN / Overkill Software (Starbreeze)",
        "origin_country": "Sweden",
        "category": "Proprietary Cooperative FPS",
        "color": "#eab308",
        "typical_games": [
            "PAYDAY: The Heist",
            "PAYDAY 2",
            "Bionic Commando (2009)",
            "Tom Clancy's Ghost Recon Advanced Warfighter 1 & 2 (PC)"
],
        "text_formats": [
            ".bundle",
            ".stream",
            ".lua",
            ".xml"
],
        "font_tech": "TrueType Vector Font / Bitmap Glyph Atlas",
        "recommended_tools": [
            "Diesel Bundle Modder",
            "SuperBLT",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นประจำค่าย Overkill ผู้สร้างเกมปล้นธนาคาร PAYDAY 2 บรรจุไฟล์เกมใน .bundle มี SuperBLT รองรับม็อดสคริปต์ Lua",
        "description_en": "Cooperative FPS engine behind PAYDAY 2, packaging assets into .bundle archives with SuperBLT mod support.",
        "detection": {
            "root_files": [
                        "payday2_win32_release.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "assets"
            ],
            "extensions": [
                        ".bundle"
            ],
            "exe_patterns": [
                        "payday2_win32_release.exe"
            ]
},
    },
    "PhyreEngine": {
        "canonical_name": "PhyreEngine",
        "aliases": [
            "phyreengine",
            "phyre",
            "sony phyreengine"
],
        "developer": "Sony Interactive Entertainment",
        "origin_country": "Japan / UK",
        "category": "Cross-Platform Framework (PS3/PS4/PC/Vita)",
        "color": "#3b82f6",
        "typical_games": [
            "Persona 5 (PS3/PS4 original)",
            "Trails of Cold Steel 1 & 2 (PS3/Vita/PC)",
            "Dragon Quest Builders 1 & 2",
            "Tokyo Xanadu eX+",
            "Demon's Souls (PS3 original framework)"
],
        "text_formats": [
            ".pkg",
            ".cpk",
            ".bin",
            ".dat"
],
        "font_tech": "FreeType Vector / TrueType embedded",
        "recommended_tools": [
            "SenPatcher",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "Medium to High",
        "description_th": "เอนจิ้นแจกฟรีของ Sony สำหรับผู้พัฒนาเกมข้ามแพลตฟอร์ม ถูกใช้ในเกม JRPG ชื่อดังมากมาย",
        "description_en": "Sony multiplatform middleware and game engine powering earlier Trails of Cold Steel titles and Persona 5.",
        "detection": {
            "root_files": [],
            "root_dlls": [
                        "phyreengine.dll"
            ],
            "sub_dirs": [],
            "extensions": [
                        ".pkg"
            ],
            "exe_patterns": []
},
    },
    "Media.Vision Engine": {
        "canonical_name": "Media.Vision Engine",
        "aliases": [
            "media.vision engine",
            "media.vision",
            "media_vision",
            "mediavision"
],
        "developer": "Media.Vision",
        "origin_country": "Japan",
        "category": "Proprietary JRPG",
        "color": "#a855f7",
        "typical_games": [
            "Digimon Story: Cyber Sleuth",
            "Digimon Story: Cyber Sleuth - Hacker's Memory",
            "Valkyria Revolution",
            "Wild Arms series"
],
        "text_formats": [
            ".dsarc",
            ".bin",
            ".mve"
],
        "font_tech": "TrueType Vector Font / Bitmap Texture Glyph Sheets",
        "recommended_tools": [
            "DSARC Tool",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นของค่าย Media.Vision ผู้สร้างเกมดิจิมอนภาคดัง ไฟล์เกมถูกบรรจุใน .dsarc",
        "description_en": "Media.Vision in-house engine powering Digimon Story: Cyber Sleuth, utilizing .dsarc packages.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".dsarc"
            ],
            "exe_patterns": [
                        "digimonstorycybersleuth.exe"
            ]
},
    },
    "Cygames Proprietary": {
        "canonical_name": "Cygames Proprietary",
        "aliases": [
            "cygames proprietary",
            "cygames",
            "cygames_proprietary",
            "relink engine"
],
        "developer": "Cygames",
        "origin_country": "Japan",
        "category": "Proprietary AAA Action RPG",
        "color": "#06b6d4",
        "typical_games": [
            "Granblue Fantasy: Relink"
],
        "text_formats": [
            ".pak",
            ".bin",
            ".msg"
],
        "font_tech": "TrueType Vector SDF / Native FreeType",
        "recommended_tools": [
            "Relink Mod Manager",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นแอ็กชันภาพสวยงามระดับพรีเมียมของ Cygames สำหรับ Granblue Fantasy: Relink บรรจุไฟล์ใน data.pak",
        "description_en": "Cygames proprietary action engine created for Granblue Fantasy: Relink, packaging data in data.pak.",
        "detection": {
            "root_files": [
                        "granblue_fantasy_relink.exe",
                        "data.pak"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".pak"
            ],
            "exe_patterns": [
                        "granblue_fantasy_relink.exe"
            ]
},
    },
    "Toylogic Engine": {
        "canonical_name": "Toylogic Engine",
        "aliases": [
            "toylogic engine",
            "toylogic",
            "toylogic_engine",
            "replicant engine"
],
        "developer": "Toylogic / Square Enix",
        "origin_country": "Japan",
        "category": "Proprietary Action RPG",
        "color": "#64748b",
        "typical_games": [
            "NieR Replicant ver.1.22474487139...",
            "Warlander",
            "Happy Wars"
],
        "text_formats": [
            ".arc",
            ".bin"
],
        "font_tech": "TrueType Vector Font / Bitmap Texture Sheets",
        "recommended_tools": [
            "NieR Replicant Unpacker",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นที่ Toylogic ปรับปรุงใหม่เพื่อรีเมก NieR Replicant ให้ลื่นไหลระดับ 60fps บรรจุเนื้อหาในแพ็กเกจ .arc",
        "description_en": "Toylogic engine built for NieR Replicant ver.1.2247..., packaging data into .arc archives.",
        "detection": {
            "root_files": [
                        "nierreplicant.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".arc"
            ],
            "exe_patterns": [
                        "nierreplicant.exe"
            ]
},
    },
    "Silicon Studio Engine": {
        "canonical_name": "Silicon Studio Engine",
        "aliases": [
            "silicon studio engine",
            "sge_engine",
            "sge",
            "mizuchi",
            "orochi"
],
        "developer": "Silicon Studio",
        "origin_country": "Japan",
        "category": "Proprietary Japanese JRPG Engine",
        "color": "#8b5cf6",
        "typical_games": [
            "Bravely Default II",
            "Gundam Breaker 3",
            "Left Alive (rendering tech)"
],
        "text_formats": [
            ".pak",
            ".bin",
            ".sge"
],
        "font_tech": "TrueType Vector Font / Font Sheet Texture",
        "recommended_tools": [
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "High",
        "description_th": "เอนจิ้นและเทคโนโลยีเรนเดอร์ของ Silicon Studio จากญี่ปุ่น",
        "description_en": "Silicon Studio game engine and rendering framework.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".sge"
            ],
            "exe_patterns": [
                        "bravelydefault2.exe"
            ]
},
    },
    "NuLibrary": {
        "canonical_name": "NuLibrary",
        "aliases": [
            "nulibrary",
            "bandai namco in-house",
            "namco engine",
            "cyberconnect2 engine"
],
        "developer": "Bandai Namco / CyberConnect2",
        "origin_country": "Japan",
        "category": "Proprietary Anime Action / JRPG",
        "color": "#f59e0b",
        "typical_games": [
            "Naruto Shippuden: Ultimate Ninja Storm (1, 2, 3, 4, Connections)",
            "Dragon Ball Z: Kakarot",
            "Demon Slayer: Kimetsu no Yaiba - The Hinokami Chronicles",
            "JoJo's Bizarre Adventure: All-Star Battle R"
],
        "text_formats": [
            ".cpk",
            ".xfbin",
            ".bin",
            ".msg"
],
        "font_tech": "TrueType Texture Font Sheet in XFBIN / CriWare CPK",
        "recommended_tools": [
            "CriPakTools",
            "XFBIN Parser",
            "TStudio",
            "TRun"
],
        "complexity": "Medium to High",
        "description_th": "เอนจิ้นเกมต่อสู้สไตล์อนิเมะของ CyberConnect2 และ Bandai Namco บรรจุไฟล์เกมใน .cpk (CRIWARE) และไฟล์ออบเจกต์ .xfbin",
        "description_en": "Anime action framework by CyberConnect2 and Bandai Namco, using CRI CPK packages and .xfbin resource archives.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".xfbin",
                        ".cpk"
            ],
            "exe_patterns": [
                        "ns4.exe",
                        "ns3fb.exe",
                        "dbzkakarot.exe"
            ]
},
    },
    "Vigil Engine": {
        "canonical_name": "Vigil Engine",
        "aliases": [
            "vigil engine",
            "vigil",
            "vigil_engine"
],
        "developer": "Vigil Games",
        "origin_country": "USA",
        "category": "Proprietary Action-Adventure / Hack & Slash",
        "color": "#e11d48",
        "typical_games": [
            "Darksiders 1 (Warmastered Edition)",
            "Darksiders II (Deathinitive Edition)"
],
        "text_formats": [
            ".pck",
            ".bin",
            ".xml"
],
        "font_tech": "Bitmap Font Sheets / Scaleform GFx",
        "recommended_tools": [
            "Darksiders PCK Extractor",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นประจำค่าย Vigil Games สำหรับมหากาพย์ Darksiders ภาค 1 และ 2 บรรจุไฟล์ใน .pck",
        "description_en": "Vigil Games engine powering Darksiders 1 & 2, using .pck container archives.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "media"
            ],
            "extensions": [
                        ".pck"
            ],
            "exe_patterns": [
                        "darksiders1.exe",
                        "darksiders2.exe"
            ]
},
    },
    "Liquid Engine": {
        "canonical_name": "Liquid Engine",
        "aliases": [
            "liquid engine",
            "liquidengine",
            "liquid_entertainment"
],
        "developer": "Liquid Entertainment",
        "origin_country": "USA",
        "category": "Classic RTS 3D",
        "color": "#0284c7",
        "typical_games": [
            "Battle Realms & Winter of the Wolf"
],
        "text_formats": [
            ".dat",
            ".h2o",
            ".txt"
],
        "font_tech": "8-bit Bitmap Font Sheets",
        "recommended_tools": [
            "H2O Extractor",
            "TStudio"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นของเกมวางแผนระดับตำนานขวัญใจคนไทย Battle Realms บรรจุไฟล์ใน .dat และ .h2o",
        "description_en": "Classic RTS engine powering Battle Realms, using .dat and .h2o archives.",
        "detection": {
            "root_files": [
                        "battlerealms.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".h2o"
            ],
            "exe_patterns": [
                        "battlerealms.exe",
                        "battle_realms_f.exe"
            ]
},
    },
    "Pixpil Engine": {
        "canonical_name": "Pixpil Engine",
        "aliases": [
            "pixpil engine",
            "pixpil",
            "pixpil_engine"
],
        "developer": "Pixpil",
        "origin_country": "China",
        "category": "Proprietary Pixel Art 2D/3D Hybrid",
        "color": "#f97316",
        "typical_games": [
            "Eastward"
],
        "text_formats": [
            ".gpk",
            ".json",
            ".lua"
],
        "font_tech": "TrueType Pixel Font (.ttf)",
        "recommended_tools": [
            "GPK Unpacker",
            "TStudio"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นพิกเซลอาร์ตอันวิจิตรงดงามของเกม Eastward บรรจุไฟล์ใน .gpk",
        "description_en": "Pixel-art engine powering Eastward, packaging assets in .gpk.",
        "detection": {
            "root_files": [
                        "eastward.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".gpk"
            ],
            "exe_patterns": [
                        "eastward.exe"
            ]
},
    },
    "Yacht Club Engine": {
        "canonical_name": "Yacht Club Engine",
        "aliases": [
            "yacht club engine",
            "yachtclubengine",
            "yacht club"
],
        "developer": "Yacht Club Games",
        "origin_country": "USA",
        "category": "Retro 8-bit Action Platformer",
        "color": "#0284c7",
        "typical_games": [
            "Shovel Knight: Treasure Trove (Shovel of Hope, Plague of Shadows, Specter of Torment, King of Cards)"
],
        "text_formats": [
            ".pak",
            ".csv",
            ".txt"
],
        "font_tech": "NES-authentic Pixel Font Glyphs",
        "recommended_tools": [
            "QuickBMS",
            "TStudio"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นสไตล์ 8-bit NES ยุคโมเดิร์นของ Shovel Knight บรรจุข้อความและสไปรต์ใน .pak",
        "description_en": "Retro 8-bit NES style engine created for Shovel Knight.",
        "detection": {
            "root_files": [
                        "shovelknight.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".pak"
            ],
            "exe_patterns": [
                        "shovelknight.exe"
            ]
},
    },
    "Polyphony Digital Engine": {
        "canonical_name": "Polyphony Digital Engine",
        "aliases": [
            "polyphony digital engine",
            "polyphony digital",
            "gran turismo engine"
],
        "developer": "Polyphony Digital / Sony",
        "origin_country": "Japan",
        "category": "Proprietary Real Driving Simulator",
        "color": "#0284c7",
        "typical_games": [
            "Gran Turismo 7",
            "Gran Turismo Sport",
            "Gran Turismo 5 & 6"
],
        "text_formats": [
            ".vol",
            ".bin",
            ".dat"
],
        "font_tech": "High-Precision TrueType Vector Font",
        "recommended_tools": [
            "GT Toolset",
            "TStudio"
],
        "complexity": "High",
        "description_th": "เอนจิ้นจำลองการขับขี่รถยนต์สมจริงระดับโลกของ Gran Turismo บรรจุไฟล์ใน .vol",
        "description_en": "Real driving simulation engine behind the Gran Turismo franchise.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".vol"
            ],
            "exe_patterns": []
},
    },
    "Torque 3D": {
        "canonical_name": "Torque 3D",
        "aliases": [
            "torque 3d",
            "torque",
            "torque engine",
            "garagegames"
],
        "developer": "GarageGames",
        "origin_country": "USA",
        "category": "Open-Source / Classic Commercial 3D",
        "color": "#ea580c",
        "typical_games": [
            "Tribes 2",
            "Blockland",
            "Marble Blast Gold / Ultra",
            "BeamNG.drive (Early prototypes)"
],
        "text_formats": [
            ".zip",
            ".dso",
            ".gui",
            ".cs"
],
        "font_tech": "TrueType to Bitmap Font Cache",
        "recommended_tools": [
            "Torque Tool",
            "TStudio"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้น 3D โอเพนซอร์สยุคคลาสสิก ใช้สคริปต์ TorqueScript (.cs) และไฟล์ .gui",
        "description_en": "Open-source 3D engine using TorqueScript and .zip containers.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "scripts",
                        "art"
            ],
            "extensions": [
                        ".dso"
            ],
            "exe_patterns": []
},
    },
    "Leadwerks": {
        "canonical_name": "Leadwerks",
        "aliases": [
            "leadwerks",
            "leadwerks engine",
            "ultra engine"
],
        "developer": "Leadwerks Software",
        "origin_country": "USA",
        "category": "Indie 3D Commercial",
        "color": "#6366f1",
        "typical_games": [
            "Various Indie 3D horror and action games"
],
        "text_formats": [
            ".pak",
            ".lua",
            ".json"
],
        "font_tech": "TrueType via FreeType",
        "recommended_tools": [
            "Leadwerks Editor",
            "TStudio"
],
        "complexity": "Easy",
        "description_th": "เอนจิ้นสร้างเกมสำหรับอินดี้ C++ และ Lua บรรจุไฟล์ใน .pak",
        "description_en": "Indie C++/Lua 3D engine using .pak archives.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".pak"
            ],
            "exe_patterns": []
},
    },
    "Stride": {
        "canonical_name": "Stride",
        "aliases": [
            "stride",
            "stride engine",
            "xenko"
],
        "developer": "Stride Community / Silicon Studio",
        "origin_country": "Japan / International",
        "category": "Open-Source C# .NET 3D",
        "color": "#10b981",
        "typical_games": [
            "Modern open-source C# 3D indie titles"
],
        "text_formats": [
            ".sdpkg",
            ".json"
],
        "font_tech": "SDF Font Asset / TrueType",
        "recommended_tools": [
            "Stride Game Studio",
            "TStudio"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นภาษา C# .NET โอเพนซอร์สประสิทธิภาพสูง เดิมชื่อ Xenko พัฒนาโดย Silicon Studio",
        "description_en": "High-performance open source C# .NET engine formerly known as Xenko.",
        "detection": {
            "root_files": [],
            "root_dlls": [
                        "stride.engine.dll"
            ],
            "sub_dirs": [],
            "extensions": [
                        ".sdpkg"
            ],
            "exe_patterns": []
},
    },
    "ZenGin": {
        "canonical_name": "ZenGin",
        "aliases": [
            "zengin",
            "zen engine",
            "gothic engine"
],
        "developer": "Piranha Bytes",
        "origin_country": "Germany",
        "category": "Classic Action RPG",
        "color": "#84cc16",
        "typical_games": [
            "Gothic 1",
            "Gothic 2 & Gold Edition / Night of the Raven"
],
        "text_formats": [
            ".vdf",
            ".bin",
            ".d"
],
        "font_tech": "FNT Bitmap Font Textures in VDF",
        "recommended_tools": [
            "GothicVDFS",
            "Daedalus Decompiler",
            "TStudio"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้น RPG สุดคลาสสิกของซีรีส์ Gothic ภาค 1 และ 2 บรรจุไฟล์เกมใน .vdf ข้อความอยู่ในสคริปต์ Daedalus",
        "description_en": "Piranha Bytes classic RPG engine behind Gothic 1 & 2, storing data in .vdf archives.",
        "detection": {
            "root_files": [
                        "gothic.exe",
                        "gothic2.exe"
            ],
            "root_dlls": [],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".vdf"
            ],
            "exe_patterns": [
                        "gothic.exe",
                        "gothic2.exe"
            ]
},
    },
    "Electron Engine": {
        "canonical_name": "Electron Engine",
        "aliases": [
            "electron engine",
            "electron",
            "nwn2 engine"
],
        "developer": "Obsidian Entertainment / BioWare",
        "origin_country": "USA",
        "category": "Classic 3D RPG",
        "color": "#f97316",
        "typical_games": [
            "Neverwinter Nights 2 & Expansions (Mask of the Betrayer, Storm of Zehir)"
],
        "text_formats": [
            ".tlk",
            ".zip",
            ".erf",
            ".trx"
],
        "font_tech": "TrueType Vector Font / XML font definitions",
        "recommended_tools": [
            "NWN2 Toolset",
            "TLK Editor",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นตระกูล Aurora ที่ Obsidian พัฒนาขนานใหญ่สำหรับ Neverwinter Nights 2 ข้อความอยู่ใน dialog.tlk",
        "description_en": "Obsidian's heavily modified Aurora successor for Neverwinter Nights 2, using dialog.tlk.",
        "detection": {
            "root_files": [
                        "nwn2main.exe",
                        "dialog.tlk"
            ],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [
                        ".tlk",
                        ".trx"
            ],
            "exe_patterns": [
                        "nwn2main.exe"
            ]
},
    },
    "CRIWARE": {
        "canonical_name": "CRIWARE",
        "aliases": [
            "criware",
            "cri ware",
            "cricpk"
],
        "developer": "CRI Middleware",
        "origin_country": "Japan",
        "category": "Multimedia Middleware / Japanese Engine Wrapper",
        "color": "#0284c7",
        "typical_games": [
            "Persona 4 Golden / Persona 3 Portable (PC ports)",
            "Sonic Frontiers / Sonic Forces",
            "Tales of Vesperia: Definitive Edition",
            "SOTDF (Shadow of the Damned: Hella Remastered)",
            "Danganronpa series"
],
        "text_formats": [
            ".cpk",
            ".usm",
            ".awb",
            ".acb"
],
        "font_tech": "TrueType or Bitmap Font embedded in CPK containers",
        "recommended_tools": [
            "CriPakTools",
            "QuickBMS",
            "CRI Atom Craft",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "มิดเดิลแวร์ระบบภาพและเสียงยอดนิยมของญี่ปุ่น เกมญี่ปุ่นหลายร้อยเกมใช้ระบบบรรจุไฟล์ .cpk (CRI File System) ซึ่งสามารถแตกและแพ็กกลับได้ด้วย CriPakTools",
        "description_en": "Leading Japanese audio/video middleware and package format (.cpk) used across hundreds of Japanese titles.",
        "detection": {
            "root_files": [],
            "root_dlls": [
                        "criware.dll"
            ],
            "sub_dirs": [],
            "extensions": [
                        ".cpk",
                        ".usm"
            ],
            "exe_patterns": []
},
    },
    "Marvelous Engine": {
        "canonical_name": "Marvelous Engine",
        "aliases": [
            "marvelous engine",
            "marvelous",
            "marvelous_engine"
],
        "developer": "Marvelous Inc.",
        "origin_country": "Japan",
        "category": "Proprietary Farming/JRPG Simulation",
        "color": "#f59e0b",
        "typical_games": [
            "Story of Seasons: A Wonderful Life",
            "Story of Seasons: Pioneers of Olive Town",
            "Story of Seasons: Friends of Mineral Town",
            "Rune Factory 3 Special",
            "Rune Factory 4 Special",
            "Rune Factory 5"
],
        "text_formats": [
            ".lzs",
            ".bin",
            ".csv",
            ".json"
],
        "font_tech": "TrueType Vector Font / Texture Font Atlas",
        "recommended_tools": [
            "LZS Decompressor",
            "QuickBMS",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นของค่าย Marvelous ผู้สร้างเกมปลูกผัก Story of Seasons และ Rune Factory บรรจุไฟล์ใน .lzs",
        "description_en": "Marvelous Inc. engine behind Story of Seasons and Rune Factory series, using .lzs compressed archives.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "data"
            ],
            "extensions": [
                        ".lzs"
            ],
            "exe_patterns": [
                        "sosawl.exe",
                        "sospoot.exe",
                        "rf5.exe"
            ]
},
    },
    "LEAD Engine": {
        "canonical_name": "LEAD Engine",
        "aliases": [
            "lead engine",
            "lead",
            "lead_engine"
],
        "developer": "Ubisoft Montreal / Red Storm",
        "origin_country": "Canada / USA",
        "category": "Proprietary Stealth/Action",
        "color": "#16a34a",
        "typical_games": [
            "Tom Clancy's Splinter Cell: Conviction",
            "Tom Clancy's Splinter Cell: Blacklist"
],
        "text_formats": [
            ".umd",
            ".bin",
            ".txt"
],
        "font_tech": "TrueType Vector / Scaleform GFx",
        "recommended_tools": [
            "QuickBMS",
            "Splinter Cell Tool",
            "TStudio",
            "TRun"
],
        "complexity": "Medium",
        "description_th": "เอนจิ้นพัฒนาเฉพาะสำหรับเกมสายลับ Splinter Cell Conviction และ Blacklist",
        "description_en": "Heavily customized Unreal-based engine developed for Splinter Cell Conviction and Blacklist.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [
                        "src/system"
            ],
            "extensions": [
                        ".umd"
            ],
            "exe_patterns": [
                        "conviction_game.exe",
                        "blacklist_game.exe"
            ]
},
    },
    "Custom Engine": {
        "canonical_name": "Custom Engine",
        "aliases": [
            "custom engine",
            "custom_engine",
            "custom",
            "in-house",
            "proprietary"
],
        "developer": "Independent / Proprietary Studios",
        "origin_country": "Various",
        "category": "In-house / Proprietary Architecture",
        "color": "#94a3b8",
        "typical_games": [
            "Hades 1 & 2 (Supergiant Games custom C++ engine)",
            "Noita (Nolla Games Falling Everything engine)",
            "No Man's Sky (Hello Games in-house engine)",
            "Eastward (Pixpil engine)",
            "Shovel Knight (Yacht Club engine)",
            "Battle Realms (Liquid Entertainment engine)"
],
        "text_formats": [
            ".json",
            ".csv",
            ".xml",
            ".txt",
            ".bin",
            ".pak"
],
        "font_tech": "Custom Implementation (TrueType, BMFont, or Texture Atlas)",
        "recommended_tools": [
            "TStudio",
            "TRun",
            "QuickBMS",
            "Hex Editor"
],
        "complexity": "Medium to High",
        "description_th": "หมวดหมู่สำหรับเกมที่มีการเขียนเอนจิ้นขึ้นมาเองเป็นการเฉพาะ (เช่น เกมค่าย Supergiant Games อย่าง Hades หรือ Noita) ระบบตรวจจับของ Modder Hub จะช่วยวิเคราะห์โครงสร้างไฟล์และเลือกเครื่องมือที่เหมาะสมที่สุดให้โดยอัตโนมัติ",
        "description_en": "General category for proprietary in-house engines such as Supergiant's Hades or Nolla's Noita. Modder Hub analyzes files to suggest the best toolchain.",
        "detection": {
            "root_files": [],
            "root_dlls": [],
            "sub_dirs": [],
            "extensions": [],
            "exe_patterns": []
},
    }
}


class EngineDatabase:
    """Master helper API for querying the global engine database."""

    _alias_cache = None

    @classmethod
    def get_all(cls):
        """Returns the full engine database dictionary."""
        return ENGINE_DATABASE

    @classmethod
    def get_engine(cls, name_or_alias):
        """Finds engine metadata by canonical name or alias."""
        if not name_or_alias:
            return ENGINE_DATABASE["Custom Engine"]

        raw = str(name_or_alias).strip()
        if raw in ENGINE_DATABASE:
            return ENGINE_DATABASE[raw]

        clean = re.sub(r'[^a-z0-9]', '', raw.lower())
        if not cls._alias_cache:
            cls._build_alias_cache()

        canonical = cls._alias_cache.get(clean)
        if canonical and canonical in ENGINE_DATABASE:
            return ENGINE_DATABASE[canonical]

        return ENGINE_DATABASE["Custom Engine"]

    @classmethod
    def normalize_name(cls, name_or_alias):
        """Converts any engine name or alias into its canonical clean name."""
        return cls.get_engine(name_or_alias).get("canonical_name", "Custom Engine")

    @classmethod
    def get_known_engine_names(cls):
        """Returns sorted list of all canonical engine names."""
        return list(ENGINE_DATABASE.keys())

    @classmethod
    def get_all_colors(cls):
        """Returns {canonical_name: hex_color}."""
        return {k: v.get("color", "#38bdf8") for k, v in ENGINE_DATABASE.items()}

    @classmethod
    def get_all_tools(cls):
        """Returns {canonical_name: [tools]}."""
        return {k: v.get("recommended_tools", ["TStudio", "TRun"]) for k, v in ENGINE_DATABASE.items()}

    @classmethod
    def get_all_exts(cls):
        """Returns {canonical_name: [exts]}."""
        return {k: v.get("text_formats", []) for k, v in ENGINE_DATABASE.items()}

    @classmethod
    def _build_alias_cache(cls):
        cls._alias_cache = {}
        for canon, data in ENGINE_DATABASE.items():
            clean_canon = re.sub(r'[^a-z0-9]', '', canon.lower())
            cls._alias_cache[clean_canon] = canon
            for alias in data.get("aliases", []):
                clean_alias = re.sub(r'[^a-z0-9]', '', alias.lower())
                cls._alias_cache[clean_alias] = canon
