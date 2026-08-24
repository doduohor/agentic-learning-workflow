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

ACCEPTED_VALUES = {
    "topic-state": {"intake", "diagnosing", "planned", "learning", "practicing", "reviewing", "completed", "paused"},
    "mastery": {"recognition", "recall", "application", "transfer", "production-ready", "stable"},
    "block-status": {"not-started", "active", "blocked", "ready-for-review", "stable", "deferred"},
    "practice-result": {"unchecked", "passed", "partial", "failed", "rework-needed"},
    "question-type": {"recall", "practice", "interview", "debugging", "design-choice", "card-candidate"},
    "question-state": {"draft", "active", "answered", "failed", "promoted", "archived", "rejected"},
    "card-status": {"none", "candidate", "rejected", "promoted"},
    "weakness-type": {"gap", "misconception", "fragile-skill", "application-blind-spot"},
    "weakness-severity": {"minor", "major", "blocker"},
    "weakness-status": {"open", "repairing", "retest-needed", "resolved", "archived"},
    "repetition-target": {"Question", "Block", "Weakness"},
    "repetition-action": {"recall", "explain", "apply", "debug", "transfer"},
    "repetition-result": {"scheduled", "passed", "partial", "failed", "missed"},
    "sensitivity": {"version-sensitive", "application-sensitive", "production", "security", "tooling-behavior", "protocol-semantics", "durable-concept"},
    "authority": {"official-docs", "spec-rfc", "release-notes", "vendor-blog", "engineering-article", "community-discussion", "course-book"},
    "source-result": {"verified", "rejected", "needs-check", "superseded"},
}


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


def record_sections(text: str, kind: str) -> Iterable[tuple[str, str]]:
    pattern = ID_PATTERNS[kind].pattern[:-1]
    for match in re.finditer(rf"^###\s+({pattern})\s+-.*?(?=^###\s+|\Z)", text, flags=re.MULTILINE | re.DOTALL):
        yield match.group(1), match.group(0)


def field_value(section: str, *labels: str) -> str | None:
    alternatives = "|".join(re.escape(label) for label in labels)
    match = re.search(rf"(?:{alternatives})[^\n`]*`([^`]+)`", section, flags=re.IGNORECASE)
    return match.group(1).strip() if match else None


def validate_value(findings: list[Finding], file: str, entity: str, value: str | None, kind: str, field: str) -> None:
    if value is None:
        append_finding(findings, "missing-required-field", "error", "blocks handoff", file, entity, f"добавьте поле {field}")
    elif value not in ACCEPTED_VALUES[kind]:
        append_finding(findings, "invalid-value", "error", "blocks handoff", file, entity, f"укажите допустимое значение {field}: " + ", ".join(sorted(ACCEPTED_VALUES[kind])))


def validate_accepted_values(files: dict[str, str], findings: list[Finding]) -> None:
    goal = files.get("Goal.md", "")
    validate_value(findings, "Goal.md", "Topic State", field_value(goal, "Topic State", "Состояние темы"), "topic-state", "Topic State")
    for match in re.finditer(r"\|\s*`(B\d{2})`[^\n]*?\|\s*`(?:required|optional)`\s*\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|", goal):
        validate_value(findings, "Goal.md", match.group(1), match.group(2), "mastery", "Mastery Level")
        validate_value(findings, "Goal.md", match.group(1), match.group(3), "block-status", "Block Status")
    specifications = {
        "Practice.md": ("PA", (("practice-result", ("Result", "Результат")),)),
        "Questions.md": ("Q", (("question-type", ("Question Type", "Тип вопроса")), ("question-state", ("Question State", "Состояние вопроса")), ("card-status", ("Card Candidate status", "Статус (Status)")))),
        "Weaknesses.md": ("W", (("weakness-type", ("Type", "Тип")), ("weakness-severity", ("Severity", "Серьезность")), ("weakness-status", ("Weakness Status", "Статус (Status)")))),
        "RepetitionLog.md": ("REP", (("repetition-target", ("Target Type", "Тип цели")), ("repetition-action", ("Action", "Действие")), ("repetition-result", ("Repetition Result", "Результат")))),
        "Sources.md": ("SRC", (("sensitivity", ("Sensitivity", "Чувствительность")), ("authority", ("Authority Type", "Тип авторитетности")), ("source-result", ("Source Check Result", "Результат (Result)")))),
    }
    for name, (kind, rules) in specifications.items():
        for entity, section in record_sections(files.get(name, ""), kind):
            for value_kind, labels in rules:
                validate_value(findings, name, entity, field_value(section, *labels), value_kind, labels[0])


def validate_weaknesses(files: dict[str, str], findings: list[Finding]) -> None:
    goal = files.get("Goal.md", "")
    text = files.get("Weaknesses.md", "")
    for weakness_id, section in record_sections(text, "W"):
        severity = field_value(section, "Severity", "Серьезность")
        status = field_value(section, "Weakness Status", "Статус (Status)")
        has_evidence = bool(re.search(r"####\s+(?:Evidence|Доказательство).*?(?:PA-|Q-|REP-|interview)", section, re.DOTALL | re.IGNORECASE))
        if not has_evidence:
            append_finding(findings, "missing-weakness-evidence", "error", "blocks handoff", "Weaknesses.md", weakness_id, "добавьте ссылку на Practice Attempt, Question, Repetition или interview answer")
        if severity in {"major", "blocker"} and status in {"open", "repairing", "retest-needed"} and not re.search(r"Repair Action[^\n]*:\s*(?!-\s*$).+|Действие.*:\s*(?!-\s*$).+", section):
            append_finding(findings, "missing-repair-action", "error", "blocks handoff", "Weaknesses.md", weakness_id, "добавьте Repair Action для открытого major/blocker Weakness")
        if status == "resolved" and not re.search(r"Resolution Evidence[^\n]*:\s*(?!-\s*$).+|Доказательство исправления.*:\s*(?!-\s*$).+", section):
            append_finding(findings, "missing-resolution-evidence", "error", "blocks handoff", "Weaknesses.md", weakness_id, "добавьте Resolution Evidence")
        if severity == "blocker" and status in {"open", "repairing", "retest-needed"} and weakness_id not in goal:
            append_finding(findings, "missing-active-weakness", "error", "blocks completed", "Goal.md", weakness_id, "добавьте открытое blocker Weakness в Active Weakness Summary")


def validate_repetitions(files: dict[str, str], findings: list[Finding]) -> None:
    records = record_ids_by_kind(files)
    for repetition_id, section in record_sections(files.get("RepetitionLog.md", ""), "REP"):
        target_type = field_value(section, "Target Type", "Тип цели")
        result = field_value(section, "Repetition Result", "Результат")
        target_ids = {kind: set(re.findall(pattern.pattern[:-1], section)) for kind, pattern in ID_PATTERNS.items()}
        expected = {"Question": "Q", "Block": "B", "Weakness": "W"}.get(target_type or "")
        if expected and not target_ids[expected]:
            append_finding(findings, "invalid-repetition-target", "error", "blocks handoff", "RepetitionLog.md", repetition_id, f"свяжите Target Type {target_type} с существующим {expected}-ID")
        if expected and any(target_ids[kind] for kind in {"Q", "B", "W"} - {expected}):
            append_finding(findings, "invalid-repetition-target", "error", "blocks handoff", "RepetitionLog.md", repetition_id, "Target должен соответствовать Target Type")
        completed = field_value(section, "Completed At", "Выполнено в")
        if result == "scheduled" and completed not in {None, "-"}:
            append_finding(findings, "invalid-repetition-completion", "error", "blocks handoff", "RepetitionLog.md", repetition_id, "scheduled repetition не имеет Completed At")
        if result in {"passed", "partial", "failed", "missed"} and completed in {None, "-"}:
            append_finding(findings, "missing-repetition-completion", "warning", "does not block", "RepetitionLog.md", repetition_id, "добавьте Completed At или объяснение")
        if result in {"partial", "failed"} and not re.search(r"Failure Analysis|Анализ провала", section):
            append_finding(findings, "missing-failure-analysis", "warning", "does not block", "RepetitionLog.md", repetition_id, "добавьте Failure Analysis")
        if result == "failed" and not target_ids["W"]:
            append_finding(findings, "unlinked-repetition-failure", "warning", "blocks completed", "RepetitionLog.md", repetition_id, "свяжите учебную проблему с W-* или явно объясните отсутствие Weakness")


def validate_sources(files: dict[str, str], findings: list[Finding]) -> None:
    sources = files.get("Sources.md", "")
    for source_id, section in source_sections(sources):
        result = field_value(section, "Source Check Result", "Результат (Result)")
        if result != "superseded":
            continue
        next_check = field_value(section, "Next Check", "Следующая проверка")
        notes = re.search(
            r"^####\s+(?:Notes|Заметки).*?\n\n(.*?)(?=^#{1,4}\s+|\Z)",
            section,
            flags=re.MULTILINE | re.DOTALL,
        )
        notes_text = notes.group(1).strip() if notes is not None else ""
        replacement_ids = set(re.findall(ID_PATTERNS["SRC"].pattern[:-1], notes_text)) - {source_id}
        has_replacement = bool(replacement_ids)
        if next_check in {None, "-"} and not has_replacement:
            append_finding(findings, "missing-superseded-followup", "warning", "does not block", "Sources.md", source_id, "укажите заменяющий источник или Next Check")


def validate_sessions(workspace: Path, files: dict[str, str], findings: list[Finding]) -> None:
    sessions = workspace / "sessions"
    records = record_ids_by_kind(files)
    for archive in sessions.rglob("*.md") if sessions.is_dir() else ():
        archive_path = str(archive.relative_to(workspace))
        if archive.parent != sessions or not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md", archive.name):
            append_finding(findings, "invalid-session-path", "error", "blocks handoff", str(archive.relative_to(workspace)), archive.name, "используйте sessions/YYYY-MM-DD-<short-slug>.md")
        text = archive.read_text(encoding="utf-8")
        if "../Goal.md" not in text:
            append_finding(findings, "missing-archive-topic-link", "error", "blocks handoff", str(archive.relative_to(workspace)), "../Goal.md", "добавьте ссылку на Topic через ../Goal.md")
        if not any(re.search(pattern.pattern[:-1], text) for pattern in ID_PATTERNS.values()):
            append_finding(findings, "missing-archive-entity-link", "error", "blocks handoff", str(archive.relative_to(workspace)), "Entity Reference", "добавьте ссылку на PA/Q/W/REP/SRC/B сущность")
        for kind, pattern in ID_PATTERNS.items():
            for entity in set(re.findall(pattern.pattern[:-1], text)):
                if entity not in records[kind]:
                    append_finding(findings, "missing-archive-entity", "error", "blocks handoff", str(archive.relative_to(workspace)), entity, "свяжите archive с существующей основной сущностью")
        for _, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text):
            target_path = target.partition("#")[0]
            if target_path.startswith("artifacts/") and not (archive.parent / target_path).is_file():
                append_finding(findings, "missing-companion-artifact", "error", "blocks handoff", archive_path, target_path, "добавьте companion artifact или исправьте ссылку")
    for name, text in files.items():
        for _, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text):
            target_path = target.partition("#")[0]
            if target_path.startswith("sessions/") and not (workspace / target_path).is_file():
                append_finding(findings, "missing-session-archive", "error", "blocks handoff", name, target_path, "исправьте ссылку на существующий archive")
            if target_path and (target_path.startswith("artifacts/") or target_path.startswith("sessions/")) and not (workspace / target_path).is_file():
                append_finding(findings, "missing-companion-artifact", "error", "blocks handoff", name, target_path, "добавьте companion artifact или исправьте ссылку")


def question_sections(text: str) -> Iterable[tuple[str, str]]:
    for match in re.finditer(r"^###\s+(Q-\d{8}-\d{2})\s+-.*?(?=^###\s+|\Z)", text, flags=re.MULTILINE | re.DOTALL):
        yield match.group(1), match.group(0)


def source_sections(text: str) -> Iterable[tuple[str, str]]:
    for match in re.finditer(r"^###\s+(SRC-\d{8}-\d{2})\s+-.*?(?=^###\s+|\Z)", text, flags=re.MULTILINE | re.DOTALL):
        yield match.group(1), match.group(0)


def unverified_source_references(sources: str) -> dict[str, set[str]]:
    references: dict[str, set[str]] = {}
    for source_id, section in source_sections(sources):
        if field_value(section, "Source Check Result", "Результат (Result)") != "verified":
            references[source_id] = {
                entity_id
                for pattern in ID_PATTERNS.values()
                for entity_id in re.findall(pattern.pattern[:-1], section)
            }
    return references


def has_unverified_source_evidence(unverified: dict[str, set[str]], target_ids: set[str]) -> bool:
    return bool(target_ids and any(target_ids & references for references in unverified.values()))


def has_unlinked_needs_check_marker(text: str) -> bool:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if "Нужно проверить" not in line:
            continue
        context = [line]
        for following in lines[index + 1:]:
            if not following.strip() or following.startswith("#"):
                break
            context.append(following)
        if not re.search(ID_PATTERNS["SRC"].pattern[:-1], "\n".join(context)):
            return True
    return False


def validate_gates(files: dict[str, str], findings: list[Finding]) -> None:
    goal = files.get("Goal.md", "")
    sources = files.get("Sources.md", "")
    questions = files.get("Questions.md", "")
    unverified = unverified_source_references(sources)
    production_blocks = set(re.findall(r"\|\s*`(B\d{2})`.*?\|\s*`production-ready`\s*\|", goal))
    if has_unverified_source_evidence(unverified, production_blocks):
        append_finding(findings, "unverified-source-gate", "error", "blocks production-ready", "Goal.md", "SRC-*", "используйте verified Source Record для production-ready")
    if production_blocks and has_unlinked_needs_check_marker(goal):
        append_finding(findings, "unlinked-needs-check", "error", "blocks production-ready", "Goal.md", "Нужно проверить", "свяжите sensitive claim с SRC-* или исключите его из gate evidence")
    for block_id in production_blocks:
        row = next((line for line in goal.splitlines() if f"`{block_id}`" in line and line.startswith("|")), "")
        if "PA-" not in row or any(result in row for result in ("`unchecked`", "`failed`", "`rework-needed`")):
            append_finding(findings, "insufficient-production-evidence", "error", "blocks production-ready", "Goal.md", block_id, "добавьте applied/transfer Practice Attempt с приемлемым результатом")
        if any(block_id in section and field_value(section, "Severity", "Серьезность") == "blocker" and field_value(section, "Weakness Status", "Статус (Status)") in {"open", "repairing", "retest-needed"} for _, section in record_sections(files.get("Weaknesses.md", ""), "W")):
            append_finding(findings, "open-blocker-weakness", "error", "blocks production-ready", "Weaknesses.md", block_id, "закройте blocker Weakness перед production-ready")
    if "Состояние темы (Topic State): `completed`" in goal:
        completion_sources = set(re.findall(ID_PATTERNS["SRC"].pattern[:-1], goal))
        if has_unverified_source_evidence(unverified, completion_sources):
            append_finding(findings, "unverified-source-gate", "error", "blocks completed", "Goal.md", "SRC-*", "используйте verified Source Record для completed")
        if has_unlinked_needs_check_marker(goal):
            append_finding(findings, "unlinked-needs-check", "error", "blocks completed", "Goal.md", "Нужно проверить", "свяжите sensitive claim с SRC-* или исключите его из Completion Evidence")
        if any(field_value(section, "Severity", "Серьезность") == "blocker" and field_value(section, "Weakness Status", "Статус (Status)") in {"open", "repairing", "retest-needed"} for _, section in record_sections(files.get("Weaknesses.md", ""), "W")):
            append_finding(findings, "open-blocker-weakness", "error", "blocks completed", "Weaknesses.md", "W-*", "закройте blocker Weakness перед completed")
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
        if has_unverified_source_evidence(unverified, question_sources):
            missing.append("verified Source Check")
        if has_unlinked_needs_check_marker(section):
            missing.append("SRC-* для Нужно проверить")
        if missing:
            append_finding(findings, "card-promotion-gate", "error" if promoted else "warning", "blocks card-promotion" if promoted else "does not block", "Questions.md", question_id, "добавьте " + ", ".join(missing))
    knowledge = files.get("Knowledge.md", "")
    knowledge_sources = set(re.findall(ID_PATTERNS["SRC"].pattern[:-1], knowledge))
    if has_unverified_source_evidence(unverified, knowledge_sources) and "Knowledge Consolidation" in knowledge:
        append_finding(findings, "unverified-source-gate", "error", "blocks knowledge-consolidation", "Knowledge.md", "SRC-*", "используйте verified Source Record для консолидации знания")
    if "Knowledge Consolidation" in knowledge and has_unlinked_needs_check_marker(knowledge):
        append_finding(findings, "unlinked-needs-check", "error", "blocks knowledge-consolidation", "Knowledge.md", "Нужно проверить", "свяжите sensitive claim с SRC-* или исключите его из консолидации")
    if "Knowledge Consolidation" in knowledge:
        if not re.search(r"(?:PA-|Q-|W-|SRC-)", knowledge):
            append_finding(findings, "missing-consolidation-trace", "error", "blocks knowledge-consolidation", "Knowledge.md", "Knowledge Consolidation", "добавьте trace к Topic Workspace evidence")
        if re.search(r"(?:raw session|Session Notes|copied source dump|archive copy)", knowledge, re.IGNORECASE):
            append_finding(findings, "raw-knowledge-consolidation", "error", "blocks knowledge-consolidation", "Knowledge.md", "Knowledge Consolidation", "перенесите только curated Knowledge, без raw/archive/source dump")


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
    topic_names = {row[2].strip() for row in rows if len(row) > 2}
    if len(rows) != len({row[5] for row in rows if len(row) > 5}):
        append_finding(findings, "duplicate-index-workspace", "error", "blocks handoff", str(index), "Topic Workspace", "оставьте одну строку на Topic Workspace")
    if len(rows) != len({row[3] for row in rows if len(row) > 3}):
        append_finding(findings, "duplicate-index-slug", "error", "blocks handoff", str(index), "Stable Slug", "сделайте Stable Slug уникальным")
    for row in rows:
        if len(row) < 9:
            append_finding(findings, "invalid-index-row", "error", "blocks handoff", str(index), "Topics", "добавьте все обязательные столбцы Topic Index")
            continue
        topic, subject, slug, workspace_value, goal_cell, parent, related = row[2], row[1], row[3].strip("`"), row[5].strip("`"), row[6], row[7].strip(), row[8].strip()
        # ADR 08 explicitly preserves the prototype's short folder slug while
        # Goal.md remains the source of truth for the full Stable Slug.
        expected = f"topics/{subject.lower()}/{workspace_value.split('/')[-1]}"
        if not re.fullmatch(r"topics/[^/]+/[^/]+", workspace_value) or workspace_value != expected:
            append_finding(findings, "invalid-index-workspace", "error", "blocks handoff", str(index), workspace_value, "используйте путь topics/<subject>/<stable-slug>")
        workspace_dir = index.parent.parent / workspace_value
        if not workspace_dir.is_dir():
            append_finding(findings, "missing-index-workspace", "error", "blocks handoff", str(index), workspace_value, "создайте Topic Workspace или исправьте строку Index")
        link = re.search(r"\]\(([^)]+)\)", goal_cell)
        if not link or not (index.parent / link.group(1)).is_file():
            append_finding(findings, "missing-index-goal", "error", "blocks handoff", str(index), topic, "исправьте ссылку Goal на существующий Goal.md")
        if parent != "-" and parent not in topic_names:
            append_finding(findings, "missing-parent-topic", "error", "blocks handoff", str(index), parent, "укажите существующую Topic в Parent Topic или -")
        if related != "-" and workspace_value and sum(1 for candidate in rows if len(candidate) > 5 and candidate[5].strip("`") == workspace_value) > 1:
            append_finding(findings, "related-subject-duplicate-workspace", "error", "blocks handoff", str(index), workspace_value, "оставьте один physical Topic Workspace и перечислите Related Subjects в той же строке")
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
    validate_accepted_values(files, findings)
    validate_weaknesses(files, findings)
    validate_repetitions(files, findings)
    validate_sources(files, findings)
    validate_sessions(workspace, files, findings)
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
