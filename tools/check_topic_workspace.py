#!/usr/bin/env python3
"""Read-only проверка Topic Index и одной Topic Workspace."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REQUIRED_ARTIFACTS = (
    "Goal.md", "Knowledge.md", "Practice.md", "Questions.md", "Weaknesses.md",
    "RepetitionLog.md", "Sources.md",
)
ID_PATTERNS = {
    "B": re.compile(r"B\d{2}$"),
    "PA": re.compile(r"PA-\d{8}-\d{2}$"),
    "Q": re.compile(r"Q-\d{8}-\d{2}$"),
    "W": re.compile(r"W-\d{8}-\d{2}$"),
    "REP": re.compile(r"REP-\d{8}-\d{2}$"),
    "SRC": re.compile(r"SRC-\d{8}-\d{2}$"),
}
ID_LABELS = {
    "Goal.md": ("Block ID", "ID блока"),
    "Practice.md": ("Practice Attempt ID", "ID попытки"),
    "Questions.md": ("Question ID", "ID вопроса"),
    "Weaknesses.md": ("Weakness ID", "ID слабого места"),
    "RepetitionLog.md": ("Repetition ID", "ID повторения"),
    "Sources.md": ("Source ID", "ID источника"),
}
ID_KINDS = {
    "Goal.md": "B",
    "Practice.md": "PA",
    "Questions.md": "Q",
    "Weaknesses.md": "W",
    "RepetitionLog.md": "REP",
    "Sources.md": "SRC",
}
OWNED_FIELDS = (
    "Topic State", "Состояние темы", "Active Block", "Активный блок",
    "Block Status", "Статус блока", "Mastery Level", "Уровень освоения",
)


@dataclass(frozen=True)
class Finding:
    id: str
    severity: str
    gate_impact: str
    file: str
    entity_or_reference: str
    explanation: str

    def render(self) -> str:
        return (
            f"[{self.id}] {self.severity}; {self.gate_impact}; файл: {self.file}; "
            f"сущность/ссылка: {self.entity_or_reference}; исправление: {self.explanation}"
        )


def markdown_slug(heading: str) -> str:
    normalized = heading.strip().lower()
    normalized = re.sub(r"[\[\]`*_~]", "", normalized)
    normalized = re.sub(r"[^\w\s-]", "", normalized, flags=re.UNICODE)
    return re.sub(r"\s", "-", normalized).strip("-")


def read_files(workspace: Path) -> dict[str, str]:
    return {
        name: (workspace / name).read_text(encoding="utf-8")
        for name in REQUIRED_ARTIFACTS
        if (workspace / name).is_file()
    }


def headings(text: str) -> set[str]:
    return {
        markdown_slug(match.group(1))
        for match in re.finditer(r"^#{1,6}\s+(.+?)\s*$", text, flags=re.MULTILINE)
    }


def append_finding(findings: list[Finding], finding_id: str, severity: str, impact: str, file: str, entity: str, explanation: str) -> None:
    findings.append(Finding(finding_id, severity, impact, file, entity, explanation))


def validate_markdown_links(workspace: Path, files: dict[str, str], findings: list[Finding]) -> None:
    for name, text in files.items():
        for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            target_path, _, anchor = target.partition("#")
            destination = (workspace / target_path).resolve() if target_path else (workspace / name).resolve()
            if not destination.is_file():
                append_finding(findings, "missing-target", "error", "blocks handoff", name, target, "создайте target file или исправьте Markdown-ссылку")
                continue
            if anchor:
                target_text = destination.read_text(encoding="utf-8")
                if anchor not in headings(target_text):
                    append_finding(findings, "missing-target", "error", "blocks handoff", name, target, "исправьте anchor на существующий heading")


def validate_ids(files: dict[str, str], findings: list[Finding]) -> None:
    for name, labels in ID_LABELS.items():
        text = files.get(name, "")
        prefix = ID_KINDS[name]
        for label in labels:
            for value in re.findall(rf"{re.escape(label)}[^\n`]*`([^`]+)`", text):
                if value != "-" and not ID_PATTERNS[prefix].fullmatch(value):
                    append_finding(findings, "invalid-id", "error", "blocks handoff", name, value, f"используйте формат {ID_PATTERNS[prefix].pattern.rstrip('$')}")
        record_ids = re.findall(
            rf"^###\s+({ID_PATTERNS[prefix].pattern[:-1]})\s+-", text, flags=re.MULTILINE
        )
        if len(record_ids) != len(set(record_ids)):
            append_finding(findings, "duplicate-id", "error", "blocks handoff", name, prefix, "сделайте ID detailed records уникальными")
        record_set = set(record_ids)
        first_record = re.search(
            rf"^###\s+{ID_PATTERNS[prefix].pattern[:-1]}\s+-", text, flags=re.MULTILINE
        )
        index_text = text[:first_record.start()] if first_record else text
        index_ids = re.findall(ID_PATTERNS[prefix].pattern[:-1], index_text)
        for entity_id in sorted(set(index_ids) - record_set):
            append_finding(
                findings,
                "missing-record",
                "error",
                "blocks handoff",
                name,
                entity_id,
                "добавьте detailed record для ID из индекса или удалите устаревшую строку",
            )


def record_ids_by_kind(files: dict[str, str]) -> dict[str, set[str]]:
    records: dict[str, set[str]] = {kind: set() for kind in ID_PATTERNS}
    for name, kind in ID_KINDS.items():
        records[kind] = set(
            re.findall(
                rf"^###\s+({ID_PATTERNS[kind].pattern[:-1]})\s+-",
                files.get(name, ""),
                flags=re.MULTILINE,
            )
        )
    return records


def validate_entity_references(files: dict[str, str], findings: list[Finding]) -> None:
    records = record_ids_by_kind(files)
    for name, text in files.items():
        for kind, pattern in ID_PATTERNS.items():
            for entity_id in set(re.findall(pattern.pattern[:-1], text)):
                if entity_id not in records[kind]:
                    append_finding(
                        findings,
                        "missing-entity-reference",
                        "error",
                        "blocks handoff",
                        name,
                        entity_id,
                        "создайте target entity или исправьте Entity Reference",
                    )


def validate_owner_invariants(files: dict[str, str], findings: list[Finding]) -> None:
    for name, text in files.items():
        if name != "Goal.md":
            for field in OWNED_FIELDS:
                if re.search(rf"^- .*{re.escape(field)}.*:\s*`", text, flags=re.MULTILINE):
                    append_finding(findings, "owner-violation", "error", "blocks handoff", name, field, "перенесите поле состояния в Goal.md")
        if name != "Sources.md" and re.search(r"^- .*Source Check Result.*:\s*`", text, flags=re.MULTILINE):
            append_finding(findings, "owner-violation", "error", "blocks handoff", name, "Source Check Result", "перенесите результат проверки в Sources.md")
        if name != "Questions.md" and re.search(r"^- .*Question State.*:\s*`", text, flags=re.MULTILINE):
            append_finding(findings, "owner-violation", "error", "blocks handoff", name, "Question State", "перенесите состояние вопроса в Questions.md")
        if name != "Weaknesses.md" and re.search(r"^- .*Weakness Status.*:\s*`", text, flags=re.MULTILINE):
            append_finding(findings, "owner-violation", "error", "blocks handoff", name, "Weakness Status", "перенесите состояние слабого места в Weaknesses.md")


def question_sections(text: str) -> Iterable[tuple[str, str]]:
    for match in re.finditer(r"^###\s+(Q-\d{8}-\d{2})\s+-.*?(?=^###\s+|\Z)", text, flags=re.MULTILINE | re.DOTALL):
        yield match.group(1), match.group(0)


def source_sections(text: str) -> Iterable[tuple[str, str]]:
    for match in re.finditer(r"^###\s+(SRC-\d{8}-\d{2})\s+-.*?(?=^###\s+|\Z)", text, flags=re.MULTILINE | re.DOTALL):
        yield match.group(1), match.group(0)


def needs_check_references(sources: str) -> dict[str, set[str]]:
    references: dict[str, set[str]] = {}
    for source_id, section in source_sections(sources):
        if re.search(r"Результат \(Result\): `needs-check`", section):
            references[source_id] = {
                entity_id
                for pattern in ID_PATTERNS.values()
                for entity_id in re.findall(pattern.pattern[:-1], section)
            }
    return references


def has_needs_check_evidence(needs_check: dict[str, set[str]], target_ids: set[str]) -> bool:
    return bool(target_ids and any(target_ids & references for references in needs_check.values()))


def validate_gates(files: dict[str, str], findings: list[Finding]) -> None:
    goal = files.get("Goal.md", "")
    sources = files.get("Sources.md", "")
    questions = files.get("Questions.md", "")
    needs_check = needs_check_references(sources)
    production_blocks = set(re.findall(r"\|\s*`(B\d{2})`.*?\|\s*`production-ready`\s*\|", goal))
    if has_needs_check_evidence(needs_check, production_blocks):
        append_finding(findings, "needs-check-gate", "error", "blocks production-ready", "Goal.md", "SRC-* needs-check", "проверьте источник или не используйте claim для production-ready")
    if "Состояние темы (Topic State): `completed`" in goal:
        completion_sources = set(re.findall(ID_PATTERNS["SRC"].pattern[:-1], goal))
        if has_needs_check_evidence(needs_check, completion_sources):
            append_finding(findings, "needs-check-gate", "error", "blocks completed", "Goal.md", "SRC-* needs-check", "проверьте обязательный источник до completed")
        for required in re.findall(r"\|\s*`(B\d{2})`.*?\|\s*`required`\s*\|\s*`([^`]+)`", goal):
            if required[1] != "stable":
                append_finding(findings, "incomplete-required-block", "error", "blocks completed", "Goal.md", required[0], "доведите required Block до stable")
    for question_id, section in question_sections(questions):
        status = re.search(r"Статус \(Status\): `([^`]+)`", section)
        if not status:
            continue
        promoted = status.group(1) == "promoted"
        candidate = status.group(1) == "candidate"
        if not (promoted or candidate):
            continue
        missing: list[str] = []
        duplicate = re.search(r"Проверка дублей \(Duplicate Check\):\s*(.+)", section)
        if not duplicate or "Obsidian" not in duplicate.group(1) or "Anki" not in duplicate.group(1) or "не проверен" in duplicate.group(1):
            missing.append("Duplicate Check в Obsidian и Anki")
        trace = re.search(r"След карточки \(Card Trace\):\s*(.+)", section)
        if not trace or trace.group(1).strip() == "-":
            missing.append("Card Trace")
        decision = re.search(r"Решение о продвижении в Anki \(Promotion Decision\):\s*(.+)", section)
        if not decision or decision.group(1).strip() == "-":
            missing.append("Promotion Decision")
        question_sources = set(re.findall(ID_PATTERNS["SRC"].pattern[:-1], section)) | {question_id}
        if has_needs_check_evidence(needs_check, question_sources):
            missing.append("verified Source Check")
        if missing:
            append_finding(findings, "card-promotion-gate", "error" if promoted else "warning", "blocks card-promotion" if promoted else "does not block", "Questions.md", question_id, "добавьте " + ", ".join(missing))
    knowledge = files.get("Knowledge.md", "")
    knowledge_sources = set(re.findall(ID_PATTERNS["SRC"].pattern[:-1], knowledge))
    if has_needs_check_evidence(needs_check, knowledge_sources) and "Knowledge Consolidation" in knowledge:
        append_finding(findings, "needs-check-gate", "error", "blocks knowledge-consolidation", "Knowledge.md", "SRC-* needs-check", "проверьте источник до консолидации знания")


def validate_index(index: Path, workspace: Path, goal: str, findings: list[Finding]) -> None:
    if not index.is_file():
        append_finding(findings, "missing-index", "error", "blocks handoff", str(index), "Topic Index", "укажите существующий Topic Index")
        return
    text = index.read_text(encoding="utf-8")
    workspace_rel = str(workspace)
    rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in text.splitlines()
        if line.startswith("|") and "Topic Workspace" not in line and "---" not in line
    ]
    if len(rows) != len({row[5] for row in rows if len(row) > 5}):
        append_finding(findings, "duplicate-index-workspace", "error", "blocks handoff", str(index), "Topic Workspace", "оставьте одну строку на Topic Workspace")
    if len(rows) != len({row[3] for row in rows if len(row) > 3}):
        append_finding(findings, "duplicate-index-slug", "error", "blocks handoff", str(index), "Stable Slug", "сделайте Stable Slug уникальным")
    relevant = [row for row in rows if len(row) > 5 and workspace.name in row[5]]
    if not relevant:
        append_finding(findings, "index-workspace-missing", "warning", "does not block", str(index), workspace_rel, "добавьте строку Topic Workspace в Index")
        return
    header_slug = re.search(r"Stable Slug\): `([^`]+)`", goal)
    goal_state = re.search(r"Topic State\): `([^`]+)`", goal)
    row = relevant[0]
    goal_link = re.search(r"\]\(([^)]+)\)", row[6]) if len(row) > 6 else None
    if not goal_link or not (index.parent / goal_link.group(1)).is_file():
        append_finding(findings, "missing-index-goal", "error", "blocks handoff", str(index), "Goal", "исправьте ссылку Goal на существующий Goal.md")
    if header_slug and f"`{header_slug.group(1)}`" not in row[3]:
        append_finding(findings, "stale-index", "warning", "does not block", str(index), "Stable Slug", "синхронизируйте Stable Slug из Goal.md")
    if goal_state and f"`{goal_state.group(1)}`" not in row[4]:
        append_finding(findings, "stale-index", "warning", "does not block", str(index), "Topic State", "синхронизируйте кэш состояния из Goal.md")
    workspace_value = row[5].strip("`")
    path_parts = workspace_value.split("/")
    if len(path_parts) != 3 or path_parts[0] != "topics" or path_parts[1] != row[1].lower() or not path_parts[2]:
        append_finding(findings, "invalid-index-workspace", "error", "blocks handoff", str(index), workspace_value, "используйте путь topics/<subject>/<stable-slug>")
    goal_workspace = re.search(r"Topic Workspace\): `([^`]+)`", goal)
    if goal_workspace and goal_workspace.group(1).rstrip("/") != workspace_value.rstrip("/"):
        append_finding(findings, "stale-index", "warning", "does not block", str(index), "Topic Workspace", "синхронизируйте Topic Workspace из Goal.md")


def run_checker(index: Path, workspace: Path) -> list[Finding]:
    """Возвращает findings, не записывая ни одного файла."""
    findings: list[Finding] = []
    if not workspace.is_dir():
        return [Finding("missing-workspace", "error", "blocks handoff", str(workspace), "Topic Workspace", "укажите существующий каталог")]
    files = read_files(workspace)
    for artifact in REQUIRED_ARTIFACTS:
        if artifact not in files:
            append_finding(findings, "missing-artifact", "error", "blocks handoff", artifact, artifact, "создайте обязательный артефакт")
    if "Goal.md" not in files:
        return findings
    for field in ("Topic", "Stable Slug", "Topic Workspace", "Topic State", "Active Block"):
        if field not in files["Goal.md"]:
            append_finding(findings, "missing-goal-header", "error", "blocks handoff", "Goal.md", field, "добавьте обязательное поле Header")
    validate_markdown_links(workspace, files, findings)
    validate_ids(files, findings)
    validate_entity_references(files, findings)
    validate_owner_invariants(files, findings)
    validate_gates(files, findings)
    validate_index(index, workspace, files["Goal.md"], findings)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only проверка Topic Index и Topic Workspace.")
    parser.add_argument("--index", type=Path, required=True, help="путь к topics/INDEX.md")
    parser.add_argument("--workspace", type=Path, required=True, help="путь к одной Topic Workspace")
    args = parser.parse_args()
    findings = run_checker(args.index, args.workspace)
    if not findings:
        print("Проверка пройдена: findings отсутствуют.")
        return 0
    for finding in findings:
        print(finding.render())
    errors = sum(finding.severity == "error" for finding in findings)
    print(f"Итог: {len(findings)} findings, ошибок: {errors}.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
