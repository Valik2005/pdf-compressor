# PDF Compressor 2.7 — SmartFit (development preview)

**Offline PDF compression for Windows — open source, Russian and English.**

> **Development branch:** This branch contains PDF Compressor 2.7 development sources. A local preview EXE was built and launched on Windows 11 on 2026-11-08; redistribution clearance is still pending. The stable Windows EXE remains [PDF Compressor 2.6](https://github.com/Valik2005/pdf-compressor/releases/tag/v2.6.0). There is no official 2.7 GitHub Release yet.

## What is new

- SmartFit: automatically classifies PDF documents and selects a conservative target-size compression strategy.
- Optional reduction of image resolution, enabled only by the user.
- Shared-image safety improvements and bounded-resolution page previews.
- Clear messages when the requested file size is not achieved.

See [SmartFit 2.7 development notes](docs/SMARTFIT_2_7.md) for details and limitations.

## Run from source

Python 3.11+, Windows 10/11 (64-bit):

```powershell
python -m pip install -r requirements.txt
python app.pyw
```

Run tests:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

**No official executable is published for 2.7.** A preview EXE was built and smoke-tested locally, but the published stable version remains v2.6.0. See [BUILDING.md](BUILDING.md), [2.7 release checklist](docs/RELEASE_CHECKLIST_2_7.md) and [draft third-party notices](docs/THIRD_PARTY_NOTICES_2_7.md). The source license is [AGPL-3.0-only](https://github.com/Valik2005/pdf-compressor/blob/main/LICENSE); review [third-party licenses](https://github.com/Valik2005/pdf-compressor/blob/main/DEPENDENCIES_AND_LICENSING.md) before distributing a bundled build.
