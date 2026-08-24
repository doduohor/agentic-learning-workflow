#!/usr/bin/env python3
"""Read-only проверка похожих записей в Obsidian и Anki.

Утилита не меняет vault, Anki или Topic Workspace. Она выдаёт Markdown-сводку,
которую Learning Orchestrator при необходимости переносит в owner artifact.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.error import URLError
from urllib.request import Request, urlopen


OBSIDIAN_VAULT = Path("/mnt/c/Users/Sergey/Documents/GPT/Work")
ANKI_READ_ACTIONS = ("findNotes", "notesInfo")
VALID_TARGETS = {"card", "knowledge"}


@dataclass(frozen=True)
class DuplicateMatch:
    source: str
    reference: str
    excerpt: str
    strength: str


@dataclass(frozen=True)
class DuplicateCheckSummary:
    target: str
    source_entity: str
    query: str
    status: str
    obsidian_availability: str
    anki_availability: str
    matches: tuple[DuplicateMatch, ...]
    recommended_action: str
    requires_orchestrator_decision: bool
    requires_user_decision: bool
    owner_artifact: str
    trace_outcome: str
    next_step: str

    def to_markdown(self) -> str:
        lines = [
            "#### Duplicate Check summary",
            "",
            f"- Target: `{self.target}`",
            f"- Source entity: `{self.source_entity}`",
            f"- Запрос: {self.query}",
            f"- Availability: Obsidian — `{self.obsidian_availability}`; Anki — `{self.anki_availability}`",
            f"- Outcome: `{self.status}`",
            f"- Owner artifact: `{self.owner_artifact}`; trace outcome: `{self.trace_outcome}`",
        ]
        if self.matches:
            lines.append("- Похожие объекты:")
            for match in self.matches:
                lines.append(
                    f"  - `{match.strength}`; {match.source}; {match.reference}; {match.excerpt}"
                )
        else:
            lines.append("- Похожие объекты: не найдены.")
        lines.extend(
            [
                f"- Рекомендованное действие: `{self.recommended_action}`",
                "- Решение Learning Orchestrator: "
                + ("требуется." if self.requires_orchestrator_decision else "может принять обычное решение."),
                "- Решение пользователя: "
                + ("требуется перед рискованным изменением." if self.requires_user_decision else "не требуется по результату проверки."),
                f"- Next step: {self.next_step}",
            ]
        )
        return "\n".join(lines)


class AnkiReader(Protocol):
    """Минимальная read-only граница Anki для Duplicate Check."""

    def search(self, query: str) -> list[dict[str, str]]: ...


class AnkiConnectReadClient:
    """Клиент AnkiConnect, вызывающий только ``findNotes`` и ``notesInfo``."""

    def __init__(self, endpoint: str = "http://localhost:8765") -> None:
        self.endpoint = endpoint

    def search(self, query: str) -> list[dict[str, str]]:
        note_ids = self._call("findNotes", {"query": query})
        if not note_ids:
            return []
        notes = self._call("notesInfo", {"notes": note_ids})
        return [
            {
                "id": str(note.get("noteId", "?")),
                "front": self._note_excerpt(note),
            }
            for note in notes
        ]

    def _call(self, action: str, params: dict[str, object]) -> object:
        if action not in ANKI_READ_ACTIONS:
            raise ValueError(f"Недопустимое действие Anki: {action}")
        payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
        request = Request(self.endpoint, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=2) as response:  # nosec B310: localhost is explicit
                response_data = json.load(response)
        except (URLError, OSError, json.JSONDecodeError, AttributeError, KeyError, TypeError) as error:
            raise ConnectionError("Anki недоступен") from error
        if response_data.get("error"):
            raise ConnectionError(f"Anki вернул ошибку: {response_data['error']}")
        return response_data["result"]

    @staticmethod
    def _note_excerpt(note: dict[str, object]) -> str:
        fields = note.get("fields", {})
        if not isinstance(fields, dict):
            return "без доступного текста"
        values = [str(field.get("value", "")) for field in fields.values() if isinstance(field, dict)]
        return compact_text(" ".join(values)) or "без доступного текста"


class DuplicateCheckWorkflow:
    """Собирает read-only evidence для Card Promotion или Consolidation."""

    def __init__(self, vault: Path = OBSIDIAN_VAULT, *, anki_reader: AnkiReader | None = None) -> None:
        self.vault = vault
        self.anki_reader = anki_reader

    def check(
        self,
        *,
        target: str,
        query: str,
        anki_required: bool = False,
        source_entity: str = "-",
        full_vault: bool = False,
    ) -> DuplicateCheckSummary:
        if target not in VALID_TARGETS:
            raise ValueError("Target должен быть `card` или `knowledge`.")
        if target != "card" and anki_required:
            raise ValueError("Anki проверяется только для планируемой записи карточки.")

        obsidian_availability, obsidian_matches = self._search_obsidian(query, full_vault=full_vault)
        anki_availability, anki_matches = self._search_anki(query, anki_required)
        unavailable = obsidian_availability == "unavailable" or anki_availability == "unavailable"
        matches = tuple(obsidian_matches + anki_matches)
        owner_artifact = "Questions.md" if target == "card" else "Knowledge.md"
        trace_outcome = "Card Promotion pending" if target == "card" else "Knowledge Consolidation pending"
        if unavailable:
            return DuplicateCheckSummary(
                target, source_entity, query, "pending", obsidian_availability, anki_availability, matches,
                "-", True, False, owner_artifact, trace_outcome,
                "Learning Orchestrator сохраняет pending trace и повторяет unavailable Duplicate Check до нужного gate.",
            )

        action, orchestrator, user = self._recommend(matches)
        return DuplicateCheckSummary(
            target, source_entity, query, "available", obsidian_availability, anki_availability, matches,
            action, orchestrator, user, owner_artifact, "not-completed",
            "Learning Orchestrator фиксирует summary в owner artifact и принимает действие до следующего gate.",
        )

    def _search_obsidian(self, query: str, *, full_vault: bool) -> tuple[str, list[DuplicateMatch]]:
        if not self.vault.is_dir():
            return "unavailable", []
        query_tokens = meaningful_tokens(query)
        matches: list[DuplicateMatch] = []
        try:
            first_pass = self._first_pass_notes(query_tokens)
            for note in first_pass:
                text = note.read_text(encoding="utf-8")
                combined = f"{note.stem}\n{text}"
                strength = match_strength(query, query_tokens, combined)
                if strength:
                    matches.append(DuplicateMatch("Obsidian", str(note.relative_to(self.vault)), excerpt_for(query_tokens, text), strength))
            if not matches or full_vault:
                seen = set(first_pass)
                for note in self.vault.rglob("*.md"):
                    if note in seen:
                        continue
                    text = note.read_text(encoding="utf-8")
                    combined = f"{note.stem}\n{text}"
                    strength = match_strength(query, query_tokens, combined)
                    if strength:
                        matches.append(DuplicateMatch("Obsidian", str(note.relative_to(self.vault)), excerpt_for(query_tokens, text), strength))
        except OSError:
            return "unavailable", []
        return "available", sorted(matches, key=lambda match: (match.strength != "strong", match.reference))

    def _first_pass_notes(self, query_tokens: set[str]) -> list[Path]:
        context_roots = [self.vault / "maps", self.vault / "40_project"]
        contextual = [
            note for note in self.vault.rglob("*.md")
            if query_tokens & meaningful_tokens(str(note.relative_to(self.vault)))
        ]
        notes = [note for root in context_roots if root.is_dir() for note in root.rglob("*.md")]
        return sorted(set(notes + contextual))

    def _search_anki(self, query: str, required: bool) -> tuple[str, list[DuplicateMatch]]:
        if not required:
            return "not-requested", []
        if self.anki_reader is None:
            return "unavailable", []
        try:
            notes = self.anki_reader.search(query)
        except (ConnectionError, OSError):
            return "unavailable", []
        matches = [
            DuplicateMatch(
                "Anki",
                f"note:{note.get('id', '?')}",
                compact_text(note.get("front", "")),
                "partial",
            )
            for note in notes
        ]
        return "available", matches

    @staticmethod
    def _recommend(matches: tuple[DuplicateMatch, ...]) -> tuple[str, bool, bool]:
        if matches:
            return "merge", *decision_requirements("merge")
        return "add", False, False


def meaningful_tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[\w-]+", text.lower(), flags=re.UNICODE) if len(token) > 2}


def match_strength(query: str, query_tokens: set[str], text: str) -> str | None:
    text_tokens = meaningful_tokens(text)
    if query_tokens and query_tokens <= text_tokens:
        return "partial"
    overlap = len(query_tokens & text_tokens)
    return "partial" if overlap >= 2 else None


def decision_requirements(action: str, *, strong_duplicate: bool = False) -> tuple[bool, bool]:
    """Возвращает необходимость решений без выбора action за Orchestrator."""
    if strong_duplicate or action in {"replace", "merge"}:
        return True, True
    return False, False


def compact_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[#*_`]+", "", str(text))).strip()[:180]


def excerpt_for(tokens: set[str], text: str) -> str:
    for line in text.splitlines():
        if tokens & meaningful_tokens(line):
            return compact_text(line)
    return compact_text(text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Duplicate Check для Obsidian и Anki.")
    parser.add_argument("--target", choices=sorted(VALID_TARGETS), required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--vault", type=Path, default=OBSIDIAN_VAULT)
    parser.add_argument("--anki-required", action="store_true", help="Проверить Anki перед планируемой записью карточки.")
    parser.add_argument("--anki-endpoint", default="http://localhost:8765")
    parser.add_argument("--source-entity", default="-", help="Q-* или Knowledge section для trace.")
    parser.add_argument("--full-vault", action="store_true", help="Расширить неоднозначный Obsidian поиск после решения Orchestrator.")
    args = parser.parse_args()
    anki_reader = AnkiConnectReadClient(args.anki_endpoint) if args.anki_required else None
    summary = DuplicateCheckWorkflow(args.vault, anki_reader=anki_reader).check(
        target=args.target, query=args.query, anki_required=args.anki_required, source_entity=args.source_entity,
        full_vault=args.full_vault,
    )
    print(summary.to_markdown())
    return 1 if summary.status == "pending" else 0


if __name__ == "__main__":
    raise SystemExit(main())
