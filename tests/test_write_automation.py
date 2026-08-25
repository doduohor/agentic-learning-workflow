from __future__ import annotations

import unittest
import tempfile
from dataclasses import replace
from pathlib import Path

from tools.write_automation import (
    GateSnapshot,
    GateVerification,
    ExternalWriteResult,
    InMemoryTraceWriter,
    MarkdownTraceWriter,
    WriteAutomation,
    WriteRequest,
)


class RecordingTarget:
    def __init__(
        self,
        *,
        available: bool = True,
        existing: bool = False,
        revision: str | None = None,
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


class WriteAutomationTests(unittest.TestCase):
    def request(self, **changes: object) -> WriteRequest:
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


if __name__ == "__main__":
    unittest.main()
