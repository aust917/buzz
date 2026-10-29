# Qt UI boundaries

- [Application](application.py) creates settings, DB/service, and
  [MainWindow](main_window.py). CLI also uses these classes and the Qt event
  loop; preserve `--hide-gui` and quit-on-complete behavior.
- Keep widgets and Qt SQL access on their owning thread. Slow plugin work uses
  [FnRunnable and the main-thread service proxy](../plugins/post_processing.py);
  avoid synchronous network/model work in GUI slots.
- Preserve `QObject` ownership and `quit`/`finished`/`deleteLater` cleanup when
  changing workers. [Recording widget](recording_transcriber_widget.py) and
  [MainWindow.closeEvent](main_window.py) contain shutdown-sensitive paths.
- Queue signals can arrive after cancellation. Task identity/activity checks in
  the [queue worker](../file_transcriber_queue_worker.py) protect later tasks;
  do not bypass them when reconnecting completion/progress handlers.
- Core user-facing strings use [_ from buzz.locale](../locale.py). Plugin UI
  strings may use the plugin's separate JSON localization mechanism.
- Use [assets.get_path](../assets.py) for shipped resources; cwd differs in
  packaged launches. Settings/preferences and keyring have separate ownership.
- Reuse [widget fixtures](../../tests/widgets/conftest.py) and Qt-aware fixtures
  in [tests/conftest.py](../../tests/conftest.py). Inspect fixture isolation before
  running tests: some settings fixtures clear the normal application settings.
- Find focused coverage under [tests/widgets](../../tests/widgets/). Queue changes
  also need [queue-worker tests](../../tests/transcriber/file_transcriber_queue_worker_test.py);
  CLI completion changes need [CLI tests](../../tests/cli_test.py).
