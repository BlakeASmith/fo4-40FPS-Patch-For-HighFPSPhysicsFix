import struct
import zipfile

import build_mod


def test_esp_header_is_plain_og_compatible():
    parsed = build_mod.parse_esp(build_mod.build_esp())
    assert parsed["hedr_version"] == struct.unpack("<f", struct.pack("<f", 0.95))[0]
    assert parsed["form_version"] == 131
    assert parsed["num_records"] == 0
    assert parsed["next_object"] == 0x800
    assert parsed["flags"] & 0x200 == 0
    assert parsed["flags"] & 0x1 == 0
    assert parsed["masters"] == "Fallout4.esm"
    assert parsed["order"] == ["HEDR", "CNAM", "SNAM", "MAST", "DATA"]


def test_presets_match_cap_and_havok_step():
    text = build_mod.custom_ini(40, 60)
    assert "ExteriorFPS=40.0" in text
    assert "InteriorFPS=60.0" in text
    assert "InGameFPS=40.0" in text
    assert "PipBoyFPS=40.0" in text
    assert "LockpickingFPS=40.0" in text
    assert "EnableVSync=false" in text
    assert "AllowTearing=true" in text
    assert "Fullscreen=false" in text
    assert "Borderless=true" in text
    assert "FramerateLimitMode=0" in text
    assert f"fMaxTime={build_mod.fmax_time(40)}" in build_mod.plugin_ini(40, 60)
    assert f"fMaxTime={build_mod.fmax_time(30)}" in build_mod.plugin_ini(50, 30)


def test_fmax_time_is_just_over_one_frame():
    assert build_mod.fmax_time(40) == "0.025500"
    value = float(build_mod.fmax_time(40))
    assert value > 1 / 40
    assert value < 1 / 39


def test_archive_lays_out_fomod_and_both_ini_names(tmp_path):
    staging = build_mod.write_tree(tmp_path / "staging")
    archive = build_mod.write_zip(staging, tmp_path / "out.zip")
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
    assert "fomod/ModuleConfig.xml" in names
    assert "SteamDeck_40FPS.esp" in names
    assert len(build_mod.PRESETS) ** 2 == 25
    for exterior in build_mod.PRESETS:
        for interior in build_mod.PRESETS:
            key = build_mod.preset_key(exterior, interior)
            for ini_name in build_mod.CUSTOM_INI_NAMES:
                assert f"presets/{key}/F4SE/Plugins/{ini_name}" in names
            assert f"presets/{key}/SteamDeck_40FPS.ini" in names
    with zipfile.ZipFile(archive) as zf:
        low = zf.read("presets/40-60/F4SE/Plugins/HighFPSPhysicsFix_custom.ini")
        high = zf.read("presets/40-60/F4SE/Plugins/HighFPSPhysicsFix_Custom.ini")
    assert low == high
    assert b"ExteriorFPS=40.0" in low
    assert b"InteriorFPS=60.0" in low
    config = (staging / "fomod" / "ModuleConfig.xml").read_text(encoding="utf-8")
    assert config.count('type name="Recommended"') == 2
    assert 'name="Exterior FPS"' in config
    assert 'name="Interior FPS"' in config
    assert 'flag name="exterior">40</flag>' in config
    assert "presets/40-60" in config
