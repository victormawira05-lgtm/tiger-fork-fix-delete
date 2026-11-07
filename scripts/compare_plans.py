#!/usr/bin/env python3
"""Compare two PostgreSQL EXPLAIN (FORMAT JSON) plan files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_plan(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read JSON plan {path}: {exc}") from exc

    # psql -t may emit a JSON array directly; a wrapper object is also accepted.
    if isinstance(data, list) and data and isinstance(data[0], dict):
        data = data[0]
    if isinstance(data, dict) and "Plan" not in data and "plan" in data:
        data = data["plan"]
    if not isinstance(data, dict) or "Plan" not in data:
        raise ValueError(f"{path} does not contain an EXPLAIN JSON Plan object")
    return data


def walk(node: dict[str, Any]):
    yield node
    for child in node.get("Plans", []):
        if isinstance(child, dict):
            yield from walk(child)


def summarize(plan: dict[str, Any]) -> dict[str, Any]:
    root = plan["Plan"]
    nodes = list(walk(root))
    scans = [node.get("Node Type", "unknown") for node in nodes]
    return {
        "execution_ms": plan.get("Execution Time"),
        "planning_ms": plan.get("Planning Time"),
        "root_node": root.get("Node Type", "unknown"),
        "scan_nodes": scans,
        "shared_hit_blocks": sum(int(node.get("Shared Hit Blocks", 0)) for node in nodes),
        "shared_read_blocks": sum(int(node.get("Shared Read Blocks", 0)) for node in nodes),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path, help="baseline EXPLAIN JSON file")
    parser.add_argument("after", type=Path, help="updated EXPLAIN JSON file")
    args = parser.parse_args()

    try:
        before = summarize(load_plan(args.before))
        after = summarize(load_plan(args.after))
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    print("Before:")
    print(json.dumps(before, indent=2))
    print("After:")
    print(json.dumps(after, indent=2))

    if isinstance(before["execution_ms"], (int, float)) and isinstance(after["execution_ms"], (int, float)):
        delta = after["execution_ms"] - before["execution_ms"]
        percent = (delta / before["execution_ms"] * 100) if before["execution_ms"] else 0
        print(f"Execution time change: {delta:+.3f} ms ({percent:+.1f}%).")
        print("Compare repeated runs under similar cache/load conditions; one plan is not a benchmark.")
    else:
        print("Execution Time was not present in both plans; use EXPLAIN ANALYZE to collect it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
