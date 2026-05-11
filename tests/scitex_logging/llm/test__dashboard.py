"""Tests for scitex_logging.llm._dashboard."""

from __future__ import annotations

from pathlib import Path

from scitex_logging.llm._dashboard import (
    _decode_project_path,
    _peek_session,
    discover_sessions,
    render_dashboard,
)


class TestDecodeProjectPath:
    def test_simple_path(self):
        # No existing path resolution → falls back to 1-segment-at-a-time
        result = _decode_project_path("-tmp-foo")
        assert result.startswith("/")
        assert "foo" in result

    def test_non_prefixed_returns_input(self):
        assert _decode_project_path("noprefix") == "noprefix"

    def test_existing_path_consumed_greedily(self, tmp_path):
        """If a multi-segment dir exists, decoder picks the longest match."""
        # Build /tmp/<scoped>/with-dashes
        with_dashes = tmp_path / "with-dashes"
        with_dashes.mkdir()
        # Encode tmp_path as Claude would: '/' → '-'
        encoded = str(tmp_path / "with-dashes").replace("/", "-")
        result = _decode_project_path(encoded)
        assert Path(result).exists()


class TestPeekSession:
    def test_returns_metadata(self, claude_dir):
        path = claude_dir / "projects" / "-tmp-projA" / "sess-a1.jsonl"
        info = _peek_session(path)
        assert info is not None
        assert info["session_id"] == "sess-a1"
        assert info["slug"] == "a-slug"
        assert info["version"] == "2.1.0"
        assert info["git_branch"] == "main"
        assert info["entry_count"] == 2
        assert info["user_count"] == 1
        assert info["assistant_count"] == 1
        assert info["file_size_kb"] >= 0
        assert info["first_timestamp"]
        assert info["last_timestamp"]

    def test_empty_returns_none(self, claude_dir):
        empty = claude_dir / "projects" / "-home-someone-projB" / "empty.jsonl"
        assert _peek_session(empty) is None

    def test_missing_file_returns_none(self, tmp_path):
        assert _peek_session(tmp_path / "no.jsonl") is None


class TestDiscoverSessions:
    def test_groups_by_project(self, claude_dir):
        projects = discover_sessions(claude_dir)
        assert len(projects) == 2
        # Each project has its session
        all_ids = {s["session_id"] for sessions in projects.values() for s in sessions}
        assert all_ids == {"sess-a1", "sess-b1"}

    def test_missing_dir_returns_empty(self, tmp_path):
        assert discover_sessions(tmp_path / "does-not-exist") == {}

    def test_skips_non_directories(self, claude_dir):
        # Fixture put a stray file in projects/ — discover should ignore it
        projects = discover_sessions(claude_dir)
        for name in projects:
            assert "stray" not in name


class TestRenderDashboard:
    def test_writes_html(self, claude_dir, tmp_path):
        out = tmp_path / "dash.html"
        result = render_dashboard(out, claude_dir)
        assert result.exists()
        text = result.read_text()
        assert "Claude Code Dashboard" in text
        assert "2 projects" in text
        assert "2 sessions" in text

    def test_includes_session_badges(self, claude_dir, tmp_path):
        out = render_dashboard(tmp_path / "d.html", claude_dir)
        text = out.read_text()
        assert "badge badge-entries" in text
        assert "badge badge-size" in text
        # Slugs surface
        assert "a-slug" in text
        assert "b-slug" in text

    def test_empty_dashboard(self, tmp_path):
        """Render against a claude_dir with no projects/ subdir."""
        empty = tmp_path / "empty-claude"
        empty.mkdir()
        out = render_dashboard(tmp_path / "e.html", empty)
        text = out.read_text()
        assert "0 projects" in text
        assert "0 sessions" in text
