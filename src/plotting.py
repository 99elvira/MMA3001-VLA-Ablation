# -*- coding: utf-8 -*-
"""Plotting functions for the MMA3001 VLA ablation analysis."""

from __future__ import annotations

from typing import Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import FIG_DIR


def plot_ablation_success_bar(df: pd.DataFrame) -> None:
    """Bar chart with Wilson 95% CI and E0 baseline."""
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(df))
    rate = df["success_rate_pct"].values
    lower = df["wilson_ci_lower_pct"].values
    upper = df["wilson_ci_upper_pct"].values
    err = np.vstack([rate - lower, upper - rate])
    ax.bar(x, rate, yerr=err, capsize=5, color="steelblue", alpha=0.85)
    e0_rate = df.loc[df["key"] == "E0", "success_rate_pct"].values[0]
    ax.axhline(e0_rate, color="red", linestyle="--", linewidth=1.5, label="E0 baseline")
    ax.set_xticks(x)
    ax.set_xticklabels(df["key"])
    ax.set_ylabel("Success rate (%)")
    ax.set_title("Ablation success rate with Wilson 95% CI")
    ax.set_ylim(0, 105)
    for i, v in enumerate(rate):
        ax.text(i, v + 2, f"{v:.1f}", ha="center", va="bottom", fontsize=9)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "ablation_success_bar.png", dpi=300)
    plt.close(fig)


def plot_effect_size_forest(df: pd.DataFrame) -> None:
    """Forest plot of absolute difference vs E0."""
    sub = df[df["key"] != "E0"].copy()
    if sub.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(sub))
    diff = sub["diff_vs_E0_pp"].values
    lower = sub["diff_ci_lower_pp"].values
    upper = sub["diff_ci_upper_pp"].values
    err = np.vstack([diff - lower, upper - diff])
    ax.errorbar(diff, y, xerr=err, fmt="o", capsize=5, color="darkred")
    ax.axvline(0, color="gray", linestyle="--", linewidth=1.2)
    ax.set_yticks(y)
    ax.set_yticklabels(sub["key"])
    ax.set_xlabel("Success rate difference vs E0 (percentage points)")
    ax.set_title("Effect size forest plot (absolute difference vs E0)")
    ax.grid(True, alpha=0.3)
    for i, (_, row) in enumerate(sub.iterrows()):
        d = row["cohen_d_vs_E0"]
        label = f"d={d:.2f}" if pd.notna(d) else "d=NA"
        ax.text(row["diff_vs_E0_pp"] + 1.0, i, label, va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "effect_size_forest.png", dpi=300)
    plt.close(fig)


def plot_paired_scatter(results: Dict) -> None:
    """Paired task-level success rates (E0 vs ablations)."""
    if "E0" not in results:
        return
    e0 = results["E0"]
    if not e0.task_successes:
        print("[WARN] E0 has no per-task successes; skip paired_scatter.png")
        return
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = plt.cm.tab10(np.linspace(0, 1, len(results) - 1))
    idx = 0
    for key, res in results.items():
        if key == "E0" or not res.task_successes:
            continue
        xs, ys = [], []
        for task_id in sorted(e0.task_successes.keys()):
            if task_id not in res.task_successes:
                continue
            x = sum(e0.task_successes[task_id]) / len(e0.task_successes[task_id])
            y = sum(res.task_successes[task_id]) / len(res.task_successes[task_id])
            jitter = 0.02
            xs.append(x + np.random.uniform(-jitter, jitter))
            ys.append(y + np.random.uniform(-jitter, jitter))
        ax.scatter(xs, ys, label=key, alpha=0.75, s=70, color=colors[idx])
        idx += 1
    ax.plot([0, 1], [0, 1], "k--", linewidth=1.2, label="y = x")
    ax.set_xlabel("E0 task success rate")
    ax.set_ylabel("Ablation task success rate")
    ax.set_title("Paired task-level success rates (E0 vs ablations)")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "paired_scatter.png", dpi=300)
    plt.close(fig)


def plot_eval_ep_s_bar(df: pd.DataFrame) -> None:
    """Bar chart of eval_ep_s across experiments."""
    fig, ax = plt.subplots(figsize=(10, 6))
    keys = df["key"].values
    values = df["eval_ep_s"].values
    colors = ["steelblue"] * len(keys)
    if "E4" in keys:
        colors[list(keys).index("E4")] = "firebrick"
    bars = ax.bar(keys, values, color=colors)
    ax.set_ylabel("eval_ep_s (seconds per episode)")
    ax.set_title("Average time per episode for each experiment")
    e0_val = df.loc[df["key"] == "E0", "eval_ep_s"].values[0]
    ax.axhline(e0_val, color="gray", linestyle="--", linewidth=1, label="E0 baseline")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 2, f"{val:.2f}",
                ha="center", va="bottom", fontsize=9)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "eval_ep_s_bar.png", dpi=300)
    plt.close(fig)