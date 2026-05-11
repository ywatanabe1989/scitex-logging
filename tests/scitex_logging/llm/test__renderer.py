"""Tests for scitex_logging.llm._renderer."""

from __future__ import annotations

from scitex_logging.llm._parser import load
from scitex_logging.llm._renderer import _fmt_tokens, render_html


class TestFmtTokens:
    def test_under_1k(self):
        assert _fmt_tokens(500) == "500"

    def test_k_suffix(self):
        assert _fmt_tokens(1500) == "1.5K"

    def test_m_suffix(self):
        assert _fmt_tokens(2_500_000) == "2.5M"

    def test_zero(self):
        assert _fmt_tokens(0) == "0"


class TestRenderHtml:
    def test_writes_file(self, rich_session, tmp_path):
        out = tmp_path / "subdir" / "out.html"
        result = render_html(load(rich_session), out)
        assert result.exists()
        # Auto-creates parent dirs
        assert result == out.resolve()

    def test_contains_meta(self, rich_session, tmp_path):
        out = render_html(load(rich_session), tmp_path / "o.html")
        text = out.read_text()
        assert "rich-slug" in text
        assert "Branch: develop" in text
        assert "Version: 2.1.76" in text
        assert "Entries:" in text

    def test_contains_tool_calls(self, rich_session, tmp_path):
        out = render_html(load(rich_session), tmp_path / "o.html")
        text = out.read_text()
        # tool-header divs for each tool
        assert text.count('class="tool-header"') >= 6
        assert ">Bash<" in text
        assert ">Write<" in text
        assert ">Agent<" in text

    def test_summary_grid(self, rich_session, tmp_path):
        out = render_html(load(rich_session), tmp_path / "o.html")
        text = out.read_text()
        assert "Session Summary" in text
        assert "User Turns" in text
        assert "Assistant Turns" in text
        assert "Total Tokens" in text
        # Tool usage breakdown present (has tool calls)
        assert "Tool Usage" in text

    def test_truncates_long_tool_result(self, rich_session, tmp_path):
        out = render_html(load(rich_session), tmp_path / "o.html")
        text = out.read_text()
        # 6000 char stdout in fixture → truncated at 5000
        assert "(truncated)" in text

    def test_escapes_html(self, tmp_path):
        """Special chars in user content must be escaped."""
        import json

        entries = [
            {
                "type": "user",
                "uuid": "u",
                "parentUuid": "",
                "timestamp": "t",
                "sessionId": "s",
                "slug": "<script>alert(1)</script>",
                "version": "1",
                "gitBranch": "x",
                "message": {"role": "user", "content": "<b>hi</b>"},
            },
        ]
        p = tmp_path / "x.jsonl"
        with open(p, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        out = render_html(load(p), tmp_path / "o.html")
        text = out.read_text()
        assert "<script>alert(1)</script>" not in text  # escaped
        assert "&lt;script&gt;" in text


def test_render_input_truncation(tmp_path):
    """Tool input longer than 2000 chars gets truncated in display."""
    import json

    big = "y" * 2500
    entries = [
        {
            "type": "user",
            "uuid": "u",
            "parentUuid": "",
            "timestamp": "t",
            "sessionId": "s",
            "slug": "s",
            "version": "1",
            "gitBranch": "x",
            "message": {"role": "user", "content": "go"},
        },
        {
            "type": "assistant",
            "uuid": "a",
            "parentUuid": "u",
            "timestamp": "t",
            "sessionId": "s",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "tu",
                        "name": "Bash",
                        "input": {"command": big},
                    }
                ],
                "model": "m",
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        },
    ]
    p = tmp_path / "b.jsonl"
    with open(p, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    out = render_html(load(p), tmp_path / "o.html")
    text = out.read_text()
    assert "(truncated)" in text
