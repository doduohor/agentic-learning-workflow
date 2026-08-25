from __future__ import annotations

import unittest
import tempfile
from dataclasses import replace
from pathlib import Path

from tools.write_automation import (
    AnkiConnectAdapter,
    ExternalWriteError,
    GateSnapshot,
    GateVerification,
    ExternalWriteResult,
    InMemoryTraceWriter,
    MarkdownTraceWriter,
    ObsidianFilesystemAdapter,
    WriteAutomation,
    WriteRequest,
)


class RecordingTarget:
    def __init__(
        self,
        *,
        available: bool = True,
        existing: bool = False,
        revision: str | None = "rev-1",
        write_error: Exception | None = None,
        write_result: str | ExternalWriteResult = "external-42",
    ) -> None:
        self.available = available
        self.existing = existing
        self.revision = revision
        self.write_error = write_error
        self.write_result = write_result
        self.writes: list[WriteRequest] = []

    def is_available(self) -> bool:
        return self.available

    def exists(self, target_identity: str) -> bool:
        return self.existing

    def preview_revision(self, request: WriteRequest) -> str | None:
        return self.revision

    def write(self, request: WriteRequest) -> str:
        self.writes.append(request)
        if self.write_error:
            raise self.write_error
        return self.write_result


class CurrentGateVerifier:
    def __init__(self, verification: GateVerification | None = None) -> None:
        self.verification = verification

    def verify(self, request: WriteRequest) -> GateVerification:
        return self.verification or GateVerification(
            request.gates,
            request.duplicate_check_summary,
            request.source_check_summary,
            request.trace,
        )


class FailingTraceWriter(InMemoryTraceWriter):
    def record(self, outcome):  # type: ignore[no-untyped-def]
        raise OSError("не удалось обновить owner artifact")


def write_request(**changes: object) -> WriteRequest:
    values: dict[str, object] = {
        "topic_workspace": "topics/rabbitmq/retry-without-idempotency",
        "target": "anki",
        "target_type": "Anki note",
        "action": "add",
        "source_entity": "Q-20260824-01",
        "target_description": "deck Kotlin Backend / Basic / Front, Back, tags",
        "proposed_content": "Front: Почему retry без idempotency опасен?\nBack: Возможны повторные side effects.",
        "duplicate_check_summary": "Obsidian: available; Anki: available; strong duplicate: no.",
        "source_check_summary": "SRC-20260824-01: verified.",
        "trace": "Q-20260824-01 -> PA-20260824-01 -> SRC-20260824-01",
        "expected_markdown_updates": "Questions.md: Anki write outcome.",
        "recovery_plan": "При сбое сохранить pending и повторить availability check.",
        "anki_deck": "Kotlin Backend",
        "anki_note_type": "Basic",
        "anki_fields": "Front, Back",
        "anki_tags": "rabbitmq retry idempotency",
        "obsidian_target_path": "Work/RabbitMQ.md",
        "obsidian_note": "RabbitMQ",
        "obsidian_section": "Retry",
        "gates": GateSnapshot(
            checker_passed=True,
            source_check_passed=True,
            duplicate_check_passed=True,
            decision_kind="card-promotion",
            decision_action="add",
            content_ready=True,
            trace_present=True,
        ),
    }
    values.update(changes)
    return WriteRequest(**values)  # type: ignore[arg-type]


def obsidian_request(action: str, **changes: object) -> WriteRequest:
    defaults: dict[str, object] = {
        "target": "obsidian",
        "action": action,
        "gates": GateSnapshot(True, True, True, "knowledge-consolidation", action, True, True),
    }
    defaults.update(changes)
    return write_request(**defaults)


class FakeAnkiTransport:
    def __init__(self, replies: dict[tuple[str, str], object] | None = None, *, error: Exception | None = None) -> None:
        self.replies = replies or {}
        self.error = error
        self.calls: list[tuple[str, dict[str, object]]] = []

    def call(self, action: str, params: dict[str, object] | None = None) -> object:
        params = params or {}
        self.calls.append((action, params))
        if self.error:
            raise self.error
        key = (action, repr(params))
        if key not in self.replies:
            raise ExternalWriteError(f"unexpected Anki action: {action} {params}")
        return self.replies[key]


class WriteAutomationTests(unittest.TestCase):
    def request(self, **changes: object) -> WriteRequest:
        return write_request(**changes)

    def test_dry_run_contains_required_context_and_never_writes(self) -> None:
        target = RecordingTarget(write_result=ExternalWriteResult("external-42", "note-42", ("card-100", "card-101")))
        automation = WriteAutomation(
            {"anki": target, "obsidian": RecordingTarget()}, trace_writer=InMemoryTraceWriter()
        )

        preview = automation.prepare(self.request())

        self.assertEqual(preview.state, "ready-for-approval")
        self.assertIn("Target: `anki`", preview.to_markdown())
        self.assertIn("Duplicate Check", preview.to_markdown())
        self.assertIn("План восстановления", preview.to_markdown())
        self.assertEqual(target.writes, [])

    def test_anki_preview_and_success_trace_include_structured_target_details_and_ids(self) -> None:
        target = RecordingTarget(write_result=ExternalWriteResult("external-42", "note-42", ("card-100", "card-101")))
        trace_writer = InMemoryTraceWriter()
        automation = WriteAutomation(
            {"anki": target, "obsidian": RecordingTarget()},
            trace_writer=trace_writer,
            gate_verifier=CurrentGateVerifier(),
        )

        preview = automation.prepare(self.request())
        outcome = automation.execute(preview, approved=True)

        self.assertIn("Topic Workspace: `topics/rabbitmq/retry-without-idempotency`", preview.to_markdown())
        self.assertIn("Anki deck: `Kotlin Backend`", preview.to_markdown())
        self.assertIn("Anki note type: `Basic`", preview.to_markdown())
        self.assertIn("Anki fields: `Front, Back`", preview.to_markdown())
        self.assertIn("Anki tags: `rabbitmq retry idempotency`", preview.to_markdown())
        self.assertEqual(outcome.anki_note_id, "note-42")
        self.assertEqual(outcome.anki_card_ids, ("card-100", "card-101"))
        self.assertIn("Anki Note ID: `note-42`", outcome.to_markdown())
        self.assertIn("Anki Card IDs: `card-100, card-101`", outcome.to_markdown())

    def test_obsidian_preview_and_trace_include_path_note_section_and_evidence(self) -> None:
        request = self.request(
            target="obsidian",
            target_type="Obsidian section",
            action="append",
            source_entity="Knowledge.md#b01---retry",
            target_description="Retry explanation",
            obsidian_target_path="Work/RabbitMQ.md",
            obsidian_note="RabbitMQ",
            obsidian_section="Retry",
            linked_evidence="[PA-20260824-01](Practice.md#pa-20260824-01---retry-safety-sketch)",
            expected_markdown_updates="Knowledge.md: Obsidian write outcome.",
            gates=GateSnapshot(True, True, True, "knowledge-consolidation", "append", True, True),
        )
        trace_writer = InMemoryTraceWriter()
        automation = WriteAutomation(
            {"anki": RecordingTarget(), "obsidian": RecordingTarget()},
            trace_writer=trace_writer,
            gate_verifier=CurrentGateVerifier(),
        )

        preview = automation.prepare(request)
        outcome = automation.execute(preview, approved=True)

        self.assertIn("Obsidian path: `Work/RabbitMQ.md`", preview.to_markdown())
        self.assertIn("Obsidian note: `RabbitMQ`", preview.to_markdown())
        self.assertIn("Obsidian section: `Retry`", preview.to_markdown())
        self.assertIn("Linked evidence", outcome.to_markdown())

    def test_merge_preserves_reason_in_successful_trace(self) -> None:
        request = self.request(
            action="merge",
            change_reason="Existing card partly duplicates the same failure mode.",
            gates=GateSnapshot(True, True, True, "card-promotion", "merge", True, True),
        )
        trace_writer = InMemoryTraceWriter()
        automation = WriteAutomation(
            {"anki": RecordingTarget(), "obsidian": RecordingTarget()},
            trace_writer=trace_writer,
            gate_verifier=CurrentGateVerifier(),
        )

        outcome = automation.execute(automation.prepare(request), approved=True)

        self.assertEqual(outcome.change_reason, request.change_reason)
        self.assertIn(request.change_reason, outcome.to_markdown())

    def test_unavailable_preview_has_no_success_trace(self) -> None:
        trace_writer = InMemoryTraceWriter()
        automation = WriteAutomation(
            {"anki": RecordingTarget(available=False), "obsidian": RecordingTarget()},
            trace_writer=trace_writer,
        )

        preview = automation.prepare(self.request())
        outcome = automation.execute(preview, approved=True)

        self.assertEqual(outcome.state, "pending")
        self.assertNotIn("успеш", outcome.to_markdown().lower())

    def test_rejected_or_missing_approval_never_calls_production_write(self) -> None:
        target = RecordingTarget()
        automation = WriteAutomation(
            {"anki": target, "obsidian": RecordingTarget()}, trace_writer=InMemoryTraceWriter()
        )
        preview = automation.prepare(self.request())

        outcome = automation.execute(preview, approved=False)

        self.assertEqual(outcome.state, "pending")
        self.assertEqual(target.writes, [])

    def test_unavailable_target_stays_pending_without_claiming_success(self) -> None:
        target = RecordingTarget(available=False)
        automation = WriteAutomation(
            {"anki": target, "obsidian": RecordingTarget()}, trace_writer=InMemoryTraceWriter()
        )

        preview = automation.prepare(self.request())
        outcome = automation.execute(preview, approved=True)

        self.assertEqual(preview.state, "pending")
        self.assertEqual(outcome.state, "pending")
        self.assertEqual(target.writes, [])

    def test_anki_requires_card_promotion_and_all_gates(self) -> None:
        target = RecordingTarget()
        automation = WriteAutomation({"anki": target, "obsidian": RecordingTarget()})
        request = self.request(gates=GateSnapshot(
            checker_passed=True, source_check_passed=True, duplicate_check_passed=True,
            decision_kind="knowledge-consolidation", decision_action="add",
            content_ready=True, trace_present=True,
        ))

        preview = automation.prepare(request)

        self.assertEqual(preview.state, "pending")
        self.assertIn("Card Promotion", preview.blockers[0])

    def test_obsidian_requires_knowledge_consolidation_and_all_gates(self) -> None:
        target = RecordingTarget()
        automation = WriteAutomation({"anki": RecordingTarget(), "obsidian": target})
        request = self.request(
            target="obsidian",
            action="append",
            source_entity="Knowledge.md#b01---retry",
            target_description="Work/RabbitMQ.md#Retry",
            expected_markdown_updates="Knowledge.md: Obsidian write outcome.",
            gates=GateSnapshot(
                checker_passed=True, source_check_passed=False, duplicate_check_passed=True,
                decision_kind="knowledge-consolidation", decision_action="append",
                content_ready=True, trace_present=True,
            ),
        )

        preview = automation.prepare(request)

        self.assertEqual(preview.state, "pending")
        self.assertTrue(any("Source Check" in blocker for blocker in preview.blockers))
        self.assertEqual(target.writes, [])

    def test_success_records_trace_only_in_target_owner_artifact(self) -> None:
        target = RecordingTarget()
        trace_writer = InMemoryTraceWriter()
        automation = WriteAutomation(
            {"anki": target, "obsidian": RecordingTarget()},
            trace_writer=trace_writer,
            gate_verifier=CurrentGateVerifier(),
        )

        outcome = automation.execute(automation.prepare(self.request()), approved=True)

        self.assertEqual(outcome.state, "succeeded")
        self.assertEqual(outcome.owner_artifact, "Questions.md")
        self.assertEqual(trace_writer.owner_artifacts, ["Questions.md"])
        self.assertEqual(target.writes, [self.request()])

    def test_repeat_after_external_success_is_no_op(self) -> None:
        target = RecordingTarget(existing=True)
        automation = WriteAutomation({"anki": target, "obsidian": RecordingTarget()})
        request = self.request(existing_target_identity="external-42")

        preview = automation.prepare(request)
        outcome = automation.execute(preview, approved=True)

        self.assertEqual(preview.state, "no-op")
        self.assertEqual(outcome.state, "no-op")
        self.assertEqual(target.writes, [])

    def test_trace_without_external_target_requires_reconciliation_preview(self) -> None:
        target = RecordingTarget(existing=False)
        automation = WriteAutomation({"anki": target, "obsidian": RecordingTarget()})
        request = self.request(existing_target_identity="external-42")

        preview = automation.prepare(request)

        self.assertEqual(preview.state, "reconciliation-preview")
        self.assertEqual(target.writes, [])

    def test_changed_content_or_duplicate_summary_turns_repeat_into_reconciliation_preview(self) -> None:
        target = RecordingTarget(existing=True)
        automation = WriteAutomation({"anki": target, "obsidian": RecordingTarget()})
        request = self.request(
            existing_target_identity="external-42",
            previous_proposed_content="Front: старый вопрос",
        )

        preview = automation.prepare(request)

        self.assertEqual(preview.state, "reconciliation-preview")
        self.assertIn("изменились", preview.blockers[0])

    def test_changed_external_target_after_preview_blocks_write_and_requests_new_preview(self) -> None:
        target = RecordingTarget(revision="before")
        trace_writer = InMemoryTraceWriter()
        automation = WriteAutomation(
            {"anki": target, "obsidian": RecordingTarget()},
            trace_writer=trace_writer,
            gate_verifier=CurrentGateVerifier(),
        )
        preview = automation.prepare(self.request())
        target.revision = "after"

        outcome = automation.execute(preview, approved=True)

        self.assertEqual(outcome.state, "pending")
        self.assertIn("изменился после dry-run", outcome.next_action)
        self.assertEqual(target.writes, [])

    def test_unavailable_revision_blocks_ready_preview(self) -> None:
        target = RecordingTarget(revision=None)
        automation = WriteAutomation({"anki": target, "obsidian": RecordingTarget()})

        preview = automation.prepare(self.request())

        self.assertEqual(preview.state, "pending")
        self.assertTrue(any("revision" in blocker.lower() for blocker in preview.blockers))
        self.assertEqual(target.writes, [])

    def test_fresh_gate_verifier_blocks_write_when_source_check_changed_after_preview(self) -> None:
        target = RecordingTarget()
        verifier = CurrentGateVerifier()
        trace_writer = InMemoryTraceWriter()
        automation = WriteAutomation(
            {"anki": target, "obsidian": RecordingTarget()},
            trace_writer=trace_writer,
            gate_verifier=verifier,
        )
        preview = automation.prepare(self.request())
        verifier.verification = GateVerification(
            GateSnapshot(
                checker_passed=True, source_check_passed=False, duplicate_check_passed=True,
                decision_kind="card-promotion", decision_action="add", content_ready=True, trace_present=True,
            ),
            preview.request.duplicate_check_summary,
            preview.request.source_check_summary,
            preview.request.trace,
        )

        outcome = automation.execute(preview, approved=True)

        self.assertEqual(outcome.state, "pending")
        self.assertIn("Gates изменились", outcome.next_action)
        self.assertEqual(target.writes, [])

    def test_fresh_changed_duplicate_summary_requires_new_preview_and_approval(self) -> None:
        target = RecordingTarget()
        verifier = CurrentGateVerifier()
        automation = WriteAutomation(
            {"anki": target, "obsidian": RecordingTarget()},
            trace_writer=InMemoryTraceWriter(),
            gate_verifier=verifier,
        )
        preview = automation.prepare(self.request())
        verifier.verification = GateVerification(
            preview.request.gates,
            "Obsidian: available; Anki: available; strong duplicate: yes; action: merge.",
            preview.request.source_check_summary,
            preview.request.trace,
        )

        outcome = automation.execute(preview, approved=True)

        self.assertEqual(outcome.state, "pending")
        self.assertIn("summary", outcome.next_action)
        self.assertEqual(target.writes, [])

    def test_forged_or_changed_preview_cannot_bypass_gates(self) -> None:
        target = RecordingTarget()
        automation = WriteAutomation({"anki": target, "obsidian": RecordingTarget()}, trace_writer=InMemoryTraceWriter())
        preview = automation.prepare(self.request())
        forged = replace(preview, request=self.request(gates=GateSnapshot(
            checker_passed=False, source_check_passed=False, duplicate_check_passed=False,
            decision_kind="card-promotion", decision_action="add", content_ready=False, trace_present=False,
        )))

        with self.assertRaises(ValueError):
            automation.execute(forged, approved=True)

        self.assertEqual(target.writes, [])

    def test_missing_trace_writer_blocks_production_write(self) -> None:
        target = RecordingTarget()
        automation = WriteAutomation({"anki": target, "obsidian": RecordingTarget()})

        outcome = automation.execute(automation.prepare(self.request()), approved=True)

        self.assertEqual(outcome.state, "pending")
        self.assertEqual(target.writes, [])

    def test_replace_or_merge_requires_a_reason_in_preview(self) -> None:
        target = RecordingTarget()
        automation = WriteAutomation({"anki": target, "obsidian": RecordingTarget()})
        request = self.request(
            action="merge",
            gates=GateSnapshot(
                checker_passed=True, source_check_passed=True, duplicate_check_passed=True,
                decision_kind="card-promotion", decision_action="merge", content_ready=True, trace_present=True,
            ),
        )

        preview = automation.prepare(request)

        self.assertEqual(preview.state, "pending")
        self.assertTrue(any("reason" in blocker for blocker in preview.blockers))

    def test_external_success_and_trace_failure_is_visible_as_partial(self) -> None:
        target = RecordingTarget()
        automation = WriteAutomation(
            {"anki": target, "obsidian": RecordingTarget()},
            trace_writer=FailingTraceWriter(),
            gate_verifier=CurrentGateVerifier(),
        )

        outcome = automation.execute(automation.prepare(self.request()), approved=True)

        self.assertEqual(outcome.state, "partial")
        self.assertEqual(outcome.external_target_identity, "external-42")
        self.assertEqual(len(target.writes), 1)

    def test_external_failure_is_recorded_as_failed_without_claiming_success(self) -> None:
        target = RecordingTarget(write_error=ConnectionError("Anki отключён"))
        trace_writer = InMemoryTraceWriter()
        automation = WriteAutomation(
            {"anki": target, "obsidian": RecordingTarget()},
            trace_writer=trace_writer,
            gate_verifier=CurrentGateVerifier(),
        )

        outcome = automation.execute(automation.prepare(self.request()), approved=True)

        self.assertEqual(outcome.state, "failed")
        self.assertEqual(trace_writer.outcomes[-1].state, "failed")
        self.assertEqual(len(target.writes), 1)

    def test_markdown_trace_writer_updates_only_questions_or_knowledge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            questions = workspace / "Questions.md"
            knowledge = workspace / "Knowledge.md"
            goal = workspace / "Goal.md"
            questions.write_text("# Questions\n\n### Q-20260824-01 — Retry\n\n- Existing: yes\n", encoding="utf-8")
            knowledge.write_text("# Knowledge\n\n## Knowledge Consolidation Trace\n\n- Existing: yes\n", encoding="utf-8")
            goal.write_text("# Goal\n", encoding="utf-8")
            writer = MarkdownTraceWriter(workspace)
            automation = WriteAutomation(
                {"anki": RecordingTarget(), "obsidian": RecordingTarget()},
                trace_writer=writer,
                gate_verifier=CurrentGateVerifier(),
            )

            automation.execute(automation.prepare(self.request()), approved=True)

            self.assertIn("Write outcome — Q-20260824-01", questions.read_text(encoding="utf-8"))
            self.assertIn("Duplicate Check", questions.read_text(encoding="utf-8"))
            self.assertIn("Trace/evidence", questions.read_text(encoding="utf-8"))
            self.assertIn("Recovery plan", questions.read_text(encoding="utf-8"))
            self.assertEqual(
                knowledge.read_text(encoding="utf-8"), "# Knowledge\n\n## Knowledge Consolidation Trace\n\n- Existing: yes\n"
            )
            self.assertEqual(goal.read_text(encoding="utf-8"), "# Goal\n")

    def test_markdown_trace_writer_uses_knowledge_consolidation_trace_for_obsidian(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "Questions.md").write_text("# Questions\n", encoding="utf-8")
            knowledge = workspace / "Knowledge.md"
            knowledge.write_text("# Knowledge\n\n## Knowledge Consolidation Trace\n\n- Existing: yes\n", encoding="utf-8")
            request = self.request(
                target="obsidian",
                action="append",
                source_entity="Knowledge.md#b01---retry",
                target_description="Work/RabbitMQ.md#Retry",
                expected_markdown_updates="Knowledge.md: Obsidian write outcome.",
                gates=GateSnapshot(
                    checker_passed=True, source_check_passed=True, duplicate_check_passed=True,
                    decision_kind="knowledge-consolidation", decision_action="append",
                    content_ready=True, trace_present=True,
                ),
            )
            automation = WriteAutomation(
                {"anki": RecordingTarget(), "obsidian": RecordingTarget()},
                trace_writer=MarkdownTraceWriter(workspace),
                gate_verifier=CurrentGateVerifier(),
            )

            outcome = automation.execute(automation.prepare(request), approved=True)

            content = knowledge.read_text(encoding="utf-8")
            self.assertEqual(outcome.owner_artifact, "Knowledge.md")
            self.assertIn("Write outcome — Knowledge.md#b01---retry", content)
            self.assertIn("Source Check", content)


class ProductionWriteAdapterTests(unittest.TestCase):
    def request(self, **changes: object) -> WriteRequest:
        return write_request(**changes)

    def anki_transport(self, replies: dict[tuple[str, str], object] | None = None, *, error: Exception | None = None) -> FakeAnkiTransport:
        base_replies: dict[tuple[str, str], object] = {
            ("version", repr({})): 6,
            ("notesInfo", repr({"notes": [42]})): [
                {
                    "noteId": 42,
                    "mod": 123,
                    "modelName": "Basic",
                    "tags": ["rabbitmq"],
                    "fields": {"Front": {"value": "front"}},
                    "cards": [100, 101],
                }
            ],
            ("addNote", repr({
                "note": {
                    "deckName": "Kotlin Backend",
                    "modelName": "Basic",
                    "fields": {
                        "Front": "Почему retry без idempotency опасен?",
                        "Back": "Возможны повторные side effects.",
                    },
                    "tags": ["rabbitmq", "retry", "idempotency"],
                }
            })): 42,
            ("canAddNotesWithErrorDetail", repr({
                "notes": [
                    {
                        "deckName": "Kotlin Backend",
                        "modelName": "Basic",
                        "fields": {
                            "Front": "Почему retry без idempotency опасен?",
                            "Back": "Возможны повторные side effects.",
                        },
                        "tags": ["rabbitmq", "retry", "idempotency"],
                    }
                ]
            })): [{"canAdd": True}],
        }
        base_replies.update(replies or {})
        return FakeAnkiTransport(base_replies, error=error)

    def test_anki_availability_identity_and_revision_are_read_only(self) -> None:
        transport = self.anki_transport()
        adapter = AnkiConnectAdapter(transport=transport)

        self.assertTrue(adapter.is_available())
        self.assertTrue(adapter.exists("42"))
        self.assertEqual(adapter.preview_revision(self.request(existing_target_identity="42")), "note:42:123:100,101")
        self.assertEqual([call[0] for call in transport.calls], ["version", "notesInfo", "notesInfo"])

    def test_anki_rejects_ambiguous_note_identity_without_update(self) -> None:
        transport = self.anki_transport()
        adapter = AnkiConnectAdapter(transport=transport)

        self.assertFalse(adapter.exists("card:42"))
        with self.assertRaises(ExternalWriteError):
            adapter.write(self.request(
                action="replace",
                existing_target_identity="card:42",
                gates=GateSnapshot(True, True, True, "card-promotion", "replace", True, True),
                change_reason="Нужно обновить карточку.",
            ))

        self.assertNotIn("updateNote", [call[0] for call in transport.calls])

    def test_anki_multiline_field_content_is_not_truncated(self) -> None:
        proposed_content = "\n".join([
            "Front: Почему retry без idempotency опасен?",
            "Back: Короткий ответ.",
            "- Повторный delivery может создать второй side effect.",
            "- Consumer должен быть идемпотентным.",
        ])
        expected_fields = {
            "Front": "Почему retry без idempotency опасен?",
            "Back": "Короткий ответ.\n- Повторный delivery может создать второй side effect.\n- Consumer должен быть идемпотентным.",
        }
        transport = self.anki_transport({
            ("addNote", repr({
                "note": {
                    "deckName": "Kotlin Backend",
                    "modelName": "Basic",
                    "fields": expected_fields,
                    "tags": ["rabbitmq", "retry", "idempotency"],
                }
            })): 42,
        })
        adapter = AnkiConnectAdapter(transport=transport)

        result = adapter.write(self.request(proposed_content=proposed_content))

        self.assertEqual(result.anki_note_id, "42")
        self.assertIn(("addNote", {
            "note": {
                "deckName": "Kotlin Backend",
                "modelName": "Basic",
                "fields": expected_fields,
                "tags": ["rabbitmq", "retry", "idempotency"],
            }
        }), transport.calls)

    def test_anki_revision_without_mod_requires_reconciliation_preview(self) -> None:
        transport = self.anki_transport({
            ("notesInfo", repr({"notes": [42]})): [{"noteId": 42, "cards": [100]}],
        })
        adapter = AnkiConnectAdapter(transport=transport)

        self.assertIsNone(adapter.preview_revision(self.request(existing_target_identity="note:42")))

    def test_anki_add_runs_through_write_automation_execute_with_read_only_revision(self) -> None:
        transport = self.anki_transport()
        adapter = AnkiConnectAdapter(transport=transport)
        automation = WriteAutomation(
            {"anki": adapter},
            trace_writer=InMemoryTraceWriter(),
            gate_verifier=CurrentGateVerifier(),
        )

        preview = automation.prepare(self.request())
        outcome = automation.execute(preview, approved=True)

        self.assertEqual(preview.state, "ready-for-approval")
        self.assertEqual(outcome.state, "succeeded")
        self.assertEqual(outcome.anki_note_id, "42")
        self.assertIn("canAddNotesWithErrorDetail", [call[0] for call in transport.calls])
        self.assertIn("addNote", [call[0] for call in transport.calls])

    def test_anki_add_stale_read_only_revision_blocks_external_write(self) -> None:
        transport = self.anki_transport()
        adapter = AnkiConnectAdapter(transport=transport)
        automation = WriteAutomation(
            {"anki": adapter},
            trace_writer=InMemoryTraceWriter(),
            gate_verifier=CurrentGateVerifier(),
        )

        preview = automation.prepare(self.request())
        transport.replies[("canAddNotesWithErrorDetail", repr({
            "notes": [
                {
                    "deckName": "Kotlin Backend",
                    "modelName": "Basic",
                    "fields": {
                        "Front": "Почему retry без idempotency опасен?",
                        "Back": "Возможны повторные side effects.",
                    },
                    "tags": ["rabbitmq", "retry", "idempotency"],
                }
            ]
        }))] = [{"canAdd": False, "error": "cannot create note because it is a duplicate"}]

        outcome = automation.execute(preview, approved=True)

        self.assertEqual(outcome.state, "pending")
        self.assertIn("изменился после dry-run", outcome.next_action)
        self.assertNotIn("addNote", [call[0] for call in transport.calls])

    def test_anki_add_remote_validation_failure_stays_pending_without_write(self) -> None:
        transport = self.anki_transport({
            ("canAddNotesWithErrorDetail", repr({
                "notes": [
                    {
                        "deckName": "Kotlin Backend",
                        "modelName": "Basic",
                        "fields": {
                            "Front": "Почему retry без idempotency опасен?",
                            "Back": "Возможны повторные side effects.",
                        },
                        "tags": ["rabbitmq", "retry", "idempotency"],
                    }
                ]
            })): [{"canAdd": False, "error": "cannot create note because it is a duplicate"}],
        })
        adapter = AnkiConnectAdapter(transport=transport)
        automation = WriteAutomation({"anki": adapter}, trace_writer=InMemoryTraceWriter())

        preview = automation.prepare(self.request())

        self.assertEqual(preview.state, "pending")
        self.assertTrue(any("Revision" in blocker for blocker in preview.blockers))
        self.assertNotIn("addNote", [call[0] for call in transport.calls])

    def test_anki_add_returns_actual_note_and_card_ids_from_notes_info(self) -> None:
        transport = self.anki_transport()
        adapter = AnkiConnectAdapter(transport=transport)

        result = adapter.write(self.request())

        self.assertEqual(result, ExternalWriteResult("note:42", "42", ("100", "101")))

    def test_anki_does_not_invent_card_ids_when_notes_info_has_none(self) -> None:
        transport = self.anki_transport({
            ("notesInfo", repr({"notes": [42]})): [{"noteId": 42, "mod": 123, "cards": []}],
        })
        adapter = AnkiConnectAdapter(transport=transport)

        result = adapter.write(self.request())

        self.assertEqual(result.anki_note_id, "42")
        self.assertEqual(result.anki_card_ids, ())

    def test_anki_replace_updates_existing_note_and_returns_actual_ids(self) -> None:
        transport = self.anki_transport({
            ("updateNote", repr({
                "note": {
                    "id": 42,
                    "fields": {
                        "Front": "Почему retry без idempotency опасен?",
                        "Back": "Возможны повторные side effects.",
                    },
                    "tags": ["rabbitmq", "retry", "idempotency"],
                }
            })): None,
        })
        adapter = AnkiConnectAdapter(transport=transport)
        request = self.request(
            action="replace",
            existing_target_identity="note:42",
            gates=GateSnapshot(True, True, True, "card-promotion", "replace", True, True),
            change_reason="Старая карточка была слишком общей.",
        )

        result = adapter.write(request)

        self.assertEqual(result, ExternalWriteResult("note:42", "42", ("100", "101")))
        self.assertIn("updateNote", [call[0] for call in transport.calls])

    def test_anki_replace_runs_through_write_automation_execute(self) -> None:
        transport = self.anki_transport({
            ("updateNote", repr({
                "note": {
                    "id": 42,
                    "fields": {
                        "Front": "Почему retry без idempotency опасен?",
                        "Back": "Возможны повторные side effects.",
                    },
                    "tags": ["rabbitmq", "retry", "idempotency"],
                }
            })): None,
        })
        adapter = AnkiConnectAdapter(transport=transport)
        automation = WriteAutomation(
            {"anki": adapter},
            trace_writer=InMemoryTraceWriter(),
            gate_verifier=CurrentGateVerifier(),
        )
        request = self.request(
            action="replace",
            existing_target_identity="note:42",
            gates=GateSnapshot(True, True, True, "card-promotion", "replace", True, True),
            change_reason="Старая карточка была слишком общей.",
        )

        outcome = automation.execute(automation.prepare(request), approved=True)

        self.assertEqual(outcome.state, "succeeded")
        self.assertEqual(outcome.anki_note_id, "42")
        self.assertIn("updateNote", [call[0] for call in transport.calls])

    def test_anki_unavailable_protocol_failure_and_skip_do_not_write(self) -> None:
        unavailable = AnkiConnectAdapter(transport=FakeAnkiTransport(error=ConnectionError("Anki недоступен")))
        self.assertFalse(unavailable.is_available())

        protocol_failure = AnkiConnectAdapter(transport=FakeAnkiTransport({
            ("version", repr({})): {"unexpected": True},
        }))
        with self.assertRaises(ExternalWriteError):
            protocol_failure.write(self.request())

        transport = self.anki_transport()
        result = AnkiConnectAdapter(transport=transport).write(self.request(action="skip", gates=GateSnapshot(True, True, True, "card-promotion", "skip", True, True)))
        self.assertEqual(result.target_identity, "skip")
        self.assertNotIn("addNote", [call[0] for call in transport.calls])

    def test_obsidian_rejects_path_traversal_and_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            outside = Path(directory) / "outside"
            vault.mkdir()
            outside.mkdir()
            (outside / "escaped.md").write_text("outside", encoding="utf-8")
            (vault / "link.md").symlink_to(outside / "escaped.md")
            adapter = ObsidianFilesystemAdapter(vault)

            with self.assertRaises(ExternalWriteError):
                adapter.preview_revision(obsidian_request("append", obsidian_target_path="../outside/escaped.md"))
            with self.assertRaises(ExternalWriteError):
                adapter.preview_revision(obsidian_request("append", obsidian_target_path="link.md"))

    def test_obsidian_rejects_non_markdown_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            vault.mkdir()
            adapter = ObsidianFilesystemAdapter(vault)

            with self.assertRaises(ExternalWriteError):
                adapter.preview_revision(obsidian_request("append", obsidian_target_path="RabbitMQ.txt"))

    def test_obsidian_add_append_and_atomic_replacement_use_temporary_vault(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            vault.mkdir()
            adapter = ObsidianFilesystemAdapter(vault)
            add_request = obsidian_request("add", proposed_content="# RabbitMQ\n", obsidian_target_path="Work/RabbitMQ.md")

            add_result = adapter.write(add_request)
            append_result = adapter.write(obsidian_request("append", proposed_content="## Retry\nИдемпотентность нужна.\n", obsidian_target_path="Work/RabbitMQ.md"))
            replace_result = adapter.write(obsidian_request("replace-section", proposed_content="## Retry\nНовая формулировка.\n", obsidian_target_path="Work/RabbitMQ.md", obsidian_section="Retry", change_reason="Секция уточнена."))

            content = (vault / "Work" / "RabbitMQ.md").read_text(encoding="utf-8")
            self.assertEqual(add_result.target_identity, "Work/RabbitMQ.md")
            self.assertEqual(append_result.target_identity, "Work/RabbitMQ.md")
            self.assertEqual(replace_result.target_identity, "Work/RabbitMQ.md#Retry")
            self.assertIn("Новая формулировка.", content)
            self.assertNotIn("Идемпотентность нужна.", content)

    def test_obsidian_stale_revision_after_preview_blocks_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            vault.mkdir()
            note = vault / "RabbitMQ.md"
            note.write_text("# RabbitMQ\n", encoding="utf-8")
            adapter = ObsidianFilesystemAdapter(vault)
            trace_writer = InMemoryTraceWriter()
            request = obsidian_request("append", proposed_content="## Retry\nТекст.\n", obsidian_target_path="RabbitMQ.md")
            automation = WriteAutomation({"obsidian": adapter}, trace_writer=trace_writer, gate_verifier=CurrentGateVerifier())

            preview = automation.prepare(request)
            note.write_text("# RabbitMQ\n\nChanged outside preview.\n", encoding="utf-8")
            outcome = automation.execute(preview, approved=True)

            self.assertEqual(outcome.state, "pending")
            self.assertNotIn("Текст.", note.read_text(encoding="utf-8"))

    def test_obsidian_merge_appends_body_without_overwriting_existing_section(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            vault.mkdir()
            note = vault / "RabbitMQ.md"
            note.write_text("# RabbitMQ\n\n## Retry\nСтарый текст.\n", encoding="utf-8")
            adapter = ObsidianFilesystemAdapter(vault)

            result = adapter.write(obsidian_request(
                "merge",
                proposed_content="## Retry\nНовая деталь.\n",
                obsidian_target_path="RabbitMQ.md",
                obsidian_section="Retry",
                change_reason="Нужно объединить пересекающееся объяснение.",
            ))

            content = note.read_text(encoding="utf-8")
            self.assertEqual(result.target_identity, "RabbitMQ.md#Retry")
            self.assertIn("Старый текст.", content)
            self.assertIn("Новая деталь.", content)

    def test_obsidian_ambiguous_merge_returns_pending_without_overwriting_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "vault"
            vault.mkdir()
            note = vault / "RabbitMQ.md"
            original = "# RabbitMQ\n\n## Retry\nСтарый текст.\n"
            note.write_text(original, encoding="utf-8")
            adapter = ObsidianFilesystemAdapter(vault)
            automation = WriteAutomation(
                {"obsidian": adapter},
                trace_writer=InMemoryTraceWriter(),
                gate_verifier=CurrentGateVerifier(),
            )
            request = obsidian_request(
                "merge",
                proposed_content="Новый текст без heading.",
                obsidian_target_path="RabbitMQ.md",
                obsidian_section="Retry",
                change_reason="Нужно объединить пересекающееся объяснение.",
            )

            outcome = automation.execute(automation.prepare(request), approved=True)

            self.assertEqual(outcome.state, "pending")
            self.assertIn("reconciliation preview", outcome.next_action)
            self.assertEqual(note.read_text(encoding="utf-8"), original)

    def test_write_automation_blocks_production_adapters_without_approval_fresh_preview_or_gate(self) -> None:
        transport = self.anki_transport()
        adapter = AnkiConnectAdapter(transport=transport)
        rejected = WriteAutomation({"anki": adapter}, trace_writer=InMemoryTraceWriter())
        rejected_outcome = rejected.execute(rejected.prepare(self.request()), approved=False)

        blocked = WriteAutomation({"anki": adapter}, trace_writer=InMemoryTraceWriter())
        blocked_request = self.request(gates=GateSnapshot(False, True, True, "card-promotion", "add", True, True))
        blocked_outcome = blocked.execute(blocked.prepare(blocked_request), approved=True)

        self.assertEqual(rejected_outcome.state, "pending")
        self.assertEqual(blocked_outcome.state, "pending")
        self.assertNotIn("addNote", [call[0] for call in transport.calls])


if __name__ == "__main__":
    unittest.main()
