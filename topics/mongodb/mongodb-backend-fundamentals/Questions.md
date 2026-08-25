# MongoDB: базовая модель хранения, записи и чтения для backend — очередь вопросов (Question Queue)

## Шапка (Header)

- Тема (Topic): MongoDB: базовая модель хранения, записи и чтения для backend
- Стабильный slug (Stable Slug): `mongodb-backend-fundamentals`
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `2026-08-25`

## Граница владения (Ownership)

Этот файл владеет Question State и Card Candidate status. Запись вопроса живёт
в одном месте: меняется поле состояния, а не раздел файла. Card Promotion не
создаёт Anki-карточку автоматически.

## Question Index

| Question ID | Question Type | Question State | Linked Block | Card Candidate status | Weaknesses | Answer/Attempt |
|---|---|---|---|---|---|---|
| [Q-20260825-01: выбор MongoDB или Postgres для данных интернет-магазина](Questions.md#q-20260825-01---выбор-mongodb-или-postgres-для-данных-интернет-магазина) | `practice` | `answered` | [B01: документная модель MongoDB](Goal.md#b01---документная-модель-mongodb), [B02: выбор MongoDB для backend](Goal.md#b02---выбор-mongodb-для-backend) | `none` | `-` | ответ принят как частичное evidence |

## Question Records

### Q-20260825-01 - выбор MongoDB или Postgres для данных интернет-магазина

- ID: `Q-20260825-01`
- Question Type: `practice`
- Question State: `answered`
- Linked Block: [B01: документная модель MongoDB](Goal.md#b01---документная-модель-mongodb), [B02: выбор MongoDB для backend](Goal.md#b02---выбор-mongodb-для-backend)
- Source: `-`

#### Формулировка (Prompt)

Представь backend для интернет-магазина с товарами, заказами, пользователями, корзиной и отзывами. Какие из этих данных ты бы мог хранить в MongoDB, какие скорее оставил бы в Postgres, и почему?

#### Ожидаемый ответ или критерии оценки (Expected Answer / Rubric)

Ответ должен отличать встраивание от ссылок по паттернам чтения/записи, росту данных и независимости обновлений. Нужна осторожность с утверждением "ACID значит только Postgres": MongoDB поддерживает атомарность документа и транзакции, но схема должна минимизировать необходимость междокументных транзакций.

#### Evidence и traceability

- Answer/Attempt Link: `-`
- Weakness Links: `-`
- Source Check: `-`
- Answer Summary: MongoDB подходит для товаров из-за разной структуры. Встраивать стоит то, что часто читается вместе с товаром: характеристики, текущую цену и, возможно, ограниченный срез отзывов. Данные, которые часто читаются отдельно, часто меняются независимо или растут как журнал, лучше выносить в отдельные документы: остатки на складе и историю изменения цены. Заказы, корзина, пользователи и отзывы были изначально отнесены к Postgres из-за ACID и одинаковой структуры.
- Feedback: Основной критерий сформулирован верно: моделирование в MongoDB должно идти от паттернов чтения/записи, а не только от формы данных. Уточнение: отзывы не стоит безусловно встраивать целиком; можно встроить ограниченный срез или агрегаты, а полный поток хранить отдельно.

#### Кандидат в карточку (Card Candidate)

- Card Candidate status: `none`
- Понимание и ценность: `-`
- Duplicate Check: `-`
- Card Trace: `-`
- Card Promotion: `-`
- Dry-run preview: `-`
- User approval: `-`
- Anki write outcome: `-`

#### Anki write trace

- Target: `-`
- Anki Note ID: `-`
- Anki Card IDs: `-`
- Change reason (`replace`/`merge`): `-`
