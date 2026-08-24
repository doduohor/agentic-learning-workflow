# Retry без идемпотентности - записи источников (Source Record)

## Шапка (Header)

- Тема (Topic): retry без идемпотентности
- Стабильный slug (Stable Slug): `rabbitmq-retry-without-idempotency`
- Основной артефакт (Primary Artifact): Source Record
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `2026-08-24`

## Правила редактирования (Edit Policy)

- Для version-sensitive, application-sensitive, production, security, protocol и tooling-behavior claims нужны Authoritative Sources.
- Для version/security/protocol claims предпочтительны `official-docs`, `spec-rfc` и `release-notes`.
- Source Notes должны быть коротким пересказом, а не скопированной документацией.
- Непроверенные утверждения получают `Result: needs-check` и могут упоминаться в других артефактах как `Нужно проверить`.
- Topic State, Active Block, Block Status и Mastery Level здесь не дублируются.

## Индекс проверок источников (Source Check Index)

| ID источника (Source ID) | Утверждение (Claim) | Чувствительность (Sensitivity) | Тип авторитетности (Authority Type) | Дата проверки (Checked At) | Результат (Result) | Где используется (Used In) |
|---|---|---|---|---|---|---|
| `SRC-20260824-01` | RabbitMQ dead-letter behavior for rejected/nacked/requeued/expired messages and delivery limits must be checked before teaching as exact mechanics. | `tooling-behavior` | `official-docs` | - | `needs-check` | [Knowledge B01](Knowledge.md#b01---retry-mental-model), [Q-20260824-04: duplicate side effect debugging](Questions.md#q-20260824-04---duplicate-side-effect-debugging) |

## Проверки источников (Source Checks)

### SRC-20260824-01 - RabbitMQ dead-letter behavior

- ID источника (Source ID): `SRC-20260824-01`
- Утверждение (Claim): RabbitMQ-specific mechanics of when a message is requeued, redelivered, rejected, nacked, dead-lettered, expired, or limited by delivery count require current official documentation before they are treated as verified.
- Чувствительность (Sensitivity): `tooling-behavior`
- URL/ссылка на источник (Source URL/Reference): Нужно проверить official RabbitMQ documentation for consumers, acknowledgements, dead lettering, TTL, and quorum queue delivery limit.
- Тип авторитетности (Authority Type): `official-docs`
- Дата проверки (Checked At): -
- Результат (Result): `needs-check`
- Где используется (Used In): [Knowledge B01](Knowledge.md#b01---retry-mental-model), [Q-20260824-04: duplicate side effect debugging](Questions.md#q-20260824-04---duplicate-side-effect-debugging), [B03: DLQ как диагностика](Goal.md#b03---dlq-как-диагностика-а-не-починка-идемпотентности)
- Следующая проверка (Next Check): перед повышением B03 выше `recognition`

#### Заметки (Notes)

Этот Source Record намеренно оставлен в `needs-check`: prototype проверяет форму рабочего пространства, а не решает полный source verification workflow.

## Заметки по источникам (Source Notes)

- [SRC-20260824-01: RabbitMQ dead-letter behavior](#src-20260824-01---rabbitmq-dead-letter-behavior) - нужен как guardrail для RabbitMQ-specific claims в `Knowledge.md` и `Questions.md`.
