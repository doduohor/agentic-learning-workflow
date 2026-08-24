# Общий контракт учебных агентов

Этот документ — рабочий контракт для будущих ролей. Используйте термины из
[CONTEXT.md](../../CONTEXT.md); полный жизненный цикл и инварианты читайте в
[спецификации](../learning-system-spec.md), а формат записей — в
[шаблонах](templates/README.md).

## Режим работы и автор состояния

Отвечайте по-русски, если пользователь не просит иначе. Learning Orchestrator —
единственный автор state-changing edits: он применяет изменения Topic State,
Active Block, Block Status, Mastery Level и Completion Criteria, а также
единственный напрямую меняет `Goal.md`, `Knowledge.md` и `Weaknesses.md`.

Supporting agent возвращает **Agent Proposal**, если в задании явно не дана узкая
append-only Agent Write Boundary. Даже при такой границе он не выполняет сквозные
изменения и не меняет три owner files выше. Перед записью проверьте границу,
owner file и отсутствие конфликта с другим агентом.

В append-only границе supporting agent дописывает только одну новую запись или
секцию с новым ID в один явно разрешённый файл; существующие записи не
переписываются. Если один файл нужен двум писателям, прямую запись выполняет
один назначенный агент, а остальные возвращают Agent Proposal.

## Agent Proposal

Передайте оркестратору: цель, прочитанный контекст, findings, предлагаемые
изменения с Entity References, evidence, риски/gates и следующий шаг. Предложение
не меняет состояние само по себе.

## Evidence и traceability

Для записей, которые уже прошли соответствующий этап lifecycle, обязательна
проверяемая связь с причиной и результатом:

- Practice Attempt: Block, prompt, artifacts, result, feedback и evidence links;
- Question: prompt/rubric, answer или attempt, Weakness и Source links;
- Weakness: evidence, severity, Repair Action, retest и Resolution Evidence;
- Active Repetition: target, action, result, failure analysis и Weakness link;
- Source Check: claim, authoritative source, result, used-in links и next check;
- Card Candidate: понимание и ценность, Card Trace, Duplicate Check и Promotion Decision;
- Knowledge Consolidation: curated Knowledge, linked evidence, Duplicate Check,
  Source Check и write outcome.

Используйте стабильные ID и Entity References. Не заменяйте evidence пересказом
и не делайте archive file владельцем состояния.

## Claims и Source Check

Для version-sensitive, application-sensitive, production, security,
protocol-semantics и tooling-behavior claims сначала смотрите
[workflow Source Check](../wayfinder/decisions/09-design-source-verification-workflow.md).
Если подтверждения нет, пишите `needs-check` в `Sources.md` и `Нужно проверить`
в связанных артефактах. Такой claim не используется для production-ready,
Completion Evidence, снятия blocker Weakness, Card Promotion или Knowledge
Consolidation.

## Карточки и внешние записи

Card Promotion допускается лишь когда материал понят и ценен, есть Card Trace,
Source Check gate пройден и выполнены Obsidian/Anki Duplicate Check с решением
`skip`, `replace`, `merge` или `add`. Promotion Decision принимает только
Learning Orchestrator; supporting agent может лишь предложить его. Подробный порядок — в
[workflow интеграции](../wayfinder/decisions/12-design-obsidian-and-anki-write-automation.md).

Только Orchestrator-controlled workflow может писать в Obsidian или Anki: он
сначала показывает dry-run preview, получает user approval, проверяет доступность
target и trace/idempotency. Supporting agents могут готовить текст и proposal,
но не пишут во внешние системы напрямую.

## Условные ссылки

- Перед lifecycle-командой читайте
  [интерфейс учебных команд](lifecycle-command-interface.md): gates и next safe
  action не заменяют owner artifacts.
- При паузе, возобновлении или смене Codex-сессии читайте
  [workflow handoff](session-handoff-workflow.md): Role Mode и Agent Write
  Boundary не заменяют owner artifacts.
- Для работы с длинными заметками и артефактами сессии читайте
  [правила архива](../wayfinder/decisions/10-design-session-notes-and-practice-artifact-archive.md):
  `sessions/` append-only по умолчанию и не заменяет owner files.
- При создании или изменении будущих ролей читайте
  [дизайн Agent Files](../wayfinder/decisions/06-design-codex-agent-files.md) и
  [роли агентов](../wayfinder/decisions/03-design-codex-agent-roles.md).
- Lightweight Checker остаётся read-only validator: его finding проверяется и
  учитывается как gate, но он не меняет Markdown и не вводит YAML/JSON schema.
