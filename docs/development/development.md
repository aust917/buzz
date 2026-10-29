# Development and verification

Read the section needed for the task. Commands below run from the repository root unless stated otherwise.

## Sources of truth

- Python: [`.python-version`](../../.python-version) and [`pyproject.toml`](../../pyproject.toml), currently Python 3.13 (`>=3.13,<3.14`).
- Dependencies and tool versions: [`pyproject.toml`](../../pyproject.toml) and [`uv.lock`](../../uv.lock). Use uv for Python commands and tests.
- Native targets and test coverage gate: [`Makefile`](../../Makefile).
- Package installation/build behavior: [`hatch_build.py`](../../hatch_build.py).
- Test behavior: [`pytest.ini`](../../pytest.ini), [`tests/conftest.py`](../../tests/conftest.py), and any closer fixtures.

## Prepare a source checkout

```sh
git submodule update --init --recursive
uv sync --locked
```

Install platform prerequisites before syncing. This is a substantial ML/native environment, not a lightweight Python-only install.

- All platforms: FFmpeg on PATH, Git, GNU Make, a C/C++ toolchain, and CMake.
- Windows: MSVC C++ build tools and Vulkan SDK. The Windows [CI recipe](../../.github/workflows/ci.yml) uses SDK 1.4.313.2 because whisper.cpp needs the SPIRV-Headers CMake package. Some Makefile recipes require Git Bash/POSIX tools; PowerShell alone does not implement them.
- Linux: Qt/X11, PortAudio, Vulkan and build libraries; use the dependency lists in [CONTRIBUTING](../../CONTRIBUTING.md) and the [CI recipe](../../.github/workflows/ci.yml) for the target distribution.
- macOS: the uv environment supports Apple Silicon; Intel macOS is excluded in `pyproject.toml`. See [CONTRIBUTING](../../CONTRIBUTING.md) for platform setup.

The [custom Hatch hook](../../hatch_build.py) builds whisper.cpp, compiles translation catalogs and patches/builds the CTC aligner during package builds. `uv sync` can trigger that work when installing the project. Native builds also download a VAD model. Installing only an interpreter does not prepare a runnable checkout.

If native artifacts need rebuilding after a source or submodule change:

```sh
uv run make buzz/whisper_cpp
uv run python scripts/build_ctc_forced_aligner.py
```

The [CTC build script](../../scripts/build_ctc_forced_aligner.py) applies files from [`patches/`](../../patches) to pinned submodules. Expected patch changes can make submodule worktrees dirty; do not reset or commit them blindly. `--force` rebuilds the extension even if its timestamp is current.

## Run the application

```sh
uv run buzz
uv run buzz --help
```

For development runs, disable launch telemetry and update requests before starting the process:

```powershell
$env:BUZZ_DISABLE_TELEMETRY = "1"
$env:BUZZ_DISABLE_UPDATE_CHECK = "1"
uv run buzz
```

The shell equivalent is `BUZZ_DISABLE_TELEMETRY=1 BUZZ_DISABLE_UPDATE_CHECK=1 uv run buzz` on POSIX systems. These flags do not disable backend model downloads or network features selected by the user.

## Choose verification by change

| Change | Starting verification |
| --- | --- |
| Agent instructions/navigation | Use the lightweight documentation check named in the root [AGENTS.md](../../AGENTS.md); no application install is needed. |
| Python behavior | Run the affected test file or node ID; inspect its fixtures and network/model usage first. |
| Qt widgets, settings or persistence | Read the isolation notes below, then use the relevant `tests/widgets/`, `tests/settings/` or `tests/db/` tests. |
| Backend/native integration | Prepare the backend artifacts and a small model, then run the matching integration tests. |
| Python style | Run Ruff on changed paths, with check-only flags below. |
| User documentation website | Follow the separate npm workflow below. |

Examples after the application environment is prepared:

```sh
uv run pytest tests/transcriber/file_transcriber_queue_worker_test.py --benchmark-skip
uv run pytest tests/plugins/loader_test.py --benchmark-skip
uv run ruff check buzz/path/to/changed_file.py
uv run ruff format --check buzz/path/to/changed_file.py
```

Replace the illustrative Ruff path with the actual changed files. [`Makefile`](../../Makefile) `lint` uses `--fix` and formatting, so it changes files. Do not run it as a read-only check or format the entire inherited codebase for an unrelated change.

For the full coverage target in a prepared, isolated environment:

```sh
uv run make test CI=1
```

`CI=1` suppresses the Makefile's local `uv lock --upgrade-package yt-dlp --upgrade-package certifi` step. Without it, `make test` can change the lockfile. This target still builds native prerequisites and runs the broad suite with a 70% coverage gate; it is not a cheap smoke test.

[`pytest.ini`](../../pytest.ini) stops on the first failure, disables xdist/pytest_parallel, and sets a 900-second timeout. Keep Qt/process tests sequential. A plain `pytest --collect-only` still imports the heavy shared fixtures.

## Test isolation and external effects

Read [`tests/conftest.py`](../../tests/conftest.py) and [`tests/widgets/conftest.py`](../../tests/widgets/conftest.py) before GUI work:

- The shared conftest imports the real [`Application`](../../buzz/widgets/application.py). Its `qapp_cls` uses that class, whose constructor opens the normal application database through [`setup_app_db`](../../buzz/db/db.py) and creates the main window.
- The explicit `db` fixture uses a temporary database and the explicit `settings` fixture uses a random application name. Those fixtures do not isolate every use of `Application` or `Settings()`.
- Widget `reset_settings` clears the default `Settings()`. Run broad GUI tests under a disposable OS user/profile, or establish equivalent isolation before running tests that use real defaults. `QT_QPA_PLATFORM=offscreen` changes display handling, not data isolation.
- Conftest disables startup update checks. Set `BUZZ_DISABLE_TELEMETRY=1` for local runs as the [CI workflow](../../.github/workflows/ci.yml) does.
- Session cleanup removes newly created files from [`testdata/`](../../testdata). Keep personal recordings and valuable outputs elsewhere.

The suite mixes mocked unit tests with actual downloads and inference. For example, [`model_loader_test.py`](../../tests/model_loader_test.py) downloads a Hugging Face model, [`whisper_cpp_test.py`](../../tests/transcriber/whisper_cpp_test.py) runs native transcription, and [`cli_test.py`](../../tests/cli_test.py) transcribes bundled audio. No global offline test marker currently separates these cases. Inspect the selected test rather than assuming an entire directory is offline.

For an intentional small model download:

```sh
uv run python scripts/download-models.py --model-type whispercpp --model-size tiny
```

[`download-models.py`](../../scripts/download-models.py) without filters downloads all standard sizes for all three supported downloader backends. `BUZZ_MODEL_ROOT` controls model storage; it does not redirect application settings or the transcript database.

## User documentation website

[`docs/`](..) is a separate Docusaurus application. Its [package manifest](../package.json) and [npm lockfile](../package-lock.json) own dependencies. The [Pages workflow](../../.github/workflows/gh-pages.yml) uses Node 22.

From `docs/`:

```sh
npm ci
npm run build
npm run typecheck
```

`npm ci` needs network access unless the dependencies are cached. This build checks the user website, not these internal development notes. Website content is under [`docs/docs/`](../docs); these notes live outside that autogenerated sidebar.

## Inherited discrepancies to watch

- README/CONTRIBUTING and workflow `setup-python` declarations still mention 3.12. Follow the Python manifest/pin; reconcile those recipes when changing build automation.
- [`manual-build.yml`](../../.github/workflows/manual-build.yml) still uses Poetry and a `poetry.lock` cache key, while the current project uses uv. It is not the canonical setup guide.
- The [website README](../README.md) describes Yarn, while CI uses npm and the committed lockfile is npm.
- Native build recipes retain some Python 3.12 paths and Intel macOS branches despite the current supported environments. Check the actual target platform before copying a command.
- Packaging, signing, publishing and Pages use upstream identities and credentials. Read the scoped [workflow instructions](../../.github/AGENTS.md) before modifying automation; a successful local test is not release validation.
