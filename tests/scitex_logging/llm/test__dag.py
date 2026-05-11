"""Tests for scitex_logging.llm._dag."""

from __future__ import annotations

from scitex_logging.llm._dag import build_dag, to_mermaid
from scitex_logging.llm._parser import load


def test_build_dag_nodes_and_edges(rich_session):
    dag = build_dag(load(rich_session))
    # 6 tool calls in fixture: Bash, Read, Write, Edit, Grep, Agent
    assert len(dag["nodes"]) == 6
    names = [n["name"] for n in dag["nodes"]]
    assert names == ["Bash", "Read", "Write", "Edit", "Grep", "Agent"]
    # Edges chain sequentially
    assert len(dag["edges"]) == 5
    assert dag["edges"][0] == {"from": "tu_bash", "to": "tu_read"}
    assert dag["edges"][-1] == {"from": "tu_grep", "to": "tu_agent"}


def test_build_dag_node_fields(rich_session):
    dag = build_dag(load(rich_session))
    first = dag["nodes"][0]
    assert first["id"] == "tu_bash"
    assert first["name"] == "Bash"
    assert first["timestamp"]  # non-empty


def test_to_mermaid_syntax(rich_session):
    text = to_mermaid(load(rich_session))
    lines = text.splitlines()
    assert lines[0] == "graph TD"
    # IDs that contain '-' get rewritten with '_'
    # Our fixture uses tu_bash (no dashes), so just verify nodes/edges format
    assert any('"Bash"' in line for line in lines)
    assert any("-->" in line for line in lines)


def test_to_mermaid_escapes_dashes(tmp_path):
    """IDs with dashes are rewritten to underscores for valid Mermaid."""
    import json

    entries = [
        {
            "type": "user",
            "uuid": "u",
            "parentUuid": "",
            "timestamp": "2026-04-01T10:00:00Z",
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
            "timestamp": "2026-04-01T10:00:01Z",
            "sessionId": "s",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "tu-with-dashes-1",
                        "name": "Bash",
                        "input": {"command": "echo"},
                    },
                    {
                        "type": "tool_use",
                        "id": "tu-with-dashes-2",
                        "name": "Read",
                        "input": {"file_path": "/x"},
                    },
                ],
                "model": "m",
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        },
    ]
    p = tmp_path / "d.jsonl"
    with open(p, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")

    text = to_mermaid(load(p))
    assert "tu_with_dashes_1" in text
    assert "tu_with_dashes_2" in text
    # Ensure the dash form is fully gone
    assert "tu-with-dashes" not in text


def test_build_dag_empty(tmp_path):
    """Session with no tool calls yields empty DAG."""
    import json

    entries = [
        {
            "type": "user",
            "uuid": "u",
            "parentUuid": "",
            "timestamp": "2026-04-01T10:00:00Z",
            "sessionId": "s",
            "slug": "",
            "version": "1",
            "gitBranch": "x",
            "message": {"role": "user", "content": "hi"},
        }
    ]
    p = tmp_path / "e.jsonl"
    with open(p, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    dag = build_dag(load(p))
    assert dag == {"nodes": [], "edges": []}
    assert to_mermaid(load(p)) == "graph TD"
