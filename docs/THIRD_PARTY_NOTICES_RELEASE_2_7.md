# Third-party attributions for PDF Compressor 2.7

This notice accompanies the **Windows single-EXE** distribution, not the historical preview builds. Component versions are pinned by `build-manifest.json`; the full combined bundle inventory and SHA-256 checksums are available in the release assets. The application is distributed under AGPL-3.0-only.

| Component | Bundled use / terms | Where to find terms & source |
| --- | --- | --- |
| PyMuPDF 1.27.2.3 / MuPDF 1.27.2 | Document reading and conversion; AGPLv3 or Artifex commercial terms | Complete AGPL application LICENSE, MuPDF `COPYING` in third-party notices ZIP; separately attached PyMuPDF + MuPDF sources |
| PySide6 / Shiboken 6.12.0 | Python bindings for Qt; LGPLv3/GPLv3/commercial alternatives | Full applicable LGPLv3/GPLv3 texts in third-party notices ZIP; separately attached PySide6/Shiboken source |
| QtBase, QtSvg, QtImageFormats 6.12.0 | Widgets/UI, icon and image plugins; LGPLv3/GPLv3 alternatives with bundled third-party code | Full LGPLv3/GPLv3 and third-party notices ZIP; separately attached QtBase/QtSvg/QtImageFormats sources |
| Pillow 12.3.0 | Imaging codecs; historical PIL license and third-party notices | Complete bundled `Pillow` LICENSE in `license-evidence.zip` from the exact Windows builder |
| Python 3.14 | Interpreter, C extensions and standard library; Python Software Foundation License | `python-runtime/LICENSE.txt` in the Windows `license-evidence.zip` |
| PyInstaller 6.22.3 | Single-EXE bootloader; GPL with bootloader exception | `pyinstaller.../COPYING.txt` in `license-evidence.zip` |
| OpenSSL 3.x | TLS cryptography used by Python and Qt; Apache License 2.0 | `LICENSES/Apache-2.0.txt` from verified QtBase source in `THIRD_PARTY_NOTICES_2_7.zip`; https://openssl-library.org/source/license/ |
| Mesa software OpenGL fallback | `opengl32sw.dll` from Qt for Windows; Mesa components have MIT and other permissive licenses | MIT license text in `THIRD_PARTY_NOTICES_2_7.zip`, plus upstream license inventory https://docs.mesa3d.org/license.html. Copyrights vary by compiled component |
| libffi | `libffi-8.dll`; MIT-like license | Complete `libffi-LICENSE.txt` in `THIRD_PARTY_NOTICES_2_7.zip`; https://github.com/libffi/libffi/blob/master/LICENSE |
| Microsoft Visual C++ Runtime / UCRT | System and toolchain runtime DLLs | Redistribution subject to Microsoft software license terms: https://learn.microsoft.com/cpp/windows/redistributing-visual-cpp-files |

The release includes the `native-source-mapping.json` inventory, which classifies all embedded DLLs/PYDs and flags missing mapping categories. The inventory and source archive checksums are not proof of reproducible byte-for-byte source builds.

**Recipient rights:** The complete application source is available at this release tag. The separate Qt, PySide6 and MuPDF source archives are distributed as durable release assets. For instructions to rebuild a **single EXE** with replacement compatible Qt binaries, refer to `LGPL_RELINKING_2_7.md` and `tools/rebuild_onefile_with_qt.py`. Do not restrict users' rights to modify/relink/reverse-engineer Qt for debugging permitted modifications. AGPLv3 corresponding-source and output producer notices remain applicable.
