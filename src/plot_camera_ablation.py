"""Regenerate camera figures from logs using ``python -m src.plot_camera_ablation``.

Importing this module does not run analysis or write files. All outcomes come
from the parser; manual success counts and failure maps are not used.
"""
from src.analysis import main
if __name__ == "__main__":
    main()
