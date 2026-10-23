# Reproducibility status

## Analysis evidence

The supplied original logs support 30 outcomes for each condition and the
published count/paired-test tables. Regenerate them with `python -m src.analysis`.
Tests include regression checks of E0-E5 counts and the P6 corrected p-value.

Historical evaluation environment from the README: Windows 11, Python 3.10,
NVIDIA RTX 5060 Laptop GPU, PyTorch nightly CUDA 12.9, robosuite 1.4.0.
This is historical metadata, not an independently recovered version lock.
`requirements.txt` describes the CPU analysis dependencies only. The accompanying
`environment.yml` is historical and does not install a complete evaluation stack.

## Original inference runs

The logs record:

- seed 1000, `init_states=True`, 10 tasks, 3 episodes/task;
- local checkpoint `D:/MMA3001_Project/models/smolvla_libero`;
- backbone `HuggingFaceTB/SmolVLM2-500M-Instruct`, or a local copy of that backbone;
- `chunk_size=50`, `num_steps=10`, and `n_action_steps=1` in printed configs;
- 360x360x3 environment images, 3x256x256 declared policy image features,
  `resize_imgs_with_padding=(512,512)`, tokenizer maximum length 48;
- configured 520 steps, with observed rollout caps of 280 steps.

E4's printed config says `n_action_steps=1`. The later supplied
[operator execution record](OPERATOR_EXECUTION_RECORD.md) contains the core
patch setting `policy.config.n_action_steps = policy.config.chunk_size`.
This supports the intended full-chunk mode and explains the earlier printed
default, but the complete installed evaluator, upstream revision and exact
call order are not archived. The historical log alone cannot prove the code
revision that executed. The record also supplies step overrides, input masks,
EMA initialization and camera edit commands; these snippets were not replayed.

Before claiming full simulator reproducibility, archive or identify:

1. The complete original evaluator/ablation revision and upstream LeRobot commit
   (core excerpts are now archived, but do not replace the complete file/diff).
2. Policy checkpoint source, revision, configuration and SHA256 manifest.
3. Runtime dependency versions and the GPU software environment.
4. Exact external/wrist XML variants and nominal-pose backups.
5. Per-condition initial-state identifiers, commanded actions and step timing.

Update on 23 October 2026: restored nominal external and wrist XML snapshots
are now [archived with hashes](../evidence/camera_xml/README.md). The operator
confirmed restoration after experiments; the file named `perturbed_P6` is
byte-identical to the nominal Panda XML. Historical perturbed snapshots remain
unavailable. This evidence does not supply checkpoint files, the evaluator,
runtime versions or fixed-input numerical verification results.

The existing `run_all_experiments.bat` is a historical launcher. It now checks
for explicit runtime paths and patch acknowledgement; it is not a replacement
for these missing components. It writes new logs to a separate run directory,
not over the archived evidence.

## Additional local records

The later N=20/40 complete logs and aggregate extracts are archived under
`results/integration/`. Runtime override messages follow earlier default
configuration printouts. Their task/timing analysis is reproducible, but
fixed-input action differences, initial-noise tensors and isolated model
latencies are absent. See [integration-step evidence](INTEGRATION_STEPS.md).

The experimenter confirmed that later completed files in the `0.05` folder
are the ±0.05 m wrist runs. They are archived as Q1-Q4 without changing the
original P1-P8 labels. Counts are 24/30, 20/30, 25/30 and 13/30. Exact XML
revisions still need archiving for full simulator reproduction. SHA256 hashes
and original filenames are recorded in `results/data_manifest.json`.
Both separate exploratory Holm results and a combined 12-camera correction
are published, avoiding a selective choice of the more favourable correction.
