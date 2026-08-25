#!/usr/bin/env python3
"""Подтверждаемая запись в Anki и Obsidian под контролем Orchestrator.

Модуль не знает, как подключаться к личным Anki или Obsidian. Реальный writer
передаётся только Learning Orchestrator после показа preview и явного approval;
по умолчанию targets недоступны. Это исключает неявную внешнюю запись.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from secrets import token_urlsafe
import re


ANKI_ACTIONS = frozenset({"add", "replace", "merge", "skip"})
OBSIDIAN_ACTIONS = frozenset({"add", "append", "merge", "replace-section", "skip"})
OWNER_ARTIFACTS = {"anki": "Questions.md", "obsidian": "Knowledge.md"}


@dataclass(frozen=True)
class GateSnapshot:
    """Результат уже выполненных gates; решения не принимаются этим модулем."""

    checker_passed: bool
    source_check_passed: bool
    duplicate_check_passed: bool
    decision_kind: str
    decision_action: str
    content_ready: bool
    trace_present: bool


@dataclass(frozen=True)
class GateVerification:
    """Свежие gate states и evidence, которые должны совпадать с preview."""

    snapshot: GateSnapshot
    duplicate_check_summary: str
    source_check_summary: str
    trace: str

@dataclass(frozen=True)
class WriteRequest:
    """Вход Orchestrator после Card Promotion или Knowledge Consolidation."""

    topic_workspace: str
    target: str
    target_type: str
    action: str
    source_entity: str
    target_description: str
    proposed_content: str
    duplicate_check_summary: str
    source_check_summary: str
    trace: str
    expected_markdown_updates: str
    recovery_plan: str
    gates: GateSnapshot
    anki_deck: str | None = None
    anki_note_type: str | None = None
    anki_fields: str | None = None
    anki_tags: str | None = None
    obsidian_target_path: str | None = None
    obsidian_note: str | None = None
    obsidian_section: str | None = None
    linked_evidence: str | None = None
    existing_target_identity: str | None = None
    external_target_found_without_trace: bool = False
    previous_proposed_content: str | None = None
    previous_duplicate_check_summary: str | None = None
    previous_source_check_summary: str | None = None
    change_reason: str | None = None


@dataclass(frozen=True)
class WritePreview:
    """Read-only dry-run: его нельзя использовать как approval сам по себе."""

    request: WriteRequest
    owner_artifact: str
    target_available: bool
    state: str
    blockers: tuple[str, ...]
    target_revision: str | None
    token: str

    def to_markdown(self) -> str:
        request = self.request
        blockers = "; ".join(self.blockers) if self.blockers else "нет"
        return "\n".join(
            [
                "## Dry-run preview",
                "",
                f"- Topic Workspace: `{request.topic_workspace}`",
                f"- Source entity: `{request.source_entity}`",
                f"- Target: `{request.target}`",
                f"- Target type: `{request.target_type}`",
                f"- Action: `{request.action}`",
                f"- Target details: {request.target_description}",
                *self._target_details(request),
                f"- Target availability: `{'available' if self.target_available else 'unavailable'}`",
                f"- Preview state: `{self.state}`",
                "- Proposed content:",
                "```text",
                request.proposed_content,
                "```",
                f"- Duplicate Check: {request.duplicate_check_summary}",
                f"- Source Check: {request.source_check_summary}",
                f"- Trace: {request.trace}",
                f"- Expected Markdown updates: {request.expected_markdown_updates}",
                f"- Owner artifact: `{self.owner_artifact}`",
                f"- Блокеры: {blockers}",
                f"- План восстановления: {request.recovery_plan}",
                "- Требуется явное user approval после этого preview: да.",
            ]
        )

    @staticmethod
    def _target_details(request: WriteRequest) -> list[str]:
        if request.target == "anki":
            return [
                f"- Anki deck: `{request.anki_deck}`", f"- Anki note type: `{request.anki_note_type}`",
                f"- Anki fields: `{request.anki_fields}`", f"- Anki tags: `{request.anki_tags}`",
            ]
        return [
            f"- Obsidian path: `{request.obsidian_target_path}`", f"- Obsidian note: `{request.obsidian_note}`",
            f"- Obsidian section: `{request.obsidian_section}`",
        ]


@dataclass(frozen=True)
class WriteOutcome:
    state: str
    action: str
    target: str
    target_type: str
    owner_artifact: str
    topic_workspace: str
    source_entity: str
    external_target_identity: str | None
    next_action: str
    target_description: str
    duplicate_check_summary: str
    source_check_summary: str
    trace: str
    change_reason: str | None
    anki_deck: str | None
    anki_note_type: str | None
    anki_fields: str | None
    anki_tags: str | None
    anki_note_id: str | None
    anki_card_ids: tuple[str, ...]
    obsidian_target_path: str | None
    obsidian_note: str | None
    obsidian_section: str | None
    linked_evidence: str | None
    expected_markdown_updates: str
    recovery_plan: str
    target_available: bool | None

    def to_markdown(self) -> str:
        target = self.external_target_identity or "-"
        return "\n".join(
            [
                f"- Write state: `{self.state}`",
                f"- Topic Workspace: `{self.topic_workspace}`",
                f"- Write action: `{self.action}`",
                f"- Target: `{self.target}` ({self.target_type})",
                f"- Source entity: `{self.source_entity}`",
                f"- External target: `{target}`",
                f"- Target details: {self.target_description}",
                f"- Duplicate Check: {self.duplicate_check_summary}",
                f"- Source Check: {self.source_check_summary}",
                f"- Trace/evidence: {self.trace}",
                f"- Linked evidence: {self.linked_evidence or '-'}",
                f"- Expected Markdown updates: {self.expected_markdown_updates}",
                f"- Target availability: `{self._availability()}`",
                f"- Recovery plan: {self.recovery_plan}",
                f"- Change reason: {self.change_reason or '-'}",
                *self._target_details(),
                f"- Next action: {self.next_action}",
            ]
        )

    def _target_details(self) -> list[str]:
        if self.target == "anki":
            return [
                f"- Anki deck: `{self.anki_deck}`", f"- Anki note type: `{self.anki_note_type}`",
                f"- Anki fields: `{self.anki_fields}`", f"- Anki tags: `{self.anki_tags}`",
                f"- Anki Note ID: `{self.anki_note_id or '-'}`",
                f"- Anki Card IDs: `{', '.join(self.anki_card_ids) or '-'}`",
            ]
        return [
            f"- Obsidian path: `{self.obsidian_target_path}`", f"- Obsidian note: `{self.obsidian_note}`",
            f"- Obsidian section: `{self.obsidian_section}`",
        ]

    def _availability(self) -> str:
        if self.target_available is None:
            return "unknown"
        return "available" if self.target_available else "unavailable"


@dataclass(frozen=True)
class ExternalWriteResult:
    """Identity returned by an explicit adapter; card IDs are optional."""

    target_identity: str
    anki_note_id: str | None = None
    anki_card_ids: tuple[str, ...] = ()


class ExternalWriteTarget(Protocol):
    """Узкая seam внешнего target; production adapter задаётся явно."""

    def is_available(self) -> bool: ...

    def exists(self, target_identity: str) -> bool: ...

    def preview_revision(self, request: WriteRequest) -> str | None: ...

    def write(self, request: WriteRequest) -> str | ExternalWriteResult: ...


class TraceWriter(Protocol):
    """Записывает outcome только в owner artifact, назначенный по target."""

    def record(self, outcome: WriteOutcome) -> None: ...


class GateVerifier(Protocol):
    """Перечитывает актуальный Checker/Source/Duplicate gate перед write."""

    def verify(self, request: WriteRequest) -> GateVerification: ...


class UnavailableTarget:
    """Безопасный production default: реальная запись невозможна."""

    def is_available(self) -> bool:
        return False

    def exists(self, target_identity: str) -> bool:
        return False

    def preview_revision(self, request: WriteRequest) -> str | None:
        return None

    def write(self, request: WriteRequest) -> str:
        raise RuntimeError("Внешний target не настроен для записи")


class InMemoryTraceWriter:
    """Изолированная test double; не предназначена для production trace."""

    def __init__(self) -> None:
        self.outcomes: list[WriteOutcome] = []
        self.owner_artifacts: list[str] = []

    def record(self, outcome: WriteOutcome) -> None:
        self.outcomes.append(outcome)
        self.owner_artifacts.append(outcome.owner_artifact)


class MarkdownTraceWriter:
    """Обновляет outcome внутри соответствующей записи owner artifact."""

    def __init__(self, workspace: Path, *, now: datetime | None = None) -> None:
        self.workspace = workspace
        self.now = now

    def record(self, outcome: WriteOutcome) -> None:
        if outcome.owner_artifact not in {"Questions.md", "Knowledge.md"}:
            raise ValueError("Write outcome разрешено хранить только в Questions.md или Knowledge.md")
        owner = self.workspace / outcome.owner_artifact
        if not owner.is_file():
            raise FileNotFoundError(f"Owner artifact не найден: {owner}")
        timestamp = (self.now or datetime.now(UTC)).date().isoformat()
        content = owner.read_text(encoding="utf-8")
        heading_level = "####" if outcome.owner_artifact == "Questions.md" else "###"
        heading = f"{heading_level} Write outcome — {outcome.source_entity}"
        record = "\n".join([heading, "", outcome.to_markdown(), f"- Written At: `{timestamp}`"])
        section = self._owner_section(content, outcome)
        updated_section = self._replace_outcome(section, heading, record)
        owner.write_text(content.replace(section, updated_section, 1), encoding="utf-8")

    @staticmethod
    def _owner_section(content: str, outcome: WriteOutcome) -> str:
        if outcome.owner_artifact == "Questions.md":
            question_id = outcome.source_entity.split("#", 1)[0]
            match = re.search(rf"^### {re.escape(question_id)}\b[\s\S]*?(?=^### |\Z)", content, flags=re.MULTILINE)
            if not match:
                raise ValueError(f"Question record не найден: {question_id}")
            return match.group(0)
        match = re.search(r"^## Knowledge Consolidation Trace[\s\S]*?(?=^## |\Z)", content, flags=re.MULTILINE)
        if not match:
            raise ValueError("Knowledge Consolidation Trace не найден")
        return match.group(0)

    @staticmethod
    def _replace_outcome(section: str, heading: str, record: str) -> str:
        existing = re.search(
            rf"^{re.escape(heading)}[\s\S]*?(?=^### |^#### |\Z)", section, flags=re.MULTILINE
        )
        if existing:
            return section[:existing.start()] + record + section[existing.end():]
        return section.rstrip() + "\n\n" + record + "\n"


class WriteAutomation:
    """Готовит preview и выполняет ровно один подтверждённый внешний write."""

    def __init__(
        self,
        targets: dict[str, ExternalWriteTarget] | None = None,
        *,
        trace_writer: TraceWriter | None = None,
        gate_verifier: GateVerifier | None = None,
    ) -> None:
        self.targets = targets or {"anki": UnavailableTarget(), "obsidian": UnavailableTarget()}
        self.trace_writer = trace_writer
        self.gate_verifier = gate_verifier
        self._prepared_previews: dict[str, WritePreview] = {}

    def prepare(self, request: WriteRequest) -> WritePreview:
        """Формирует preview; никогда не вызывает ``write`` и не меняет trace."""
        self._validate(request)
        target = self.targets.get(request.target, UnavailableTarget())
        available = self._available(target)
        blockers = self._gate_blockers(request)
        target_revision = self._revision(target, request) if available else None

        if not available and request.action != "skip":
            blockers.append("Target unavailable: внешняя запись остаётся pending.")
        if request.existing_target_identity:
            if not available:
                blockers.append("Нельзя проверить предыдущий external target до восстановления доступности.")
            elif self._exists(target, request.existing_target_identity):
                if blockers:
                    return self._new_preview(request, True, "pending", tuple(blockers), target_revision)
                if self._preview_changed(request):
                    return self._new_preview(
                        request,
                        True,
                        "reconciliation-preview",
                        ("Proposed content или Check summary изменились; нужен новый preview и approval.",),
                        target_revision,
                    )
                return self._new_preview(request, True, "no-op", tuple(), target_revision)
            else:
                return self._new_preview(
                    request,
                    True,
                    "reconciliation-preview",
                    ("Trace есть, но внешний target не найден; нужен reconciliation preview.",),
                    target_revision,
                )
        if request.external_target_found_without_trace:
            return self._new_preview(
                request,
                available,
                "reconciliation-preview",
                ("External target найден без Topic Workspace trace; нужен reconciliation preview.",),
                target_revision,
            )
        state = "ready-for-approval" if not blockers else "pending"
        return self._new_preview(request, available, state, tuple(blockers), target_revision)

    def execute(self, preview: WritePreview, *, approved: bool) -> WriteOutcome:
        """Пишет во внешний target лишь после preview, gates и явного approval."""
        prepared = self._prepared_previews.pop(preview.token, None)
        if prepared != preview:
            raise ValueError("Preview не был подготовлен этим WriteAutomation или уже использован.")
        request = preview.request
        self._validate(request)
        if preview.state == "no-op":
            return self._outcome(request, "no-op", request.existing_target_identity, "Повторный запуск не требует записи.")
        if self.trace_writer is None:
            return self._outcome(request, "pending", None, "Настройте TraceWriter owner artifact до внешней записи.")
        if not approved:
            return self._record_pending(request, "Пользователь не подтвердил preview; покажите его повторно для следующего запуска.")
        if preview.state != "ready-for-approval":
            return self._record_pending(request, "Устраните blockers или выполните reconciliation preview до записи.")
        if self.gate_verifier is None:
            return self._record_pending(request, "Перед внешней записью настройте свежую проверку Checker, Source Check и Duplicate Check.")
        try:
            verification = self.gate_verifier.verify(request)
        except Exception as error:
            return self._record_pending(request, f"Свежая проверка gates недоступна: {error}.")
        if self._gate_blockers(request, verification.snapshot):
            return self._record_pending(request, "Gates изменились или не пройдены; подготовьте новый preview.")
        if self._evidence_changed(request, verification):
            return self._record_pending(request, "Duplicate/Source Check summary или trace изменились; подготовьте новый preview и approval.")
        if request.action == "skip":
            outcome = self._outcome(request, "no-op", None, "Решение skip зафиксировано без внешней записи.")
            self._record(outcome)
            return outcome

        target = self.targets.get(request.target, UnavailableTarget())
        if not self._available(target):
            return self._record_pending(request, "Target недоступен; повторите availability check и preview.")
        if self._revision(target, request) != preview.target_revision:
            return self._record_pending(request, "Target изменился после dry-run; подготовьте новый preview и approval.")
        try:
            result = target.write(request)
        except Exception as error:
            outcome = self._outcome(request, "failed", None, f"Внешняя запись не выполнена: {error}. Повторите preview после проверки target.", target_available=True)
            self._record(outcome)
            return outcome
        target_identity, anki_note_id, anki_card_ids = self._result_details(request, result)
        outcome = self._outcome(
            request, "succeeded", target_identity, "Внешняя запись и trace завершены.", anki_note_id, anki_card_ids, True
        )
        try:
            self._record(outcome)
        except Exception:
            return self._outcome(
                request,
                "partial",
                target_identity,
                "Внешняя запись выполнена, но trace не обновлён; подготовьте reconciliation preview.",
                anki_note_id,
                anki_card_ids,
                True,
            )
        return outcome

    @staticmethod
    def _available(target: ExternalWriteTarget) -> bool:
        try:
            return target.is_available()
        except Exception:
            return False

    def _new_preview(
        self,
        request: WriteRequest,
        target_available: bool,
        state: str,
        blockers: tuple[str, ...],
        target_revision: str | None,
    ) -> WritePreview:
        preview = WritePreview(
            request,
            OWNER_ARTIFACTS[request.target],
            target_available,
            state,
            blockers,
            target_revision,
            token_urlsafe(24),
        )
        self._prepared_previews[preview.token] = preview
        return preview

    @staticmethod
    def _exists(target: ExternalWriteTarget, target_identity: str) -> bool:
        try:
            return target.exists(target_identity)
        except Exception:
            return False

    @staticmethod
    def _revision(target: ExternalWriteTarget, request: WriteRequest) -> str | None:
        try:
            return target.preview_revision(request)
        except Exception:
            return None

    @staticmethod
    def _preview_changed(request: WriteRequest) -> bool:
        comparisons = (
            (request.previous_proposed_content, request.proposed_content),
            (request.previous_duplicate_check_summary, request.duplicate_check_summary),
            (request.previous_source_check_summary, request.source_check_summary),
        )
        return any(previous is not None and previous != current for previous, current in comparisons)

    @staticmethod
    def _evidence_changed(request: WriteRequest, verification: GateVerification) -> bool:
        return (
            verification.duplicate_check_summary != request.duplicate_check_summary
            or verification.source_check_summary != request.source_check_summary
            or verification.trace != request.trace
        )

    @staticmethod
    def _validate(request: WriteRequest) -> None:
        if request.target not in OWNER_ARTIFACTS:
            raise ValueError("Target должен быть `anki` или `obsidian`.")
        actions = ANKI_ACTIONS if request.target == "anki" else OBSIDIAN_ACTIONS
        if request.action not in actions:
            raise ValueError(f"Действие `{request.action}` недопустимо для {request.target}.")
        target_fields = (
            (request.anki_deck, request.anki_note_type, request.anki_fields, request.anki_tags)
            if request.target == "anki"
            else (request.obsidian_target_path, request.obsidian_note, request.obsidian_section)
        )
        if not request.topic_workspace or not request.target_type or not all(target_fields):
            raise ValueError("Для preview нужны Topic Workspace и полные structured target details.")

    @staticmethod
    def _gate_blockers(request: WriteRequest, gates: GateSnapshot | None = None) -> list[str]:
        gates = gates or request.gates
        blockers: list[str] = []
        expected_decision = "card-promotion" if request.target == "anki" else "knowledge-consolidation"
        expected_label = "Card Promotion" if request.target == "anki" else "Knowledge Consolidation"
        if gates.decision_kind != expected_decision:
            blockers.append(f"{expected_label} decision отсутствует.")
        if gates.decision_action != request.action:
            blockers.append("Решение Orchestrator не совпадает с запрошенным action.")
        if not gates.checker_passed:
            blockers.append("Lightweight Checker не прошёл blocking gates.")
        if not gates.source_check_passed:
            blockers.append("Source Check не прошёл; чувствительный claim остаётся needs-check/rejected/superseded.")
        if not gates.duplicate_check_passed:
            blockers.append("Duplicate Check не завершён или устарел.")
        if not gates.content_ready:
            blockers.append("Контент не готов: нужна atomic card или curated Knowledge.")
        if not gates.trace_present:
            blockers.append("Card/Knowledge trace отсутствует.")
        if request.action in {"replace", "merge"} and not request.change_reason:
            blockers.append("Для replace/merge нужен reason изменения существующего target.")
        return blockers

    @staticmethod
    def _result_details(
        request: WriteRequest, result: str | ExternalWriteResult
    ) -> tuple[str, str | None, tuple[str, ...]]:
        if isinstance(result, ExternalWriteResult):
            return result.target_identity, result.anki_note_id, result.anki_card_ids
        return result, result if request.target == "anki" else None, ()

    @staticmethod
    def _outcome(
        request: WriteRequest,
        state: str,
        target_identity: str | None,
        next_action: str,
        anki_note_id: str | None = None,
        anki_card_ids: tuple[str, ...] = (),
        target_available: bool | None = None,
    ) -> WriteOutcome:
        return WriteOutcome(
            state,
            request.action,
            request.target,
            request.target_type,
            OWNER_ARTIFACTS[request.target],
            request.topic_workspace,
            request.source_entity,
            target_identity,
            next_action,
            request.target_description,
            request.duplicate_check_summary,
            request.source_check_summary,
            request.trace,
            request.change_reason,
            request.anki_deck,
            request.anki_note_type,
            request.anki_fields,
            request.anki_tags,
            anki_note_id if request.target == "anki" and state in {"succeeded", "partial"} else None,
            anki_card_ids if request.target == "anki" and state in {"succeeded", "partial"} else (),
            request.obsidian_target_path,
            request.obsidian_note,
            request.obsidian_section,
            request.linked_evidence,
            request.expected_markdown_updates,
            request.recovery_plan,
            target_available,
        )

    def _record_pending(self, request: WriteRequest, next_action: str) -> WriteOutcome:
        target = self.targets.get(request.target, UnavailableTarget())
        outcome = self._outcome(request, "pending", None, next_action, target_available=self._available(target))
        self._record(outcome)
        return outcome

    def _record(self, outcome: WriteOutcome) -> None:
        if self.trace_writer is None:
            raise RuntimeError("Нужен TraceWriter для фиксации outcome в owner artifact")
        self.trace_writer.record(outcome)
