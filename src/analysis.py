# -*- coding: utf-8 -*-
"""
MMA3001 VLA Robotic Grasping Ablation Analysis
File: D:\MMA3001_Project\analysis.py

修正版：
- E1/E2/E3 方差为 0 时，Cohen's d 返回 NaN。
- E1/E2/E3 方差为 0 时，跳过 Welch，强制使用 Fisher 精确检验。
- Holm 校正基于正确的 p 值序列重新计算。
"""

from __future__ import annotations

import ast
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# ============================================================
# 路径与常量
# ============================================================
BASE_DIR = Path(r"D:\MMA3001_Project")
RESULTS_DIR = BASE_DIR / "results"
FIG_DIR = RESULTS_DIR / "figures"

N_EPISODES = 30
TASK_SIZE = 3

EXPERIMENTS = [
    ("E0", "baseline", "baseline_results.txt"),
    ("E1", "no_agentview", "no_agentview_results.txt"),
    ("E2", "no_wrist", "no_wrist_results.txt"),
    ("E3", "no_state", "no_state_results.txt"),
    ("E4", "use_chunk", "use_chunk_results.txt"),
    ("E5", "ema", "ema_results.txt"),
]

np.random.seed(42)

# ============================================================
# 工具函数
# ============================================================
def extract_balanced(text: str, start_idx: int, open_char: str, close_char: str) -> Optional[str]:
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
                    return text[i:j + 1]
    return None

def wilson_ci(k: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    if n <= 0:
        return np.nan, np.nan
    z = stats.norm.ppf(1 - alpha / 2)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt((p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return max(0.0, centre - half), min(1.0, centre + half)

def cohens_d(group1: List[bool], group2: List[bool]) -> float:
    """
    修正版：如果任一组的方差为 0，直接返回 NaN。
    """
    a = np.asarray(group1, dtype=float)
    b = np.asarray(group2, dtype=float)
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return np.nan
    s1 = np.var(a, ddof=1)
    s2 = np.var(b, ddof=1)
    # 关键修正：只要有一组方差为 0，d 不适用
    if s1 == 0 or s2 == 0:
        return np.nan
    pooled_var = ((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2)
    if pooled_var <= 0:
        return np.nan
    return (np.mean(a) - np.mean(b)) / np.sqrt(pooled_var)

def safe_welch(group1: List[bool], group2: List[bool]) -> Tuple[float, float]:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t_stat, p_val = stats.ttest_ind(group1, group2, equal_var=False)
        if np.isnan(p_val):
            return np.nan, np.nan
        return float(t_stat), float(p_val)
    except Exception:
        return np.nan, np.nan

def fisher_p(success1: int, n1: int, success2: int, n2: int) -> float:
    fail1 = n1 - success1
    fail2 = n2 - success2
    table = [[success1, fail1], [success2, fail2]]
    try:
        _, p_val = stats.fisher_exact(table)
        return float(p_val)
    except Exception:
        return np.nan

def safe_anova(groups: List[List[bool]]) -> Tuple[float, float]:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            f_stat, p_val = stats.f_oneway(*groups)
        if np.isnan(p_val):
            return np.nan, np.nan
        return float(f_stat), float(p_val)
    except Exception:
        return np.nan, np.nan

def holm_adjust(p_values: List[Tuple[str, float]]) -> List[float]:
    m = len(p_values)
    adjusted = [np.nan] * m
    valid = [(i, p) for i, (_, p) in enumerate(p_values) if not np.isnan(p)]
    if not valid:
        return adjusted
    valid_sorted = sorted(valid, key=lambda x: x[1])
    prev = 0.0
    for rank, (idx, p) in enumerate(valid_sorted, start=1):
        adj = min(1.0, (len(valid) - rank + 1) * p)
        adj = max(adj, prev)
        adjusted[idx] = adj
        prev = adj
    return adjusted

def diff_ci(k1: int, n1: int, k2: int, n2: int, alpha: float = 0.05) -> Tuple[float, float, float]:
    p1 = k1 / n1 if n1 else np.nan
    p2 = k2 / n2 if n2 else np.nan
    diff = p1 - p2
    if n1 <= 0 or n2 <= 0:
        return diff, np.nan, np.nan
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    z = stats.norm.ppf(1 - alpha / 2)
    return diff, diff - z * se, diff + z * se

def significance_marker(p: float) -> str:
    if pd.isna(p): return ""
    if p < 0.001: return "***"
    if p < 0.01: return "**"
    if p < 0.05: return "*"
    if p < 0.1: return "."
    return "ns"

# ============================================================
# 数据结构与解析
# ============================================================
@dataclass
class ExperimentResult:
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

def parse_result_file(path: Path, key: str, name: str) -> ExperimentResult:
    text = path.read_text(encoding="utf-8", errors="ignore")
    overall = None
    per_task = None
    idx = text.find("Overall Aggregated Metrics:")
    if idx != -1:
        brace_str = extract_balanced(text, idx, "{", "}")
        if brace_str:
            try: overall = ast.literal_eval(brace_str)
            except Exception as e: print(f"[WARN] failed to parse overall metrics in {path}: {e}")
    idx = text.find("Aggregated Metrics for per_task:")
    if idx != -1:
        bracket_str = extract_balanced(text, idx, "[", "]")
        if bracket_str:
            try: per_task = ast.literal_eval(bracket_str)
            except Exception as e: print(f"[WARN] failed to parse per_task metrics in {path}: {e}")
    task_successes: Dict[int, List[bool]] = {}
    if per_task:
        for item in per_task:
            task_id = item.get("task_id")
            metrics = item.get("metrics", {})
            successes = metrics.get("successes")
            if task_id is not None and successes is not None:
                task_successes[int(task_id)] = [bool(x) for x in successes]
    if task_successes:
        all_successes = [s for lst in task_successes.values() for s in lst]
        success_count = sum(all_successes)
        n_episodes = len(all_successes)
    elif overall:
        n_episodes = int(overall.get("n_episodes", 0))
        pc = float(overall.get("pc_success", 0.0))
        if pc > 1.0: pc = pc / 100.0
        success_count = int(round(pc * n_episodes)) if n_episodes else 0
    else:
        raise ValueError(f"Cannot parse results from {path}")
    if n_episodes != N_EPISODES:
        print(f"[WARN] {key} n_episodes={n_episodes}, expected {N_EPISODES}")
    success_rate = success_count / n_episodes if n_episodes else np.nan
    eval_s = overall.get("eval_s") if overall else None
    eval_ep_s = overall.get("eval_ep_s") if overall else None
    avg_sum_reward = overall.get("avg_sum_reward") if overall else None
    avg_max_reward = overall.get("avg_max_reward") if overall else None
    return ExperimentResult(key, name, path, success_count, n_episodes, success_rate,
                            task_successes, eval_s, eval_ep_s, avg_sum_reward, avg_max_reward)

def get_flat_successes(res: ExperimentResult) -> List[bool]:
    if res.task_successes:
        return [s for lst in res.task_successes.values() for s in lst]
    return [True] * res.success_count + [False] * (res.n_episodes - res.success_count)

# ============================================================
# 绘图
# ============================================================
def plot_ablation_success_bar(df: pd.DataFrame) -> None:
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

def plot_paired_scatter(results: Dict[str, ExperimentResult]) -> None:
    if "E0" not in results: return
    e0 = results["E0"]
    if not e0.task_successes:
        print("[WARN] E0 has no per-task successes; skip paired_scatter.png")
        return
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = plt.cm.tab10(np.linspace(0, 1, len(results) - 1))
    idx = 0
    for key, res in results.items():
        if key == "E0" or not res.task_successes: continue
        xs, ys = [], []
        for task_id in sorted(e0.task_successes.keys()):
            if task_id not in res.task_successes: continue
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
    ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3); ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "paired_scatter.png", dpi=300)
    plt.close(fig)

def plot_effect_size_forest(df: pd.DataFrame) -> None:
    sub = df[df["key"] != "E0"].copy()
    if sub.empty: return
    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(sub))
    diff = sub["diff_vs_E0_pp"].values
    lower = sub["diff_ci_lower_pp"].values
    upper = sub["diff_ci_upper_pp"].values
    err = np.vstack([diff - lower, upper - diff])
    ax.errorbar(diff, y, xerr=err, fmt="o", capsize=5, color="darkred")
    ax.axvline(0, color="gray", linestyle="--", linewidth=1.2)
    ax.set_yticks(y); ax.set_yticklabels(sub["key"])
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

# ============================================================
# 报告生成
# ============================================================
def build_report(results, df, anova_f, anova_p, holm_rows):
    lines = []
    lines.append("=" * 90)
    lines.append("MMA3001 VLA Robotic Grasping Ablation Analysis Report")
    lines.append("=" * 90)
    lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("1. Experiment summary")
    lines.append("-" * 90)
    for key, res in results.items():
        lines.append(f"{key} {res.name}: {res.success_count}/{res.n_episodes} = {res.success_rate * 100:.2f}%")
        lo, hi = wilson_ci(res.success_count, res.n_episodes)
        lines.append(f"    Wilson 95% CI: [{lo * 100:.2f}%, {hi * 100:.2f}%]")
        lines.append(f"    eval_s: {res.eval_s}, eval_ep_s: {res.eval_ep_s}")
    lines.append("")
    lines.append("2. Overall ANOVA across 6 groups")
    lines.append("-" * 90)
    lines.append(f"One-way ANOVA: F = {anova_f:.6f}, p = {anova_p:.6e}")
    lines.append("")
    lines.append("3. Pairwise comparisons vs E0 (E1-E5), Holm-adjusted")
    lines.append("-" * 90)
    lines.append(f"{'Comparison':<12} {'Diff(pp)':>10} {'95% CI(pp)':>22} {'Cohen d':>10} {'Welch p':>12} {'Fisher p':>12} {'Holm p':>12} {'Sig':>6}")
    for row in holm_rows:
        d_str = f"{row['cohen_d']:.4f}" if pd.notna(row["cohen_d"]) else "NA"
        welch_str = f"{row['welch_p']:.4e}" if pd.notna(row["welch_p"]) else "NA"
        fisher_str = f"{row['fisher_p']:.4e}" if pd.notna(row["fisher_p"]) else "NA"
        holm_str = f"{row['holm_p']:.4e}" if pd.notna(row["holm_p"]) else "NA"
        ci_str = f"[{row['diff_ci_lower_pp']:.2f}, {row['diff_ci_upper_pp']:.2f}]" if pd.notna(row["diff_ci_lower_pp"]) and pd.notna(row["diff_ci_upper_pp"]) else "NA"
        lines.append(f"{row['comparison']:<12} {row['diff_pp']:>10.2f} {ci_str:>22} {d_str:>10} {welch_str:>12} {fisher_str:>12} {holm_str:>12} {row['sig']:>6}")
    lines.append("")
    lines.append("4. Statistical notes")
    lines.append("-" * 90)
    lines.append("- Wilson 95% CI is reported for each group's success rate.")
    lines.append("- Welch t-test uses equal_var=False. If any group's variance is zero, Welch is invalid and Fisher exact test is used instead.")
    lines.append("- Cohen's d uses pooled standard deviation. If any group's variance is zero, d is NaN (not applicable).")
    lines.append("- For E1/E2/E3, success rate is 0/30, variance is zero. Cohen's d is not applicable. Fisher exact test is used.")
    lines.append("- Holm correction is applied to the 5 comparisons E1-E5 vs E0.")
    lines.append("")
    lines.append("5. Per-task success details")
    lines.append("-" * 90)
    for key, res in results.items():
        lines.append(f"{key} ({res.name}):")
        if not res.task_successes:
            lines.append("    no per-task successes parsed.")
            continue
        for task_id in sorted(res.task_successes.keys()):
            s = res.task_successes[task_id]
            lines.append(f"    task {task_id}: {s} -> {sum(s)}/{len(s)}")
    lines.append("")
    lines.append("End of report.")
    return "\n".join(lines)

# ============================================================
# 主流程
# ============================================================
def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    results: Dict[str, ExperimentResult] = {}
    for key, name, fname in EXPERIMENTS:
        path = RESULTS_DIR / fname
        if not path.exists():
            print(f"[WARN] missing result file: {path}")
            continue
        print(f"[INFO] parsing {key} from {path}")
        results[key] = parse_result_file(path, key, name)

    order = [k for k, _, _ in EXPERIMENTS]
    missing = [k for k in order if k not in results]
    if missing:
        raise SystemExit(f"Missing required experiment results: {missing}")

    rows = []
    for key, res in results.items():
        lo, hi = wilson_ci(res.success_count, res.n_episodes)
        rows.append({
            "key": key, "name": res.name, "success_count": res.success_count,
            "n_episodes": res.n_episodes, "success_rate": res.success_rate,
            "success_rate_pct": res.success_rate * 100,
            "wilson_ci_lower": lo, "wilson_ci_upper": hi,
            "wilson_ci_lower_pct": lo * 100, "wilson_ci_upper_pct": hi * 100,
            "eval_s": res.eval_s, "eval_ep_s": res.eval_ep_s,
            "avg_sum_reward": res.avg_sum_reward, "avg_max_reward": res.avg_max_reward,
            "cohen_d_vs_E0": np.nan, "cohen_d_label": "",
            "welch_p_vs_E0": np.nan, "fisher_p_vs_E0": np.nan,
            "p_used_vs_E0": np.nan, "holm_adjusted_p": np.nan,
            "significance": "", "diff_vs_E0_pp": np.nan,
            "diff_ci_lower_pp": np.nan, "diff_ci_upper_pp": np.nan,
        })

    df = pd.DataFrame(rows)
    df = df.set_index("key").loc[order].reset_index()

    e0 = results["E0"]
    e0_flat = get_flat_successes(e0)

    p_values_for_holm = []
    holm_rows = []

    for key in ["E1", "E2", "E3", "E4", "E5"]:
        res = results[key]
        flat = get_flat_successes(res)

        var_a = np.var(flat, ddof=1)
        var_b = np.var(e0_flat, ddof=1)

        # 修正核心：方差为 0 时，d 返回 NaN，强制走 Fisher
        d = cohens_d(flat, e0_flat)
        fisher_p_val = fisher_p(res.success_count, res.n_episodes, e0.success_count, e0.n_episodes)

        if var_a == 0 or var_b == 0:
            welch_p = np.nan
            p_used = fisher_p_val
        else:
            _, welch_p = safe_welch(flat, e0_flat)
            p_used = welch_p if not np.isnan(welch_p) else fisher_p_val

        p_values_for_holm.append((key, p_used))
        diff, diff_lo, diff_hi = diff_ci(res.success_count, res.n_episodes, e0.success_count, e0.n_episodes)

        idx = df.index[df["key"] == key][0]
        df.at[idx, "cohen_d_vs_E0"] = d
        df.at[idx, "cohen_d_label"] = f"{d:.4f}" if pd.notna(d) else "NA"
        df.at[idx, "welch_p_vs_E0"] = welch_p
        df.at[idx, "fisher_p_vs_E0"] = fisher_p_val
        df.at[idx, "p_used_vs_E0"] = p_used
        df.at[idx, "diff_vs_E0_pp"] = diff * 100
        df.at[idx, "diff_ci_lower_pp"] = diff_lo * 100 if pd.notna(diff_lo) else np.nan
        df.at[idx, "diff_ci_upper_pp"] = diff_hi * 100 if pd.notna(diff_hi) else np.nan

    holm_adjusted = holm_adjust(p_values_for_holm)
    for (key, _), holm_p in zip(p_values_for_holm, holm_adjusted):
        idx = df.index[df["key"] == key][0]
        df.at[idx, "holm_adjusted_p"] = holm_p
        df.at[idx, "significance"] = significance_marker(holm_p)

    anova_groups = [get_flat_successes(results[k]) for k in order]
    anova_f, anova_p = safe_anova(anova_groups)

    for key in ["E1", "E2", "E3", "E4", "E5"]:
        row = df[df["key"] == key].iloc[0]
        holm_rows.append({
            "comparison": f"{key} vs E0", "diff_pp": row["diff_vs_E0_pp"],
            "diff_ci_lower_pp": row["diff_ci_lower_pp"], "diff_ci_upper_pp": row["diff_ci_upper_pp"],
            "cohen_d": row["cohen_d_vs_E0"], "welch_p": row["welch_p_vs_E0"],
            "fisher_p": row["fisher_p_vs_E0"], "holm_p": row["holm_adjusted_p"],
            "sig": row["significance"],
        })

    summary_path = RESULTS_DIR / "summary.csv"
    df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    print(f"[INFO] saved {summary_path}")

    plot_ablation_success_bar(df)
    plot_paired_scatter(results)
    plot_effect_size_forest(df)
    print(f"[INFO] figures saved to {FIG_DIR}")

    report = build_report(results, df, anova_f, anova_p, holm_rows)
    report_path = RESULTS_DIR / "analysis_report.txt"
    report_path.write_text(report, encoding="utf-8")
    print(f"[INFO] saved {report_path}")

    print("\n" + "=" * 90)
    print("SUMMARY")
    print("=" * 90)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    print(df[["key", "success_count", "n_episodes", "success_rate_pct",
              "wilson_ci_lower_pct", "wilson_ci_upper_pct",
              "diff_vs_E0_pp", "cohen_d_vs_E0",
              "welch_p_vs_E0", "fisher_p_vs_E0", "holm_adjusted_p", "significance"]].to_string(index=False))
    print(f"\nANOVA: F={anova_f:.6f}, p={anova_p:.6e}")

if __name__ == "__main__":
    main()