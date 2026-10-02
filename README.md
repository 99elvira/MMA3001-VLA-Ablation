\# MMA3001 - VLA Robustness Analysis



Ablation study on SmolVLA + LIBERO for robotic grasping.



\## Project Overview



This repository contains the computational workflow for an MMA3001 project:

\*\*Robustness Analysis of a Vision-Language-Action Model for Robotic Grasping\*\*.



We evaluate a pre-trained SmolVLA model on the LIBERO-object benchmark

under 6 configurations (E0–E5), without any fine-tuning. The goal is to

quantify the impact of input modality masking and inference mechanism changes.



\## Repository Structure



github\_repo/

\- src/           Core Python modules (parser, statistics, plotting)

\- tests/         Pytest test suite

\- docs/          HTML documentation and pipeline diagram

\- results/       Experiment outputs (summary.csv, report, figures)

\- scripts/       Batch scripts to reproduce experiments



\## Environment



\- OS: Windows 11

\- Python: 3.10 (Conda environment `vla\_project`)

\- GPU: NVIDIA RTX 5060 Laptop (sm\_120)

\- PyTorch: Nightly with CUDA 12.9

\- LeRobot, LIBERO, robosuite 1.4.0



See `requirements.txt` for Python dependencies.



\## Installation



1\. Create the Conda environment:

&#x20;  conda env create -f environment.yml

&#x20;  conda activate vla\_project



2\. Install PyTorch Nightly for RTX 5060:

&#x20;  pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu129



3\. Install remaining dependencies:

&#x20;  pip install -r requirements.txt



\## Reproducing the Experiments



Set the environment variables:

&#x20;  set HF\_HUB\_OFFLINE=1

&#x20;  set TRANSFORMERS\_OFFLINE=1

&#x20;  set MUJOCO\_GL=wgl

&#x20;  set PYOPENGL\_PLATFORM=wgl

&#x20;  set PYTHONPATH=D:\\MMA3001\_Project\\LIBERO



Run each ablation mode:

&#x20;  scripts\\run\_all\_experiments.bat



Regenerate analysis outputs:

&#x20;  scripts\\regenerate\_analysis.bat



\## Results Summary



| Experiment | Success Rate | Wilson 95% CI | Absolute Drop | Cohen's d | Holm p | Sig. |

|------------|--------------|---------------|---------------|-----------|--------|------|

| E0         | 93.33%       | \[78.68, 98.15]| —             | —         | —      | —    |

| E1         | 0.00%        | \[0.00, 11.35] | -93.33 pp     | NA        | 4.19e-14 | \*\*\* |

| E2         | 0.00%        | \[0.00, 11.35] | -93.33 pp     | NA        | 4.19e-14 | \*\*\* |

| E3         | 0.00%        | \[0.00, 11.35] | -93.33 pp     | NA        | 4.19e-14 | \*\*\* |

| E4         | 56.67%       | \[39.20, 72.62]| -36.67 pp     | -0.919    | 4.26e-03 | \*\* |

| E5         | 56.67%       | \[39.20, 72.62]| -36.67 pp     | -0.919    | 4.26e-03 | \*\* |



\## Testing



Run the test suite:

&#x20;  pytest tests/ -v --tb=short



Generate an HTML test report:

&#x20;  pytest tests/ --html=docs/test\_report.html



\## Documentation



Generate HTML documentation with pdoc:

&#x20;  pdoc src/ -o docs/



Open `docs/index.html` in a browser to view.



\## License



MIT License. See `LICENSE`.



\## AI Use



Claude (Anthropic) was used to assist with code debugging, statistical method

verification, and documentation structuring. All results were verified locally

with scipy and reviewed by the student.

