# Запись решения: дизайн шаблонов учебных артефактов (Design Learning Artifact Templates)

## Статус (Status)

Accepted.

Scope correction 2026-08-24: шаблоны описывают универсальный Topic Workspace для programming learning. Backend-формулировки заменены на профильные или прикладные; конкретный стек относится к текущему Learning Profile.

## Контекст (Context)

Учебной системе нужны точные Markdown-шаблоны (Markdown templates) для одной рабочей папки темы (Topic Workspace), но сами рабочие файлы темы пока создавать нельзя.

Каноническая доменная модель (domain model) описана в [CONTEXT.md](../../../CONTEXT.md). Предыдущее решение закрепило соответствие артефактов (artifacts):

```text
Goal.md              -> цель темы (Topic Goal)
Knowledge.md         -> база знаний темы (Topic Knowledge Base)
Practice.md          -> журнал практики (Practice Journal)
Questions.md         -> очередь вопросов (Question Queue)
RepetitionLog.md     -> журнал повторений (Repetition Log)
Weaknesses.md        -> реестр слабых мест (Weakness Register)
Sources.md           -> записи источников (Source Record)
```

Шаблоны должны быть достаточно точными для Codex CLI и multi-agent workflow, но оставаться удобными для живого обучения.

## Решение (Decision)

Использовать human-first Markdown (читаемый человеком Markdown): стабильные заголовки (headings), стабильные идентификаторы (stable IDs), таблицы для индексов (indexes) и подробные записи (records) как отдельные Markdown-заголовки.

В этом ticket не создаются живые `Goal.md`, `Knowledge.md`, `Practice.md`, `Questions.md`, `RepetitionLog.md`, `Weaknesses.md` и `Sources.md`. Здесь фиксируется дизайн шаблонов для будущего prototype/implementation ticket.

Основной язык шаблонов - русский. Важные канонические термины указываются рядом на английском в скобках.

## Общие соглашения (Shared Conventions)

### Форматы ID (ID Formats)

| Сущность (Entity) | Формат (Format) | Пример (Example) |
|---|---|---|
| Стабильный slug (Stable Slug) | ASCII kebab-case | `rabbitmq-retry-dlq` |
| ID блока (Block ID) | `BNN` | `B01` |
| ID вопроса (Question ID) | `Q-YYYYMMDD-NN` | `Q-20260823-01` |
| ID практической попытки (Practice Attempt ID) | `PA-YYYYMMDD-NN` | `PA-20260823-01` |
| ID слабого места (Weakness ID) | `W-YYYYMMDD-NN` | `W-20260823-01` |
| ID повторения (Repetition ID) | `REP-YYYYMMDD-NN` | `REP-20260823-01` |
| ID источника (Source ID) | `SRC-YYYYMMDD-NN` | `SRC-20260823-01` |

### Ссылки на сущности (Entity References)

Ссылка на сущность (Entity Reference) объединяет ID, короткий смысл и Markdown-ссылку:

```md
[B01: mental model](Goal.md#b01---mental-model)
[PA-20260823-01: retry queue design](Practice.md#pa-20260823-01---retry-queue-design)
[W-20260823-01: requeue loop misconception](Weaknesses.md#w-20260823-01---requeue-loop-misconception)
```

### Пустые и непроверенные значения (Empty and Unverified Values)

- `-` означает пусто, неприменимо или намеренно отсутствует.
- `Нужно проверить` используется только для непроверенных утверждений (unverified claims).
- `TBD` в шаблонах не используется.

### Владение состоянием (State Ownership)

Только `Goal.md` владеет:

- состоянием темы (Topic State);
- активным блоком (Active Block);
- статусом блока (Block Status);
- уровнем освоения (Mastery Level).

Остальные артефакты владеют только состояниями своих сущностей:

- состояние вопроса (Question State) в `Questions.md`;
- результат практической попытки (Practice Attempt Result) в `Practice.md`;
- статус слабого места (Weakness Status) в `Weaknesses.md`;
- результат повторения (Repetition Result) в `RepetitionLog.md`;
- результат проверки источника (Source Check Result) в `Sources.md`.

### Допустимые значения (Allowed Values)

`production-ready` используется только когда Topic или Learning Profile делают реальные ограничения применения важной частью освоения. Для других тем этот уровень может быть неприменим.

| Поле (Field) | Значения (Values) |
|---|---|
| Состояние темы (Topic State) | `intake`, `diagnosing`, `planned`, `learning`, `practicing`, `reviewing`, `completed`, `paused` |
| Обязательность блока (Requirement) | `required`, `optional` |
| Уровень освоения (Mastery Level) | `recognition`, `recall`, `application`, `transfer`, `production-ready`, `stable` |
| Статус блока (Block Status) | `not-started`, `active`, `blocked`, `ready-for-review`, `stable`, `deferred` |
| Тип вопроса (Question Type) | `recall`, `practice`, `interview`, `debugging`, `design-choice`, `card-candidate` |
| Состояние вопроса (Question State) | `draft`, `active`, `answered`, `failed`, `promoted`, `archived`, `rejected` |
| Кандидат в карточку (Card Candidate) | `none`, `candidate`, `rejected`, `promoted` |
| Результат практической попытки (Practice Attempt Result) | `unchecked`, `passed`, `partial`, `failed`, `rework-needed` |
| Тип слабого места (Weakness Type) | `gap`, `misconception`, `fragile-skill`, `application-blind-spot` |
| Серьезность слабого места (Weakness Severity) | `minor`, `major`, `blocker` |
| Статус слабого места (Weakness Status) | `open`, `repairing`, `retest-needed`, `resolved`, `archived` |
| Тип цели повторения (Repetition Target Type) | `Question`, `Block`, `Weakness` |
| Действие повторения (Repetition Action) | `recall`, `explain`, `apply`, `debug`, `transfer` |
| Результат повторения (Repetition Result) | `scheduled`, `passed`, `partial`, `failed`, `missed` |
| Чувствительность источника (Source Sensitivity) | `version-sensitive`, `application-sensitive`, `production`, `security`, `tooling-behavior`, `protocol-semantics`, `durable-concept` |
| Тип авторитетности (Authority Type) | `official-docs`, `spec-rfc`, `release-notes`, `vendor-blog`, `engineering-article`, `community-discussion`, `course-book` |
| Результат проверки источника (Source Check Result) | `verified`, `rejected`, `needs-check`, `superseded` |

## Шаблон Goal.md

```md
# <Название темы> - цель темы (Topic Goal)

## Шапка (Header)

- Учебный проект (Learning Project): <Learning Project>
- Учебный профиль (Learning Profile): <Learning Profile>
- Предмет (Subject): <Subject>
- Тема (Topic): <Topic>
- Стабильный slug (Stable Slug): `<stable-slug>`
- Рабочая папка темы (Topic Workspace): `<relative/path>`
- Состояние темы (Topic State): `intake | diagnosing | planned | learning | practicing | reviewing | completed | paused`
- Активный блок (Active Block): `[B01: <block title>](#b01---<block-title>)` или `-`
- Последнее обновление (Last Updated): `YYYY-MM-DD`

## Правила редактирования (Edit Policy)

- Оркестратор обучения (Learning Orchestrator) владеет состоянием темы (Topic State), активным блоком (Active Block), статусами блоков (Block Status) и уровнями освоения (Mastery Level).
- Поддерживающие агенты (supporting agents) могут предлагать изменения, но state-changing edits требуют проверки оркестратора (Orchestrator review).
- Сырые заметки (raw notes), длинные объяснения, тела практических попыток и выдержки из источников здесь не хранятся.
- `Goal.md` хранит краткие ссылки на доказательства (evidence); сами доказательства живут в других артефактах.

## Управление темой (Topic Control)

- Зачем изучаем (Purpose): <1-3 предложения>
- Практический контекст (Applied Context): <сценарий из текущего Learning Profile>
- Текущий маршрут (Current Route): <короткий путь по required Blocks>
- Главный риск забывания (Main Forgetting Risk): <что сломается, если это забыть>

## Предпосылки (Prerequisites)

| Предпосылка (Prerequisite) | Статус (Status) | Доказательство/источник (Evidence/Source) | Действие (Action) |
|---|---|---|---|
| <предпосылка> | <статус свободным текстом> | <ссылка на сущность (Entity Reference) или `-`> | <следующее действие или `-`> |

## Карта обучения (Learning Map)

| ID блока (Block ID) | Блок (Block) | Обязательность (Requirement) | Уровень освоения (Mastery Level) | Статус (Status) | Доказательства (Evidence) | Открытые слабые места (Open Weaknesses) | Следующее действие (Next Action) |
|---|---|---|---|---|---|---|---|
| `B01` | <название блока> | `required` | `recognition` | `not-started` | `-` | `-` | <следующее действие> |

## Сводка активных слабых мест (Active Weakness Summary)

Правило: required Block не может стать `stable`, пока связанное blocker Weakness остается открытым.

| Слабое место (Weakness) | Серьезность (Severity) | Статус (Status) | Связанный блок (Linked Block) | Нужное исправление (Required Repair) |
|---|---|---|---|---|
| `[W-YYYYMMDD-01: <title>](Weaknesses.md#w-yyyymmdd-01---<title>)` | `blocker` | `open` | `[B01: <block>](#b01---<block>)` | <действие по исправлению> |

## Критерии завершения (Completion Criteria)

| Критерий (Criterion) | Нужное доказательство (Required Evidence) | Статус (Status) | Связанное доказательство (Linked Evidence) |
|---|---|---|---|
| Все required Blocks стали `stable`. | Learning Map показывает `stable` для required Blocks. | <статус> | <ссылка на сущность (Entity Reference) или `-`> |
| Блоки с реальными ограничениями применения достигли `production-ready` или `stable`, если этот уровень применим. | Transfer/practice evidence покрывает важные риски, ограничения или условия применения. | <статус> | <ссылка на сущность (Entity Reference) или `-`> |
| Нет открытых blocker Weaknesses. | Weakness Register не содержит связанных открытых blocker Weaknesses. | <статус> | <ссылка на сущность (Entity Reference) или `-`> |

## Следующие действия (Next Actions)

1. <следующее действие>
2. <следующее действие>
```

## Шаблон Knowledge.md

```md
# <Название темы> - база знаний темы (Topic Knowledge Base)

## Шапка (Header)

- Тема (Topic): <Topic>
- Стабильный slug (Stable Slug): `<stable-slug>`
- Основной артефакт (Primary Artifact): Topic Knowledge Base
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `YYYY-MM-DD`

## Правила редактирования (Edit Policy)

- Здесь хранится только отобранное знание (curated Knowledge): объясненное, примененное, исправленное после ошибки или проверенное по источнику.
- Сырые заметки сессии (Session Notes), стенограммы чата и скопированная документация сюда не вставляются.
- Версионочувствительные, application-sensitive, production, security, protocol или tooling claims должны ссылаться на `Sources.md` или иметь метку `Нужно проверить`.
- Состояние темы (Topic State), активный блок (Active Block), статус блока (Block Status) и уровень освоения (Mastery Level) здесь не дублируются.

## Индекс знаний (Knowledge Index)

| Блок (Block) | Покрытие (Coverage) | Ключевые источники (Sources) | Открытые проверки (Open Checks) |
|---|---|---|---|
| `[B01: <block>](Goal.md#b01---<block>)` | <краткое покрытие> | `[SRC-YYYYMMDD-01](Sources.md#src-yyyymmdd-01---<short-title>)` | `-` или `Нужно проверить` |

## B01 - <Название блока> (Block)

### Основное понимание (Core Understanding)

- <1-3 коротких пункта>

### Механика (Mechanics)

- <как это работает, с причинно-следственными связями>

### Пример применения (Applied Example)

<Конкретный пример из текущего Learning Profile.>

### Риски и ограничения применения (Risks and Limits)

- <failure mode, operational risk, consistency risk, security risk, observability risk, performance limit, compatibility issue или другое важное ограничение применения>

### Исправленные заблуждения (Corrected Misconceptions)

- Ошибка (Misconception): <ошибочная модель>
  Исправление (Correction): <правильная модель>
  Доказательство (Evidence): <ссылка на сущность (Entity Reference)>

### Ссылки на источники (Source Links)

- `[SRC-YYYYMMDD-01: <claim/source>](Sources.md#src-yyyymmdd-01---<short-title>)`
```

## Шаблон Practice.md

```md
# <Название темы> - журнал практики (Practice Journal)

## Шапка (Header)

- Тема (Topic): <Topic>
- Стабильный slug (Stable Slug): `<stable-slug>`
- Основной артефакт (Primary Artifact): Practice Journal
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `YYYY-MM-DD`

## Правила редактирования (Edit Policy)

- Тело практической попытки (Practice Attempt body) становится append-only после первичной записи.
- Обратная связь (Feedback), исправления (Corrections), связанные слабые места (Linked Weaknesses), перенесенное знание (Promoted Knowledge) и последующие вопросы (Follow-up Questions) дописываются под той же попыткой.
- Длинный сырой материал хранится в optional Session Archive; здесь остаются структурированные попытки и доказательства (evidence).
- Состояние темы (Topic State), активный блок (Active Block), статус блока (Block Status) и уровень освоения (Mastery Level) здесь не дублируются.

## Индекс практических попыток (Practice Attempt Index)

| ID попытки (Practice Attempt ID) | Дата сессии (Session Date) | Связанный блок (Linked Block) | Результат (Result) | Доказательство для (Evidence Use) | Слабые места (Weaknesses) | Перенесенное знание (Promoted Knowledge) |
|---|---|---|---|---|---|---|
| `PA-YYYYMMDD-01` | `YYYY-MM-DD` | `[B01: <block>](Goal.md#b01---<block>)` | `unchecked` | <что доказывает попытка> | `-` | `-` |

## Практические попытки (Practice Attempts)

### PA-YYYYMMDD-01 - <Короткое название попытки>

- ID практической попытки (Practice Attempt ID): `PA-YYYYMMDD-01`
- Дата сессии (Session Date): `YYYY-MM-DD`
- Связанный блок (Linked Block): `[B01: <block>](Goal.md#b01---<block>)`
- Задание (Prompt/Task): <задание>
- Артефакты (Artifacts): <ссылки на code/SQL/logs/tests/diagrams или `-`>
- Результат (Result): `unchecked | passed | partial | failed | rework-needed`

#### Тело попытки (Attempt Body)

<Исходная активная попытка learner. После записи этот блок append-only.>

#### Обратная связь (Feedback)

- <feedback item или `-`>

#### Исправления (Corrections)

- <correction или `-`>

#### Связанные слабые места (Linked Weaknesses)

- `[W-YYYYMMDD-01: <weakness>](Weaknesses.md#w-yyyymmdd-01---<weakness>)`

#### Знание, перенесенное в Knowledge.md (Promoted Knowledge)

- `[B01: <knowledge section>](Knowledge.md#b01---<block>)`

#### Последующие вопросы (Follow-up Questions)

- `[Q-YYYYMMDD-01: <question>](Questions.md#q-yyyymmdd-01---<question>)`

## Ссылки на архивы сессий (Session Archive Links)

| Дата (Date) | Архив (Archive) | Причина архивации (Why Archived) | Связанные попытки (Linked Attempts) |
|---|---|---|---|
| `YYYY-MM-DD` | `<path>` | <причина> | `PA-YYYYMMDD-01` |
```

## Шаблон Questions.md

```md
# <Название темы> - очередь вопросов (Question Queue)

## Шапка (Header)

- Тема (Topic): <Topic>
- Стабильный slug (Stable Slug): `<stable-slug>`
- Основной артефакт (Primary Artifact): Question Queue
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `YYYY-MM-DD`

## Правила редактирования (Edit Policy)

- Здесь хранится полный жизненный цикл вопроса (Question lifecycle).
- Запись вопроса (Question record) живет в одном месте; при изменении меняется поле `Question State`, а не раздел файла.
- Продвижение в Anki (Card Promotion) требует понимания, проверки релевантности, проверки дублей в Obsidian и проверки дублей в Anki.
- Anki-карточки автоматически из этого файла не создаются.
- Состояние темы (Topic State), активный блок (Active Block), статус блока (Block Status) и уровень освоения (Mastery Level) здесь не дублируются.

## Индекс вопросов (Question Index)

| ID вопроса (Question ID) | Тип (Question Type) | Состояние (Question State) | Связанный блок (Linked Block) | Кандидат в карточку (Card Candidate) | Слабые места (Weaknesses) | Ответ/попытка (Answer/Attempt) |
|---|---|---|---|---|---|---|
| `Q-YYYYMMDD-01` | `recall` | `draft` | `[B01: <block>](Goal.md#b01---<block>)` | `none` | `-` | `-` |

## Записи вопросов (Question Records)

### Q-YYYYMMDD-01 - <Короткое название вопроса>

- ID вопроса (Question ID): `Q-YYYYMMDD-01`
- Тип вопроса (Question Type): `recall | practice | interview | debugging | design-choice | card-candidate`
- Состояние вопроса (Question State): `draft | active | answered | failed | promoted | archived | rejected`
- Связанный блок (Linked Block): `[B01: <block>](Goal.md#b01---<block>)`
- Источник (Source): <ссылка на сущность (Entity Reference), `SRC-...` или `-`>

#### Формулировка (Prompt)

<Формулировка вопроса.>

#### Ожидаемый ответ или критерии оценки (Expected Answer / Rubric)

<Короткий ожидаемый ответ, rubric или `-`, если пока неприменимо.>

#### Ссылка на ответ/попытку (Answer/Attempt Link)

- <ссылка на сущность (Entity Reference) или `-`>

#### Связанные слабые места (Weakness Links)

- `[W-YYYYMMDD-01: <weakness>](Weaknesses.md#w-yyyymmdd-01---<weakness>)`

#### Кандидат в карточку (Card Candidate)

- Статус (Status): `none | candidate | rejected | promoted`
- Проверка дублей (Duplicate Check): <summary проверки Obsidian + Anki или `-`>
- След карточки (Card Trace): <Knowledge/Practice/Weakness/Source reference или `-`>
- Решение о продвижении в Anki (Promotion Decision): <skip/replace/merge/add или `-`>
```

## Шаблон Weaknesses.md

```md
# <Название темы> - реестр слабых мест (Weakness Register)

## Шапка (Header)

- Тема (Topic): <Topic>
- Стабильный slug (Stable Slug): `<stable-slug>`
- Основной артефакт (Primary Artifact): Weakness Register
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `YYYY-MM-DD`

## Правила редактирования (Edit Policy)

- Слабое место (Weakness) записывается только при наличии доказательства (Weakness Evidence).
- Каждое открытое `major` или `blocker` Weakness должно иметь действие по исправлению (Repair Action).
- Статус `resolved` требует доказательства исправления (Resolution Evidence).
- `blocker` Weakness блокирует закрытие блока и темы через `Goal.md`.
- Состояние темы (Topic State), активный блок (Active Block), статус блока (Block Status) и уровень освоения (Mastery Level) здесь не дублируются.

## Индекс слабых мест (Weakness Index)

| ID слабого места (Weakness ID) | Тип (Type) | Серьезность (Severity) | Статус (Status) | Связанный блок (Linked Block) | Доказательство (Evidence) | Действие (Action) |
|---|---|---|---|---|---|---|
| `W-YYYYMMDD-01` | `gap` | `major` | `open` | `[B01: <block>](Goal.md#b01---<block>)` | <ссылка на сущность (Entity Reference)> | <действие по исправлению> |

## Записи слабых мест (Weakness Records)

### W-YYYYMMDD-01 - <Короткое название слабого места>

- ID слабого места (Weakness ID): `W-YYYYMMDD-01`
- Тип (Type): `gap | misconception | fragile-skill | application-blind-spot`
- Серьезность (Severity): `minor | major | blocker`
- Статус (Status): `open | repairing | retest-needed | resolved | archived`
- Связанный блок (Linked Block): `[B01: <block>](Goal.md#b01---<block>)`
- Кандидат в карточку (Card Candidate): `none | candidate | rejected | promoted`

#### Доказательство (Evidence)

- <Practice Attempt, failed Question, Repetition Failure или interview answer>

#### Наблюдаемый паттерн ошибки (Observed Pattern)

<Что повторно идет не так?>

#### Действие по исправлению (Repair Action)

<Конкретное действие по ремонту слабого места.>

#### План повторной проверки (Retest Plan)

<Как доказать, что слабое место исправлено?>

#### Доказательство исправления (Resolution Evidence)

- <ссылка на сущность (Entity Reference) или `-`>

## Сводка исправленных/архивных (Resolved/Archived Summary)

| Слабое место (Weakness) | Финальный статус (Final Status) | Доказательство исправления (Resolution Evidence) | Заметки (Notes) |
|---|---|---|---|
| `[W-YYYYMMDD-01: <weakness>](#w-yyyymmdd-01---<weakness>)` | `resolved` | <ссылка на сущность (Entity Reference)> | <короткая заметка> |
```

## Шаблон RepetitionLog.md

```md
# <Название темы> - журнал повторений (Repetition Log)

## Шапка (Header)

- Тема (Topic): <Topic>
- Стабильный slug (Stable Slug): `<stable-slug>`
- Основной артефакт (Primary Artifact): Repetition Log
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `YYYY-MM-DD`

## Правила редактирования (Edit Policy)

- Повторение должно быть активным (Active Repetition): recall, explain, apply, debug или transfer.
- `missed` означает, что повторение не выполнено вовремя; `failed` означает, что попытка была, но recall/application не удались.
- Проваленное активное повторение (Repetition Failure) должно открыть или обновить Weakness, если оно выявляет учебную проблему.
- Состояние темы (Topic State), активный блок (Active Block), статус блока (Block Status) и уровень освоения (Mastery Level) здесь не дублируются.

## Очередь повторений (Repetition Queue)

| ID повторения (Repetition ID) | Тип цели (Target Type) | Цель (Target) | Запланировано на (Scheduled For) | Действие (Action) | Результат (Result) | Следующее повторение (Next Repetition) |
|---|---|---|---|---|---|---|
| `REP-YYYYMMDD-01` | `Question` | `[Q-YYYYMMDD-01: <question>](Questions.md#q-yyyymmdd-01---<question>)` | `YYYY-MM-DD` | `recall` | `scheduled` | `-` |

## Записи повторений (Repetition Records)

### REP-YYYYMMDD-01 - <Короткое название повторения>

- ID повторения (Repetition ID): `REP-YYYYMMDD-01`
- Тип цели (Target Type): `Question | Block | Weakness`
- Цель (Target): <ссылка на сущность (Entity Reference)>
- Запланировано на (Scheduled For): `YYYY-MM-DD`
- Выполнено в (Completed At): `YYYY-MM-DD` или `-`
- Действие (Action): `recall | explain | apply | debug | transfer`
- Результат (Result): `scheduled | passed | partial | failed | missed`
- Без подсказки? (No-Hint?): `yes | no | -`
- Следующее повторение (Next Repetition): `YYYY-MM-DD` или `-`

#### Анализ провала (Failure Analysis)

<Почему повторение провалилось или стало partial? Использовать `-`, если неприменимо.>

#### Связанное слабое место (Linked Weakness)

- `[W-YYYYMMDD-01: <weakness>](Weaknesses.md#w-yyyymmdd-01---<weakness>)`

## Провалы, открытые как слабые места (Failures Opened As Weaknesses)

| Провал повторения (Repetition Failure) | Слабое место (Weakness) | Действие (Action) |
|---|---|---|
| `[REP-YYYYMMDD-01: <repetition>](#rep-yyyymmdd-01---<repetition>)` | `[W-YYYYMMDD-01: <weakness>](Weaknesses.md#w-yyyymmdd-01---<weakness>)` | <действие по исправлению> |
```

## Шаблон Sources.md

```md
# <Название темы> - записи источников (Source Record)

## Шапка (Header)

- Тема (Topic): <Topic>
- Стабильный slug (Stable Slug): `<stable-slug>`
- Основной артефакт (Primary Artifact): Source Record
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `YYYY-MM-DD`

## Правила редактирования (Edit Policy)

- Для version-sensitive, application-sensitive, production, security, protocol и tooling-behavior claims нужны авторитетные источники (Authoritative Sources).
- Для version/security/protocol claims предпочтительны `official-docs`, `spec-rfc` и `release-notes`.
- Заметки по источникам (Source Notes) должны быть коротким пересказом, а не скопированной документацией.
- Непроверенные утверждения получают `Result: needs-check` и могут упоминаться в других артефактах как `Нужно проверить`.
- Состояние темы (Topic State), активный блок (Active Block), статус блока (Block Status) и уровень освоения (Mastery Level) здесь не дублируются.

## Индекс проверок источников (Source Check Index)

| ID источника (Source ID) | Утверждение (Claim) | Чувствительность (Sensitivity) | Тип авторитетности (Authority Type) | Дата проверки (Checked At) | Результат (Result) | Где используется (Used In) |
|---|---|---|---|---|---|---|
| `SRC-YYYYMMDD-01` | <утверждение> | `version-sensitive` | `official-docs` | `YYYY-MM-DD` | `verified` | <ссылка на сущность (Entity Reference)> |

## Проверки источников (Source Checks)

### SRC-YYYYMMDD-01 - <Короткое название проверки>

- ID источника (Source ID): `SRC-YYYYMMDD-01`
- Утверждение (Claim): <проверяемое утверждение>
- Чувствительность (Sensitivity): `version-sensitive | application-sensitive | production | security | tooling-behavior | protocol-semantics | durable-concept`
- URL/ссылка на источник (Source URL/Reference): <URL, RFC, docs page, book reference>
- Тип авторитетности (Authority Type): `official-docs | spec-rfc | release-notes | vendor-blog | engineering-article | community-discussion | course-book`
- Дата проверки (Checked At): `YYYY-MM-DD`
- Результат (Result): `verified | rejected | needs-check | superseded`
- Где используется (Used In): <ссылка на сущность (Entity Reference) или `-`>
- Следующая проверка (Next Check): `YYYY-MM-DD` или `-`

#### Заметки (Notes)

<Короткий пересказ того, что источник подтверждает или опровергает. Длинный текст источника не копировать.>

## Заметки по источникам (Source Notes)

Использовать только для коротких source-level notes, которые не относятся к одному claim.

- `[SRC-YYYYMMDD-01: <source>](#src-yyyymmdd-01---<short-title>)` - <короткий пересказ>
```

## Обоснование (Rationale)

Шаблоны разделяют управление, знания, практику, вопросы, повторения, слабые места и источники:

- `Goal.md` остается контрольным артефактом (control artifact), а не смешанной тетрадью.
- `Knowledge.md` хранит отобранное знание (curated Knowledge) по блокам (Blocks), а не хронологию сессий.
- `Practice.md` записывает проверяемые практические попытки (Practice Attempts) как единицы доказательства (evidence units).
- `Questions.md` сохраняет полный lifecycle вопросов и traceability для кандидатов в карточки (Card Candidates).
- `Weaknesses.md` делает учебные проблемы actionable через evidence, repair и retest.
- `RepetitionLog.md` различает scheduled, missed и failed активные повторения (Active Repetitions).
- `Sources.md` связывает claims с проверками источников (Source Checks), а не хранит свободную bibliography.

Дизайн намеренно остается human-first. Машиночитаемый слой (Machine-Readable Layer) остается вне scope, пока автоматизация не докажет необходимость.

## Последствия (Consequences)

- Будущие агенты должны соблюдать edit boundaries каждого артефакта.
- Будущий prototype ticket должен создать эти семь шаблонов в одной Topic Workspace.
- Будущая Anki-интеграция должна читать Card Candidate поля из `Questions.md`, но Card Promotion все равно требует duplicate checks в Obsidian и Anki.
- Будущая проверка источников должна обновлять `Sources.md` и ссылать claims из других артефактов через `Source ID`.
- `CONTEXT.md` дополнен терминами `Repetition ID` и `Source ID`, потому что шаблоны требуют стабильных ссылок на эти записи.

## Вне scope (Out Of Scope)

Это решение не создает:

- реальные файлы Topic Workspace;
- `.codex/agents/*.toml`;
- slash commands;
- Obsidian write-back automation;
- Anki automation;
- YAML front matter или machine-readable schema;
- prototype topic.

## Критерии завершения (Completion Criteria)

Решение завершено, когда:

- все семь Markdown-шаблонов описаны в этой записи;
- общие ID formats и allowed values зафиксированы;
- edit boundaries сохраняют single-writer state model;
- ticket не создает реальные рабочие файлы темы.
