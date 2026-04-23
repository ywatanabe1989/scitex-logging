# scitex-logging

Logging utilities for the SciTeX ecosystem.

## Problem and Solution


| # | Problem | Solution |
|---|---------|----------|
| 1 | **stdlib `logging` has only 5 levels** -- experiment scripts want a distinct SUCCESS and FAIL signal that stands out in `grep` | **SUCCESS + FAIL levels added** -- color-coded, level-aware handlers; drop-in compatible with `getLogger(__name__)` |
| 2 | **`raise ValueError("shape mismatch")` loses context** -- every package rolls its own exception hierarchy | **30+ typed exceptions** -- `SciTeXError` root + `ShapeError`, `DTypeError`, `ConfigKeyError`, `PDFDownloadError`, ...; `isinstance(e, DataError)` catches the whole class |
| 3 | **Tee stdout-to-file is a recipe** -- every script implements it differently | **`Tee("run.log")` context-manager** -- one import, no boilerplate |

## Installation

```bash
pip install scitex-logging
```

## Usage

```python
import scitex_logging

# Configure logging
scitex_logging.configure(level=scitex_logging.INFO, enable_file=True)

# Get a logger
import logging
logger = logging.getLogger(__name__)
logger.info("Hello from SciTeX logging")

# Tee stdout/stderr to log files
import sys
sys.stdout, sys.stderr = scitex_logging.tee(sys)

# Custom error classes
from scitex_logging import SciTeXError, SaveError

# Warning utilities
from scitex_logging import warn_deprecated, warn_performance

# LLM session log parsing
log = scitex_logging.llm.load("session.jsonl")
log.summary()
log.render("out.html")
```

## License

AGPL-3.0 -- see [LICENSE](LICENSE).
