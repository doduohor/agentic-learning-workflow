# Сессия J: исправления по итоговому Spec-ревью

## Назначение запуска

Отдельный агент исправляет два подтверждённых Spec finding из
`.agent-reports/session-i-final-review.md` и добавляет регрессионные тесты.
Рабочая директория:
`/home/doduohor/learning/agentic-learning-workflow`.

## Предпосылки

До изменений проверь:

1. ветка — `learning-system-implementation`;
2. рабочее дерево чисто, кроме игнорируемой `.agent-reports/`;
3. HEAD содержит `afa892b` или более поздний коммит;
4. текущий набор тестов проходит.

Если любая предпосылка не выполнена, остановись и сообщи блокер; не смешивай
эту сессию с чужими незакоммиченными изменениями.

## Обязательные skills

1. Обнаружь skills: `rg --files /mnt/c/Users/Sergey/.codex/skills | rg 'SKILL\.md$'`.
   До действий полностью прочитай все применимые и явно указанные `SKILL.md`.
2. Используй `$implement` по пути
   `/mnt/c/Users/Sergey/.codex/skills/implement/SKILL.md`.
3. Используй `$tdd` для обеих регрессионных границ.
4. Перед финальной передачей используй `verification-before-completion`.
5. После реализации используй `$code-review`, устрани релевантные findings,
   повтори проверки и закоммить результат.

## Обязательное чтение

Прочитай в указанном порядке:

1. `AGENTS.md`, `CONTEXT.md`, `docs/learning-system-spec.md`;
2. `.agent-reports/session-i-final-review.md`;
3. `docs/wayfinder/decisions/11-design-lightweight-checker-for-entity-references-and-ids.md`:
   Draft Orphan rules и Entity References;
4. `docs/wayfinder/decisions/12-design-obsidian-and-anki-write-automation.md`:
   dry-run/preview, Anki trace, Obsidian trace и re-run safety;
5. `tools/check_topic_workspace.py`, `tests/test_check_topic_workspace.py`,
   `tools/write_automation.py`, `tests/test_write_automation.py`;
6. `docs/learning-system/templates/Questions.md`,
   `docs/learning-system/templates/Knowledge.md` и
   `docs/learning-system/write-automation-workflow.md`.

## Подтверждённые finding 1: bare ID без Entity Reference

ADR 11 требует **warning** для bare ID без Markdown-ссылки в значимой связи.
Checker сейчас находит ID и проверяет target, но не отличает bare ID от
Entity Reference.

Реализуй минимальную проверку только для значимых полей cross-file
traceability: evidence/linked entities в `Goal.md`, `Practice.md`,
`Questions.md`, `Weaknesses.md`, `RepetitionLog.md`, `Sources.md` и archive
files, когда они существуют. Не считай bare ID внутри заголовка, таблицы ID,
форматного примера, prose или локального identifier ошибкой.

Требования finding:

- bare ID в значимой связи создаёт `warning`, `does not block`, с понятным
  repair hint: заменить на Markdown Entity Reference;
- корректный `[ID: краткий смысл](file.md#anchor)` не создаёт finding;
- missing target остаётся существующим `error`, а warning не должен его
  маскировать;
- draft-исключения ADR 11 сохраняются: новый warning сам по себе не запрещает
  ранний lifecycle;
- добавь изолированные fixtures и red/green tests.

## Подтверждённое finding 2: полный preview и owner trace write automation

ADR 12 требует явные human-readable детали target и trace. Свободная строка
`target_description` остаётся полезным пояснением, но не заменяет обязательные
поля.

Расширь request/preview/outcome/trace так, чтобы они сохраняли и рендерили:

- всегда: Topic Workspace, source entity, target type, action, Duplicate Check,
  Source Check, Card Trace или Knowledge Consolidation trace, expected Markdown
  updates, recovery plan и availability;
- для Anki: deck, note type, fields, tags; после успешной записи — Anki Note ID
  и Anki Card IDs, если доступны; `replace`/`merge` также сохраняют reason;
- для Obsidian: target path, note и section; после успешной записи — action,
  written-at, source Knowledge section, linked evidence, Duplicate/Source
  summary и write result;
- pending/unavailable/failed/partial/no-op outcomes остаются честными и не
  выглядят как успешная запись.

Сохрани human-first Markdown и текущую границу: только owner artifact получает
trace (`Questions.md` для Anki, `Knowledge.md` для Obsidian). Не вводи
YAML/JSON machine-readable schema, реальный внешний adapter или запись в
Obsidian/Anki.

Добавь red/green тесты как минимум для:

1. полного Anki preview и успешного trace с target IDs/tags;
2. полного Obsidian preview и trace с path/note/section/evidence;
3. `replace` или `merge` с сохранённым reason;
4. unavailable/pending без ложного success trace.

## Явно вне scope

Не меняй правило stale Topic Index: ADR 11 определяет расхождение Topic State
между Index и `Goal.md` как `warning`, потому что `Goal.md` — источник истины.
Не повышай его до `error` и не делай `completed` заблокированным только из-за
устаревшего index cache.

Также вне scope: реальная проверка/запись в Obsidian или Anki, новый Topic
Workspace, изменение prototype, внешний API, автоисправление checker,
рефакторинг Data Clumps/adapter duplication без необходимости и любые изменения
помимо двух finding.

## Проверка

Выполняй отдельные тесты после каждого шага, затем минимум:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_topic_workspace -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_write_automation -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 tools/check_topic_workspace.py --index topics/INDEX.md \
  --workspace topics/rabbitmq/retry-without-idempotency
git diff --check
git status --short
```

Подтверди, что checker на prototype остаётся read-only. После `$code-review`
исправь все релевантные замечания, повтори необходимые проверки и закоммить.

## Финальная передача

В ответе перечисли: оба исправленных finding, изменённые файлы, новые тесты и
их результаты, результат `$code-review`/исправления, результат prototype run,
хеш коммита и оставшиеся ограничения. Создай также краткий отчёт в
`.agent-reports/session-j-final-review-fixes.md`; он не включается в Git.
