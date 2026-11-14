# PDF Compressor 2.8 — Windows runtime redistribution review

**Scope:** Exact unsigned Windows x64 onefile v2.8 candidate. **Status: review incomplete; NOT authorization to publish.** Do not confuse ordinary system-library licensing exceptions in GPL/AGPL with Microsoft's separate permission to copy and redistribute Microsoft-owned DLL files.

## Observed runtime inventory

The project-wide native inventory currently groups **53** Windows runtime entries: **42** `api-ms-win-*.dll` API-set forwarders, **10** `MSVCP*/VCRUNTIME*` copies in the root, PySide6 and Shiboken folders, and **one** `ucrtbase.dll`. The inventory identifies *presence*, not the legal right to distribute any specific file. See `native-source-mapping.json` inside the 2.8 technical review ZIP.

## Actual SHA-256 origin audit

[Windows run #43628766396](https://github.com/Valik2005/pdf-compressor/actions/runs/43628766396) collected `native-binary-origin.json` from the exact unpacked EXE. **All ten** `MSVCP140`/`VCRUNTIME140` copies matched an installed **PySide6_Essentials 6.12.0**, **shiboken6 6.12.0**, or **CPython 3.14.10** binary byte-for-byte. The **42 API-set** compatibility DLLs and **ucrtbase.dll** did not match the limited wheel/CPython install-directory lookup and still require correct Windows system/SDK classification and redistribution rights. The report contains SHA-256 and package-relative paths only, not absolute Windows directories.

A matching runtime file is evidence of **binary origin**, not proof that the project owner satisfies Microsoft's distribution license. This rights check remains separate from the technical audit.

## Authoritative Microsoft licensing information

- [Redistribute Visual C++ Files — Microsoft Learn](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files): distributing runtime packages or individual DLLs is restricted to appropriately **licensed Visual Studio users**, subject to Microsoft Software License Terms and the corresponding **REDIST list**. App-local DLL distribution is technically supported, though Microsoft recommends central deployment so it can service the runtime independently.
- [Visual Studio licensing guidance](https://www.microsoft.com/licensing/guidance/Visual-Studio): qualifying **individual developers and open-source contributors** can use **Visual Studio Community at no charge**, subject to its license terms. This may resolve the eligibility of an individual developer without buying a paid IDE; it does *not* establish that the current project maintainer or GitHub builder has met all redistribution conditions.
- [Microsoft's license directory](https://visualstudio.microsoft.com/license-terms/): review the applicable IDE/Build Tools and MSVC runtime EULAs for the toolchain version, plus [Visual Studio redistribution lists](https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution).
- [Qt 6.12 Windows deployment](https://doc.qt.io/qt-6.12/windows-deployment.html) explicitly notes that Windows deployment may include Microsoft C/C++ runtimes and the optional software OpenGL renderer.

## Review required before public distribution

1. Record the **exact relative path and SHA-256** of each root/PySide6/Shiboken MSVC and UCRT binary from the final onefile archive, and determine whether it is copied from Windows, a redistributable package, the Python installer, the Qt Python wheels, or another dependency.
2. Check whether each non-API-set Microsoft runtime copy is among the **official REDIST files** and is distributed unmodified in a way permitted by the relevant license. Merely finding it inside an installed PySide6 wheel does not grant independent redistribution rights.
3. Confirm the maintainer's legal entitlement to distribute using the relevant **Visual Studio Community / Build Tools / redistributable license**, or obtain review by a qualified OSS licensing professional. No paid tooling is presumed required.
4. Verify applicable GPLv3/AGPLv3 **System Library** exception only for qualifying libraries; do not apply it automatically to all redistributed Microsoft DLLs.
5. If unpermitted DLL redistribution cannot be resolved, evaluate a separate dependency-on-VC-Redist build **with its own clean-Windows installation, GUI startup and PDF regression tests**. Do not strip runtime DLLs from the already tested EXE merely to make an audit checkbox green.

**Technical evidence available:** six upstream source hashes, complete unsigned release-candidate Windows test suite, native onefile inventory, and a three-file review bundle. The current GitHub Actions tests show the application works; they are **not a Microsoft redistribution license**. Final status remains *blocking for public v2.8 distribution until independently resolved*.
