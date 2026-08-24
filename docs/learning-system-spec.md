# Learning System Specification

Дата сборки: 2026-08-24.

Эта спецификация собирает принятые wayfinder-решения в рабочий контракт для будущей реализации учебной системы и будущих агентов. Она не заменяет decision records как историю решений, но задает цельную модель: какие артефакты существуют, кто ими владеет, какие gates блокируют продвижение и какие будущие implementation tickets можно начинать.

## 1. Назначение системы

Система нужна, чтобы изучать темы программирования через Codex CLI и многоагентный учебный процесс не как набор конспектов, а как проверяемое движение к умению.

Целевой цикл:

```text
запрос пользователя -> уточнение темы и диагностика -> Goal.md -> цикл блока
-> Knowledge.md -> Practice.md -> Questions.md/Card Candidates -> RepetitionLog.md
-> Knowledge Consolidation и Card Promotion при выполненных gates
```

Система должна помогать learner:

- объяснить тему без подсказки;
- применить ее в профильном сценарии;
- изменить пример, а не только прочитать его;
- намеренно сломать сценарий и объяснить поломку;
- увидеть реальные ограничения применения;
- выдержать повторение и уточняющие вопросы;
- перенести только устойчивое знание в Long-Term Knowledge Base.

## 2. Scope и out of scope

В scope первой спецификации входит:

- human-first Markdown модель Topic Workspace;
- доменная модель Learning Project, Subject, Topic, Block и Session;
- Learning Profile как источник приоритетов;
- path convention `topics/<subject>/<stable-slug>/`;
- роли артефактов `Goal.md`, `Knowledge.md`, `Practice.md`, `Questions.md`, `Weaknesses.md`, `RepetitionLog.md`, `Sources.md`, optional `sessions/` и `topics/INDEX.md`;
- single-writer state model;
- boundaries для supporting agents;
- Topic lifecycle scenarios;
- Block Learning Cycle;
- Mastery Level и Completion Evidence;
- Weakness workflow;
- Source Verification Workflow и `Нужно проверить`;
- Questions, Card Candidates и Card Promotion;
- Obsidian/Anki integration;
- Obsidian/Anki write automation на уровне workflow, gates, preview, approval и trace;
- read-only Lightweight Checker contract;
- future implementation tickets.

Out of scope этой спецификации:

- реальная запись в Obsidian;
- реальная запись в Anki;
- создание Anki-карточек;
- изменение Obsidian vault;
- реализация automation scripts;
- реализация slash commands;
- создание `.codex/agents/*.toml`;
- создание новых учебных тем;
- расширение prototype в полноценную учебную тему;
- реальная RabbitMQ source verification;
- реализация Lightweight Checker;
- введение YAML/JSON machine-readable schema.

## 3. Доменная модель и ключевые термины

Базовая иерархия:

```text
Learning Project -> Subject -> Topic -> Block -> Session
```

`Learning Project` - верхний учебный контекст. `Subject` - крупная область знаний. `Topic` - конкретная учебная цель внутри Subject. `Block` - логическая часть Topic. `Session` - датированный проход работы по Topic или Block.

Ключевые сущности:

- `Topic Workspace` - папка темы в репозитории.
- `Topic Goal` - управляющий артефакт темы, физически `Goal.md`.
- `Knowledge` - curated Knowledge, а не raw Session Notes.
- `Practice Attempt` - активная попытка learner, которую можно проверить.
- `Question` - prompt для recall, practice, interview, debugging или design choice.
- `Card Candidate` - еще не карточка, а кандидат на Card Promotion.
- `Weakness` - evidence-backed учебная проблема, меняющая следующий шаг.
- `Active Repetition` - активное повторение через recall, explain, apply, debug или transfer.
- `Source Check` - проверка чувствительного claim.
- `Entity Reference` - стабильный ID плюс Markdown-ссылка на сущность.

Canonical glossary живет в `CONTEXT.md`. Спецификация не превращает `CONTEXT.md` в полный документ правил.

## 4. Learning Profile и универсальность системы

Система универсальна для обучения темам программирования. Конкретная область, стек, проект и карьерный контекст задаются через `Learning Profile`, а не через границы самой системы.

Текущий Learning Profile:

```text
Junior+/Middle Kotlin Backend для ЦУП РТ / АИС МИДИО
```

Профильный контекст включает Kotlin, Ktor, Git, Postgres/Exposed, Docker/Docker Compose, RabbitMQ, Prometheus, Grafana, MongoDB, ClickHouse, DDD, Transactional Outbox, system design, CI/CD, reliability, security, observability и Sports Facility Booking / MIDIO-inspired project.

Learning Profile влияет на:

- приоритет Topic;
- выбор Applied Context;
- выбор required Blocks;
- применимость `production-ready`;
- ценность Card Candidate;
- необходимость Source Check;
- место Knowledge Consolidation в Obsidian;
- примеры и практические задания.

Learning Profile не должен превращаться в жесткий фильтр: тема может быть полезна нескольким профилям.

## 5. Topic Workspace layout и path convention

Topic Workspaces живут по пути:

```text
topics/<subject>/<stable-slug>/
```

Правила:

- `<subject>` - короткий ASCII slug primary Subject.
- `<stable-slug>` - короткий ASCII slug темы внутри Subject.
- полный Stable Slug хранится в `Goal.md` и может быть глобально уникальным.
- путь является физическим расположением, а не единственным идентификатором темы.
- multi-subject Topic имеет одну физическую Topic Workspace; дополнительные Subject указываются в `topics/INDEX.md`.
- Parent Topic является Topic, а не Subject.

Минимальный layout:

```text
topics/<subject>/<stable-slug>/
  Goal.md
  Knowledge.md
  Practice.md
  Questions.md
  Weaknesses.md
  RepetitionLog.md
  Sources.md
  sessions/                  # optional
```

`topics/INDEX.md` находится рядом с `topics/` и является human-first Topic Index.

## 6. Роли основных артефактов

`Goal.md` - управляющий артефакт темы. Он владеет Topic State, Active Block, Block Status, Mastery Level, Learning Map, Completion Criteria, Active Weakness Summary и Next Actions. Он хранит краткие ссылки на evidence, но не тела evidence.

`Knowledge.md` - Topic Knowledge Base. Он хранит curated Knowledge: очищенные объяснения, применимые примеры, corrected misconceptions, risks and limits и ссылки на Source Records. Он не хранит raw Session Notes, transcript, длинные terminal logs или копии источников.

`Practice.md` - Practice Journal. Он хранит structured Practice Attempts, result, feedback, corrections, linked Weaknesses, promoted Knowledge links, follow-up Questions и ссылки на artifacts. Он является основным evidence-слоем для application и transfer.

`Questions.md` - Question Queue. Он владеет Question State и Card Candidate status, хранит prompt, rubric, answer/attempt links, Weakness links, Duplicate Check summary, Card Trace и Promotion Decision.

`Weaknesses.md` - Weakness Register. Он владеет Weakness Status, severity, repair action и resolution evidence. Weakness без evidence не открывается как `W-*`; pre-evidence risk можно держать отдельно как risk index.

`RepetitionLog.md` - Repetition Log. Он владеет Active Repetition records и results. Повторение должно требовать активного действия: recall, explain, apply, debug или transfer.

`Sources.md` - Source Record artifact. Он владеет Source Records и Source Check Result. Другие файлы могут ссылаться на `SRC-*` и писать `Нужно проверить`, но не владеют результатом проверки.

`sessions/` - optional archive внутри Topic Workspace. Он хранит длинные Session Notes и Practice Artifacts, если они нужны для traceability, но не становятся Knowledge и не владеют состояниями.

`topics/INDEX.md` - навигационный Topic Index. Он помогает найти Topic Workspace и может показывать кэш Topic State, но не является source of truth для учебного состояния.

## 7. Ownership model

Система использует single-writer state model.

Learning Orchestrator:

- единственный применяет state-changing edits;
- меняет `Goal.md`, `Knowledge.md`, `Weaknesses.md`;
- может применять согласованные изменения в `Practice.md`, `Questions.md`, `Sources.md`, `RepetitionLog.md`;
- принимает решения о Topic State, Active Block, Block Status, Mastery Level, Completion Criteria, Card Promotion и Knowledge Consolidation.

Owner files:

| Owner file | Чем владеет |
|---|---|
| `Goal.md` | Topic State, Active Block, Block Status, Mastery Level |
| `Sources.md` | Source Check Result |
| `Questions.md` | Question State, Card Candidate status |
| `Weaknesses.md` | Weakness Status, severity, repair action, resolution evidence |
| `RepetitionLog.md` | Active Repetition records и results |
| `Practice.md` | Practice Attempts, attempt result, feedback, evidence links |
| `Knowledge.md` | curated Knowledge |

Supporting agents работают через Agent Proposal или узкие append-only boundaries:

- Practice Agent может дописать новую Practice Attempt в `Practice.md` только по явному заданию.
- Question/Card Agent может дописать draft Questions и Card Candidates в `Questions.md`.
- Source Agent может дописать Source Records в `Sources.md`.
- Repetition Agent может дописать Active Repetitions и results в `RepetitionLog.md`.
- Diagnostic Agent и Knowledge Curator Agent обычно возвращают только Agent Proposal.

Supporting agents не меняют `Goal.md`, `Knowledge.md`, `Weaknesses.md` напрямую и не выполняют сквозные изменения нескольких файлов.

## 8. Topic lifecycle

Первая версия описывает scenarios, а не реализованные slash commands.

`start/intake`: превращает сырой запрос пользователя в Intake Topic. Должны появиться Subject, Topic, Stable Slug, предполагаемый path, черновая цель и Topic State `intake`.

`diagnose`: проверяет стартовое понимание, prerequisites, начальные Weaknesses и форму маршрута. Перед `planned` нужны цель, проверенные или отмеченные риском prerequisites, 3-7 blocks, required/optional split, первый Active Block и диагностическое evidence.

`plan`: превращает диагностику в Learning Map, Completion Criteria, Active Weakness Summary и первый Next Action. Разрешенный переход: `diagnosing -> planned`.

`learn-block`: проводит Active Block через Block Learning Cycle. Разрешает появление Knowledge, Practice Attempt, Questions, Source Checks и Weaknesses, но изменение уровня блока применяет Learning Orchestrator.

`practice`: получает проверяемую Practice Attempt. Попытка должна иметь ID, linked Block, result, feedback и evidence links.

`review`: проверяет устойчивость через no-hint answer, application, transfer, failure analysis, Weakness review и RepetitionLog. Именно здесь решается, можно ли повышать Mastery Level или двигаться к `completed`.

`repeat`: планирует или проводит Active Repetition. Failed или partial repetition может открыть Weakness и понизить Mastery Level только через Learning Orchestrator.

`pause`: останавливает работу без потери маршрута. `Goal.md` должен хранить предыдущее рабочее состояние и next safe action.

`resume`: восстанавливает работу из `Goal.md` и связанных артефактов. Пропущенные повторения и открытые blocker Weaknesses не игнорируются.

`complete`: закрывает Topic только если все required Blocks стали `stable`, применимые production/application constraints покрыты, blocker Weaknesses отсутствуют, evidence собрано, а blocking `needs-check` не используется для gates.

Основной путь:

```text
intake -> diagnosing -> planned -> learning -> practicing -> reviewing -> completed
```

Пауза:

```text
intake | diagnosing | planned | learning | practicing | reviewing -> paused
paused -> diagnosing | planned | learning | practicing | reviewing
```

## 9. Block Learning Cycle

Базовый цикл блока:

```text
теория -> пример -> изменить пример -> сломать -> объяснить поломку
```

Минимальный качественный проход:

- learner получил короткую теорию;
- learner увидел пример в контексте Learning Profile;
- learner изменил пример;
- learner разобрал намеренную или реальную поломку;
- learner объяснил причину поломки без подсказки или провал зафиксирован как evidence;
- появилась обратная связь и следующий шаг;
- новые Weaknesses открыты только при наличии Weakness Evidence;
- чувствительные claims ушли в Source Check или получили `Нужно проверить`.

Block Learning Cycle не закрывает блок сам по себе. Он создает Completion Evidence, которое Learning Orchestrator использует при review.

## 10. Mastery Level и Completion Evidence

Mastery Level:

```text
recognition -> recall -> application -> transfer -> production-ready -> stable
```

`production-ready` применяется только когда Topic или Learning Profile делают реальные ограничения применения важной частью освоения. Для других тем этот уровень может быть неприменим.

Минимальные evidence expectations:

| Level | Evidence |
|---|---|
| `recall` | объяснение без подсказки |
| `application` | checked Practice Attempt |
| `transfer` | перенос в новый практический сценарий |
| `production-ready` | разбор важных рисков и ограничений применения |
| `stable` | успешное Active Repetition |

Completed Topic требует:

- все required Blocks имеют `stable`;
- применимые реальные ограничения достигли `production-ready` или `stable`;
- нет open blocker Weaknesses;
- major Weaknesses исправлены или явно вынесены за scope темы;
- есть evidence практики, failure analysis, вопросов и повторения;
- blocking `needs-check` не используется как подтвержденное evidence.

## 11. Weakness workflow

Weakness - typed learning problem, который меняет следующий шаг.

Типы:

- `gap`;
- `misconception`;
- `fragile-skill`;
- `application-blind-spot`.

Severity:

- `minor` - не блокирует движение, но может породить вопрос или repetition;
- `major` - требует planned repair action;
- `blocker` - запрещает закрывать связанный Block и Topic.

Workflow:

1. Weakness открывается только при наличии Weakness Evidence: Practice Attempt, failed Question, Repetition Failure, interview answer или другой проверяемый evidence target.
2. `major` и `blocker` обязаны иметь Repair Action.
3. После ремонта нужен retest.
4. `resolved` требует Resolution Evidence.
5. Повторный провал может переоткрыть Weakness или понизить Mastery Level через Learning Orchestrator.

Pre-evidence risk может жить в `Weaknesses.md` без `W-*`, но не считается evidence-backed Weakness и не закрывает gates.

## 12. Source Verification Workflow и `Нужно проверить`

Source Check обязателен для claims, которые влияют на:

- `production-ready`;
- security;
- protocol semantics;
- Card Promotion;
- Knowledge Consolidation;
- переход Topic в `completed`;
- Completion Evidence;
- реальное поведение инструмента, библиотеки, платформы или runtime;
- версионно-зависимые рекомендации;
- performance, operational и production guidance, когда это важно для Learning Profile.

`Sources.md` владеет Source Check Result:

```text
verified | rejected | needs-check | superseded
```

`Нужно проверить` означает, что claim можно использовать как гипотезу или ориентир для раннего понимания, но нельзя выдавать как подтвержденный факт.

`needs-check` блокирует:

- `production-ready`, если claim нужен для этого level;
- `completed`, если claim нужен для Completion Criteria;
- Card Promotion, если карточка зависит от claim;
- Knowledge Consolidation, если переносимый фрагмент зависит от claim;
- снятие blocker Weakness, если repair зависит от claim.

Если источник недоступен, агент не подтверждает claim по памяти. Он оставляет или создает Source Record с `needs-check`, сохраняет `Нужно проверить` в связанных артефактах и фиксирует next check.

## 13. Questions, Card Candidates и Card Promotion

Questions появляются после диагностики, Block Learning Cycle, Practice Attempt, failed Question, failed Repetition или перед закрытием блока.

`Questions.md` владеет:

- Question State;
- Card Candidate status;
- Duplicate Check summary;
- Card Trace;
- Promotion Decision;
- Anki write outcome после будущей write automation.

Card Candidate создается только если материал:

- уже понят;
- важен для Learning Profile;
- достаточно атомарен;
- имеет trace к Knowledge, Practice Attempt, Weakness, Source Record, Repetition или Question;
- не является сырым куском объяснения.

Card Promotion невозможен без:

- понимания материала;
- ценности для Learning Profile;
- Card Trace;
- Obsidian Duplicate Check;
- Anki Duplicate Check;
- Source Check gates;
- решения `skip`, `replace`, `merge` или `add`;
- участия пользователя при strong duplicate, `replace`, спорном `merge` или сомнительной ценности.

Anki unavailable mode блокирует `promoted`: Card Candidate остается `candidate`, пока Anki Duplicate Check и фактическая запись невозможны.

## 14. Obsidian/Anki integration

Obsidian выполняет две роли:

- Long-Term Knowledge Base для consolidated Knowledge;
- источник контекста и duplicate checks.

Anki используется для интервального повторения через карточки, но карточки не создаются из raw material.

Obsidian проверяется:

- на старте новой Topic, если есть пересечение с уже изученным;
- перед Card Promotion;
- перед Knowledge Consolidation.

Anki проверяется только перед фактическим добавлением или изменением карточки.

Knowledge Consolidation переносит только curated Knowledge:

- короткие объяснения;
- corrected misconceptions;
- risks and limits;
- связи с проектом;
- source/date context;
- компактные примеры, если они помогают recall.

Не переносится:

- весь `Knowledge.md`;
- raw Session Notes;
- длинные logs;
- временные Questions;
- промежуточные рассуждения;
- sensitive claims с blocking `needs-check`.

Для Obsidian decisions используются `skip`, `append`, `merge`, `replace-section`, `add`. Для Anki decisions используются `skip`, `replace`, `merge`, `add`.

## 15. Obsidian/Anki write automation

Write automation - Orchestrator-controlled workflow для фактической записи после принятого решения. Он не решает, ценна ли карточка, проверен ли claim или можно ли закрыть Topic.

Write targets:

```text
Anki write
Obsidian write
```

Обязательные checks перед записью:

1. Lightweight Checker для Topic Workspace и gate impact.
2. Source Check gates в `Sources.md`.
3. Duplicate Check results по Obsidian и Anki для Card Promotion.
4. Obsidian Duplicate Check для Knowledge Consolidation.
5. Dry-run preview.
6. User approval.
7. Availability check нужного write target.
8. Re-run/idempotency check по существующему trace.

Dry-run / preview должен показать target, action, proposed content, Duplicate Check summary, Source Check summary, Card Trace или Knowledge Consolidation trace, expected Markdown updates, unavailable targets и failure/recovery plan. Dry-run не меняет Anki, Obsidian или Topic Workspace.

User approval обязателен перед любым write после preview. `replace`, `merge`, изменение существующей Anki-карточки или Obsidian note, strong duplicate и неоднозначные targets требуют особенно явного approval.

Write outcome хранится в:

- `Questions.md` для Card Promotion и Anki write outcome;
- `Knowledge.md` для Knowledge Consolidation и Obsidian write outcome;
- `Goal.md` только как краткая ссылка на readiness/outcome, если это влияет на next action или Completion Criteria.

Write automation должна быть idempotent и safe for re-run через stable source entity, target identity, write action, write result, Duplicate Check summary, Source Check summary и user approval trace.

## 20. Prototype findings

Prototype Topic Workspace:

```text
topics/rabbitmq/retry-without-idempotency/
```

Что подтвердилось:

- семь основных артефактов хорошо разделяют control, Knowledge, Practice, Questions, Weaknesses, Repetitions и Sources;
- Entity References читаемы без YAML/JSON machine-readable schema;
- `Goal.md` естественно работает как владелец Topic State, Active Block, Block Status и Mastery Level;
- `Sources.md` с `needs-check` позволяет сохранить sensitive claim без ложного подтверждения;
- `topics/INDEX.md` удобен как navigation layer, но не должен владеть состоянием.

Что оказалось тяжелым:

- ручная проверка ID и cross-file references быстро становится заметной работой;
- пустой `Weaknesses.md` нужен как место для risk index, но Weakness Record без evidence открывать нельзя;
- Card Candidate в `Questions.md` полезен рано, но без Duplicate Check его легко ошибочно принять за готовую карточку;
- повторение `Last Updated` во всех файлах может стать механическим шумом без автоматизации;
- `Session Archive Links` в маленькой теме выглядит рано, но остается понятным расширением.

Prototype остается prototype. Он не расширяется в полноценную учебную тему в рамках этой спецификации.

## 21. Future implementation tickets

Рекомендуемые следующие tickets:

1. `Implement Learning Artifact Templates`: создать reusable starter templates для семи файлов Topic Workspace и optional `sessions/`, сохраняя human-first Markdown.
2. `Implement Lightweight Checker`: read-only validator для `topics/INDEX.md`, Topic Workspace files, Entity References, ID formats, owner invariants и gate impact.
3. `Implement Agent Common Instructions`: рабочий документ для будущих учебных агентов с context pointers, single-writer rules, Agent Proposal format и gates.
4. `Create Codex Agent Files`: создать `.codex/agents/*.toml` после проверки актуального Codex Manual и без расширения прав supporting agents.
5. `Design Lifecycle Command Interface`: превратить lifecycle scenarios в slash command или другой интерфейс без изменения ownership model.
6. `Implement Topic Intake Workspace Creation`: создать безопасный workflow для `start/intake`, который добавляет Topic Workspace и строку в `topics/INDEX.md`.
7. `Implement Source Verification Support`: workflow для Source Agent и Source Records без реальной проверки по памяти агента.
8. `Implement Obsidian/Anki Duplicate Check`: read/check workflow для похожих notes и cards до Card Promotion и Knowledge Consolidation.
9. `Implement Obsidian/Anki Write Automation`: dry-run preview, user approval, unavailable mode, idempotency и trace outcome.
10. `Implement Handoff Support`: Topic Workspace Handoff checks и optional `Handoff.md` только для рискованных продолжений.

Эти tickets являются implementation work. Они не должны вводить YAML/JSON machine-readable schema без отдельного decision ticket.

## 22. Hard invariants

- `Goal.md` владеет Topic State, Active Block, Block Status, Mastery Level.
- `Sources.md` владеет Source Check Result.
- `Questions.md` владеет Question State и Card Candidate status.
- `Knowledge.md` хранит curated Knowledge, не raw Session Notes.
- `Practice.md` хранит structured Practice Attempts и evidence.
- `Weaknesses.md` владеет Weakness Status, severity, repair action и resolution evidence.
- `RepetitionLog.md` владеет Active Repetition records и results.
- `topics/INDEX.md` является навигационным индексом, не source of truth.
- Supporting agents не меняют state-changing artifacts напрямую.
- Supporting agents работают через Agent Proposal или явную узкую append-only boundary.
- Card Promotion невозможен без Duplicate Check, Card Trace и Source Check gates.
- Knowledge Consolidation невозможна для нужного sensitive claim с `needs-check`.
- `Нужно проверить` нельзя молча снять без обновления `Sources.md`.
- Write automation не выполняется без dry-run preview и user approval.
- Lightweight Checker ничего не меняет.
- Archive files в `sessions/` не владеют Topic State, evidence gates, Question State, Weakness Status или Source Check Result.
- Anki unavailable mode не разрешает ставить Card Candidate в `promoted`.
- Obsidian unavailable mode не разрешает считать Knowledge Consolidation выполненной.
- `Goal.md`, `Knowledge.md` и `Weaknesses.md` меняет только Learning Orchestrator.
- YAML/JSON machine-readable schema не вводится.
