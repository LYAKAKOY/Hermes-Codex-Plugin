from pathlib import Path
import os
import sys


def add_src_to_path() -> None:
    root = os.environ.get("PLUGIN_ROOT")
    if root:
        plugin_root = Path(root)
    else:
        plugin_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(plugin_root / "src"))
