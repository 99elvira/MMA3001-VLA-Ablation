# -*- coding: utf-8 -*-
"""Configuration constants for the MMA3001 VLA ablation analysis."""

from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE_DIR / "results"
FIG_DIR = RESULTS_DIR / "figures"

# Evaluation constants
N_EPISODES = 30
TASK_SIZE = 3

# Experiment definitions: (key, name, filename)
EXPERIMENTS = [
    ("E0", "baseline", "baseline_results.txt"),
    ("E1", "no_agentview", "no_agentview_results.txt"),
    ("E2", "no_wrist", "no_wrist_results.txt"),
    ("E3", "no_state", "no_state_results.txt"),
    ("E4", "use_chunk", "use_chunk_results.txt"),
    ("E5", "ema", "ema_results.txt"),
]

CAMERA_EXPERIMENTS = [(f"P{i}", "external" if i <= 4 else "wrist", f"P{i}_results.txt") for i in range(1, 9)]
SUPPLEMENTARY_EXPERIMENTS = [(f"Q{i}", name, f"Q{i}_results.txt") for i, name in enumerate(['wrist_forward_0.05', 'wrist_backward_0.05', 'wrist_lateral_0.05', 'wrist_vertical_0.05'], 1)]

# Random seed for paired scatter jitter
RANDOM_SEED = 42

# Significance thresholds
ALPHA = 0.05
