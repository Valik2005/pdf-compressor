"""Inspect PyInstaller one-file CArchive without running or extracting an EXE.

Format-specific; fail closed on unknown cookies and invalid TOC data.
A clean inventory is NOT a license-compliance certificate.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

MAGIC = b"MEI\x0c\x0b\x0a\x0b\x0e"
COOKIE = struct.Struct("!8sIIII64s")
TOC_ENTRY = struct.Struct("!IIIIBc")


def inspect_executable(exe: Path) -> dict:
    exe = exe.resolve()
    size = exe.stat().st_size
    if size < COOKIE.size:
        raise ValueError("File is too small for a PyInstaller one-file archive")
    h = hashlib.sha256()
    with exe.open("rb") as stream:
        for part in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(part)
        stream.seek(-COOKIE.size, 2)
        magic, package_size, toc_offset, toc_length, py_version, python_lib = COOKIE.unpack(stream.read(COOKIE.size))
        if magic != MAGIC:
            raise ValueError("No supported PyInstaller CArchive cookie at end of file")
        if (package_size < COOKIE.size + TOC_ENTRY.size or
                package_size > size or
                toc_offset < 0 or toc_length < TOC_ENTRY.size or
                toc_offset + toc_length > package_size - COOKIE.size):
            raise ValueError("Invalid PyInstaller archive bounds")
        archive_start = size - package_size
        stream.seek(archive_start + toc_offset)
        toc_data = stream.read(toc_length)
    entries = []
    pos = 0
    while pos < len(toc_data):
        if pos + TOC_ENTRY.size > len(toc_data):
            raise ValueError("Truncated TOC entry")
        entry_size, offset, packed, unpacked, compressed, kind = TOC_ENTRY.unpack_from(toc_data, pos)
        if entry_size <= TOC_ENTRY.size or pos + entry_size > len(toc_data):
            raise ValueError("Invalid TOC entry length")
        raw_name = toc_data[pos + TOC_ENTRY.size:pos + entry_size]
        if b"\x00" not in raw_name:
            raise ValueError("TOC entry missing name terminator")
        name = raw_name.split(b"\x00", 1)[0].decode("utf-8", "replace").replace("\\", "/")
        if offset + packed > toc_offset or compressed not in (0, 1):
            raise ValueError("Invalid TOC payload location")
        entries.append({"name": name, "packed_bytes": packed,
                        "unpacked_bytes": unpacked, "type": kind.decode("ascii", "replace")})
        pos += entry_size
    names = [e["name"] for e in entries]
    keyboard = [n for n in names if (
        n.lower().endswith("/qt6virtualkeyboard.dll") or
        n.lower().endswith("/qtvirtualkeyboardplugin.dll") or
        "/qtquick/virtualkeyboard/" in n.lower()
    )]
    notice_files = [n for n in names if (
        any(token in n.rsplit("/", 1)[-1].lower()
            for token in ("copying", "license", "licence", "notice", "copyright"))
    )]
    return {
        "schema_version": 1,
        "exe_name": exe.name,
        "exe_size_bytes": size,
        "sha256": h.hexdigest(),
        "python_archive_version": py_version,
        "python_library": python_lib.split(b"\x00")[0].decode("ascii", "replace"),
        "archive_items": len(entries),
        "archive_item_types": dict(Counter(e["type"] for e in entries)),
        "included_virtual_keyboard_files": keyboard,
        "embedded_notice_like_files": notice_files,
        "qt_dlls": [n for n in names if n.lower().startswith("pyside6/qt6") and n.lower().endswith(".dll")],
        "all_entries": entries,
        "warning": "Inventory only; does not establish licensing compliance or EXE runtime health.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--reject-virtual-keyboard", action="store_true")
    args = parser.parse_args()
    try:
        data = inspect_executable(args.exe)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Bundle audit failed: {exc}\n")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("EXE SHA256:", data["sha256"])
    print("Archive entries:", data["archive_items"])
    print("Qt Virtual Keyboard entries:", len(data["included_virtual_keyboard_files"]))
    if data["included_virtual_keyboard_files"]:
        print("  " + "\n  ".join(data["included_virtual_keyboard_files"]))
    print("Embedded notice-like files:", data["embedded_notice_like_files"])
    if args.reject_virtual_keyboard and data["included_virtual_keyboard_files"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
