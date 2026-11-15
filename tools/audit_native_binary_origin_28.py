"""Trace EXACT packaged DLL/PYD bytes to installed Windows Python wheels/runtime.

Produces package-relative provenance and hashes, no local builder file paths.
Byte correspondence is NOT confirmation of redistribution rights, LGPL/AGPL
license compliance or a binary reproducibility certificate.
"""
from __future__ import annotations

import argparse
import base64
from collections import defaultdict
import hashlib
from importlib import metadata
import json
from pathlib import Path
import struct
import sys
import zlib

MAGIC = b"MEI\x0c\x0b\x0a\x0b\x0e"
COOKIE = struct.Struct("!8sIIII64s")
TOC = struct.Struct("!IIIIBc")
PACKAGES = ("PyMuPDF", "PySide6", "PySide6_Essentials",
            "PySide6_Addons", "shiboken6", "Pillow")
PAYLOAD_PREFIXES = ("pyside6/", "shiboken6/", "pil/", "pymupdf/")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def embedded_native_members(exe: Path):
    """Yield validated uncompressed named native bytes from PyInstaller onefile."""
    exe = Path(exe).resolve(strict=True)
    size = exe.stat().st_size
    if size <= COOKIE.size:
        raise ValueError("File too small for PyInstaller onefile")
    with exe.open("rb") as f:
        f.seek(-COOKIE.size, 2)
        magic, packet, toc_start, toc_length, _version, _lib = COOKIE.unpack(f.read(COOKIE.size))
        if (magic != MAGIC or packet > size or packet <= COOKIE.size or
                toc_start <= 0 or toc_length <= TOC.size or
                toc_start + toc_length > packet - COOKIE.size):
            raise ValueError("Invalid PyInstaller CArchive bounds")
        start = size - packet
        f.seek(start + toc_start)
        toc = f.read(toc_length)
        pos = 0
        seen = set()
        while pos < len(toc):
            if pos + TOC.size > len(toc):
                raise ValueError("Truncated CArchive TOC")
            length, offset, packed_bytes, unpacked_bytes, compressed, _type = TOC.unpack_from(toc, pos)
            if length <= TOC.size or pos + length > len(toc):
                raise ValueError("Invalid CArchive TOC item size")
            name = toc[pos + TOC.size: pos + length].split(b"\0", 1)[0].decode("utf-8").replace("\\", "/")
            pos += length
            if not name.lower().endswith((".dll", ".pyd")):
                continue
            if (name in seen or not name or name.startswith("/") or
                    ".." in name.split("/") or offset + packed_bytes > toc_start or
                    unpacked_bytes > 150_000_000 or compressed not in (0, 1)):
                raise ValueError(f"Invalid native member {name}")
            seen.add(name)
            f.seek(start + offset)
            raw = f.read(packed_bytes)
            if len(raw) != packed_bytes:
                raise ValueError("Native archive member is truncated")
            if compressed:
                decompressor = zlib.decompressobj()
                raw = decompressor.decompress(raw, unpacked_bytes + 1) + decompressor.flush()
                if not decompressor.eof or decompressor.unused_data:
                    raise ValueError(f"Invalid compressed native member {name}")
            if len(raw) != unpacked_bytes:
                raise ValueError(f"Native member byte count differs: {name}")
            yield name, raw


def installed_sources(basenames: set[str]) -> dict[str, list[dict]]:
    """Index installed wheel files and validate PEP 376 RECORD SHA-256 fields."""
    results = defaultdict(list)
    for package in PACKAGES:
        try:
            dist = metadata.distribution(package)
        except metadata.PackageNotFoundError:
            continue
        for row in dist.files or ():
            name = str(row).replace("\\", "/")
            base = name.rsplit("/", 1)[-1].lower()
            if base not in basenames or not name.lower().endswith((".dll", ".pyd")):
                continue
            file = Path(dist.locate_file(row))
            if not file.is_file() or file.is_symlink():
                continue
            sha = sha256_bytes(file.read_bytes())
            record_verified = None
            if row.hash and row.hash.mode == "sha256":
                wanted = base64.urlsafe_b64decode(
                    row.hash.value + "=" * (-len(row.hash.value) % 4)
                ).hex()
                record_verified = wanted == sha
            results[base].append({
                "origin": "wheel:" + package,
                "version": dist.version,
                "relative_path": name,
                "sha256": sha,
                "wheel_record_matches_installed_file": record_verified,
            })

    # CPython itself supplies some root-level Python/runtime DLLs. Do not
    # enumerate C:\Windows or assume every matching system DLL is redistributable.
    dirs = [Path(sys.base_prefix), Path(sys.base_prefix) / "DLLs",
            Path(sys.prefix), Path(sys.prefix) / "DLLs", Path(sys.executable).parent]
    for name in basenames:
        for root in dirs:
            path = root / name
            if path.is_file() and not path.is_symlink():
                results[name].append({
                    "origin": "installed-cpython",
                    "version": ".".join(map(str, sys.version_info[:3])),
                    "relative_path": name,
                    "sha256": sha256_bytes(path.read_bytes()),
                    "wheel_record_matches_installed_file": None,
                })
    return results


def audit(exe: Path, commit: str, candidates: dict | None = None) -> dict:
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit.lower()):
        raise ValueError("Exactly 40 hex characters required for source commit")
    natives = [(name, sha256_bytes(blob), len(blob))
               for name, blob in embedded_native_members(exe)]
    basenames = {name.rsplit("/", 1)[-1].lower() for name, _, _ in natives}
    found = installed_sources(basenames) if candidates is None else candidates
    records = []
    unmatched_wheel = []
    mismatched_record = []
    for name, sha, size in natives:
        base = name.rsplit("/", 1)[-1].lower()
        matches = [candidate for candidate in found.get(base, []) if candidate["sha256"] == sha]
        from_wheel = name.lower().startswith(PAYLOAD_PREFIXES)
        if from_wheel and not matches:
            unmatched_wheel.append(name)
        if any(c.get("wheel_record_matches_installed_file") is False for c in matches):
            mismatched_record.append(name)
        records.append({
            "name": name, "sha256": sha, "size_bytes": size,
            "matched_installed_origins": matches,
            "status": "byte-identical" if matches else "unverified-build-origin",
        })
    h = hashlib.sha256()
    with Path(exe).open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return {
        "schema_version": 1,
        "source_git_commit": commit,
        "exe_sha256": h.hexdigest(),
        "native_file_count": len(natives),
        "matched_count": sum(bool(x["matched_installed_origins"]) for x in records),
        "unmatched_wheel_entries": unmatched_wheel,
        "installed_wheel_record_mismatches": mismatched_record,
        "entries": records,
        "redistribution_rights_verified": False,
        "warning": "Exact binary copy provenance only; MSVC/AGPL/LGPL rights not certified.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe", type=Path, required=True)
    p.add_argument("--source-sha", required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    result = audit(args.exe, args.source_sha)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Native library count:", result["native_file_count"])
    print("Byte-identical installed package/runtime origins:", result["matched_count"])
    print("Unmatched packaged wheel binaries:", result["unmatched_wheel_entries"])
    print("Installed wheel RECORD failures:", result["installed_wheel_record_mismatches"])
    if result["unmatched_wheel_entries"] or result["installed_wheel_record_mismatches"]:
        p.exit(2, "Native file differs from its installed wheel; investigate before release\n")


if __name__ == "__main__":
    main()
