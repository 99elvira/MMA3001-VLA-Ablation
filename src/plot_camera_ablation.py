"""
Generate Figure 4.7a (success-rate bar chart) and
Figure 4.7b (failing-episode heatmap) for the camera perturbation ablation.

Data source: terminal logs of E0 and P1-P8, parsed manually into the
tables below. Only matplotlib and numpy are required.

Run:
    python plot_camera_ablation.py
Output:
    D:\\MMA3001_Project\\results\\fig_4_7a_success_rate.png
    D:\\MMA3001_Project\\results\\fig_4_7b_failure_heatmap.png
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

OUT_DIR = r"D:\MMA3001_Project\results"
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Data
# ---------------------------------------------------------------------------
# Order matches the report: E0, then P1-P8
LABELS = ["E0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]

# Success counts out of 30
SUCCESS = np.array([28, 28, 28, 28, 28, 27, 16, 28, 25], dtype=float)
N_EP = 30
SR = SUCCESS / N_EP * 100.0

# Camera group, only used for colour coding in the bar chart
GROUP = ["base", "ext", "ext", "ext", "ext", "wrist", "wrist", "wrist", "wrist"]
GROUP_COLOR = {
    "base":  "#4C72B0",
    "ext":   "#7FB3D5",
    "wrist": "#C0392B",
}

# Failing (task, episode) pairs. Task 0-9, episode 0-2.
FAILING = {
    "E0": [(0, 1), (5, 2)],
    "P1": [(0, 1), (5, 2)],
    "P2": [(0, 1), (5, 2)],
    "P3": [(0, 1), (5, 2)],
    "P4": [(0, 1), (5, 2)],
    "P5": [(4, 2), (7, 1), (9, 0)],
    "P6": [(0, 0), (0, 1), (0, 2),
           (1, 0),
           (2, 0), (2, 1), (2, 2),
           (3, 2),
           (4, 0), (4, 1),
           (7, 0), (7, 1),
           (9, 0), (9, 2)],
    "P7": [(5, 0), (9, 1)],
    "P8": [(1, 0), (1, 1), (1, 2),
           (6, 0),
           (7, 0)],
}

# ---------------------------------------------------------------------------
# 2. Figure 4.7a - Success rate bar chart
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.5), dpi=200)

x = np.arange(len(LABELS))
colors = [GROUP_COLOR[g] for g in GROUP]
bars = ax.bar(x, SR, color=colors, edgecolor="black", linewidth=0.6, width=0.62)

# Baseline reference line
ax.axhline(SR[0], color="gray", linestyle="--", linewidth=0.9,
           label=f"E0 baseline = {SR[0]:.2f}%")

# Value labels above bars
for i, (bar, val) in enumerate(zip(bars, SR)):
    ax.text(bar.get_x() + bar.get_width() / 2,
            val + 1.0, f"{val:.2f}",
            ha="center", va="bottom", fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels(LABELS, fontsize=10)
ax.set_ylabel("Success rate (%)", fontsize=10)
ax.set_ylim(0, 110)
ax.set_title("Camera perturbation ablation: success rate "
             "(10 tasks × 3 episodes = 30 per bar)", fontsize=11)
ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.7)

# Custom legend for the three camera groups
from matplotlib.patches import Patch
legend_handles = [
    Patch(facecolor=GROUP_COLOR["base"],  edgecolor="black", label="Baseline"),
    Patch(facecolor=GROUP_COLOR["ext"],   edgecolor="black", label="External camera"),
    Patch(facecolor=GROUP_COLOR["wrist"], edgecolor="black", label="Wrist camera"),
    plt.Line2D([0], [0], color="gray", linestyle="--", label="E0 baseline"),
]
ax.legend(handles=legend_handles, fontsize=8, loc="lower left", framealpha=0.9)

plt.tight_layout()
out_a = os.path.join(OUT_DIR, "fig_4_7a_success_rate.png")
plt.savefig(out_a, bbox_inches="tight")
plt.close(fig)
print(f"[OK] wrote {out_a}")

# ---------------------------------------------------------------------------
# 3. Figure 4.7b - Failing-episode heatmap
# ---------------------------------------------------------------------------
# Matrix: rows = configurations, cols = 30 episodes (task*3 + episode)
# 0 = success, 1 = failure
n_rows = len(LABELS)
n_cols = 30
mat = np.zeros((n_rows, n_cols), dtype=int)
for r, lab in enumerate(LABELS):
    for (task, ep) in FAILING[lab]:
        col = task * 3 + ep
        mat[r, col] = 1

fig, ax = plt.subplots(figsize=(11, 3.8), dpi=200)

cmap = ListedColormap(["#F4F6F7", "#C0392B"])  # 0 light, 1 red
ax.imshow(mat, aspect="auto", cmap=cmap, vmin=0, vmax=1)

# Task separators: vertical lines every 3 episodes
for t in range(1, 10):
    ax.axvline(t * 3 - 0.5, color="black", linewidth=0.6, alpha=0.5)

# Row labels
ax.set_yticks(np.arange(n_rows))
ax.set_yticklabels(LABELS, fontsize=10)

# Column labels: only show task number at the centre of each 3-episode block
ax.set_xticks([t * 3 + 1 for t in range(10)])
ax.set_xticklabels([f"T{t}" for t in range(10)], fontsize=9)
ax.set_xlabel("LIBERO-object tasks (T0–T9), 3 episodes per task", fontsize=10)
ax.set_title("Failing-episode map: red = failure, white = success",
             fontsize=11)

# Annotate each red cell with a small dot for clarity
for r in range(n_rows):
    for c in range(n_cols):
        if mat[r, c] == 1:
            ax.text(c, r, "×", ha="center", va="center",
                    color="white", fontsize=10, fontweight="bold")

# Light grid
ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
ax.grid(which="minor", color="white", linewidth=0.4)
ax.tick_params(which="minor", bottom=False, left=False)

plt.tight_layout()
out_b = os.path.join(OUT_DIR, "fig_4_7b_failure_heatmap.png")
plt.savefig(out_b, bbox_inches="tight")
plt.close(fig)
print(f"[OK] wrote {out_b}")