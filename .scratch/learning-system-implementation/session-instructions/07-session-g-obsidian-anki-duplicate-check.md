# Сессия G: проверка дублей в Obsidian и Anki

## Назначение запуска

Отдельный агент выполняет тикет `08-obsidian-anki-duplicate-check.md`:
реализует read/check workflow перед Card Promotion и Knowledge Consolidation,
не выполняя внешнюю запись.

Рабочая директория: `/home/doduohor/learning/agentic-learning-workflow`.

## Предпосылки и skills

Нужны B, C и F: checker, общий контракт/Agent Files и Source Verification
workflow. Используй `$implement`, `$tdd` для read/check логики,
`verification-before-completion` и `$code-review`. Для реального доступа к
локальному Obsidian/Anki используй только уже доступные read-only возможности;
не запрашивай и не используй write API.

## Обязательное чтение до изменений

1. `AGENTS.md`, `CONTEXT.md`, `docs/wayfinder/00-map.md`,
   `docs/learning-system-spec.md` и тикет 08.
2. `docs/learning-system/agent-common-instructions.md`, Checker contract,
   Source Verification workflow и Agent Files.
3. Decisions 05, 09, 11 и 12 в `docs/wayfinder/decisions/`.
4. Для Obsidian-контекста используй vault из `AGENTS.md`;
   `Questions.md` и `Knowledge.md` — owner artifacts для trace.

## Результат сессии

Реализуй read/check workflow, который ищет релевантные Obsidian notes перед
Card Promotion и Knowledge Consolidation, а Anki — только перед планируемым
созданием/изменением карточки. Он формирует Duplicate Check summary с target,
похожими объектами, силой совпадения, availability и рекомендованным действием:
`skip`, `replace`, `merge`, `add`, `append` или `replace-section`.

При недоступности Obsidian или Anki итог — `pending`/`unavailable`; workflow не
считает promotion/consolidation выполненными. Strong duplicate, `replace`,
спорный `merge` и сомнительная ценность оставляет для решения Learning
Orchestrator и, когда нужно, пользователя. Поддерживающие агенты готовят
Proposal/summary; только Orchestrator записывает итоговый trace в owner
artifacts.

## Границы и проверка

Разрешены read-only implementation/tests/docs, тикет 08 и узкие дополнения
общего контракта. Не создавай Anki cards, не меняй Obsidian vault, не выполняй
write automation, не меняй prototype и не добавляй YAML/JSON schema.

Покрой тестами: нет дубля, сильный дубль, частичное совпадение, недоступный
Obsidian, недоступный Anki и отсутствие внешних изменений. Проверь, что любой
внешний вызов работает только на чтение. После `$code-review` повтори tests,
`git diff --check` и закоммить.

В финальной передаче укажи доступные/недоступные режимы, место хранения summary,
результаты tests и ревью, коммит и закрытые criteria. Следующая зависимая
сессия — H.
