"""Shared fixtures for scitex_logging.llm tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def _write_jsonl(entries: list[dict], path: Path) -> Path:
    with open(path, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    return path


@pytest.fixture
def rich_session(tmp_path):
    """Session with mixed tool types: Bash, Write, Edit, Read, Grep, Agent."""
    entries = [
        {
            "type": "user",
            "uuid": "u1",
            "parentUuid": "",
            "timestamp": "2026-04-01T10:00:00Z",
            "sessionId": "rich-session-001",
            "slug": "rich-slug",
            "version": "2.1.76",
            "gitBranch": "develop",
            "message": {"role": "user", "content": "do many things"},
        },
        # Assistant turn with two tool calls (Bash + Read)
        {
            "type": "assistant",
            "uuid": "a1",
            "parentUuid": "u1",
            "timestamp": "2026-04-01T10:00:05Z",
            "sessionId": "rich-session-001",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "running ls and reading a file"},
                    {
                        "type": "tool_use",
                        "id": "tu_bash",
                        "name": "Bash",
                        "input": {"command": "ls /tmp", "description": "list tmp"},
                    },
                    {
                        "type": "tool_use",
                        "id": "tu_read",
                        "name": "Read",
                        "input": {"file_path": "/tmp/foo.py"},
                    },
                ],
                "model": "claude-opus-4-7",
                "usage": {
                    "input_tokens": 200,
                    "output_tokens": 100,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 0,
                },
            },
        },
        # tool_result for Bash with structured toolUseResult
        {
            "type": "user",
            "uuid": "u2",
            "parentUuid": "a1",
            "timestamp": "2026-04-01T10:00:06Z",
            "sessionId": "rich-session-001",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tu_bash",
                        "content": [{"type": "text", "text": "foo.py\nbar.py"}],
                    }
                ],
            },
            "toolUseResult": {
                "stdout": "foo.py\nbar.py",
                "stderr": "",
                "exit_code": 0,
                "interrupted": False,
                "isImage": False,
            },
        },
        # tool_result for Read (string content)
        {
            "type": "user",
            "uuid": "u3",
            "parentUuid": "u2",
            "timestamp": "2026-04-01T10:00:07Z",
            "sessionId": "rich-session-001",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tu_read",
                        "content": "print('hello')",
                    }
                ],
            },
        },
        # Assistant: Write + Edit + Grep + Agent
        {
            "type": "assistant",
            "uuid": "a2",
            "parentUuid": "u3",
            "timestamp": "2026-04-01T10:00:10Z",
            "sessionId": "rich-session-001",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "tu_write",
                        "name": "Write",
                        "input": {
                            "file_path": "/tmp/out.py",
                            "content": "print('written')\n",
                        },
                    },
                    {
                        "type": "tool_use",
                        "id": "tu_edit",
                        "name": "Edit",
                        "input": {
                            "file_path": "/tmp/out.py",
                            "old_string": "written",
                            "new_string": "edited",
                        },
                    },
                    {
                        "type": "tool_use",
                        "id": "tu_grep",
                        "name": "Grep",
                        "input": {"pattern": "TODO", "path": "/tmp"},
                    },
                    {
                        "type": "tool_use",
                        "id": "tu_agent",
                        "name": "Agent",
                        "input": {
                            "description": "deep search",
                            "subagent_type": "Explore",
                            "prompt": "find stuff",
                        },
                    },
                ],
                "model": "claude-opus-4-7",
                "usage": {
                    "input_tokens": 300,
                    "output_tokens": 80,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 0,
                },
            },
        },
        # tool_result for Write with large stdout (truncation test)
        {
            "type": "user",
            "uuid": "u4",
            "parentUuid": "a2",
            "timestamp": "2026-04-01T10:00:11Z",
            "sessionId": "rich-session-001",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tu_write",
                        "content": [{"type": "text", "text": "x" * 6000}],
                    }
                ],
            },
            "toolUseResult": {
                "stdout": "x" * 6000,
                "stderr": "warning: something",
                "exit_code": 0,
                "interrupted": False,
                "isImage": False,
            },
        },
    ]
    return _write_jsonl(entries, tmp_path / "rich.jsonl")


@pytest.fixture
def claude_dir(tmp_path):
    """Mock ~/.claude directory with two projects and two sessions."""
    root = tmp_path / ".claude"
    projects = root / "projects"
    projects.mkdir(parents=True)

    proj_a = projects / "-tmp-projA"
    proj_a.mkdir()
    proj_b = projects / "-home-someone-projB"
    proj_b.mkdir()

    s1 = [
        {
            "type": "user",
            "uuid": "u",
            "parentUuid": "",
            "timestamp": "2026-04-02T10:00:00Z",
            "sessionId": "sess-a1",
            "slug": "a-slug",
            "version": "2.1.0",
            "gitBranch": "main",
            "message": {"role": "user", "content": "hi"},
        },
        {
            "type": "assistant",
            "uuid": "a",
            "parentUuid": "u",
            "timestamp": "2026-04-02T10:00:01Z",
            "sessionId": "sess-a1",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "hi back"}],
                "model": "claude-opus-4-7",
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        },
    ]
    s2 = [
        {
            "type": "user",
            "uuid": "u",
            "parentUuid": "",
            "timestamp": "2026-04-03T10:00:00Z",
            "sessionId": "sess-b1",
            "slug": "b-slug",
            "version": "2.1.0",
            "gitBranch": "feat",
            "message": {"role": "user", "content": "yo"},
        },
    ]
    _write_jsonl(s1, proj_a / "sess-a1.jsonl")
    _write_jsonl(s2, proj_b / "sess-b1.jsonl")
    # Empty file — should be skipped
    (proj_b / "empty.jsonl").write_text("")
    # Stray non-dir entry inside projects — should be skipped
    (projects / "stray.txt").write_text("ignore me")

    return root
