# Сессия K: адаптеры записи AnkiConnect и Obsidian filesystem

## Назначение запуска

Отдельный агент реализует два concrete adapter для существующего
`tools/write_automation.py`:

```text
ExternalWriteTarget
├── AnkiConnectAdapter
└── ObsidianFilesystemAdapter
```

`WriteAutomation` остаётся transport-agnostic: он формирует preview, проверяет
gates, требует актуальный user approval и пишет outcome в owner artifacts.
Адаптеры знают только, как проверить/прочитать/записать конкретный внешний
target и вернуть фактический результат.

Рабочая директория:
`/home/doduohor/learning/agentic-learning-workflow`.

## Предпосылки

До первого изменения проверь:

1. ветка — `learning-system-implementation`;
2. рабочее дерево чисто, кроме `.agent-reports/`;
3. существует `tools/write_automation.py` с `ExternalWriteTarget`,
   `ExternalWriteResult`, preview/approval/gate/revision boundaries;
4. весь текущий набор тестов проходит.

Если предпосылка не выполнена, остановись и отрази блокер в отчёте. Не
смешивай сессию с чужими незакоммиченными изменениями.

## Обязательные skills

1. Найди skills:
   `rg --files /mnt/c/Users/Sergey/.codex/skills | rg 'SKILL\.md$'`.
   Полностью прочитай каждый применимый и явно названный `SKILL.md` до работы.
2. Используй `$implement`:
   `/mnt/c/Users/Sergey/.codex/skills/implement/SKILL.md`.
3. Используй `$tdd` для сетевой границы AnkiConnect и файловой границы Obsidian.
4. Используй `verification-before-completion` перед финальным выводом.
5. Используй `$code-review`, исправь все релевантные findings, повтори
   проверки и закоммить результат.
6. Для current API AnkiConnect и официально документированных interfaces
   Obsidian сначала проведи Source Check по первичным источникам. Если
   актуальный интерфейс или его семантика недоступны, зафиксируй
   `needs-check`/`Нужно проверить` и не реализуй write по памяти.

## Обязательное чтение

1. `AGENTS.md`, `CONTEXT.md`, `docs/learning-system-spec.md`;
2. `docs/learning-system/write-automation-workflow.md` и
   `docs/learning-system/agent-common-instructions.md`;
3. decisions 05, 09, 11 и 12 в `docs/wayfinder/decisions/`;
4. `tools/write_automation.py` и `tests/test_write_automation.py`;
5. `tools/duplicate_check.py`, `docs/learning-system/duplicate-check-workflow.md`;
6. templates `Questions.md`, `Knowledge.md`, `Sources.md`;
7. `.agent-reports/session-j-final-review-fixes.md`.

## Общие неизменяемые границы

- Никакой реальной записи в личные Anki или Obsidian во время разработки,
  тестов, smoke checks или проверки CLI.
- `prepare()` остаётся read-only. Внешний `write()` возможен лишь внутри
  `WriteAutomation.execute()` с актуальным preview, положительным `approved`,
  свежими gates и явно переданным adapter.
- Не храни URL, токены, пароли, пути к личному vault или содержимое личных
  заметок в Git, Topic Workspace, тестах или отчётах.
- Конфигурация adapter передаётся явно в runtime (constructor/CLI flag/env),
  но development defaults не обращаются к localhost и к реальному vault.
- Не меняй prototype, не создавай карточки/notes, не вводи YAML/JSON
  machine-readable schema и не обходи owner model.
- Любой реальный smoke write остаётся отдельным последующим запуском после
  показанного пользователю preview и нового явного approval.

## AnkiConnectAdapter

Реализуй adapter с узким HTTP transport, который следует **проверенной
актуальной** спецификации AnkiConnect, а не предположениям. Выдели transport
так, чтобы unit tests подменяли его fake server/client и не открывали реальный
сетевой порт.

Минимальное поведение:

- availability — read-only health/version check;
- `exists(identity)` — read-only проверка существования trace target;
- `preview_revision(request)` — read-only revision/identity, достаточная для
  stale-target check; если API не даёт корректной revision, верни явное
  ограничение и требуй reconciliation preview, а не имитируй проверку;
- `write(request)` поддерживает только действия, уже подтверждённые
  Orchestrator: `add`, `replace`, `merge`, `skip`;
- `add`/`replace`/`merge` используют конкретные note/deck/field/tag данные из
  `WriteRequest`; adapter возвращает `ExternalWriteResult` с реальным target
  identity, Note ID и Card IDs, **если API их фактически возвращает или их
  можно read-only получить по созданному Note ID**;
- если Card IDs недоступны, верни пустой набор: нельзя придумывать IDs;
- `skip` не вызывает внешний write и возвращает честный `no-op` pathway;
- сетевые, protocol и remote validation ошибки не превращай в success:
  возвращай/поднимай различимый failure, который `WriteAutomation` фиксирует
  как `failed`, `partial` или `pending` согласно контракту.

Не добавляй «тихий» fallback к AnkiConnect. Adapter не получает endpoint без
явной конфигурации.

## ObsidianFilesystemAdapter

Реализуй adapter для **явно переданного vault root**, не для произвольного
пути. Он работает с Markdown-файлами в vault и не зависит от community plugin.

Минимальное поведение:

- разрешай только target path внутри `vault_root`; нормализуй пути и отвергай
  traversal/symlink escape за пределы vault;
- availability — read-only проверка существования и доступности vault root;
- `exists(identity)` и `preview_revision(request)` — read-only;
- revision строится из содержимого/метаданных так, чтобы изменение после
  preview требовало reconciliation preview;
- поддержи `add`, `append`, `replace-section`, `merge`, `skip` только по
  already approved request; алгоритм `merge` должен быть детерминированным и
  минимальным, а при неоднозначности возвращать pending/reconciliation, а не
  перезаписывать текст;
- запись выполняй atomic replace в том же filesystem; до replace повторно
  сверяй revision; при ошибке не оставляй частично записанный target;
- recovery plan/backup trace остаются human-readable в owner artifact и не
  требуют отдельного machine-readable state file;
- adapter возвращает реальный path/section identity; `skip` не пишет файл.

Не реализуй агрессивное удаление, массовую миграцию, двустороннюю синхронизацию
или автоматическое разрешение конфликтов.

## Тесты и TDD

Сначала добавь isolated failing tests, затем реализацию. Используй:

- fake AnkiConnect transport/server с зафиксированными успешными и ошибочными
  ответами;
- `TemporaryDirectory` как synthetic Obsidian vault;
- test doubles для `TraceWriter` и `GateVerifier`.

Покрой минимум:

1. Anki availability/identity/read-only Card ID lookup без write;
2. `add` с фактически возвращёнными Note/Card IDs;
3. отсутствие Card IDs без их выдумывания;
4. Anki unavailable, network/protocol failure и `skip` без write;
5. Obsidian path traversal и symlink escape rejection;
6. append/add и atomic replacement в temporary vault;
7. stale revision после preview → reconciliation без write;
8. конфликт/partial failure → честный outcome и recovery trace;
9. отсутствие production write при `approved=False`, stale preview или
   непрошедшем gate;
10. полный regression suite, включая существующие preview/trace tests.

## Проверка

После каждого логического шага запускай относящиеся тесты. Перед завершением:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_write_automation -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 tools/check_topic_workspace.py --index topics/INDEX.md \
  --workspace topics/rabbitmq/retry-without-idempotency
git diff --check
git status --short
```

Подтверди, что tests/checker не изменили tracked files или реальный vault/Anki.
Выполни `$code-review` относительно текущего базового коммита, исправь
релевантные findings и повтори проверки.

## Финальная передача

Создай `.agent-reports/session-k-production-write-adapters.md` (игнорируется
Git) со следующими разделами:

1. `## Результат` — commit hash и реализованные adapters.
2. `## Контракты` — configuration, действия, result/identity/Card IDs.
3. `## Безопасность` — какие write paths запрещены без preview/approval и что
   тестировалось только через doubles/temporary vault.
4. `## Проверка` — команды и измеримые результаты.
5. `## Ревью` — findings и исправления.
6. `## Ограничения и следующий ручной шаг` — что нужно пользователю для
   отдельного approved smoke write; без выполнения этого шага агентом.

В финальном ответе перечисли изменённые файлы, результаты test/review,
commit hash, Source Check basis для AnkiConnect/Obsidian interfaces и любые
`needs-check`/unavailable ограничения.
