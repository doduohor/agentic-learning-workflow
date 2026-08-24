# Запись решения: передача контекста между Codex-сессиями

## Статус

Принято.

Scope correction 2026-08-24: handoff model универсальна для wayfinder tickets и Topic Workspaces по любым темам программирования. Topic Workspace Handoff не предполагает backend-тему, если это не задано текущим Learning Profile.

## Контекст

Учебная система проектируется как работа через Codex CLI, wayfinder tickets и будущие Topic Workspaces. Работа может прерываться между Codex-сессиями, переходить от одного ticket к другому или продолжаться другим Physical Agent.

Уже принято:

- есть один Learning Orchestrator, который владеет состоянием темы;
- роль не равна отдельному запущенному агенту;
- `Goal.md`, `Knowledge.md`, `Weaknesses.md` меняет только Learning Orchestrator;
- supporting roles не меняют состояние темы и маршрут напрямую;
- supporting role передает Agent Proposal с проверенным контекстом, предлагаемым изменением, доказательствами, рисками и точным фрагментом для вставки;
- Physical Agent может выполнять несколько ролей только через явный Role Mode;
- если Role Mode неясен, supporting agent работает только с предложениями;
- wayfinder map является индексом решений, а подробное содержание решения живет в decision record.

Нужно решить, как новая Codex-сессия надежно продолжает работу без потери состояния, нарушения single-writer state model и смешивания артефактов разных тем.

## Решение

Handoff в этой системе - устойчивый контракт продолжения между Codex-сессиями. Он отвечает на вопросы:

- где именно продолжать работу;
- что уже принято;
- что еще открыто;
- какие файлы являются источниками истины;
- какой следующий безопасный шаг;
- кто имеет право писать;
- какой scope запрещен.

Handoff не является стенограммой чата, полным журналом рассуждений или заменой рабочим артефактам. Чат может помочь новой сессии сориентироваться, но сведения, влияющие на состояние, маршрут, права записи или следующий шаг, должны быть записаны в устойчивых файлах.

## Два вида handoff

Используем два разных вида handoff.

### Wayfinder Handoff

Wayfinder Handoff передает проектное решение между wayfinder tickets.

Источники истины:

- `docs/wayfinder/00-map.md` - обзорная карта destination, принятых решений, текущего состояния, fog и out of scope;
- `docs/wayfinder/decisions/*.md` - подробное содержание закрытых решений;
- текущий decision draft, если сессия была прервана до закрытия ticket.

Для wayfinder не создается отдельный `HANDOFF.md`. Карта и decision records уже выполняют эту функцию. Отдельный файл добавил бы дублирование и риск расхождения.

Wayfinder Handoff должен показывать:

- текущий ticket по имени;
- destination из карты;
- закрытые решения через `Decisions So Far`;
- открытый fog через `Not Yet Specified`;
- запрещенный scope через `Out Of Scope`;
- следующий ticket или следующий безопасный шаг, если ticket еще не закрыт;
- какие решения являются prerequisites для текущей работы.

### Topic Workspace Handoff

Topic Workspace Handoff передает учебное состояние конкретной темы.

Источники истины:

- `Goal.md` - Topic State, Active Block, Learning Map, Completion Criteria, Active Weakness Summary и следующий шаг;
- `Weaknesses.md` - открытые Weaknesses и repair/retest;
- `Questions.md` - active Questions и Card Candidates;
- `Sources.md` - pending Source Checks и `Нужно проверить`;
- `RepetitionLog.md` - Active Repetitions, failures и missed repetitions;
- `Practice.md` и `Knowledge.md` - evidence и curated Knowledge, если следующий шаг зависит от них.

Для каждой Topic Workspace не нужен обязательный `Handoff.md`. Отдельный Topic Handoff Note создается только если есть риск потери контекста:

- сессия остановлена посреди незавершенного действия;
- следующий шаг зависит от нескольких артефактов сразу;
- работу продолжит другой Physical Agent;
- есть незавершенный Agent Proposal;
- есть высокий риск случайно продолжить не тот Role Mode или не тот Block.

Если `Handoff.md` создан, он не становится источником истины для состояния. Он указывает на источники истины и кратко связывает их в безопасный следующий шаг.

## Минимальный handoff-контекст новой Codex-сессии

Новая Codex-сессия должна получить или восстановить из файлов минимум:

- вид работы: wayfinder ticket или Topic Workspace;
- destination или Topic;
- текущий ticket или путь к Topic Workspace;
- актуальный указатель состояния: карта для wayfinder, `Goal.md` для Topic Workspace;
- последнее принятое решение или последний устойчиво записанный учебный шаг;
- следующий безопасный шаг;
- запрещенный scope;
- Role Mode текущего Physical Agent;
- Agent Write Boundary;
- незавершенные Agent Proposals, если они есть;
- список файлов, которые нужно прочитать перед записью.

Если этого минимума нет, сессия не должна менять состояние. Она сначала восстанавливает контекст из устойчивых файлов или уточняет противоречие у пользователя.

## Что нельзя передавать только через чат

Через чат нельзя передавать как единственный источник:

- Topic State;
- Active Block;
- Block Status и Mastery Level;
- открытые `major` и `blocker` Weaknesses;
- pending Source Checks;
- `Нужно проверить` по чувствительным утверждениям;
- Card Candidates и решения по Card Promotion;
- Active Repetitions, missed repetitions и repetition failures;
- закрытые wayfinder decisions;
- открытый fog;
- out of scope;
- права записи текущей роли;
- незавершенный Agent Proposal;
- следующий шаг, если он влияет на состояние темы или закрытие ticket.

Эти сведения могут быть кратко пересказаны в чате, но новая сессия обязана сверить их с файлами.

## Обязательное чтение перед продолжением

### Для wayfinder-сессии

Перед продолжением wayfinder ticket новая сессия читает:

1. `docs/wayfinder/00-map.md`.
2. `CONTEXT.md`.
3. Текущий decision draft, если он существует.
4. Закрытые decision records, от которых зависит текущий ticket.

Не обязательно перечитывать все decision records всегда. Но если ticket затрагивает роли, состояние темы, карточки, источники или Agent Files, сессия читает соответствующие решения `01-06`.

### Для Topic Workspace

Перед продолжением Topic Workspace новая сессия читает:

1. `Goal.md`.
2. `Handoff.md`, если он есть.
3. Все артефакты, на которые ссылаются `Goal.md` и `Handoff.md`.

Минимальный набор для обычного продолжения:

- `Goal.md`;
- `Weaknesses.md`, если есть открытые Weaknesses;
- `Questions.md`, если следующий шаг связан с Questions или Card Candidates;
- `Sources.md`, если есть pending Source Checks или `Нужно проверить`;
- `RepetitionLog.md`, если есть Active Repetitions, missed repetitions или review;
- `Practice.md` и `Knowledge.md`, если следующий шаг зависит от evidence или curated Knowledge.

Learning Orchestrator читает шире, если собирается менять состояние темы. Supporting role читает только нужный ролевой контекст и возвращает Agent Proposal, если действие выходит за ее Role Mode.

## Topic Handoff Note

Если создается `Handoff.md`, он должен быть коротким и структурированным. Он не ведет хронологический журнал и не копирует содержимое рабочих файлов.

Рекомендуемый формат:

```md
# Handoff - <Topic>

## Scope

- Topic Workspace: `<path>`
- Topic State: `<state>` через [Goal.md](Goal.md)
- Active Block: `<Entity Reference>` через [Goal.md](Goal.md)
- Role Mode for next session: `<role-mode>`
- Agent Write Boundary: `<коротко>`
- Forbidden Scope: `<что не делать>`

## Current State Pointers

- Open Weaknesses: <ссылки на Weaknesses.md или `-`>
- Pending Source Checks: <ссылки на Sources.md или `-`>
- Card Candidates: <ссылки на Questions.md или `-`>
- Active Repetitions: <ссылки на RepetitionLog.md или `-`>
- Required Evidence: <ссылки на Practice.md/Knowledge.md или `-`>

## Next Safe Action

<один конкретный следующий шаг>

## Open Risks

- <противоречие, риск потери контекста или `-`>

## Agent Proposals

- <ссылка или краткий указатель на незавершенный Agent Proposal или `-`>
```

Обновлять устойчивый `Handoff.md` может только Learning Orchestrator. Supporting role может вернуть только Agent Proposal с точным фрагментом для вставки в `Handoff.md`, если считает такой handoff нужным.

## Предотвращение конфликта записи

Новая сессия перед записью проверяет:

1. Какая работа продолжается: wayfinder ticket или Topic Workspace.
2. Какой Role Mode активен.
3. Какой Agent Write Boundary действует.
4. Какие файлы можно менять напрямую.
5. Не требует ли изменение нескольких файлов решения Learning Orchestrator.
6. Не является ли изменение state-changing edit.

Правила:

- `Goal.md`, `Knowledge.md`, `Weaknesses.md` меняет только Learning Orchestrator.
- Supporting role без явного Role Mode работает только через Agent Proposal.
- Supporting role с явным Role Mode пишет напрямую только в разрешенный файл и только append-only, если это явно поручено.
- Один запуск supporting agent пишет максимум в один разрешенный файл.
- Если продолжение требует нескольких файлов, supporting role возвращает Agent Proposal.
- Если сессия видит противоречие между чатом и устойчивыми файлами, она верит файлам и уточняет у пользователя, если продолжение зависит от выбора.

## Проверка, что ticket не старый и не закрытый

Перед продолжением wayfinder ticket новая сессия проверяет:

1. `docs/wayfinder/00-map.md`.
2. Что ticket не находится в `Decisions So Far`.
3. Что ticket не был вытеснен новым решением.
4. Что его вопрос не перенесен в `Out Of Scope`.
5. Что fog не изменился так, что ticket больше нельзя решать в прежней форме.

Если чат, карта и файлы противоречат друг другу, сессия не продолжает молча. Она формулирует противоречие и уточняет у пользователя.

## Physical Agent, Role Mode и Agent Proposal

Handoff должен указывать не только "кто продолжает", а границу продолжения:

- Physical Agent, если он известен или важен для продолжения;
- Role Mode следующей сессии;
- разрешенную границу записи;
- нужно ли продолжать как Learning Orchestrator или как supporting role;
- незавершенный Agent Proposal, если он есть;
- какие файлы были прочитаны агентом, который сделал proposal;
- какие доказательства и риски приложены к proposal.

Если Role Mode неясен, новая сессия действует как supporting role без прав записи состояния и возвращает proposal.

## Проверки перед закрытием и началом сессии

### Проверка перед закрытием Codex-сессии

Перед остановкой сессия проверяет:

- текущее решение или учебное состояние записано в устойчивых файлах;
- следующий безопасный шаг записан в карте, decision draft, `Goal.md` или условном `Handoff.md`;
- открытый fog или scope-риск не остался только в чате;
- pending Source Checks видимы в `Sources.md` или decision draft;
- Card Candidates не выданы за уже продвинутые карточки;
- открытые Weaknesses не скрыты;
- Active Repetitions и missed repetitions не потеряны;
- Role Mode и Agent Write Boundary не стали неявными;
- незавершенный Agent Proposal сохранен или явно отклонен.

### Проверка перед продолжением

Новая сессия перед работой проверяет:

- она читает актуальную карту или `Goal.md`;
- ticket не закрыт и не out of scope;
- Topic State и Active Block актуальны;
- следующий шаг не противоречит открытым Weaknesses;
- чувствительные утверждения с `Нужно проверить` не используются как подтвержденные;
- Role Mode указан;
- запись не нарушает Agent Write Boundary;
- работа относится к одному ticket или одной Topic Workspace.

## Обоснование

Разделение Wayfinder Handoff и Topic Workspace Handoff сохраняет разные источники истины. Wayfinder работает с проектными решениями и fog, а Topic Workspace - с учебным состоянием, evidence, Weaknesses, Questions, Sources и Repetitions.

Условный `Handoff.md` полезен как страховка при рискованном продолжении, но обязательный handoff-файл в каждой теме добавил бы лишний артефакт и стал бы дублировать `Goal.md`. Поэтому он остается файлом-указателем, а не новым владельцем состояния.

Правило обязательной проверки перед закрытием и продолжением защищает систему от трех ошибок:

- продолжить закрытый или устаревший ticket;
- потерять незавершенное учебное состояние между Codex-сессиями;
- дать supporting agent фактические права Learning Orchestrator через неясный Role Mode.

## Последствия

- Будущие Agent Files и общий файл инструкций должны ссылаться на это решение, когда описывают продолжение сессии.
- Будущие slash commands должны уметь явно указывать Role Mode и состояние продолжения.
- Prototype Topic Workspace должен проверить, достаточно ли `Goal.md` и условного `Handoff.md` для надежного продолжения.
- Финальная спецификация должна включить два вида handoff и проверки перед закрытием и продолжением.

## Вне области

Это решение не создает:

- реальные `.codex/agents/*.toml`;
- реальные slash commands;
- рабочие файлы темы;
- prototype Topic Workspace;
- запись в Obsidian или Anki;
- финальный `learning-system-spec.md`.

## Критерии завершения

Решение завершено, когда:

- определено, что такое handoff;
- разделены Wayfinder Handoff и Topic Workspace Handoff;
- описан минимальный handoff-контекст новой Codex-сессии;
- перечислены обязательные файлы для чтения;
- указано, что нельзя передавать только через чат;
- решено, где живет устойчивый handoff;
- решен статус условного `Handoff.md`;
- описана передача ticket, fog, out of scope и закрытых решений;
- описана передача Topic State, Active Block, Weaknesses, Source Checks, Card Candidates и Active Repetitions;
- описано предотвращение конфликта записи;
- описана проверка устаревших и закрытых tickets;
- учтены Physical Agent, Role Mode и Agent Proposal;
- описаны минимальные проверки перед закрытием и продолжением;
- карта wayfinder обновлена;
- новые устойчивые термины добавлены в `CONTEXT.md`, если они нужны.
