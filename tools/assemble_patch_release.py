"""Build the public three-file Windows release set from independently audited CI assets.

Never downloads, publishes, or deletes anything. Fail closed if source archives,
license bundles, native audits, or the Windows onefile EXE do not match their
committed expected SHA-256 and source commit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

SOURCES = 6
RELEASE_DOCS = ("LGPL_RELINKING_2_7.md", "THIRD_PARTY_NOTICES_2_7.md",
                "libffi-LICENSE.txt", "THIRD_PARTY_NOTICES_2_7.zip")
WINDOWS_DOCS = ("license-evidence.zip",)
SOURCE_REPORTS = ("source-download-report.json", "source-archive-audit.json")
WINDOWS_REPORTS = ("build-manifest.json", "bundle-audit.json", "native-source-mapping.json")
BUNDLE_NAME = "Third_Party_Sources_and_Licenses.zip"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as src:
        for piece in iter(lambda: src.read(1024 * 1024), b""):
            h.update(piece)
    return h.hexdigest()


def require_file(folder: Path, name: str) -> Path:
    path = folder / name
    if not path.is_file() or path.is_symlink() or path.stat().st_size == 0:
        raise ValueError(f"Required review asset missing, empty or symlinked: {path}")
    return path


def check_zip(path: Path, minimum_entries: int = 2) -> None:
    with zipfile.ZipFile(path) as archive:
        if len(archive.namelist()) < minimum_entries or archive.testzip() is not None:
            raise ValueError(f"Corrupted or incomplete ZIP: {path}")


def assemble(sources_dir: Path, windows_dir: Path, catalog_path: Path,
             destination: Path, exe_name: str, source_sha: str) -> dict:
    if exe_name != "PDF_Compressor_2_7_1.exe":
        raise ValueError("Refusing unexpected binary name for 2.7.1")
    if len(source_sha) != 40 or any(ch not in "0123456789abcdef" for ch in source_sha.lower()):
        raise ValueError("A full source git commit SHA is required")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    entries = [item for item in catalog["entries"] if item["required"]]
    if len(entries) != SOURCES or any(not item.get("expected_sha256") for item in entries):
        raise ValueError("Six verified source archives with pinned SHA-256 are mandatory")

    # Audit the exact final Windows build, rather than relying on prior runs.
    exe = require_file(windows_dir, exe_name)
    manifest = json.loads(require_file(windows_dir, "build-manifest.json").read_text(encoding="utf-8"))
    native = json.loads(require_file(windows_dir, "native-source-mapping.json").read_text(encoding="utf-8"))
    bundle_audit = json.loads(require_file(windows_dir, "bundle-audit.json").read_text(encoding="utf-8"))
    source_audit = json.loads(require_file(sources_dir, "source-archive-audit.json").read_text(encoding="utf-8"))
    source_downloads = json.loads(require_file(sources_dir, "source-download-report.json").read_text(encoding="utf-8"))

    exe_sha = digest(exe)
    if not (manifest.get("exe_sha256") == exe_sha == native.get("exe_sha256") == bundle_audit.get("sha256")):
        raise ValueError("Final EXE and Windows native/manifest audits disagree")
    if manifest.get("exe_name") != exe_name or manifest.get("exe_size_bytes") != exe.stat().st_size:
        raise ValueError("Final EXE name or size differs from manifest")
    if manifest.get("source_git_commit") != source_sha or manifest.get("source_has_local_changes") is not False:
        raise ValueError("Release binary does not come from exact clean source commit")
    if native.get("unmapped_native_files") or native.get("missing_required_source_entries"):
        raise ValueError("Missing binary component-to-source map")
    if native.get("native_file_count", 0) < 100:
        raise ValueError("Unexpectedly small native library inventory")
    if bundle_audit.get("included_virtual_keyboard_files"):
        raise ValueError("Qt Virtual Keyboard accidentally bundled")

    if not source_audit.get("all_required_with_published_hashes"):
        raise ValueError("Required corresponding-source archive hashes not verified")
    if not source_downloads.get("all_required_archives_verified"):
        raise ValueError("Not every source archive passed upstream checksum validation")

    asset_entries: dict[str, Path] = {}
    for item in entries:
        name = item["filename"]
        if Path(name).name != name:
            raise ValueError(f"Unsafe source archive filename: {name}")
        path = require_file(sources_dir, name)
        if digest(path).lower() != item["expected_sha256"].lower():
            raise ValueError(f"Upstream source archive checksum mismatch: {name}")
        asset_entries[f"sources/{name}"] = path

    for name in RELEASE_DOCS:
        asset_entries[f"licenses/{name}"] = require_file(sources_dir, name)
    for name in WINDOWS_DOCS:
        asset_entries[f"licenses/{name}"] = require_file(windows_dir, name)
    for name in SOURCE_REPORTS:
        asset_entries[f"reports/{name}"] = require_file(sources_dir, name)
    for name in WINDOWS_REPORTS:
        asset_entries[f"reports/{name}"] = require_file(windows_dir, name)

    check_zip(asset_entries["licenses/THIRD_PARTY_NOTICES_2_7.zip"], minimum_entries=65)
    check_zip(asset_entries["licenses/license-evidence.zip"])

    notes = (
        "PDF COMPRESSOR 2.7.1 — THIRD-PARTY SOURCE CODE AND LICENSES\n"
        "================================================================\n"
        "The executable is the separate PDF_Compressor_2_7_1.exe asset.\n"
        "For regular use, only download the EXE.\n\n"
        "sources/  — six version-pinned Qt/PySide6/PyMuPDF/MuPDF archives.\n"
        "licenses/ — full notices, LGPL onefile relinking instructions, and\n"
        "             Windows package license evidence.\n"
        "reports/  — source/EXE SHA-256 and exact native binary inventory.\n"
        "SOURCES_SHA256SUMS.txt — official pinned SHA-256 for the six archives.\n\n"
        "Tagged application source: https://github.com/Valik2005/pdf-compressor\n"
        "The source/binary provenance and technical audits are not a legal\n"
        "certificate and do not waive third-party redistribution obligations.\n"
        "Use licenses/LGPL_RELINKING_2_7.md to rebuild with modified Qt DLLs.\n"
    )
    sums = "".join(f"{item['expected_sha256']}  {item['filename']}\n" for item in entries)

    destination.mkdir(parents=True, exist_ok=True)
    bundle = destination / BUNDLE_NAME
    if bundle.exists():
        raise ValueError("Refusing to overwrite an existing third-party bundle")
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as out:
        out.writestr("README.txt", notes)
        out.writestr("SOURCES_SHA256SUMS.txt", sums)
        for name, path in sorted(asset_entries.items()):
            out.write(path, arcname=name, compress_type=zipfile.ZIP_STORED)

    with zipfile.ZipFile(bundle) as archive:
        required = {"README.txt", "SOURCES_SHA256SUMS.txt", *asset_entries.keys()}
        if set(archive.namelist()) != required or archive.testzip() is not None:
            raise ValueError("Combined source ZIP is incomplete or corrupted")

    final_exe = destination / exe_name
    if final_exe.exists():
        raise ValueError("Refusing to overwrite an existing final EXE")
    shutil.copyfile(exe, final_exe)
    if digest(final_exe) != exe_sha:
        raise ValueError("Binary was altered while staging release")
    sums_path = destination / "SHA256SUMS.txt"
    sums_path.write_text(
        f"{exe_sha}  {exe_name}\n{digest(bundle)}  {BUNDLE_NAME}\n",
        encoding="utf-8",
    )
    result = {"version": "2.7.1", "source_git_commit": source_sha,
              "exe_sha256": exe_sha, "bundle_sha256": digest(bundle),
              "files": [exe_name, BUNDLE_NAME, "SHA256SUMS.txt"],
              "source_archives": len(entries),
              "third_party_bundle_records": len(asset_entries) + 2,
              "exe_bytes": final_exe.stat().st_size,
              "bundle_bytes": bundle.stat().st_size}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--windows", required=True, type=Path)
    parser.add_argument("--catalog", default=Path("docs/source-archives-2_7.json"), type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--exe-name", default="PDF_Compressor_2_7_1.exe")
    parser.add_argument("--source-sha", required=True)
    args = parser.parse_args()
    assemble(args.sources, args.windows, args.catalog, args.out, args.exe_name, args.source_sha)


if __name__ == "__main__":
    main()
