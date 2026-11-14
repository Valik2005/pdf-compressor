"""Synthetic, offline release-gate tests. No real certificate is simulated as valid."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

import pytest

from tools.assemble_signed_release_28 import assemble_signed_28, BUNDLE_NAME, EXE_NAME
from tools.assemble_patch_release import digest


def inputs(tmp_path: Path):
    sources = tmp_path / "sources"
    windows = tmp_path / "windows"
    catalog_path = tmp_path / "catalog.json"
    out = tmp_path / "final"
    sources.mkdir()
    windows.mkdir()
    sha = "b" * 40

    unsigned = b"STUB-UNSIGNED-PE" * 200
    signed = unsigned + b"STUB-FAKE-CERT"  # hash check only; never actual trust
    unsigned_sha = hashlib.sha256(unsigned).hexdigest()
    signed_file = windows / EXE_NAME
    signed_file.write_bytes(signed)
    signed_sha = digest(signed_file)
    (windows / "unsigned-build-manifest.json").write_text(json.dumps({
        "exe_name": EXE_NAME,
        "exe_sha256": unsigned_sha,
        "exe_size_bytes": len(unsigned),
        "source_git_commit": sha,
        "source_has_local_changes": False,
        "builder_os": "Windows", "builder_python": "3.14.10",
    }), encoding="utf-8")
    (windows / "unsigned-bundle-audit.json").write_text(json.dumps({
        "sha256": unsigned_sha,
        "included_virtual_keyboard_files": [],
    }), encoding="utf-8")
    (windows / "native-source-mapping.json").write_text(json.dumps({
        "exe_sha256": unsigned_sha, "native_file_count": 118,
        "unmapped_native_files": [], "missing_required_source_entries": [],
    }), encoding="utf-8")
    (windows / "signature-verification.json").write_text(json.dumps({
        "version": "2.8",
        "source_git_commit": sha,
        "authenticode_verified": True,
        "public_release_created": False,
        "signed_sha256": signed_sha,
        "signed_size_bytes": len(signed),
        "unsigned_sha256": unsigned_sha,
        "signer_subject": "CN=SignPath Foundation",
        "timestamp_certificate_subject": "CN=Trusted TSA",
    }), encoding="utf-8")
    (windows / "authenticode-verification.json").write_text(json.dumps({
        "signature_status": "Valid",
        "signtool_verified": True,
        "signed_sha256": signed_sha,
        "signer_subject": "CN=SignPath Foundation",
        "timestamper_subject": "CN=Trusted TSA",
    }), encoding="utf-8")

    with zipfile.ZipFile(windows / "license-evidence.zip", "w") as z:
        z.writestr("notice.txt", "Pretend audit")
        z.writestr("audit.json", "{}")
    entries = []
    for i in range(6):
        name = f"source{i}.tar.xz"
        file = sources / name
        file.write_bytes(f"source-file-{i}".encode() * 200)
        entries.append({"filename": name, "required": True,
                        "expected_sha256": digest(file)})
    catalog_path.write_text(json.dumps({"entries": entries}), encoding="utf-8")
    for name in ("LGPL_RELINKING_2_7.md", "THIRD_PARTY_NOTICES_2_7.md",
                 "libffi-LICENSE.txt"):
        (sources / name).write_text("Reviewed license text (fixture)", encoding="utf-8")
    with zipfile.ZipFile(sources / "THIRD_PARTY_NOTICES_2_7.zip", "w") as z:
        for i in range(70):
            z.writestr(f"license-{i}.txt", "Fixture")
    (sources / "source-archive-audit.json").write_text(json.dumps({
        "all_required_with_published_hashes": True,
    }), encoding="utf-8")
    (sources / "source-download-report.json").write_text(json.dumps({
        "all_required_archives_verified": True,
    }), encoding="utf-8")
    return sources, windows, catalog_path, out, sha


def test_three_signed_release_assets_and_postsign_hash(tmp_path):
    sources, windows, catalog, out, sha = inputs(tmp_path)
    info = assemble_signed_28(sources, windows, catalog, out, sha)
    assert info["source_archives"] == 6
    assert set(info["files"]) == {EXE_NAME, BUNDLE_NAME, "SHA256SUMS.txt"}
    checksum_lines = (out / "SHA256SUMS.txt").read_text().splitlines()
    assert len(checksum_lines) == 2
    assert checksum_lines[0] == f"{digest(out / EXE_NAME)}  {EXE_NAME}"
    assert checksum_lines[1] == f"{digest(out / BUNDLE_NAME)}  {BUNDLE_NAME}"
    with zipfile.ZipFile(out / BUNDLE_NAME) as z:
        assert z.testzip() is None
        assert len([x for x in z.namelist() if x.startswith("sources/")]) == 6
        assert "reports/authenticode-verification.json" in z.namelist()
        assert "reports/unsigned-build-manifest.json" in z.namelist()


@pytest.mark.parametrize("defect", [
    "unsigned_same_as_signed", "bad_proof_hash", "missing_timestamper",
    "source_sha_mismatch", "tampered_source", "missing_native_audit",
])
def test_bad_evidence_refuses_to_package(tmp_path, defect):
    sources, windows, catalog, out, sha = inputs(tmp_path)
    signing = windows / "signature-verification.json"
    data = json.loads(signing.read_text())
    if defect == "unsigned_same_as_signed":
        data["unsigned_sha256"] = data["signed_sha256"]
    elif defect == "bad_proof_hash":
        proof = windows / "authenticode-verification.json"
        p = json.loads(proof.read_text())
        p["signed_sha256"] = "0" * 64
        proof.write_text(json.dumps(p))
    elif defect == "missing_timestamper":
        data["timestamp_certificate_subject"] = ""
    elif defect == "source_sha_mismatch":
        data["source_git_commit"] = "c" * 40
    elif defect == "tampered_source":
        (sources / "source2.tar.xz").write_bytes(b"tampered")
    else:
        (windows / "native-source-mapping.json").unlink()
    signing.write_text(json.dumps(data))
    with pytest.raises((ValueError, FileNotFoundError)):
        assemble_signed_28(sources, windows, catalog, out, sha)
    assert not out.exists()
