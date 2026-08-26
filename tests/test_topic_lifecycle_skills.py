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


class C4StructurizrDslDocumentationContractTests(unittest.TestCase):
    DOC = REPO_ROOT / "docs" / "agents" / "c4-structurizr-dsl.md"
    REQUIRED_HEADINGS = (
        "Когда использовать инструкцию",
        "Обязательный порядок работы",
        "Минимальный шаблон DSL",
        "Правила моделирования C4",
        "Идентификаторы и порядок объявления",
        "Relationships",
        "Выбор view",
        "Правила `include *`",
        "Dynamic view",
        "Стили и терминология",
        "Модульность",
        "Проверка результата",
        "Чеклист типичных ошибок",
    )
    REQUIRED_REFERENCE_HEADINGS = (
        "Полный справочник Structurizr DSL",
        "Лексические правила и структура файла",
        "Workspace, constants и переменные",
        "Идентификаторы и области видимости",
        "Model и типы элементов",
        "Общие свойства элементов",
    )

    def test_instruction_exists_and_has_required_sections(self) -> None:
        self.assertTrue(self.DOC.is_file())
        text = self.DOC.read_text(encoding="utf-8")
        for heading in self.REQUIRED_HEADINGS:
            with self.subTest(heading=heading):
                self.assertIn(f"## {heading}", text)
        for heading in self.REQUIRED_REFERENCE_HEADINGS:
            with self.subTest(heading=heading):
                self.assertIn(heading, text)

    def test_agent_pointer_is_specific_and_discoverable(self) -> None:
        text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("docs/agents/c4-structurizr-dsl.md", text)
        self.assertRegex(text, r"(?is)C4.*Structurizr DSL.*создани[яе].*изменени[яе].*диаграм")

    def test_instruction_keeps_critical_modeling_and_source_rules(self) -> None:
        text = self.DOC.read_text(encoding="utf-8")
        for anchor in (
            "structurizr-dsl-for-agents-research.md",
            "сначала модель, потом views",
            "стабильн",
            "forward reference",
            "static relationship",
            "`include *` зависит от типа view",
        ):
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, text)

    def test_instruction_defines_validation_gates_and_fallback(self) -> None:
        text = self.DOC.read_text(encoding="utf-8")
        for anchor in (
            "Structurizr CLI",
            "экспорт",
            "CLI недоступен",
            "синтаксической валидности",
        ):
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, text)

    def test_instruction_covers_issue_8_dsl_basics_and_sources(self) -> None:
        text = self.DOC.read_text(encoding="utf-8")
        for marker in (
            "workspace",
            "model",
            "configuration",
            "!const",
            "!var",
            "${NAME}",
            "!identifiers hierarchical",
            "this",
            "person",
            "softwareSystem",
            "container",
            "component",
            "custom element",
            "archetype",
            "group",
            "description",
            "technology",
            "tags",
            "url",
            "properties",
            "perspectives",
            "instances",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

        for source in (
            "https://docs.structurizr.com/dsl/basics",
            "https://docs.structurizr.com/dsl/language",
            "https://docs.structurizr.com/dsl/identifiers",
            "https://docs.structurizr.com/dsl/archetypes",
            "structurizr-dsl-for-agents-research.md",
        ):
            with self.subTest(source=source):
                self.assertIn(source, text)


if __name__ == "__main__":
    unittest.main()
