# THub hardening — 16 October 2026

Scope: THub Launcher, its project services/UI, launchers and build pipeline. No edits or synchronization of TStudio, TRun, or tools/flagship/Core by this work.

## Implemented

1. Captured a recoverable source/config/EXE backup before edits, plus hashes of protected tool files.
2. Fixed Dashboard note loss on selection, filtering and storage refresh. Writes capture the project/text; closing drains pending notes and reports write failure.
3. Added verified full-file adoption snapshots, unique collision-safe transfers, transfer journals, failure reporting and a backup restore action in the Adoption dialog. Copy-to-new-workspace preserves originals.
4. Added shared workspace-folder resolution for Dashboard and progress calculation across current/adopted layouts.
5. Centralized project-list refresh for instantiated THub views, including selection after deleting a project.
6. Moved cover downloads, installed-game scans, Wizard creation/detection, project settings saves/detection, knowledge initialization/reading and AI prompt generation to owned background jobs.
7. Replaced forced adoption-thread termination with managed task lifetime and deferred dialog shutdown. Storage cancellation is checked during recursion.
8. Added atomic metadata writes and serialization of metadata patches, preserved unreadable JSON, and propagated config write failures.
9. Reworked VBS/batch launchers to resolve their own directory, use THub.exe in a release, and avoid a visible Python fallback/pause.
10. Established a canonical staged PyQt6 build, protected runtime promotion and a frozen startup/shutdown gate. Added an ICU runtime hook after reproducing a packaging DLL conflict.

## Validation

- 18 THub regression tests pass in tests/test_thub_hardening.py.
- Source integration smoke passes: Dashboard, Knowledge, AI Helper, project list add/delete, global/project Settings, Wizard and pending-note close.
- Staged windowless EXE startup/shutdown and packaged Dashboard/Knowledge/AI Helper/Apps routes pass with isolated temporary config.
- New backup/task/schema/Bible Viewer modules are present in the EXE archive. The old TLogo modules are absent from that archive.
- All THub-owned Python modules are synchronized to dist/THub/_internal.
- Build/deployment evidence is saved in the staging directory's source_sha256.json, verified_smoke.json and deployment_result.json.

## Recovery and boundaries

- Before-edit backup: workspace/backups/thub_hardening_20261016_094501/before.zip.
- Replaced production runtime files: the same directory's previous-runtime/; launchers in previous-launchers/.
- Adoption recovery: open “สานต่องาน”, choose “กู้คืนจากสำรอง...”, then select the verified snapshot_manifest.json. New post-backup files are retained.
- Tool files changed externally during this task. Promotion preserves their current versions and does not restore the older baseline over them.
- Existing source and production hub_config.json files are preserved during promotion; smoke tests use temporary registries.
- TStudio/TRun translation/export fixes from the original audit remain with their owning chat. No real game translation or tool translation session was run here.
- Atomic writes/metadata locks protect a single process. Cross-process concurrent registry edits remain a separate design concern.
- Offscreen UI rendering checks layout and navigation; this work does not certify 60 FPS or every third-party tool dependency.

Technical guide: Modding-Knowledge/Techniques/THub_Safe_Project_IO_and_Qt_Workers.md, also synchronized to the central knowledge base.

## Performance and stability update 26 October 2026

The October 26 work covers the current THub source, its frozen EXE, Dashboard, Gallery, worker management, knowledge/engine/cover services and project migration. TStudio, TRun and tools/flagship/Core remain separately maintained and were not edited or synchronized by this work.

### Changes

- Project cards retain a bounded LRU of rendered images (128 entries / 32 MiB), downsample during decoding, detect replacement files and update pin/archive badges from immutable state. Automatic cover retrieval respects the setting and does not accumulate listeners.
- Hero covers retain 24 rendered images keyed by file version/crop/progress. Grid reflow is skipped when card order and columns are unchanged. Search input is debounced by 100 ms.
- Each BackgroundTasks manager runs at most four threads and replaces outdated queued requests. Pending identical note saves are deduplicated; metadata/config errors remain visible. Shutdown waits for child dialogs and migration workers without a blocking GUI wait.
- Workspace scanning prunes uninspected deep descendants. A malformed Starfield test no longer prevents detection of engines later in the scan. Lazy database collections publish only after a successful load.
- Knowledge refresh builds a replacement catalog privately, publishes it atomically and invalidates dependent title/engine caches. Failed refreshes preserve the previous catalog.
- Cover download queues release completed keys/listeners, allow retry after failure and handle enqueue during worker retirement. Interrupted Qt searches do not start subsequent candidate requests.
- Gallery fixes all dimension-filter exceptions, loads metadata/thumbnails in workers, uses a 64-entry / 16 MiB QImage thumbnail cache and converts to QPixmap on the GUI thread. Harvests are deduplicated, downloads use temporary files and cancellation stops subsequent requests. The Sony headless process uses a hidden Windows creation flag.
- Migration verifies every file with streaming SHA-256 in an owned staging directory before publishing. Overwritten destination files are retained separately; failed merges roll back. Source cleanup rechecks the original tree and removes only verified original paths, preserving new or changed files. Drive queries run off the GUI thread.
- Adoption preflights existing metadata before transferring files, reports recovery paths after later failures and permits workspaces on different Windows drives.
- Rebuilt the frozen runtime so newer art/migration modules and current Python code are embedded, then synchronized 43 THub Python files.

### Measurements

Controlled local fixtures use generated 2560×1440 covers, with network and disk-size scans disabled during timed UI work. The baseline is the before-edit source ZIP; unchanged locale/helper resources come from the repository. These timings describe the fixture rather than a whole-application FPS claim.

| Operation | Before | After |
| --- | ---: | ---: |
| Refresh 60 projects, median of 3 rounds | 1,802.02 ms | 61.43 ms |
| Search and restore 60 projects, median pair | 1,835.91 ms | 44.99 ms |
| Construct the 60-project window | 2,356.91 ms | 1,994.04 ms |
| Hero cover 60 repeated render calls | 1,698.20 ms / 60 decodes | 67.10 ms / 2 decodes |
| Workspace traversal in a 1,365-directory tree | 241.25 ms / 1,365 visits | 4.10 ms / 21 visits |

First-time loading of many full-size card covers still takes about two seconds in this fixture; the largest gain is repeated navigation/refresh. SHA-256 verification intentionally reads complete files rather than trading source safety for faster sampled checks.

### Validation and evidence

- 70 regression tests pass with `python -B -m unittest discover -s tests -p 'test_*.py'`.
- Source integration smoke passes. The frozen runtime passes startup/shutdown, Dashboard, Knowledge, AI Helper, Apps, migration-dialog initialization and all Gallery filters, using disposable configs and local images.
- REA/Ghidra identified the original x64 PE and inspected its bootloader layout, native string inventory and references. Python application behavior is established separately by source, PyInstaller archive inspection and controlled runtime tests; native decompilation is not treated as recovered Python application source.
- Original REA records: `scratch/rea_20261026_before.evidence.json`; updated PE resource evidence: `scratch/rea_20261026_after.evidence.json`. The Windows REA provider does not support its PTY process-capture operation, so runtime checks use local Python/subprocess fixtures instead.
- Native overview evidence: `ev_3c675ef423a7e371473025042f388f9563cab6da5c956435bfa6674e0fcdb8c9`; original resource evidence: `ev_87df38ca49886e4b015e945061b0da62052e82c91c073d2cdbbd2cfaddff1eee`.
- Build/deployment evidence: `workspace/builds/rea_20261026_105237/`, including source hashes, embedded-source comparison, smoke results and deployment_result.json. Before promotion, 41 embedded THub modules match current compiled source; the unused legacy core/i18n.py is shipped loose.
- Tool hashes for 2,673 files and both existing hub_config.json files were preserved during runtime promotion. No external-tool updates were rolled back.
- Before-edit source/config/EXE backup: `workspace/backups/rea_20261026_103756/before.zip`. Replaced runtime files are also retained under that directory.

Migration interruption retains source data and/or verified destination copies, but is not a single transaction spanning the registry and filesystem. Concurrent writers must stop changing a workspace before moving it; changes detected during the move preserve the source. A network request already in progress can wait for its bounded read/timeout before cancellation takes effect. Real provider downloads and third-party tool sessions were not exercised by the offline tests.

## Startup follow up 26 October 2026

THub now shows its project window while a shared worker service decodes cover images. The completed images are delivered to the GUI thread for rounded corners and progress overlays. The service uses the Dashboard's bounded task manager, deduplicates requests, limits its QImage cache to 128 entries / 32 MiB, and identifies images by file version, crop and output size. QPixmap remains on the GUI thread. TStudio, TRun and shared Core are unchanged.

Startup also defers project/adoption dialog imports, loads Steam HTTP/Pillow dependencies only when their functions are used, and avoids applying an identical stylesheet both globally and to the main window. Packaged dependencies remain available to the existing tool dispatcher.

The initial window remains interactive while covers load. `DashboardViewQt.startup_ready()` separately identifies the point when every requested card image is delivered and Dashboard jobs have drained. Closing cancels only the image tasks, preserving note saves. If a failed note save prevents closing, the image service reopens with a new generation so old callbacks cannot replace new requests.

### Frozen EXE measurements

Each value is the median of three fresh processes with an isolated config and generated PNG covers at 2560×1440. Time begins at subprocess launch. The filesystem cache is warm; network and folder-size scanning are disabled during timing. First-window measurements use the first offscreen QWidget Paint event, rather than a physical display/compositor measurement. Fully ready requires real completed images, rather than only placeholders.

| Projects | Window before | Window after | Images complete before | Images complete after |
| --- | ---: | ---: | ---: | ---: |
| 60 | 2.413 s | 0.569 s | 2.437 s | 1.112 s |
| 111 | 4.161 s | 0.847 s | 4.187 s | 1.877 s |

The same source fixture improved constructor-to-first-paint from 2.078 to 0.475 seconds for 60 cards, and from 3.816 to 0.734 seconds for 111 cards. Source profiling identified about 1.515 seconds in synchronous image decoding for 60 cards before the change; this decoding now runs off the GUI thread. Window/card widget creation remains part of the initial GUI work.

### Validation and recovery

- 92 regression tests pass. New checks cover shared decode deduplication, worker-thread execution, cache bounds, crop/file replacement, stale results, close/reopen, lazy imports, first-window interaction and failed-note-save recovery.
- Source smoke and the frozen Production smoke pass, including completed Dashboard/hero images, all four routes, migration dialog and Gallery filters.
- 44 THub Python files are synchronized. The frozen archive contains current matching code for 42 reachable THub modules; unused legacy core/i18n.py remains a loose source file.
- Before-edit backup: `workspace/backups/startup_20261026_110332/before.zip`; replaced runtime files are under that directory's `previous-runtime/`.
- Build and deployment evidence: `workspace/builds/startup_20261026_111151/`. Benchmark samples, cProfile files and the combined result are in `scratch/startup_20261026/`.
- Production EXE SHA-256: `7e2e1c914004558da84000d59497b7689a27bc9f134a5fc83dc8517a66aad4f4`.
- Protected tools and both user config files retain their pre-change bytes. No translation or tool session was started by these tests.

Reproduce source timing with `python -B tests/benchmark_thub_startup.py --projects 111 --samples 3 --output scratch/startup_check.json`. For the frozen runtime add `--executable <absolute-path-to-THub.exe> --no-profile`.
