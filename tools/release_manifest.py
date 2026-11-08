"""Create a private-data-minimized build manifest for a Windows EXE.

Records the local builder's dependency versions, not a signed attestation of
the actual contents of the PyInstaller archive.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform
import subprocess

PACKAGES = (
    "PyMuPDF", "PySide6", "PySide6_Addons", "PySide6_Essentials",
    "shiboken6", "Pillow", "pyinstaller",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(source_dir: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args], cwd=source_dir, check=False,
            capture_output=True, text=True, encoding="utf-8",
        )
    except (OSError, ValueError):
        return None
    if result.returncode:
        return None
    return result.stdout.strip()


def make_manifest(exe: Path, source_dir: Path) -> dict:
    exe = exe.resolve()
    if not exe.is_file():
        raise FileNotFoundError(f"EXE not found: {exe}")
    commit = git_value(source_dir, "rev-parse", "HEAD")
    dirty = git_value(source_dir, "status", "--porcelain")
    packages = {}
    for name in PACKAGES:
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            packages[name] = None

    return {
        "schema_version": 1,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "exe_name": exe.name,
        "exe_size_bytes": exe.stat().st_size,
        "exe_sha256": sha256_file(exe),
        "source_git_commit": commit,
        "source_has_local_changes": bool(dirty) if dirty is not None else None,
        "builder_python": platform.python_version(),
        "builder_os": platform.system(),
        "builder_architecture": platform.machine(),
        "installed_builder_package_versions": packages,
        "note": "Build environment inventory only; verify actual bundled components and licenses separately.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    source_dir = Path(__file__).resolve().parents[1]
    result = make_manifest(args.exe, source_dir)
    destination = args.out or args.exe.with_suffix(".build-manifest.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"SHA-256: {result['exe_sha256']}")
    print(f"Manifest: {destination}")


if __name__ == "__main__":
    main()
