"""Gather installed license-file evidence; NOT a redistribution-compliance certificate."""
from __future__ import annotations

import argparse
import hashlib
from importlib import metadata
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile

PACKAGES = ("PyMuPDF", "PySide6", "PySide6_Essentials", "PySide6_Addons", "shiboken6", "Pillow", "pyinstaller")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def notice_file(path: str) -> bool:
    p = PurePosixPath(path.replace("\\", "/"))
    if p.is_absolute() or ".." in p.parts:
        return False
    return any(p.name.lower().startswith(t) for t in ("license", "licence", "copying", "notice", "copyright"))


def collect(exe: Path, app_license: Path, manifest: Path | None, output: Path) -> dict:
    exe = exe.resolve(strict=True)
    digest = sha256_file(exe)
    if manifest is not None:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("exe_sha256", "").lower() != digest or data.get("exe_size_bytes") != exe.stat().st_size:
            raise ValueError("Build manifest does not match this EXE")
    report = {
        "exe_name": exe.name, "exe_sha256": digest, "exe_size_bytes": exe.stat().st_size,
        "packages": {}, "documents": [], "missing": [],
        "status": "INCOMPLETE EVIDENCE ONLY; NOT approved for redistribution",
        "mandatory_review": [
            "Inventory every Qt DLL/plugin, PDFium and all transitive native code in the final EXE.",
            "Provide corresponding library source, notices, and rights to relink/rebuild modified LGPL Qt.",
            "Review AGPL source/producer-notice requirements for PyMuPDF and other covered code.",
            "Verify Qt PDF/PDFium/Chromium/codec/OpenSSL third-party licenses individually."
        ],
    }
    collected = {}
    def add(name: str, content: bytes):
        if content and len(content) <= 2_000_000 and name not in collected:
            collected[name] = content
            report["documents"].append(name)
    if app_license.is_file():
        add("application/LICENSE", app_license.read_bytes())
    else:
        report["missing"].append("Repository LICENSE not found")
    for pkg in PACKAGES:
        record = {"version": None, "documents": 0}
        report["packages"][pkg] = record
        try:
            dist = metadata.distribution(pkg)
        except metadata.PackageNotFoundError:
            report["missing"].append(f"Not installed in builder: {pkg}")
            continue
        record["version"] = dist.version
        for f in dist.files or ():
            rel = str(f).replace("\\", "/")
            if not notice_file(rel):
                continue
            path = Path(dist.locate_file(f))
            if path.is_file() and not path.is_symlink() and path.stat().st_size <= 2_000_000:
                name = f"packages/{pkg}/{dist.version}/{rel}"
                add(name, path.read_bytes())
                if name in collected:
                    record["documents"] += 1
        if not record["documents"]:
            report["missing"].append(f"No local license-document files: {pkg} {dist.version}")
    python_lic = next((p for p in (Path(sys.base_prefix) / "LICENSE.txt", Path(sys.base_prefix) / "LICENSE") if p.is_file()), None)
    if python_lic:
        add("python-runtime/LICENSE.txt", python_lic.read_bytes())
    else:
        report["missing"].append("Python runtime LICENSE not found")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, contents in sorted(collected.items()):
            z.writestr(name, contents)
        z.writestr("README.txt", "INCOMPLETE evidence; verify full licenses, corresponding sources and Qt LGPL relinking rights before publishing.\n")
        z.writestr("evidence-report.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe", type=Path, required=True)
    p.add_argument("--manifest", type=Path)
    p.add_argument("--app-license", type=Path, default=Path("LICENSE"))
    p.add_argument("--out", type=Path, default=Path("dist/license-evidence-not-for-release.zip"))
    args = p.parse_args()
    try:
        report = collect(args.exe, args.app_license, args.manifest, args.out)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        p.exit(1, f"License evidence collection failed: {e}\n")
    print("EXE SHA-256:", report["exe_sha256"])
    print("Evidence files:", len(report["documents"]))
    print("Archive:", args.out)
    print("INCOMPLETE: this is not a license-compliance certificate.")


if __name__ == "__main__":
    main()
