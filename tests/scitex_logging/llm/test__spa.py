"""Tests for scitex_logging.llm._spa."""

from __future__ import annotations

import json
import re

from scitex_logging.llm._spa import _serialize_session, _truncate_input, render_spa


class TestTruncateInput:
    def test_long_string_truncated(self):
        result = _truncate_input({"k": "x" * 100}, max_len=10)
        assert result["k"] == "x" * 10 + "..."

    def test_short_string_unchanged(self):
        result = _truncate_input({"k": "abc"}, max_len=10)
        assert result["k"] == "abc"

    def test_non_string_passthrough(self):
        result = _truncate_input({"k": 123, "j": [1, 2, 3]}, max_len=10)
        assert result["k"] == 123
        assert result["j"] == [1, 2, 3]


class TestSerializeSession:
    def test_basic_shape(self, rich_session):
        info = {"path": rich_session, "first_timestamp": "ts", "last_timestamp": "ts2"}
        data = _serialize_session(info, max_output=5000)
        assert data is not None
        assert data["id"] == "rich-session-001"
        assert data["slug"] == "rich-slug"
        assert data["git_branch"] == "develop"
        assert "stats" in data
        assert data["stats"]["tool_calls"] == 6
        assert len(data["actions"]) == 6

    def test_handles_load_failure(self, tmp_path):
        bad = tmp_path / "broken.jsonl"
        bad.write_text("not valid json\n")
        info = {"path": bad}
        # load() succeeds with no entries; extract_actions also returns []
        # _serialize_session returns a valid dict, not None
        data = _serialize_session(info)
        assert data is not None
        assert data["actions"] == []

    def test_missing_file_returns_none(self, tmp_path):
        info = {"path": tmp_path / "missing.jsonl"}
        assert _serialize_session(info) is None

    def test_truncates_long_output(self, rich_session):
        info = {"path": rich_session}
        data = _serialize_session(info, max_output=100)
        # The Bash result content was "foo.py\nbar.py" (short), but Write
        # had 6000 chars — find that action
        for a in data["actions"]:
            if a["tool_name"] == "Write":
                assert len(a["stdout"]) <= 100
                break


class TestRenderSpa:
    def test_writes_html(self, claude_dir, tmp_path):
        out = render_spa(tmp_path / "spa.html", claude_dir)
        assert out.exists()
        text = out.read_text()
        assert "Claude Code Sessions" in text
        # Embedded JSON
        assert 'id="app-data"' in text

    def test_escapes_closing_script(self, tmp_path):
        """Ensure </script> in serialized data does not break out of <script>."""
        # Create a session whose content contains </script>
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
        # The literal </script> from the data should be escaped.
        # The only legitimate </script> closes the data block + closes the JS block (2).
        # Total </script> count must be exactly the 2 structural closers.
        assert len(re.findall(r"</script>", text)) == 2

    def test_per_project_session_limit(self, tmp_path):
        """max_sessions_per_project caps how many sessions are fully serialized."""
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
        out = render_spa(tmp_path / "spa.html", claude, max_sessions_per_project=2)
        text = out.read_text()
        # Pull the embedded JSON
        m = re.search(
            r'<script id="app-data" type="application/json">(.*?)</script>',
            text,
            flags=re.S,
        )
        assert m is not None
        # The JSON has </ replaced; reverse-replace for parsing
        raw = m.group(1).replace("<\\u002f", "</")
        data = json.loads(raw)
        proj_data = next(iter(data["projects"].values()))
        assert len(proj_data["sessions"]) == 2

    def test_per_session_entry_cap(self, tmp_path):
        """max_entries_per_session truncates entries and marks truncated."""
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
        out = render_spa(tmp_path / "spa.html", claude, max_entries_per_session=5)
        text = out.read_text()
        m = re.search(
            r'<script id="app-data" type="application/json">(.*?)</script>',
            text,
            flags=re.S,
        )
        raw = m.group(1).replace("<\\u002f", "</")
        data = json.loads(raw)
        sess = next(iter(data["projects"].values()))["sessions"][0]
        assert len(sess["entries"]) == 5
        assert sess["truncated"] is True
