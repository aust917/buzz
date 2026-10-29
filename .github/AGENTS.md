# Workflow changes

- Inspect the relevant workflow and [development notes](../docs/development/development.md) before copying commands. The Python manifest/pin uses 3.13; inherited workflow declarations still mention 3.12.
- [CI](workflows/ci.yml) tests/builds on three platforms and builds native wheels. Keep lightweight documentation checks independent of application installation, submodules, models and signing secrets.
- [Manual Build](workflows/manual-build.yml) still uses Poetry; reconcile it with the current uv manifest when repairing that workflow.
- Review both event triggers and job conditions. [CI](workflows/ci.yml) includes tag-triggered PyPI publishing and GitHub releases; [Snapcraft](workflows/snapcraft.yml) can publish edge/stable; [Pages](workflows/gh-pages.yml) deploys on main.
- Preserve the distinction between build/test and publication. Fork builds need their own identities, environments and credentials; do not enable publishing as a side effect of a test fix.
- The macOS bundle path needs signing/notarization credentials. Do not describe a local build or unsigned bundle as signed release validation.
- Review [Docusaurus configuration](../docs/docusaurus.config.js), packaging manifests and credential references together when changing release destinations.
- Keep workflow permissions and secrets limited to the jobs that need them. Untrusted pull request code must not gain release credentials.
- Report which platform/jobs were actually validated and any native/toolchain or credential gaps.
