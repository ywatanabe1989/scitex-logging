# scitex-logging

<!-- scitex-badges:start -->
[![PyPI](https://img.shields.io/pypi/v/scitex-logging.svg)](https://pypi.org/project/scitex-logging/)
[![Python](https://img.shields.io/pypi/pyversions/scitex-logging.svg)](https://pypi.org/project/scitex-logging/)
[![Tests](https://github.com/ywatanabe1989/scitex-logging/actions/workflows/test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-logging/actions/workflows/test.yml)
[![Install Test](https://github.com/ywatanabe1989/scitex-logging/actions/workflows/install-test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-logging/actions/workflows/install-test.yml)
[![Coverage](https://codecov.io/gh/ywatanabe1989/scitex-logging/graph/badge.svg)](https://codecov.io/gh/ywatanabe1989/scitex-logging)
[![Docs](https://readthedocs.org/projects/scitex-logging/badge/?version=latest)](https://scitex-logging.readthedocs.io/en/latest/)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
<!-- scitex-badges:end -->


Logging utilities for the SciTeX ecosystem.

> **Interfaces:** Python ⭐⭐⭐ (primary) · CLI — · MCP — · Skills ⭐⭐ · Hook — · HTTP —

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
