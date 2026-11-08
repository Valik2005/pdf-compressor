"""Read-only Windows one-folder layout audit; not a LGPL/AGPL certificate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

BUNDLE_NAME = "PDF_Compressor_2_7_onedir_review"
REQUIRED_DLLS = ("Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll")
REQUIRED_PLUGINS = ("qwindows.dll",)
VIRTUAL_KEYBOARD = ("qt6virtualkeyboard.dll", "qtvirtualkeyboardplugin.dll")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify(bundle_dir: Path, executable_name: str = BUNDLE_NAME) -> dict:
    bundle_dir = bundle_dir.resolve(strict=True)
    if not bundle_dir.is_dir():
        raise ValueError("Bundle path is not a directory")
    exe = bundle_dir / (executable_name + ".exe")
    if not exe.is_file():
        raise ValueError("Main executable missing")
    qt_dir = bundle_dir / "_internal" / "PySide6"
    if not qt_dir.is_dir():
        raise ValueError("External PySide6 directory missing")
    dlls = list(qt_dir.rglob("*.dll"))
    name_set = {p.name.casefold() for p in dlls}
    for expected in REQUIRED_DLLS:
        if expected.casefold() not in name_set:
            raise ValueError(f"Required external Qt DLL missing: {expected}")
    plugins_dir = qt_dir / "plugins"
    plugins = list(plugins_dir.rglob("*.dll")) if plugins_dir.is_dir() else []
    for expected in REQUIRED_PLUGINS:
        if not any(p.name.casefold() == expected.casefold() for p in plugins):
            raise ValueError(f"Qt Windows platform plugin missing: {expected}")
    forbidden = []
    for path in bundle_dir.rglob("*"):
        if not path.is_file():
            continue
        name = path.name.casefold()
        rel = path.relative_to(bundle_dir).as_posix().casefold()
        if name in VIRTUAL_KEYBOARD or "/qtquick/virtualkeyboard/" in "/" + rel:
            forbidden.append(rel)
    if forbidden:
        raise ValueError(f"Virtual Keyboard unexpectedly included: {forbidden}")
    # Verify the EXE doesn't itself embed Qt DLLs: it must be possible to
    # replace external components without first modifying/repacking the EXE.
    from audit_pyinstaller_bundle import inspect_executable
    entries = inspect_executable(exe)["all_entries"]
    embedded = [e["name"] for e in entries
                if e["name"].lower().endswith((".dll", ".pyd"))
                and "pyside6" in e["name"].lower()]
    if embedded:
        raise ValueError(f"PySide6 binaries unexpectedly inside EXE: {embedded[:5]}")
    # Hash every native executable/binding in the *actual* folder tree, not
    # just the top-level Qt DLLs. Reviewers can correlate this immutable
    # inventory with the exact third-party source and license evidence.
    native_extensions = {".dll", ".pyd", ".exe"}
    native_files = sorted(
        (p for p in bundle_dir.rglob("*")
         if p.is_file() and not p.is_symlink()
         and p.suffix.casefold() in native_extensions),
        key=lambda p: p.relative_to(bundle_dir).as_posix().casefold(),
    )
    native_manifest = [
        {
            "path": p.relative_to(bundle_dir).as_posix(),
            "size_bytes": p.stat().st_size,
            "sha256": sha256_file(p),
        }
        for p in native_files
    ]
    module_observations = {
        "qt_pdf_or_pdfium": sorted(
            p.relative_to(bundle_dir).as_posix()
            for p in dlls
            if p.name.casefold() in {"qt6pdf.dll", "qt6pdfwidgets.dll", "qpdf.dll"}
        ),
        "qt_qml": sorted(
            p.relative_to(bundle_dir).as_posix()
            for p in dlls if p.name.casefold().startswith("qt6qml")
        ),
        "qt_quick": sorted(
            p.relative_to(bundle_dir).as_posix()
            for p in dlls if p.name.casefold().startswith("qt6quick")
        ),
    }
    return {
        "schema_version": 2,
        "status": "EXPERIMENTAL EXTERNAL-DLL LAYOUT; LICENSE COMPLIANCE NOT CERTIFIED",
        "exe_name": exe.name,
        "exe_sha256": sha256_file(exe),
        "external_qt_dll_count": len(dlls),
        "external_qt_dlls": sorted(p.relative_to(bundle_dir).as_posix() for p in dlls),
        "qt_platform_plugins": sorted(p.relative_to(bundle_dir).as_posix() for p in plugins),
        "native_binary_count": len(native_manifest),
        "native_binary_manifest": native_manifest,
        "optional_qt_module_observations": module_observations,
        "virtual_keyboard_files": forbidden,
        "warning": "The modified-library replacement path, full license terms and source delivery remain unverified.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.bundle_dir)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"One-folder audit failed: {exc}\n")
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("External Qt DLLs:", result["external_qt_dll_count"])
    print("Virtual Keyboard entries:", len(result["virtual_keyboard_files"]))
    print("EXE SHA256:", result["exe_sha256"])
    print("NOT a license compliance certificate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
