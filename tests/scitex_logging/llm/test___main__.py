"""Tests for scitex_logging.llm.__main__ CLI.

The original `--open` flag tests asserted on mocked `subprocess.Popen`
calls (pure mock-on-internals theater). They were removed per the
no-mocks doctrine: see `general/02_package_12_no-mocks.md` §"When the
replacement feels too expensive". `--open` itself is still wired in
production; integration coverage for the spawn happens at the demo /
smoke level rather than via a behaviour-on-`Popen` assertion.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
from contextlib import contextmanager

import pytest

from scitex_logging.llm.__main__ import main


@contextmanager
def _swap_argv(new_argv):
    """Save / restore ``sys.argv`` around a CLI invocation."""
    old = sys.argv
    sys.argv = new_argv
    try:
        yield
    finally:
        sys.argv = old


def _run(argv):
    """Run ``main()`` with patched argv. Returns (rc, captured_stdout)."""
    buf = io.StringIO()
    prog_argv = ["scitex_logging.llm.__main__", *argv]
    with _swap_argv(prog_argv):
        with contextlib.redirect_stdout(buf):
            rc = main()
    return rc, buf.getvalue()


class TestRenderCommand:
    def test_render_default_output_exit_code_zero(self, rich_session, tmp_path):
        """`render <session>` exits 0 with no `-o` flag."""
        # Arrange
        argv = ["render", str(rich_session)]
        # Act
        rc, _ = _run(argv)
        # Assert
        assert rc == 0

    def test_render_default_output_writes_html_alongside_session(
        self, rich_session, tmp_path
    ):
        """`render <session>` writes `<session>.html` alongside the session."""
        # Arrange
        argv = ["render", str(rich_session)]
        # Act
        _run(argv)
        expected = rich_session.with_suffix(".html")
        # Assert
        assert expected.exists()

    def test_render_default_output_reports_rendered_keyword(
        self, rich_session, tmp_path
    ):
        """`render <session>` prints `Rendered` to stdout."""
        # Arrange
        argv = ["render", str(rich_session)]
        # Act
        _, out = _run(argv)
        # Assert
        assert "Rendered" in out

    def test_render_explicit_output_exit_code_zero(self, rich_session, tmp_path):
        """`render <session> -o <out>` exits 0."""
        # Arrange
        target = tmp_path / "custom.html"
        argv = ["render", str(rich_session), "-o", str(target)]
        # Act
        rc, _ = _run(argv)
        # Assert
        assert rc == 0

    def test_render_explicit_output_writes_target_file(self, rich_session, tmp_path):
        """`render <session> -o <out>` writes the explicit target path."""
        # Arrange
        target = tmp_path / "custom.html"
        argv = ["render", str(rich_session), "-o", str(target)]
        # Act
        _run(argv)
        # Assert
        assert target.exists()


class TestSummaryCommand:
    def test_summary_command_exit_code_is_zero(self, rich_session):
        """`summary <session>` exits 0."""
        # Arrange
        argv = ["summary", str(rich_session)]
        # Act
        rc, _ = _run(argv)
        # Assert
        assert rc == 0

    def test_summary_command_output_includes_total_entries_key(self, rich_session):
        """`summary <session>` prints JSON containing `total_entries`."""
        # Arrange
        argv = ["summary", str(rich_session)]
        # Act
        _, out = _run(argv)
        data = json.loads(out)
        # Assert
        assert "total_entries" in data

    def test_summary_command_output_includes_total_tool_calls_key(self, rich_session):
        """`summary <session>` prints JSON containing `total_tool_calls`."""
        # Arrange
        argv = ["summary", str(rich_session)]
        # Act
        _, out = _run(argv)
        data = json.loads(out)
        # Assert
        assert "total_tool_calls" in data


class TestDagCommand:
    def test_dag_command_exit_code_is_zero(self, rich_session):
        """`dag <session>` exits 0."""
        # Arrange
        argv = ["dag", str(rich_session)]
        # Act
        rc, _ = _run(argv)
        # Assert
        assert rc == 0

    def test_dag_command_output_starts_with_graph_td_header(self, rich_session):
        """`dag <session>` prints mermaid output starting with `graph TD`."""
        # Arrange
        argv = ["dag", str(rich_session)]
        # Act
        _, out = _run(argv)
        # Assert
        assert out.startswith("graph TD")

    def test_dag_command_output_includes_edge_arrow_syntax(self, rich_session):
        """`dag <session>` prints at least one `-->` edge line."""
        # Arrange
        argv = ["dag", str(rich_session)]
        # Act
        _, out = _run(argv)
        # Assert
        assert "-->" in out


class TestActionsCommand:
    def test_actions_log_format_exit_code_zero(self, rich_session):
        """`actions <session>` (log format) exits 0."""
        # Arrange
        argv = ["actions", str(rich_session)]
        # Act
        rc, _ = _run(argv)
        # Assert
        assert rc == 0

    def test_actions_log_format_includes_bash_header(self, rich_session):
        """`actions <session>` (log format) prints `Tool: Bash`."""
        # Arrange
        argv = ["actions", str(rich_session)]
        # Act
        _, out = _run(argv)
        # Assert
        assert "Tool: Bash" in out

    def test_actions_jsonl_format_exit_code_zero(self, rich_session):
        """`actions <session> -f jsonl` exits 0."""
        # Arrange
        argv = ["actions", str(rich_session), "-f", "jsonl"]
        # Act
        rc, _ = _run(argv)
        # Assert
        assert rc == 0

    def test_actions_jsonl_format_first_line_keeps_tool_name(self, rich_session):
        """`actions <session> -f jsonl` first line has `tool_name == 'Bash'`."""
        # Arrange
        argv = ["actions", str(rich_session), "-f", "jsonl"]
        # Act
        _, out = _run(argv)
        first = json.loads(out.splitlines()[0])
        # Assert
        assert first["tool_name"] == "Bash"

    def test_actions_json_format_exit_code_zero(self, rich_session):
        """`actions <session> -f json` exits 0."""
        # Arrange
        argv = ["actions", str(rich_session), "-f", "json"]
        # Act
        rc, _ = _run(argv)
        # Assert
        assert rc == 0

    def test_actions_json_format_returns_top_level_list(self, rich_session):
        """`actions <session> -f json` top-level JSON is a list."""
        # Arrange
        argv = ["actions", str(rich_session), "-f", "json"]
        # Act
        _, out = _run(argv)
        data = json.loads(out)
        # Assert
        assert isinstance(data, list)

    def test_actions_json_format_first_item_keeps_tool_name(self, rich_session):
        """`actions <session> -f json` first item has `tool_name == 'Bash'`."""
        # Arrange
        argv = ["actions", str(rich_session), "-f", "json"]
        # Act
        _, out = _run(argv)
        data = json.loads(out)
        # Assert
        assert data[0]["tool_name"] == "Bash"

    def test_actions_writes_explicit_output_file_exit_zero(
        self, rich_session, tmp_path
    ):
        """`actions <session> -o <path>` exits 0."""
        # Arrange
        target = tmp_path / "acts.txt"
        argv = ["actions", str(rich_session), "-o", str(target)]
        # Act
        rc, _ = _run(argv)
        # Assert
        assert rc == 0

    def test_actions_writes_explicit_output_file_to_disk(
        self, rich_session, tmp_path
    ):
        """`actions <session> -o <path>` writes the explicit target file."""
        # Arrange
        target = tmp_path / "acts.txt"
        argv = ["actions", str(rich_session), "-o", str(target)]
        # Act
        _run(argv)
        # Assert
        assert target.exists()

    def test_actions_writes_explicit_output_reports_written_prefix(
        self, rich_session, tmp_path
    ):
        """`actions <session> -o <path>` prints `Written:` to stdout."""
        # Arrange
        target = tmp_path / "acts.txt"
        argv = ["actions", str(rich_session), "-o", str(target)]
        # Act
        _, out = _run(argv)
        # Assert
        assert "Written:" in out


class TestDashboardCommand:
    def test_dashboard_writes_target_html_exit_zero(self, claude_dir, tmp_path):
        """`dashboard -o <html> --claude-dir <dir>` exits 0."""
        # Arrange
        target = tmp_path / "dash.html"
        argv = ["dashboard", "-o", str(target), "--claude-dir", str(claude_dir)]
        # Act
        rc, _ = _run(argv)
        # Assert
        assert rc == 0

    def test_dashboard_writes_target_html_file_to_disk(self, claude_dir, tmp_path):
        """`dashboard -o <html> --claude-dir <dir>` writes the target HTML."""
        # Arrange
        target = tmp_path / "dash.html"
        argv = ["dashboard", "-o", str(target), "--claude-dir", str(claude_dir)]
        # Act
        _run(argv)
        # Assert
        assert target.exists()

    def test_dashboard_writes_target_html_reports_dashboard_prefix(
        self, claude_dir, tmp_path
    ):
        """`dashboard -o <html> --claude-dir <dir>` prints `Dashboard:`."""
        # Arrange
        target = tmp_path / "dash.html"
        argv = ["dashboard", "-o", str(target), "--claude-dir", str(claude_dir)]
        # Act
        _, out = _run(argv)
        # Assert
        assert "Dashboard:" in out


class TestScriptsCommand:
    def test_scripts_writes_target_dir_exit_zero(self, rich_session, tmp_path):
        """`scripts <session> -o <dir> --tools Bash,Write` exits 0."""
        # Arrange
        target = tmp_path / "scripts_out"
        argv = [
            "scripts",
            str(rich_session),
            "-o",
            str(target),
            "--tools",
            "Bash,Write",
        ]
        # Act
        rc, _ = _run(argv)
        # Assert
        assert rc == 0

    def test_scripts_writes_target_dir_to_disk(self, rich_session, tmp_path):
        """`scripts <session> -o <dir>` creates the target directory."""
        # Arrange
        target = tmp_path / "scripts_out"
        argv = [
            "scripts",
            str(rich_session),
            "-o",
            str(target),
            "--tools",
            "Bash,Write",
        ]
        # Act
        _run(argv)
        # Assert
        assert target.exists()

    def test_scripts_writes_target_dir_reports_scripts_prefix(
        self, rich_session, tmp_path
    ):
        """`scripts <session> -o <dir>` prints `Scripts:` to stdout."""
        # Arrange
        target = tmp_path / "scripts_out"
        argv = [
            "scripts",
            str(rich_session),
            "-o",
            str(target),
            "--tools",
            "Bash,Write",
        ]
        # Act
        _, out = _run(argv)
        # Assert
        assert "Scripts:" in out

    def test_scripts_writes_target_dir_includes_index_file(
        self, rich_session, tmp_path
    ):
        """`scripts <session> -o <dir>` writes an `INDEX.txt` inside the dir."""
        # Arrange
        target = tmp_path / "scripts_out"
        argv = [
            "scripts",
            str(rich_session),
            "-o",
            str(target),
            "--tools",
            "Bash,Write",
        ]
        # Act
        _run(argv)
        index_path = target / "INDEX.txt"
        # Assert
        assert index_path.exists()


class TestSpaCommand:
    def test_spa_writes_target_html_exit_zero(self, claude_dir, tmp_path):
        """`spa -o <html> --claude-dir <dir>` exits 0."""
        # Arrange
        target = tmp_path / "spa.html"
        argv = ["spa", "-o", str(target), "--claude-dir", str(claude_dir)]
        # Act
        rc, _ = _run(argv)
        # Assert
        assert rc == 0

    def test_spa_writes_target_html_file_to_disk(self, claude_dir, tmp_path):
        """`spa -o <html> --claude-dir <dir>` writes the target HTML file."""
        # Arrange
        target = tmp_path / "spa.html"
        argv = ["spa", "-o", str(target), "--claude-dir", str(claude_dir)]
        # Act
        _run(argv)
        # Assert
        assert target.exists()

    def test_spa_writes_target_html_reports_spa_prefix(
        self, claude_dir, tmp_path
    ):
        """`spa -o <html> --claude-dir <dir>` prints `SPA:` to stdout."""
        # Arrange
        target = tmp_path / "spa.html"
        argv = ["spa", "-o", str(target), "--claude-dir", str(claude_dir)]
        # Act
        _, out = _run(argv)
        # Assert
        assert "SPA:" in out


class TestMissingSubcommand:
    def test_main_with_empty_argv_raises_system_exit(self):
        """Running `main()` with no subcommand argv raises SystemExit."""
        # Arrange
        argv: list[str] = []
        # Act
        # Assert
        with pytest.raises(SystemExit):
            _run(argv)
