# Сессия D: интерфейс учебных команд и handoff

## Назначение запуска

Отдельный агент выполняет два связанных тикета:

- `05-lifecycle-command-interface.md`;
- `10-handoff-support.md`.

Результат — рабочее описание интерфейса lifecycle commands и handoff, которое
будущие команды и агенты смогут применять без потери владельцев состояния.
Рабочая директория: `/home/doduohor/learning/agentic-learning-workflow`.

## Предпосылки

Требуются завершенные сессии A и B: шаблоны, общий контракт и read-only
Lightweight Checker. Если любой из результатов отсутствует, остановись и
укажи блокер.

## Обязательные skills

1. Используй `$implement`, `writing-for-agents` и
   `verification-before-completion`.
2. `$tdd` здесь неприменим: ticket проектирует интерфейс и handoff, не
   исполняемые slash commands.
3. После работы используй `$code-review` и закоммить результат.

## Обязательное чтение до изменений

1. `AGENTS.md`, `docs/wayfinder/00-map.md`, `CONTEXT.md`,
   `docs/learning-system-spec.md`.
2. Тикеты 05 и 10 в `.scratch/learning-system-implementation/issues/`.
3. `docs/learning-system/templates/` и
   `docs/learning-system/agent-common-instructions.md`.
4. Decisions 03, 04, 07, 08, 09, 10 и 11 в `docs/wayfinder/decisions/`.

## Результат сессии

Создай:

```text
docs/learning-system/lifecycle-command-interface.md
docs/learning-system/session-handoff-workflow.md
```

Первый документ задает для `start/intake`, `diagnose`, `plan`, `learn-block`,
`practice`, `review`, `repeat`, `pause`, `resume`, `complete`: входные условия,
обязательный читаемый контекст, допустимые действия Learning Orchestrator,
gates, stop conditions и изменяемые owner artifacts. Не создавай реальные slash
commands.

Второй документ различает Wayfinder Handoff и Topic Workspace Handoff. Он
описывает минимальный набор читаемых owner artifacts, next safe action, Role
Mode, Agent Write Boundary, pending Source Checks, Card Candidates, Active
Repetitions и open Weaknesses. Optional `Handoff.md` допустим только при риске
потери контекста и не становится source of truth.

`pause`/`resume` должны сохранять следующий безопасный шаг, а `complete` —
блокироваться при open blocker Weakness, отсутствующем Completion Evidence или
gate-blocking `needs-check`. Команды не обходят Checker, Source Check, Duplicate
Check, Card Promotion или Knowledge Consolidation.

## Границы и проверка

Разрешены только два документа, отметки в тикетах и минимальные ссылки из
общего контракта. Не создавай slash commands, `Handoff.md` в prototype, новые
темы, внешние записи или YAML/JSON schema.

Проверь наличие всех десяти команд, обоих видов handoff, owner files, gates и
stop conditions через `rg`; проверь ссылки на существующие файлы; выполни
`git diff --check`, `$code-review`, повторную проверку и коммит.

В финальной передаче перечисли документы, результаты проверок и ревью, хеш
коммита, закрытые criteria тикетов 05 и 10. Следующая зависимая сессия — E.
