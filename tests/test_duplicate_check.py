from __future__ import annotations

import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from tools.duplicate_check import AnkiConnectReadClient, DuplicateCheckWorkflow, decision_requirements


class RecordingAnkiReader:
    def __init__(self, notes: list[dict[str, str]] | None = None, *, available: bool = True) -> None:
        self.notes = notes or []
        self.available = available
        self.actions: list[str] = []

    def search(self, query: str) -> list[dict[str, str]]:
        self.actions.append("findNotes")
        if not self.available:
            raise ConnectionError("Anki недоступен")
        return self.notes


class InvalidJsonResponse:
    def __enter__(self) -> BytesIO:
        return BytesIO(b"not-json")

    def __exit__(self, *args: object) -> None:
        return None


class DuplicateCheckWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault = Path(self.temp_dir.name) / "vault"
        self.vault.mkdir()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def workflow(self, anki: RecordingAnkiReader | None = None) -> DuplicateCheckWorkflow:
        return DuplicateCheckWorkflow(self.vault, anki_reader=anki)

    def test_reports_add_when_no_duplicate_is_found(self) -> None:
        summary = self.workflow().check(
            target="card",
            query="retry without idempotency",
            anki_required=False,
        )

        self.assertEqual(summary.status, "available")
        self.assertEqual(summary.recommended_action, "add")
        self.assertFalse(summary.matches)
        self.assertEqual(summary.anki_availability, "not-requested")

    def test_strong_obsidian_duplicate_requires_orchestrator_decision(self) -> None:
        self.assertEqual(decision_requirements("skip", strong_duplicate=True), (True, True))

    def test_partial_match_recommends_merge_and_requires_decision(self) -> None:
        (self.vault / "RabbitMQ.md").write_text(
            "# RabbitMQ\n\nRetry повторяет доставку сообщений после сбоя consumer.",
            encoding="utf-8",
        )

        summary = self.workflow().check(target="knowledge", query="retry idempotency consumer")

        self.assertEqual(summary.recommended_action, "merge")
        self.assertTrue(summary.requires_orchestrator_decision)
        self.assertEqual(summary.matches[0].strength, "partial")

    def test_token_substring_does_not_create_a_strong_match(self) -> None:
        (self.vault / "Rapid delivery.md").write_text("# Rapid delivery\n", encoding="utf-8")

        summary = self.workflow().check(target="knowledge", query="api")

        self.assertFalse(summary.matches)

    def test_anki_search_result_is_partial_when_front_does_not_cover_query(self) -> None:
        anki = RecordingAnkiReader([{"id": "42", "front": "Retry consumer после сбоя"}])

        summary = self.workflow(anki).check(
            target="card",
            query="retry idempotency consumer",
            anki_required=True,
        )

        self.assertEqual(summary.matches[0].strength, "partial")
        self.assertEqual(summary.recommended_action, "merge")

    def test_textual_match_is_not_strong_without_semantic_assessment(self) -> None:
        (self.vault / "RabbitMQ.md").write_text(
            "# Retry without idempotency\n\nМатериал о другой единице знания.", encoding="utf-8"
        )

        summary = self.workflow().check(target="knowledge", query="retry without idempotency")

        self.assertEqual(summary.matches[0].strength, "partial")
        self.assertEqual(summary.recommended_action, "merge")

    def test_ambiguous_first_pass_expands_to_full_vault_only_on_orchestrator_request(self) -> None:
        (self.vault / "maps").mkdir()
        (self.vault / "maps" / "MOC_Roadmap.md").write_text("# retry idempotency\n", encoding="utf-8")
        (self.vault / "archive").mkdir()
        (self.vault / "archive" / "old.md").write_text("# retry idempotency\n", encoding="utf-8")

        summary = self.workflow().check(target="knowledge", query="retry idempotency", full_vault=True)

        self.assertEqual(
            [match.reference for match in summary.matches],
            ["archive/old.md", "maps/MOC_Roadmap.md"],
        )

    def test_unavailable_obsidian_leaves_pending_outcome(self) -> None:
        summary = DuplicateCheckWorkflow(self.vault / "missing").check(
            target="knowledge",
            query="retry idempotency",
        )

        self.assertEqual(summary.status, "pending")
        self.assertEqual(summary.obsidian_availability, "unavailable")
        self.assertEqual(summary.recommended_action, "-")

    def test_invalid_anki_response_becomes_unavailable(self) -> None:
        client = AnkiConnectReadClient()

        with patch("tools.duplicate_check.urlopen", return_value=InvalidJsonResponse()):
            with self.assertRaises(ConnectionError):
                client.search("retry")

    def test_unavailable_anki_leaves_card_candidate_pending(self) -> None:
        anki = RecordingAnkiReader(available=False)

        summary = self.workflow(anki).check(
            target="card",
            query="retry idempotency",
            anki_required=True,
            source_entity="Q-20260824-03",
        )

        self.assertEqual(summary.status, "pending")
        self.assertEqual(summary.anki_availability, "unavailable")
        self.assertEqual(summary.recommended_action, "-")
        self.assertEqual(summary.trace_outcome, "Card Promotion pending")
        self.assertEqual(summary.owner_artifact, "Questions.md")
        self.assertEqual(anki.actions, ["findNotes"])

    def test_anki_is_checked_only_for_planned_card_write(self) -> None:
        anki = RecordingAnkiReader()

        self.workflow(anki).check(target="knowledge", query="retry idempotency")
        self.workflow(anki).check(target="card", query="retry idempotency", anki_required=False)

        self.assertEqual(anki.actions, [])

    def test_workflow_does_not_modify_external_data(self) -> None:
        note = self.vault / "RabbitMQ.md"
        note.write_text("# RabbitMQ\n\nRetry", encoding="utf-8")
        anki = RecordingAnkiReader([{"id": "42", "front": "Что делает retry?"}])
        before = note.read_text(encoding="utf-8")

        self.workflow(anki).check(target="card", query="retry", anki_required=True)

        self.assertEqual(note.read_text(encoding="utf-8"), before)
        self.assertEqual(anki.actions, ["findNotes"])


if __name__ == "__main__":
    unittest.main()
