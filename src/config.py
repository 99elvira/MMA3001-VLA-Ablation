# -*- coding: utf-8 -*-
"""Configuration constants for the MMA3001 VLA ablation analysis."""

from pathlib import Path

# Base project directory
BASE_DIR = Path(r"D:\MMA3001_Project")
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

# Random seed for paired scatter jitter
RANDOM_SEED = 42

# Significance thresholds
ALPHA = 0.05