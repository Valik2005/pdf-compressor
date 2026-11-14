"""Synthetic unsigned v2.8 packaging tests; no real trust signature is forged."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import runpy
import zipfile

import pytest

from tools.assemble_unsigned_release_28 import (
    assemble_unsigned_28, EXE_NAME, BUNDLE_NAME,
)
from tools.verify_presign_evidence_28 import validate


def prepare(tmp_path: Path):
    source_test = Path(__file__).with_name("test_28_presign_evidence.py")
    make_fixture = runpy.run_path(str(source_test))["fixture"]
    windows, sources, catalog, commit = make_fixture(tmp_path)
    # Real installed-package evidence contains several documents; the shared
    # presign fixture needs a second record for the release packaging gate.
    with zipfile.ZipFile(windows / "license-evidence.zip", "a") as z:
        z.writestr("README-license.txt", "synthetic notice for ZIP completeness")
    evidence = tmp_path / "pre-sign-check.json"
    evidence.write_text(
        json.dumps(validate(windows, sources, catalog, commit)), encoding="utf-8"
    )
    exe = windows / EXE_NAME
    (windows / "unsigned-authenticode-check.json").write_text(
        json.dumps({
            "status": "NotSigned",
            "checked_on_windows": True,
            "source_git_commit": commit,
            "exe_sha256": hashlib.sha256(exe.read_bytes()).hexdigest(),
        }),
        encoding="utf-8",
    )
    return windows, sources, evidence, catalog, tmp_path / "release", commit


def test_unsigned_release_has_exact_three_assets_and_no_fake_signature(tmp_path):
    windows, sources, evidence, catalog, out, sha = prepare(tmp_path)
    info = assemble_unsigned_28(sources, windows, evidence, catalog, out, sha)
    assert info["signature"] == "NotSigned"
    assert info["license_compliance_certified"] is False
    assert info["release_authorized"] is False
    assert info["source_archives"] == 6
    assert set(info["files"]) == {EXE_NAME, BUNDLE_NAME, "SHA256SUMS.txt"}
    lines = (out / "SHA256SUMS.txt").read_text().splitlines()
    assert len(lines) == 2
    for name, line in [(EXE_NAME, lines[0]), (BUNDLE_NAME, lines[1])]:
        assert line == f"{hashlib.sha256((out / name).read_bytes()).hexdigest()}  {name}"
    with zipfile.ZipFile(out / BUNDLE_NAME) as z:
        assert z.testzip() is None
        names = set(z.namelist())
        assert len([x for x in names if x.startswith("sources/")]) == 6
        assert "licenses/LGPL_RELINKING_2_8.md" in names
        assert "licenses/THIRD_PARTY_NOTICES_2_8.zip" in names
        assert "reports/unsigned-authenticode-check.json" in names
        assert "reports/presign-technical-evidence.json" in names
        assert "reports/signature-verification.json" not in names
        assert "reports/authenticode-verification.json" not in names
        assert b"NO trusted" in z.read("README.txt")


@pytest.mark.parametrize("fault", [
    "tampered_exe", "altered_source", "altered_presign",
    "fake_signature", "wrong_windows_source", "missing_notice",
    "signed_evidence_intrusion", "staging_already_exists",
    "corrupt_native_inventory",
])
def test_reject_unverified_or_contaminated_release(tmp_path, fault):
    windows, sources, evidence, catalog, out, sha = prepare(tmp_path)
    if fault == "tampered_exe":
        (windows / EXE_NAME).write_bytes(b"tampered")
    elif fault == "altered_source":
        (sources / "test0.tar.gz").write_bytes(b"tampered")
    elif fault == "altered_presign":
        proof = json.loads(evidence.read_text())
        proof["source_git_commit"] = "0" * 40
        evidence.write_text(json.dumps(proof))
    elif fault == "fake_signature":
        check = windows / "unsigned-authenticode-check.json"
        proof = json.loads(check.read_text())
        proof["status"] = "Valid"
        check.write_text(json.dumps(proof))
    elif fault == "wrong_windows_source":
        check = windows / "unsigned-authenticode-check.json"
        proof = json.loads(check.read_text())
        proof["source_git_commit"] = "0" * 40
        check.write_text(json.dumps(proof))
    elif fault == "missing_notice":
        (sources / "THIRD_PARTY_NOTICES_2_8.zip").unlink()
    elif fault == "signed_evidence_intrusion":
        (windows / "signature-verification.json").write_text('{"fake":true}')
    elif fault == "staging_already_exists":
        out.mkdir()
    else:
        file = windows / "native-source-mapping.json"
        native = json.loads(file.read_text())
        native["unmapped_native_files"] = ["suspicious.dll"]
        file.write_text(json.dumps(native))
    with pytest.raises((ValueError, FileNotFoundError, KeyError, zipfile.BadZipFile)):
        assemble_unsigned_28(sources, windows, evidence, catalog, out, sha)
    if fault != "staging_already_exists":
        assert not out.exists()
