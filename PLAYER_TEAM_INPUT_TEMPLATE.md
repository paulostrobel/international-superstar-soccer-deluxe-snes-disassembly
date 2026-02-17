# Player & Team Input Template

This template explains how to add or modify a **player** and a **team** in the International Superstar Soccer Deluxe disassembly.

---

## Table of Contents

1. [Overview](#overview)
2. [Team Template](#team-template)
3. [Player Name Template](#player-name-template)
4. [Player Stats Template](#player-stats-template)
5. [Kit Palette Pointers](#kit-palette-pointers)
6. [Closeup Appearance Pointers](#closeup-appearance-pointers)
7. [Fan Appearance Pointers](#fan-appearance-pointers)
8. [All-Star Team Roster Template](#all-star-team-roster-template)
9. [Step-by-Step Walkthrough](#step-by-step-walkthrough)

---

## Overview

Each team in the game is composed of several data pieces spread across the ROM:

| Data | Location | File |
|------|----------|------|
| Team ID constant | `Misc_Defines_ISSD.asm` | Defines file |
| Player names (20 per team) | `Routine_Macros_ISSD.asm` Bank $87 | Main code |
| Player stats (20 per team) | `Routine_Macros_ISSD.asm` Bank $8A | Main code |
| Home kit palette pointer | `Routine_Macros_ISSD.asm` line ~24265 | Main code |
| Away kit palette pointer | `Routine_Macros_ISSD.asm` line ~24273 | Main code |
| Goalkeeper palette pointer | `Routine_Macros_ISSD.asm` line ~24281 | Main code |
| Closeup appearance (7 tables) | `Routine_Macros_ISSD.asm` lines ~117751-118057 | Main code |
| Fan shirt/hair/skin/flag palettes | `Routine_Macros_ISSD.asm` lines ~182518-182668 | Main code |
| Team name graphic (Layer 3) | `Graphics/` folder | Binary asset |
| Team flag graphic (top+bottom) | `Graphics/Compressed/` folder | Binary asset |

---

## Team Template

### Team ID Define

In `Misc_Defines_ISSD.asm`, each team has a unique ID (used throughout the code):

```asm
; Format:
; !Define_ISSD_TeamIDs_<TeamName> = $<ID>
;
; IDs increment by $0002 (they are word-indexed).
; Existing teams use IDs $0000 through $0054.

; Example - existing teams:
!Define_ISSD_TeamIDs_Italy = $0000
!Define_ISSD_TeamIDs_Holland = $0002
!Define_ISSD_TeamIDs_England = $0004
; ... (full list of 43 teams in the file)
```

> **Note:** To modify an existing team, you do NOT need to change the Team ID. Simply edit the player names, stats, and palettes for that team's existing slot.

### Full Team ID Reference

| ID | Team | ID | Team |
|----|------|----|------|
| `$0000` | Italy | `$0026` | Wales |
| `$0002` | Holland | `$0028` | Scotland |
| `$0004` | England | `$002A` | North Ireland |
| `$0006` | Norway | `$002C` | Czech Republic |
| `$0008` | Spain | `$002E` | Poland |
| `$000A` | Ireland | `$0030` | Japan |
| `$000C` | Portugal | `$0032` | South Korea |
| `$000E` | Denmark | `$0034` | Turkey |
| `$0010` | Germany | `$0036` | Nigeria |
| `$0012` | France | `$0038` | Cameroon |
| `$0014` | Belgium | `$003A` | Morocco |
| `$0016` | Sweden | `$003C` | Brazil |
| `$0018` | Romania | `$003E` | Argentina |
| `$001A` | Bulgaria | `$0040` | Colombia |
| `$001C` | Russia | `$0042` | Mexico |
| `$001E` | Switzerland | `$0044` | USA |
| `$0020` | Greece | `$0046` | Uruguay |
| `$0022` | Croatia | `$0048` | All-Star |
| `$0024` | Austria | `$004A`-`$0052` | Star Teams |

---

## Player Name Template

### Location

Player names are in `Routine_Macros_ISSD.asm`, Bank $87. The pointer table at `DATA_878138` (line ~99487) indexes each team's name block.

### Format

- Each team has exactly **20 players**
- Each name is exactly **8 characters** (pad with spaces)
- Names use the **TallMenuText.txt** character encoding (loaded via `table` directive)
- Player order: #1 through #20 (GK first, then defenders, midfielders, forwards, subs)

### Available Characters

```
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
a b c d e f g h i j k l m n o p q r s t u v w x y z
0 1 2 3 4 5 6 7 8 9
(space)  .  -  '  /  !  :  ?  +
```

### Template (Blank Team)

```asm
; To replace a team's roster, find the team's DATA_ label and replace its names.
; Example: To edit Italy, find DATA_87818E and modify:

DATA_87818E:                    ; <-- Team label (Italy in this case)
    db "PLAYER01"               ; Player  1 (GK)
    db "PLAYER02"               ; Player  2
    db "PLAYER03"               ; Player  3
    db "PLAYER04"               ; Player  4
    db "PLAYER05"               ; Player  5
    db "PLAYER06"               ; Player  6
    db "PLAYER07"               ; Player  7
    db "PLAYER08"               ; Player  8
    db "PLAYER09"               ; Player  9
    db "PLAYER10"               ; Player 10
    db "PLAYER11"               ; Player 11
    db "PLAYER12"               ; Player 12
    db "PLAYER13"               ; Player 13
    db "PLAYER14"               ; Player 14
    db "PLAYER15"               ; Player 15
    db "PLAYER16"               ; Player 16
    db "PLAYER17"               ; Player 17
    db "PLAYER18"               ; Player 18
    db "PLAYER19"               ; Player 19
    db "PLAYER20"               ; Player 20
```

### Filled Example (Italy)

```asm
DATA_87818E:
    db "Pagani  "               ; Player  1 (GK)
    db "Premoli "               ; Player  2 (DF)
    db " Pabi   "               ; Player  3 (DF)
    db "Antonini"               ; Player  4 (DF)
    db "Graziano"               ; Player  5 (DF)
    db " Zappa  "               ; Player  6 (MF)
    db "DeSinone"               ; Player  7 (MF)
    db "Passaro "               ; Player  8 (MF)
    db "Galfano "               ; Player  9 (MF)
    db "Carboni "               ; Player 10 (MF)
    db "Coliuto "               ; Player 11 (FW)
    db "Mancini "               ; Player 12 (FW)
    db "Bucario "               ; Player 13
    db "Pabrizio"               ; Player 14
    db "Riggio  "               ; Player 15
    db " Zanga  "               ; Player 16
    db "Bittani "               ; Player 17
    db "Anticoli"               ; Player 18
    db "Cortese "               ; Player 19
    db "Fidrini "               ; Player 20
```

### All Team Name Labels

| Team | Label | ~Line |
|------|-------|-------|
| Italy | `DATA_87818E` | 99498 |
| Holland | `DATA_87822E` | 99520 |
| England | `DATA_8782CE` | 99542 |
| Norway | `DATA_87836E` | 99564 |
| Spain | `DATA_87840E` | 99586 |
| Ireland | `DATA_8784AE` | 99608 |
| Portugal | `DATA_87854E` | 99630 |
| Denmark | `DATA_8785EE` | 99652 |
| Germany | `DATA_87868E` | 99674 |
| France | `DATA_87872E` | 99696 |
| Belgium | `DATA_8787CE` | 99718 |
| Sweden | `DATA_87886E` | 99740 |
| Romania | `DATA_87890E` | 99762 |
| Bulgaria | `DATA_8789AE` | 99784 |
| Russia | `DATA_878A4E` | 99806 |
| Switzerland | `DATA_878AEE` | 99828 |
| Greece | `DATA_878B8E` | 99850 |
| Croatia | `DATA_878C2E` | 99872 |
| Austria | `DATA_878CCE` | 99894 |
| Wales | `DATA_878D6E` | 99916 |
| Scotland | `DATA_878E0E` | 99938 |
| North Ireland | `DATA_878EAE` | 99960 |
| Czech Republic | `DATA_878F4E` | 99982 |
| Poland | `DATA_878FEE` | 100004 |
| Japan | `DATA_87908E` | 100026 |
| South Korea | `DATA_87912E` | 100048 |
| Turkey | `DATA_8791CE` | 100070 |
| Nigeria | `DATA_87926E` | 100092 |
| Cameroon | `DATA_87930E` | 100114 |
| Morocco | `DATA_8793AE` | 100136 |
| Brazil | `DATA_87944E` | 100158 |
| Argentina | `DATA_8794EE` | 100180 |
| Colombia | `DATA_87958E` | 100202 |
| Mexico | `DATA_87962E` | 100224 |
| USA | `DATA_8796CE` | 100246 |
| Uruguay | `DATA_87976E` | 100268 |

---

## Player Stats Template

### Location

Player stats are in `Routine_Macros_ISSD.asm`, Bank $8A, starting at `DATA_8A8000` (line ~122472).

### Format

- Each team has **20 players x 7 bytes = 140 bytes ($8C)** of stat data
- Teams are stored consecutively in team ID order (Italy first, then Holland, etc.)
- Stats are packed as **nibbles** (4-bit values, range 0-9)
- 7 bytes = 14 nibbles per player

### Stat Loading Routine (for reference)

The copy routine at `CODE_83C6AE` (line ~44089):
1. Computes the team offset: `team_index * $8C` into `DATA_8A8000`
2. Loops 20 times (one per player)
3. Copies **7 bytes** from ROM to a **10-byte** RAM slot at `$7E3E00` (P1) or `$7E3EC8` (P2)
4. ROM source advances by 7, RAM destination advances by 10 (3 bytes padding per slot)

### 7-Byte Player Stat Layout

Each player's 7 ROM bytes contain packed nibble values for the player's attributes. The stats visible on the **Edit Player Skills** screen in-game are:

- **Head** (heading ability, 0-9)
- **Speed** (running speed, 0-9)
- **Kick** (shot/pass power, 0-9)
- **Dribble** (ball control, 0-9)
- **Stamina** (endurance, 0-9)
- **Defense** (tackling, 0-9)

Additional nibbles encode metadata such as player position type and appearance flags.

### How Stats Are Stored

The data at `DATA_8A8000` is stored as raw `dw` (word) values in the assembly. Each word is 2 bytes in little-endian. Teams are packed back-to-back with no separators.

```
Team 0 (Italy):   bytes $000-$08B  (140 bytes, 20 players x 7 bytes)
Team 1 (Holland):  bytes $08C-$117
Team 2 (England):  bytes $118-$1A3
... and so on for each team
```

### Reading Existing Stats

To find a specific team's stats in the `dw` data:

1. **Team byte offset** = `(TeamID / 2) * $8C`
2. **Player byte offset within team** = `PlayerIndex * 7` (PlayerIndex = 0-19)
3. Locate that byte position in the `DATA_8A8000` block

### Example - Modifying Stats

The stat data is densely packed as `dw` values. If you want to replace an entire team's stats, you need to replace exactly **140 bytes** (70 words) starting at the team's offset.

> **Tip:** The simplest approach to editing individual player stats is to use the in-game **Edit Player Skills** screen during gameplay, then capture the modified RAM values with a save state.

---

## Kit Palette Pointers

### Location

Three palette pointer tables in `Routine_Macros_ISSD.asm` (lines ~24265-24287):

| Table | Label | Purpose |
|-------|-------|---------|
| Home kit | `DATA_82827A` | Primary jersey colors |
| Away kit | `DATA_8282D0` | Alternate jersey colors |
| Goalkeeper | `DATA_828326` | Goalkeeper jersey colors |

### Format

Each table has **43 word entries** (one per team, in team ID order). Each entry is a `dw` pointer to palette data in bank $89.

```asm
; Template entry format:
; dw <pointer_to_palette_data>

; Example - Home kit table excerpt:
DATA_82827A:
    dw DATA_89XXXX    ; Italy home kit palette
    dw DATA_89XXXX    ; Holland home kit palette
    dw DATA_89XXXX    ; England home kit palette
    ; ... (43 entries total)
```

### Palette Files

Extracted palette files are in `Palettes/`:
```
PAL_Sprite_TeamPalettes_Italy.tpl
PAL_Sprite_TeamPalettes_Holland.tpl
PAL_Sprite_TeamPalettes_England.tpl
... (one per team)
```

Edit these `.tpl` files with a hex editor or SNES palette tool. Each color is 2 bytes in SNES **15-bit BGR** format (`0BBBBBGGGGGRRRRR`).

---

## Closeup Appearance Pointers

When a goal or own-goal triggers a player closeup, seven palette tables control the visual appearance. Each table is at a fixed location in `Routine_Macros_ISSD.asm`:

| Table | Label | Controls |
|-------|-------|----------|
| Hair color | `DATA_88FB00` (line ~117751) | Player hair |
| Skin color | `DATA_88FBA8` (line ~117795) | Player skin tone |
| Jersey color | `DATA_88FC50` (line ~117839) | Closeup jersey |
| Shorts/cuffs | `DATA_88FCF8` (line ~117883) | Shorts and jersey cuffs |
| Sock color | `DATA_88FDA0` (line ~117927) | Sock base color |
| Sock stripe | `DATA_88FE48` (line ~117971) | Sock stripe color |
| Jersey number | `DATA_88FEF0` (line ~118015) | Number color on jersey |

### Format

Each table has **43 team entries**, with **2 pointers per team** (primary and alternate player appearance):

```asm
; Template:
DATA_88FB00:                              ; Hair color palettes
    dw <PrimaryHairPal>,<AltHairPal>      ; Italy
    dw <PrimaryHairPal>,<AltHairPal>      ; Holland
    ; ... (43 teams)
```

---

## Fan Appearance Pointers

Stadium fan/audience appearance is controlled by four tables near the end of `Routine_Macros_ISSD.asm`:

| Table | Label | Entries/Team | Purpose |
|-------|-------|--------------|---------|
| Fan shirts | `DATA_A4F8EF` (line ~182518) | 4 pointers | Shirt color variations |
| Fan hair | `DATA_A4FA0F` (line ~182556) | 2 pointers | Hair color variations |
| Fan skin | `DATA_A4FA9F` (line ~182594) | 2 pointers | Skin tone variations |
| Fan flags | `DATA_A4FB2F` (line ~182632) | 2 pointers | Flag color variations |

```asm
; Template - Fan shirt colors:
DATA_A4F8EF:
    dw <Pal1>,<Pal2>,<Pal3>,<Pal4>       ; Italy
    dw <Pal1>,<Pal2>,<Pal3>,<Pal4>       ; Holland
    ; ... (43 teams)
```

---

## All-Star Team Roster Template

All-Star teams (IDs `$0048`-`$0052`) are composed by selecting players from existing national teams. Their roster data is at `DATA_A4F64F` (line ~182423).

### Format

Each All-Star team has **20 entries**, stored as pairs of words: `(TeamID, PlayerNameOffset)`.

```asm
; Each entry = dw TeamID, PlayerNameOffsetInBytes
; PlayerNameOffset = PlayerIndex * 8 (since names are 8 chars)
;
; Example - first few entries of the All-Star team:
DATA_A4F64F:
    dw $0014,$0000    ; Belgium player  1 (offset $00 = player index 0)
    dw $0000,$0008    ; Italy player    2 (offset $08 = player index 1)
    dw $0000,$0010    ; Italy player    3 (offset $10 = player index 2)
    dw $0010,$0010    ; Germany player  3
    ; ... (20 entries per All-Star team)
```

---

## Step-by-Step Walkthrough

### Editing an Existing Team's Player

**Example: Change Italy's first player name from "Pagani" to "Buffon"**

1. Open `Routine_Macros_ISSD.asm`
2. Search for `DATA_87818E` (Italy's name table)
3. Replace:
   ```asm
   db "Pagani  "
   ```
   with:
   ```asm
   db " Buffon "
   ```
4. Ensure the name is **exactly 8 characters** (pad with spaces)
5. Rebuild the ROM with `Assemble_ISSD.bat`

### Editing an Existing Team's Kit Colors

1. Edit the `.tpl` palette file in `Palettes/`:
   - e.g., `PAL_Sprite_TeamPalettes_Italy.tpl`
2. Skip the 4-byte TPL header
3. Modify the 2-byte SNES BGR color values
4. Rebuild the ROM

### Editing All 20 Player Names for a Team

1. Find the team's label in the [All Team Name Labels](#all-team-name-labels) table
2. Replace all 20 `db` strings with your new names
3. Each name must be **exactly 8 characters**
4. Rebuild the ROM

### Quick Reference - File Locations

| What to Edit | Where |
|-------------|-------|
| Player names | `Routine_Macros_ISSD.asm` search for team's `DATA_87xxxx` label |
| Player stats | `Routine_Macros_ISSD.asm` at `DATA_8A8000` (line ~122472) |
| Kit colors | `Palettes/PAL_Sprite_TeamPalettes_<Team>.tpl` |
| Team name graphic | `Graphics/GFX_Layer3_TeamNames_<Team>.bin` (edit with tile editor) |
| Team flag graphic | `Graphics/Compressed/GFX_Sprite_TeamFlags_<Group>_TopHalf.bin` + `BottomHalf.bin` |
| Team ID constant | `Misc_Defines_ISSD.asm` |
| Default team selection | RAM defines in `RAM_Map_ISSD.asm` (`!RAM_ISSD_MainMenu_DefaultP1Team`, `!RAM_ISSD_MainMenu_DefaultP2Team`) |
