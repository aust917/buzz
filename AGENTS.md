# Working in Buzz

Buzz is a Python / PyQt6 desktop application and Qt-based CLI for transcription.
Keep changes compatible with the upstream layout; this fork's product direction
is not yet defined. [Fork maintenance](docs/development/fork.md) owns that context.

## Find the relevant context

Read the applicable nested `AGENTS.md` before editing an area, including when
your agent starts at the repository root. Load only the references needed for
the current task; do not read the entire documentation tree.

| Task | Start here |
| --- | --- |
| Locate implementation or tests; follow a task through the app | [Architecture map](docs/development/architecture.md) |
| Install, run, test, lint, or build | [Development commands](docs/development/development.md) |
| GUI, viewer, preferences, microphone UI | [Widget rules](buzz/widgets/AGENTS.md) |
| Backends, segment units, inference processes | [Transcriber rules](buzz/transcriber/AGENTS.md) |
| SQLite schema, history, DAO/service changes | [Database rules](buzz/db/AGENTS.md) |
| Plugin hooks, configuration, localization | [Plugin rules](buzz/plugins/AGENTS.md) |
| Test fixtures, Qt lifecycle, isolation | [Test rules](tests/AGENTS.md) |
| CI, packaging automation, publishing | [Workflow rules](.github/AGENTS.md) |
| Complex tasks, parallel work, context handoffs | [Agent workflow](docs/development/agent-workflow.md) |

The queue coordinator is [file_transcriber_queue_worker.py](buzz/file_transcriber_queue_worker.py),
outside `buzz/transcriber/`. Startup and CLI share [buzz.py](buzz/buzz.py).

## Commands and constraints

- Use `uv` for tests and Python scripts. Python is **3.13** according to
  [.python-version](.python-version) and [pyproject.toml](pyproject.toml);
  some inherited setup examples still say 3.12.
- For navigation/docs changes, run
  `uv run --no-project --python 3.13 python scripts/check_agent_docs.py`
  and `git diff --check`. This bypasses application installation/native builds.
- Once the development environment is prepared, run affected tests with
  `uv run pytest tests/<affected_path> --benchmark-skip`. Inspect relevant
  fixtures first: GUI tests can touch user settings/data; some tests download
  models or use external services. See the development guide for isolation.
- `make test` builds native dependencies and, outside CI, upgrades packages in
  `uv.lock`. Use `uv run make test CI=1` for the full gate without that upgrade.
  `make lint` rewrites files; use targeted `uv run ruff check <paths>` and
  `uv run ruff format --check <paths>` for read-only checks.
- Preserve CUDA setup/import ordering in `buzz/buzz.py`, lazy backend imports,
  Qt thread ownership, and cancellation cleanup when changing those flows.
- Keep generated binaries, compiled locales, caches and model weights out of
  changes. Dependencies are pinned by `uv.lock`; update it intentionally.

## Keep context small and useful

Use `rg --files buzz tests` and targeted `rg -n` searches. Avoid broad reads of
`uv.lock`, `docs/package-lock.json`, locale catalogs, media, assets, submodules,
`.venv/`, `build/`, and `dist/` unless the task concerns them.

Keep reusable constraints in the closest `AGENTS.md`; detailed explanations
belong in linked development docs. `CLAUDE.md` and Copilot instructions are
adapters to these rules. Update relevant links when moving code. Record only
durable decisions and actionable handoffs, not chat transcripts or tool logs.
Validate the requested change and report what ran, what passed, and any checks
that remain unverified.
