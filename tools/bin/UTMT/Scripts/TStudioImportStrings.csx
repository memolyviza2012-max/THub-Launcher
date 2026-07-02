using System.Text;
using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using UndertaleModLib.Util;

EnsureDataLoaded();

string stringsPath = "Import_Strings.txt";
if (!File.Exists(stringsPath)) return;

string[] lines = File.ReadAllLines(stringsPath, Encoding.UTF8);

int max = Math.Min(lines.Length, Data.Strings.Count);
for (int i = 0; i < max; i++)
{
    string content = lines[i];
    // Unescape newlines
    content = content.Replace("\\r", "\r").Replace("\\n", "\n");
    Data.Strings[i].Content = content;
}

// Automatically save as data_modded.win in the same directory
ScriptMessage("Import complete, saving...");
using (FileStream fs = new FileStream("data_modded.win", FileMode.Create, FileAccess.Write))
{
    UndertaleModLib.UndertaleIO.Write(fs, Data);
}
