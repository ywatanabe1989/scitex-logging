"""Tests for scitex_logging.llm._spa."""

from __future__ import annotations

import json
import re

from scitex_logging.llm._spa import _serialize_session, _truncate_input, render_spa


class TestTruncateInput:
    def test_truncate_input_long_string_is_truncated_with_ellipsis(self):
        """A long string is truncated to `max_len` chars + `...` ellipsis."""
        # Arrange
        payload = {"k": "x" * 100}
        max_len = 10
        # Act
        result = _truncate_input(payload, max_len=max_len)
        # Assert
        assert result["k"] == "x" * max_len + "..."

    def test_truncate_input_short_string_unchanged(self):
        """A short string (≤max_len) is returned unchanged."""
        # Arrange
        payload = {"k": "abc"}
        # Act
        result = _truncate_input(payload, max_len=10)
        # Assert
        assert result["k"] == "abc"

    def test_truncate_input_int_value_passthrough(self):
        """Non-string scalar values pass through unchanged."""
        # Arrange
        payload = {"k": 123, "j": [1, 2, 3]}
        # Act
        result = _truncate_input(payload, max_len=10)
        # Assert
        assert result["k"] == 123

    def test_truncate_input_list_value_passthrough(self):
        """List values pass through unchanged."""
        # Arrange
        payload = {"k": 123, "j": [1, 2, 3]}
        # Act
        result = _truncate_input(payload, max_len=10)
        # Assert
        assert result["j"] == [1, 2, 3]


class TestSerializeSession:
    def test_serialize_session_returns_non_none_for_real_path(self, rich_session):
        """`_serialize_session({'path': real})` returns a non-None dict."""
        # Arrange
        info = {
            "path": rich_session,
            "first_timestamp": "ts",
            "last_timestamp": "ts2",
        }
        # Act
        data = _serialize_session(info, max_output=5000)
        # Assert
        assert data is not None

    def test_serialize_session_records_session_id_field(self, rich_session):
        """`_serialize_session(...)['id']` carries the JSONL `sessionId`."""
        # Arrange
        info = {
            "path": rich_session,
            "first_timestamp": "ts",
            "last_timestamp": "ts2",
        }
        # Act
        data = _serialize_session(info, max_output=5000)
        # Assert
        assert data["id"] == "rich-session-001"

    def test_serialize_session_records_slug_field(self, rich_session):
        """`_serialize_session(...)['slug']` carries the JSONL `slug`."""
        # Arrange
        info = {
            "path": rich_session,
            "first_timestamp": "ts",
            "last_timestamp": "ts2",
        }
        # Act
        data = _serialize_session(info, max_output=5000)
        # Assert
        assert data["slug"] == "rich-slug"

    def test_serialize_session_records_git_branch_field(self, rich_session):
        """`_serialize_session(...)['git_branch']` carries the JSONL branch."""
        # Arrange
        info = {
            "path": rich_session,
            "first_timestamp": "ts",
            "last_timestamp": "ts2",
        }
        # Act
        data = _serialize_session(info, max_output=5000)
        # Assert
        assert data["git_branch"] == "develop"

    def test_serialize_session_includes_stats_dict_key(self, rich_session):
        """`_serialize_session(...)['stats']` exists in the payload."""
        # Arrange
        info = {
            "path": rich_session,
            "first_timestamp": "ts",
            "last_timestamp": "ts2",
        }
        # Act
        data = _serialize_session(info, max_output=5000)
        # Assert
        assert "stats" in data

    def test_serialize_session_stats_tool_calls_count(self, rich_session):
        """`_serialize_session(...)['stats']['tool_calls']` is 6 in fixture."""
        # Arrange
        info = {
            "path": rich_session,
            "first_timestamp": "ts",
            "last_timestamp": "ts2",
        }
        # Act
        data = _serialize_session(info, max_output=5000)
        # Assert
        assert data["stats"]["tool_calls"] == 6

    def test_serialize_session_actions_list_length_matches_tool_count(
        self, rich_session
    ):
        """`_serialize_session(...)['actions']` has one entry per tool call."""
        # Arrange
        info = {
            "path": rich_session,
            "first_timestamp": "ts",
            "last_timestamp": "ts2",
        }
        # Act
        data = _serialize_session(info, max_output=5000)
        # Assert
        assert len(data["actions"]) == 6

    def test_serialize_session_returns_dict_for_broken_jsonl(self, tmp_path):
        """A non-JSON file yields a non-None dict with empty actions."""
        # Arrange
        bad = tmp_path / "broken.jsonl"
        bad.write_text("not valid json\n")
        info = {"path": bad}
        # Act
        data = _serialize_session(info)
        # Assert
        assert data is not None

    def test_serialize_session_broken_jsonl_actions_is_empty_list(self, tmp_path):
        """A non-JSON file yields `actions == []`."""
        # Arrange
        bad = tmp_path / "broken.jsonl"
        bad.write_text("not valid json\n")
        info = {"path": bad}
        # Act
        data = _serialize_session(info)
        # Assert
        assert data["actions"] == []

    def test_serialize_session_missing_file_returns_none(self, tmp_path):
        """A nonexistent path makes `_serialize_session(...)` return None."""
        # Arrange
        info = {"path": tmp_path / "missing.jsonl"}
        # Act
        result = _serialize_session(info)
        # Assert
        assert result is None

    def test_serialize_session_truncates_long_stdout_per_max_output(
        self, rich_session
    ):
        """`_serialize_session(max_output=100)` clamps long stdout fields."""
        # Arrange
        info = {"path": rich_session}
        max_output = 100  # stx-allow: STX-NL001
        # Act
        data = _serialize_session(info, max_output=max_output)
        write_actions = [a for a in data["actions"] if a["tool_name"] == "Write"]
        # Assert
        assert len(write_actions[0]["stdout"]) <= max_output


class TestRenderSpa:
    def test_render_spa_writes_target_html_file(self, claude_dir, tmp_path):
        """`render_spa(out, claude_dir)` writes the output HTML file."""
        # Arrange
        out = tmp_path / "spa.html"
        # Act
        result = render_spa(out, claude_dir)
        # Assert
        assert result.exists()

    def test_render_spa_output_includes_app_title(self, claude_dir, tmp_path):
        """Rendered SPA includes the `Claude Code Sessions` title."""
        # Arrange
        result = render_spa(tmp_path / "spa.html", claude_dir)
        # Act
        text = result.read_text()
        # Assert
        assert "Claude Code Sessions" in text

    def test_render_spa_output_embeds_app_data_script_id(
        self, claude_dir, tmp_path
    ):
        """Rendered SPA embeds the `<script id="app-data">` block."""
        # Arrange
        result = render_spa(tmp_path / "spa.html", claude_dir)
        # Act
        text = result.read_text()
        # Assert
        assert 'id="app-data"' in text

    def test_render_spa_escapes_closing_script_to_prevent_xss(self, tmp_path):
        """A `</script>` payload is escaped so only the two structural closers remain."""
        # Arrange
        claude = tmp_path / ".claude"
        proj = claude / "projects" / "-tmp-x"
        proj.mkdir(parents=True)
        entries = [
            {
                "type": "user",
                "uuid": "u",
                "parentUuid": "",
                "timestamp": "ts",
                "sessionId": "s",
                "slug": "evil",
                "version": "1",
                "gitBranch": "x",
                "message": {"role": "user", "content": "</script><b>xss</b>"},
            }
        ]
        with open(proj / "s.jsonl", "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        out = render_spa(tmp_path / "spa.html", claude)
        text = out.read_text()
        # Act
        count = len(re.findall(r"</script>", text))
        # Assert
        assert count == 2

    def test_render_spa_per_project_session_limit_caps_count(self, tmp_path):
        """`max_sessions_per_project=2` caps each project's session count."""
        # Arrange
        claude = tmp_path / ".claude"
        proj = claude / "projects" / "-tmp-many"
        proj.mkdir(parents=True)
        for i in range(5):
            entries = [
                {
                    "type": "user",
                    "uuid": f"u{i}",
                    "parentUuid": "",
                    "timestamp": f"2026-04-{i + 1:02d}T10:00:00Z",
                    "sessionId": f"sess-{i}",
                    "slug": f"slug-{i}",
                    "version": "1",
                    "gitBranch": "x",
                    "message": {"role": "user", "content": "hi"},
                }
            ]
            with open(proj / f"s{i}.jsonl", "w") as f:
                for e in entries:
                    f.write(json.dumps(e) + "\n")
        out = render_spa(
            tmp_path / "spa.html", claude, max_sessions_per_project=2
        )
        text = out.read_text()
        m = re.search(
            r'<script id="app-data" type="application/json">(.*?)</script>',
            text,
            flags=re.S,
        )
        raw = m.group(1).replace("<\\u002f", "</")
        data = json.loads(raw)
        proj_data = next(iter(data["projects"].values()))
        # Act
        session_count = len(proj_data["sessions"])
        # Assert
        assert session_count == 2

    def test_render_spa_per_session_entry_cap_truncates_count(self, tmp_path):
        """`max_entries_per_session=5` caps each session's entry count."""
        # Arrange
        claude = tmp_path / ".claude"
        proj = claude / "projects" / "-tmp-big"
        proj.mkdir(parents=True)
        entries = []
        for i in range(20):
            entries.append(
                {
                    "type": "user",
                    "uuid": f"u{i}",
                    "parentUuid": "",
                    "timestamp": f"2026-04-01T10:00:{i:02d}Z",
                    "sessionId": "big",
                    "slug": "big-slug",
                    "version": "1",
                    "gitBranch": "x",
                    "message": {"role": "user", "content": f"msg {i}"},
                }
            )
        with open(proj / "big.jsonl", "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        out = render_spa(
            tmp_path / "spa.html", claude, max_entries_per_session=5
        )
        text = out.read_text()
        m = re.search(
            r'<script id="app-data" type="application/json">(.*?)</script>',
            text,
            flags=re.S,
        )
        raw = m.group(1).replace("<\\u002f", "</")
        data = json.loads(raw)
        sess = next(iter(data["projects"].values()))["sessions"][0]
        # Act
        entry_count = len(sess["entries"])
        # Assert
        assert entry_count == 5

    def test_render_spa_per_session_entry_cap_sets_truncated_flag(self, tmp_path):
        """`max_entries_per_session=5` sets the session's `truncated` flag."""
        # Arrange
        claude = tmp_path / ".claude"
        proj = claude / "projects" / "-tmp-big2"
        proj.mkdir(parents=True)
        entries = []
        for i in range(20):
            entries.append(
                {
                    "type": "user",
                    "uuid": f"u{i}",
                    "parentUuid": "",
                    "timestamp": f"2026-04-01T10:00:{i:02d}Z",
                    "sessionId": "big",
                    "slug": "big-slug",
                    "version": "1",
                    "gitBranch": "x",
                    "message": {"role": "user", "content": f"msg {i}"},
                }
            )
        with open(proj / "big.jsonl", "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        out = render_spa(
            tmp_path / "spa.html", claude, max_entries_per_session=5
        )
        text = out.read_text()
        m = re.search(
            r'<script id="app-data" type="application/json">(.*?)</script>',
            text,
            flags=re.S,
        )
        raw = m.group(1).replace("<\\u002f", "</")
        data = json.loads(raw)
        sess = next(iter(data["projects"].values()))["sessions"][0]
        # Act
        is_truncated = sess["truncated"]
        # Assert
        assert is_truncated is True
