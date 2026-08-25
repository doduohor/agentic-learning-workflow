#!/usr/bin/env python3
"""Создаёт минимальную Topic Workspace для сценария ``start/intake``."""

from __future__ import annotations

import argparse
import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path

try:
    from tools.check_topic_workspace import Finding, REQUIRED_ARTIFACTS, run_checker
except ModuleNotFoundError:  # direct execution: ``python3 tools/start_topic_intake.py``
    from check_topic_workspace import Finding, REQUIRED_ARTIFACTS, run_checker


SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*$")
TEMPLATE_FILENAMES = REQUIRED_ARTIFACTS


class IntakeValidationError(ValueError):
    """Входные данные или итог intake не проходят обязательную проверку."""


@dataclass(frozen=True)
class IntakeRequest:
    subject: str
    topic: str
    stable_slug: str
    learning_profile: str
    draft_goal: str
    learning_project: str = "Codex CLI learning system"


@dataclass(frozen=True)
class IntakeResult:
    workspace: Path
    findings: list[Finding]


def create_topic_workspace(root: Path, request: IntakeRequest, *, templates_dir: Path) -> IntakeResult:
    """Создаёт Topic Workspace и строку индекса либо откатывает обе записи.

    Публичный seam сценария — один аргументный вызов. Checker запускается после
    записи и при его error возвращает файловую систему к исходному состоянию.
    """
    validate_request(root, request, templates_dir)
    index = root / "topics" / "INDEX.md"
    workspace = root / "topics" / request.subject.lower() / request.stable_slug
    original_index = index.read_text(encoding="utf-8")

    try:
        workspace.mkdir(parents=True)
        for filename in TEMPLATE_FILENAMES:
            template = (templates_dir / filename).read_text(encoding="utf-8")
            (workspace / filename).write_text(render_template(filename, template, request), encoding="utf-8")
        index.write_text(append_index_row(original_index, request), encoding="utf-8")

        findings = run_checker(index, workspace)
        errors = [finding for finding in findings if finding.severity == "error"]
        if errors:
            raise IntakeValidationError(render_findings(errors))
        return IntakeResult(workspace=workspace, findings=findings)
    except Exception:
        index.write_text(original_index, encoding="utf-8")
        if workspace.exists():
            shutil.rmtree(workspace)
            remove_empty_parent(workspace.parent, root / "topics")
        raise


def validate_request(root: Path, request: IntakeRequest, templates_dir: Path) -> None:
    required = {
        "Subject": request.subject,
        "Topic": request.topic,
        "Stable Slug": request.stable_slug,
        "Learning Profile": request.learning_profile,
        "Черновая цель": request.draft_goal,
    }
    missing = [name for name, value in required.items() if not value.strip()]
    if missing:
        raise IntakeValidationError("Заполните: " + ", ".join(missing))
    for name, value in required.items():
        if any(character in value for character in ("|", "\r", "\n")):
            raise IntakeValidationError(f"{name} не должен содержать | или перевод строки.")
    if not SLUG_PATTERN.fullmatch(request.subject.lower()) or request.subject != request.subject.strip():
        raise IntakeValidationError("Subject должен быть ASCII kebab-case без пробелов.")
    if not SLUG_PATTERN.fullmatch(request.stable_slug):
        raise IntakeValidationError("Stable Slug должен быть ASCII kebab-case в нижнем регистре.")
    missing_templates = [name for name in TEMPLATE_FILENAMES if not (templates_dir / name).is_file()]
    if missing_templates:
        raise IntakeValidationError("Не найдены принятые templates: " + ", ".join(missing_templates))
    index = root / "topics" / "INDEX.md"
    if not index.is_file():
        raise IntakeValidationError("Не найден topics/INDEX.md.")
    workspace = root / "topics" / request.subject.lower() / request.stable_slug
    if workspace.exists():
        raise IntakeValidationError(f"Topic Workspace уже существует: {workspace}")
    index_text = index.read_text(encoding="utf-8")
    if f"`{request.stable_slug}`" in index_text:
        raise IntakeValidationError(f"Stable Slug уже занят в Topic Index: {request.stable_slug}")
    workspace_rel = f"topics/{request.subject.lower()}/{request.stable_slug}"
    if f"`{workspace_rel}`" in index_text:
        raise IntakeValidationError(f"Путь Topic Workspace уже занят: {workspace_rel}")


def render_template(filename: str, template: str, request: IntakeRequest) -> str:
    subject_slug = request.subject.lower()
    workspace = f"topics/{subject_slug}/{request.stable_slug}"
    substitutions = {
        "<Название темы>": request.topic,
        "<тема>": request.topic,
        "<stable-slug>": request.stable_slug,
        "<subject>": subject_slug,
        "<профиль>": request.learning_profile,
        "<проект>": request.learning_project,
        "YYYY-MM-DD": date.today().isoformat(),
    }
    rendered = template
    for source, target in substitutions.items():
        rendered = rendered.replace(source, target)
    rendered = rendered.replace(f"topics/{subject_slug}/{request.stable_slug}/", workspace)
    if filename == "Goal.md":
        return render_goal(rendered, request)
    return render_empty_owner_artifact(filename, rendered)


def render_goal(template: str, request: IntakeRequest) -> str:
    replacement = (
        "- Зачем изучаем (Purpose): " + request.draft_goal + "\n"
        "- Практический контекст (Applied Context): определить в diagnosing по Learning Profile.\n"
        "- Текущий маршрут (Current Route): диагностика до построения Blocks.\n"
        "- Главный риск забывания (Main Forgetting Risk): -"
    )
    template = re.sub(
        r"- Зачем изучаем \(Purpose\): .*\n- Практический контекст \(Applied Context\): .*\n- Текущий маршрут \(Current Route\): .*\n- Главный риск забывания \(Main Forgetting Risk\): .*",
        lambda _: replacement,
        template,
    )
    template = re.sub(r"\| <предпосылка> \| <статус> \| <Entity Reference или `-`> \| <следующее действие> \|", "| - | `-` | `-` | определить в diagnosing |", template)
    template = re.sub(r"\| `B01`[^\n]*\n\n### B01[^\n]*\n\n(?:.*\n){0,3}", "| - | - | - | - | - | - | - | провести diagnosing |\n\nBlocks создаются после diagnosing.\n", template)
    template = template.replace("| <Entity Reference или `-`> | `-` | `-` | <Entity Reference или `-`> | `-` |", "| `-` | `-` | `-` | `-` | `-` |")
    return template.replace("1. <следующее действие>", "1. Провести diagnosing: уточнить предпосылки и выбрать первый безопасный Block.")


def render_empty_owner_artifact(filename: str, template: str) -> str:
    replacements = {
        "Knowledge.md": [
            (r"\| <Entity Reference>[^\n]*\n\n## B01[\s\S]*?(?=## Knowledge Consolidation Trace)", "| `-` | Intake ещё не содержит Knowledge. | `-` | `-` |\n\n"),
        ],
        "Practice.md": [
            (r"\| `PA-(?:\d{8}|YYYYMMDD)-\d{2}`[^\n]*\n\n## Practice Attempts[\s\S]*?(?=## Session Archive Links)", "| `-` | `-` | `-` | `-` | `-` | `-` | `-` |\n\n## Practice Attempts\n\nПрактические попытки появляются после diagnosing.\n\n"),
        ],
        "Questions.md": [
            (r"\| `Q-(?:\d{8}|YYYYMMDD)-\d{2}`[^\n]*\n\n## Question Records[\s\S]*$", "| `-` | `-` | `-` | `-` | `-` | `-` | `-` |\n\n## Question Records\n\nВопросы появятся после diagnosing; Anki-карточки этот сценарий не создаёт.\n"),
        ],
        "Weaknesses.md": [
            (r"\| `W-(?:\d{8}|YYYYMMDD)-\d{2}`[^\n]*\n\n## Weakness Records[\s\S]*?(?=## Resolved/Archived Summary)", "| `-` | `-` | `-` | `-` | `-` | `-` | `-` |\n\n## Weakness Records\n\nEvidence-backed Weaknesses пока отсутствуют.\n\n"),
        ],
        "RepetitionLog.md": [
            (r"\| `REP-(?:\d{8}|YYYYMMDD)-\d{2}`[^\n]*\n\n## Active Repetition Records[\s\S]*?(?=## Failures Opened As Weaknesses)", "| `-` | `-` | `-` | `-` | `-` | `-` | `-` |\n\n## Active Repetition Records\n\nПовторения появляются после evidence-backed learning work.\n\n"),
        ],
        "Sources.md": [
            (r"\| `SRC-(?:\d{8}|YYYYMMDD)-\d{2}`[^\n]*\n\n## Source Checks[\s\S]*?(?=## Source Notes)", "| `-` | `-` | `-` | `-` | `-` | `-` | `-` |\n\n## Source Checks\n\nSource Checks появляются при чувствительных claims.\n\n"),
        ],
    }
    for pattern, replacement in replacements.get(filename, []):
        template = re.sub(pattern, replacement, template)
    template = re.sub(r"\[B01: название\]\(Goal\.md#b01---название\)", "[Goal.md](Goal.md)", template)
    template = re.sub(r"\[PA-\d{8}-\d{2}: название\]\(Practice\.md#pa-yyyymmdd-01---название\)", "[Practice.md](Practice.md)", template)
    template = re.sub(r"\[Q-\d{8}-\d{2}: название\]\(Questions\.md#q-yyyymmdd-01---название\)", "[Questions.md](Questions.md)", template)
    template = re.sub(r"\[W-\d{8}-\d{2}: название\]\(Weaknesses\.md#w-yyyymmdd-01---название\)", "[Weaknesses.md](Weaknesses.md)", template)
    template = re.sub(r"\[SRC-\d{8}-\d{2}: название\]\(Sources\.md#src-yyyymmdd-01---название\)", "[Sources.md](Sources.md)", template)
    template = template.replace("Knowledge Consolidation Trace", "Consolidation Trace")
    return template


def append_index_row(index_text: str, request: IntakeRequest) -> str:
    subject_slug = request.subject.lower()
    workspace = f"topics/{subject_slug}/{request.stable_slug}"
    row = (
        f"| {request.learning_profile} | {request.subject} | {request.topic} | `{request.stable_slug}` | `intake` | "
        f"`{workspace}` | [Goal.md]({subject_slug}/{request.stable_slug}/Goal.md) | - | - |\n"
    )
    topic_tree_match = re.search(r"^## Topic Tree\s*$", index_text, flags=re.MULTILINE)
    if topic_tree_match is None:
        return index_text.rstrip() + "\n" + row

    topics_table = index_text[:topic_tree_match.start()].rstrip()
    topic_tree = index_text[topic_tree_match.start():].lstrip("\n")
    return topics_table + "\n" + row + "\n" + topic_tree


def remove_empty_parent(directory: Path, stop_at: Path) -> None:
    if directory != stop_at and directory.is_dir() and not any(directory.iterdir()):
        directory.rmdir()


def render_findings(findings: list[Finding]) -> str:
    return "\n".join(finding.render() for finding in findings)


def main() -> int:
    parser = argparse.ArgumentParser(description="Создать Topic Workspace через start/intake.")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--stable-slug", required=True)
    parser.add_argument("--learning-profile", required=True)
    parser.add_argument("--draft-goal", required=True)
    parser.add_argument("--learning-project", default="Codex CLI learning system")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="корень Learning Project")
    parser.add_argument("--templates-dir", type=Path, default=Path(__file__).resolve().parents[1] / "docs/learning-system/templates")
    args = parser.parse_args()
    request = IntakeRequest(args.subject, args.topic, args.stable_slug, args.learning_profile, args.draft_goal, args.learning_project)
    try:
        result = create_topic_workspace(args.root.resolve(), request, templates_dir=args.templates_dir.resolve())
    except IntakeValidationError as error:
        print(f"Intake не создан: {error}")
        return 1
    print(f"Intake создан: {result.workspace}")
    if result.findings:
        for finding in result.findings:
            print(finding.render())
    else:
        print("Checker: findings отсутствуют.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
