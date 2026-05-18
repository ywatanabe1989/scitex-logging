"""PS303 example mirror stub: ensure examples/quickstart.py is syntactically valid."""

import subprocess
import sys
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "quickstart.py"


def test_quickstart_example_file_exists_on_disk():
    """The `examples/quickstart.py` file is present on disk."""
    # Arrange
    expected_path = EXAMPLE
    # Act
    is_present = expected_path.exists()
    # Assert
    assert is_present is True, f"missing example: {expected_path}"


def test_quickstart_example_compiles_under_py_compile():
    """`python -m py_compile examples/quickstart.py` exits 0."""
    # Arrange
    cmd = [sys.executable, "-m", "py_compile", str(EXAMPLE)]
    # Act
    result = subprocess.run(cmd, capture_output=True, text=True)
    # Assert
    assert result.returncode == 0, (
        f"py_compile failed for {EXAMPLE}:\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
