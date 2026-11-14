# Code signing policy — PDF Compressor

**Status (2026-11-14): application preparation; SignPath Foundation has NOT approved this project, no SignPath certificate or signed EXE is currently available.** Published v2.7.1 and current 2.8 previews are unsigned. This document is a policy, not a claim of existing code signing.

## Provider and verification

If the project is accepted: **Free code signing provided by [SignPath.io](https://signpath.io/), certificate by [SignPath Foundation](https://signpath.org/)**. The Authenticode publisher would be SignPath Foundation rather than the individual maintainer. SignPath Foundation decides whether a project is eligible and requires manual approval for each release.

- Repository and complete application source: https://github.com/Valik2005/pdf-compressor
- Only release-grade **PDF_Compressor_2_8.exe** built in this repository by GitHub-hosted GitHub Actions from reviewed source on **main** may be submitted.
- **Never sign** `testing/*`, `*.1-testing`, preview binaries, PR artifacts, local builds, or downloaded/unverified executables.
- The signing workflow is **manual-only**, does not create a public release, and fails if SignPath has not been configured.
- SignPath confirms origin using GitHub workflow artifact metadata; the result must pass Windows Authenticode validation, have a trusted timestamp, and receive a new **post-signature SHA-256**. The original unsigned SHA-256 will change when a signature is embedded.
- Distribute only the final signed binary after matching source/license verification and the maintainer's explicit release authorization. Keep the three-asset format: EXE, third-party source/license ZIP, SHA256SUMS.txt.
- If SignPath approval is declined or unavailable, do not claim a trusted signature. Do not buy a certificate or use a misleading self-signed certificate.

## Team roles and security

- Project maintainer, committer, reviewer, signing approver: GitHub **[Valik2005](https://github.com/Valik2005)**. Do not add unnamed contributors. Every external contribution must be reviewed by a maintainer before a signed build.
- The maintainer must enable multi-factor authentication for both GitHub and SignPath, review each release, and approve each SignPath signing request.
- Signing credentials are maintained by SignPath; API tokens are stored only as GitHub Actions secrets, never committed or printed. A project-specific GitHub App/organization configuration is required before enabling signing.

## Privacy and external services

PDF Compressor processes PDF data **locally**, with no document upload or background analytics. The user may explicitly open web pages or export reports; the program does not transmit PDF content during compression. GitHub Actions sends **program binaries and build metadata**, not users' PDF documents, to the SignPath signing service for the maintainer-approved signing process. See https://signpath.org/terms for the signing service's requirements.

## Verification for users

On Windows, open the final EXE's **Properties → Digital Signatures** tab or run `signtool verify /pa /tw /v PDF_Compressor_2_8.exe`. Compare the **signed** EXE's hash with `SHA256SUMS.txt` from the same GitHub Release. A valid signature confirms publisher association and integrity but **does not guarantee Microsoft SmartScreen will never warn**.

## Status and links

- Internal implementation guide: [FREE_CODE_SIGNING_PLAN.md](FREE_CODE_SIGNING_PLAN.md)
- Foundation application: https://signpath.org/apply
- Signing workflow: [../.github/workflows/sign-v2_8.yml](../.github/workflows/sign-v2_8.yml)
- Approved OSS projects and requirements: https://signpath.org/terms
