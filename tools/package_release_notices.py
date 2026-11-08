"""Package redistribution review notices from verified corresponding-source archives.

No binary published, no claim that every transitive obligation is satisfied.
All licenses are read *inside* upstream tar files without extracting paths.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile
import zipfile

SOURCES = {
    "qtbase-6.12.0-required": ["LICENSES/LGPL-3.0-only.txt", "LICENSES/GPL-3.0-only.txt"],
    "qtsvg-6.12.0": ["LICENSES/LGPL-3.0-only.txt", "LICENSES/GPL-3.0-only.txt"],
    "qtimageformats-6.12.0": ["LICENSES/LGPL-3.0-only.txt", "LICENSES/GPL-3.0-only.txt"],
    "qtforpython-6.12.0": [
        "LICENSES/LGPL-3.0-only.txt", "LICENSES/GPL-3.0-only.txt",
        "sources/pyside6/COPYING", "sources/shiboken6/COPYING",
        "sources/shiboken6/COPYING.libshiboken",
    ],
    "mupdf-1.27.2-native": ["COPYING", "docs/license.md"],
    "pymupdf-1.27.2.3": ["COPYING"],
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def make_pack(source_dir: Path, catalog: Path, project_license: Path, out: Path) -> dict:
    entries = json.loads(catalog.read_text(encoding="utf-8"))["entries"]
    selected = {e["id"]: e for e in entries if e["id"] in SOURCES}
    if set(selected) != set(SOURCES):
        raise ValueError("Missing required source entry in catalog")
    if not project_license.is_file():
        raise ValueError("Application AGPL LICENSE file missing")
    notices: dict[str, bytes] = {"app/AGPL-3.0/LICENSE": project_license.read_bytes()}
    download_report_path = source_dir / "source-download-report.json"
    download_report = json.loads(download_report_path.read_text(encoding="utf-8"))
    verified_upstream = {item["id"]: item for item in download_report["archives"]
                         if item.get("status") == "hash_matches_official_source"}
    provenance = []
    for component_id, paths in SOURCES.items():
        entry = selected[component_id]
        archive = source_dir / entry["filename"]
        reported = verified_upstream.get(component_id, {})
        expected = entry.get("expected_sha256") or reported.get("trusted_expected_sha256")
        if not archive.is_file() or not expected or (not entry.get("expected_sha256") and not entry.get("checksum_source")):
            raise ValueError(f"Source archive/official checksum missing: {component_id}")
        got = digest(archive)
        if got != expected.lower() or got != reported.get("downloaded_sha256"):
            raise ValueError(f"Source archive SHA-256 mismatch: {component_id}")
        if reported.get("trusted_expected_sha256") != got:
            raise ValueError(f"Source archive lacks matching upstream checksum: {component_id}")
        if got != expected.lower():
            raise ValueError(f"Source archive SHA-256 mismatch: {component_id}")
        provenance.append({"component": component_id, "archive": archive.name, "sha256": got})
        with tarfile.open(archive, "r:*") as tar:
            members = {m.name: m for m in tar.getmembers() if m.isfile()}
            root = next((m.name.split("/")[0] for m in members.values()), None)
            if not root:
                raise ValueError(f"Empty archive: {component_id}")
            for rel in paths:
                key = f"{root}/{rel}"
                member = members.get(key)
                if member is None or member.size > 512_000:
                    raise ValueError(f"Missing or unusually large license text: {component_id}/{rel}")
                f = tar.extractfile(member)
                if f is None:
                    raise ValueError(f"Cannot read license: {key}")
                notices[f"components/{component_id}/{rel}"] = f.read()
            # Include vendored third-party notice files where present.
            for member in members.values():
                rel = member.name.removeprefix(root + "/")
                if not (rel.startswith(("src/3rdparty/", "thirdparty/")) and
                        Path(rel).name.lower().startswith(("license", "copying", "notice", "copyright"))):
                    continue
                if member.size == 0 or member.size > 512_000:
                    continue
                file = tar.extractfile(member)
                if file is not None:
                    notices[f"components/{component_id}/{rel}"] = file.read()
    report = {
        "schema_version": 1, "matching_archive_hashes_verified": True,
        "licenses_extracted_from_verified_sources": sorted(notices),
        "source_archives": provenance,
        "full_binary_license_compliance_certified": False,
        "outstanding": [
            "Native component-to-source correspondence and transitive notices require final verification.",
            "Library relinking/recombination with genuinely modified Qt is not tested.",
            "Corresponding source and license texts must be permanently available alongside public EXE.",
        ],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(notices.items()):
            z.writestr(name, data)
        z.writestr("notice-manifest.json", json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        z.writestr("README.txt", (
            "PDF Compressor 2.7 review notices (NOT a legal-compliance certificate).\n"
            "Full upstream source archives are separate GitHub Actions artifacts and must\n"
            "be included permanently if a distributable executable is published.\n"
            "Rebuilding with modified Qt: docs/LGPL_RELINKING_2_7.md.\n"
        ))
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sources", type=Path, default=Path("dist/source-candidates"))
    p.add_argument("--catalog", type=Path, default=Path("docs/source-archives-2_7.json"))
    p.add_argument("--license", type=Path, default=Path("LICENSE"))
    p.add_argument("--out", type=Path, default=Path("dist/release-notices-review.zip"))
    args = p.parse_args()
    report = make_pack(args.sources, args.catalog, args.license, args.out)
    print("Source licenses extracted:", len(report["licenses_extracted_from_verified_sources"]))
    print("Source archive hashes checked:", len(report["source_archives"]))
    print("Prepared:", args.out)


if __name__ == "__main__":
    main()
