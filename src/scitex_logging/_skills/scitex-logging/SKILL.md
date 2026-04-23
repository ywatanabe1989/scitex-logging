---
name: scitex-logging
description: SciTeX logging — enhanced stdlib-logging wrapper with file output, SUCCESS/FAIL levels, structured warnings, and a broad SciTeX exception hierarchy. Use for any logging, warning, or error-class needs in SciTeX packages.
user-invocable: false
---

# scitex-logging

Auto-configured drop-in extension of `logging`:

## Installation & import (two equivalent paths)

The same module is reachable via two install paths. Both forms work at
runtime; which one a user has depends on their install choice.

```python
# Standalone — pip install scitex-logging
import scitex_logging
scitex_logging.getLogger(...)

# Umbrella — pip install scitex
import scitex.logging
scitex.logging.getLogger(...)
```

`pip install scitex-logging` alone does NOT expose the `scitex` namespace;
`import scitex.logging` raises `ModuleNotFoundError`. To use the
`scitex.logging` form, also `pip install scitex`.

See [../../general/02_interface-python-api.md] for the ecosystem-wide
rule and empirical verification table.

- Adds `SUCCESS` and `FAIL` levels on top of DEBUG/INFO/WARNING/ERROR/CRITICAL.
- File logging is on by default; log path via `get_log_path()`.
- Ships a SciTeX-wide **exception hierarchy** (`SciTeXError` and ~30 subclasses)
  plus a `warnings`-style API (`SciTeXWarning` etc.).
- Env var `SCITEX_LOGGING_LEVEL` picks the default level at import time.

## Sub-skills

- [01_quick-start.md](01_quick-start.md) — get a logger, log at any level
- [02_python-api.md](02_python-api.md) — config, levels, warnings, errors

No CLI, no MCP tools.
