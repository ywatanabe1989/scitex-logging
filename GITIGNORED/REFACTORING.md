# Refactoring context

## sync.py size split (active)

`sync.py` exceeded the 512-line cap after adding `exclude:` support.
`sync_tags` is logically separate (pushes git tags, unrelated to
package deployment). Extract to `sync_tags.py` and re-export from
`sync.py`.

---


`src/scitex_dev/cli.py` is currently 573 lines (over 512 cap). Refactor
is needed to split the argparse wiring and click-group factories into
dedicated modules under `_cli/`. Bypassing the size limit for the
`skills_click_group` extension (adding `export` subcommand) because
splitting `cli.py` first would expand the diff beyond the feature scope.

Follow-up task (new issue): split `cli.py` into:
- `_cli/_docs.py` (docs_click_group + register_docs_subcommand)
- `_cli/_skills.py` (skills_click_group + register_skills_subcommand)
- `cli.py` becomes a thin re-export aggregator

---

## `_cli/audit/_project/_audit.py` size (2198 lines, active bypass)

The project-structure audit module aggregates ~25 rule checks plus
their regex/constant tables in one file. Long-term split:

- `_audit/_rules/_test_layout.py`     — PS-203/204/205/206 (test files)
- `_audit/_rules/_src_layout.py`      — PS-1xx (src structure, flat-layout)
- `_audit/_rules/_top_level.py`       — PS-13x (LICENSE/CHANGELOG/etc.)
- `_audit/_rules/_docs.py`            — PS-3xx (docs/, sphinx, RTD)
- `_audit/_rules/_examples.py`        — examples + matching tests
- `_audit/_rules/_readme.py`          — README sections, badges, captions
- `_audit/_constants.py`              — `_PRIVATE_TEST_RE`, junk patterns,
                                        allow-lists, rule registry
- `_audit/__init__.py`                — thin orchestrator + public re-exports

Bypassing the size cap for a one-line regex fix (allow `_*` prefix in
`_PRIVATE_TEST_RE` so `test___main__.py` is recognised as the correct
mirror for `__main__.py`). Splitting this 2198-line file is a much
larger refactor and would balloon a bug-fix release.
