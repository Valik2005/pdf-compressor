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
    excludes=["PySide6.QtVirtualKeyboard"],
    noarchive=False,
)


def drop_virtual_keyboard(destination):
    name = destination.replace("\\", "/").lower()
    return (name.endswith("/qt6virtualkeyboard.dll") or
            name.endswith("/qtvirtualkeyboardplugin.dll") or
            "/qtquick/virtualkeyboard/" in name)


removed = [entry[0] for entry in a.binaries + a.datas if drop_virtual_keyboard(entry[0])]
a.binaries = [entry for entry in a.binaries if not drop_virtual_keyboard(entry[0])]
a.datas = [entry for entry in a.datas if not drop_virtual_keyboard(entry[0])]
print("Qt Virtual Keyboard items filtered:", removed)

pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name="PDF_Compressor_2_7_license_review",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon="app_icon.ico",
)
