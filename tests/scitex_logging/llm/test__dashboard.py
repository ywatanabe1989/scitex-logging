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
    def test_decode_project_path_simple_starts_with_slash(self):
        """`_decode_project_path('-tmp-foo')` returns an absolute path."""
        # Arrange
        encoded = "-tmp-foo"
        # Act
        result = _decode_project_path(encoded)
        # Assert
        assert result.startswith("/")

    def test_decode_project_path_simple_contains_leaf_segment(self):
        """`_decode_project_path('-tmp-foo')` keeps the `foo` leaf segment."""
        # Arrange
        encoded = "-tmp-foo"
        # Act
        result = _decode_project_path(encoded)
        # Assert
        assert "foo" in result

    def test_decode_project_path_non_prefixed_returns_input_unchanged(self):
        """No leading `-` → the input string is returned verbatim."""
        # Arrange
        plain = "noprefix"
        # Act
        result = _decode_project_path(plain)
        # Assert
        assert result == plain

    def test_decode_project_path_existing_dir_consumed_greedily(self, tmp_path):
        """If a multi-segment dir exists, decoder picks the longest match."""
        # Arrange
        with_dashes = tmp_path / "with-dashes"
        with_dashes.mkdir()
        encoded = str(tmp_path / "with-dashes").replace("/", "-")
        # Act
        result = _decode_project_path(encoded)
        # Assert
        assert Path(result).exists()


class TestPeekSession:
    def test_peek_session_returns_non_none_for_real_file(self, claude_dir):
        """`_peek_session(path)` returns a dict (not None) for a real file."""
        # Arrange
        path = claude_dir / "projects" / "-tmp-projA" / "sess-a1.jsonl"
        # Act
        info = _peek_session(path)
        # Assert
        assert info is not None

    def test_peek_session_reports_session_id_field(self, claude_dir):
        """`_peek_session(...).session_id` matches the file's session id."""
        # Arrange
        path = claude_dir / "projects" / "-tmp-projA" / "sess-a1.jsonl"
        # Act
        info = _peek_session(path)
        # Assert
        assert info["session_id"] == "sess-a1"

    def test_peek_session_reports_slug_field(self, claude_dir):
        """`_peek_session(...).slug` matches the slug recorded in the file."""
        # Arrange
        path = claude_dir / "projects" / "-tmp-projA" / "sess-a1.jsonl"
        # Act
        info = _peek_session(path)
        # Assert
        assert info["slug"] == "a-slug"

    def test_peek_session_reports_version_field(self, claude_dir):
        """`_peek_session(...).version` matches the version in the file."""
        # Arrange
        path = claude_dir / "projects" / "-tmp-projA" / "sess-a1.jsonl"
        # Act
        info = _peek_session(path)
        # Assert
        assert info["version"] == "2.1.0"

    def test_peek_session_reports_git_branch_field(self, claude_dir):
        """`_peek_session(...).git_branch` matches the branch in the file."""
        # Arrange
        path = claude_dir / "projects" / "-tmp-projA" / "sess-a1.jsonl"
        # Act
        info = _peek_session(path)
        # Assert
        assert info["git_branch"] == "main"

    def test_peek_session_reports_total_entry_count(self, claude_dir):
        """`_peek_session(...).entry_count` is the total record count."""
        # Arrange
        path = claude_dir / "projects" / "-tmp-projA" / "sess-a1.jsonl"
        # Act
        info = _peek_session(path)
        # Assert
        assert info["entry_count"] == 2

    def test_peek_session_reports_user_entry_count(self, claude_dir):
        """`_peek_session(...).user_count` counts user-typed records."""
        # Arrange
        path = claude_dir / "projects" / "-tmp-projA" / "sess-a1.jsonl"
        # Act
        info = _peek_session(path)
        # Assert
        assert info["user_count"] == 1

    def test_peek_session_reports_assistant_entry_count(self, claude_dir):
        """`_peek_session(...).assistant_count` counts assistant records."""
        # Arrange
        path = claude_dir / "projects" / "-tmp-projA" / "sess-a1.jsonl"
        # Act
        info = _peek_session(path)
        # Assert
        assert info["assistant_count"] == 1

    def test_peek_session_reports_file_size_kb_non_negative(self, claude_dir):
        """`_peek_session(...).file_size_kb` is a non-negative number."""
        # Arrange
        path = claude_dir / "projects" / "-tmp-projA" / "sess-a1.jsonl"
        # Act
        info = _peek_session(path)
        # Assert
        assert info["file_size_kb"] >= 0

    def test_peek_session_reports_first_timestamp_present(self, claude_dir):
        """`_peek_session(...).first_timestamp` is truthy (non-empty)."""
        # Arrange
        path = claude_dir / "projects" / "-tmp-projA" / "sess-a1.jsonl"
        # Act
        info = _peek_session(path)
        # Assert
        assert info["first_timestamp"]

    def test_peek_session_reports_last_timestamp_present(self, claude_dir):
        """`_peek_session(...).last_timestamp` is truthy (non-empty)."""
        # Arrange
        path = claude_dir / "projects" / "-tmp-projA" / "sess-a1.jsonl"
        # Act
        info = _peek_session(path)
        # Assert
        assert info["last_timestamp"]

    def test_peek_session_empty_file_returns_none(self, claude_dir):
        """An empty `.jsonl` file makes `_peek_session(...)` return None."""
        # Arrange
        empty = claude_dir / "projects" / "-home-someone-projB" / "empty.jsonl"
        # Act
        info = _peek_session(empty)
        # Assert
        assert info is None

    def test_peek_session_missing_file_returns_none(self, tmp_path):
        """A nonexistent path makes `_peek_session(...)` return None."""
        # Arrange
        missing = tmp_path / "no.jsonl"
        # Act
        info = _peek_session(missing)
        # Assert
        assert info is None


class TestDiscoverSessions:
    def test_discover_sessions_groups_by_project_count(self, claude_dir):
        """`discover_sessions(...)` returns one entry per `projects/<dir>/`."""
        # Arrange
        root = claude_dir
        # Act
        projects = discover_sessions(root)
        # Assert
        assert len(projects) == 2

    def test_discover_sessions_collects_every_session_id(self, claude_dir):
        """`discover_sessions(...)` aggregates every `session_id` it finds."""
        # Arrange
        root = claude_dir
        # Act
        projects = discover_sessions(root)
        all_ids = {s["session_id"] for sessions in projects.values() for s in sessions}
        # Assert
        assert all_ids == {"sess-a1", "sess-b1"}

    def test_discover_sessions_missing_root_returns_empty_dict(self, tmp_path):
        """A nonexistent root returns the empty dict `{}`."""
        # Arrange
        root = tmp_path / "does-not-exist"
        # Act
        projects = discover_sessions(root)
        # Assert
        assert projects == {}

    def test_discover_sessions_skips_stray_files_in_projects_dir(self, claude_dir):
        """Stray files inside `projects/` are not surfaced as project names."""
        # Arrange
        projects = discover_sessions(claude_dir)
        # Act
        has_stray = any("stray" in name for name in projects)
        # Assert
        assert has_stray is False


class TestRenderDashboard:
    def test_render_dashboard_writes_output_file(self, claude_dir, tmp_path):
        """`render_dashboard(out, claude_dir)` writes the output path."""
        # Arrange
        out = tmp_path / "dash.html"
        # Act
        result = render_dashboard(out, claude_dir)
        # Assert
        assert result.exists()

    def test_render_dashboard_output_includes_title(self, claude_dir, tmp_path):
        """Rendered HTML includes the `Claude Code Dashboard` title text."""
        # Arrange
        out = tmp_path / "dash.html"
        # Act
        result = render_dashboard(out, claude_dir)
        text = result.read_text()
        # Assert
        assert "Claude Code Dashboard" in text

    def test_render_dashboard_output_reports_project_count(self, claude_dir, tmp_path):
        """Rendered HTML reports `2 projects` for a 2-project fixture."""
        # Arrange
        out = tmp_path / "dash.html"
        # Act
        result = render_dashboard(out, claude_dir)
        text = result.read_text()
        # Assert
        assert "2 projects" in text

    def test_render_dashboard_output_reports_session_count(self, claude_dir, tmp_path):
        """Rendered HTML reports `2 sessions` for a 2-session fixture."""
        # Arrange
        out = tmp_path / "dash.html"
        # Act
        result = render_dashboard(out, claude_dir)
        text = result.read_text()
        # Assert
        assert "2 sessions" in text

    def test_render_dashboard_output_includes_entries_badge_class(
        self, claude_dir, tmp_path
    ):
        """Rendered HTML carries the `badge badge-entries` CSS class."""
        # Arrange
        out = render_dashboard(tmp_path / "d.html", claude_dir)
        # Act
        text = out.read_text()
        # Assert
        assert "badge badge-entries" in text

    def test_render_dashboard_output_includes_size_badge_class(
        self, claude_dir, tmp_path
    ):
        """Rendered HTML carries the `badge badge-size` CSS class."""
        # Arrange
        out = render_dashboard(tmp_path / "d.html", claude_dir)
        # Act
        text = out.read_text()
        # Assert
        assert "badge badge-size" in text

    def test_render_dashboard_output_surfaces_first_slug(
        self, claude_dir, tmp_path
    ):
        """Rendered HTML surfaces the first session's slug (`a-slug`)."""
        # Arrange
        out = render_dashboard(tmp_path / "d.html", claude_dir)
        # Act
        text = out.read_text()
        # Assert
        assert "a-slug" in text

    def test_render_dashboard_output_surfaces_second_slug(
        self, claude_dir, tmp_path
    ):
        """Rendered HTML surfaces the second session's slug (`b-slug`)."""
        # Arrange
        out = render_dashboard(tmp_path / "d.html", claude_dir)
        # Act
        text = out.read_text()
        # Assert
        assert "b-slug" in text

    def test_render_dashboard_empty_root_reports_zero_projects(self, tmp_path):
        """An empty claude_dir produces `0 projects` in the HTML."""
        # Arrange
        empty = tmp_path / "empty-claude"
        empty.mkdir()
        out = render_dashboard(tmp_path / "e.html", empty)
        # Act
        text = out.read_text()
        # Assert
        assert "0 projects" in text

    def test_render_dashboard_empty_root_reports_zero_sessions(self, tmp_path):
        """An empty claude_dir produces `0 sessions` in the HTML."""
        # Arrange
        empty = tmp_path / "empty-claude"
        empty.mkdir()
        out = render_dashboard(tmp_path / "e.html", empty)
        # Act
        text = out.read_text()
        # Assert
        assert "0 sessions" in text
