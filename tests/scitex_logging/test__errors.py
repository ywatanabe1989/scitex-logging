#!/usr/bin/env python3
"""Tests for scitex.logging._errors module."""

import os
import tempfile

import pytest


def _capture_raise(func, *args, **kwargs):
    """Invoke ``func`` and return the raised exception (or ``None``).

    Lets tests assert on the raised exception's payload without combining
    ``with pytest.raises(...)`` and a follow-up ``assert`` in the same
    test body (STX-TQ007).
    """
    try:
        func(*args, **kwargs)
    except BaseException as captured:
        return captured
    return None


class TestSciTeXError:
    """Test base SciTeXError class."""

    def test_scitex_error_basic_message_appears_in_str(self):
        """SciTeXError(msg) puts `msg` in its `str(...)` rendering."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        # Act
        error = SciTeXError("Test error")
        # Assert
        assert "Test error" in str(error)

    def test_scitex_error_basic_message_attribute_is_stored(self):
        """SciTeXError(msg) stores `msg` on `error.message`."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        # Act
        error = SciTeXError("Test error")
        # Assert
        assert error.message == "Test error"

    def test_scitex_error_context_header_in_str(self):
        """SciTeXError with context prints the `Context:` heading."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        # Act
        error = SciTeXError("Test error", context={"key1": "value1"})
        # Assert
        assert "Context:" in str(error)

    def test_scitex_error_context_value_rendered_as_key_colon_value(self):
        """SciTeXError context renders each entry as `key: value`."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        # Act
        error = SciTeXError("Test error", context={"key1": "value1"})
        # Assert
        assert "key1: value1" in str(error)

    def test_scitex_error_context_is_stored_on_attribute(self):
        """SciTeXError context is preserved on `error.context`."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        original = {"key1": "value1", "key2": "value2"}
        # Act
        error = SciTeXError("Test error", context=original)
        # Assert
        assert error.context == original

    def test_scitex_error_suggestion_text_appears_in_str(self):
        """SciTeXError suggestion is rendered with the `Suggestion:` prefix."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        # Act
        error = SciTeXError("Test error", suggestion="Try this instead")
        # Assert
        assert "Suggestion: Try this instead" in str(error)

    def test_scitex_error_suggestion_is_stored_on_attribute(self):
        """SciTeXError suggestion is preserved on `error.suggestion`."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        # Act
        error = SciTeXError("Test error", suggestion="Try this instead")
        # Assert
        assert error.suggestion == "Try this instead"

    def test_scitex_error_full_format_renders_brand_prefix(self):
        """SciTeXError with all parts prefixes with `SciTeX Error:`."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        # Act
        error = SciTeXError(
            "Test error",
            context={"file": "test.py"},
            suggestion="Check the file",
        )
        # Assert
        assert "SciTeX Error:" in str(error)

    def test_scitex_error_full_format_renders_context_pair(self):
        """SciTeXError with all parts renders the context pair line."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        # Act
        error = SciTeXError(
            "Test error",
            context={"file": "test.py"},
            suggestion="Check the file",
        )
        # Assert
        assert "file: test.py" in str(error)

    def test_scitex_error_full_format_renders_suggestion_line(self):
        """SciTeXError with all parts renders the suggestion line."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        # Act
        error = SciTeXError(
            "Test error",
            context={"file": "test.py"},
            suggestion="Check the file",
        )
        # Assert
        assert "Suggestion: Check the file" in str(error)

    def test_scitex_error_empty_context_dict_is_stored(self):
        """SciTeXError(context={}) keeps the empty dict on the attribute."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        # Act
        error = SciTeXError("Test error", context={})
        # Assert
        assert error.context == {}

    def test_scitex_error_is_exception_subclass(self):
        """SciTeXError is a subclass of the builtin Exception."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        # Act
        is_subclass = issubclass(SciTeXError, Exception)
        # Assert
        assert is_subclass is True

    def test_scitex_error_is_raisable_as_exception(self):
        """SciTeXError can be raised and caught with `pytest.raises`."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        def _raise():
            raise SciTeXError("Test raise")

        # Act
        # Assert
        with pytest.raises(SciTeXError):
            _raise()

    def test_scitex_error_raised_instance_preserves_message(self):
        """Raised SciTeXError keeps the message in its `str` form."""
        # Arrange
        from scitex_logging._errors import SciTeXError

        def _raise():
            raise SciTeXError("Test raise")

        # Act
        captured = _capture_raise(_raise)
        # Assert
        assert "Test raise" in str(captured)


class TestConfigurationErrors:
    """Test configuration-related errors."""

    def test_configuration_error_subclasses_scitex_error(self):
        """ConfigurationError is a subclass of SciTeXError."""
        # Arrange
        from scitex_logging._errors import ConfigurationError, SciTeXError

        # Act
        is_subclass = issubclass(ConfigurationError, SciTeXError)
        # Assert
        assert is_subclass is True

    def test_config_file_not_found_error_message_includes_filepath(self):
        """ConfigFileNotFoundError prints the offending filepath."""
        # Arrange
        from scitex_logging._errors import ConfigFileNotFoundError

        # Act
        error = ConfigFileNotFoundError("/path/to/config.yaml")
        # Assert
        assert "/path/to/config.yaml" in str(error)

    def test_config_file_not_found_error_context_has_filepath_key(self):
        """ConfigFileNotFoundError context has a `filepath` key."""
        # Arrange
        from scitex_logging._errors import ConfigFileNotFoundError

        # Act
        error = ConfigFileNotFoundError("/path/to/config.yaml")
        # Assert
        assert "filepath" in error.context

    def test_config_file_not_found_error_context_filepath_value(self):
        """ConfigFileNotFoundError context maps `filepath` to the input path."""
        # Arrange
        from scitex_logging._errors import ConfigFileNotFoundError

        # Act
        error = ConfigFileNotFoundError("/path/to/config.yaml")
        # Assert
        assert error.context["filepath"] == "/path/to/config.yaml"

    def test_config_file_not_found_error_has_non_null_suggestion(self):
        """ConfigFileNotFoundError ships a suggestion string by default."""
        # Arrange
        from scitex_logging._errors import ConfigFileNotFoundError

        # Act
        error = ConfigFileNotFoundError("/path/to/config.yaml")
        # Assert
        assert error.suggestion is not None

    def test_config_key_error_message_includes_missing_key(self):
        """ConfigKeyError prints the missing key name."""
        # Arrange
        from scitex_logging._errors import ConfigKeyError

        # Act
        error = ConfigKeyError("missing_key")
        # Assert
        assert "missing_key" in str(error)

    def test_config_key_error_context_maps_missing_key(self):
        """ConfigKeyError context maps `missing_key` to the key name."""
        # Arrange
        from scitex_logging._errors import ConfigKeyError

        # Act
        error = ConfigKeyError("missing_key")
        # Assert
        assert error.context["missing_key"] == "missing_key"

    def test_config_key_error_with_available_keys_message_names_key(self):
        """ConfigKeyError with `available_keys` still mentions the missing key."""
        # Arrange
        from scitex_logging._errors import ConfigKeyError

        # Act
        error = ConfigKeyError("missing", available_keys=["key1", "key2"])
        # Assert
        assert "missing" in str(error)

    def test_config_key_error_with_available_keys_adds_context_entry(self):
        """ConfigKeyError with `available_keys` adds the entry to context."""
        # Arrange
        from scitex_logging._errors import ConfigKeyError

        # Act
        error = ConfigKeyError("missing", available_keys=["key1", "key2"])
        # Assert
        assert "available_keys" in error.context


class TestIOErrors:
    """Test IO-related errors."""

    def test_io_error_subclasses_scitex_error(self):
        """IOError is a subclass of SciTeXError."""
        # Arrange
        from scitex_logging._errors import IOError, SciTeXError

        # Act
        is_subclass = issubclass(IOError, SciTeXError)
        # Assert
        assert is_subclass is True

    def test_file_format_error_message_includes_filepath(self):
        """FileFormatError prints the offending filepath."""
        # Arrange
        from scitex_logging._errors import FileFormatError

        # Act
        error = FileFormatError("/path/file.txt")
        # Assert
        assert "/path/file.txt" in str(error)

    def test_file_format_error_context_filepath_value(self):
        """FileFormatError context maps `filepath` to the input path."""
        # Arrange
        from scitex_logging._errors import FileFormatError

        # Act
        error = FileFormatError("/path/file.txt")
        # Assert
        assert error.context["filepath"] == "/path/file.txt"

    def test_file_format_error_message_includes_expected_format(self):
        """FileFormatError prints `expected: <fmt>` when supplied."""
        # Arrange
        from scitex_logging._errors import FileFormatError

        # Act
        error = FileFormatError(
            "/path/file.txt", expected_format="json", actual_format="csv"
        )
        # Assert
        assert "expected: json" in str(error)

    def test_file_format_error_message_includes_actual_format(self):
        """FileFormatError prints `got: <fmt>` when supplied."""
        # Arrange
        from scitex_logging._errors import FileFormatError

        # Act
        error = FileFormatError(
            "/path/file.txt", expected_format="json", actual_format="csv"
        )
        # Assert
        assert "got: csv" in str(error)

    def test_save_error_message_includes_filepath(self):
        """SaveError prints the offending filepath."""
        # Arrange
        from scitex_logging._errors import SaveError

        # Act
        error = SaveError("/path/file.txt", "Permission denied")
        # Assert
        assert "/path/file.txt" in str(error)

    def test_save_error_message_includes_reason(self):
        """SaveError prints the failure reason."""
        # Arrange
        from scitex_logging._errors import SaveError

        # Act
        error = SaveError("/path/file.txt", "Permission denied")
        # Assert
        assert "Permission denied" in str(error)

    def test_save_error_context_filepath_value(self):
        """SaveError context maps `filepath` to the input path."""
        # Arrange
        from scitex_logging._errors import SaveError

        # Act
        error = SaveError("/path/file.txt", "Permission denied")
        # Assert
        assert error.context["filepath"] == "/path/file.txt"

    def test_save_error_context_reason_value(self):
        """SaveError context maps `reason` to the input reason."""
        # Arrange
        from scitex_logging._errors import SaveError

        # Act
        error = SaveError("/path/file.txt", "Permission denied")
        # Assert
        assert error.context["reason"] == "Permission denied"

    def test_load_error_message_includes_filepath(self):
        """LoadError prints the offending filepath."""
        # Arrange
        from scitex_logging._errors import LoadError

        # Act
        error = LoadError("/path/file.txt", "File not found")
        # Assert
        assert "/path/file.txt" in str(error)

    def test_load_error_message_includes_reason(self):
        """LoadError prints the failure reason."""
        # Arrange
        from scitex_logging._errors import LoadError

        # Act
        error = LoadError("/path/file.txt", "File not found")
        # Assert
        assert "File not found" in str(error)


class TestScholarErrors:
    """Test scholar module errors."""

    def test_scholar_error_subclasses_scitex_error(self):
        """ScholarError is a subclass of SciTeXError."""
        # Arrange
        from scitex_logging._errors import ScholarError, SciTeXError

        # Act
        is_subclass = issubclass(ScholarError, SciTeXError)
        # Assert
        assert is_subclass is True

    def test_search_error_message_includes_query(self):
        """SearchError prints the search query in its message."""
        # Arrange
        from scitex_logging._errors import SearchError

        # Act
        error = SearchError("machine learning", "PubMed", "API timeout")
        # Assert
        assert "machine learning" in str(error)

    def test_search_error_message_includes_source(self):
        """SearchError prints the search source in its message."""
        # Arrange
        from scitex_logging._errors import SearchError

        # Act
        error = SearchError("machine learning", "PubMed", "API timeout")
        # Assert
        assert "PubMed" in str(error)

    def test_search_error_context_query_value(self):
        """SearchError context maps `query` to the input query."""
        # Arrange
        from scitex_logging._errors import SearchError

        # Act
        error = SearchError("machine learning", "PubMed", "API timeout")
        # Assert
        assert error.context["query"] == "machine learning"

    def test_enrichment_error_message_includes_paper_title(self):
        """EnrichmentError prints the paper title."""
        # Arrange
        from scitex_logging._errors import EnrichmentError

        # Act
        error = EnrichmentError("Paper Title", "Missing journal info")
        # Assert
        assert "Paper Title" in str(error)

    def test_enrichment_error_context_paper_title_value(self):
        """EnrichmentError context maps `paper_title` to the input title."""
        # Arrange
        from scitex_logging._errors import EnrichmentError

        # Act
        error = EnrichmentError("Paper Title", "Missing journal info")
        # Assert
        assert error.context["paper_title"] == "Paper Title"

    def test_pdf_download_error_message_includes_host(self):
        """PDFDownloadError prints the host portion of the URL."""
        # Arrange
        from scitex_logging._errors import PDFDownloadError

        # Act
        error = PDFDownloadError("https://example.com/paper.pdf", "404 Not Found")
        # Assert
        assert "example.com" in str(error)

    def test_pdf_download_error_context_url_value(self):
        """PDFDownloadError context maps `url` to the input URL."""
        # Arrange
        from scitex_logging._errors import PDFDownloadError

        # Act
        error = PDFDownloadError("https://example.com/paper.pdf", "404 Not Found")
        # Assert
        assert error.context["url"] == "https://example.com/paper.pdf"

    def test_doi_resolution_error_message_includes_doi(self):
        """DOIResolutionError prints the offending DOI."""
        # Arrange
        from scitex_logging._errors import DOIResolutionError

        # Act
        error = DOIResolutionError("10.1234/example", "Invalid DOI format")
        # Assert
        assert "10.1234/example" in str(error)

    def test_doi_resolution_error_context_doi_value(self):
        """DOIResolutionError context maps `doi` to the input DOI."""
        # Arrange
        from scitex_logging._errors import DOIResolutionError

        # Act
        error = DOIResolutionError("10.1234/example", "Invalid DOI format")
        # Assert
        assert error.context["doi"] == "10.1234/example"

    def test_pdf_extraction_error_message_includes_filepath(self):
        """PDFExtractionError prints the offending PDF filepath."""
        # Arrange
        from scitex_logging._errors import PDFExtractionError

        # Act
        error = PDFExtractionError("/path/paper.pdf", "Encrypted PDF")
        # Assert
        assert "/path/paper.pdf" in str(error)

    def test_bibtex_enrichment_error_message_includes_filepath(self):
        """BibTeXEnrichmentError prints the offending bib filepath."""
        # Arrange
        from scitex_logging._errors import BibTeXEnrichmentError

        # Act
        error = BibTeXEnrichmentError("/path/refs.bib", "Parse error")
        # Assert
        assert "/path/refs.bib" in str(error)

    def test_translator_error_message_includes_translator_name(self):
        """TranslatorError prints the translator name."""
        # Arrange
        from scitex_logging._errors import TranslatorError

        # Act
        error = TranslatorError("PubMedTranslator", "JavaScript error")
        # Assert
        assert "PubMedTranslator" in str(error)

    def test_authentication_error_message_includes_provider(self):
        """AuthenticationError prints the auth provider."""
        # Arrange
        from scitex_logging._errors import AuthenticationError

        # Act
        error = AuthenticationError("API", "Invalid token")
        # Assert
        assert "API" in str(error)

    def test_authentication_error_context_provider_value(self):
        """AuthenticationError context maps `provider` to the input provider."""
        # Arrange
        from scitex_logging._errors import AuthenticationError

        # Act
        error = AuthenticationError("API", "Invalid token")
        # Assert
        assert error.context["provider"] == "API"


class TestPlottingErrors:
    """Test plotting-related errors."""

    def test_plotting_error_subclasses_scitex_error(self):
        """PlottingError is a subclass of SciTeXError."""
        # Arrange
        from scitex_logging._errors import PlottingError, SciTeXError

        # Act
        is_subclass = issubclass(PlottingError, SciTeXError)
        # Assert
        assert is_subclass is True

    def test_figure_not_found_error_message_includes_integer_id(self):
        """FigureNotFoundError prints the integer figure id."""
        # Arrange
        from scitex_logging._errors import FigureNotFoundError

        # Act
        error = FigureNotFoundError(1)
        # Assert
        assert "1" in str(error)

    def test_figure_not_found_error_context_integer_id_value(self):
        """FigureNotFoundError context maps `figure_id` to the integer id."""
        # Arrange
        from scitex_logging._errors import FigureNotFoundError

        # Act
        error = FigureNotFoundError(1)
        # Assert
        assert error.context["figure_id"] == 1

    def test_figure_not_found_error_message_includes_string_id(self):
        """FigureNotFoundError prints the string figure id."""
        # Arrange
        from scitex_logging._errors import FigureNotFoundError

        # Act
        error = FigureNotFoundError("my_figure")
        # Assert
        assert "my_figure" in str(error)

    def test_axis_error_message_includes_text(self):
        """AxisError prints the supplied message."""
        # Arrange
        from scitex_logging._errors import AxisError

        # Act
        error = AxisError("Invalid axis index")
        # Assert
        assert "Invalid axis index" in str(error)

    def test_axis_error_with_info_has_non_null_context(self):
        """AxisError with `axis_info` carries a non-null context dict."""
        # Arrange
        from scitex_logging._errors import AxisError

        # Act
        error = AxisError("Bad axis", axis_info={"row": 0, "col": 1})
        # Assert
        assert error.context is not None


class TestDataErrors:
    """Test data processing errors."""

    def test_data_error_subclasses_scitex_error(self):
        """DataError is a subclass of SciTeXError."""
        # Arrange
        from scitex_logging._errors import DataError, SciTeXError

        # Act
        is_subclass = issubclass(DataError, SciTeXError)
        # Assert
        assert is_subclass is True

    def test_shape_error_message_includes_operation_name(self):
        """ShapeError prints the operation name."""
        # Arrange
        from scitex_logging._errors import ShapeError

        # Act
        error = ShapeError((10, 20), (10, 30), "matrix multiply")
        # Assert
        assert "matrix multiply" in str(error)

    def test_shape_error_context_expected_shape_value(self):
        """ShapeError context maps `expected_shape` to the input tuple."""
        # Arrange
        from scitex_logging._errors import ShapeError

        # Act
        error = ShapeError((10, 20), (10, 30), "matrix multiply")
        # Assert
        assert error.context["expected_shape"] == (10, 20)

    def test_shape_error_context_actual_shape_value(self):
        """ShapeError context maps `actual_shape` to the input tuple."""
        # Arrange
        from scitex_logging._errors import ShapeError

        # Act
        error = ShapeError((10, 20), (10, 30), "matrix multiply")
        # Assert
        assert error.context["actual_shape"] == (10, 30)

    def test_dtype_error_message_includes_operation_name(self):
        """DTypeError prints the operation name."""
        # Arrange
        from scitex_logging._errors import DTypeError

        # Act
        error = DTypeError("float32", "int64", "tensor operation")
        # Assert
        assert "tensor operation" in str(error)

    def test_dtype_error_context_expected_dtype_value(self):
        """DTypeError context maps `expected_dtype` to the input dtype."""
        # Arrange
        from scitex_logging._errors import DTypeError

        # Act
        error = DTypeError("float32", "int64", "tensor operation")
        # Assert
        assert error.context["expected_dtype"] == "float32"

    def test_dtype_error_context_actual_dtype_value(self):
        """DTypeError context maps `actual_dtype` to the input dtype."""
        # Arrange
        from scitex_logging._errors import DTypeError

        # Act
        error = DTypeError("float32", "int64", "tensor operation")
        # Assert
        assert error.context["actual_dtype"] == "int64"


class TestPathErrors:
    """Test path-related errors."""

    def test_path_error_subclasses_scitex_error(self):
        """PathError is a subclass of SciTeXError."""
        # Arrange
        from scitex_logging._errors import PathError, SciTeXError

        # Act
        is_subclass = issubclass(PathError, SciTeXError)
        # Assert
        assert is_subclass is True

    def test_invalid_path_error_message_includes_path(self):
        """InvalidPathError prints the offending path."""
        # Arrange
        from scitex_logging._errors import InvalidPathError

        # Act
        error = InvalidPathError("/absolute/path", "Must be relative")
        # Assert
        assert "/absolute/path" in str(error)

    def test_invalid_path_error_context_path_value(self):
        """InvalidPathError context maps `path` to the input path."""
        # Arrange
        from scitex_logging._errors import InvalidPathError

        # Act
        error = InvalidPathError("/absolute/path", "Must be relative")
        # Assert
        assert error.context["path"] == "/absolute/path"

    def test_path_not_found_error_message_includes_path(self):
        """PathNotFoundError prints the offending path."""
        # Arrange
        from scitex_logging._errors import PathNotFoundError

        # Act
        error = PathNotFoundError("./missing/file.txt")
        # Assert
        assert "./missing/file.txt" in str(error)


class TestTemplateErrors:
    """Test template-related errors."""

    def test_template_error_subclasses_scitex_error(self):
        """TemplateError is a subclass of SciTeXError."""
        # Arrange
        from scitex_logging._errors import SciTeXError, TemplateError

        # Act
        is_subclass = issubclass(TemplateError, SciTeXError)
        # Assert
        assert is_subclass is True

    def test_template_violation_error_message_includes_filepath(self):
        """TemplateViolationError prints the offending file path."""
        # Arrange
        from scitex_logging._errors import TemplateViolationError

        # Act
        error = TemplateViolationError("script.py", "Missing header")
        # Assert
        assert "script.py" in str(error)

    def test_template_violation_error_message_includes_violation_text(self):
        """TemplateViolationError prints the violation description."""
        # Arrange
        from scitex_logging._errors import TemplateViolationError

        # Act
        error = TemplateViolationError("script.py", "Missing header")
        # Assert
        assert "Missing header" in str(error)


class TestNNErrors:
    """Test neural network errors."""

    def test_nn_error_subclasses_scitex_error(self):
        """NNError is a subclass of SciTeXError."""
        # Arrange
        from scitex_logging._errors import NNError, SciTeXError

        # Act
        is_subclass = issubclass(NNError, SciTeXError)
        # Assert
        assert is_subclass is True

    def test_model_error_message_includes_model_name(self):
        """ModelError prints the model name."""
        # Arrange
        from scitex_logging._errors import ModelError

        # Act
        error = ModelError("ResNet50", "Weight loading failed")
        # Assert
        assert "ResNet50" in str(error)

    def test_model_error_context_model_name_value(self):
        """ModelError context maps `model_name` to the input name."""
        # Arrange
        from scitex_logging._errors import ModelError

        # Act
        error = ModelError("ResNet50", "Weight loading failed")
        # Assert
        assert error.context["model_name"] == "ResNet50"


class TestStatsErrors:
    """Test statistics errors."""

    def test_stats_error_subclasses_scitex_error(self):
        """StatsError is a subclass of SciTeXError."""
        # Arrange
        from scitex_logging._errors import SciTeXError, StatsError

        # Act
        is_subclass = issubclass(StatsError, SciTeXError)
        # Assert
        assert is_subclass is True

    def test_test_error_message_includes_test_name(self):
        """TestError prints the statistical test name."""
        # Arrange
        from scitex_logging._errors import TestError

        # Act
        error = TestError("t-test", "Sample size too small")
        # Assert
        assert "t-test" in str(error)

    def test_test_error_context_test_name_value(self):
        """TestError context maps `test_name` to the input name."""
        # Arrange
        from scitex_logging._errors import TestError

        # Act
        error = TestError("t-test", "Sample size too small")
        # Assert
        assert error.context["test_name"] == "t-test"


class TestValidationHelpers:
    """Test validation helper functions."""

    def test_check_path_valid_relative_dot_slash_does_not_raise(self):
        """`check_path('./valid/path')` accepts a `./` relative path."""
        # Arrange
        from scitex_logging._errors import check_path

        # Act
        result = _capture_raise(check_path, "./valid/path")
        # Assert
        assert result is None

    def test_check_path_valid_relative_dotdot_slash_does_not_raise(self):
        """`check_path('../parent/path')` accepts a `../` relative path."""
        # Arrange
        from scitex_logging._errors import check_path

        # Act
        result = _capture_raise(check_path, "../parent/path")
        # Assert
        assert result is None

    def test_check_path_absolute_path_raises_invalid_path_error(self):
        """`check_path('/absolute/path')` raises InvalidPathError."""
        # Arrange
        from scitex_logging._errors import InvalidPathError, check_path

        # Act
        # Assert
        with pytest.raises(InvalidPathError):
            check_path("/absolute/path")

    def test_check_path_non_string_input_raises_invalid_path_error(self):
        """`check_path(123)` raises InvalidPathError for non-str input."""
        # Arrange
        from scitex_logging._errors import InvalidPathError, check_path

        # Act
        # Assert
        with pytest.raises(InvalidPathError):
            check_path(123)

    def test_check_file_exists_with_existing_file_does_not_raise(self):
        """`check_file_exists(<existing>)` is a no-op for existing files."""
        # Arrange
        from scitex_logging._errors import check_file_exists

        with tempfile.NamedTemporaryFile() as f:
            # Act
            result = _capture_raise(check_file_exists, f.name)
        # Assert
        assert result is None

    def test_check_file_exists_with_missing_file_raises_path_not_found(self):
        """`check_file_exists(<missing>)` raises PathNotFoundError."""
        # Arrange
        from scitex_logging._errors import PathNotFoundError, check_file_exists

        # Act
        # Assert
        with pytest.raises(PathNotFoundError):
            check_file_exists("/nonexistent/file.txt")

    def test_check_shape_compatibility_matching_shapes_does_not_raise(self):
        """`check_shape_compatibility` accepts identical shapes silently."""
        # Arrange
        from scitex_logging._errors import check_shape_compatibility

        # Act
        result = _capture_raise(
            check_shape_compatibility, (10, 20), (10, 20), "test op"
        )
        # Assert
        assert result is None

    def test_check_shape_compatibility_mismatch_raises_shape_error(self):
        """`check_shape_compatibility` raises ShapeError on mismatch."""
        # Arrange
        from scitex_logging._errors import ShapeError, check_shape_compatibility

        # Act
        # Assert
        with pytest.raises(ShapeError):
            check_shape_compatibility((10, 20), (10, 30), "test op")


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/logging/_errors.py
# --------------------------------------------------------------------------------
# (source code preserved separately — see git history)
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/logging/_errors.py
# --------------------------------------------------------------------------------
