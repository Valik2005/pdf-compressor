"""Audit the REAL installed Pillow 12.3.0 Windows wheel's PEP 770 SBOM.

The supplier's CycloneDX SBOM lists build candidates, including optional and
excluded libraries. Its edges alone DO NOT prove static linkage into an EXE.
Preserve the RECORD-verified original SBOM, bind it to the selected exact
PyInstaller native inventory, and report potential dependencies honestly.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
from importlib import metadata
import json
from pathlib import Path
import shutil

PILLOW_TIFF_PATCH_GIT_BLOB = "e7a88cadcbfe21fef40386627b9473c80b183ddf"
PILLOW_TIFF_PATCH = (
    Path(__file__).resolve().parents[1] / "docs" / "third_party"
    / "PILLOW_TIFF_4_7_1_CVE_PATCH.patch"
)


def verify_libtiff_vendor_patch(sbom: dict) -> dict:
    """Check supplier SBOM's actual base64 patch against the original tag blob."""
    source = PILLOW_TIFF_PATCH.read_bytes().replace(b"\r\n", b"\n")
    if b"\r" in source:
        raise ValueError("Unexpected original Pillow TIFF patch line endings")
    git_blob = hashlib.sha1(
        b"blob " + str(len(source)).encode("ascii") + b"\0" + source
    ).hexdigest()
    if git_blob != PILLOW_TIFF_PATCH_GIT_BLOB:
        raise ValueError("Pillow TIFF security patch differs from official 12.3.0 tag")
    candidates = [x for x in sbom.get("components", [])
                  if x.get("bom-ref") == "pkg:generic/libtiff"
                  and x.get("name") == "libtiff"]
    if len(candidates) != 1:
        raise ValueError("Exact official Pillow libtiff component not found")
    patches = candidates[0].get("pedigree", {}).get("patches", [])
    found = []
    for patch in patches:
        wrapper = patch.get("diff", {}).get("text", {})
        if wrapper.get("encoding") != "base64":
            continue
        try:
            data = base64.b64decode(wrapper.get("content", ""), validate=True)
        except Exception as exc:
            raise ValueError("Invalid Pillow vendor SBOM patch data") from exc
        found.append(data)
    if source not in found:
        raise ValueError("Pillow SBOM libtiff patch differs from original tag source")
    return {"tag_git_blob": git_blob, "patch_sha256": sha256_bytes(source),
            "vendor_sbom_patch_matched": True}



def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("Expected JSON object: " + str(path))
    return value


def pillow_members(mapping: dict) -> list[str]:
    entries = mapping.get("native_component_mapping")
    if not isinstance(entries, list):
        raise ValueError("Native component mapping absent")
    result = sorted(e.get("path") for e in entries
                    if e.get("component") == "Pillow codecs")
    if not result or any(
        not isinstance(name, str) or not name.lower().startswith("pil/")
        or not name.lower().endswith(".pyd") for name in result
    ):
        raise ValueError("Expected exact packaged Pillow native modules")
    return result


def analyze_sbom(sbom: dict, native_paths: list[str]) -> dict:
    if (sbom.get("bomFormat") != "CycloneDX"
            or not str(sbom.get("specVersion", "")).startswith("1.")
            or sbom.get("metadata", {}).get("component", {}).get("name") != "Pillow"
            or sbom["metadata"]["component"].get("version") != "12.3.0"):
        raise ValueError("Not the Pillow 12.3.0 CycloneDX vendor SBOM")

    components = sbom.get("components")
    deps = sbom.get("dependencies")
    if not isinstance(components, list) or not isinstance(deps, list):
        raise ValueError("Malformed Pillow vendor dependency graph")
    by_ref = {}
    by_name = {}
    for part in components:
        if not isinstance(part, dict):
            raise ValueError("Malformed CycloneDX component")
        ref, name = part.get("bom-ref"), part.get("name")
        if (not isinstance(ref, str) or not ref or ref in by_ref
                or not isinstance(name, str) or not name):
            raise ValueError("Duplicated or malformed CycloneDX component")
        by_ref[ref] = part
        by_name.setdefault(name, []).append(ref)
    graph = {}
    for edge in deps:
        if (not isinstance(edge, dict) or not isinstance(edge.get("ref"), str)
                or not isinstance(edge.get("dependsOn"), list)
                or any(not isinstance(x, str) for x in edge["dependsOn"])):
            raise ValueError("Invalid SBOM dependency edge")
        if edge["ref"] in graph:
            raise ValueError("Duplicate SBOM dependency edge")
        graph[edge["ref"]] = edge["dependsOn"]

    module_rows = []
    potential = {}
    for path in native_paths:
        base = path.replace("\\", "/").rsplit("/", 1)[-1]
        module = "PIL." + base.split(".", 1)[0]
        refs = by_name.get(module, [])
        if len(refs) != 1:
            raise ValueError("Packaged Pillow extension not uniquely identified in vendor SBOM: " + path)
        ref = refs[0]
        module_rows.append({"native_member": path, "sbom_ref": ref})
        seen = set()
        pending = list(graph.get(ref, []))
        while pending:
            dep = pending.pop()
            if dep in seen:
                continue
            seen.add(dep)
            if dep not in by_ref:
                raise ValueError("Pillow vendor SBOM references unknown native component: " + dep)
            item = by_ref[dep]
            potential[dep] = item
            pending.extend(graph.get(dep, []))

    dependencies = []
    for ref, item in sorted(potential.items()):
        dependencies.append({
            "bom_ref": ref,
            "name": item["name"],
            "version": item.get("version"),
            "supplier_sbom_scope": item.get("scope", "unspecified"),
            "licenses": item.get("licenses", []),
            "supplier_patch_metadata_present": bool(item.get("pedigree", {}).get("patches")),
            "actual_static_linkage_proven": False,
        })
    return {
        "native_pillow_extensions": module_rows,
        "potential_native_dependencies_from_vendor_sbom": dependencies,
        "potential_native_dependency_count": len(dependencies),
        "supplier_sbom_is_wheel_specific_linker_manifest": False,
        "actual_static_linkage_confirmed": False,
    }


def capture(native_path: Path, manifest_path: Path,
            sbom_out: Path, report_out: Path) -> dict:
    native = read_json(native_path)
    manifest = read_json(manifest_path)
    if native.get("exe_sha256") != manifest.get("exe_sha256"):
        raise ValueError("Pillow SBOM audit native inventory differs from EXE manifest")
    exact_members = pillow_members(native)
    wheel = metadata.distribution("Pillow")
    if wheel.version != "12.3.0":
        raise ValueError("Installed Pillow does not match final pinned release")
    candidates = [file for file in (wheel.files or [])
                  if "/sboms/" in str(file).replace("\\", "/").lower()
                  and str(file).lower().endswith(".cdx.json")]
    if len(candidates) != 1:
        raise ValueError("Expected exactly one original PEP 770 Pillow wheel SBOM")
    entry = candidates[0]
    file = Path(wheel.locate_file(entry))
    if not file.is_file() or file.is_symlink():
        raise ValueError("Original Pillow SBOM is missing or symlinked")
    source = file.read_bytes()
    sha = sha256_bytes(source)
    record = entry.hash
    if record is None or record.mode != "sha256":
        raise ValueError("Pillow wheel SBOM not protected by PEP 376 RECORD SHA-256")
    official_sha = base64.urlsafe_b64decode(
        record.value + "=" * (-len(record.value) % 4)
    ).hex()
    if sha != official_sha:
        raise ValueError("Pillow vendor SBOM bytes differ from installed wheel RECORD")
    parsed = json.loads(source)
    assessed = analyze_sbom(parsed, exact_members)
    patch = verify_libtiff_vendor_patch(parsed)
    report = {
        "schema_version": 1,
        "source_git_commit": manifest.get("source_git_commit"),
        "exe_sha256": manifest["exe_sha256"],
        "pillow_version": wheel.version,
        "sbom_wheel_relative_path": str(entry).replace("\\", "/"),
        "sbom_sha256": sha,
        "sbom_matches_installed_wheel_record": True,
        "official_libtiff_patch_evidence": patch,
        **assessed,
        "corresponding_source_complete": False,
        "legal_compliance_certified": False,
    }
    sbom_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    sbom_out.write_bytes(source)
    report_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def verify(windows_dir: Path) -> dict:
    native = read_json(windows_dir / "native-source-mapping.json")
    manifest = read_json(windows_dir / "build-manifest.json")
    report = read_json(windows_dir / "pillow-wheel-sbom-evidence.json")
    source = (windows_dir / "pillow-wheel-sbom.cdx.json").read_bytes()
    if (report.get("schema_version") != 1
            or report.get("source_git_commit") != manifest.get("source_git_commit")
            or report.get("exe_sha256") != manifest.get("exe_sha256")
            or native.get("exe_sha256") != manifest.get("exe_sha256")
            or report.get("sbom_sha256") != sha256_bytes(source)
            or report.get("sbom_matches_installed_wheel_record") is not True
            or report.get("corresponding_source_complete") is not False
            or report.get("legal_compliance_certified") is not False):
        raise ValueError("Pillow wheel SBOM report/source/EXE identity mismatch")
    sbom = json.loads(source)
    expected = analyze_sbom(sbom, pillow_members(native))
    if report.get("official_libtiff_patch_evidence") != verify_libtiff_vendor_patch(sbom):
        raise ValueError("Pillow libtiff vendor security patch evidence mismatch")
    for key, value in expected.items():
        if report.get(key) != value:
            raise ValueError("Independent Pillow SBOM analysis does not match build report: " + key)
    if report.get("pillow_version") != "12.3.0":
        raise ValueError("Wrong Pillow SBOM version")
    return report


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--native", type=Path, required=True)
    cli.add_argument("--manifest", type=Path, required=True)
    cli.add_argument("--sbom-out", type=Path, required=True)
    cli.add_argument("--report-out", type=Path, required=True)
    args = cli.parse_args()
    report = capture(args.native, args.manifest, args.sbom_out, args.report_out)
    print("Preserved original RECORD-verified Pillow SBOM", report["sbom_sha256"])
    print("Shipped Pillow native modules:", len(report["native_pillow_extensions"]))
    print("Potential linked libraries (NOT verified linkage):",
          report["potential_native_dependency_count"])
    print("Actual packaged Pillow extensions:",
          [x["native_member"] for x in report["native_pillow_extensions"]])
    print("Supplier dependency graph (not actual native linkage):",
          [(x["name"], x["version"], x["supplier_sbom_scope"])
           for x in report["potential_native_dependencies_from_vendor_sbom"]])


if __name__ == "__main__":
    main()
