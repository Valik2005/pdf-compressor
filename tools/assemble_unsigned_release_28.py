"""Stage v2.8 UNSIGNED Windows release files from one audited GitHub Actions run.

This tool cannot publish, tag or sign anything. It verifies exact source and
binary provenance, an independently run Windows unsigned-signature check,
nine source archives and 2.8 notices, then stages exactly three files.

Technical integrity does not constitute legal clearance of third-party
redistribution terms. A separate, explicit maintainer release decision is
required, even if this script and all CI jobs succeed.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import zipfile

from tools.assemble_patch_release import (
    SOURCE_REPORTS, BUNDLE_NAME, check_zip, digest, require_file,
)
from tools.verify_presign_evidence_28 import validate as verify_presign
from tools.audit_source_coverage_28 import analyze as review_source_coverage
from tools.fetch_supplemental_sources_28 import verify_prepared as verify_supplemental_sources

EXE_NAME = "PDF_Compressor_2_8.exe"
SOURCES = 9  # v2.8: + Pillow/Mesa/LLVM; historical v2.7 remains 6.
RELEASE_DOCS = (
    "LGPL_RELINKING_2_8.md",
    "THIRD_PARTY_NOTICES_2_8.md",
    "libffi-LICENSE.txt",
    "THIRD_PARTY_NOTICES_2_8.zip",
)
BINARY_REPORTS = (
    "build-manifest.json",
    "bundle-audit.json",
    "native-source-mapping.json",
    "native-binary-origin.json",
    "native-collection-sources.json",
    "unsigned-authenticode-check.json",
    "presign-technical-evidence.json",
)


def assemble_unsigned_28(
    sources_dir: Path,
    windows_dir: Path,
    evidence_path: Path,
    catalog_path: Path,
    destination: Path,
    source_sha: str,
) -> dict:
    """Validate all evidence before writing files; refuse existing destinations."""
    if destination.exists():
        raise ValueError("Refusing to overwrite an existing release staging directory")
    exe = require_file(windows_dir, EXE_NAME)

    # Recalculate, do not just trust a pass/fail bit in a workflow artifact.
    recomputed = verify_presign(windows_dir, sources_dir, catalog_path, source_sha)
    evidence = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
    if recomputed != evidence or recomputed.get("license_compliance_certified") is not False:
        raise ValueError("Same-commit source/binary cross-audit differs from independent evidence")

    check = json.loads(
        require_file(windows_dir, "unsigned-authenticode-check.json")
        .read_text(encoding="utf-8-sig")
    )
    if not (
        check.get("status") == "NotSigned"
        and check.get("checked_on_windows") is True
        and check.get("source_git_commit") == source_sha
        and check.get("exe_sha256") == digest(exe)
    ):
        raise ValueError("No matching Windows Authenticode NotSigned evidence")
    if any((windows_dir / name).exists() for name in (
        "signature-verification.json", "authenticode-verification.json"
    )):
        raise ValueError("Signed-release evidence must never enter unsigned packaging")

    required = [x for x in json.loads(catalog_path.read_text(encoding="utf-8"))["entries"]
                if x.get("required")]
    if len(required) != SOURCES or len({x["filename"] for x in required}) != SOURCES:
        raise ValueError("Nine distinct exact source archives are required")

    files: dict[str, Path] = {}
    for component in required:
        name = component["filename"]
        if name != Path(name).name or "/" in name or chr(92) in name:
            raise ValueError("Unsafe source archive name")
        archive = require_file(sources_dir, name)
        if digest(archive) != component["expected_sha256"].lower():
            raise ValueError("Source archive hash does not match pinned upstream checksum")
        files["sources/" + name] = archive

    supplemental_rows = []
    supplement_report = sources_dir / "supplemental-source-report.json"
    if supplement_report.exists():
        supplement_catalog = (
            Path(__file__).resolve().parents[1] /
            "docs" / "supplemental-source-archives-2_8.json"
        )
        supplemental_rows = verify_supplemental_sources(
            supplement_catalog, sources_dir
        )
        for entry in supplemental_rows:
            files["sources/" + entry["filename"]] = require_file(
                sources_dir, entry["filename"]
            )
        files["reports/supplemental-source-report.json"] = supplement_report
    elif os.environ.get("PDF28_REQUIRE_SUPPLEMENTAL") == "1":
        raise ValueError("Verified CPython/OpenSSL/libffi full source archives required")

    for name in RELEASE_DOCS:
        files["licenses/" + name] = require_file(sources_dir, name)
    files["licenses/license-evidence.zip"] = require_file(windows_dir, "license-evidence.zip")
    for name in SOURCE_REPORTS:
        files["reports/" + name] = require_file(sources_dir, name)
    for name in ("build-manifest.json", "bundle-audit.json",
                 "native-source-mapping.json", "native-binary-origin.json",
                 "native-collection-sources.json", "unsigned-authenticode-check.json"):
        files["reports/" + name] = require_file(windows_dir, name)
    files["reports/presign-technical-evidence.json"] = evidence_path

    # Require the exact same native/source coverage audit produced independently
    # during cross-verify. This report explicitly records missing code and cannot
    # be used as a false claim of completed legal licensing review.
    coverage_path = require_file(evidence_path.parent, "source-coverage-report.json")
    recorded_coverage = json.loads(coverage_path.read_text(encoding="utf-8-sig"))
    independent_coverage = review_source_coverage(windows_dir, sources_dir, catalog_path)
    if recorded_coverage != independent_coverage:
        raise ValueError("Independent source coverage audit differs from staged evidence")
    if recorded_coverage.get("legal_compliance_certified") is not False:
        raise ValueError("A source inventory cannot certify third-party redistribution rights")
    files["reports/source-coverage-report.json"] = coverage_path

    check_zip(files["licenses/THIRD_PARTY_NOTICES_2_8.zip"], minimum_entries=65)
    check_zip(files["licenses/license-evidence.zip"])

    notice = (
        "PDF Compressor v2.8 — UNSIGNED Windows release\n"
        "================================================\n"
        "The separately provided PDF_Compressor_2_8.exe has NO trusted\n"
        "Authenticode signature. Verify SHA256SUMS.txt against the release page.\n"
        "A checksum is an integrity check, not proof of publisher identity.\n"
        "\n"
        "sources/: nine core SHA-256 archives, plus separately checked runtime sources if provided.\n"
        "licenses/: Qt LGPL relinking instructions, licenses and notices.\n"
        "reports/: build/source/native provenance, missing-source audit, Windows NotSigned evidence.\n"
        "SOURCES_SHA256SUMS.txt: independent upstream checksums.\n"
        "\n"
        "Official project source: https://github.com/Valik2005/pdf-compressor\n"
        "These technical reports do NOT certify third-party legal compliance.\n"
    )
    source_sums = "".join(
        f"{entry['expected_sha256'].lower()}  {entry['filename']}\n"
        for entry in required
    )
    source_sums += "".join(
        f"{entry['sha256']}  {entry['filename']}\n"
        for entry in supplemental_rows
    )

    destination.mkdir(parents=True)
    bundle = destination / BUNDLE_NAME
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_STORED,
                         allowZip64=True) as out:
        out.writestr("README.txt", notice)
        out.writestr("SOURCES_SHA256SUMS.txt", source_sums)
        for name, file in sorted(files.items()):
            out.write(file, arcname=name, compress_type=zipfile.ZIP_STORED)

    with zipfile.ZipFile(bundle) as archive:
        expected = {"README.txt", "SOURCES_SHA256SUMS.txt", *files}
        if set(archive.namelist()) != expected or archive.testzip() is not None:
            raise ValueError("Source/license ZIP failed post-assembly validation")

    final_exe = destination / EXE_NAME
    shutil.copyfile(exe, final_exe)
    if digest(final_exe) != evidence["unsigned_exe_sha256"]:
        raise ValueError("EXE changed while staging")
    sums = destination / "SHA256SUMS.txt"
    sums.write_text(
        f"{digest(final_exe)}  {EXE_NAME}\n"
        f"{digest(bundle)}  {BUNDLE_NAME}\n",
        encoding="utf-8",
    )
    if {x.name for x in destination.iterdir()} != {
        EXE_NAME, BUNDLE_NAME, "SHA256SUMS.txt"
    }:
        raise ValueError("Unexpected release output assets")
    result = {
        "release": "v2.8",
        "signature": "NotSigned",
        "source_git_commit": source_sha,
        "unsigned_exe_sha256": digest(final_exe),
        "source_archives": SOURCES,
        "supplemental_source_archives": len(supplemental_rows),
        "files": sorted(x.name for x in destination.iterdir()),
        "license_compliance_certified": False,
        "release_authorized": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--windows", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--catalog", type=Path,
                        default=Path("docs/source-archives-2_8.json"))
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--source-sha", required=True)
    args = parser.parse_args()
    assemble_unsigned_28(args.sources, args.windows, args.evidence,
                         args.catalog, args.out, args.source_sha)


if __name__ == "__main__":
    main()
