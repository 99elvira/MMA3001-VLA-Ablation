# MMA3001 - VLA Robustness Analysis

Ablation study on SmolVLA + LIBERO for robotic grasping.

## Project Overview

This repository contains the computational workflow for an MMA3001 project:
**Robustness Analysis of a Vision-Language-Action Model for Robotic Grasping**.

We evaluate a pre-trained SmolVLA model on the LIBERO-object benchmark
under 6 input/mechanism configurations (E0-E5) and 8 camera-pose
configurations (P1-P8), without any fine-tuning. The goal is to quantify
the impact of input-modality masking, inference-mechanism changes, and
camera-geometry perturbations.

## Repository Structure

```
github_repo/
├── src/          Core Python modules (parser, statistics, plotting,
│                 camera-pose editors)
├── tests/        Pytest test suite
├── docs/         HTML documentation and pipeline diagram
├── results/      Experiment outputs (raw logs, summary.csv, figures)
├── scripts/      Batch scripts to reproduce experiments
└── README.md
```

## Environment

- OS: Windows 11
- Python: 3.10 (Conda environment `vla_project`)
- GPU: NVIDIA RTX 5060 Laptop (sm_120)
- PyTorch: Nightly with CUDA 12.9
- LeRobot, LIBERO, robosuite 1.4.0

See `requirements.txt` for Python dependencies.

## Installation

1. Create the Conda environment:

   ```
   conda env create -f environment.yml
   conda activate vla_project
   ```

2. Install PyTorch Nightly for RTX 5060:

   ```
   pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu129
   ```

3. Install remaining dependencies:

   ```
   pip install -r requirements.txt
   ```

## Reproducing the Experiments

Set the environment variables:

```
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
set MUJOCO_GL=wgl
set PYOPENGL_PLATFORM=wgl
set PYTHONPATH=D:\MMA3001_Project\LIBERO
```

Run each ablation mode:

```
scripts\run_all_experiments.bat
```

Regenerate analysis outputs:

```
scripts\regenerate_analysis.bat
```

## Results Summary (E0-E5)

| Experiment | Success Rate | Wilson 95% CI  | Absolute Drop | Cohen's d | Holm p   | Sig. |
|------------|--------------|----------------|---------------|-----------|----------|------|
| E0         | 93.33%       | [78.68, 98.15] | -             | -         | -        | -    |
| E1         | 0.00%        | [0.00, 11.35]  | -93.33 pp     | NA        | 4.19e-14 | ***  |
| E2         | 0.00%        | [0.00, 11.35]  | -93.33 pp     | NA        | 4.19e-14 | ***  |
| E3         | 0.00%        | [0.00, 11.35]  | -93.33 pp     | NA        | 4.19e-14 | ***  |
| E4         | 56.67%       | [39.20, 72.62] | -36.67 pp     | -0.919    | 4.26e-03 | **   |
| E5         | 56.67%       | [39.20, 72.62] | -36.67 pp     | -0.919    | 4.26e-03 | **   |

## Camera Perturbation Ablation (P1-P8)

Following the input-masking and mechanism ablations (E0-E5), we added a
second experiment class: geometric perturbation of the two camera streams.

### Design

- External agentview camera: vertical +/- 0.15 m (P1, P2), horizontal +/- 0.20 m (P3, P4).
- Wrist camera `robot0_eye_in_hand`: 0.03 m along each local axis
  (P5 forward, P6 backward, P7 lateral, P8 vertical).
- Each configuration: 10 LIBERO-object tasks x 3 episodes = 30 episodes.

### Results

| Experiment | Camera   | Perturbation         | Success Rate | Delta vs E0   |
|------------|----------|----------------------|--------------|---------------|
| E0         | -        | baseline             | 93.33%       | 0 pp          |
| P1         | external | z +0.15 m            | 93.33%       | 0 pp          |
| P2         | external | z -0.15 m            | 93.33%       | 0 pp          |
| P3         | external | x = 0.30 m           | 93.33%       | 0 pp          |
| P4         | external | x = 0.70 m           | 93.33%       | 0 pp          |
| P5         | wrist    | x +0.03 m (forward)  | 90.00%       | -3.33 pp      |
| P6         | wrist    | x -0.03 m (backward) | **53.33%**   | **-40.00 pp** |
| P7         | wrist    | y +0.03 m (lateral)  | 93.33%       | 0 pp          |
| P8         | wrist    | z +0.03 m (vertical) | 83.33%       | -10.00 pp     |

### Key Findings

- External-camera pose is irrelevant within the tested range: identical
  success rate, identical failing-episode set, identical peak GPU memory.
- Wrist-camera pose is directionally sensitive. A 0.03 m backward shift
  along the tool axis halves success (Fisher p approximately 2.1e-04,
  Cohen's d approximately -1.55). Vertical shift costs 10 pp. Forward and
  lateral shifts are tolerated.
- Every wrist perturbation rearranges the failing-episode set, even
  when aggregate success is not statistically distinguishable from
  baseline. Masking and perturbing probe different failure modes.

### Scripts and Figures

- `src/modify_wrist_camera.py` - edit the wrist camera pose in Panda XML.
- `src/plot_camera_ablation.py` - regenerate the two figures.
- `results/figures/fig_4_7a_success_rate.png`
- `results/figures/fig_4_7b_failure_heatmap.png`

**Note:** The external-camera perturbations (P1-P4) were applied by
editing the `agentview` line in
`LIBERO/libero/libero/assets/scenes/libero_floor_base_style.xml`.

## Testing

Run the test suite:

```
pytest tests/ -v --tb=short
```

Generate an HTML test report:

```
pytest tests/ --html=docs/test_report.html
```

## Documentation

Generate HTML documentation with pdoc:

```
pdoc src/ -o docs/
```

Open `docs/index.html` in a browser to view.

## License

MIT License. See `LICENSE`.

## AI Use

Claude (Anthropic) was used to assist with code debugging, statistical
method verification, and documentation structuring. All results were
verified locally with scipy and reviewed by the student.