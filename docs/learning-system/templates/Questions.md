# <Название темы> — очередь вопросов (Question Queue)

## Шапка (Header)

- Тема (Topic): <тема>
- Стабильный slug (Stable Slug): `<stable-slug>`
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `YYYY-MM-DD`

## Граница владения (Ownership)

Этот файл владеет Question State и Card Candidate status. Запись вопроса живёт
в одном месте: меняется поле состояния, а не раздел файла. Card Promotion не
создаёт Anki-карточку автоматически.

## Question Index

| Question ID | Question Type | Question State | Linked Block | Card Candidate status | Weaknesses | Answer/Attempt |
|---|---|---|---|---|---|---|
| `Q-YYYYMMDD-01` | `recall` | `draft` | `[B01: название](Goal.md#b01---название)` | `none` | `-` | `-` |

## Question Records

### Q-YYYYMMDD-01 — <короткое название>

- ID: `Q-YYYYMMDD-01`
- Question Type: `recall | practice | interview | debugging | design-choice | card-candidate`
- Question State: `draft | active | answered | failed | promoted | archived | rejected`
- Linked Block: `[B01: название](Goal.md#b01---название)`
- Source: <Entity Reference, SRC reference или `-`>

#### Формулировка (Prompt)

<вопрос для recall, practice или разбора ошибки>

#### Ожидаемый ответ или критерии оценки (Expected Answer / Rubric)

<короткий ответ или rubric>

#### Evidence и traceability

- Answer/Attempt Link: `[PA-YYYYMMDD-01: название](Practice.md#pa-yyyymmdd-01---название)` или `-`
- Weakness Links: `[W-YYYYMMDD-01: название](Weaknesses.md#w-yyyymmdd-01---название)` или `-`
- Source Check: `[SRC-YYYYMMDD-01: название](Sources.md#src-yyyymmdd-01---название)`, `Нужно проверить` или `-`

#### Кандидат в карточку (Card Candidate)

- Card Candidate status: `none | candidate | rejected | promoted`
- Понимание и ценность: <evidence или `-`>
- Duplicate Check: <Obsidian + Anki summary или `-`>
- Card Trace: <Knowledge/Practice/Weakness/Source Entity References или `-`>
- Card Promotion: `skip | replace | merge | add | -`
- Dry-run preview: `-`
- User approval: `-`
- Anki write outcome: `-`

#### Anki write trace

- Target: deck, note type, fields и tags или `-`
- Anki Note ID: `-`
- Anki Card IDs: `-`
- Change reason (`replace`/`merge`): `-`
