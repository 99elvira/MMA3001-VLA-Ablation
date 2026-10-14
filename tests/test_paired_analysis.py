"""Regression tests of report values and rejection of invalid paired evidence."""
from dataclasses import replace
import numpy as np
import pytest
from src.analysis import analyse_family
from src.config import RESULTS_DIR, EXPERIMENTS, CAMERA_EXPERIMENTS, SUPPLEMENTARY_EXPERIMENTS
from src.parser import paired_successes
from src.statistics import exact_mcnemar, holm_adjust, wilson_ci


@pytest.mark.parametrize("a,b,counts,p", [([1,1],[1,1],(0,0),1), ([1]*10,[0]*10,(10,0),2/1024), ([1,0],[0,1],(1,1),1)])
def test_exact_pairs(a,b,counts,p):
    loss,gain,value = exact_mcnemar(a,b)
    assert (loss,gain) == counts and value == pytest.approx(p)


@pytest.mark.parametrize("a,b", [([],[]),([1],[1,0]),([1],[2]),([1],[np.nan])])
def test_invalid_pairs(a,b):
    with pytest.raises(ValueError): exact_mcnemar(a,b)


def test_holm_restores_unsorted_order():
    assert holm_adjust([.03,.01,.02]) == pytest.approx([.04,.03,.04])


def test_original_logs_match_report():
    e, parsed = analyse_family(EXPERIMENTS, RESULTS_DIR)
    p, _ = analyse_family(CAMERA_EXPERIMENTS, RESULTS_DIR, parsed['E0'])
    assert list(e.success_count) == [28,0,0,0,17,17]
    assert list(p.success_count) == [28,28,28,28,27,16,28,25]
    assert list(e.holm_adjusted_p[1:]) == pytest.approx([3.725290298461914e-8]*3 + [.0068359375,.00738525390625])
    assert p.loc[p.key == 'P6','holm_adjusted_p'].item() == pytest.approx(.0146484375)


def test_aggregate_only_cannot_create_pairs():
    _, parsed = analyse_family(EXPERIMENTS, RESULTS_DIR)
    with pytest.raises(ValueError): paired_successes(parsed['E0'], replace(parsed['E1'], task_successes={}))


def test_missing_task_cannot_create_pairs():
    _, parsed = analyse_family(EXPERIMENTS, RESULTS_DIR)
    with pytest.raises(ValueError): paired_successes(parsed['E0'], replace(parsed['E1'], task_successes={0:[False]*3}))


@pytest.mark.parametrize('k,n', [(31,30),(-1,30),(0,-1)])
def test_invalid_success_counts(k,n):
    with pytest.raises(ValueError): wilson_ci(k,n)


def test_later_completed_runs():
    _,parsed=analyse_family(EXPERIMENTS,RESULTS_DIR)
    q,_=analyse_family(SUPPLEMENTARY_EXPERIMENTS,RESULTS_DIR,parsed['E0'])
    assert list(q.success_count)==[24,20,25,13]
    assert list(q.n_episodes)==[30]*4
