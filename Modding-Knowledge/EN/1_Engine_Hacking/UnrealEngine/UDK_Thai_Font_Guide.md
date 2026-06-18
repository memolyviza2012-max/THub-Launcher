# 🛠️ Guide to Creating Thai Fonts for XCOM with UDK

Creating a Canvas font for Unreal Engine 3 yourself is an ultimate modding skill! And here is the detailed step-by-step process from start to finish:

## 1. Finding and Downloading the UDK Program
**UDK (Unreal Development Kit)** is a free game engine version previously released by Epic Games. Since XCOM was released in 2012, we should use a UDK version from around the same year.
- It is recommended to download it from **ModDB** (search Google for `UDK 2012 Download ModDB` or `UDK 2011`).
- Once downloaded, install it on your computer normally.

## 2. Preparing Characters to Embed into the Font
The UE3 system will "Rasterize" the characters we specify and save them as an image file. Therefore, we need to prepare all the characters for it. Please copy the text in the box below to prepare:

```text
 !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤลฦวศษสหฬอฮฯะัาำิีึืฺุู฿เแโใไๅๆ็่้๊๋์ํ๎๏๐๑๒๓๔๕๖๗๘๙๚๛
```

## 3. Steps to Create a Font in UDK
1. Open the **UDK Editor** program (it might take a while to load the first time).
2. Once opened, find the **Content Browser** window (usually at the bottom, or click the folder icon with a magnifying glass at the top).
3. In the bottom left corner of the Content Browser, click the **New** button.
4. A window will pop up to configure as follows:
   - **Package:** Type the desired file name, e.g., `XcomThaiFont` (no spaces).
   - **Grouping:** Leave it blank.
   - **Name:** Type the font name, e.g., `SubtitleThai` (no spaces).
   - **Factory:** Select `Font`.
   - Click the **OK** button.
5. A **Font Properties** window will pop up:
   - **FontName:** Select a Thai font available on your computer (e.g., `Tahoma`, `DB Helvethaica`, or `Kanit` which are easy to read).
   - **Height:** Font size. It's recommended to try setting it around `24` or `28`.
   - **CharacterSet:** Change from Default to `Custom`.
   - **Chars:** Copy all English and Thai characters from step 2 and **Paste** them completely into this box.
   - Click the **OK** button.
6. The program will process for a moment, and then you will see your font icon appear in the Content Browser (if you double-click to view it, you will see that the program has successfully prepared the Thai character images!).

## 4. Saving the File
1. In the Content Browser window, right-click the package name `XcomThaiFont` (on the left side) and select **Save**.
2. Choose any location to save the file. You will then have the **`XcomThaiFont.upk`** file in your possession! 🎉

## 5. Installing into the XCOM Game
1. Place the `XcomThaiFont.upk` file in the folder `F:\SteamLibrary\steamapps\common\XCom-Enemy-Unknown\XComGame\CookedPCConsole`
2. Go in and edit the game's `DefaultEngine.ini` file.
3. Search for the line `SubtitleFontName=UEFonts.SubtitleFont`
4. Change it to point to our font like this:
   ```ini
   SubtitleFontName=XcomThaiFont.SubtitleThai
   ```
5. Save the INI file and enter the game to test the cutscenes right away!

> [!NOTE]
> **What you should know about floating vowels:**
> Using a standard Thai font directly might cause a slight issue of "floating vowels" or "imperfectly overlapping vowels" (for example, the tone mark over the word "ที่" might float a bit high). This is a limitation of older game engines.
> 
> However, it will make Thai 100% readable without having to waste time doing PUA or hardcoding subtitles into videos! It's considered the most worthwhile starting point!


---
**Created by:** [NodNuatTranslator](https://www.facebook.com/NodNuatTranslator/)
