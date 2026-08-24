# Workflow проверки источников

Этот workflow ведёт Source Record от запроса до решения Learning Orchestrator.
Он работает с human-first Markdown в `Sources.md` и не выполняет внешнюю
проверку автоматически.

## Когда запускать

Запускайте Source Check до того, как claim будет использован для
`production-ready`, `completed`, Card Promotion или Knowledge Consolidation.
Проверка обязательна для version-sensitive, application-sensitive, production,
security, protocol-semantics и tooling-behavior claims. Durable concept можно
оставить без отдельного Source Check, пока он не зависит от такого поведения.

Source Agent сначала читает `Goal.md`, `Knowledge.md`, `Questions.md`,
`Practice.md` и `Sources.md`, затем формулирует один проверяемый claim и его
планируемое использование. Он не подтверждает claim по памяти.

## Создание Source Record

Source Agent может по явному поручению дописать в `Sources.md` только одну
новую запись с новым `SRC-YYYYMMDD-NN`. Запись использует поля шаблона:

- Claim и Sensitivity;
- Source URL/Reference и Authority Type;
- Checked At;
- Source Check Result;
- Used In как Entity References;
- Next Check и короткие Notes.

`Sources.md` — единственный владелец Source Check Result. В `Goal.md`,
`Knowledge.md` и `Questions.md` разрешены только ссылка на `SRC-*` и пометка
`Нужно проверить`, но не второй результат проверки.

## Результаты проверки

| Результат | Когда ставить | Что делать дальше |
|---|---|---|
| `verified` | Авторитетный источник достаточен для текущего claim и его gate. | Передать Orchestrator evidence и точный Proposal для связанных артефактов. |
| `rejected` | Claim неверен, неприменим в этом контексте или небезопасен для использования. | Не использовать claim как evidence; предложить исправление Knowledge, Questions или Goal. |
| `needs-check` | Источник недоступен, недостаточен, противоречив или ещё не проверен. | Оставить `Нужно проверить`, записать причину и Next Check до нужного gate. |
| `superseded` | Старый record вытеснен более свежим или точным record. | Сохранить старый record для traceability и указать новый `SRC-*` либо следующий источник в Notes/Next Check. |

Source Agent не переписывает старую запись. Если результат меняется, он либо
добавляет новый Source Record, либо возвращает Proposal для Orchestrator: тот
может изменить старую запись и связанные state-changing артефакты.

## Недоступный источник

Недоступный сайт, документация или иной источник — нормальный результат, а не
разрешение сделать вывод по памяти. Source Agent создаёт либо сохраняет
`needs-check`, указывает в Notes причину недоступности и ставит Next Check,
например «перед Card Promotion». В связанных Knowledge/Questions сохраняется
`Нужно проверить` со ссылкой на тот же `SRC-*`.

## Gate impact

Если чувствительный claim нужен для gate, `needs-check` блокирует:

- `production-ready`;
- `completed`;
- Card Promotion;
- Knowledge Consolidation.

`rejected` также не является положительным evidence. `superseded` нельзя
использовать вместо текущей проверки, пока ссылка не переведена на пригодный
новый record. `needs-check` не блокирует раннее обучение, черновые вопросы или
обсуждение claim как гипотезы.

## Передача результата

После append-only записи или без права записи Source Agent возвращает:

```md
## Agent Proposal

- Role Mode: source
- Прочитанный контекст: Goal.md, Knowledge.md, Questions.md, Practice.md, Sources.md
- Claim: <проверяемое утверждение>
- Source Record: [SRC-...](Sources.md#...)
- Result: `verified | rejected | needs-check | superseded`
- Evidence: <авторитетный источник или причина недоступности>
- Gate impact: <какие gate разрешены или заблокированы>
- Предлагаемые изменения: <Knowledge.md, Questions.md или Goal.md; только точный фрагмент>
- Риски: <неопределённость, конфликт источников, устаревание>
- Next step: <следующее безопасное действие>
```

Только Learning Orchestrator применяет Proposal, который меняет `Goal.md`,
`Knowledge.md`, `Questions.md`, Card Promotion, Knowledge Consolidation или
любое учебное состояние. Source Agent не пишет в Obsidian/Anki и не выполняет
реальную проверку RabbitMQ prototype без отдельного поручения.

## Проверка перед применением

Перед чувствительным gate Orchestrator запускает Lightweight Checker. Он
проверяет ссылку на `SRC-*`, допустимость результата и blocking `needs-check`;
он не проверяет содержание внешнего источника и не меняет Markdown.
