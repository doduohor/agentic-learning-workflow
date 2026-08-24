# Запись решения: автоматизация записи в Obsidian и Anki

## Статус

Принято.

## Контекст

Предыдущие решения уже закрепили правила Duplicate Check, Card Promotion, Knowledge Consolidation, Source Check и lightweight checker. Оставался вопрос: как будущая система должна выполнять фактическую запись во внешние долговременные хранилища после того, как Learning Orchestrator уже принял решение.

Это решение проектирует write automation только на уровне workflow, gates, traceability и failure modes. Оно не реализует запись, не создает API client, CLI, slash commands, Obsidian notes, Anki cards, `.codex/agents/*.toml` или parser internals.

Уже принято:

- `Goal.md` владеет Topic State, Active Block, Block Status и Mastery Level;
- `Sources.md` владеет Source Records и Source Check Result;
- `Questions.md` владеет Question State и Card Candidate status;
- Card Promotion требует понимания, ценности, Card Trace, Duplicate Check в Obsidian и Anki и решения `skip`, `replace`, `merge` или `add`;
- Knowledge Consolidation переносит только curated Knowledge, а не raw Session Notes;
- `needs-check` и `Нужно проверить` блокируют Card Promotion и Knowledge Consolidation, если claim нужен для переносимого знания или карточки;
- lightweight checker является read-only validator и сам ничего не меняет;
- система использует human-first Markdown и не вводит YAML/JSON machine-readable schema.

## Решение

Первая версия write automation проектируется как Orchestrator-controlled write workflow с обязательным dry-run preview.

Workflow покрывает два независимых write target:

```text
Anki write      -> фактическое создание или изменение карточки после Card Promotion
Obsidian write  -> фактическая запись consolidated Knowledge в Long-Term Knowledge Base
```

Оба направления входят в первую версию как один общий workflow, потому что они используют общие gates: Source Check, Duplicate Check, traceability, user approval и idempotency/re-run safety. При этом каждый write target может быть выполнен или отложен отдельно.

## Назначение write automation

Write automation выполняет только уже принятое решение:

- создать новую Anki-карточку;
- заменить или объединить существующую Anki-карточку;
- добавить curated Knowledge в существующую Obsidian note;
- создать новую Obsidian note, если сильного существующего места нет;
- заменить или объединить секцию Obsidian note;
- зафиксировать durable trace и write outcome в Topic Workspace.

Write automation не решает, нужно ли учить материал, ценна ли карточка, достаточно ли понимание, какой claim проверен, является ли дубль сильным или можно ли закрыть тему. Эти решения принимает Learning Orchestrator до записи, используя предложения supporting agents и существующие gates.

## Входные артефакты

Write automation читает:

- `Goal.md` - Topic, Active Block, Completion Criteria, gate context и краткие ссылки на readiness;
- `Knowledge.md` - curated Knowledge, готовое к Knowledge Consolidation;
- `Questions.md` - Card Candidates, Card Trace, Duplicate Check, Promotion Decision и write outcome по карточкам;
- `Sources.md` - Source Records и Source Check Result;
- `Practice.md`, `Weaknesses.md`, `RepetitionLog.md` - evidence для ценности карточки или знания;
- optional `sessions/*.md` - только как context/evidence, если на него уже ссылаются основные артефакты;
- `topics/INDEX.md` - только для навигации к Topic Workspace;
- Obsidian vault - для target notes и проверки фактического места записи;
- Anki - для target deck/note/card и проверки фактического результата записи.

`topics/INDEX.md` не становится владельцем учебного состояния. Archive files не становятся владельцами evidence gates.

## Кто запускает запись

Фактическую write automation запускает только Learning Orchestrator.

Supporting agents не пишут в Obsidian или Anki напрямую. Они могут:

- подготовить Agent Proposal;
- предложить Card Promotion action;
- предложить Knowledge Consolidation action;
- подготовить текст карточки или фрагмент Obsidian note;
- приложить Duplicate Check results;
- указать risks, target candidates и exact insertion text.

Будущая slash command или ручной пользовательский запуск допустимы только как интерфейс к Orchestrator-controlled workflow. Такой запуск не должен обходить gates и не дает supporting agent прав внешней записи.

## User approval

Обязательный user approval нужен:

- перед любым write после dry-run preview;
- для `replace` в Anki;
- для `merge` в Anki;
- для изменения существующей Anki-карточки;
- для изменения существующей Obsidian note;
- для `merge` или `replace-section` в Obsidian;
- если Duplicate Check нашел сильный дубль;
- если target deck, note type, tags, Obsidian path или target note выглядят неоднозначно;
- если карточка может изменить уже привычную формулировку пользователя.

Для `add` новой Anki-карточки или новой Obsidian note не требуется отдельный approval сверх обязательного dry-run preview, если:

- Duplicate Check не нашел сильный дубль;
- Source Check gates пройдены;
- preview ясно показывает target, действие, текст и trace;
- пользователь подтвердил preview.

Если пользователь не подтверждает preview, write automation оставляет pending write decision и не меняет внешние системы.

## Dry-run / preview contract

Dry-run обязателен для первой версии.

Preview должен показать:

- Topic Workspace и source entity: `Q-*` для Anki или Knowledge section для Obsidian;
- write target: Anki или Obsidian;
- action: `add`, `replace`, `merge`, `skip`, `append`, `replace-section` или `pending`;
- target deck, note type, fields и tags для Anki;
- target Obsidian path, target note и target section для Obsidian;
- полный proposed front/back или cloze text для Anki;
- proposed Obsidian fragment или section replacement;
- Duplicate Check summary по Obsidian и Anki;
- Source Check summary и blocking `needs-check`, если есть;
- Card Trace или Knowledge Consolidation trace;
- expected Markdown updates в Topic Workspace после успешной записи;
- unavailable targets, если они есть;
- failure/recovery plan для частичной записи.

Dry-run не меняет Anki, Obsidian или Topic Workspace. Он создает только human-readable preview в текущей Codex-сессии или в будущем явном preview artifact, если отдельный implementation ticket это решит.

## Правила записи в Anki

Anki write разрешен только после Card Promotion decision.

Перед записью должны быть выполнены gates:

- материал понят пользователем;
- карточка проверяет одну извлекаемую единицу знания;
- ответ короткий и самопроверяемый;
- Card Trace есть в `Questions.md`;
- Obsidian Duplicate Check выполнен;
- Anki Duplicate Check выполнен и Anki доступен;
- Source Check gates пройдены для чувствительных claims;
- принято решение `add`, `replace`, `merge` или `skip`;
- dry-run preview подтвержден пользователем.

Deck, note type, tags и fields выбираются так:

- Learning Profile задает defaults;
- похожие Anki-карточки могут подсказать существующую convention;
- dry-run preview показывает итоговый выбор;
- пользователь подтверждает preview перед записью.

Жесткое глобальное правило для deck/note type/tags не вводится. Полностью ручной выбор каждого поля тоже не является базовым режимом первой версии.

После успешной записи `Questions.md` получает trace outcome:

- `Anki Deck`;
- `Anki Note Type`;
- `Anki Note ID`;
- `Anki Card IDs`, если доступны;
- `Tags`;
- `Written At`;
- `Write Action`;
- `Write Result`;
- `Source Question`;
- `Source Knowledge` или другой source entity;
- `Duplicate Check`;
- краткий reason, если был `replace` или `merge`.

Эти строки остаются обычным human-first Markdown внутри Question record. Они не являются YAML/JSON machine-readable schema.

## Правила записи в Obsidian

Obsidian write разрешен только после Knowledge Consolidation decision.

Перед записью должны быть выполнены gates:

- фрагмент является curated Knowledge, а не raw Session Note;
- knowledge подтверждено practice, repetition, Weakness correction или Source Check;
- похожие Obsidian notes проверены;
- выбран action: `skip`, `append`, `merge`, `replace-section` или `add`;
- чувствительные claims, нужные для переносимого knowledge, имеют verified Source Record;
- `Нужно проверить` по такому claim оставляет Obsidian write в `pending`, пока claim не будет проверен или исключен из переносимого фрагмента;
- lightweight checker не сообщает blocking finding для Knowledge Consolidation;
- dry-run preview подтвержден пользователем.

Obsidian path выбирается в таком порядке:

1. Существующая профильная note по Subject, Topic или Learning Profile, если она является естественным местом для знания.
2. Новая note по Subject/Topic, если сильного существующего места нет.
3. Временный inbox только при неопределенности target path, когда запись в основную note была бы рискованной.

Knowledge Consolidation не должна делать Obsidian копией `Knowledge.md`. Переносятся только короткие объяснения, исправленные заблуждения, риски применения, связи с проектом, компактные примеры и source/date context, если они помогают долговременному знанию.

После успешной записи `Knowledge.md` получает consolidation trace:

- Obsidian target path;
- target note и section;
- write action;
- written at;
- source Knowledge section;
- linked evidence;
- Duplicate Check summary;
- Source Check summary;
- write result.

`Goal.md` может ссылаться на результат консолидации только кратко, если это влияет на готовность темы или Completion Criteria. `Goal.md` не хранит тело Obsidian note.

## Правила `add`, `replace`, `merge`, `skip`

Для Anki:

| Action | Правило |
|---|---|
| `add` | Создать новую карточку, если сильного дубля нет и preview подтвержден. |
| `replace` | Изменить существующую карточку, если она проверяет ту же единицу знания, но формулировка устарела, ошибочна или плохо помогает recall. Требует отдельного user approval. |
| `merge` | Объединить новый материал с существующей карточкой, если пересечение частичное и новая формулировка лучше сохраняет одну retrievable unit. Требует отдельного user approval. |
| `skip` | Не писать в Anki, если существующая карточка или note уже покрывает материал без добавленной ценности. |

Для Obsidian:

| Action | Правило |
|---|---|
| `add` | Создать новую note, если сильного смыслового места в существующих notes нет. |
| `append` | Добавить отдельный пример, риск, связь с проектом или уточнение в существующую note. |
| `merge` | Свести пересекающиеся объяснения в одну секцию. Требует user approval. |
| `replace-section` | Заменить устаревшую или ошибочную секцию. Требует user approval. |
| `skip` | Не писать в Obsidian, если существующая note уже покрывает материал достаточно хорошо. |

`replace` и `merge` не должны стирать историю бесследно. Минимально нужно сохранить target identity, reason и source trace в Topic Workspace. Для Obsidian желательно оставить короткую change note рядом с измененной секцией, если это не засоряет долговременную note.

## Unavailable mode

Недоступность Obsidian или Anki является нормальным состоянием workflow.

Если доступен только один target:

- доступный write target можно выполнить, если его gates пройдены и preview подтвержден;
- недоступный target остается pending write;
- Topic Workspace фиксирует pending write reason и next action;
- Card Candidate не получает `promoted`, если Anki недоступен;
- Knowledge Consolidation не считается выполненной, если Obsidian write не произошел.

Если запись во внешний target невозможна:

- решение не теряется;
- proposed text и trace остаются в Topic Workspace или preview context;
- следующий запуск должен повторить availability check и stale Duplicate Check review перед записью.

Недоступность внешней системы не разрешает создавать карточку или note "по памяти" без фактической проверки target.

## Idempotency и re-run safety

Повторный запуск write automation должен быть безопасным.

Главный idempotency guard в первой версии - human-first trace в Topic Workspace:

- stable source entity: `Q-*` для Anki или Knowledge section для Obsidian;
- write action;
- write target;
- target identity после записи;
- write result;
- written at;
- Duplicate Check summary;
- Source Check summary;
- user approval note или ссылка на подтвержденный preview, если такой artifact существует.

При re-run automation сначала ищет существующий trace:

- если target identity уже записан и внешний target существует, повторная запись становится no-op;
- если trace есть, но внешний target не найден, нужен reconciliation preview;
- если внешний target есть, но trace в Topic Workspace отсутствует, нужен reconciliation preview перед восстановлением trace;
- если proposed text изменился после предыдущего preview, нужен новый dry-run и user approval;
- если Duplicate Check устарел или неполон, запись блокируется до повторной проверки.

Re-run safety не требует YAML/JSON schema. Проверка строится на стабильных ID, Markdown headings, bullet fields и внешних target IDs.

## Где хранится trace после записи

Trace хранится в комбинации:

- `Questions.md` - Card Trace, Promotion Decision, Anki write outcome и pending/failed state по карточке;
- `Knowledge.md` - Knowledge Consolidation trace и Obsidian write outcome;
- `Goal.md` - только краткие ссылки на readiness/outcome, если это влияет на Topic State, Completion Criteria или next action;
- Anki card fields/tags - минимальная обратная ссылка на Topic/Question/Knowledge, если note type и поля это позволяют;
- Obsidian note - короткая обратная ссылка на Topic Workspace или source Knowledge section, если это не портит читаемость note.

Отдельный write log artifact не входит в первую версию. Его можно спроектировать позже, если audit/reconciliation станет слишком тяжелым для `Questions.md` и `Knowledge.md`.

## Обязательные checks перед записью

Перед фактической записью Learning Orchestrator запускает или проверяет:

1. Lightweight checker для Topic Workspace и gate impact.
2. Source Check gates в `Sources.md`.
3. Duplicate Check results по Obsidian и Anki, если action связан с Card Promotion.
4. Obsidian Duplicate Check для Knowledge Consolidation.
5. Dry-run preview.
6. User approval.
7. Availability check для нужного write target.
8. Re-run/idempotency check по существующему trace.

Если любой blocking check не пройден, write automation не выполняет внешнюю запись и оставляет pending write decision с next action.

## Как Learning Orchestrator использует результат

После write automation Learning Orchestrator:

- обновляет `Questions.md`, если Anki write выполнен, отложен или провален;
- обновляет `Knowledge.md`, если Obsidian write выполнен, отложен или провален;
- обновляет `Goal.md` только если результат меняет next action, readiness, Completion Criteria или Topic handoff;
- оставляет Card Candidate в `candidate`, если Anki write не выполнен;
- не считает Knowledge Consolidation выполненной, если Obsidian write не выполнен;
- создает next action для pending/failed writes;
- не закрывает Topic как `completed`, если обязательная консолидация или карточка заблокирована действующими gates.

Write outcome не заменяет Completion Evidence. Карточка в Anki и note в Obsidian помогают долговременной работе, но Mastery Level по-прежнему требует practice, recall, transfer, repetition и отсутствие blocker Weakness.

## Видимые failure modes

Следующие сбои должны быть видимы в Topic Workspace:

- Obsidian write succeeded, Anki write failed;
- Anki write succeeded, Obsidian write failed;
- external write succeeded, but Topic Workspace trace update failed;
- Topic Workspace trace exists, but external target is missing;
- target note/card changed since dry-run preview;
- Duplicate Check result became stale before write;
- Source Check changed from `verified` to `needs-check`, `rejected` or `superseded`;
- merge conflict in Obsidian note;
- Anki deck, note type or fields unavailable;
- user rejected preview;
- user approved only one target;
- supporting agent attempted external write without Orchestrator control.

Write outcome uses human-readable states:

```text
succeeded
partial
failed
pending
no-op
```

These states are plain Markdown values, not machine-readable schema.

## Что остается вне первой версии

Первая версия не включает:

- конкретный CLI design;
- API clients для Obsidian или Anki;
- parser internals;
- background jobs;
- auto-fix;
- полноценную двустороннюю синхронизацию;
- массовую миграцию notes или cards;
- отдельный write log artifact;
- реализацию checker;
- реализацию slash commands;
- создание `.codex/agents/*.toml`;
- реальные Obsidian notes;
- реальные Anki cards;
- новые учебные темы;
- финальный `learning-system-spec.md`;
- YAML/JSON machine-readable schema.

## Отношение к human-first Markdown

Write automation не вводит YAML/JSON machine-readable schema.

Первая версия опирается на уже принятые conventions:

- stable IDs;
- Markdown headings;
- Markdown links;
- bullet fields внутри records;
- owner files для состояний и результатов;
- human-readable preview;
- human-readable write outcome.

Если этих conventions позже окажется недостаточно для надежной автоматизации записи, Machine-Readable Layer должен быть спроектирован отдельным decision ticket. До такого решения write automation не должна превращать Topic Workspace в YAML/JSON-backed data store.

## Обоснование

Обязательный dry-run preview снижает риск испортить Anki или Obsidian и делает user approval осмысленным: пользователь видит target, action, текст, trace и последствия до записи.

Orchestrator-controlled workflow сохраняет single-writer state model. Supporting agents могут готовить сильные proposals, но не получают права напрямую менять внешние долговременные хранилища.

Одновременное проектирование Anki и Obsidian write нужно, потому что карточки и consolidated Knowledge используют один источник evidence и часто один Duplicate Check context. Разделение на независимые write targets позволяет нормально переживать unavailable mode и частичные сбои.

Trace в Topic Workspace делает handoff и re-run safety возможными без машинной схемы. Внешние IDs полезны, но они не заменяют учебный trace: система должна знать, из какого вопроса, знания, практики или слабого места появилась карточка или note.

## Последствия

- Будущие lifecycle commands должны вызывать write automation только через Learning Orchestrator.
- Будущие Agent Files должны запретить supporting agents прямую запись в Obsidian и Anki.
- Future checker может проверять write outcome и pending writes, но остается read-only.
- Future implementation ticket должен отдельно спроектировать CLI/API details, если они понадобятся.
- `Questions.md` и `Knowledge.md` становятся основными местами trace outcome для внешней записи.
- `Goal.md` остается владельцем Topic State, Active Block, Block Status и Mastery Level.
- `Sources.md` остается владельцем Source Check Result.
- `Questions.md` остается владельцем Question State и Card Candidate status.

## Вне области

Это решение не делает:

- реальную запись в Obsidian;
- реальную запись в Anki;
- создание Anki-карточек;
- изменение Obsidian vault;
- automation scripts;
- slash commands;
- `.codex/agents/*.toml`;
- новые Topic Workspaces;
- расширение prototype темы;
- RabbitMQ source verification;
- checker implementation;
- финальный `learning-system-spec.md`;
- YAML/JSON machine-readable schema.

## Следующие тикеты

1. `Assemble Learning System Specification`
2. Будущий implementation ticket для write automation, если после спецификации решено переходить к реализации.
3. Будущий command/API ticket, если нужен конкретный CLI или slash command.

## Критерии завершения

Это решение считается закрытым, когда:

- назначение write automation описано;
- входные артефакты перечислены;
- запуск записи закреплен за Learning Orchestrator;
- user approval rules зафиксированы;
- dry-run preview contract описан;
- правила записи в Anki и Obsidian описаны;
- правила `add`, `replace`, `merge`, `skip` описаны;
- unavailable mode описан;
- idempotency/re-run safety описаны;
- trace outcome размещен по owner files;
- обязательные checks перед записью описаны;
- использование результата Learning Orchestrator описано;
- failure modes видимы;
- out of scope первой версии перечислен;
- YAML/JSON machine-readable schema не введена;
- карта wayfinder обновлена.
