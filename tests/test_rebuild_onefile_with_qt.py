"""Unit tests for safe recipient supplied Qt overrides (no Windows build needed)."""
from pathlib import Path
import pytest

from tools.rebuild_onefile_with_qt import apply_overrides, sha256, RELEASE_SPECS


def test_matching_dll_replaced_and_reported(tmp_path: Path) -> None:
    qt = tmp_path / "QtInstalled"
    user = tmp_path / "ModifiedQt"
    (qt / "plugins" / "platforms").mkdir(parents=True)
    (user / "plugins" / "platforms").mkdir(parents=True)
    native = qt / "plugins" / "platforms" / "qwindows.dll"
    replacement = user / "plugins" / "platforms" / "qwindows.dll"
    native.write_bytes(b"original-dll")
    replacement.write_bytes(b"recompiled-dll")
    before = sha256(native)
    changes = apply_overrides(qt, user)
    assert native.read_bytes() == b"recompiled-dll"
    assert changes == [{
        "path": "plugins/platforms/qwindows.dll",
        "original_sha256": before,
        "replacement_sha256": sha256(replacement),
    }]


@pytest.mark.parametrize("name", ["unknown.dll", "suspicious.exe"])
def test_rejects_unknown_or_wrong_kind(tmp_path: Path, name: str) -> None:
    qt = tmp_path / "QtInstalled"
    user = tmp_path / "ModifiedQt"
    qt.mkdir()
    user.mkdir()
    (user / name).write_bytes(b"payload")
    with pytest.raises(ValueError):
        apply_overrides(qt, user)


def test_rejects_empty_override(tmp_path: Path) -> None:
    qt = tmp_path / "QtInstalled"
    user = tmp_path / "ModifiedQt"
    qt.mkdir()
    user.mkdir()
    (qt / "Qt6Core.dll").write_bytes(b"stock")
    (user / "Qt6Core.dll").touch()
    with pytest.raises(ValueError, match="Empty"):
        apply_overrides(qt, user)


def test_rejects_no_replacement_files(tmp_path: Path) -> None:
    qt = tmp_path / "QtInstalled"
    user = tmp_path / "ModifiedQt"
    qt.mkdir()
    user.mkdir()
    with pytest.raises(ValueError, match="contains no"):
        apply_overrides(qt, user)


def test_release_28_relink_mapping_is_explicit_and_legacy_27_unchanged() -> None:
    assert RELEASE_SPECS["2.7"] == ("release_windows_review.spec",
                                    "PDF_Compressor_2_7_license_review.exe")
    assert RELEASE_SPECS["2.8"] == ("release_windows_2_8.spec",
                                    "PDF_Compressor_2_8.exe")
