# Knowledge Item: Wasteland 3 Addressables, DLC Strings, and Repack Crash Fix

## Issue 1: NullReferenceException and AsyncUploadManager Crash
**Symptoms:** 
When repacking the base game string table (`oei_assets_stringtabledata_english_e4607_53e66ff883d71916e61d183a34eab7aa.bundle`) using standard UnityPy saving methods, the game may load fine initially but will crash during specific conversation transitions (e.g., Angela Deth radio calls). Errors in the log show:
- `NullReferenceException: Object reference not set to an instance of an object`
- `AsyncUploadManager: Failed to close file archive`
- Errors related to `.resS` files.

**Root Cause:**
1. **CAB ID Mismatch:** Standard saving in UnityPy may alter the internal CAB ID, breaking hardcoded references in the game's streaming assets catalog.
2. **Missing LZ4 Compression:** Saving the bundle uncompressed bloats the file size (e.g., from 3MB to 12MB). Unity's Addressables system in Wasteland 3 aggressively streams bundles asynchronously and relies on LZ4 chunk-based decompression. Uncompressed bundles can lead to memory fragmentation or timeout issues in `AsyncUploadManager`.

**Solution:**
When modifying and saving Addressables bundles for Wasteland 3:
1. **Preserve CAB ID:** Load the bundle from raw bytes rather than path to retain original header metadata:
   ```python
   with open(bundle_path, 'rb') as f:
       env = UnityPy.load(f.read())
   ```
2. **Force LZ4 Compression:** Always use `packer="lz4"` when saving the modified bundle:
   ```python
   with open(output_bundle_path, 'wb') as f:
       f.write(env.file.save(packer="lz4"))
   ```

---

## Issue 2: Missing DLC Strings (Steeltown & Cult of the Holy Detonation)
**Symptoms:**
Even if you extract all `StringTable` entries from the base `StringTableData_English` script, thousands of DLC story strings will still be missing, leaving the DLCs in English. 

**Root Cause:**
Wasteland 3 uses separate `StringTableData_English` MonoBehaviour objects for DLCs, and they are packed into entirely different bundles located in hidden subdirectories, despite appearing in the main `catalog.json`.

**Location of DLC Bundles:**
- **DLC1 (The Battle of Steeltown):** `WL3_Data\StreamingAssets\aa\StandaloneWindows64\DLC1\oei_dlc1_assets_all.bundle`
- **DLC2 (Cult of the Holy Detonation):** `WL3_Data\StreamingAssets\aa\StandaloneWindows64\DLC2\oei_dlc2_assets_all.bundle`

**Solution:**
To fully translate the game, you must extract and inject strings for all three bundles independently using UnityPy. Ensure you maintain the correct folder structure (`WL3_Data\StreamingAssets\aa\StandaloneWindows64\DLC1\...`) when releasing the mod.
