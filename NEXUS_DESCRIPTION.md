# Steam Deck FPS Preset

A small overlay for **High FPS Physics Fix**. Install it after that mod. It writes `HighFPSPhysicsFix_custom.ini` so the game caps itself at a steady frame rate. **40 FPS** is the default: set the Steam Deck display to 40 Hz and let this limiter pace the game. Fallout 4 stutters and speeds physics up when the Deck's own frame limiter is what holds it at 40.

The installer also offers 30, 45, 50, and 60. The physics fix reads the ini at launch, so changing the number means installing again (or editing the ini) and starting the game again.

VSync is turned off, borderless window and tearing are turned on, and Pip-Boy and lockpicking use the same cap. `fMaxTime` in `SteamDeck_40FPS.ini` matches that cap. Enable the esp.

## Compatibility

The archive has no DLL. It follows whichever High FPS Physics Fix you already installed.

* **Fallout 4 Original / Old-Gen:** `1.10.163`
* **Fallout 4 Next-Gen:** `1.10.980` – `1.10.984`
* **Fallout 4 Anniversary Edition:** `1.11.x`
* **Fallout London:** GOG one-click and downgraded Steam (F4SE and High FPS Physics Fix are already in the one-click install)

The plugin header is HEDR 0.95, form version 131, and a normal esp (not a light plugin), which is the header OG and Fallout London actually load.

## Requirements

* **F4SE** for your game version
* **High FPS Physics Fix** for your game version — [Nexus](https://www.nexusmods.com/fallout4/mods/44798)

On the Fallout 4 Nexus page, tag Original, Next-Gen, and Anniversary Edition. The same zip is the Fallout London upload.
