from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / ".agents" / "skills"
SKILL_NAMES = ("learn-start", "learn-continue", "learn-report")
FORBIDDEN_SCOPE = (
    "Card Promotion",
    "Knowledge Consolidation",
    "Obsidian write",
    "Anki write",
    "personal installation",
    "plugin packaging",
)


def read_skill(name: str) -> str:
    return (SKILLS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip().strip('"')
    return fields


class TopicLifecycleSkillContractTests(unittest.TestCase):
    def test_repo_scoped_skill_files_exist_with_required_frontmatter(self) -> None:
        for name in SKILL_NAMES:
            with self.subTest(skill=name):
                skill_file = SKILLS_ROOT / name / "SKILL.md"

                self.assertTrue(skill_file.is_file(), f"missing {skill_file}")
                fields = frontmatter(skill_file.read_text(encoding="utf-8"))
                self.assertEqual(fields.get("name"), name)
                self.assertTrue(fields.get("description"))

    def test_learn_start_requires_preview_and_existing_intake_utility(self) -> None:
        text = read_skill("learn-start")

        self.assertIn("preview", text)
        self.assertIn("подтверждение пользователя", text)
        self.assertLess(text.index("preview"), text.index("tools/start_topic_intake.py"))
        self.assertIn("tools/start_topic_intake.py", text)
        self.assertIn("не копирует templates вручную", text)
        self.assertIn("Topic State", text)
        self.assertIn("`intake`", text)
        self.assertIn("первый диагностический вопрос", text)

    def test_learn_continue_requires_proposed_changes_before_state_changing_edits(self) -> None:
        text = read_skill("learn-continue")

        self.assertIn("Goal.md", text)
        self.assertIn("Next Actions", text)
        self.assertIn("tools/check_topic_workspace.py", text)
        self.assertIn("blocker Weaknesses", text)
        self.assertIn("pending Source Checks", text)
        self.assertIn("active/missed repetitions", text)
        self.assertIn("proposed changes", text)
        self.assertIn("подтверждение пользователя", text)
        self.assertLess(text.index("proposed changes"), text.index("state-changing edits"))
        self.assertIn("один ограниченный мини-цикл Active Block", text)

    def test_learn_report_is_read_only_and_russian(self) -> None:
        text = read_skill("learn-report")

        self.assertIn("read-only", text)
        self.assertIn("не изменяет файлы", text)
        self.assertIn("отвечай на русском", text.lower())
        self.assertIn("topics/INDEX.md", text)
        self.assertIn("Goal.md", text)
        self.assertIn("tools/check_topic_workspace.py", text)
        self.assertIn("Topic State", text)
        self.assertIn("Active Block", text)
        self.assertIn("Next Actions", text)

    def test_skills_keep_forbidden_workflows_out_of_scope(self) -> None:
        for name in SKILL_NAMES:
            text = read_skill(name)
            with self.subTest(skill=name):
                for phrase in FORBIDDEN_SCOPE:
                    self.assertIn(phrase, text)
                self.assertRegex(text, r"(?is)вне области.*Card Promotion")
                self.assertRegex(text, r"(?is)вне области.*Knowledge Consolidation")

    def test_skills_link_to_authoritative_project_docs(self) -> None:
        for name in SKILL_NAMES:
            text = read_skill(name)
            with self.subTest(skill=name):
                self.assertIn("CONTEXT.md", text)
                self.assertIn("docs/wayfinder/00-map.md", text)
                self.assertIn("docs/learning-system/topic-lifecycle-skills.md", text)
                self.assertIn("docs/learning-system/lifecycle-command-interface.md", text)
                self.assertIn("docs/learning-system/agent-common-instructions.md", text)
                self.assertIn("docs/learning-system/session-handoff-workflow.md", text)
                self.assertIn("docs/learning-system/templates/README.md", text)
                self.assertIn("docs/wayfinder/decisions/13-design-topic-lifecycle-skills.md", text)


if __name__ == "__main__":
    unittest.main()
