# Code signing policy — PDF Compressor

## Status

**SignPath Foundation application declined (14 November 2026).** The Foundation replied that the project does not yet demonstrate enough independent public recognition and community trust (such as GitHub stars, forks, contributors, independent coverage or sustained public engagement). The Foundation explicitly said this is **not an assessment of project quality or potential**, and invited a new application after greater public adoption. **No approval, certificate, or trusted signature has been granted.** The publicly available PDF Compressor releases v2.6.0, v2.7.0, and v2.7.1 are **unsigned**.

**Signing status:** No trusted code-signing provider is currently approved for this project. The **free** [SignPath Foundation](https://signpath.org/) route is unavailable following the declined application; it can be reconsidered only after stronger independent community signals and a new successful application. The maintainer does **not** plan to pay for a signing subscription.

## Source and project ownership

- Project: [PDF Compressor](https://github.com/Valik2005/pdf-compressor)
- Maintainer and source repository owner: [Valik2005](https://github.com/Valik2005)
- Author/committer: Valik2005; repository owner reviews external pull requests before they are merged.
- Signing approver: Valik2005. Every public signing request requires explicit manual approval. No undisclosed team members are asserted.
- License: [GNU AGPL-3.0](../LICENSE). Third-party libraries retain their own licensing obligations; see [DEPENDENCIES_AND_LICENSING.md](../DEPENDENCIES_AND_LICENSING.md).

## Privacy and security

The application processes users' PDF content locally on their computers. **It does not send PDF files, file content, or analytics to external services during PDF processing.** Users may explicitly use external links, GitHub downloads, or export reports. GitHub/SignPath would receive project build artifacts, not users' PDF files, only as part of the maintainer's separate code-signing process after approval.

The application does not require a user account or background network data collection. Local application preferences may be stored on the user's computer. This statement applies to the app's own behavior, not third-party websites opened at a user's request.

## Publication while unsigned

The existing releases are unsigned. **An unsigned v2.8 is a possible alternative, not yet an approved release.** It must be separately authorized by the maintainer **only after** the exact final build passes Windows tests, SHA-256 provenance/source checks and remaining third-party distribution-license requirements. Users must be told clearly that the EXE has no trusted Authenticode signature; SHA-256 proves integrity against the trusted published reference hash, **not publisher identity, malware safety or Microsoft SmartScreen reputation**. No unsigned build may use the signed-only workflow or claim the SignPath Foundation publisher.

The prepared v2.8 SignPath and signed-release workflows remain **dormant** unless a later application is accepted; no automation may publish in response to the denial.

## Signing and release rules (only if a future application is approved)

1. Build the official Windows EXE from reviewed source using the project's GitHub Actions on a protected release revision.
2. Verify source revision, test results, native dependencies, required notices and artifact integrity. Check the signature's trusted publisher and timestamp, and calculate SHA-256 **after signing**.
3. Keep internal testing-only branches (including `testing/2.8.1-automatic-test-report`) and all preview or experimental binaries **unsigned** and outside public releases.
4. Keep per-release approval in the maintainer's control. Never automatically publish or claim a build is signed before verified signing completes.
5. Publish the signed release only after license and compliance checks and express maintainer authorization. Preserve the existing public release layout (EXE, third-party source/license archive, SHA256SUMS.txt).
6. Should the application be declined, continue to state that published files are unsigned; do not substitute a self-signed certificate or a paid certificate.

Before installing a downloaded release, users can independently validate its published SHA-256. Once a SignPath-signed release actually exists, they can verify its **Digital Signatures** tab and publisher. A verified digital signature does not guarantee zero SmartScreen warnings.

## References

- [Public releases](https://github.com/Valik2005/pdf-compressor/releases)
- [SignPath Foundation eligibility and code signing rules](https://signpath.org/terms)
- [SignPath Foundation application](https://signpath.org/apply)
