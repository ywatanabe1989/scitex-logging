"""Tests for scitex_logging.llm.__main__ CLI."""

from __future__ import annotations

import json
import sys
from unittest.mock import patch

import pytest

from scitex_logging.llm.__main__ import main


def _run(argv):
    """Run `main()` with patched argv. Returns (rc, captured_stdout)."""
    import contextlib
    import io

    buf = io.StringIO()
    with patch.object(sys, "argv", ["scitex_logging.llm.__main__", *argv]):
        with contextlib.redirect_stdout(buf):
            rc = main()
    return rc, buf.getvalue()


class TestRenderCommand:
    def test_default_output_alongside_session(self, rich_session, tmp_path):
        rc, out = _run(["render", str(rich_session)])
        assert rc == 0
        # Default output: <session>.html alongside session
        expected = rich_session.with_suffix(".html")
        assert expected.exists()
        assert "Rendered" in out

    def test_explicit_output(self, rich_session, tmp_path):
        target = tmp_path / "custom.html"
        rc, out = _run(["render", str(rich_session), "-o", str(target)])
        assert rc == 0
        assert target.exists()

    def test_render_open_flag(self, rich_session, tmp_path):
        target = tmp_path / "o.html"
        with patch("subprocess.Popen") as mock_popen:
            rc, _ = _run(["render", str(rich_session), "-o", str(target), "--open"])
        assert rc == 0
        mock_popen.assert_called_once()


class TestSummaryCommand:
    def test_summary_prints_json(self, rich_session):
        rc, out = _run(["summary", str(rich_session)])
        assert rc == 0
        data = json.loads(out)
        assert "total_entries" in data
        assert "total_tool_calls" in data


class TestDagCommand:
    def test_dag_prints_mermaid(self, rich_session):
        rc, out = _run(["dag", str(rich_session)])
        assert rc == 0
        assert out.startswith("graph TD")
        assert "-->" in out


class TestActionsCommand:
    def test_log_format(self, rich_session):
        rc, out = _run(["actions", str(rich_session)])
        assert rc == 0
        assert "Tool: Bash" in out

    def test_jsonl_format(self, rich_session):
        rc, out = _run(["actions", str(rich_session), "-f", "jsonl"])
        assert rc == 0
        first = json.loads(out.splitlines()[0])
        assert first["tool_name"] == "Bash"

    def test_json_format(self, rich_session):
        rc, out = _run(["actions", str(rich_session), "-f", "json"])
        assert rc == 0
        data = json.loads(out)
        assert isinstance(data, list)
        assert data[0]["tool_name"] == "Bash"

    def test_writes_output_file(self, rich_session, tmp_path):
        target = tmp_path / "acts.txt"
        rc, out = _run(["actions", str(rich_session), "-o", str(target)])
        assert rc == 0
        assert target.exists()
        assert "Written:" in out


class TestDashboardCommand:
    def test_writes_dashboard(self, claude_dir, tmp_path):
        target = tmp_path / "dash.html"
        rc, out = _run(
            ["dashboard", "-o", str(target), "--claude-dir", str(claude_dir)]
        )
        assert rc == 0
        assert target.exists()
        assert "Dashboard:" in out

    def test_dashboard_open_flag(self, claude_dir, tmp_path):
        target = tmp_path / "dash.html"
        with patch("subprocess.Popen") as mock_popen:
            rc, _ = _run(
                [
                    "dashboard",
                    "-o",
                    str(target),
                    "--claude-dir",
                    str(claude_dir),
                    "--open",
                ]
            )
        assert rc == 0
        mock_popen.assert_called_once()


class TestScriptsCommand:
    def test_writes_scripts_dir(self, rich_session, tmp_path):
        target = tmp_path / "scripts_out"
        rc, out = _run(
            [
                "scripts",
                str(rich_session),
                "-o",
                str(target),
                "--tools",
                "Bash,Write",
            ]
        )
        assert rc == 0
        assert target.exists()
        assert "Scripts:" in out
        assert (target / "INDEX.txt").exists()

    def test_scripts_open_flag(self, rich_session, tmp_path):
        target = tmp_path / "s_out"
        with patch("subprocess.Popen") as mock_popen:
            rc, _ = _run(
                [
                    "scripts",
                    str(rich_session),
                    "-o",
                    str(target),
                    "--open",
                ]
            )
        assert rc == 0
        mock_popen.assert_called_once()


class TestSpaCommand:
    def test_writes_spa(self, claude_dir, tmp_path):
        target = tmp_path / "spa.html"
        rc, out = _run(["spa", "-o", str(target), "--claude-dir", str(claude_dir)])
        assert rc == 0
        assert target.exists()
        assert "SPA:" in out

    def test_spa_open_flag(self, claude_dir, tmp_path):
        target = tmp_path / "spa.html"
        with patch("subprocess.Popen") as mock_popen:
            rc, _ = _run(
                [
                    "spa",
                    "-o",
                    str(target),
                    "--claude-dir",
                    str(claude_dir),
                    "--open",
                ]
            )
        assert rc == 0
        mock_popen.assert_called_once()


class TestMissingSubcommand:
    def test_no_subcommand_errors(self):
        with pytest.raises(SystemExit):
            _run([])
