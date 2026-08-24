# Запись решения: дизайн будущих файлов Codex-агентов

## Статус

Принято.

Scope correction 2026-08-24: дизайн Agent Files универсален для programming learning. Source Check и Agent Files не привязаны только к backend production; конкретные риски и источники зависят от темы и Learning Profile.

## Контекст

Предыдущие решения закрепили доменную модель, шаблоны рабочих артефактов темы, роли Codex-агентов, сценарии жизненного цикла темы и правила Obsidian/Anki. Теперь нужно спроектировать, как будущие `.codex/agents/*.toml` выразят эти роли без создания самих файлов.

Уже принято:

- есть один учебный оркестратор (Learning Orchestrator), который владеет состоянием темы;
- роль не равна отдельному запущенному агенту;
- в первой реализации роли можно объединять ради экономии токенов;
- `Goal.md`, `Knowledge.md`, `Weaknesses.md` меняет только учебный оркестратор;
- поддерживающие роли либо возвращают предложение оркестратору, либо делают узкую append-only запись в разрешенный файл;
- Anki-карточки не создаются напрямую из сырого материала;
- версионные, application-sensitive, production, security, protocol и tooling claims требуют Source Check.

Факт по текущему Codex Manual, проверенный 2026-08-24: project-scoped custom agents задаются отдельными TOML-файлами под `.codex/agents/`; каждый файл должен содержать `name`, `description`, `developer_instructions`; настройки вроде `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers` и `skills.config` опциональны. Документация также отмечает, что формат custom agent files может развиваться, поэтому это решение фиксирует содержание и границы будущих файлов, а не окончательную TOML-схему. Источник: Codex Manual, раздел `Subagents`, `https://learn.chatgpt.com/docs/agent-configuration/subagents.md`.

## Решение

В первой реализации проектируем шесть будущих Agent Files:

```text
.codex/agents/learning-orchestrator.toml
.codex/agents/learning-support.toml
.codex/agents/learning-practice.toml
.codex/agents/learning-question-card.toml
.codex/agents/learning-source.toml
.codex/agents/learning-repetition.toml
```

`learning-support.toml` объединяет диагностическую роль (Diagnostic Agent) и роль куратора знаний (Knowledge Curator Agent). Объединение допустимо, потому что обе роли обычно работают read-only, читают широкий контекст и возвращают предложения оркестратору.

Остальные роли остаются отдельными физическими агентами, потому что у них есть разные append-only границы:

- Practice Agent может дописывать новые Practice Attempts в `Practice.md`;
- Question/Card Agent может дописывать draft Questions и Card Candidates в `Questions.md`;
- Source Agent может дописывать Source Checks в `Sources.md`;
- Repetition Agent может дописывать записи в `RepetitionLog.md`.

## Learning Orchestrator как единственный автор состояния

`learning-orchestrator.toml` должен явно сказать, что агент:

- владеет Topic State, Active Block, Block Status, Mastery Level, Completion Criteria и согласованностью файлов;
- применяет принятые предложения supporting roles;
- единственный меняет `Goal.md`, `Knowledge.md`, `Weaknesses.md`;
- может применять согласованные изменения в `Practice.md`, `Questions.md`, `Sources.md`, `RepetitionLog.md`;
- не закрывает блок или тему без Completion Evidence;
- не продвигает Card Candidate без Duplicate Check, Card Trace и решения о Card Promotion.

Каждый Agent File для supporting agent должен иметь короткий ограничитель:

```text
You are not the Learning Orchestrator.
Do not change Topic State, Active Block, Block Status, Mastery Level,
Goal.md, Knowledge.md, or Weaknesses.md.
Return an Agent Proposal unless your role has an explicit append-only write
boundary for this run.
```

В русской версии будущих инструкций этот смысл должен быть сохранен без ослабления.

## Общие инструкции для всех агентских файлов

Будущие `.toml` не должны копировать большие одинаковые правила. Общие правила нужно вынести в отдельный документ, например:

```text
docs/learning-system/agent-common-instructions.md
```

Каждый будущий Agent File должен ссылаться на этот общий документ и требовать чтения нужного контекста перед действием.

Общий документ должен содержать:

- русский язык ответа по умолчанию;
- канонические термины из `CONTEXT.md`;
- single-writer state model;
- правила Agent Proposal;
- правила evidence и traceability;
- правила `Нужно проверить`;
- когда нужен Source Check;
- когда нужен Duplicate Check;
- запрет Card Promotion без понимания, ценности, Duplicate Check, Card Trace и решения оркестратора;
- запрет сырых Anki-карточек;
- правило предотвращения конфликта записи: один supporting agent, один разрешенный файл, новая запись, новый ID, без переписывания старых записей.

В самих `.toml` должны остаться только:

- `name`;
- `description`;
- `developer_instructions`;
- при необходимости `model`, `model_reasoning_effort`, `sandbox_mode` и другие поддерживаемые Codex-настройки;
- роль, Role Mode, чтение, запись, формат результата и ограничения.

## Контекстные ссылки из будущих Agent Files

Все будущие Agent Files должны ссылаться на:

- `CONTEXT.md` как канонический глоссарий;
- `docs/wayfinder/00-map.md` как карту проектных решений;
- `docs/wayfinder/decisions/03-design-codex-agent-roles.md` как источник ролевых границ;
- `docs/wayfinder/decisions/06-design-codex-agent-files.md` как источник физической упаковки ролей в Agent Files;
- общий документ инструкций для учебных агентов, когда он будет создан.

Оркестратор перед изменением состояния читает все решения `01-06`.

Поддерживающие агенты читают общий минимум:

- `CONTEXT.md`;
- `docs/wayfinder/00-map.md`;
- `docs/wayfinder/decisions/03-design-codex-agent-roles.md`;
- `docs/wayfinder/decisions/06-design-codex-agent-files.md`.

Профильные решения читаются по роли:

- `learning-practice`: решения `02`, `03`, `04`, `06`;
- `learning-question-card`: решения `02`, `03`, `04`, `05`, `06`;
- `learning-source`: решения `02`, `03`, `04`, `05`, `06`;
- `learning-repetition`: решения `02`, `03`, `04`, `06`;
- `learning-support`: решения `01`, `02`, `03`, `04`, `06`, а при карточках или консолидации также `05`.

## Ролевые границы будущих файлов

| Будущий Agent File | Role Mode | Читает | Может менять напрямую | Когда возвращает только предложение |
|---|---|---|---|---|
| `learning-orchestrator.toml` | `orchestrator` | Все файлы темы, `CONTEXT.md`, карта, решения `01-06`, нужный Obsidian-контекст | `Goal.md`, `Knowledge.md`, `Weaknesses.md`; также согласованные изменения в `Practice.md`, `Questions.md`, `Sources.md`, `RepetitionLog.md` | Когда нужно решение пользователя по сильному дублю, спорному merge/replace, изменению привычной Anki-карточки или смене границ темы |
| `learning-support.toml` | `diagnostic` | `Goal.md`, `Knowledge.md`, `Practice.md`, `Questions.md`, `Weaknesses.md`, `Sources.md`, релевантный Obsidian-контекст | Ничего | Всегда: маршрут, предпосылки, слабые места, вопросы, первый блок |
| `learning-support.toml` | `knowledge-curator` | `Goal.md`, `Knowledge.md`, `Practice.md`, `Questions.md`, `Weaknesses.md`, `Sources.md` | Ничего | Всегда: фрагменты для `Knowledge.md`, исправления заблуждений, пометки для утверждений, требующих Source Check |
| `learning-practice.toml` | `practice` | `Goal.md`, `Knowledge.md`, `Practice.md`, `Weaknesses.md`, `Questions.md`, `Sources.md` | Новые Practice Attempts и первичная обратная связь в `Practice.md`, только по явному заданию оркестратора | Если нужно изменить маршрут, уровень освоения, Weakness, Knowledge, Questions или Goal |
| `learning-question-card.toml` | `question-card` | `Goal.md`, `Knowledge.md`, `Practice.md`, `Questions.md`, `Weaknesses.md`, `Sources.md`, Obsidian и Anki при доступности | Draft Questions и Card Candidates в `Questions.md` | Если нужно активировать, отклонить, архивировать, продвинуть карточку, заменить или объединить существующую карточку |
| `learning-source.toml` | `source` | `Sources.md`, `Knowledge.md`, `Questions.md`, `Practice.md`, `Goal.md`, авторитетные внешние источники | Новые Source Checks в `Sources.md` | Если нужно менять Knowledge, Goal, Questions, Weaknesses или учебный маршрут |
| `learning-repetition.toml` | `repetition` | `Goal.md`, `Questions.md`, `Practice.md`, `Weaknesses.md`, `RepetitionLog.md` | Новые Active Repetitions и результаты повторений в `RepetitionLog.md` | Если повторение выявило Weakness, требует снижения Mastery Level, нового вопроса или изменения маршрута |

## Role mode для физического агента

Один Physical Agent может выполнять несколько ролей, но только через явный Role Mode в текущем запуске.

Правило:

- если Role Mode указан, агент получает права только этого Role Mode;
- если Role Mode смешанный, неясный или отсутствует, агент работает только с предложениями;
- объединенный физический агент не получает автоматическое объединение прав всех ролей;
- один запуск supporting agent не должен писать больше чем в один файл;
- если работа требует изменений в нескольких файлах, агент возвращает Agent Proposal оркестратору.

Это правило сохраняет экономию токенов от объединения ролей, но не размывает single-writer state model.

## Evidence, traceability и проверки

Каждый будущий Agent File должен требовать, чтобы значимая запись или предложение содержали:

- прочитанный контекст;
- связанный Block ID;
- ссылки на доказательства: Practice Attempt, Question, Weakness, Repetition, Source Check или Knowledge section;
- риск неполноты или ошибки;
- точный Markdown-фрагмент для вставки, если предлагается изменение;
- `Нужно проверить`, если Source Check еще не выполнен для чувствительного утверждения.

Source Agent отвечает за Source Check, но любой агент обязан распознать утверждение, требующее проверки источника, и не подавать его как проверенное без записи в `Sources.md`.

Question/Card Agent отвечает за Duplicate Check и предложение Card Promotion, но не создает Anki-карточку напрямую и не принимает окончательное решение при сильном дубле, `replace`, спорном `merge` или сомнительной ценности.

Practice Agent и Repetition Agent могут дать доказательство для Weakness, но Weakness открывает, закрывает или меняет только Learning Orchestrator.

## Предотвращение конфликтов записи

Будущие Agent Files должны закрепить следующие правила:

1. `Goal.md`, `Knowledge.md`, `Weaknesses.md` меняет только Learning Orchestrator.
2. Supporting agent пишет напрямую только при явном поручении оркестратора.
3. Прямая запись supporting agent всегда append-only.
4. Supporting agent использует новый ID и не переписывает существующие записи.
5. Один запуск supporting agent пишет максимум в один разрешенный файл.
6. Сквозные изменения между файлами выполняет только Learning Orchestrator.
7. Если два агента хотят писать в один файл, прямую запись выполняет только один; остальные возвращают Agent Proposal.
8. Оркестратор проверяет ссылки между файлами перед применением предложения.

## Минимальные проверки перед созданием реальных `.toml`

Перед будущим созданием файлов `.codex/agents/*.toml` нужно выполнить минимум:

1. Проверить актуальный Codex Manual на текущую схему custom agent files.
2. Убедиться, что каждый будущий файл имеет `name`, `description`, `developer_instructions`.
3. Убедиться, что каждый supporting agent явно содержит границу чтения/записи.
4. Убедиться, что ни один supporting agent не может менять `Goal.md`, `Knowledge.md`, `Weaknesses.md`.
5. Проверить существование всех ссылок на `CONTEXT.md`, `docs/wayfinder/00-map.md`, decision records и общий файл инструкций.
6. Проверить, что общий файл инструкций не дублирует полностью decision records, а дает рабочие правила и context pointers.
7. Провести сухой сценарий `learn-block`: какой агент что читает, куда пишет и где возвращает Agent Proposal.
8. Провести сухой сценарий Card Promotion: утверждение, требующее Source Check, Duplicate Check, сильный дубль, решение пользователя.
9. Проверить, что объединенный `learning-support` при неясном Role Mode остается read-only.
10. Проверить, что будущие `.toml` не создают новые права записи относительно решений `03` и `06`.

## Обоснование

Шесть файлов дают практичный первый набор: оркестратор отделен от исполнителей, а read-only роли диагностики и курации знаний объединены без потери границ. Это снижает стоимость в токенах и число запусков, но оставляет отдельными роли, у которых есть собственные append-only файлы.

Общий файл инструкций уменьшает расхождение между Agent Files. Короткий ограничитель в каждом Agent File для supporting agent остается намеренным повторением: запрет на изменение состояния должен быть виден даже при частичном чтении контекста.

Role Mode нужен, потому что Physical Agent может выполнять несколько ролей. Без явного Role Mode объединение ролей превращалось бы в скрытое объединение прав записи.

## Последствия

- Будущий ticket по созданию `.codex/agents/*.toml` должен начинаться с проверки текущего Codex Manual.
- Будущий общий файл инструкций для агентов должен быть отдельным источником рабочих правил, а не копией всех decision records.
- Будущие slash commands должны указывать Role Mode при запуске объединенного или supporting agent.
- Prototype Topic Workspace должен проверить эти границы на реальной теме, но не менять их без отдельного решения.

## Вне области

Это решение не создает:

- реальные `.codex/agents/*.toml`;
- общий файл `docs/learning-system/agent-common-instructions.md`;
- slash commands;
- рабочие файлы темы;
- prototype Topic Workspace;
- запись в Obsidian или Anki;
- финальный `learning-system-spec.md`.

## Критерии завершения

Решение завершено, когда:

- перечислены будущие Agent Files;
- решено, какие роли отдельные, а какие объединены;
- Learning Orchestrator выражен как единственный автор состояния;
- общие и ролевые инструкции разделены;
- для каждой роли указаны чтение, прямая запись и случаи Agent Proposal;
- описаны ссылки на `CONTEXT.md`, карту и decision records;
- правила evidence, traceability, Source Check, Duplicate Check и Card Promotion встроены в Agent Files;
- описано предотвращение конфликтов записи;
- описано выполнение нескольких ролей одним Physical Agent через Role Mode;
- перечислены минимальные проверки перед созданием реальных `.toml`.
