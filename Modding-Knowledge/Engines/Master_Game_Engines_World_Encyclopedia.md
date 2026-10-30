# สารานุกรมเอนจิ้นเกมทั่วโลกฉบับสมบูรณ์ (Master Game Engines of the World Encyclopedia)

> **Modder Hub Engine Intelligence Archive**  
> รวบรวมและวิเคราะห์สถาปัตยกรรมเอนจิ้นเกมชั้นนำทั่วโลกจำนวน **132 เอนจิ้น**  
> สำหรับงานวิศวกรรมย้อนกลับ (Reverse Engineering), การสกัดและแปลภาษา (Localization), และระบบเรนเดอร์ฟอนต์ไทย (Thai Typography Subsystem)

---

## 📑 สารบัญเนื้อหา (Table of Contents)
1. [ภาพรวมสถาปัตยกรรมเอนจิ้นเกมทั่วโลก (Global Game Engine Architecture Hierarchy)](#1-ภาพรวมสถาปัตยกรรมเอนจิ้นเกมทั่วโลก)
2. [ตารางดัชนีเอนจิ้นเกม 132 รายการ (Master Index Table)](#2-ตารางดัชนีเอนจิ้นเกม-132-รายการ)
3. [คู่มือวิศวกรรมฟอนต์และวรรณยุกต์ภาษาไทย (Thai Typography & Font Engineering)](#3-คู่มือวิศวกรรมฟอนต์และวรรณยุกต์ภาษาไทย)
4. [สารานุกรมเจาะลึกรายเอนจิ้น (Comprehensive Engine Deep-Dive Profiles)](#4-สารานุกรมเจาะลึกรายเอนจิ้น)
5. [มาตรฐานโครงสร้างโปรเจกต์ม็อด THub 01–06 (THub Standard Workflow)](#5-มาตรฐานโครงสร้างโปรเจกต์ม็อด-thub-0106)

---

## 1. ภาพรวมสถาปัตยกรรมเอนจิ้นเกมทั่วโลก

เอนจิ้นเกมในโลกปัจจุบันสามารถแบ่งออกเป็น 5 ตระกูลใหญ่ตามลักษณะการนำไปใช้งานและการพัฒนา:

1. **Commercial Multi-Platform Engines (เอนจิ้นพาณิชย์สากล)**: เช่น Unreal Engine (1-5), Unity, CryEngine, Godot ซึ่งมีเครื่องมือแกะ/แพ็กแบบสำเร็จรูป เช่น FModel, repak, AssetRipper, UAssetGUI, quickbms
2. **AAA Proprietary In-House Studio Engines (เอนจิ้นสตูดิโอระดับโลก)**: เช่น RE Engine (Capcom), Decima (Guerrilla/Kojima), Frostbite (EA DICE), REDengine (CDPR), RAGE (Rockstar), Creation Engine (Bethesda), Dantelion (FromSoftware) กลุ่มนี้มักใช้ Container บีบอัดเฉพาะ (Oodle, ZSTD, LZ4) และตารางสตริงเฉพาะตัว
3. **Japanese JRPG & Action Specialist Engines (เอนจิ้นค่ายเกมญี่ปุ่น)**: เช่น Dragon Engine (RGG/Sega), MT Framework (Capcom), Katana/Gust (Koei Tecmo), Napishtim/Yarn (Falcom), Luminous (Square Enix), PlatinumGames In-house โครงสร้างมักเน้นตาราง Shift-JIS/UTF-8 และ Bitmap Font Atlas ที่ต้องจัดทำ glyph mapping
4. **Visual Novel & 2D Specialized Engines (เอนจิ้นวิชวลโนเวลและเกมผจญภัย 2D)**: เช่น Ren'Py (Python/RPYC), RPG Maker, Wolf RPG Editor, Kirikiri/KAG (XP3), NScripter, SiglusEngine, CatSystem2 (HGB) ซึ่งแก้ไขข้อความผ่านสคริปต์ข้อความเปิดหรือถอดรหัส bytecode ได้โดยตรง
5. **Low-Code & Indie Frameworks (เฟรมเวิร์กเกมอินดี้)**: เช่น MonoGame/XNA (C# .NET), Love2D (Lua), LibGDX (Java), PICO-8 (Virtual Machine) มักฝังข้อมูลและฟอนต์ไว้ในโค้ด C#/Lua/Bytecode

---

## 2. ตารางดัชนีเอนจิ้นเกม 132 รายการ

| ลำดับ | ชื่อเอนจิ้น (Canonical Name) | ผู้พัฒนา (Developer) | สัญชาติ | หมวดหมู่ (Category) | ไฟล์ข้อความ/แพ็กเกจหลัก | เครื่องมือแนะนำ | ความยาก |
|:---:|:---|:---|:---:|:---|:---|:---|:---:|
| 1 | **Unreal Engine 5** | Epic Games | USA | Commercial AAA 3D | `.locres, .pak, .ucas` | repak, FModel | Medium |
| 2 | **Unreal Engine 4** | Epic Games | USA | Commercial AAA 3D | `.locres, .pak, .uasset` | repak, FModel | Easy to Medium |
| 3 | **Unreal Engine 3** | Epic Games | USA | Commercial AAA 3D (Classic) | `.upk, .txt, .int` | UDK MCP, TStudio | High |
| 4 | **Unreal Engine 2** | Epic Games | USA | Classic 3D Commercial | `.u, .int, .ini` | TStudio, TRun | High |
| 5 | **Unreal Engine 1** | Epic Games | USA | Retro 3D Commercial | `.int, .ini, .u` | UnrealEd, TStudio | Medium |
| 6 | **Unreal Engine** | Epic Games | USA | Commercial AAA 3D | `.locres, .pak, .ucas` | repak, FModel | Medium |
| 7 | **Unity** | Unity Technologies | USA / Denmark | Commercial Multi-Platform 2D/3D | `.assets, .bundle, .json` | UnityPy, UABEA | Easy to Medium |
| 8 | **CryEngine** | Crytek | Germany | Commercial AAA 3D | `.pak, .xml, .gfx` | QuickBMS, CryPak | Medium to High |
| 9 | **Amazon Lumberyard / O3DE** | Amazon Game Tech / Linux Foundation | USA | Open-Source / Commercial AAA 3D | `.pak, .xml, .json` | QuickBMS, TStudio | High |
| 10 | **Godot Engine** | Godot Engine Community | International / Argentina | Open-Source 2D/3D | `.pck, .tscn, .po` | GDRE Tools, Godot PCK Explorer | Easy |
| 11 | **GameMaker** | YoYo Games / Opera | UK | Commercial 2D | `data.win, .csv, .json` | UndertaleModTool, UTMT Bleeding Edge | Easy |
| 12 | **Construct** | Scirra | UK | HTML5 / WebGL 2D Commercial | `.json, package.nw, c2runtime.js` | 7-Zip, TStudio | Easy |
| 13 | **Cocos2d-x / Cocos Creator** | Cocos / Chukong Technologies | China | Open-Source 2D/3D Multi-Platform | `.json, .plist, .lua` | TStudio, Plist Editor | Medium |
| 14 | **Defold** | Defold Foundation / King | Sweden | Lightweight 2D/3D Commercial | `.dmanifest, .arcd, .json` | Defold Toolsuite, QuickBMS | Medium |
| 15 | **Unigine** | Unigine Corp | Cyprus / Russia | Enterprise / High-End 3D Simulation | `.ung, .xml, .json` | ung_extract, TStudio | Medium |
| 16 | **Flax Engine** | Flax Engine | Poland | Modern Commercial 3D Open-Source | `.flx, .json, .flaxpackage` | Flax Editor, TStudio | Medium |
| 17 | **RE Engine** | Capcom | Japan | Proprietary AAA Action/Survival | `.msg.XX, .msg, .pak` | REFramework, REE.PAK.Tool | Medium |
| 18 | **MT Framework** | Capcom | Japan | Proprietary AAA Action | `.arc, .bin, .gmd` | ARC Tool, Fluffy Mod Manager | Medium to High |
| 19 | **Classic RE Engine** | Capcom | Japan | Retro Survival Horror (PS1 Era) | `.bin, .adt, .pvd` | REtool, Hex Editor | High |
| 20 | **REDengine** | CD Projekt RED | Poland | Proprietary AAA Open-World RPG | `.w2strings, .archive, .json` | WolvenKit, w3strings encoder/decoder | Medium |
| 21 | **C-Engine** | Techland | Poland | Proprietary AAA First-Person Open-World | `.rpack, .scr, .csv` | QuickBMS, Dying Light 2 Mod Tools | Medium |
| 22 | **Chrome Engine** | Techland | Poland | Proprietary 3D Action | `.pak, .scr, .txt` | 7-Zip, QuickBMS | Easy |
| 23 | **4A Engine** | 4A Games | Ukraine / Malta | Proprietary AAA Post-Apocalyptic FPS | `.vfs0, .bin, .txt` | 4A Games Unpacker, QuickBMS | High |
| 24 | **Decima Engine** | Guerrilla Games | Netherlands | Proprietary AAA Open-World | `.bin, .core, .stream` | Decima Explorer, QuickBMS | High to Very High |
| 25 | **Naughty Dog Engine** | Naughty Dog | USA | Proprietary AAA Cinematic Action | `.psarc, .bin, .dcx` | PSARC Tool, TStudio | High |
| 26 | **Insomniac Games Engine** | Insomniac Games | USA | Proprietary AAA Open-World Action | `.toc, .archive, .stage` | SMPC Mod Tool, Insomniac Archive Tool | Medium to High |
| 27 | **Sucker Punch Engine** | Sucker Punch Productions | USA | Proprietary AAA Open-World | `.psarc, .bin, .spk` | PSARC Tool, TStudio | High |
| 28 | **Santa Monica Engine** | Santa Monica Studio | USA | Proprietary AAA Action/Adventure | `.wad, .pkg, .bin` | GOW WAD Extractor, QuickBMS | High |
| 29 | **Northlight Engine** | Remedy Entertainment | Finland | Proprietary AAA Narrative/Cinematic | `.bin, .rmd, .package` | Northlight Tool, QuickBMS | High |
| 30 | **Remedy Engine** | Remedy Entertainment | Finland | Classic 3D Action | `.bin, .ras, .mpm` | Max Payne Toolset, TStudio | Medium |
| 31 | **Ubisoft Anvil** | Ubisoft Montreal | Canada / France | Proprietary AAA Open-World | `.forge, .pck, .bin` | AnvilToolkit, QuickBMS | High |
| 32 | **Dunia Engine** | Ubisoft Montreal | Canada | Proprietary AAA Open-World FPS | `.dat, .fat, .xml` | Gibbed Dunia Tools, Far Cry Mod Installer | Medium |
| 33 | **Disrupt Engine** | Ubisoft Montreal | Canada | Proprietary AAA Modern Urban Open-World | `.dat, .fat, .xml` | Gibbed Disrupt Tools, TStudio | Medium |
| 34 | **Snowdrop** | Massive Entertainment / Ubisoft | Sweden | Proprietary AAA Dynamic 3D | `.sdf, .dat, .bin` | Snowdrop Extractor, QuickBMS | Very High |
| 35 | **Jade Engine** | Ubisoft Montpellier | France | Classic 3D Action/Adventure | `.bf, .bin` | Jade BF Ripper, QuickBMS | High |
| 36 | **Creation Engine 2** | Bethesda Game Studios | USA | Proprietary AAA Open-World RPG | `.ba2, .strings, .dlstrings` | Creation Kit 2, xEdit (SF1Edit) | Medium |
| 37 | **Creation Engine** | Bethesda Game Studios | USA | Proprietary AAA Open-World RPG | `.ba2, .bsa, .strings` | Creation Kit, xEdit (TES5Edit / FO4Edit) | Easy to Medium |
| 38 | **Gamebryo** | Gamebase / Numerical Design Limited (NDL) | USA | Commercial / Classic 3D RPG | `.bsa, .esp, .esm` | FOMM, BSA Commander | Medium |
| 39 | **id Tech 7** | id Software | USA | Proprietary AAA Ultra-Fast FPS | `.package, .resources, .json` | id-tech-7-extractor, QuickBMS | High |
| 40 | **id Tech 6** | id Software | USA | Proprietary AAA FPS | `.resources, .package, .json` | QuickBMS, TStudio | High |
| 41 | **id Tech 5** | id Software | USA | Proprietary 3D Action | `.streamed, .resources, .bimage` | QuickBMS, TStudio | Very High |
| 42 | **id Tech 3** | id Software | USA | Classic 3D Action | `.pk3, .str, .cfg` | Pakscape, 7-Zip | Easy to Medium |
| 43 | **id Tech** | id Software | USA | Proprietary FPS | `.pk3, .pk4, .wad` | Pakscape, QuickBMS | Medium |
| 44 | **Void Engine** | Arkane Studios | France | Proprietary AAA Immersive Sim | `.sharedresources, .resources, .bimage` | QuickBMS, Dishonored 2 Tool | High |
| 45 | **STEM Engine** | Tango Gameworks | Japan | Proprietary AAA Survival Horror | `.sharedresources, .resources` | QuickBMS, TStudio | High |
| 46 | **RAGE Engine** | Rockstar Games | USA / UK | Proprietary AAA Open-World Action | `.rpf, .gxt2, .gxt` | OpenIV, CodeWalker | Medium to High |
| 47 | **RenderWare** | Criterion Games | UK | Classic 3D Multi-Platform | `.img, .txd, .dff` | IMG Tool, TXD Workshop | Easy |
| 48 | **Source 2** | Valve Corporation | USA | Proprietary AAA Next-Gen 3D | `.vpk, .vdata, .txt` | VRF (Source 2 Viewer), GCFScape | Medium |
| 49 | **Source Engine** | Valve Corporation | USA | Proprietary AAA 3D Classic | `.vpk, .txt, .res` | GCFScape, VTFEdit | Easy |
| 50 | **GoldSrc** | Valve Corporation | USA | Retro 3D (Modified Quake) | `.pak, .wad, .txt` | Wally, PakExplorer | Medium |
| 51 | **FromSoftware Proprietary** | FromSoftware | Japan | Proprietary AAA Action RPG | `.bdt, .bhd, .msgbnd.dcx` | WitchyBND, Yabber | Medium to High |
| 52 | **Dragon Engine** | Ryu Ga Gotoku Studio / Sega | Japan | Proprietary AAA Action/Adventure | `.par, .bin, .po` | PAR Tool, Ryu Mod Manager (RMM) | Medium |
| 53 | **Old Yakuza Engine** | Ryu Ga Gotoku Studio / Sega | Japan | Proprietary Action (Previous-Gen) | `.par, .bin` | PAR Tool, Ryu Mod Manager | Medium |
| 54 | **Luminous Engine** | Square Enix / Luminous Productions | Japan | Proprietary AAA Open-World Action RPG | `.earc, .bin, .json` | Flagrum, Luminous Tool | High |
| 55 | **Crystal Tools** | Square Enix | Japan | Proprietary AAA RPG (PS3 Era) | `.bin, .win32.bin, .xwb` | FF13 Tool, QuickBMS | High |
| 56 | **Katana / Gust** | Gust / Koei Tecmo | Japan | Proprietary JRPG | `.rdb, .fdata, .ebm` | Gust Tools, Gust_Pak | Medium |
| 57 | **KT Engine** | Koei Tecmo / Omega Force | Japan | Proprietary Musou / Action | `.bin, .idx, linkdata` | Linkdata Tool, Koei Tecmo Tool | Medium to High |
| 58 | **Team Ninja Engine** | Team Ninja / Koei Tecmo | Japan | Proprietary Hardcore Action RPG | `.bin, .cpk, .idx` | QuickBMS, CriPakTools | High |
| 59 | **Falcom Engine** | Nihon Falcom | Japan | Proprietary JRPG | `.tbl, .dat, .pkg` | SenPatcher, ED8 Decompiler | Medium |
| 60 | **PlatinumGames** | PlatinumGames | Japan | Proprietary High-Speed Action | `.dat, .dtt, .cpk` | DAT Tool, CriPakTools | Medium to High |
| 61 | **FOX Engine** | Kojima Productions / Konami | Japan | Proprietary AAA Photorealistic Stealth/Action | `.dat, .fpk, .fpkd` | GzsTool, FtexTool | Medium to High |
| 62 | **Asura Engine** | Rebellion Developments | UK | Proprietary AAA Tactical Stealth/Action | `.asr, .asr_en, .pc_en` | Asura Extractor, QuickBMS | Medium |
| 63 | **Foundation Engine** | Crystal Dynamics / Eidos | USA | Proprietary AAA Cinematic Action/Adventure | `bigfile.000, bigfile.update.000, .bin` | Gibbed Tomb Raider Tools, QuickBMS | High |
| 64 | **Dawn Engine** | Eidos-Montréal | Canada | Proprietary AAA Immersive Cyberpunk RPG | `.dat, .bin, .archive` | QuickBMS, TStudio | High |
| 65 | **Glacier Engine** | IO Interactive | Denmark | Proprietary AAA Stealth/Action | `.rpkg, .locr, .json` | RPKG Tool, QuickBMS | Medium to High |
| 66 | **Frostbite** | EA DICE | Sweden | Proprietary AAA Dynamic 3D | `.cas, .toc, .res` | Frosty Toolsuite (Frosty Editor / Mod Manager), TStudio | High |
| 67 | **Visceral Engine** | Visceral Games / EA | USA | Proprietary Survival Horror / Action | `.str, .big, .dat` | Gibbed Dead Space Tools, QuickBMS | High |
| 68 | **Aurora Engine** | BioWare | Canada | Classic 3D RPG | `.tlk, .bif, .key` | TLK Editor, Kotor Tool | Easy to Medium |
| 69 | **Odyssey Engine** | BioWare | Canada | Classic 3D RPG | `.tlk, .bif, .rim` | Kotor Tool, TLK Editor | Medium |
| 70 | **Eclipse Engine** | BioWare | Canada | Proprietary 3D RPG | `.erf, .gda, .tlk` | DA Toolset, gdapp | Medium |
| 71 | **Infinity Engine** | BioWare / Black Isle Studios | Canada | Retro Isometric 2D RPG | `.tlk, .bif, .key` | NearInfinity, WeiDU | Medium |
| 72 | **Divinity Engine** | Larian Studios | Belgium | Proprietary AAA Isometric/Cinematic RPG | `.pak, .loca, .xml` | LSLib (Divine Tool), BG3 Mod Manager | Medium |
| 73 | **Clausewitz Engine** | Paradox Interactive | Sweden | Proprietary Grand Strategy | `.yml, .csv, .txt` | VS Code, Paradox Launcher | Easy |
| 74 | **Apex Engine** | Avalanche Studios | Sweden | Proprietary AAA Open-World Action | `.tab, .arc, .bin` | Gibbed Avalanche Tools, QuickBMS | Medium to High |
| 75 | **Saber Engine** | Saber Interactive | USA | Proprietary AAA Swarm/Physics | `.pak, .pct, .xml` | QuickBMS, SnowRunner Editor | Medium |
| 76 | **Asobo Engine** | Asobo Studio | France | Proprietary AAA Cinematic/Flight Sim | `.bin, .pck, .fsarchive` | QuickBMS, TStudio | High |
| 77 | **Crate Engine** | Crate Entertainment | USA | Proprietary ARPG (Iron Lore Titan Quest evolution) | `.arz, .arc, .txt` | ARC Tool, Grim Dawn Asset Manager | Easy |
| 78 | **10tons Engine** | 10tons Ltd | Finland | Proprietary 2D/3D Indie | `.pak, .csv, .json` | QuickBMS, 10tons Extractor | Easy |
| 79 | **FLEDGE Engine** | Deck13 | Germany | Proprietary Action RPG | `.ff, .bin` | QuickBMS, TStudio | High |
| 80 | **Genome Engine** | Piranha Bytes | Germany | Proprietary Action RPG | `.pak, .hdr, .csv` | ELEX Resource Manager, Risen Tool | Medium |
| 81 | **Essence Engine** | Relic Entertainment | Canada | Proprietary AAA Real-Time Strategy | `.sga, .ucs, .txt` | SGA Reader, Relic Modding Tool | Medium |
| 82 | **RenPy** | PyTom / Ren'Py Community | USA | Visual Novel Open-Source | `.rpa, .rpy, .rpyc` | UnRPA, rpyc decrypter | Easy |
| 83 | **RPG Maker** | Gotcha Gotcha Games / Enterbrain | Japan | 2D JRPG Creation Software | `.json, .rvdata2, .rxdata` | RPG Maker Decrypter, RPGMakerMV-Extract | Easy |
| 84 | **Wolf RPG Editor** | SmokingWOLF | Japan | 2D Indie RPG/Adventure | `.wolf, .dat` | Wolf Decryptor, WolfTrans | Medium |
| 85 | **Kirikiri** | WXP / Kazuki Ohta | Japan | Visual Novel Engine | `.xp3, .ks, .tjs` | XP3Viewer, KrkrExtract | Easy to Medium |
| 86 | **NScripter / ONScripter** | Naoki Takahashi | Japan | Classic Visual Novel Engine | `nscript.dat, 0.txt, arc.nsa` | NSDEC, NSA Extractor | Easy |
| 87 | **SiglusEngine** | Visual Arts / Key | Japan | Proprietary Visual Novel Engine | `Gameexe.dat, .pck, .g00` | SiglusExtract, RealLiveMax | High |
| 88 | **CatSystem2** | Windmill | Japan | Proprietary Visual Novel Engine | `.int, .cst, .fes` | cs2_decompiler, intExtract | Medium |
| 89 | **BGI / Ethornell** | Buriko General Interpreter | Japan | Proprietary Visual Novel Engine | `.arc, ._bp` | BGI Tool, Sys4 Editor | Medium |
| 90 | **Adventure Game Studio** | Chris Jones / AGS Community | UK | Point & Click 2D Adventure | `.ags, ac2game.dta, .tra` | AGS Editor, AGS Unpacker | Easy |
| 91 | **SCUMM** | LucasArts (Ron Gilbert & Aric Wilmunder) | USA | Retro Point & Click Adventure | `.000, .001, .sou` | ScummVM Tools, SCUMM Revisited | Medium |
| 92 | **Build Engine** | Ken Silverman / 3D Realms | USA | Retro 2.5D FPS | `.grp, .con, .def` | eDuke32, GRP Explorer | Medium |
| 93 | **MonoGame / XNA** | Microsoft / MonoGame Team | USA | C# .NET Indie Game Framework | `.xnb, .json, .yaml` | XNB Extract, SMAPI (Stardew) | Easy |
| 94 | **Love2D** | LÖVE Development Team | International | Lua 2D Game Framework | `.love, .lua, .json` | 7-Zip, Lovely (Balatro Mod Loader) | Easy |
| 95 | **Java / LibGDX** | Badlogic Games / Mojang | International | Java Multi-Platform Game Framework | `.jar, .zip, .json` | ModTheSpire, 7-Zip | Easy |
| 96 | **PICO-8** | Lexaloffle Games | International | Fantasy Console 8-bit | `.p8, .p8.png` | PICO-8 Console, Text Editor | Medium |
| 97 | **PopCap Framework** | PopCap Games | USA | Casual 2D Framework | `.pak, .txt, .xml` | PopCap PAK Extractor, QuickBMS | Easy |
| 98 | **IW Engine** | Infinity Ward / Activision | USA | Proprietary AAA FPS | `.iwd, .ff, .zone` | Greyhound, Cordycep | High |
| 99 | **Evolution Engine** | Digital Extremes | Canada | Proprietary AAA Live-Service Action | `.toc, .pkg, .cache` | QuickBMS, Evolution Engine Tool | High |
| 100 | **Quantic Dream Engine** | Quantic Dream | France | Proprietary Interactive Narrative/Cinematic | `.dax, .idx, .bin` | QuickBMS, Detroit Localization Tool | High |
| 101 | **Silk Engine** | Spiders | France | Proprietary Action RPG | `.spk, .bin, .xml` | QuickBMS, Spiders SPK Extractor | Medium |
| 102 | **Iron Engine** | Volition | USA | Proprietary Open-World Destruction/Action | `.vpp_pc, .str2_pc, .le_strings` | Gibbed Saints Row Tools, ThomasJepp Tools | Medium |
| 103 | **TW Engine** | Creative Assembly | UK | Proprietary Grand Tactical/RTS | `.pack, .loc, .tsv` | RPFM (Rusted PackFile Manager), Pack File Manager (PFM) | Easy to Medium |
| 104 | **LithTech** | Monolith Productions | USA | Classic FPS / Horror | `.arch00, .rez, .str` | FEAR Extractor, RezExtract | Medium |
| 105 | **Firefly Engine** | Monolith Productions | USA | Proprietary AAA Action/Adventure | `.arch06, .bin, .bnd` | QuickBMS, Shadow of Mordor Tools | High |
| 106 | **Hello Games Engine** | Hello Games | UK | Proprietary Procedural Infinite Universe | `.pak, .mbin, .exml` | MBINCompiler, PSArcTool | Medium |
| 107 | **Blizzard Proprietary** | Blizzard Entertainment | USA | Proprietary AAA Strategy / Action RPG / Hero Shooter | `.mpq, .casc, .txt` | CascView, MPQEditor | High |
| 108 | **Blam Engine** | Bungie | USA | Proprietary Sci-Fi FPS | `.map, .unic, .txt` | Assembly, Halo Editing Kit (HEK) | High |
| 109 | **Tiger Engine** | Bungie | USA | Proprietary AAA MMO-FPS | `.pkg, .bin` | Destiny PKG Tool, TStudio | Very High |
| 110 | **Slipspace Engine** | 343 Industries | USA | Proprietary AAA FPS | `.module, .bin` | Slipspace Extractor, TStudio | Very High |
| 111 | **Telltale Tool** | Telltale Games | USA | Proprietary Episodic Narrative Adventure | `.ttarch, .ttarch2, .landb` | TTG Tools, Telltale Inspector | Medium |
| 112 | **Diesel Engine** | GRIN / Overkill Software (Starbreeze) | Sweden | Proprietary Cooperative FPS | `.bundle, .stream, .lua` | Diesel Bundle Modder, SuperBLT | Medium |
| 113 | **PhyreEngine** | Sony Interactive Entertainment | Japan / UK | Cross-Platform Framework (PS3/PS4/PC/Vita) | `.pkg, .cpk, .bin` | SenPatcher, QuickBMS | Medium to High |
| 114 | **Media.Vision Engine** | Media.Vision | Japan | Proprietary JRPG | `.dsarc, .bin, .mve` | DSARC Tool, QuickBMS | Medium |
| 115 | **Cygames Proprietary** | Cygames | Japan | Proprietary AAA Action RPG | `.pak, .bin, .msg` | Relink Mod Manager, QuickBMS | High |
| 116 | **Toylogic Engine** | Toylogic / Square Enix | Japan | Proprietary Action RPG | `.arc, .bin` | NieR Replicant Unpacker, QuickBMS | High |
| 117 | **Silicon Studio Engine** | Silicon Studio | Japan | Proprietary Japanese JRPG Engine | `.pak, .bin, .sge` | QuickBMS, TStudio | High |
| 118 | **NuLibrary** | Bandai Namco / CyberConnect2 | Japan | Proprietary Anime Action / JRPG | `.cpk, .xfbin, .bin` | CriPakTools, XFBIN Parser | Medium to High |
| 119 | **Vigil Engine** | Vigil Games | USA | Proprietary Action-Adventure / Hack & Slash | `.pck, .bin, .xml` | Darksiders PCK Extractor, QuickBMS | Medium |
| 120 | **Liquid Engine** | Liquid Entertainment | USA | Classic RTS 3D | `.dat, .h2o, .txt` | H2O Extractor, TStudio | Easy |
| 121 | **Pixpil Engine** | Pixpil | China | Proprietary Pixel Art 2D/3D Hybrid | `.gpk, .json, .lua` | GPK Unpacker, TStudio | Easy |
| 122 | **Yacht Club Engine** | Yacht Club Games | USA | Retro 8-bit Action Platformer | `.pak, .csv, .txt` | QuickBMS, TStudio | Easy |
| 123 | **Polyphony Digital Engine** | Polyphony Digital / Sony | Japan | Proprietary Real Driving Simulator | `.vol, .bin, .dat` | GT Toolset, TStudio | High |
| 124 | **Torque 3D** | GarageGames | USA | Open-Source / Classic Commercial 3D | `.zip, .dso, .gui` | Torque Tool, TStudio | Medium |
| 125 | **Leadwerks** | Leadwerks Software | USA | Indie 3D Commercial | `.pak, .lua, .json` | Leadwerks Editor, TStudio | Easy |
| 126 | **Stride** | Stride Community / Silicon Studio | Japan / International | Open-Source C# .NET 3D | `.sdpkg, .json` | Stride Game Studio, TStudio | Medium |
| 127 | **ZenGin** | Piranha Bytes | Germany | Classic Action RPG | `.vdf, .bin, .d` | GothicVDFS, Daedalus Decompiler | Medium |
| 128 | **Electron Engine** | Obsidian Entertainment / BioWare | USA | Classic 3D RPG | `.tlk, .zip, .erf` | NWN2 Toolset, TLK Editor | Medium |
| 129 | **CRIWARE** | CRI Middleware | Japan | Multimedia Middleware / Japanese Engine Wrapper | `.cpk, .usm, .awb` | CriPakTools, QuickBMS | Medium |
| 130 | **Marvelous Engine** | Marvelous Inc. | Japan | Proprietary Farming/JRPG Simulation | `.lzs, .bin, .csv` | LZS Decompressor, QuickBMS | Medium |
| 131 | **LEAD Engine** | Ubisoft Montreal / Red Storm | Canada / USA | Proprietary Stealth/Action | `.umd, .bin, .txt` | QuickBMS, Splinter Cell Tool | Medium |
| 132 | **Custom Engine** | Independent / Proprietary Studios | Various | In-house / Proprietary Architecture | `.json, .csv, .xml` | TStudio, TRun | Medium to High |

---

## 3. คู่มือวิศวกรรมฟอนต์และวรรณยุกต์ภาษาไทย

การดัดแปลงเกมให้รองรับภาษาไทยในระดับสากล จะต้องรับมือกับระบบฟอนต์หลัก 4 รูปแบบ:

### 3.1 รูปแบบเทคโนโลยีฟอนต์ (Font Paradigms)
1. **Dynamic TTF/OTF Vector Font (FreeType / DirectWrite / HarfBuzz)**:
   - ใช้ในเอนจิ้นสมัยใหม่ เช่น Unreal Engine (Slate Font), Unity (เมื่อใช้ UI Text แบบดั้งเดิม), Ren'Py
   - ข้อดี: คมชัดทุกขนาดเรโซลูชัน และรองรับ OpenType GPOS/GSUB อัตโนมัติ
   - การใช้งาน: ใส่ฟอนต์ภาษาไทยแท้ เช่น Noto Sans Thai, LINE Seed Sans TH ลงในเกมได้โดยตรง

2. **Signed Distance Field (SDF / Multi-Channel MSDF)**:
   - ใช้ใน TextMeshPro (Unity), Slate Distance Field (UE4/5), Godot MSDF, Custom Modern Engines
   - กลไก: เก็บระยะห่างจากเส้นขอบเวกเตอร์ลงใน Texture Atlas 2D ทำให้ขยายตัวอักษรได้ไม่แตก
   - หัวใจสำคัญ: ต้องสร้าง Asset Font Atlas ที่มีตารางพิกัด Character Mapping ครบทั้งชุดอักษรไทย (ก-ฮ, สระ, วรรณยุกต์, เลขไทย)

3. **Bitmap Font Atlas / Sprite Sheet (BMFont / FNT)**:
   - ใช้ในเกม 2D, JRPG คลาสสิก, MT Framework, RE Engine (บางส่วน), Falcom, RPG Maker
   - กลไก: ประกอบด้วยไฟล์ภาพ (.dds, .png, .tex) และไฟล์กำหนดตำแหน่งพิกัด (`.fnt`, `.bin`, `.xml`)
   - หัวใจสำคัญ: จำเป็นต้องสร้างรูปอักษรไทยลงบน Atlas พร้อมสลับหรือแทรก Glyphs เข้าไปในตารางรหัสเดิม

### 3.2 ปัญหาวรรณยุกต์ซ้อน (Tone Mark Collision) และการแก้ปัญหาด้วย PUA
- ตัวอักษรไทยที่มีหางยาวด้านบน เช่น **ป, ผ, ฝ, ฟ, ฬ** เมื่อผสมกับสระบน (อิ, อี, อึ, อื, ไม้หันอากาศ) และวรรณยุกต์ (เอก, โท, ตรี, จัตวา) จะเกิดปัญหาชนหางหรือวรรณยุกต์ลอย/จม
- **วิธีแก้ระดับสากล (Private Use Area - PUA Scheme)**:
  - ย้ายตัวอักษรวรรณยุกต์ที่ปรับตำแหน่งระดับสูง (Shifted Glyphs) ไปไว้ในรหัส PUA ช่วง `0xF700` ถึง `0xF71A`
  - ในระบบ Ai helper / Font Subsystem ของเรา ได้ทำการขยับความสูงวรรณยุกต์ขึ้น 160–200 หน่วย เพื่อให้แสดงผลได้อย่างถูกต้องสมบูรณ์แบบไม่ชนหาง

---

## 4. สารานุกรมเจาะลึกรายเอนจิ้น (Comprehensive Engine Deep-Dive Profiles)

### 📂 หมวดหมู่: Commercial AAA 3D

#### 1. Unreal Engine 5
- **ผู้พัฒนา (Developer)**: Epic Games (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#00bcff`
- **ชื่อเรียกอื่นๆ (Aliases)**: `unreal engine 5`, `unreal_engine_5`, `unrealengine5`, `ue5`, `unreal 5`

**คำอธิบาย (Overview)**:  
เอนจิ้นยุคเน็กซ์เจนเรือธงระดับโลกจาก Epic Games โดดเด่นด้วยระบบ Nanite และ Lumen ข้อความภาษาในเกมจัดเก็บในระบบ Zen Store (.utoc / .ucas) และ .pak โดยไฟล์แปลหลักคือ .locres สามารถแกะและแพ็กกลับได้ด้วย repak และแก้ไขข้อความผ่าน TStudio อย่างรวดเร็ว  
*Next-gen flagship engine by Epic Games featuring Nanite and Lumen. Localization uses Zen Store (.utoc/.ucas) and .pak with .locres binary string tables.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Black Myth: Wukong, S.T.A.L.K.E.R. 2: Heart of Chornobyl, Silent Hill 2 Remake, Tekken 8, Senua's Saga: Hellblade II, Lords of the Fallen (2023), Remnant II, RoboCop: Rogue City, The Matrix Awakens, The First Descendant, Fortnite (UE5 era)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.locres`, `.pak`, `.ucas`, `.utoc`, `.uasset`
- **ระบบฟอนต์ (Font Subsystem)**: Slate Font / Distance Field SDF / Offline TTF/OTF. รองรับ Dynamic Font และ PUA สมบูรณ์แบบ
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **repak**, **FModel**, **UnrealLocres**, **UAssetGUI**, **TStudio**, **TRun**, **ZenTools**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: engine, paks, content | รูปแบบชื่อ Exe: -win64-shipping.exe

---

#### 2. Unreal Engine 4
- **ผู้พัฒนา (Developer)**: Epic Games (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy to Medium` | **ธีมสี**: `#38bdf8`
- **ชื่อเรียกอื่นๆ (Aliases)**: `unreal engine 4`, `unreal_engine_4`, `unrealengine4`, `ue4`, `unreal 4`

**คำอธิบาย (Overview)**:  
หนึ่งในเอนจิ้นที่มีเกมสร้างมากที่สุดในโลก จัดเก็บไฟล์เกมใน .pak ข้อความแปลหลักอยู่ในไฟล์ .locres (UTF-16) และ .uasset มีเครื่องมือซัพพอร์ตล้นหลาม สามารถใช้ repak ดึง/แพ็กกลับ และสร้างม็อดใส่โฟลเดอร์ ~mods ได้ทันที  
*Widely adopted commercial engine by Epic Games. Localization relies on .locres and .uasset in standard .pak containers.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Final Fantasy VII Remake, Star Wars Jedi: Fallen Order, Star Wars Jedi: Survivor, Hogwarts Legacy, Hi-Fi Rush, Tales of Arise, Shin Megami Tensei V: Vengeance, Dragon Quest XI S, Octopath Traveler 1 & 2, Stray, Psychonauts 2, Lies of P, Hellblade: Senua's Sacrifice, Life is Strange 2, Ghostrunner

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.locres`, `.pak`, `.uasset`, `.uexp`
- **ระบบฟอนต์ (Font Subsystem)**: Slate Font / Font Face (.uasset) / Distance Field Font / TTF/OTF PUA Injection
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **repak**, **FModel**, **UnrealLocres**, **UAssetGUI**, **UE4SS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: paks, binaries/win64 | รูปแบบชื่อ Exe: -win64-shipping.exe

---

#### 3. Unreal Engine
- **ผู้พัฒนา (Developer)**: Epic Games (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#38bdf8`
- **ชื่อเรียกอื่นๆ (Aliases)**: `unreal engine`, `unreal`, `unrealengine`, `ue`

**คำอธิบาย (Overview)**:  
หมวดหมู่ทั่วไปสำหรับเกมตระกูล Unreal Engine ทุกรุ่น  
*General category for Unreal Engine family titles.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
General Unreal Engine Titles

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.locres`, `.pak`, `.ucas`, `.utoc`
- **ระบบฟอนต์ (Font Subsystem)**: Slate / SDF / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **repak**, **FModel**, **UnrealLocres**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: engine

---

#### 4. CryEngine
- **ผู้พัฒนา (Developer)**: Crytek (Germany)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium to High` | **ธีมสี**: `#06b6d4`
- **ชื่อเรียกอื่นๆ (Aliases)**: `cryengine`, `cryengine 3`, `cryengine v`, `cry engine`, `cryengine 2`, `cryengine 1`

**คำอธิบาย (Overview)**:  
เอนจิ้นกราฟิกสมจริงขั้นสุดยอดจากเยอรมนี จัดเก็บไฟล์ทั้งหมดในแพ็กเกจ .pak ข้อความแปลมักเป็นไฟล์ XML บรรจุใน Localization pak และ UI ใช้ Autodesk Scaleform GFx สำหรับเรนเดอร์ข้อความและฟอนต์ สามารถแก้ไขฟอนต์ไทยผ่าน JPEXS ได้อย่างแม่นยำ  
*Cutting-edge visual engine by Crytek. Uses .pak archives, XML text databases, and Scaleform GFx Flash font libraries.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Crysis 1, 2, 3 (Original & Remastered), Kingdom Come: Deliverance (KCD1 & KCD2), Hunt: Showdown, Sniper Ghost Warrior Contracts 1 & 2, Prey (2017), Homefront: The Revolution, Far Cry 1 (CryEngine 1)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.xml`, `.gfx`, `.tbl`, `.csv`
- **ระบบฟอนต์ (Font Subsystem)**: Scaleform GFx Font Library (gfxfontlib.gfx), TrueType via Flash, Bitmap Font
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **CryPak**, **JPEXS Free Flash Decompiler**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: system.cfg, engine.pak, crysystem.dll, cryengine.dll | DLL หลัก: crysystem.dll, cryengine.dll | โฟลเดอร์ระบุ: localized, engine | รูปแบบชื่อ Exe: kingdomcome.exe, crysis.exe

---

### 📂 หมวดหมู่: Commercial AAA 3D (Classic)

#### 5. Unreal Engine 3
- **ผู้พัฒนา (Developer)**: Epic Games (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#0284c7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `unreal engine 3`, `unreal_engine_3`, `unrealengine3`, `ue3`, `unreal 3`, `udk`

**คำอธิบาย (Overview)**:  
เอนจิ้นยอดนิยมยุค PS3/Xbox 360 บรรจุเนื้อหาในแพ็กเกจ .upk ข้อความส่วนใหญ่อยู่ในโฟลเดอร์ Localization (.int, .txt) หรือฝังใน UPK ฟอนต์เป็น Bitmap Texture ต้องแทนที่ Glyph หรือฉีดฟอนต์ผ่าน Scaleform GFx  
*Iconic generation engine using .upk packages and localized text files (.int/.txt). Fonts are typically texture-based bitmap atlases or Scaleform GFx.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Batman: Arkham Asylum / City / Origins, BioShock Infinite, Mass Effect 1, 2, 3, Borderlands 1, 2, The Pre-Sequel, Dishonored 1, XCOM: Enemy Unknown, Gears of War 1, 2, 3, DmC: Devil May Cry, Life is Strange 1, Outlast 1, Alice: Madness Returns, Remember Me, The Vanishing of Ethan Carter

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.upk`, `.txt`, `.int`, `.fra`, `.deu`, `.locres`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Texture (Font'Package.FontName') / MultiFont / Scaleform GFx
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **UDK MCP**, **TStudio**, **TRun**, **UE Viewer (UModel)**, **QuickBMS**, **Scaleform Tools**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: cookedpcconsole, cookedpc, udkgame

---

### 📂 หมวดหมู่: Classic 3D Commercial

#### 6. Unreal Engine 2
- **ผู้พัฒนา (Developer)**: Epic Games (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#0369a1`
- **ชื่อเรียกอื่นๆ (Aliases)**: `unreal engine 2`, `unreal_engine_2`, `unrealengine2`, `ue2`, `unreal 2`, `ue2.5`

**คำอธิบาย (Overview)**:  
เอนจิ้นคลาสสิกยุค 2002-2006 ข้อความและภาษาถูกเก็บเป็นไฟล์ข้อความธรรมดาตามรหัสภาษา เช่น .int, .ini หรือฝังในสคริปต์ .u ฟอนต์แปลงเป็น Texture แผ่นบิตแมปในไฟล์แพ็กเกจ  
*Classic engine era using .int/.ini text files and .u packages with bitmap texture fonts.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Tom Clancy's Splinter Cell 1, Pandora Tomorrow, Chaos Theory, BioShock 1 & 2 (Custom UE2.5), Unreal Tournament 2003 / 2004, Postal 2, Lineage II, Star Wars Republic Commando, Deus Ex: Invisible War, Thief: Deadly Shadows

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.u`, `.int`, `.ini`, `.txt`
- **ระบบฟอนต์ (Font Subsystem)**: Texture-based TrueType Bitmap rasterizer / Native Font packages
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **TStudio**, **TRun**, **UnrealEd**, **Wotgreal**, **DragonUnPACKer**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: system, maps, textures | รูปแบบชื่อ Exe: ut2004.exe, postal2.exe

---

### 📂 หมวดหมู่: Retro 3D Commercial

#### 7. Unreal Engine 1
- **ผู้พัฒนา (Developer)**: Epic Games (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#0c4a6e`
- **ชื่อเรียกอื่นๆ (Aliases)**: `unreal engine 1`, `unreal_engine_1`, `ue1`, `unreal 1`

**คำอธิบาย (Overview)**:  
ต้นกำเนิดตระกูล Unreal Engine ยุคปี 1998 การแปลเกมทำได้โดยการแปลไฟล์ข้อความภาษา .int และแก้ไขฟอนต์บิตแมปในเท็กซ์เจอร์ .utx  
*The original Unreal Engine (1998) with .int text files and .utx texture sheets.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Unreal (1998), Unreal Tournament (1999), Deus Ex (2000), Rune, Clive Barker's Undying, Wheel of Time

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.int`, `.ini`, `.u`
- **ระบบฟอนต์ (Font Subsystem)**: Monochrome / 8-bit Font Texture Sheets
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **UnrealEd**, **TStudio**, **Hex Editor**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: unreal.exe | DLL หลัก: engine.dll, core.dll | โฟลเดอร์ระบุ: system | รูปแบบชื่อ Exe: unreal.exe, deusex.exe

---

### 📂 หมวดหมู่: Commercial Multi-Platform 2D/3D

#### 8. Unity
- **ผู้พัฒนา (Developer)**: Unity Technologies (USA / Denmark)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy to Medium` | **ธีมสี**: `#22c55e`
- **ชื่อเรียกอื่นๆ (Aliases)**: `unity`, `unity engine`, `unity3d`, `unity mono`, `unity il2cpp`

**คำอธิบาย (Overview)**:  
เอนจิ้นยอดนิยมอันดับ 1 ของวงการเกมอินดี้และเกมมือถือ มีโครงสร้างแบบ Mono หรือ IL2CPP ไฟล์เกมจัดเก็บใน .assets หรือ AssetBundle (.bundle) ข้อความมักเป็น TextAsset/JSON และแสดงผลด้วย TextMeshPro ซึ่งม็อดไทยนิยมสร้าง Font Asset SDF บรรจุ PUA หรือฉีดฟอนต์ผ่าน BepInEx Hook  
*Top commercial multi-platform engine. Employs TextMeshPro SDF fonts and serialized AssetBundles. Moddable via BepInEx and AssetStudio/UABEA.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Hollow Knight, Ori and the Blind Forest / Will of the Wisps, Cuphead, Genshin Impact, Subnautica 1 & Below Zero, Valheim, Escape from Tarkov, Cities: Skylines, Outer Wilds, Risk of Rain 2, Cult of the Lamb, Sea of Stars, Sons of the Forest, Rust, Tunic, Dredge, Dave the Diver

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.assets`, `.bundle`, `.json`, `.csv`, `.txt`, `.bytes`
- **ระบบฟอนต์ (Font Subsystem)**: TextMeshPro (TMP_FontAsset / SDF Font), Bitmap Font, Dynamic TrueType Font
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **UnityPy**, **UABEA**, **AssetStudio**, **BepInEx**, **MelonLoader**, **XUnity.AutoTranslator**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: unityplayer.dll, gameassembly.dll | DLL หลัก: unityplayer.dll | โฟลเดอร์ระบุ: _data, mono, il2cpp_data

---

### 📂 หมวดหมู่: Open-Source / Commercial AAA 3D

#### 9. Amazon Lumberyard / O3DE
- **ผู้พัฒนา (Developer)**: Amazon Game Tech / Linux Foundation (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#0ea5e9`
- **ชื่อเรียกอื่นๆ (Aliases)**: `lumberyard`, `amazon lumberyard`, `o3de`, `open 3d engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นที่แยกสายการพัฒนามาจาก CryEngine โดย Amazon พัฒนาต่อเป็น Open 3D Engine (O3DE) รองรับโครงสร้างไฟล์คล้าย CryEngine (.pak) แต่ปรับปรุงระบบเน็ตเวิร์กและเอนทิตี UI สมัยใหม่  
*CryEngine fork by Amazon evolved into O3DE open source, using .pak archives and modernized UI systems.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
New World, Deadhaus Sonata, Star Citizen (StarEngine - modified Lumberyard)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.xml`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: FreeType 2 / OpenType Native / Scaleform GFx
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: system.cfg | DLL หลัก: crysystem.dll, lyengine.dll

---

### 📂 หมวดหมู่: Open-Source 2D/3D

#### 10. Godot Engine
- **ผู้พัฒนา (Developer)**: Godot Engine Community (International / Argentina)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#74c7ec`
- **ชื่อเรียกอื่นๆ (Aliases)**: `godot`, `godot engine`, `godot 4`, `godot 3`, `godotengine`

**คำอธิบาย (Overview)**:  
เอนจิ้นโอเพนซอร์สยอดนิยมอันดับ 1 ของโลก ตัวเกมรวมไฟล์แพ็กเกจเป็น .pck ไฟล์แปลนิยมใช้รูปแบบมาตรฐานสากล gettext (.po) หรือ .csv และใน Godot 4 มี TextServer HarfBuzz ในตัว ทำให้รองรับการจัดวางสระวรรณยุกต์ไทยได้อย่างถูกต้อง 100% โดยไม่ต้องแก้ฟอนต์  
*Leading free open-source engine. Uses .pck archives and standard gettext .po files. Godot 4 features native HarfBuzz text shaping with flawless Thai support.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Brotato, Cassette Beasts, Buckshot Roulette, Halls of Torment, Sonic Colors: Ultimate (Blind Squirrel engine port), Dome Keeper, Rogue State Revolution, Ex-Zodiac

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pck`, `.tscn`, `.po`, `.csv`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: Native Dynamic Font (.ttf / .otf) via FreeType / TextServer HarfBuzz (Godot 4 รองรับสระไทยสมบูรณ์แบบ)
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **GDRE Tools**, **Godot PCK Explorer**, **poedit**, **TStudio**, **TRun**

---

### 📂 หมวดหมู่: Commercial 2D

#### 11. GameMaker
- **ผู้พัฒนา (Developer)**: YoYo Games / Opera (UK)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#10b981`
- **ชื่อเรียกอื่นๆ (Aliases)**: `gamemaker`, `gamemaker studio`, `gamemaker: studio`, `gms2`, `gms`, `gamemaker studio 2`

**คำอธิบาย (Overview)**:  
เอนจิ้น 2D ชื่อดัง ตัวเกมคอมไพล์รวมทุกอย่างไว้ในไฟล์เดียว data.win (หรือ game.unx/game.ios) สามารถใช้ UndertaleModTool (UTMT) เปิดดู แก้ไขข้อความใน Strings Table และเพิ่มสระวรรณยุกต์หรือ PUA ใน Sprite Fonts ได้ง่ายดาย  
*Leading 2D engine packaging assets into a single data.win file. Fully editable via UndertaleModTool for string tables and font sprites.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Undertale, Deltarune, Hotline Miami 1 & 2, Katana ZERO, Pizza Tower, Risk of Rain (Original), Nuclear Throne, VA-11 Hall-A, Hyper Light Drifter, Forager, Gunpoint

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `data.win`, `.csv`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: Embedded Sprite Font / Font Texture Glyphs in data.win
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **UndertaleModTool**, **UTMT Bleeding Edge**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: data.win

---

### 📂 หมวดหมู่: HTML5 / WebGL 2D Commercial

#### 12. Construct
- **ผู้พัฒนา (Developer)**: Scirra (UK)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#f97316`
- **ชื่อเรียกอื่นๆ (Aliases)**: `construct`, `construct 2`, `construct 3`, `scirra construct`

**คำอธิบาย (Overview)**:  
เอนจิ้นสร้างเกม HTML5 รันบน NW.js หรือ Electron ใน Windows ไฟล์เกมถูกรวมใน package.nw (เปิดได้ด้วย 7-Zip) ข้อความมักเป็น JSON หรือตัวแปรใน JS แก้ไขง่ายมาก  
*HTML5-based game creator wrapped in NW.js/Electron. Modded by opening package.nw with 7-Zip and editing JSON/JS files.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
There Is No Game: Wrong Dimension, Iconoclasts (prototype era), The Next Penelope, Airscape: The Fall of Gravity

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.json`, `package.nw`, `c2runtime.js`, `c3runtime.js`
- **ระบบฟอนต์ (Font Subsystem)**: CSS Web Fonts / Canvas Text / SpriteFont
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **7-Zip**, **TStudio**, **Text Editor**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: package.nw, nw.exe | DLL หลัก: nw.dll, ffmpeg.dll

---

### 📂 หมวดหมู่: Open-Source 2D/3D Multi-Platform

#### 13. Cocos2d-x / Cocos Creator
- **ผู้พัฒนา (Developer)**: Cocos / Chukong Technologies (China)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#06b6d4`
- **ชื่อเรียกอื่นๆ (Aliases)**: `cocos2d-x`, `cocos`, `cocos creator`, `cocos2d`

**คำอธิบาย (Overview)**:  
เฟรมเวิร์กยอดนิยมสำหรับเกม 2D ข้ามแพลตฟอร์ม ข้อความมักเก็บใน .plist, .json หรือสคริปต์ Lua นิยมใช้ฟอนต์บิตแมป BMFont (.fnt) ร่วมกับ FreeType  
*Open-source multi-platform framework using BMFont (.fnt), FreeType, and plist/json/lua data files.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Geometry Dash, Badland 1 & 2, Fire Emblem Heroes, Dragon Ball Z Dokkan Battle, Kingdom Rush (Mobile ports)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.json`, `.plist`, `.lua`, `.csv`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font (.fnt / .png), FreeType TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **TStudio**, **Plist Editor**, **TexturePacker**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: DLL หลัก: cocos2d.dll, libcocos2d.dll | โฟลเดอร์ระบุ: resources | รูปแบบชื่อ Exe: geometrydash.exe

---

### 📂 หมวดหมู่: Lightweight 2D/3D Commercial

#### 14. Defold
- **ผู้พัฒนา (Developer)**: Defold Foundation / King (Sweden)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#f59e0b`
- **ชื่อเรียกอื่นๆ (Aliases)**: `defold`, `defold engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นขนาดเล็กกินแรมน้อยพัฒนาโดย King ข้อความถูกคอมไพล์ในคลังข้อมูล Defold (.arcd) หรือเขียนผ่านสคริปต์ Lua  
*Ultra-lightweight game engine originally from King, utilizing Lua and packed archive files (.arcd).*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Blossom Tales II, Fates of Ort, Void Scrappers

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.dmanifest`, `.arcd`, `.json`, `.lua`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Generator / Distance Field Fonts
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Defold Toolsuite**, **QuickBMS**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: game.projectc, game.arcd

---

### 📂 หมวดหมู่: Enterprise / High-End 3D Simulation

#### 15. Unigine
- **ผู้พัฒนา (Developer)**: Unigine Corp (Cyprus / Russia)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#8b5cf6`
- **ชื่อเรียกอื่นๆ (Aliases)**: `unigine`, `unigine 2`, `unigine engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นสำหรับงานจำลองเสมือนจริงและกราฟิกสมจริง ไฟล์ทั้งหมดถูกบรรจุในคลัง .ung ข้อความใช้ XML/JSON  
*High-fidelity simulation and visual engine using .ung archive packages and standard XML text formatting.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Oil Rush, Cradle, Valley Benchmark, Superposition Benchmark

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.ung`, `.xml`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: Native TrueType / TrueType Atlas Cache
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **ung_extract**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: DLL หลัก: unigine_x64.dll | โฟลเดอร์ระบุ: data

---

### 📂 หมวดหมู่: Modern Commercial 3D Open-Source

#### 16. Flax Engine
- **ผู้พัฒนา (Developer)**: Flax Engine (Poland)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#06b6d4`
- **ชื่อเรียกอื่นๆ (Aliases)**: `flax`, `flax engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นยุคใหม่สไตล์ C++ และ C# โครงสร้างคล้าย Unreal Engine ผสมผสาน Unity ทำงานรวดเร็ว  
*Modern lightweight C++/C# engine with Unreal-inspired workflow and modular packaging.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Indie titles and commercial tech demos

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.flx`, `.json`, `.flaxpackage`
- **ระบบฟอนต์ (Font Subsystem)**: SDF Font Asset / FreeType Native
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Flax Editor**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: DLL หลัก: flaxengine.dll | โฟลเดอร์ระบุ: content

---

### 📂 หมวดหมู่: Proprietary AAA Action/Survival

#### 17. RE Engine
- **ผู้พัฒนา (Developer)**: Capcom (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#f43f5e`
- **ชื่อเรียกอื่นๆ (Aliases)**: `re engine`, `reengine`, `re_engine`, `reach for the moon engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นเรือธงที่ดีที่สุดของ Capcom โดดเด่นเรื่องโฟโตเรียลลิสติกและการโหลดฉากไร้รอยต่อ ไฟล์เกมถูกบีบอัดเป็น re_chunk_xxx.pak ข้อความภาษาเก็บในฟอร์แมต .msg (เช่น .msg.22 หรือ .msg.5391) มีระบบ REFramework ที่เปิดทางให้ฉีดฟอนต์ไทยและระบบแปลเข้าไปได้แบบเรียลไทม์  
*Capcom's flagship engine powering Resident Evil, DMC5, and Monster Hunter Wilds. Uses .msg inside re_chunk_xxx.pak with native REFramework modding support.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Resident Evil 7: Biohazard, Resident Evil 2 Remake, Resident Evil 3 Remake, Resident Evil Village (RE8), Resident Evil 4 Remake, Devil May Cry 5, Monster Hunter Rise & Sunbreak, Monster Hunter Wilds, Dragon's Dogma 2, Street Fighter 6, Kunitsu-Gami: Path of the Goddess, Dead Rising Deluxe Remaster, Apollo Justice: Ace Attorney Trilogy

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.msg.XX`, `.msg`, `.pak`
- **ระบบฟอนต์ (Font Subsystem)**: SDF Font Texture Atlas (.otf / .ttf embedded in GFX / DirectDraw via REFramework PUA hook)
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **REFramework**, **REE.PAK.Tool**, **TStudio**, **TRun**, **GMR**, **Kuriimu**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: re_chunk_000.pak, reframework | DLL หลัก: dinput8.dll | รูปแบบชื่อ Exe: re7.exe, re2.exe, re3.exe

---

### 📂 หมวดหมู่: Proprietary AAA Action

#### 18. MT Framework
- **ผู้พัฒนา (Developer)**: Capcom (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium to High` | **ธีมสี**: `#eab308`
- **ชื่อเรียกอื่นๆ (Aliases)**: `mt framework`, `mtframework`, `mt_framework`

**คำอธิบาย (Overview)**:  
เอนจิ้นคลาสสิกผู้สร้างตำนานให้ Capcom ตลอดยุค PS3/PS4 ไฟล์บรรจุในแพ็กเกจ .arc ข้อความภาษาถูกเก็บในโครงสร้าง .gmd (Game Message Data) ฟอนต์เป็นแผ่น Texture บิตแมป ต้องขยายขนาดชีตและจัดเรียง Glyph ใหม่สำหรับภาษาไทย  
*Capcom's legendary previous-gen engine. Assets packed in .arc archives with text stored in .gmd binary files. Font rendering uses bitmap textures.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Monster Hunter: World & Iceborne, Dragon's Dogma: Dark Arisen, Resident Evil 5 & 6, Resident Evil: Revelations 1 & 2, Devil May Cry 4 & Special Edition, Dead Rising 1 & 2, Marvel vs. Capcom 3, Mega Man 11, Lost Planet 1 & 2, DuckTales: Remastered

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.arc`, `.bin`, `.gmd`, `.msg`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Sheets (.gfd / .tex / .dds) / MultiFont
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **ARC Tool**, **Fluffy Mod Manager**, **GMD Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: nativepc, nativedx10, nativedx11 | รูปแบบชื่อ Exe: monsterhunterworld.exe, ddda.exe, re5dx9.exe

---

### 📂 หมวดหมู่: Retro Survival Horror (PS1 Era)

#### 19. Classic RE Engine
- **ผู้พัฒนา (Developer)**: Capcom (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#dc2626`
- **ชื่อเรียกอื่นๆ (Aliases)**: `classic re`, `classic_re`, `biohazard engine`, `classic resident evil`

**คำอธิบาย (Overview)**:  
เอนจิ้น Resident Evil ยุคดั้งเดิมบน PS1/PC ยุค 90 ข้อความฝังในไบนารีและสคริปต์ห้อง (Room data) ฟอนต์เป็นรูปภาพ TIM ขนาดเล็ก  
*Classic 90s survival horror engine storing text within room data and rendering fonts from small TIM textures.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Resident Evil (1996), Resident Evil 2 (1998), Resident Evil 3: Nemesis (1999)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.bin`, `.adt`, `.pvd`, `.rofs`
- **ระบบฟอนต์ (Font Subsystem)**: 16-color 4-bit / 8-bit TIM / VRAM Texture Bitmaps
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **REtool**, **Hex Editor**, **TIM2Viewer**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: bio2.exe, bio3.exe, residentevil.exe | โฟลเดอร์ระบุ: pl0, pl1 | รูปแบบชื่อ Exe: bio2.exe, bio3.exe

---

### 📂 หมวดหมู่: Proprietary AAA Open-World RPG

#### 20. REDengine
- **ผู้พัฒนา (Developer)**: CD Projekt RED (Poland)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#c084fc`
- **ชื่อเรียกอื่นๆ (Aliases)**: `redengine`, `redengine 3`, `redengine 4`, `red engine`, `red_engine`, `redengine 2`

**คำอธิบาย (Overview)**:  
เอนจิ้นโลกเปิดคุณภาพสูงจากโปแลนด์ ใน The Witcher 3 ข้อความอยู่ในไฟล์ .w3strings / .w2strings บรรจุใน .bundle และใน Cyberpunk 2077 อยู่ใน .archive แก้ไขข้อความได้ผ่าน WolvenKit และ w3strings tool ฟอนต์รองรับ TTF/OTF ผ่านระบบ inkUI  
*CD Projekt RED's world-class RPG engine. Localization uses .w3strings (Witcher 3) and JSON inside .archive (Cyberpunk 2077), modded via WolvenKit.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
The Witcher 2: Assassins of Kings (REDengine 1/2), The Witcher 3: Wild Hunt (REDengine 3), Cyberpunk 2077 & Phantom Liberty (REDengine 4)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.w2strings`, `.archive`, `.json`, `.w3strings`
- **ระบบฟอนต์ (Font Subsystem)**: FreeType Vector Font Package / Cyberpunk inkHUD Font (.inkfont)
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **WolvenKit**, **w3strings encoder/decoder**, **CyberCAT**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: witcher3.exe, cyberpunk2077.exe | โฟลเดอร์ระบุ: r6, content/content0 | รูปแบบชื่อ Exe: witcher3.exe, cyberpunk2077.exe

---

#### 21. Creation Engine 2
- **ผู้พัฒนา (Developer)**: Bethesda Game Studios (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#f59e0b`
- **ชื่อเรียกอื่นๆ (Aliases)**: `creation engine 2`, `creation 2`, `creationengine2`

**คำอธิบาย (Overview)**:  
วิวัฒนาการล่าสุดของเอนจิ้น Bethesda สำหรับ Starfield ใช้ระบบคลังข้อมูล .ba2 และไฟล์ข้อความ .strings มีระบบ Creation Kit รองรับม็อดเต็มรูปแบบ  
*Next-generation Bethesda engine powering Starfield, featuring updated .ba2 archives and .strings localization tables.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Starfield, The Elder Scrolls VI (Upcoming)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.ba2`, `.strings`, `.dlstrings`, `.ilstrings`, `.esm`
- **ระบบฟอนต์ (Font Subsystem)**: Scaleform GFx / SWF Flash Fonts / Direct TTF Injection
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Creation Kit 2**, **xEdit (SF1Edit)**, **BA2 Manager**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: starfield.exe | โฟลเดอร์ระบุ: data | รูปแบบชื่อ Exe: starfield.exe

---

#### 22. Creation Engine
- **ผู้พัฒนา (Developer)**: Bethesda Game Studios (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy to Medium` | **ธีมสี**: `#fbbf24`
- **ชื่อเรียกอื่นๆ (Aliases)**: `creation engine`, `creation`, `creationengine`

**คำอธิบาย (Overview)**:  
หนึ่งในเอนจิ้นที่มีคอมมูนิตี้ม็อดใหญ่ที่สุดในโลก ไฟล์บรรจุใน .bsa หรือ .ba2 ข้อความภาษาแยกเป็นไฟล์ .strings (.dlstrings/.ilstrings) และฟอนต์ควบคุมผ่าน fontconfig.txt ในโฟลเดอร์ Interface สามารถใส่ฟอนต์ไทย TTF ได้ง่ายมาก  
*Immense modding ecosystem engine. Uses .bsa/.ba2 archives with .strings tables and fontconfig.txt pointing to TrueType SWF fonts.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
The Elder Scrolls V: Skyrim (Legendary, Special, Anniversary Editions), Fallout 4, Fallout 76

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.ba2`, `.bsa`, `.strings`, `.dlstrings`, `.ilstrings`, `.esp`, `.esm`
- **ระบบฟอนต์ (Font Subsystem)**: Flash SWF (fontconfig.txt / fonts_en.swf) / Direct TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Creation Kit**, **xEdit (TES5Edit / FO4Edit)**, **BSA Browser**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: skyrim.exe, skyrimse.exe, fallout4.exe | โฟลเดอร์ระบุ: data/interface, data/strings | รูปแบบชื่อ Exe: tesv.exe, skyrimse.exe, fallout4.exe

---

### 📂 หมวดหมู่: Proprietary AAA First-Person Open-World

#### 23. C-Engine
- **ผู้พัฒนา (Developer)**: Techland (Poland)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#84cc16`
- **ชื่อเรียกอื่นๆ (Aliases)**: `c-engine`, `cengine`, `c_engine`, `techland c-engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นยุคล่าสุดของ Techland พัฒนาต่อยอดจาก Chrome Engine เพื่อรองรับโลกเปิดขนาดใหญ่ของ Dying Light 2 ไฟล์บรรจุใน .rpack ในโฟลเดอร์ ph ข้อความอยู่ในสคริปต์ .scr และไฟล์แปลภาษา รองรับฟอนต์ TTF ภาษาไทยได้ดีเยี่ยม  
*Techland's cutting-edge open world engine powering Dying Light 2. Packages assets into .rpack archives under the 'ph' directory.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Dying Light 2: Stay Human, Dying Light: The Beast

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.rpack`, `.scr`, `.csv`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: Dynamic TrueType Font Atlas (.ttf) embedded in rpack packages
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **Dying Light 2 Mod Tools**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: DLL หลัก: rwdi.dll | โฟลเดอร์ระบุ: ph, ph/source | รูปแบบชื่อ Exe: dyinglightgame_x64_rwdi.exe

---

### 📂 หมวดหมู่: Proprietary 3D Action

#### 24. Chrome Engine
- **ผู้พัฒนา (Developer)**: Techland (Poland)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#a3e635`
- **ชื่อเรียกอื่นๆ (Aliases)**: `chrome engine`, `chrome_engine`, `chrome engine 4`, `chrome engine 5`, `chrome engine 6`

**คำอธิบาย (Overview)**:  
เอนจิ้นสร้างชื่อของ Techland ไฟล์ .pak ของ Chrome Engine เป็นมาตรฐาน ZIP สามารถใช้ 7-Zip หรือ WinRAR เปิดแตกไฟล์และแพ็กกลับได้ทันที ข้อความอยู่ในไฟล์ .scr หรือ .txt ใน Data0.pak แก้ไขสะดวกมาก  
*Classic Techland engine whose .pak archives are standard ZIP containers, making text editing in .scr and .txt extremely straightforward.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Dying Light 1, Call of Juarez 1 (2006), Call of Juarez: Bound in Blood, Call of Juarez: Gunslinger, Dead Island (2011), Dead Island: Riptide, Nail'd, Sniper: Ghost Warrior 1

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.scr`, `.txt`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Generator (.fnt / .dds) / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **7-Zip**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: data | รูปแบบชื่อ Exe: coj.exe, coj2.exe, cojgunslinger.exe

---

#### 25. id Tech 5
- **ผู้พัฒนา (Developer)**: id Software (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Very High` | **ธีมสี**: `#db2777`
- **ชื่อเรียกอื่นๆ (Aliases)**: `id tech 5`, `id_tech_5`, `idtech5`

**คำอธิบาย (Overview)**:  
เอนจิ้นที่มีเทคโนโลยี MegaTexture อันเป็นเอกลักษณ์ บรรจุไฟล์ลงใน .resources  
*Famous for MegaTexture virtual texturing, storing assets in .streamed/.resources containers.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Rage (2011), Wolfenstein: The New Order, Wolfenstein: The Old Blood, The Evil Within 1

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.streamed`, `.resources`, `.bimage`
- **ระบบฟอนต์ (Font Subsystem)**: MegaTexture Virtual Texturing / TrueType TTF
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: virtualtextures, base | รูปแบบชื่อ Exe: rage.exe, wolfneworder_x64.exe, theevilwithin.exe

---

### 📂 หมวดหมู่: Proprietary AAA Post-Apocalyptic FPS

#### 26. 4A Engine
- **ผู้พัฒนา (Developer)**: 4A Games (Ukraine / Malta)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#e11d48`
- **ชื่อเรียกอื่นๆ (Aliases)**: `4a engine`, `4a_engine`, `4a`

**คำอธิบาย (Overview)**:  
เอนจิ้นที่มีระบบแสงเงาและบรรยากาศอันดับต้นๆ ของวงการ พัฒนาโดยอดีตทีมงาน S.T.A.L.K.E.R. บรรจุไฟล์เกมใน content.vfs0 ข้อความถูกเก็บเป็นโครงสร้างไบนารี .bin ฟอนต์เป็นแผ่นเท็กซ์เจอร์บิตแมป  
*Atmospheric high-fidelity FPS engine powering the Metro series. Packs assets in .vfs0 containers with binary text databases.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Metro 2033 (Original & Redux), Metro: Last Light (Original & Redux), Metro Exodus & Enhanced Edition, Arktika.1

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.vfs0`, `.bin`, `.txt`
- **ระบบฟอนต์ (Font Subsystem)**: DDS Bitmap Font Sheets / Texture Font Mapping
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **4A Games Unpacker**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: content.vfs0 | DLL หลัก: 4a.dll | รูปแบบชื่อ Exe: metro.exe, metroexodus.exe

---

### 📂 หมวดหมู่: Proprietary AAA Open-World

#### 27. Decima Engine
- **ผู้พัฒนา (Developer)**: Guerrilla Games (Netherlands)
- **ความซับซ้อนในการม็อด (Complexity)**: `High to Very High` | **ธีมสี**: `#8b5cf6`
- **ชื่อเรียกอื่นๆ (Aliases)**: `decima engine`, `decima`, `decima_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นโอเพนเวิลด์ชั้นนำระดับโลกของ Guerrilla Games ร่วมพัฒนากับ Kojima Productions ไฟล์เกมบรรจุในแพ็กเกจ .bin มีระบบ Core Assets ที่มีโครงสร้างซับซ้อน ตัวอักษรและฟอนต์ใช้ระบบเวกเตอร์ความละเอียดสูง  
*Premier open-world engine by Guerrilla Games used for Horizon and Death Stranding. Uses .bin packages and structured .core binary formats.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Horizon Zero Dawn & Remastered, Horizon Forbidden West, Death Stranding & Director's Cut, Death Stranding 2: On the Beach, Killzone: Shadow Fall, Until Dawn (PS4 Original)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.bin`, `.core`, `.stream`
- **ระบบฟอนต์ (Font Subsystem)**: Vector Distance Field SDF Font / TrueType Core Assets
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Decima Explorer**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: horizonzerodawn.exe, ds.exe

---

#### 28. Sucker Punch Engine
- **ผู้พัฒนา (Developer)**: Sucker Punch Productions (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#ef4444`
- **ชื่อเรียกอื่นๆ (Aliases)**: `sucker punch`, `sucker punch engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นโอเพนเวิลด์ความงามวิจิตรของ Ghost of Tsushima จัดเก็บไฟล์เกมหลักในคลัง .psarc  
*Visually stunning open world engine behind Ghost of Tsushima, packaging data in .psarc containers.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Ghost of Tsushima Director's Cut (PC/PS5), Ghost of Yotei, inFAMOUS: Second Son & First Light

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.psarc`, `.bin`, `.spk`
- **ระบบฟอนต์ (Font Subsystem)**: Unicode Vector Font Rendering / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **PSARC Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: ghost.exe, ghostoftsushima.exe

---

#### 29. Ubisoft Anvil
- **ผู้พัฒนา (Developer)**: Ubisoft Montreal (Canada / France)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#ca8a04`
- **ชื่อเรียกอื่นๆ (Aliases)**: `anvil`, `anvilnext`, `anvilnext 2.0`, `scimitar`, `scimitar engine`, `scimitar_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นหลักของตระกูล Assassin's Creed เดิมชื่อ Scimitar และพัฒนาเป็น AnvilNext ไฟล์เกมทั้งหมดบรรจุในแพ็กเกจ .forge ขนาดใหญ่ ข้อความถูกบีบอัดเป็นไบนารี สามารถเปิดและแก้ไขผ่าน AnvilToolkit  
*Ubisoft's primary open-world engine for Assassin's Creed and Rainbow Six. Packs assets into massive .forge containers, modded via AnvilToolkit.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Assassin's Creed (All: Mirage, Valhalla, Odyssey, Origins, Unity, Black Flag, etc.), Prince of Persia: The Forgotten Sands, Tom Clancy's Rainbow Six Siege, Immortals Fenyx Rising, For Honor, Ghost Recon Breakpoint, Ghost Recon Wildlands

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.forge`, `.pck`, `.bin`
- **ระบบฟอนต์ (Font Subsystem)**: Scaleform GFx / Distance Field Vector / TrueType embedded in Forge
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **AnvilToolkit**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: acvalhalla.exe, acodyssey.exe, acorigins.exe

---

### 📂 หมวดหมู่: Proprietary AAA Cinematic Action

#### 30. Naughty Dog Engine
- **ผู้พัฒนา (Developer)**: Naughty Dog (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#dc2626`
- **ชื่อเรียกอื่นๆ (Aliases)**: `naughty dog`, `naughty dog engine`, `naughty_dog`

**คำอธิบาย (Overview)**:  
เอนจิ้นภาพยนตร์เกมที่ทรงพลังที่สุดของ Sony ข้อความและไฟล์เกมจัดเก็บในระบบคลัง .psarc มีการจัดการสคริปต์ภาษาอย่างเป็นระบบ ฟอนต์รองรับ Unicode  
*Naughty Dog's cinematic powerhouse engine. Uses .psarc archive packages with embedded string tables.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
The Last of Us Part I (PC/PS5), The Last of Us Part II Remastered, Uncharted: Legacy of Thieves Collection (Uncharted 4 & Lost Legacy), The Last of Us (PS3/PS4 Original), Uncharted 1, 2, 3

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.psarc`, `.bin`, `.dcx`, `.txt`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Embedded / High-Res Distance Field Font
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **PSARC Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: tlou-i.exe, u4.exe

---

### 📂 หมวดหมู่: Proprietary AAA Open-World Action

#### 31. Insomniac Games Engine
- **ผู้พัฒนา (Developer)**: Insomniac Games (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium to High` | **ธีมสี**: `#0284c7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `insomniac engine`, `insomniac`, `insomniac games engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นที่ขึ้นชื่อเรื่องความเร็วในการสตรีมฉากและกราฟิกที่ลื่นไหล ในเวอร์ชัน PC บรรจุไฟล์เกมใน .archive และมีสารบัญ .toc มีเครื่องมือ SMPC Mod Tool รองรับการแก้ไขและติดตั้งม็อดอย่างเป็นระบบ  
*High-velocity streaming open-world engine. Employs .archive/.toc formats, moddable on PC via SMPC Tool.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Marvel's Spider-Man Remastered (PC), Marvel's Spider-Man: Miles Morales (PC), Marvel's Spider-Man 2, Ratchet & Clank: Rift Apart (PC), Sunset Overdrive

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.toc`, `.archive`, `.stage`, `.mod`
- **ระบบฟอนต์ (Font Subsystem)**: Direct TrueType / OTF Font Asset with Custom Shaping
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **SMPC Mod Tool**, **Insomniac Archive Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: asset_archive | รูปแบบชื่อ Exe: spider-man.exe, milesmorales.exe, riftapart.exe

---

#### 32. RAGE Engine
- **ผู้พัฒนา (Developer)**: Rockstar Games (USA / UK)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium to High` | **ธีมสี**: `#e11d48`
- **ชื่อเรียกอื่นๆ (Aliases)**: `rage engine`, `rage`, `rage_engine`, `rockstar advanced game engine`, `rockstar`

**คำอธิบาย (Overview)**:  
เอนจิ้นโลกเปิดระดับตำนานของ Rockstar Games บรรจุไฟล์เกมทั้งหมดในแพ็กเกจ .rpf สามารถใช้ OpenIV หรือ CodeWalker เปิดแก้ไขได้ ข้อความภาษาอยู่ในไฟล์ตารางข้อความ .gxt2 มีระบบม็อดที่กว้างขวาง  
*Rockstar Advanced Game Engine powering GTA and Red Dead. Data resides in .rpf archives with text stored in .gxt2 tables.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Grand Theft Auto V & Online, Grand Theft Auto IV & Episodes from Liberty City, Red Dead Redemption 1 (PC), Red Dead Redemption 2, Max Payne 3, Midnight Club: Los Angeles, Rockstar Games Presents Table Tennis

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.rpf`, `.gxt2`, `.gxt`, `.oiv`
- **ระบบฟอนต์ (Font Subsystem)**: Scaleform GFx / Texture Font Dictionary (.wtd / .ytd) / Direct TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **OpenIV**, **CodeWalker**, **GXT2 Editor**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: gta5.exe, rdr2.exe, playrdr.exe | รูปแบบชื่อ Exe: gta5.exe, gtaiv.exe, rdr2.exe

---

#### 33. Apex Engine
- **ผู้พัฒนา (Developer)**: Avalanche Studios (Sweden)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium to High` | **ธีมสี**: `#ea580c`
- **ชื่อเรียกอื่นๆ (Aliases)**: `apex engine`, `apex`, `apex_engine`, `avalanche_engine`, `avalanche engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นระเบิดภูเขาเผากระท่อมโลกเปิดของ Just Cause และ Mad Max ไฟล์เกมบรรจุในแพ็กเกจ .tab และ .arc แก้ไขได้ด้วย Gibbed Avalanche Tools  
*Open world destruction engine powering Just Cause and Mad Max. Uses .tab/.arc container archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Just Cause 2, 3, 4, Mad Max (2015), Generation Zero, theHunter: Call of the Wild, Rage 2 (co-developed with id Software), Contraband

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.tab`, `.arc`, `.bin`
- **ระบบฟอนต์ (Font Subsystem)**: Texture Glyph Atlas / Distance Field Font
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Gibbed Avalanche Tools**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: archives_win64 | รูปแบบชื่อ Exe: justcause3.exe, justcause4.exe, madmax.exe

---

### 📂 หมวดหมู่: Proprietary AAA Action/Adventure

#### 34. Santa Monica Engine
- **ผู้พัฒนา (Developer)**: Santa Monica Studio (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#b91c1c`
- **ชื่อเรียกอื่นๆ (Aliases)**: `santa monica`, `proprietary_santa_monica`, `santa monica engine`, `god of war engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นสำหรับมหากาพย์ God of War โดยเฉพาะ จัดเก็บไฟล์ในรูปแบบแพ็กเกจ .wad และ .pkg  
*Proprietary powerhouse engine designed specifically for the God of War Norse saga.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
God of War (2018 / PC), God of War Ragnarok (PC/PS5), God of War III & Remastered

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.wad`, `.pkg`, `.bin`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector SDF / Glyphs atlas
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **GOW WAD Extractor**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: gow.exe, godofwar.exe, gowragnarok.exe

---

#### 35. Dragon Engine
- **ผู้พัฒนา (Developer)**: Ryu Ga Gotoku Studio / Sega (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#dc2626`
- **ชื่อเรียกอื่นๆ (Aliases)**: `dragon engine`, `dragon_engine`, `rgg dragon engine`, `yakuza dragon engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นยุคใหม่ของสตูดิโอ Ryu Ga Gotoku โดดเด่นด้วยระบบฟิสิกส์สมจริงและกราฟิกแสงไฟนีออนยามค่ำคืน ไฟล์เกมบรรจุในคลัง .par สามารถแกะและแพ็กกลับได้ด้วย PAR Tool และจัดการม็อดผ่าน Ryu Mod Manager  
*RGG Studio's modern flagship engine powering Yakuza 6-8 and Judgment series. Packs assets in .par archives, moddable via Ryu Mod Manager.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Yakuza 6: The Song of Life, Yakuza: Kiwami 2, Judgment (Judge Eyes), Lost Judgment, Yakuza: Like a Dragon (Yakuza 7), Like a Dragon: Infinite Wealth (Yakuza 8), Like a Dragon Gaiden: The Man Who Erased His Name, Virtua Fighter 5 Ultimate Showdown

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.par`, `.bin`, `.po`, `.csv`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / Font Sheet Texture (.gfd / .dds)
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **PAR Tool**, **Ryu Mod Manager (RMM)**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: data | รูปแบบชื่อ Exe: yakuza6.exe, yakuzakiwami2.exe, judgment.exe

---

#### 36. Firefly Engine
- **ผู้พัฒนา (Developer)**: Monolith Productions (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#ca8a04`
- **ชื่อเรียกอื่นๆ (Aliases)**: `firefly engine`, `firefly`, `nemesis engine`, `monolith firefly`

**คำอธิบาย (Overview)**:  
เอนจิ้นที่มีระบบ Nemesis System อันโด่งดัง บรรจุไฟล์ใน .arch06  
*Monolith engine powering Shadow of Mordor and Shadow of War, utilizing .arch06 archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Middle-earth: Shadow of Mordor, Middle-earth: Shadow of War, Wonder Woman (Upcoming)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.arch06`, `.bin`, `.bnd`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / Scaleform GFx
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **Shadow of Mordor Tools**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: shadowofmordor.exe, shadowofwar.exe | รูปแบบชื่อ Exe: shadowofmordor.exe, shadowofwar.exe

---

### 📂 หมวดหมู่: Proprietary AAA Narrative/Cinematic

#### 37. Northlight Engine
- **ผู้พัฒนา (Developer)**: Remedy Entertainment (Finland)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#6366f1`
- **ชื่อเรียกอื่นๆ (Aliases)**: `northlight engine`, `northlight`, `northlight_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นแห่งยุคจากฟินแลนด์ โดดเด่นด้วยระบบแสง Ray Tracing / Path Tracing และการผสมผสานวิดีโอ Live-Action ไร้รอยต่อ ไฟล์เกมบรรจุใน .bin หรือ .rmd ข้อความและสคริปต์อยู่ในรูปแบบไบนารี  
*Remedy's state-of-the-art engine featuring path-tracing and live-action integration. Uses .bin and .rmd packages.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Alan Wake 2, Control & Ultimate Edition, Quantum Break, CrossfireX (Campaign)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.bin`, `.rmd`, `.package`
- **ระบบฟอนต์ (Font Subsystem)**: Distance Field SDF Font / TrueType Vector
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Northlight Tool**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: data | รูปแบบชื่อ Exe: alanwake2.exe, control.exe, quantumbreak.exe

---

### 📂 หมวดหมู่: Classic 3D Action

#### 38. Remedy Engine
- **ผู้พัฒนา (Developer)**: Remedy Entertainment (Finland)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#4f46e5`
- **ชื่อเรียกอื่นๆ (Aliases)**: `remedy engine`, `max payne engine`, `alan wake engine`, `remedycustom`

**คำอธิบาย (Overview)**:  
เอนจิ้นยุคคลาสสิกของ Remedy ใน Max Payne ใช้ไฟล์ .ras และใน Alan Wake 1 ใช้ไฟล์ .bin  
*Remedy's classic generation engine used for Max Payne 1-2 (.ras) and Alan Wake 1 (.bin).*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Alan Wake (2010), Alan Wake's American Nightmare, Max Payne 1 (2001), Max Payne 2: The Fall of Max Payne (2003)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.bin`, `.ras`, `.mpm`, `.txt`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Sheet / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Max Payne Toolset**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: maxpayne.exe, maxpayne2.exe, alanwake.exe

---

#### 39. id Tech 3
- **ผู้พัฒนา (Developer)**: id Software (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy to Medium` | **ธีมสี**: `#be185d`
- **ชื่อเรียกอื่นๆ (Aliases)**: `id tech 3`, `id_tech_3`, `idtech3`, `quake 3 engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นยอดนิยมยุค 2000 ไฟล์ .pk3 เป็นมาตรฐานไฟล์ ZIP สามารถเปิดดูด้วย 7-Zip ได้ทันที ข้อความอยู่ในไฟล์ .str และฟอนต์เป็นไฟล์บิตแมป  
*Legendary engine packaging assets into standard ZIP-based .pk3 archives with .str localization files.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Quake III Arena, Star Wars Jedi Knight II: Jedi Outcast, Star Wars Jedi Knight: Jedi Academy, Return to Castle Wolfenstein, Call of Duty 1 & 2 (Original IW Engine based on id Tech 3), Medal of Honor: Allied Assault, Soldier of Fortune II

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pk3`, `.str`, `.cfg`, `.menu`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Glyphs (.dat / .tga) in fonts/ folder
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Pakscape**, **7-Zip**, **OpenJK**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: base, gamedata | รูปแบบชื่อ Exe: jamp.exe, jasp.exe, quake3.exe

---

### 📂 หมวดหมู่: Proprietary AAA Open-World FPS

#### 40. Dunia Engine
- **ผู้พัฒนา (Developer)**: Ubisoft Montreal (Canada)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#d97706`
- **ชื่อเรียกอื่นๆ (Aliases)**: `dunia engine`, `dunia`, `dunia_engine`, `dunia 2`

**คำอธิบาย (Overview)**:  
เอนจิ้นสร้างสรรค์หมู่เกาะและทุ่งกว้างของ Far Cry ต่อยอดมาจาก CryEngine บรรจุไฟล์คู่ .dat และ .fat แก้ไขง่ายผ่าน Gibbed Dunia Tools ข้อความภาษาอยู่ในไฟล์ XML/Oasis strings  
*Ubisoft's Far Cry engine derived from CryEngine. Packages data in matching .dat/.fat archives with XML text databases.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Far Cry 2, Far Cry 3 & Blood Dragon, Far Cry 4, Far Cry Primal, Far Cry 5 & New Dawn, Far Cry 6, Avatar: The Game (2009)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.dat`, `.fat`, `.xml`, `.oasis`
- **ระบบฟอนต์ (Font Subsystem)**: Direct TrueType / OASIS Font Database / Scaleform GFx
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Gibbed Dunia Tools**, **Far Cry Mod Installer**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: data_win32 | รูปแบบชื่อ Exe: farcry3.exe, farcry4.exe, farcry5.exe

---

### 📂 หมวดหมู่: Proprietary AAA Modern Urban Open-World

#### 41. Disrupt Engine
- **ผู้พัฒนา (Developer)**: Ubisoft Montreal (Canada)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#3b82f6`
- **ชื่อเรียกอื่นๆ (Aliases)**: `disrupt engine`, `disrupt`, `disrupt_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นจำลองเมืองใหญ่และระบบแฮกของตระกูล Watch Dogs ใช้โครงสร้างไฟล์คู่ .dat/.fat คล้าย Dunia แต่ปรับแต่งสำหรับจำลองประชากรเมืองและการจราจร  
*Urban open-world engine for Watch Dogs, using .dat/.fat container archives and XML text structures.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Watch Dogs 1, Watch Dogs 2, Watch Dogs: Legion

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.dat`, `.fat`, `.xml`, `.bin`
- **ระบบฟอนต์ (Font Subsystem)**: Distance Field Font / Scaleform GFx
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Gibbed Disrupt Tools**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: data_win64 | รูปแบบชื่อ Exe: watch_dogs.exe, watchdogs2.exe, watchdogslegion.exe

---

### 📂 หมวดหมู่: Proprietary AAA Dynamic 3D

#### 42. Snowdrop
- **ผู้พัฒนา (Developer)**: Massive Entertainment / Ubisoft (Sweden)
- **ความซับซ้อนในการม็อด (Complexity)**: `Very High` | **ธีมสี**: `#0ea5e9`
- **ชื่อเรียกอื่นๆ (Aliases)**: `snowdrop`, `snowdrop engine`, `snowdrop_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นยุคใหม่ของ Ubisoft พัฒนาโดย Massive โดดเด่นด้านระบบ Node Scripting กราฟิก และระบบสภาพอากาศ ไฟล์ถูกบีบอัดสูงมากในคลัง .sdf  
*Massive Entertainment's powerhouse engine powering The Division and Star Wars Outlaws. High compression .sdf packages.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Tom Clancy's The Division 1 & 2, Avatar: Frontiers of Pandora, Star Wars Outlaws, South Park: The Fractured But Whole, Mario + Rabbids Kingdom Battle / Sparks of Hope, The Settlers: New Allies

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.sdf`, `.dat`, `.bin`
- **ระบบฟอนต์ (Font Subsystem)**: Direct SDF Font (Signed Distance Field) / TrueType Embedded
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Snowdrop Extractor**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: thedivision.exe, thedivision2.exe, outlaws.exe

---

#### 43. Frostbite
- **ผู้พัฒนา (Developer)**: EA DICE (Sweden)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#fb923c`
- **ชื่อเรียกอื่นๆ (Aliases)**: `frostbite`, `frostbite 2`, `frostbite 3`, `frostbite engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นกราฟิกระดับพระกาฬของ EA DICE โดดเด่นเรื่องการทำลายสิ่งแวดล้อม ไฟล์เกมจัดเก็บในระบบ .cas และ .toc แก้ไขและสร้างม็อดผ่าน Frosty Editor  
*EA DICE's visual powerhouse featuring destructible environments. Modded via the Frosty Toolsuite for .cas/.toc databases.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Battlefield (All: 3, 4, 1, V, 2042, Bad Company 2), Dead Space Remake (2023), Dragon Age: Inquisition, Dragon Age: The Veilguard, Mass Effect: Andromeda, Need for Speed (Heat, Unbound, Rivals), Star Wars Battlefront 1 & 2, Star Wars: Squadrons, EA Sports FC (FIFA series), Mirror's Edge Catalyst

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.cas`, `.toc`, `.res`, `.sb`
- **ระบบฟอนต์ (Font Subsystem)**: Distance Field TrueType / TrueType vector embedded in initfs_win32
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Frosty Toolsuite (Frosty Editor / Mod Manager)**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: initfs_win32 | โฟลเดอร์ระบุ: data/win32 | รูปแบบชื่อ Exe: bf4.exe, bf1.exe, bf2042.exe

---

### 📂 หมวดหมู่: Classic 3D Action/Adventure

#### 44. Jade Engine
- **ผู้พัฒนา (Developer)**: Ubisoft Montpellier (France)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#14b8a6`
- **ชื่อเรียกอื่นๆ (Aliases)**: `jade engine`, `jade`, `jade_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นระดับตำนานของผู้สร้าง Michel Ancel บรรจุเนื้อหาทั้งหมดในไฟล์ BigFile (.bf) ขนาดใหญ่เพียงไฟล์เดียว ฟอนต์เป็นแผ่นบิตแมปความละเอียดต่ำ  
*Legendary Ubisoft engine by Michel Ancel. Encapsulates all game data inside a single BigFile (.bf) container.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Beyond Good & Evil (Original & 20th Anniversary), Prince of Persia: The Sands of Time (2003), Prince of Persia: Warrior Within (2004), Prince of Persia: The Two Thrones (2005), Peter Jackson's King Kong, Rayman Raving Rabbids

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.bf`, `.bin`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Textures / TrueType Rasterized Sheets
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Jade BF Ripper**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: bge.exe, pop.exe, pop2.exe

---

### 📂 หมวดหมู่: Commercial / Classic 3D RPG

#### 45. Gamebryo
- **ผู้พัฒนา (Developer)**: Gamebase / Numerical Design Limited (NDL) (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#78716c`
- **ชื่อเรียกอื่นๆ (Aliases)**: `gamebryo`, `netimmerse`

**คำอธิบาย (Overview)**:  
รากฐานของเอนจิ้น RPG ชื่อดังยุค 2000 บรรจุไฟล์ใน .bsa ฟอนต์เป็นไฟล์บิตแมปคู่ .fnt และ .tex สามารถสร้างฟอนต์ไทยด้วย BMFont และแทนที่เข้าไปได้โดยตรง  
*Predecessor to Creation Engine powering Oblivion and Fallout New Vegas. Uses .bsa archives and .fnt bitmap fonts.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
The Elder Scrolls IV: Oblivion, Fallout 3, Fallout: New Vegas, The Elder Scrolls III: Morrowind (NetImmerse), Catherine (Atlus), Epic Mickey, Civilization IV, Bully: Scholarship Edition (NetImmerse)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.bsa`, `.esp`, `.esm`, `.txt`, `.xml`
- **ระบบฟอนต์ (Font Subsystem)**: FNT / TEX Bitmap Fonts (.fnt) in Fonts directory
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **FOMM**, **BSA Commander**, **FNVEdit**, **FO3Edit**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: fallout3.exe, falloutnv.exe, oblivion.exe, morrowind.exe | โฟลเดอร์ระบุ: data/fonts | รูปแบบชื่อ Exe: falloutnv.exe, fallout3.exe, oblivion.exe

---

### 📂 หมวดหมู่: Proprietary AAA Ultra-Fast FPS

#### 46. id Tech 7
- **ผู้พัฒนา (Developer)**: id Software (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#f43f5e`
- **ชื่อเรียกอื่นๆ (Aliases)**: `id tech 7`, `id_tech_7`, `idtech7`

**คำอธิบาย (Overview)**:  
เอนจิ้นความเร็วสูงระดับตำนาน รันด้วย Vulkan 100% จัดเก็บไฟล์ใน .package และ .resources ข้อความภาษาและสตริงถูกเข้ารหัสเฉพาะ  
*Vulkan-exclusive high-velocity FPS engine behind DOOM Eternal. Packaged in .package and .resources files.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
DOOM Eternal & The Ancient Gods Part 1 & 2

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.package`, `.resources`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: Signed Distance Field (SDF) Font Atlas / Vulkan Native
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **id-tech-7-extractor**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: doometernal.exe | โฟลเดอร์ระบุ: base | รูปแบบชื่อ Exe: doometernal.exe

---

### 📂 หมวดหมู่: Proprietary AAA FPS

#### 47. id Tech 6
- **ผู้พัฒนา (Developer)**: id Software (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#ec4899`
- **ชื่อเรียกอื่นๆ (Aliases)**: `id tech 6`, `id_tech_6`, `idtech6`

**คำอธิบาย (Overview)**:  
เอนจิ้นที่ฟื้นคืนชีพซีรีส์ DOOM ในปี 2016 จัดเก็บเนื้อหาใน .resources และ .package  
*Reboot engine for DOOM 2016 and Wolfenstein II, utilizing .resources packages.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
DOOM (2016), Wolfenstein II: The New Colossus, Wolfenstein: Youngblood

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.resources`, `.package`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector SDF / MegaTexture Font
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: doomx64.exe | โฟลเดอร์ระบุ: base | รูปแบบชื่อ Exe: doomx64.exe, newcolossus_x64.exe

---

#### 48. IW Engine
- **ผู้พัฒนา (Developer)**: Infinity Ward / Activision (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#16a34a`
- **ชื่อเรียกอื่นๆ (Aliases)**: `iw engine`, `iw`, `iw_engine`, `call of duty engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นเรือธงที่ขับเคลื่อนมหากาพย์ Call of Duty มายาวนาน พัฒนาต่อยอดมาจาก id Tech 3 บรรจุไฟล์ใน Fastfile (.ff) หรือ .iwd  
*Activision and Infinity Ward flagship engine powering the Call of Duty franchise, using Fastfile (.ff) containers.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Call of Duty: Modern Warfare (2019) & MWII/MWIII, Call of Duty: Warzone, Call of Duty: Black Ops Cold War, Call of Duty 4: Modern Warfare (Original), Call of Duty: Modern Warfare 2 (2009), Call of Duty: Black Ops (1, 2, 3, 4)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.iwd`, `.ff`, `.zone`, `.txt`, `.csv`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Texture Atlas in Fastfile (.ff) / Distance Field Font
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Greyhound**, **Cordycep**, **FFXtract**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: main, zone | รูปแบบชื่อ Exe: cod.exe, iw3sp.exe, iw4sp.exe

---

#### 49. Slipspace Engine
- **ผู้พัฒนา (Developer)**: 343 Industries (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Very High` | **ธีมสี**: `#0369a1`
- **ชื่อเรียกอื่นๆ (Aliases)**: `slipspace engine`, `slipspace`, `halo infinite engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นยุคใหม่ของแฟรนไชส์ Halo สร้างขึ้นสำหรับ Halo Infinite บรรจุไฟล์ใน .module  
*Modern 343 Industries engine designed for Halo Infinite, utilizing .module containers.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Halo Infinite

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.module`, `.bin`
- **ระบบฟอนต์ (Font Subsystem)**: Signed Distance Field Vector / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Slipspace Extractor**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: haloinfinite.exe | รูปแบบชื่อ Exe: haloinfinite.exe

---

### 📂 หมวดหมู่: Proprietary FPS

#### 50. id Tech
- **ผู้พัฒนา (Developer)**: id Software (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#ec4899`
- **ชื่อเรียกอื่นๆ (Aliases)**: `id tech`, `idtech`, `id_tech`, `id software engine`

**คำอธิบาย (Overview)**:  
หมวดหมู่ทั่วไปสำหรับเอนจิ้นตระกูล id Tech  
*General category for id Software's id Tech engine lineage.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
General id Tech titles

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pk3`, `.pk4`, `.wad`, `.resources`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Pakscape**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: base

---

### 📂 หมวดหมู่: Proprietary AAA Immersive Sim

#### 51. Void Engine
- **ผู้พัฒนา (Developer)**: Arkane Studios (France)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#a855f7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `void engine`, `void`, `void_engine`, `arkane void`

**คำอธิบาย (Overview)**:  
เอนจิ้นที่ Arkane Studios นำ id Tech 5 มาปรับแต่งขนานใหญ่เพื่อสร้างระบบ Immersive Sim ที่สมบูรณ์แบบ จัดเก็บไฟล์ใน .sharedresources  
*Customized id Tech 5 fork built by Arkane for Dishonored 2, packaging assets in .sharedresources.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Dishonored 2, Dishonored: Death of the Outsider

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.sharedresources`, `.resources`, `.bimage`
- **ระบบฟอนต์ (Font Subsystem)**: Distance Field Font / TTF embedded in resources
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **Dishonored 2 Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: dishonored2.exe | โฟลเดอร์ระบุ: base | รูปแบบชื่อ Exe: dishonored2.exe, dishonoreddot_o.exe

---

### 📂 หมวดหมู่: Proprietary AAA Survival Horror

#### 52. STEM Engine
- **ผู้พัฒนา (Developer)**: Tango Gameworks (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#b91c1c`
- **ชื่อเรียกอื่นๆ (Aliases)**: `stem engine`, `stem`, `stem_engine`, `tango stem`

**คำอธิบาย (Overview)**:  
เอนจิ้นเฉพาะตัวของ Tango Gameworks ที่พัฒนาต่อจาก id Tech เพื่อสร้างบรรยากาศหลอนใน The Evil Within 2  
*Tango Gameworks' id Tech-based customized engine powering The Evil Within 2.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
The Evil Within 2

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.sharedresources`, `.resources`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / SDF
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: teiw2.exe | โฟลเดอร์ระบุ: base | รูปแบบชื่อ Exe: theevilwithin2.exe, teiw2.exe

---

### 📂 หมวดหมู่: Classic 3D Multi-Platform

#### 53. RenderWare
- **ผู้พัฒนา (Developer)**: Criterion Games (UK)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#ea580c`
- **ชื่อเรียกอื่นๆ (Aliases)**: `renderware`, `criterion renderware`

**คำอธิบาย (Overview)**:  
เอนจิ้นยุคทอง PS2 ผู้สร้างความสำเร็จให้ GTA ภาค 3, Vice City และ San Andreas ไฟล์เก็บใน gta3.img ข้อความอยู่ใน american.gxt และฟอนต์เป็นไฟล์เท็กซ์เจอร์ fonts.txd  
*The iconic PS2-era engine behind classic GTA trilogy, storing assets in .img and fonts in fonts.txd.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Grand Theft Auto III, Grand Theft Auto: Vice City, Grand Theft Auto: San Andreas, Burnout 3: Takedown / Revenge / Paradise, Sonic Heroes, Bully (Original PS2 era), Tony Hawk's Pro Skater 3 & 4

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.img`, `.txd`, `.dff`, `.gxt`
- **ระบบฟอนต์ (Font Subsystem)**: fonts.txd (Texture Dictionary Bitmap Glyph Sheets)
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **IMG Tool**, **TXD Workshop**, **GXT Editor**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: gta-sa.exe, gta-vc.exe, gta3.exe | โฟลเดอร์ระบุ: models, text | รูปแบบชื่อ Exe: gta-sa.exe, gta-vc.exe, gta3.exe

---

### 📂 หมวดหมู่: Proprietary AAA Next-Gen 3D

#### 54. Source 2
- **ผู้พัฒนา (Developer)**: Valve Corporation (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#ea580c`
- **ชื่อเรียกอื่นๆ (Aliases)**: `source 2`, `source2`, `source_2`

**คำอธิบาย (Overview)**:  
เอนจิ้นรุ่นใหม่ล่าสุดจาก Valve ปรับปรุงจาก Source Engine เดิม ใช้ระบบ Panorama UI ที่เขียนด้วย HTML/CSS/JS ข้อความอยู่ในคลัง .vpk และรองรับฟอนต์ TTF ภาษาไทยได้ง่ายผ่าน CSS styling  
*Valve's next-gen engine powered by Panorama UI (HTML/CSS/JS). Content packed in .vpk with excellent modern typography support.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Half-Life: Alyx, Counter-Strike 2 (CS2), Dota 2, Deadlock, Aperture Desk Job

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.vpk`, `.vdata`, `.txt`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: Panorama UI / FreeType Native TrueType / TrueType Vector
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **VRF (Source 2 Viewer)**, **GCFScape**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: cs2.exe, hlvr.exe | DLL หลัก: tier0.dll, engine2.dll | โฟลเดอร์ระบุ: game/csgo, game/hlvr | รูปแบบชื่อ Exe: cs2.exe, hlvr.exe

---

### 📂 หมวดหมู่: Proprietary AAA 3D Classic

#### 55. Source Engine
- **ผู้พัฒนา (Developer)**: Valve Corporation (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#f97316`
- **ชื่อเรียกอื่นๆ (Aliases)**: `source engine`, `source`, `source_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นยอดนิยมตลอดกาลจาก Valve บรรจุไฟล์เกมใน .vpk ข้อความแปลอยู่ในโฟลเดอร์ resource (เช่น closecaption_english.txt หรือ basemodui_english.txt) ในรูปแบบ KeyValues และฟอนต์ควบคุมผ่าน ClientScheme.res สามารถใช้ฟอนต์ TTF จาก Windows ได้ทันที  
*Iconic Valve engine packing content in .vpk files. Localization uses KeyValues text in resource/ folder and ClientScheme.res for system font mapping.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Half-Life 2 (Episodes 1 & 2), Portal 1 & 2, Left 4 Dead 1 & 2, Team Fortress 2, Counter-Strike: Global Offensive (CS:GO), Counter-Strike: Source, Garry's Mod, Titanfall 1 & 2 (Customized Source), Apex Legends (Customized Source), The Stanley Parable, Vampire: The Masquerade - Bloodlines

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.vpk`, `.txt`, `.res`, `.pcf`
- **ระบบฟอนต์ (Font Subsystem)**: VGUI Font Mapping / TrueType System Fonts via ClientScheme.res
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **GCFScape**, **VTFEdit**, **Crowbar**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: hl2.exe | DLL หลัก: tier0.dll, vstdlib.dll | โฟลเดอร์ระบุ: hl2, portal2, left4dead2, csgo | รูปแบบชื่อ Exe: hl2.exe, portal2.exe, left4dead2.exe

---

### 📂 หมวดหมู่: Retro 3D (Modified Quake)

#### 56. GoldSrc
- **ผู้พัฒนา (Developer)**: Valve Corporation (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#c2410c`
- **ชื่อเรียกอื่นๆ (Aliases)**: `goldsrc`, `goldsource`, `half-life 1 engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นแรกของ Valve ที่นำเอนจิ้น Quake มาพัฒนาต่อ บรรจุเท็กซ์เจอร์ใน .wad และแพ็กเกจ .pak  
*Valve's debut engine based on modified Quake engine, utilizing .wad and .pak archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Half-Life 1 (1998), Counter-Strike 1.6, Day of Defeat, Team Fortress Classic, Sven Co-op

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.wad`, `.txt`, `.titles`
- **ระบบฟอนต์ (Font Subsystem)**: VGUI Bitmap Font Glyphs / TrueType in Steam era
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Wally**, **PakExplorer**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: hl.exe | โฟลเดอร์ระบุ: valve, cstrike | รูปแบบชื่อ Exe: hl.exe

---

### 📂 หมวดหมู่: Proprietary AAA Action RPG

#### 57. FromSoftware Proprietary
- **ผู้พัฒนา (Developer)**: FromSoftware (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium to High` | **ธีมสี**: `#475569`
- **ชื่อเรียกอื่นๆ (Aliases)**: `fromsoftware`, `fromsoftware engine`, `dantelion`, `fromsoftware proprietary`, `souls engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นเฉพาะตัวของ FromSoftware ที่สร้างความประทับใจให้เกมเมอร์ทั่วโลก บรรจุไฟล์ในคลังข้อมูล Data0.bdt/bhd ข้อความอยู่ในไฟล์ .fmg ภายในแพ็กเกจ .msgbnd.dcx แก้ไขได้ง่ายด้วย WitchyBND หรือ FMG Editor ฟอนต์เชื่อมโยงผ่าน Scaleform GFx  
*FromSoftware's renowned Soulsborne engine. Uses .bdt/.bhd archives with text stored in .fmg files inside .msgbnd.dcx packages.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Elden Ring & Shadow of the Erdtree, Dark Souls: Remastered, Dark Souls II: Scholar of the First Sin, Dark Souls III, Bloodborne, Sekiro: Shadows Die Twice, Armored Core VI: Fires of Rubicon, Demon's Souls (Original PS3)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.bdt`, `.bhd`, `.msgbnd.dcx`, `.fmg`, `.param`
- **ระบบฟอนต์ (Font Subsystem)**: Scaleform GFx / Font Sheet Atlas (.gfxfontlib) / TrueType Embedded in Layouts
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **WitchyBND**, **Yabber**, **FMG Editor**, **UXM Selective Unpacker**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: eldenring.exe, darksoulsiii.exe, sekiro.exe, armoredcore6.exe | โฟลเดอร์ระบุ: msg, param | รูปแบบชื่อ Exe: eldenring.exe, darksoulsiii.exe, darksoulsii.exe

---

#### 58. Cygames Proprietary
- **ผู้พัฒนา (Developer)**: Cygames (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#06b6d4`
- **ชื่อเรียกอื่นๆ (Aliases)**: `cygames proprietary`, `cygames`, `cygames_proprietary`, `relink engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นแอ็กชันภาพสวยงามระดับพรีเมียมของ Cygames สำหรับ Granblue Fantasy: Relink บรรจุไฟล์ใน data.pak  
*Cygames proprietary action engine created for Granblue Fantasy: Relink, packaging data in data.pak.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Granblue Fantasy: Relink

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.bin`, `.msg`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector SDF / Native FreeType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Relink Mod Manager**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: granblue_fantasy_relink.exe, data.pak | รูปแบบชื่อ Exe: granblue_fantasy_relink.exe

---

### 📂 หมวดหมู่: Proprietary Action (Previous-Gen)

#### 59. Old Yakuza Engine
- **ผู้พัฒนา (Developer)**: Ryu Ga Gotoku Studio / Sega (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#ef4444`
- **ชื่อเรียกอื่นๆ (Aliases)**: `old yakuza engine`, `rgg old engine`, `yakuza 0 engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นคลาสสิกของซีรีส์ Yakuza ก่อนยุค Dragon Engine บรรจุไฟล์ใน .par  
*Pre-Dragon Engine era powering Yakuza 0 and Kiwami 1, utilizing .par archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Yakuza 0, Yakuza Kiwami 1, Yakuza 3, 4, 5 Remastered, Fist of the North Star: Lost Paradise

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.par`, `.bin`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Glyphs in font.par / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **PAR Tool**, **Ryu Mod Manager**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: yakuza0.exe, yakuzakiwami.exe | โฟลเดอร์ระบุ: media/data | รูปแบบชื่อ Exe: yakuza0.exe, yakuzakiwami.exe

---

### 📂 หมวดหมู่: Proprietary AAA Open-World Action RPG

#### 60. Luminous Engine
- **ผู้พัฒนา (Developer)**: Square Enix / Luminous Productions (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#a855f7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `luminous engine`, `luminous`, `luminous_engine`, `luminous productions`

**คำอธิบาย (Overview)**:  
เอนจิ้นกราฟิกสุดอลังการของ Square Enix จัดเก็บไฟล์ในแพ็กเกจ .earc มีโปรแกรม Flagrum ที่ทำให้การม็อดข้อความและสกินใน FFXV ทำได้อย่างสะดวก  
*Square Enix's graphical powerhouse engine behind FFXV and Forspoken. Modded using Flagrum tool for .earc packages.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Final Fantasy XV (Windows Edition), Forspoken

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.earc`, `.bin`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: Distance Field TrueType / Vector SDF
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Flagrum**, **Luminous Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: ffxv.exe, forspoken.exe | โฟลเดอร์ระบุ: datas | รูปแบบชื่อ Exe: ffxv.exe, forspoken.exe

---

### 📂 หมวดหมู่: Proprietary AAA RPG (PS3 Era)

#### 61. Crystal Tools
- **ผู้พัฒนา (Developer)**: Square Enix (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#c084fc`
- **ชื่อเรียกอื่นๆ (Aliases)**: `crystal tools`, `crystal_tools`, `white engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นสำหรับ Final Fantasy ยุค PS3 เดิมมีชื่อว่า White Engine บรรจุไฟล์เกมใน .bin  
*Square Enix's PS3-generation RPG engine behind the FFXIII trilogy.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Final Fantasy XIII, Final Fantasy XIII-2, Lightning Returns: Final Fantasy XIII, Final Fantasy XIV (1.0 Original)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.bin`, `.win32.bin`, `.xwb`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Glyphs in .win32.bin
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **FF13 Tool**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: white_data | รูปแบบชื่อ Exe: ffxiiiimg.exe, ffxiii2img.exe

---

### 📂 หมวดหมู่: Proprietary JRPG

#### 62. Katana / Gust
- **ผู้พัฒนา (Developer)**: Gust / Koei Tecmo (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#06b6d4`
- **ชื่อเรียกอื่นๆ (Aliases)**: `katana / gust`, `gust engine`, `gust_engine`, `katana`, `gust`

**คำอธิบาย (Overview)**:  
เอนจิ้นประจำค่าย Gust ผู้สร้างซีรีส์ Atelier ปรุงยา จัดเก็บไฟล์ในแพ็กเกจ PACK00_01.DAT หรือ root.rdb ข้อความภาษาถูกจัดระเบียบในตารางไบนารี สามารถสกัดและแปลงเป็นข้อความได้ผ่าน Gust Tools  
*Engine used for the Atelier and Blue Reflection series by Gust. Uses .rdb and PACK files, moddable with Gust Tools.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Atelier Ryza 1, 2, 3, Atelier Sophie 1 & 2, Atelier Yumia, Atelier Mysterious Trilogy, Nights of Azure 1 & 2, Blue Reflection & Second Light, Fairy Tail (Gust)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.rdb`, `.fdata`, `.ebm`, `.bin`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / Bitmap Texture Sheets
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Gust Tools**, **Gust_Pak**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: data, motor | รูปแบบชื่อ Exe: atelier_ryza.exe, atelier_ryza2.exe, atelier_ryza3.exe

---

#### 63. Falcom Engine
- **ผู้พัฒนา (Developer)**: Nihon Falcom (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#ec4899`
- **ชื่อเรียกอื่นๆ (Aliases)**: `falcom engine`, `falcomengine`, `napishtim_engine`, `falcom`, `yeti engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นประจำค่าย Nihon Falcom ผู้สร้างตำนาน Trails (Kiseki) และ Ys ในเกมยุค Cold Steel และ Daybreak มีการจัดเก็บข้อความในตาราง .tbl และแพ็กเกจ .pkg รองรับฟอนต์ TTF ภาษาไทยได้สมบูรณ์แบบด้วย SenPatcher  
*Nihon Falcom's engine behind Trails and Ys series. Text resides in .tbl tables and .pkg archives, with full TTF support via SenPatcher.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
The Legend of Heroes: Trails of Cold Steel 1, 2, 3, 4, The Legend of Heroes: Trails from Zero & Trails to Azure, The Legend of Heroes: Trails into Reverie, The Legend of Heroes: Trails through Daybreak (Kuro no Kiseki), Ys VIII: Lacrimosa of DANA, Ys IX: Monstrum Nox, Ys X: Nordics, Ys: Memories of Celceta, Ys Origin, Ys: The Oath in Felghana

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.tbl`, `.dat`, `.pkg`, `.t_text`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: Direct TrueType (.ttf/.otf) mapped in ED8 font tables / SenPatcher
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **SenPatcher**, **ED8 Decompiler**, **Falcom TBL Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: data/text, text | รูปแบบชื่อ Exe: ed8.exe, ed8_2.exe, ed8_3.exe

---

#### 64. Media.Vision Engine
- **ผู้พัฒนา (Developer)**: Media.Vision (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#a855f7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `media.vision engine`, `media.vision`, `media_vision`, `mediavision`

**คำอธิบาย (Overview)**:  
เอนจิ้นของค่าย Media.Vision ผู้สร้างเกมดิจิมอนภาคดัง ไฟล์เกมถูกบรรจุใน .dsarc  
*Media.Vision in-house engine powering Digimon Story: Cyber Sleuth, utilizing .dsarc packages.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Digimon Story: Cyber Sleuth, Digimon Story: Cyber Sleuth - Hacker's Memory, Valkyria Revolution, Wild Arms series

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.dsarc`, `.bin`, `.mve`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / Bitmap Texture Glyph Sheets
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **DSARC Tool**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: data | รูปแบบชื่อ Exe: digimonstorycybersleuth.exe

---

### 📂 หมวดหมู่: Proprietary Musou / Action

#### 65. KT Engine
- **ผู้พัฒนา (Developer)**: Koei Tecmo / Omega Force (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium to High` | **ธีมสี**: `#0284c7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `kt engine`, `kt_engine`, `tecmo_engine`, `omega_engine`, `despair engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นเกมฟันแหลกแนว Musou ของ Omega Force บรรจุไฟล์เกมใน LINKDATA.BIN และไฟล์ดัชนี .IDX  
*Koei Tecmo's Musou engine behind Dynasty Warriors and Warriors Orochi. Packages data into LINKDATA.BIN and .IDX tables.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Dynasty Warriors 7, 8, 9, Samurai Warriors 4 & 5, Warriors Orochi 3 & 4 Ultimate, Fate/Samurai Remnant, Persona 5 Strikers, Dragon Quest Heroes 1 & 2, One Piece: Pirate Warriors 3 & 4, Attack on Titan 1 & 2

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.bin`, `.idx`, `linkdata`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Glyphs in LINKDATA / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Linkdata Tool**, **Koei Tecmo Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: dw8.exe, dw9.exe, wo4.exe

---

### 📂 หมวดหมู่: Proprietary Hardcore Action RPG

#### 66. Team Ninja Engine
- **ผู้พัฒนา (Developer)**: Team Ninja / Koei Tecmo (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#0369a1`
- **ชื่อเรียกอื่นๆ (Aliases)**: `team ninja engine`, `team_ninja_engine`, `team ninja`, `katana team ninja`

**คำอธิบาย (Overview)**:  
เอนจิ้นเกมต่อสู้แอ็กชันดุดันของ Team Ninja โครงสร้างจัดเก็บข้อมูลใช้แพ็กเกจไบนารีความเร็วสูง  
*High-intensity combat engine powering Nioh and Wo Long.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Nioh 1: Complete Edition, Nioh 2: Complete Edition, Wo Long: Fallen Dynasty, Stranger of Paradise: Final Fantasy Origin, Ninja Gaiden: Master Collection (Sigma 1, 2, 3 Razor's Edge), Rise of the Ronin (Ronin Engine)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.bin`, `.cpk`, `.idx`
- **ระบบฟอนต์ (Font Subsystem)**: FreeType TrueType / TrueType SDF Font
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **CriPakTools**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: nioh.exe, nioh2.exe, wolong.exe | รูปแบบชื่อ Exe: nioh.exe, nioh2.exe, wolong.exe

---

### 📂 หมวดหมู่: Proprietary High-Speed Action

#### 67. PlatinumGames
- **ผู้พัฒนา (Developer)**: PlatinumGames (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium to High` | **ธีมสี**: `#64748b`
- **ชื่อเรียกอื่นๆ (Aliases)**: `platinumgames`, `platinumgames engine`, `platinumgames_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นแอ็กชันความเร็ว 60fps อันลือชื่อ ไฟล์เกมบรรจุในแพ็กเกจ .dat และ .dtt ข้อความใน NieR: Automata ถูกบีบอัดในไฟล์แพ็กเกจ มีเครื่องมือ DAT Tool ช่วยแกะและแพ็กกลับได้  
*High-octane action engine behind NieR: Automata and Bayonetta, using .dat and .dtt containers.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
NieR: Automata, Bayonetta 1, 2, 3, Metal Gear Rising: Revengeance, Astral Chain, Vanquish, The Wonderful 101: Remastered

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.dat`, `.dtt`, `.cpk`, `.wta`, `.wtp`
- **ระบบฟอนต์ (Font Subsystem)**: Direct TrueType Font / Texture Bitmap Font in .dat
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **DAT Tool**, **CriPakTools**, **NieR Mod Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: nierautomata.exe | โฟลเดอร์ระบุ: data | รูปแบบชื่อ Exe: nierautomata.exe, metalgearrising.exe, bayonetta.exe

---

### 📂 หมวดหมู่: Proprietary AAA Photorealistic Stealth/Action

#### 68. FOX Engine
- **ผู้พัฒนา (Developer)**: Kojima Productions / Konami (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium to High` | **ธีมสี**: `#eab308`
- **ชื่อเรียกอื่นๆ (Aliases)**: `fox engine`, `fox`, `fox_engine`, `kojima fox engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นชิ้นเอกของ Hideo Kojima ก่อนแยกตัวจาก Konami โดดเด่นด้านระบบฟิสิกส์ การจัดแสงเสมือนจริง และการเรนเดอร์ระดับสูง บรรจุไฟล์เกมใน .dat และ .fpk สามารถแตกไฟล์ด้วย GzsTool  
*Hideo Kojima's masterpiece engine featuring stunning lighting and physics in MGSV, modded using GzsTool.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Metal Gear Solid V: The Phantom Pain, Metal Gear Solid V: Ground Zeroes, P.T. (Playable Teaser), eFootball PES 2014 through PES 2021, Metal Gear Survive

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.dat`, `.fpk`, `.fpkd`, `.lng`
- **ระบบฟอนต์ (Font Subsystem)**: Vector SDF Font Sheets / Scaleform GFx
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **GzsTool**, **FtexTool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: mgsvtpp.exe | โฟลเดอร์ระบุ: master | รูปแบบชื่อ Exe: mgsvtpp.exe, mgsvgz.exe, pes2021.exe

---

### 📂 หมวดหมู่: Proprietary AAA Tactical Stealth/Action

#### 69. Asura Engine
- **ผู้พัฒนา (Developer)**: Rebellion Developments (UK)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#14b8a6`
- **ชื่อเรียกอื่นๆ (Aliases)**: `asura engine`, `asura`, `asura_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นประจำค่าย Rebellion ผู้สร้างซีรีส์ Sniper Elite และ Zombie Army ไฟล์เกมทั้งหมดถูกบรรจุเป็นคลัง .asr และ .asr_en ข้อความอยู่ในสตรีมไบนารี สามารถสกัดและแพ็กกลับได้ด้วย Asura Extractor  
*Rebellion's proprietary engine powering Sniper Elite and Zombie Army series, utilizing .asr and .asr_en packages.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Sniper Elite 3, Sniper Elite 4, Sniper Elite 5, Zombie Army Trilogy, Zombie Army 4: Dead War, Evil Genius 2: World Domination, Strange Brigade, Aliens vs. Predator (2010), Rogue Trooper Redux

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.asr`, `.asr_en`, `.pc_en`, `.zip`
- **ระบบฟอนต์ (Font Subsystem)**: Compressed Font Glyph Archive (.asr.zip / .asr) / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Asura Extractor**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: sniperelite4.exe, sniperelite5.exe, za4.exe

---

### 📂 หมวดหมู่: Proprietary AAA Cinematic Action/Adventure

#### 70. Foundation Engine
- **ผู้พัฒนา (Developer)**: Crystal Dynamics / Eidos (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#6366f1`
- **ชื่อเรียกอื่นๆ (Aliases)**: `foundation engine`, `cdc engine`, `cdc`, `crystal dynamics foundation engine`, `crystal_dynamics_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นภาพยนตร์ผจญภัยของ Tomb Raider ยุค Reboot บรรจุไฟล์เกมทั้งหมดในไฟล์ขนาดใหญ่ bigfile.000 และ bigfile.update.xxx จัดการและแตกไฟล์ด้วยเครื่องมือ Gibbed Tools  
*Crystal Dynamics' engine powering the modern Tomb Raider reboot trilogy. Encapsulates assets inside bigfile.000 packages.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Tomb Raider (2013), Rise of the Tomb Raider (2015), Shadow of the Tomb Raider (2018), Deus Ex: Human Revolution, Marvel's Avengers

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `bigfile.000`, `bigfile.update.000`, `.bin`, `.pak`
- **ระบบฟอนต์ (Font Subsystem)**: Scaleform GFx / Texture Glyph Atlases / Distance Field Font
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Gibbed Tomb Raider Tools**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: tombraider.exe, rottr.exe, sottr.exe

---

### 📂 หมวดหมู่: Proprietary AAA Immersive Cyberpunk RPG

#### 71. Dawn Engine
- **ผู้พัฒนา (Developer)**: Eidos-Montréal (Canada)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#f59e0b`
- **ชื่อเรียกอื่นๆ (Aliases)**: `dawn engine`, `dawn`, `dawn_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นที่ต่อยอดมาจาก Glacier 2 เพื่อสร้างโลกไซเบอร์พังก์อันละเอียดอ่อนใน Deus Ex: Mankind Divided  
*Eidos-Montreal's tailored engine evolved from Glacier 2 for Deus Ex: Mankind Divided.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Deus Ex: Mankind Divided

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.dat`, `.bin`, `.archive`
- **ระบบฟอนต์ (Font Subsystem)**: Vector SDF Font Asset / DirectDraw
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: dxmd.exe | รูปแบบชื่อ Exe: dxmd.exe

---

### 📂 หมวดหมู่: Proprietary AAA Stealth/Action

#### 72. Glacier Engine
- **ผู้พัฒนา (Developer)**: IO Interactive (Denmark)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium to High` | **ธีมสี**: `#0284c7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `glacier engine`, `glacier`, `glacier_engine`, `glacier 2`, `glacier_2`

**คำอธิบาย (Overview)**:  
เอนจิ้นจำลองฝูงชน AI และระบบลอบเร้นระดับโลกของ IO Interactive บรรจุไฟล์เกมใน .rpkg ข้อความภาษาอยู่ในไฟล์ .locr สามารถแกะ แปล และแพ็กกลับได้อย่างแม่นยำด้วย RPKG Tool  
*IO Interactive's sophisticated crowd AI engine for the Hitman World of Assassination. Data packaged in .rpkg with .locr string databases.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Hitman: World of Assassination (Hitman 1, 2, 3), Hitman: Absolution, Kane & Lynch: Dead Men / Dog Days, Freedom Fighters, Project 007 (Upcoming)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.rpkg`, `.locr`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: Signed Distance Field (SDF) Font in RPKG / Vector TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **RPKG Tool**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: runtime | รูปแบบชื่อ Exe: hitman.exe, hitman2.exe, hitman3.exe

---

### 📂 หมวดหมู่: Proprietary Survival Horror / Action

#### 73. Visceral Engine
- **ผู้พัฒนา (Developer)**: Visceral Games / EA (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#991b1b`
- **ชื่อเรียกอื่นๆ (Aliases)**: `visceral engine`, `visceral`, `visceral_engine`, `godfather engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นอวกาศสยองขวัญของ Dead Space ไตรภาคดั้งเดิม บรรจุไฟล์เกมใน .str และ .big  
*Visceral Games' survival horror engine behind the original Dead Space trilogy.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Dead Space (2008 Original), Dead Space 2, Dead Space 3, Dante's Inferno, The Godfather 1 & 2, The Simpsons Game

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.str`, `.big`, `.dat`, `.bin`
- **ระบบฟอนต์ (Font Subsystem)**: Texture Glyph Atlas / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Gibbed Dead Space Tools**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: deadspace.exe, deadspace2.exe | รูปแบบชื่อ Exe: deadspace.exe, deadspace2.exe, deadspace3.exe

---

### 📂 หมวดหมู่: Classic 3D RPG

#### 74. Aurora Engine
- **ผู้พัฒนา (Developer)**: BioWare (Canada)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy to Medium` | **ธีมสี**: `#f97316`
- **ชื่อเรียกอื่นๆ (Aliases)**: `aurora engine`, `aurora`, `aurora_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้น RPG คลาสสิกของ BioWare ข้อความทั้งหมดจัดเก็บในไฟล์ตารางข้อความ dialog.tlk และคลังข้อมูล .bif มีเครื่องมือ TLK Editor แก้ไขภาษาไทยได้อย่างตรงไปตรงมา  
*BioWare's classic RPG engine. All dialog strings reside in dialog.tlk, easily modified via TLK Editor.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
The Witcher: Enhanced Edition (Witcher 1), Neverwinter Nights (Original & Enhanced Edition)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.tlk`, `.bif`, `.key`, `.erf`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Font / Bitmap Texture Sheets in bif
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **TLK Editor**, **Kotor Tool**, **NWN Explorer**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: dialog.tlk, chitin.key | โฟลเดอร์ระบุ: data | รูปแบบชื่อ Exe: witcher.exe, nwmain.exe

---

#### 75. Odyssey Engine
- **ผู้พัฒนา (Developer)**: BioWare (Canada)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#ea580c`
- **ชื่อเรียกอื่นๆ (Aliases)**: `odyssey engine`, `odyssey`, `odyssey_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นตระกูล Aurora ที่พัฒนาต่อเพื่อจักรวาล Star Wars ข้อความอยู่ใน dialog.tlk และฟอนต์เป็นไฟล์เท็กซ์เจอร์ TGA พร้อมเมตริก TXI  
*BioWare's Aurora-derived Star Wars engine. Uses dialog.tlk and TGA/TXI font texture pairs.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Star Wars: Knights of the Old Republic (KOTOR), Star Wars: Knights of the Old Republic II - The Sith Lords

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.tlk`, `.bif`, `.rim`, `.erf`
- **ระบบฟอนต์ (Font Subsystem)**: TXI / TGA Font Texture Glyphs (fnt_*.tga)
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Kotor Tool**, **TLK Editor**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: chitin.key, dialog.tlk | โฟลเดอร์ระบุ: override | รูปแบบชื่อ Exe: swkotor.exe, swkotor2.exe

---

#### 76. Electron Engine
- **ผู้พัฒนา (Developer)**: Obsidian Entertainment / BioWare (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#f97316`
- **ชื่อเรียกอื่นๆ (Aliases)**: `electron engine`, `electron`, `nwn2 engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นตระกูล Aurora ที่ Obsidian พัฒนาขนานใหญ่สำหรับ Neverwinter Nights 2 ข้อความอยู่ใน dialog.tlk  
*Obsidian's heavily modified Aurora successor for Neverwinter Nights 2, using dialog.tlk.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Neverwinter Nights 2 & Expansions (Mask of the Betrayer, Storm of Zehir)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.tlk`, `.zip`, `.erf`, `.trx`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / XML font definitions
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **NWN2 Toolset**, **TLK Editor**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: nwn2main.exe, dialog.tlk | รูปแบบชื่อ Exe: nwn2main.exe

---

### 📂 หมวดหมู่: Proprietary 3D RPG

#### 77. Eclipse Engine
- **ผู้พัฒนา (Developer)**: BioWare (Canada)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#c2410c`
- **ชื่อเรียกอื่นๆ (Aliases)**: `eclipse engine`, `eclipse`, `eclipse_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นสร้างชื่อของซีรีส์ Dragon Age ยุคคลาสสิก บรรจุไฟล์ใน .erf และข้อความอยู่ในตาราง .tlk และ .gda  
*BioWare's engine for Dragon Age: Origins and DA2. Uses .erf packages and .tlk string tables.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Dragon Age: Origins, Dragon Age II

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.erf`, `.gda`, `.tlk`
- **ระบบฟอนต์ (Font Subsystem)**: Scaleform GFx Flash Fonts / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **DA Toolset**, **gdapp**, **talkhelper**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: daorigins.exe | โฟลเดอร์ระบุ: packages/core | รูปแบบชื่อ Exe: daorigins.exe, dragonage2.exe

---

### 📂 หมวดหมู่: Retro Isometric 2D RPG

#### 78. Infinity Engine
- **ผู้พัฒนา (Developer)**: BioWare / Black Isle Studios (Canada)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#9a3412`
- **ชื่อเรียกอื่นๆ (Aliases)**: `infinity engine`, `infinity`, `infinity_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นไอโซเมตริก RPG คลาสสิกยอดเยี่ยมตลอดกาล ข้อความอยู่ใน dialog.tlk รองรับม็อดภาษาไทยอย่างดีในเวอร์ชัน Enhanced Edition  
*Classic isometric D&D engine. Uses dialog.tlk with robust WeiDU modding community.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Baldur's Gate 1 & 2 (Original & Enhanced Edition), Icewind Dale 1 & 2, Planescape: Torment

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.tlk`, `.bif`, `.key`
- **ระบบฟอนต์ (Font Subsystem)**: BAM Font Glyphs / TrueType in EE editions
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **NearInfinity**, **WeiDU**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: chitin.key, dialog.tlk | รูปแบบชื่อ Exe: baldur.exe, bg2main.exe, torment.exe

---

### 📂 หมวดหมู่: Proprietary AAA Isometric/Cinematic RPG

#### 79. Divinity Engine
- **ผู้พัฒนา (Developer)**: Larian Studios (Belgium)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#d97706`
- **ชื่อเรียกอื่นๆ (Aliases)**: `divinity engine`, `divinityengine`, `divinity`, `larian engine`, `divinity 4.0`

**คำอธิบาย (Overview)**:  
เอนจิ้นยอดเยี่ยมแห่งยุคของ Baldur's Gate 3 บรรจุเนื้อหาในแพ็กเกจ .pak สามารถแกะและสร้างใหม่ด้วย LSLib (Divine Tool) ข้อความภาษาถูกจัดระเบียบในไฟล์ .loca / .xml มีระบบรองรับม็อดในเกมอย่างเป็นทางการ  
*Larian's award-winning RPG engine behind Baldur's Gate 3. Packages data in .pak archives with .loca localization tables, moddable with LSLib.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Baldur's Gate 3, Divinity: Original Sin 1 & Enhanced Edition, Divinity: Original Sin 2 & Definitive Edition, Divinity II: Developer's Cut

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.loca`, `.xml`, `.lsf`, `.lsx`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / OTF embedded in Virtual Textures
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **LSLib (Divine Tool)**, **BG3 Mod Manager**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: bg3.exe, bg3_dx11.exe | โฟลเดอร์ระบุ: data/localization | รูปแบบชื่อ Exe: bg3.exe, bg3_dx11.exe, eocapp.exe

---

### 📂 หมวดหมู่: Proprietary Grand Strategy

#### 80. Clausewitz Engine
- **ผู้พัฒนา (Developer)**: Paradox Interactive (Sweden)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#0284c7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `clausewitz engine`, `clausewitz`, `jomini`, `paradox_custom`, `paradox clausewitz`

**คำอธิบาย (Overview)**:  
เอนจิ้นสำหรับเกมวางแผนมหภาคอันดับ 1 ของโลก ข้อความและภาษาอยู่ในไฟล์ข้อความ YAML (.yml) รูปแบบ UTF-8 with BOM ฟอนต์กำหนดค่าผ่านไฟล์ gui/fonts.gui ใส่ฟอนต์ไทย TTF ได้สะดวกง่ายดาย  
*Paradox's grand strategy engine. Localization is plain-text UTF-8-BOM YAML (.yml), making Thai translation and font modding very accessible.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Crusader Kings III & II, Hearts of Iron IV, Stellaris, Europa Universalis IV, Victoria 3, Imperator: Rome, Age of Wonders 4 (Triumph)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.yml`, `.csv`, `.txt`, `.gui`
- **ระบบฟอนต์ (Font Subsystem)**: OpenType / TrueType (.otf/.ttf) defined in gui/fonts.gui
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **VS Code**, **Paradox Launcher**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: game/localization, localization | รูปแบบชื่อ Exe: ck3.exe, hoi4.exe, stellaris.exe

---

### 📂 หมวดหมู่: Proprietary AAA Swarm/Physics

#### 81. Saber Engine
- **ผู้พัฒนา (Developer)**: Saber Interactive (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#059669`
- **ชื่อเรียกอื่นๆ (Aliases)**: `saber engine`, `saber`, `swarm engine`, `saber swarm`

**คำอธิบาย (Overview)**:  
เอนจิ้นที่เก่งกาจด้านการจำลองฝูงศัตรูนับพันตัว (Swarm) และระบบฟิสิกส์โคลนน้ำสมจริง ใน Space Marine 2 และ SnowRunner ไฟล์ถูกบีบอัดใน .pak  
*Proprietary swarm AI and terrain deformation engine behind Space Marine 2 and SnowRunner.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Warhammer 40,000: Space Marine 2, World War Z & Aftermath, SnowRunner, MudRunner, Expeditions: A MudRunner Game, Halo: Combat Evolved Anniversary (Campaign), Halo 2: Anniversary

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.pct`, `.xml`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / Swarm UI
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **SnowRunner Editor**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: client/packaged, en_us | รูปแบบชื่อ Exe: spacemarine2.exe, snowrunner.exe, wwz.exe

---

### 📂 หมวดหมู่: Proprietary AAA Cinematic/Flight Sim

#### 82. Asobo Engine
- **ผู้พัฒนา (Developer)**: Asobo Studio (France)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#0284c7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `asobo engine`, `asobo`, `asobo_engine`, `silas engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นที่มีคุณภาพกราฟิกและระบบจำลองฝูงหนูอันน่าทึ่งใน A Plague Tale และระบบโลกเสมือนจริงใน MSFS  
*Asobo's in-house engine for A Plague Tale and Microsoft Flight Simulator.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
A Plague Tale: Innocence, A Plague Tale: Requiem, Microsoft Flight Simulator (2020 & 2024)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.bin`, `.pck`, `.fsarchive`
- **ระบบฟอนต์ (Font Subsystem)**: Direct TrueType / OTF Font Asset with high-DPI scaling
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: aplaguetaleinnocence.exe, aplaguetalerequiem.exe, flightsimulator.exe

---

### 📂 หมวดหมู่: Proprietary ARPG (Iron Lore Titan Quest evolution)

#### 83. Crate Engine
- **ผู้พัฒนา (Developer)**: Crate Entertainment (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#d97706`
- **ชื่อเรียกอื่นๆ (Aliases)**: `crate engine`, `crate`, `crate_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นสร้างสรรค์ Grim Dawn ต่อยอดมาจาก Titan Quest ไฟล์เกมถูกบีบอัดใน .arc และฐานข้อมูล .arz ข้อความอยู่ในไฟล์ .txt ในคลัง ZIP ภาษา รองรับภาษาไทยได้ง่ายดาย  
*Iron Lore engine evolution for Grim Dawn. Text resides in simple text files inside language archives, easily modded.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Grim Dawn & Expansions (Ashes of Malmouth, Forgotten Gods, Fangs of Asterkarn), Titan Quest (Original Iron Lore engine)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.arz`, `.arc`, `.txt`
- **ระบบฟอนต์ (Font Subsystem)**: Direct TrueType Font mapped in font replacement files
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **ARC Tool**, **Grim Dawn Asset Manager**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: database.arz, grim dawn.exe | โฟลเดอร์ระบุ: resources | รูปแบบชื่อ Exe: grim dawn.exe

---

### 📂 หมวดหมู่: Proprietary 2D/3D Indie

#### 84. 10tons Engine
- **ผู้พัฒนา (Developer)**: 10tons Ltd (Finland)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#10b981`
- **ชื่อเรียกอื่นๆ (Aliases)**: `10tons engine`, `10tons`, `10tons_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นสร้างเกมแนวเอาชีวิตรอดและ Twin-stick shooter ของ 10tons ไฟล์เกมจัดเก็บใน .pak ข้อความจัดเก็บเป็นตาราง CSV หรือ JSON  
*Proprietary lightweight engine powering DYSMANTLE and Tesla vs Lovecraft, packaging CSV/JSON into .pak archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
DYSMANTLE, Tesla vs Lovecraft, Undead Horde 1 & 2, JYDGE, Neon Chrome, Crimsonland

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.csv`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: Embedded TrueType / Custom font atlas
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **10tons Extractor**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: dysmantle.exe, teslavslovecraft.exe

---

### 📂 หมวดหมู่: Proprietary Action RPG

#### 85. FLEDGE Engine
- **ผู้พัฒนา (Developer)**: Deck13 (Germany)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#f59e0b`
- **ชื่อเรียกอื่นๆ (Aliases)**: `fledge engine`, `fledge`, `fledge_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นของค่าย Deck13 จากเยอรมนี โดดเด่นด้านระบบฟิสิกส์การตัดชิ้นส่วนในซีรีส์ The Surge  
*Deck13's proprietary action RPG engine for The Surge and Atlas Fallen.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
The Surge 1, The Surge 2, Atlas Fallen, Lords of the Fallen (2014)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.ff`, `.bin`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector SDF / DirectDraw
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: thesurge.exe, thesurge2.exe, atlasfallen.exe

---

#### 86. Genome Engine
- **ผู้พัฒนา (Developer)**: Piranha Bytes (Germany)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#65a30d`
- **ชื่อเรียกอื่นๆ (Aliases)**: `genome engine`, `genome`, `genome_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นสวมบทบาทโลกเปิดที่มีเอกลักษณ์เฉพาะตัวสูงของ Piranha Bytes บรรจุไฟล์ใน .pak  
*Piranha Bytes' open world RPG engine powering Gothic 3, Risen, and ELEX.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
ELEX 1 & 2, Risen 1, 2, 3, Gothic 3

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.hdr`, `.csv`
- **ระบบฟอนต์ (Font Subsystem)**: FNT Bitmap Font / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **ELEX Resource Manager**, **Risen Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: data/ini | รูปแบบชื่อ Exe: elex.exe, elex2.exe, risen.exe

---

#### 87. Silk Engine
- **ผู้พัฒนา (Developer)**: Spiders (France)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#06b6d4`
- **ชื่อเรียกอื่นๆ (Aliases)**: `silk engine`, `silk`, `silk_engine`, `spiders engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นประจำค่าย Spiders จากฝรั่งเศส บรรจุไฟล์เกมใน .spk ข้อความจัดเก็บเป็น XML ในแพ็กเกจ  
*Spiders in-house RPG engine powering GreedFall and Steelrising, packaging content in .spk archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
GreedFall 1 & 2, Steelrising, The Technomancer, Bound by Flame

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.spk`, `.bin`, `.xml`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / Bitmap Texture Atlas
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **Spiders SPK Extractor**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: datalocal | รูปแบบชื่อ Exe: greedfall.exe, steelrising.exe, thetechnomancer.exe

---

#### 88. Toylogic Engine
- **ผู้พัฒนา (Developer)**: Toylogic / Square Enix (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#64748b`
- **ชื่อเรียกอื่นๆ (Aliases)**: `toylogic engine`, `toylogic`, `toylogic_engine`, `replicant engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นที่ Toylogic ปรับปรุงใหม่เพื่อรีเมก NieR Replicant ให้ลื่นไหลระดับ 60fps บรรจุเนื้อหาในแพ็กเกจ .arc  
*Toylogic engine built for NieR Replicant ver.1.2247..., packaging data into .arc archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
NieR Replicant ver.1.22474487139..., Warlander, Happy Wars

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.arc`, `.bin`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / Bitmap Texture Sheets
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **NieR Replicant Unpacker**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: nierreplicant.exe | โฟลเดอร์ระบุ: data | รูปแบบชื่อ Exe: nierreplicant.exe

---

### 📂 หมวดหมู่: Proprietary AAA Real-Time Strategy

#### 89. Essence Engine
- **ผู้พัฒนา (Developer)**: Relic Entertainment (Canada)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#2563eb`
- **ชื่อเรียกอื่นๆ (Aliases)**: `essence engine`, `essence`, `essence_engine`, `essence 5`

**คำอธิบาย (Overview)**:  
เอนจิ้นเกม RTS แนวหน้าของโลก บรรจุไฟล์เกมในคลัง .sga ข้อความภาษาอยู่ในไฟล์ข้อความ .ucs (Unicode String)  
*Relic's premier strategy engine for Company of Heroes and AoE4. Uses .sga archives and .ucs string files.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Company of Heroes 1, 2, 3, Warhammer 40,000: Dawn of War 1, 2, 3, Age of Empires IV

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.sga`, `.ucs`, `.txt`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector / Scaleform GFx
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **SGA Reader**, **Relic Modding Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: reliccoh.exe, reliccoh2.exe, coh3.exe

---

### 📂 หมวดหมู่: Visual Novel Open-Source

#### 90. RenPy
- **ผู้พัฒนา (Developer)**: PyTom / Ren'Py Community (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#f472b6`
- **ชื่อเรียกอื่นๆ (Aliases)**: `renpy`, `ren'py`, `ren_py`

**คำอธิบาย (Overview)**:  
เอนจิ้นนิยายภาพ (Visual Novel) ยอดนิยมอันดับ 1 ของโลก ไฟล์รวมในแพ็กเกจ .rpa สคริปต์ภาษา Python/RenPy (.rpy) มีระบบ Localization ในตัว รองรับฟอนต์ TTF ภาษาไทยได้ง่ายที่สุดในบรรดาทุกเอนจิ้น  
*World-leading visual novel engine using Python and .rpa packages. Features built-in translation system and flawless TrueType Thai font support.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Doki Doki Literature Club! (DDLC), Slay the Princess, Katawa Shoujo, Being a DIK, Scarlet Hollow, Needy Streamer Overload (partly)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.rpa`, `.rpy`, `.rpyc`
- **ระบบฟอนต์ (Font Subsystem)**: Native TrueType / OpenType (.ttf/.otf) with custom word-wrap and full Thai Unicode support
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **UnRPA**, **rpyc decrypter**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: game, renpy

---

### 📂 หมวดหมู่: 2D JRPG Creation Software

#### 91. RPG Maker
- **ผู้พัฒนา (Developer)**: Gotcha Gotcha Games / Enterbrain (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#10b981`
- **ชื่อเรียกอื่นๆ (Aliases)**: `rpg maker`, `rpgmaker`, `rpg maker mv`, `rpg maker mz`, `rpg maker vx ace`, `rpg maker xp`

**คำอธิบาย (Overview)**:  
เครื่องมือสร้างเกม RPG สไตล์ญี่ปุ่น 16-bit ที่ได้รับความนิยมสูงสุด รุ่นใหม่ (MV, MZ) ใช้ JavaScript และ HTML5 ข้อความอยู่ในไฟล์ .json ในโฟลเดอร์ data รุ่นเก่า (XP, VX Ace) ใช้ Ruby RGSS  
*Iconic JRPG creation engine. Modern versions (MV/MZ) store text in JSON, older versions (XP/VX Ace) in Ruby data files.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
OMORI (RPG Maker MV), To the Moon (RPG Maker XP), Fear & Hunger 1 & 2 (RPG Maker MV), LISA: The Painful (VX Ace), Ib (Original), The Witch's House, Mad Father (Original), Pocket Mirror, Corpse Party (Original), Space Funeral

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.json`, `.rvdata2`, `.rxdata`, `.rgssad`
- **ระบบฟอนต์ (Font Subsystem)**: Canvas Web Font (MV/MZ) / TrueType Embedded in Game.ini (XP/VX/VX Ace)
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **RPG Maker Decrypter**, **RPGMakerMV-Extract**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: game.exe | โฟลเดอร์ระบุ: data, js/plugins, www/data | รูปแบบชื่อ Exe: game.exe

---

### 📂 หมวดหมู่: 2D Indie RPG/Adventure

#### 92. Wolf RPG Editor
- **ผู้พัฒนา (Developer)**: SmokingWOLF (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#34d399`
- **ชื่อเรียกอื่นๆ (Aliases)**: `wolf rpg`, `wolf rpg editor`, `wolfrpg`

**คำอธิบาย (Overview)**:  
โปรแกรมสร้างเกมอินดี้สยองขวัญและผจญภัยชื่อดังจากญี่ปุ่น ข้อความถูกเข้ารหัสในไฟล์แพ็กเกจ .wolf แตกไฟล์ด้วย Wolf Decryptor หรือ WolfTrans  
*Popular Japanese indie adventure engine powering Mad Father and Misao. Encrypted inside .wolf archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Mad Father (Remake), Misao, The Witch's House MV, LiEat, 1BitHeart

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.wolf`, `.dat`
- **ระบบฟอนต์ (Font Subsystem)**: Windows GDI TrueType / Font mapped in Game.dat
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Wolf Decryptor**, **WolfTrans**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: game.exe | โฟลเดอร์ระบุ: data/basicdata | รูปแบบชื่อ Exe: game.exe

---

### 📂 หมวดหมู่: Visual Novel Engine

#### 93. Kirikiri
- **ผู้พัฒนา (Developer)**: WXP / Kazuki Ohta (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy to Medium` | **ธีมสี**: `#f472b6`
- **ชื่อเรียกอื่นๆ (Aliases)**: `kirikiri`, `kirikiri2`, `kirikiri z`, `krkr`, `tvp`

**คำอธิบาย (Overview)**:  
เอนจิ้นวิชวลโนเวลระดับตำนานของญี่ปุ่น ผู้สร้างความสำเร็จให้ Type-Moon และ Yuzusoft ไฟล์เกมบรรจุใน .xp3 สคริปต์เขียนด้วย KAG/TJS (.ks) แตกไฟล์ง่ายด้วย KrkrExtract  
*Legendary Japanese visual novel engine powering Type-Moon classics. Uses .xp3 packages and .ks scripts.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Fate/stay night, Fate/hollow ataraxia, Tsukihime (Original & Plus-Disc), Witch on the Holy Night (Mahoyo PC), G-senjou no Maou, Sabbat of the Witch (Yuzusoft), Senren*Banka

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.xp3`, `.ks`, `.tjs`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Rendering via FreeType/GDI
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **XP3Viewer**, **KrkrExtract**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: tvpwin32.exe | รูปแบบชื่อ Exe: fate.exe, tvpwin32.exe

---

### 📂 หมวดหมู่: Classic Visual Novel Engine

#### 94. NScripter / ONScripter
- **ผู้พัฒนา (Developer)**: Naoki Takahashi (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#fb7185`
- **ชื่อเรียกอื่นๆ (Aliases)**: `nscripter`, `onscripter`, `ponscripter`

**คำอธิบาย (Overview)**:  
เอนจิ้นนิยายภาพยุคคลาสสิกที่สร้างประวัติศาสตร์ให้ซีรีส์ 'แว่วเสียงเรไร' Higurashi ข้อความอ่านง่ายจาก 0.txt หรือ nscript.dat  
*Classic Japanese VN engine behind Higurashi and Umineko, using nscript.dat and .nsa archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Higurashi When They Cry (Original), Umineko When They Cry (Original), Tsukihime (Original NScripter port), Narcissu

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `nscript.dat`, `0.txt`, `arc.nsa`, `.sar`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType (default.ttf in root)
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **NSDEC**, **NSA Extractor**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: nscript.dat, 0.txt | รูปแบบชื่อ Exe: onscripter.exe

---

### 📂 หมวดหมู่: Proprietary Visual Novel Engine

#### 95. SiglusEngine
- **ผู้พัฒนา (Developer)**: Visual Arts / Key (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#ec4899`
- **ชื่อเรียกอื่นๆ (Aliases)**: `siglusengine`, `siglus`, `reallive`

**คำอธิบาย (Overview)**:  
เอนจิ้นประจำค่าย Key (Visual Arts) ผู้สร้างเกมบ่อน้ำตาแตกอย่าง CLANNAD และ Summer Pockets ไฟล์เกมหลักบรรจุใน Gameexe.dat และ Scene.pck  
*Visual Arts/Key's proprietary engine for CLANNAD and Summer Pockets, using Gameexe.dat and Scene.pck.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
CLANNAD (HD Edition), Little Busters! (English Edition), Summer Pockets & Reflection Blue, Angel Beats! 1st beat, Rewrite & Harvest festa!, Kanon, AIR

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `Gameexe.dat`, `.pck`, `.g00`, `.dxf`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Font via GDI/DirectWrite
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **SiglusExtract**, **RealLiveMax**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: siglusengine.exe, gameexe.dat | รูปแบบชื่อ Exe: siglusengine.exe

---

#### 96. CatSystem2
- **ผู้พัฒนา (Developer)**: Windmill (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#f472b6`
- **ชื่อเรียกอื่นๆ (Aliases)**: `catsystem2`, `cs2`, `catsystem`

**คำอธิบาย (Overview)**:  
เอนจิ้นวิชวลโนเวลที่ใช้สร้างซีรีส์ Grisaia อันเลื่องชื่อ ไฟล์เกมบรรจุในคลัง .int ข้อความอยู่ในสคริปต์ .cst  
*Visual novel engine behind the Grisaia trilogy, using .int archives and .cst script files.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
The Fruit of Grisaia (Grisaia no Kajitsu), The Labyrinth of Grisaia, The Eden of Grisaia, Chrono Clock, Hatsuyuki Sakura

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.int`, `.cst`, `.fes`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType with FreeType renderer
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **cs2_decompiler**, **intExtract**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: grisaia.exe

---

#### 97. BGI / Ethornell
- **ผู้พัฒนา (Developer)**: Buriko General Interpreter (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#fb7185`
- **ชื่อเรียกอื่นๆ (Aliases)**: `bgi`, `ethornell`, `bgi / ethornell`, `buriko general interpreter`

**คำอธิบาย (Overview)**:  
เอนจิ้นสำหรับเกมวิชวลโนเวลชื่อดังในญี่ปุ่น ไฟล์ถูกรวมใน .arc  
*Widely used Japanese VN engine for August titles and others, using .arc archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Daitoshokan no Hitsujikai, August titles, Steins;Gate (PSP/PC ports)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.arc`, `._bp`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType via FreeType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **BGI Tool**, **Sys4 Editor**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: bgi.exe | รูปแบบชื่อ Exe: bgi.exe

---

### 📂 หมวดหมู่: Point & Click 2D Adventure

#### 98. Adventure Game Studio
- **ผู้พัฒนา (Developer)**: Chris Jones / AGS Community (UK)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#d97706`
- **ชื่อเรียกอื่นๆ (Aliases)**: `adventure game studio`, `ags`, `ags engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นสร้างเกมผจญภัย Point & Click แนวสืบสวนยอดนิยม ไฟล์เกมบรรจุใน ac2game.dta หรือ .ags รองรับไฟล์แปลภาษา .tra  
*Leading point-and-click retro adventure engine. Uses ac2game.dta and .tra translation files.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Gemini Rue, Blackwell series, Kathy Rain, Whispers of a Machine, Resonance, Primordia

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.ags`, `ac2game.dta`, `.tra`
- **ระบบฟอนต์ (Font Subsystem)**: WFN / TrueType Fonts (.ttf) embedded in AGS package
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **AGS Editor**, **AGS Unpacker**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: ac2game.dta | รูปแบบชื่อ Exe: geminirue.exe, kathyrain.exe

---

### 📂 หมวดหมู่: Retro Point & Click Adventure

#### 99. SCUMM
- **ผู้พัฒนา (Developer)**: LucasArts (Ron Gilbert & Aric Wilmunder) (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#b45309`
- **ชื่อเรียกอื่นๆ (Aliases)**: `scumm`, `scummvm`, `lucasarts scumm`

**คำอธิบาย (Overview)**:  
เอนจิ้นสร้างประวัติศาสตร์เกมผจญภัยของ LucasArts รันได้อย่างสมบูรณ์แบบบน ScummVM  
*LucasArts' legendary adventure engine running natively on ScummVM.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
The Secret of Monkey Island 1 & 2, Maniac Mansion & Day of the Tentacle, Indiana Jones and the Fate of Atlantis, Full Throttle, Sam & Max Hit the Road

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.000`, `.001`, `.sou`
- **ระบบฟอนต์ (Font Subsystem)**: 8-bit Bitmap Character Glyphs
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **ScummVM Tools**, **SCUMM Revisited**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: scummvm.exe

---

### 📂 หมวดหมู่: Retro 2.5D FPS

#### 100. Build Engine
- **ผู้พัฒนา (Developer)**: Ken Silverman / 3D Realms (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#ea580c`
- **ชื่อเรียกอื่นๆ (Aliases)**: `build engine`, `build`, `ken silverman build`

**คำอธิบาย (Overview)**:  
เอนจิ้น 2.5D ระดับตำนานผู้ให้กำเนิด Duke Nukem 3D ไฟล์บรรจุใน .grp ข้อความอยู่ในสคริปต์ .con  
*Ken Silverman's classic 2.5D engine powering Duke Nukem 3D and Ion Fury.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Duke Nukem 3D, Blood (Monolith), Shadow Warrior (1997), Ion Fury (Modern Build engine), Redneck Rampage

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.grp`, `.con`, `.def`
- **ระบบฟอนต์ (Font Subsystem)**: Sprite Glyphs in TILES000.ART
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **eDuke32**, **GRP Explorer**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: duke3d.grp | รูปแบบชื่อ Exe: eduke32.exe, duke3d.exe

---

### 📂 หมวดหมู่: C# .NET Indie Game Framework

#### 101. MonoGame / XNA
- **ผู้พัฒนา (Developer)**: Microsoft / MonoGame Team (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#8b5cf6`
- **ชื่อเรียกอื่นๆ (Aliases)**: `monogame`, `xna`, `fna`, `monogame / xna`

**คำอธิบาย (Overview)**:  
เฟรมเวิร์กภาษา C# ยอดนิยมสูงสุดของวงการเกมอินดี้ บรรจุเนื้อหาใน .xnb มีคอมมูนิตี้ม็อดขนาดใหญ่ยักษ์ เช่น SMAPI ใน Stardew Valley และ tModLoader ใน Terraria ข้อความมักเป็น JSON  
*C# .NET framework behind Stardew Valley and Celeste. Uses .xnb assets and JSON text with strong mod API support.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Stardew Valley, Terraria, Celeste, Bastion, Transistor, Fez, Rogue Legacy, Axiom Verge

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.xnb`, `.json`, `.yaml`, `.csv`
- **ระบบฟอนต์ (Font Subsystem)**: SpriteFont (.xnb) / TrueType via BMFont or Dynamic SpriteFont
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **XNB Extract**, **SMAPI (Stardew)**, **tModLoader (Terraria)**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: stardew valley.exe, terraria.exe, celeste.exe | DLL หลัก: monogame.framework.dll, fna.dll | โฟลเดอร์ระบุ: content | รูปแบบชื่อ Exe: stardew valley.exe, terraria.exe, celeste.exe

---

### 📂 หมวดหมู่: Lua 2D Game Framework

#### 102. Love2D
- **ผู้พัฒนา (Developer)**: LÖVE Development Team (International)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#ec4899`
- **ชื่อเรียกอื่นๆ (Aliases)**: `love2d`, `love`, `löve`, `love 2d`

**คำอธิบาย (Overview)**:  
เฟรมเวิร์ก 2D ภาษา Lua ยอดฮิต ตัวเกมคือไฟล์ ZIP ที่เปลี่ยนนามสกุลเป็น .love (หรือรวมใน .exe) เปิดแตกไฟล์ด้วย 7-Zip ได้ทันที และในเกมฟีเวอร์อย่าง Balatro มี Lovely Mod Loader ช่วยฉีดข้อความและฟอนต์ไทยได้อย่างสมบูรณ์  
*Lua 2D framework powering smash-hits like Balatro. Moddable by opening the .exe or .love archive with 7-Zip.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Balatro, Move or Die, Mari0, Kingdom Rush (PC Port), SNKRX, BABA IS YOU (custom engine using Lua/Love concept)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.love`, `.lua`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: Embedded TrueType (.ttf/.otf) with native FreeType rendering
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **7-Zip**, **Lovely (Balatro Mod Loader)**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: love.dll | DLL หลัก: love.dll, lua51.dll | รูปแบบชื่อ Exe: balatro.exe

---

### 📂 หมวดหมู่: Java Multi-Platform Game Framework

#### 103. Java / LibGDX
- **ผู้พัฒนา (Developer)**: Badlogic Games / Mojang (International)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#ea580c`
- **ชื่อเรียกอื่นๆ (Aliases)**: `java / libgdx`, `libgdx`, `java`, `java_libgdx`

**คำอธิบาย (Overview)**:  
เฟรมเวิร์กภาษา Java สำหรับเกมข้ามแพลตฟอร์ม ไฟล์เกมบรรจุใน .jar (มาตรฐาน ZIP) ข้อความมักเป็นไฟล์ JSON หรือ Properties รองรับฟอนต์ TTF ภาษาไทยได้ทันที  
*Java-based game framework behind Slay the Spire and Minecraft Java, using standard .jar ZIP packaging and JSON/Properties.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Slay the Spire, Minecraft (Java Edition), Delver, Mindy

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.jar`, `.zip`, `.json`, `.properties`, `.csv`
- **ระบบฟอนต์ (Font Subsystem)**: FreeTypeFontGenerator / TrueType (.ttf) embedded in JAR
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **ModTheSpire**, **7-Zip**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: slaythespire.exe, slaythespire.jar | โฟลเดอร์ระบุ: jre | รูปแบบชื่อ Exe: slaythespire.exe, javaw.exe

---

### 📂 หมวดหมู่: Fantasy Console 8-bit

#### 104. PICO-8
- **ผู้พัฒนา (Developer)**: Lexaloffle Games (International)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#eab308`
- **ชื่อเรียกอื่นๆ (Aliases)**: `pico-8`, `pico8`, `tic-80`

**คำอธิบาย (Overview)**:  
คอนโซลจำลองยุค 8-bit ข้อความอยู่ในตลับสคริปต์ Lua .p8  
*Fantasy console running Lua cartridges (.p8) with fixed 4x6 pixel fonts.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Celeste Classic, Slipways (Pico-8 edition), Dusk Child

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.p8`, `.p8.png`
- **ระบบฟอนต์ (Font Subsystem)**: 4x6 Pixel Fixed Bitmap Font
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **PICO-8 Console**, **Text Editor**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: pico8.exe

---

### 📂 หมวดหมู่: Casual 2D Framework

#### 105. PopCap Framework
- **ผู้พัฒนา (Developer)**: PopCap Games (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#10b981`
- **ชื่อเรียกอื่นๆ (Aliases)**: `popcap`, `popcap framework`, `sexyappframework`

**คำอธิบาย (Overview)**:  
เอนจิ้นสำหรับเกมแคชชวลอันดับ 1 ของโลกอย่าง Plants vs. Zombies ไฟล์รวมอยู่ใน main.pak แตกและแพ็กกลับได้ง่ายมาก  
*Casual framework powering Plants vs. Zombies, storing assets in main.pak.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Plants vs. Zombies (PvZ), Peggle & Peggle Nights, Bejeweled 2 & 3, Zuma & Zuma's Revenge, Bookworm

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.txt`, `.xml`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Image (.png/.xml pair)
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **PopCap PAK Extractor**, **QuickBMS**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: main.pak, plantsvszombies.exe | รูปแบบชื่อ Exe: plantsvszombies.exe, peggle.exe

---

### 📂 หมวดหมู่: Proprietary AAA Live-Service Action

#### 106. Evolution Engine
- **ผู้พัฒนา (Developer)**: Digital Extremes (Canada)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#8b5cf6`
- **ชื่อเรียกอื่นๆ (Aliases)**: `evolution engine`, `evolution`, `evolution_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นขับเคลื่อนเกมออนไลน์ยอดนิยม Warframe บรรจุไฟล์ใน .toc และ .pkg  
*Digital Extremes in-house engine powering Warframe, using .toc and .pkg packages.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Warframe, The Darkness II, Dark Sector, Soulframe (Upcoming)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.toc`, `.pkg`, `.cache`, `.txt`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / Flash UI Cache
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **Evolution Engine Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: warframe.x64.exe | โฟลเดอร์ระบุ: cache.windows | รูปแบบชื่อ Exe: warframe.x64.exe, thedarknessii.exe

---

### 📂 หมวดหมู่: Proprietary Interactive Narrative/Cinematic

#### 107. Quantic Dream Engine
- **ผู้พัฒนา (Developer)**: Quantic Dream (France)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#3b82f6`
- **ชื่อเรียกอื่นๆ (Aliases)**: `quantic dream engine`, `quantic dream`, `quantic_dream_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นภาพยนตร์แบบโต้ตอบชั้นนำของ Quantic Dream บรรจุไฟล์ใน BigFile .dax และ .idx  
*Interactive drama engine behind Detroit: Become Human, packaging data into .dax and .idx files.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Detroit: Become Human, Beyond: Two Souls, Heavy Rain, Fahrenheit (Indigo Prophecy)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.dax`, `.idx`, `.bin`, `.xml`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector SDF / FreeType Embedded
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **Detroit Localization Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: detroitbecomehuman.exe | รูปแบบชื่อ Exe: detroitbecomehuman.exe, beyondtwosouls.exe, heavyrain.exe

---

### 📂 หมวดหมู่: Proprietary Open-World Destruction/Action

#### 108. Iron Engine
- **ผู้พัฒนา (Developer)**: Volition (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#9333ea`
- **ชื่อเรียกอื่นๆ (Aliases)**: `iron engine`, `iron_engine`, `ctg engine`, `volition iron engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นของค่าย Volition ผู้สร้าง Saints Row และ Red Faction บรรจุไฟล์ใน .vpp_pc และ .str2_pc ข้อความอยู่ใน .le_strings  
*Volition engine behind Saints Row and Red Faction Guerrilla, using .vpp_pc and .str2_pc packages.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Saints Row 2, 3, 4 & Gat out of Hell, Saints Row (2022 Reboot), Red Faction: Guerrilla (Geo-Mod 2.0 / Iron Engine), Agents of Mayhem

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.vpp_pc`, `.str2_pc`, `.le_strings`, `.xml`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector / Scaleform GFx
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Gibbed Saints Row Tools**, **ThomasJepp Tools**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: packfiles/pc | รูปแบบชื่อ Exe: saintsrowthethird.exe, saintsrowiv.exe, saintsrow.exe

---

### 📂 หมวดหมู่: Proprietary Grand Tactical/RTS

#### 109. TW Engine
- **ผู้พัฒนา (Developer)**: Creative Assembly (UK)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy to Medium` | **ธีมสี**: `#b45309`
- **ชื่อเรียกอื่นๆ (Aliases)**: `tw engine`, `tw_engine`, `warscape`, `total war engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นสงครามยุทธการจำลองทหารนับหมื่นนายของ Total War บรรจุไฟล์เกมใน .pack ข้อความภาษาจัดเก็บในตาราง .loc ใน db/ สามารถแก้ด้วย RPFM ได้อย่างเป็นมืออาชีพ  
*Creative Assembly strategic battle engine. Localization is stored in .loc tables within .pack files, modded with RPFM.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Total War: Warhammer 1, 2, 3, Total War: Three Kingdoms, Total War: Rome II, Total War: Medieval II, Total War: Shogun 2, Total War: Pharaoh, Total War: Attila

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pack`, `.loc`, `.tsv`, `.xml`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Font (.ttf) mapped in db/fonts table
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **RPFM (Rusted PackFile Manager)**, **Pack File Manager (PFM)**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: data | รูปแบบชื่อ Exe: warhammer3.exe, threekingdoms.exe, rome2.exe

---

### 📂 หมวดหมู่: Classic FPS / Horror

#### 110. LithTech
- **ผู้พัฒนา (Developer)**: Monolith Productions (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#475569`
- **ชื่อเรียกอื่นๆ (Aliases)**: `lithtech`, `lithtech jupiter`, `jupiter ex`, `talon`

**คำอธิบาย (Overview)**:  
เอนจิ้นยิงสยองขวัญระดับตำนานของ F.E.A.R. บรรจุไฟล์ใน .arch00 หรือ .rez ข้อความอยู่ในตาราง .str  
*Monolith Productions classic engine powering F.E.A.R. and Condemned, using .arch00 archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
F.E.A.R. 1 (Jupiter EX), F.E.A.R. 2: Project Origin, Condemned: Criminal Origins, No One Lives Forever 1 & 2, Shogo: Mobile Armor Division, Aliens versus Predator 2 (2001)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.arch00`, `.rez`, `.str`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Sheets / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **FEAR Extractor**, **RezExtract**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: fear.exe, fear2.exe, condemned.exe

---

### 📂 หมวดหมู่: Proprietary Procedural Infinite Universe

#### 111. Hello Games Engine
- **ผู้พัฒนา (Developer)**: Hello Games (UK)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#06b6d4`
- **ชื่อเรียกอื่นๆ (Aliases)**: `hello games engine`, `in-house (hello games)`, `no man's sky engine`, `hello games`

**คำอธิบาย (Overview)**:  
เอนจิ้นสร้างจักรวาลแบบ Procedural Generation ระดับมหากาพย์ บรรจุไฟล์เกมใน .pak ข้อความอยู่ในไฟล์ .mbin ซึ่งสามารถแปลงเป็น XML (.exml) ได้ผ่าน MBINCompiler  
*Procedural universe engine powering No Man's Sky. Localized text sits inside .mbin files, convertible with MBINCompiler.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
No Man's Sky, Light No Fire (Upcoming), The Last Campfire

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.mbin`, `.exml`
- **ระบบฟอนต์ (Font Subsystem)**: DDS Texture Font Atlas / FreeType TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **MBINCompiler**, **PSArcTool**, **NMS Modding Tools**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: nms.exe | โฟลเดอร์ระบุ: gamedata/pcbanks | รูปแบบชื่อ Exe: nms.exe

---

### 📂 หมวดหมู่: Proprietary AAA Strategy / Action RPG / Hero Shooter

#### 112. Blizzard Proprietary
- **ผู้พัฒนา (Developer)**: Blizzard Entertainment (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#0284c7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `blizzard engine`, `blizzard proprietary`, `blizzard_engine`, `blizzard`

**คำอธิบาย (Overview)**:  
เอนจิ้นระดับตำนานของ Blizzard ในยุคใหม่ใช้ระบบคลังเก็บข้อมูล CASC (Content Addressable Storage Container) ข้อความอยู่ในไฟล์ String tables ฟอนต์รองรับ TTF ในคลังข้อมูล  
*Blizzard's flagship proprietary technology using CASC and MPQ storage containers with embedded TrueType fonts.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Warcraft III: Reforged & The Frozen Throne, StarCraft II: Wings of Liberty / Heart of the Swarm / Legacy of the Void, Overwatch 1 & 2 (Tank Engine), Diablo III & Diablo IV, Heroes of the Storm, World of Warcraft

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.mpq`, `.casc`, `.txt`, `.json`, `.srt`
- **ระบบฟอนต์ (Font Subsystem)**: Embedded TrueType (.ttf/.otf) with custom shaping engine
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **CascView**, **MPQEditor**, **CASC Explorer**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: data/data, warcraft iii | รูปแบบชื่อ Exe: warcraft iii.exe, sc2_x64.exe, overwatch.exe

---

### 📂 หมวดหมู่: Proprietary Sci-Fi FPS

#### 113. Blam Engine
- **ผู้พัฒนา (Developer)**: Bungie (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#059669`
- **ชื่อเรียกอื่นๆ (Aliases)**: `blam engine`, `blam`, `bungie blam`, `halo engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นต้นกำเนิดตำนาน Master Chief ข้อมูลทั้งหมดถูกรวมอยู่ในไฟล์ .map  
*Bungie's classic FPS engine behind Halo 1 through Reach, packaging assets in .map files.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Halo: Combat Evolved, Halo 2, Halo 3 & ODST, Halo: Reach, Halo 4 (343 modified Blam)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.map`, `.unic`, `.txt`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Glyphs in .map tags
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Assembly**, **Halo Editing Kit (HEK)**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: maps | รูปแบบชื่อ Exe: halo.exe, halo2.exe

---

### 📂 หมวดหมู่: Proprietary AAA MMO-FPS

#### 114. Tiger Engine
- **ผู้พัฒนา (Developer)**: Bungie (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Very High` | **ธีมสี**: `#0284c7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `tiger engine`, `tiger`, `bungie tiger`

**คำอธิบาย (Overview)**:  
เอนจิ้นของเกม Destiny 2 พัฒนาต่อยอดจาก Blam เพื่อรองรับเกมยิงออนไลน์ขนาดยักษ์  
*Bungie's evolved engine powering Destiny 2, using .pkg archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Destiny 1, Destiny 2 & Expansions

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pkg`, `.bin`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font in PKG / Scaleform
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Destiny PKG Tool**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: destiny2.exe | โฟลเดอร์ระบุ: packages | รูปแบบชื่อ Exe: destiny2.exe

---

### 📂 หมวดหมู่: Proprietary Episodic Narrative Adventure

#### 115. Telltale Tool
- **ผู้พัฒนา (Developer)**: Telltale Games (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#f97316`
- **ชื่อเรียกอื่นๆ (Aliases)**: `telltale tool`, `telltale`, `telltale engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นเกมผจญภัยแบบแบ่งตอนยอดนิยม บรรจุไฟล์ทั้งหมดใน .ttarch หรือ .ttarch2 ข้อความอยู่ในไฟล์ฐานข้อมูลภาษา .landb สามารถแตกและแพ็กกลับได้ด้วย TTG Tools  
*Episodic story engine behind The Walking Dead and The Wolf Among Us. Assets packed in .ttarch/.ttarch2 with .landb string tables.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
The Walking Dead (Seasons 1, 2, A New Frontier, The Final Season), The Wolf Among Us, Tales from the Borderlands, Batman: The Telltale Series & The Enemy Within, Game of Thrones: A Telltale Games Series, Minecraft: Story Mode

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.ttarch`, `.ttarch2`, `.landb`, `.prop`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Font (.ttf) embedded in TTARCH packages / Font metadata .prop
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **TTG Tools**, **Telltale Inspector**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: archives | รูปแบบชื่อ Exe: walkingdead.exe, walkingdead2.exe, wwau.exe

---

### 📂 หมวดหมู่: Proprietary Cooperative FPS

#### 116. Diesel Engine
- **ผู้พัฒนา (Developer)**: GRIN / Overkill Software (Starbreeze) (Sweden)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#eab308`
- **ชื่อเรียกอื่นๆ (Aliases)**: `diesel engine`, `diesel`, `overkill diesel`

**คำอธิบาย (Overview)**:  
เอนจิ้นประจำค่าย Overkill ผู้สร้างเกมปล้นธนาคาร PAYDAY 2 บรรจุไฟล์เกมใน .bundle มี SuperBLT รองรับม็อดสคริปต์ Lua  
*Cooperative FPS engine behind PAYDAY 2, packaging assets into .bundle archives with SuperBLT mod support.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
PAYDAY: The Heist, PAYDAY 2, Bionic Commando (2009), Tom Clancy's Ghost Recon Advanced Warfighter 1 & 2 (PC)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.bundle`, `.stream`, `.lua`, `.xml`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / Bitmap Glyph Atlas
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Diesel Bundle Modder**, **SuperBLT**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: payday2_win32_release.exe | โฟลเดอร์ระบุ: assets | รูปแบบชื่อ Exe: payday2_win32_release.exe

---

### 📂 หมวดหมู่: Cross-Platform Framework (PS3/PS4/PC/Vita)

#### 117. PhyreEngine
- **ผู้พัฒนา (Developer)**: Sony Interactive Entertainment (Japan / UK)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium to High` | **ธีมสี**: `#3b82f6`
- **ชื่อเรียกอื่นๆ (Aliases)**: `phyreengine`, `phyre`, `sony phyreengine`

**คำอธิบาย (Overview)**:  
เอนจิ้นแจกฟรีของ Sony สำหรับผู้พัฒนาเกมข้ามแพลตฟอร์ม ถูกใช้ในเกม JRPG ชื่อดังมากมาย  
*Sony multiplatform middleware and game engine powering earlier Trails of Cold Steel titles and Persona 5.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Persona 5 (PS3/PS4 original), Trails of Cold Steel 1 & 2 (PS3/Vita/PC), Dragon Quest Builders 1 & 2, Tokyo Xanadu eX+, Demon's Souls (PS3 original framework)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pkg`, `.cpk`, `.bin`, `.dat`
- **ระบบฟอนต์ (Font Subsystem)**: FreeType Vector / TrueType embedded
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **SenPatcher**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: DLL หลัก: phyreengine.dll

---

### 📂 หมวดหมู่: Proprietary Japanese JRPG Engine

#### 118. Silicon Studio Engine
- **ผู้พัฒนา (Developer)**: Silicon Studio (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#8b5cf6`
- **ชื่อเรียกอื่นๆ (Aliases)**: `silicon studio engine`, `sge_engine`, `sge`, `mizuchi`, `orochi`

**คำอธิบาย (Overview)**:  
เอนจิ้นและเทคโนโลยีเรนเดอร์ของ Silicon Studio จากญี่ปุ่น  
*Silicon Studio game engine and rendering framework.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Bravely Default II, Gundam Breaker 3, Left Alive (rendering tech)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.bin`, `.sge`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / Font Sheet Texture
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: รูปแบบชื่อ Exe: bravelydefault2.exe

---

### 📂 หมวดหมู่: Proprietary Anime Action / JRPG

#### 119. NuLibrary
- **ผู้พัฒนา (Developer)**: Bandai Namco / CyberConnect2 (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium to High` | **ธีมสี**: `#f59e0b`
- **ชื่อเรียกอื่นๆ (Aliases)**: `nulibrary`, `bandai namco in-house`, `namco engine`, `cyberconnect2 engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นเกมต่อสู้สไตล์อนิเมะของ CyberConnect2 และ Bandai Namco บรรจุไฟล์เกมใน .cpk (CRIWARE) และไฟล์ออบเจกต์ .xfbin  
*Anime action framework by CyberConnect2 and Bandai Namco, using CRI CPK packages and .xfbin resource archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Naruto Shippuden: Ultimate Ninja Storm (1, 2, 3, 4, Connections), Dragon Ball Z: Kakarot, Demon Slayer: Kimetsu no Yaiba - The Hinokami Chronicles, JoJo's Bizarre Adventure: All-Star Battle R

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.cpk`, `.xfbin`, `.bin`, `.msg`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Texture Font Sheet in XFBIN / CriWare CPK
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **CriPakTools**, **XFBIN Parser**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: data | รูปแบบชื่อ Exe: ns4.exe, ns3fb.exe, dbzkakarot.exe

---

### 📂 หมวดหมู่: Proprietary Action-Adventure / Hack & Slash

#### 120. Vigil Engine
- **ผู้พัฒนา (Developer)**: Vigil Games (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#e11d48`
- **ชื่อเรียกอื่นๆ (Aliases)**: `vigil engine`, `vigil`, `vigil_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นประจำค่าย Vigil Games สำหรับมหากาพย์ Darksiders ภาค 1 และ 2 บรรจุไฟล์ใน .pck  
*Vigil Games engine powering Darksiders 1 & 2, using .pck container archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Darksiders 1 (Warmastered Edition), Darksiders II (Deathinitive Edition)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pck`, `.bin`, `.xml`
- **ระบบฟอนต์ (Font Subsystem)**: Bitmap Font Sheets / Scaleform GFx
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Darksiders PCK Extractor**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: media | รูปแบบชื่อ Exe: darksiders1.exe, darksiders2.exe

---

### 📂 หมวดหมู่: Classic RTS 3D

#### 121. Liquid Engine
- **ผู้พัฒนา (Developer)**: Liquid Entertainment (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#0284c7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `liquid engine`, `liquidengine`, `liquid_entertainment`

**คำอธิบาย (Overview)**:  
เอนจิ้นของเกมวางแผนระดับตำนานขวัญใจคนไทย Battle Realms บรรจุไฟล์ใน .dat และ .h2o  
*Classic RTS engine powering Battle Realms, using .dat and .h2o archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Battle Realms & Winter of the Wolf

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.dat`, `.h2o`, `.txt`
- **ระบบฟอนต์ (Font Subsystem)**: 8-bit Bitmap Font Sheets
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **H2O Extractor**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: battlerealms.exe | รูปแบบชื่อ Exe: battlerealms.exe, battle_realms_f.exe

---

### 📂 หมวดหมู่: Proprietary Pixel Art 2D/3D Hybrid

#### 122. Pixpil Engine
- **ผู้พัฒนา (Developer)**: Pixpil (China)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#f97316`
- **ชื่อเรียกอื่นๆ (Aliases)**: `pixpil engine`, `pixpil`, `pixpil_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นพิกเซลอาร์ตอันวิจิตรงดงามของเกม Eastward บรรจุไฟล์ใน .gpk  
*Pixel-art engine powering Eastward, packaging assets in .gpk.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Eastward

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.gpk`, `.json`, `.lua`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Pixel Font (.ttf)
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **GPK Unpacker**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: eastward.exe | รูปแบบชื่อ Exe: eastward.exe

---

### 📂 หมวดหมู่: Retro 8-bit Action Platformer

#### 123. Yacht Club Engine
- **ผู้พัฒนา (Developer)**: Yacht Club Games (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#0284c7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `yacht club engine`, `yachtclubengine`, `yacht club`

**คำอธิบาย (Overview)**:  
เอนจิ้นสไตล์ 8-bit NES ยุคโมเดิร์นของ Shovel Knight บรรจุข้อความและสไปรต์ใน .pak  
*Retro 8-bit NES style engine created for Shovel Knight.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Shovel Knight: Treasure Trove (Shovel of Hope, Plague of Shadows, Specter of Torment, King of Cards)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.csv`, `.txt`
- **ระบบฟอนต์ (Font Subsystem)**: NES-authentic Pixel Font Glyphs
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: shovelknight.exe | โฟลเดอร์ระบุ: data | รูปแบบชื่อ Exe: shovelknight.exe

---

### 📂 หมวดหมู่: Proprietary Real Driving Simulator

#### 124. Polyphony Digital Engine
- **ผู้พัฒนา (Developer)**: Polyphony Digital / Sony (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `High` | **ธีมสี**: `#0284c7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `polyphony digital engine`, `polyphony digital`, `gran turismo engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นจำลองการขับขี่รถยนต์สมจริงระดับโลกของ Gran Turismo บรรจุไฟล์ใน .vol  
*Real driving simulation engine behind the Gran Turismo franchise.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Gran Turismo 7, Gran Turismo Sport, Gran Turismo 5 & 6

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.vol`, `.bin`, `.dat`
- **ระบบฟอนต์ (Font Subsystem)**: High-Precision TrueType Vector Font
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **GT Toolset**, **TStudio**

---

### 📂 หมวดหมู่: Open-Source / Classic Commercial 3D

#### 125. Torque 3D
- **ผู้พัฒนา (Developer)**: GarageGames (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#ea580c`
- **ชื่อเรียกอื่นๆ (Aliases)**: `torque 3d`, `torque`, `torque engine`, `garagegames`

**คำอธิบาย (Overview)**:  
เอนจิ้น 3D โอเพนซอร์สยุคคลาสสิก ใช้สคริปต์ TorqueScript (.cs) และไฟล์ .gui  
*Open-source 3D engine using TorqueScript and .zip containers.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Tribes 2, Blockland, Marble Blast Gold / Ultra, BeamNG.drive (Early prototypes)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.zip`, `.dso`, `.gui`, `.cs`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType to Bitmap Font Cache
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Torque Tool**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: scripts, art

---

### 📂 หมวดหมู่: Indie 3D Commercial

#### 126. Leadwerks
- **ผู้พัฒนา (Developer)**: Leadwerks Software (USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Easy` | **ธีมสี**: `#6366f1`
- **ชื่อเรียกอื่นๆ (Aliases)**: `leadwerks`, `leadwerks engine`, `ultra engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นสร้างเกมสำหรับอินดี้ C++ และ Lua บรรจุไฟล์ใน .pak  
*Indie C++/Lua 3D engine using .pak archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Various Indie 3D horror and action games

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.pak`, `.lua`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType via FreeType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Leadwerks Editor**, **TStudio**

---

### 📂 หมวดหมู่: Open-Source C# .NET 3D

#### 127. Stride
- **ผู้พัฒนา (Developer)**: Stride Community / Silicon Studio (Japan / International)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#10b981`
- **ชื่อเรียกอื่นๆ (Aliases)**: `stride`, `stride engine`, `xenko`

**คำอธิบาย (Overview)**:  
เอนจิ้นภาษา C# .NET โอเพนซอร์สประสิทธิภาพสูง เดิมชื่อ Xenko พัฒนาโดย Silicon Studio  
*High-performance open source C# .NET engine formerly known as Xenko.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Modern open-source C# 3D indie titles

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.sdpkg`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: SDF Font Asset / TrueType
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **Stride Game Studio**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: DLL หลัก: stride.engine.dll

---

### 📂 หมวดหมู่: Classic Action RPG

#### 128. ZenGin
- **ผู้พัฒนา (Developer)**: Piranha Bytes (Germany)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#84cc16`
- **ชื่อเรียกอื่นๆ (Aliases)**: `zengin`, `zen engine`, `gothic engine`

**คำอธิบาย (Overview)**:  
เอนจิ้น RPG สุดคลาสสิกของซีรีส์ Gothic ภาค 1 และ 2 บรรจุไฟล์เกมใน .vdf ข้อความอยู่ในสคริปต์ Daedalus  
*Piranha Bytes classic RPG engine behind Gothic 1 & 2, storing data in .vdf archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Gothic 1, Gothic 2 & Gold Edition / Night of the Raven

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.vdf`, `.bin`, `.d`
- **ระบบฟอนต์ (Font Subsystem)**: FNT Bitmap Font Textures in VDF
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **GothicVDFS**, **Daedalus Decompiler**, **TStudio**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: ไฟล์ราก: gothic.exe, gothic2.exe | โฟลเดอร์ระบุ: data | รูปแบบชื่อ Exe: gothic.exe, gothic2.exe

---

### 📂 หมวดหมู่: Multimedia Middleware / Japanese Engine Wrapper

#### 129. CRIWARE
- **ผู้พัฒนา (Developer)**: CRI Middleware (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#0284c7`
- **ชื่อเรียกอื่นๆ (Aliases)**: `criware`, `cri ware`, `cricpk`

**คำอธิบาย (Overview)**:  
มิดเดิลแวร์ระบบภาพและเสียงยอดนิยมของญี่ปุ่น เกมญี่ปุ่นหลายร้อยเกมใช้ระบบบรรจุไฟล์ .cpk (CRI File System) ซึ่งสามารถแตกและแพ็กกลับได้ด้วย CriPakTools  
*Leading Japanese audio/video middleware and package format (.cpk) used across hundreds of Japanese titles.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Persona 4 Golden / Persona 3 Portable (PC ports), Sonic Frontiers / Sonic Forces, Tales of Vesperia: Definitive Edition, SOTDF (Shadow of the Damned: Hella Remastered), Danganronpa series

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.cpk`, `.usm`, `.awb`, `.acb`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType or Bitmap Font embedded in CPK containers
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **CriPakTools**, **QuickBMS**, **CRI Atom Craft**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: DLL หลัก: criware.dll

---

### 📂 หมวดหมู่: Proprietary Farming/JRPG Simulation

#### 130. Marvelous Engine
- **ผู้พัฒนา (Developer)**: Marvelous Inc. (Japan)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#f59e0b`
- **ชื่อเรียกอื่นๆ (Aliases)**: `marvelous engine`, `marvelous`, `marvelous_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นของค่าย Marvelous ผู้สร้างเกมปลูกผัก Story of Seasons และ Rune Factory บรรจุไฟล์ใน .lzs  
*Marvelous Inc. engine behind Story of Seasons and Rune Factory series, using .lzs compressed archives.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Story of Seasons: A Wonderful Life, Story of Seasons: Pioneers of Olive Town, Story of Seasons: Friends of Mineral Town, Rune Factory 3 Special, Rune Factory 4 Special, Rune Factory 5

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.lzs`, `.bin`, `.csv`, `.json`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector Font / Texture Font Atlas
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **LZS Decompressor**, **QuickBMS**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: data | รูปแบบชื่อ Exe: sosawl.exe, sospoot.exe, rf5.exe

---

### 📂 หมวดหมู่: Proprietary Stealth/Action

#### 131. LEAD Engine
- **ผู้พัฒนา (Developer)**: Ubisoft Montreal / Red Storm (Canada / USA)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium` | **ธีมสี**: `#16a34a`
- **ชื่อเรียกอื่นๆ (Aliases)**: `lead engine`, `lead`, `lead_engine`

**คำอธิบาย (Overview)**:  
เอนจิ้นพัฒนาเฉพาะสำหรับเกมสายลับ Splinter Cell Conviction และ Blacklist  
*Heavily customized Unreal-based engine developed for Splinter Cell Conviction and Blacklist.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Tom Clancy's Splinter Cell: Conviction, Tom Clancy's Splinter Cell: Blacklist

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.umd`, `.bin`, `.txt`
- **ระบบฟอนต์ (Font Subsystem)**: TrueType Vector / Scaleform GFx
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **QuickBMS**, **Splinter Cell Tool**, **TStudio**, **TRun**

> 🔍 **กฎการตรวจจับอัตโนมัติ (Auto-Detection Heuristics)**: โฟลเดอร์ระบุ: src/system | รูปแบบชื่อ Exe: conviction_game.exe, blacklist_game.exe

---

### 📂 หมวดหมู่: In-house / Proprietary Architecture

#### 132. Custom Engine
- **ผู้พัฒนา (Developer)**: Independent / Proprietary Studios (Various)
- **ความซับซ้อนในการม็อด (Complexity)**: `Medium to High` | **ธีมสี**: `#94a3b8`
- **ชื่อเรียกอื่นๆ (Aliases)**: `custom engine`, `custom_engine`, `custom`, `in-house`, `proprietary`

**คำอธิบาย (Overview)**:  
หมวดหมู่สำหรับเกมที่มีการเขียนเอนจิ้นขึ้นมาเองเป็นการเฉพาะ (เช่น เกมค่าย Supergiant Games อย่าง Hades หรือ Noita) ระบบตรวจจับของ Modder Hub จะช่วยวิเคราะห์โครงสร้างไฟล์และเลือกเครื่องมือที่เหมาะสมที่สุดให้โดยอัตโนมัติ  
*General category for proprietary in-house engines such as Supergiant's Hades or Nolla's Noita. Modder Hub analyzes files to suggest the best toolchain.*  

**เกมตัวอย่างที่ใช้เอนจิ้นนี้ (Notable Games)**:  
Hades 1 & 2 (Supergiant Games custom C++ engine), Noita (Nolla Games Falling Everything engine), No Man's Sky (Hello Games in-house engine), Eastward (Pixpil engine), Shovel Knight (Yacht Club engine), Battle Realms (Liquid Entertainment engine)

**สถาปัตยกรรมไฟล์และการแปล (Localization Architecture)**:  
- **นามสกุลไฟล์หลัก (Text / Data Formats)**: `.json`, `.csv`, `.xml`, `.txt`, `.bin`, `.pak`
- **ระบบฟอนต์ (Font Subsystem)**: Custom Implementation (TrueType, BMFont, or Texture Atlas)
- **เครื่องมือม็อดแนะนำ (Recommended Tools)**: **TStudio**, **TRun**, **QuickBMS**, **Hex Editor**

---

## 5. มาตรฐานโครงสร้างโปรเจกต์ม็อด THub 01–06

เพื่อให้การแปลและสร้างม็อดเป็นไปตามมาตรฐานสูงสุดและป้องกันข้อผิดพลาด THub กำหนดโครงสร้าง 6 โฟลเดอร์หลักสำหรับทุกโปรเจกต์:

```text
<Project_Workspace>/
├── 01_Original_Files/      # ไฟล์ต้นฉบับดั้งเดิมที่แตกออกมาจากเกม (ห้ามแก้ไขเด็ดขาด ใช้เปรียบเทียบ)
├── 02_Extracted_Text/      # ข้อความภาษาอังกฤษหรือญี่ปุ่นที่ถอดออกมาเป็น .txt, .json, .locres, .po
├── 03_Translated_Text/     # ข้อความที่ได้รับการแปลเป็นภาษาไทยเรียบร้อยแล้ว (ผ่าน TStudio / AI)
├── 04_Font_Assets/         # ฟอนต์ TTF/OTF, PUA Mapped, SDF Texture Atlas, FNT Coordinates
├── 05_Packed_Mod/          # ไฟล์แพ็กเกจม็อดสำเร็จรูป (.pak, .cpk, .bnd, .arc) พร้อมนำไปทดสอบ
├── 06_Release/             # แพ็กเกจสำหรับแจกจ่ายผู้เล่น (ZIP, 7z, ตัวติดตั้ง)
└── 07_Image_Resources/     # ภาพแคปซูล ปกเกม Official Art และภาพประกอบสำหรับแปล UI
```

---

*จัดทำและดูแลโดยระบบ Modder Hub Knowledge Management Protocol*