from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import shutil

from tools.start_topic_intake import IntakeRequest, IntakeValidationError, create_topic_workspace


REPO_ROOT = Path(__file__).resolve().parents[1]


class TopicIntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "topics").mkdir()
        (self.root / "topics" / "INDEX.md").write_text(
            "# Topic Index\n\n"
            "## Topics\n\n"
            "| Learning Profile | Subject | Topic | Stable Slug | Topic State | Topic Workspace | Goal | Parent Topic | Related Subjects |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            "| Junior+/Middle Kotlin Backend для ЦУП РТ / АИС МИДИО | RabbitMQ | retry без идемпотентности | `rabbitmq-retry-without-idempotency` | `learning` | "
            "`topics/rabbitmq/retry-without-idempotency` | [Goal.md](rabbitmq/retry-without-idempotency/Goal.md) | - | reliability, Postgres |\n"
            "\n## Topic Tree\n\n"
            "Связи Parent Topic показываются здесь, когда они появляются.\n\n"
            "- -\n",
            encoding="utf-8",
        )
        shutil.copytree(
            REPO_ROOT / "topics" / "rabbitmq" / "retry-without-idempotency",
            self.root / "topics" / "rabbitmq" / "retry-without-idempotency",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def request(self, **changes: str) -> IntakeRequest:
        values = {
            "subject": "Postgres",
            "topic": "изоляция транзакций",
            "stable_slug": "postgres-transaction-isolation",
            "learning_profile": "Junior+/Middle Kotlin Backend",
            "draft_goal": "Понять, как выбирать уровень изоляции для прикладной транзакции.",
        }
        values.update(changes)
        return IntakeRequest(**values)

    def test_creates_a_checked_intake_workspace_from_templates(self) -> None:
        result = create_topic_workspace(self.root, self.request(), templates_dir=REPO_ROOT / "docs/learning-system/templates")

        self.assertEqual(result.workspace, self.root / "topics/postgres/postgres-transaction-isolation")
        self.assertFalse(result.findings)
        self.assertEqual((result.workspace / "Goal.md").read_text(encoding="utf-8").count("`intake`"), 1)
        self.assertIn("изоляция транзакций", (result.workspace / "Goal.md").read_text(encoding="utf-8"))
        self.assertIn("[Goal.md](postgres/postgres-transaction-isolation/Goal.md)", (self.root / "topics/INDEX.md").read_text(encoding="utf-8"))
        self.assertNotIn("Активный блок", (self.root / "topics/INDEX.md").read_text(encoding="utf-8"))
        self.assertEqual({path.name for path in result.workspace.iterdir()}, {
            "Goal.md", "Knowledge.md", "Practice.md", "Questions.md", "Weaknesses.md", "RepetitionLog.md", "Sources.md",
        })

    def test_appends_index_row_to_topics_table_before_topic_tree(self) -> None:
        result = create_topic_workspace(self.root, self.request(), templates_dir=REPO_ROOT / "docs/learning-system/templates")

        index_text = (self.root / "topics/INDEX.md").read_text(encoding="utf-8")
        row = "| Junior+/Middle Kotlin Backend | Postgres | изоляция транзакций | `postgres-transaction-isolation` | `intake` | "
        self.assertLess(index_text.index(row), index_text.index("## Topic Tree"))
        self.assertEqual(result.workspace, self.root / "topics/postgres/postgres-transaction-isolation")

    def test_rejects_a_conflicting_workspace_without_writing(self) -> None:
        target = self.root / "topics/postgres/postgres-transaction-isolation"
        target.mkdir(parents=True)

        with self.assertRaises(IntakeValidationError):
            create_topic_workspace(self.root, self.request(), templates_dir=REPO_ROOT / "docs/learning-system/templates")

        self.assertEqual(list(target.iterdir()), [])
        self.assertNotIn("postgres-transaction-isolation", (self.root / "topics/INDEX.md").read_text(encoding="utf-8"))

    def test_rejects_an_invalid_slug_without_writing(self) -> None:
        with self.assertRaises(IntakeValidationError):
            create_topic_workspace(self.root, self.request(stable_slug="Postgres Isolation"), templates_dir=REPO_ROOT / "docs/learning-system/templates")

        self.assertFalse((self.root / "topics/postgres").exists())
        self.assertNotIn("Postgres Isolation", (self.root / "topics/INDEX.md").read_text(encoding="utf-8"))

    def test_accepts_backslashes_in_a_draft_goal(self) -> None:
        result = create_topic_workspace(
            self.root,
            self.request(draft_goal=r"Разобрать путь C:\\tmp\\1 как пример."),
            templates_dir=REPO_ROOT / "docs/learning-system/templates",
        )

        self.assertIn(r"C:\\tmp\\1", (result.workspace / "Goal.md").read_text(encoding="utf-8"))

    def test_rejects_markdown_table_delimiters_without_writing(self) -> None:
        with self.assertRaises(IntakeValidationError):
            create_topic_workspace(self.root, self.request(topic="изоляция | транзакций"), templates_dir=REPO_ROOT / "docs/learning-system/templates")

        self.assertFalse((self.root / "topics/postgres").exists())
        self.assertNotIn("изоляция | транзакций", (self.root / "topics/INDEX.md").read_text(encoding="utf-8"))

    def test_rolls_back_all_writes_when_checker_rejects_the_workspace(self) -> None:
        templates = self.root / "templates"
        templates.mkdir()
        for source in (REPO_ROOT / "docs/learning-system/templates").glob("*.md"):
            (templates / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        (templates / "Knowledge.md").write_text("[broken](Missing.md)\n", encoding="utf-8")

        with self.assertRaises(IntakeValidationError):
            create_topic_workspace(self.root, self.request(), templates_dir=templates)

        self.assertFalse((self.root / "topics/postgres").exists())
        self.assertNotIn("postgres-transaction-isolation", (self.root / "topics/INDEX.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
