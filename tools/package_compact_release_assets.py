"""Repack existing v2.7.0 GitHub Release assets into one transparent source bundle.

Offline-only, fail-closed. Does not access GitHub or modify any release.
Supply the folder containing the original release assets, and the pinned
source-catalog JSON from the released repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

RELEASE_EXE = "PDF_Compressor_2_7.exe"
BUNDLE = "Third_Party_Sources_and_Licenses.zip"
CHECKSUMS = "SHA256SUMS.txt"
REQUIRED_DOCUMENTS = {
    "LGPL_RELINKING_2_7.md",
    "libffi-LICENSE.txt",
    "license-evidence.zip",
    "THIRD_PARTY_NOTICES_2_7.md",
    "THIRD_PARTY_NOTICES_2_7.zip",
}
REQUIRED_REPORTS = {
    "build-manifest.json",
    "bundle-audit.json",
    "native-source-mapping.json",
    "source-archive-audit.json",
    "source-download-report.json",
}

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def package(folder: Path, catalog: Path, asset_inventory: Path) -> dict:
    folder = folder.resolve(strict=True)
    if not folder.is_dir():
        raise ValueError("Release assets directory must exist")
    entries = json.loads(catalog.read_text(encoding="utf-8"))["entries"]
    sources = {e["filename"]: e for e in entries if e["required"]}
    if len(sources) != 6 or not all(e.get("expected_sha256") for e in sources.values()):
        raise ValueError("Expected six pinned third-party source archives")
    docs = REQUIRED_DOCUMENTS | REQUIRED_REPORTS
    original_assets = {RELEASE_EXE, CHECKSUMS} | docs | set(sources)
    if len(original_assets) != 18:
        raise ValueError("Original release inventory is unexpectedly incomplete")

    inventory = json.loads(asset_inventory.read_text(encoding="utf-8"))
    if inventory["tag_name"] != "v2.7.0" or inventory["draft"]:
        raise ValueError("Incorrect or unpublished release")
    published = {e["name"]: e for e in inventory["assets"]}
    if set(published) != original_assets:
        raise ValueError(f"Unexpected release assets: {sorted(set(published) ^ original_assets)}")

    for name in sorted(original_assets):
        f = folder / name
        if not f.is_file() or f.is_symlink() or not f.stat().st_size:
            raise ValueError(f"Missing, empty, or symlinked release file: {name}")
        sha = digest(f)
        if published[name].get("digest") != f"sha256:{sha}":
            raise ValueError(f"GitHub-reported SHA-256 differs from downloaded file: {name}")
        if name in sources and sources[name]["expected_sha256"] != sha:
            raise ValueError(f"Pinned upstream source SHA-256 mismatch: {name}")

    exe = folder / RELEASE_EXE
    manifest = json.loads((folder / "build-manifest.json").read_text(encoding="utf-8"))
    if manifest["exe_sha256"] != digest(exe) or manifest["exe_size_bytes"] != exe.stat().st_size:
        raise ValueError("EXE differs from its released build manifest")
    with zipfile.ZipFile(folder / "THIRD_PARTY_NOTICES_2_7.zip") as z:
        if z.testzip() is not None:
            raise ValueError("Third-party notice archive corrupted")
        if len(z.namelist()) < 65:
            raise ValueError("Third-party notice archive unexpectedly small")
    with zipfile.ZipFile(folder / "license-evidence.zip") as z:
        if z.testzip() is not None:
            raise ValueError("Windows license evidence archive corrupted")

    documentation = (
        "PDF COMPRESSOR 2.7 — SOURCES, LICENSES AND AUDIT RECORDS\n"
        "==========================================================\n"
        "The program itself is the separate PDF_Compressor_2_7.exe release asset.\n"
        "This single archive preserves ALL original third-party source archives,\n"
        "full source-derived notices, builder license evidence, relevant license\n"
        "instructions, exact source/EXE audit reports, and the original checksum list.\n\n"
        "sources/  : Six original, unchanged version-pinned source tarballs.\n"
        "licenses/ : Full third-party notices, LGPL relinking instructions, licenses.\n"
        "reports/  : Original build, bundle, source and native DLL/PYD audits.\n"
        "SOURCES_SHA256SUMS.txt : Independent SHA-256 values for six source tarballs.\n"
        "README.txt: This guide.\n\n"
        "To modify and rebuild Qt in the onefile package, read\n"
        "licenses/LGPL_RELINKING_2_7.md and obtain the tagged application sources\n"
        "from https://github.com/Valik2005/pdf-compressor/tree/v2.7.0\n"
        "Actual library terms, copyright notices and source rights are retained.\n"
        "Packaging into one ZIP does not waive or alter third-party licenses.\n"
    )
    archive = folder / BUNDLE
    if archive.exists():
        raise ValueError("Consolidated archive already exists; refusing overwrite")
    records: dict[str, Path | bytes] = {"README.txt": documentation.encode("utf-8")}
    source_lines = []
    for name in sorted(sources):
        records[f"sources/{name}"] = folder / name
        source_lines.append(f"{sources[name]['expected_sha256']}  {name}")
    records["SOURCES_SHA256SUMS.txt"] = ("\n".join(source_lines) + "\n").encode("utf-8")
    for name in sorted(REQUIRED_DOCUMENTS):
        records[f"licenses/{name}"] = folder / name
    for name in sorted(REQUIRED_REPORTS):
        records[f"reports/{name}"] = folder / name
    records["reports/ORIGINAL_SHA256SUMS.txt"] = folder / CHECKSUMS

    # The .tar.gz and .tar.xz files are already compressed: do not
    # waste CPU or expand memory trying to compress them again.
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as out:
        for name, source in sorted(records.items()):
            if isinstance(source, Path):
                out.write(source, arcname=name, compress_type=zipfile.ZIP_STORED)
            else:
                out.writestr(name, source, compress_type=zipfile.ZIP_STORED)
    with zipfile.ZipFile(archive) as z:
        if set(z.namelist()) != set(records) or z.testzip() is not None:
            raise ValueError("Consolidated source bundle validation failed")
        for name in sorted(sources):
            with z.open(f"sources/{name}") as source:
                h = hashlib.sha256()
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    h.update(block)
                if h.hexdigest() != sources[name]["expected_sha256"]:
                    raise ValueError(f"Source ZIP entry SHA mismatch: {name}")

    checksum_text = (f"{digest(exe)}  {RELEASE_EXE}\n"
                     f"{digest(archive)}  {BUNDLE}\n")
    (folder / "SHA256SUMS_COMPACT.txt").write_text(checksum_text, encoding="utf-8")
    report = {
        "tag": "v2.7.0",
        "original_asset_count": len(original_assets),
        "new_asset_count": 3,
        "exe_sha256": digest(exe),
        "exe_size_bytes": exe.stat().st_size,
        "bundle_name": BUNDLE,
        "bundle_sha256": digest(archive),
        "bundle_size_bytes": archive.stat().st_size,
        "bundle_records": sorted(records),
        "remove_after_upload_and_verified": sorted(original_assets - {RELEASE_EXE, CHECKSUMS}),
    }
    (folder / "release-compaction-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--assets", type=Path, required=True)
    p.add_argument("--catalog", type=Path, default=Path("docs/source-archives-2_7.json"))
    p.add_argument("--release-json", type=Path, required=True)
    a = p.parse_args()
    report = package(a.assets, a.catalog, a.release_json)
    print("Preserved 18 original assets as EXE, ZIP and checksums.")
    print("EXE SHA-256:", report["exe_sha256"])
    print("Bundle SHA-256:", report["bundle_sha256"])
    print("Packed records:", len(report["bundle_records"]))

if __name__ == "__main__":
    main()
