# MinHook Blueprint for Dawn Engine (and others)

This guide documents the architecture for hooking game functions safely using MinHook.

## 1. Setup MinHook
Initialize MinHook during `DLL_PROCESS_ATTACH` after obtaining the base address and ensuring the environment is safe.

```cpp
MH_Initialize();
```

## 2. Locate Functions
Use a Pattern Scanner to find functions instead of hardcoded addresses.
*Example: String Allocation, String Equality, or UI Render routines.*

## 3. Create Detour Functions
Always keep the exact same signature as the target function. Use `__thiscall` if it's a member function.

```cpp
typedef const char* (__thiscall* StringAlloc_t)(void* mem_mgr, const char* original_str);
StringAlloc_t g_orig_StringAlloc = nullptr;

const char* detour_string_alloc(void* mem_mgr, const char* original_str) {
    if (!original_str) {
        if (g_orig_StringAlloc) return g_orig_StringAlloc(mem_mgr, original_str);
        return original_str;
    }

    // Insert translation logic here...
    const char* translated = lookup_translation(original_str);
    
    if (g_orig_StringAlloc) return g_orig_StringAlloc(mem_mgr, translated);
    return translated;
}
```

## 4. Install Hooks
Wrap the hook creation in error handling and log the status.

```cpp
MH_STATUS status = MH_CreateHook(
    (LPVOID)target_func_addr,
    &detour_string_alloc,
    reinterpret_cast<LPVOID*>(&g_orig_StringAlloc)
);

if (status == MH_OK) {
    MH_EnableHook((LPVOID)target_func_addr);
} else {
    // Log error (e.g., MH_STATUS_MESSAGE(status))
}
```

## 5. Cleanup
Always uninitialize MinHook when the DLL detaches (`DLL_PROCESS_DETACH`).

```cpp
MH_Uninitialize();
```


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
