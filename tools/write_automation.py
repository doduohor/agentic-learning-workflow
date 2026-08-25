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
from urllib.error import URLError
from urllib.request import Request, urlopen
from secrets import token_urlsafe
import hashlib
import json
import os
import re
import tempfile


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
    """Идентификатор от явного адаптера; ID карточек необязательны."""

    target_identity: str
    anki_note_id: str | None = None
    anki_card_ids: tuple[str, ...] = ()


class ExternalWriteTarget(Protocol):
    """Узкая граница внешнего target; рабочий адаптер задаётся явно."""

    def is_available(self) -> bool: ...

    def exists(self, target_identity: str) -> bool: ...

    def preview_revision(self, request: WriteRequest) -> str | None: ...

    def write(self, request: WriteRequest) -> str | ExternalWriteResult: ...


class AnkiConnectTransport(Protocol):
    """Узкий транспорт AnkiConnect; тесты подменяют его без сетевого порта."""

    def call(self, action: str, params: dict[str, object] | None = None) -> object: ...


class TraceWriter(Protocol):
    """Записывает outcome только в owner artifact, назначенный по target."""

    def record(self, outcome: WriteOutcome) -> None: ...


class GateVerifier(Protocol):
    """Перечитывает актуальный Checker/Source/Duplicate gate перед write."""

    def verify(self, request: WriteRequest) -> GateVerification: ...


class ExternalWriteError(RuntimeError):
    """Различимая ошибка внешнего target без превращения сбоя в успех."""


class ExternalWritePending(ExternalWriteError):
    """Нужен новый preview/reconciliation вместо внешней записи."""


class UnavailableTarget:
    """Безопасная настройка по умолчанию: реальная запись невозможна."""

    def is_available(self) -> bool:
        return False

    def exists(self, target_identity: str) -> bool:
        return False

    def preview_revision(self, request: WriteRequest) -> str | None:
        return None

    def write(self, request: WriteRequest) -> str:
        raise RuntimeError("Внешний target не настроен для записи")


class AnkiConnectHttpTransport:
    """Явно настроенный HTTP-транспорт для AnkiConnect API v6."""

    def __init__(self, endpoint: str, *, timeout: float = 5.0) -> None:
        if not endpoint:
            raise ValueError("AnkiConnect endpoint должен быть передан явно.")
        self.endpoint = endpoint
        self.timeout = timeout

    def call(self, action: str, params: dict[str, object] | None = None) -> object:
        payload: dict[str, object] = {"action": action, "version": 6}
        if params is not None:
            payload["params"] = params
        request = Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:  # nosec B310: endpoint передаётся явно
                response_data = json.load(response)
        except (URLError, OSError, json.JSONDecodeError, TypeError) as error:
            raise ExternalWriteError(f"AnkiConnect недоступен: {error}") from error
        if not isinstance(response_data, dict) or "error" not in response_data or "result" not in response_data:
            raise ExternalWriteError("AnkiConnect вернул неожиданный ответ протокола.")
        if response_data["error"]:
            raise ExternalWriteError(f"AnkiConnect вернул ошибку: {response_data['error']}")
        return response_data["result"]


class AnkiConnectAdapter:
    """Конкретный адаптер AnkiConnect; endpoint или транспорт задаётся явно."""

    def __init__(self, *, endpoint: str | None = None, transport: AnkiConnectTransport | None = None) -> None:
        if transport is None and endpoint is None:
            raise ValueError("AnkiConnectAdapter требует явный endpoint или транспорт.")
        self.transport = transport or AnkiConnectHttpTransport(endpoint or "")

    def is_available(self) -> bool:
        try:
            version = self.transport.call("version")
        except Exception:
            return False
        return isinstance(version, int) and version >= 6

    def exists(self, target_identity: str) -> bool:
        note_id = self._note_id(target_identity)
        if note_id is None:
            return False
        return bool(self._notes_info([note_id]))

    def preview_revision(self, request: WriteRequest) -> str | None:
        note_id = self._note_id(request.existing_target_identity or "")
        if note_id is None:
            result = self.transport.call("canAddNotesWithErrorDetail", {"notes": [self._note_payload(request)]})
            if not isinstance(result, list) or not result or not isinstance(result[0], dict):
                raise ExternalWriteError("AnkiConnect canAddNotesWithErrorDetail должен вернуть список результатов.")
            can_add = result[0].get("canAdd")
            error = result[0].get("error", "")
            if not isinstance(can_add, bool):
                raise ExternalWriteError("AnkiConnect canAddNotesWithErrorDetail не вернул canAdd.")
            if not can_add:
                return None
            return f"anki-add:canAdd={can_add}:error={error or '-'}"
        info = self._single_note_info(note_id)
        if info is None:
            return None
        cards = tuple(str(card) for card in info.get("cards", ()) if isinstance(card, int | str))
        mod = info.get("mod")
        if not isinstance(mod, int | str) or mod == "":
            return None
        return f"note:{note_id}:{mod}:{','.join(cards)}"

    def write(self, request: WriteRequest) -> ExternalWriteResult:
        if request.action == "skip":
            return ExternalWriteResult("skip")
        if request.action not in ANKI_ACTIONS - {"skip"}:
            raise ExternalWriteError(f"Anki action `{request.action}` не поддержан.")
        fields = self._fields_from_request(request)
        tags = self._tags_from_request(request)
        if request.action == "add":
            note_id = self.transport.call(
                "addNote",
                {"note": self._note_payload(request, fields=fields, tags=tags)},
            )
            if not isinstance(note_id, int | str) or note_id == "":
                raise ExternalWriteError("AnkiConnect addNote не вернул Note ID.")
        else:
            note_id = self._note_id(request.existing_target_identity or "")
            if note_id is None:
                raise ExternalWriteError("Для replace/merge нужен существующий Anki Note ID.")
            self.transport.call("updateNote", {"note": {"id": int(note_id), "fields": fields, "tags": tags}})
        return self._result_for_note(str(note_id))

    def _notes_info(self, note_ids: list[str]) -> list[dict[str, object]]:
        result = self.transport.call("notesInfo", {"notes": [int(note_id) for note_id in note_ids]})
        if not isinstance(result, list):
            raise ExternalWriteError("AnkiConnect notesInfo должен вернуть список.")
        return [note for note in result if isinstance(note, dict)]

    def _single_note_info(self, note_id: str) -> dict[str, object] | None:
        notes = self._notes_info([note_id])
        return notes[0] if notes else None

    def _result_for_note(self, note_id: str) -> ExternalWriteResult:
        info = self._single_note_info(note_id)
        cards: tuple[str, ...] = ()
        if info is not None:
            raw_cards = info.get("cards", ())
            if isinstance(raw_cards, list):
                cards = tuple(str(card) for card in raw_cards if isinstance(card, int | str))
        return ExternalWriteResult(f"note:{note_id}", note_id, cards)

    @staticmethod
    def _note_id(identity: str) -> str | None:
        normalized = identity.strip()
        if re.fullmatch(r"\d+", normalized):
            return normalized
        match = re.fullmatch(r"note:(\d+)", normalized)
        return match.group(1) if match else None

    @staticmethod
    def _fields_from_request(request: WriteRequest) -> dict[str, str]:
        field_names = [field.strip() for field in (request.anki_fields or "").split(",") if field.strip()]
        content_by_field: dict[str, list[str]] = {}
        current_field: str | None = None
        for line in request.proposed_content.splitlines():
            matched_field: str | None = None
            matched_value = ""
            for field_name in field_names:
                match = re.match(rf"^{re.escape(field_name)}\s*:\s?(.*)$", line)
                if match:
                    matched_field = field_name
                    matched_value = match.group(1)
                    break
            if matched_field is not None:
                current_field = matched_field
                content_by_field[current_field] = [matched_value]
            elif current_field is not None:
                content_by_field[current_field].append(line)
        missing = [field for field in field_names if field not in content_by_field]
        if missing:
            raise ExternalWriteError(f"Proposed content не содержит поля Anki: {', '.join(missing)}")
        return {field: "\n".join(lines).strip() for field, lines in content_by_field.items()}

    @staticmethod
    def _tags_from_request(request: WriteRequest) -> list[str]:
        return [tag for tag in re.split(r"\s+", request.anki_tags or "") if tag]

    def _note_payload(
        self,
        request: WriteRequest,
        *,
        fields: dict[str, str] | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, object]:
        return {
            "deckName": request.anki_deck or "",
            "modelName": request.anki_note_type or "",
            "fields": fields if fields is not None else self._fields_from_request(request),
            "tags": tags if tags is not None else self._tags_from_request(request),
        }


class ObsidianFilesystemAdapter:
    """Конкретный адаптер для Markdown-файлов внутри явно переданного vault root."""

    def __init__(self, vault_root: Path | str) -> None:
        self.vault_root = Path(vault_root).resolve()

    def is_available(self) -> bool:
        return self.vault_root.is_dir() and os.access(self.vault_root, os.R_OK | os.W_OK)

    def exists(self, target_identity: str) -> bool:
        try:
            path = self._target_path(target_identity.split("#", 1)[0])
        except ExternalWriteError:
            return False
        return path.is_file()

    def preview_revision(self, request: WriteRequest) -> str | None:
        path = self._target_path(request.obsidian_target_path or "")
        return self._revision(path)

    def write(self, request: WriteRequest) -> ExternalWriteResult:
        if request.action == "skip":
            return ExternalWriteResult("skip")
        path = self._target_path(request.obsidian_target_path or "")
        before_revision = self._revision(path)
        if request.action == "add":
            if path.exists():
                raise ExternalWriteError("Obsidian target уже существует; нужен append/merge/replace-section.")
            updated = request.proposed_content
        else:
            if not path.is_file():
                raise ExternalWriteError("Obsidian target не найден.")
            current = path.read_text(encoding="utf-8")
            if request.action == "append":
                updated = current.rstrip() + "\n\n" + request.proposed_content.rstrip() + "\n"
            elif request.action == "replace-section":
                updated = self._replace_section(current, request.obsidian_section or "", request.proposed_content)
            elif request.action == "merge":
                updated = self._deterministic_merge_section(
                    current,
                    request.obsidian_section or "",
                    request.proposed_content,
                )
            else:
                raise ExternalWriteError(f"Obsidian action `{request.action}` не поддержан.")
        if before_revision != self._revision(path):
            raise ExternalWriteError("Obsidian target изменился перед записью; нужен новый preview.")
        self._atomic_write(path, updated)
        identity = self._identity(path, request.obsidian_section if request.action in {"replace-section", "merge"} else None)
        return ExternalWriteResult(identity)

    def _target_path(self, target_path: str) -> Path:
        if not target_path or Path(target_path).is_absolute():
            raise ExternalWriteError("Целевой путь Obsidian должен быть относительным путём внутри vault.")
        if Path(target_path).suffix.lower() != ".md":
            raise ExternalWriteError("Адаптер Obsidian пишет только Markdown-файлы `.md`.")
        candidate = (self.vault_root / target_path).resolve(strict=False)
        if not self._inside_vault(candidate):
            raise ExternalWriteError("Целевой путь Obsidian выходит за пределы vault.")
        existing = self._nearest_existing(candidate)
        if existing is not None and existing.resolve() != existing.absolute():
            resolved_existing = existing.resolve()
            if not self._inside_vault(resolved_existing):
                raise ExternalWriteError("Символическая ссылка Obsidian выходит за пределы vault.")
        return candidate

    def _inside_vault(self, path: Path) -> bool:
        return path == self.vault_root or self.vault_root in path.parents

    @staticmethod
    def _nearest_existing(path: Path) -> Path | None:
        current = path
        while not current.exists():
            parent = current.parent
            if parent == current:
                return None
            current = parent
        return current

    def _revision(self, path: Path) -> str:
        if not path.exists():
            return "missing"
        if not path.is_file():
            raise ExternalWriteError("Obsidian target должен быть Markdown-файлом.")
        content = path.read_bytes()
        stat = path.stat()
        digest = hashlib.sha256(content).hexdigest()
        return f"sha256:{digest}:size:{stat.st_size}:mtime:{stat.st_mtime_ns}"

    def _identity(self, path: Path, section: str | None = None) -> str:
        relative = path.relative_to(self.vault_root).as_posix()
        if section:
            return f"{relative}#{section}"
        return relative

    @staticmethod
    def _replace_section(content: str, section: str, replacement: str) -> str:
        bounds = ObsidianFilesystemAdapter._section_bounds(content, section)
        if bounds is None:
            raise ExternalWriteError(f"Obsidian section `{section}` не найдена.")
        start, end = bounds
        return content[:start] + replacement.rstrip() + "\n" + content[end:]

    @staticmethod
    def _deterministic_merge_section(content: str, section: str, proposed_content: str) -> str:
        proposed = proposed_content.strip()
        heading = re.match(r"^(?P<level>#{1,6})\s+(?P<title>.+?)\s*$", proposed, flags=re.MULTILINE)
        if heading is None or heading.group("title") != section.strip():
            raise ExternalWritePending("Неоднозначный merge: предложенный контент должен содержать тот же Markdown-заголовок.")
        bounds = ObsidianFilesystemAdapter._section_bounds(content, section)
        if bounds is None:
            raise ExternalWriteError(f"Obsidian section `{section}` не найдена.")
        body = proposed[heading.end():].strip()
        if not body:
            raise ExternalWritePending("Неоднозначный merge: предложенный контент не содержит нового тела секции.")
        start, end = bounds
        existing_section = content[start:end].rstrip()
        merged_section = existing_section + "\n\n" + body + "\n"
        return content[:start] + merged_section + content[end:]

    @staticmethod
    def _section_bounds(content: str, section: str) -> tuple[int, int] | None:
        escaped = re.escape(section.strip())
        heading = re.search(rf"^(?P<level>#{{1,6}})\s+{escaped}\s*$", content, flags=re.MULTILINE)
        if heading is None:
            return None
        level = len(heading.group("level"))
        next_heading = re.search(rf"^#{{1,{level}}}\s+", content[heading.end():], flags=re.MULTILINE)
        end = heading.end() + next_heading.start() if next_heading else len(content)
        return heading.start(), end

    @staticmethod
    def _atomic_write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_name = ""
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as temp_file:
                temp_name = temp_file.name
                temp_file.write(content)
                temp_file.flush()
                os.fsync(temp_file.fileno())
            os.replace(temp_name, path)
        except Exception as error:
            if temp_name:
                try:
                    Path(temp_name).unlink(missing_ok=True)
                except OSError:
                    pass
            raise ExternalWriteError(f"Atomic write в Obsidian не выполнен: {error}") from error


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
            blockers.append("Write Target недоступен: внешняя запись остаётся Pending Write.")
        if available and request.action != "skip" and target_revision is None:
            blockers.append("Revision Write Target недоступна; нужен reconciliation preview до записи.")
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
                if request.action in {"replace", "merge", "replace-section"}:
                    return self._new_preview(request, True, "ready-for-approval", tuple(), target_revision)
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
        except ExternalWritePending as error:
            return self._record_pending(request, f"{error} Подготовьте reconciliation preview.")
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
