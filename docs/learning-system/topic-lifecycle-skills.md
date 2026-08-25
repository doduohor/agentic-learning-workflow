# Скиллы жизненного цикла темы

Этот документ описывает первую версию Topic Lifecycle Skills для проекта. Реальные `SKILL.md` должны быть созданы в `.agents/skills/` отдельным этапом реализации.

## Общие правила

- Скиллы отвечают по-русски, если пользователь не просит иначе.
- Перед действием они читают `CONTEXT.md`, `docs/learning-system/lifecycle-command-interface.md`, `docs/learning-system/agent-common-instructions.md`, `docs/learning-system/session-handoff-workflow.md` и нужные owner artifacts.
- `Goal.md` остаётся источником истины для Topic State, Active Block, Block Status, Mastery Level, Completion Criteria и Next Actions.
- `topics/INDEX.md` используется для навигации и отчёта, но при расхождении с `Goal.md` скилл верит `Goal.md`.
- State-changing edits применяются только после preview или proposed changes и подтверждения пользователя.
- Supporting roles подключаются только при явной причине и соблюдают Agent Write Boundary.
- Card Promotion и Knowledge Consolidation не выполняются первой тройкой skills.

## `learn-start`

### Когда использовать

Когда пользователь хочет начать изучение новой Topic или просит завести новую учебную тему.

### Вход

Минимально нужны:

- сырой запрос пользователя;
- Learning Profile или возможность взять текущий профиль проекта;
- достаточно узкая Topic.

Если запрос слишком широкий, скилл сначала сужает Topic или предлагает Parent Topic и первую конкретную Topic.

### Порядок работы

1. Прочитать `CONTEXT.md`, `topics/INDEX.md`, `docs/learning-system/lifecycle-command-interface.md` и `docs/learning-system/templates/README.md`.
2. Сформулировать `Subject`, `Topic`, `Stable Slug`, путь `topics/<subject>/<stable-slug>/` и draft goal.
3. Показать preview:

   ```text
   Создать Topic Workspace?

   Learning Profile: ...
   Subject: ...
   Topic: ...
   Stable Slug: ...
   Path: topics/<subject>/<stable-slug>/
   Draft goal: ...
   ```

4. Дождаться подтверждения пользователя.
5. После подтверждения вызвать `tools/start_topic_intake.py` с явными аргументами.
6. Прочитать результат и findings.
7. Если создание прошло, задать первый диагностический вопрос.
8. Не переводить Topic из `intake` дальше без ответа пользователя и отдельного подтверждения изменений состояния.

### Границы записи

Скилл не копирует templates вручную. Запись выполняется через `tools/start_topic_intake.py`, который создаёт семь owner artifacts, обновляет `topics/INDEX.md`, запускает Lightweight Checker и откатывает изменения при error.

## `learn-continue`

### Когда использовать

Когда пользователь хочет продолжить существующую Topic, вернуться к paused Topic, выполнить следующий учебный шаг или продолжить Active Block.

### Выбор Topic

Если Topic Workspace указан явно, скилл использует его.

Если путь не указан:

- найти активные темы через `topics/INDEX.md`;
- сверить кандидатов с `Goal.md`;
- если активная тема одна, выбрать её;
- если активных тем несколько, показать короткий список и попросить выбрать;
- если активных тем нет, предложить `learn-start` или вывести `learn-report`.

Активными считаются Topic State: `intake`, `diagnosing`, `planned`, `learning`, `practicing`, `reviewing`, `paused`.

### Порядок работы

1. Прочитать `Goal.md`, затем owner artifacts, нужные для `Next Actions`.
2. Проверить `Handoff.md`, если Topic State равен `paused` или есть риск потери контекста.
3. Определить ближайшее безопасное действие из `Next Actions`.
4. Проверить долги: blocker Weaknesses, pending Source Checks, active/missed repetitions и blocking checker findings.
5. Если долг блокирует текущий шаг или gate, остановиться и предложить repair route.
6. Если `Next Actions` задаёт узкий шаг, выполнить его.
7. Иначе провести один мини-цикл Active Block:
   - короткая теория;
   - пример в контексте Learning Profile;
   - изменение примера пользователем;
   - намеренная поломка или разбор ошибки;
   - объяснение причины поломки;
   - feedback и следующий шаг.
8. Подключить supporting role только при явной причине:
   - `learning-support` для диагностики или курации Knowledge;
   - `learning-practice` для практической попытки;
   - `learning-source` для Source Check;
   - `learning-question-card` для вопросов и Card Candidates;
   - `learning-repetition` для Active Repetition.
9. В конце показать proposed changes: какие файлы, какие сущности, какие evidence links, какие gates затронуты.
10. Дождаться подтверждения пользователя перед записью.

### Границы записи

`learn-continue` не применяет скрытые изменения состояния. После учебной части он показывает пакет изменений, например:

- обновить `Goal.md`: Topic State, Active Block, Block Status, Mastery Level или Next Actions;
- добавить Practice Attempt в `Practice.md`;
- добавить curated Knowledge в `Knowledge.md`;
- добавить или обновить Weakness в `Weaknesses.md`;
- добавить Question или Card Candidate в `Questions.md`;
- добавить Source Record в `Sources.md`;
- добавить Active Repetition в `RepetitionLog.md`.

Пакет применяется только после подтверждения. Если изменение требует решения пользователя по gate, strong duplicate, `replace`, `merge`, Card Promotion или Knowledge Consolidation, скилл останавливается и не подменяет это решение.

## `learn-report`

### Когда использовать

Когда пользователь хочет увидеть, какие темы сейчас изучаются, где остановилась работа, что заблокировано и какой следующий шаг безопасен.

### Порядок работы

1. Прочитать `topics/INDEX.md`.
2. Найти активные Topic Workspaces.
3. Для каждой активной темы прочитать `Goal.md`.
4. Запустить read-only Lightweight Checker для активных тем.
5. При необходимости прочитать `Weaknesses.md`, `Sources.md` и `RepetitionLog.md`, чтобы показать долги.
6. Сформировать отчёт на русском.

### Формат отчёта

По умолчанию отчёт короткий, но рабочий:

```md
## Активные темы

### <Topic>

- Состояние: `<Topic State>`
- Рабочая папка: `topics/<subject>/<stable-slug>/`
- Активный блок: <Block или `-`>
- Следующий безопасный шаг: <Next Actions>
- Блокирующие слабые места: <W-* или `-`>
- Непроверенные источники: <SRC-* или `-`>
- Повторения: <active/missed или `-`>
- Проверка workspace: <кратко errors/warnings или `без блокирующих ошибок`>
```

Если строка `topics/INDEX.md` расходится с `Goal.md`, отчёт явно показывает предупреждение и предлагает обновить индекс отдельным подтверждённым действием.

## Будущие расширения

Отдельными skills или workflows позже можно добавить:

- Card Promotion;
- Knowledge Consolidation;
- полный audit report;
- maintenance skill для исправления индекса и ссылок;
- personal installation или plugin packaging.
