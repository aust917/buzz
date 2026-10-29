# Architecture and task routing

Use the row matching the requested behavior, then inspect that code and its tests.
The tables are entry points, not a required reading list. Paths and symbols in
source remain authoritative when implementation changes.

## Find the owner

| Change | Start here | Related tests |
| --- | --- | --- |
| Startup / platform initialization | [buzz.py](../../buzz/buzz.py), [Application](../../buzz/widgets/application.py) | [GUI startup](../../tests/gui_test.py) |
| CLI arguments / batch completion | [cli.py](../../buzz/cli.py), [MainWindow](../../buzz/widgets/main_window.py) | [CLI](../../tests/cli_test.py) |
| File queue / cancellation / URL preparation | [queue worker](../../buzz/file_transcriber_queue_worker.py), [file transcriber](../../buzz/transcriber/file_transcriber.py) | [queue worker](../../tests/transcriber/file_transcriber_queue_worker_test.py), [file transcriber](../../tests/transcriber/file_transcriber_test.py) |
| Task options / segment contract / output formats | [transcriber.py](../../buzz/transcriber/transcriber.py), [output writers](../../buzz/transcriber/file_transcriber.py) | [contracts](../../tests/transcriber/transcriber_test.py), [writers](../../tests/transcriber/file_transcriber_test.py) |
| Local Whisper / Faster Whisper | [WhisperFileTranscriber](../../buzz/transcriber/whisper_file_transcriber.py) | [local transcription](../../tests/transcriber/whisper_file_transcriber_test.py) |
| Whisper.cpp / local server | [whisper_cpp.py](../../buzz/transcriber/whisper_cpp.py), [local server](../../buzz/transcriber/local_whisper_cpp_server_transcriber.py) | [Whisper.cpp](../../tests/transcriber/whisper_cpp_test.py) |
| Hugging Face model families | [transformers_whisper.py](../../buzz/transformers_whisper.py), [model_loader.py](../../buzz/model_loader.py) | [backend](../../tests/transcriber/transformers_whisper_test.py), [model families](../../tests/transformers_transcriber_test.py) |
| OpenAI-compatible transcription API | [API transcriber](../../buzz/transcriber/openai_whisper_api_file_transcriber.py) | [API transcriber](../../tests/transcriber/openai_whisper_api_file_transcriber_test.py) |
| Model discovery / download / custom paths | [model_loader.py](../../buzz/model_loader.py), [custom models](../../buzz/settings/whisper_cpp_custom_models.py) | [model loader](../../tests/model_loader_test.py), [custom models](../../tests/settings/whisper_cpp_custom_models_test.py) |
| Microphone / live transcription | [recording widget](../../buzz/widgets/recording_transcriber_widget.py), [recording transcriber](../../buzz/transcriber/recording_transcriber.py), [audio capture](../../buzz/recording.py) | [widget](../../tests/widgets/recording_transcriber_widget_test.py), [transcriber](../../tests/transcriber/recording_transcriber_test.py), [capture](../../tests/recording_test.py) |
| Transcript editing / playback / translation | [viewer](../../buzz/widgets/transcription_viewer/), [translator](../../buzz/translator.py) | [viewer](../../tests/widgets/transcription_viewer/), [translation](../../tests/translator_test.py) |
| Speaker identification | [transcriber adapter](../../buzz/transcriber/speaker_identifier.py), [implementation](../../buzz/widgets/transcription_viewer/speaker_identification_widget.py) | [adapter](../../tests/transcriber/speaker_identifier_test.py), [end to end](../../tests/speaker_identification_e2e_test.py) |
| Folder watching / import settling | [folder watcher](../../buzz/widgets/transcription_task_folder_watcher.py), [MainWindow](../../buzz/widgets/main_window.py) | [folder watcher](../../tests/widgets/transcription_task_folder_watcher_test.py) |
| Queue activity / sleep inhibition | [sleep_inhibitor.py](../../buzz/sleep_inhibitor.py), [queue worker](../../buzz/file_transcriber_queue_worker.py) | [sleep inhibitor](../../tests/sleep_inhibitor_test.py), [queue worker](../../tests/transcriber/file_transcriber_queue_worker_test.py) |
| History / schema / persistence | [schema.sql](../../buzz/schema.sql), [database](../../buzz/db/db.py), [service](../../buzz/db/service/transcription_service.py), [DAOs](../../buzz/db/dao/) | [database tests](../../tests/db/) |
| Settings / preferences / secrets | [settings](../../buzz/settings/settings.py), [preferences](../../buzz/widgets/preferences_dialog/), [keyring](../../buzz/store/keyring_store.py) | [settings](../../tests/settings/), [preferences](../../tests/widgets/preferences_dialog/), [keyring](../../tests/store/keyring_store_test.py) |
| Plugins / hooks / bundled plugins | [plugin instructions](../../buzz/plugins/AGENTS.md), [contract](../../buzz/plugins/base.py), [manager](../../buzz/plugins/manager.py), [loader](../../buzz/plugins/loader.py) | [plugin system](../../tests/plugins/), [management UI](../../tests/widgets/plugins_dialog/) |
| Core UI translations | [locale.py](../../buzz/locale.py), [gettext catalogs](../../buzz/locale/), translation targets in [Makefile](../../Makefile) | Exercise affected UI in the selected locale |
| CUDA / packaged runtime / DLL loading | [cuda_setup.py](../../buzz/cuda_setup.py), [cuda_manager.py](../../buzz/cuda_manager.py), [assets.py](../../buzz/assets.py) | [CUDA setup](../../tests/cuda_setup_test.py), [CUDA manager](../../tests/cuda_manager_test.py) |
| Native builds / desktop distributions | [Makefile](../../Makefile), [hatch_build.py](../../hatch_build.py), [Buzz.spec](../../Buzz.spec), [CI](../../.github/workflows/ci.yml) | Follow the relevant platform build job |
| User documentation website | [Docusaurus package](../package.json), [site content](../docs/), [site README](../README.md) | Website build defined in [package.json](../package.json) |

## Startup and execution boundaries

The `buzz` console script in [pyproject.toml](../../pyproject.toml),
[`python -m buzz`](../../buzz/__main__.py), and [main.py](../../main.py) all call
`buzz.buzz.main()`. It initializes platform behavior, creates `Application`, parses
CLI arguments, and runs the Qt event loop. `--hide-gui` still uses Qt.

`buzz.buzz` imports CUDA setup before modules that may import torch. It also
configures Windows DLL paths, Hugging Face cache paths, multiprocessing
`freeze_support()`, and Linux's `spawn` start method. Preserve those ordering
constraints when changing startup or imports.

`Application` creates settings, the SQLite connection, DAOs, the transcription
service, and `MainWindow`. Opening it can write to the user's database/settings,
initialize plugins, and contact telemetry/update services. A GUI launch is not a
read-only inspection step.

## File transcription lifecycle

1. GUI import, folder watching, and CLI construct `FileTranscriptionTask` values.
   `MainWindow.add_task()` creates the history entry and queues the task.
2. `FileTranscriberQueueWorker` lives on a `QThread` and uses a Python
   `queue.Queue`. URL tasks download audio before other processing.
3. The worker optionally extracts speech, then runs plugin
   `before_transcription` and `check_skip` hooks. A skip returns existing segments
   without running a transcription backend.
4. A per-task transcriber runs on its own `QThread`. Local Whisper backends also
   use a `multiprocessing.Process`; [ConnWriter](../../buzz/conn.py) transports
   stderr/progress/results over a pipe. API transcription has a separate class.
5. Completion reaches `MainWindow.on_task_completed()`. With post hooks, the
   pipeline is `after_transcription` -> persist -> `on_complete`; otherwise the
   service persists directly. GUI post hooks use a thread pool, while CLI
   quit-on-complete runs them synchronously before exiting.

Cancellation and shutdown must stop child processes, close pipes, release
`TaskActivity`, clean temporary speech files, and finish Qt objects on the right
thread. URL downloads can emit late signals after cancellation; the queue checks
task identity and activity tokens to reject obsolete callbacks. Preserve these
checks when changing task handoff or retry behavior.

`Segment.start` and `Segment.end` are **milliseconds**. Backend timestamps often
need conversion from seconds. Segments also carry translation, speaker, and
metadata. Tasks snapshot transcription options so later UI changes cannot mutate
queued work. Original media paths and temporary speech paths serve different
purposes; persisted playback paths must survive temporary-file cleanup.

## Persistence, settings, and plugins

- `buzz/schema.sql` declares the desired SQLite schema. `db/helpers.py` applies
  it through the declarative migrator, imports legacy JSON history, and marks
  interrupted queued/running tasks canceled at startup. There is no numbered
  migration directory; verify existing-data preservation when changing schema.
- Qt SQL connections are thread-affine. GUI slots and the service own normal DB
  access. Plugin background hooks use `MainThreadServiceProxy` and
  `MainThreadInvoker` in [post_processing.py](../../buzz/plugins/post_processing.py)
  to marshal calls to the main thread.
- `Settings` wraps `QSettings`; secrets use OS keyring. Changing stored enum
  values, settings keys, or plugin IDs can require compatibility handling.
- Bundled plugins are copied to a writable user cache. Plugin dependencies share
  a separate cache directory. Edit repository sources, not cached copies.
- Core UI localization uses gettext `.po` catalogs compiled to `.mo`; plugins
  use their own JSON catalogs and `plugin_gettext`.

## Model, native, and asset boundaries

- `model_loader.py` owns model types, lookup, and downloads. `BUZZ_MODEL_ROOT`
  selects the model cache. Check the relevant symbol with scoped search instead
  of loading the entire file. Preserve lazy backend imports in the queue worker;
  eager torch/transformers imports increase application startup time.
- Speaker identification spans the transcriber adapter and a widget module;
  its heavy dependencies are imported lazily. `whisper.cpp`,
  `whisper_diarization`, `deepmultilingualpunctuation`, and `ctc_forced_aligner`
  are pinned git submodules declared in [.gitmodules](../../.gitmodules).
- `hatch_build.py` compiles native components and translation catalogs during
  package builds. `Makefile test` also builds native components and, outside CI,
  upgrades two lockfile packages. Use targeted `uv run pytest <paths>` for
  routine validation; consult the [development guide](development.md) for prerequisites.
- `assets.get_path()` resolves source and PyInstaller layouts. Resolve shipped
  resources through it rather than assuming the working directory.
- This `docs/development/` directory contains engineering references; the
  Docusaurus user-facing content lives in `docs/docs/`.
