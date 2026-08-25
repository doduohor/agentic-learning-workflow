# Wayfinder Map: Codex Learning System

Last updated: 2026-08-25

## Destination

Спроектировать рабочую систему обучения темам программирования через Codex CLI и multi-agent workflow.

Система должна покрывать полный цикл:

```text
запрос пользователя -> уточнение темы и диагностика -> Goal.md -> цикл блока
-> Knowledge.md -> практика -> Questions.md/Card Candidates -> RepetitionLog.md
-> консолидация в long-term knowledge base
```

Цель проекта - не просто хранить конспекты, а доводить тему до проверяемого умения: объяснить, применить, изменить пример, разобрать поломку, увидеть реальные ограничения применения и выдержать уточняющие вопросы.

## Notes

- Канонический глоссарий: [CONTEXT.md](../../CONTEXT.md).
- Decision records хранятся в [`decisions/`](./decisions/).
- Ядро системы универсально для программирования: конкретная область, стек или проект задаются через Learning Profile, а не через границы самой системы.
- Текущий Learning Profile пользователя: Junior+/Middle Kotlin Backend для ЦУП РТ / АИС МИДИО.
- Пример текущего профильного стека: Kotlin, Ktor, Git, Postgres/Exposed, Docker/Docker Compose, RabbitMQ, Prometheus, Grafana, MongoDB, ClickHouse, DDD, Transactional Outbox, system design, CI/CD, reliability, security, observability.
- Проектируемая система использует human-first Markdown: файлы должны быть удобны человеку, но достаточно стабильны для Codex CLI и агентов.
- Принята single-writer state model: Learning Orchestrator владеет изменениями состояния, supporting agents анализируют и предлагают изменения в ограниченных границах.
- Anki-карточки не создаются напрямую из сырого материала. Сначала нужны понимание, ценность, traceability, проверка дублей в Obsidian/Anki и решение о promotion.
- Версионно-зависимые, application-sensitive, production, security, tooling и protocol claims требуют Source Check. Непроверенное помечается как `Нужно проверить`.
- Один Wayfinder ticket должен закрывать одно проектное решение. Реальные рабочие файлы темы создаются только в prototype/implementation ticket.

## Decisions So Far

1. [Define Domain Model](./decisions/01-define-domain-model.md) - принято.

   Закреплена доменная модель:

   ```text
   Learning Project -> Subject -> Topic -> Block -> Session
   ```

   Приняты основные сущности, lifecycle темы, модель освоения блока, критерии Learned Block/Completed Topic, single-writer state model, разделение Working Knowledge Base и Long-Term Knowledge Base, Source Check и `Нужно проверить`.

2. [Design Learning Artifact Templates](./decisions/02-design-learning-artifact-templates.md) - принято.

   Закреплен дизайн семи Markdown-артефактов Topic Workspace:

   ```text
   Goal.md
   Knowledge.md
   Practice.md
   Questions.md
   Weaknesses.md
   RepetitionLog.md
   Sources.md
   ```

   Приняты форматы ID, entity references, allowed values, edit boundaries, структура индексов и записей. Ticket намеренно не создает реальные файлы темы, `.codex/agents/*.toml`, slash commands, Obsidian/Anki automation или machine-readable schema.

3. [Design Codex Agent Roles](./decisions/03-design-codex-agent-roles.md) - принято.

   Закреплены роли Codex-агентов для учебной системы: один Learning Orchestrator, обязательные поддерживающие роли, будущие необязательные роли, права записи по артефактам, передача предложений оркестратору, предотвращение конфликтов, правила доказательств и прослеживаемости, ответственность за Source Check, Duplicate Check и Card Promotion.

   Отдельно принято, что основной учебный цикл блока ведет Learning Orchestrator, а Practice Agent исполняет активную практическую часть: теория, пример, изменение примера, намеренная поломка и объяснение поломки.

4. [Design Topic Lifecycle Commands](./decisions/04-design-topic-lifecycle-commands.md) - принято.

   Закреплены сценарии жизненного цикла темы: `start/intake`, `diagnose`, `plan`, `learn-block`, `practice`, `review`, `repeat`, `pause`, `resume`, `complete`.

   Приняты правила превращения пользовательского запроса в Intake Topic, достаточной диагностики перед `planned`, заполнения `Goal.md`, выбора Active Block, прохода Block Learning Cycle, фиксации Practice Attempts, Questions, Card Candidates, Active Repetition, Weakness routing, проверки источников, evidence и traceability.

5. [Design Obsidian/Anki Integration](./decisions/05-design-obsidian-anki-integration.md) - принято.

   Закреплены правила проверки похожего материала в Obsidian, проверки Anki перед продвижением карточки, режима недоступного Anki, решений `skip`, `replace`, `merge`, `add`, следа карточки и переноса очищенного знания в долговременную базу.

6. [Design Codex Agent Files](./decisions/06-design-codex-agent-files.md) - принято.

   Закреплен дизайн будущих `.codex/agents/*.toml`: шесть Agent Files первой реализации, объединение Diagnostic Agent и Knowledge Curator Agent в `learning-support`, Learning Orchestrator как единственный автор состояния, Role Mode для Physical Agent, общие инструкции, ролевые границы чтения/записи, правила evidence, traceability, Source Check, Duplicate Check, Card Promotion и минимальные проверки перед созданием реальных TOML-файлов.

7. [Design Codex Session Handoff](./decisions/07-design-codex-session-handoff.md) - принято.

   Закреплены два вида handoff: Wayfinder Handoff через карту и decision records, и Topic Workspace Handoff через `Goal.md`, связанные артефакты темы и условный `Handoff.md` только при риске потери контекста. Приняты минимальный handoff-контекст, обязательное чтение на входе, проверки перед закрытием и продолжением, проверка устаревших tickets, учет Physical Agent, Role Mode, Agent Proposal и Agent Write Boundary.

8. [Design Topic Workspace Index And Path Convention](./decisions/08-design-topic-workspace-index-and-path.md) - принято.

   Закреплены постоянный path convention `topics/<subject>/<stable-slug>/`, корневой human-first Topic Index `topics/INDEX.md`, правила для Parent Topic, multi-subject тем и отношение индекса к `Goal.md` как источнику истины для Topic State, Active Block, Block Status и Mastery Level.

9. [Design Source Verification Workflow](./decisions/09-design-source-verification-workflow.md) - принято.

   Закреплено, какие claims требуют Source Check, что `Sources.md` владеет Source Records и результатами проверки, что означает `Нужно проверить`, какие действия блокирует `needs-check`, как Source Agent и Learning Orchestrator делят ответственность, и какие инварианты передать будущему lightweight checker.

10. [Design Session Notes And Practice Artifact Archive](./decisions/10-design-session-notes-and-practice-artifact-archive.md) - принято.

   Закреплен optional per-topic каталог `sessions/` для длинных Session Notes и Practice Artifacts, path convention `sessions/YYYY-MM-DD-<short-slug>.md`, правила ссылок из `Practice.md` и других артефактов, права записи ролей, append-only/edit правила, retention/pruning и отношение archive files к Source Check и `Нужно проверить`.

11. [Design Lightweight Checker For Entity References And IDs](./decisions/11-design-lightweight-checker-for-entity-references-and-ids.md) - принято.

   Закреплен read-only lightweight checker для human-first Markdown: он проверяет Entity References, ID formats, missing targets, stale references, ownership-инварианты, Draft Orphan rules и gate-blocking inconsistencies без введения YAML/JSON machine-readable schema.

12. [Design Obsidian And Anki Write Automation](./decisions/12-design-obsidian-and-anki-write-automation.md) - принято.

   Закреплен Orchestrator-controlled write workflow для фактической записи в Obsidian и Anki после Card Promotion или Knowledge Consolidation: обязательный dry-run preview, user approval, independent write targets, unavailable mode, idempotency/re-run safety, trace outcome в `Questions.md` и `Knowledge.md`, pre-write checks и failure modes без введения YAML/JSON machine-readable schema.

13. [Design Topic Lifecycle Skills](./decisions/13-design-topic-lifecycle-skills.md) - принято.

   Закреплена первая версия Topic Lifecycle Skills репозитория под `.agents/skills/`: `learn-start`, `learn-continue`, `learn-report`. Приняты preview перед `learn-start`, продолжение от ближайшего безопасного `Next Actions`, пакет proposed changes перед записью, read-only русский `learn-report` и опора на существующие утилиты проекта.

## Current State

Выполнено:

- итоговая спецификация учебной системы собрана: [`docs/learning-system-spec.md`](../learning-system-spec.md);
- доменная модель принята и отражена в `CONTEXT.md`;
- mapping рабочих артефактов принят;
- шаблоны всех семи файлов Topic Workspace спроектированы;
- правила владения состоянием и границы редактирования зафиксированы;
- базовые статусы, ID и traceability между файлами определены;
- роли Codex-агентов и их права записи спроектированы;
- основной учебный цикл блока закреплен за Learning Orchestrator;
- сценарии жизненного цикла темы и переходы Topic State спроектированы;
- проверки перед переходами состояния определены;
- Obsidian/Anki integration спроектирована на уровне правил и сценариев;
- правила Duplicate Check и Card Promotion уточнены;
- перенос очищенного знания в Long-Term Knowledge Base спроектирован;
- будущие `.codex/agents/*.toml` спроектированы на уровне набора файлов, ролевых границ, общего контекста, Role Mode и проверок перед созданием;
- handoff между Codex-сессиями спроектирован для wayfinder tickets и Topic Workspaces;
- постоянный путь Topic Workspaces и `topics/INDEX.md` спроектированы;
- Source Verification Workflow спроектирован;
- архив Session Notes и Practice Artifacts спроектирован;
- lightweight checker для Entity References и ID спроектирован;
- write automation для Obsidian и Anki спроектирована на уровне workflow, gates, preview, approval, trace и failure modes;
- первая версия Topic Lifecycle Skills спроектирована: `learn-start`, `learn-continue`, `learn-report`;
- prototype одной Topic Workspace создан: [`topics/rabbitmq/retry-without-idempotency/`](../../topics/rabbitmq/retry-without-idempotency/).

## Prototype Findings

Prototype ticket `Prototype One Topic Workspace` создал одну минимальную Topic Workspace для темы `retry без идемпотентности`.

Что оказалось удобным:

- семь артефактов хорошо разделяют контроль темы, знание, практику, вопросы, повторения, слабые места и источники;
- entity references делают связи между `Goal.md`, `Knowledge.md`, `Practice.md`, `Questions.md`, `RepetitionLog.md` и `Sources.md` читаемыми без машинной схемы;
- `Goal.md` естественно работает как единственный владелец Topic State, Active Block, Block Status и Mastery Level;
- `Sources.md` с `needs-check` позволяет записать чувствительный claim без ложного подтверждения.

Что оказалось тяжелым:

- короткий prototype быстро требует много ссылок, и ручная проверка ID становится заметной работой;
- пустой `Weaknesses.md` нужен даже без evidence-backed Weakness, иначе теряется место для риска, но запись Weakness без evidence нарушила бы собственные правила;
- Card Candidate полезен уже в `Questions.md`, но без Obsidian/Anki duplicate checks его легко ошибочно прочитать как готовую карточку.

Поля, которые выглядят лишними или спорными на минимальном prototype:

- повторение `Last Updated` во всех семи файлах может стать механическим шумом без автоматизации;
- `Session Archive Links` в маленькой теме выглядит рано, хотя как место для будущего роста остается понятным;
- таблицы индексов удобны для сканирования, но в малой теме создают больше разметки, чем содержания.

Вопросы, закрытые следующими tickets:

- постоянный путь Topic Workspaces и `topics/INDEX.md` закрыты в [Design Topic Workspace Index And Path Convention](./decisions/08-design-topic-workspace-index-and-path.md);
- lightweight проверка cross-file Entity References и ID закрыта в [Design Lightweight Checker For Entity References And IDs](./decisions/11-design-lightweight-checker-for-entity-references-and-ids.md).

Оставшиеся вопросы:

- как лучше фиксировать prototype findings: в карте, отдельном artifact или в issue tracker;

## Grilling Outcomes

После `grill-with-docs` по prototype принято:

- считать семь файлов Topic Workspace пригодной основой с малыми правками; выявленное трение выносить в следующие tickets, а не переписывать шаблоны сразу;
- использовать `topics/<subject>/<stable-slug>/` как provisional convention для следующих prototype/implementation работ до решения про Topic Index; ticket `Design Topic Workspace Index And Path Convention` позже закрепил этот путь как permanent decision;
- хранить pre-evidence риск внутри `Weaknesses.md` как `Risk Index Without Weakness Records` без конкретного `W-*`, пока нет evidence-backed Weakness;
- завести отдельный будущий ticket на lightweight проверку entity references и ID без введения YAML/JSON machine-readable schema.

## Not Yet Specified

Пусто: итоговая спецификация собрана в [`docs/learning-system-spec.md`](../learning-system-spec.md).

## Out Of Scope

- Автоматическое создание Anki-карточек без duplicate checks.
- Реальная реализация Obsidian/Anki write automation до отдельного implementation ticket.
- Calendar/task-manager integration на первом проходе.
- UI/dashboard поверх файловой системы.
- YAML/JSON machine-readable schema до доказанной необходимости.
- Реальная реализация учебной темы внутри decision tickets, кроме отдельного prototype ticket.
