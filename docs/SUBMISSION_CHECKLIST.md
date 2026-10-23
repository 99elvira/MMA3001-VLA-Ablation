# Submission and presentation checklist

This checklist supports the course requirements; it is not a guarantee of a
particular mark. The report, presentation and repository must describe the
same measured study and its limitations.

## Narrative and computational method

- Begin with camera placement as the engineering concern, not an unverified
  claim that an early observation already established a statistical result.
- Explain input dependence, camera sensitivity, supplementary wrist magnitude
  probes and computational cost as distinct questions (see the README).
- Explain the conditioned vector field, Forward Euler update, signed step,
  artificial integration coordinate, 50-action chunk and 7 final controls.
- Distinguish integration updates from execution/feedback frequency. E4 is
  not the N=20/40 integration-step intervention.
- State that the step study measures task success and end-to-end time, not
  fixed-input solver error, isolated inference latency or numerical convergence.

## Evidence to show

- Keep the report body within the brief's 5-10 page limit, excluding references
  and appendices. Include figures, equations, interpretation and AI disclosure.
- Rehearse the approximately 4.5-minute presentation; show the actual repository,
  source, HTML API documentation and test report within the five-minute slot.
- Run the README verification commands in a clean environment and retain the
  generated test report. Tests validate analysis code, not simulator correctness.
- Submit the required repository clone ZIP alongside the report through the
  course submission system. A GitHub link alone is not that ZIP submission.
- Use paired Boolean outcomes for McNemar tests; jittered scatter coordinates
  are display offsets and must not be used as probabilities or test inputs.

## Remaining reproducibility limitations

Core execution snippets and camera edit commands are archived. Independent
full simulation replay still requires the complete versioned evaluator,
checkpoint identity/provenance, exact camera XML snapshots and a locked runtime
environment. Initial-state identities and shared initial noise were not logged.
Do not silently replace missing historical evidence with a new guessed file.

No additional experiment is asserted to be mandatory for submission. A
fixed-input, shared-noise integration comparison would address a different
question from the existing rollout study; N=40 would be a numerical reference,
not ground-truth correct robot actions. More matched repetitions and other
seeds/tasks would strengthen generalisation, but are not already demonstrated.
