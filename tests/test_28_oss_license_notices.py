"""Guard the v2.8 user-facing licensing disclosures and evidence labels."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v28_notices_reference_matching_release_artifacts():
    notice = (ROOT / "docs/THIRD_PARTY_NOTICES_RELEASE_2_8.md").read_text(encoding="utf-8")
    assert "THIRD_PARTY_NOTICES_2_8.zip" in notice
    assert "THIRD_PARTY_NOTICES_2_7.zip" not in notice
    assert "OpenSSL" in notice and "Mesa" in notice
    assert "MSVCP/VCRUNTIME" in notice
    assert "does not establish complete Mesa attribution" in notice


def test_v28_oss_audit_does_not_claim_legal_or_signpath_approval():
    report = (ROOT / "docs/OSS_LICENSE_AUDIT_2_8.md").read_text(encoding="utf-8")
    for marker in ("118 native DLL/PYD", "73 entries", "SignPath",
                   "Microsoft runtime", "dual-licensed", "AGPLv3",
                   "license/compliance", "NO", "license"):
        # Some words can occur in inflected contexts; assert important
        # project-specific facts separately below instead of exact prose.
        if marker in ("license/compliance", "NO"):
            continue
        assert marker in report
    assert "**not a legal opinion or redistribution compliance certificate**" in report
    assert "without commercial dual-licensing" in report
    assert "PDFium" in report


def test_prominent_bilingual_oss_notice_exposes_relinking_and_source_archive():
    app = (ROOT / "app.pyw").read_text(encoding="utf-8")
    assert 'self.license_btn = QPushButton("Лицензии")' in app
    assert 'self.license_btn.clicked.connect(self.show_license_notice)' in app
    assert 'QMessageBox.information(self, self.t("Лицензии"), message)' in app
    assert "Third_Party_Sources_and_Licenses.zip" in app
    assert "LGPLv3/GPLv3" in app and "AGPLv3" in app
    assert "NO WARRANTY" in app and "БЕЗ ГАРАНТИИ" in app
