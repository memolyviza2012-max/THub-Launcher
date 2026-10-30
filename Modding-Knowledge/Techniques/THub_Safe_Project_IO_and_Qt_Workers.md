# THub: Safe project files and Qt background tasks

Verified locally on 2026-10-16 with Python 3.10.11, PyQt6 6.11.0 and PyInstaller 6.22.2.
Scope: THub launcher services and UI. TStudio, TRun and tools/flagship/Core are separately maintained.

## Project metadata

- Use core.safe_io.write_json_atomic() for complete objects and update_json_atomic() for patches.
- Read existing metadata strictly; never replace malformed JSON with an empty object and silently save it.
- Atomic writes use a unique temporary file in the destination directory, flush/fsync and os.replace.
- A process-local lock serializes metadata read/patch/write. It does not coordinate separate THub processes.
- ConfigManager propagates failed writes. An unreadable registry is retained and cannot be silently overwritten.
- Game translation bytes are outside this API; preserve their source encoding, BOM and line counts in their owning tool.

## Notes and project identity

- Capture project identity and note text at the textChanged event, before changing selection.
- Keep unsaved text in a dirty map; storage refresh, filtering and inspector completion must not reload over it.
- Persist only the current registry's matching project. Never save an old full project list from a worker.
- Drain pending note jobs before closing. Keep the window open and show the error if notes cannot be persisted.

## Adoption and recovery

- create_snapshot() copies regular source files and verifies SHA-256 before any transfer starts.
- Store snapshots under _thub_legacy_snapshot/<unique-id>/files with snapshot_manifest.json.
- A manifest alone is not a backup. A failed requested backup must stop restructuring.
- Reject overlapping source/destination workspaces and filesystem links/reparse points during backup/transfer.
- transfer_unique() reserves destinations exclusively; repeated names receive unique suffixes without overwrites.
- Verify a copied file before removing its source in move mode. Save a journal of completed transfers.
- A partial transfer returns failure and retains its snapshot/journal. It must not register a successful new project.
- Use the Adoption dialog's “กู้คืนจากสำรอง...” action and select snapshot_manifest.json to restore.
- restore_snapshot() verifies every backup checksum before restoring original paths. Files created after the snapshot are retained for review; restoration is not an exact directory rollback.
- Snapshot restoration restores workspace files, not the global project registry. The pre-change registry is separately included in the engineering backup.

## Qt tasks

- BackgroundTasks owns QThreads until their finished signal and delivers callbacks on the GUI thread.
- Repeated requests on one key keep only the newest pending request. Old results must not update current selection.
- Capture widget values on the GUI thread; workers receive ordinary data and never access widgets.
- QTimer debounces/schedules work; synchronous filesystem/network work still requires a worker.
- Cancellation is cooperative. Do not call QThread.terminate() or destroy a running QThread.
- TaskDialogMixin defers dialog destruction until jobs finish. Main-window close drains notes and workers without blocking the event loop.
- Storage scanning checks cancellation within recursive scans, so it can stop within a large single project.

## Workspace compatibility

Use WorkspaceSchema for folder discovery instead of making every view guess independently:

| Logical role | Current folders | Adopted alternatives |
| --- | --- | --- |
| Original | 01_Original_Backup | 01_Original_Files |
| Translation | 02_Translation_Workspace | 03_Translated_Text, 02_Extracted_Text |
| Fonts | 03_Font_and_UI | 04_Font_Assets |
| Packed mod | 04_Packed_Mod | 05_Packed_Mod |
| Releases | 06_Releases | 06_Release |

This resolves existing projects without moving them. It does not change the schema consumed by separately maintained tools.

## Frozen releases

- THub.spec is the canonical PyQt6 entry. THub_2.0.spec delegates for command compatibility.
- Build into a separate staging directory. Test the frozen EXE before promoting any binaries.
- Keep dist/THub/_internal THub Python modules synchronized, but also rebuild compiled modules in the EXE/PYZ.
- promote_runtime() excludes tools and live hub_config.json, and backs up replaced runtime files.
- Preserve concurrent tool updates from other chats. Compare tool hashes immediately before/after promotion, rather than restoring an older start-of-task snapshot over active work.
- Use isolated THUB_CONFIG_PATH and THUB_SMOKE_RESULT for --smoke-test. Test fixtures must never use a real project registry.
- On this machine an unrelated icuuc.dll was collected from the build environment. thub_runtime_hook.py loads Windows' system ICU before Qt to avoid that DLL conflict. Do not replace Windows system DLLs or edit protected tool files as a workaround.
- Test source behavior and packaged routes separately. A successful PyInstaller build alone is not runtime verification.

Regression commands from the THub root:

```powershell
python -B tests/test_thub_hardening.py
python -B tests/smoke_thub.py
```

## Verified refinements 26 October 2026

- BackgroundTasks now bounds each manager to four live threads, replaces queued stale work before starting it, and discards queued side effects when cancelled. Connect idle handlers before cancelling because an all-queued manager can become idle immediately.
- A dirty note map and a separate in-flight value map prevent repeated navigation/shutdown from cancelling and duplicating identical saves. Skip setPlainText when text has not changed to preserve cursor/selection during refresh.
- Rendered image keys include file mtime_ns/size, output dimensions, crop and progress. Refreshing one card must never clear a class-wide cache. Bound both the entry count and byte estimate; QPixmap stays on the GUI thread.
- Gallery metadata and QImage thumbnail decoding run in workers. Cache GUI-delivered QImages at 64 entries/16 MiB; create QPixmap only in the result callback. Deduplicate per-file decoding and discard callbacks to deleted labels.
- Pruning os.walk requires changing dirs in place. A depth check followed only by continue still traverses the uninspected descendants. Check signatures at the boundary before pruning children.
- Build knowledge catalogs privately and atomically publish a replacement. Title caches and any attached Bible detection cache belong to the same catalog generation. Failed refreshes retain the previous catalog.
- Every auto-download queue key/listener must be released on success and failure. Enqueue and worker retirement share a lock, so the last-empty observation cannot strand a new request. Check cancellation between candidates and network requests; a current blocking request remains bounded by its timeout.
- Full move verification hashes every byte, including large archive middles. A sampled hash cannot authorize deletion of a source. Copy into a uniquely-owned staging directory, verify, then publish. Never recursively delete a user destination after verification failure.
- Merge commits retain overwritten destination files and a manifest under .thub-move-previous-*. Roll back failed commits and keep source on registry failure. Recheck source identities/tree before cleanup and remove only verified original paths; preserve files created during the move.
- Cross-drive containment checks must catch commonpath's ValueError on Windows and compare normalized path case. Different volumes cannot contain one another.
- Cached storage results do not need another full registry write. Bound intermediate persistence frequency and always signal completion even when cache saving fails.
- Confirm both loose source parity and embedded Python code parity. Copying current .py files into _internal can leave stale compiled modules in the executable archive.

Expanded regression command:

```powershell
python -B -m unittest discover -s tests -p 'test_*.py'
python -B tests/benchmark_thub_runtime.py --projects 60 --rounds 3 --output scratch/runtime_benchmark.json
```

The benchmark uses disposable generated covers and projects with network/storage scanning disabled during timed rendering. It is not a certification of 60 FPS or real network throughput.

## First window and actual image readiness

The startup follow-up on 26 October 2026 uses `core.startup_images.StartupImageService` shared by Dashboard cards and Hero covers. Pass the Dashboard's BackgroundTasks manager to the service and pass `image_service=service` to ProjectCardQt. A missing argument retains the synchronous standalone-card API for existing callers.

- `request()` returns a cached final rectangular QImage or None while a worker decodes it. A null QImage denotes a completed but unreadable image, allowing stable placeholders without endless retries.
- `decode()` uses QImageReader downsampling, then applies scale/crop on a worker. It creates no QPixmap or QWidget. GUI callbacks paint the delivered rectangle once; applying crop/zoom again would distort it.
- Keys include mtime_ns/size, dimensions, crop and zoom. In-flight requests are deduplicated, with an LRU of at most 128 images / 32 MiB.
- Cards expose `poster_ready`; Dashboard exposes `startup_ready()` to distinguish a visible window from completed images. Benchmarks must wait for both card delivery and owned jobs to drain.
- Image close cancels only its own task keys with `BackgroundTasks.cancel(key)`. It must not cancel pending notes that use the same manager.
- Close/reopen changes a generation. Ignore callbacks from older generations, reset pending card identities on generation changes, and do not cache a closing placeholder as a completed image.
- A failed note save can keep the main window open. Reopen the image service before allowing continued interaction and note retry.
- Keep HTTP and Pillow imports inside Steam functions that need them, so a local cover-cache lookup does not import networking and image-manipulation packages.
- Apply a global stylesheet once and avoid copying the same sheet onto the main window, which repeats selector matching for its widget tree.

Use `tests/benchmark_thub_startup.py` for before/after startup timing. It supports a saved source ZIP, fresh-process samples, frozen EXE dispatch, first Paint, image-complete readiness, heartbeat and shutdown. Fixture generation occurs before timed launch. Retain source profiles separately from unprofiled frozen comparisons and state the warm-filesystem/offscreen boundary beside the timing claims.
