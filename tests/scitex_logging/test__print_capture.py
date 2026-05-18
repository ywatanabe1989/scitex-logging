#!/usr/bin/env python3
"""Tests for scitex.logging._print_capture module."""

import logging
import os
import sys
from io import StringIO

import pytest


class TestPrintCapture:
    """Test PrintCapture class."""

    def teardown_method(self):
        """Ensure stdout is restored after each test."""
        from scitex_logging._print_capture import disable_print_capture

        disable_print_capture()

    def test_print_capture_init_starts_not_capturing(self):
        """Fresh PrintCapture starts with `capturing is False`."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        # Act
        capture = PrintCapture()
        # Assert
        assert capture.capturing is False

    def test_print_capture_init_stores_current_stdout(self):
        """Fresh PrintCapture snapshots the current `sys.stdout`."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        expected_stdout = sys.stdout
        # Act
        capture = PrintCapture()
        # Assert
        assert capture.original_stdout is expected_stdout

    def test_print_capture_init_custom_logger_name_is_used(self):
        """`PrintCapture(logger_name=...)` uses that logger name."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        # Act
        capture = PrintCapture(logger_name="custom.logger")
        # Assert
        assert capture.logger.name == "custom.logger"

    def test_print_capture_start_capture_sets_capturing_true(self):
        """`start_capture()` flips `capturing` to True."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        capture = PrintCapture()
        try:
            # Act
            capture.start_capture()
            captured_state = capture.capturing
        finally:
            capture.stop_capture()
        # Assert
        assert captured_state is True

    def test_print_capture_start_capture_replaces_sys_stdout(self):
        """`start_capture()` installs the capture as `sys.stdout`."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        capture = PrintCapture()
        try:
            # Act
            capture.start_capture()
            installed_stdout = sys.stdout
        finally:
            capture.stop_capture()
        # Assert
        assert installed_stdout is capture

    def test_print_capture_stop_capture_clears_capturing_flag(self):
        """`stop_capture()` flips `capturing` back to False."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        capture = PrintCapture()
        capture.start_capture()
        # Act
        capture.stop_capture()
        # Assert
        assert capture.capturing is False

    def test_print_capture_stop_capture_restores_original_stdout(self):
        """`stop_capture()` restores the snapshot of `sys.stdout`."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        original = sys.stdout
        capture = PrintCapture()
        capture.start_capture()
        # Act
        capture.stop_capture()
        # Assert
        assert sys.stdout is original

    def test_print_capture_double_start_is_idempotent(self):
        """Calling `start_capture()` twice does not raise."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        capture = PrintCapture()
        try:
            capture.start_capture()
            # Act
            capture.start_capture()
            captured_state = capture.capturing
        finally:
            capture.stop_capture()
        # Assert
        assert captured_state is True

    def test_print_capture_double_stop_is_safe(self):
        """Calling `stop_capture()` twice does not raise."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        capture = PrintCapture()
        # Act
        capture.stop_capture()
        capture.stop_capture()
        # Assert
        assert capture.capturing is False

    def test_print_capture_write_forwards_to_original_stdout(self):
        """`write(text)` forwards the text to the original stdout."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        buffer = StringIO()
        capture = PrintCapture()
        capture.original_stdout = buffer
        # Act
        capture.write("test message")
        # Assert
        assert "test message" in buffer.getvalue()

    def test_print_capture_flush_does_not_raise(self):
        """`flush()` is callable and returns without raising."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        capture = PrintCapture()
        # Act
        returned = capture.flush()
        # Assert
        assert returned is None

    def test_print_capture_isatty_returns_boolean(self):
        """`isatty()` returns a boolean (mirroring `sys.stdout.isatty`)."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        capture = PrintCapture()
        # Act
        result = capture.isatty()
        # Assert
        assert isinstance(result, bool)

    def test_print_capture_context_manager_yields_self(self):
        """`with PrintCapture() as c` yields the capture itself."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        capture = PrintCapture()
        # Act
        with capture as c:
            yielded = c
        # Assert
        assert yielded is capture

    def test_print_capture_context_manager_enters_capturing_state(self):
        """`with PrintCapture()` flips `capturing` to True inside the block."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        capture = PrintCapture()
        # Act
        with capture:
            captured_state = capture.capturing
        # Assert
        assert captured_state is True

    def test_print_capture_context_manager_installs_self_as_stdout(self):
        """`with PrintCapture() as c` makes `sys.stdout is c` inside the block."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        capture = PrintCapture()
        # Act
        with capture:
            installed = sys.stdout
        # Assert
        assert installed is capture

    def test_print_capture_context_manager_exit_clears_capturing(self):
        """After `with PrintCapture()` exits, `capturing` is False."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        capture = PrintCapture()
        # Act
        with capture:
            pass
        # Assert
        assert capture.capturing is False

    def test_print_capture_context_manager_exit_restores_stdout(self):
        """After `with PrintCapture()` exits, `sys.stdout` is restored."""
        # Arrange
        from scitex_logging._print_capture import PrintCapture

        original = sys.stdout
        capture = PrintCapture()
        # Act
        with capture:
            pass
        # Assert
        assert sys.stdout is original


class TestGlobalPrintCapture:
    """Test global print capture functions."""

    def teardown_method(self):
        """Ensure print capture is disabled after each test."""
        from scitex_logging._print_capture import disable_print_capture

        disable_print_capture()
        # Reset the global state
        import scitex_logging._print_capture as pc_module

        pc_module._print_capture = None

    def test_enable_print_capture_activates_global_capture(self):
        """`enable_print_capture()` flips the global state to enabled."""
        # Arrange
        from scitex_logging._print_capture import (
            enable_print_capture,
            is_print_capture_enabled,
        )

        # Act
        enable_print_capture()
        state = is_print_capture_enabled()
        # Assert
        assert state is True

    def test_disable_print_capture_deactivates_global_capture(self):
        """`disable_print_capture()` flips the global state to disabled."""
        # Arrange
        from scitex_logging._print_capture import (
            disable_print_capture,
            enable_print_capture,
            is_print_capture_enabled,
        )

        enable_print_capture()
        # Act
        disable_print_capture()
        state = is_print_capture_enabled()
        # Assert
        assert state is False

    def test_is_print_capture_enabled_is_false_at_import_time(self):
        """Print capture starts disabled at module import."""
        # Arrange
        from scitex_logging._print_capture import is_print_capture_enabled

        # Act
        state = is_print_capture_enabled()
        # Assert
        assert state is False

    def test_enable_print_capture_with_custom_logger_does_not_raise(self):
        """`enable_print_capture(logger_name=...)` accepts a custom logger name."""
        # Arrange
        from scitex_logging._print_capture import (
            enable_print_capture,
            is_print_capture_enabled,
        )

        # Act
        enable_print_capture(logger_name="custom.print.logger")
        state = is_print_capture_enabled()
        # Assert
        assert state is True

    def test_enable_print_capture_repeated_calls_are_idempotent(self):
        """Multiple `enable_print_capture()` calls leave state enabled."""
        # Arrange
        from scitex_logging._print_capture import (
            enable_print_capture,
            is_print_capture_enabled,
        )

        enable_print_capture()
        # Act
        enable_print_capture()
        state = is_print_capture_enabled()
        # Assert
        assert state is True


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/logging/_print_capture.py
# --------------------------------------------------------------------------------
# (source code preserved separately — see git history)
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/logging/_print_capture.py
# --------------------------------------------------------------------------------
