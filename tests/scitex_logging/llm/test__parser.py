#!/usr/bin/env python3
# Timestamp: 2026-03-19
# File: /home/ywatanabe/proj/scitex-python/tests/scitex/logging/llm/test__parser.py

"""Tests for scitex.logging.llm parser."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from scitex_logging.llm._parser import (
    ClaudeCodeSession,
    Entry,
    ToolCall,
    ToolResult,
    load,
)


def _write_jsonl(lines: list[dict], path: Path) -> Path:
    """Write JSONL test data."""
    with open(path, "w") as f:
        for line in lines:
            f.write(json.dumps(line) + "\n")
    return path


@pytest.fixture
def sample_session(tmp_path):
    """Create a minimal session JSONL for testing."""
    entries = [
        {
            "type": "user",
            "uuid": "u1",
            "parentUuid": "",
            "timestamp": "2026-03-19T10:00:00Z",
            "sessionId": "test-session-123",
            "slug": "test-slug",
            "version": "2.1.76",
            "gitBranch": "develop",
            "message": {"role": "user", "content": "Hello world"},
        },
        {
            "type": "assistant",
            "uuid": "a1",
            "parentUuid": "u1",
            "timestamp": "2026-03-19T10:00:05Z",
            "sessionId": "test-session-123",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "I will read that file."},
                    {
                        "type": "tool_use",
                        "id": "toolu_abc",
                        "name": "Read",
                        "input": {"file_path": "/tmp/test.py"},
                    },
                ],
                "model": "claude-opus-4-6",
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cache_creation_input_tokens": 10,
                    "cache_read_input_tokens": 5,
                },
            },
        },
        {
            "type": "user",
            "uuid": "u2",
            "parentUuid": "a1",
            "timestamp": "2026-03-19T10:00:06Z",
            "sessionId": "test-session-123",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_abc",
                        "content": [{"type": "text", "text": "file contents here"}],
                    }
                ],
            },
            "toolUseResult": {
                "stdout": "file contents here",
                "stderr": "",
                "interrupted": False,
                "isImage": False,
            },
        },
        {
            "type": "system",
            "uuid": "s1",
            "timestamp": "2026-03-19T10:01:00Z",
            "sessionId": "test-session-123",
            "subtype": "turn_duration",
            "durationMs": 60_000,
            "message": {},
        },
        {
            "type": "progress",
            "data": {"type": "hook_progress"},
            "timestamp": "2026-03-19T10:00:07Z",
        },
    ]
    return _write_jsonl(entries, tmp_path / "test.jsonl")


class TestLoad:
    def test_load_returns_claude_code_session_instance(self, sample_session):
        """`load(path)` returns a ClaudeCodeSession dataclass."""
        # Arrange
        path = sample_session
        # Act
        session = load(path)
        # Assert
        assert isinstance(session, ClaudeCodeSession)

    def test_load_populates_session_id_attribute(self, sample_session):
        """`load(path).session_id` is the JSONL's `sessionId` field."""
        # Arrange
        path = sample_session
        # Act
        session = load(path)
        # Assert
        assert session.session_id == "test-session-123"

    def test_load_populates_slug_attribute(self, sample_session):
        """`load(path).slug` is the JSONL's `slug` field."""
        # Arrange
        path = sample_session
        # Act
        session = load(path)
        # Assert
        assert session.slug == "test-slug"

    def test_load_populates_version_attribute(self, sample_session):
        """`load(path).version` is the JSONL's `version` field."""
        # Arrange
        path = sample_session
        # Act
        session = load(path)
        # Assert
        assert session.version == "2.1.76"

    def test_load_populates_git_branch_attribute(self, sample_session):
        """`load(path).git_branch` is the JSONL's `gitBranch` field."""
        # Arrange
        path = sample_session
        # Act
        session = load(path)
        # Assert
        assert session.git_branch == "develop"

    def test_load_filters_progress_entries_from_session(self, sample_session):
        """`load(...)` drops `progress`-type rows from `.entries`."""
        # Arrange
        path = sample_session
        # Act
        session = load(path)
        types = [e.type for e in session.entries]
        # Assert
        assert "progress" not in types

    def test_load_entry_count_excludes_progress_row(self, sample_session):
        """`load(...).entries` length equals the non-progress row count."""
        # Arrange
        path = sample_session
        # Act
        session = load(path)
        # Assert
        assert len(session.entries) == 4

    def test_load_nonexistent_path_raises_file_not_found(self, tmp_path):
        """`load(<missing>)` raises `FileNotFoundError`."""
        # Arrange
        missing = tmp_path / "nonexistent.jsonl"
        # Act
        # Assert
        with pytest.raises(FileNotFoundError):
            load(missing)


class TestEntry:
    def test_user_entry_type_is_user_string(self, sample_session):
        """First user entry has `type == 'user'`."""
        # Arrange
        session = load(sample_session)
        # Act
        user = session.user_entries[0]
        # Assert
        assert user.type == "user"

    def test_user_entry_text_carries_user_message_text(self, sample_session):
        """First user entry's `text` is the user message body."""
        # Arrange
        session = load(sample_session)
        # Act
        user = session.user_entries[0]
        # Assert
        assert user.text == "Hello world"

    def test_user_entry_uuid_carries_jsonl_uuid_value(self, sample_session):
        """First user entry's `uuid` is the JSONL `uuid` field."""
        # Arrange
        session = load(sample_session)
        # Act
        user = session.user_entries[0]
        # Assert
        assert user.uuid == "u1"

    def test_assistant_entry_type_is_assistant_string(self, sample_session):
        """First assistant entry has `type == 'assistant'`."""
        # Arrange
        session = load(sample_session)
        # Act
        asst = session.assistant_entries[0]
        # Assert
        assert asst.type == "assistant"

    def test_assistant_entry_text_carries_assistant_message_text(self, sample_session):
        """First assistant entry's `text` is the leading text block."""
        # Arrange
        session = load(sample_session)
        # Act
        asst = session.assistant_entries[0]
        # Assert
        assert asst.text == "I will read that file."

    def test_assistant_entry_records_model_name(self, sample_session):
        """First assistant entry records the message-level `model` name."""
        # Arrange
        session = load(sample_session)
        # Act
        asst = session.assistant_entries[0]
        # Assert
        assert asst.model == "claude-opus-4-6"

    def test_assistant_entry_records_input_token_count(self, sample_session):
        """First assistant entry records the message-level input tokens."""
        # Arrange
        session = load(sample_session)
        # Act
        asst = session.assistant_entries[0]
        # Assert
        assert asst.input_tokens == 100

    def test_assistant_entry_records_output_token_count(self, sample_session):
        """First assistant entry records the message-level output tokens."""
        # Arrange
        session = load(sample_session)
        # Act
        asst = session.assistant_entries[0]
        # Assert
        assert asst.output_tokens == 50

    def test_tool_calls_count_matches_tool_use_blocks(self, sample_session):
        """First assistant entry has one `ToolCall` (matches the JSONL)."""
        # Arrange
        session = load(sample_session)
        # Act
        asst = session.assistant_entries[0]
        # Assert
        assert len(asst.tool_calls) == 1

    def test_tool_call_object_is_toolcall_instance(self, sample_session):
        """The first tool_use block parses into a `ToolCall` dataclass."""
        # Arrange
        session = load(sample_session)
        # Act
        tc = session.assistant_entries[0].tool_calls[0]
        # Assert
        assert isinstance(tc, ToolCall)

    def test_tool_call_records_tool_name(self, sample_session):
        """`ToolCall.name` matches the JSONL `name` field."""
        # Arrange
        session = load(sample_session)
        # Act
        tc = session.assistant_entries[0].tool_calls[0]
        # Assert
        assert tc.name == "Read"

    def test_tool_call_records_tool_id(self, sample_session):
        """`ToolCall.id` matches the JSONL `id` field."""
        # Arrange
        session = load(sample_session)
        # Act
        tc = session.assistant_entries[0].tool_calls[0]
        # Assert
        assert tc.id == "toolu_abc"

    def test_tool_call_records_tool_input_dict(self, sample_session):
        """`ToolCall.input` is the verbatim JSONL `input` dict."""
        # Arrange
        session = load(sample_session)
        # Act
        tc = session.assistant_entries[0].tool_calls[0]
        # Assert
        assert tc.input == {"file_path": "/tmp/test.py"}

    def test_tool_result_attribute_is_not_none(self, sample_session):
        """The follow-up user entry's `tool_result` is not None."""
        # Arrange
        session = load(sample_session)
        # Act
        user2 = session.entries[2]
        # Assert
        assert user2.tool_result is not None

    def test_tool_result_attribute_is_toolresult_instance(self, sample_session):
        """The follow-up user entry's `tool_result` is a `ToolResult`."""
        # Arrange
        session = load(sample_session)
        # Act
        user2 = session.entries[2]
        # Assert
        assert isinstance(user2.tool_result, ToolResult)

    def test_tool_result_records_stdout_field(self, sample_session):
        """`ToolResult.stdout` carries the JSONL `stdout` field."""
        # Arrange
        session = load(sample_session)
        # Act
        user2 = session.entries[2]
        # Assert
        assert user2.tool_result.stdout == "file contents here"

    def test_system_entry_records_duration_ms_field(self, sample_session):
        """The `system` entry preserves the `durationMs` field."""
        # Arrange
        session = load(sample_session)
        # Act
        sys_entry = [e for e in session.entries if e.type == "system"][0]
        # Assert
        assert sys_entry.duration_ms == 60_000


class TestSummary:
    def test_summary_dict_includes_session_id_key(self, sample_session):
        """`session.summary()` dict includes `session_id`."""
        # Arrange
        session = load(sample_session)
        # Act
        s = session.summary()
        # Assert
        assert "session_id" in s

    def test_summary_dict_includes_total_tokens_key(self, sample_session):
        """`session.summary()` dict includes `total_tokens`."""
        # Arrange
        session = load(sample_session)
        # Act
        s = session.summary()
        # Assert
        assert "total_tokens" in s

    def test_summary_dict_includes_tool_usage_key(self, sample_session):
        """`session.summary()` dict includes `tool_usage`."""
        # Arrange
        session = load(sample_session)
        # Act
        s = session.summary()
        # Assert
        assert "tool_usage" in s

    def test_summary_dict_user_turns_count_value(self, sample_session):
        """`session.summary()` dict reports `user_turns == 2`."""
        # Arrange
        session = load(sample_session)
        # Act
        s = session.summary()
        # Assert
        assert s["user_turns"] == 2

    def test_summary_dict_assistant_turns_count_value(self, sample_session):
        """`session.summary()` dict reports `assistant_turns == 1`."""
        # Arrange
        session = load(sample_session)
        # Act
        s = session.summary()
        # Assert
        assert s["assistant_turns"] == 1

    def test_summary_dict_total_tool_calls_count_value(self, sample_session):
        """`session.summary()` dict reports `total_tool_calls == 1`."""
        # Arrange
        session = load(sample_session)
        # Act
        s = session.summary()
        # Assert
        assert s["total_tool_calls"] == 1

    def test_summary_dict_tool_usage_mapping_value(self, sample_session):
        """`session.summary()` dict reports `tool_usage == {'Read': 1}`."""
        # Arrange
        session = load(sample_session)
        # Act
        s = session.summary()
        # Assert
        assert s["tool_usage"] == {"Read": 1}

    def test_summary_dict_total_input_tokens_value(self, sample_session):
        """`session.summary()` dict reports `total_input_tokens == 100`."""
        # Arrange
        session = load(sample_session)
        # Act
        s = session.summary()
        # Assert
        assert s["total_input_tokens"] == 100

    def test_summary_dict_total_output_tokens_value(self, sample_session):
        """`session.summary()` dict reports `total_output_tokens == 50`."""
        # Arrange
        session = load(sample_session)
        # Act
        s = session.summary()
        # Assert
        assert s["total_output_tokens"] == 50

    def test_summary_dict_total_tokens_value(self, sample_session):
        """`session.summary()` dict reports `total_tokens == 150`."""
        # Arrange
        session = load(sample_session)
        # Act
        s = session.summary()
        # Assert
        assert s["total_tokens"] == 150


class TestProperties:
    def test_session_tool_calls_count_property(self, sample_session):
        """`session.tool_calls` has one entry (the only tool call here)."""
        # Arrange
        session = load(sample_session)
        # Act
        tool_calls = session.tool_calls
        # Assert
        assert len(tool_calls) == 1

    def test_session_tool_calls_first_name_property(self, sample_session):
        """`session.tool_calls[0].name == 'Read'`."""
        # Arrange
        session = load(sample_session)
        # Act
        first = session.tool_calls[0]
        # Assert
        assert first.name == "Read"

    def test_session_total_tokens_property_sums_to_expected(self, sample_session):
        """`session.total_tokens == 150` (input + output)."""
        # Arrange
        session = load(sample_session)
        # Act
        total = session.total_tokens
        # Assert
        assert total == 150


# EOF
