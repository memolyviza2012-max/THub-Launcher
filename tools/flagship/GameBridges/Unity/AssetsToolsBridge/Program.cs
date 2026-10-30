using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.Json;
using AssetsTools.NET;
using AssetsTools.NET.Extra;

namespace THub.Unity.NativeAssetPacker;

public static class Program
{
    public static int Main(string[] args)
    {
        if (args.Length == 0 || args.Contains("--help") || args.Contains("-h"))
        {
            PrintUsage();
            return 0;
        }

        string? inputPath = null;
        string? outputPath = null;
        string? translationsPath = null;
        string? dummyDllDirectory = null;
        string? unityVersion = "2020.3.22f1";
        string? classDataPath = null;
        string? fontBundlePath = null;
        long targetFontPathId = 0;
        long targetMaterialPathId = 0;
        long targetAtlasPathId = 0;
        bool forceOverwrite = false;
        List<string> targetFields = new() { "EN", "English", "m_StringEN", "m_NameEN", "m_CommentEN", "m_DescEN", "m_TitleEN" };

        for (int i = 0; i < args.Length; i++)
        {
            string arg = args[i];
            if (arg == "--input" && i + 1 < args.Length) inputPath = Path.GetFullPath(args[++i]);
            else if (arg == "--output" && i + 1 < args.Length) outputPath = Path.GetFullPath(args[++i]);
            else if (arg == "--translations" && i + 1 < args.Length) translationsPath = Path.GetFullPath(args[++i]);
            else if (arg == "--dummy-dlls" && i + 1 < args.Length) dummyDllDirectory = Path.GetFullPath(args[++i]);
            else if (arg == "--unity-version" && i + 1 < args.Length) unityVersion = args[++i];
            else if (arg == "--classdata" && i + 1 < args.Length) classDataPath = Path.GetFullPath(args[++i]);
            else if (arg == "--font-bundle" && i + 1 < args.Length) fontBundlePath = Path.GetFullPath(args[++i]);
            else if (arg == "--target-font-pathid" && i + 1 < args.Length) targetFontPathId = long.Parse(args[++i], CultureInfo.InvariantCulture);
            else if (arg == "--target-material-pathid" && i + 1 < args.Length) targetMaterialPathId = long.Parse(args[++i], CultureInfo.InvariantCulture);
            else if (arg == "--target-atlas-pathid" && i + 1 < args.Length) targetAtlasPathId = long.Parse(args[++i], CultureInfo.InvariantCulture);
            else if (arg == "--target-fields" && i + 1 < args.Length)
            {
                targetFields = args[++i].Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries).ToList();
            }
            else if (arg == "--force") forceOverwrite = true;
        }

        if (string.IsNullOrEmpty(inputPath) || !File.Exists(inputPath))
        {
            Console.Error.WriteLine("Error: Valid --input asset file is required.");
            return 1;
        }
        if (string.IsNullOrEmpty(outputPath))
        {
            Console.Error.WriteLine("Error: --output asset file path is required.");
            return 1;
        }
        if (File.Exists(outputPath) && !forceOverwrite)
        {
            Console.Error.WriteLine($"Error: Output file '{outputPath}' already exists. Use --force to overwrite.");
            return 1;
        }
        if (string.IsNullOrEmpty(translationsPath) || !File.Exists(translationsPath))
        {
            Console.Error.WriteLine("Error: Valid --translations JSON file is required.");
            return 1;
        }

        // Locate classdata.tpk
        if (string.IsNullOrEmpty(classDataPath) || !File.Exists(classDataPath))
        {
            string candidate = Path.Combine(AppContext.BaseDirectory, "classdata.tpk");
            if (File.Exists(candidate)) classDataPath = candidate;
            else
            {
                candidate = @"E:\Mod_Workspace\Tool\UABE\uabea-windows\classdata.tpk";
                if (File.Exists(candidate)) classDataPath = candidate;
            }
        }
        if (string.IsNullOrEmpty(classDataPath) || !File.Exists(classDataPath))
        {
            Console.Error.WriteLine("Error: classdata.tpk could not be located. Provide via --classdata <path>.");
            return 1;
        }

        // Parse translations JSON
        // Structure: PathID -> (Source -> Queue<Translation>)
        Dictionary<long, Dictionary<string, Queue<string>>> translationQueuesByPathId = new();
        using (JsonDocument doc = JsonDocument.Parse(File.ReadAllText(translationsPath)))
        {
            JsonElement root = doc.RootElement;
            JsonElement tablesElement = root;
            if (root.ValueKind == JsonValueKind.Object && root.TryGetProperty("tables", out JsonElement tElem))
            {
                tablesElement = tElem;
            }

            foreach (JsonProperty tableProp in tablesElement.EnumerateObject())
            {
                if (!long.TryParse(tableProp.Name, NumberStyles.Integer, CultureInfo.InvariantCulture, out long pathId))
                {
                    continue;
                }

                Dictionary<string, Queue<string>> queueDict = new(StringComparer.Ordinal);
                if (tableProp.Value.ValueKind == JsonValueKind.Array)
                {
                    foreach (JsonElement row in tableProp.Value.EnumerateArray())
                    {
                        string source = "";
                        string trans = "";
                        if (row.TryGetProperty("source", out JsonElement srcEl)) source = srcEl.GetString() ?? "";
                        if (row.TryGetProperty("translation", out JsonElement transEl)) trans = transEl.GetString() ?? "";

                        if (string.IsNullOrEmpty(source) || string.IsNullOrEmpty(trans)) continue;

                        if (!queueDict.TryGetValue(source, out Queue<string>? queue))
                        {
                            queue = new Queue<string>();
                            queueDict.Add(source, queue);
                        }
                        queue.Enqueue(trans);
                    }
                }
                translationQueuesByPathId[pathId] = queueDict;
            }
        }

        Console.WriteLine($"[NativeAssetPacker] Loaded {translationQueuesByPathId.Count} table(s) with translation queues.");

        // Initialize AssetsTools Manager
        AssetsManager manager = new();
        manager.LoadClassPackage(classDataPath);
        manager.LoadClassDatabaseFromPackage(unityVersion);

        if (!string.IsNullOrEmpty(dummyDllDirectory) && Directory.Exists(dummyDllDirectory))
        {
            Console.WriteLine($"[NativeAssetPacker] Using MonoCecil DummyDlls at: {dummyDllDirectory}");
            manager.MonoTempGenerator = new MonoCecilTempGenerator(dummyDllDirectory);
        }

        AssetsFileInstance targetAssets = manager.LoadAssetsFile(inputPath, false);
        List<AssetsReplacer> replacers = new();

        // Optional Font Transplanting
        if (!string.IsNullOrEmpty(fontBundlePath) && File.Exists(fontBundlePath))
        {
            if (targetFontPathId == 0 || targetMaterialPathId == 0 || targetAtlasPathId == 0)
            {
                Console.Error.WriteLine("Error: Font transplanting requires --target-font-pathid, --target-material-pathid, and --target-atlas-pathid.");
                return 1;
            }

            Console.WriteLine($"[NativeAssetPacker] Transplanting TMP Font Asset from bundle: {fontBundlePath}");
            BundleFileInstance fontBundle = manager.LoadBundleFile(fontBundlePath, false);
            AssetsFileInstance fontAssets = manager.LoadAssetsFileFromBundle(fontBundle, 0, false);

            AssetFileInfo sourceFontInfo = fontAssets.file.Metadata.AssetInfos.Single(a => a.TypeId == 114);
            AssetFileInfo sourceTextureInfo = fontAssets.file.Metadata.AssetInfos.Single(a => a.TypeId == 28);
            AssetFileInfo sourceMaterialInfo = fontAssets.file.Metadata.AssetInfos.Single(a => a.TypeId == 21);
            AssetTypeValueField sourceFont = manager.GetBaseField(fontAssets, sourceFontInfo, AssetReadFlags.None);
            AssetTypeValueField sourceTexture = manager.GetBaseField(fontAssets, sourceTextureInfo, AssetReadFlags.None);
            AssetTypeValueField sourceMaterial = manager.GetBaseField(fontAssets, sourceMaterialInfo, AssetReadFlags.None);

            AssetFileInfo targetFontInfo = targetAssets.file.Metadata.AssetInfos.Single(a => a.PathId == targetFontPathId);
            AssetFileInfo targetMaterialInfo = targetAssets.file.Metadata.AssetInfos.Single(a => a.PathId == targetMaterialPathId);
            AssetTypeValueField targetFont = manager.GetBaseField(targetAssets, targetFontInfo, AssetReadFlags.None);
            AssetTypeValueField targetMaterial = manager.GetBaseField(targetAssets, targetMaterialInfo, AssetReadFlags.None);

            // Preserve local GameObject and Script IDs
            sourceFont["m_GameObject"]["m_FileID"].AsInt = targetFont["m_GameObject"]["m_FileID"].AsInt;
            sourceFont["m_GameObject"]["m_PathID"].AsLong = targetFont["m_GameObject"]["m_PathID"].AsLong;
            sourceFont["m_Script"]["m_FileID"].AsInt = targetFont["m_Script"]["m_FileID"].AsInt;
            sourceFont["m_Script"]["m_PathID"].AsLong = targetFont["m_Script"]["m_PathID"].AsLong;

            // Redirect material & atlas PPtrs
            sourceFont["material"]["m_FileID"].AsInt = 0;
            sourceFont["material"]["m_PathID"].AsLong = targetMaterialPathId;

            AssetTypeValueField atlasArray = sourceFont["m_AtlasTextures"]["Array"];
            AssetTypeValueField atlas = atlasArray.Children.Last();
            atlas["m_FileID"].AsInt = 0;
            atlas["m_PathID"].AsLong = targetAtlasPathId;

            sourceFont["atlas"]["m_FileID"].AsInt = 0;
            sourceFont["atlas"]["m_PathID"].AsLong = targetAtlasPathId;

            // The source SDF atlas has different dimensions and gradient metrics
            // from Fontin. Keep the game's shader reference, but transplant the
            // source material properties and point _MainTex at the local atlas.
            sourceMaterial["m_Shader"]["m_FileID"].AsInt = targetMaterial["m_Shader"]["m_FileID"].AsInt;
            sourceMaterial["m_Shader"]["m_PathID"].AsLong = targetMaterial["m_Shader"]["m_PathID"].AsLong;
            foreach (AssetTypeValueField texEnv in sourceMaterial["m_SavedProperties"]["m_TexEnvs"]["Array"].Children)
            {
                if (texEnv.Children.Count < 2 || texEnv.Children[0].AsString != "_MainTex")
                    continue;
                AssetTypeValueField mainTexture = texEnv.Children[1]["m_Texture"];
                mainTexture["m_FileID"].AsInt = 0;
                mainTexture["m_PathID"].AsLong = targetAtlasPathId;
                break;
            }

            replacers.Add(new AssetsReplacerFromMemory(targetAssets.file, targetFontInfo, sourceFont.WriteToByteArray(false)));
            replacers.Add(new AssetsReplacerFromMemory(targetAssets.file, targetMaterialInfo, sourceMaterial.WriteToByteArray(false)));
            replacers.Add(new AssetsReplacerFromMemory(
                targetAssets.file,
                targetAssets.file.Metadata.AssetInfos.Single(a => a.PathId == targetAtlasPathId),
                sourceTexture.WriteToByteArray(false)
            ));
            Console.WriteLine("[NativeAssetPacker] Successfully prepared TMP font and atlas texture replacers.");
        }

        // Pack localized MonoBehaviour tables
        int totalReplaced = 0;
        int totalUnmatched = 0;

        foreach ((long pathId, Dictionary<string, Queue<string>> queues) in translationQueuesByPathId)
        {
            AssetFileInfo? tableInfo = targetAssets.file.Metadata.AssetInfos.SingleOrDefault(a => a.PathId == pathId);
            if (tableInfo == null)
            {
                Console.WriteLine($"[NativeAssetPacker] Warning: PathID {pathId} was not found in target asset file. Skipping.");
                continue;
            }

            AssetTypeValueField tableRoot = manager.GetBaseField(targetAssets, tableInfo, AssetReadFlags.None);
            int tableChanged = ReplaceStringsRecursive(tableRoot, queues, targetFields);
            int tableUnmatched = queues.Values.Sum(q => q.Count);

            totalReplaced += tableChanged;
            totalUnmatched += tableUnmatched;

            Console.WriteLine($"[NativeAssetPacker] PathID={pathId}: Replaced={tableChanged}, Remaining Unmatched={tableUnmatched}");
            replacers.Add(new AssetsReplacerFromMemory(targetAssets.file, tableInfo, tableRoot));
        }

        if (totalReplaced == 0 && replacers.Count == 0)
        {
            Console.Error.WriteLine("Error: No localized fields were changed or matched.");
            manager.UnloadAll(true);
            return 1;
        }

        // Create directory and write destination assets file
        Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);
        using (FileStream stream = File.Open(outputPath, FileMode.Create, FileAccess.Write, FileShare.None))
        using (AssetsFileWriter writer = new(stream))
        {
            targetAssets.file.Write(writer, 0, replacers, manager.ClassDatabase);
        }

        manager.UnloadAll(true);
        Console.WriteLine($"[NativeAssetPacker] SUCCESS: Created native packed asset at: {outputPath}");
        Console.WriteLine($"[NativeAssetPacker] Summary: Total Replaced Strings = {totalReplaced}, Total Unmatched = {totalUnmatched}");
        return 0;
    }

    private static int ReplaceStringsRecursive(
        AssetTypeValueField field,
        Dictionary<string, Queue<string>> queues,
        List<string> targetFields
    )
    {
        int changed = 0;

        if (field.TypeName == "string")
        {
            bool isTargetField = false;
            foreach (string tf in targetFields)
            {
                if (field.FieldName.Equals(tf, StringComparison.OrdinalIgnoreCase) ||
                    field.FieldName.EndsWith(tf, StringComparison.OrdinalIgnoreCase))
                {
                    isTargetField = true;
                    break;
                }
            }

            if (isTargetField)
            {
                string source = field.AsString;
                if (queues.TryGetValue(source, out Queue<string>? queue) && queue.Count > 0)
                {
                    field.AsString = queue.Dequeue();
                    changed++;
                }
            }
        }

        foreach (AssetTypeValueField child in field.Children)
        {
            changed += ReplaceStringsRecursive(child, queues, targetFields);
        }

        return changed;
    }

    private static void PrintUsage()
    {
        Console.WriteLine("THub NativeAssetPacker - Unity IL2CPP Serialized Asset Repacker");
        Console.WriteLine("Usage:");
        Console.WriteLine("  NativeAssetPacker --input <original.assets> --output <packed.assets> --translations <map.json> [options]");
        Console.WriteLine();
        Console.WriteLine("Options:");
        Console.WriteLine("  --dummy-dlls <dir>              Path to Il2CppDumper DummyDll directory for MonoCecil");
        Console.WriteLine("  --unity-version <ver>           Target Unity version (default: 2020.3.22f1)");
        Console.WriteLine("  --classdata <path>              Explicit path to classdata.tpk");
        Console.WriteLine("  --target-fields <f1,f2,...>     Comma-separated field suffixes or exact names to replace (default: EN,English,m_StringEN,m_NameEN)");
        Console.WriteLine("  --font-bundle <path>            Path to Unity TMP Font AssetBundle to transplant");
        Console.WriteLine("  --target-font-pathid <id>       PathID of target FontAsset");
        Console.WriteLine("  --target-material-pathid <id>   PathID of target Material");
        Console.WriteLine("  --target-atlas-pathid <id>      PathID of target Atlas Texture2D");
        Console.WriteLine("  --force                         Overwrite existing output file");
    }
}
