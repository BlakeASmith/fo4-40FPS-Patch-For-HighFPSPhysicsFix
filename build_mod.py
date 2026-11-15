"""Build the Steam Deck FPS preset for High FPS Physics Fix.

The physics plugin reads HighFPSPhysicsFix.ini at startup, then overlays
HighFPSPhysicsFix_custom.ini key by key (Nexus 0.8.4 spelling). A later
fork looks for HighFPSPhysicsFix_Custom.ini. Both copies are written with
the same bytes so the overlay is found on a case-sensitive Steam Deck
prefix and on Windows.

Fallout 4 also loads Data/<plugin>.ini for every active plugin. That file
carries fMaxTime so the Havok step matches the cap even before F4SE loads.
"""

from __future__ import annotations

import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAGING = ROOT / "dist" / "staging"
ZIP_NAME = "SteamDeck_40FPS_Preset-v1.1.0.zip"

PLUGIN = "SteamDeck_40FPS.esp"
AUTHOR = "SteamDeck 40FPS Preset"
DESCRIPTION = "FPS cap preset for High FPS Physics Fix. Cap is chosen at install and applied on launch."

# One installer choice. 40 is the Deck VRR default.
PRESETS: dict[int, str] = {
    30: "30 FPS",
    40: "40 FPS (Steam Deck)",
    45: "45 FPS",
    50: "50 FPS",
    60: "60 FPS",
}
DEFAULT_FPS = 40

# Official Nexus changelog name, then the fork's capitalisation.
CUSTOM_INI_NAMES = (
    "HighFPSPhysicsFix_custom.ini",
    "HighFPSPhysicsFix_Custom.ini",
)


def fmax_time(fps: int) -> str:
    """Havok max frame time. A hair above 1/fps so a locked frame is not slowed."""
    return f"{(1.0 / fps) + 0.0005:.6f}"


def preset_key(exterior: int, interior: int) -> str:
    return f"{exterior}-{interior}"


def custom_ini(exterior: int, interior: int) -> str:
    # Menus, Pip-Boy, and lockpicking follow the lower cap so they never
    # jump past the slower of the two areas.
    shared = min(exterior, interior)
    return f"""\
; Steam Deck FPS preset for High FPS Physics Fix
; Overrides only the keys below. Loaded at game start. Restart to apply edits.
; https://www.nexusmods.com/fallout4/mods/44798
;
; VSync is off so this limiter owns the cap. Fallout 4 fights the Steam Deck
; framerate limiter; a cap inside the physics fix does not.
; Borderless + tearing is what Deck VRR / Gamescope can pace.
; Exterior and interior are independent. 0 on either key would fall back to InGameFPS.

[Main]
UntieSpeedFromFPS=true
DisableiFPSClamp=true
EnableVSync=false
AllowTearing=true
DisableVSyncWhileLoading=true

[Limiter]
InGameFPS={shared}.0
ExteriorFPS={exterior}.0
InteriorFPS={interior}.0
PipBoyFPS={shared}.0
LockpickingFPS={shared}.0
OutOfFocusFPS=30.0
FramerateLimitMode=0

[Display]
Fullscreen=false
Borderless=true
"""


def plugin_ini(exterior: int, interior: int) -> str:
    fps = min(exterior, interior)
    return f"""\
; Loaded by Fallout 4 while {PLUGIN} is active.
; fMaxTime is the longest frame Havok will simulate before slowing the game.
; Matched to the lower of the exterior ({exterior}) and interior ({interior}) caps.
; High FPS Physics Fix unties speed as well.

[General]
iFPSClamp=0

[HAVOK]
fMaxTime={fmax_time(fps)}

[Display]
iPresentInterval=0
bFull Screen=0
bBorderless=1
"""


def _zstring(text: str) -> bytes:
    return text.encode("latin-1") + b"\x00"


def _subrecord(tag: str, data: bytes) -> bytes:
    if len(tag) != 4:
        raise ValueError(tag)
    return tag.encode("ascii") + struct.pack("<H", len(data)) + data


def build_esp() -> bytes:
    """Empty Fallout 4 plugin. HEDR 0.95, form version 131, not a light plugin.

    0.95 is the header every OG, NG, AE, and Fallout London plugin uses.
    HEDR 1.0 and the 0x200 light flag are NG-only and are rejected or ignored
    on 1.10.163 and Fallout London. Zero records: the file exists so the
    game loads the matching plugin ini. It still uses one normal plugin slot.
    """
    body = b"".join(
        (
            _subrecord("HEDR", struct.pack("<fII", 0.95, 0, 0x800)),
            _subrecord("CNAM", _zstring(AUTHOR)),
            _subrecord("SNAM", _zstring(DESCRIPTION)),
            _subrecord("MAST", _zstring("Fallout4.esm")),
            _subrecord("DATA", struct.pack("<Q", 0)),
        )
    )
    header = b"".join(
        (
            b"TES4",
            struct.pack("<I", len(body)),
            struct.pack("<I", 0),  # flags: not ESM, not ESL
            struct.pack("<I", 0),  # form id
            struct.pack("<I", 0),  # timestamp
            struct.pack("<HH", 0, 131),
        )
    )
    return header + body


def parse_esp(data: bytes) -> dict:
    if data[:4] != b"TES4":
        raise ValueError("missing TES4")
    data_size, flags, form_id, _ts = struct.unpack_from("<IIII", data, 4)
    _vc, form_version = struct.unpack_from("<HH", data, 20)
    pos = 24
    end = 24 + data_size
    subs: dict[str, bytes] = {}
    order: list[str] = []
    while pos < end:
        tag = data[pos : pos + 4].decode("ascii")
        size = struct.unpack_from("<H", data, pos + 4)[0]
        blob = data[pos + 6 : pos + 6 + size]
        subs[tag] = blob
        order.append(tag)
        pos += 6 + size
    version, num_records, next_object = struct.unpack("<fII", subs["HEDR"])
    return {
        "flags": flags,
        "form_id": form_id,
        "form_version": form_version,
        "hedr_version": version,
        "num_records": num_records,
        "next_object": next_object,
        "author": subs["CNAM"].split(b"\x00", 1)[0].decode("latin-1"),
        "masters": subs["MAST"].split(b"\x00", 1)[0].decode("latin-1"),
        "order": order,
        "size": len(data),
    }


def _choice_plugins(flag: str) -> str:
    blocks = []
    for fps, label in PRESETS.items():
        kind = "Recommended" if fps == DEFAULT_FPS else "Optional"
        blocks.append(
            f"""\
          <plugin name="{label}">
            <description>Cap {flag} cells at {fps} FPS. Applied on the next launch.</description>
            <conditionFlags>
              <flag name="{flag}">{fps}</flag>
            </conditionFlags>
            <typeDescriptor>
              <type name="{kind}" />
            </typeDescriptor>
          </plugin>"""
        )
    return "\n".join(blocks)


def _conditional_patterns() -> str:
    patterns = []
    for exterior in PRESETS:
        for interior in PRESETS:
            key = preset_key(exterior, interior)
            patterns.append(
                f"""\
    <pattern>
      <dependencies operator="And">
        <flagDependency flag="exterior" value="{exterior}" />
        <flagDependency flag="interior" value="{interior}" />
      </dependencies>
      <files>
        <folder source="presets/{key}" destination="" priority="0" />
      </files>
    </pattern>"""
            )
    return "\n".join(patterns)


def module_config() -> str:
    return f"""\
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">
  <moduleName>Steam Deck FPS Preset</moduleName>
  <requiredInstallFiles>
    <file source="{PLUGIN}" destination="{PLUGIN}" priority="0" />
  </requiredInstallFiles>
  <installSteps order="Explicit">
    <installStep name="Exterior">
      <optionalFileGroups order="Explicit">
        <group name="Exterior FPS" type="SelectExactlyOne">
          <plugins order="Explicit">
{_choice_plugins("exterior")}
          </plugins>
        </group>
      </optionalFileGroups>
    </installStep>
    <installStep name="Interior">
      <optionalFileGroups order="Explicit">
        <group name="Interior FPS" type="SelectExactlyOne">
          <plugins order="Explicit">
{_choice_plugins("interior")}
          </plugins>
        </group>
      </optionalFileGroups>
    </installStep>
  </installSteps>
  <conditionalFileInstalls>
    <patterns>
{_conditional_patterns()}
    </patterns>
  </conditionalFileInstalls>
</config>
"""


def info_xml() -> str:
    return """\
<fomod>
  <Name>Steam Deck FPS Preset</Name>
  <Author>SteamDeck 40FPS Preset</Author>
  <Version>1.1.0</Version>
  <Description>Separate exterior and interior FPS caps for High FPS Physics Fix. 40/40 is the Deck default. Restart to apply.</Description>
  <Website>https://www.nexusmods.com/fallout4/mods/44798</Website>
</fomod>
"""


def write_tree(staging: Path = STAGING) -> Path:
    if staging.exists():
        for path in sorted(staging.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            else:
                path.rmdir()
    staging.mkdir(parents=True, exist_ok=True)
    (staging / PLUGIN).write_bytes(build_esp())
    fomod = staging / "fomod"
    fomod.mkdir()
    (fomod / "ModuleConfig.xml").write_text(module_config(), encoding="utf-8")
    (fomod / "info.xml").write_text(info_xml(), encoding="utf-8")
    for exterior in PRESETS:
        for interior in PRESETS:
            folder = staging / "presets" / preset_key(exterior, interior)
            plugins = folder / "F4SE" / "Plugins"
            plugins.mkdir(parents=True)
            ini = custom_ini(exterior, interior)
            for name in CUSTOM_INI_NAMES:
                (plugins / name).write_text(ini, encoding="utf-8", newline="\r\n")
            (folder / "SteamDeck_40FPS.ini").write_text(
                plugin_ini(exterior, interior), encoding="utf-8", newline="\r\n"
            )
    return staging


def write_zip(staging: Path = STAGING, dest: Path | None = None) -> Path:
    dest = dest or (ROOT / "dist" / ZIP_NAME)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(staging).as_posix())
    return dest


def main() -> None:
    staging = write_tree()
    archive = write_zip(staging)
    print(archive)


if __name__ == "__main__":
    main()
