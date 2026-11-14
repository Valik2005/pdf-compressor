# PDF Compressor 2.8 — Windows runtime redistribution review

**Scope:** Exact unsigned Windows x64 onefile v2.8 candidate. **Status: review incomplete; NOT authorization to publish.** Do not confuse ordinary system-library licensing exceptions in GPL/AGPL with Microsoft's separate permission to copy and redistribute Microsoft-owned DLL files.

## Current editor is VS Code — not evidence of Visual Studio redistribution license

- [x] The maintainer reports using **Visual Studio Code (VS Code)** for Python development. This is a separate code editor; it is **not Visual Studio Community, Professional, Enterprise, or Visual Studio Build Tools**, and its license **does not grant Microsoft VC/REDIST redistribution rights**. See [Microsoft VS Code FAQ](https://code.visualstudio.com/docs/supporting/faq) and [Visual C++ redistribution terms](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files).
- [x] **No paid IDE or editor migration is necessary to keep developing** PDF Compressor. Building Python code in VS Code is compatible with using a correctly licensed Microsoft toolchain/redistributable when distribution is required. Eligibility for the free Community **individual** edition is possible, but **no installation, acceptance of Community/Build Tools terms, or license holding has been asserted**.
- [ ] Before distribution of current Windows EXE, independently establish an applicable license permitting these particular Microsoft MSVC/UCRT copies, and verify each redistributed file/source against Microsoft's conditions and REDIST list. Do not treat files copied from the CPython/PySide6/Shiboken wheels as automatically being from an authorized VS Redist directory.
- [ ] Alternative, if entitlement or file provenance cannot be established: independently install official Microsoft VC Runtime on the user's Windows from Microsoft and deliver a tested **runtime-dependent** edition that does not redistribute questionable DLLs. This would change system requirements and must pass real clean Windows 10/11 install, startup and PDF regression tests. **Do not silently remove DLLs from the verified 2.8 candidate.**

**Current status:** maintainer is an individual using VS Code; Microsoft redistribution permission is **not yet established** by either fact. Open-source Qt and MuPDF conditions are separate.

## License route for an independent developer (owner-confirmed 15 Nov 2026)

- [x] The project maintainer confirmed that PDF Compressor is released **personally as an individual developer, not on behalf of an organization**. This selects the individual-developer terms; it is **not** a declaration that a particular Visual Studio license or redistributable copy has been obtained or legally cleared.
- [x] Microsoft's [Visual Studio licensing guidance](https://www.microsoft.com/licensing/guidance/Visual-Studio) and [Community FAQ](https://visualstudio.microsoft.com/vs/pricing/) allow individuals to use Visual Studio Community for their own free **or paid** applications; a paid Visual Studio Professional/Enterprise subscription is **not required merely because the EXE is public or open-source**.
- [x] The [Visual Studio 2022 official REDIST list](https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution) explicitly covers **Community 2022** users who hold a valid license and permits the **unmodified listed** redistributable files under that edition's terms.
- [ ] Developer uses **VS Code**, not a claimed Visual Studio IDE. Determine whether they have **separate** valid Visual Studio Community/Build Tools licensing or another legally sufficient redistribution route. Do not imply VS Code supplies or requires a VS Community license. **Individual status alone does not grant REDIST rights**.
- [ ] Confirm which of the ten embedded MSVCP/VCRUNTIME files are redistributable under that valid license and identify their exact original package, hashes, version, architecture and location against the official REDIST list. Byte-identical Python/Qt wheel copies are valuable provenance but **not automatically** copies from a permitted Microsoft REDIST source.
- [ ] Keep the 43 UCRT/API-set cases separate. Microsoft's [Universal CRT deployment guidance](https://learn.microsoft.com/en-us/cpp/windows/universal-crt-deployment) states that Windows 10/11 **always use the OS UCRT**. Experimental [Windows Server 2022/2025 checks #43650037426](https://github.com/Valik2005/pdf-compressor/actions/runs/43650037426) passed with those 43 copies omitted, but that experimental branch was **not** merged into the v2.8 candidate; clean Windows 10/11 application/GUI/PDF tests are still needed before replacing the stable builder.

**Practical conclusion:** Do not buy a Visual Studio subscription solely for this review. First check the free individual Community license and exact Microsoft redistributable lists. Do not self-certify redistribution rights, silently substitute third-party binaries, strip the known-working release EXE, or publish without a final verified release manifest.

## Observed runtime inventory

The project-wide native inventory currently groups **53** Windows runtime entries: **42** `api-ms-win-*.dll` API-set forwarders, **10** `MSVCP*/VCRUNTIME*` copies in the root, PySide6 and Shiboken folders, and **one** `ucrtbase.dll`. The inventory identifies *presence*, not the legal right to distribute any specific file. See `native-source-mapping.json` inside the 2.8 technical review ZIP.

## Actual SHA-256 origin audit

[Windows run #43628766396](https://github.com/Valik2005/pdf-compressor/actions/runs/43628766396) collected `native-binary-origin.json` from the exact unpacked EXE. **All ten** `MSVCP140`/`VCRUNTIME140` copies matched an installed **PySide6_Essentials 6.12.0**, **shiboken6 6.12.0**, or **CPython 3.14.10** binary byte-for-byte. The **42 API-set** compatibility DLLs and **ucrtbase.dll** did not match the limited wheel/CPython install-directory lookup and still require correct Windows system/SDK classification and redistribution rights. The report contains SHA-256 and package-relative paths only, not absolute Windows directories.

A matching runtime file is evidence of **binary origin**, not proof that the project owner satisfies Microsoft's distribution license. This rights check remains separate from the technical audit.

## Exact ten MSVC runtime copies from reviewed candidate `b66ab014`

The following SHA-256 values were read from `native-collection-sources.json` inside the GitHub artifact's `Third_Party_Sources_and_Licenses.zip` produced by [six-job run #43651626694](https://github.com/Valik2005/pdf-compressor/actions/runs/43651626694). Every source byte hash was also checked against the embedded EXE member. **All filenames are non-Debug VCRUNTIME/MSVCP-family DLLs; their origin is Python/Qt distribution files, not a verified official Microsoft VC/Redist path.**

| Embedded filename | Actual collected file origin | SHA-256 |
| --- | --- | --- |
| `VCRUNTIME140.dll` | CPython installation | `d1f4225df2cd877dbf130d5668a021dce3f94118455ff5ec952061c30afc9ce7` |
| `VCRUNTIME140_1.dll` | CPython installation | `a7146c08f89fe5b04541ab507cdb59ff7b44534d4ba3c668a426c6450a03434e` |
| `PySide6/VCRUNTIME140.dll` | PySide6 Essentials 6.12.0 wheel | `a36e0cb185eb89533ed96d4568138f86a1315756a8b2644c5963a8ce23e32101` |
| `PySide6/VCRUNTIME140_1.dll` | PySide6 Essentials 6.12.0 wheel | `302b1e160e858602490a55e32ae2e29ddfc0bec2a188e19550cb655cdaa58f9c` |
| `PySide6/MSVCP140.dll` | PySide6 Essentials 6.12.0 wheel | `f6f1d55bfd64027820ddce48f9cd8cf46d53bfa34047e6acf4ef348d492a05cb` |
| `PySide6/MSVCP140_1.dll` | PySide6 Essentials 6.12.0 wheel | `2be87527c41e1ba8aff48e326e0adcd4743516e0bbcc9304986c726e27de6aca` |
| `PySide6/MSVCP140_2.dll` | PySide6 Essentials 6.12.0 wheel | `6a72ed8a87eae1671640bd1ca98eccb989f1772ae46ab84594e385bf6d4ac4fb` |
| `shiboken6/VCRUNTIME140.dll` | Shiboken6 6.12.0 wheel | `e7be9112ee9a5b9f44b44bff24cb761cca9b1ed7550b612f77b70edfcf5fdabf` |
| `shiboken6/VCRUNTIME140_1.dll` | Shiboken6 6.12.0 wheel | `f02cd4a862b85a9a3153d27e15e5a213f5df8e3d77004ed2e87b8a7e8873d97c` |
| `shiboken6/MSVCP140.dll` | Shiboken6 6.12.0 wheel | `1ba4d7c0a95d375da138a057a57593b33510ad5bda6c5e2686afd68faa5b4231` |

The [official VS 2022 REDIST list](https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution) permits licensed Community 2022 users to distribute eligible unmodified files from the Visual Studio VC redist tree; **filename family alone and a matching Qt/Python wheel RECORD do not establish that these particular copies are authorized Microsoft REDIST material**. A legal owner assertion cannot be fabricated from a CI pass.

## Authoritative Microsoft licensing information

- [Redistribute Visual C++ Files — Microsoft Learn](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files): distributing runtime packages or individual DLLs is restricted to appropriately **licensed Visual Studio users**, subject to Microsoft Software License Terms and the corresponding **REDIST list**. App-local DLL distribution is technically supported, though Microsoft recommends central deployment so it can service the runtime independently.
- [Visual Studio licensing guidance](https://www.microsoft.com/licensing/guidance/Visual-Studio): qualifying **individual developers and open-source contributors** can use **Visual Studio Community at no charge**, subject to its license terms. This may resolve the eligibility of an individual developer without buying a paid IDE; it does *not* establish that the current project maintainer or GitHub builder has met all redistribution conditions.
- [Microsoft's license directory](https://visualstudio.microsoft.com/license-terms/): review the applicable IDE/Build Tools and MSVC runtime EULAs for the toolchain version, plus [Visual Studio redistribution lists](https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution).
- [Qt 6.12 Windows deployment](https://doc.qt.io/qt-6.12/windows-deployment.html) explicitly notes that Windows deployment may include Microsoft C/C++ runtimes and the optional software OpenGL renderer.

## Official UCRT deployment vs actual redistribution permission

Microsoft's [UCRT deployment guidance](https://learn.microsoft.com/en-us/cpp/porting/upgrade-your-code-to-the-universal-crt) specifically names **`ucrtbase.dll` and `api-ms-win-*.dll`** as Windows SDK app-local UCRT deployable components. This explains why the candidate may contain 42 API-set forwarders and UCRT, but **does not independently authorize the maintainer to distribute a particular copy**: check the exact Windows SDK redist location, official license terms and original file identity. Microsoft's [VS 2022 REDIST list](https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution) explicitly conditions redistribution on valid Visual Studio licensing.

The 2.8 CI now captures `native-collection-sources.json` from PyInstaller Analysis and verifies the *actual collected original bytes* against the EXE. Inspect its sanitized source scopes for all 53 runtime entries and, especially, the previously unmatched 42 API-set forwarders and `ucrtbase.dll`. An `installed-wheel`, `windows-system` or `windows-sdk` label is an origin observation, not redistribution permission.

Avoid blindly deleting 43 UCRT/API-set payloads to avoid an open license question: this could break the standalone app on older supported Windows installations. A true dependency-on-installed-Windows-runtimes variant would require separate compatibility testing and explicit UX guidance.

## Review required before public distribution

1. Record the **exact relative path and SHA-256** of each root/PySide6/Shiboken MSVC and UCRT binary from the final onefile archive, and determine whether it is copied from Windows, a redistributable package, the Python installer, the Qt Python wheels, or another dependency.
2. Check whether each non-API-set Microsoft runtime copy is among the **official REDIST files** and is distributed unmodified in a way permitted by the relevant license. Merely finding it inside an installed PySide6 wheel does not grant independent redistribution rights.
3. Owner's **individual-developer status is confirmed**. Confirm the maintainer holds and complies with an applicable **free Visual Studio Community individual license** (or other valid license), and that the exact shipped Microsoft files qualify under the corresponding REDIST list. Record the license/version and evidence without exposing personal identifiers. Independent qualified licensing review is an alternative if unclear; no paid tooling is presumed required.
4. Verify applicable GPLv3/AGPLv3 **System Library** exception only for qualifying libraries; do not apply it automatically to all redistributed Microsoft DLLs.
5. If unpermitted DLL redistribution cannot be resolved, evaluate a separate dependency-on-VC-Redist build **with its own clean-Windows installation, GUI startup and PDF regression tests**. Do not strip runtime DLLs from the already tested EXE merely to make an audit checkbox green.

**Technical evidence available:** six upstream source hashes, complete unsigned release-candidate Windows test suite, native onefile inventory, and a three-file review bundle. The current GitHub Actions tests show the application works; they are **not a Microsoft redistribution license**. Final status remains *blocking for public v2.8 distribution until independently resolved*.
