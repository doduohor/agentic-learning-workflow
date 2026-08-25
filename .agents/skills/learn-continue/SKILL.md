---
name: learn-continue
description: "Продолжить существующую учебную Topic от ближайшего безопасного Next Actions."
---

# learn-continue

Используй этот skill, когда пользователь хочет продолжить существующую Topic,
вернуться к paused Topic, выполнить следующий учебный шаг или пройти один
ограниченный цикл Active Block.

Отвечай по-русски, если пользователь не просит иначе. Сначала прочитай:

- `CONTEXT.md`
- `docs/wayfinder/00-map.md`
- `topics/INDEX.md`
- `docs/learning-system/topic-lifecycle-skills.md`
- `docs/learning-system/lifecycle-command-interface.md`
- `docs/learning-system/agent-common-instructions.md`
- `docs/learning-system/session-handoff-workflow.md`
- `docs/learning-system/templates/README.md`
- `docs/wayfinder/decisions/13-design-topic-lifecycle-skills.md`

## Topic Selection

Если пользователь указал Topic Workspace, используй его и проверь, что там есть
`Goal.md`.

Если workspace не указан:

1. Прочитай `topics/INDEX.md`.
2. Найди active Topics со state `intake`, `diagnosing`, `planned`, `learning`,
   `practicing`, `reviewing` или `paused`.
3. Для каждого кандидата прочитай `Goal.md` и верь `Goal.md`, если индекс с ним
   расходится.
4. Если активная Topic одна, выбери ее.
5. Если активных Topic несколько, покажи короткий список и попроси пользователя
   выбрать.
6. Если активных Topic нет, предложи `learn-start` или `learn-report`.

## Workflow

1. Прочитай `Goal.md` как источник истины для Topic State, Active Block, Block
   Status, Mastery Level, Completion Criteria и Next Actions.
2. Затем прочитай owner artifacts, которые нужны для ближайшего Next Actions:
   `Knowledge.md`, `Practice.md`, `Questions.md`, `Weaknesses.md`,
   `RepetitionLog.md`, `Sources.md`.
3. Если Topic State равен `paused` или есть риск потери контекста, проверь
   `Handoff.md`, если он существует. При конфликте доверяй owner artifacts.
4. Определи ближайшее безопасное действие из Next Actions.
5. Запусти read-only Lightweight Checker для выбранной Topic Workspace:

   ```bash
   python3 tools/check_topic_workspace.py topics/INDEX.md topics/<subject>/<stable-slug>
   ```

6. До учебной работы явно покажи долги:
   - blocker Weaknesses;
   - pending Source Checks;
   - active/missed repetitions;
   - blocking findings от read-only Lightweight Checker.
7. Если долг блокирует текущий шаг или gate, остановись и предложи маршрут
   исправления.
8. Если Next Actions задает узкий шаг, выполни именно его.
9. Иначе проведи один ограниченный мини-цикл Active Block:
   - короткая теория;
   - пример в контексте Learning Profile;
   - изменение примера пользователем;
   - намеренная поломка или разбор ошибки;
   - объяснение причины поломки;
   - feedback и следующий безопасный шаг.
10. Подключай supporting role только при явной причине: диагностика, практика,
   Source Check, вопросы, Card Candidates или repetition. Supporting role без
   явной append-only boundary возвращает Agent Proposal.
11. Перед любой записью покажи proposed changes: затронутые файлы, сущности,
    evidence links, gates, риски и ожидаемый новый Next Actions.
12. Дождись подтверждение пользователя. Только после этого Learning Orchestrator
    может применить state-changing edits в разрешенных owner artifacts.

## Stop Conditions

- Не выбран Topic Workspace.
- `Goal.md` отсутствует или не дает однозначного Next Actions.
- Несколько active Topics и пользователь еще не выбрал одну.
- Есть blocker Weaknesses, pending Source Checks, active/missed repetitions или
  checker finding, который блокирует текущий gate.
- Proposed changes не показаны или подтверждение пользователя не получено.
- Нужно решение по duplicate check, replace, merge, Card Promotion или Knowledge
  Consolidation.

## Write Boundary

`learn-continue` не делает скрытые state-changing edits. Он сначала проводит
учебную работу или узкий Next Actions, затем предлагает пакет изменений.
Пакет может затрагивать только owner artifacts темы:

- `Goal.md` для Topic State, Active Block, Block Status, Mastery Level и Next
  Actions;
- `Knowledge.md` для curated Knowledge;
- `Practice.md` для Practice Attempt;
- `Questions.md` для Question или Card Candidate;
- `Weaknesses.md` для evidence-backed Weakness;
- `Sources.md` для Source Record;
- `RepetitionLog.md` для Active Repetition.

Запись возможна только после подтверждения пользователя и с учетом
single-writer state model.

## Out Of Scope

Вне области этого skill: Card Promotion, Knowledge Consolidation, Obsidian write,
Anki write, personal installation, plugin packaging, новые slash
commands, новые lifecycle states, новые owner artifacts, автоматическое
завершение Topic и применение внешних write targets.
