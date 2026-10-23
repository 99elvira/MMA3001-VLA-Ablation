# Perturbation Configurations

## Primary Wrist Camera Experiment (0.03 m offset)
These configurations correspond to the main results reported in Section 4.7.
Base Pose: `pos="0.05 0 0" quat="0 0.707108 0.707108 0"`
- P5 (Forward): `pos="0.08 0 0"`
- P6 (Backward): `pos="0.02 0 0"`
- P7 (Lateral): `pos="0.05 0.03 0"`
- P8 (Vertical): `pos="0.05 0 0.03"`

## Supplementary Boundary Test (0.05 m offset)
These extreme offsets were tested to probe the physical limits of the camera mounting.
- P5 (Forward): `pos="0.10 0 0"`
- P6 (Backward): `pos="0.00 0 0"` (Camera touches the gripper center, causes severe occlusion or rendering anomalies)
- P7 (Lateral): `pos="0.05 0.05 0"`
- P8 (Vertical): `pos="0.05 0 0.05"`

## External Camera (agentview)
Base Pose: `pos="0.5 0 1.35"`
- P1 (Up): `pos="0.5 0 1.50"`
- P2 (Down): `pos="0.5 0 1.20"`
- P3 (Left): `pos="0.3 0 1.35"`
- P4 (Right): `pos="0.7 0 1.35"`