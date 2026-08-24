# <Название темы> — журнал повторений (Repetition Log)

## Шапка (Header)

- Тема (Topic): <тема>
- Стабильный slug (Stable Slug): `<stable-slug>`
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `YYYY-MM-DD`

## Граница владения (Ownership)

Этот файл владеет Active Repetition records и results. Повторение требует
действия `recall`, `explain`, `apply`, `debug` или `transfer`. `failed` и
`partial` при учебной проблеме создают или обновляют Weakness через Orchestrator.

## Repetition Queue

| Repetition ID | Target Type | Target | Scheduled For | Action | Repetition Result | Next Repetition |
|---|---|---|---|---|---|---|
| `REP-YYYYMMDD-01` | `Question` | `[Q-YYYYMMDD-01: название](Questions.md#q-yyyymmdd-01---название)` | `YYYY-MM-DD` | `recall` | `scheduled` | `-` |

## Active Repetition Records

### REP-YYYYMMDD-01 — <короткое название>

- ID: `REP-YYYYMMDD-01`
- Target Type: `Question | Block | Weakness`
- Target: `[Q-YYYYMMDD-01: название](Questions.md#q-yyyymmdd-01---название)`
- Scheduled For: `YYYY-MM-DD`
- Completed At: `YYYY-MM-DD` или `-`
- Action: `recall | explain | apply | debug | transfer`
- Repetition Result: `scheduled | passed | partial | failed | missed`
- No-Hint?: `yes | no | -`
- Next Repetition: `YYYY-MM-DD` или `-`

#### Результат и traceability

- Result evidence: <Entity Reference или `-`>
- Failure Analysis: <текст или `-`>
- Linked Weakness: <W Entity Reference или `-`>

## Failures Opened As Weaknesses

| Repetition Failure | Weakness | Action |
|---|---|---|
| `-` | `-` | `-` |
