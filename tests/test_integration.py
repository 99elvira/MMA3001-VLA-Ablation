"""Regression and provenance checks for the later integration-step runs."""
from pathlib import Path
import pytest
from src.config import RESULTS_DIR
from src.integration import analyse_steps, recorded_steps


def test_original_step_results():
    """Recompute totals, paired failures, uncertainty and wall-clock ratios."""
    table, manifest = analyse_steps(RESULTS_DIR)
    assert table.success_count.tolist() == [28, 29, 28]
    assert table.eval_ep_s.tolist() == pytest.approx([111.9914458433787, 158.27716511090597, 315.17306163311])
    assert table.time_ratio_vs_N10.tolist() == pytest.approx([1, 1.4132969176, 2.8142601648], rel=1e-6)
    assert table.mcnemar_p.iloc[1:].tolist() == [1, 1]
    assert table.holm_adjusted_p.iloc[1:].tolist() == [1, 1]
    assert table.baseline_only.iloc[1:].tolist() == [0, 2]
    assert table.condition_only.iloc[1:].tolist() == [1, 2]
    assert len(manifest["outcomes"]) == 90
    assert manifest["distinct_new_runs"] == 2


@pytest.mark.parametrize("content", ["'num_steps': 10", "[ABLATION] Set num_steps to 0",
    "[ABLATION] Set num_steps to 20\n[ABLATION] Set num_steps to 40"])
def test_missing_or_conflicting_override_rejected(tmp_path: Path, content: str):
    """A printed default is not evidence of a later runtime override."""
    path = tmp_path / "run.txt"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        recorded_steps(path)


def test_runtime_override_takes_precedence(tmp_path: Path):
    """Read explicit N=20 even when configuration was printed before the edit."""
    path = tmp_path / "run.txt"
    path.write_text("'num_steps': 10\n[ABLATION] Set num_steps to 20", encoding="utf-8")
    assert recorded_steps(path) == 20
