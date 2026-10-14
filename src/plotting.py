"""Scientific figures derived from log-parsed outcomes, with no data hardcoding."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

plt.rcParams.update({"font.family": "Times New Roman", "font.size": 13})


def _success(df, path, title):
    """Plot success percentages with asymmetric Wilson confidence intervals."""
    fig, ax = plt.subplots(figsize=(9, 4.8))
    rate = df.success_rate_pct.to_numpy()
    err = np.vstack([rate - df.wilson_ci_lower_pct, df.wilson_ci_upper_pct - rate])
    colors = ["#4C72B0" if k.startswith("E") else "#7FB3D5" if int(k[1:]) <= 4 else "#C0392B" for k in df.key]
    ax.bar(df.key, rate, yerr=err, capsize=4, color=colors)
    ax.axhline(rate[0], color="gray", linestyle="--", label="E0 baseline")
    for i, v in enumerate(rate):
        ax.text(i, float(df.wilson_ci_upper_pct.iloc[i]) + 1.5, f"{v:.2f}", ha="center", fontsize=11)
    ax.set(ylim=(0, 105), ylabel="Success rate (%)", title=title)
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(path, dpi=240)
    plt.close(fig)


def make_figures(e_df, p_df, results, directory):
    """Write success, runtime, paired-task and episode-failure figures.

    Args:
        e_df: E0-E5 statistics including Wilson endpoints and wall times.
        p_df: P1-P8 statistics.
        results: Parsed outcomes keyed by experiment ID.
        directory: Destination directory, created if absent.

    Returns:
        None. Files are written without modifying the source experiment logs.
    """
    import pandas as pd
    directory.mkdir(parents=True, exist_ok=True)
    _success(e_df, directory / "ablation_success_bar.png", "Ablation success with Wilson 95% confidence intervals")
    cameras = pd.concat([e_df.iloc[[0]], p_df], ignore_index=True)
    _success(cameras, directory / "fig_4_7a_success_rate.png", "Camera translations: 30 episodes per condition")
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(e_df.key, e_df.eval_ep_s, color="#4C72B0")
    for i, v in enumerate(e_df.eval_ep_s):
        ax.text(i, v + 2, f"{v:.2f}", ha="center", fontsize=11)
    ax.set(ylabel="Seconds per episode", title="Recorded end-to-end evaluation time")
    fig.tight_layout(); fig.savefig(directory / "eval_ep_s_bar.png", dpi=240); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 6))
    rng = np.random.default_rng(42)
    base = results["E0"]
    for key in e_df.key[1:]:
        other = results[key]
        tasks = sorted(base.task_successes)
        x = np.array([np.mean(base.task_successes[t]) for t in tasks])
        y = np.array([np.mean(other.task_successes[t]) for t in tasks])
        ax.scatter(x + rng.uniform(-.012, .012, len(x)), y + rng.uniform(-.012, .012, len(y)), label=key, alpha=.7)
    ax.plot([0, 1], [0, 1], "k--")
    ax.set(xlim=(-.05, 1.05), ylim=(-.05, 1.05), xlabel="E0 task success rate", ylabel="Condition task success rate", title="Task-level outcomes (display jitter only)")
    ax.legend(); fig.tight_layout(); fig.savefig(directory / "paired_scatter.png", dpi=240); plt.close(fig)
    labels = list(cameras.key)
    matrix = [[int(not s) for t in sorted(results[k].task_successes) for s in results[k].task_successes[t]] for k in labels]
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.imshow(matrix, aspect="auto", cmap=ListedColormap(["#F4F6F7", "#C0392B"]), vmin=0, vmax=1)
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xticks([3*t+1 for t in range(10)], [f"T{t}" for t in range(10)])
    ax.set(xlabel="Three ordered episodes per task", title="Episode failures: red = failure, white = success")
    for t in range(1, 10): ax.axvline(3*t-.5, color="black", linewidth=.5)
    fig.tight_layout(); fig.savefig(directory / "fig_4_7b_failure_heatmap.png", dpi=240); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(e_df.key[1:], e_df.diff_vs_E0_pp[1:], color="#C0392B")
    ax.set(xlabel="Difference from E0 (percentage points)", title="Observed paired success difference (point estimates)")
    fig.tight_layout(); fig.savefig(directory / "effect_size_forest.png", dpi=240); plt.close(fig)


def plot_wrist_magnitudes(p_df, q_df, path):
    """Compare the two observed wrist-translation magnitudes by direction.

    Args:
        p_df: Primary camera statistics, including P5-P8 at 0.03 m.
        q_df: Supplementary Q1-Q4 statistics at 0.05 m.
        path: Destination PNG. Error bars show separate Wilson intervals.
    """
    small=p_df[p_df.key.isin(['P5','P6','P7','P8'])]
    x=np.arange(4);fig,ax=plt.subplots(figsize=(8.5,4.5))
    for delta,df,label,color in [(-.18,small,'0.03 m','#4C72B0'),(.18,q_df,'0.05 m (supplementary)','#C0392B')]:
        rate=df.success_rate_pct.to_numpy()
        err=np.vstack([rate-df.wilson_ci_lower_pct,df.wilson_ci_upper_pct-rate])
        ax.bar(x+delta,rate,.34,yerr=err,capsize=3,label=label,color=color)
        for i,v in enumerate(rate):ax.text(i+delta,float(df.wilson_ci_upper_pct.iloc[i])+1.5,f'{v:.1f}',ha='center',fontsize=10)
    ax.axhline(100*28/30,linestyle='--',color='gray',label='E0 baseline')
    ax.set_xticks(x,['Forward','Backward','Lateral','Vertical'])
    ax.set(ylim=(0,110),ylabel='Success rate (%)',title='Wrist translation by direction and magnitude')
    ax.legend(loc='lower left',fontsize=10);fig.tight_layout();fig.savefig(path,dpi=240);plt.close(fig)
