from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.check_topic_workspace import run_checker


REPO_ROOT = Path(__file__).resolve().parents[1]


class TopicWorkspaceCheckerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.workspace = self.root / "topics" / "rabbitmq" / "rabbitmq-retry-without-idempotency"
        shutil.copytree(
            REPO_ROOT / "topics" / "rabbitmq" / "retry-without-idempotency",
            self.workspace,
        )
        self.index = self.root / "topics" / "INDEX.md"
        self.index.parent.mkdir(parents=True, exist_ok=True)
        self.index.write_text(
            "| Learning Profile | Subject | Topic | Stable Slug | Topic State | Topic Workspace | Goal | Parent Topic | Related Subjects |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            "| profile | rabbitmq | retry | `rabbitmq-retry-without-idempotency` | `learning` | "
            "`topics/rabbitmq/rabbitmq-retry-without-idempotency` | [Goal.md](rabbitmq/rabbitmq-retry-without-idempotency/Goal.md) | - | - |\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def check(self):
        return run_checker(self.index, self.workspace)

    def test_accepts_the_repository_prototype(self) -> None:
        findings = run_checker(
            REPO_ROOT / "topics" / "INDEX.md",
            REPO_ROOT / "topics" / "rabbitmq" / "retry-without-idempotency",
        )

        self.assertFalse([finding for finding in findings if finding.severity == "error"])

    def test_reports_invalid_practice_id_as_a_blocking_error(self) -> None:
        practice = self.workspace / "Practice.md"
        practice.write_text(
            practice.read_text(encoding="utf-8").replace("PA-20260824-01", "PA-bad"),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.id == "invalid-id" and finding.severity == "error" for finding in findings))

    def test_reports_index_entity_without_a_detailed_record(self) -> None:
        practice = self.workspace / "Practice.md"
        practice.write_text(
            practice.read_text(encoding="utf-8").replace(
                "PA-20260824-01", "PA-20260824-99", 1
            ),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(
            any(
                finding.id == "missing-record" and finding.entity_or_reference == "PA-20260824-99"
                for finding in findings
            )
        )

    def test_reports_missing_markdown_target(self) -> None:
        knowledge = self.workspace / "Knowledge.md"
        knowledge.write_text(
            knowledge.read_text(encoding="utf-8").replace(
                "#b01---retry-mental-model", "#missing-target", 1
            ),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.id == "missing-target" for finding in findings))

    def test_reports_owner_violation_outside_goal(self) -> None:
        knowledge = self.workspace / "Knowledge.md"
        knowledge.write_text(
            knowledge.read_text(encoding="utf-8") + "\n- Состояние темы (Topic State): `completed`\n",
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.id == "owner-violation" for finding in findings))

    def test_keeps_topic_state_owner_field_exclusive_to_goal(self) -> None:
        for artifact in (
            "Knowledge.md",
            "Practice.md",
            "Questions.md",
            "Weaknesses.md",
            "RepetitionLog.md",
            "Sources.md",
        ):
            target = self.workspace / artifact
            target.write_text(
                target.read_text(encoding="utf-8") + "\n- Topic State: `completed`\n",
                encoding="utf-8",
            )

        findings = self.check()

        violating_files = {finding.file for finding in findings if finding.id == "owner-violation"}
        self.assertTrue(
            {
                "Knowledge.md",
                "Practice.md",
                "Questions.md",
                "Weaknesses.md",
                "RepetitionLog.md",
                "Sources.md",
            }.issubset(violating_files)
        )

    def test_needs_check_blocks_production_ready(self) -> None:
        goal = self.workspace / "Goal.md"
        goal.write_text(
            goal.read_text(encoding="utf-8").replace("`recognition` | `active`", "`production-ready` | `active`", 1),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.gate_impact == "blocks production-ready" for finding in findings))

    def test_english_source_result_field_still_blocks_production_ready(self) -> None:
        sources = self.workspace / "Sources.md"
        sources.write_text(
            sources.read_text(encoding="utf-8").replace(
                "Результат (Result): `needs-check`",
                "Source Check Result: `needs-check`",
            ),
            encoding="utf-8",
        )
        goal = self.workspace / "Goal.md"
        goal.write_text(
            goal.read_text(encoding="utf-8").replace("`recognition` | `active`", "`production-ready` | `active`", 1),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.gate_impact == "blocks production-ready" for finding in findings))

    def test_verified_source_result_is_accepted(self) -> None:
        sources = self.workspace / "Sources.md"
        sources.write_text(
            sources.read_text(encoding="utf-8").replace("`needs-check`", "`verified`"),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertFalse(
            any(finding.id == "invalid-value" and finding.file == "Sources.md" for finding in findings)
        )

    def test_rejected_source_blocks_completed_topic(self) -> None:
        sources = self.workspace / "Sources.md"
        sources.write_text(
            sources.read_text(encoding="utf-8").replace("`needs-check`", "`rejected`"),
            encoding="utf-8",
        )
        goal = self.workspace / "Goal.md"
        goal.write_text(
            goal.read_text(encoding="utf-8").replace("`learning`", "`completed`", 1),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.id == "unverified-source-gate" for finding in findings))

    def test_superseded_source_without_follow_up_is_reported(self) -> None:
        sources = self.workspace / "Sources.md"
        content = sources.read_text(encoding="utf-8").replace("`needs-check`", "`superseded`")
        content = content.replace(
            "#### Заметки (Notes)\n\nЭтот Source Record намеренно оставлен в `superseded`: prototype проверяет форму рабочего пространства, а не решает полный source verification workflow.",
            "#### Заметки (Notes)\n\n-",
        )
        content = content.replace(
            "Следующая проверка (Next Check): перед повышением B03 выше `recognition`",
            "Следующая проверка (Next Check): -",
        )
        sources.write_text(content, encoding="utf-8")

        findings = self.check()

        self.assertTrue(any(finding.id == "missing-superseded-followup" for finding in findings))

    def test_superseded_source_requires_replacement_or_next_check(self) -> None:
        sources = self.workspace / "Sources.md"
        content = sources.read_text(encoding="utf-8").replace("`needs-check`", "`superseded`")
        content = content.replace(
            "#### Заметки (Notes)\n\nЭтот Source Record намеренно оставлен в `superseded`: prototype проверяет форму рабочего пространства, а не решает полный source verification workflow.",
            "#### Заметки (Notes)\n\nСтарый источник больше не использовать.",
        )
        content = content.replace(
            "Следующая проверка (Next Check): перед повышением B03 выше `recognition`",
            "Следующая проверка (Next Check): -",
        )
        sources.write_text(content, encoding="utf-8")

        findings = self.check()

        self.assertTrue(any(finding.id == "missing-superseded-followup" for finding in findings))

    def test_superseded_source_cannot_name_itself_as_replacement(self) -> None:
        sources = self.workspace / "Sources.md"
        content = sources.read_text(encoding="utf-8").replace("`needs-check`", "`superseded`")
        content = content.replace(
            "#### Заметки (Notes)\n\nЭтот Source Record намеренно оставлен в `superseded`: prototype проверяет форму рабочего пространства, а не решает полный source verification workflow.",
            "#### Заметки (Notes)\n\nЗаменён [SRC-20260824-01](#src-20260824-01---rabbitmq-dead-letter-behavior).",
        )
        content = content.replace(
            "Следующая проверка (Next Check): перед повышением B03 выше `recognition`",
            "Следующая проверка (Next Check): -",
        )
        sources.write_text(content, encoding="utf-8")

        findings = self.check()

        self.assertTrue(any(finding.id == "missing-superseded-followup" for finding in findings))

    def test_superseded_source_cannot_support_production_ready(self) -> None:
        sources = self.workspace / "Sources.md"
        sources.write_text(
            sources.read_text(encoding="utf-8").replace("`needs-check`", "`superseded`"),
            encoding="utf-8",
        )
        goal = self.workspace / "Goal.md"
        goal.write_text(
            goal.read_text(encoding="utf-8").replace("`recognition` | `active`", "`production-ready` | `active`", 1),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.id == "unverified-source-gate" for finding in findings))

    def test_unlinked_needs_check_marker_blocks_completed_topic(self) -> None:
        goal = self.workspace / "Goal.md"
        goal.write_text(
            goal.read_text(encoding="utf-8").replace("`learning`", "`completed`", 1)
            + "\n- Sensitive claim: Нужно проверить.\n",
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.id == "unlinked-needs-check" and finding.gate_impact == "blocks completed" for finding in findings))

    def test_needs_check_marker_can_link_source_in_next_list_item(self) -> None:
        goal = self.workspace / "Goal.md"
        goal.write_text(
            goal.read_text(encoding="utf-8").replace("`learning`", "`completed`", 1)
            + "\n- Sensitive claim: Нужно проверить.\n- Source: [SRC-20260824-01](Sources.md#src-20260824-01---rabbitmq-dead-letter-behavior)\n",
            encoding="utf-8",
        )

        findings = self.check()

        self.assertFalse(any(finding.id == "unlinked-needs-check" for finding in findings))

    def test_needs_check_blocks_completed(self) -> None:
        goal = self.workspace / "Goal.md"
        goal.write_text(
            goal.read_text(encoding="utf-8").replace("`learning`", "`completed`", 1),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.gate_impact == "blocks completed" for finding in findings))

    def test_promoted_card_requires_trace_duplicate_checks_and_decision(self) -> None:
        questions = self.workspace / "Questions.md"
        content = questions.read_text(encoding="utf-8").replace("Статус (Status): `candidate`", "Статус (Status): `promoted`", 1)
        content = content.replace("Проверка дублей (Duplicate Check): Obsidian не проверен; Anki не проверен; promotion запрещен до duplicate checks.", "Проверка дублей (Duplicate Check): -")
        content = content.replace("След карточки (Card Trace): [Knowledge B01](Knowledge.md#b01---retry-mental-model), [B01: retry mental model](Goal.md#b01---retry-mental-model), [PA-20260824-01: retry safety sketch](Practice.md#pa-20260824-01---retry-safety-sketch)", "След карточки (Card Trace): -")
        questions.write_text(content, encoding="utf-8")

        findings = self.check()

        self.assertTrue(any(finding.gate_impact == "blocks card-promotion" for finding in findings))

    def test_needs_check_blocks_knowledge_consolidation(self) -> None:
        knowledge = self.workspace / "Knowledge.md"
        knowledge.write_text(
            knowledge.read_text(encoding="utf-8")
            + "\n## Knowledge Consolidation\n\n- Source: [SRC-20260824-01](Sources.md#src-20260824-01---rabbitmq-dead-letter-behavior)\n",
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.gate_impact == "blocks knowledge-consolidation" for finding in findings))

    def test_candidate_card_is_a_non_blocking_draft_orphan_warning(self) -> None:
        findings = self.check()

        self.assertTrue(
            any(
                finding.id == "card-promotion-gate"
                and finding.severity == "warning"
                and finding.gate_impact == "does not block"
                for finding in findings
            )
        )

    def test_cli_returns_nonzero_for_blocking_findings_and_prints_contract(self) -> None:
        practice = self.workspace / "Practice.md"
        practice.write_text(
            practice.read_text(encoding="utf-8").replace("PA-20260824-01", "PA-bad"),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "tools" / "check_topic_workspace.py"),
                "--index",
                str(self.index),
                "--workspace",
                str(self.workspace),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("[invalid-id] error; blocks handoff; файл:", result.stdout)

    def test_reports_invalid_accepted_value_in_practice_record(self) -> None:
        practice = self.workspace / "Practice.md"
        practice.write_text(
            practice.read_text(encoding="utf-8").replace("Результат (Result): `unchecked`", "Результат (Result): `unknown`"),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.id == "invalid-value" and finding.file == "Practice.md" for finding in findings))

    def test_reports_open_blocker_missing_from_goal_summary(self) -> None:
        weaknesses = self.workspace / "Weaknesses.md"
        weaknesses.write_text(
            weaknesses.read_text(encoding="utf-8").replace(
                "Evidence-backed Weakness Records пока отсутствуют.",
                """### W-20260824-01 - missing transaction boundary

- ID слабого места (Weakness ID): `W-20260824-01`
- Тип (Type): `gap`
- Серьезность (Severity): `blocker`
- Статус (Status): `open`
- Связанный блок (Linked Block): [B01: retry mental model](Goal.md#b01---retry-mental-model)

#### Evidence

- [PA-20260824-01: retry safety sketch](Practice.md#pa-20260824-01---retry-safety-sketch)

#### Repair Action и ретест (Retest)

- Repair Action: добавить разбор транзакционной границы
- Resolution Evidence: -""",
            ),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.id == "missing-active-weakness" for finding in findings))

    def test_reports_invalid_session_path_and_missing_archive_topic_link(self) -> None:
        sessions = self.workspace / "sessions"
        sessions.mkdir()
        (sessions / "notes.md").write_text("# Notes\n\n[B01](#b01---retry-mental-model)\n", encoding="utf-8")

        findings = self.check()

        self.assertTrue(any(finding.id == "invalid-session-path" for finding in findings))
        self.assertTrue(any(finding.id == "missing-archive-topic-link" for finding in findings))

    def test_reports_missing_companion_artifact(self) -> None:
        practice = self.workspace / "Practice.md"
        practice.write_text(
            practice.read_text(encoding="utf-8").replace("Артефакты (Artifacts): -", "Артефакты (Artifacts): [diagram](artifacts/retry.png)"),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.id == "missing-companion-artifact" for finding in findings))

    def test_reports_missing_parent_topic_for_any_index_row(self) -> None:
        self.index.write_text(
            self.index.read_text(encoding="utf-8").replace("| - | - |", "| unknown parent | - |"),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.id == "missing-parent-topic" for finding in findings))

    def test_warns_about_bare_id_in_significant_evidence_field_only(self) -> None:
        practice = self.workspace / "Practice.md"
        practice.write_text(
            practice.read_text(encoding="utf-8").replace(
                "- Связанный блок (Linked Block): [B01: retry mental model](Goal.md#b01---retry-mental-model)",
                "- Связанный блок (Linked Block): B01",
            ),
            encoding="utf-8",
        )

        findings = self.check()

        bare = [finding for finding in findings if finding.id == "bare-entity-reference"]
        self.assertEqual(len(bare), 1)
        self.assertEqual(bare[0].severity, "warning")
        self.assertEqual(bare[0].gate_impact, "does not block")
        self.assertIn("Markdown Entity Reference", bare[0].explanation)

    def test_accepts_markdown_entity_reference_in_significant_evidence_field(self) -> None:
        findings = self.check()

        self.assertFalse(any(finding.id == "bare-entity-reference" for finding in findings))

    def test_warns_about_bare_id_in_archive_evidence_field(self) -> None:
        sessions = self.workspace / "sessions"
        sessions.mkdir()
        (sessions / "2026-08-24-retry.md").write_text(
            "# Session\n\n- Topic: [Goal](../Goal.md)\n- Evidence: PA-20260824-01\n",
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(
            finding.id == "bare-entity-reference" and finding.file == "sessions/2026-08-24-retry.md"
            for finding in findings
        ))

    def test_warns_about_bare_id_in_significant_table_cell(self) -> None:
        questions = self.workspace / "Questions.md"
        questions.write_text(
            questions.read_text(encoding="utf-8").replace(
                "[B01: retry mental model](Goal.md#b01---retry-mental-model)", "B01", 1
            ),
            encoding="utf-8",
        )

        findings = self.check()

        self.assertTrue(any(finding.id == "bare-entity-reference" and finding.file == "Questions.md" for finding in findings))


if __name__ == "__main__":
    unittest.main()
