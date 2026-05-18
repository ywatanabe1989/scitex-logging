"""Tests for scitex_logging.llm._dag."""

from __future__ import annotations

import json

from scitex_logging.llm._dag import build_dag, to_mermaid
from scitex_logging.llm._parser import load


def test_build_dag_nodes_count_matches_tool_calls(rich_session):
    """The DAG node list has one entry per tool call (6 in the fixture)."""
    # Arrange
    entries = load(rich_session)
    # Act
    dag = build_dag(entries)
    # Assert
    assert len(dag["nodes"]) == 6


def test_build_dag_node_name_order_matches_tool_call_order(rich_session):
    """DAG node names list the tool calls in chronological order."""
    # Arrange
    entries = load(rich_session)
    # Act
    dag = build_dag(entries)
    names = [n["name"] for n in dag["nodes"]]
    # Assert
    assert names == ["Bash", "Read", "Write", "Edit", "Grep", "Agent"]


def test_build_dag_edges_chain_sequentially_in_count(rich_session):
    """N tool calls produce N-1 chained edges (linear chain)."""
    # Arrange
    entries = load(rich_session)
    # Act
    dag = build_dag(entries)
    # Assert
    assert len(dag["edges"]) == 5


def test_build_dag_first_edge_chains_bash_to_read(rich_session):
    """The first edge chains the Bash node to the Read node."""
    # Arrange
    entries = load(rich_session)
    # Act
    dag = build_dag(entries)
    # Assert
    assert dag["edges"][0] == {"from": "tu_bash", "to": "tu_read"}


def test_build_dag_last_edge_chains_grep_to_agent(rich_session):
    """The last edge chains the Grep node to the Agent node."""
    # Arrange
    entries = load(rich_session)
    # Act
    dag = build_dag(entries)
    # Assert
    assert dag["edges"][-1] == {"from": "tu_grep", "to": "tu_agent"}


def test_build_dag_first_node_id_is_tu_bash(rich_session):
    """The first DAG node's id is `tu_bash` (from the fixture)."""
    # Arrange
    entries = load(rich_session)
    # Act
    dag = build_dag(entries)
    # Assert
    assert dag["nodes"][0]["id"] == "tu_bash"


def test_build_dag_first_node_name_is_bash(rich_session):
    """The first DAG node's `name` is `Bash` (from the fixture)."""
    # Arrange
    entries = load(rich_session)
    # Act
    dag = build_dag(entries)
    # Assert
    assert dag["nodes"][0]["name"] == "Bash"


def test_build_dag_first_node_timestamp_is_non_empty(rich_session):
    """The first DAG node's `timestamp` is non-empty (truthy)."""
    # Arrange
    entries = load(rich_session)
    # Act
    dag = build_dag(entries)
    # Assert
    assert dag["nodes"][0]["timestamp"]  # non-empty


def test_to_mermaid_emits_graph_td_header(rich_session):
    """`to_mermaid(...)` emits the `graph TD` header on its first line."""
    # Arrange
    entries = load(rich_session)
    # Act
    text = to_mermaid(entries)
    first_line = text.splitlines()[0]
    # Assert
    assert first_line == "graph TD"


def test_to_mermaid_emits_quoted_bash_node_label(rich_session):
    """`to_mermaid(...)` emits at least one `"Bash"` quoted node label."""
    # Arrange
    entries = load(rich_session)
    # Act
    text = to_mermaid(entries)
    has_bash_node = any('"Bash"' in line for line in text.splitlines())
    # Assert
    assert has_bash_node is True


def test_to_mermaid_emits_edge_arrow_syntax(rich_session):
    """`to_mermaid(...)` emits at least one `-->` edge line."""
    # Arrange
    entries = load(rich_session)
    # Act
    text = to_mermaid(entries)
    has_arrow = any("-->" in line for line in text.splitlines())
    # Assert
    assert has_arrow is True


def test_to_mermaid_rewrites_dashes_in_first_node_id(tmp_path):
    """`to_mermaid(...)` rewrites `-` to `_` in the first dashed id."""
    # Arrange
    entries_payload = [
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
        for e in entries_payload:
            f.write(json.dumps(e) + "\n")
    # Act
    text = to_mermaid(load(p))
    # Assert
    assert "tu_with_dashes_1" in text


def test_to_mermaid_rewrites_dashes_in_second_node_id(tmp_path):
    """`to_mermaid(...)` rewrites `-` to `_` in the second dashed id."""
    # Arrange
    entries_payload = [
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
        for e in entries_payload:
            f.write(json.dumps(e) + "\n")
    # Act
    text = to_mermaid(load(p))
    # Assert
    assert "tu_with_dashes_2" in text


def test_to_mermaid_removes_dash_form_completely_from_output(tmp_path):
    """`to_mermaid(...)` removes every occurrence of `tu-with-dashes` text."""
    # Arrange
    entries_payload = [
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
        for e in entries_payload:
            f.write(json.dumps(e) + "\n")
    # Act
    text = to_mermaid(load(p))
    # Assert
    assert "tu-with-dashes" not in text


def test_build_dag_empty_session_returns_empty_node_edge_dict(tmp_path):
    """A session with no tool calls produces `{'nodes': [], 'edges': []}`."""
    # Arrange
    entries_payload = [
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
        for e in entries_payload:
            f.write(json.dumps(e) + "\n")
    # Act
    dag = build_dag(load(p))
    # Assert
    assert dag == {"nodes": [], "edges": []}


def test_to_mermaid_empty_session_returns_header_only_text(tmp_path):
    """A session with no tool calls produces just the `graph TD` header."""
    # Arrange
    entries_payload = [
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
        for e in entries_payload:
            f.write(json.dumps(e) + "\n")
    # Act
    text = to_mermaid(load(p))
    # Assert
    assert text == "graph TD"
