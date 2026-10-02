# -*- coding: utf-8 -*-
"""Statistical functions for the MMA3001 VLA ablation analysis."""

from __future__ import annotations

import warnings
from typing import List, Tuple

import numpy as np
from scipy import stats


def wilson_ci(k: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if n <= 0:
        return np.nan, np.nan
    z = stats.norm.ppf(1 - alpha / 2)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt((p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def cohens_d(group1: List[bool], group2: List[bool]) -> float:
    """Cohen's d with pooled standard deviation.

    Returns NaN if either group has zero variance, since d is not applicable
    when the pooled standard deviation is zero.
    """
    a = np.asarray(group1, dtype=float)
    b = np.asarray(group2, dtype=float)
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return np.nan
    s1 = np.var(a, ddof=1)
    s2 = np.var(b, ddof=1)
    if s1 == 0 or s2 == 0:
        return np.nan
    pooled_var = ((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2)
    if pooled_var <= 0:
        return np.nan
    return (np.mean(a) - np.mean(b)) / np.sqrt(pooled_var)


def safe_welch(group1: List[bool], group2: List[bool]) -> Tuple[float, float]:
    """Welch t-test; returns (NaN, NaN) if variance is zero or invalid."""
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
    """Fisher exact test on a 2x2 table."""
    fail1 = n1 - success1
    fail2 = n2 - success2
    table = [[success1, fail1], [success2, fail2]]
    try:
        _, p_val = stats.fisher_exact(table)
        return float(p_val)
    except Exception:
        return np.nan


def safe_anova(groups: List[List[bool]]) -> Tuple[float, float]:
    """One-way ANOVA; returns (NaN, NaN) if invalid."""
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
    """Holm correction. Returns adjusted p-values in the same order."""
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
    """Confidence interval for the difference between two proportions."""
    p1 = k1 / n1 if n1 else np.nan
    p2 = k2 / n2 if n2 else np.nan
    diff = p1 - p2
    if n1 <= 0 or n2 <= 0:
        return diff, np.nan, np.nan
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    z = stats.norm.ppf(1 - alpha / 2)
    return diff, diff - z * se, diff + z * se


def significance_marker(p: float) -> str:
    """Return significance marker for a p-value."""
    if p is None or np.isnan(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    if p < 0.1:
        return "."
    return "ns"