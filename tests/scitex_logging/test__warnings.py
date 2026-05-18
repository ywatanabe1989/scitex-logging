#!/usr/bin/env python3
"""Tests for scitex.logging._warnings module."""

import logging
import logging.handlers
import os

import pytest


def _capture_raise(func, *args, **kwargs):
    """Invoke ``func`` and return the raised exception (or ``None``).

    This helper lets tests assert on the raised exception's *message*
    without combining ``with pytest.raises(...)`` and a follow-up
    ``assert`` in the same test body (STX-TQ007).
    """
    try:
        func(*args, **kwargs)
    except BaseException as captured:
        return captured
    return None


class TestWarningCategories:
    """Test warning category classes."""

    def test_scitex_warning_subclasses_user_warning(self):
        """SciTeXWarning is a subclass of the stdlib UserWarning."""
        # Arrange
        from scitex_logging._warnings import SciTeXWarning

        # Act
        is_subclass = issubclass(SciTeXWarning, UserWarning)
        # Assert
        assert is_subclass is True

    def test_unit_warning_subclasses_scitex_warning(self):
        """UnitWarning is a subclass of SciTeXWarning."""
        # Arrange
        from scitex_logging._warnings import SciTeXWarning, UnitWarning

        # Act
        is_subclass = issubclass(UnitWarning, SciTeXWarning)
        # Assert
        assert is_subclass is True

    def test_style_warning_subclasses_scitex_warning(self):
        """StyleWarning is a subclass of SciTeXWarning."""
        # Arrange
        from scitex_logging._warnings import SciTeXWarning, StyleWarning

        # Act
        is_subclass = issubclass(StyleWarning, SciTeXWarning)
        # Assert
        assert is_subclass is True

    def test_deprecation_warning_subclasses_scitex_warning(self):
        """SciTeXDeprecationWarning is a subclass of SciTeXWarning."""
        # Arrange
        from scitex_logging._warnings import SciTeXDeprecationWarning, SciTeXWarning

        # Act
        is_subclass = issubclass(SciTeXDeprecationWarning, SciTeXWarning)
        # Assert
        assert is_subclass is True

    def test_performance_warning_subclasses_scitex_warning(self):
        """PerformanceWarning is a subclass of SciTeXWarning."""
        # Arrange
        from scitex_logging._warnings import PerformanceWarning, SciTeXWarning

        # Act
        is_subclass = issubclass(PerformanceWarning, SciTeXWarning)
        # Assert
        assert is_subclass is True

    def test_data_loss_warning_subclasses_scitex_warning(self):
        """DataLossWarning is a subclass of SciTeXWarning."""
        # Arrange
        from scitex_logging._warnings import DataLossWarning, SciTeXWarning

        # Act
        is_subclass = issubclass(DataLossWarning, SciTeXWarning)
        # Assert
        assert is_subclass is True


class TestFilterWarnings:
    """Test filterwarnings function."""

    def setup_method(self):
        """Reset warning filters before each test."""
        from scitex_logging._warnings import resetwarnings

        resetwarnings()

    def teardown_method(self):
        """Reset warning filters after each test."""
        from scitex_logging._warnings import resetwarnings

        resetwarnings()

    def test_filterwarnings_ignore_does_not_raise_or_log(self):
        """`filterwarnings('ignore', ...)` registers without raising."""
        # Arrange
        from scitex_logging._warnings import UnitWarning, filterwarnings, warn

        filterwarnings("ignore", category=UnitWarning)
        # Act
        result = warn("Test", UnitWarning)
        # Assert
        assert result is None

    def test_filterwarnings_error_action_promotes_warn_to_exception(self):
        """`filterwarnings('error', ...)` makes `warn(...)` raise the category."""
        # Arrange
        from scitex_logging._warnings import UnitWarning, filterwarnings, warn

        filterwarnings("error", category=UnitWarning)
        # Act
        # Assert
        with pytest.raises(UnitWarning):
            warn("Test warning", UnitWarning)

    def test_filterwarnings_always_action_registers_without_error(self):
        """`filterwarnings('always', ...)` registers without raising."""
        # Arrange
        from scitex_logging._warnings import UnitWarning, filterwarnings

        # Act
        returned = filterwarnings("always", category=UnitWarning)
        # Assert
        assert returned is None

    def test_filterwarnings_invalid_action_raises_value_error(self):
        """Unknown action strings cause `filterwarnings` to raise ValueError."""
        # Arrange
        from scitex_logging._warnings import filterwarnings

        # Act
        # Assert
        with pytest.raises(ValueError):
            filterwarnings("invalid_action")

    @pytest.mark.parametrize(
        "action", ["ignore", "error", "always", "default", "once", "module"]
    )
    def test_filterwarnings_accepts_valid_action_string(self, action):
        """Each documented action string is accepted by `filterwarnings`."""
        # Arrange
        from scitex_logging._warnings import filterwarnings

        # Act
        returned = filterwarnings(action)
        # Assert
        assert returned is None


class TestResetWarnings:
    """Test resetwarnings function."""

    def test_resetwarnings_clears_registered_error_filter(self):
        """`resetwarnings()` removes a previously installed `error` filter."""
        # Arrange
        from scitex_logging._warnings import (
            UnitWarning,
            filterwarnings,
            resetwarnings,
            warn,
        )

        filterwarnings("error", category=UnitWarning)
        # Act
        resetwarnings()
        # After reset, the default action is "default" (log only, no raise),
        # so the same warn() call must NOT raise.
        result = warn("Test", UnitWarning)
        # Assert
        assert result is None


class TestWarn:
    """Test warn function."""

    def setup_method(self):
        """Reset warning filters before each test."""
        from scitex_logging._warnings import resetwarnings

        resetwarnings()

    def teardown_method(self):
        """Reset warning filters after each test."""
        from scitex_logging._warnings import resetwarnings

        resetwarnings()

    def test_warn_under_ignore_filter_returns_silently(self):
        """`warn(...)` is a silent no-op when category is filtered to ignore."""
        # Arrange
        from scitex_logging._warnings import UnitWarning, filterwarnings, warn

        filterwarnings("ignore", category=UnitWarning)
        # Act
        result = warn("Ignored warning", UnitWarning)
        # Assert
        assert result is None

    def test_warn_under_error_filter_raises_category(self):
        """`warn(...)` raises the configured category as an exception."""
        # Arrange
        from scitex_logging._warnings import UnitWarning, filterwarnings, warn

        filterwarnings("error", category=UnitWarning)
        # Act
        # Assert
        with pytest.raises(UnitWarning):
            warn("Error warning", UnitWarning)

    def test_warn_error_filter_preserves_message_in_exception(self):
        """The raised exception's `str` includes the original message."""
        # Arrange
        from scitex_logging._warnings import UnitWarning, filterwarnings, warn

        filterwarnings("error", category=UnitWarning)
        # Act
        captured = _capture_raise(warn, "Error warning", UnitWarning)
        # Assert
        assert "Error warning" in str(captured)

    def test_warn_default_category_is_scitex_warning(self):
        """`warn(...)` without category uses SciTeXWarning."""
        # Arrange
        from scitex_logging._warnings import SciTeXWarning, filterwarnings, warn

        filterwarnings("error", category=SciTeXWarning)
        # Act
        # Assert
        with pytest.raises(SciTeXWarning):
            warn("Default category warning")

    def test_warn_subclass_inherits_parent_filter(self):
        """Setting `error` on parent raises for emitted subclass warnings."""
        # Arrange
        from scitex_logging._warnings import (
            SciTeXWarning,
            UnitWarning,
            filterwarnings,
            warn,
        )

        filterwarnings("error", category=SciTeXWarning)
        # Act
        # Assert
        with pytest.raises(UnitWarning):
            warn("Test", UnitWarning)


class TestConvenienceWarnings:
    """Test convenience warning functions."""

    def setup_method(self):
        """Reset warning filters before each test."""
        from scitex_logging._warnings import resetwarnings

        resetwarnings()

    def teardown_method(self):
        """Reset warning filters after each test."""
        from scitex_logging._warnings import resetwarnings

        resetwarnings()

    def test_warn_deprecated_raises_under_error_filter(self):
        """`warn_deprecated(...)` raises SciTeXDeprecationWarning under error."""
        # Arrange
        from scitex_logging._warnings import (
            SciTeXDeprecationWarning,
            filterwarnings,
            warn_deprecated,
        )

        filterwarnings("error", category=SciTeXDeprecationWarning)
        # Act
        # Assert
        with pytest.raises(SciTeXDeprecationWarning):
            warn_deprecated("old_func", "new_func")

    def test_warn_deprecated_message_names_old_symbol(self):
        """`warn_deprecated(...)` mentions the deprecated old name."""
        # Arrange
        from scitex_logging._warnings import (
            SciTeXDeprecationWarning,
            filterwarnings,
            warn_deprecated,
        )

        filterwarnings("error", category=SciTeXDeprecationWarning)
        # Act
        captured = _capture_raise(warn_deprecated, "old_func", "new_func")
        # Assert
        assert "old_func" in str(captured)

    def test_warn_deprecated_message_names_new_symbol(self):
        """`warn_deprecated(...)` mentions the replacement new name."""
        # Arrange
        from scitex_logging._warnings import (
            SciTeXDeprecationWarning,
            filterwarnings,
            warn_deprecated,
        )

        filterwarnings("error", category=SciTeXDeprecationWarning)
        # Act
        captured = _capture_raise(warn_deprecated, "old_func", "new_func")
        # Assert
        assert "new_func" in str(captured)

    def test_warn_deprecated_message_contains_deprecated_keyword(self):
        """`warn_deprecated(...)` emits the `deprecated` keyword in the message."""
        # Arrange
        from scitex_logging._warnings import (
            SciTeXDeprecationWarning,
            filterwarnings,
            warn_deprecated,
        )

        filterwarnings("error", category=SciTeXDeprecationWarning)
        # Act
        captured = _capture_raise(warn_deprecated, "old_func", "new_func")
        # Assert
        assert "deprecated" in str(captured)

    def test_warn_deprecated_with_version_includes_version_string(self):
        """`warn_deprecated(..., version=...)` embeds the version in the message."""
        # Arrange
        from scitex_logging._warnings import (
            SciTeXDeprecationWarning,
            filterwarnings,
            warn_deprecated,
        )

        filterwarnings("error", category=SciTeXDeprecationWarning)
        # Act
        captured = _capture_raise(
            warn_deprecated, "old_func", "new_func", version="2.0"
        )
        # Assert
        assert "2.0" in str(captured)

    def test_warn_performance_raises_performance_warning(self):
        """`warn_performance(...)` raises PerformanceWarning under error filter."""
        # Arrange
        from scitex_logging._warnings import (
            PerformanceWarning,
            filterwarnings,
            warn_performance,
        )

        filterwarnings("error", category=PerformanceWarning)
        # Act
        # Assert
        with pytest.raises(PerformanceWarning):
            warn_performance("matrix_multiply", "Use vectorized operations")

    def test_warn_performance_message_names_operation(self):
        """`warn_performance(...)` mentions the operation name."""
        # Arrange
        from scitex_logging._warnings import (
            PerformanceWarning,
            filterwarnings,
            warn_performance,
        )

        filterwarnings("error", category=PerformanceWarning)
        # Act
        captured = _capture_raise(
            warn_performance, "matrix_multiply", "Use vectorized operations"
        )
        # Assert
        assert "matrix_multiply" in str(captured)

    def test_warn_performance_message_includes_suggestion(self):
        """`warn_performance(...)` carries the supplied suggestion through."""
        # Arrange
        from scitex_logging._warnings import (
            PerformanceWarning,
            filterwarnings,
            warn_performance,
        )

        filterwarnings("error", category=PerformanceWarning)
        # Act
        captured = _capture_raise(
            warn_performance, "matrix_multiply", "Use vectorized operations"
        )
        # Assert
        assert "vectorized" in str(captured)

    def test_warn_data_loss_raises_data_loss_warning(self):
        """`warn_data_loss(...)` raises DataLossWarning under error filter."""
        # Arrange
        from scitex_logging._warnings import (
            DataLossWarning,
            filterwarnings,
            warn_data_loss,
        )

        filterwarnings("error", category=DataLossWarning)
        # Act
        # Assert
        with pytest.raises(DataLossWarning):
            warn_data_loss("truncation", "Values will be truncated")

    def test_warn_data_loss_message_names_operation(self):
        """`warn_data_loss(...)` mentions the operation name."""
        # Arrange
        from scitex_logging._warnings import (
            DataLossWarning,
            filterwarnings,
            warn_data_loss,
        )

        filterwarnings("error", category=DataLossWarning)
        # Act
        captured = _capture_raise(
            warn_data_loss, "truncation", "Values will be truncated"
        )
        # Assert
        assert "truncation" in str(captured)

    def test_warn_data_loss_message_includes_detail(self):
        """`warn_data_loss(...)` carries the supplied detail through."""
        # Arrange
        from scitex_logging._warnings import (
            DataLossWarning,
            filterwarnings,
            warn_data_loss,
        )

        filterwarnings("error", category=DataLossWarning)
        # Act
        captured = _capture_raise(
            warn_data_loss, "truncation", "Values will be truncated"
        )
        # Assert
        assert "truncated" in str(captured)


class TestOnceAndDefaultActions:
    """Test 'once' and 'default' warning actions."""

    def setup_method(self):
        """Reset warning filters before each test."""
        from scitex_logging._warnings import resetwarnings

        resetwarnings()

    def teardown_method(self):
        """Reset warning filters after each test."""
        from scitex_logging._warnings import resetwarnings

        resetwarnings()

    def test_once_action_emits_warning_only_a_single_time(self):
        """`filterwarnings('once', ...)` deduplicates repeated warn() calls."""
        # Arrange
        from scitex_logging._warnings import UnitWarning, filterwarnings, warn

        filterwarnings("once", category=UnitWarning)
        logger = logging.getLogger("scitex.warnings")
        capacity = 100  # stx-allow: STX-NL001
        handler = logging.handlers.MemoryHandler(capacity=capacity)
        handler.setLevel(logging.WARNING)
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
        try:
            # Act
            warn("Same warning", UnitWarning)
            warn("Same warning", UnitWarning)
            handler.flush()
            captured_count = len(handler.buffer)
        finally:
            logger.removeHandler(handler)
        # Assert
        assert captured_count <= 1


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/logging/_warnings.py
# --------------------------------------------------------------------------------
# (source code preserved separately — see git history)
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/logging/_warnings.py
# --------------------------------------------------------------------------------
