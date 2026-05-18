"""Smoke test: every example script under examples/ runs to completion."""

import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES = sorted(Path(__file__).resolve().parents[2].joinpath("examples").glob("*.py"))


def test_examples_directory_contains_at_least_one_script():
    """The examples/ directory must hold at least one `*.py` script."""
    # Arrange
    discovered = EXAMPLES
    # Act
    count = len(discovered)
    # Assert
    assert count > 0


@pytest.mark.parametrize("example_path", EXAMPLES, ids=lambda p: p.name)
def test_example_script_runs_to_completion(tmp_path, example_path):
    """Each example script exits with returncode 0 under a fresh tmp cwd."""
    # Arrange
    cmd = [sys.executable, str(example_path)]
    # Act
    timeout_s = 120  # stx-allow: STX-NL001
    result = subprocess.run(
        cmd,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )
    # Assert
    assert result.returncode == 0, (
        f"{example_path.name} failed:\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
