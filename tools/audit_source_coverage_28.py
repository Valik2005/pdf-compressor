"""Cross-reference exact v2.8 native EXE members with distributed source evidence.

This report is intentionally *not* a proof of corresponding-source completeness.
A wheel RECORD proves native byte origin, not the sources of statically linked
libraries; text in a license file does not prove that source is bundled.
This script must run on the same GitHub Actions source/executable artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tarfile
import zipfile

from tools.audit_onefile_native_sources import component
from tools.fetch_supplemental_sources_28 import verify_prepared as verify_supplemental_sources
from tools.audit_pillow_wheel_sbom_28 import verify as verify_pillow_sbom

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
PILLOW_BUILD_KEYS = {
    "libavif": "libavif",
    "libjpeg-turbo": "jpegturbo",
    "libpng": "libpng",
    "libwebp": "libwebp",
    "openjpeg": "openjpeg",
    "tiff": "tiff",
    "freetype": "freetype",
    "lcms2": "lcms2",
    "harfbuzz": "harfbuzz",
    "brotli": "brotli",
    "zlib-ng": "zlib-ng",
}


# This is the exact *Git blob* of the official Pillow tag 12.3.0:
# https://github.com/python-pillow/Pillow/blob/bb1d8e8ab8d29048624d96e3ee53cecf7c13d13d/.github/dependencies.json
# GitHub content API returned this blob SHA for that tag.
PILLOW_UPSTREAM_DEPENDENCY_BLOB = "cc6e74fbac5f96fe795f653aa107bff4d9554c32"
PILLOW_UPSTREAM_DEPENDENCY_FILE = "PILLOW_12_3_0_BUILD_DEPENDENCIES.json"


def pillow_source_dependencies(source: Path) -> dict:
    """Verify the actual PyPI sdist and a tag-pinned upstream build catalog.

    Pillow's source distribution deliberately excludes .github/ from MANIFEST,
    while winbuild/build_prepare.py (included in the sdist) reads
    .github/dependencies.json from the *GitHub source checkout*. Therefore we
    preserve the separately authenticated original Git blob in this repo.
    """
    with tarfile.open(source, "r:gz") as tar:
        scripts = [
            member for member in tar.getmembers()
            if member.isfile() and member.name.endswith("/winbuild/build_prepare.py")
        ]
        if len(scripts) != 1 or scripts[0].size > 100_000:
            raise ValueError("Pillow sdist lacks Windows build dependency script")
        stream = tar.extractfile(scripts[0])
        if stream is None or b".github" not in stream.read():
            raise ValueError("Pillow sdist does not reference the upstream build catalog")

    original = (Path(__file__).resolve().parents[1] / "docs" / "third_party" /
                PILLOW_UPSTREAM_DEPENDENCY_FILE).read_bytes()
    # Windows Git checkout may transparently convert source-file LF to CRLF.
    # Git blob IDs are computed over committed LF bytes, not the worktree's
    # platform-specific line endings. Refuse stray CRs and normalize CRLF only.
    committed_bytes = original.replace(b"\r\n", b"\n")
    if b"\r" in committed_bytes:
        raise ValueError("Malformed Pillow upstream dependency manifest line endings")
    git_blob = hashlib.sha1(
        b"blob " + str(len(committed_bytes)).encode("ascii") + b"\0" + committed_bytes
    ).hexdigest()
    if git_blob != PILLOW_UPSTREAM_DEPENDENCY_BLOB:
        raise ValueError("Pillow build dependency manifest differs from tag 12.3.0 Git blob")
    result = json.loads(original.decode("utf-8"))
    if not isinstance(result, dict):
        raise ValueError("Pillow upstream build dependency catalog malformed")
    return result


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

    supplemental_groups = {}
    supplemental_verified_ids = set()
    if (sources / "supplemental-source-report.json").exists():
        supplement_catalog = (
            Path(__file__).resolve().parents[1] /
            "docs" / "supplemental-source-archives-2_8.json"
        )
        reviewed = verify_supplemental_sources(supplement_catalog, sources)
        verified_ids = {entry["id"] for entry in reviewed}
        supplemental_verified_ids = verified_ids
        supplements = {
            "Python runtime": "cpython-3.14.10",
            "OpenSSL": "openssl-3.5.9",
            "libffi": "libffi-3.4.4",
        }
        if not set(supplements.values()).issubset(verified_ids):
            raise ValueError("Incomplete verified CPython/OpenSSL/libffi source set")
        supplemental_groups = {
            group: (source_id,) for group, source_id in supplements.items()
        }
        # Correlate the *actual* CPython source package's Windows build script
        # with the OpenSSL/libffi versions, rather than guessing from DLL names.
        python_source = sources / "Python-3.14.10.tar.xz"
        with tarfile.open(python_source, "r:xz") as tar:
            scripts = [
                member for member in tar.getmembers()
                if member.isfile() and member.name.endswith("/PCbuild/get_externals.bat")
            ]
            if len(scripts) != 1 or scripts[0].size > 100_000:
                raise ValueError("CPython source lacks its Windows native dependency build pins")
            content = tar.extractfile(scripts[0])
            if content is None:
                raise ValueError("CPython Windows build dependency script cannot be read")
            pins = content.read().decode("utf-8", "replace").lower()
            if "libffi-3.4.4" not in pins or "openssl-3.5.9" not in pins:
                raise ValueError("CPython Windows source pins differ from packaged native sources")

    reported = []
    groups = set()
    for entry in entries:
        name = entry.get("path")
        group = entry.get("component")
        if (not isinstance(name, str) or name not in by_name
                or component(name) != group or group not in SOURCE_GROUPS):
            raise ValueError("Unmapped or misclassified native component: " + str(name))
        groups.add(group)
        core_sources = SOURCE_GROUPS[group]
        sources_for_group = core_sources + supplemental_groups.get(group, ())
        for source_id in core_sources:
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

    vendor_sbom = None
    if "Pillow codecs" in groups:
        if (windows / "pillow-wheel-sbom-evidence.json").is_file():
            vendor_sbom = verify_pillow_sbom(windows)
        elif os.environ.get("PDF28_REQUIRE_PILLOW_SBOM") == "1":
            raise ValueError("Missing required exact installed Pillow wheel SBOM")

    candidates = []
    if "Pillow codecs" in groups:
        evidence = windows / "license-evidence.zip"
        if not evidence.is_file():
            raise ValueError("Exact installed Pillow LICENSE ZIP absent")
        with zipfile.ZipFile(evidence) as archive:
            if PILLOW_LICENSE not in archive.namelist():
                raise ValueError("Exact Pillow wheel license absent")
            license_text = archive.read(PILLOW_LICENSE).decode("utf-8").lower()
        upstream = pillow_source_dependencies(sources / "pillow-12.3.0.tar.gz")
        for lib, version in sorted(PILLOW_CANDIDATES.items()):
            if upstream.get(PILLOW_BUILD_KEYS[lib]) != version:
                raise ValueError(
                    "Pillow upstream Windows build version disagrees with wheel: " + lib
                )
            marker = lib + "-" + version
            if marker not in license_text:
                raise ValueError("Missing installed Pillow wheel notice: " + marker)
            candidates.append({
                "component": lib,
                "version_in_wheel_notices": version,
                "version_matches_hash_verified_upstream_build_catalog": True,
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

    # All original source archives below were independently hash-verified
    # against official upstream release asset digests. This is source supply,
    # not proof of exact static linkage or binary-patch equivalence.
    additional_pillow_archives = {
        "libjpeg-turbo": "libjpeg-turbo-3.1.4.1",
        "harfbuzz": "harfbuzz-14.2.1",
    }
    for candidate in candidates:
        source_id = additional_pillow_archives.get(candidate["component"])
        candidate["supplemental_source_archive_id"] = (
            source_id if source_id in supplemental_verified_ids else None
        )
        candidate["supplemental_original_source_sha256_verified"] = bool(
            source_id and source_id in supplemental_verified_ids
        )

    # Version-locked wheel SBOM reflects official *candidate* edges for the
    # exact C extensions that PyInstaller actually packs. Its optional/excluded
    # scope does not prove linker membership; preserve that distinction.
    if vendor_sbom is not None:
        aliases = {
            "libavif": "libavif",
            "libjpeg-turbo": "libjpeg / libjpeg-turbo",
            "libwebp": "libwebp",
            "openjpeg": "OpenJPEG",
            "tiff": "libtiff",
            "freetype": "FreeType",
            "lcms2": "Little CMS 2",
            "harfbuzz": "HarfBuzz",
            "zlib-ng": "zlib",
            "libaom": None,
            "dav1d": None,
            "liblzma": None,
        }
        vendor_candidates = {
            x["name"].lower(): x
            for x in vendor_sbom["potential_native_dependencies_from_vendor_sbom"]
        }
        for candidate in candidates:
            key = aliases.get(candidate["component"], candidate["component"])
            hit = vendor_candidates.get(key.lower()) if key else None
            candidate["official_wheel_sbom_edge_for_packaged_extension"] = bool(hit)
            candidate["official_wheel_sbom_scope"] = (
                hit["supplier_sbom_scope"] if hit else "not enumerated or transitive"
            )
            candidate["official_wheel_sbom_establishes_static_linkage"] = False

    without_sources = sorted(group for group in groups
                             if not SOURCE_GROUPS[group] and group not in supplemental_groups)
    # These are *explicit* checks, never silently treated as source complete.
    review_items = [
        "Verify actual source/wheel build options and third-party patches for shipped Qt/PySide6/MuPDF.",
        "Verify each Pillow codec's binary linkage and applicable corresponding source, not just wheel LICENSE markers.",
        "Review AGPL System Library exclusions for CPython/OpenSSL/libffi individually; do not assume an exception. Full original sources are now bundled, but wheel-specific patches are not certified.",
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
            name for row in reported for name in row["upstream_source_archive_ids"]
        }),
        "supplemental_archives_independently_verified": len(supplemental_verified_ids),
        "component_groups_without_separate_source_archives": without_sources,
        "pillow_native_candidate_sources": candidates,
        "pillow_vendor_sbom_evidence": (
            {
                "original_record_sha256": vendor_sbom["sbom_sha256"],
                "record_sha256_verified": True,
                "native_extensions_matched": len(vendor_sbom["native_pillow_extensions"]),
                "potential_dependency_graph_count":
                    vendor_sbom["potential_native_dependency_count"],
                "dependency_graph_proves_actual_linkage": False,
            } if vendor_sbom is not None else None
        ),
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
