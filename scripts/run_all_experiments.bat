@echo off
setlocal
REM Historical evaluation launcher: requires the original patched runtime.
if not "%ABLATION_PATCH_VERIFIED%"=="1" (
  echo ERROR: provide and inspect the original LeRobot ablation patch first.
  echo Set ABLATION_PATCH_VERIFIED=1 only after confirming all five modes.
  exit /b 2
)
if not defined SMOLVLA_CHECKPOINT (
  echo ERROR: set SMOLVLA_CHECKPOINT to the original policy directory.
  exit /b 2
)
if not defined LIBERO_PATH (
  echo ERROR: set LIBERO_PATH to the original LIBERO checkout.
  exit /b 2
)
if not defined RUN_OUTPUT_DIR (
  echo ERROR: set RUN_OUTPUT_DIR to a NEW directory for fresh logs.
  exit /b 2
)
if exist "%RUN_OUTPUT_DIR%" (
  echo ERROR: output directory already exists; use a new name to preserve evidence.
  exit /b 2
)
mkdir "%RUN_OUTPUT_DIR%"
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
set MUJOCO_GL=wgl
set PYOPENGL_PLATFORM=wgl
set PYTHONPATH=%LIBERO_PATH%
for %%M in (none no_agentview no_wrist no_state use_chunk ema) do (
  set ABLATION_MODE=%%M
  lerobot-eval --policy.path="%SMOLVLA_CHECKPOINT%" --env.type=libero --env.task=libero_object --eval.batch_size=1 --eval.n_episodes=3 --seed=1000 > "%RUN_OUTPUT_DIR%\%%M_results.txt" 2>&1
  if errorlevel 1 exit /b 1
)
echo Completed new runs; inspect logs and poses before comparing with archived results.
