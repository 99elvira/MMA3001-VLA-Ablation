import numpy as np

from src.statistics import wilson_ci, cohens_d, fisher_p, holm_adjust


class TestWilsonCI:
    def test_basic(self):
        lo, hi = wilson_ci(28, 30)
        assert 0.78 < lo < 0.80
        assert 0.97 < hi < 0.99

    def test_zero_success(self):
        lo, hi = wilson_ci(0, 30)
        assert lo == 0.0
        assert 0.10 < hi < 0.13

    def test_full_success(self):
        lo, hi = wilson_ci(30, 30)
        assert 0.85 < lo < 0.90
        assert hi == 1.0

    def test_zero_n(self):
        lo, hi = wilson_ci(0, 0)
        assert np.isnan(lo) and np.isnan(hi)


class TestCohensD:
    def test_normal_case(self):
        a = [1, 1, 1, 1, 0, 1, 1, 0, 1, 1]
        b = [1, 0, 1, 0, 0, 1, 1, 0, 1, 1]
        d = cohens_d(a, b)
        assert not np.isnan(d)

    def test_zero_variance_returns_nan(self):
        a = [1, 1, 1, 1]
        b = [0, 0, 0, 0]
        assert np.isnan(cohens_d(a, b))

    def test_small_sample_returns_nan(self):
        assert np.isnan(cohens_d([1], [0]))


class TestFisherP:
    def test_identical_groups(self):
        p = fisher_p(28, 30, 28, 30)
        assert p > 0.99

    def test_opposite_groups(self):
        p = fisher_p(28, 30, 0, 30)
        assert p < 1e-10


class TestHolmAdjust:
    def test_monotone(self):
        p = [0.01, 0.02, 0.03]
        adj = holm_adjust(p)
        assert len(adj) == 3
        assert all(0.0 <= x <= 1.0 for x in adj)
        assert adj[0] <= adj[1] <= adj[2]