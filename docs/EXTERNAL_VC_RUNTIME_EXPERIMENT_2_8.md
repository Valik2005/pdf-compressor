# TEST ONLY: PDF Compressor 2.8 using Microsoft's installed VC++ Runtime

**This is not the v2.8 public release.** It is an alternative Windows 10/11 x64 packaging experiment for a private developer working in VS Code. Do **not** replace the stable release candidate or tag/publish this build without full consumer-Windows testing and a separate release/license decision.

## What is different

The normal unsigned v2.8 EXE currently contains 115 native DLL/PYD members, including 43 local UCRT/API-set and 10 app-local MSVC VCRUNTIME/MSVCP copies. This experiment **does not bundle those 53 Microsoft DLL files**. Windows 10/11 provides UCRT in the operating system; **the user must already have Microsoft's official Visual C++ Redistributable (x64)** to satisfy the other DLL dependencies. The experiment retains Qt, MuPDF, Python/OpenSSL and other needed native modules. No Microsoft redist installer is redistributed.

Microsoft official sources:

- [Universal CRT deployment](https://learn.microsoft.com/en-us/cpp/windows/universal-crt-deployment) — Windows 10/11 use the operating system's UCRT.
- [Visual C++ redistributable installation](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files) — centrally installed VC Runtime is Microsoft's recommended deployment model.
- [Latest supported VC++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) — download the **x64** installer only from Microsoft if a machine is missing it.

Removing DLLs from the EXE **does not create a Microsoft license**, and can make the program fail on clean Windows systems until the official package is installed. The GUI and native inventory were tested on hosted Windows Server 2022/2025. Those runners already have an x64 VC Runtime; they **cannot be used to claim that a default clean Windows 10/11 installation will work**.

## Manual consumer Windows 10/11 verification (without editing personal PDFs)

1. From the experiment's GitHub Actions run, download one of the **EXPERIMENT-runtime-prerequisite-...-NOT-FOR-RELEASE** artifacts and extract both `PDF_Compressor_2_8.exe` and its matching `runtime-experiment-manifest.json`. This is a test build, not an official release or authenticated publisher.
2. Keep the matching `tools/test_external_runtime_windows_28.ps1` from this exact branch and read it before running it. The script contains **no automatic downloads, installations, privilege elevation, uploads, network activity or accesses to your PDF files**.
3. From an ordinary PowerShell terminal inside the repo folder, run (adjust the EXE path):

```powershell
powershell -NoProfile -File .\tools\test_external_runtime_windows_28.ps1 -ExePath .\test-build\PDF_Compressor_2_8.exe -ManifestPath .\test-build\runtime-experiment-manifest.json -LaunchSmoke -ReportPath .\runtime-test.json
```

The script **requires the matching CI-generated 62-native manifest**, checks its exact source commit, EXE SHA-256, no bundled Microsoft runtime and unsigned test-only status. It then checks that the EXE is a version `2.8.0.0` unsigned build, checks for `vcruntime140.dll`, `vcruntime140_1.dll`, `msvcp140.dll` and `ucrtbase.dll` in Windows System32, and attempts a **12-second offscreen Qt startup using a sanitized PATH** (no Python, Qt or MySQL from the development machine). Its JSON report contains **no user name, device name, full local file paths, PDF text or PDF documents**. Its `gui_smoke_passed` field is a technical test, not a legal clearance.

If the runtime files are missing, **do not bypass the test**. Obtain and install the latest supported **Microsoft** VC++ x64 Redistributable manually from Microsoft's official site. Do not download individual DLLs from unknown sites. Rerun the check after installation.

4. Separately, launch the EXE normally and manually check PDF opening, compression quality, combining, extracting and rotating using **disposable copies of your own sample PDFs**. Report whether it worked on actual Windows 10 and Windows 11 clients with their exact OS build, and whether the Microsoft VC++ x64 Runtime needed to be installed first. Do not send any private PDFs.
5. Only if the consumer Windows checks pass can this variant be considered for replacing the normal portable EXE. At that point **update the 115-native acceptance baseline to 62**, rebuild all exact-source notices/metadata, rerun six-job cross-audit, verify the final source SHA and release asset hashes, and obtain the maintainer's separate permission **before merging into main and before publication**.

## Important licensing and compatibility constraints

- The source remains AGPL for PyMuPDF/MuPDF; Qt LGPL relinking and notices remain required, and the existing corresponding-source pack and producer-metadata policy still need independent review.
- Avoid modifying a working user's PDFs merely for testing or copyright notices.
- If the user has to install official Microsoft's VC++ runtime first, say so clearly on the download page; do not advertise this variant as completely standalone.
- There is no official digital signature. Users must verify the SHA-256 of a known-reviewed build. A checksum does not authenticate the developer's identity.
- All GitHub Actions evidence from hosted Windows Server versions is **supporting evidence, not proof of clean consumer Windows compatibility**.
