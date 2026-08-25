# Сессия F: поддержка проверки источников

## Назначение запуска

Отдельный агент выполняет тикет `07-source-verification-support.md`. Он
создает управляемый workflow для Source Records и Source Check Result, не
подменяя непроверенный claim правдоподобным текстом.

Рабочая директория: `/home/doduohor/learning/agentic-learning-workflow`.

## Предпосылки и skills

Требуются результаты A, B и C: templates, общий контракт, checker и Agent
Files. Используй `$implement`; применяй `$tdd` к исполняемой логике, если она
нужна; используй `verification-before-completion` и `$code-review`.

## Обязательное чтение до изменений

1. `AGENTS.md`, `CONTEXT.md`, `docs/wayfinder/00-map.md`,
   `docs/learning-system-spec.md` и тикет 07.
2. `docs/learning-system/templates/Sources.md` и общий контракт агентов.
3. Реализация Checker и роль `source` из сессий B/C.
4. Decisions 03, 05, 09, 11 и 12 в `docs/wayfinder/decisions/`.

## Результат сессии

Сделай практический Source Verification workflow, совместимый с `Sources.md`:
как создать/обновить Source Record, классифицировать результат `verified`,
`rejected`, `needs-check`, `superseded`, связать claim и evidence, назначить
gate impact и подготовить Agent Proposal для Knowledge, Questions или Goal.

Если нужна автоматизация, она должна быть узким инструментом Learning
Orchestrator, сохранять human-first Markdown и работать с Source Records, а не
создавать новую machine-readable schema. Недоступность источника фиксируй как
`needs-check`/`Нужно проверить`; не подтверждай claim по памяти и не выполняй
реальную проверку RabbitMQ prototype без отдельного поручения.

`Sources.md` остается единственным владельцем Source Check Result. Только
Learning Orchestrator применяет state-changing edits в Goal/Knowledge/Questions;
Source Agent предлагает изменения через Agent Proposal или разрешенную
append-only границу.

## Границы и проверка

Разрешены workflow-документы, узкая Orchestrator-controlled поддержка при
необходимости, tests, тикет 07 и минимальные обновления общего контракта.
Запрещены реальная внешняя Source Verification, Obsidian/Anki write,
YAML/JSON schema и изменение prototype.

Проверь `verified`, `rejected`, `needs-check`, `superseded`, недоступный
источник и gate-blocking scenario. Подтверди, что `needs-check` блокирует
`production-ready`, `completed`, Card Promotion и Knowledge Consolidation,
когда claim нужен для gate. После `$code-review` повтори проверки и закоммить.

В финальной передаче укажи новые contracts, результаты tests/проверок и ревью,
хеш коммита и закрытые criteria. Следующая зависимая сессия — G.
