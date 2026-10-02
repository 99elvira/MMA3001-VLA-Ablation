# -*- coding: utf-8 -*-
"""Parsing functions for LIBERO evaluation logs.

This module extracts structured metrics from the raw text output of
`lerobot-eval` runs on the LIBERO-object benchmark.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from src.config import N_EPISODES


# ============================================================
# Data structure
# ============================================================
@dataclass
class ExperimentResult:
    """Structured result for a single ablation experiment."""
    key: str
    name: str
    file: Path
    success_count: int
    n_episodes: int
    success_rate: float
    task_successes: Dict[int, List[bool]]
    eval_s: Optional[float]
    eval_ep_s: Optional[float]
    avg_sum_reward: Optional[float]
    avg_max_reward: Optional[float]


# ============================================================
# Low-level text extraction
# ============================================================
def extract_balanced(
    text: str,
    start_idx: int,
    open_char: str,
    close_char: str,
) -> Optional[str]:
    """Extract the first balanced bracket expression after `start_idx`.

    Handles nested brackets and skips brackets that appear inside string
    literals, so paths such as 'D:/x/y' inside a dict do not break parsing.

    Args:
        text: Full log text.
        start_idx: Index to begin searching from.
        open_char: Opening bracket character, e.g. '{' or '['.
        close_char: Closing bracket character, e.g. '}' or ']'.

    Returns:
        The balanced substring including brackets, or None if not found.
    """
    i = text.find(open_char, start_idx)
    if i == -1:
        return None

    depth = 0
    in_str = False
    escape = False
    quote = None

    for j in range(i, len(text)):
        ch = text[j]

        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_str = False
        else:
            if ch in ("'", '"'):
                in_str = True
                quote = ch
            elif ch == open_char:
                depth += 1
            elif ch == close_char:
                depth -= 1
                if depth == 0:
                    return text[i : j + 1]

    return None


# ============================================================
# High-level parsing
# ============================================================
def parse_result_file(path: Path, key: str, name: str) -> ExperimentResult:
    """Parse a single `lerobot-eval` log file into an ExperimentResult.

    The parser looks for two blocks in the log:
      1. `Overall Aggregated Metrics: {...}`
      2. `Aggregated Metrics for per_task: [...]`

    Per-task successes are preferred because they preserve the per-task
    structure required for paired scatter plots. If per-task data is not
    available, the parser falls back to reconstructing the total success
    count from the overall `pc_success` metric.

    Args:
        path: Path to the log file.
        key: Experiment key, e.g. 'E0'.
        name: Experiment name, e.g. 'baseline'.

    Returns:
        A populated ExperimentResult.

    Raises:
        ValueError: If neither per-task nor overall metrics can be parsed.
    """
    text = path.read_text(encoding="utf-8", errors="ignore")

    overall = None
    per_task = None

    # --- Overall Aggregated Metrics ---
    idx = text.find("Overall Aggregated Metrics:")
    if idx != -1:
        brace_str = extract_balanced(text, idx, "{", "}")
        if brace_str:
            try:
                overall = ast.literal_eval(brace_str)
            except Exception as e:
                print(f"[WARN] failed to parse overall metrics in {path}: {e}")

    # --- Per-task Aggregated Metrics ---
    idx = text.find("Aggregated Metrics for per_task:")
    if idx != -1:
        bracket_str = extract_balanced(text, idx, "[", "]")
        if bracket_str:
            try:
                per_task = ast.literal_eval(bracket_str)
            except Exception as e:
                print(f"[WARN] failed to parse per_task metrics in {path}: {e}")

    # --- Extract per-task success booleans ---
    task_successes: Dict[int, List[bool]] = {}
    if per_task:
        for item in per_task:
            task_id = item.get("task_id")
            metrics = item.get("metrics", {})
            successes = metrics.get("successes")
            if task_id is not None and successes is not None:
                task_successes[int(task_id)] = [bool(x) for x in successes]

    # --- Compute totals ---
    if task_successes:
        all_successes = [s for lst in task_successes.values() for s in lst]
        success_count = sum(all_successes)
        n_episodes = len(all_successes)
    elif overall:
        n_episodes = int(overall.get("n_episodes", 0))
        pc = float(overall.get("pc_success", 0.0))
        if pc > 1.0:
            pc = pc / 100.0
        success_count = int(round(pc * n_episodes)) if n_episodes else 0
    else:
        raise ValueError(f"Cannot parse results from {path}")

    # --- Sanity check on episode count ---
    if n_episodes != N_EPISODES:
        print(f"[WARN] {key} n_episodes={n_episodes}, expected {N_EPISODES}")

    success_rate = success_count / n_episodes if n_episodes else float("nan")

    eval_s = overall.get("eval_s") if overall else None
    eval_ep_s = overall.get("eval_ep_s") if overall else None
    avg_sum_reward = overall.get("avg_sum_reward") if overall else None
    avg_max_reward = overall.get("avg_max_reward") if overall else None

    return ExperimentResult(
        key=key,
        name=name,
        file=path,
        success_count=success_count,
        n_episodes=n_episodes,
        success_rate=success_rate,
        task_successes=task_successes,
        eval_s=eval_s,
        eval_ep_s=eval_ep_s,
        avg_sum_reward=avg_sum_reward,
        avg_max_reward=avg_max_reward,
    )


def get_flat_successes(res: ExperimentResult) -> List[bool]:
    """Return a flat list of per-episode success booleans.

    Prefers per-task data when available. If per-task data was not parsed,
    reconstructs a list from the total success count (losing task structure).
    """
    if res.task_successes:
        return [s for lst in res.task_successes.values() for s in lst]
    return [True] * res.success_count + [False] * (
        res.n_episodes - res.success_count
    )