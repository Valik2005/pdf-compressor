"""Guard Qt Mesa/llvmpipe attribution for the exact v2.8 notice build."""
from pathlib import Path

from tools.package_release_notices import SOURCES
from tools.verify_presign_evidence_28 import NOTICES

ROOT = Path(__file__).resolve().parents[1]


def test_source_pack_includes_complete_upstream_boost_mit_license_texts():
    assert "LICENSES/BSL-1.0.txt" in SOURCES["qtbase-6.12.0-required"]
    assert "LICENSES/MIT.txt" in SOURCES["qtbase-6.12.0-required"]
    assert "components/qtbase-6.12.0-required/LICENSES/BSL-1.0.txt" in NOTICES
    assert "notices/QT_MESA_LLVMPIPE_ATTRIBUTION_2_8.txt" in NOTICES


def test_notice_pack_identifies_upstream_copyright_without_claiming_binary_certification():
    code = (ROOT / "tools/package_release_notices.py").read_text(encoding="utf-8")
    assert "Qt for Windows / Mesa llvmpipe software OpenGL fallback" in code
    assert "1999-2007 Brian Paul" in code
    assert "2013-2016 The Khronos Group" in code
    assert "yohhoy 2012" in code
    assert "Boost Software License 1.0" in code
    assert "Exact provenance, additional Mesa/LLVM notices" in code


def test_release_documentation_still_requires_specific_mesa_binary_evidence():
    notices = (ROOT / "docs/THIRD_PARTY_NOTICES_RELEASE_2_8.md").read_text(encoding="utf-8")
    assert "QT_MESA_LLVMPIPE_ATTRIBUTION_2_8.txt" in notices
    assert "does not establish complete Mesa attribution" in notices
    assert "full MIT and Boost Software License 1.0 texts" in notices
