"""Static policy checks for manual-only release pipelines. No SignPath credentials needed.

External signing trust and actual release publication are intentionally NOT tested here.
PyYAML is an isolated CI-checking dependency, not part of the distributed EXE.
"""
from __future__ import annotations
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def workflow(name: str) -> dict:
    value = yaml.load((ROOT / ".github/workflows" / name).read_text(encoding="utf-8"),
                      Loader=yaml.BaseLoader)
    if not isinstance(value, dict):
        raise AssertionError(f"Invalid workflow: {name}")
    return value


def check() -> None:
    signer = workflow("sign-v2_8.yml")
    publisher = workflow("publish-v2_8-signed.yml")
    unsigned_publisher = workflow("publish-v2_8-unsigned.yml")
    unsigned_review = workflow("review-28-final-unsigned.yml")
    metadata = workflow("review-28-metadata.yml")
    sources = workflow("source-28-preflight.yml")
    relink = workflow("review-28-relink.yml")

    assert list(signer["on"]) == ["workflow_dispatch"], "Signing must be opt-in only"
    assert list(publisher["on"]) == ["workflow_dispatch"], "Publication must be opt-in only"
    assert signer["permissions"] == {"contents": "read", "actions": "read"}
    assert publisher["permissions"] == {"contents": "read"}
    assert "contents" not in signer["jobs"]["sign-reviewed-main"].get("permissions", {})
    assert "main" in signer["jobs"]["sign-reviewed-main"]["if"]
    assert signer["jobs"]["sign-reviewed-main"]["needs"] == ["windows-tests", "sources-and-notices"]
    assert signer["jobs"]["package-three-files-for-review"]["needs"] == [
        "sources-and-notices", "sign-reviewed-main"
    ]
    assert publisher["jobs"]["publish-signed-28"]["permissions"] == {
        "contents": "write", "actions": "read"
    }
    assert "github.actor" in publisher["jobs"]["publish-signed-28"]["if"]
    assert "main" in publisher["jobs"]["publish-signed-28"]["if"]

    sign_steps = signer["jobs"]["sign-reviewed-main"]["steps"]
    submit = [step for step in sign_steps if
              step.get("uses", "").startswith("signpath/github-action-submit-signing-request@v3")]
    assert len(submit) == 1
    assert submit[0]["with"]["wait-for-completion"] == "true"
    assert int(submit[0]["with"]["wait-for-completion-timeout-in-seconds"]) >= 1200
    assert "github-artifact-id" in submit[0]["with"]
    assert submit[0]["with"]["artifact-configuration-slug"] == "${{ vars.SIGNPATH_ARTIFACT_CONFIGURATION_SLUG }}"
    assert "SIGNPATH_ARTIFACT_CONFIG" in str(sign_steps)
    assert "SIGNPATH_PROJECT" in str(sign_steps)
    signtext = (ROOT / ".github/workflows/sign-v2_8.yml").read_text(encoding="utf-8")
    publishtext = (ROOT / ".github/workflows/publish-v2_8-signed.yml").read_text(encoding="utf-8")
    assert "test_report.py" in signtext and 'APP_VERSION = "2.8"' in signtext
    assert "docs/source-archives-2_8.json" in signtext
    assert "THIRD_PARTY_NOTICES_2_8.zip" in signtext
    assert "tools.assemble_signed_release_28" in signtext
    assert "release_windows_2_8.spec" in signtext
    assert "PDF Compressor by Valik2005" in signtext
    assert "v2-8-exact-three-files-REVIEW-NOT-PUBLISHED" in signtext
    assert "RELEASE_V2_8_SIGNED" in publishtext
    assert "signed-run.json" in publishtext and "head_sha" in publishtext
    assert "signature-verification.json" in publishtext
    assert "sha256sum --check" in publishtext
    assert "gh release create v2.8" in publishtext
    assert "gh release edit v2.8 --draft=false --latest" in publishtext

    # Unsigned release is an entirely separate, owner-authorized release path.
    assert list(unsigned_publisher["on"]) == ["workflow_dispatch"]
    assert unsigned_publisher["permissions"] == {"contents": "read"}
    release_job = unsigned_publisher["jobs"]["publish-unsigned-28"]
    assert release_job["permissions"] == {"contents": "write", "actions": "read"}
    assert "github.actor == 'Valik2005'" in release_job["if"]
    assert "github.ref == 'refs/heads/main'" in release_job["if"]
    requirements = set(unsigned_publisher["on"]["workflow_dispatch"]["inputs"])
    assert requirements == {"acceptance_run_id", "release_confirmation", "license_confirmation"}
    unsigned_yaml = (ROOT / ".github/workflows/publish-v2_8-unsigned.yml").read_text(encoding="utf-8")
    review_yaml = (ROOT / ".github/workflows/review-28-final-unsigned.yml").read_text(encoding="utf-8")
    for phrase in (
        "RELEASE_V2_8_UNSIGNED", "LICENSE_OBLIGATIONS_REVIEWED",
        "NotSigned", "unsigned-authenticode-check.json",
        "license_compliance_certified", "source_git_commit",
        "head_sha", "sha256sum --check", "docs/RELEASE_NOTES_2_8_UNSIGNED.md",
        "v2-8-UNSIGNED-three-file-candidate-NOT-PUBLISHED"
    ):
        assert phrase in unsigned_yaml, f"Missing unsigned publishing gate: {phrase}"
    assert "signpath/github-action" not in unsigned_yaml.lower()
    assert "gh release create v2.8" in unsigned_yaml
    assert "gh release edit v2.8 --draft=false --latest" in unsigned_yaml
    assert unsigned_review["permissions"] == {"contents": "read"}
    jobs = unsigned_review["jobs"]
    assert jobs["stage-unsigned-three-files"]["needs"] == ["cross-verify-source-and-exe"]
    assert jobs["cross-verify-source-and-exe"]["needs"] == [
        "build-final-unsigned", "source-license-preflight"
    ]
    assert "Get-AuthenticodeSignature" in review_yaml
    assert "status = 'NotSigned'" in review_yaml
    assert "tools.assemble_unsigned_release_28" in review_yaml
    assert "v2-8-UNSIGNED-three-file-candidate-NOT-PUBLISHED" in review_yaml
    assert not any("gh release create" in str(job) for job in jobs.values())
    assert not any("signpath" in str(job).lower() for job in jobs.values())
    assert (ROOT / "tools/assemble_unsigned_release_28.py").is_file()

    for obj in (metadata, sources, relink):
        assert "publish" not in obj.get("jobs", {})
    print("Signed/unsigned workflows validated independently: owner-only release gates and exact artifacts.")


if __name__ == "__main__":
    check()
