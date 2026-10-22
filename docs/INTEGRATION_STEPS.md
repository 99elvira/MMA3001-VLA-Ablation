# Integration-step task study

The later N=20 and N=40 runs supplement the original N=10 E0 reference.
They compare closed-loop task completion and end-to-end evaluation time,
not fixed-input action accuracy or isolated inference latency.

| N | Success | Wilson 95% CI (%) | Mean eval_ep_s (s) | Time / N10 | E0-only / N-only | Exact McNemar p | Holm p (2 contrasts) |
|---|---|---|---|---|---|---|---|
| 10 | 28/30 (93.33%) | 78.68–98.15 | 111.99 | 1.00 | — | — | — |
| 20 | 29/30 (96.67%) | 83.33–99.41 | 158.28 | 1.41 | 0 / 1 | 1.00 | 1.00 |
| 40 | 28/30 (93.33%) | 78.68–98.15 | 315.17 | 2.81 | 2 / 2 | 1.00 | 1.00 |

N=20 has one observed additional success, but no statistically detected
improvement against N=10. N=40 has equal totals but different failed episodes.
Neither p=1 nor overlapping intervals establish equivalence. N=10 remains a
cost-conscious reference within these tested settings, not a proven optimum.

## Sources and settings

- `results/baseline_results.txt`: existing E0, not a new N=10 repeat.
- `results/integration/E0_steps20.txt` and `E0_steps40.txt`: complete new logs.
- `results/integration/N=20.txt` and `N=40.txt`: aggregate extracts of the same
  two runs, not two additional repetitions.
- Complete logs print the default `num_steps=10` before the explicit messages
  `[ABLATION] Set num_steps to 20` or `40`. These later messages support the
  recorded setting. The later [operator execution record](OPERATOR_EXECUTION_RECORD.md)
  contains the step-override snippet, but not the complete versioned evaluator.
- Printed settings include seed 1000, `init_states=True`, `n_action_steps=1`,
  the same local checkpoint path, ten tasks and three episodes per task.
  Initial-state identities, checkpoint hashes and initial noise tensors are
  not archived, so full matched-input numerical verification is not possible.

`python -m src.analysis` now regenerates this study as well as all original
families. `python -m src.integration` regenerates only this study. Outputs:
`integration_summary.csv`, `integration_outcomes.csv`,
`integration_manifest.json` and `figures/integration_steps.png` under `results`.
The manifest records original-file SHA256 hashes and distinguishes extracts
from independent runs. New regression tests check the counts, pairs, timing,
extract consistency and precedence of runtime overrides over defaults.

## Numerical interpretation

Forward Euler uses a step magnitude of 1/N. Increasing N therefore refines
the integration grid, but the available outcomes measure complete robot
rollouts, whose observations change after each action. There are no archived
fixed-observation, fixed-initial-noise action differences at N=10,20,40.
Consequently, these runs do not demonstrate first-order convergence or
quantify discretisation error. N=40 is not ground-truth action output.

`eval_ep_s` includes policy calls, simulation, rendering and termination effects.
One mean per setting, without independent timing repetitions or component
profiling, cannot establish a latency scaling law or inference-only speedup.
The camera-study conclusions and twelve-comparison family remain unchanged.
