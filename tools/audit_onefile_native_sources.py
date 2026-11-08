"""Map every native library in the *actual* onefile archive to provenance scope.

Fail if a new binary is unclassified. A source archive matching a package
version DOES NOT prove byte-for-byte binary/source correspondence or licenses.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

COVERED_SOURCES = {
    "QtBase": "qtbase-6.12.0-required",
    "QtSvg": "qtsvg-6.12.0",
    "QtImageFormats": "qtimageformats-6.12.0",
    "PySide6/Shiboken": "qtforpython-6.12.0",
    "PyMuPDF": "pymupdf-1.27.2.3",
    "MuPDF": "mupdf-1.27.2-native",
}
MANUAL_COMPONENTS = {
    "OpenSSL": "OpenSSL source/version and applicable Apache-style notices",
    "Pillow codecs": "Pillow, bundled codecs (AVIF/WebP/JPEG/etc) and their notices",
    "Mesa OpenGL software rasterizer": "Mesa/LLVM software-renderer notices and source origin",
    "libffi": "libffi license/version",
    "Python runtime": "Python PSF license, C extension and interpreter provenance",
    "Microsoft runtime": "Microsoft redistributable runtime distribution terms",
}


def component(path: str) -> str | None:
    p = path.replace(chr(92), "/").lower()
    base = p.rsplit("/", 1)[-1]
    if base.startswith(("vcruntime", "msvcp", "api-ms-win-", "ucrtbase")):
        return "Microsoft runtime"
    if base.startswith(("libcrypto-", "libssl-")):
        return "OpenSSL"
    if p.startswith("pyside6/"):
        if base == "opengl32sw.dll":
            return "Mesa OpenGL software rasterizer"
        if base in ("qt6svg.dll", "qsvg.dll", "qsvgicon.dll"):
            return "QtSvg"
        if p.startswith("pyside6/plugins/imageformats/"):
            if base in ("qicns.dll", "qtga.dll", "qtiff.dll", "qwbmp.dll", "qwebp.dll"):
                return "QtImageFormats"
            if base in ("qgif.dll", "qico.dll", "qjpeg.dll"):
                return "QtBase"
            return None
        if base.startswith("qt6") and base.endswith(".dll"):
            if base in ("qt6core.dll", "qt6gui.dll", "qt6widgets.dll", "qt6network.dll",
                        "qt6opengl.dll"):
                return "QtBase"
            return None
        if base in ("pyside6.abi3.dll", "qtcore.pyd", "qtgui.pyd",
                    "qtwidgets.pyd", "qtnetwork.pyd"):
            return "PySide6/Shiboken"
        if p.startswith("pyside6/plugins/"):
            return "QtBase"
        return None
    if p.startswith("shiboken6/"):
        if base in ("shiboken6.abi3.dll", "shiboken.pyd"):
            return "PySide6/Shiboken"
        return None
    if p.startswith("pymupdf/") and base.endswith((".pyd", ".dll")):
        return "MuPDF" if base in ("_mupdf.pyd", "mupdfcpp64.dll") else "PyMuPDF"
    if p.startswith("pil/") and base.endswith(".pyd"):
        return "Pillow codecs"
    if base == "libffi-8.dll":
        return "libffi"
    if base.startswith(("python3", "libpython")) and base.endswith(".dll"):
        return "Python runtime"
    if base.endswith(".pyd") and "/" not in p:
        return "Python runtime"
    return None


def audit(bundle: dict, catalog: dict) -> dict:
    if bundle.get("schema_version") != 1 or not isinstance(bundle.get("all_entries"), list):
        raise ValueError("Expected a PyInstaller onefile audit with all entries")
    archives = {item["id"]: item for item in catalog["entries"] if item.get("required")}
    missing = sorted(set(COVERED_SOURCES.values()) - set(archives))
    rows = []
    for item in bundle["all_entries"]:
        path = item["name"]
        if not path.lower().endswith((".dll", ".pyd")):
            continue
        group = component(path)
        rows.append({"path": path, "component": group, "source_catalog_id":
                     COVERED_SOURCES.get(group)})
    unmapped = [row["path"] for row in rows if row["component"] is None]
    counts = dict(Counter(row["component"] or "UNMAPPED" for row in rows))
    return {
        "schema_version": 1,
        "exe_sha256": bundle["sha256"],
        "exe_size_bytes": bundle["exe_size_bytes"],
        "native_file_count": len(rows),
        "component_counts": counts,
        "missing_required_source_entries": missing,
        "unmapped_native_files": unmapped,
        "native_component_mapping": rows,
        "source_archive_hashes_match_exact_native_binary_provenance": False,
        "open_manual_review_components": [
            {"component": k, "review": value}
            for k, value in sorted(MANUAL_COMPONENTS.items())
            if k in counts
        ],
        "status": "NATIVE FILES CLASSIFIED; BINARY/SOURCE EQUIVALENCE AND TRANSITIVE NOTICES NOT CERTIFIED",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audit", type=Path, required=True)
    p.add_argument("--catalog", type=Path, default=Path("docs/source-archives-2_7.json"))
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    bundle = json.loads(args.audit.read_text(encoding="utf-8"))
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    report = audit(bundle, catalog)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Native mapped:", report["native_file_count"])
    print("Components:", report["component_counts"])
    print("Unmapped:", report["unmapped_native_files"])
    print("Missing source catalog entries:", report["missing_required_source_entries"])
    if report["unmapped_native_files"] or report["missing_required_source_entries"]:
        p.exit(2, "Native component provenance classification incomplete\n")


if __name__ == "__main__":
    main()
