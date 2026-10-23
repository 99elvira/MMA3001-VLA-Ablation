# Perturbation Configurations

## Primary Wrist Camera Experiment (0.03 m offset)
These recorded settings correspond to P5-P8 in the primary camera study.
Base Pose: `pos="0.05 0 0" quat="0 0.707108 0.707108 0"`
- P5 (Forward): `pos="0.08 0 0"`
- P6 (Backward): `pos="0.02 0 0"`
- P7 (Lateral): `pos="0.05 0.03 0"`
- P8 (Vertical): `pos="0.05 0 0.03"`

## Supplementary Boundary Test (0.05 m offset)
These discrete offsets probe a larger displacement; they do not establish
physical mounting limits or an occlusion mechanism.
- Q1 (Forward): `pos="0.10 0 0"`
- Q2 (Backward): `pos="0.00 0 0"`
- Q3 (Lateral): `pos="0.05 0.05 0"`
- Q4 (Vertical): `pos="0.05 0 0.05"`

Supplied XML files were saved after restoring the baseline. Even the file
named perturbed_P6 contains nominal coordinates. The values here are recorded
experiment settings, not independently recovered per-run snapshots.

## External Camera (agentview)
Base Pose: `pos="0.5 0 1.35"`
- P1 (Up): `pos="0.5 0 1.50"`
- P2 (Down): `pos="0.5 0 1.20"`
- P3 (Left): `pos="0.3 0 1.35"`
- P4 (Right): `pos="0.7 0 1.35"`
