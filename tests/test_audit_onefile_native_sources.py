"""Guard onefile native source mapping from missing Qt modules and new payloads."""
from tools.audit_onefile_native_sources import component, audit


def test_native_component_examples():
    assert component("PySide6/Qt6Widgets.dll") == "QtBase"
    assert component("PySide6/Qt6Svg.dll") == "QtSvg"
    assert component("PySide6/plugins/imageformats/qwebp.dll") == "QtImageFormats"
    assert component("PySide6/plugins/imageformats/qjpeg.dll") == "QtBase"
    assert component("PySide6/opengl32sw.dll") == "Mesa OpenGL software rasterizer"
    assert component("pymupdf/mupdfcpp64.dll") == "MuPDF"
    assert component("pymupdf/_extra.pyd") == "PyMuPDF"
    assert component("PIL/_avif.cp314-win_amd64.pyd") == "Pillow codecs"
    assert component("libcrypto-3-x64.dll") == "OpenSSL"
    assert component("shiboken6/shiboken6.abi3.dll") == "PySide6/Shiboken"
    assert component("python314.dll") == "Python runtime"


def test_unexpected_qt_module_must_be_reviewed():
    assert component("PySide6/Qt6Pdf.dll") is None
    assert component("PySide6/plugins/imageformats/qpdf.dll") is None


def test_audit_fails_unknown_binary_and_unpinned_required_module():
    bundle = {"schema_version": 1, "sha256": "a" * 64, "exe_size_bytes": 123,
              "all_entries": [{"name": "PySide6/plugins/imageformats/qwebp.dll"},
                              {"name": "other/new_lib.dll"}]}
    result = audit(bundle, {"entries": []})
    assert "other/new_lib.dll" in result["unmapped_native_files"]
    assert "qtimageformats-6.12.0" in result["missing_required_source_entries"]


def test_audit_accepts_mapped_native_components_with_pins():
    entries = [{"id": n, "required": True} for n in (
        "qtbase-6.12.0-required", "qtsvg-6.12.0", "qtimageformats-6.12.0",
        "qtforpython-6.12.0", "mupdf-1.27.2-native", "pymupdf-1.27.2.3")]
    bundle = {"schema_version": 1, "sha256": "a" * 64, "exe_size_bytes": 123,
              "all_entries": [{"name": "PySide6/Qt6Widgets.dll"},
                              {"name": "PySide6/plugins/imageformats/qwebp.dll"},
                              {"name": "pymupdf/mupdfcpp64.dll"}]}
    result = audit(bundle, {"entries": entries})
    assert not result["unmapped_native_files"]
    assert not result["missing_required_source_entries"]
    assert not result["source_archive_hashes_match_exact_native_binary_provenance"]
