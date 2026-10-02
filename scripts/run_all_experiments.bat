@echo off
REM Run all ablation experiments for MMA3001 project.

set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
set MUJOCO_GL=wgl
set PYOPENGL_PLATFORM=wgl
set PYTHONPATH=D:\MMA3001_Project\LIBERO

cd /d D:\MMA3001_Project

echo [E0] Baseline
set ABLATION_MODE=none
lerobot-eval --policy.path="D:\MMA3001_Project\models\smolvla_libero" --env.type=libero --env.task=libero_object --eval.batch_size=1 --eval.n_episodes=3 > results\baseline_results.txt 2>&1

echo [E1] No agentview
set ABLATION_MODE=no_agentview
lerobot-eval --policy.path="D:\MMA3001_Project\models\smolvla_libero" --env.type=libero --env.task=libero_object --eval.batch_size=1 --eval.n_episodes=3 > results\no_agentview_results.txt 2>&1

echo [E2] No wrist
set ABLATION_MODE=no_wrist
lerobot-eval --policy.path="D:\MMA3001_Project\models\smolvla_libero" --env.type=libero --env.task=libero_object --eval.batch_size=1 --eval.n_episodes=3 > results\no_wrist_results.txt 2>&1

echo [E3] No state
set ABLATION_MODE=no_state
lerobot-eval --policy.path="D:\MMA3001_Project\models\smolvla_libero" --env.type=libero --env.task=libero_object --eval.batch_size=1 --eval.n_episodes=3 > results\no_state_results.txt 2>&1

echo [E4] Use chunk
set ABLATION_MODE=use_chunk
lerobot-eval --policy.path="D:\MMA3001_Project\models\smolvla_libero" --env.type=libero --env.task=libero_object --eval.batch_size=1 --eval.n_episodes=3 > results\use_chunk_results.txt 2>&1

echo [E5] EMA
set ABLATION_MODE=ema
lerobot-eval --policy.path="D:\MMA3001_Project\models\smolvla_libero" --env.type=libero --env.task=libero_object --eval.batch_size=1 --eval.n_episodes=3 > results\ema_results.txt 2>&1

echo All experiments complete.