"""Entry point: `python -m scitex_logging.llm`. Real logic lives in `_cli.py`."""

from __future__ import annotations

import sys

from ._cli import main

if __name__ == "__main__":
    sys.exit(main())
