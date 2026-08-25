# Подтверждаемая запись в Obsidian и Anki

`tools/write_automation.py` реализует узкую границу Orchestrator-controlled
write workflow. Он не выбирает материал, не принимает Card Promotion или
Knowledge Consolidation decision и не подключается к личным внешним системам
самостоятельно.

## Порядок запуска

1. Learning Orchestrator собирает `WriteRequest` из owner artifacts и уже
   принятых решений.
2. `WriteAutomation.prepare()` формирует human-readable dry-run preview. В нём
   всегда есть Topic Workspace, source entity, target/type, action, proposed
   content, Duplicate/Source Check summaries, Card или Knowledge trace,
   ожидаемое Markdown-изменение, availability и recovery plan. Для Anki также
   обязательны deck, note type, fields и tags; для Obsidian — target path, note
   и section. Свободный `target_description` остаётся пояснением, но не заменяет
   эти поля. Этот шаг не пишет никуда.
3. Пользователь явно подтверждает именно показанный preview. Если текст,
   target или Duplicate Check изменился, нужен новый preview и approval.
4. Только затем Orchestrator вызывает `execute(preview, approved=True)` с
   явно переданным adapter target. Без approval, при blocker или unavailable
   target внешний `write()` не вызывается.

Anki допускает `add`, `replace`, `merge`, `skip` только после
`card-promotion`; Obsidian допускает `add`, `append`, `merge`,
`replace-section`, `skip` только после `knowledge-consolidation`. `replace` и
`merge` уже должны быть точным решением Orchestrator и всё равно требуют
явного approval preview.

## Gates и доступность

Перед ready-for-approval проверяются: Lightweight Checker, Source Check,
Duplicate Check, принятое решение с совпадающим action, готовность content и
Card/Knowledge Trace. Непройденный gate, `needs-check`, устаревшая проверка
дублей или unavailable target дают `pending`, а не имитацию успешной записи.

Production default намеренно использует `UnavailableTarget`: конкретный
adapter для Anki или Obsidian не встроен. Это не даёт случайно записать в
личный vault или Anki без доступного target, preview и отдельного approval.
Для `execute()` также нужен явно переданный `TraceWriter`; без него внешний
write не запускается. Перед write нужен и `GateVerifier`, который заново
проверяет актуальные Checker, Source Check и Duplicate Check, а также сверяет
с preview их summaries и trace; сохранённый snapshot сам по себе не считается
свежей проверкой. При расхождении нужен новый preview и approval. Тесты
используют изолированные doubles.

## Trace и повторный запуск

`MarkdownTraceWriter` обновляет human-readable outcome внутри нужной записи
owner file:

- Anki/Card Promotion — `Questions.md`;
- Obsidian/Knowledge Consolidation — `Knowledge.md`.

Outcome содержит target identity и structured details, Duplicate/Source Check
summaries, source trace/evidence, action, result, time и reason для
`replace`/`merge`. Anki outcome фиксирует deck, note type, fields, tags, Anki
Note ID и доступные Anki Card IDs; Obsidian outcome — path, note, section,
linked evidence и write result. `pending`, `unavailable`, `failed`, `partial`
и `no-op` рендерятся с собственным состоянием, без ложной отметки успеха.

`Goal.md` не получает тело write outcome; Orchestrator может отдельно добавить
в него краткую ссылку, только если меняются next action или Completion
Criteria. Возможные состояния: `succeeded`, `partial`, `failed`, `pending`,
`no-op`.

При existing external target и сохранённом trace повторный запуск становится
`no-op`. Если trace есть, но target исчез, либо target найден без trace,
формируется `reconciliation-preview`; запись не повторяется автоматически.
После `partial` или `failed` следующий шаг также начинается с preview и
проверки доступности.
