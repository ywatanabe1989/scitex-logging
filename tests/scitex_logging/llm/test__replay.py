"""Tests for scitex_logging.llm._replay."""

from __future__ import annotations

import stat

from scitex_logging.llm._actions import Action
from scitex_logging.llm._replay import (
    _action_to_script,
    _safe_name,
    export_scripts,
)


class TestSafeName:
    def test_bash_uses_first_token_basename(self):
        a = Action(
            tool_name="Bash",
            tool_input={"command": "/usr/bin/ls -la /tmp"},
            tool_use_id="x",
        )
        assert _safe_name(a) == "ls"

    def test_bash_empty_command(self):
        a = Action(tool_name="Bash", tool_input={}, tool_use_id="x")
        assert _safe_name(a) == "cmd"

    def test_file_path_uses_stem(self):
        a = Action(
            tool_name="Write",
            tool_input={"file_path": "/a/b/output.py"},
            tool_use_id="x",
        )
        assert _safe_name(a) == "output"

    def test_falls_back_to_description(self):
        a = Action(
            tool_name="Agent",
            tool_input={"description": "my long description with spaces"},
            tool_use_id="x",
        )
        out = _safe_name(a)
        assert " " not in out
        assert len(out) <= 30


class TestActionToScript:
    def test_bash_script_has_shebang_and_pipefail(self):
        a = Action(
            tool_name="Bash",
            tool_input={"command": "echo hi", "description": "say hi"},
            tool_use_id="t1",
            timestamp="2026-01-01T00:00:00Z",
        )
        s = _action_to_script(a, 1)
        assert s.startswith("#!/bin/bash")
        assert "set -euo pipefail" in s
        assert "echo hi" in s
        assert "# Description: say hi" in s
        assert "# Tool ID: t1" in s

    def test_bash_empty_command_falls_through(self):
        a = Action(tool_name="Bash", tool_input={}, tool_use_id="x")
        s = _action_to_script(a, 1)
        assert "# (empty command)" in s

    def test_write_script_uses_heredoc(self):
        a = Action(
            tool_name="Write",
            tool_input={"file_path": "/tmp/x.py", "content": "print(1)"},
            tool_use_id="x",
        )
        s = _action_to_script(a, 1)
        assert "cat > '/tmp/x.py' << 'SCITEX_EOF'" in s
        assert "print(1)" in s
        assert "SCITEX_EOF" in s

    def test_edit_script_uses_python(self):
        a = Action(
            tool_name="Edit",
            tool_input={
                "file_path": "/tmp/x.py",
                "old_string": "foo",
                "new_string": "bar",
            },
            tool_use_id="x",
        )
        s = _action_to_script(a, 1)
        assert "python3 -c" in s
        assert "foo" in s
        assert "bar" in s

    def test_read_only_tool_just_comments(self):
        a = Action(
            tool_name="Read",
            tool_input={"file_path": "/tmp/x.py"},
            tool_use_id="x",
        )
        s = _action_to_script(a, 1)
        assert "# Read (read-only" in s
        assert "# file_path: /tmp/x.py" in s

    def test_unknown_tool_dumps_inputs(self):
        a = Action(
            tool_name="WeirdTool",
            tool_input={"a": "1", "b": "2"},
            tool_use_id="x",
        )
        s = _action_to_script(a, 1)
        assert "# Tool: WeirdTool" in s
        assert "# a: 1" in s


class TestExportScripts:
    def test_creates_executable_scripts(self, rich_session, tmp_path):
        out = export_scripts(rich_session, tmp_path / "scripts")
        # Default tools=("Bash",) → 1 script
        scripts = sorted(out.glob("[0-9]*.sh"))
        assert len(scripts) == 1
        # Executable
        mode = scripts[0].stat().st_mode
        assert mode & stat.S_IEXEC

    def test_filters_by_tool_set(self, rich_session, tmp_path):
        out = export_scripts(
            rich_session, tmp_path / "s2", tools=("Bash", "Write", "Edit")
        )
        scripts = sorted(out.glob("[0-9]*.sh"))
        # Bash + Write + Edit = 3
        assert len(scripts) == 3

    def test_writes_index_and_run_all(self, rich_session, tmp_path):
        out = export_scripts(rich_session, tmp_path / "s3", tools=("Bash",))
        assert (out / "INDEX.txt").exists()
        assert (out / "run_all.sh").exists()
        assert (out / "index.html").exists()
        run_all = (out / "run_all.sh").read_text()
        assert run_all.startswith("#!/bin/bash")
        assert "set -euo pipefail" in run_all
        # Executable
        assert (out / "run_all.sh").stat().st_mode & stat.S_IEXEC

    def test_html_index_content(self, rich_session, tmp_path):
        out = export_scripts(
            rich_session, tmp_path / "s4", tools=("Bash", "Write", "Edit")
        )
        html_text = (out / "index.html").read_text()
        assert "Session Actions" in html_text
        # Stats show the counts
        assert "3 actions" in html_text
        assert "1 Bash commands" in html_text
        # File path label
        assert "File: /tmp/out.py" in html_text
