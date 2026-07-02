using System.Text;
using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using UndertaleModLib.Util;

EnsureDataLoaded();

string stringsPath = "Export_Strings.txt";
using (StreamWriter writer = new StreamWriter(stringsPath, false, new UTF8Encoding(true)))
{
    foreach (var str in Data.Strings)
    {
        string content = str.Content ?? "";
        // Escape newlines to make sure each string is on exactly one line
        content = content.Replace("\r", "\\r").Replace("\n", "\\n");
        writer.WriteLine(content);
    }
}
