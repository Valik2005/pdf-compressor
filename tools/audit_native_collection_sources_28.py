"""Record the actual PyInstaller Analysis source file for every bundled native entry.

Run INSIDE the spec after Qt pruning, before EXE creation. Keep sensitive
absolute builder paths out of artifacts. Source-file identity does not grant
permission to redistribute a binary or prove corresponding-source equivalence.
"""
from __future__ import annotations

from collections import Counter
import base64
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import sys


WHEELS = ("PyMuPDF", "PySide6", "PySide6_Essentials", "PySide6_Addons",
          "shiboken6", "Pillow")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def wheel_locations() -> dict[Path, dict]:
    """Use dist-info RECORD *paths*, not guessed DLL file name ownership."""
    known = {}
    for package in WHEELS:
        try:
            dist = metadata.distribution(package)
        except metadata.PackageNotFoundError:
            continue
        for item in dist.files or ():
            rel = str(item).replace("\\", "/")
            if not rel.lower().endswith((".dll", ".pyd")):
                continue
            path = Path(dist.locate_file(item)).resolve()
            record_sha = None
            if item.hash and item.hash.mode == "sha256":
                encoded = item.hash.value
                record_sha = base64.urlsafe_b64decode(
                    encoded + "=" * (-len(encoded) % 4)
                ).hex()
            known[path] = {"scope": "installed-wheel", "distribution": package,
                           "version": dist.version, "relative_path": rel,
                           "record_sha256": record_sha}
    return known


def scope_for(path: Path, known: dict) -> dict:
    if path in known:
        return dict(known[path])
    for base in (sys.base_prefix, sys.prefix):
        root = Path(base).resolve()
        if path.is_relative_to(root):
            return {"scope": "python-installation",
                    "relative_path": path.relative_to(root).as_posix()}
    windir = os.environ.get("SystemRoot") or os.environ.get("WINDIR")
    if windir and path.is_relative_to(Path(windir).resolve()):
        return {"scope": "windows-system",
                "relative_path": path.name}
    for key in ("ProgramFiles(x86)", "ProgramFiles"):
        root = os.environ.get(key)
        if root and path.is_relative_to(Path(root).resolve()):
            parts = path.relative_to(Path(root).resolve()).parts
            # Program Files paths are machine-wide and contain no account
            # names. Keep the *relative* path so a reviewer can distinguish
            # e.g. Git/OpenSSL/Visual Studio and the actual SDK Redist tree.
            # Never emit the absolute Program Files root.
            relative = "/".join(parts)
            if len(parts) >= 2 and parts[0].lower() == "windows kits":
                return {"scope": "windows-sdk", "relative_path": relative}
            return {"scope": "installed-program", "relative_path": relative}
    return {"scope": "unclassified-builder-path", "relative_path": path.name}


def capture(binaries, datas, out: Path, source_sha: str | None = None,
            known: dict | None = None) -> dict:
    wheel_index = wheel_locations() if known is None else known
    rows = {}
    for entry in list(binaries) + list(datas):
        if len(entry) < 2:
            raise ValueError("Invalid PyInstaller Analysis item")
        destination = str(entry[0]).replace("\\", "/")
        if not destination.lower().endswith((".dll", ".pyd")):
            continue
        if (not destination or destination.startswith("/")
                or ".." in destination.split("/") or destination in rows):
            raise ValueError(f"Duplicate or unsafe PyInstaller native member: {destination}")
        path = Path(entry[1])
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Invalid collected native source: {destination}")
        path = path.resolve()
        origin = scope_for(path, wheel_index)
        sha = digest(path)
        wheel_record = origin.pop("record_sha256", None)
        if origin["scope"] == "installed-wheel" and wheel_record is not None and wheel_record != sha:
            raise ValueError(f"Installed wheel RECORD disagrees for {destination}")
        rows[destination] = {
            "path": destination,
            "source_sha256": sha,
            "size_bytes": path.stat().st_size,
            "source_scope": origin["scope"],
            "source_relative_path": origin["relative_path"],
            "distribution": origin.get("distribution"),
            "distribution_version": origin.get("version"),
            "wheel_record_matched": wheel_record == sha if wheel_record else None,
        }
    if not rows:
        raise ValueError("No native files in collected PyInstaller Analysis")
    report = {
        "schema_version": 1,
        "source_git_commit": source_sha,
        "native_file_count": len(rows),
        "source_scope_counts": dict(sorted(Counter(
            row["source_scope"] for row in rows.values()
        ).items())),
        "entries": list(rows.values()),
        "redistribution_rights_verified": False,
        "note": "Actual build-stage source SHA/relative scope only. Not an OSS legal certification.",
    }
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Native collection source scopes:", report["source_scope_counts"])
    return report
