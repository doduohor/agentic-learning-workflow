# <Название темы> — реестр слабых мест (Weakness Register)

## Шапка (Header)

- Тема (Topic): <тема>
- Стабильный slug (Stable Slug): `<stable-slug>`
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `YYYY-MM-DD`

## Граница владения (Ownership)

Этот файл владеет Weakness Status, severity, Repair Action и Resolution Evidence.
Learning Orchestrator — единственный автор изменений. Evidence-backed Weakness
открывается только с проверяемым evidence; pre-evidence risk не получает `W-*`.

## Weakness Index

| Weakness ID | Type | Severity | Weakness Status | Linked Block | Evidence | Repair Action |
|---|---|---|---|---|---|---|
| `W-YYYYMMDD-01` | `gap` | `major` | `open` | `[B01: название](Goal.md#b01---название)` | <Entity Reference> | <действие> |

## Weakness Records

### W-YYYYMMDD-01 — <короткое название>

- ID: `W-YYYYMMDD-01`
- Type: `gap | misconception | fragile-skill | application-blind-spot`
- Severity: `minor | major | blocker`
- Weakness Status: `open | repairing | retest-needed | resolved | archived`
- Linked Block: `[B01: название](Goal.md#b01---название)`
- Card Candidate status: `none | candidate | rejected | promoted`

#### Evidence

- <Practice Attempt, failed Question, Repetition Failure или interview answer>

#### Наблюдаемый паттерн ошибки (Observed Pattern)

<что идёт не так>

#### Repair Action и ретест (Retest)

- Repair Action: <конкретное действие>
- Retest Plan: <как доказать исправление>
- Resolution Evidence: <Entity Reference или `-`>

## Resolved/Archived Summary

| Weakness | Final Status | Resolution Evidence | Notes |
|---|---|---|---|
| `-` | `-` | `-` | `-` |
