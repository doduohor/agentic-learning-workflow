# Сессия I: итоговое ревью реализации учебной системы

## Назначение запуска

Отдельный агент проводит итоговое read-only ревью реализации тикетов 01–10,
созданной в сессиях A–H. Цель — дать проверяемый отчёт о соответствии
спецификации, инвариантам и документированным стандартам. Это аудит, а не
сессия исправлений: findings передаются пользователю отдельным последующим
запуском.

Рабочая директория:
`/home/doduohor/learning/agentic-learning-workflow`.

## Предпосылки

Перед началом убедись, что:

1. текущая ветка — `learning-system-implementation`;
2. `main` разрешается как Git ref и является фиксированной точкой ревью;
3. `git diff main...HEAD` не пуст;
4. рабочее дерево чисто, кроме `.agent-reports/`, которая локальна и игнорируется.

Если одна из предпосылок не выполнена, не начинай ревью: запиши блокер в отчёт.

## Обязательные skills

1. Сначала обнаружь доступные skills через
   `rg --files /mnt/c/Users/Sergey/.codex/skills | rg 'SKILL\.md$'` и прочитай
   полный `SKILL.md` для каждого применимого или явно названного skill.
2. Используй `$code-review` по точному пути
   `/mnt/c/Users/Sergey/.codex/skills/code-review/SKILL.md`. Fixed point:
   `main`; diff command: `git diff main...HEAD`.
3. Используй `verification-before-completion` перед финальным утверждением.
4. Не используй `$implement` или `$tdd`: эта сессия не меняет реализацию и не
   добавляет исполняемый код.

`docs/agents/issue-tracker.md` не требуется: источники спецификации явно
перечислены ниже. Если `$code-review` упоминает отсутствие issue tracker,
отрази это как ограничение маршрута, но продолжи Spec axis по указанным файлам.

## Обязательное чтение

Прочитай в этом порядке:

1. `AGENTS.md`, `docs/wayfinder/00-map.md`, `CONTEXT.md` и
   `docs/learning-system-spec.md`;
2. все тикеты `01`–`10` в `.scratch/learning-system-implementation/issues/`;
3. все instructions сессий A–H в
   `.scratch/learning-system-implementation/session-instructions/`;
4. все decisions `01`–`12` в `docs/wayfinder/decisions/`;
5. итоговые артефакты: `docs/learning-system/`, `.codex/agents/`, `tools/`,
   `tests/`, `topics/INDEX.md` и prototype Topic Workspace.

## Границы аудита

- Не меняй tracked files, тикеты, prototype, Obsidian vault, Anki или внешние
  системы.
- Не создавай коммит, новую тему, fixture в постоянной папке `topics/`,
  YAML/JSON schema или automation side effect.
- Разрешено создать только игнорируемый отчёт
  `.agent-reports/session-i-final-review.md`.
- Тесты запускай с `PYTHONDONTWRITEBYTECODE=1`; после каждого запуска сверяй,
  что ревью не изменило рабочее дерево.

## План ревью

### 1. Фиксация сравнения

Выполни и зафиксируй в отчёте:

```sh
git rev-parse main
git log main..HEAD --oneline
git diff --stat main...HEAD
git diff main...HEAD
```

Укажи число коммитов и затронутые подсистемы. Не включай полный diff в отчёт.

### 2. Проверка полноты реализации

Составь traceability matrix «тикет → созданные/изменённые файлы → acceptance
criteria → evidence проверки» для тикетов 01–10. Отдельно проверь:

- seven Topic Workspace templates и owner model;
- общий контракт и шесть `.codex/agents/*.toml`;
- Lightweight Checker, intake, Source Verification, Duplicate Check и Write
  Automation;
- lifecycle command interface и два вида handoff;
- source, duplicate и write gates: `needs-check`, Card Promotion, Knowledge
  Consolidation, dry-run, user approval, unavailable/pending, idempotency;
- human-first Markdown, отсутствие YAML/JSON machine-readable schema и
  отсутствие реальных изменений prototype/Obsidian/Anki.

Не засчитывай отмеченный checkbox без соответствующего артефакта и проверяемого
evidence.

### 3. Запуск объединённых проверок

Выполни минимум:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -c "import pathlib, tomllib; files = sorted(pathlib.Path('.codex/agents').glob('*.toml')); [tomllib.loads(path.read_text()) for path in files]; print(f'TOML parsed: {len(files)}/{len(files)}')"
python3 tools/check_topic_workspace.py --index topics/INDEX.md --workspace topics/rabbitmq/retry-without-idempotency
git diff --check main...HEAD
git status --short
```

Проверь ключевые CLI contract через `--help` и test doubles; не запускай
production write path и не подтверждай никакой dry-run preview от имени
пользователя.

### 4. Двухосевое `$code-review`

Выполни `$code-review` относительно `main`. Он обязан запустить два независимых
подагента параллельно и сохранить оси раздельными.

Для **Standards** передай `AGENTS.md`, conventions human-first Markdown,
read-only/external-write boundaries, а также Fowler smell baseline из skill.
Для **Spec** передай пути к `docs/learning-system-spec.md`, тикетам 01–10,
decisions 01–12 и instructions A–H. Проверяй missing/partial requirements,
scope creep и неверную реализацию. Каждый finding должен содержать severity,
точный файл/строку, нарушенное правило, evidence и безопасное направление
исправления.

Не объединяй и не переупорядочивай findings двух осей: приведи их отдельными
разделами `## Standards` и `## Spec`.

## Формат итогового отчёта

Создай `.agent-reports/session-i-final-review.md`:

```md
# Итоговое ревью реализации

## Контекст ревью

- Fixed point: `<main SHA>`
- Reviewed HEAD: `<HEAD SHA>`
- Коммиты/подсистемы: <кратко>
- Ограничения: <нет или список>

## Проверка реализации

| Тикет | Acceptance criteria | Evidence | Статус |
|---|---|---|---|

## Проверки

- <команда>: <результат>

## Standards

<неизменённый или минимально очищенный отчёт Standards axis>

## Spec

<неизменённый или минимально очищенный отчёт Spec axis>

## Итог и следующие действия

- Standards findings: <N>; самый серьёзный: <кратко или `нет`>
- Spec findings: <N>; самый серьёзный: <кратко или `нет`>
- Рекомендуемый следующий запуск: <исправление findings / финальная передача>
```

Статус `пройдено` допустим только при свежем evidence. Если есть blocking
finding, назови его явно; не объявляй реализацию завершённой по одному лишь
успешному тестовому набору.

## Финальная передача

В ответе пользователю укажи путь к отчёту, fixed point, reviewed HEAD,
результаты объединённых проверок и отдельно количество findings Standards/Spec.
Не создавай коммит.
