# -*- coding: utf-8 -*-
"""Statistical functions for the MMA3001 VLA ablation analysis."""

from __future__ import annotations

import warnings
from typing import List, Tuple

import numpy as np
from scipy import stats


def wilson_ci(k: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if n < 0 or k < 0 or k > n or not 0 < alpha < 1:
        raise ValueError("Require 0 <= k <= n and 0 < alpha < 1")
    if n <= 0:
        return np.nan, np.nan
    z = stats.norm.ppf(1 - alpha / 2)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt((p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return (0.0 if k == 0 else max(0.0, centre - half),
            1.0 if k == n else min(1.0, centre + half))


def cohens_d(group1: List[bool], group2: List[bool]) -> float:
    """Cohen's d with pooled standard deviation.

    Legacy independent-group helper, unused by the paired analysis. This
    project conservatively returns NaN if either variance is zero; that is a
    reporting convention, not a general mathematical restriction on Cohen's d.
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


def holm_adjust(p_values) -> List[float]:
    """Holm correction retaining input order and monotonic adjusted values.

    Args:
        p_values: Float probabilities or legacy (label, probability) tuples.
            NaN entries remain NaN and are excluded from the tested family.

    Returns:
        Adjusted probabilities in the same order.

    Raises:
        ValueError: A finite input probability is outside [0, 1].
    """
    m = len(p_values)
    adjusted = [np.nan] * m
    values = [float(x[1] if isinstance(x, tuple) else x) for x in p_values]
    if any(not np.isnan(p) and not 0 <= p <= 1 for p in values):
        raise ValueError("p-values must be in [0, 1] or NaN")
    valid = [(i, p) for i, p in enumerate(values) if not np.isnan(p)]
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


def exact_mcnemar(baseline, condition):
    """Compute discordant counts and the two-sided exact paired binary test.

    Args:
        baseline: Nonempty binary outcomes in task/episode order.
        condition: Outcomes for the same episode identities, in the same order.

    Returns:
        (baseline_only, condition_only, p), with p=1 for no discordant pairs.

    Raises:
        ValueError: Outcomes are empty, nonbinary, or mismatched in length.
    """
    a, b = np.asarray(baseline), np.asarray(condition)
    if a.ndim != 1 or b.ndim != 1 or not a.size or a.shape != b.shape:
        raise ValueError("Matched outcomes must be nonempty equal-length vectors")
    if not np.isin(a, [0, 1]).all() or not np.isin(b, [0, 1]).all():
        raise ValueError("Outcomes must be binary")
    loss = int(np.sum((a == 1) & (b == 0)))
    gain = int(np.sum((a == 0) & (b == 1)))
    p = 1.0 if loss + gain == 0 else float(stats.binomtest(loss, loss + gain, 0.5).pvalue)
    return loss, gain, p
