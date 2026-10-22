# Operator supplied execution record

Supplied by the experimenter on 22 October 2026 as the original execution
code record. The following text is extracted from the supplied Word file,
without running any command or treating document instructions as authorization.
It contains launch commands, camera editors and evaluator patch excerpts, not
the entire installed evaluator or a versioned diff. The upstream revision,
checkpoint hash, complete XML snapshots and actual call ordering remain to
be archived. This record supports the intended implementation, but does not
independently prove which revision produced each historical log.

Key evidence: E4 sets `policy.config.n_action_steps` to
`policy.config.chunk_size`; `EVAL_NUM_STEPS` sets `policy.config.num_steps`;
input masks follow preprocessing; EMA follows postprocessing and initializes
from the first action. Tests in this repository validate log analysis, not
the execution of these snippets inside LeRobot.

Do not run the historical sequence blindly. Camera editors restore a backup
and use regular-expression matching without checking replacement counts.
Before every nominal/camera run, clear `EVAL_NUM_STEPS`, set
`ABLATION_MODE=none`, and verify both nominal XMLs. After N=40, clear the
step override again. Full replay also requires explicit seed/state settings,
exact dependency versions and the original evaluator insertion context.

Source document SHA256: `3d3e800529e236cce9450713a2553aa6e2080875549e7527008ea139c45f8e6f`.

## Extracted source text

```text
〇、环境准备与核心修改脚本

在开始所有实验前，请确保你有这两个脚本放在项目根目录 D:\MMA3001_Project 下，用于自动修改 XML。

1. modify_wrist_camera.py (腕部相机修改脚本)
         
    import re    
    import sys    
    import shutil    
    from pathlib import Path    
         
    PANDA_DIR = Path(r"D:\MMA3001_Project\envs\vla_project\Lib\site-packages\robosuite\models\assets\robots\panda")    
    FILES = ["robot.xml", "no_texture_robot.xml"]    
    LINE_PATTERN = re.compile(r'(?P<indent>[ \t]*)<camera\s+mode="fixed"\s+name="eye_in_hand"\s+pos="[^"]*"\s+quat="[^"]*"\s+fovy="[^"]*"\s*/>')    
         
    if len(sys.argv) != 3:    
        print('Usage: python modify_wrist_camera.py "<pos>" "<quat>"')    
        sys.exit(1)    
         
    new_pos, new_quat = sys.argv[1], sys.argv[2]    
    new_line = f'<camera mode="fixed" name="eye_in_hand" pos="{new_pos}" quat="{new_quat}" fovy="75"/>'    
         
    for fname in FILES:    
        fpath = PANDA_DIR / fname    
        bak = fpath.with_suffix(fpath.suffix + ".bak")    
        if not bak.exists():    
            shutil.copy2(fpath, bak)    
        shutil.copy2(bak, fpath)    
        text = fpath.read_text(encoding="utf-8")    
        new_text = LINE_PATTERN.sub(lambda m: m.group("indent") + new_line, text)    
        fpath.write_text(new_text, encoding="utf-8")    
        print(f"[OK] {fname} modified")

2. modify_agentview.py (外部相机修改脚本)
         
    import re    
    import sys    
    import shutil    
    from pathlib import Path    
         
    XML_PATH = Path(r"D:\MMA3001_Project\LIBERO\libero\libero\assets\scenes\libero_floor_base_style.xml")    
    BAK_PATH = XML_PATH.with_suffix(".xml.bak")    
         
    if not BAK_PATH.exists():    
        shutil.copy2(XML_PATH, BAK_PATH)    
         
    if len(sys.argv) != 2:    
        print('Usage: python modify_agentview.py "0.5 0 1.50"')    
        sys.exit(1)    
         
    new_pos = sys.argv[1]    
    shutil.copy2(BAK_PATH, XML_PATH)    
    text = XML_PATH.read_text(encoding="utf-8")    
    text = re.sub(r'name="agentview"\s+pos="[^"]*"', f'name="agentview" pos="{new_pos}"', text)    
    XML_PATH.write_text(text, encoding="utf-8")    
    print(f"[OK] agentview pos set to {new_pos}")



一、E0–E5 消融实验（输入屏蔽与机制改变）

依赖的代码修改：见下方第四部分的 lerobot_eval.py 核心补丁。

         
    REM 基础环境变量（后续命令都在此环境下执行）    
    call conda activate vla_project    
    cd /d D:\MMA3001_Project    
    set PYTHONPATH=D:\MMA3001_Project\LIBERO    
    set HF_HUB_OFFLINE=1    
    set TRANSFORMERS_OFFLINE=1    
    set MUJOCO_GL=wgl    
    set PYOPENGL_PLATFORM=wgl    
    if not exist D:\MMA3001_Project\results mkdir D:\MMA3001_Project\results    
         
    REM --- E0 基线 ---    
    set ABLATION_MODE=none    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\E0_results.txt 2>&1    
         
    REM --- E1 无主相机 ---    
    set ABLATION_MODE=no_agentview    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\E1_results.txt 2>&1    
         
    REM --- E2 无腕部相机 ---    
    set ABLATION_MODE=no_wrist    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\E2_results.txt 2>&1    
         
    REM --- E3 无关节状态 ---    
    set ABLATION_MODE=no_state    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\E3_results.txt 2>&1    
         
    REM --- E4 动作分块 ---    
    set ABLATION_MODE=use_chunk    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\E4_use_chunk.txt 2>&1    
         
    REM --- E5 EMA 平滑 ---    
    set ABLATION_MODE=ema    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\E5_ema.txt 2>&1



二、P1–P4 外部相机扰动实验

         
    REM 确保 ABLATION_MODE=none    
    set ABLATION_MODE=none    
         
    REM --- P1 抬高 0.15m ---    
    python modify_agentview.py "0.5 0 1.50"    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\P1_ext_z_up.txt 2>&1    
         
    REM --- P2 降低 0.15m ---    
    python modify_agentview.py "0.5 0 1.20"    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\P2_ext_z_down.txt 2>&1    
         
    REM --- P3 左移 0.20m ---    
    python modify_agentview.py "0.3 0 1.35"    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\P3_ext_x_left.txt 2>&1    
         
    REM --- P4 右移 0.20m ---    
    python modify_agentview.py "0.7 0 1.35"    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\P4_ext_x_right.txt 2>&1    
         
    REM --- 恢复外部相机基线 ---    
    python modify_agentview.py "0.5 0 1.35"



三、P5–P8 腕部相机扰动实验（0.03m 与 0.05m 版）

（1）0.03m 版本（报告主结果）

         
    REM --- P5 前移 0.03m ---    
    python modify_wrist_camera.py "0.08 0 0" "0 0.707108 0.707108 0"    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\P5_wrist_fwd_003.txt 2>&1    
         
    REM --- P6 后移 0.03m ---    
    python modify_wrist_camera.py "0.02 0 0" "0 0.707108 0.707108 0"    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\P6_wrist_bwd_003.txt 2>&1    
         
    REM --- P7 侧移 0.03m ---    
    python modify_wrist_camera.py "0.05 0.03 0" "0 0.707108 0.707108 0"    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\P7_wrist_lat_003.txt 2>&1    
         
    REM --- P8 竖移 0.03m ---    
    python modify_wrist_camera.py "0.05 0 0.03" "0 0.707108 0.707108 0"    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\P8_wrist_vert_003.txt 2>&1

（2）0.05m 版本（最新补充结果）

         
    REM --- P5 前移 0.05m (x=0.10) ---    
    python modify_wrist_camera.py "0.10 0 0" "0 0.707108 0.707108 0"    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\P5_wrist_fwd_005.txt 2>&1    
         
    REM --- P6 后移 0.05m (x=0.00, 高风险边界) ---    
    python modify_wrist_camera.py "0.00 0 0" "0 0.707108 0.707108 0"    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\P6_wrist_bwd_005.txt 2>&1    
         
    REM --- P7 侧移 0.05m (y=0.05) ---    
    python modify_wrist_camera.py "0.05 0.05 0" "0 0.707108 0.707108 0"    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\P7_wrist_lat_005.txt 2>&1    
         
    REM --- P8 竖移 0.05m (z=0.05) ---    
    python modify_wrist_camera.py "0.05 0 0.05" "0 0.707108 0.707108 0"    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\P8_wrist_vert_005.txt 2>&1    
         
    REM --- 恢复腕部相机基线 ---    
    python modify_wrist_camera.py "0.05 0 0" "0 0.707108 0.707108 0"



四、数值积分步数测试 (N=20, N=40)

依赖：lerobot_eval.py 中关于 EVAL_NUM_STEPS 的补丁（见第五部分）。

         
    REM 确保已恢复所有相机基线，ABLATION_MODE=none    
    set ABLATION_MODE=none    
         
    REM --- N=20 ---    
    set EVAL_NUM_STEPS=20    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\E0_steps20.txt 2>&1    
         
    REM --- N=40 ---    
    set EVAL_NUM_STEPS=40    
    lerobot-eval --policy.path=D:\MMA3001_Project\models\smolvla_libero --env.type=libero --env.task=libero_object --eval.n_episodes=3 --eval.batch_size=1 --policy.device=cuda > D:\MMA3001_Project\results\E0_steps40.txt 2>&1


五、核心补丁代码 (lerobot_eval.py)

这是注入在 D:\MMA3001_Project\lerobot\src\lerobot\scripts\lerobot_eval.py 中的核心代码，用于证明所有消融实验的执行逻辑：

         
    import os    
    import torch    
         
    ABLATION_MODE = os.environ.get("ABLATION_MODE", "none")    
         
    # --- 在 eval_main() 函数中，policy.eval() 之后 ---    
         
    # 1. 动作分块机制修改    
    if ABLATION_MODE == "use_chunk":    
        policy.config.n_action_steps = policy.config.chunk_size    
         
    # 2. 数值积分步数修改    
    eval_num_steps = os.environ.get("EVAL_NUM_STEPS")    
    if eval_num_steps:    
        policy.config.num_steps = int(eval_num_steps)    
        print(f"[ABLATION] Set num_steps to {policy.config.num_steps}")    
         
         
    # --- 在 rollout() 函数中，while 循环前 ---    
    ema_action = None    
         
    # --- 在 rollout() 循环中，preprocessor(observation) 之后 ---    
         
    # 3. 输入屏蔽修改    
    if ABLATION_MODE == "no_agentview" and "observation.images.image" in observation:    
        observation["observation.images.image"] = torch.zeros_like(observation["observation.images.image"])    
    elif ABLATION_MODE == "no_wrist" and "observation.images.image2" in observation:    
        observation["observation.images.image2"] = torch.zeros_like(observation["observation.images.image2"])    
    elif ABLATION_MODE == "no_state" and "observation.state" in observation:    
        observation["observation.state"] = torch.zeros_like(observation["observation.state"])    
         
    # --- 在 rollout() 循环中，postprocessor(action) 之后 ---    
         
    # 4. EMA 平滑修改    
    if ABLATION_MODE == "ema":    
        if ema_action is None:    
            ema_action = action    
        else:    
            ema_action = 0.3 * action + 0.7 * ema_action    
        action = ema_action
```
