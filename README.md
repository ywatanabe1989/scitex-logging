# scitex-logging

Logging utilities for the SciTeX ecosystem.

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
