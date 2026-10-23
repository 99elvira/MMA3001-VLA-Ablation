# Model Provenance and Integrity

- **Policy Name**: SmolVLA LIBERO Checkpoint
- **HuggingFace Source**: HuggingFaceVLA/smolvla_libero
- **Local Path**: D:\MMA3001_Project\models\smolvla_libero
- **VLM Backbone**: HuggingFaceTB/SmolVLM2-500M-Instruct (local path: D:\MMA3001_Project\models\SmolVLM2-500M-Instruct)
- **Download Date**: 2026-09-15 (Recorded by author)
- **Modifications**: The weights are strictly frozen. No fine-tuning or gradient updates were applied. Only inference-time hyperparameter overrides (masking, chunk size, N-steps) were performed.
- **Integrity and Reproducibility Note**: 
  - **Hash Verification Status**: SHA256 checksums against the remote HuggingFace registry were **not performed** for this submission. 
  - **Impact on Reproducibility**: The raw model weights were not altered. The results are reproducible as long as the local weight files remain intact. Future work should include a formal hash verification step (e.g., using `certutil -hashfile <file> SHA256`) to guarantee absolute provenance.