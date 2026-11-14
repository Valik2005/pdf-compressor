"""Synthetic CArchive tests for exact native wheel origin auditing."""
import hashlib
from pathlib import Path
import zlib

import pytest

from tools.audit_native_binary_origin_28 import (
    MAGIC, COOKIE, TOC, audit, embedded_native_members,
)


def make_exe(path: Path, native: list[tuple[str, bytes]]) -> Path:
    payload = bytearray()
    toc = bytearray()
    for name, content in native:
        zipped = zlib.compress(content)
        name_bytes = name.encode("utf-8") + b"\0"
        toc.extend(TOC.pack(TOC.size + len(name_bytes), len(payload),
                            len(zipped), len(content), 1, b"b"))
        toc.extend(name_bytes)
        payload.extend(zipped)
    packet_len = len(payload) + len(toc) + COOKIE.size
    cookie = COOKIE.pack(MAGIC, packet_len, len(payload),
                         len(toc), 314, b"python314.dll".ljust(64, b"\0"))
    path.write_bytes(b"MZ" + b"\0" * 500 + payload + toc + cookie)
    return path


def wheel_match(payload: bytes, origin: str) -> dict:
    return {
        "origin": "wheel:" + origin, "version": "6.12.0",
        "relative_path": "PySide6/MSVCP140.dll",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "wheel_record_matches_installed_file": True,
    }


def test_bundle_native_member_exact_byte_hash_and_relative_source(tmp_path):
    dll = b"MZ" + bytes(range(256)) * 500
    pyd = b"MZ" + b"python-extension" * 100
    exe = make_exe(tmp_path / "test.exe", [
        ("PySide6\\MSVCP140.dll", dll),
        ("VCRUNTIME140.dll", b"MZ" + b"runtime"),
        ("PIL/_webp.pyd", pyd),
    ])
    members = dict(embedded_native_members(exe))
    assert members["PySide6/MSVCP140.dll"] == dll
    assert members["PIL/_webp.pyd"] == pyd
    assert all(not x.startswith("/") for x in members)
    candidates = {
        "msvcp140.dll": [wheel_match(dll, "PySide6_Essentials")],
        "_webp.pyd": [dict(wheel_match(pyd, "Pillow"),
                           relative_path="PIL/_webp.pyd")],
    }
    result = audit(exe, "a" * 40, candidates)
    assert result["native_file_count"] == 3
    assert result["matched_count"] == 2
    assert result["unmatched_wheel_entries"] == []
    assert result["redistribution_rights_verified"] is False
    assert result["entries"][1]["status"] == "unverified-build-origin"


def test_fail_closed_if_embedded_wheel_dll_differs_from_installed(tmp_path):
    exe = make_exe(tmp_path / "tamper.exe", [("PySide6/Qt6Widgets.dll", b"MZWRONG")])
    candidates = {"qt6widgets.dll": [wheel_match(b"MZCORRECT", "PySide6_Essentials")]}
    report = audit(exe, "f" * 40, candidates)
    assert report["unmatched_wheel_entries"] == ["PySide6/Qt6Widgets.dll"]


def test_fail_closed_if_installed_wheel_record_mismatches(tmp_path):
    data = b"MZ" + b"x" * 120
    exe = make_exe(tmp_path / "mismatch.exe", [("PIL/_avif.pyd", data)])
    entry = dict(wheel_match(data, "Pillow"),
                 wheel_record_matches_installed_file=False)
    report = audit(exe, "f" * 40, {"_avif.pyd": [entry]})
    assert report["installed_wheel_record_mismatches"] == ["PIL/_avif.pyd"]


@pytest.mark.parametrize("corruption", ["bad_cookie", "bad_toc", "truncated"])
def test_refuse_invalid_archive(corruption, tmp_path):
    exe = make_exe(tmp_path / "bad.exe", [("PySide6/Qt6Core.dll", b"MZ" + b"x" * 10)])
    raw = exe.read_bytes()
    if corruption == "bad_cookie":
        exe.write_bytes(raw[:-COOKIE.size] + b"\0" * COOKIE.size)
    elif corruption == "bad_toc":
        exe.write_bytes(raw[:510] + b"\0" * 40 + raw[550:])
    else:
        exe.write_bytes(raw[:-20])
    with pytest.raises((ValueError, Exception)):
        list(embedded_native_members(exe))
