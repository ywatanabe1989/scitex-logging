#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for SciTeXLogger class."""

import logging
import tempfile
from pathlib import Path

import pytest

from scitex_logging._levels import DEBUG, FAIL, INFO, SUCCESS
from scitex_logging._logger import SciTeXLogger, setup_logger_class


class TestSciTeXLogger:
    """Test SciTeXLogger class functionality."""

    @pytest.fixture(autouse=True)
    def setup_logger(self):
        """Setup a fresh logger for each test."""
        # Setup the logger class
        setup_logger_class()

        # Create a test logger
        logger = logging.getLogger(f"test_logger_{id(self)}")
        logger.handlers.clear()
        logger.setLevel(DEBUG)

        # Add a handler to capture output
        self.log_records = []

        class ListHandler(logging.Handler):
            def __init__(self, records_list):
                super().__init__()
                self.records = records_list

            def emit(self, record):
                self.records.append(record)

        handler = ListHandler(self.log_records)
        handler.setLevel(DEBUG)
        logger.addHandler(handler)

        self.logger = logger
        yield

        # Cleanup
        logger.handlers.clear()

    def test_logger_is_scitex_logger_instance(self):
        """Fixture-built logger is an instance of SciTeXLogger."""
        # Arrange
        observed = self.logger
        # Act
        is_scitex = isinstance(observed, SciTeXLogger)
        # Assert
        assert is_scitex is True

    def test_debug_method_emits_one_record(self):
        """`logger.debug(...)` emits exactly one log record."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.debug("Debug message")
        # Assert
        assert len(records) == 1

    def test_debug_method_emits_record_at_debug_level(self):
        """`logger.debug(...)` records at the DEBUG numeric level."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.debug("Debug message")
        # Assert
        assert records[0].levelno == DEBUG

    def test_debug_method_preserves_message_text(self):
        """`logger.debug(text)` round-trips `text` through the record."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.debug("Debug message")
        # Assert
        assert records[0].getMessage() == "Debug message"

    def test_info_method_emits_one_record(self):
        """`logger.info(...)` emits exactly one log record."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.info("Info message")
        # Assert
        assert len(records) == 1

    def test_info_method_emits_record_at_info_level(self):
        """`logger.info(...)` records at the INFO numeric level."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.info("Info message")
        # Assert
        assert records[0].levelno == INFO

    def test_info_method_preserves_message_text(self):
        """`logger.info(text)` round-trips `text` through the record."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.info("Info message")
        # Assert
        assert records[0].getMessage() == "Info message"

    def test_warning_method_emits_one_record(self):
        """`logger.warning(...)` emits exactly one log record."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.warning("Warning message")
        # Assert
        assert len(records) == 1

    def test_warning_method_emits_record_at_warning_level(self):
        """`logger.warning(...)` records at the WARNING numeric level."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.warning("Warning message")
        # Assert
        assert records[0].levelno == logging.WARNING

    def test_error_method_emits_one_record(self):
        """`logger.error(...)` emits exactly one log record."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.error("Error message")
        # Assert
        assert len(records) == 1

    def test_error_method_emits_record_at_error_level(self):
        """`logger.error(...)` records at the ERROR numeric level."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.error("Error message")
        # Assert
        assert records[0].levelno == logging.ERROR

    def test_critical_method_emits_one_record(self):
        """`logger.critical(...)` emits exactly one log record."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.critical("Critical message")
        # Assert
        assert len(records) == 1

    def test_critical_method_emits_record_at_critical_level(self):
        """`logger.critical(...)` records at the CRITICAL numeric level."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.critical("Critical message")
        # Assert
        assert records[0].levelno == logging.CRITICAL

    def test_success_method_emits_one_record(self):
        """`logger.success(...)` emits exactly one log record."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.success("Success message")
        # Assert
        assert len(records) == 1

    def test_success_method_emits_record_at_success_level(self):
        """`logger.success(...)` records at the SUCCESS numeric level."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.success("Success message")
        # Assert
        assert records[0].levelno == SUCCESS

    def test_success_method_preserves_message_text(self):
        """`logger.success(text)` round-trips `text` through the record."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.success("Success message")
        # Assert
        assert records[0].getMessage() == "Success message"

    def test_fail_method_emits_one_record(self):
        """`logger.fail(...)` emits exactly one log record."""
        # Arrange
        records = self.log_records
        # Act
        getattr(self.logger, "fail")("Fail message")
        # Assert
        assert len(records) == 1

    def test_fail_method_emits_record_at_fail_level(self):
        """`logger.fail(...)` records at the FAIL numeric level."""
        # Arrange
        records = self.log_records
        # Act
        getattr(self.logger, "fail")("Fail message")
        # Assert
        assert records[0].levelno == FAIL

    def test_fail_method_preserves_message_text(self):
        """`logger.fail(text)` round-trips `text` through the record."""
        # Arrange
        records = self.log_records
        # Act
        getattr(self.logger, "fail")("Fail message")
        # Assert
        assert records[0].getMessage() == "Fail message"

    def test_indent_parameter_is_attached_to_record(self):
        """`logger.info(..., indent=N)` stores N as `record.indent`."""
        # Arrange
        records = self.log_records
        requested_indent = 2
        # Act
        self.logger.info("Indented message", indent=requested_indent)
        # Assert
        assert records[0].indent == requested_indent

    def test_separator_parameter_repeats_character_n_times(self):
        """`sep='='` with `n_sep=20` inserts a 20-char `=` separator line."""
        # Arrange
        records = self.log_records
        n = 20
        # Act
        self.logger.info("Message with separator", sep="=", n_sep=n)
        # Assert
        assert "=" * n in records[0].getMessage()

    def test_separator_parameter_keeps_payload_in_record(self):
        """`sep='='` keeps the supplied payload visible in the rendered message."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.info("Message with separator", sep="=", n_sep=20)
        # Assert
        assert "Message with separator" in records[0].getMessage()

    def test_color_parameter_is_attached_to_record(self):
        """`logger.info(..., c='red')` stores 'red' as `record.color`."""
        # Arrange
        records = self.log_records
        # Act
        self.logger.info("Colored message", c="red")
        # Assert
        assert records[0].color == "red"

    def test_to_context_manager_creates_log_file(self):
        """`logger.to(path)` creates the file when entered."""
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            # Act
            with self.logger.to(str(log_file)):
                self.logger.info("Message to file")
            file_exists = log_file.exists()
        # Assert
        assert file_exists is True

    def test_to_context_manager_writes_message_to_file(self):
        """Messages emitted inside `logger.to(path)` end up in the file."""
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            # Act
            with self.logger.to(str(log_file)):
                self.logger.info("Message to file")
            content = log_file.read_text()
        # Assert
        assert "Message to file" in content


class TestSetupLoggerClass:
    """Test setup_logger_class function."""

    def test_setup_logger_class_makes_new_loggers_scitex_loggers(self):
        """After `setup_logger_class()`, new loggers are SciTeXLogger instances."""
        # Arrange
        logging.setLoggerClass(logging.Logger)
        setup_logger_class()
        # Act
        logger = logging.getLogger("test_setup_logger_class_subject")
        try:
            is_scitex = isinstance(logger, SciTeXLogger)
        finally:
            logger.handlers.clear()
        # Assert
        assert is_scitex is True

    def test_setup_logger_class_promotes_existing_root_logger(self):
        """`setup_logger_class()` retro-fits the existing root logger."""
        # Arrange
        setup_logger_class()
        # Act
        root_logger = logging.getLogger()
        # Assert
        assert root_logger.__class__ == SciTeXLogger


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/logging/_logger.py
# --------------------------------------------------------------------------------
# (source code preserved separately — see git history)
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/logging/_logger.py
# --------------------------------------------------------------------------------
