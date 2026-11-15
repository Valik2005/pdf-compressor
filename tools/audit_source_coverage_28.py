"""Cross-reference exact v2.8 native EXE members with distributed source evidence.

This report is intentionally *not* a proof of corresponding-source completeness.
A wheel RECORD proves native byte origin, not the sources of statically linked
libraries; text in a license file does not prove that source is bundled.
This script must run on the same GitHub Actions source/executable artifacts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import zipfile

from tools.audit_onefile_native_sources import component

# Versions from the Pillow 12.3.0 wheel's independently checked license text
# and its upstream Windows build dependency catalog. These are candidates,
# NOT a claim that each library is present in all six packaged PIL/*.pyd files.
# The exact native linkage and any incorporated patches still require evidence.
PILLOW_CANDIDATES = {
    "libavif": "1.4.2",
    "libjpeg-turbo": "3.1.4.1",
    "libpng": "1.6.58",
    "libwebp": "1.6.0",
    "openjpeg": "2.5.4",
    "tiff": "4.7.1",
    "freetype": "2.14.3",
    "lcms2": "2.19.1",
    "harfbuzz": "14.2.1",
    "brotli": "1.2.0",
    "zlib-ng": "2.3.3",
}
# In addition to the 11 notices above, libavif can incorporate libaom and
# dav1d. libtiff may incorporate liblzma. Check actual linkage/build evidence.
POSSIBLE_TRANSITIVE = ("libaom", "dav1d", "liblzma")

SOURCE_GROUPS = {
    "QtBase": ("qtbase-6.12.0-required",),
    "QtSvg": ("qtsvg-6.12.0",),
    "QtImageFormats": ("qtimageformats-6.12.0",),
    "PySide6/Shiboken": ("qtforpython-6.12.0",),
    "PyMuPDF": ("pymupdf-1.27.2.3",),
    "MuPDF": ("mupdf-1.27.2-native",),
    "Pillow codecs": ("pillow-12.3.0",),
    "Mesa OpenGL software rasterizer": ("mesa-11.2.2", "llvm-3.6.2"),
    "OpenSSL": (),
    "libffi": (),
    "Python runtime": (),
}
PILLOW_LICENSE = (
    "packages/Pillow/12.3.0/"
    "pillow-12.3.0.dist-info/licenses/LICENSE"
)
SHA_RE = re.compile(r"^[a-f0-9]{64}$")


def json_file(folder: Path, name: str) -> dict:
    path = folder / name
    if not path.is_file():
        raise ValueError("Required binary provenance report absent: " + name)
    result = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(result, dict):
        raise ValueError("Provenance report is not a JSON object: " + name)
    return result


def analyze(windows: Path, sources: Path, catalog_path: Path) -> dict:
    manifest = json_file(windows, "build-manifest.json")
    native = json_file(windows, "native-source-mapping.json")
    collection = json_file(windows, "native-collection-sources.json")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    source_sha = manifest.get("source_git_commit")
    exe_sha = manifest.get("exe_sha256")
    if (not isinstance(source_sha, str) or len(source_sha) != 40
            or not isinstance(exe_sha, str) or not SHA_RE.fullmatch(exe_sha)):
        raise ValueError("Missing exact EXE/source identity")
    if (collection.get("source_git_commit") != source_sha
            or native.get("exe_sha256") != exe_sha):
        raise ValueError("Native inventory is not from the same EXE/source commit")
    entries = native.get("native_component_mapping")
    collected = collection.get("entries")
    if (not isinstance(entries, list) or not isinstance(collected, list)
            or not entries or len(entries) != len(collected)
            or native.get("native_file_count") != len(entries)
            or collection.get("native_file_count") != len(entries)):
        raise ValueError("Native coverage inventory length differs from build audit")
    catalog_items = {
        item["id"]: item for item in catalog.get("entries", [])
        if item.get("required") is True
    }
    by_name = {}
    for row in collected:
        name = row.get("path")
        if not isinstance(name, str) or not name or name in by_name:
            raise ValueError("Invalid/duplicate exact native member")
        sha = row.get("source_sha256")
        if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
            raise ValueError("Missing collected native SHA-256: " + name)
        by_name[name] = row

    reported = []
    groups = set()
    for entry in entries:
        name = entry.get("path")
        group = entry.get("component")
        if (not isinstance(name, str) or name not in by_name
                or component(name) != group or group not in SOURCE_GROUPS):
            raise ValueError("Unmapped or misclassified native component: " + str(name))
        groups.add(group)
        sources_for_group = SOURCE_GROUPS[group]
        for source_id in sources_for_group:
            desc = catalog_items.get(source_id)
            if not desc:
                raise ValueError("Required source absent from catalog: " + source_id)
            archive = sources / desc["filename"]
            if not archive.is_file() or archive.is_symlink():
                raise ValueError("Required upstream source archive absent: " + source_id)
        origin = by_name[name]
        reported.append({
            "member": name,
            "native_sha256": origin["source_sha256"],
            "component": group,
            "origin_scope": origin.get("source_scope"),
            "origin_distribution": origin.get("distribution"),
            "origin_version": origin.get("distribution_version"),
            "upstream_source_archive_ids": list(sources_for_group),
            "source_evidence": (
                "version-pinned-upstream-archives; exact wheel patches/build inputs unverified"
                if sources_for_group else
                "NO separate source archive in nine-source release pack; system-library exception unassessed"
            ),
            "full_corresponding_source_verified": False,
        })
    if len({x["member"] for x in reported}) != len(entries):
        raise ValueError("Native membership mismatch")

    candidates = []
    if "Pillow codecs" in groups:
        evidence = windows / "license-evidence.zip"
        if not evidence.is_file():
            raise ValueError("Exact installed Pillow LICENSE ZIP absent")
        with zipfile.ZipFile(evidence) as archive:
            if PILLOW_LICENSE not in archive.namelist():
                raise ValueError("Exact Pillow wheel license absent")
            license_text = archive.read(PILLOW_LICENSE).decode("utf-8").lower()
        for lib, version in sorted(PILLOW_CANDIDATES.items()):
            marker = lib + "-" + version
            if marker not in license_text:
                raise ValueError("Missing installed Pillow wheel notice: " + marker)
            candidates.append({
                "component": lib,
                "version_in_wheel_notices": version,
                "source_in_nine_archives": False,
                "compiled_linkage_confirmed": False,
                "source_obligation_or_system_library_exception_reviewed": False,
                "decision": "verify actual wheel linkage and provide sources if applicable",
            })
        for lib in POSSIBLE_TRANSITIVE:
            candidates.append({
                "component": lib,
                "version_in_wheel_notices": None,
                "source_in_nine_archives": False,
                "compiled_linkage_confirmed": False,
                "source_obligation_or_system_library_exception_reviewed": False,
                "decision": "check AV1/TIFF transitive compiled implementation before deciding applicability",
            })

    without_sources = sorted(group for group in groups if not SOURCE_GROUPS[group])
    # These are *explicit* checks, never silently treated as source complete.
    review_items = [
        "Verify actual source/wheel build options and third-party patches for shipped Qt/PySide6/MuPDF.",
        "Verify each Pillow codec's binary linkage and applicable corresponding source, not just wheel LICENSE markers.",
        "Review AGPL System Library exclusions for CPython/OpenSSL/libffi individually; do not assume an exception.",
        "Preserve LGPL replacement/rebuild rights, notices, and exact tagged app source with public EXE.",
    ]
    return {
        "schema_version": 1,
        "source_git_commit": source_sha,
        "exe_sha256": exe_sha,
        "native_file_count": len(reported),
        "native_component_groups": sorted(groups),
        "native_members": reported,
        "sources_catalogued_from_verified_archives": sorted({
            name for group in groups for name in SOURCE_GROUPS[group]
        }),
        "component_groups_without_separate_source_archives": without_sources,
        "pillow_native_candidate_sources": candidates,
        "outstanding_source_checks": review_items,
        "exact_native_member_identity_checked": True,
        "pillow_wheel_license_markers_checked": bool("Pillow codecs" in groups),
        "complete_corresponding_source_verified": False,
        "legal_compliance_certified": False,
        "publication_decision": "HOLD: validate native transitive source correspondence and recipient rights",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--windows", required=True, type=Path)
    p.add_argument("--sources", required=True, type=Path)
    p.add_argument("--catalog", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--require-complete", action="store_true",
                   help="Return failure while corresponding-source completeness is unverified")
    args = p.parse_args()
    result = analyze(args.windows, args.sources, args.catalog)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print("Exact native members audited:", result["native_file_count"])
    print("Component groups without original source archive:",
          result["component_groups_without_separate_source_archives"])
    print("Pillow native/source review candidates:",
          len(result["pillow_native_candidate_sources"]))
    if args.require_complete and not result["complete_corresponding_source_verified"]:
        p.exit(2, "Corresponding-source review incomplete; publication must remain gated.\n")


if __name__ == "__main__":
    main()
