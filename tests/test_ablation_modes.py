"""Tests for ablation mode configuration consistency."""

import os
import pytest


VALID_MODES = {"none", "no_agentview", "no_wrist", "no_state", "use_chunk", "ema"}


def test_ablation_mode_env_default():
    """When ABLATION_MODE is not set, default should be 'none'."""
    mode = os.environ.get("ABLATION_MODE", "none")
    assert mode in VALID_MODES


def test_ablation_mode_set():
    """If ABLATION_MODE is set, it must be a valid mode."""
    mode = os.environ.get("ABLATION_MODE", "none")
    assert mode in VALID_MODES


def test_no_chunk_deprecated():
    """'no_chunk' should not be used as a valid ablation mode."""
    mode = os.environ.get("ABLATION_MODE", "none")
    assert mode != "no_chunk"