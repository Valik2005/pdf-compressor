"""Assemble exactly three v2.8 release files from an independently verified SIGNED EXE.

No downloads or publication. Input Windows artifacts must originate from the
approved SignPath/Windows GitHub Actions workflow. This assembler validates
cross-file integrity but does NOT itself perform an Authenticode trust check;
only the Windows runner with a trust store can do that.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

from tools.assemble_patch_release import (
    SOURCES, RELEASE_DOCS, SOURCE_REPORTS, BUNDLE_NAME,
    check_zip, digest, require_file,
)

EXE_NAME = "PDF_Compressor_2_8.exe"
AUDIT_FILES = (
    "unsigned-build-manifest.json",
    "unsigned-bundle-audit.json",
    "native-source-mapping.json",
    "signature-verification.json",
    "authenticode-verification.json",
)


def assemble_signed_28(sources_dir: Path, windows_dir: Path, catalog_path: Path,
                       destination: Path, source_sha: str) -> dict:
    """Fail closed BEFORE creating the destination on any invalid evidence."""
    if len(source_sha) != 40 or any(ch not in "0123456789abcdef"
                                    for ch in source_sha.lower()):
        raise ValueError("A full expected source commit SHA is mandatory")

    signed = require_file(windows_dir, EXE_NAME)
    signature = json.loads(require_file(windows_dir, "signature-verification.json")
                           .read_text(encoding="utf-8-sig"))
    trust = json.loads(require_file(windows_dir, "authenticode-verification.json")
                       .read_text(encoding="utf-8-sig"))
    unsigned = json.loads(require_file(windows_dir, "unsigned-build-manifest.json")
                          .read_text(encoding="utf-8-sig"))
    bundle_audit = json.loads(require_file(windows_dir, "unsigned-bundle-audit.json")
                              .read_text(encoding="utf-8-sig"))
    natives = json.loads(require_file(windows_dir, "native-source-mapping.json")
                         .read_text(encoding="utf-8-sig"))

    signed_sha = digest(signed)
    unsigned_sha = unsigned.get("exe_sha256")
    if (signature.get("version") != "2.8"
            or signature.get("source_git_commit") != source_sha
            or signature.get("authenticode_verified") is not True
            or signature.get("public_release_created") is not False
            or signature.get("signed_sha256") != signed_sha
            or signature.get("signed_size_bytes") != signed.stat().st_size
            or signature.get("unsigned_sha256") != unsigned_sha
            or signed_sha == unsigned_sha):
        raise ValueError("Signed EXE or signature-verification report mismatch")
    signer = signature.get("signer_subject") or ""
    timestamper = signature.get("timestamp_certificate_subject") or ""
    if "SignPath Foundation" not in signer or not timestamper:
        raise ValueError("Missing expected SignPath Foundation publisher/timestamp")
    if (trust.get("signature_status") != "Valid"
            or trust.get("signtool_verified") is not True
            or trust.get("signed_sha256") != signed_sha
            or trust.get("signer_subject") != signer
            or trust.get("timestamper_subject") != timestamper):
        raise ValueError("Windows Authenticode verification evidence mismatch")

    if (unsigned.get("exe_name") != EXE_NAME
            or unsigned.get("source_git_commit") != source_sha
            or unsigned.get("source_has_local_changes") is not False
            or unsigned.get("exe_sha256") != bundle_audit.get("sha256")
            or unsigned.get("exe_sha256") != natives.get("exe_sha256")
            or unsigned.get("exe_size_bytes", 0) <= 0
            or unsigned.get("builder_os") != "Windows"
            or not str(unsigned.get("builder_python", "")).startswith("3.14.")):
        raise ValueError("Unsigned build provenance and native inventory mismatch")
    if (natives.get("native_file_count", 0) < 100
            or natives.get("unmapped_native_files")
            or natives.get("missing_required_source_entries")
            or bundle_audit.get("included_virtual_keyboard_files")):
        raise ValueError("Unmapped native dependency or prohibited Qt module")

    check_zip(require_file(windows_dir, "license-evidence.zip"))
    cat = json.loads(catalog_path.read_text(encoding="utf-8"))
    required = [item for item in cat.get("entries", []) if item.get("required")]
    if (len(required) != SOURCES
            or any(not item.get("expected_sha256") for item in required)):
        raise ValueError("Six exact verified upstream source archives required")
    archived_sources = {}
    for entry in required:
        filename = entry["filename"]
        if Path(filename).name != filename:
            raise ValueError("Unsafe upstream source archive name")
        source = require_file(sources_dir, filename)
        if digest(source).lower() != entry["expected_sha256"].lower():
            raise ValueError("Upstream source archive checksum mismatch")
        archived_sources["sources/" + filename] = source

    audit = json.loads(require_file(sources_dir, "source-archive-audit.json")
                       .read_text(encoding="utf-8-sig"))
    downloads = json.loads(require_file(sources_dir, "source-download-report.json")
                           .read_text(encoding="utf-8-sig"))
    if (audit.get("all_required_with_published_hashes") is not True
            or downloads.get("all_required_archives_verified") is not True):
        raise ValueError("Required source archive checks were not verified")

    records = dict(archived_sources)
    for name in RELEASE_DOCS:
        records["licenses/" + name] = require_file(sources_dir, name)
    records["licenses/license-evidence.zip"] = require_file(windows_dir, "license-evidence.zip")
    for name in SOURCE_REPORTS:
        records["reports/" + name] = require_file(sources_dir, name)
    for name in AUDIT_FILES:
        records["reports/" + name] = require_file(windows_dir, name)
    check_zip(records["licenses/THIRD_PARTY_NOTICES_2_7.zip"], minimum_entries=65)

    if destination.exists():
        raise ValueError("Destination already exists: refusing overwrite")
    destination.mkdir(parents=True)
    bundle = destination / BUNDLE_NAME
    notes = (
        "PDF Compressor v2.8 — exact third-party sources and licenses\n"
        "================================================================\n"
        "This ZIP accompanies the separately signed PDF_Compressor_2_8.exe.\n"
        "sources/: six hash-verified upstream archives (dependency versions pinned).\n"
        "licenses/: upstream notices, source and relinking information.\n"
        "reports/: pre-sign native/manifest provenance and signed Authenticode checks.\n"
        "The source/notice audit is evidence, not a legal certification.\n"
        "App source for exact commit: https://github.com/Valik2005/pdf-compressor\n"
    )
    sums = "".join(f"{row['expected_sha256']}  {row['filename']}\n"
                   for row in required)
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_STORED,
                         allowZip64=True) as out:
        out.writestr("README.txt", notes)
        out.writestr("SOURCES_SHA256SUMS.txt", sums)
        for name, path in sorted(records.items()):
            out.write(path, arcname=name, compress_type=zipfile.ZIP_STORED)
    with zipfile.ZipFile(bundle) as out:
        if (set(out.namelist()) != {"README.txt", "SOURCES_SHA256SUMS.txt", *records}
                or out.testzip() is not None):
            raise ValueError("Third-party ZIP damaged during assembly")

    final_exe = destination / EXE_NAME
    shutil.copyfile(signed, final_exe)
    if digest(final_exe) != signed_sha:
        raise ValueError("Signed EXE changed while staging release")
    (destination / "SHA256SUMS.txt").write_text(
        f"{signed_sha}  {EXE_NAME}\n{digest(bundle)}  {BUNDLE_NAME}\n",
        encoding="utf-8",
    )
    result = {"release": "v2.8", "source_git_commit": source_sha,
              "signed_exe_sha256": signed_sha, "source_archives": SOURCES,
              "files": sorted(p.name for p in destination.iterdir())}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--windows", required=True, type=Path)
    parser.add_argument("--catalog", type=Path,
                        default=Path("docs/source-archives-2_7.json"))
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--source-sha", required=True)
    args = parser.parse_args()
    assemble_signed_28(args.sources, args.windows, args.catalog,
                       args.out, args.source_sha)


if __name__ == "__main__":
    main()
