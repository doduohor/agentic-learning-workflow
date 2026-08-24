# Retry без идемпотентности - цель темы (Topic Goal)

## Шапка (Header)

- Учебный проект (Learning Project): Codex CLI learning system
- Учебный профиль (Learning Profile): Junior+/Middle Kotlin Backend для ЦУП РТ / АИС МИДИО
- Предмет (Subject): RabbitMQ
- Тема (Topic): retry без идемпотентности
- Стабильный slug (Stable Slug): `rabbitmq-retry-without-idempotency`
- Рабочая папка темы (Topic Workspace): `topics/rabbitmq/retry-without-idempotency`
- Состояние темы (Topic State): `learning`
- Активный блок (Active Block): [B01: retry mental model](#b01---retry-mental-model)
- Последнее обновление (Last Updated): `2026-08-24`

## Правила редактирования (Edit Policy)

- Learning Orchestrator владеет Topic State, Active Block, Block Status и Mastery Level.
- Supporting agents могут предлагать изменения, но state-changing edits требуют Orchestrator review.
- Сырые заметки, длинные объяснения, тела практических попыток и выдержки из источников здесь не хранятся.
- `Goal.md` хранит краткие ссылки на evidence; сами evidence живут в других артефактах темы.

## Управление темой (Topic Control)

- Зачем изучаем (Purpose): научиться видеть, почему повторная доставка сообщения сама по себе не делает обработку безопасной. Тема нужна для backend-сервисов, где RabbitMQ используется для фоновых задач, интеграционных событий или отложенной обработки.
- Практический контекст (Applied Context): Ktor-сервис обрабатывает команду бронирования спортивного объекта через RabbitMQ consumer; повторная доставка может привести к повторному списанию квоты, повторной записи события или лишнему внешнему вызову.
- Текущий маршрут (Current Route): сначала различить retry и идемпотентность, затем спроектировать безопасную границу обработки, затем понять место DLQ.
- Главный риск забывания (Main Forgetting Risk): начать чинить временную ошибку через retry и случайно усилить побочный эффект, потому что обработчик не умеет безопасно переживать повтор.

## Предпосылки (Prerequisites)

| Предпосылка (Prerequisite) | Статус (Status) | Доказательство/источник (Evidence/Source) | Действие (Action) |
|---|---|---|---|
| Понимать базовую модель producer, queue, consumer и ack/nack в RabbitMQ. | assumed | [SRC-20260824-01: RabbitMQ dead-letter behavior](Sources.md#src-20260824-01---rabbitmq-dead-letter-behavior) | Нужно проверить детали RabbitMQ перед переносом знания в долгосрочную базу. |
| Понимать, что обработчик сообщения может иметь побочные эффекты в Postgres или внешнем сервисе. | assumed | - | Проверить через [PA-20260824-01: retry safety sketch](Practice.md#pa-20260824-01---retry-safety-sketch). |

## Карта обучения (Learning Map)

| ID блока (Block ID) | Блок (Block) | Обязательность (Requirement) | Уровень освоения (Mastery Level) | Статус (Status) | Доказательства (Evidence) | Открытые слабые места (Open Weaknesses) | Следующее действие (Next Action) |
|---|---|---|---|---|---|---|---|
| `B01` | retry mental model | `required` | `recognition` | `active` | [Knowledge B01](Knowledge.md#b01---retry-mental-model), [Q-20260824-01: retry vs idempotency](Questions.md#q-20260824-01---retry-vs-idempotency) | - | Выполнить [PA-20260824-01: retry safety sketch](Practice.md#pa-20260824-01---retry-safety-sketch). |
| `B02` | идемпотентная граница consumer | `required` | `recognition` | `not-started` | [Q-20260824-03: idempotency card candidate](Questions.md#q-20260824-03---idempotency-card-candidate) | - | После B01 описать, где хранить ключ идемпотентности. |
| `B03` | DLQ как диагностика, а не починка идемпотентности | `required` | `recognition` | `not-started` | [SRC-20260824-01: RabbitMQ dead-letter behavior](Sources.md#src-20260824-01---rabbitmq-dead-letter-behavior) | - | Проверить источник и разобрать, когда сообщение уходит в DLQ. |

### B01 - retry mental model

- Смысл блока: различить "попробовать снова" и "сделать повтор безопасным".
- Минимальное evidence для движения дальше: no-hint объяснение, checked practice attempt и активное повторение по вопросу B01.

### B02 - идемпотентная граница consumer

- Смысл блока: определить, где consumer распознает повтор и как это связано с транзакцией приложения.
- Минимальное evidence для движения дальше: design-choice ответ по хранению ключа идемпотентности.

### B03 - DLQ как диагностика, а не починка идемпотентности

- Смысл блока: понять, что DLQ помогает изолировать проблемное сообщение, но не делает побочные эффекты безопасными.
- Минимальное evidence для движения дальше: проверенный источник и разбор failure mode.

## Сводка активных слабых мест (Active Weakness Summary)

Evidence-backed Weaknesses пока не открыты: это prototype workspace до реальной попытки learner. Наблюдаемый риск записан в [Weaknesses.md](Weaknesses.md#risk-index-without-weakness-records) без Weakness ID, чтобы не нарушать правило "Weakness требует evidence".

## Критерии завершения (Completion Criteria)

| Критерий (Criterion) | Нужное доказательство (Required Evidence) | Статус (Status) | Связанное доказательство (Linked Evidence) |
|---|---|---|---|
| Все required Blocks стали `stable`. | Learning Map показывает `stable` для B01, B02 и B03. | open | - |
| Блоки с реальными ограничениями применения достигли `production-ready` или `stable`. | Practice и Questions покрывают retry, идемпотентность, DLQ и риск повторных побочных эффектов. | open | [PA-20260824-01: retry safety sketch](Practice.md#pa-20260824-01---retry-safety-sketch) |
| Нет открытых blocker Weaknesses. | Weakness Register не содержит связанных открытых blocker Weaknesses. | open | [Weaknesses.md](Weaknesses.md) |
| Чувствительные claims либо проверены, либо явно помечены. | `Sources.md` содержит Source Records для RabbitMQ behavior claims. | open | [SRC-20260824-01: RabbitMQ dead-letter behavior](Sources.md#src-20260824-01---rabbitmq-dead-letter-behavior) |

## Следующие действия (Next Actions)

1. Выполнить [PA-20260824-01: retry safety sketch](Practice.md#pa-20260824-01---retry-safety-sketch) без подсказок.
2. Ответить на [Q-20260824-01: retry vs idempotency](Questions.md#q-20260824-01---retry-vs-idempotency).
3. Проверить [SRC-20260824-01: RabbitMQ dead-letter behavior](Sources.md#src-20260824-01---rabbitmq-dead-letter-behavior) перед повышением уверенности в RabbitMQ-specific claims.
