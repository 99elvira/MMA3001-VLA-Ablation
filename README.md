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

### Results (Primary: 0.03 m offset)

| Experiment | Camera   | Perturbation         | Success Rate | Delta vs E0   |
|------------|----------|----------------------|--------------|---------------|
| E0         | -        | baseline             | 93.33%       | 0 pp          |
| P1         | external | z +0.15 m            | 93.33%       | 0 pp          |
| P2         | external | z -0.15 m            | 93.33%       | 0 pp          |
| P3         | external | x -0.20 m            | 93.33%       | 0 pp          |
| P4         | external | x +0.20 m            | 93.33%       | 0 pp          |
| P5         | wrist    | x +0.03 m (forward)  | 90.00%       | -3.33 pp      |
| P6         | wrist    | x -0.03 m (backward) | **53.33%**   | **-40.00 pp** |
| P7         | wrist    | y +0.03 m (lateral)  | 93.33%       | 0 pp          |
| P8         | wrist    | z +0.03 m (vertical) | 83.33%       | -10.00 pp     |

### Supplementary Boundary Test (0.05 m offset)

To probe the physical limits of the camera mounting, a supplementary test with a 0.05 m offset was conducted for the wrist camera. Note that at 0.05 m backward (P6, `x=0.00`), the camera reaches the gripper center, causing severe occlusion or rendering anomalies.

| Experiment | Camera   | Perturbation (0.05 m) | Success Rate | Delta vs E0 |
|------------|----------|-----------------------|--------------|-------------|
| P5_ext     | wrist    | x +0.05 m (forward)   | 80.00%       | -13.33 pp   |
| P6_ext     | wrist    | x -0.05 m (backward)  | 66.67%       | -26.66 pp   |
| P7_ext     | wrist    | y +0.05 m (lateral)   | 83.33%       | -10.00 pp   |
| P8_ext     | wrist    | z +0.05 m (vertical)  | **43.33%**   | **-50.00 pp** |

### Key Findings

- External-camera pose is irrelevant within the tested range: identical success rate, identical failing-episode set, identical peak GPU memory.
- Wrist-camera pose is directionally sensitive. At 0.03 m, a backward shift along the tool axis significantly degrades success (McNemar p = 0.00183, Holm p = 0.01465). 
- Boundary test (0.05 m) reveals that extreme vertical shifts (P8_ext) cause the most severe performance drop (-50 pp), likely due to the loss of crucial local grasping geometry, whereas backward shifts approach full occlusion (P6_ext).
- Every wrist perturbation rearranges the failing-episode set, even when aggregate success is not statistically distinguishable from baseline. Masking and perturbing probe different failure modes.

## Testing

Run the test suite:

```
pytest tests/ -v --tb=short
```

Generate an HTML test report:

```
pytest tests/ --html=docs/test_report.html
```
## Solver Step Sensitivity Analysis

To evaluate the impact of integration steps on action execution, we compared the policy under N=10, 20, and 40. We do not treat N=10 as the ground truth; rather, it serves as the pre-trained reference baseline.

| Integration Steps (N) | Success Rate | Wilson 95% CI | Wall-clock Time (s/ep) | Relative Time vs N=10 | exact McNemar p |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **10 (default)** | **93.33% (28/30)** | [78.68, 98.15] | **111.99 s** | 1.00× (baseline) | — |
| **20** | 96.67% (29/30) | [83.33, 99.40] | 158.28 s | 1.41× | 1.00 |
| **40** | 93.33% (28/30) | [78.68, 98.15] | 315.17 s | 2.81× | 1.00 |

**Key Findings**:
- Increasing N changed the output action chunks (MSE = 0.00156 for N=20, MSE = 0.00363 for N=40 relative to N=10).
- However, this divergence did not yield a statistically significant improvement in success rate (McNemar p=1.00).
- Wall-clock time increased substantially, nearly tripling at N=40.
- **Conclusion**: In the tested settings, N=10 achieves the lowest inference time and provides no statistically detectable success-rate benefit when increased. It serves as the Pareto-optimal engineering trade-off for this fixed pre-trained model.

### Raw Action Outputs

To verify the sensitivity of the action generation to the Euler integration step size, we provided a fixed-input test script and the corresponding raw outputs:
- **Test Script**: `scripts/test_solver_convergence.py` (sets `torch.manual_seed(42)` to ensure identical initial noise).
- **Raw Outputs**: `results/solver_steps_raw/action_N10.npy`, `action_N20.npy`, and `action_N40.npy`.
These raw arrays (shape: `[50, 7]` each) allow exact reproduction of the MSE and Max Diff calculations reported in the paper.
## Documentation

Generate HTML documentation with pdoc:

```
pdoc src/ -o docs/
```

Open `docs/index.html` in a browser to view.

## License

MIT License. See `LICENSE`.

## Model Provenance
- Policy: `HuggingFaceVLA/smolvla_libero` (downloaded on 2026-09-15)
- VLM Backbone: `HuggingFaceTB/SmolVLM2-500M-Instruct`
- Local path: `D:\MMA3001_Project\models\smolvla_libero`
- Weights are unmodified; no fine-tuning was performed.

## AI Use

Claude (Anthropic) was used to assist with code debugging, statistical
method verification, and documentation structuring. All results were
verified locally with scipy and reviewed by the student.