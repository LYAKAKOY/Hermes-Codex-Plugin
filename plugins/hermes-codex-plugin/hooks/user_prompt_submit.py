from _bootstrap import add_src_to_path

add_src_to_path()

from hermes_codex_plugin.presentation.hooks.controller import main


if __name__ == "__main__":
    main("UserPromptSubmit")
