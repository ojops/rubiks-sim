"""Benchmark summaries must retain failures without manufacturing speedups."""

import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "suite", Path(__file__).resolve().parents[1] / "benchmarks/suite.py"
)
suite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(suite)


def row(name, seed, status="solved", nodes=100, depth=4, repeat=1):
    return {
        "heuristic_name": name,
        "repeat": repeat,
        "length": 4,
        "seed": seed,
        "status": status,
        "nodes": nodes,
        "elapsed_seconds": 0.1,
        "process_peak_rss_bytes": 1234,
        "solution_depth": depth if status == "solved" else None,
    }


def test_failed_comparisons_are_counted_but_not_used_as_speedups():
    rows = [
        row("basic", 0, nodes=100),
        row("pattern", 0, nodes=10),
        row("basic", 1, "node_limit"),
        row("pattern", 1, nodes=20),
    ]
    result = suite.summarize(rows)
    assert result["basic"]["attempts"] == 2
    assert result["basic"]["statuses"] == {"solved": 1, "node_limit": 1}
    assert result["paired_node_ratio"] == {
        "count": 1,
        "median": 10,
        "min": 10,
        "max": 10,
    }


def test_one_failed_repetition_excludes_entire_case_from_ratios():
    rows = [
        row("basic", 0),
        row("pattern", 0),
        row("basic", 0, "time_limit", repeat=2),
        row("pattern", 0, repeat=2),
    ]
    assert suite.summarize(rows)["paired_node_ratio"]["count"] == 0


def test_disagreeing_solution_depths_are_rejected():
    with pytest.raises(ValueError, match="optimal depth"):
        suite.summarize([row("basic", 0, depth=4), row("pattern", 0, depth=5)])


@pytest.mark.parametrize(
    "rows",
    [
        [],
        [row("basic", 0)],
        [row("basic", 0), row("pattern", 0, repeat=2)],
        [row("basic", 0), row("basic", 0), row("pattern", 0)],
    ],
)
def test_incomplete_or_duplicate_measurements_are_rejected(rows):
    with pytest.raises(ValueError):
        suite.summarize(rows)
