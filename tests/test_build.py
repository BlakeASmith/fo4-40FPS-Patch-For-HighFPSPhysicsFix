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
    for fps in build_mod.PRESETS:
        text = build_mod.custom_ini(fps)
        assert f"InGameFPS={fps}.0" in text
        assert f"PipBoyFPS={fps}.0" in text
        assert f"LockpickingFPS={fps}.0" in text
        assert "EnableVSync=false" in text
        assert "AllowTearing=true" in text
        assert "Fullscreen=false" in text
        assert "Borderless=true" in text
        assert "FramerateLimitMode=0" in text
        assert f"fMaxTime={build_mod.fmax_time(fps)}" in build_mod.plugin_ini(fps)


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
    for fps in build_mod.PRESETS:
        for ini_name in build_mod.CUSTOM_INI_NAMES:
            assert f"presets/{fps}/F4SE/Plugins/{ini_name}" in names
        assert f"presets/{fps}/SteamDeck_40FPS.ini" in names
    with zipfile.ZipFile(archive) as zf:
        low = zf.read("presets/40/F4SE/Plugins/HighFPSPhysicsFix_custom.ini")
        high = zf.read("presets/40/F4SE/Plugins/HighFPSPhysicsFix_Custom.ini")
    assert low == high
    assert b"InGameFPS=40.0" in low
    config = (staging / "fomod" / "ModuleConfig.xml").read_text(encoding="utf-8")
    assert 'type name="Recommended"' in config
    assert config.count('type name="Recommended"') == 1
    assert "presets/40" in config
