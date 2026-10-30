# รายงานตรวจโครงสร้างและโค้ด THub / TStudio

วันที่ตรวจ: 16 ตุลาคม 2026 (Asia/Bangkok)
ตำแหน่ง: `E:\Mod_Workspace\Modder_project\modder-hub`

## ขอบเขตและวิธีตรวจ

- สำรวจโครงสร้าง THub, core services, PyQt6 UI, AI, เครื่องมือ Flagship, ตัวเปิดโปรแกรม และระบบ build/distribution
- ตรวจ Python AST 191 ไฟล์: root 8, ai 1, core 12, tools 140, ui 10, ui_pyqt6 20 ไม่พบ Syntax Error
- ไม่รวม dist, build, _archive, scratch, backups, _legacy_archive และ __pycache__ ในการตรวจ AST ชุดนี้
- เทียบเนื้อหา Python ต้นฉบับกับ dist แบบ byte-for-byte และอ่านสารบัญโมดูลใน THub.exe/PYZ โดยไม่รัน EXE
- ทดสอบ PyQt6 แบบ offscreen และใช้ temporary directories สำหรับข้อมูลทดสอบทั้งหมด ไม่แก้โค้ดแอปหรือข้อมูลโปรเจกต์จริง
- ทดสอบบางเมธอดโดยดึง AST ของเมธอดจริงมารันกับ stub เพื่อไม่เปิด AI/network/GUI เต็มระบบ
- การตรวจนี้ครอบคลุมโครงสร้างทั้งชุดและเจาะเส้นทางสำคัญ ไม่ใช่การรับรองทุกฟีเจอร์ของทุกเครื่องมือ ไม่มีการวัด 60 FPS หรือทดสอบเกมจริง
- พบการแก้ไข/ไฟล์ untracked อยู่ก่อนแล้วจำนวนมากใน Git โดยเฉพาะ app_pyqt6.py, ui_pyqt6, ai และ core หลายไฟล์ รายงานนี้ไม่เปลี่ยนแปลงสิ่งเหล่านั้น
- ไม่พบ AGENTS.md จากการค้นหาใน workspace และตำแหน่ง parent ที่ตรวจ

## แผนผังระบบ

```text
modder-hub/
├── app_pyqt6.py                 THub 2.2 entry point, shell, routing, tool dispatch
├── core/                       12 Python files
│   ├── config_manager.py       Singleton config, JSON persistence, process-local RLock
│   ├── project_service.py      Create/edit/status/order/metadata/project statistics
│   ├── project_storage_service.py  Folder-size cache + QThread scanner
│   ├── engine_scanner.py       Lazy database proxy, detection tiers, cache
│   ├── engine_database.py      Engine definitions (~6,700 lines)
│   ├── game_scanner.py         Installed libraries and game matching
│   ├── steam_service.py        Steam search/art download + background queue
│   ├── knowledge_service.py    Bible/guide index and matching
│   ├── mod_adoption_service.py Legacy audit and restructure
│   ├── tool_launcher.py        Launch tool scripts / frozen dispatcher
│   ├── font_service.py        Font catalog and deployment
│   └── i18n.py                Older localization manager
├── ui_pyqt6/                   20 Python files: theme + 4 components + 4 views + 11 dialogs
│   ├── views/                  Dashboard, AI Helper, Apps, Knowledge
│   ├── components/             Sidebar, Storage/Donut, Header, Project Card
│   └── dialogs/                Project Wizard, Adoption, Settings, Cover, Bible, Fonts, Theme
├── ai/prompt_engine.py         AI planning prompts
├── tools/flagship/
│   ├── Core/                   Shared TStudioCore, AI, formats, translation transport
│   ├── TStudio/                Translation editor, models, dialogs, parsers, batch dock
│   ├── TRun/                   Batch worker and standalone/integrated runner
│   ├── TPUA/, TGlyph/, TFont/   Font utilities
│   ├── TVox/                   Audio tools
│   ├── GameBridges/, Plugins/  Game/engine integrations
│   └── Legacy/                 Legacy tools
├── tools/Standalone/TSub/      Subtitle tool
├── assets/, templates/, locales/
├── Modding-Knowledge/          Bundled knowledge fallback
├── workspace/                 Logs and application workspace
├── main.py, app_nextgen.py, ui/ Older entry points/UI coexist with PyQt6
├── run_thub*.bat, run_thub_silent.vbs
├── THub.spec, THub_2.0.spec, build_release*.py
└── dist/THub/                  Production EXE + _internal sources/resources
```

Main flow: launcher → app_pyqt6.main() → ConfigManager → THubPyQt6App → Dashboard → lazy views. Services share mutable project dictionaries from ConfigManager. ToolLauncher starts child processes, and the frozen entry point dispatches scripts through runpy. TStudio/TRun share tools/flagship/Core.

KnowledgeService prefers `E:\Mod_Workspace\Modding-Knowledge` and falls back to the bundled Modding-Knowledge directory. There are also knowledge directories elsewhere in the parent workspace; their presence alone does not make them active sources for THub.

## Findings

Priority: P1 = data loss / important operation fails; P2 = functional inconsistency or operational risk. “Reproduced” means reproduced on disposable data or with isolated actual methods. “Static” means established from code paths; full UI runtime impact has not been exercised.

### F01 — P1 — CSV round trip loses rows and duplicate IDs [reproduced]

Locations: `tools/flagship/Core/tstudio_core.py:1776-1787`, `:1867-1871`.

`format_to_standard()` drops rows with empty IDs and stores original rows in a dictionary keyed by ID. Duplicate IDs overwrite earlier rows in that dictionary. `export_original()` writes that reduced dictionary back without a row-count check.

Test: three original rows, two with the same ID and one with an empty ID → two standard rows → one metadata row → one exported row. Export still returned success.

Fix direction: preserve ordered row identity separately from game IDs, retain blank-ID rows, validate input/output counts, and reject ambiguous mappings rather than silently losing content.

### F02 — P1 — Adoption overwrites colliding filenames [reproduced with Wizard-equivalent copy options]

Location: `core/mod_adoption_service.py:317-341`.

All categorized files are flattened to their basename. If a destination exists, the code tries one `_legacy` suffix without checking that suffix for another collision. With `shutil.copy2`, the next collision overwrites it.

Test: three source folders each containing text.csv → destination contains text.csv and text_legacy.csv only; the latter contains the third payload. The second payload is missing at the destination, while the service reports success. With copy mode the originals remain; an in-place move can remove that recovery source.

Fix direction: preserve relative paths or allocate unique collision-safe names and persist a complete transfer manifest; return failure when any transfer fails.

### F03 — P1 — “Safe Backup” creates a manifest without backing up file contents [reproduced/static]

Location: `core/mod_adoption_service.py:258-274`.

The safe_backup branch creates `_thub_legacy_snapshot/snapshot_manifest.json`. It copies no source bytes and has no rollback implementation. This does not provide recovery for in-place moves or overwrites. Failure to create the manifest is logged as a warning and restructuring continues.

Fix direction: create and verify a real backup before mutations, or clearly describe the option as a manifest rather than a backup. Stop destructive restructuring if the requested backup fails.

### F04 — P1 — Dashboard Quick Note loses edits during project switches/search/refresh [reproduced]

Locations: `ui_pyqt6/views/dashboard_view_qt.py:108-111`, `:690-697`, `:950-953`, `:1051-1074`, `:1233-1234`.

Saving is delayed 500 ms. Switching projects replaces the editor contents before the pending save has captured the previous project's text. Filtering and storage refresh also call `_update_hero_stage()`, which reloads the old note into the editor.

Test: edit A, switch to B before the timer fires → A keeps the old note. Edit A then call search/filter → the editor immediately returns to A's old note.

Fix direction: bind pending changes to a stable project key and captured text, save before switching/reloading, avoid resetting a dirty note during storage refresh, and flush pending edits during close.

### F05 — P1 — TRun start/stop and TStudio translation-options error paths crash [reproduced]

Locations:

- `tools/flagship/TRun/trun_app.py:1964-1988`: start with an empty queue
- `tools/flagship/TRun/trun_app.py:2266-2282`: stop an active worker
- `tools/flagship/TStudio/tstudio_app.py:6000-6027`: translation options with no selected row

Each function assigns to `_` as a loop variable and also calls `_()` for translation. Python treats `_` as local throughout that function. Calling `_()` before the loop assignment raises `UnboundLocalError`. Checking `'_' in globals()` does not change local-variable resolution.

All three isolated method calls reproduced `UnboundLocalError: local variable '_' referenced before assignment`. The TRun findings concern TRunApp paths, including standalone mode; the integrated batch dock has its own paths.

Fix direction: rename throwaway variables or use an unambiguous translation alias.

### F06 — P1 — .lang reconstruction does not enforce encoding/BOM or line-count preservation [partly reproduced]

Location: `tools/flagship/TStudio/tstudio_models.py:525-552`.

The writer hardcodes UTF-8 without BOM and LF; it has no original encoding/BOM/newline metadata. A translation containing a real newline is inserted verbatim into an entry, creating extra physical lines. There is no row/line-count assertion.

Test: metadata describing one entry + a translation containing a newline → two output physical lines. The output has no BOM. For inputs that require a BOM, the writer cannot preserve it through this interface.

The generic CSV conversion/export path also hardcodes utf-8-sig and decodes with errors='replace'; original encoding is not retained there either.

Fix direction: retain source bytes/encoding/BOM/newline metadata, define multiline escaping per format, validate physical lines before replacing outputs, and use strict decoding with explicit error handling.

### F07 — P1 — Production sources and embedded application are from different revisions [verified artifact inspection]

THub root/app/core/ui/ai Python comparison (34 files): 31 identical, 2 different, 1 missing.

- Different: `ui_pyqt6/theme_qss.py`, `ui_pyqt6/dialogs/cover_editor_dialog_qt.py`
- Missing: `ui_pyqt6/dialogs/bible_viewer_dialog_qt.py`

tools Python comparison (140 files): 124 identical, 9 different, 7 missing.

Different:

```text
tools/flagship/Core/tstudio_core.py
tools/flagship/Core/tstudio_tlm_studio.py
tools/flagship/TRun/trun_app.py
tools/flagship/TStudio/trun_batch_dock.py
tools/flagship/TStudio/tstudio_analyzer_dialog.py
tools/flagship/TStudio/tstudio_app.py
tools/flagship/TStudio/tstudio_editor.py
tools/fonts/generate_all_variant_previews.py
tools/fonts/generate_previews.py
```

Missing:

```text
tools/flagship/Core/translation_transport/__init__.py
tools/flagship/Core/translation_transport/contracts.py
tools/flagship/Core/translation_transport/gateway.py
tools/flagship/Core/translation_transport/qt_controls.py
tools/flagship/Core/translation_transport/settings.py
tools/flagship/Core/translation_transport/web_client.py
tools/fonts/generate_retro_pua.py
```

THub.exe contains app_pyqt6 as its entry script. Its PYZ still contains `core.logo_service`, `ui_pyqt6.dialogs.tlogo_studio_dialog`, and `ui_pyqt6.views.tstudio_view_qt`; it lacks the new Bible Viewer and several new services/dialogs. Thus copying loose .py files alone does not demonstrate that the embedded application has been updated. Whether a given module resolves from the embedded archive or a loose source must be verified in the frozen runtime.

Do not infer that the current EXE necessarily crashes from a missing loose file: its embedded code is older. A production runtime smoke test and rebuild are needed to establish actual loaded modules and behavior.

### F08 — P2 — Blocking I/O remains on the GUI thread [static]

Examples:

- `ui_pyqt6/dialogs/cover_editor_dialog_qt.py`: `_download_from_steam()` and `_download_from_url()` call synchronous network methods directly in button handlers. Service timeouts occur per request and Steam search can try several candidates/CDNs.
- `ui_pyqt6/dialogs/project_wizard_qt.py:330-339`: engine detection is synchronous during text changes. `_submit()` calls create_project, including template copying and engine scans, synchronously.
- `ui_pyqt6/dialogs/settings_dialog_qt.py:350-351`, `:424`: installed-game scans run directly in UI handlers.
- `ui_pyqt6/views/dashboard_view_qt.py:876-881`: selection/refresh enumerates four project directories on the UI thread.
- `ui_pyqt6/views/knowledge_view_qt.py:23`: first KnowledgeService construction calls reindex() synchronously; the index traverses and reads markdown files.
- `ui_pyqt6/views/ai_helper_view_qt.py:1546-1550`: continuation prompt generation may audit the project folder synchronously.

Fix direction: bounded background tasks, cached results, progress signals and generation IDs for stale results. QTimer can schedule work but does not move a synchronous scan/network call off the GUI thread.

### F09 — P2 — Worker lifetime and cancellation are incomplete [static risk]

Locations: `ui_pyqt6/dialogs/mod_adoption_wizard_dialog_qt.py:345-356`, `ui_pyqt6/views/dashboard_view_qt.py:1433-1444`, `core/project_storage_service.py:107-141`.

Adoption uses terminate() on a running audit then immediately replaces its reference without waiting for finished. Dashboard owns a StorageScanWorker but has no application close cleanup. Its cancel flag is checked between projects, not inside recursive directory scanning. Adoption dialog workers similarly lack an explicit close/reject cleanup protocol.

These are lifetime/abort risks; a process-abort reproduction was deliberately not run. Fix direction: cooperative interruption, retain workers until finished, and defer final window destruction until workers finish safely.

### F10 — P2 — Adoption and Dashboard use different workspace schemas [static]

Locations: `core/project_service.py:10-18`, `core/mod_adoption_service.py:276-288`, `ui_pyqt6/views/dashboard_view_qt.py:878-881`.

Create Project writes 01_Original_Backup, 02_Translation_Workspace, 03_Font_and_UI, 04_Packed_Mod, 05_Scripts_and_Tools, 06_Releases. Adoption writes 01_Original_Files, 02_Extracted_Text, 03_Translated_Text, 04_Font_Assets, 05_Packed_Mod, 06_Release.

Dashboard hardcodes the first scheme, so adopted projects can show empty file/font counts and open different directories. Progress calculation also hardcodes 02_Translation_Workspace. TStudioCore already supports several alternate translation folders, so this is not a claim that all TStudio project discovery fails.

Fix direction: a shared schema resolver/manifest used by every component, with explicit migration support.

### F11 — P2 — AI Helper project selector is not refreshed by main-window project mutations [static]

Locations: `app_pyqt6.py:185-198`, `:261`, `:332`, `:388`, `:464` and project lifecycle handlers; `ui_pyqt6/views/ai_helper_view_qt.py` set_project()/update_projects().

AI Helper is created with a project list and reused thereafter. Creation/adoption/deletion/edit handlers refresh Dashboard but do not call the AI Helper's existing update_projects() API. Switching a single active project is not sufficient to rebuild the selector, particularly when delete_project replaces the config list.

Fix direction: one project-list-change signal consumed by all views; refresh active project references after deletion.

### F12 — P2 — Launch scripts in the release point to a source entry file that is not shipped at that location [static]

Locations: `build_release_2.0.py:84-95`, `run_thub.bat`, `run_thub_pyqt6.bat`, `run_thub_silent.vbs`.

The release builder copies run_thub.bat into dist/THub, but that batch file runs pythonw app_pyqt6.py relative to that directory. app_pyqt6.py is the compiled EXE entry rather than a root loose source file there. It also unnecessarily requires a user's Python installation for a frozen release.

Both batch launchers fall back to visible python and pause on failure, violating the requested silent behavior. The VBS launcher hardcodes this developer's absolute installation directory.

Fix direction: release launcher should invoke the shipped THub.exe; development launchers should resolve interpreter/location robustly and log errors without a persistent console.

## Additional engineering concerns

- ConfigManager's RLock protects only one process. It returns live mutable lists/dicts, so callers mutate outside that lock. Atomic replace avoids a torn JSON file but does not solve cross-process lost updates. save_projects() does not propagate save failure to callers, allowing success-looking UI after a failed write.
- execute_adoption_restructure(in_place=False) defaults copy_mode=False. Its special 01_Original_Backup migration checks only copy_mode and can move source files even though most transfers correctly honor `or not in_place`. Reproduced through the service API. The current Wizard explicitly passes copy_mode=True and therefore protects this specific UI path.
- Metadata is rewritten in place in several services. Some read errors fall back to an empty dictionary, which risks replacing existing metadata rather than preserving the unreadable file for recovery.
- THub.spec analyzes main.py while THub_2.0.spec analyzes app_pyqt6.py. Build paths are ambiguous; build_release_2.0.py selects the latter but defaults the release version to 2.0.1.
- TStudioCore has duplicate set_project_path/get_project_path definitions at lines 88/739 and 92/746. Later definitions replace earlier ones. This deserves cleanup after confirming intended behavior, not removal during an audit.
- Source trees lack a central requirements/lock file for the complete suite; requirements files exist only for selected tools. The inspected Python runtime has PyQt6, Pillow, requests, markdown, fontTools and PyInstaller; pytest/ruff/pyflakes are absent. No new packages were installed.
- ui/main.py legacy paths and scratch test scripts coexist with production code. There is no single suite-level automated regression command established by this inspection.

## Checks that passed / historical issues

- Syntax parsing passed for all 191 inspected Python files.
- EngineScanner returned Custom Engine for empty/unknown input and Creation Engine for Skyrim. The EngineDatabase NameError in the old crash log did not reproduce; the current lazy proxy addresses that name.
- SidebarDonutWidget accepted six project sizes. A simplistic underscore-shadow scan flags its comprehensions, but those are scoped separately in Python 3 and are not the reproduced TRun/TStudio bug.
- Historical media_kit_dialog crash entries refer to modules removed from the current source. They are not reported as current source bugs.
- No source, translation, production, or knowledge files were modified for fixes. This report is the audit deliverable.

## Recommended repair order

1. Protect translation round trips and adoption: F01, F02, F03, F06, with backups and regression fixtures.
2. Fix note persistence and failing actions: F04, F05.
3. Establish consistent workspace schema and worker lifecycle: F08–F10.
4. Refresh dependent views and repair launchers: F11–F12.
5. Sync and rebuild production from the verified source revision, then smoke-test THub.exe and every supported tool. Check hashes and actual loaded module paths; retain the user's required root-to-dist sync as part of the release process.
