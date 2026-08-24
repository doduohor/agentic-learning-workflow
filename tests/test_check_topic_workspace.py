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
        self.workspace = self.root / "topics" / "rabbitmq" / "retry"
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
            "`topics/rabbitmq/retry` | [Goal.md](rabbitmq/retry/Goal.md) | - | - |\n",
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


if __name__ == "__main__":
    unittest.main()
