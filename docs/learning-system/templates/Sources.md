# <Название темы> — записи источников (Source Record)

## Шапка (Header)

- Тема (Topic): <тема>
- Стабильный slug (Stable Slug): `<stable-slug>`
- Связанная цель (Related Goal): [Goal.md](Goal.md)
- Последнее обновление (Last Updated): `YYYY-MM-DD`

## Граница владения (Ownership)

Этот файл владеет Source Records и Source Check Result. Для version-sensitive,
application-sensitive, production, security, tooling-behavior и protocol claims
нужен Source Check. Непроверенный claim имеет `needs-check` и метку `Нужно
проверить`; он не проходит чувствительные gates.

## Source Check Index

| Source ID | Claim | Sensitivity | Authority Type | Checked At | Source Check Result | Used In |
|---|---|---|---|---|---|---|
| `SRC-YYYYMMDD-01` | <claim> | `version-sensitive` | `official-docs` | `-` | `needs-check` | <Entity Reference> |

## Source Checks

### SRC-YYYYMMDD-01 — <короткое название>

- ID: `SRC-YYYYMMDD-01`
- Claim: <проверяемое утверждение>
- Sensitivity: `version-sensitive | application-sensitive | production | security | tooling-behavior | protocol-semantics | durable-concept`
- Source URL/Reference: <URL/RFC/docs/book или `Нужно проверить`>
- Authority Type: `official-docs | spec-rfc | release-notes | vendor-blog | engineering-article | community-discussion | course-book`
- Checked At: `YYYY-MM-DD` или `-`
- Source Check Result: `verified | rejected | needs-check | superseded`
- Used In: <Entity References или `-`>
- Next Check: `YYYY-MM-DD` или `-`

#### Заметки (Notes)

<короткий пересказ; не копировать источник>

## Source Notes

- <SRC Entity Reference> — <короткая заметка>
