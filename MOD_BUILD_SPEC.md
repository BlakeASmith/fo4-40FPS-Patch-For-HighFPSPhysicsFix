# Steam Deck FPS preset (OG, NG, AE, Fallout London)

## 1. Objective

One MO2/Vortex archive, `dist/SteamDeck_40FPS_Preset-v1.0.0.zip`, installed after [High FPS Physics Fix](https://www.nexusmods.com/fallout4/mods/44798).

Works with the physics-fix build the user already has for:

- Fallout 4 OG `1.10.163`
- Next-Gen `1.10.980`–`1.10.984`
- Anniversary Edition `1.11.x`
- Fallout London (GOG one-click and downgraded Steam), which already ships F4SE and the physics fix

No DLL in this archive. `HighFPSPhysicsFix_custom.ini` is the overlay the Nexus DLL has loaded since 0.8.4. The same file is also written as `HighFPSPhysicsFix_Custom.ini` because a later fork opens that spelling. Proton on Deck is case-sensitive on disk; Wine's lookup is not. Both names are identical.

## 2. Plugin header

`SteamDeck_40FPS.esp` is an empty plugin so the game loads `SteamDeck_40FPS.ini`.

- HEDR version **0.95** (the Fallout 4 header). Not 1.0.
- Form version **131**
- Flags **0** (not ESM, not the `0x200` light-plugin flag)
- `numRecords = 0`, `nextObjectId = 0x800`
- Master: `Fallout4.esm`

HEDR 1.0 and the light flag belong to Next-Gen light plugins. OG `1.10.163` and Fallout London do not load those. An empty non-light esp costs one normal plugin slot. It does not add FormIDs.

## 3. Settings

FOMOD asks for exterior and interior separately (`SelectExactlyOne` each): 30, 40 (recommended), 45, 50, 60. The matching `presets/<exterior>-<interior>/` tree is installed from those flags.

| Key | Value |
| --- | --- |
| `ExteriorFPS` | exterior choice |
| `InteriorFPS` | interior choice |
| `InGameFPS`, `PipBoyFPS`, `LockpickingFPS` | the lower of the two |
| `EnableVSync` | `false` |
| `AllowTearing` | `true` |
| `Fullscreen` / `Borderless` | `false` / `true` |
| `FramerateLimitMode` | `0` |
| `OutOfFocusFPS` | `30` |
| `UntieSpeedFromFPS`, `DisableiFPSClamp` | `true` |
| plugin ini `fMaxTime` | `1/min(exterior, interior) + 0.0005` |
| plugin ini `iFPSClamp`, `iPresentInterval` | `0` |

Papyrus `DynamicUpdateBudget` is left alone. That option cuts script time when the frame rate is above 60. At 40 it would not change the budget.

The cap is read when the game starts. An MCM cannot change it: High FPS Physics Fix does not publish a setter. Re-run the installer or edit the custom ini, then restart.

## 4. Rebuild

`python3 build_mod.py` writes `dist/staging/` and the zip. `pytest` checks the header, the caps, and the archive layout.
