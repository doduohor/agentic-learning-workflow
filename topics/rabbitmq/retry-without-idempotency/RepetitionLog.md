# Retry без идемпотентности - журнал повторений (Repetition Log)

## Шапка (Header)

- Тема (Topic): retry без идемпотентности
- Стабильный slug (Stable Slug): `rabbitmq-retry-without-idempotency`
- Основной артефакт (Primary Artifact): Repetition Log
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `2026-08-24`

## Правила редактирования (Edit Policy)

- Повторение должно быть Active Repetition: recall, explain, apply, debug или transfer.
- `missed` означает, что повторение не выполнено вовремя; `failed` означает, что попытка была, но recall/application не удались.
- Repetition Failure должно открыть или обновить Weakness, если оно выявляет учебную проблему.
- Topic State, Active Block, Block Status и Mastery Level здесь не дублируются.

## Очередь повторений (Repetition Queue)

| ID повторения (Repetition ID) | Тип цели (Target Type) | Цель (Target) | Запланировано на (Scheduled For) | Действие (Action) | Результат (Result) | Следующее повторение (Next Repetition) |
|---|---|---|---|---|---|---|
| `REP-20260824-01` | `Question` | [Q-20260824-03: idempotency card candidate](Questions.md#q-20260824-03---idempotency-card-candidate) | `2026-08-26` | `explain` | `scheduled` | - |

## Записи повторений (Repetition Records)

### REP-20260824-01 - explain retry without idempotency

- ID повторения (Repetition ID): `REP-20260824-01`
- Тип цели (Target Type): `Question`
- Цель (Target): [Q-20260824-03: idempotency card candidate](Questions.md#q-20260824-03---idempotency-card-candidate)
- Запланировано на (Scheduled For): `2026-08-26`
- Выполнено в (Completed At): -
- Действие (Action): `explain`
- Результат (Result): `scheduled`
- Без подсказки? (No-Hint?): -
- Следующее повторение (Next Repetition): -

#### Анализ провала (Failure Analysis)

-

#### Связанное слабое место (Linked Weakness)

- -

## Провалы, открытые как слабые места (Failures Opened As Weaknesses)

| Провал повторения (Repetition Failure) | Слабое место (Weakness) | Действие (Action) |
|---|---|---|
| - | - | Провалов повторения пока нет. |
