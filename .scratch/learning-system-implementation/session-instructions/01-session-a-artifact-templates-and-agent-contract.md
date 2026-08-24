# Сессия A: шаблоны учебных артефактов и общий контракт агентов

## Назначение запуска

Эту инструкцию передают одному отдельному агенту для выполнения двух связанных
тикетов:

- `01-learning-artifact-templates.md`;
- `03-agent-common-instructions.md`.

Запуск выполняется в рабочей директории
`/home/doduohor/learning/agentic-learning-workflow`. Это
реализационная сессия: агент создает шаблоны и общий контракт, но не создает
файлы ролей в `.codex/agents/*.toml`. Последнее относится к следующей сессии C.

## Обязательные skills

1. Сначала используй `$implement` для реализации по тикетам.
2. Используй `writing-for-agents`, потому что `agent-common-instructions.md`
   предназначен для будущих агентов.
3. Перед утверждением о завершении используй
   `verification-before-completion`.
4. Используй `$tdd` только если появится исполняемый код с заранее определенной
   тестируемой границей. Для данной сессии базовый результат состоит из
   Markdown-документов, поэтому вместо несуществующих unit-тестов выполняй
   структурные и поисковые проверки из раздела «Проверка».
5. После реализации обязательно используй `$code-review` для проверки своих
   изменений.

## Обязательное чтение до изменений

Прочитай файлы в указанном порядке. Это обязательный маршрут workflow: не
заменяй его кратким пересказом и не выводи правила только из prototype.

1. `AGENTS.md`.
2. `docs/wayfinder/00-map.md` — карта workflow и текущая граница проекта.
3. `CONTEXT.md` — канонический словарь; не переопределяй его термины.
4. `docs/learning-system-spec.md` — итоговая спецификация и hard invariants.
5. `.scratch/learning-system-implementation/issues/01-learning-artifact-templates.md`.
6. `.scratch/learning-system-implementation/issues/03-agent-common-instructions.md`.
7. `docs/wayfinder/decisions/02-design-learning-artifact-templates.md`.
8. `docs/wayfinder/decisions/03-design-codex-agent-roles.md`.
9. `docs/wayfinder/decisions/06-design-codex-agent-files.md`.
10. `docs/wayfinder/decisions/09-design-source-verification-workflow.md`.
11. `docs/wayfinder/decisions/10-design-session-notes-and-practice-artifact-archive.md`.
12. `docs/wayfinder/decisions/12-design-obsidian-and-anki-write-automation.md`.
13. Prototype как рабочий пример, но не как источник новых правил:
    `topics/INDEX.md` и семь основных файлов в
    `topics/rabbitmq/retry-without-idempotency/`.

До первого редактирования проверь, что рабочая директория находится в Git
репозитории и есть текущая ветка: `$implement` требует коммит в конце. Если
Git-репозитория или ветки нет, остановись до изменений и сообщи об этом как о
блокере запуска.

## Результат сессии

Создай следующие reusable human-first Markdown-шаблоны:

```text
docs/learning-system/templates/Goal.md
docs/learning-system/templates/Knowledge.md
docs/learning-system/templates/Practice.md
docs/learning-system/templates/Questions.md
docs/learning-system/templates/Weaknesses.md
docs/learning-system/templates/RepetitionLog.md
docs/learning-system/templates/Sources.md
```

При необходимости создай `docs/learning-system/templates/README.md`, но только
если он помогает однозначно применять набор шаблонов без копирования правил из
спецификации.

Также создай:

```text
docs/learning-system/agent-common-instructions.md
```

Документ должен быть практическим контрактом для будущих ролей, а не копией
decision records. Он должен направлять агента к соответствующим источникам
workflow по условию работы и закреплять single-writer state model.

## Содержание шаблонов

Шаблоны должны сохранять owner files и оставаться удобными для ручного чтения:

- `Goal.md`: Topic State, Active Block, Block Status, Mastery Level, блоки,
  completion criteria и ссылки на evidence.
- `Knowledge.md`: только curated Knowledge, а не raw Session Notes.
- `Practice.md`: structured Practice Attempts и evidence.
- `Questions.md`: Question State, Card Candidate status, Card Trace,
  Duplicate Check и Promotion Decision.
- `Weaknesses.md`: Weakness Status, severity, repair action и resolution
  evidence.
- `RepetitionLog.md`: Active Repetition records и результаты повторений.
- `Sources.md`: Source Records и Source Check Result, включая
  `needs-check` / `Нужно проверить`.
- Optional `sessions/`: описание архива Session Notes и Practice Artifacts;
  каталог не создается как новая Topic Workspace и не становится владельцем
  состояния.

Используй согласованные форматы идентификаторов, entity references, допустимые
статусы и границы редактирования из decision records. Не вводи YAML/JSON
machine-readable schema.

## Содержание общего контракта агентов

`docs/learning-system/agent-common-instructions.md` должен явно закреплять:

- Learning Orchestrator — единственный автор state-changing edits;
- supporting agents возвращают Agent Proposal или работают только в явно
  разрешенной append-only границе;
- supporting agents не меняют напрямую `Goal.md`, `Knowledge.md` и
  `Weaknesses.md`, если это не следует из отдельной явно разрешенной границы;
- обязательные evidence и traceability для Practice Attempts, Questions,
  Weaknesses, Source Checks, Repetitions, Card Candidates и Knowledge
  Consolidation;
- `needs-check` / `Нужно проверить` как gate для чувствительных claims;
- Card Promotion только при понимании, ценности, Card Trace, Source Check и
  Obsidian/Anki Duplicate Check с решением `skip`, `replace`, `merge` или
  `add`;
- прямую запись в Obsidian и Anki только через Orchestrator-controlled
  workflow после dry-run preview и user approval;
- Lightweight Checker как read-only validator.

Не превращай общий контракт в спецификацию конкретных `.codex/agents/*.toml`:
их реализация относится к тикету 04.

## Границы сессии

Разрешено менять только:

- `docs/learning-system/templates/*`;
- `docs/learning-system/agent-common-instructions.md`;
- два исходных тикета, если нужно отметить выполненные acceptance criteria;
- `CONTEXT.md` только при появлении нового устойчивого термина. Не превращай
  его в спецификацию.

Не создавай и не меняй:

- реальные записи Obsidian и Anki, Anki-карточки или Obsidian vault;
- automation scripts, slash commands, `.codex/agents/*.toml`;
- новые Topic Workspaces и prototype;
- реализацию Lightweight Checker;
- реальную Source Verification для RabbitMQ;
- YAML/JSON machine-readable schema.

## Порядок работы

1. Пройди обязательное чтение и зафиксируй для себя owner files и жесткие
   инварианты.
2. Проверь Git-предпосылку запуска.
3. Сопоставь каждый шаблон с его владельцем состояния и правилами ссылок.
4. Создай шаблоны, не копируя содержимое prototype как готовую тему.
5. Создай общий контракт с условными ссылками на workflow-материалы вместо
   дублирования их полного содержания.
6. Сверь изменения с acceptance criteria обоих тикетов.
7. Выполни проверки, затем `$code-review`.
8. Исправь все релевантные замечания ревью, повтори необходимые проверки и
   закоммить результат в текущую ветку.

## Проверка

Перед финальным сообщением выполни как минимум:

```sh
test -f docs/learning-system/templates/Goal.md
test -f docs/learning-system/templates/Knowledge.md
test -f docs/learning-system/templates/Practice.md
test -f docs/learning-system/templates/Questions.md
test -f docs/learning-system/templates/Weaknesses.md
test -f docs/learning-system/templates/RepetitionLog.md
test -f docs/learning-system/templates/Sources.md
test -f docs/learning-system/agent-common-instructions.md

rg -n "Topic State|Active Block|Block Status|Mastery Level|Source Check Result|Question State|Card Candidate status|curated Knowledge|Practice Attempts|Weakness Status|Active Repetition|Agent Proposal|Duplicate Check|Card Promotion|Knowledge Consolidation|Нужно проверить|dry-run|user approval|Lightweight Checker|YAML/JSON" docs/learning-system

find topics -mindepth 2 -maxdepth 2 -type d | sort
find . -path './.codex/agents/*.toml' -print
```

Дополнительно проверь, что вне разрешенного списка нет измененных файлов,
новых Topic Workspaces, скриптов, slash commands и файлов `.codex/agents/*.toml`.

## Финальная передача

В финальном сообщении укажи:

- созданные и измененные файлы;
- менялся ли `CONTEXT.md`;
- менялся ли prototype Topic Workspace;
- результаты структурных проверок;
- результат `$code-review` и устраненные замечания;
- хеш коммита;
- какие acceptance criteria тикетов 01 и 03 закрыты;
- что далее доступно для отдельного агента: сессия B (тикет 02) и сессия C
  (тикет 04, после успешного результата этой сессии).
