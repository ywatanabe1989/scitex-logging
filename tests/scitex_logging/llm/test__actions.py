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
    def test_returns_one_action_per_tool_call(self, rich_session):
        acts = extract_actions(rich_session)
        names = [a.tool_name for a in acts]
        assert names == ["Bash", "Read", "Write", "Edit", "Grep", "Agent"]

    def test_pairs_tool_result_content(self, rich_session):
        acts = extract_actions(rich_session)
        bash = next(a for a in acts if a.tool_name == "Bash")
        # Bash has list-style result content (text blocks joined)
        assert "foo.py" in bash.result_content
        read = next(a for a in acts if a.tool_name == "Read")
        # Read has string-style result content
        assert read.result_content == "print('hello')"

    def test_pairs_structured_tooluseresult(self, rich_session):
        acts = extract_actions(rich_session)
        bash = next(a for a in acts if a.tool_name == "Bash")
        assert bash.stdout == "foo.py\nbar.py"
        assert bash.stderr == ""
        assert bash.exit_code == 0
        assert bash.interrupted is False
        assert bash.is_image is False

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            extract_actions(tmp_path / "missing.jsonl")

    def test_skips_blank_and_invalid_lines(self, tmp_path):
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
        acts = extract_actions(p)
        assert len(acts) == 1
        assert acts[0].tool_name == "Bash"

    def test_tool_result_with_non_string_content(self, tmp_path):
        """Defensive: content that is neither str nor list still resolves."""
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
        acts = extract_actions(p)
        assert acts[0].result_content == "42"


class TestActionProperties:
    def test_command(self):
        a = Action(tool_name="Bash", tool_input={"command": "ls -la"}, tool_use_id="x")
        assert a.command == "ls -la"

    def test_file_path(self):
        a = Action(tool_name="Read", tool_input={"file_path": "/x.py"}, tool_use_id="x")
        assert a.file_path == "/x.py"

    def test_description(self):
        a = Action(
            tool_name="Bash", tool_input={"description": "do X"}, tool_use_id="x"
        )
        assert a.description == "do X"

    def test_defaults_empty(self):
        a = Action(tool_name="Read", tool_input={}, tool_use_id="x")
        assert a.command == ""
        assert a.file_path == ""
        assert a.description == ""


class TestToDict:
    def test_omits_empty_optional_fields(self):
        a = Action(tool_name="Read", tool_input={}, tool_use_id="x")
        d = a.to_dict()
        assert d["tool_name"] == "Read"
        assert "command" not in d
        assert "stdout" not in d
        assert "exit_code" not in d

    def test_includes_populated_fields(self):
        a = Action(
            tool_name="Bash",
            tool_input={"command": "ls"},
            tool_use_id="x",
            stdout="foo",
            stderr="err",
            exit_code=0,
            result_content="rc",
        )
        d = a.to_dict()
        assert d["command"] == "ls"
        assert d["stdout"] == "foo"
        assert d["stderr"] == "err"
        assert d["exit_code"] == 0
        assert d["result_content"] == "rc"
        assert d["tool_input"] == {"command": "ls"}


class TestActionsToLog:
    def test_bash_section(self, rich_session):
        text = actions_to_log(extract_actions(rich_session))
        assert "Tool: Bash" in text
        assert "Cmd:  ls /tmp" in text
        assert "Desc: list tmp" in text

    def test_write_and_edit_sections(self, rich_session):
        text = actions_to_log(extract_actions(rich_session))
        assert "File: /tmp/out.py" in text
        assert "Old:  written" in text
        assert "New:  edited" in text

    def test_grep_section(self, rich_session):
        text = actions_to_log(extract_actions(rich_session))
        assert "Pattern: TODO" in text
        assert "Path: /tmp" in text

    def test_agent_section(self, rich_session):
        text = actions_to_log(extract_actions(rich_session))
        assert "Desc: deep search" in text
        assert "Agent: Explore" in text

    def test_truncates_long_stdout(self, rich_session):
        text = actions_to_log(extract_actions(rich_session), max_output=100)
        assert "[truncated," in text

    def test_includes_stderr(self, rich_session):
        text = actions_to_log(extract_actions(rich_session))
        assert "--- stderr ---" in text
        assert "warning: something" in text

    def test_unknown_tool_falls_back_to_inputs(self):
        a = Action(
            tool_name="MysteryTool",
            tool_input={"foo": "bar", "baz": "qux"},
            tool_use_id="x",
            timestamp="t",
        )
        text = actions_to_log([a])
        assert "foo: bar" in text
        assert "baz: qux" in text


class TestActionsToJsonl:
    def test_one_object_per_line(self, rich_session):
        text = actions_to_jsonl(extract_actions(rich_session))
        lines = text.splitlines()
        assert len(lines) == 6
        first = json.loads(lines[0])
        assert first["tool_name"] == "Bash"
        assert first["command"] == "ls /tmp"
