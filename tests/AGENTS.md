# Tests

- Use uv and start with the affected test file or node ID. Test/setup commands and limitations are in [development.md](../docs/development/development.md).
- Read [shared fixtures](conftest.py) and any closer conftest before changing lifecycle or isolation. The shared conftest imports the real application even for collection.
- Qt tests use pytest-qt (`qtbot`, `qapp`). Keep process/Qt tests sequential as configured in [pytest.ini](../pytest.ini); preserve spawn semantics and explicit object/thread cleanup.
- The explicit `db` fixture is temporary and `settings` uses a random application name, but `qapp_cls` constructs the real [Application](../buzz/widgets/application.py), which opens the normal application database.
- [Widget fixtures](widgets/conftest.py) can clear default `Settings()`. Establish a disposable user/profile or equivalent isolation before broad GUI runs; offscreen rendering does not isolate data.
- Set `BUZZ_DISABLE_TELEMETRY=1` for local runs. Shared conftest already disables startup update checks; neither setting prevents model/network operations selected by tests.
- The suite mixes mocked tests, downloads and native inference. Inspect each selected test and reuse existing mocks; do not claim an entire directory is offline.
- Use the temporary path/DB/settings fixtures for new cases. Do not add new dependence on a developer's real database, keyring, models, microphone or network unless the case intentionally tests that integration.
- Do not put personal recordings in [testdata](../testdata): shared session cleanup removes newly created files there.
- `uv run make test CI=1` retains the full native/coverage gate while suppressing the Makefile's local lockfile upgrade. It is not a smoke test.
- Pair new behavior with a focused regression test. Reuse the existing widget, service, queue and backend test structure rather than creating a second harness.
