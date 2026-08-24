# Передача контекста между сессиями

Handoff передаёт следующей Codex-сессии путь к устойчивому контексту, а не
заменяет его. Передающий агент не меняет владельцев состояния: Learning
Orchestrator остаётся единственным автором изменений состояния.

## Общие правила

- Новая сессия сначала определяет вид handoff: проектный Wayfinder или
  учебный Topic Workspace. Она читает owner artifacts, а затем действует.
- Handoff всегда содержит next safe action, Role Mode и Agent Write Boundary.
  Если любой из них неясен, supporting agent возвращает Agent Proposal.
- `Handoff.md` — условный краткий снимок только при реальном риске потери
  контекста: длинная работа, несколько связанных открытых действий, смена
  Physical Agent или сложный cross-file gate. Он не источник истины и не
  создаётся для обычной паузы.
- При расхождении снимка и владельческого файла верить владельцу: `Goal.md`
  для Topic State/Blocks/Mastery, `Sources.md` для Source Check Result,
  `Weaknesses.md` для Weakness Status, `Questions.md` для Question/Card
  Candidate state и `RepetitionLog.md` для repetition.

## Wayfinder Handoff

Используется для project decisions, tickets и реализации без конкретного Topic
Workspace.

### Минимальное чтение на входе

1. `docs/wayfinder/00-map.md` и `CONTEXT.md`.
2. Связанные decision records и `docs/learning-system-spec.md`.
3. Актуальный ticket/инструкция сессии, его статус и критерии.
4. Затронутые templates, общий контракт и уже реализованные инструменты.
5. `git status`, последние commits и незавершённые, но разрешённые изменения.

### Обязательное содержание передачи

Передающий агент фиксирует: текущий ticket, Destination из карты, закрытые
`Decisions So Far`, открытый `Not Yet Specified`, `Out Of Scope`, следующий
ticket/next safe action, prerequisites, уже проверенное, действующие границы
владения, Role Mode и Agent Write Boundary. При возобновлении новая сессия
сверяет это с карточкой тикета и решениями; устаревший ticket не исполняется
без проверки актуального решения.

**Stop condition:** если предпосылка ticket отсутствует, scope расходится с
принятым decision record или граница записи неясна, остановиться и вернуть
Agent Proposal/блокер, а не создавать побочные артефакты.

## Topic Workspace Handoff

Используется при `pause`, смене сессии или передаче работы по конкретной Topic.
Path Workspace и Stable Slug должны быть указаны явно.

### Минимальное чтение на входе

1. `Goal.md` и существующий `Handoff.md`: Topic State, Active Block, Block
   Status, Mastery, Completion Criteria, Active Weakness Summary и Next
   Actions.
2. `Weaknesses.md`, если next safe action, Active Weakness Summary или handoff
   ссылается на Weakness: все open/repairing/retest-needed записи, особенно
   `blocker`, их evidence, Repair Action и retest.
3. `Questions.md`, если есть active/failed Question или Card Candidate:
   Card Trace, Duplicate Check и Promotion Decision.
4. `Sources.md`, если маршрут использует sensitive claim или pending check:
   `needs-check`, `rejected` и `superseded` Source Records, Used In и Next
   Check.
5. `RepetitionLog.md`, если есть Active/Missed Repetition или следующий шаг
   связан с повторением: target, Failure Analysis и следующая дата.
6. `Practice.md`, если следующий шаг продолжает Attempt либо использует его как
   evidence: feedback, follow-ups и ссылки на `sessions/`.
7. `Knowledge.md`, если следующий шаг использует curated Knowledge,
   corrected misconception или sensitive claim; archive files — только по
   ссылкам активного evidence.
8. `topics/INDEX.md` перед state-changing edit для навигационной сверки пути;
   затем повторно сверяется `Goal.md` как источник истины.

### Обязательное содержание передачи

Кратко перечислить:

- Topic Workspace и Stable Slug;
- текущее Topic State, Active Block и **next safe action**;
- Role Mode текущего Physical Agent и точную Agent Write Boundary либо
  `Agent Proposal only`;
- open Weaknesses с severity и repair/retest;
- pending Source Checks с `SRC-*`, Used In и gate impact;
- Card Candidates с состоянием Duplicate Check и тем, что Card Promotion
  остаётся решением Orchestrator;
- Active Repetitions и missed/failed repetitions с требуемым follow-up;
- pending Checker findings, Completion Evidence и применимые stop conditions.

### `pause` и `resume`

`pause` сохраняет предыдущее рабочее состояние и next safe action в `Goal.md`;
если риск потери контекста высок, рядом создаётся `Handoff.md` со ссылками, а
не копиями owner state. `resume` читает список выше, сверяет снимок с owners и
возвращает Topic в предыдущий безопасный lifecycle state. Пропущенное
повторение фиксируется, а blocker Weakness и `needs-check` остаются видимыми.

**Stop condition:** не возобновлять state-changing работу, если следующий шаг
опирается на отсутствующее evidence, blocking Checker finding или неясную роль.
Поддерживающий агент при такой неопределённости передаёт предложение
Orchestrator.

## Шаблон условного `Handoff.md`

Используйте только при описанном риске и храните файл в Topic Workspace:

```md
# Handoff — <Topic>

- Создан: `YYYY-MM-DD`
- Причина: <риск потери контекста>
- Topic Workspace: `topics/<subject>/<stable-slug>/`
- Stable Slug: `<stable-slug>`
- Topic State: `<state>` (ссылка на `Goal.md`)
- Active Block: `<B*>` (ссылка на `Goal.md`)
- Next safe action: <действие + Entity References>
- Role Mode: <роль Physical Agent>
- Agent Write Boundary: <один append-only файл/раздел или Agent Proposal only>

## Обязательства для сверки с owner artifacts

- Open Weaknesses: <W-* references или `-`>
- Pending Source Checks: <SRC-* references или `-`>
- Card Candidates: <Q-* references или `-`>
- Active/Missed Repetitions: <REP-* references или `-`>
- Pending checker/gates: <finding и нужное действие или `-`>
```

Этот файл не создаёт нового состояния, не хранит сырые Session Notes и не
заменяет `Goal.md`, `Sources.md`, `Weaknesses.md`, `Questions.md` или
`RepetitionLog.md`.
