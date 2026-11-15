# Steam Deck FPS preset for High FPS Physics Fix

Overlay for [High FPS Physics Fix](https://www.nexusmods.com/fallout4/mods/44798). It does not ship a DLL. After that mod (and F4SE), install this and pick a cap. **40 FPS** is the default, for a Steam Deck refresh set to 40 Hz.

The physics fix reads its ini at startup. Changing the cap means running the installer again, or editing the custom ini, then launching the game again. There is no MCM: the DLL has no runtime setter.

## What it sets

In `Data/F4SE/Plugins/HighFPSPhysicsFix_custom.ini` (and the same bytes as `HighFPSPhysicsFix_Custom.ini`, for the fork that capitalises the name):

- `ExteriorFPS` and `InteriorFPS` = the caps you picked. `InGameFPS`, `PipBoyFPS`, and `LockpickingFPS` = the lower of the two
- `EnableVSync=false`, `AllowTearing=true` so the limiter, not the Deck's frame limiter, paces the game
- `Fullscreen=false`, `Borderless=true`
- `FramerateLimitMode=0` (limit before present, steadier frametimes)
- `OutOfFocusFPS=30`

`Data/SteamDeck_40FPS.ini` (loaded because the empty esp is active) sets `iFPSClamp=0`, `iPresentInterval=0`, borderless window, and `fMaxTime` just above `1/fps`.

## Install

Requires F4SE and High FPS Physics Fix for the same game build (OG 1.10.163, NG 1.10.980–1.10.984, AE 1.11, or the copy bundled with Fallout London).

MO2 or Vortex: install `dist/SteamDeck_40FPS_Preset-v1.1.0.zip`. Pick an exterior cap and an interior cap (40 and 40 is the default). Enable `SteamDeck_40FPS.esp`. Load it after the physics fix.

Manual: copy `SteamDeck_40FPS.esp` plus one `presets/<exterior>-<interior>/` tree into the game `Data` folder.

Set the Deck refresh to the same number (40 Hz for the default). Leave the Steam fps limiter off or at least as high as the cap.

## Build

```
python3 build_mod.py
pytest
```
