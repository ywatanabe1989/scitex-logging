#!/usr/bin/env python3
"""Tests for scitex.logging._context module."""

import logging
import os
import tempfile
from pathlib import Path

import pytest


class TestLogToFile:
    """Test log_to_file context manager."""

    def test_log_to_file_creates_target_log_file(self):
        """`log_to_file(path)` creates the target file when entered."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            # Act
            with log_to_file(log_path):
                pass
            file_exists = log_path.exists()
        # Assert
        assert file_exists is True

    def test_log_to_file_creates_parent_directories_on_demand(self):
        """`log_to_file(nested_path)` creates missing parent directories."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "nested" / "dirs" / "test.log"
            # Act
            with log_to_file(log_path):
                pass
            parent_exists = log_path.parent.exists()
        # Assert
        assert parent_exists is True

    def test_log_to_file_writes_emitted_message_to_disk(self):
        """Messages emitted inside `log_to_file` show up in the file."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = logging.getLogger("test_context")
            logger.setLevel(logging.DEBUG)
            # Act
            with log_to_file(log_path, level=logging.DEBUG):
                logger.info("Test message")
            content = log_path.read_text()
        # Assert
        assert "Test message" in content

    def test_log_to_file_warning_level_drops_debug_messages(self):
        """`log_to_file(level=WARNING)` filters out emitted DEBUG records."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = logging.getLogger("test_context_level")
            logger.setLevel(logging.DEBUG)
            # Act
            with log_to_file(log_path, level=logging.WARNING):
                logger.debug("Debug message")
                logger.warning("Warning message")
            content = log_path.read_text()
        # Assert
        assert "Debug message" not in content

    def test_log_to_file_warning_level_keeps_warning_messages(self):
        """`log_to_file(level=WARNING)` keeps emitted WARNING records."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = logging.getLogger("test_context_level_warn")
            logger.setLevel(logging.DEBUG)
            # Act
            with log_to_file(log_path, level=logging.WARNING):
                logger.warning("Warning message")
            content = log_path.read_text()
        # Assert
        assert "Warning message" in content

    def test_log_to_file_append_mode_keeps_first_message(self):
        """`log_to_file(mode='a')` keeps the previously written content."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = logging.getLogger("test_context_append")
            logger.setLevel(logging.DEBUG)
            with log_to_file(log_path, mode="w"):
                logger.info("First message")
            # Act
            with log_to_file(log_path, mode="a"):
                logger.info("Second message")
            content = log_path.read_text()
        # Assert
        assert "First message" in content

    def test_log_to_file_append_mode_records_second_message(self):
        """`log_to_file(mode='a')` records the second message too."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = logging.getLogger("test_context_append_two")
            logger.setLevel(logging.DEBUG)
            with log_to_file(log_path, mode="w"):
                logger.info("First message")
            # Act
            with log_to_file(log_path, mode="a"):
                logger.info("Second message")
            content = log_path.read_text()
        # Assert
        assert "Second message" in content

    def test_log_to_file_overwrite_mode_drops_first_message(self):
        """`log_to_file(mode='w')` overwrites the previously written content."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = logging.getLogger("test_context_overwrite")
            logger.setLevel(logging.DEBUG)
            with log_to_file(log_path, mode="w"):
                logger.info("First message")
            # Act
            with log_to_file(log_path, mode="w"):
                logger.info("Second message")
            content = log_path.read_text()
        # Assert
        assert "First message" not in content

    def test_log_to_file_overwrite_mode_records_second_message(self):
        """`log_to_file(mode='w')` records the new message after overwrite."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = logging.getLogger("test_context_overwrite_two")
            logger.setLevel(logging.DEBUG)
            with log_to_file(log_path, mode="w"):
                logger.info("First message")
            # Act
            with log_to_file(log_path, mode="w"):
                logger.info("Second message")
            content = log_path.read_text()
        # Assert
        assert "Second message" in content

    def test_log_to_file_attaches_one_handler_inside_block(self):
        """Inside `log_to_file`, root has exactly one extra handler."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            root_logger = logging.getLogger()
            handlers_before = len(root_logger.handlers)
            # Act
            with log_to_file(log_path):
                handlers_during = len(root_logger.handlers)
        # Assert
        assert handlers_during == handlers_before + 1

    def test_log_to_file_removes_handler_after_block_exit(self):
        """After `log_to_file` exits, handler count returns to baseline."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            root_logger = logging.getLogger()
            handlers_before = len(root_logger.handlers)
            # Act
            with log_to_file(log_path):
                pass
            handlers_after = len(root_logger.handlers)
        # Assert
        assert handlers_after == handlers_before

    def test_log_to_file_yields_a_file_handler(self):
        """`with log_to_file(path) as h` yields a `logging.FileHandler`."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            # Act
            with log_to_file(log_path) as handler:
                yielded = handler
        # Assert
        assert isinstance(yielded, logging.FileHandler)

    def test_log_to_file_accepts_string_path_input(self):
        """`log_to_file(str_path)` accepts a plain string path."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "test.log")
            # Act
            with log_to_file(log_path):
                pass
            file_exists = os.path.exists(log_path)
        # Assert
        assert file_exists is True

    def test_log_to_file_accepts_path_object_input(self):
        """`log_to_file(Path(...))` accepts a `pathlib.Path` object."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            # Act
            with log_to_file(log_path):
                pass
            file_exists = log_path.exists()
        # Assert
        assert file_exists is True

    def test_log_to_file_default_formatter_is_scitex_file_formatter(self):
        """`log_to_file(...)` installs a SciTeXFileFormatter by default."""
        # Arrange
        from scitex_logging._context import log_to_file
        from scitex_logging._formatters import SciTeXFileFormatter

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            # Act
            with log_to_file(log_path) as handler:
                attached = handler.formatter
        # Assert
        assert isinstance(attached, SciTeXFileFormatter)

    def test_log_to_file_custom_formatter_is_attached_to_handler(self):
        """`log_to_file(formatter=...)` attaches the supplied formatter."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            custom_formatter = logging.Formatter("CUSTOM: %(message)s")
            # Act
            with log_to_file(log_path, formatter=custom_formatter) as handler:
                attached = handler.formatter
        # Assert
        assert attached is custom_formatter

    def test_log_to_file_cleans_up_handler_on_inner_exception(self):
        """Handler count returns to baseline even when block raises."""
        # Arrange
        from scitex_logging._context import log_to_file

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            root_logger = logging.getLogger()
            handlers_before = len(root_logger.handlers)
            # Act
            try:
                with log_to_file(log_path):
                    raise ValueError("Test exception")
            except ValueError:
                pass
            handlers_after = len(root_logger.handlers)
        # Assert
        assert handlers_after == handlers_before


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/logging/_context.py
# --------------------------------------------------------------------------------
# (source code preserved separately — see git history)
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/logging/_context.py
# --------------------------------------------------------------------------------
