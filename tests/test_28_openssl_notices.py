"""Preserve official OpenSSL 3.5.9 license/author notices without guessing DLL origin."""
import hashlib
from pathlib import Path

from tools.verify_presign_evidence_28 import NOTICES

ROOT = Path(__file__).resolve().parents[1]

UPSTREAM_GIT_BLOBS = {
    "OPENSSL_3_5_9_LICENSE.txt": "49cc83d2ee29d13453188217f0e4edd70c7f842f",
    "OPENSSL_3_5_9_AUTHORS.md": "5b036a0d8358167c87c7fa275cc671cd222dcce6",
}


def test_exact_original_openssl_license_and_author_blobs():
    # Exact contents were fetched from openssl/openssl tag openssl-3.5.9.
    # Git SHA-1 object identities are a source-content check, NOT a certificate
    # that the four bundled OpenSSL DLLs came from this source.
    for name, expected_blob in UPSTREAM_GIT_BLOBS.items():
        content = (ROOT / "docs" / "third_party" / name).read_bytes()
        blob = hashlib.sha1(f"blob {len(content)}\0".encode("ascii") + content).hexdigest()
        assert blob == expected_blob
    license_text = (ROOT / "docs/third_party/OPENSSL_3_5_9_LICENSE.txt").read_text(encoding="utf-8")
    assert "Apache License" in license_text
    assert "TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION" in license_text
    assert "OpenSSL" in (ROOT / "docs/third_party/OPENSSL_3_5_9_AUTHORS.md").read_text(encoding="utf-8")


def test_release_notice_manifest_requires_original_openssl_texts():
    assert "components/openssl-3.5.9/LICENSE.txt" in NOTICES
    assert "components/openssl-3.5.9/AUTHORS.md" in NOTICES
    script = (ROOT / "tools/package_release_notices.py").read_text(encoding="utf-8")
    assert 'if release_version == "2.8":' in script
    assert 'OPENSSL_3_5_9_LICENSE.txt' in script
    assert 'OPENSSL_3_5_9_AUTHORS.md' in script
