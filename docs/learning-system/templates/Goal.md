# <Название темы> — цель темы (Topic Goal)

## Шапка (Header)

- Учебный проект (Learning Project): <проект>
- Учебный профиль (Learning Profile): <профиль>
- Предмет (Subject): <subject>
- Тема (Topic): <тема>
- Стабильный slug (Stable Slug): `<stable-slug>`
- Рабочая папка темы (Topic Workspace): `topics/<subject>/<stable-slug>/`
- Состояние темы (Topic State): `intake`
- Активный блок (Active Block): `-`
- Последнее обновление (Last Updated): `YYYY-MM-DD`

## Граница владения (Ownership)

Только этот файл владеет Topic State, Active Block, Block Status и Mastery Level.
Он хранит ссылки на evidence, но не тела evidence. Learning Orchestrator применяет
state-changing edits; supporting agents возвращают Agent Proposal.

## Управление темой (Topic Control)

- Зачем изучаем (Purpose): <1–3 предложения>
- Практический контекст (Applied Context): <сценарий Learning Profile>
- Текущий маршрут (Current Route): <required Blocks>
- Главный риск забывания (Main Forgetting Risk): <риск>

## Предпосылки (Prerequisites)

| Предпосылка | Статус | Evidence/Source | Действие |
|---|---|---|---|
| <предпосылка> | <статус> | <Entity Reference или `-`> | <следующее действие> |

## Карта обучения (Learning Map)

| Block ID | Блок | Requirement | Mastery Level | Block Status | Evidence | Open Weaknesses | Next Action |
|---|---|---|---|---|---|---|---|
| `B01` | <название> | `required` | `recognition` | `not-started` | `-` | `-` | <действие> |

### B01 — <название блока>

Краткая роль блока и его граница. Подробное knowledge, practice и evidence живут
в связанных owner files.

## Active Weakness Summary

| Weakness | Severity | Weakness Status | Linked Block | Required Repair |
|---|---|---|---|---|
| <Entity Reference или `-`> | `-` | `-` | <Entity Reference или `-`> | `-` |

Required Block не становится `stable`, пока связанное blocker Weakness открыто.

## Критерии завершения (Completion Criteria)

| Критерий | Нужное evidence | Статус | Linked Evidence |
|---|---|---|---|
| Все required Blocks — `stable`. | Learning Map и evidence. | `-` | `-` |
| Применимые реальные ограничения покрыты. | Practice/transfer/source evidence. | `-` | `-` |
| Нет открытых blocker Weaknesses. | Weakness Register. | `-` | `-` |
| Нет blocking `needs-check`. | Source Check Result. | `-` | `-` |

## Следующие действия (Next Actions)

1. <следующее действие>
