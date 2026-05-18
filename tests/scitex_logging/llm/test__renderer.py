"""Tests for scitex_logging.llm._renderer."""

from __future__ import annotations

import json

from scitex_logging.llm._parser import load
from scitex_logging.llm._renderer import _fmt_tokens, render_html


class TestFmtTokens:
    def test_fmt_tokens_under_one_thousand_returns_plain_digits(self):
        """`_fmt_tokens(500)` returns the bare string `"500"`."""
        # Arrange
        n = 500
        # Act
        result = _fmt_tokens(n)
        # Assert
        assert result == "500"

    def test_fmt_tokens_one_thousand_plus_returns_k_suffix(self):
        """`_fmt_tokens(1500)` returns the abbreviated `"1.5K"`."""
        # Arrange
        n = 1500
        # Act
        result = _fmt_tokens(n)
        # Assert
        assert result == "1.5K"

    def test_fmt_tokens_million_plus_returns_m_suffix(self):
        """`_fmt_tokens(2_500_000)` returns the abbreviated `"2.5M"`."""
        # Arrange
        n = 2_500_000
        # Act
        result = _fmt_tokens(n)
        # Assert
        assert result == "2.5M"

    def test_fmt_tokens_zero_returns_string_zero(self):
        """`_fmt_tokens(0)` returns the bare string `"0"`."""
        # Arrange
        n = 0
        # Act
        result = _fmt_tokens(n)
        # Assert
        assert result == "0"


class TestRenderHtml:
    def test_render_html_writes_target_file_to_disk(self, rich_session, tmp_path):
        """`render_html(session, out)` writes the output file."""
        # Arrange
        out = tmp_path / "subdir" / "out.html"
        # Act
        result = render_html(load(rich_session), out)
        # Assert
        assert result.exists()

    def test_render_html_returns_resolved_path_of_output(
        self, rich_session, tmp_path
    ):
        """`render_html(session, out)` returns `out.resolve()`."""
        # Arrange
        out = tmp_path / "subdir" / "out.html"
        # Act
        result = render_html(load(rich_session), out)
        # Assert
        assert result == out.resolve()

    def test_render_html_output_includes_session_slug(self, rich_session, tmp_path):
        """Rendered HTML embeds the session slug `rich-slug`."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        # Assert
        assert "rich-slug" in text

    def test_render_html_output_includes_branch_meta_line(
        self, rich_session, tmp_path
    ):
        """Rendered HTML embeds the `Branch: develop` meta line."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        # Assert
        assert "Branch: develop" in text

    def test_render_html_output_includes_version_meta_line(
        self, rich_session, tmp_path
    ):
        """Rendered HTML embeds the `Version: 2.1.76` meta line."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        # Assert
        assert "Version: 2.1.76" in text

    def test_render_html_output_includes_entries_meta_label(
        self, rich_session, tmp_path
    ):
        """Rendered HTML embeds the `Entries:` meta label."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        # Assert
        assert "Entries:" in text

    def test_render_html_output_has_one_tool_header_per_tool_call(
        self, rich_session, tmp_path
    ):
        """Rendered HTML has at least 6 `tool-header` divs (one per tool)."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        header_count = text.count('class="tool-header"')
        # Assert
        assert header_count >= 6

    def test_render_html_output_lists_bash_tool_label(
        self, rich_session, tmp_path
    ):
        """Rendered HTML lists `>Bash<` for the Bash tool call."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        # Assert
        assert ">Bash<" in text

    def test_render_html_output_lists_write_tool_label(
        self, rich_session, tmp_path
    ):
        """Rendered HTML lists `>Write<` for the Write tool call."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        # Assert
        assert ">Write<" in text

    def test_render_html_output_lists_agent_tool_label(
        self, rich_session, tmp_path
    ):
        """Rendered HTML lists `>Agent<` for the Agent tool call."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        # Assert
        assert ">Agent<" in text

    def test_render_html_output_has_session_summary_section(
        self, rich_session, tmp_path
    ):
        """Rendered HTML has the `Session Summary` block."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        # Assert
        assert "Session Summary" in text

    def test_render_html_output_lists_user_turns_label(
        self, rich_session, tmp_path
    ):
        """Rendered HTML lists `User Turns` in the summary grid."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        # Assert
        assert "User Turns" in text

    def test_render_html_output_lists_assistant_turns_label(
        self, rich_session, tmp_path
    ):
        """Rendered HTML lists `Assistant Turns` in the summary grid."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        # Assert
        assert "Assistant Turns" in text

    def test_render_html_output_lists_total_tokens_label(
        self, rich_session, tmp_path
    ):
        """Rendered HTML lists `Total Tokens` in the summary grid."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        # Assert
        assert "Total Tokens" in text

    def test_render_html_output_lists_tool_usage_breakdown_label(
        self, rich_session, tmp_path
    ):
        """Rendered HTML lists `Tool Usage` breakdown when tool calls exist."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        # Assert
        assert "Tool Usage" in text

    def test_render_html_truncates_long_tool_result_stdout(
        self, rich_session, tmp_path
    ):
        """A 6000-char tool stdout is truncated and marked `(truncated)`."""
        # Arrange
        out = render_html(load(rich_session), tmp_path / "o.html")
        # Act
        text = out.read_text()
        # Assert
        assert "(truncated)" in text

    def test_render_html_does_not_emit_raw_script_tag(self, tmp_path):
        """Special characters in user content must be HTML-escaped."""
        # Arrange
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
        # Act
        text = out.read_text()
        # Assert
        assert "<script>alert(1)</script>" not in text  # escaped

    def test_render_html_emits_escaped_script_entity(self, tmp_path):
        """Special chars in user content emit `&lt;script&gt;` (escaped)."""
        # Arrange
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
        # Act
        text = out.read_text()
        # Assert
        assert "&lt;script&gt;" in text


def test_render_html_truncates_long_tool_input_command(tmp_path):
    """Tool input longer than the display cap gets truncated in display."""
    # Arrange
    big = "y" * 2500  # stx-allow: STX-NL001
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
    # Act
    text = out.read_text()
    # Assert
    assert "(truncated)" in text
