# Final Windows v2.8 UNSIGNED review candidate; publication is a separate owner-only gate.
# Build-source provenance is captured before EXE creation; not a license certification.
from PyInstaller.utils.hooks import collect_all

mupdf_data, mupdf_bins, mupdf_hidden = collect_all("pymupdf")
a = Analysis(
    ["app.pyw"],
    pathex=[],
    binaries=mupdf_bins,
    datas=mupdf_data + [("app_icon.ico", ".")],
    hiddenimports=mupdf_hidden + [
        "PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets"
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PySide6.QtVirtualKeyboard",
        "PySide6.QtPdf", "PySide6.QtPdfWidgets",
        "PySide6.QtQml", "PySide6.QtQuick",
        "PySide6.QtQuickWidgets", "PySide6.QtQuickControls2",
    ],
    noarchive=False,
)


# The application imports QtCore, QtGui and QtWidgets only. Qt PDF and
# QML/Quick are not used by this application; strip their *native* payloads
# as well as excluding the Python modules above. CI asserts their absence
# and verifies that the executable still starts on Windows.
def drop_unused_qt(destination):
    name = destination.replace(chr(92), "/").lower()
    basename = name.rsplit("/", 1)[-1]
    if basename == "qt6pdf.dll" or basename.startswith("qt6qml") and basename.endswith(".dll"):
        return True
    if basename.startswith("qt6quick") and basename.endswith(".dll"):
        return True
    if basename in ("qpdf.dll", "qpdfium.dll"):
        return True
    if "/pyside6/qt/qml/" in name or "/pyside6/qml/" in name:
        return True
    return False


def drop_virtual_keyboard(destination):
    name = destination.replace("\\", "/").lower()
    return (name.endswith("/qt6virtualkeyboard.dll") or
            name.endswith("/qtvirtualkeyboardplugin.dll") or
            "/qtquick/virtualkeyboard/" in name)


removed = [entry[0] for entry in a.binaries + a.datas if drop_virtual_keyboard(entry[0]) or drop_unused_qt(entry[0])]
a.binaries = [entry for entry in a.binaries if not (drop_virtual_keyboard(entry[0]) or drop_unused_qt(entry[0]))]
a.datas = [entry for entry in a.datas if not (drop_virtual_keyboard(entry[0]) or drop_unused_qt(entry[0]))]
print("Unused Qt PDF/QML/Quick and Virtual Keyboard items filtered:", removed)

# EXPERIMENT ONLY: Qt's optional OpenSSL TLS plugin causes PyInstaller
# to collect libssl-3-x64.dll and libcrypto-3-x64.dll from an unrelated
# installed MySQL Server on the Windows runner (confirmed exact source).
# PDF Compressor is local/offline and imports no QtNetwork itself.
# Python's own libssl-3.dll/libcrypto-3.dll and _ssl.pyd are NOT removed.
def remove_optional_qt_tls_openssl(destination):
    dest = destination.replace(chr(92), "/").lower()
    name = dest.rsplit("/", 1)[-1]
    return (name in ("libssl-3-x64.dll", "libcrypto-3-x64.dll") or
            dest.endswith("/plugins/tls/qopensslbackend.dll"))


openssl_removed = [entry[0] for entry in a.binaries + a.datas
                   if remove_optional_qt_tls_openssl(entry[0])]
if len(openssl_removed) != 3:
    raise RuntimeError(
        f"Expected exactly 3 optional MySQL OpenSSL/Qt TLS members; "
        f"found {len(openssl_removed)}; refuse to ship unreviewed supplier DLLs."
    )
a.binaries = [entry for entry in a.binaries
              if not remove_optional_qt_tls_openssl(entry[0])]
a.datas = [entry for entry in a.datas
           if not remove_optional_qt_tls_openssl(entry[0])]
print("EXPERIMENT: accidental MySQL OpenSSL and optional Qt TLS removed:", openssl_removed)

# EXPERIMENT ONLY — this changes the deployment contract:
# Windows 10/11 supplies the OS UCRT; the MSVC C++ Runtime must be
# independently installed (e.g. Microsoft's official x64 VC Redistributable).
# This is NOT a legal shortcut for redistributing the Microsoft-owned DLLs.
# The stable 2.8 EXE is intentionally unaffected.
MSVC_DLL_BASENAMES = {
    "vcruntime140.dll", "vcruntime140_1.dll",
    "msvcp140.dll", "msvcp140_1.dll", "msvcp140_2.dll",
}


def microsoft_runtime_group(destination):
    basename = destination.replace(chr(92), "/").rsplit("/", 1)[-1].lower()
    if basename == "ucrtbase.dll" or (
        basename.startswith("api-ms-win-") and basename.endswith(".dll")
    ):
        return "system-ucrt"
    if basename in MSVC_DLL_BASENAMES:
        return "vc-redistributable-prerequisite"
    return None


runtime_members = [(entry[0], microsoft_runtime_group(entry[0]))
                   for entry in a.binaries + a.datas]
ucrt_members = [name for name, group in runtime_members if group == "system-ucrt"]
msvc_members = [name for name, group in runtime_members
                if group == "vc-redistributable-prerequisite"]
if len(ucrt_members) != 43 or len(msvc_members) != 10:
    raise RuntimeError(
        "Expected 43 app-local UCRT/API-set entries and 10 MSVC DLLs, "
        f"got {len(ucrt_members)} and {len(msvc_members)}. "
        "Refusing to silently change the runtime deployment contract."
    )
a.binaries = [e for e in a.binaries if not microsoft_runtime_group(e[0])]
a.datas = [e for e in a.datas if not microsoft_runtime_group(e[0])]
print("EXPERIMENT: 43 OS-UCRT files excluded:", ucrt_members)
print("EXPERIMENT: 10 app-local MSVC runtime files excluded:", msvc_members)
print("EXPERIMENT: requires official system VC++ x64 runtime installed")

# Record EXACT original Windows collection paths and SHA-256 for native members.
# Report contains ONLY sanitized source scopes / package-relative paths.
# The downstream independent cross-audit compares each recorded source hash
# to the bytes actually extracted from this onefile executable.
import os
from pathlib import Path
from tools.audit_native_collection_sources_28 import capture
capture(a.binaries, a.datas, Path("dist/native-collection-sources.json"),
        source_sha=os.environ.get("GITHUB_SHA"))

pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name="PDF_Compressor_2_8",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    version="tools/windows_version_info_2_8.txt",
    icon="app_icon.ico",
)
