# Retry без идемпотентности - реестр слабых мест (Weakness Register)

## Шапка (Header)

- Тема (Topic): retry без идемпотентности
- Стабильный slug (Stable Slug): `rabbitmq-retry-without-idempotency`
- Основной артефакт (Primary Artifact): Weakness Register
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `2026-08-24`

## Правила редактирования (Edit Policy)

- Weakness записывается только при наличии Weakness Evidence.
- Каждое открытое `major` или `blocker` Weakness должно иметь Repair Action.
- Статус `resolved` требует Resolution Evidence.
- `blocker` Weakness блокирует закрытие блока и темы через `Goal.md`.
- Topic State, Active Block, Block Status и Mastery Level здесь не дублируются.

## Индекс слабых мест (Weakness Index)

| ID слабого места (Weakness ID) | Тип (Type) | Серьезность (Severity) | Статус (Status) | Связанный блок (Linked Block) | Доказательство (Evidence) | Действие (Action) |
|---|---|---|---|---|---|---|
| - | - | - | - | - | - | Evidence-backed Weaknesses пока не открыты. |

## Risk Index Without Weakness Records

Этот prototype содержит риск слабого места, но не создает Weakness ID: реальной неудачной попытки learner еще нет, а правила системы требуют evidence перед открытием Weakness.

| Риск | Возможный тип Weakness | Где проявится | Как открыть запись, если подтвердится |
|---|---|---|---|
| Learner может считать DLQ достаточной защитой от повторных побочных эффектов. | `application-blind-spot` | [PA-20260824-01: retry safety sketch](Practice.md#pa-20260824-01---retry-safety-sketch), [Q-20260824-04: duplicate side effect debugging](Questions.md#q-20260824-04---duplicate-side-effect-debugging) | После failed/partial ответа создать новый `W-YYYYMMDD-NN` с evidence на попытку или вопрос. |

## Записи слабых мест (Weakness Records)

Evidence-backed Weakness Records пока отсутствуют.

## Сводка исправленных/архивных (Resolved/Archived Summary)

| Слабое место (Weakness) | Финальный статус (Final Status) | Доказательство исправления (Resolution Evidence) | Заметки (Notes) |
|---|---|---|---|
| - | - | - | Исправленных или архивных Weaknesses пока нет. |
