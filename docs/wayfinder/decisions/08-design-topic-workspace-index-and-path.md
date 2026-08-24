# Запись решения: путь и индекс рабочих папок тем

## Статус

Принято.

## Контекст

После prototype одной Topic Workspace нужно закрепить постоянное место, где физически живут рабочие папки тем, и способ, которым человек или агент находит нужную тему.

Уже принято:

- Topic Workspace состоит из `Goal.md`, `Knowledge.md`, `Practice.md`, `Questions.md`, `Weaknesses.md`, `RepetitionLog.md` и `Sources.md`;
- `Goal.md` владеет Topic State, Active Block, Block Status и Mastery Level;
- wayfinder map является индексом проектных решений, а не индексом учебных тем;
- система универсальна для programming learning, а конкретная область задается через Learning Profile;
- prototype создал тему `retry без идемпотентности` в `topics/rabbitmq/retry-without-idempotency/`.

Этот ticket не проектирует lightweight checker, не вводит YAML/JSON machine-readable schema и не меняет шаблоны Topic Workspace.

## Решение

Topic Workspaces живут в корневом каталоге `topics/` по правилу:

```text
topics/<subject>/<stable-slug>/
```

Где:

- `<subject>` - короткий ASCII slug основного Subject в нижнем регистре;
- `<stable-slug>` - короткий ASCII slug темы внутри выбранного Subject;
- полный Stable Slug темы хранится в `Goal.md` и может быть глобально уникальным, например `rabbitmq-retry-without-idempotency`;
- путь является физическим расположением, а не единственным идентификатором темы.

Для навигации создается human-first Topic Index:

```text
topics/INDEX.md
```

`topics/INDEX.md` является источником навигации: он помогает человеку и агенту найти Topic Workspace, увидеть Learning Profile, Subject, Topic, Stable Slug, Topic State, Parent Topic, связанные Subject и путь к `Goal.md`.

`topics/INDEX.md` не является владельцем учебного состояния. Если индекс и `Goal.md` расходятся, источником истины является `Goal.md`.

## Минимальные поля Topic Index

Минимальная строка индекса содержит:

| Поле | Смысл |
|---|---|
| Learning Profile | Профиль, для которого тема сейчас релевантна. |
| Subject | Primary Subject, который определяет папку первого уровня. |
| Topic | Человекочитаемое название темы. |
| Stable Slug | Устойчивый slug из `Goal.md`. |
| Topic State | Состояние, прочитанное из `Goal.md`; не источник истины. |
| Topic Workspace | Относительный путь к папке темы. |
| Goal | Ссылка на `Goal.md`. |
| Parent Topic | Родительская Topic или `-`. |
| Related Subjects | Дополнительные Subject для multi-subject темы или `-`. |

Индекс может иметь дополнительные человекочитаемые разделы, например `Topic Tree`, если появится несколько родительских и дочерних тем. Эти разделы не должны дублировать внутреннее состояние блоков.

## Parent Topic

Parent Topic используется, когда исходная Topic слишком широкая и ее нужно разложить на дочерние Topics.

Правила:

- Parent Topic является Topic, а не Subject;
- Parent Topic показывается в `topics/INDEX.md`;
- дочерняя Topic остается отдельной Topic Workspace со своим `Goal.md`;
- физический путь дочерней Topic не обязан вкладываться в папку родителя;
- если нужен обзор дерева, его можно добавить в `topics/INDEX.md` как human-first раздел.

## Multi-subject темы

Если тема относится к нескольким Subject, у нее все равно одна физическая Topic Workspace.

Правила:

- выбирается primary Subject, и именно он входит в путь `topics/<subject>/<stable-slug>/`;
- остальные Subject указываются в `Related Subjects` в `topics/INDEX.md`;
- дублировать одну тему в нескольких Subject-папках нельзя;
- если primary Subject позже выбран неудачно, миграция пути должна быть явным implementation ticket с обновлением ссылок.

## Отношение Topic Index к Goal.md

`topics/INDEX.md` отвечает за навигацию и обзор.

`Goal.md` остается источником истины для:

- Topic State;
- Active Block;
- Block Status;
- Mastery Level;
- Learning Map;
- Completion Criteria;
- Active Weakness Summary;
- Next Actions.

Индекс может показывать Topic State для сканирования, но это кэш из `Goal.md`, а не отдельное состояние. Агент, который собирается менять состояние темы или продолжать Topic Workspace, обязан читать `Goal.md`.

## Completed и archived темы

`topics/INDEX.md` индексирует все существующие Topic Workspaces, включая active, completed и archived.

Причина: завершенные темы остаются частью Working Knowledge Base и должны находиться для повторения, консолидации, duplicate checks и handoff. Состояние темы показывает, нужна ли активная работа.

## Prototype Topic Workspace

Prototype-папка остается на месте:

```text
topics/rabbitmq/retry-without-idempotency/
```

Она совпадает с принятой path convention:

```text
topics/<subject>/<stable-slug>/
```

Здесь `<subject>` равен `rabbitmq`, а короткий slug папки темы равен `retry-without-idempotency`. Полный Stable Slug остается в `Goal.md`: `rabbitmq-retry-without-idempotency`.

Миграция prototype-папки не нужна.

## Требования к будущему lightweight checker

Будущий lightweight checker должен получить от этого решения только требования, не готовый дизайн реализации.

Минимально он должен уметь проверять:

- каждая строка `topics/INDEX.md` с Topic Workspace ссылается на существующий `Goal.md`;
- путь соответствует `topics/<subject>/<stable-slug>/`;
- `Subject`, `Topic`, `Stable Slug`, `Topic State` и `Topic Workspace` в индексе не противоречат шапке `Goal.md`;
- `Stable Slug` не конфликтует с другими Topic Workspaces;
- `Parent Topic`, если указан, ссылается на существующую Topic;
- `Related Subjects` не создают дубликат физической Topic Workspace;
- `Goal.md` остается владельцем Topic State, Active Block, Block Status и Mastery Level;
- checker работает с human-first Markdown и не требует YAML/JSON machine-readable schema.

Полный алгоритм, формат отчета и границы автоматического исправления остаются отдельным future ticket.

## Обоснование

`topics/<subject>/<stable-slug>/` дает простой путь, который хорошо читается в файловой системе и не требует отдельной базы данных. Primary Subject в пути помогает быстро сузить поиск, а Topic Index покрывает случаи, где тема связана с несколькими Subject.

Корневой `topics/INDEX.md` лучше отдельного `TopicIndex.md` или индекса в `docs/`, потому что навигационный артефакт находится рядом с тем, что он индексирует. Индекс внутри Learning Profile был бы слишком узким: одна Topic может быть полезна нескольким профилям или пережить смену текущего Learning Profile.

Разделение ролей между `topics/INDEX.md` и `Goal.md` сохраняет single-writer state model. Индекс помогает найти тему, но не становится вторым владельцем состояния.

## Последствия

Будущие сценарии `start/intake`, `resume`, `review`, `repeat`, `complete`, Duplicate Check и Topic Workspace Handoff должны сначала находить тему через `topics/INDEX.md`, а затем читать `Goal.md` перед любым state-changing edit.

Новые Topic Workspaces должны добавляться в `topics/INDEX.md` в том же ticket, где создается рабочая папка темы, если создание темы входит в scope этого ticket.

Если Topic переезжает, migration ticket должен обновить:

- путь в файловой системе;
- `Topic Workspace` в `Goal.md`;
- строку в `topics/INDEX.md`;
- все Markdown-ссылки, которые указывают на старый путь извне Topic Workspace.

## Вне области

Это решение не делает:

- lightweight checker;
- YAML/JSON machine-readable schema;
- `.codex/agents/*.toml`;
- slash commands;
- Obsidian/Anki automation;
- новые учебные темы;
- расширение prototype в полноценную учебную тему;
- финальный `learning-system-spec.md`.

## Следующие тикеты

1. `Design Source Verification Workflow`
2. `Design Session Notes And Practice Artifact Archive`
3. `Design Lightweight Checker For Entity References And IDs`
4. `Design Obsidian And Anki Write Automation`
5. `Assemble Learning System Specification`

## Критерии завершения

Это решение считается закрытым, когда:

- принят path convention `topics/<subject>/<stable-slug>/`;
- создан `topics/INDEX.md` как human-first Topic Index;
- prototype Topic Workspace внесен в индекс;
- карта wayfinder обновлена;
- `Goal.md` остается источником истины для Topic State, Active Block, Block Status и Mastery Level;
- future checker получил только требования, без реализации и без machine-readable schema.
