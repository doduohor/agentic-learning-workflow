# Шаблоны Topic Workspace

Скопируйте семь файлов в новую папку `topics/<subject>/<stable-slug>/` и замените
угловые скобки значениями темы. Это human-first Markdown, а не YAML/JSON schema.
`sessions/` создавайте только для длинных Session Notes или Practice Artifacts; он
не владеет учебным состоянием.

## Общие соглашения

- `-` означает пустое, неприменимое или намеренно отсутствующее значение.
- `Нужно проверить` относится только к непроверенному утверждению. Результат его
  проверки принадлежит `Sources.md`.
- Entity Reference: `[B01: название](Goal.md#b01---название)`; идентификатор,
  короткий смысл и Markdown-ссылка всегда идут вместе.
- Форматы ID: `B01`, `Q-YYYYMMDD-NN`, `PA-YYYYMMDD-NN`, `W-YYYYMMDD-NN`,
  `REP-YYYYMMDD-NN`, `SRC-YYYYMMDD-NN`; Stable Slug — ASCII kebab-case.

## Допустимые значения

| Поле | Значения |
|---|---|
| Topic State | `intake`, `diagnosing`, `planned`, `learning`, `practicing`, `reviewing`, `completed`, `paused` |
| Block Status | `not-started`, `active`, `blocked`, `ready-for-review`, `stable`, `deferred` |
| Mastery Level | `recognition`, `recall`, `application`, `transfer`, `production-ready`, `stable` |
| Practice Attempt Result | `unchecked`, `passed`, `partial`, `failed`, `rework-needed` |
| Question State | `draft`, `active`, `answered`, `failed`, `promoted`, `archived`, `rejected` |
| Card Candidate status | `none`, `candidate`, `rejected`, `promoted` |
| Weakness Status | `open`, `repairing`, `retest-needed`, `resolved`, `archived` |
| Repetition Result | `scheduled`, `passed`, `partial`, `failed`, `missed` |
| Source Check Result | `verified`, `rejected`, `needs-check`, `superseded` |

`production-ready` используйте только когда реальные ограничения применения важны
для Topic или Learning Profile. Полные правила и границы ролей: [общий контракт
агентов](../agent-common-instructions.md).

## Необязательный архив сессии

Путь: `sessions/YYYY-MM-DD-<short-slug>.md`. Минимальные разделы: `Session`,
`Raw Notes`, `Practice Artifacts`, `Extracted Follow-Ups`, `Source Check Warnings`,
`Notes After Curation`. Основные артефакты ссылаются на архив, а не дублируют его.
