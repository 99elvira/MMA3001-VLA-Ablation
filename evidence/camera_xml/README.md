# Restored nominal camera snapshots

On 23 October 2026 the experimenter confirmed that the cameras had been
restored to their initial positions after the camera experiments. These
supplied files therefore document restored nominal configurations, not
per-condition historical snapshots. Original filenames and bytes are retained.

| Supplied file | Camera | Position (m) | SHA256 |
|---|---|---|---|
| libero_floor_original(1).xml | agentview | 0.5 0 1.35 | ee9aeb83cdbf6afe84d409120a8e709002bfa40af407253ce6da8cdf5c04aabd |
| panda_robot_original.xml | eye_in_hand | 0.05 0 0 | 51e3a4a6d54bcaf77e9d36a27372b871728590eedf53d4fd0e195525950eb988 |
| panda_robot_perturbed_P6.xml | eye_in_hand | 0.05 0 0 | 51e3a4a6d54bcaf77e9d36a27372b871728590eedf53d4fd0e195525950eb988 |

The two Panda files are byte-identical. Despite its filename, the P6 file
contains the restored nominal position. It is not evidence of a failed
historical perturbation, nor evidence of the pose actually used during P6.
The wrist camera is nested under `right_hand`, with quaternion
`0 0.707108 0.707108 0` and vertical field of view 75 degrees. The external
camera is directly under `worldbody`, with quaternion
`0.653 0.271 0.271 0.653`; its element does not specify a field of view.

P6's recorded x displacement -0.03 m implies position (0.02, 0, 0).
Q2's recorded x displacement -0.05 m implies position (0, 0, 0).
Those positions follow the operator record and nominal configuration;
they must not be described as independently recovered historical snapshots.
Any newly generated variants must be labelled reconstructed configurations.

These are supplied LIBERO/robosuite asset files, not newly authored project
analysis code. Upstream asset licences apply; the project MIT licence does
not relicense them. Relative mesh/texture dependencies are not bundled here.
The snapshots alone are not a standalone runnable simulation.
