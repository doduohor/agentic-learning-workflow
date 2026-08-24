# Сессия H: автоматизация записи в Obsidian и Anki

## Назначение запуска

Отдельный агент выполняет тикет `09-obsidian-anki-write-automation.md`.
Сессия реализует Orchestrator-controlled write automation после уже принятого
Card Promotion или Knowledge Consolidation decision.

Рабочая директория: `/home/doduohor/learning/agentic-learning-workflow`.

## Предпосылки и skills

Требуются B, F и G: Checker, Source Verification и Duplicate Check workflow.
Используй `$implement`, `$tdd`, `verification-before-completion` и
`$code-review`. До работы проверь реальные доступные interfaces Obsidian/Anki;
не имитируй успешную запись, если target недоступен.

## Обязательное чтение до изменений

1. `AGENTS.md`, `CONTEXT.md`, `docs/wayfinder/00-map.md`,
   `docs/learning-system-spec.md` и тикет 09.
2. Checker, Source Verification и Duplicate Check результаты/контракты.
3. `Questions.md`, `Knowledge.md`, `Sources.md`, `Goal.md` templates и общий
   контракт агентов.
4. Decisions 05, 09, 11 и 12 в `docs/wayfinder/decisions/`.

## Результат сессии

Реализуй два независимых write target: Anki после Card Promotion и Obsidian
после Knowledge Consolidation. До каждой операции обязателен dry-run preview,
который показывает target, action, proposed content, Duplicate Check summary,
Source Check summary, Card/Knowledge Trace, ожидаемые Markdown updates и план
восстановления при частичном сбое.

Внешняя запись выполняется только после явного user approval preview. Действия
Anki: `add`, `replace`, `merge`, `skip`; Obsidian: `add`, `append`, `merge`,
`replace-section`, `skip`. `replace`/`merge` требуют явного решения и approval.
Без доступного target сохраняй `pending`/`unavailable`, не выдавая операцию за
выполненную.

После успешной записи trace outcome пишется только в owner artifacts:
`Questions.md` для Anki/Card Promotion, `Knowledge.md` для Obsidian/Knowledge
Consolidation, `Goal.md` — только краткая ссылка при влиянии на next action или
Completion Criteria. Повторный запуск обязан различать no-op, pending, partial,
failed и reconciliation preview, не создавая дубликат.

## Границы и проверка

Разрешены automation implementation/tests/docs, тикет 09 и минимальные
контрактные дополнения. Не обходи user approval, gates или owner files; не
вводи YAML/JSON machine-readable schema. Никакой реальной записи в личные
Obsidian/Anki данные без отдельного явного подтверждения пользователя в момент
dry-run preview.

Покрой тестами gates, отказ approval, unavailable target, успешный dry-run без
write, идемпотентный повтор, partial failure и trace outcome. Используй
изолированные test doubles для write tests. Проверь, что production write path
не вызывается без approval. После `$code-review` повтори весь набор tests,
выполни `git diff --check` и закоммить.

В финальной передаче укажи границы внешней записи, результаты tests/review,
хеш коммита, закрытые criteria и любые pending/unavailable ограничения.
