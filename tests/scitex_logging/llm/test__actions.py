"""Tests for scitex_logging.llm._actions."""

from __future__ import annotations

import json

import pytest

from scitex_logging.llm._actions import (
    Action,
    actions_to_jsonl,
    actions_to_log,
    extract_actions,
)


class TestExtractActions:
    def test_extract_actions_returns_one_per_tool_call(self, rich_session):
        """`extract_actions(session)` returns one Action per tool_use block."""
        # Arrange
        session = rich_session
        # Act
        acts = extract_actions(session)
        names = [a.tool_name for a in acts]
        # Assert
        assert names == ["Bash", "Read", "Write", "Edit", "Grep", "Agent"]

    def test_extract_actions_pairs_bash_tool_result_content(self, rich_session):
        """Bash actions pair with their tool_result content (list form)."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        bash = next(a for a in acts if a.tool_name == "Bash")
        # Assert
        assert "foo.py" in bash.result_content

    def test_extract_actions_pairs_read_tool_result_content(self, rich_session):
        """Read actions pair with their tool_result content (str form)."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        read = next(a for a in acts if a.tool_name == "Read")
        # Assert
        assert read.result_content == "print('hello')"

    def test_extract_actions_pairs_structured_bash_stdout(self, rich_session):
        """Structured ToolUseResult populates `bash.stdout`."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        bash = next(a for a in acts if a.tool_name == "Bash")
        # Assert
        assert bash.stdout == "foo.py\nbar.py"

    def test_extract_actions_pairs_structured_bash_stderr(self, rich_session):
        """Structured ToolUseResult populates `bash.stderr` (empty string here)."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        bash = next(a for a in acts if a.tool_name == "Bash")
        # Assert
        assert bash.stderr == ""

    def test_extract_actions_pairs_structured_bash_exit_code(self, rich_session):
        """Structured ToolUseResult populates `bash.exit_code = 0`."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        bash = next(a for a in acts if a.tool_name == "Bash")
        # Assert
        assert bash.exit_code == 0

    def test_extract_actions_pairs_structured_bash_interrupted_flag(self, rich_session):
        """Structured ToolUseResult populates `bash.interrupted = False`."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        bash = next(a for a in acts if a.tool_name == "Bash")
        # Assert
        assert bash.interrupted is False

    def test_extract_actions_pairs_structured_bash_is_image_flag(self, rich_session):
        """Structured ToolUseResult populates `bash.is_image = False`."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        bash = next(a for a in acts if a.tool_name == "Bash")
        # Assert
        assert bash.is_image is False

    def test_extract_actions_raises_for_nonexistent_file(self, tmp_path):
        """`extract_actions(path)` raises FileNotFoundError for missing paths."""
        # Arrange
        missing_path = tmp_path / "missing.jsonl"
        # Act
        # Assert
        with pytest.raises(FileNotFoundError):
            extract_actions(missing_path)

    def test_extract_actions_skips_blank_and_invalid_jsonl_lines(self, tmp_path):
        """Blank lines and non-JSON lines are silently skipped."""
        # Arrange
        p = tmp_path / "mixed.jsonl"
        p.write_text(
            "\n\nnot-json\n"
            + json.dumps(
                {
                    "type": "assistant",
                    "timestamp": "t",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "x",
                                "name": "Bash",
                                "input": {"command": "echo"},
                            }
                        ]
                    },
                }
            )
            + "\n"
        )
        # Act
        acts = extract_actions(p)
        # Assert
        assert len(acts) == 1

    def test_extract_actions_skips_invalid_lines_keeps_valid_action(self, tmp_path):
        """The single valid line yields one Action with the right tool name."""
        # Arrange
        p = tmp_path / "mixed.jsonl"
        p.write_text(
            "\n\nnot-json\n"
            + json.dumps(
                {
                    "type": "assistant",
                    "timestamp": "t",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "x",
                                "name": "Bash",
                                "input": {"command": "echo"},
                            }
                        ]
                    },
                }
            )
            + "\n"
        )
        # Act
        acts = extract_actions(p)
        # Assert
        assert acts[0].tool_name == "Bash"

    def test_extract_actions_tool_result_int_content_is_stringified(self, tmp_path):
        """Tool result whose `content` is an int is rendered as `str(int)`."""
        # Arrange
        p = tmp_path / "x.jsonl"
        entries = [
            {
                "type": "assistant",
                "timestamp": "t",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "tu1",
                            "name": "Bash",
                            "input": {"command": "ls"},
                        }
                    ]
                },
            },
            {
                "type": "user",
                "timestamp": "t",
                "message": {
                    "content": [
                        {"type": "tool_result", "tool_use_id": "tu1", "content": 42}
                    ]
                },
            },
        ]
        with open(p, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        # Act
        acts = extract_actions(p)
        # Assert
        assert acts[0].result_content == "42"


class TestActionProperties:
    def test_action_command_property_extracts_command_field(self):
        """`Action(tool_input={'command': ...}).command` returns the command."""
        # Arrange
        a = Action(tool_name="Bash", tool_input={"command": "ls -la"}, tool_use_id="x")
        # Act
        observed = a.command
        # Assert
        assert observed == "ls -la"

    def test_action_file_path_property_extracts_file_path_field(self):
        """`Action(tool_input={'file_path': ...}).file_path` returns the path."""
        # Arrange
        a = Action(
            tool_name="Read", tool_input={"file_path": "/x.py"}, tool_use_id="x"
        )
        # Act
        observed = a.file_path
        # Assert
        assert observed == "/x.py"

    def test_action_description_property_extracts_description_field(self):
        """`Action(tool_input={'description': ...}).description` returns it."""
        # Arrange
        a = Action(
            tool_name="Bash", tool_input={"description": "do X"}, tool_use_id="x"
        )
        # Act
        observed = a.description
        # Assert
        assert observed == "do X"

    def test_action_command_defaults_to_empty_string(self):
        """`Action(tool_input={}).command` defaults to the empty string."""
        # Arrange
        a = Action(tool_name="Read", tool_input={}, tool_use_id="x")
        # Act
        observed = a.command
        # Assert
        assert observed == ""

    def test_action_file_path_defaults_to_empty_string(self):
        """`Action(tool_input={}).file_path` defaults to the empty string."""
        # Arrange
        a = Action(tool_name="Read", tool_input={}, tool_use_id="x")
        # Act
        observed = a.file_path
        # Assert
        assert observed == ""

    def test_action_description_defaults_to_empty_string(self):
        """`Action(tool_input={}).description` defaults to the empty string."""
        # Arrange
        a = Action(tool_name="Read", tool_input={}, tool_use_id="x")
        # Act
        observed = a.description
        # Assert
        assert observed == ""


class TestToDict:
    def test_to_dict_keeps_tool_name_field(self):
        """`Action.to_dict()` always serializes `tool_name`."""
        # Arrange
        a = Action(tool_name="Read", tool_input={}, tool_use_id="x")
        # Act
        d = a.to_dict()
        # Assert
        assert d["tool_name"] == "Read"

    def test_to_dict_omits_empty_command_field(self):
        """`Action.to_dict()` drops the `command` key when empty."""
        # Arrange
        a = Action(tool_name="Read", tool_input={}, tool_use_id="x")
        # Act
        d = a.to_dict()
        # Assert
        assert "command" not in d

    def test_to_dict_omits_empty_stdout_field(self):
        """`Action.to_dict()` drops the `stdout` key when empty."""
        # Arrange
        a = Action(tool_name="Read", tool_input={}, tool_use_id="x")
        # Act
        d = a.to_dict()
        # Assert
        assert "stdout" not in d

    def test_to_dict_omits_empty_exit_code_field(self):
        """`Action.to_dict()` drops the `exit_code` key when unset."""
        # Arrange
        a = Action(tool_name="Read", tool_input={}, tool_use_id="x")
        # Act
        d = a.to_dict()
        # Assert
        assert "exit_code" not in d

    def test_to_dict_includes_populated_command_field(self):
        """`Action.to_dict()` keeps the `command` key when populated."""
        # Arrange
        a = Action(
            tool_name="Bash",
            tool_input={"command": "ls"},
            tool_use_id="x",
            stdout="foo",
            stderr="err",
            exit_code=0,
            result_content="rc",
        )
        # Act
        d = a.to_dict()
        # Assert
        assert d["command"] == "ls"

    def test_to_dict_includes_populated_stdout_field(self):
        """`Action.to_dict()` keeps the `stdout` key when populated."""
        # Arrange
        a = Action(
            tool_name="Bash",
            tool_input={"command": "ls"},
            tool_use_id="x",
            stdout="foo",
            stderr="err",
            exit_code=0,
            result_content="rc",
        )
        # Act
        d = a.to_dict()
        # Assert
        assert d["stdout"] == "foo"

    def test_to_dict_includes_populated_stderr_field(self):
        """`Action.to_dict()` keeps the `stderr` key when populated."""
        # Arrange
        a = Action(
            tool_name="Bash",
            tool_input={"command": "ls"},
            tool_use_id="x",
            stdout="foo",
            stderr="err",
            exit_code=0,
            result_content="rc",
        )
        # Act
        d = a.to_dict()
        # Assert
        assert d["stderr"] == "err"

    def test_to_dict_includes_populated_exit_code_field(self):
        """`Action.to_dict()` keeps the `exit_code` key when populated."""
        # Arrange
        a = Action(
            tool_name="Bash",
            tool_input={"command": "ls"},
            tool_use_id="x",
            stdout="foo",
            stderr="err",
            exit_code=0,
            result_content="rc",
        )
        # Act
        d = a.to_dict()
        # Assert
        assert d["exit_code"] == 0

    def test_to_dict_includes_populated_result_content_field(self):
        """`Action.to_dict()` keeps the `result_content` key when populated."""
        # Arrange
        a = Action(
            tool_name="Bash",
            tool_input={"command": "ls"},
            tool_use_id="x",
            stdout="foo",
            stderr="err",
            exit_code=0,
            result_content="rc",
        )
        # Act
        d = a.to_dict()
        # Assert
        assert d["result_content"] == "rc"

    def test_to_dict_includes_full_tool_input_object(self):
        """`Action.to_dict()` keeps the verbatim `tool_input` dict."""
        # Arrange
        a = Action(
            tool_name="Bash",
            tool_input={"command": "ls"},
            tool_use_id="x",
            stdout="foo",
            stderr="err",
            exit_code=0,
            result_content="rc",
        )
        # Act
        d = a.to_dict()
        # Assert
        assert d["tool_input"] == {"command": "ls"}


class TestActionsToLog:
    def test_actions_to_log_renders_bash_tool_header(self, rich_session):
        """Output includes a `Tool: Bash` header line for Bash actions."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_log(acts)
        # Assert
        assert "Tool: Bash" in text

    def test_actions_to_log_renders_bash_command_line(self, rich_session):
        """Output includes a `Cmd:  ls /tmp` line for the Bash action."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_log(acts)
        # Assert
        assert "Cmd:  ls /tmp" in text

    def test_actions_to_log_renders_bash_description_line(self, rich_session):
        """Output includes a `Desc: list tmp` line for the Bash action."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_log(acts)
        # Assert
        assert "Desc: list tmp" in text

    def test_actions_to_log_renders_write_file_line(self, rich_session):
        """Output includes the `File: /tmp/out.py` line for Write actions."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_log(acts)
        # Assert
        assert "File: /tmp/out.py" in text

    def test_actions_to_log_renders_edit_old_string_line(self, rich_session):
        """Output includes the `Old:  written` line for Edit actions."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_log(acts)
        # Assert
        assert "Old:  written" in text

    def test_actions_to_log_renders_edit_new_string_line(self, rich_session):
        """Output includes the `New:  edited` line for Edit actions."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_log(acts)
        # Assert
        assert "New:  edited" in text

    def test_actions_to_log_renders_grep_pattern_line(self, rich_session):
        """Output includes a `Pattern: TODO` line for Grep actions."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_log(acts)
        # Assert
        assert "Pattern: TODO" in text

    def test_actions_to_log_renders_grep_path_line(self, rich_session):
        """Output includes a `Path: /tmp` line for Grep actions."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_log(acts)
        # Assert
        assert "Path: /tmp" in text

    def test_actions_to_log_renders_agent_description_line(self, rich_session):
        """Output includes a `Desc: deep search` line for Agent actions."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_log(acts)
        # Assert
        assert "Desc: deep search" in text

    def test_actions_to_log_renders_agent_subagent_line(self, rich_session):
        """Output includes the `Agent: Explore` line for Agent actions."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_log(acts)
        # Assert
        assert "Agent: Explore" in text

    def test_actions_to_log_truncates_long_stdout(self, rich_session):
        """With `max_output=100`, long stdout is marked `[truncated, ...]`."""
        # Arrange
        acts = extract_actions(rich_session)
        max_chars = 100  # stx-allow: STX-NL001
        # Act
        text = actions_to_log(acts, max_output=max_chars)
        # Assert
        assert "[truncated," in text

    def test_actions_to_log_emits_stderr_section_header(self, rich_session):
        """Output includes a `--- stderr ---` section header line."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_log(acts)
        # Assert
        assert "--- stderr ---" in text

    def test_actions_to_log_renders_stderr_payload_line(self, rich_session):
        """Output includes the captured stderr line `warning: something`."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_log(acts)
        # Assert
        assert "warning: something" in text

    def test_actions_to_log_unknown_tool_renders_first_input_pair(self):
        """For an unknown tool, the first key/value pair is rendered verbatim."""
        # Arrange
        a = Action(
            tool_name="MysteryTool",
            tool_input={"foo": "bar", "baz": "qux"},
            tool_use_id="x",
            timestamp="t",
        )
        # Act
        text = actions_to_log([a])
        # Assert
        assert "foo: bar" in text

    def test_actions_to_log_unknown_tool_renders_second_input_pair(self):
        """For an unknown tool, the second key/value pair is also rendered."""
        # Arrange
        a = Action(
            tool_name="MysteryTool",
            tool_input={"foo": "bar", "baz": "qux"},
            tool_use_id="x",
            timestamp="t",
        )
        # Act
        text = actions_to_log([a])
        # Assert
        assert "baz: qux" in text


class TestActionsToJsonl:
    def test_actions_to_jsonl_emits_one_object_per_line(self, rich_session):
        """`actions_to_jsonl(acts)` emits exactly len(acts) lines."""
        # Arrange
        acts = extract_actions(rich_session)
        expected_count = 6
        # Act
        text = actions_to_jsonl(acts)
        line_count = len(text.splitlines())
        # Assert
        assert line_count == expected_count

    def test_actions_to_jsonl_first_line_keeps_tool_name_field(self, rich_session):
        """First emitted JSON object preserves `tool_name == 'Bash'`."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_jsonl(acts)
        first = json.loads(text.splitlines()[0])
        # Assert
        assert first["tool_name"] == "Bash"

    def test_actions_to_jsonl_first_line_keeps_command_field(self, rich_session):
        """First emitted JSON object preserves `command == 'ls /tmp'`."""
        # Arrange
        acts = extract_actions(rich_session)
        # Act
        text = actions_to_jsonl(acts)
        first = json.loads(text.splitlines()[0])
        # Assert
        assert first["command"] == "ls /tmp"
