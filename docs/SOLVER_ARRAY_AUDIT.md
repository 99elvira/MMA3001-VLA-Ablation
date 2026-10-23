# Exploratory single-action array audit

The original script and arrays are retained as supplied. Each array has shape
(1, 7) and dtype float32. They are not full 50-action chunks. N=10 is a
comparison reference, not a correct-action target.

| Label | MSE versus N10 | Maximum absolute difference |
|---|---|---|
| N20 | 0.0015628282 | 0.08264172 |
| N40 | 0.0036283776 | 0.12438238 |

The script supplies synthetic zero-valued images and robot state, sets the
random seed, and calls select_action. In the recorded LeRobot revision,
select_action returns one action and may reuse queued actions when
n_action_steps exceeds one. No reset occurs between these calls. The archived
evidence does not record queue occupancy or the initial noise tensor. It
therefore cannot establish that each result used fresh integration at the
labelled step count with identical noise. This does not prove queue reuse
occurred; it means the required control evidence is missing.

These differences must not be called numerical error, percentage action
error, a convergence result or evidence of training-distribution shift.
The separate 30-episode N=10/20/40 rollout study remains valid as the logged
task-success and end-to-end timing comparison, with the limitations in
INTEGRATION_STEPS.md. No new training or experiment is required to report
these existing observations honestly. The exploratory arrays are not used
to select the reference integration count.

If this question is investigated later, record fixed observations and noise,
request complete chunks directly, verify sampler calls, reset policy state,
and archive repeated timings. This is future work, not a completed result.
