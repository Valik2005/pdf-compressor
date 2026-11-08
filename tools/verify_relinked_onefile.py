"""Verify PyInstaller onefile CArchive embeds the exact replacement Qt DLL.

Inspects CArchive TOC and one selected binary; never executes the EXE or
trusts the package inventory alone. Designed for Windows relink integration.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import struct
import zlib

MAGIC = b"MEI\x0c\x0b\x0a\x0b\x0e"
COOKIE = struct.Struct("!8sIIII64s")
ENTRY = struct.Struct("!IIIIBc")


def embedded_file(exe: Path, internal_name: str) -> bytes:
    file_size = exe.stat().st_size
    with exe.open("rb") as f:
        f.seek(-COOKIE.size, 2)
        magic, package_size, toc_offset, toc_size, _, _ = COOKIE.unpack(f.read(COOKIE.size))
        if magic != MAGIC or not (COOKIE.size < package_size <= file_size):
            raise ValueError("Invalid PyInstaller CArchive")
        archive_start = file_size - package_size
        if toc_offset + toc_size > package_size - COOKIE.size:
            raise ValueError("TOC out of bounds")
        f.seek(archive_start + toc_offset)
        toc = f.read(toc_size)
        pos = 0
        while pos < len(toc):
            if pos + ENTRY.size > len(toc):
                raise ValueError("Truncated TOC")
            record_size, offset, packed, unpacked, compressed, kind = ENTRY.unpack_from(toc, pos)
            if record_size <= ENTRY.size or pos + record_size > len(toc):
                raise ValueError("Invalid TOC record")
            name = toc[pos + ENTRY.size:pos + record_size].split(b"\0", 1)[0].decode("utf-8")
            pos += record_size
            if name.replace(chr(92), "/").casefold() != internal_name.casefold():
                continue
            if offset + packed > toc_offset or unpacked > 256_000_000:
                raise ValueError("Invalid embedded DLL bounds")
            f.seek(archive_start + offset)
            data = f.read(packed)
            if len(data) != packed:
                raise ValueError("Truncated binary payload")
            data = zlib.decompress(data) if compressed else data
            if len(data) != unpacked:
                raise ValueError("Embedded binary length mismatch")
            return data
    raise ValueError(f"DLL not embedded in EXE: {internal_name}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe", type=Path, required=True)
    p.add_argument("--dll", type=Path, required=True)
    p.add_argument("--internal-name", default="PySide6/Qt6Widgets.dll")
    args = p.parse_args()
    actual = hashlib.sha256(embedded_file(args.exe, args.internal_name)).hexdigest()
    expected = hashlib.sha256(args.dll.read_bytes()).hexdigest()
    if actual != expected:
        p.exit(2, f"Embedded Qt DLL mismatch: expected {expected}, found {actual}\n")
    print("Modified Qt DLL SHA-256 matches onefile embedded payload:", actual)


if __name__ == "__main__":
    main()
