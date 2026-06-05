from hermes_codex_plugin.application.skills.dto import SkillDraftDTO


def format_skill_draft(draft: SkillDraftDTO) -> str:
    lines = [
        "---",
        "name: {}".format(draft.name),
        "description: {}".format(draft.description),
        "---",
        "",
        "# {}".format(title_from_name(draft.name)),
        "",
        "Use this skill when the task matches the rules below.",
        "",
        "## Rules",
    ]
    for rule in draft.rules:
        lines.append("- {}".format(rule))
    lines.extend(
        [
            "",
            "## Workflow",
            "",
            "1. Check whether the task matches the rules.",
            "2. Apply the relevant rules before editing or answering.",
            "3. Verify the result with the project's normal checks when possible.",
            "",
        ]
    )
    return "\n".join(lines)


def title_from_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))
