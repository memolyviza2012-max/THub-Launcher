# Remnant 2 → TStudio bridge

This is Approach B: Remnant 2 stores its text in a UE5 `.locres` inside a pak, so the bridge exports the locres to Modder Hub's standard `ID,Source,Translation,AI_Reference` CSV and returns the reviewed translations through the Thai-safe UTF-16LE injector.

## Export all game text

Use the pristine English locres, not a previously translated file:

```powershell
python .\Remnant2_unpacker.py "E:\Mod_Workspace\Remnant2\Check_LocRes\Original\Remnant2\Content\Localization\Remnant2\en\Remnant2.locres" --output "E:\Mod_Workspace\Remnant2\02_Translation_Workspace\Remnant2_TStudio.csv"
```

The output contains every locres string-array entry (about 53,031 rows) in TStudio's native CSV layout. Do not change the `ID` or `Source` columns. Rich-text tags (`<...>`) and placeholders (`{...}`) in `Source` must be retained in the `Translation` column.

## Translate in TStudio or TRun

1. Start `E:\Mod_Workspace\Modder_project\modder-hub\tools\flagship\TStudio\run_tstudio.bat` and open `Remnant2_TStudio.csv`.
2. Translate with TStudio, or give the same standard CSV to TRun for batch translation.
3. Save the translated file, retaining these four columns and their order: `ID,Source,Translation,AI_Reference`.

## Inject, pack, and deploy

```powershell
python .\Remnant2_packer.py "E:\Mod_Workspace\Remnant2\02_Translation_Workspace\Remnant2_TStudio.csv" "E:\Mod_Workspace\Remnant2\Check_LocRes\Original\Remnant2\Content\Localization\Remnant2\en\Remnant2.locres" --build-pak --deploy
```

`Remnant2_packer.py` exclusively calls `E:\Mod_Workspace\Remnant2\translate_locres.py`; it never uses `UnrealLocres.exe`. The final V11 pak is placed in `F:\SteamLibrary\steamapps\common\Remnant2\Remnant2\Content\Paks\~mods\pakchunk99-Windows_P.pak`.
