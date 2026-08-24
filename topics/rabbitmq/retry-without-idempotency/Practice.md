# Retry без идемпотентности - журнал практики (Practice Journal)

## Шапка (Header)

- Тема (Topic): retry без идемпотентности
- Стабильный slug (Stable Slug): `rabbitmq-retry-without-idempotency`
- Основной артефакт (Primary Artifact): Practice Journal
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `2026-08-24`

## Правила редактирования (Edit Policy)

- Тело Practice Attempt становится append-only после первичной записи.
- Feedback, Corrections, Linked Weaknesses, Promoted Knowledge и Follow-up Questions дописываются под той же попыткой.
- Длинный сырой материал хранится в optional Session Archive; здесь остаются структурированные попытки и evidence.
- Topic State, Active Block, Block Status и Mastery Level здесь не дублируются.

## Индекс практических попыток (Practice Attempt Index)

| ID попытки (Practice Attempt ID) | Дата сессии (Session Date) | Связанный блок (Linked Block) | Результат (Result) | Доказательство для (Evidence Use) | Слабые места (Weaknesses) | Перенесенное знание (Promoted Knowledge) |
|---|---|---|---|---|---|---|
| `PA-20260824-01` | `2026-08-24` | [B01: retry mental model](Goal.md#b01---retry-mental-model) | `unchecked` | Проверить, может ли learner объяснить безопасный retry-сценарий до кода. | - | [B01: retry mental model](Knowledge.md#b01---retry-mental-model) |

## Практические попытки (Practice Attempts)

### PA-20260824-01 - retry safety sketch

- ID практической попытки (Practice Attempt ID): `PA-20260824-01`
- Дата сессии (Session Date): `2026-08-24`
- Связанный блок (Linked Block): [B01: retry mental model](Goal.md#b01---retry-mental-model)
- Задание (Prompt/Task): Нарисовать или описать поток обработки сообщения `ReserveFacilitySlotRequested`: получение сообщения, запись в Postgres, подтверждение брокеру, падение между записью и подтверждением, повторная доставка. Отдельно указать, где нужна идемпотентная проверка.
- Артефакты (Artifacts): -
- Результат (Result): `unchecked`

#### Тело попытки (Attempt Body)

Планируемая попытка: learner должен без подсказок указать, какой побочный эффект уже мог произойти до retry, и почему повторная доставка требует проверки бизнес-ключа или другого идемпотентного guard.

#### Обратная связь (Feedback)

- Попытка еще не проверена.

#### Исправления (Corrections)

- -

#### Связанные слабые места (Linked Weaknesses)

- -

#### Знание, перенесенное в Knowledge.md (Promoted Knowledge)

- [B01: retry mental model](Knowledge.md#b01---retry-mental-model)

#### Последующие вопросы (Follow-up Questions)

- [Q-20260824-02: safe retry design](Questions.md#q-20260824-02---safe-retry-design)
- [Q-20260824-04: duplicate side effect debugging](Questions.md#q-20260824-04---duplicate-side-effect-debugging)

## Ссылки на архивы сессий (Session Archive Links)

| Дата (Date) | Архив (Archive) | Причина архивации (Why Archived) | Связанные попытки (Linked Attempts) |
|---|---|---|---|
| `2026-08-24` | - | Архив не нужен: prototype содержит одну короткую planned попытку. | `PA-20260824-01` |
