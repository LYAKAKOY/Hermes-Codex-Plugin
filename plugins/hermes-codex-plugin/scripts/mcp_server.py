from pathlib import Path
import os
import sys


def main() -> None:
    root = os.environ.get("PLUGIN_ROOT")
    if root:
        plugin_root = Path(root)
    else:
        plugin_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(plugin_root / "src"))

    from hermes_codex_plugin.presentation.mcp.server import main as server_main

    server_main()


if __name__ == "__main__":
    main()
