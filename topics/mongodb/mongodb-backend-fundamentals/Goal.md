# MongoDB: базовая модель хранения, записи и чтения для backend — цель темы (Topic Goal)

## Шапка (Header)

- Учебный проект (Learning Project): Codex CLI learning system
- Учебный профиль (Learning Profile): Junior+/Middle Kotlin Backend для ЦУП РТ / АИС МИДИО
- Предмет (Subject): mongodb
- Тема (Topic): MongoDB: базовая модель хранения, записи и чтения для backend
- Стабильный slug (Stable Slug): `mongodb-backend-fundamentals`
- Рабочая папка темы (Topic Workspace): `topics/mongodb/mongodb-backend-fundamentals`
- Состояние темы (Topic State): `diagnosing`
- Активный блок (Active Block): [B01: документная модель MongoDB](Goal.md#b01---документная-модель-mongodb)
- Последнее обновление (Last Updated): `2026-08-25`

## Граница владения (Ownership)

Только этот файл владеет Topic State, Active Block, Block Status и Mastery Level.
Он хранит ссылки на evidence, но не тела evidence. Learning Orchestrator применяет
state-changing edits; supporting agents возвращают Agent Proposal.

## Управление темой (Topic Control)

- Зачем изучаем (Purpose): Понять, для чего MongoDB применяют в backend, как документная модель отличается от реляционной, как данные хранятся в коллекциях и документах, и что концептуально происходит при записи и чтении данных, чтобы осознанно выбирать MongoDB для backend-задач.
- Практический контекст (Applied Context): определить в diagnosing по Learning Profile.
- Текущий маршрут (Current Route): диагностика до построения Blocks.
- Главный риск забывания (Main Forgetting Risk): -

## Предпосылки (Prerequisites)

| Предпосылка | Статус | Evidence/Source | Действие |
|---|---|---|---|
| Реляционная модель и базовое понимание таблиц/строк | `partial` | [Q-20260825-01: выбор MongoDB или Postgres для данных интернет-магазина](Questions.md#q-20260825-01---выбор-mongodb-или-postgres-для-данных-интернет-магазина) | уточнить отличия документа от строки |

## Карта обучения (Learning Map)

| Block ID | Блок | Requirement | Mastery Level | Block Status | Evidence | Open Weaknesses | Next Action |
|---|---|---|---|---|---|---|---|
| [B01: документная модель MongoDB](Goal.md#b01---документная-модель-mongodb) | Документ, коллекция, вложенность, ссылки и граница документа. | `required` | `recognition` | `active` | [Q-20260825-01: выбор MongoDB или Postgres для данных интернет-магазина](Questions.md#q-20260825-01---выбор-mongodb-или-postgres-для-данных-интернет-магазина) | `-` | разобрать document/collection/embed/reference на простом примере |
| [B02: выбор MongoDB для backend](Goal.md#b02---выбор-mongodb-для-backend) | Когда MongoDB уместна, а когда Postgres проще и надежнее. | `required` | `recognition` | `not-started` | [Q-20260825-01: выбор MongoDB или Postgres для данных интернет-магазина](Questions.md#q-20260825-01---выбор-mongodb-или-postgres-для-данных-интернет-магазина) | `-` | вернуться после B01 |
| [B03: запись и чтение данных](Goal.md#b03---запись-и-чтение-данных) | Что концептуально происходит при insert/update/find и как это связано с индексами. | `required` | `recognition` | `not-started` | `-` | `-` | начать после B02 |
| [B04: риски моделирования](Goal.md#b04---риски-моделирования) | Растущие массивы, частые обновления, индексы и консистентность. | `required` | `recognition` | `not-started` | `-` | `-` | начать после B03 |

### B01 - документная модель MongoDB

- Цель блока: понять, что MongoDB хранит данные как документы в коллекциях, когда данные встраивают внутрь документа, а когда связывают ссылками.
- Практика: спроектировать документ товара и отделить вложенные данные от внешних сущностей.
- Gate: объяснить без подсказки разницу между документом, коллекцией, вложенным документом и ссылкой.

### B02 - выбор MongoDB для backend

- Цель блока: отличать случаи, где гибкая документная модель помогает, от случаев, где реляционная модель и строгие связи проще.
- Практика: выбрать MongoDB или Postgres для нескольких backend-сценариев и объяснить trade-off.
- Gate: назвать критерии выбора по паттернам чтения/записи, росту данных и консистентности.

### B03 - запись и чтение данных

- Цель блока: понять базовую механику записи, обновления и чтения документов без углубления в internals движка хранения.
- Практика: разобрать несколько запросов и объяснить, что ищется по индексу, а что требует сканирования.
- Gate: объяснить, почему индекс влияет на чтение и почему запись меняет не только документ, но и связанные индексы.

### B04 - риски моделирования

- Цель блока: увидеть типовые ошибки схемы MongoDB на backend-уровне.
- Практика: найти проблемы в модели товара, отзывов, остатков и истории цен.
- Gate: объяснить, почему бесконечно растущие массивы, частые независимые обновления и неправильные индексы опасны.
## Active Weakness Summary

| Weakness | Severity | Weakness Status | Linked Block | Required Repair |
|---|---|---|---|---|
| `-` | `-` | `-` | `-` | `-` |

Required Block не становится `stable`, пока связанное blocker Weakness открыто.

## Критерии завершения (Completion Criteria)

| Критерий | Нужное evidence | Статус | Linked Evidence |
|---|---|---|---|
| Все required Blocks — `stable`. | Learning Map и evidence. | `-` | `-` |
| Применимые реальные ограничения покрыты. | Practice/transfer/source evidence. | `-` | `-` |
| Нет открытых blocker Weaknesses. | Weakness Register. | `-` | `-` |
| Нет blocking `needs-check`. | Source Check Result. | `-` | `-` |

## Следующие действия (Next Actions)

1. Начать [B01: документная модель MongoDB](Goal.md#b01---документная-модель-mongodb): разобрать document, collection, embedded document и reference на примере товара интернет-магазина.
