# Fork maintenance

## Baseline and scope

- Fork: [aust917/buzz](https://github.com/aust917/buzz).
- Upstream: [chidiwilliams/buzz](https://github.com/chidiwilliams/buzz).
- Foundation reviewed on 2026-10-29 at upstream commit
  [298dbf003505cf945bdfd1eb8e705348b59a5b34](https://github.com/chidiwilliams/buzz/commit/298dbf003505cf945bdfd1eb8e705348b59a5b34).
- This foundation adds agent navigation, engineering references and a light
  documentation check. It keeps application behavior and package layout intact.
- Product features, branding and distribution targets for the fork have not
  been chosen. Do not infer them from the setup work.

The repository is MIT licensed; preserve [LICENSE](../../LICENSE) and attribution.
Existing installation links and badges in the inherited README describe upstream
distribution, not a new fork release.

## Repository layout decision

Keep `buzz/`, `tests/`, native submodules and packaging files in their existing
locations. Moving them for cosmetic organization would change imports, resource
lookup, build hooks and merge paths. Short task maps and scoped instructions
provide navigation without introducing that migration into an unmodified fork.

Revisit a boundary when an actual feature requires it. Record its motivation,
compatibility impact and validation next to the relevant development reference.
Do not add empty service layers, speculative skills or a product roadmap.

## Remotes and branches

For this checkout, `origin` is the fork, `upstream` is the original project,
and `remote.pushDefault` is `origin`. Confirm with `git remote -v` before pushing.
Use topic branches for changes; review the diff against the intended base.

For a fresh checkout:

```sh
git clone https://github.com/aust917/buzz.git
cd buzz
git remote add upstream https://github.com/chidiwilliams/buzz.git
git config remote.pushDefault origin
```

When synchronizing, start with a clean worktree, fetch upstream and review its
changes. A reviewable sync branch can be prepared with:

```sh
git fetch upstream
git switch -c chore/sync-upstream origin/main
git merge upstream/main
```

Resolve conflicts, run checks appropriate to the incoming changes and merge
through the fork's review process. Avoid rewriting shared history. After a
reviewed submodule pin change, use `git submodule update --init --recursive`;
do not use `--remote` to replace pinned revisions with dependency HEADs.

## Inherited automation and release identity

The initial fork inherits release configuration; it is not yet a separately
configured distributor. Inspect this table before enabling publication or
creating a release tag. The navigation workflow itself has read-only contents
permission and does not publish packages or run inference.

| Area | Current source / follow-up |
| --- | --- |
| Python mismatch | [pyproject.toml](../../pyproject.toml) and [.python-version](../../.python-version) require 3.13; inherited [CI](../../.github/workflows/ci.yml) still selects 3.12. Align and validate native builds in a separate change. |
| Heavy CI | [CI](../../.github/workflows/ci.yml) builds/tests three platforms; [Snapcraft](../../.github/workflows/snapcraft.yml) builds a snap. Documentation-only changes are filtered out of these workflows. |
| PyPI / GitHub releases | Tag jobs in [CI](../../.github/workflows/ci.yml) publish using inherited package/release conventions. Choose fork naming, credentials and signing before using them. |
| Snap Store | [Snapcraft](../../.github/workflows/snapcraft.yml) uploads main to edge and tags to stable when credentials exist; [snapcraft.yaml](../../snap/snapcraft.yaml) owns the package identity. |
| Pages | [Pages workflow](../../.github/workflows/gh-pages.yml) deploys main. [Docusaurus config](../docusaurus.config.js) still uses the upstream host/organization. |
| Manual builds | [manual-build.yml](../../.github/workflows/manual-build.yml) still references Poetry; it is not the canonical uv workflow. |
| Version / installers | Version is coordinated across [pyproject.toml](../../pyproject.toml), [Makefile](../../Makefile) and [__version__.py](../../buzz/__version__.py). [Buzz.spec](../../Buzz.spec), [installer.iss](../../installer.iss), [Flatpak](../../flatpak/) and [desktop metadata](../../share/) own packaging details. |

Path filters do not suppress tag-triggered workflows; release tags retain their
inherited publishing behavior. The navigation check runs on all pushes and pull
requests so source renames also reveal stale documentation links.

Use [development commands](development.md) for setup and validation. Keep
observed limitations here until they are fixed; do not turn them into claims
that the application has already been built or tested on this checkout.
