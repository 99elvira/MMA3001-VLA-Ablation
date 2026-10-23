# Camera conditions and source provenance

Before the later integration-step study, success totals were checked against
all 24 text files then present, with 18 distinct log contents: six early logs
duplicate the six ablation logs byte for byte. The ZIP contains 14 copies of
existing primary logs. None supplies additional independent repetitions.
See `results/raw_log_audit.json` for relative filenames and SHA256 hashes.

The later `积分步数` folder adds two full logs and two corresponding aggregate
extracts, representing **two new runs**, not four repetitions. The 28-file
count described that earlier snapshot. The subsequent two-folder audit found
42 text files in `实验数据` and 18 in `实验数据(1)`: all 60 match archived
repository contents byte for byte. There are 22 distinct file contents but
only 20 experimental conditions, because two contents are aggregate extracts.
Three ZIP copies each contain 14 existing logs; they add no repetitions.
See [the separate step-study record](INTEGRATION_STEPS.md) and
`results/integration_manifest.json`. Camera definitions and totals below are
unchanged; N=20/40 are not additional camera perturbations.

The mapping below follows the experiment record and operator confirmations.
The later [operator execution record](OPERATOR_EXECUTION_RECORD.md) supplies
camera edit commands consistent with these coordinates. It is not a complete
XML snapshot or proof of a successful regex replacement in a historical run.
The logs independently verify outcomes, but do not preserve edited camera XML.
Exact XML variants are still needed to independently reproduce geometry.

Restored nominal XML files were subsequently supplied and are archived in
[the camera evidence folder](../evidence/camera_xml/README.md). The operator
confirmed that cameras were reset after the experiments. Both Panda files,
including the one named `perturbed_P6`, contain the same nominal configuration.
They confirm the supplied baseline positions but not historical per-run poses.

| ID | Camera and signed translation (m) | Direction label | Success | Original local filename |
|---|---|---|---|---|
| P1 | External z +0.15 | up | 28/30 | P1_ext_z_up_results.txt |
| P2 | External z -0.15 | down | 28/30 | P2_ext_z_down_results.txt |
| P3 | External x -0.20 | negative x | 28/30 | P3_ext_x_left_results.txt |
| P4 | External x +0.20 | positive x | 28/30 | P4_ext_x_right_results.txt |
| P5 | Wrist local x +0.03 | forward | 27/30 | P5_wrist_results.txt |
| P6 | Wrist local x -0.03 | backward | 16/30 | P6_wrist_results.txt |
| P7 | Wrist local y +0.03 | lateral | 28/30 | P7_wrist_results.txt |
| P8 | Wrist local z +0.03 | vertical | 25/30 | P8_wrist_results.txt |
| Q1 | Wrist local x +0.05 | forward | 24/30 | P5_x10.txt |
| Q2 | Wrist local x -0.05 | backward | 20/30 | P6_boundary_x0(1).txt |
| Q3 | Wrist local y +0.05 | lateral | 25/30 | P7_y05(1).txt |
| Q4 | Wrist local z +0.05 | vertical | 13/30 | P8_z05.txt |

## Displacement versus absolute position

Reported nominal positions: external `(0.50, 0, 1.35)` m and wrist local
`(0.05, 0, 0)` m. A signed displacement is added to the nominal position:

- Wrist x +0.05: final `(0.10, 0, 0)` m, Q1, **24/30**.
- Wrist x -0.05: final `(0, 0, 0)` m, Q2, **20/30**.
- Wrist y +0.05: final `(0.05, 0.05, 0)` m, Q3, **25/30**.
- Wrist z +0.05: final `(0.05, 0, 0.05)` m, Q4, **13/30**.

These final coordinates are derived from the reported nominal values, not
independently read from the logs. The complete machine-readable mapping is
`results/camera_condition_registry.csv`. Do not identify the condition by its
success rate, interchange y/lateral and z/vertical, or call final x=0.05 an
x displacement of +0.05. Local z does not necessarily remain world-up while
the wrist moves. The coordinate-frame transform requires the original XML.

## Interpretation

Increasing magnitude from 0.03 to 0.05 m is a **66.7% increase**, not doubling.
Backward success rises from 16/30 to 20/30; z success falls from 25/30 to 13/30.
Observed rates therefore do not show a uniformly monotone magnitude effect.
The report does not claim a direct significance test between magnitudes.
P6 and Q4 remain significant against E0 under Holm correction across all twelve
camera comparisons (0.02014160 and 0.00329590 respectively).

`python -m src.analysis` regenerates axis-labelled figures
`results/figures/primary_camera_axes.png` and
`results/figures/wrist_axes_magnitudes.png`, in addition to existing outputs.
