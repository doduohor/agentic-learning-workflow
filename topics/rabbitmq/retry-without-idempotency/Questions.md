# Retry без идемпотентности - очередь вопросов (Question Queue)

## Шапка (Header)

- Тема (Topic): retry без идемпотентности
- Стабильный slug (Stable Slug): `rabbitmq-retry-without-idempotency`
- Основной артефакт (Primary Artifact): Question Queue
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `2026-08-24`

## Правила редактирования (Edit Policy)

- Здесь хранится полный lifecycle вопроса.
- Question record живет в одном месте; при изменении меняется поле Question State, а не раздел файла.
- Card Promotion требует понимания, проверки релевантности, проверки дублей в Obsidian и проверки дублей в Anki.
- Anki-карточки автоматически из этого файла не создаются.
- Topic State, Active Block, Block Status и Mastery Level здесь не дублируются.

## Индекс вопросов (Question Index)

| ID вопроса (Question ID) | Тип (Question Type) | Состояние (Question State) | Связанный блок (Linked Block) | Кандидат в карточку (Card Candidate) | Слабые места (Weaknesses) | Ответ/попытка (Answer/Attempt) |
|---|---|---|---|---|---|---|
| `Q-20260824-01` | `recall` | `active` | [B01: retry mental model](Goal.md#b01---retry-mental-model) | `none` | - | - |
| `Q-20260824-02` | `design-choice` | `draft` | [B02: идемпотентная граница consumer](Goal.md#b02---идемпотентная-граница-consumer) | `none` | - | [PA-20260824-01: retry safety sketch](Practice.md#pa-20260824-01---retry-safety-sketch) |
| `Q-20260824-03` | `card-candidate` | `active` | [B01: retry mental model](Goal.md#b01---retry-mental-model) | `candidate` | - | - |
| `Q-20260824-04` | `debugging` | `draft` | [B03: DLQ as diagnosis](Goal.md#b03---dlq-как-диагностика-а-не-починка-идемпотентности) | `none` | - | [PA-20260824-01: retry safety sketch](Practice.md#pa-20260824-01---retry-safety-sketch) |

## Записи вопросов (Question Records)

### Q-20260824-01 - retry vs idempotency

- ID вопроса (Question ID): `Q-20260824-01`
- Тип вопроса (Question Type): `recall`
- Состояние вопроса (Question State): `active`
- Связанный блок (Linked Block): [B01: retry mental model](Goal.md#b01---retry-mental-model)
- Источник (Source): [Knowledge B01](Knowledge.md#b01---retry-mental-model)

#### Формулировка (Prompt)

Чем retry отличается от идемпотентности в consumer, который обрабатывает RabbitMQ-сообщение?

#### Ожидаемый ответ или критерии оценки (Expected Answer / Rubric)

Retry повторяет попытку обработки после сбоя. Идемпотентность делает повтор безопасным для бизнес-состояния и побочных эффектов. Хороший ответ отдельно называет сценарий частичного успеха: запись в Postgres прошла, подтверждение сообщения не дошло, сообщение доставили повторно.

#### Ссылка на ответ/попытку (Answer/Attempt Link)

- -

#### Связанные слабые места (Weakness Links)

- -

#### Кандидат в карточку (Card Candidate)

- Статус (Status): `none`
- Проверка дублей (Duplicate Check): -
- След карточки (Card Trace): -
- Решение о продвижении в Anki (Promotion Decision): -

### Q-20260824-02 - safe retry design

- ID вопроса (Question ID): `Q-20260824-02`
- Тип вопроса (Question Type): `design-choice`
- Состояние вопроса (Question State): `draft`
- Связанный блок (Linked Block): [B02: идемпотентная граница consumer](Goal.md#b02---идемпотентная-граница-consumer)
- Источник (Source): [PA-20260824-01: retry safety sketch](Practice.md#pa-20260824-01---retry-safety-sketch)

#### Формулировка (Prompt)

Где безопаснее поставить идемпотентную проверку для команды бронирования: только в памяти consumer, в Postgres рядом с бизнес-операцией или только перед отправкой ack? Объясни критерий выбора.

#### Ожидаемый ответ или критерии оценки (Expected Answer / Rubric)

Для надежного backend-сервиса проверка должна переживать падение процесса, поэтому in-memory guard недостаточен. Обычно нужна устойчивая запись или constraint рядом с бизнес-операцией, чтобы повтор после сбоя видел уже выполненную команду.

#### Ссылка на ответ/попытку (Answer/Attempt Link)

- [PA-20260824-01: retry safety sketch](Practice.md#pa-20260824-01---retry-safety-sketch)

#### Связанные слабые места (Weakness Links)

- -

#### Кандидат в карточку (Card Candidate)

- Статус (Status): `none`
- Проверка дублей (Duplicate Check): -
- След карточки (Card Trace): -
- Решение о продвижении в Anki (Promotion Decision): -

### Q-20260824-03 - idempotency card candidate

- ID вопроса (Question ID): `Q-20260824-03`
- Тип вопроса (Question Type): `card-candidate`
- Состояние вопроса (Question State): `active`
- Связанный блок (Linked Block): [B01: retry mental model](Goal.md#b01---retry-mental-model)
- Источник (Source): [Knowledge B01](Knowledge.md#b01---retry-mental-model)

#### Формулировка (Prompt)

Почему retry без идемпотентной границы может ухудшить надежность consumer вместо того, чтобы ее повысить?

#### Ожидаемый ответ или критерии оценки (Expected Answer / Rubric)

Потому что retry повторяет обработку после неопределенного исхода. Если первый запуск уже сделал побочный эффект, повтор может продублировать бизнес-операцию, событие или внешний вызов.

#### Ссылка на ответ/попытку (Answer/Attempt Link)

- -

#### Связанные слабые места (Weakness Links)

- -

#### Кандидат в карточку (Card Candidate)

- Статус (Status): `candidate`
- Проверка дублей (Duplicate Check): Obsidian не проверен; Anki не проверен; promotion запрещен до duplicate checks.
- След карточки (Card Trace): [Knowledge B01](Knowledge.md#b01---retry-mental-model), [B01: retry mental model](Goal.md#b01---retry-mental-model), [PA-20260824-01: retry safety sketch](Practice.md#pa-20260824-01---retry-safety-sketch)
- Решение о продвижении в Anki (Promotion Decision): -

### Q-20260824-04 - duplicate side effect debugging

- ID вопроса (Question ID): `Q-20260824-04`
- Тип вопроса (Question Type): `debugging`
- Состояние вопроса (Question State): `draft`
- Связанный блок (Linked Block): [B03: DLQ as diagnosis](Goal.md#b03---dlq-как-диагностика-а-не-починка-идемпотентности)
- Источник (Source): [SRC-20260824-01: RabbitMQ dead-letter behavior](Sources.md#src-20260824-01---rabbitmq-dead-letter-behavior)

#### Формулировка (Prompt)

В логах видно два успешных создания одной брони после временного падения consumer. Сообщение потом ушло в DLQ. Почему DLQ не доказывает, что бизнес-состояние осталось корректным?

#### Ожидаемый ответ или критерии оценки (Expected Answer / Rubric)

DLQ говорит, что сообщение изолировано после неуспешной обработки или политики доставки, но не отменяет уже сделанные приложением побочные эффекты. Нужно проверять бизнес-таблицы, идемпотентный ключ и порядок commit/ack.

#### Ссылка на ответ/попытку (Answer/Attempt Link)

- [PA-20260824-01: retry safety sketch](Practice.md#pa-20260824-01---retry-safety-sketch)

#### Связанные слабые места (Weakness Links)

- -

#### Кандидат в карточку (Card Candidate)

- Статус (Status): `none`
- Проверка дублей (Duplicate Check): -
- След карточки (Card Trace): -
- Решение о продвижении в Anki (Promotion Decision): -
