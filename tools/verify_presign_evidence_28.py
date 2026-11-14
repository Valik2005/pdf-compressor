"""Verify exact v2.8 *pre-sign technical* evidence across Windows and upstream archives.

This is a fail-closed technical identity/integrity gate. It is NOT a legal opinion:
all transitive licenses, corresponding-source completeness and recipient rights must
still be assessed before a public release.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

APP_EXE = "PDF_Compressor_2_8.exe"
PINS = {
    "PyMuPDF": "1.27.2.3",
    "PySide6": "6.12.0",
    "PySide6_Addons": "6.12.0",
    "PySide6_Essentials": "6.12.0",
    "shiboken6": "6.12.0",
    "Pillow": "12.3.0",
    "pyinstaller": "6.22.3",
}
NOTICES = {
    "app/AGPL-3.0/LICENSE",
    "components/qtbase-6.12.0-required/LICENSES/LGPL-3.0-only.txt",
    "components/qtbase-6.12.0-required/LICENSES/GPL-3.0-only.txt",
    "components/qtbase-6.12.0-required/LICENSES/Apache-2.0.txt",
    "components/qtbase-6.12.0-required/LICENSES/MIT.txt",
    "components/mupdf-1.27.2-native/COPYING",
    "components/openssl-3.5.9/LICENSE.txt",
    "components/openssl-3.5.9/AUTHORS.md",
    "notice-manifest.json",
    "components/qtbase-6.12.0-required/LICENSES/BSL-1.0.txt",
    "notices/QT_MESA_LLVMPIPE_ATTRIBUTION_2_8.txt",
}

def file_required(root: Path, name: str) -> Path:
    path = root / name
    if not path.is_file() or path.is_symlink() or not path.stat().st_size:
        raise ValueError(f"Missing/invalid review artifact: {name}")
    return path

def read_json(root: Path, name: str) -> dict:
    value = json.loads(file_required(root, name).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {name}")
    return value

def sha256(path: Path) -> str:
    d = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            d.update(block)
    return d.hexdigest()

def validate(windows: Path, sources: Path, catalog_path: Path, commit: str) -> dict:
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit.lower()):
        raise ValueError("Exact 40-character commit SHA required")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if catalog.get("schema_version") != 1 or "2.8" not in catalog.get("release", ""):
        raise ValueError("Incorrect v2.8 source catalog")
    required = [e for e in catalog.get("entries", []) if e.get("required")]
    if len(required) != 6 or len({e["id"] for e in required}) != 6:
        raise ValueError("Exactly six distinct source components expected")
    exe = file_required(windows, APP_EXE)
    manifest = read_json(windows, "build-manifest.json")
    binary = read_json(windows, "bundle-audit.json")
    native = read_json(windows, "native-source-mapping.json")
    signed_independent = sha256(exe)
    if not (manifest.get("source_git_commit") == commit
            and manifest.get("source_has_local_changes") is False
            and manifest.get("exe_name") == APP_EXE
            and manifest.get("exe_size_bytes") == exe.stat().st_size
            and manifest.get("exe_sha256") == binary.get("sha256")
            == native.get("exe_sha256") == signed_independent
            and str(manifest.get("builder_python", "")).startswith("3.14.")
            and manifest.get("builder_os") == "Windows"):
        raise ValueError("Exact clean Windows build SHA/commit/size mismatch")
    packages = manifest.get("installed_builder_package_versions", {})
    if {k: packages.get(k) for k in PINS} != PINS:
        raise ValueError("Installed build dependencies differ from v2.8 pinned packages")
    if (native.get("native_file_count", 0) < 100
            or native.get("unmapped_native_files")
            or native.get("missing_required_source_entries")
            or binary.get("included_virtual_keyboard_files")):
        raise ValueError("Native bundle has missing or prohibited components")

    downloads = read_json(sources, "source-download-report.json")
    audited = read_json(sources, "source-archive-audit.json")
    if (downloads.get("all_required_archives_verified") is not True
            or audited.get("all_required_with_published_hashes") is not True):
        raise ValueError("Source hash verification flag missing")
    reported = {e["id"]: e for e in downloads.get("archives", [])}
    inspected = {e["id"]: e for e in audited.get("archives", [])}
    entries = []
    for item in required:
        name, component = item["filename"], item["id"]
        if (Path(name).name != name or "/" in name or chr(92) in name):
            raise ValueError("Unsafe archive name")
        actual = sha256(file_required(sources, name))
        record = reported.get(component, {})
        reviewed = inspected.get(component, {})
        if (actual != item.get("expected_sha256", "").lower()
                or record.get("status") != "hash_matches_official_source"
                or record.get("trusted_expected_sha256") != actual
                or record.get("downloaded_sha256") != actual
                or reviewed.get("status") != "hash_matches_published_value"
                or reviewed.get("local_sha256") != actual):
            raise ValueError(f"Source archive evidence mismatch: {component}")
        entries.append({"component": component, "source_sha256": actual})

    notice_zip = file_required(sources, "THIRD_PARTY_NOTICES_2_8.zip")
    with zipfile.ZipFile(notice_zip) as z:
        names = set(z.namelist())
        if z.testzip() is not None or len(names) < 65 or not NOTICES.issubset(names):
            raise ValueError("Missing third-party license texts/notices in ZIP")
        declaration = json.loads(z.read("notice-manifest.json"))
        if declaration.get("matching_archive_hashes_verified") is not True:
            raise ValueError("Notice manifest did not verify matching source hashes")
        licensed = {x.get("component"): x.get("sha256")
                    for x in declaration.get("source_archives", [])}
        if any(licensed.get(e["component"]) != e["source_sha256"] for e in entries):
            raise ValueError("Notices not generated from exact source archives")
    for name in ("LGPL_RELINKING_2_8.md", "THIRD_PARTY_NOTICES_2_8.md", "libffi-LICENSE.txt"):
        file_required(sources, name)

    license_zip = file_required(windows, "license-evidence.zip")
    with zipfile.ZipFile(license_zip) as z:
        if z.testzip() is not None:
            raise ValueError("Corrupted installed-package license archive")
        rec = json.loads(z.read("evidence-report.json"))
        if rec.get("exe_sha256") != signed_independent or rec.get("exe_name") != APP_EXE:
            raise ValueError("License evidence does not match the Windows EXE")
        missing_license_material = rec.get("missing", [])
    return {
        "schema_version": 1,
        "source_git_commit": commit,
        "unsigned_exe_sha256": signed_independent,
        "source_archives_verified": len(entries),
        "source_archive_provenance": entries,
        "third_party_license_records": len(names),
        "version_pins_match": True,
        "native_file_count": native["native_file_count"],
        "native_component_counts": native.get("component_counts", {}),
        "technical_integrity_checks_passed": True,
        "license_compliance_certified": False,
        "upstream_native_review_items": native.get("open_manual_review_components", []),
        "installed_package_evidence_missing_or_incomplete": missing_license_material,
        "legal_review_status": "REQUIRES INDEPENDENT FINAL REVIEW; do not claim compliance from this report",
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--windows", type=Path, required=True)
    p.add_argument("--sources", type=Path, required=True)
    p.add_argument("--catalog", type=Path, default=Path("docs/source-archives-2_8.json"))
    p.add_argument("--source-sha", required=True)
    p.add_argument("--out", type=Path, required=True)
    a=p.parse_args()
    result=validate(a.windows, a.sources, a.catalog, a.source_sha)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print("Exact v2.8 source+Windows hash/version audit passed; licensing review is not certified.")

if __name__ == "__main__":
    main()
