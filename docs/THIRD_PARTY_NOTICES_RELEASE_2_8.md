# Third-party attributions for PDF Compressor 2.8

This notice accompanies the **Windows single-EXE** distribution, not the historical preview builds. Component versions are pinned by `build-manifest.json`; the full combined bundle inventory and SHA-256 checksums are available in the release assets. The application is distributed under AGPL-3.0-only.

| Component | Bundled use / terms | Where to find terms & source |
| --- | --- | --- |
| PyMuPDF 1.27.2.3 / MuPDF 1.27.2 | Document reading and conversion; AGPLv3 or Artifex commercial terms | Complete AGPL application LICENSE, MuPDF `COPYING` in third-party notices ZIP; separately attached PyMuPDF + MuPDF sources |
| PySide6 / Shiboken 6.12.0 | Python bindings for Qt; LGPLv3/GPLv3/commercial alternatives | Full applicable LGPLv3/GPLv3 texts in third-party notices ZIP; separately attached PySide6/Shiboken source |
| QtBase, QtSvg, QtImageFormats 6.12.0 | Widgets/UI, icon and image plugins; LGPLv3/GPLv3 alternatives with bundled third-party code | Full LGPLv3/GPLv3 and third-party notices ZIP; separately attached QtBase/QtSvg/QtImageFormats sources |
| Pillow 12.3.0 | Imaging codecs; historical PIL license and third-party notices | Complete bundled `Pillow` LICENSE in `license-evidence.zip` from the exact Windows builder |
| Python 3.14 | Interpreter, C extensions and standard library; Python Software Foundation License | `python-runtime/LICENSE.txt` in the Windows `license-evidence.zip` |
| PyInstaller 6.22.3 | Single-EXE bootloader; GPL with bootloader exception | `pyinstaller.../COPYING.txt` in `license-evidence.zip` |
| OpenSSL 3.5.x | TLS cryptography used by Python and Qt, Apache 2.0 | The release source notice archive now includes **full original OpenSSL 3.5.9 LICENSE.txt and AUTHORS.md** from upstream tag `openssl-3.5.9` (separate from generic QtBase Apache text). Two embedded libcrypto DLLs report 3.5.9; **provenance of all four exact binary builds and possible other applicable notices are still under review**. https://openssl-library.org/source/license/ |
| Mesa software OpenGL fallback | `PySide6/opengl32sw.dll` from Qt for Windows; Mesa and LLVM components may use multiple permissive licenses | **Still pending for the exact bundled binary:** confirm upstream build provenance, included LLVM/Mesa parts and their applicable notices. The generic QtBase MIT text does not establish complete Mesa attribution. https://docs.mesa3d.org/license.html |
| libffi | `libffi-8.dll`; MIT-like license | Complete `libffi-LICENSE.txt` in `THIRD_PARTY_NOTICES_2_8.zip`; https://github.com/libffi/libffi/blob/master/LICENSE |
| Microsoft Visual C++ Runtime / UCRT | System and toolchain runtime DLLs | Redistribution subject to Microsoft software license terms: https://learn.microsoft.com/cpp/windows/redistributing-visual-cpp-files |

The release includes the `native-source-mapping.json` inventory, which classifies all embedded DLLs/PYDs and flags missing mapping categories. The *reviewed v2.8 unsigned candidate* had 118 native DLL/PYD entries including **53 Microsoft runtime** entries (42 API-set DLLs, 10 MSVCP/VCRUNTIME copies, 1 UCRTBase) and **4 OpenSSL** libraries; these must be reviewed individually, not assumed to be automatically redistributable. The inventory and source archive checksums are not proof of reproducible byte-for-byte source builds.

**Recipient rights:** The complete application source is available at this release tag. The separate Qt, PySide6 and MuPDF source archives are distributed as durable release assets. For instructions to rebuild a **single EXE** with replacement compatible Qt binaries, refer to `LGPL_RELINKING_2_8.md` and `tools/rebuild_onefile_with_qt.py`. Do not restrict users' rights to modify/relink/reverse-engineer Qt for debugging permitted modifications. AGPLv3 corresponding-source and output producer notices remain applicable.


## Specific to the v2.8 release

The unsigned v2.8 release must be audited against the **exact final EXE**. Its SHA-256 is computed after the final Windows build and must match the same-run native inventory, installed-package notices, version-pinned sources and cross-audit evidence. No code-signing key, publisher certificate or Authenticode verification is claimed. The published source tag is part of the corresponding-source offer.

The main application processes PDF content locally. The unsigned release is not sent to SignPath; it contains no signing credentials or users' PDF documents. Users can compare the published SHA-256, but a checksum is not a certificate of publisher identity.

**Compliance gate:** verification of six source archive hashes, license notices and Qt relinking instructions provides useful evidence but is not a legal conclusion about all upstream binary components, embedded codecs, supplier-specific notices, LGPL rights, or Microsoft redistributables. Unresolved obligations block release **whether signed or unsigned**.
