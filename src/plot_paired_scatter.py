"""
Regenerate the paired task-level scatter plot for Slide 13,
with larger fonts for projection.

输出到 D:\\MMA3001_Project\\results\\figures\\paired_scatter.png
（与原图同路径，覆盖旧版小字体图）。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ---------------- Global font settings for projection ----------------
rcParams["font.family"] = "Arial"
rcParams["font.size"] = 24
rcParams["axes.titlesize"] = 32
rcParams["axes.labelsize"] = 28
rcParams["xtick.labelsize"] = 24
rcParams["ytick.labelsize"] = 24
rcParams["legend.fontsize"] = 24

# ---------------- Data ----------------
# E0 per-task success rate (10 tasks), from E0 baseline run.
e0 = np.array([0.667, 1.0, 1.0, 1.0, 1.0, 0.667, 1.0, 1.0, 1.0, 1.0])

# Per-task success rates for each ablation (10 tasks each).
data = {
    "E1": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    "E2": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    "E3": np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    "E4": np.array([0.667, 1.0, 1.0, 0.667, 1.0, 0.667, 0.667, 1.0, 0.333, 0.667]),
    "E5": np.array([0.667, 1.0, 1.0, 1.0, 1.0, 0.667, 1.0, 1.0, 0.333, 0.333]),
}

colors = {
    "E1": "#4C72B0",
    "E2": "#2CA02C",
    "E3": "#8C564B",
    "E4": "#7F7F7F",
    "E5": "#17BECF",
}

# ---------------- Plot ----------------
np.random.seed(42)
fig, ax = plt.subplots(figsize=(8, 8), dpi=200)

# y = x reference line
ax.plot([0, 1], [0, 1], "k--", linewidth=2.2, label="y = x")

# Scatter each ablation, with small jitter so overlapping points are visible
jitter = 0.02
for label, y in data.items():
    xs = e0 + np.random.uniform(-jitter, jitter, size=e0.shape)
    ys = y + np.random.uniform(-jitter, jitter, size=y.shape)
    ax.scatter(xs, ys, s=220, alpha=0.8, color=colors[label],
               edgecolor="none", label=label)

ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.05, 1.05)
ax.set_xlabel("E0 task success rate", fontsize=28)
ax.set_ylabel("Ablation task success rate", fontsize=28)
ax.set_title("Paired task-level success rates (E0 vs ablations)", fontsize=32)

ax.tick_params(axis="both", labelsize=24)
ax.grid(True, linestyle="-", linewidth=0.8, alpha=0.4)
ax.legend(loc="upper left", fontsize=24, framealpha=0.9)

plt.tight_layout()
out = r"D:\MMA3001_Project\results\figures\paired_scatter.png"
plt.savefig(out, bbox_inches="tight")
plt.close(fig)
print(f"[OK] wrote {out}")
