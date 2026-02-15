# International Superstar Soccer Deluxe - SNES Disassembly

A full disassembly of **International Superstar Soccer Deluxe** (SNES), enabling ROM hacking, modding, and custom builds. This project exposes all game data in human-readable assembly, allowing you to edit teams, player names, stats, graphics, palettes, stadium banners, audio, and more.

**Supported ROM versions:**
- USA *(base version for this disassembly)*

**Framework:** [SNES ROM Framework v1.3.1](https://github.com/Yoshifanatic1/SNES-ROM-Framework) (included in download)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Extracting Assets](#extracting-assets)
4. [Building the ROM](#building-the-rom)
5. [Project Structure](#project-structure)
6. [Editing Teams](#editing-teams)
7. [Editing Player Names](#editing-player-names)
8. [Editing Player/Team Palettes (Kit Colors)](#editing-playerteam-palettes-kit-colors)
9. [Editing Closeup Player Appearance](#editing-closeup-player-appearance)
10. [Editing Stadium Fan Colors](#editing-stadium-fan-colors)
11. [Editing Stadium Banners and Graphics](#editing-stadium-banners-and-graphics)
12. [Editing Title Screen Graphics](#editing-title-screen-graphics)
13. [Editing Team Flags](#editing-team-flags)
14. [Editing Team Selection Screen](#editing-team-selection-screen)
15. [Editing Splash Screens](#editing-splash-screens)
16. [Editing In-Game HUD and Text](#editing-in-game-hud-and-text)
17. [Editing Font Graphics](#editing-font-graphics)
18. [Editing Scenario Mode Data](#editing-scenario-mode-data)
19. [Editing Game Settings and Defaults](#editing-game-settings-and-defaults)
20. [Editing Audio (Music and Samples)](#editing-audio-music-and-samples)
21. [Graphics Format Reference](#graphics-format-reference)
22. [Palette Format Reference](#palette-format-reference)
23. [File Naming Conventions](#file-naming-conventions)
24. [Tips and Troubleshooting](#tips-and-troubleshooting)
25. [ROM Verification](#rom-verification)

---

## Prerequisites

| Tool | Purpose | Notes |
|------|---------|-------|
| **Asar** | 65816 assembler | Must be placed in a `Global/` folder one level above the project root. Download from [the Asar releases page](https://github.com/RPGHacker/asar/releases) |
| **Clean SNES ROM** | Asset extraction source | Headerless USA copy of International Superstar Soccer Deluxe |
| **Tile editor** | Editing `.bin` graphics | [YY-CHR](https://www.romhacking.net/utilities/119/), [Tilemap Studio](https://github.com/Rangi42/tilemap-studio), or similar SNES 4bpp tile editor |
| **Palette editor** | Editing `.tpl` palette files | Any hex editor or a dedicated SNES palette tool |
| **Text editor** | Editing `.asm` source files | Any editor with syntax highlighting for 65816 ASM (VS Code with a 65816 extension recommended) |
| **Windows** | Running `.bat` build scripts | Or use Wine/WSL on Linux/macOS |

---

## Initial Setup

1. **Clone this repository** (or extract the download):
   ```
   git clone <repository-url>
   ```

2. **Place the Asar assembler** in a `Global/` folder located one level above the project root:
   ```
   Parent_Folder/
   ├── Global/
   │   └── asar.exe          <-- Asar assembler binary
   │   └── AssembleFile.asm   <-- Framework assembly entry point
   ├── international-superstar-soccer-deluxe-snes-disassembly/
   │   └── International_Superstar_Soccer_Deluxe/
   │       └── ...
   ```

3. **Obtain a headerless, clean USA ROM** of International Superstar Soccer Deluxe. Verify its integrity with the MD5 hash:
   ```
   USA = 345ddedcd63412b9373dabb67c11fc05
   ```
   If your ROM has a 512-byte header, remove it first (many ROM tools can do this).

---

## Extracting Assets

Before you can build or edit the ROM, you must extract binary assets (graphics, palettes, tilemaps, audio) from the original ROM.

1. **Copy your clean ROM** into the `AsarScripts/` folder and rename it:
   - For USA: `ISSD_USA.sfc`

2. **Run the extraction script:**
   ```
   cd International_Superstar_Soccer_Deluxe/AsarScripts/
   ExtractAssets.bat
   ```

3. When prompted, enter `0` for the USA ROM.

4. The script will extract all assets into the appropriate directories:
   - `Graphics/` - Uncompressed graphics (`.bin`)
   - `Graphics/Compressed/` - Compressed graphics (`.bin`)
   - `Graphics/DynamicSprites/` - Dynamic sprite data (`.bin`)
   - `Palettes/` - Palette files (`.tpl`)
   - `Tilemaps/Compressed/` - Compressed tilemap data (`.bin`)
   - `Tilemaps/Compressed/Map32/` - 32x32 tilemap data (`.bin`)
   - `CompressedOAMData/` - Compressed sprite/OAM data (`.bin`)
   - `SPC700/` - Audio engine binary (`.bin`)
   - `SPC700/Music/` - Music sequence data (`.bin`)
   - `SPC700/Samples/` - BRR audio samples (`.brr`, `.bin`)

5. A file `AssetsExtracted.txt` is created to signal that extraction completed. **Do not delete this file.**

---

## Building the ROM

Once assets are extracted, you can assemble a playable ROM:

1. **Run the assembly script:**
   ```
   cd International_Superstar_Soccer_Deluxe/
   Assemble_ISSD.bat
   ```

2. When prompted, enter the ROM version:
   - `ISSD_U` for USA
   - `HACK_<name>` for a custom ROM map (see [Custom ROM Versions](#tips-and-troubleshooting))

3. The script performs multiple assembly passes:
   - **Pass 0:** Initial setup/validation
   - **Pass 4:** SPC700 audio block assembly
   - **Pass 1:** Main ROM code assembly
   - **Pass 6:** Firmware check
   - **Pass 2:** Final assembly
   - **Pass 3:** Checksum correction

4. The output ROM is created in the project folder:
   - `International Superstar Soccer Deluxe (USA).sfc`

5. After the build completes, press Enter to re-assemble (useful for iterative editing).

---

## Project Structure

```
International_Superstar_Soccer_Deluxe/
│
├── Assemble_ISSD.bat                  # Main build script
├── Misc_Defines_ISSD.asm              # Game constants (team IDs, stadium IDs, weather, etc.)
├── RAM_Map_ISSD.asm                   # RAM address definitions
├── Routine_Macros_ISSD.asm            # Main game code + all data tables (~186K lines)
├── SNES_Macros_ISSD.asm               # SNES hardware macros (palette scripts, menus)
│
├── AsarScripts/
│   ├── ExtractAssets.bat              # Asset extraction from clean ROM
│   ├── AssetPointersAndFiles.asm      # Asset pointer tables and filenames
│   └── ...                            # Other extraction/disassembly scripts
│
├── RomMap/
│   └── ROM_Map_ISSD_U.asm            # USA ROM configuration and bank layout
│
├── SPC700/                            # Audio processor code and data
│   ├── ARAM_Map_ISSD.asm             # Audio RAM layout
│   ├── SPC700_Routine_Macros_ISSD.asm # Audio engine code
│   ├── Music/                         # Extracted music sequences
│   └── Samples/                       # Extracted BRR audio samples
│
├── Graphics/                          # Extracted uncompressed graphics
│   ├── Compressed/                    # Extracted compressed graphics
│   └── DynamicSprites/                # Extracted dynamic sprite data
│
├── Palettes/                          # Extracted palette files (.tpl)
├── Tilemaps/
│   └── Compressed/                    # Extracted tilemaps
│       └── Map32/                     # 32x32 tilemaps
│
├── CompressedOAMData/                 # Extracted OAM/sprite data
├── GarbageData/                       # Unused/padding data from ROM
│
├── Tables/
│   └── Fonts/
│       ├── SmallMenuText.txt          # Character encoding for small text
│       └── TallMenuText.txt           # Character encoding for tall text
│
└── Custom/
    └── Patches/
        └── Default/                   # Custom patch files
```

---

## Editing Teams

### Team IDs

All 43 teams are defined in `Misc_Defines_ISSD.asm` (lines 8-50):

| Define | Team | ID |
|--------|------|----|
| `!Define_ISSD_TeamIDs_Italy` | Italy | `$0000` |
| `!Define_ISSD_TeamIDs_Holland` | Holland | `$0002` |
| `!Define_ISSD_TeamIDs_England` | England | `$0004` |
| `!Define_ISSD_TeamIDs_Norway` | Norway | `$0006` |
| `!Define_ISSD_TeamIDs_Spain` | Spain | `$0008` |
| `!Define_ISSD_TeamIDs_Ireland` | Ireland | `$000A` |
| `!Define_ISSD_TeamIDs_Portugal` | Portugal | `$000C` |
| `!Define_ISSD_TeamIDs_Denmark` | Denmark | `$000E` |
| `!Define_ISSD_TeamIDs_Germany` | Germany | `$0010` |
| `!Define_ISSD_TeamIDs_France` | France | `$0012` |
| `!Define_ISSD_TeamIDs_Belgium` | Belgium | `$0014` |
| `!Define_ISSD_TeamIDs_Sweden` | Sweden | `$0016` |
| `!Define_ISSD_TeamIDs_Romania` | Romania | `$0018` |
| `!Define_ISSD_TeamIDs_Bulgaria` | Bulgaria | `$001A` |
| `!Define_ISSD_TeamIDs_Russia` | Russia | `$001C` |
| `!Define_ISSD_TeamIDs_Switzerland` | Switzerland | `$001E` |
| `!Define_ISSD_TeamIDs_Greece` | Greece | `$0020` |
| `!Define_ISSD_TeamIDs_Croatia` | Croatia | `$0022` |
| `!Define_ISSD_TeamIDs_Austria` | Austria | `$0024` |
| `!Define_ISSD_TeamIDs_Wales` | Wales | `$0026` |
| `!Define_ISSD_TeamIDs_Scotland` | Scotland | `$0028` |
| `!Define_ISSD_TeamIDs_NorthIreland` | North Ireland | `$002A` |
| `!Define_ISSD_TeamIDs_CzechRepublic` | Czech Republic | `$002C` |
| `!Define_ISSD_TeamIDs_Poland` | Poland | `$002E` |
| `!Define_ISSD_TeamIDs_Japan` | Japan | `$0030` |
| `!Define_ISSD_TeamIDs_SouthKorea` | South Korea | `$0032` |
| `!Define_ISSD_TeamIDs_Turkey` | Turkey | `$0034` |
| `!Define_ISSD_TeamIDs_Nigeria` | Nigeria | `$0036` |
| `!Define_ISSD_TeamIDs_Cameroon` | Cameroon | `$0038` |
| `!Define_ISSD_TeamIDs_Morocco` | Morocco | `$003A` |
| `!Define_ISSD_TeamIDs_Brazil` | Brazil | `$003C` |
| `!Define_ISSD_TeamIDs_Argentina` | Argentina | `$003E` |
| `!Define_ISSD_TeamIDs_Columbia` | Colombia | `$0040` |
| `!Define_ISSD_TeamIDs_Mexico` | Mexico | `$0042` |
| `!Define_ISSD_TeamIDs_USA` | USA | `$0044` |
| `!Define_ISSD_TeamIDs_Uruguay` | Uruguay | `$0046` |
| `!Define_ISSD_TeamIDs_AllStar` | All-Star | `$0048` |
| `!Define_ISSD_TeamIDs_EuroStarA` | Euro Star A | `$004A` |
| `!Define_ISSD_TeamIDs_EuroStarB` | Euro Star B | `$004C` |
| `!Define_ISSD_TeamIDs_AsianStar` | Asian Star | `$004E` |
| `!Define_ISSD_TeamIDs_AfricanStar` | African Star | `$0050` |
| `!Define_ISSD_TeamIDs_AllAmericanStar` | All American Star | `$0052` |
| `!Define_ISSD_TeamIDs_ChallengeMode` | Challenge Mode | `$0054` |

### Stadium IDs

Eight stadiums are defined in `Misc_Defines_ISSD.asm` (lines 52-59):

| Define | Stadium | ID |
|--------|---------|-----|
| `!Define_ISSD_StadiumIDs_Japan` | Japan | `$0000` |
| `!Define_ISSD_StadiumIDs_USA` | USA | `$0001` |
| `!Define_ISSD_StadiumIDs_Spain` | Spain | `$0002` |
| `!Define_ISSD_StadiumIDs_Italy` | Italy | `$0003` |
| `!Define_ISSD_StadiumIDs_England` | England | `$0004` |
| `!Define_ISSD_StadiumIDs_Germany` | Germany | `$0005` |
| `!Define_ISSD_StadiumIDs_Brazil` | Brazil | `$0006` |
| `!Define_ISSD_StadiumIDs_Nigeria` | Nigeria | `$0007` |

### Stadium Name Strings

Stadium display names are located in `Routine_Macros_ISSD.asm` at `DATA_87CA9B` (line ~104831):

```asm
DATA_87CA9B:
    db "  JAPAN"
    db "  U.S.A"
    db "  SPAIN"
    db "  ITALY"
    db "ENGLAND"
    db "GERMANY"
    db " BRAZIL"
    db "NIGERIA"
```

Each name is 7 characters, padded with leading spaces. Edit these strings to change the displayed stadium names.

---

## Editing Player Names

### Player Name Tables

All player names are stored in `Routine_Macros_ISSD.asm` starting at line ~99485. The master pointer table at `DATA_878138` (line 99487) contains pointers to each team's roster.

Each team has **20 players**, stored as **8-character fixed-width strings** using the `TallMenuText.txt` character encoding.

**Example - Italy (DATA_87818E, line ~99498):**
```asm
DATA_87818E:
    db "Pagani  "
    db "Premoli "
    db " Pabi   "
    db "Antonini"
    db "Graziano"
    db " Zappa  "
    db "DeSinone"
    db "Passaro "
    db "Galfano "
    db "Carboni "
    db "Coliuto "
    db "Mancini "
    db "Bucario "
    db "Pabrizio"
    db "Riggio  "
    db " Zanga  "
    db "Bittani "
    db "Anticoli"
    db "Cortese "
    db "Fidrini "
```

### How to Edit Player Names

1. Open `Routine_Macros_ISSD.asm` and search for the team's `DATA_` label (see list below).
2. Each name must be **exactly 8 characters** (pad with spaces as needed).
3. Names use the character set from `Tables/Fonts/TallMenuText.txt`.
4. Available characters: `A-Z`, `a-z`, `0-9`, `.`, `-`, `'`, `/`, space, and a few special characters.

### Team Roster Label Reference

| Team | Label | Line |
|------|-------|------|
| Italy | `DATA_87818E` | ~99498 |
| Holland | `DATA_87822E` | ~99520 |
| England | `DATA_8782CE` | ~99542 |
| Norway | `DATA_87836E` | ~99564 |
| Spain | `DATA_87840E` | ~99586 |
| Ireland | `DATA_8784AE` | ~99608 |
| Portugal | `DATA_87854E` | ~99630 |
| Denmark | `DATA_8785EE` | ~99652 |
| Germany | `DATA_87868E` | ~99674 |
| France | `DATA_87872E` | ~99696 |
| Belgium | `DATA_8787CE` | ~99718 |
| Sweden | `DATA_87886E` | ~99740 |
| Romania | `DATA_87890E` | ~99762 |
| Bulgaria | `DATA_8789AE` | ~99784 |
| Russia | `DATA_878A4E` | ~99806 |
| Switzerland | `DATA_878AEE` | ~99828 |
| Greece | `DATA_878B8E` | ~99850 |
| Croatia | `DATA_878C2E` | ~99872 |
| Austria | `DATA_878CCE` | ~99894 |
| Wales | `DATA_878D6E` | ~99916 |
| Scotland | `DATA_878E0E` | ~99938 |
| North Ireland | `DATA_878EAE` | ~99960 |
| Czech Republic | `DATA_878F4E` | ~99982 |
| Poland | `DATA_878FEE` | ~100004 |
| Japan | `DATA_87908E` | ~100026 |
| South Korea | `DATA_87912E` | ~100048 |
| Turkey | `DATA_8791CE` | ~100070 |
| Nigeria | `DATA_87926E` | ~100092 |
| Cameroon | `DATA_87930E` | ~100114 |
| Morocco | `DATA_8793AE` | ~100136 |
| Brazil | `DATA_87944E` | ~100158 |
| Argentina | `DATA_8794EE` | ~100180 |
| Colombia | `DATA_87958E` | ~100202 |
| Mexico | `DATA_87962E` | ~100224 |
| USA | `DATA_8796CE` | ~100246 |
| Uruguay | `DATA_87976E` | ~100268 |
| All-Star Teams | `DATA_87980E` | ~100290 |

---

## Editing Player/Team Palettes (Kit Colors)

Team kit colors (jerseys, shorts, socks) during gameplay are controlled by palette pointer tables in `Routine_Macros_ISSD.asm`.

### In-Match Jersey Palettes

Three palette tables control on-field appearance (lines ~24265-24287):

| Label | Purpose | Line |
|-------|---------|------|
| `DATA_82827A` | **Home kit** palettes (Type 1) | ~24265 |
| `DATA_8282D0` | **Away kit** palettes (Type 2) | ~24273 |
| `DATA_828326` | **Goalkeeper** palettes | ~24281 |

Each table contains **43 entries** (one per team, in team ID order). Each entry is a `dw` pointer to a palette data block elsewhere in the ROM (in banks `$89xxxx`).

**To change a team's kit colors**, you need to:

1. Find the team's pointer entry in one of these tables (entries are ordered by team ID / 2).
2. Follow the pointer to the actual palette data.
3. Edit the SNES 15-bit BGR color values at that location.
4. Alternatively, edit the extracted `.tpl` palette files in the `Palettes/` folder.

### Team Palette Files

Per-team palette files are extracted to the `Palettes/` folder with names like:
- `PAL_Sprite_TeamPalettes_Italy.tpl`
- `PAL_Sprite_TeamPalettes_Brazil.tpl`
- `PAL_Sprite_TeamPalettes_Germany.tpl`
- (one for each team)

These `.tpl` files contain the SNES color data and can be edited with a hex editor or palette tool. See [Palette Format Reference](#palette-format-reference) for the file format.

---

## Editing Closeup Player Appearance

When a goal is scored or during an own goal, the game shows a closeup of a player. These closeup appearances are controlled by seven palette pointer tables at lines ~117751-118057 of `Routine_Macros_ISSD.asm`:

| Label | Controls | Line |
|-------|----------|------|
| `DATA_88FB00` | **Hair color** palettes | ~117751 |
| `DATA_88FBA8` | **Skin color** palettes | ~117795 |
| `DATA_88FC50` | **Jersey color** palettes | ~117839 |
| `DATA_88FCF8` | **Shorts/jersey cuff** palettes | ~117883 |
| `DATA_88FDA0` | **Sock color** palettes | ~117927 |
| `DATA_88FE48` | **Sock stripe** palettes | ~117971 |
| `DATA_88FEF0` | **Jersey number color** palettes | ~118015 |

Each table has **43 team entries** with **2 pointers per team** (primary player and alternate player). This controls the visual appearance of closeup celebrations per team.

**Example - Italy hair palettes:**
```asm
DATA_88FB00:
    dw DATA_89AE76,DATA_89AF16    ; Italy (player 1, player 2)
    dw DATA_89AEC6,DATA_89AE76    ; Holland
    ...
```

To change a team's closeup appearance, modify the pointer to reference a different palette data block, or edit the palette data at the referenced address.

---

## Editing Stadium Fan Colors

The audience/fan appearance in stadiums is controlled by four palette tables at the end of `Routine_Macros_ISSD.asm` (lines ~182518-182668):

### Fan Shirt Colors
**Label:** `DATA_A4F8EF` (line ~182518)

Each team has **4 palette pointers** controlling the shirt colors of fans in the stands:

```asm
DATA_A4F8EF:                           ; Info: Team fan shirt color palettes
    dw DATA_89B6DE,DATA_89B696,DATA_89B67E,DATA_89B696    ; Italy
    dw DATA_89B6B6,DATA_89B6BE,DATA_89B67E,DATA_89B6B6    ; Holland
    dw DATA_89B69E,DATA_89B6BE,DATA_89B67E,DATA_89B69E    ; England
    ...
```

### Fan Hair Colors
**Label:** `DATA_A4FA0F` (line ~182556)
- 2 palette pointers per team (hair color variation for audience members)

### Fan Skin Colors
**Label:** `DATA_A4FA9F` (line ~182594)
- 2 palette pointers per team (skin tone variation for audience members)

### Fan Flag Colors
**Label:** `DATA_A4FB2F` (line ~182632)
- 2 palette pointers per team (colors of flags waved by fans)

---

## Editing Stadium Banners and Graphics

Stadium banners are the large graphical elements displayed behind the goals and around the pitch. They are stored as compressed graphics in the `Graphics/Compressed/` folder.

### Banner Graphics Files

Each stadium has its own set of banner files:

| Stadium | Files |
|---------|-------|
| **Japan** | `GFX_Layer1_JapanStadium_Banner1.bin`, `Banner2.bin`, `Banner3.bin` |
| **USA** | `GFX_Layer1_USAStadium_Banner1.bin`, `Banner2.bin`, `Banner3.bin`, `Banner4.bin` |
| **England** | `GFX_Layer1_EnglandStadium_Banner1.bin`, `Banner3.bin`, `Banners4.bin` |
| **Spain** | `GFX_Layer1_SpainStadium_Banner1.bin`, `Banner2.bin`, `Banner3.bin` |
| **Italy** | `GFX_Layer1_ItalyStadium_Banner1.bin`, `Banner2.bin` |
| **Germany** | `GFX_Layer1_GermanyStadium_Banners3.bin` |
| **Unused** | `GFX_Layer1_UnusedBanner.bin` |

### Additional Stadium Graphics

| File | Description |
|------|-------------|
| `GFX_Layer1_InGame_StadiumWallAndAudience.bin` | Stadium walls and crowd |
| `GFX_Layer1_InGame_SoccerNet.bin` | Goal net graphics |
| `GFX_Layer1_BleachersScreen_BannerEdges1.bin` | Banner edge decorations |
| `GFX_Layer1_BleachersScreen_BannerEdges2.bin` | Banner edge decorations |
| `GFX_Layer2_PenaltyKick_ExtraBannerCorners.bin` | Penalty kick banner corners |
| `GFX_Layer2_PenaltyKick_AnimatedAudience.bin` | Animated crowd during penalties |

### Stadium Palette Files

Each stadium has associated palette files:
- `PAL_FGBG_JapanStadium_File1.tpl`, `PAL_FGBG_JapanStadium_File2.tpl`
- `PAL_FGBG_USAStadium_File1.tpl`, `PAL_FGBG_USAStadium_File2.tpl`
- `PAL_FGBG_SpainStadium_File1.tpl`, `PAL_FGBG_SpainStadium_File2.tpl`
- (similar for other stadiums)

### How to Edit Banners

1. **Locate the `.bin` file** for the banner you want to change in `Graphics/Compressed/`.
2. **Open it in a tile editor** (YY-CHR or similar) configured for SNES **4bpp** tile format.
3. **Edit the tile graphics** as desired. Keep the same tile dimensions.
4. **Save the file** with the exact same filename.
5. **Edit the matching `.tpl` palette file** in `Palettes/` if you need different colors.
6. **Rebuild the ROM** using `Assemble_ISSD.bat`.

> **Note:** Compressed graphics (in `Graphics/Compressed/`) use the game's built-in compression. The extraction script decompresses them for you. The assembler re-compresses them during the build.

---

## Editing Title Screen Graphics

The title screen is composed of multiple graphic layers:

| File | Description |
|------|-------------|
| `GFX_Layer1_TitleScreen_PlayerPortraits.bin` | The player portrait images on the title screen |
| `GFX_Sprite_TitleScreen_SmallText.bin` | Small text elements on title |
| `GFX_Sprite_TitleScreen_Logo.bin` | The game logo sprite |
| `GFX_FGBG_TitleScreen_PaintAndDeluxeBall.bin` | Paint splash and "Deluxe" ball graphic |
| `TM_Layer1_TitleScreen_Logo.bin` | Title screen Layer 1 tilemap |
| `TM_Layer2_TitleScreen_Logo.bin` | Title screen Layer 2 tilemap |
| `PAL_All_TitleScreen.tpl` | Title screen color palette |

### How to Edit the Title Screen

1. Edit `GFX_Sprite_TitleScreen_Logo.bin` in a tile editor to change the game logo.
2. Edit `GFX_Layer1_TitleScreen_PlayerPortraits.bin` to change the player portrait artwork.
3. Edit `PAL_All_TitleScreen.tpl` to change colors.
4. If you change tile layout, you may also need to edit the corresponding `TM_` tilemap files.

---

## Editing Team Flags

Team flags are split into two halves (top and bottom) and grouped by visual similarity. They are found in `Graphics/Compressed/`:

### Flag File Naming Pattern

```
GFX_Sprite_TeamFlags_[TeamGrouping]_TopHalf.bin
GFX_Sprite_TeamFlags_[TeamGrouping]_BottomHalf.bin
```

### Flag File Groups

| File Group | Teams Included |
|------------|----------------|
| `GermanyHollandRussia` | Germany, Holland, Russia |
| `ItalyFranceIrelandBelgiumRomaniaNigeria` | Italy, France, Ireland, Belgium, Romania, Nigeria |
| `EnglandNorwaySwedenDenmark` | England, Norway, Sweden, Denmark |
| `Mexico` | Mexico |
| `SouthKorea` | South Korea |
| `USA` | USA |
| `CameroonColumbia` | Cameroon, Colombia |
| `Wales` | Wales |
| `Brazil` | Brazil |
| `SpainArgentina` | Spain, Argentina |
| `Japan` | Japan |
| `BulgariaMorocco` | Bulgaria, Morocco |
| `Turkey` | Turkey |
| `NorthIreland` | North Ireland |
| `Uruguay` | Uruguay |
| `CzechRepublic` | Czech Republic |
| `AustriaPortugalPoland` | Austria, Portugal, Poland |
| `GreeceSwitzerlandScotlandCroatia` | Greece, Switzerland, Scotland, Croatia |
| `EuroStarAEuroStarBAsianStarAfricanStarAllAmericanStarAllStar` | All star teams |

To edit a flag, modify both the `_TopHalf.bin` and `_BottomHalf.bin` files for the relevant group using a tile editor.

---

## Editing Team Selection Screen

The team selection screen graphics are in `Graphics/Compressed/`:

| File | Description |
|------|-------------|
| `GFX_Sprite_TeamSelectionScreen_Players1.bin` through `Players6.bin` | Player sprites shown during team selection |
| `GFX_Layer1_TeamSelectionScreen_GradientBorders.bin` | Screen border decorations |
| `GFX_Layer3_TeamSelectionScreen_ContinentText.bin` | Continent name text graphics |
| `GFX_Layer3_TeamSelectScreen_MiscText.bin` | Miscellaneous text on selection screen |
| `GFX_Sprite_TeamSelectScreen_TeamAccessories1.bin` | Team-specific accessories (hats, etc.) |
| `GFX_Sprite_TeamSelectScreen_TeamAccessories2.bin` | Additional accessories |
| `GFX_Sprite_TeamSelectScreen_AlternateHeads.bin` | Alternate player head sprites |
| `TM_Layer1_TeamSelectScreen.bin` | Team select screen tilemap |

### Team Selection Palettes

- `PAL_Sprite_TeamSelectScreen_JerseyDetails_File1.tpl`
- `PAL_Sprite_TeamSelectScreen_JerseyDetails_File2.tpl`
- `PAL_Sprite_TeamSelectScreen_JerseyDetails_File3.tpl`
- `PAL_Sprite_TeamSelectScreen_AltHeads.tpl`
- `PAL_FG_TeamSelectScreen.tpl`

---

## Editing Splash Screens

Splash screens (tournament mode intro screens) share a common graphics set with per-mode palettes:

### Shared Graphics
| File | Description |
|------|-------------|
| `GFX_FGBG_MainMenus_SplashScreens.bin` | Shared splash screen tile graphics |
| `TM_Layer2_MainMenus_SplashScreens.bin` | Splash screen tilemap |

### Per-Mode Palettes
| File | Mode |
|------|------|
| `PAL_FGBG_InternationalSplashScreen.tpl` | International mode |
| `PAL_FGBG_WorldSeriesSplashScreen.tpl` | World Series mode |
| `PAL_FGBG_ChampionshipSplashScreen.tpl` | Championship mode |
| `PAL_FGBG_SpecialScreenSplashScreen.tpl` | Special game mode |
| `PAL_FGBG_ShortTournamentSplashScreen.tpl` | Short Tournament mode |
| `PAL_FGBG_ShortLeagueSplashScreen.tpl` | Short League mode |

To give each tournament mode a different look, edit the corresponding `.tpl` palette file.

---

## Editing In-Game HUD and Text

### In-Game Text Graphics

| File | Description |
|------|-------------|
| `GFX_Layer3_InGame_GOALTextLetters.bin` | "GOAL" text displayed on screen |
| `GFX_Layer3_InGame_FlashingTextLetters.bin` | Flashing text effects |
| `GFX_Layer3_InGame_TimerCircle.bin` | Timer circle graphics |
| `GFX_Layer3_InGame_LargeScoreNumbers.bin` | Large score number digits |
| `GFX_Layer3_InGame_PauseMenuCursor.bin` | Pause menu cursor sprite |

### Team Name Display Graphics

Each team has a **Layer 3 team name graphic** for in-game display:

```
GFX_Layer3_TeamNames_Italy.bin
GFX_Layer3_TeamNames_Holland.bin
GFX_Layer3_TeamNames_England.bin
... (one for each team)
```

These are located in the `Graphics/` folder. Edit them with a tile editor to change how team names appear during matches.

### Player In-Game Graphics

| File | Description |
|------|-------------|
| `GFX_Sprite_Ingame_PlayerJerseyDetails.bin` | Jersey detail sprites |
| `GFX_Sprite_Ingame_PlayerJerseyNumbers.bin` | Jersey number sprites |
| `GFX_Sprite_Ingame_PlayerHairStyles.bin` | Player hair style sprites |
| `PAL_Sprite_InGame_AltPlayerSkinColor.tpl` | Alternate skin tone palette |

---

## Editing Font Graphics

Font tiles are stored in multiple files:

| File | Description |
|------|-------------|
| `GFX_Layer3_SmallAndMediumFont1.bin` through `...Font10.bin` | Small and medium font tile sets |

### Character Encoding Tables

The game uses two text encoding schemes defined in `Tables/Fonts/`:

**SmallMenuText.txt** - Used for small in-game text:
- Space = `$00`, Numbers 0-9 = `$01-$0A`, Letters A-Z = `$0B-$24`
- Lowercase a-z = `$2A-$43`
- Special: `:` `$25`, `-` `$26`, `!` `$27`, `.` `$29`, `?` `$4C`

**TallMenuText.txt** - Used for menu text and player names:
- Space = `$00`, Numbers 0-9 = `$5E-$67`, Letters A-Z = `$68-$81`
- Lowercase a-z = `$82-$9B`
- Special: `!` `$52`, `.` `$54`, `-` `$57`, `'` `$5A`, `:` `$5C`

When editing player names or other text strings in the assembly, characters are automatically converted using these tables via the `table` directive.

---

## Editing Scenario Mode Data

The Scenario Mode presents 12 pre-set match situations for the player to overcome. The data for these is in `Routine_Macros_ISSD.asm` at lines ~147541-147575.

### Scenario Structure

Each scenario is a 15-byte data block:

```asm
DATA_8BFCF8:    ; Scenario 1
    db $34,$01,$14,$01,!Define_ISSD_TeamIDs_Italy,!Define_ISSD_TeamIDs_Croatia,$01,$02,$01,$04,$10,$00,$09,$40,$00
```

**Key fields (bytes 4-5):** The two team IDs that play in the scenario. You can swap in any team from the team ID table.

### Scenario Descriptions

The text shown for each scenario is at lines ~105896-105942:

```asm
DATA_87EE3B:
    db "NO.1  ITALY 1-2 CROATIA     "
    db "      1:14 ITALY'S C.K.     "
```

Each scenario has a **28-character** description line and a **28-character** detail line. Edit these to match any changes you make to the scenario data.

---

## Editing Game Settings and Defaults

### Default Menu Settings

Default values for game options are read from RAM addresses defined in `RAM_Map_ISSD.asm`:

| RAM Address | Setting | Define |
|-------------|---------|--------|
| `$001F88` | Default game time | `!RAM_ISSD_MainMenu_SelectedGameTimeSetting` |
| `$001F8C` | Default P1 team | `!RAM_ISSD_MainMenu_DefaultP1Team` |
| `$001F8E` | Default P2 team | `!RAM_ISSD_MainMenu_DefaultP2Team` |
| `$001F90` | Sound setting (stereo/mono) | `!RAM_ISSD_MainMenu_SelectedSoundSetting` |
| `$001F92` | Offside on/off | `!RAM_ISSD_MainMenu_SelectedOffSideSetting` |
| `$001F94` | Weather | `!RAM_ISSD_MainMenu_SelectedWeather` |
| `$001F98` | Foul setting | `!RAM_ISSD_MainMenu_SelectedFoulSetting` |
| `$001F9A` | Yellow card setting | `!RAM_ISSD_MainMenu_SelectedYellowCardSetting` |
| `$001F9C` | Game difficulty level | `!RAM_ISSD_MainMenu_SelectedGameLevel` |
| `$001FA0` | Referee selection | `!RAM_ISSD_MainMenu_SelectedReferee` |
| `$001FA2` | Stadium selection | `!RAM_ISSD_MainMenu_SelectedStadium` |
| `$001FA4` | Time of day | `!RAM_ISSD_MainMenu_SelectedTime` |
| `$001FE0` | Overtime on/off | `!RAM_ISSD_MainMenu_SelectedOverTimeSetting` |

### Weather Constants

```asm
!Define_ISSD_Weather_Snow = $0000
!Define_ISSD_Weather_Fine = $0001
!Define_ISSD_Weather_Rain = $0002
```

### Time of Day Constants

```asm
!Define_ISSD_Time_Day   = $0000
!Define_ISSD_Time_Dusk  = $0001
!Define_ISSD_Time_Night = $0002
```

### Handicap Settings

In-game handicap adjustments (accessible via code modifications):

| RAM Address | Setting |
|-------------|---------|
| `$00156C` | Goalie condition P1 |
| `$00156E` | Goalie condition P2 |
| `$001570` | Number of players on field P1 |
| `$001572` | Number of players on field P2 |
| `$001574` | Goalie skill level P1 |
| `$001576` | Goalie skill level P2 |

### Cheat Flags

| RAM Address | Flag |
|-------------|------|
| `$7ED854` | Dog referee flag |
| `$7ED856` | Unlock All-Star teams flag |
| `$7ED858` | Unknown cheat flag |

---

## Editing Audio (Music and Samples)

### Audio Architecture

The game uses the SNES SPC700 audio processor. Audio data is in the `SPC700/` directory:

| File | Purpose |
|------|---------|
| `SPC700_Routine_Macros_ISSD.asm` | Audio engine code |
| `SPC700_Macros_ISSD.asm` | Audio macros |
| `ARAM_Map_ISSD.asm` | Audio RAM address map |
| `ARAMPtrs_ISSD.asm` | Audio pointer tables |
| `Music/*.bin` | Music sequence data files |
| `Samples/*.brr` | BRR-encoded audio samples |

### Music IDs

Music tracks are defined in `Misc_Defines_ISSD.asm` (lines ~89-108):

| Define | Track |
|--------|-------|
| `!Define_ISSD_MusicID_KonamiScreen` | Konami logo jingle |
| `!Define_ISSD_MusicID_MainMenu` | Main menu music |
| `!Define_ISSD_MusicID_International` | International mode theme |
| `!Define_ISSD_MusicID_WorldSeries` | World Series theme |
| `!Define_ISSD_MusicID_ScenarioMenu` | Scenario mode menu |
| `!Define_ISSD_MusicID_Practicing` | Training mode music |
| `!Define_ISSD_MusicID_StaffRoll` | Credits music |
| `!Define_ISSD_MusicID_IntroCutscene` | Intro cutscene music |
| `!Define_ISSD_MusicID_GameOver` | Game over jingle |
| `!Define_ISSD_MusicID_ScenarioModeClear` | Scenario complete jingle |

### Announcer Voice IDs

All announcer voice clips are defined in `Misc_Defines_ISSD.asm` (lines ~120-194):

Examples: `CornerKick`, `GoalKick`, `ThrowIn`, `FreeKick`, `PenaltyKick`, `OffSide`, `HalfTime`, `Goal`, `GOOOOOOOOOOOOAAAAAALLLLLL`, `YellowCard`, `RedCard`, and many more.

### Streamed Samples

| Define | Sample |
|--------|--------|
| `!Define_ISSD_StreamedSampleID_VictoryMusic` | Victory music |
| `!Define_ISSD_StreamedSampleID_TitleScreenNameDrop` | Title screen voice |

---

## Graphics Format Reference

### SNES 4bpp Tile Format

Graphics `.bin` files use the SNES **4 bits-per-pixel (4bpp)** planar tile format:
- Each 8x8 tile is **32 bytes**
- Colors are stored across 4 bitplanes
- Tiles can be viewed/edited in tools like YY-CHR (set to "SNES 4BPP" mode)

### Compressed vs Uncompressed

- Files in `Graphics/` are **uncompressed** - edit directly
- Files in `Graphics/Compressed/` are **decompressed during extraction** - edit the decompressed `.bin` files; the assembler handles re-compression
- Files in `Graphics/DynamicSprites/` are **dynamic sprite** data

### Tilemap Files

Tilemap `.bin` files (prefix `TM_`) define how tiles are arranged on screen:
- Each tilemap entry is **2 bytes** (tile number + attributes)
- Attributes include: palette number, priority, horizontal/vertical flip
- `Map32/` files use 32x32 tile arrangement

---

## Palette Format Reference

### .tpl Palette Files

Extracted palette files use the `.tpl` format:
- **Header:** 4 bytes (`"TPL"` + version byte `$02`)
- **Data:** SNES 15-bit BGR color values, 2 bytes per color

### SNES Color Format

Each color is a 16-bit value in `0BBBBBGGGGGRRRRR` format:
- Bits 0-4: Red (0-31)
- Bits 5-9: Green (0-31)
- Bits 10-14: Blue (0-31)
- Bit 15: Always 0

**Example:** Pure red = `$001F`, Pure green = `$03E0`, Pure blue = `$7C00`, White = `$7FFF`, Black = `$0000`

### Editing Palettes

1. Open a `.tpl` file in a hex editor.
2. Skip the first 4 bytes (header).
3. Edit the 2-byte color values in little-endian format.
4. Save and rebuild the ROM.

Alternatively, use a SNES palette editor that supports `.tpl` files for visual editing.

---

## File Naming Conventions

All asset files follow a consistent naming convention:

| Prefix | Asset Type | Location |
|--------|-----------|----------|
| `GFX_Layer1_` | Background layer graphics | `Graphics/` or `Graphics/Compressed/` |
| `GFX_Layer2_` | Mid-ground layer graphics | `Graphics/Compressed/` |
| `GFX_Layer3_` | Foreground/UI layer graphics | `Graphics/` or `Graphics/Compressed/` |
| `GFX_Sprite_` | Sprite graphics | `Graphics/Compressed/` |
| `GFX_FGBG_` | Foreground/Background combined | `Graphics/Compressed/` |
| `TM_Layer1_` | Layer 1 tilemaps | `Tilemaps/Compressed/` |
| `TM_Layer2_` | Layer 2 tilemaps | `Tilemaps/Compressed/` |
| `TM_Layer3_` | Layer 3 tilemaps | `Tilemaps/Compressed/` |
| `TM_Map32_` | 32x32 tilemaps | `Tilemaps/Compressed/Map32/` |
| `PAL_All_` | Full-screen palettes | `Palettes/` |
| `PAL_Sprite_` | Sprite palettes | `Palettes/` |
| `PAL_FGBG_` | FG/BG palettes | `Palettes/` |
| `PAL_Layer1_` | Layer 1 palettes | `Palettes/` |
| `PAL_FG_` | Foreground palettes | `Palettes/` |

---

## Tips and Troubleshooting

### Build Fails: "Assets not extracted"
Run `ExtractAssets.bat` first. The build requires `AssetsExtracted.txt` to exist.

### Build Fails: "ROM Map file missing"
Ensure you typed the ROM version correctly (`ISSD_U`). For custom hacks, create a ROM map file in `RomMap/` following the pattern of `ROM_Map_ISSD_U.asm`.

### Custom ROM Versions
To create a custom hack version:
1. Copy `RomMap/ROM_Map_ISSD_U.asm` to `RomMap/ROM_Map_HACK_MyHack.asm`
2. At build time, enter `HACK_MyHack` as the ROM version
3. Modify the ROM map as needed for your hack

### Player Name Too Long
Player names must be **exactly 8 characters**. Pad shorter names with spaces.

### Colors Look Wrong After Editing
- Verify you're using SNES 15-bit BGR format (not RGB)
- Check that palette files still have the 4-byte `TPL` header
- Make sure you're editing the correct palette table for the screen/context

### ROM Checksum Mismatch
The assembler automatically fixes the checksum. If your emulator still complains, ensure you used `ISSD_U` as the build target and that all assets are intact.

### Working on Linux/macOS
The `.bat` scripts are Windows-specific. Options:
- Use **Wine**: `wine cmd /c Assemble_ISSD.bat`
- Use **WSL** (Windows Subsystem for Linux)
- Manually invoke Asar with the same parameters shown in the `.bat` files

### Recommended Workflow

1. Extract assets once from a clean ROM
2. Make your edits to `.asm` files, `.bin` graphics, or `.tpl` palettes
3. Run `Assemble_ISSD.bat` to build
4. Test in an SNES emulator (bsnes, Snes9x, etc.)
5. Iterate as needed (press Enter in the build script to re-assemble)

---

## ROM Verification

| Version | MD5 Hash |
|---------|----------|
| USA | `345ddedcd63412b9373dabb67c11fc05` |

The ROM must be **headerless** (exactly 2MB / 2,097,152 bytes). If your ROM is 2,097,664 bytes, it has a 512-byte copier header that must be removed.

---

## ROM Configuration Reference

From `RomMap/ROM_Map_ISSD_U.asm`:

| Property | Value |
|----------|-------|
| Internal Name | `SUPERSTAR SOCCER 2` |
| Game Code | `AWJE` |
| Maker Code | `A4` (Konami) |
| ROM Layout | LoROM FastROM |
| ROM Size | 2MB |
| SRAM Size | 0KB |
| Region | North America |
| Release Date | November 1995 |

---

## Credits and References

- Disassembly by [Yoshifanatic1](https://github.com/Yoshifanatic1)
- Built on [SNES ROM Framework v1.3.1](https://github.com/Yoshifanatic1/SNES-ROM-Framework)
- Assembler: [Asar](https://github.com/RPGHacker/asar)

For more information on the framework, its functions, and other guidelines, consult "Framework Readme.txt" included with the download and/or in the SNES ROM framework repository.
