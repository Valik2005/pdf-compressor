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

from tools.audit_native_binary_origin_28 import embedded_native_members, sha256_bytes

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
    origin = read_json(windows, "native-binary-origin.json")
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

    if (origin.get("source_git_commit") != commit
            or origin.get("exe_sha256") != signed_independent
            or origin.get("native_file_count") != native.get("native_file_count")
            or origin.get("unmatched_wheel_entries")
            or origin.get("installed_wheel_record_mismatches")
            or origin.get("redistribution_rights_verified") is not False):
        raise ValueError("Exact embedded native byte provenance failed")
    # Cross-check all independently produced inventories against the ACTUAL
    # decompressed onefile bytes. A matching top-level EXE hash alone does not
    # prove an artifact's separately uploaded JSON inventory is complete.
    unpacked = [(name, sha256_bytes(blob), len(blob))
                for name, blob in embedded_native_members(exe)]
    packed_names = [name for name, _, _ in unpacked]
    binary_names = [item.get("name") for item in binary.get("all_entries", [])
                    if str(item.get("name", "")).lower().endswith((".dll", ".pyd"))]
    mapped_names = [row.get("path") for row in native.get("native_component_mapping", [])]
    records = origin.get("entries")
    count = native["native_file_count"]
    if (not isinstance(records, list) or len(records) != count
            or len(unpacked) != count or binary_names != packed_names
            or mapped_names != packed_names or len(set(packed_names)) != count
            or [record.get("name") for record in records] != packed_names):
        raise ValueError("Native EXE, bundle, classification and byte-origin inventories differ")
    matches_count = 0
    for record, (name, expected_hash, expected_size) in zip(records, unpacked):
        matches = record.get("matched_installed_origins")
        if (record.get("sha256") != expected_hash
                or record.get("size_bytes") != expected_size
                or not isinstance(matches, list)
                or record.get("status") != (
                    "byte-identical" if matches else "unverified-build-origin")
                or any(candidate.get("sha256") != expected_hash or
                       candidate.get("wheel_record_matches_installed_file") is False
                       for candidate in matches)):
            raise ValueError(f"Native byte-origin report differs from EXE: {name}")
        if name.lower().startswith(("pyside6/", "shiboken6/", "pil/", "pymupdf/")) and not matches:
            raise ValueError(f"Bundled wheel binary has no matching installed origin: {name}")
        matches_count += bool(matches)
    if origin.get("matched_count") != matches_count:
        raise ValueError("Native byte-origin matched count does not equal inventory")

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
        pillow_notice_path = (
            "packages/Pillow/12.3.0/"
            "pillow-12.3.0.dist-info/licenses/LICENSE"
        )
        if pillow_notice_path not in z.namelist():
            raise ValueError("Exact Pillow 12.3.0 wheel license text not packaged")
        pillow_license = z.read(pillow_notice_path).decode("utf-8", "strict").lower()
        # The Windows wheel embeds these codecs, and its LICENSE includes
        # their upstream notices. Do not accept a short generic Pillow-only
        # license in place of the complete wheel distribution notice.
        codec_markers = (
            "libavif-1.4.2", "libjpeg-turbo-3.1.4.1", "libpng-1.6.58",
            "libwebp-1.6.0", "openjpeg-2.5.4", "tiff-4.7.1",
            "freetype-2.14.3", "lcms2-2.19.1", "harfbuzz-14.2.1",
            "brotli-1.2.0", "zlib-ng-2.3.3",
        )
        if len(pillow_license) < 50_000 or any(
            marker not in pillow_license for marker in codec_markers
        ):
            raise ValueError("Pillow codec and font/image library notices are incomplete")

    return {
        "schema_version": 1,
        "source_git_commit": commit,
        "unsigned_exe_sha256": signed_independent,
        "source_archives_verified": len(entries),
        "source_archive_provenance": entries,
        "third_party_license_records": len(names),
        "version_pins_match": True,
        "native_file_count": native["native_file_count"],
        "native_byte_identical_origin_count": origin["matched_count"],
        "pillow_codec_license_notices_checked": list(codec_markers),
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
