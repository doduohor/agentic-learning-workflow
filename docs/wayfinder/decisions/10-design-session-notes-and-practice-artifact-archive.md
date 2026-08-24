# Запись решения: архив Session Notes и Practice Artifacts

## Статус

Принято.

## Контекст

Topic Workspace уже разделяет устойчивые учебные артефакты:

```text
Goal.md
Knowledge.md
Practice.md
Questions.md
Weaknesses.md
RepetitionLog.md
Sources.md
```

Уже принято:

- `Goal.md` владеет Topic State, Active Block, Block Status и Mastery Level;
- `Knowledge.md` хранит curated Knowledge, а не сырой лог сессии;
- `Practice.md` хранит Practice Journal: структурированные Practice Attempts, feedback, corrections, evidence и ссылки;
- `Sources.md` владеет Source Records и Source Check Result;
- Topic Workspaces живут по пути `topics/<subject>/<stable-slug>/`;
- система использует human-first Markdown и не вводит YAML/JSON machine-readable schema.

Prototype Topic Workspace показал, что раздел `Session Archive Links` в маленькой теме выглядит рано, но остается понятным местом для будущего роста. Теперь нужно решить, куда убирать длинные Session Notes, команды, выводы терминала, схемы, SQL, Docker files, кодовые фрагменты и промежуточные материалы, чтобы они не засоряли `Knowledge.md` и не раздували `Practice.md`.

## Решение

Внутри каждой Topic Workspace допускается optional per-topic каталог:

```text
topics/<subject>/<stable-slug>/sessions/
```

Каталог `sessions/` создается только когда есть реальный материал для архивации. Пустой placeholder не нужен.

Основной archive file имеет путь:

```text
topics/<subject>/<stable-slug>/sessions/YYYY-MM-DD-<short-slug>.md
```

Пример:

```text
topics/rabbitmq/retry-without-idempotency/sessions/2026-08-24-retry-safety-sketch.md
```

Archive file соответствует одной learning Session. Один archive file может ссылаться на несколько Practice Attempts, Questions, Weaknesses, Sources и Blocks, если они появились в этой Session.

`Practice.md` остается основным Practice Journal. В нем остаются:

- короткая structured Practice Attempt entry;
- Practice Attempt ID;
- дата Session;
- linked Block;
- prompt/task;
- краткое тело попытки, если оно не раздувает файл;
- result;
- feedback;
- corrections;
- linked Weaknesses;
- promoted Knowledge links;
- follow-up Questions;
- ссылки на archive file и Practice Artifacts.

Длинный сырой материал выносится в `sessions/`, если он иначе сделал бы `Practice.md` шумным или тяжелым для чтения.

## Где живут Session Notes

Краткие Session Notes, которые напрямую объясняют Practice Attempt и помещаются в короткую запись, могут оставаться в `Practice.md`.

Длинные или сырые Session Notes живут в archive file:

```text
sessions/YYYY-MM-DD-<short-slug>.md
```

К таким notes относятся:

- сырой ход рассуждения сессии;
- длинный ответ learner;
- промежуточные черновики;
- команды и выводы терминала;
- разбор нескольких вариантов решения;
- подробный failure analysis, который слишком длинный для `Practice.md`;
- материал, который полезен как historical evidence, но еще не является Knowledge.

Session Note не является Knowledge. Если из него появляется устойчивое понимание, Learning Orchestrator переносит очищенный фрагмент в `Knowledge.md` и оставляет ссылку на evidence.

## Где живут Practice Artifacts

Practice Artifact может жить:

- как короткая Markdown-ссылка внутри `Practice.md`, если artifact уже находится в устойчивом месте;
- внутри archive file, если artifact представлен текстом, командным выводом, коротким SQL, Docker Compose fragment, схемой или логом;
- отдельным файлом рядом с archive file в `sessions/`, если это реально нужно для читаемости или запуска.

Для отдельных файлов используется тот же date/short-slug prefix:

```text
sessions/YYYY-MM-DD-<short-slug>.<kind>.<ext>
```

Примеры:

```text
sessions/2026-08-24-retry-safety-sketch.sql
sessions/2026-08-24-retry-safety-sketch.consumer.kt
sessions/2026-08-24-retry-safety-sketch.log
```

Отдельный `Artifact ID` не вводится. Для traceability достаточно существующих ID:

- `PA-*` для Practice Attempt;
- `Q-*` для Question;
- `W-*` для Weakness;
- `SRC-*` для Source Record;
- `B*` для Block;
- Markdown-ссылок на archive file или companion files.

## Когда создавать archive file

Archive file создается только при наличии практической причины.

Создавать archive file нужно, если Session содержит:

- длинный сырой learner answer;
- несколько связанных Practice Attempts;
- много команд или терминального вывода;
- логи, SQL, Docker files, кодовые фрагменты или схемы;
- подробный debugging/failure trace;
- source-sensitive гипотезы, которые нужно сохранить до Source Check;
- промежуточные материалы, которые полезны как evidence, но не должны попадать в `Knowledge.md`;
- риск потери traceability, если оставить только краткую запись в `Practice.md`.

Archive file не создается только ради единообразия. Обычные короткие Session Notes остаются в `Practice.md` как часть structured Practice Attempt.

## Что не должно попадать в Knowledge.md

В `Knowledge.md` не попадают:

- raw Session Notes;
- стенограммы чата;
- длинные terminal logs;
- полные команды и выводы, если они нужны только как trace;
- промежуточные черновики;
- большие SQL, Docker, Kotlin или другие code fragments;
- непроверенные sensitive claims без `Нужно проверить` и ссылки на `SRC-*`;
- копии archive files.

`Knowledge.md` получает только curated Knowledge: очищенное понимание, короткий пример, исправленное заблуждение, применимый риск или проверенное утверждение. Если знание пришло из archive file, оно ссылается на Practice Attempt, Question, Weakness или Source Record, а не копирует сырой архив.

## Минимальный формат archive file

Archive file использует human-first Markdown без YAML/JSON metadata.

Минимальный формат:

```md
# Session Archive - <short title>

## Session

- Date: `YYYY-MM-DD`
- Topic: [Goal.md](../Goal.md)
- Linked Blocks: [B01: <block>](../Goal.md#b01---<block>)
- Linked Practice Attempts: [PA-YYYYMMDD-01: <attempt>](../Practice.md#pa-yyyymmdd-01---<attempt>)
- Linked Questions: [Q-YYYYMMDD-01: <question>](../Questions.md#q-yyyymmdd-01---<question>) или `-`
- Linked Weaknesses: [W-YYYYMMDD-01: <weakness>](../Weaknesses.md#w-yyyymmdd-01---<weakness>) или `-`
- Linked Sources: [SRC-YYYYMMDD-01: <source>](../Sources.md#src-yyyymmdd-01---<source>) или `-`
- Why Archived: <короткая причина>

## Raw Notes

<сырой или lightly structured материал>

## Practice Artifacts

- <Markdown-ссылки на companion files или inline artifact sections>

## Extracted Follow-Ups

- Knowledge to curate: <ссылка/кратко или `-`>
- Questions to add: <ссылка/кратко или `-`>
- Weakness evidence: <ссылка/кратко или `-`>
- Source checks needed: <ссылка/кратко или `-`>

## Source Check Warnings

- <claims с `Нужно проверить` и ссылками на `SRC-*`, если есть>

## Notes After Curation

- <что перенесено, свернуто или исправлено позже>
```

Разделы можно оставлять с `-`, если они не применимы. Новые обязательные machine-readable поля не добавляются.

## Правила ссылок

`Practice.md`:

- является основным входом к archive file через раздел `Session Archive Links`;
- каждая Practice Attempt с вынесенным сырьем указывает archive file в поле `Артефакты (Artifacts)` или в связанных ссылках;
- индекс `Session Archive Links` хранит дату, ссылку, причину архивации и связанные `PA-*`.

`Questions.md`:

- может ссылаться на archive file только как на context/evidence для ответа, попытки или Card Trace;
- Question State остается в `Questions.md`, а не в archive file.

`Weaknesses.md`:

- может ссылаться на archive file как на дополнительный evidence context;
- Weakness ID, severity, status, repair action и resolution evidence остаются в `Weaknesses.md`.

`Sources.md`:

- может ссылаться на archive file как на место, где появился claim или raw source note;
- Source Check Result остается только в `Sources.md`.

`Goal.md`:

- может ссылаться на Practice Attempt, Question, Weakness или Source Record, которые в свою очередь ведут в archive file;
- не должен использовать archive file как прямого владельца Topic State, Block Status, Mastery Level или Completion Criteria.

Archive file:

- может ссылаться на `Goal.md`, `Practice.md`, `Questions.md`, `Weaknesses.md` и `Sources.md`;
- не владеет состояниями этих сущностей;
- не заменяет записи в основных артефактах.

## Права записи

Learning Orchestrator может:

- создавать `sessions/`;
- создавать archive files;
- обновлять ссылки из `Practice.md`;
- применять выводы из archive file в `Knowledge.md`, `Questions.md`, `Weaknesses.md`, `Sources.md` и `Goal.md`;
- сворачивать или помечать архивный материал после curation.

Practice Agent может:

- создать новый archive file или companion artifact file только в явном Role Mode и только если Learning Orchestrator дал практическое задание;
- дописать archive file для текущей Session;
- добавить ссылку на archive file в новую Practice Attempt, если пишет `Practice.md` в разрешенной append-only границе.

Source Agent может:

- ссылаться на archive file из `Sources.md`;
- добавлять Source Records в `Sources.md` в своих обычных границах;
- предлагать правки, если source-sensitive claim из archive file должен повлиять на `Knowledge.md` или `Goal.md`.

Question/Card Agent и Repetition Agent:

- могут читать archive files как context;
- могут ссылаться на archive file в proposal;
- не создают и не переписывают archive files без явного Role Mode и поручения Learning Orchestrator.

Если изменение archive file требует согласованных правок нескольких основных артефактов, supporting agent возвращает Agent Proposal.

## Append-only и редактирование

Raw sections archive file являются append-only после первичной записи. Исторический материал не переписывается задним числом.

Разрешено редактировать:

- ссылки и короткие summary-поля;
- `Extracted Follow-Ups`;
- `Source Check Warnings`;
- `Notes After Curation`;
- явные correction notes, если исходный raw material оказался ошибочным.

Если ошибка в raw material влияет на Knowledge, Weakness, Question, Source Check или Goal, исправление применяется в соответствующем основном артефакте через Learning Orchestrator. Archive file сохраняет исторический след и получает заметку о коррекции.

## Retention и pruning

Archive не должен становиться свалкой.

Правила:

- не создавать archive file для короткой Session, где structured Practice Attempt в `Practice.md` достаточна;
- не копировать в archive file весь чат, если достаточно короткой Session Note и ссылок;
- не хранить большие выводы без причины: сохранять только часть, которая объясняет evidence, failure или решение;
- не дублировать один и тот же artifact в `Practice.md`, archive file и companion file;
- не переносить в archive file curated Knowledge, если оно уже принадлежит `Knowledge.md`;
- оставлять raw historical evidence, пока на него ссылаются Practice Attempt, Weakness, Source Record, Question, Card Trace или Completion Evidence;
- после curation можно свернуть неиспользуемый raw material короткой заметкой в `Notes After Curation`, если это не ломает traceability;
- удаление raw material допустимо только если он не является evidence, не содержит pending `Нужно проверить`, не нужен для duplicate/card trace и его смысл уже сохранен в основных артефактах.

Для текущей версии предпочтительно оставлять historical evidence, а не агрессивно чистить архив. Pruning должен быть осознанным действием Learning Orchestrator, а не автоматической чисткой.

## Отношение к Source Check и `Нужно проверить`

Archive file может хранить непроверенные claims и сырой источник их появления.

Правила:

- archive file не подтверждает claim сам по себе;
- sensitive claim в archive file получает `Нужно проверить`, если используется дальше;
- если claim нужен в `Knowledge.md`, `Questions.md`, `Goal.md` или Card Trace, должен быть связанный `SRC-*` в `Sources.md`;
- Source Check Result живет только в `Sources.md`;
- `needs-check` из archive file не должен незаметно исчезать при переносе в curated Knowledge;
- archive file не может быть единственным основанием для `production-ready`, `completed`, Card Promotion или Knowledge Consolidation, если claim чувствительный.

## Требования к будущему lightweight checker

Этот ticket передает будущему lightweight checker только инварианты, не дизайн реализации.

Checker должен уметь проверять:

- ссылки из `Practice.md` на `sessions/*.md` ведут на существующие файлы;
- archive files находятся внутри своего Topic Workspace по пути `sessions/YYYY-MM-DD-<short-slug>.md`;
- companion artifact files, упомянутые в archive file или `Practice.md`, существуют;
- archive file содержит ссылки хотя бы на Topic и одну связанную сущность: `PA-*`, `Q-*`, `W-*`, `SRC-*` или `B*`;
- `Practice.md` содержит structured Practice Attempt для каждого `PA-*`, на который ссылается archive file;
- archive file не содержит полей, выдающих его за владельца Topic State, Block Status, Mastery Level, Question State, Weakness Status или Source Check Result;
- sensitive `Нужно проверить` в archive file имеет связанный `SRC-*`, если claim используется вне archive file;
- `Knowledge.md` не содержит raw Session Notes или копии archive file;
- `Goal.md` остается владельцем Topic State, Active Block, Block Status и Mastery Level;
- checker работает с human-first Markdown и не требует YAML/JSON machine-readable schema.

Полный алгоритм, формат отчета и auto-fix rules остаются отдельным ticket.

## Обоснование

`sessions/` решает проблему роста без превращения каждого учебного шага в отдельный обязательный файл. `Practice.md` остается читаемым журналом попыток, а archive file сохраняет traceability для длинного сырья и concrete artifacts.

Выбор file-per-Session совпадает с доменной моделью: Session является датированным проходом работы по Topic, а Practice Attempt является проверяемой единицей evidence внутри этой Session. Поэтому один archive file может обслуживать несколько попыток, вопросов и слабых мест без введения нового `Artifact ID`.

Отказ от обязательного `artifacts/` каталога и `ART-*` ID сохраняет систему легкой. Если artifact становится большим файлом, Markdown-ссылки и существующие entity IDs достаточны для первого прохода.

Append-only raw sections защищают historical evidence. Ограниченное редактирование summary, links и curation notes позволяет архиву не застывать в неудобном виде.

## Последствия

- Новые Topic Workspaces не обязаны заранее создавать `sessions/`.
- `Practice.md` должен использовать `Session Archive Links` только когда архив реально создан.
- Будущие lifecycle commands и Agent Files должны учитывать, что archive files не являются источниками истины для учебного состояния.
- Future checker должен проверять ссылки и ownership-инварианты, но не требовать machine-readable schema.

Prototype Topic Workspace остается без изменений: для одной короткой planned Practice Attempt archive file не нужен.

## Вне области

Это решение не делает:

- создание каталога `sessions/` в prototype;
- новые учебные темы;
- реальную RabbitMQ source verification;
- lightweight checker;
- YAML/JSON machine-readable schema;
- `.codex/agents/*.toml`;
- slash commands;
- Obsidian/Anki automation;
- финальный `learning-system-spec.md`.

## Следующие тикеты

1. `Design Lightweight Checker For Entity References And IDs`
2. `Design Obsidian And Anki Write Automation`
3. `Assemble Learning System Specification`

## Критерии завершения

Решение считается закрытым, когда:

- закреплено, что Session Notes и Practice Artifacts могут архивироваться в optional `sessions/`;
- принят path convention `sessions/YYYY-MM-DD-<short-slug>.md`;
- описано, когда archive file создается;
- описано, что остается в `Practice.md`;
- описано, что не попадает в `Knowledge.md`;
- описан минимальный формат archive file;
- описаны правила ссылок из основных артефактов;
- описаны права записи Learning Orchestrator и supporting agents;
- описаны append-only/edit правила;
- описаны retention/pruning правила;
- описано отношение к Source Check и `Нужно проверить`;
- future checker получил требования без реализации и без YAML/JSON machine-readable schema;
- карта wayfinder обновлена.
