# Сессия C: файлы Codex-агентов

## Назначение запуска

Передай эту инструкцию отдельному агенту для тикета `04-codex-agent-files.md`.
Сессия создает реальные Codex Agent Files, которые применяют общий контракт из
сессии A и не обходят single-writer state model.

Рабочая директория:
`/home/doduohor/learning/agentic-learning-workflow`.

## Предпосылки

До работы убедись, что сессия A завершена и существуют:

```text
docs/learning-system/agent-common-instructions.md
docs/learning-system/templates/Goal.md
```

Если их нет или acceptance criteria тикетов 01/03 не закрыты, остановись и
сообщи блокер; не создавай временную замену общего контракта.

## Обязательные skills

1. Используй `$implement`.
2. Используй `openai-docs`, чтобы проверить актуальную схему Codex custom
   agent files перед созданием TOML.
3. Используй `writing-for-agents` для инструкций, которые будут читать роли.
4. Используй `$tdd` только если для проверки появится собственный исполняемый
   валидатор; TOML проверяй доступным parser'ом.
5. Перед завершением используй `verification-before-completion`, затем
   `$code-review`.

## Обязательное чтение до изменений

1. `AGENTS.md`, `docs/wayfinder/00-map.md`, `CONTEXT.md`,
   `docs/learning-system-spec.md`.
2. `.scratch/learning-system-implementation/issues/04-codex-agent-files.md`.
3. `docs/learning-system/agent-common-instructions.md`.
4. `docs/wayfinder/decisions/03-design-codex-agent-roles.md`.
5. `docs/wayfinder/decisions/06-design-codex-agent-files.md`.
6. `docs/wayfinder/decisions/07-design-codex-session-handoff.md`.
7. `docs/wayfinder/decisions/09-design-source-verification-workflow.md` и
   `12-design-obsidian-and-anki-write-automation.md`.

## Результат сессии

После проверки актуальной схемы создай шесть Agent Files в `.codex/agents/`:

```text
learning-orchestrator.toml
learning-support.toml
practice.toml
question-card.toml
source.toml
repetition.toml
```

Названия и поля можно скорректировать только если актуальная документация Codex
требует другую схему; зафиксируй такую коррекцию в финальном отчете.

Каждый файл обязан задавать Role Mode, узкую область чтения, разрешенную запись
и формат результата. `learning-orchestrator` — единственный автор Topic State,
Active Block, Block Status, Mastery Level, Completion Criteria, Card Promotion
и Knowledge Consolidation decisions. Остальные роли возвращают Agent Proposal
либо используют только явно разрешенную append-only границу.

Supporting agents не получают права прямо менять `Goal.md`, `Knowledge.md` или
`Weaknesses.md`, не пишут в Obsidian/Anki и ссылаются на общий контракт вместо
дублирования всей спецификации.

## Границы сессии

Разрешены `.codex/agents/*.toml`, при необходимости краткий README рядом с
ними, тикет 04 и корректировка общего контракта только при обнаруженной
неустранимой неоднозначности. Не создавай новые Topic Workspaces, slash
commands, checker, Anki cards, Obsidian notes или automation scripts.

## Проверка

1. Проверь TOML parser'ом все шесть файлов.
2. Сверь каждый файл с current Codex schema и общим контрактом.
3. Поиском подтверди наличие Role Mode, Agent Proposal, Agent Write Boundary,
   Source Check, Duplicate Check, Card Promotion и запрета прямой внешней
   записи там, где это относится к роли.
4. Выполни `$code-review`, исправь замечания, повтори проверки и закоммить.

Финальная передача: список Agent Files, источник проверки схемы, результаты
парсинга и ревью, хеш коммита, закрытые acceptance criteria. Следующая
зависимая сессия — D; сессия F также зависит от этого результата.
