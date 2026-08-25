---
name: learn-report
description: "Показать read-only отчёт на русском по активным Topic и рабочим долгам."
---

# learn-report

Используй этот skill, когда пользователь хочет понять, какие Topic сейчас
активны, где остановилась работа, что заблокировано и какой следующий шаг
безопасен.

Отвечай на русском. Этот skill строго read-only: он не изменяет файлы, не
исправляет индекс и не применяет proposed changes.

Сначала прочитай:

- `CONTEXT.md`
- `docs/wayfinder/00-map.md`
- `topics/INDEX.md`
- `docs/learning-system/topic-lifecycle-skills.md`
- `docs/learning-system/lifecycle-command-interface.md`
- `docs/learning-system/agent-common-instructions.md`
- `docs/learning-system/session-handoff-workflow.md`
- `docs/learning-system/templates/README.md`
- `docs/wayfinder/decisions/13-design-topic-lifecycle-skills.md`

## Workflow

1. Прочитай `topics/INDEX.md`.
2. Найди active Topics со state `intake`, `diagnosing`, `planned`, `learning`,
   `practicing`, `reviewing` или `paused`.
3. Для каждой active Topic прочитай `Goal.md`. Если Topic State, Active Block
   или Next Actions расходятся с индексом, в отчете явно покажи предупреждение
   и доверяй `Goal.md`.
4. Запусти read-only Lightweight Checker для каждой active Topic:

   ```bash
   python3 tools/check_topic_workspace.py topics/INDEX.md topics/<subject>/<stable-slug>
   ```

   Если прямой запуск невозможен, прочитай нужные owner artifacts и честно отметь,
   что `tools/check_topic_workspace.py` не был выполнен.

5. При необходимости прочитай `Weaknesses.md`, `Sources.md` и
   `RepetitionLog.md`, чтобы показать:
   - blocker Weaknesses;
   - pending Source Checks;
   - active/missed repetitions.
6. Сформируй короткий рабочий отчет.

## Output Shape

По умолчанию используй такой формат:

```md
## Активные темы

### <Topic>

- Состояние: `<Topic State>`
- Рабочая папка: `topics/<subject>/<stable-slug>/`
- Активный блок: <Active Block или `-`>
- Следующий безопасный шаг: <Next Actions>
- Блокирующие слабые места: <W-* или `-`>
- Непроверенные источники: <SRC-* или `-`>
- Повторения: <active/missed или `-`>
- Проверка workspace: <кратко errors/warnings или `без блокирующих ошибок`>
```

Если активных тем нет, скажи это прямо и предложи следующий безопасный шаг:
запустить `learn-start` для новой Topic или просмотреть завершенные темы.

## Stop Conditions

- `topics/INDEX.md` отсутствует или не читается.
- Активная Topic указана в индексе, но ее `Goal.md` отсутствует.
- Read-only checker сообщает blocking findings: покажи их в отчете, но не
  исправляй автоматически.
- Пользователь просит применить исправление: останови report workflow и перейди
  к отдельному подтвержденному lifecycle или maintenance шагу.

## Read-Only Boundary

`learn-report` не изменяет `topics/INDEX.md`, `Goal.md`, owner artifacts,
`Handoff.md`, Obsidian, Anki или любые внешние write targets. Он может только
читать файлы и запускать read-only проверку `tools/check_topic_workspace.py`.

## Out Of Scope

Вне области этого skill: Card Promotion, Knowledge Consolidation, Obsidian write,
Anki write, personal installation, plugin packaging, исправление Topic
Index, создание Topic Workspace, проведение учебного mini-cycle, новые slash
commands и новые Python-утилиты.
