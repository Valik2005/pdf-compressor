# Experimental Windows one-file build for third-party bundle review.
# This is NOT a distribution-compliance certification.
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

pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name="PDF_Compressor_2_8_1_testing_NOT_FOR_RELEASE",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon="app_icon.ico",
)
