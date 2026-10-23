import os
os.environ["MUJOCO_GL"] = "wgl"
os.environ["PYOPENGL_PLATFORM"] = "wgl"

import torch
import numpy as np
from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
from lerobot.policies.factory import make_pre_post_processors

print("Loading policy...")
policy_path = r"D:\MMA3001_Project\models\smolvla_libero"
policy = SmolVLAPolicy.from_pretrained(policy_path)
policy.to("cuda")
policy.eval()

print("Loading preprocessor...")
preprocess, postprocess = make_pre_post_processors(policy.config, policy_path)

raw_obs = {
    "observation.images.image": torch.zeros((1, 3, 360, 360), device="cuda"),
    "observation.images.image2": torch.zeros((1, 3, 360, 360), device="cuda"),
    "observation.state": torch.zeros((1, 8), device="cuda"),
    "task": ["Pick up the red block and place it on the plate."]
}

print("Preprocessing observation...")
batch = preprocess(raw_obs)

results = {}
steps_list = [10, 20, 40]
output_dir = r"D:\MMA3001_Project\results\solver_steps_raw"
os.makedirs(output_dir, exist_ok=True)

for n in steps_list:
    print(f"Running inference with N={n}...")
    policy.config.num_steps = n
    
    # 确保每次推理前重置随机种子，以复用初始噪声
    torch.manual_seed(42)
    
    with torch.inference_mode():
        action_chunk = policy.select_action(batch)
        if isinstance(action_chunk, torch.Tensor):
            action_chunk = action_chunk.cpu().numpy()
            
    print(f"Action shape for N={n}: {action_chunk.shape}")
    
    # 保存原始数据以备审查
    np.save(os.path.join(output_dir, f"action_N{n}.npy"), action_chunk)
    results[n] = action_chunk

# 对比分析
base_action = results[10]
print("\n" + "="*50)
print(f"{'N':<5} | {'MSE (vs N=10)':<15} | {'Max Diff (vs N=10)':<20} | {'Mean Action Norm'}")
print("-" * 50)

for n in steps_list:
    act = results[n]
    mean_norm = np.mean(np.linalg.norm(act, axis=-1)) # 计算动作平均幅值以提供尺度参考
    
    if n == 10:
        print(f"{n:<5} | {0.0:<15.6f} | {0.0:<20.6f} | {mean_norm:.4f}")
    else:
        mse = np.mean((act - base_action) ** 2)
        max_diff = np.max(np.abs(act - base_action))
        print(f"{n:<5} | {mse:<15.6f} | {max_diff:<20.6f} | {mean_norm:.4f}")
print("="*50)
print(f"Raw arrays saved to: {output_dir}")