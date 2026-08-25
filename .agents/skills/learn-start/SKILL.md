---
name: learn-start
description: "Начать новую учебную Topic через preview, подтверждение пользователя и существующий intake workflow."
---

# learn-start

Используй этот skill, когда пользователь хочет начать изучение новой Topic,
завести новую учебную тему или превратить сырой учебный запрос в Topic
Workspace.

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

## Workflow

1. Проверь, достаточно ли узкая Topic. Если запрос слишком широкий, остановись:
   предложи Parent Topic и первую конкретную Topic либо задай один уточняющий
   вопрос. Не создавай workspace из расплывчатой цели.
2. Сформулируй:
   - Learning Profile;
   - Subject;
   - Topic;
   - Stable Slug;
   - path `topics/<subject>/<stable-slug>/`;
   - draft goal.
3. Покажи preview и дождись явного подтверждения пользователя:

   ```text
   Создать Topic Workspace?

   Learning Profile: ...
   Subject: ...
   Topic: ...
   Stable Slug: ...
   Path: topics/<subject>/<stable-slug>/
   Draft goal: ...
   ```

4. Только после подтверждения пользователя вызови существующую intake-утилиту:

   ```bash
   python3 tools/start_topic_intake.py \
     --subject "<subject>" \
     --topic "<topic>" \
     --stable-slug "<stable-slug>" \
     --learning-profile "<learning-profile>" \
     --draft-goal "<draft-goal>"
   ```

5. Прочитай вывод `tools/start_topic_intake.py`. Если intake не создан, передай
   пользователю причину и остановись.
6. Если intake создан, прочитай созданный `Goal.md` и findings Lightweight
   Checker из вывода.
7. Задай первый диагностический вопрос. Topic State должен остаться `intake`,
   пока пользователь не ответит и отдельно не подтвердит следующий переход.

## Stop Conditions

- Неясная, слишком широкая или смешанная Topic.
- Конфликт Stable Slug или path с существующим `topics/INDEX.md`.
- Пользователь не подтвердил preview.
- `tools/start_topic_intake.py` вернул ошибку или Lightweight Checker нашел
  blocking finding.
- Следующий шаг требует перехода Topic State из `intake` без ответа пользователя
  и отдельного подтверждения.

## Write Boundary

`learn-start` не копирует templates вручную и не редактирует `topics/INDEX.md`
напрямую. Запись выполняет только `tools/start_topic_intake.py`: она создает
семь owner artifacts, обновляет Topic Index, запускает read-only checker и
откатывает изменения при error.

## Out Of Scope

Вне области этого skill: Card Promotion, Knowledge Consolidation, Obsidian write,
Anki write, personal installation, plugin packaging, новые slash
commands, новые Python-утилиты, создание реальной учебной сессии и перевод
Topic дальше `intake` без отдельного подтвержденного lifecycle-шагa.
