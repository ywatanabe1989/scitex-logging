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
    def test_safe_name_bash_uses_first_token_basename(self):
        """`_safe_name(Bash, '/usr/bin/ls -la /tmp')` returns `"ls"`."""
        # Arrange
        a = Action(
            tool_name="Bash",
            tool_input={"command": "/usr/bin/ls -la /tmp"},
            tool_use_id="x",
        )
        # Act
        result = _safe_name(a)
        # Assert
        assert result == "ls"

    def test_safe_name_bash_empty_command_returns_cmd_fallback(self):
        """`_safe_name(Bash, {})` falls back to the literal `"cmd"`."""
        # Arrange
        a = Action(tool_name="Bash", tool_input={}, tool_use_id="x")
        # Act
        result = _safe_name(a)
        # Assert
        assert result == "cmd"

    def test_safe_name_write_uses_file_path_stem(self):
        """`_safe_name(Write, file_path='/a/b/output.py')` returns `"output"`."""
        # Arrange
        a = Action(
            tool_name="Write",
            tool_input={"file_path": "/a/b/output.py"},
            tool_use_id="x",
        )
        # Act
        result = _safe_name(a)
        # Assert
        assert result == "output"

    def test_safe_name_falls_back_to_description_without_spaces(self):
        """The description-fallback name strips internal spaces out."""
        # Arrange
        a = Action(
            tool_name="Agent",
            tool_input={"description": "my long description with spaces"},
            tool_use_id="x",
        )
        # Act
        result = _safe_name(a)
        # Assert
        assert " " not in result

    def test_safe_name_description_fallback_respects_length_cap(self):
        """The description-fallback name is clamped to ≤30 characters."""
        # Arrange
        a = Action(
            tool_name="Agent",
            tool_input={"description": "my long description with spaces"},
            tool_use_id="x",
        )
        # Act
        result = _safe_name(a)
        max_length = 30
        # Assert
        assert len(result) <= max_length


class TestActionToScript:
    def test_bash_script_starts_with_shebang(self):
        """`_action_to_script(Bash, ...)` starts with `#!/bin/bash`."""
        # Arrange
        a = Action(
            tool_name="Bash",
            tool_input={"command": "echo hi", "description": "say hi"},
            tool_use_id="t1",
            timestamp="2026-01-01T00:00:00Z",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert s.startswith("#!/bin/bash")

    def test_bash_script_includes_pipefail_directive(self):
        """`_action_to_script(Bash, ...)` emits `set -euo pipefail`."""
        # Arrange
        a = Action(
            tool_name="Bash",
            tool_input={"command": "echo hi", "description": "say hi"},
            tool_use_id="t1",
            timestamp="2026-01-01T00:00:00Z",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "set -euo pipefail" in s

    def test_bash_script_embeds_command_payload(self):
        """`_action_to_script(Bash, ...)` embeds the supplied command."""
        # Arrange
        a = Action(
            tool_name="Bash",
            tool_input={"command": "echo hi", "description": "say hi"},
            tool_use_id="t1",
            timestamp="2026-01-01T00:00:00Z",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "echo hi" in s

    def test_bash_script_embeds_description_comment(self):
        """`_action_to_script(Bash, ...)` emits the description as a comment."""
        # Arrange
        a = Action(
            tool_name="Bash",
            tool_input={"command": "echo hi", "description": "say hi"},
            tool_use_id="t1",
            timestamp="2026-01-01T00:00:00Z",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "# Description: say hi" in s

    def test_bash_script_embeds_tool_id_comment(self):
        """`_action_to_script(Bash, ...)` emits the tool id as a comment."""
        # Arrange
        a = Action(
            tool_name="Bash",
            tool_input={"command": "echo hi", "description": "say hi"},
            tool_use_id="t1",
            timestamp="2026-01-01T00:00:00Z",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "# Tool ID: t1" in s

    def test_bash_empty_command_emits_placeholder_comment(self):
        """`_action_to_script(Bash, {})` emits `# (empty command)`."""
        # Arrange
        a = Action(tool_name="Bash", tool_input={}, tool_use_id="x")
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "# (empty command)" in s

    def test_write_script_uses_heredoc_opening_line(self):
        """`_action_to_script(Write, ...)` opens with `cat > '...' << ...`."""
        # Arrange
        a = Action(
            tool_name="Write",
            tool_input={"file_path": "/tmp/x.py", "content": "print(1)"},
            tool_use_id="x",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "cat > '/tmp/x.py' << 'SCITEX_EOF'" in s

    def test_write_script_embeds_content_payload(self):
        """`_action_to_script(Write, ...)` embeds the supplied content."""
        # Arrange
        a = Action(
            tool_name="Write",
            tool_input={"file_path": "/tmp/x.py", "content": "print(1)"},
            tool_use_id="x",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "print(1)" in s

    def test_write_script_uses_heredoc_terminator(self):
        """`_action_to_script(Write, ...)` closes with the `SCITEX_EOF` marker."""
        # Arrange
        a = Action(
            tool_name="Write",
            tool_input={"file_path": "/tmp/x.py", "content": "print(1)"},
            tool_use_id="x",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "SCITEX_EOF" in s

    def test_edit_script_invokes_python_interpreter(self):
        """`_action_to_script(Edit, ...)` invokes `python3 -c`."""
        # Arrange
        a = Action(
            tool_name="Edit",
            tool_input={
                "file_path": "/tmp/x.py",
                "old_string": "foo",
                "new_string": "bar",
            },
            tool_use_id="x",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "python3 -c" in s

    def test_edit_script_embeds_old_string(self):
        """`_action_to_script(Edit, ...)` embeds the old-string payload."""
        # Arrange
        a = Action(
            tool_name="Edit",
            tool_input={
                "file_path": "/tmp/x.py",
                "old_string": "foo",
                "new_string": "bar",
            },
            tool_use_id="x",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "foo" in s

    def test_edit_script_embeds_new_string(self):
        """`_action_to_script(Edit, ...)` embeds the new-string payload."""
        # Arrange
        a = Action(
            tool_name="Edit",
            tool_input={
                "file_path": "/tmp/x.py",
                "old_string": "foo",
                "new_string": "bar",
            },
            tool_use_id="x",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "bar" in s

    def test_read_only_tool_emits_marker_comment(self):
        """`_action_to_script(Read, ...)` opens with a `# Read (read-only` line."""
        # Arrange
        a = Action(
            tool_name="Read",
            tool_input={"file_path": "/tmp/x.py"},
            tool_use_id="x",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "# Read (read-only" in s

    def test_read_only_tool_records_file_path_comment(self):
        """`_action_to_script(Read, ...)` records the file path as a comment."""
        # Arrange
        a = Action(
            tool_name="Read",
            tool_input={"file_path": "/tmp/x.py"},
            tool_use_id="x",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "# file_path: /tmp/x.py" in s

    def test_unknown_tool_emits_tool_name_comment(self):
        """For an unknown tool, the script opens with a `# Tool:` comment."""
        # Arrange
        a = Action(
            tool_name="WeirdTool",
            tool_input={"a": "1", "b": "2"},
            tool_use_id="x",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "# Tool: WeirdTool" in s

    def test_unknown_tool_records_first_input_pair_comment(self):
        """For an unknown tool, the first input pair is emitted as comment."""
        # Arrange
        a = Action(
            tool_name="WeirdTool",
            tool_input={"a": "1", "b": "2"},
            tool_use_id="x",
        )
        # Act
        s = _action_to_script(a, 1)
        # Assert
        assert "# a: 1" in s


class TestExportScripts:
    def test_export_scripts_default_tools_emits_one_script(
        self, rich_session, tmp_path
    ):
        """`export_scripts(...)` with default tools writes 1 `.sh` file."""
        # Arrange
        out = export_scripts(rich_session, tmp_path / "scripts")
        # Act
        scripts = sorted(out.glob("[0-9]*.sh"))
        # Assert
        assert len(scripts) == 1

    def test_export_scripts_default_tool_emits_executable_script(
        self, rich_session, tmp_path
    ):
        """`export_scripts(...)` writes the script with its IXUSR bit set."""
        # Arrange
        out = export_scripts(rich_session, tmp_path / "scripts")
        scripts = sorted(out.glob("[0-9]*.sh"))
        # Act
        mode = scripts[0].stat().st_mode
        executable_bit = mode & stat.S_IEXEC
        # Assert
        assert executable_bit != 0

    def test_export_scripts_filters_by_supplied_tool_set(
        self, rich_session, tmp_path
    ):
        """`export_scripts(..., tools=(...))` writes 1 script per matching tool."""
        # Arrange
        out = export_scripts(
            rich_session, tmp_path / "s2", tools=("Bash", "Write", "Edit")
        )
        # Act
        scripts = sorted(out.glob("[0-9]*.sh"))
        # Assert
        assert len(scripts) == 3

    def test_export_scripts_writes_index_txt_manifest(
        self, rich_session, tmp_path
    ):
        """`export_scripts(...)` writes an `INDEX.txt` manifest."""
        # Arrange
        out = export_scripts(rich_session, tmp_path / "s3", tools=("Bash",))
        # Act
        manifest = out / "INDEX.txt"
        # Assert
        assert manifest.exists()

    def test_export_scripts_writes_run_all_shell_script(
        self, rich_session, tmp_path
    ):
        """`export_scripts(...)` writes a `run_all.sh` driver script."""
        # Arrange
        out = export_scripts(rich_session, tmp_path / "s3", tools=("Bash",))
        # Act
        driver = out / "run_all.sh"
        # Assert
        assert driver.exists()

    def test_export_scripts_writes_index_html_summary(
        self, rich_session, tmp_path
    ):
        """`export_scripts(...)` writes an `index.html` summary file."""
        # Arrange
        out = export_scripts(rich_session, tmp_path / "s3", tools=("Bash",))
        # Act
        summary = out / "index.html"
        # Assert
        assert summary.exists()

    def test_export_scripts_run_all_starts_with_bash_shebang(
        self, rich_session, tmp_path
    ):
        """`run_all.sh` starts with the `#!/bin/bash` shebang."""
        # Arrange
        out = export_scripts(rich_session, tmp_path / "s3", tools=("Bash",))
        # Act
        run_all = (out / "run_all.sh").read_text()
        # Assert
        assert run_all.startswith("#!/bin/bash")

    def test_export_scripts_run_all_uses_pipefail_directive(
        self, rich_session, tmp_path
    ):
        """`run_all.sh` includes `set -euo pipefail`."""
        # Arrange
        out = export_scripts(rich_session, tmp_path / "s3", tools=("Bash",))
        # Act
        run_all = (out / "run_all.sh").read_text()
        # Assert
        assert "set -euo pipefail" in run_all

    def test_export_scripts_run_all_is_executable(self, rich_session, tmp_path):
        """`run_all.sh` has its IXUSR executable bit set."""
        # Arrange
        out = export_scripts(rich_session, tmp_path / "s3", tools=("Bash",))
        # Act
        mode = (out / "run_all.sh").stat().st_mode
        executable_bit = mode & stat.S_IEXEC
        # Assert
        assert executable_bit != 0

    def test_export_scripts_index_html_includes_session_title(
        self, rich_session, tmp_path
    ):
        """`index.html` includes the title `Session Actions`."""
        # Arrange
        out = export_scripts(
            rich_session, tmp_path / "s4", tools=("Bash", "Write", "Edit")
        )
        # Act
        html_text = (out / "index.html").read_text()
        # Assert
        assert "Session Actions" in html_text

    def test_export_scripts_index_html_reports_action_count(
        self, rich_session, tmp_path
    ):
        """`index.html` reports `3 actions` for three exported scripts."""
        # Arrange
        out = export_scripts(
            rich_session, tmp_path / "s4", tools=("Bash", "Write", "Edit")
        )
        # Act
        html_text = (out / "index.html").read_text()
        # Assert
        assert "3 actions" in html_text

    def test_export_scripts_index_html_reports_bash_count(
        self, rich_session, tmp_path
    ):
        """`index.html` reports `1 Bash commands` (Bash-class breakdown)."""
        # Arrange
        out = export_scripts(
            rich_session, tmp_path / "s4", tools=("Bash", "Write", "Edit")
        )
        # Act
        html_text = (out / "index.html").read_text()
        # Assert
        assert "1 Bash commands" in html_text

    def test_export_scripts_index_html_lists_write_file_label(
        self, rich_session, tmp_path
    ):
        """`index.html` lists `File: /tmp/out.py` for the Write action."""
        # Arrange
        out = export_scripts(
            rich_session, tmp_path / "s4", tools=("Bash", "Write", "Edit")
        )
        # Act
        html_text = (out / "index.html").read_text()
        # Assert
        assert "File: /tmp/out.py" in html_text
