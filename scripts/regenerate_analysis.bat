@echo off
REM Regenerate analysis outputs from existing results.

cd /d "%~dp0.."
python -m src.analysis
if errorlevel 1 exit /b 1
echo Analysis regenerated.
