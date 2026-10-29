# Database boundaries

- The desired schema is [buzz/schema.sql](../schema.sql).
  [helpers.run_sqlite_migrations](helpers.py) invokes the declarative
  [migrator](migrator.py); this project does not use numbered migration files.
  Schema edits must preserve existing transcripts and related segment data.
- [db.py](db.py) opens SQLite through `sqlite3` for migration, then exposes a
  Qt `QSqlDatabase`. Normal application DB access is thread-affine; do not pass
  DAOs directly into background workers. Plugins use the existing
  [main-thread service proxy](../plugins/post_processing.py).
- Startup also imports legacy JSON history and marks interrupted queued/running
  tasks canceled. Preserve those recovery steps when changing DB setup.
- Keep [entities](entity/), [DAOs](dao/), and
  [TranscriptionService](service/transcription_service.py) aligned with schema
  changes. Segment time fields use milliseconds, matching
  [the transcription contract](../transcriber/transcriber.py).
- Use [temporary DB fixtures](../../tests/conftest.py); they require a live Qt
  application even for tests without widgets. Do not validate migrations against
  the user's `Buzz.sqlite`.
- Coverage lives in [tests/db](../../tests/db/), including
  [speaker schema preservation](../../tests/db/speaker_schema_test.py),
  [DAO tests](../../tests/db/dao/transcription_dao_test.py), and
  [service tests](../../tests/db/service/transcription_service_test.py).
