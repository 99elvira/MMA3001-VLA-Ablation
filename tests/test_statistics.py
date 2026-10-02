"""Tests for statistical functions."""

import numpy as np
import pytest
from src.statistics import wilson_ci, cohens_d, holm_adjust


def test_wilson_ci_bounds():
    lo, hi = wilson_ci(28, 30)
    assert 0.0 <= lo <= 1.0
    assert 0.0 <= hi <= 1.0
    assert lo < hi


def test_wilson_ci_zero():
    lo, hi = wilson_ci(0, 30)
    assert lo == 0.0
    assert 0.0 < hi < 0.2


def test_cohens_d_zero_variance():
    """Cohen's d must be NaN when variance is zero."""
    group1 = [True] * 30
    group2 = [True] * 28 + [False] * 2
    d = cohens_d(group1, group2)
    assert np.isnan(d)


def test_cohens_d_nonzero_variance():
    group1 = [True, False] * 15
    group2 = [True] * 28 + [False] * 2
    d = cohens_d(group1, group2)
    assert not np.isnan(d)


def test_holm_adjust_order():
    p_values = [("E1", 0.001), ("E2", 0.01), ("E3", 0.05)]
    adjusted = holm_adjust(p_values)
    assert len(adjusted) == 3
    assert adjusted[0] <= adjusted[1] <= adjusted[2]