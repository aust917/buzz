# Plugins

- Use the [plugin reference](../../docs/development/plugins.md) when implementing
  hooks, configuration or distribution; load examples only as needed.
- The contract is [base.py](base.py); discovery/cache copying is in
  [loader.py](loader.py); configuration and dispatch are in [manager.py](manager.py).
- Keep plugin IDs stable and folder names aligned with metadata. For a new bundled
  plugin, update `BUNDLED_PLUGIN_IDS` and data entries in [Buzz.spec](../../Buzz.spec).
- Hooks must not manipulate Qt widgets. `before_transcription` runs on the worker;
  `check_skip` runs after it. Post hooks run in the background for GUI tasks and
  synchronously for CLI quit-on-complete. DB access is marshaled by
  [post_processing.py](post_processing.py). Use the supplied service,
  not a DAO/connection from another thread. Preserve `after_transcription` -> save
  -> `on_complete` ordering and CLI completion waiting for hooks.
- Segment timestamps are milliseconds. Preserve translation, speaker and metadata
  when replacing segments. A skip result may be an empty list; `None` means proceed.
- Password config uses keyring, not plain settings or logs. Reuse bundled packages
  before adding runtime pip dependencies, which may be unavailable offline.
- Plugin localization uses `plugin_gettext` and JSON beside `plugin.py`, independent
  of core gettext catalogs. Keep English keys and supported locale files aligned;
  provide real translations or omit a key rather than adding empty values.
- Edit bundled sources here, not user-cache copies. The loader refreshes changed
  bundled content on launch; user-installed plugins have separate ownership.
- Start validation with [plugin tests](../../tests/plugins/) and
  [dialog tests](../../tests/widgets/plugins_dialog/); read [test rules](../../tests/AGENTS.md)
  before running them.
