# Запись решения: workflow проверки источников

## Статус

Принято.

## Контекст

Учебная система уже требует Source Check для чувствительных programming claims, но до этого ticket не было полного workflow: когда проверка обязательна, где живет результат, что означает `Нужно проверить`, кто может выполнять проверку и какие действия запрещены при `needs-check`.

Уже принято:

- `Sources.md` является артефактом Source Record внутри Topic Workspace;
- `Goal.md` владеет Topic State, Active Block, Block Status и Mastery Level;
- Source Agent является поддерживающей ролью;
- Source Agent может дописывать новые записи в `Sources.md`, но не меняет учебное состояние;
- Card Promotion требует понимания, ценности, traceability, проверки дублей в Obsidian и Anki;
- Topic Workspaces живут по пути `topics/<subject>/<stable-slug>/`, а `topics/INDEX.md` является источником навигации.

Prototype Topic Workspace содержит `SRC-20260824-01` со статусом `needs-check`: RabbitMQ-specific dead-letter behavior намеренно не проверен, потому что prototype проверял форму workspace, а не реальный Source Verification Workflow.

Этот ticket не выполняет реальную RabbitMQ-проверку и не реализует lightweight checker.

## Решение

Source Verification Workflow определяет, как система проверяет claims перед тем, как использовать их для надежного применения, закрытия темы, продвижения карточек или консолидации знания.

### Claims, которые требуют Source Check

Source Check обязателен для claims, которые влияют на:

- `production-ready`;
- безопасность;
- семантику протоколов;
- Card Promotion;
- Knowledge Consolidation в Obsidian;
- переход Topic в `completed`;
- закрытие блока или темы, если claim является частью Completion Evidence;
- реальное поведение инструмента, библиотеки, платформы или runtime;
- версионно-зависимые рекомендации;
- performance, operational и production guidance, если они важны для текущего Learning Profile.

Остальные claims можно считать durable concept без отдельного Source Check, если они не зависят от версии, инструмента, политики безопасности, производительности, протокола или конкретного поведения платформы.

Пример durable concept: "идемпотентность нужна, чтобы повтор операции не ломал бизнес-состояние".  
Пример claim, требующий Source Check: "RabbitMQ dead-letters message when condition X happens in configuration Y".

### Типы источников

Используем уже принятые `Authority Type` без отдельной tier-модели:

```text
official-docs
spec-rfc
release-notes
vendor-blog
engineering-article
community-discussion
course-book
```

Достаточность источника определяется по ситуации.

Ориентиры:

- для security, protocol-semantics и tooling-behavior обычно нужны `official-docs`, `spec-rfc` или `release-notes`;
- `vendor-blog`, `engineering-article` и `course-book` могут быть достаточны для объяснения подхода, практического опыта или устойчивого design guidance;
- `community-discussion` можно использовать как сигнал проблемы, пример edge case или указатель на спорную область, но его качество должно быть явно видно в `Sources.md`;
- если claim влияет на `production-ready`, `completed`, Card Promotion или Knowledge Consolidation, источник должен быть достаточно сильным для этой ответственности.

Отдельные authority tiers не вводятся, чтобы не создавать новую схему раньше необходимости.

## Где живет Source Check

`Sources.md` владеет:

- Source Records;
- Source IDs;
- проверяемыми claims;
- чувствительностью claim;
- типом источника;
- датой проверки;
- результатом проверки;
- краткими Source Notes.

`Knowledge.md`, `Questions.md`, `Goal.md`, `Practice.md` и `RepetitionLog.md` не владеют результатом проверки. Они могут:

- ссылаться на `SRC-*`;
- ставить `Нужно проверить` рядом с непроверенным claim;
- использовать Source Record как evidence;
- показывать, где claim применяется.

Если `Sources.md` и другой артефакт расходятся по статусу проверки, источником истины для Source Check является `Sources.md`. Если вывод из Source Check меняет Topic State, Block Status, Mastery Level, Card Promotion или Completion, решение применяет Learning Orchestrator.

## Значение `Нужно проверить`

`Нужно проверить` означает: claim сохранен как потенциально полезный, но система не считает его подтвержденным.

С claim в `needs-check` можно:

- использовать его для ориентации;
- обсуждать как гипотезу;
- строить раннее понимание до `recognition` или `recall`;
- создавать черновые вопросы;
- планировать будущий Source Check.

С claim в `needs-check` нельзя:

- выдавать его как подтвержденный факт;
- использовать как единственное основание для `production-ready`;
- закрывать Topic как `completed`, если claim нужен для Completion Criteria;
- продвигать связанную карточку в Anki;
- консолидировать знание в Obsidian без явной оговорки;
- снимать blocker, если исправление зависит от этого claim;
- удалять пометку `Нужно проверить` из связанных артефактов без обновления `Sources.md`.

## Lifecycle gates

Source Check обязателен перед:

- повышением блока до `production-ready`, если чувствительный claim является частью evidence;
- переходом Topic в `completed`, если Completion Criteria зависят от чувствительного claim;
- Card Promotion, если карточка содержит чувствительный claim;
- Knowledge Consolidation в Obsidian, если переносимый фрагмент содержит чувствительный claim;
- переносом claim в устойчивое `Knowledge.md` без пометки `Нужно проверить`.

Source Check не обязателен перед `planned`, если claim не используется как подтвержденный факт. В таком случае Topic может двигаться дальше с явным `needs-check`, но маршрут должен учитывать ограничение.

## Кто выполняет Source Check

Source Agent может:

- читать `Sources.md`, `Knowledge.md`, `Questions.md`, `Practice.md`, `Goal.md` и нужные источники;
- добавлять новые Source Records в `Sources.md`;
- предлагать результат `verified`, `rejected`, `needs-check` или `superseded`;
- предлагать точные правки в `Knowledge.md`, `Questions.md` или `Goal.md`;
- указывать риски и ограничения найденных источников.

Learning Orchestrator применяет выводы, если они меняют:

- `Goal.md`;
- `Knowledge.md`;
- `Weaknesses.md`;
- Topic State;
- Active Block;
- Block Status;
- Mastery Level;
- Completion Criteria;
- Card Promotion;
- Knowledge Consolidation decision.

Любой Physical Agent может выполнять Source Agent work только в явном Role Mode. Если Role Mode неясен, он возвращает Agent Proposal, а не меняет state-changing артефакты.

## Минимальная запись в Sources.md

Текущий шаблон `Sources.md` достаточен. Обязательные поля остаются:

| Поле | Назначение |
|---|---|
| Source ID | Устойчивый `SRC-YYYYMMDD-NN`. |
| Claim | Проверяемое утверждение. |
| Sensitivity | Почему claim требует проверки или почему это durable concept. |
| Authority Type | Тип источника. |
| Checked At | Дата проверки или `-`, если проверки не было. |
| Result | `verified`, `rejected`, `needs-check`, `superseded`. |
| Used In | Где claim используется. |
| Source URL/Reference | URL, RFC, documentation page, book reference или описание недоступного источника. |
| Next Check | Когда или перед каким gate нужна следующая проверка. |
| Notes | Короткий пересказ вывода без длинного копирования источника. |

Новые обязательные поля не добавляются. Если нужно объяснить последствия проверки, это пишется в `Notes` и затем применяется Learning Orchestrator в связанных артефактах.

## Результаты Source Check

`verified` означает: источник достаточен для текущего использования claim.

`rejected` означает: claim опровергнут, неверен для текущего контекста или не должен использоваться в этой теме.

`needs-check` означает: claim не подтвержден, источник недоступен, недостаточен или проверка еще не выполнена.

`superseded` означает: Source Record вытеснен более свежим или более точным Source Record. Запись не удаляется, чтобы сохранять traceability.

## Противоречивые и устаревшие источники

Если источники противоречат друг другу:

- не ставить `verified` автоматически;
- оставить или вернуть `needs-check`, если нужен дополнительный источник;
- поставить `rejected`, если claim нельзя безопасно использовать;
- записать конфликт в `Notes`;
- передать Learning Orchestrator proposal, если конфликт влияет на route, Mastery Level, Card Promotion или Completion.

Если источник устарел:

- старый Source Record получает `superseded`;
- новый Source Record получает новый `SRC-*`;
- связанные артефакты обновляются через Learning Orchestrator, если меняется учебное состояние или устойчивое знание;
- если новое подтверждение еще не найдено, claim возвращается в `needs-check`.

## Работа без доступа к источникам

Если интернет, документация, Anki, Obsidian или нужный источник недоступны:

- не считать claim проверенным по памяти агента;
- создать или оставить Source Record с `Result: needs-check`;
- в `Notes` указать, что проверка не выполнена из-за недоступности источника;
- сохранить `Нужно проверить` в связанных артефактах;
- ограничить действия с claim по правилам `needs-check`;
- записать `Next Check`, если понятно, перед каким gate проверка нужна.

Учебная работа может продолжаться, если claim используется только для ориентации или раннего понимания. Закрывающие действия ждут проверки.

## Отношение к другим артефактам

`Knowledge.md`:

- может хранить claim с `Нужно проверить`;
- должен ссылаться на `SRC-*`, если claim чувствительный;
- не снимает `Нужно проверить` без обновленного Source Record.

`Questions.md`:

- может иметь черновой или active вопрос по claim в `needs-check`;
- не может продвигать Card Candidate в Anki, если карточка зависит от `needs-check`.

`Goal.md`:

- может ссылаться на pending Source Check как Completion Evidence или risk;
- не может использовать `needs-check` как подтвержденное evidence для `production-ready` или `completed`;
- остается владельцем Topic State, Active Block, Block Status и Mastery Level.

`Practice.md`:

- может фиксировать practice, построенную вокруг непроверенного claim, если это явно учебная гипотеза;
- не превращает непроверенный claim в подтвержденное знание.

`RepetitionLog.md`:

- может планировать повторение по durable concept;
- не должен закреплять карточку или устойчивое знание на основе чувствительного `needs-check` claim.

## Требования к будущему lightweight checker

Будущему lightweight checker нужно передать только инварианты, не алгоритм реализации.

Checker должен уметь проверять:

- `SRC-*` references ведут на существующие Source Records;
- `Result` использует только `verified`, `rejected`, `needs-check`, `superseded`;
- `Нужно проверить` в `Knowledge.md`, `Questions.md` или `Goal.md` имеет связанный `SRC-*`, если claim чувствительный;
- `Card Candidate` не имеет `promoted`, если связанный обязательный Source Check остается `needs-check`;
- блок не имеет `production-ready`, если его обязательный чувствительный Source Check остается `needs-check`;
- Topic не имеет `completed`, если Completion Criteria зависят от `needs-check`;
- `superseded` Source Record указывает в `Notes` или `Next Check` на дальнейшую проверку или новый Source Record;
- checker работает с human-first Markdown и не требует YAML/JSON machine-readable schema.

Полный дизайн checker остается отдельным ticket.

## Обоснование

Выбранный workflow делает проверку источников строгой там, где система обещает надежное знание, но не блокирует раннее обучение. Это важно для живого учебного процесса: learner может разбираться в теме, пока точные детали инструмента еще не проверены, но система не выдает непроверенное за подтвержденное.

`Sources.md` как единственный владелец Source Records снижает риск расхождения между файлами. Разделение Source Agent и Learning Orchestrator сохраняет single-writer state model: один агент может собрать и записать проверку, но изменение учебного состояния применяет оркестратор.

Отказ от отдельной tier-модели для источников сохраняет human-first Markdown. Существующих `Authority Type` достаточно для первой версии, а достаточность источника оценивается по риску claim и месту использования.

## Последствия

Будущие lifecycle commands и Agent Files должны учитывать gate-правила:

- `needs-check` не блокирует раннее обучение;
- `needs-check` блокирует `production-ready`, `completed`, Card Promotion и Knowledge Consolidation, если claim обязателен для этих действий;
- Source Agent может дописывать `Sources.md`, но не применяет state-changing выводы.

Prototype Topic Workspace остается без изменений: `SRC-20260824-01` по-прежнему является корректным примером `needs-check` Source Record.

## Вне области

Это решение не делает:

- реальную RabbitMQ source verification;
- lightweight checker;
- YAML/JSON machine-readable schema;
- `.codex/agents/*.toml`;
- slash commands;
- Obsidian/Anki automation;
- новые учебные темы;
- расширение prototype в полноценную учебную тему;
- финальный `learning-system-spec.md`.

## Следующие тикеты

1. `Design Session Notes And Practice Artifact Archive`
2. `Design Lightweight Checker For Entity References And IDs`
3. `Design Obsidian And Anki Write Automation`
4. `Assemble Learning System Specification`

## Критерии завершения

Это решение считается закрытым, когда:

- определено, какие claims требуют Source Check;
- закреплено, что существующие `Authority Type` используются без отдельной tier-модели;
- `Sources.md` закреплен как владелец Source Records и результатов проверки;
- определено точное значение `Нужно проверить`;
- определены lifecycle gates для `production-ready`, `completed`, Card Promotion и Knowledge Consolidation;
- разделены права Source Agent и Learning Orchestrator;
- описано поведение при conflict, stale source и недоступности источника;
- future checker получил требования без реализации и без machine-readable schema;
- карта wayfinder обновлена.
