@echo off
REM Regenerate analysis outputs from existing results.

cd /d D:\MMA3001_Project
conda activate vla_project

python github_repo\src\analysis.py
echo Analysis regenerated.