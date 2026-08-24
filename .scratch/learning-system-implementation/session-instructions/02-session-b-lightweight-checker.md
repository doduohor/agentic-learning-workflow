# Сессия B: легковесная проверка Topic Workspace

## Назначение запуска

Передай эту инструкцию одному отдельному агенту для выполнения тикета
`02-lightweight-checker.md`. Результат — read-only Lightweight Checker для
Topic Index и одной Topic Workspace с понятным отчетом о структурных и
gate-blocking ошибках.

Рабочая директория:
`/home/doduohor/learning/agentic-learning-workflow`.

## Обязательные skills

1. Используй `$implement`.
2. Используй `$tdd` для логики разбора, валидации и классификации findings.
3. Перед финальным утверждением используй `verification-before-completion`.
4. После реализации используй `$code-review` и устрани релевантные замечания.

## Обязательное чтение до изменений

1. `AGENTS.md`, `docs/wayfinder/00-map.md`, `CONTEXT.md` и
   `docs/learning-system-spec.md`.
2. `.scratch/learning-system-implementation/issues/02-lightweight-checker.md`.
3. `docs/wayfinder/decisions/02-design-learning-artifact-templates.md` —
   форматы Markdown, ID и entity references.
4. `docs/wayfinder/decisions/08-design-topic-workspace-index-and-path.md`.
5. `docs/wayfinder/decisions/09-design-source-verification-workflow.md`.
6. `docs/wayfinder/decisions/11-design-lightweight-checker-for-entity-references-and-ids.md`.
7. Prototype: `topics/INDEX.md` и все основные файлы
   `topics/rabbitmq/retry-without-idempotency/`.

Сначала проверь Git-ветку и чисто отдели собственные изменения от уже
существующих. Не изменяй prototype для создания искусственных ошибок: используй
изолированные тестовые fixtures.

## Результат сессии

Реализуй CLI-утилиту и тесты в обычных для репозитория путях. Если паттерна еще
нет, используй Python standard library, `tools/check_topic_workspace.py` и
`tests/test_check_topic_workspace.py`. CLI принимает Topic Index и путь одной
Topic Workspace, возвращает человекочитаемый отчет и ненулевой код при
blocking findings. Формат отчета должен содержать finding ID, severity, gate
impact, файл, entity/reference и объяснение исправления.

Проверяй как минимум:

- наличие и допустимые ID, Entity References и targets;
- owner invariants всех семи основных артефактов;
- stale/missing links и Draft Orphans;
- `needs-check`, использованный как evidence для `production-ready`,
  `completed`, Card Promotion или Knowledge Consolidation;
- Card Candidate со статусом `promoted` без Card Trace, Duplicate Check,
  Promotion Decision или Source Check gates;
- gate impact: `blocks production-ready`, `blocks completed`,
  `blocks card-promotion`, `blocks knowledge-consolidation`, `blocks handoff`
  либо `does not block`.

## Жесткие границы

- Checker только читает: он не исправляет Markdown, не обновляет индекс, не
  пишет в Obsidian или Anki и не выполняет Source Verification.
- Human-first Markdown остается источником данных; не вводи YAML/JSON
  machine-readable schema, базу данных или скрытый state file.
- Не меняй owner model и не создавай новые Topic Workspaces.
- Разрешены файлы checker, тесты, краткая документация запуска и отметки в
  тикете 02; `CONTEXT.md` меняй только для действительно нового устойчивого
  термина.

## Порядок работы

1. Зафиксируй поведение CLI и коды завершения до реализации.
2. Напиши fixtures и failing tests для каждого класса blocking finding и для
   корректного prototype.
3. Реализуй минимальный разбор human-first Markdown без требования строгой
   машинной схемы.
4. Запускай отдельные тесты после каждого логического шага, затем весь набор.
5. Проверь CLI на prototype в read-only режиме.
6. Выполни `$code-review`, исправь замечания, повтори проверки и закоммить.

## Проверка

Выполни все созданные тесты, затем как минимум:

```sh
python3 tools/check_topic_workspace.py --index topics/INDEX.md \
  --workspace topics/rabbitmq/retry-without-idempotency
git diff --check
git status --short
```

Подтверди, что запуск checker не изменил ни один файл. В финальной передаче
укажи CLI contract, результаты tests/prototype run, результат `$code-review`,
хеш коммита и закрытые acceptance criteria тикета 02. После успеха доступны
сессия D при уже завершенной сессии A. Сессия C зависит только от результата
сессии A.
