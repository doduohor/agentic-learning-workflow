# Запись решения: lightweight checker для Entity References и ID

## Статус

Принято.

## Контекст

Topic Workspace остается human-first Markdown. Система уже приняла:

- `topics/INDEX.md` является навигационным индексом, но не владельцем учебного состояния;
- `Goal.md` владеет Topic State, Active Block, Block Status и Mastery Level;
- `Knowledge.md` хранит curated Knowledge, а не raw Session Notes;
- `Practice.md` хранит structured Practice Attempts и evidence;
- `Questions.md` владеет Question State и Card Candidate status;
- `Weaknesses.md` владеет Weakness Status, severity, repair action и resolution evidence;
- `RepetitionLog.md` владеет Active Repetition records и results;
- `Sources.md` владеет Source Records и Source Check Result;
- optional `sessions/` хранит длинные Session Notes и Practice Artifacts;
- sensitive claims с `needs-check` или `Нужно проверить` не используются как подтвержденные evidence для closing gates.

Prototype Topic Workspace показал, что ручная проверка cross-file links, ID и ownership-инвариантов быстро становится заметной работой. При этом система не должна вводить YAML/JSON machine-readable schema только ради проверки.

## Решение

Спроектировать lightweight checker как read-only validator для Topic Workspace и `topics/INDEX.md`.

Checker читает human-first Markdown, строит легкий inventory сущностей по Markdown headings, таблицам-индексам, ID-паттернам и Markdown-ссылкам, а затем возвращает текстовый отчет о нарушениях. Он не меняет файлы, не принимает учебные решения и не создает новые артефакты.

В первой версии checker может быть реализован как строго read-only. Decision допускает будущий режим текстовых repair hints, но не допускает auto-fix без отдельного решения.

Checker помогает Learning Orchestrator и supporting agents увидеть:

- битые Markdown-ссылки;
- отсутствующие target headings;
- неверные ID formats;
- stale references;
- рассинхрон между index tables и detailed records;
- нарушение владельцев состояния;
- gate-blocking `needs-check`;
- Card Candidate promotion без нужных проверок;
- archive links, которые потеряли linked evidence.

Checker не решает, выучена ли тема. Он только сообщает, какие structural, traceability или gate инварианты нарушены. Решение о переходе состояния, продвижении карточки, консолидации знания или исправлении файла принимает Learning Orchestrator.

## Что checker читает

Для `topics/INDEX.md` checker читает:

- таблицу `## Topics`;
- `Topic Workspace`;
- ссылку на `Goal.md`;
- `Stable Slug`;
- `Topic State`;
- `Subject`;
- `Parent Topic`;
- `Related Subjects`.

Для одной Topic Workspace checker читает:

- `Goal.md`;
- `Knowledge.md`;
- `Practice.md`;
- `Questions.md`;
- `Weaknesses.md`;
- `RepetitionLog.md`;
- `Sources.md`;
- optional `sessions/*.md`;
- companion artifact files, если на них есть Markdown-ссылки из `Practice.md` или archive files.

Checker не обязан читать Obsidian, Anki, интернет, внешнюю документацию или issue tracker. Он может видеть следы этих проверок только через Markdown-поля, уже записанные в Topic Workspace.

## Что checker не меняет

Checker не выполняет:

- auto-fix;
- запись в Markdown-файлы;
- изменение Topic State, Active Block, Block Status или Mastery Level;
- изменение Source Check Result;
- Card Promotion;
- Knowledge Consolidation;
- Source Verification;
- Duplicate Check в Obsidian или Anki;
- создание `sessions/`;
- создание `.codex/agents/*.toml`;
- запуск slash commands.

Если checker умеет показывать repair hints, они остаются текстовыми подсказками в отчете. Применяет их только Learning Orchestrator или другой явно разрешенный writer.

## Уровни результата

Отчет использует две человекочитаемые оси.

Severity:

- `error` - нарушение структурного, ownership или gate-инварианта;
- `warning` - вероятный рассинхрон, stale reference, raw dump smell или неполная draft-связность, которая пока не блокирует gate;
- `info` - заметка о состоянии, например pending `needs-check`, draft orphan или optional archive absence.

Gate impact:

- `blocks production-ready`;
- `blocks completed`;
- `blocks card-promotion`;
- `blocks knowledge-consolidation`;
- `blocks handoff`;
- `does not block`.

Эти уровни являются форматом текстового отчета, а не новой machine-readable schema. Один finding может быть, например:

```text
error, blocks completed: Goal.md has Topic State `completed`, but Sources.md contains SRC-20260824-01 with Result `needs-check` used by Completion Criteria.
```

## Обязательные проверки по `topics/INDEX.md`

Checker должен проверять:

- каждая строка `## Topics` с Topic Workspace указывает на существующий каталог;
- каждый Topic Workspace находится по пути `topics/<subject>/<stable-slug>/`;
- каждый `Goal` ведет на существующий `Goal.md`;
- `Stable Slug` в индексе совпадает со `Stable Slug` в `Goal.md`;
- `Topic Workspace` в индексе совпадает с `Topic Workspace` в `Goal.md`;
- `Topic State` в индексе не противоречит `Topic State` в `Goal.md`; расхождение является warning, потому что `Goal.md` остается источником истины;
- `Stable Slug` не дублируется между Topic Workspaces;
- один и тот же Topic Workspace не дублируется несколькими строками;
- `Parent Topic`, если указан, ссылается на существующую Topic;
- `Related Subjects` не создают второй физический Topic Workspace для той же Topic.

Индекс не становится владельцем Topic State. Checker использует его как навигационный кэш и указывает, когда кэш устарел.

## Обязательные проверки по `Goal.md`

Checker должен проверять:

- присутствует header с Topic, Stable Slug, Topic Workspace, Topic State и Active Block;
- Topic State использует принятое значение;
- Active Block либо `-`, либо Entity Reference на существующий Block в `Goal.md`;
- каждый Block ID имеет формат `BNN`;
- Block IDs уникальны внутри Learning Map;
- required Blocks явно отмечены как `required`;
- Mastery Level использует принятое значение;
- Block Status использует принятое значение;
- Evidence и Open Weaknesses ссылаются на существующие сущности или равны `-`;
- Completion Criteria не ссылаются на отсутствующие evidence;
- Topic State `completed` не стоит при открытом blocker Weakness, required Block ниже `stable` или blocking `needs-check`;
- Block не имеет `production-ready`, если обязательный sensitive claim для этого уровня остается `needs-check`;
- `Goal.md` остается единственным владельцем Topic State, Active Block, Block Status и Mastery Level.

Во время ранних состояний `intake`, `diagnosing`, `planned`, `learning` checker допускает неполную evidence-связность как warning, если она не используется для gate.

## Обязательные проверки по `Knowledge.md`

Checker должен проверять:

- `Knowledge.md` ссылается на правильный `Goal.md`;
- Stable Slug совпадает с `Goal.md`;
- каждый Block reference ведет на существующий `B*` в `Goal.md`;
- `SRC-*` references ведут на существующие Source Records в `Sources.md`;
- `Нужно проверить` рядом с sensitive claim имеет связанный `SRC-*`, если claim используется вне локального чернового контекста;
- `Knowledge.md` не содержит явных владельческих полей Topic State, Active Block, Block Status или Mastery Level;
- `Knowledge.md` не содержит Source Check Result как владельческое поле;
- большие raw Session Notes, длинные terminal logs, copied source dumps или archive copy выглядят как warning.

Checker не оценивает полноту объяснения, педагогическое качество Knowledge или глубину понимания.

## Обязательные проверки по `Practice.md`

Checker должен проверять:

- каждый `PA-*` имеет формат `PA-YYYYMMDD-NN`;
- `PA-*` в Practice Attempt Index имеет соответствующий detailed record;
- detailed record `PA-*` не дублирует другой `PA-*`;
- Linked Block ведет на существующий `B*` в `Goal.md`;
- Result использует принятое значение;
- Linked Weaknesses ведут на существующие `W-*` или равны `-`;
- Promoted Knowledge links ведут на существующие headings в `Knowledge.md`;
- Follow-up Questions ведут на существующие `Q-*` в `Questions.md`;
- ссылки на `sessions/*.md` ведут на существующие archive files, если указаны;
- companion artifact files, упомянутые в Artifacts или archive links, существуют;
- `Practice.md` не владеет Topic State, Active Block, Block Status, Mastery Level, Question State, Weakness Status или Source Check Result.

Unchecked Practice Attempt допустима, пока она не используется как единственное evidence для повышения Mastery Level, `completed`, Card Promotion или Knowledge Consolidation.

## Обязательные проверки по `Questions.md`

Checker должен проверять:

- каждый `Q-*` имеет формат `Q-YYYYMMDD-NN`;
- `Q-*` в Question Index имеет соответствующий detailed record;
- Question Type использует принятое значение;
- Question State использует принятое значение;
- Card Candidate status использует принятое значение;
- Linked Block ведет на существующий `B*`;
- Answer/Attempt Link ведет на существующий `PA-*`, `REP-*` или другой допустимый target, если указан;
- Weakness Links ведут на существующие `W-*` или равны `-`;
- Source links ведут на существующие `SRC-*`, `Knowledge.md`, `Practice.md` или другой допустимый context target;
- `promoted` Card Candidate имеет Card Trace, Duplicate Check по Obsidian и Anki, Promotion Decision и отсутствие blocking `needs-check`;
- `candidate` Card Candidate может иметь неполный Duplicate Check, но checker должен сообщить warning, что promotion заблокирован до проверки;
- `Questions.md` не владеет Topic State, Active Block, Block Status, Mastery Level, Weakness Status или Source Check Result.

Checker не оценивает качество формулировки вопроса, атомарность Anki-карточки или учебную ценность Card Candidate.

## Обязательные проверки по `Weaknesses.md`

Checker должен проверять:

- каждый `W-*` имеет формат `W-YYYYMMDD-NN`;
- `W-*` в Weakness Index имеет соответствующий detailed record;
- Type, Severity и Status используют принятые значения;
- Linked Block ведет на существующий `B*`;
- open `major` или `blocker` Weakness имеет Repair Action;
- `resolved` Weakness имеет Resolution Evidence;
- Weakness Evidence ведет на существующий `PA-*`, `Q-*`, `REP-*`, interview answer reference или другой допустимый evidence target;
- Active Weakness Summary в `Goal.md` не пропускает открытые `blocker` Weaknesses;
- `Weaknesses.md` не владеет Topic State, Active Block, Block Status, Mastery Level, Question State или Source Check Result.

Draft risk без `W-*`, как `Risk Index Without Weakness Records`, допустим. Он не должен использоваться как evidence-backed Weakness и не должен закрывать или блокировать Block сам по себе.

## Обязательные проверки по `RepetitionLog.md`

Checker должен проверять:

- каждый `REP-*` имеет формат `REP-YYYYMMDD-NN`;
- `REP-*` в Repetition Queue имеет соответствующий detailed record;
- Target Type использует принятое значение;
- Target ведет на существующий `Q-*`, `B*` или `W-*` в соответствии с Target Type;
- Action использует принятое значение;
- Result использует принятое значение;
- `failed` или `partial` repetition имеет Failure Analysis или warning;
- `failed` repetition, который выявляет учебную проблему, связан с `W-*` или помечен warning для Orchestrator;
- `scheduled` repetition не должен иметь Completed At;
- `passed`, `partial`, `failed` или `missed` repetition должен иметь Completed At или объясняющий warning;
- `RepetitionLog.md` не владеет Topic State, Active Block, Block Status, Mastery Level, Question State, Weakness Status или Source Check Result.

Checker не выбирает интервалы повторения и не решает, что память стала stable.

## Обязательные проверки по `Sources.md`

Checker должен проверять:

- каждый `SRC-*` имеет формат `SRC-YYYYMMDD-NN`;
- `SRC-*` в Source Check Index имеет соответствующий detailed record;
- Sensitivity использует принятое значение;
- Authority Type использует принятое значение;
- Result использует `verified`, `rejected`, `needs-check` или `superseded`;
- `Used In` ведет на существующие сущности или равен `-`;
- `needs-check` Source Record не используется как подтвержденное evidence для `production-ready`, `completed`, Card Promotion или Knowledge Consolidation;
- `superseded` Source Record указывает в Notes или Next Check, чем он вытеснен или где продолжать проверку;
- другие артефакты не удалили `Нужно проверить`, если связанный `SRC-*` остается `needs-check`;
- `Sources.md` остается единственным владельцем Source Check Result.

Checker не выполняет Source Verification и не оценивает достаточность источника по содержанию внешней страницы.

## Обязательные проверки по `sessions/` archive files

Если `sessions/` отсутствует, это не ошибка.

Если archive files существуют, checker должен проверять:

- каждый archive file находится по пути `sessions/YYYY-MM-DD-<short-slug>.md`;
- ссылки из `Practice.md` на archive files ведут на существующие файлы;
- archive file содержит ссылку на Topic через `../Goal.md`;
- archive file содержит хотя бы одну ссылку на связанную сущность: `PA-*`, `Q-*`, `W-*`, `SRC-*` или `B*`;
- каждый `PA-*`, упомянутый archive file, существует в `Practice.md`;
- каждый `Q-*`, `W-*` или `SRC-*`, упомянутый archive file, существует в своем владельческом файле;
- companion artifact files, упомянутые в archive file или `Practice.md`, существуют;
- archive file не содержит явных владельческих полей Topic State, Block Status, Mastery Level, Question State, Weakness Status или Source Check Result;
- sensitive `Нужно проверить` в archive file имеет связанный `SRC-*`, если claim используется вне archive file.

Archive file не может быть единственным прямым evidence для `production-ready`, `completed`, Card Promotion или Knowledge Consolidation. Для gate нужна основная сущность: Practice Attempt, Question, Weakness, Repetition или Source Record.

## Draft Orphan rules

Draft Orphan допустим, если сущность еще не используется как основание для другого решения.

Допустимо:

- `draft` Question без Answer/Attempt Link;
- Card Candidate со статусом `candidate`, у которого Duplicate Check еще не завершен;
- risk entry без `W-*`, пока нет Weakness Evidence;
- archive file с follow-up notes, которые еще не перенесены в основные артефакты.

Становится warning:

- bare ID без Markdown-ссылки в значимой связи;
- draft сущность, на которую уже ссылается другой файл;
- Card Candidate без полного Card Trace;
- archive note с follow-up, который долго не перенесен в основные артефакты.

Становится error:

- active, answered, failed, promoted или archived Question с битой обязательной ссылкой;
- `promoted` Card Candidate без Duplicate Check, Card Trace или Promotion Decision;
- Weakness без evidence;
- `resolved` Weakness без Resolution Evidence;
- Repetition target без существующей целевой сущности;
- Completion Evidence, которое ведет на missing target;
- любой orphan, используемый для `production-ready`, `completed`, Card Promotion или Knowledge Consolidation.

## Gate-проверки

### `production-ready`

Checker сообщает `error, blocks production-ready`, если:

- Block не имеет существующего evidence для applied или transfer understanding;
- связанный sensitive claim остается `needs-check`;
- linked blocker Weakness остается open, repairing или retest-needed;
- required Practice Attempt имеет Result `unchecked`, `failed` или `rework-needed`;
- evidence link ведет на missing target.

### `completed`

Checker сообщает `error, blocks completed`, если:

- Topic State равен `completed`, но не все required Blocks имеют Mastery Level `stable`;
- есть открытый `blocker` Weakness;
- Completion Criteria ссылаются на missing evidence;
- Completion Criteria зависят от `SRC-*` с Result `needs-check` или `rejected`;
- есть failed или missed Active Repetition, который должен открыть Weakness, но не связан с ним;
- `topics/INDEX.md` указывает другой Topic State и не обновлен после `Goal.md`.

### Card Promotion

Checker сообщает `error, blocks card-promotion`, если Card Candidate имеет статус `promoted`, но:

- нет Card Trace;
- Duplicate Check не упоминает Obsidian и Anki;
- Promotion Decision отсутствует;
- связанный sensitive claim остается `needs-check`;
- trace ведет на missing Knowledge, Practice Attempt, Weakness, Source Record или Question.

Для статуса `candidate` эти же проблемы являются warning, если promotion еще не произошел.

### Knowledge Consolidation

Checker сообщает `error, blocks knowledge-consolidation`, если переносимый Knowledge:

- содержит sensitive claim без verified Source Record или явной `Нужно проверить`;
- ссылается на missing Practice Attempt, Question, Weakness или Source Record;
- выглядит как raw Session Note, copied source dump или archive copy;
- зависит от unresolved blocker Weakness;
- не имеет trace к Topic Workspace evidence.

Checker не выполняет реальную запись в Long-Term Knowledge Base.

## Кто запускает checker

Checker является общим guardrail.

Learning Orchestrator запускает его:

- перед `production-ready`;
- перед `completed`;
- перед Card Promotion;
- перед Knowledge Consolidation;
- после сложной правки, которая затрагивает несколько файлов;
- перед Topic Workspace Handoff, если есть риск потери связности.

Supporting agents могут запускать checker перед Agent Proposal или после своей append-only записи в разрешенном файле. Такой запуск не дает supporting agent права менять состояние.

Будущая slash command или ручной запуск допустимы, но это отдельный implementation или command ticket. В этом decision record фиксируется только роль checker в процессе.

## Как Learning Orchestrator использует результат

Learning Orchestrator читает отчет checker как evidence о состоянии файлов.

Правила:

- `error` с gate impact блокирует соответствующий gate до исправления или осознанного изменения решения;
- `warning` требует review, но не всегда блокирует текущую учебную работу;
- `info` помогает handoff и планированию;
- checker findings не применяются автоматически;
- если checker и текстовые артефакты расходятся, Orchestrator проверяет владельческий файл: `Goal.md` для учебного состояния и `Sources.md` для Source Check Result;
- если finding спорный, Orchestrator может оставить явную note или отдельный future ticket, но не скрывает blocking error при закрытии темы.

## Что остается вне первой версии

Первая версия checker не включает:

- реальную реализацию checker;
- CLI-дизайн;
- parser internals;
- auto-fix;
- YAML/JSON machine-readable schema;
- отдельный Machine-Readable Layer;
- source verification по интернету;
- Obsidian/Anki automation;
- Duplicate Check execution;
- создание Anki-карточек;
- оценку педагогического качества Knowledge, Questions или Practice;
- расчет Mastery Level;
- генерацию новых Topic Workspaces;
- `.codex/agents/*.toml`;
- slash commands;
- финальный `learning-system-spec.md`.

## Отношение к human-first Markdown

Checker не вводит YAML/JSON machine-readable schema.

Проверяемость строится на уже принятых conventions:

- устойчивые ID;
- Markdown headings;
- Markdown-ссылки;
- таблицы-индексы;
- короткие поля внутри records;
- owner files для состояний и результатов.

Если этих conventions позже окажется недостаточно, Machine-Readable Layer может быть спроектирован отдельным decision ticket. До этого checker должен работать с readable Markdown и не заставлять учебные файлы превращаться в данные ради автоматизации.

## Обоснование

Read-only checker защищает систему от наиболее вероятных поломок без нарушения single-writer state model. Он снижает ручную стоимость проверки ссылок и ID, но не становится вторым Learning Orchestrator.

Две оси результата нужны потому, что severity без gate impact мало помогает учебному процессу. Битая ссылка в draft вопросе и битая ссылка в Completion Evidence имеют разный вес. При этом отчет остается текстовым и человекочитаемым.

Смешанная политика по Draft Orphan сохраняет возможность думать черновиками. Сущность становится проблемой не потому, что она неполная, а потому что на нее уже опирается состояние, evidence, promotion или consolidation.

## Последствия

- Future implementation ticket может создать checker, опираясь на этот контракт.
- Future command ticket может решить, как запускать checker из slash command.
- Agent Files должны использовать checker как guardrail, но не как источник прав записи.
- Финальная спецификация должна включить checker как read-only validation layer для Topic Workspace.

Prototype Topic Workspace остается без изменений.

## Критерии завершения

Решение считается закрытым, когда:

- назначение checker описано;
- входные файлы перечислены;
- read-only граница зафиксирована;
- уровни результата и gate impact описаны;
- проверки по `topics/INDEX.md`, `Goal.md`, `Knowledge.md`, `Practice.md`, `Questions.md`, `Weaknesses.md`, `RepetitionLog.md`, `Sources.md` и `sessions/` описаны;
- Draft Orphan rules зафиксированы;
- gate-проверки для `production-ready`, `completed`, Card Promotion и Knowledge Consolidation описаны;
- роль Learning Orchestrator и supporting agents при запуске checker описана;
- вне scope первой версии явно перечислено;
- YAML/JSON machine-readable schema не введена.
