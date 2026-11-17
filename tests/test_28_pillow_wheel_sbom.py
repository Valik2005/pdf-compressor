"""The vendor Pillow 12.3.0 SBOM is useful evidence, not a linker map."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

import pytest

from tools.audit_pillow_wheel_sbom_28 import (
    analyze_sbom, capture, verify, pillow_members,
)


def fixture_sbom():
    import tools.audit_pillow_wheel_sbom_28 as evidence
    libtiff_patch = evidence.PILLOW_TIFF_PATCH.read_bytes().replace(b"\r\n", b"\n")
    root = "pkg:pypi/pillow@12.3.0"
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.7",
        "metadata": {"component": {"name": "Pillow", "version": "12.3.0"}},
        "components": [
            {"bom-ref": root + "#c-ext/PIL._imaging", "name": "PIL._imaging"},
            {"bom-ref": root + "#c-ext/PIL._avif", "name": "PIL._avif"},
            {"bom-ref": "pkg:generic/libtiff", "name": "libtiff",
             "version": "4.7.1", "pedigree": {
                 "patches": [{"type": "cherry-pick", "diff": {"text": {
                     "encoding": "base64",
                     "content": base64.b64encode(libtiff_patch).decode("ascii")
                 }}}]
             }},
            {"bom-ref": "pkg:generic/libjpeg", "name": "libjpeg / libjpeg-turbo",
             "version": "3.1.4.1"},
            {"bom-ref": "pkg:generic/libavif", "name": "libavif",
             "scope": "optional", "version": "1.4.2"},
            {"bom-ref": "pkg:generic/libimagequant", "name": "libimagequant",
             "scope": "excluded", "version": "4.4.1"},
        ],
        "dependencies": [
            {"ref": root + "#c-ext/PIL._imaging",
             "dependsOn": ["pkg:generic/libjpeg", "pkg:generic/libimagequant"]},
            {"ref": root + "#c-ext/PIL._avif",
             "dependsOn": ["pkg:generic/libavif"]},
        ],
    }


def test_maps_only_the_packaged_extension_candidates():
    r = analyze_sbom(fixture_sbom(), ["PIL/_imaging.cp314-win_amd64.pyd"])
    assert len(r["native_pillow_extensions"]) == 1
    found = {x["name"]: x for x in r["potential_native_dependencies_from_vendor_sbom"]}
    assert "libjpeg / libjpeg-turbo" in found
    assert "libavif" not in found
    assert found["libimagequant"]["supplier_sbom_scope"] == "excluded"
    assert all(x["actual_static_linkage_proven"] is False for x in found.values())


def test_optional_avif_does_not_assert_real_compiled_linkage():
    result = analyze_sbom(fixture_sbom(), ["PIL/_avif.pyd"])
    assert [x["name"] for x in result["potential_native_dependencies_from_vendor_sbom"]] == ["libavif"]
    assert result["actual_static_linkage_confirmed"] is False


@pytest.mark.parametrize("bad", [
    "wrong_version", "wrong_format", "missing_c_extension",
    "duplicate_dependency", "unknown_dependency", "duplicate_component",
])
def test_refuse_misidentified_vendor_component_data(bad):
    sbom = fixture_sbom()
    if bad == "wrong_version":
        sbom["metadata"]["component"]["version"] = "12.2.0"
    elif bad == "wrong_format":
        sbom["bomFormat"] = "fake"
    elif bad == "missing_c_extension":
        sbom["components"] = [x for x in sbom["components"] if x["name"] != "PIL._imaging"]
    elif bad == "duplicate_dependency":
        sbom["dependencies"].append(sbom["dependencies"][0].copy())
    elif bad == "unknown_dependency":
        sbom["dependencies"][0]["dependsOn"] = ["pkg:not-present/secret"]
    elif bad == "duplicate_component":
        sbom["components"].append(sbom["components"][0].copy())
    with pytest.raises(ValueError):
        analyze_sbom(sbom, ["PIL/_imaging.pyd"])


def test_wheel_record_hash_is_verified_and_original_sbom_preserved(tmp_path, monkeypatch):
    sbom_bytes = json.dumps(fixture_sbom()).encode("utf-8")
    digest = hashlib.sha256(sbom_bytes).digest()
    record_value = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    folder = tmp_path / "wheel"
    folder.mkdir()
    original = folder / "pillow-12.3.0.cdx.json"
    original.write_bytes(sbom_bytes)

    class Entry:
        def __str__(self):
            return "pillow-12.3.0.dist-info/sboms/pillow-12.3.0.cdx.json"

        hash = type("Hash", (), {"mode": "sha256", "value": record_value})()

    class FakeDist:
        version = "12.3.0"
        files = [Entry()]

        def locate_file(self, entry):
            return original

    import tools.audit_pillow_wheel_sbom_28 as lib
    monkeypatch.setattr(lib.metadata, "distribution", lambda name: FakeDist())

    manifest = tmp_path / "build-manifest.json"
    native = tmp_path / "native-source-mapping.json"
    commit = "b" * 40
    hash_exe = "c" * 64
    manifest.write_text(json.dumps({"source_git_commit": commit, "exe_sha256": hash_exe}))
    native.write_text(json.dumps({"exe_sha256": hash_exe, "native_component_mapping": [
        {"path": "PIL/_imaging.pyd", "component": "Pillow codecs"}
    ]}))
    out_sbom = tmp_path / "pillow-wheel-sbom.cdx.json"
    out_report = tmp_path / "pillow-wheel-sbom-evidence.json"
    report = capture(native, manifest, out_sbom, out_report)
    assert report["sbom_matches_installed_wheel_record"] is True
    assert out_sbom.read_bytes() == sbom_bytes
    assert verify(tmp_path) == report
    assert report["official_libtiff_patch_evidence"]["vendor_sbom_patch_matched"] is True

    out_sbom.write_bytes(sbom_bytes.replace(b"libjpeg", b"libbadg"))
    with pytest.raises(ValueError, match="mismatch"):
        verify(tmp_path)


def test_non_pillow_native_group_is_not_silently_counted():
    with pytest.raises(ValueError):
        pillow_members({"native_component_mapping": [
            {"path": "PIL/_imaging.pyd", "component": "QtBase"},
        ]})


def test_supplier_libtiff_patch_is_verified_against_original_tag():
    import tools.audit_pillow_wheel_sbom_28 as evidence
    result = evidence.verify_libtiff_vendor_patch(fixture_sbom())
    assert result["tag_git_blob"] == evidence.PILLOW_TIFF_PATCH_GIT_BLOB
    assert result["vendor_sbom_patch_matched"] is True


def test_supplier_patch_tampering_is_rejected():
    import tools.audit_pillow_wheel_sbom_28 as evidence
    sbom = fixture_sbom()
    patch = next(x for x in sbom["components"] if x["name"] == "libtiff")
    patch["pedigree"]["patches"][0]["diff"]["text"]["content"] = "aW52YWxpZA=="
    with pytest.raises(ValueError, match="differs"):
        evidence.verify_libtiff_vendor_patch(sbom)
