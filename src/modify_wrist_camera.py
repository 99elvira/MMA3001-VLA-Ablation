import re
import sys
import shutil
from pathlib import Path

PANDA_DIR = Path(r"D:\MMA3001_Project\envs\vla_project\Lib\site-packages\robosuite\models\assets\robots\panda")
FILES = ["robot.xml", "no_texture_robot.xml"]

LINE_PATTERN = re.compile(
    r'(?P<indent>[ \t]*)<camera\s+mode="fixed"\s+name="eye_in_hand"\s+'
    r'pos="[^"]*"\s+quat="[^"]*"\s+fovy="[^"]*"\s*/>'
)

def main():
    if len(sys.argv) != 3:
        print('Usage: python modify_wrist_camera.py "<pos>" "<quat>"')
        print('Example: python modify_wrist_camera.py "0.08 0 0" "0 0.707108 0.707108 0"')
        sys.exit(1)

    new_pos, new_quat = sys.argv[1], sys.argv[2]
    new_line = (
        f'<camera mode="fixed" name="eye_in_hand" '
        f'pos="{new_pos}" quat="{new_quat}" fovy="75"/>'
    )

    for fname in FILES:
        fpath = PANDA_DIR / fname
        bak = fpath.with_suffix(fpath.suffix + ".bak")
        if not bak.exists():
            shutil.copy2(fpath, bak)
            print(f"[BACKUP] {bak}")
        shutil.copy2(bak, fpath)

        text = fpath.read_text(encoding="utf-8")
        new_text, n = LINE_PATTERN.subn(
            lambda m: m.group("indent") + new_line, text
        )
        if n == 0:
            print(f"[WARN] no eye_in_hand camera line matched in {fname}")
        else:
            fpath.write_text(new_text, encoding="utf-8")
            print(f"[OK] {fname}: replaced {n} line(s)")

if __name__ == "__main__":
    main()