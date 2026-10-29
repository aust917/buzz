# Transcription contracts

- [Segment](transcriber.py) times are **milliseconds**; backend outputs may be
  seconds. Preserve translation, speaker, and metadata when transforming results.
  Tasks snapshot options so subsequent UI edits cannot mutate queued work.
- [Queue orchestration](../file_transcriber_queue_worker.py) is outside this
  directory. It prepares URL audio, optional speech extraction, plugin pre-hooks,
  and backend dispatch. Preserve original media paths for playback/export when
  temporary speech files are removed.
- [WhisperFileTranscriber](whisper_file_transcriber.py) uses a child process and
  [stderr/result pipes](../conn.py). Cancellation must terminate descendant
  processes and close/drain pipes; Qt completion must release the owning thread.
- Keep backend imports lazy in the queue worker. Startup must initialize
  [CUDA paths](../cuda_setup.py) before importing torch indirectly.
- Model types, downloads, and `BUZZ_MODEL_ROOT` lookup belong to
  [model_loader.py](../model_loader.py); model-family adapters also live in
  [transformers_whisper.py](../transformers_whisper.py). Preserve CLI/backend
  mapping when adding a type in [cli.py](../cli.py).
- [Speaker identification](speaker_identifier.py) delegates to a
  [widget-module implementation](../widgets/transcription_viewer/speaker_identification_widget.py)
  with lazy imports from pinned submodules.
- Use [transcriber tests](../../tests/transcriber/) for changed contracts,
  [queue-worker tests](../../tests/transcriber/file_transcriber_queue_worker_test.py)
  for lifecycle behavior, and [model-loader tests](../../tests/model_loader_test.py)
  for lookup/download changes. Some backend tests download models; inspect the
  selected test and [model helper](../../tests/model_loader.py) before running it.
