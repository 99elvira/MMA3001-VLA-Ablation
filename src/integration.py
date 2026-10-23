"""Analyse the later N=20/40 task-level integration-step experiments.

This is a closed-loop success/runtime comparison, not a fixed-input solver
convergence test. Run ``python -m src.integration`` from the repository root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

from src.config import RESULTS_DIR
from src.parser import parse_result_file, paired_successes
from src.statistics import exact_mcnemar, holm_adjust, wilson_ci


def recorded_steps(path: Path) -> int:
    """Read the unique runtime override, rather than the earlier default.

    Args:
        path: Complete evaluator log with an explicit override message.
    Returns:
        Positive integration-step count recorded at runtime.
    Raises:
        ValueError: The override is absent, conflicting or nonpositive.
    """
    values = {int(n) for n in re.findall(
        r"\[ABLATION\] Set num_steps to (\d+)",
        path.read_text(encoding="utf-8", errors="replace"))}
    if len(values) != 1 or next(iter(values)) <= 0:
        raise ValueError("Require one unambiguous positive runtime step override")
    return values.pop()


def analyse_steps(directory: Path) -> tuple[pd.DataFrame, dict]:
    """Validate full logs and extracts, and compare ordered episodes to E0.

    Args:
        directory: Results directory containing baseline and integration logs.
    Returns:
        Summary table and provenance dictionary including original-file hashes.
    Raises:
        ValueError: Step labels, extracts, times or outcome pairings disagree.
    """
    baseline_path = directory / "baseline_results.txt"
    baseline = parse_result_file(baseline_path, "N10", "existing E0 reference")
    runs = [(10, baseline, baseline_path)]
    sources = [baseline_path]
    for n in (20, 40):
        full = directory / "integration" / f"E0_steps{n}.txt"
        extract = directory / "integration" / f"N={n}.txt"
        if recorded_steps(full) != n:
            raise ValueError("Filename and runtime override disagree")
        result = parse_result_file(full, f"N{n}", f"Euler N={n}")
        copy = parse_result_file(extract, f"N{n}_extract", "same run extract")
        if (result.task_successes, result.eval_s, result.eval_ep_s) != (
                copy.task_successes, copy.eval_s, copy.eval_ep_s):
            raise ValueError("Full log and aggregate extract disagree")
        runs.append((n, result, full))
        sources.extend([full, extract])
    rows = []
    outcomes = []
    for n, result, path in runs:
        if result.n_episodes != 30 or result.eval_ep_s is None or result.eval_ep_s <= 0:
            raise ValueError("Require 30 outcomes and positive end-to-end time")
        lo, hi = wilson_ci(result.success_count, result.n_episodes)
        loss, gain, p = (None, None, None) if n == 10 else exact_mcnemar(
            *paired_successes(baseline, result))
        rows.append(dict(integration_steps=n, success_count=result.success_count,
                         n_episodes=result.n_episodes,
                         success_rate_pct=100 * result.success_rate,
                         wilson_ci_lower_pct=100 * lo, wilson_ci_upper_pct=100 * hi,
                         eval_ep_s=result.eval_ep_s,
                         time_ratio_vs_N10=result.eval_ep_s / baseline.eval_ep_s,
                         baseline_only=loss, condition_only=gain, mcnemar_p=p,
                         source=str(path.relative_to(directory)).replace("\\", "/")))
        outcomes.extend(dict(integration_steps=n, task_id=t, episode_index=i, success=s)
                        for t in sorted(result.task_successes)
                        for i, s in enumerate(result.task_successes[t]))
    table = pd.DataFrame(rows)
    table.loc[table.integration_steps != 10, "holm_adjusted_p"] = holm_adjust(
        table.loc[table.integration_steps != 10, "mcnemar_p"].tolist())
    manifest = dict(
        files=[dict(path=str(p.relative_to(directory)).replace("\\", "/"),
                    sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)
               for p in sources],
        distinct_new_runs=2, aggregate_extracts_are_not_repetitions=True,
        baseline_is_reused_not_rerun=True,
        timing="End-to-end eval_ep_s; not isolated inference latency",
        matching="Task ID and ordered episode; exact initial states/noise not archived",
        convergence="No fixed-input action differences or numerical error estimates supplied",
        outcomes=outcomes)
    return table, manifest


def plot_steps(table: pd.DataFrame, output: Path) -> None:
    """Save two aligned evidence plots without a misleading dual axis.

    Args:
        table: Validated rows from ``analyse_steps``.
        output: PNG destination. Parent directory must exist.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({"font.family": ["Times New Roman", "DejaVu Serif"], "font.size": 12})
    fig, (left, right) = plt.subplots(1, 2, figsize=(11.8, 4.1), constrained_layout=True)
    x = np.arange(len(table))
    rates = table.success_rate_pct.to_numpy()
    left.bar(x, rates, color="#5579AE", width=0.55)
    left.errorbar(x, rates, yerr=np.array([rates-table.wilson_ci_lower_pct,
                     table.wilson_ci_upper_pct-rates]), fmt="none", color="#172F50", capsize=5)
    left.set(xticks=x, xticklabels=table.integration_steps, ylim=(0, 108),
             xlabel="Integration steps N", ylabel="Task success (%)",
             title="Success with Wilson 95% intervals")
    for i, row in table.iterrows():
        left.text(i, 52, f"{int(row.success_count)}/30\n({row.success_rate_pct:.2f}%)",
                  ha="center", color="white", weight="bold")
    right.bar(x, table.eval_ep_s, color="#5579AE", width=0.55)
    right.set(xticks=x, xticklabels=table.integration_steps, ylim=(0, 365),
              xlabel="Integration steps N", ylabel="Mean seconds per episode",
              title="End-to-end evaluation time")
    for i, row in table.iterrows():
        right.text(i, row.eval_ep_s+8, f"{row.eval_ep_s:.2f} s\n{row.time_ratio_vs_N10:.2f}x",
                   ha="center", fontsize=11)
    for ax in (left, right):
        ax.spines[["top", "right"]].set_visible(False)
        ax.yaxis.grid(True, alpha=.2)
        ax.set_axisbelow(True)
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main(argv=None) -> None:
    """Regenerate step-study CSV, provenance, ordered outcomes and figure.

    Args:
        argv: Optional command-line arguments with input/output directories.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    output = args.output_dir or args.results_dir
    output.mkdir(parents=True, exist_ok=True)
    table, manifest = analyse_steps(args.results_dir)
    table.to_csv(output / "integration_summary.csv", index=False)
    pd.DataFrame(manifest.pop("outcomes")).to_csv(output / "integration_outcomes.csv", index=False)
    (output / "integration_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (output / "figures").mkdir(exist_ok=True)
    plot_steps(table, output / "figures/integration_steps.png")
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
