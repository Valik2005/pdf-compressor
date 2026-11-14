"""Rebuild the one-file Windows EXE with recipient-supplied modified Qt libraries.

This is a relinking/recombination tool, not a legal compliance certificate.
Run on Windows from a full source checkout. It works in an isolated virtualenv.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

PINS = ("PyMuPDF==1.27.2.3", "PySide6==6.12.0", "Pillow==12.3.0", "pyinstaller==6.22.3")
EXE_NAME = "PDF_Compressor_2_7_license_review.exe"
RELEASE_SPECS = {"2.7": ("release_windows_review.spec", EXE_NAME),
                 "2.8": ("release_windows_2_8.spec", "PDF_Compressor_2_8.exe")}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def apply_overrides(package_dir: Path, override_dir: Path) -> list[dict]:
    """Replace matching installed DLL/PYD files, never creating new package paths."""
    package_dir = package_dir.resolve(strict=True)
    override_dir = override_dir.resolve(strict=True)
    if not package_dir.is_dir() or not override_dir.is_dir():
        raise ValueError("Qt package/override must be directories")
    changes: list[dict] = []
    for src in sorted(override_dir.rglob("*")):
        if src.is_symlink():
            raise ValueError(f"Symlink in override directory: {src}")
        if not src.is_file():
            continue
        if src.suffix.lower() not in (".dll", ".pyd"):
            raise ValueError(f"Only DLL/PYD overrides are supported: {src}")
        rel = src.relative_to(override_dir)
        if any(part in (".", "..") for part in rel.parts):
            raise ValueError(f"Unsafe override path: {rel}")
        target = (package_dir / rel).resolve(strict=False)
        if not target.is_relative_to(package_dir) or not target.is_file():
            raise ValueError(f"Override has no corresponding installed Qt file: {rel}")
        if src.stat().st_size == 0:
            raise ValueError(f"Empty override: {rel}")
        old_sha = sha256(target)
        new_sha = sha256(src)
        shutil.copyfile(src, target)
        changes.append({"path": rel.as_posix(), "original_sha256": old_sha, "replacement_sha256": new_sha})
    if not changes:
        raise ValueError("Qt override directory contains no DLL/PYD files")
    return changes


def run(args: list[str], cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def build(work_dir: Path, overrides: Path | None, *, release_version: str = "2.7") -> dict:
    if os.name != "nt":
        raise RuntimeError("Windows is required to build a Windows executable")
    source = Path(__file__).resolve().parents[1]
    if release_version not in RELEASE_SPECS:
        raise ValueError("Unsupported release version")
    spec_name, output_name = RELEASE_SPECS[release_version]
    if not (source / spec_name).is_file():
        raise FileNotFoundError("Required PyInstaller spec missing")
    work_dir = work_dir.resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    venv_dir = work_dir / "venv"
    # Recreate the environment every time: a previous Qt replacement must not
    # silently contaminate the next build (even when version pins match).
    if venv_dir.exists():
        shutil.rmtree(venv_dir)
    run([sys.executable, "-m", "venv", str(venv_dir)], source)
    py = venv_dir / "Scripts" / "python.exe"
    run([str(py), "-m", "pip", "install", *PINS], source)
    # Ask the environment itself for its installed PySide6 package location.
    qt_path = subprocess.check_output(
        [str(py), "-c", "import pathlib, PySide6; print(pathlib.Path(PySide6.__file__).resolve().parent)"],
        cwd=source, text=True, encoding="utf-8",
    ).strip()
    installed_qt = Path(qt_path)
    applied = apply_overrides(installed_qt, overrides) if overrides else []
    dist = work_dir / "dist"
    run(
        [str(py), "-m", "PyInstaller", "--noconfirm", "--clean",
         "--distpath", str(dist), "--workpath", str(work_dir / "pyinstaller"),
         spec_name],
        source,
    )
    exe = dist / output_name
    if not exe.is_file():
        raise FileNotFoundError(f"No rebuilt EXE: {exe}")
    run(
        [str(py), "tools/audit_pyinstaller_bundle.py", "--exe", str(exe),
         "--reject-virtual-keyboard", "--out", str(dist / "bundle-audit.json")],
        source,
    )
    run(
        [str(py), "tools/release_manifest.py", "--exe", str(exe),
         "--out", str(dist / "build-manifest.json")],
        source,
    )
    report = {"exe_path": str(exe), "exe_sha256": sha256(exe),
              "release_version": release_version, "spec_name": spec_name,
              "qt_package_path_in_isolated_venv": str(installed_qt),
              "qt_overrides": applied, "build_pins": list(PINS),
              "note": "Rebuild mechanism, not legal-compliance certification"}
    (dist / "qt-relink-build-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Built:", exe)
    print("SHA-256:", report["exe_sha256"])
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qt-overrides", type=Path,
                        help="Folder mirroring PySide6 relative paths, containing replacement DLL/PYD files")
    parser.add_argument("--work-dir", type=Path, default=Path("qt-relink-work"),
                        help="Separate local build directory, outside of source distribution")
    parser.add_argument("--release-version", choices=tuple(RELEASE_SPECS),
                        default="2.7", help="Release source/spec for recipient relinking")
    args = parser.parse_args()
    if args.qt_overrides and not args.qt_overrides.is_dir():
        parser.error("--qt-overrides must be an existing directory")
    build(args.work_dir, args.qt_overrides, release_version=args.release_version)


if __name__ == "__main__":
    main()
