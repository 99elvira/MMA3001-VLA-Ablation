"""Reproduce E0-E5 and P1-P8 from original logs with paired binary inference.

Run ``python -m src.analysis`` from the repository root. Analysis requires no
robot checkpoint, GPU or simulator. Initial-state equality is assumed from
the fixed evaluation protocol; the logs only identify task and episode order.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from src.config import RESULTS_DIR, EXPERIMENTS, CAMERA_EXPERIMENTS, SUPPLEMENTARY_EXPERIMENTS
from src.parser import parse_result_file, paired_successes
from src.statistics import wilson_ci, exact_mcnemar, holm_adjust
from src.plotting import make_figures


def analyse_family(definitions, directory, baseline=None):
    """Parse one experiment family and apply its separate Holm correction.

    Args:
        definitions: Sequence of (key, name, log filename) tuples.
        directory: Directory of original logs.
        baseline: Parsed E0, needed for the camera family.

    Returns:
        DataFrame of statistics and a dictionary of parsed experiment results.

    Raises:
        ValueError: Logs cannot support valid task/episode pairing.
    """
    parsed = {k: parse_result_file(directory / f, k, name) for k, name, f in definitions}
    ref = parsed.get("E0", baseline)
    rows = []
    for key, res in parsed.items():
        lo, hi = wilson_ci(res.success_count, res.n_episodes)
        loss, gain, p = (None, None, None) if key == "E0" else exact_mcnemar(*paired_successes(ref, res))
        rows.append(dict(key=key, name=res.name, success_count=res.success_count,
                         n_episodes=res.n_episodes, success_rate_pct=100 * res.success_rate,
                         wilson_ci_lower_pct=100 * lo, wilson_ci_upper_pct=100 * hi,
                         diff_vs_E0_pp=100 * (res.success_rate - ref.success_rate),
                         baseline_only=loss, condition_only=gain, mcnemar_p=p,
                         eval_ep_s=res.eval_ep_s))
    df = pd.DataFrame(rows)
    compared = df.key != "E0"
    df.loc[compared, "holm_adjusted_p"] = holm_adjust(df.loc[compared, "mcnemar_p"].tolist())
    return df, parsed


def main(argv=None):
    """Write count tables, paired episode records and data-derived figures.

    Args:
        argv: Optional CLI list. ``--results-dir`` selects inputs and
            ``--output-dir`` selects derived outputs (default: input directory).
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    output = args.output_dir or args.results_dir
    output.mkdir(parents=True, exist_ok=True)
    e_df, e = analyse_family(EXPERIMENTS, args.results_dir)
    p_df, p = analyse_family(CAMERA_EXPERIMENTS, args.results_dir, e["E0"])
    q_df, q = analyse_family(SUPPLEMENTARY_EXPERIMENTS, args.results_dir, e["E0"])
    # Preserve the original family and explicitly check all 12 camera contrasts.
    all_camera = pd.concat([p_df, q_df], ignore_index=True)
    all_camera['holm_all_12'] = holm_adjust(all_camera.mcnemar_p.tolist())
    e_df.to_csv(output / "summary.csv", index=False)
    p_df.to_csv(output / "camera_summary.csv", index=False)
    q_df.to_csv(output / "supplementary_summary.csv", index=False)
    all_camera.to_csv(output / "all_camera_summary.csv", index=False)
    records = [dict(condition=k, task_id=t, episode_index=i, success=s)
               for k, res in {**e, **p, **q}.items() for t in sorted(res.task_successes)
               for i, s in enumerate(res.task_successes[t])]
    pd.DataFrame(records).to_csv(output / "paired_outcomes.csv", index=False)
    make_figures(e_df, p_df, {**e, **p}, output / "figures")
    # Keep the later solver-step family separate from the camera comparisons.
    from src.integration import main as integration_main
    integration_main(["--results-dir", str(args.results_dir), "--output-dir", str(output)])
    from src.plotting import plot_wrist_magnitudes
    plot_wrist_magnitudes(p_df, q_df, output / 'figures/wrist_magnitude_comparison.png')
    report = "Wilson 95% intervals; exact paired McNemar; separate Holm families (5 and 8).\n"
    report += "Pairs: task ID and episode index; initial-state equality relies on the evaluation protocol.\n"
    report += "Single seed, three episodes per task: inference is conditional on this finite task sample.\n\n"
    report += e_df.to_string(index=False) + "\n\n" + p_df.to_string(index=False)
    report += '\n\nSupplementary 0.05 m (four exploratory comparisons):\n' + q_df.to_string(index=False)
    report += '\n\nSensitivity check: Holm correction over ALL 12 camera comparisons:\n' + all_camera.to_string(index=False)
    (output / "analysis_report.txt").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
