# Интерфейс учебных lifecycle-команд

Этот документ описывает будущие человекочитаемые команды для Topic Workspace.
Это не реализация slash-команд: Learning Orchestrator применяет изменения после
проверок, а supporting agents работают через Agent Proposal либо в явно заданной
append-only Agent Write Boundary.

## Общие правила

- Перед изменением состояния Orchestrator читает `Goal.md` как источник истины
  для Topic State, Active Block, Block Status и Mastery Level; `topics/INDEX.md`
  служит только навигацией.
- Изменения состояния, `Goal.md`, `Knowledge.md` и `Weaknesses.md` применяет
  только Learning Orchestrator. Поддерживающая роль без явного Role Mode
  возвращает Agent Proposal.
- Entity References и evidence остаются в owner artifacts. `sessions/` может
  хранить сырой контекст, но не владеет учебным состоянием.
- Sensitive claim проходит Source Check в `Sources.md`. `needs-check` и
  `Нужно проверить` допустимы для раннего обучения, но блокируют применимый
  gate: `production-ready`, `completed`, Card Promotion или Knowledge
  Consolidation.
- Card Candidate не становится карточкой автоматически: нужны понимание,
  ценность, Card Trace, Duplicate Check в Obsidian и Anki, решение
  `skip`/`replace`/`merge`/`add`, а также решение Orchestrator. Внешняя запись
  требует отдельного dry-run и user approval.
- Lightweight Checker остаётся read-only guardrail. Его error с gate impact
  должен быть устранён либо учтён как явный блокер до соответствующего gate.

## `start/intake`

- **Вход:** запрос пользователя и достаточно конкретная Topic; слишком широкая
  тема сначала сужается либо получает Parent Topic.
- **Читается:** `CONTEXT.md`, `docs/wayfinder/00-map.md`, `topics/INDEX.md` и,
  когда это нужно для маршрута, существующий Obsidian-контекст.
- **Действия Orchestrator:** определяет Subject, Stable Slug и путь
  `topics/<subject>/<stable-slug>/`; создаёт Topic Workspace по шаблонам,
  вносит навигационную строку в `topics/INDEX.md`, устанавливает `intake` в
  `Goal.md` и записывает черновой следующий безопасный шаг.
- **Gate:** семь owner artifacts существуют, slug и путь уникальны, а индекс
  ссылается на правильный `Goal.md`.
- **Stop condition:** при неясной или слишком широкой цели остановиться на
  уточнении; переход возможен только `intake -> diagnosing`.
- **Изменяемые owner artifacts:** `Goal.md`; остальные файлы создаются из
  шаблонов, `topics/INDEX.md` получает только навигационную запись.

## `diagnose`

- **Вход:** Topic в `intake` или безопасно возобновлённый диагностический шаг.
- **Читается:** `Goal.md`, `Knowledge.md`, `Practice.md`, `Questions.md`,
  `Weaknesses.md`, `Sources.md` и релевантный Obsidian-контекст.
- **Действия Orchestrator:** переводит Topic в `diagnosing`, принимает
  диагностические вопросы/попытки, уточняет предпосылки и принимает только
  evidence-backed Weaknesses.
- **Gate:** перед `planned` есть понятная цель, проверенные либо явно рискованные
  предпосылки, 3–7 обязательных/необязательных Blocks, первый Active Block и
  хотя бы одно диагностическое evidence.
- **Stop condition:** не переходить к плану при непонятной цели, невыясненных
  ключевых предпосылках или отсутствии первого безопасного блока.
- **Изменяемые owner artifacts:** `Goal.md`, `Weaknesses.md`, `Questions.md`;
  supporting agents предлагают, но не меняют состояние.

## `plan`

- **Вход:** достаточная диагностика и Topic в `diagnosing`.
- **Читается:** `Goal.md`, `Weaknesses.md`, `Questions.md`, при наличии
  `Practice.md` и `Sources.md`.
- **Действия Orchestrator:** формирует Learning Map, Completion Criteria,
  Active Weakness Summary, первый Active Block и конкретный next safe action;
  переводит Topic в `planned`.
- **Gate:** каждый required Block имеет смысл и маршрут, критерии имеют
  фиксируемое evidence, а blocker Weakness включена в маршрут, а не скрыта.
- **Stop condition:** не начинать `learning`, если не выбран Active Block или
  completion требует несуществующего evidence.
- **Изменяемые owner artifacts:** `Goal.md`, при необходимости
  `Weaknesses.md` и `Questions.md`.

## `learn-block`

- **Вход:** Topic в `planned` или `learning`, выбран Active Block.
- **Читается:** `Goal.md`, `Knowledge.md`, `Practice.md`, `Weaknesses.md`,
  `Questions.md`, `Sources.md`.
- **Действия Orchestrator:** ведёт цикл «теория → пример → изменение примера →
  намеренная поломка/разбор реальной ошибки → объяснение → feedback»; принимает
  evidence и выбирает следующий маршрут. Practice Agent может дописать одну
  новую попытку только в явной границе.
- **Gate:** есть объяснение без подсказки либо зафиксированная причина неудачи,
  изменённый пример, поломка/ошибка с объяснением и evidence для каждой новой
  Weakness.
- **Stop condition:** не повышать Block Status/Mastery и не закрывать Block,
  если практика была только прочитана, поломка не разобрана или есть открытая
  blocker Weakness.
- **Изменяемые owner artifacts:** `Goal.md`, `Knowledge.md`, `Practice.md`,
  `Questions.md`, `Weaknesses.md`, `Sources.md` по их владельческим границам.

## `practice`

- **Вход:** Active Block требует применения либо ремонта понимания.
- **Читается:** `Goal.md`, `Knowledge.md`, `Practice.md`, `Questions.md`,
  `Weaknesses.md`, `Sources.md`.
- **Действия Orchestrator:** назначает проверяемую попытку; принимает её
  результат, feedback и follow-ups. Практика может быть кодом, SQL, схемой,
  логами, проектным выбором или объяснением компромисса.
- **Gate:** Attempt имеет новый `PA-*`, Linked Block, проверенный Result,
  отделённый feedback и ссылки на открытые по evidence Weaknesses.
- **Stop condition:** `unchecked`, `failed` или `rework-needed` не служат
  единственным основанием для повышения Mastery; sensitive claim не становится
  подтверждённым без Source Check.
- **Изменяемые owner artifacts:** `Practice.md`, а согласованные изменения
  маршрута — в `Goal.md`, `Weaknesses.md`, `Knowledge.md`, `Questions.md`.

## `review`

- **Вход:** достаточно practice/evidence для Active Block или темы.
- **Читается:** сначала `topics/INDEX.md`, затем `Goal.md` и все семь owner
  artifacts.
- **Действия Orchestrator:** проверяет recall без подсказки, application,
  transfer, разбор ошибки и Weaknesses; фиксирует результат вопросов и при
  необходимости создаёт/обновляет Active Repetition.
- **Gate:** Mastery подтверждён подходящим evidence; нет скрытых провалов;
  закрываемый Block не имеет open blocker Weakness. Для `production-ready`
  запускается Checker и проверяются sensitive Source Records.
- **Stop condition:** не переводить Block или Topic вперёд без evidence;
  не скрывать failed/partial результат вместо Weakness/repair route.
- **Изменяемые owner artifacts:** `Goal.md`, `Weaknesses.md`, `Questions.md`,
  `RepetitionLog.md` и при необходимости curated `Knowledge.md`.

## `repeat`

- **Вход:** достигнут `application`, исправляется major/blocker Weakness,
  близится завершение Topic или есть запланированное повторение.
- **Читается:** сначала `topics/INDEX.md`, затем `Goal.md`, `Questions.md`,
  `Practice.md`, `Weaknesses.md`, `RepetitionLog.md`.
- **Действия Orchestrator:** планирует либо принимает active repetition с
  действием `recall`, `explain`, `apply`, `debug` или `transfer`; Repetition
  Agent может дописать одну запись в своей границе.
- **Gate:** target существует, результат и Completed At согласованы; failed или
  partial с учебной проблемой имеют Failure Analysis и Weakness либо явный
  warning для Orchestrator.
- **Stop condition:** перечитывание не засчитывается как repetition; failed или
  missed repetition не игнорируется и может заблокировать `completed`.
- **Изменяемые owner artifacts:** `RepetitionLog.md`, а изменения маршрута и
  Weaknesses принимает Orchestrator в `Goal.md`/`Weaknesses.md`.

## `pause`

- **Вход:** любое незавершённое состояние Topic.
- **Читается:** `Goal.md` и связанные owner artifacts настолько, насколько это
  нужно, чтобы не потерять незавершённую попытку, вопрос, Source Check или
  repetition.
- **Действия Orchestrator:** сохраняет предыдущее рабочее состояние, next safe
  action и ссылки на открытые обязательства; переводит Topic в `paused`.
- **Gate:** следующее действие выполнимо и однозначно; open Weaknesses, pending
  Source Checks, Card Candidates, Active и missed Repetitions остаются в своих
  owner artifacts и видимы из `Goal.md` или handoff.
- **Stop condition:** не считать незавершённый Question/Attempt закрытым и не
  создавать `Handoff.md` без риска потери контекста.
- **Изменяемые owner artifacts:** `Goal.md`; при риске потери контекста —
  условный `Handoff.md` как снимок, не источник истины.

## `resume`

- **Вход:** Topic в `paused` и сохранённый next safe action.
- **Читается:** сначала `topics/INDEX.md`, затем `Goal.md`, `Practice.md`,
  `Questions.md`, `Weaknesses.md`, `RepetitionLog.md`, а при ссылках/гейтах —
  `Knowledge.md` и `Sources.md`.
- **Действия Orchestrator:** сверяет snapshot с owner artifacts, восстанавливает
  предыдущее рабочее состояние либо выбирает ближайший безопасный маршрут;
  отмечает missed repetitions, когда они обнаружены.
- **Gate:** Role Mode и Agent Write Boundary известны для исполняющего агента;
  blocker Weaknesses и pending Source Checks не потеряны; Checker запускается
  перед сложной cross-file правкой или handoff с риском связности.
- **Stop condition:** при конфликте snapshot и owner file доверять owner file;
  при неясной роли supporting agent вернуть Agent Proposal.
- **Изменяемые owner artifacts:** `Goal.md`, при необходимости
  `RepetitionLog.md`; остальные изменения проходят по обычным границам.

## `complete`

- **Вход:** Topic в `reviewing`; все required Blocks готовы к финальной
  проверке.
- **Читается:** все семь owner artifacts, `topics/INDEX.md` и, если есть,
  `sessions/` со связанными evidence.
- **Действия Orchestrator:** запускает Lightweight Checker, проверяет
  Completion Criteria и переводит Topic в `completed`; при необходимости
  фиксирует будущие repetitions и готовность Knowledge к отдельной
  консолидации.
- **Gate:** каждый required Block имеет `stable`; применимые production blocks
  имеют `production-ready` или `stable`; практическое evidence, объяснение
  поломки и active repetition существуют; индекс согласован с `Goal.md`.
- **Stop condition:** `complete` блокируется при open blocker Weakness,
  missing Completion Evidence, failed/missed repetition без требуемого
  Weakness и blocking `needs-check`/`rejected` Source Record. Команда не
  выполняет Card Promotion или Knowledge Consolidation вместо их отдельных
  gates.
- **Изменяемые owner artifacts:** `Goal.md`, при необходимости `Questions.md`,
  `RepetitionLog.md`, `Knowledge.md` и навигационная строка `topics/INDEX.md`.

## Разрешённые переходы

`intake → diagnosing → planned → learning → practicing → reviewing → completed`.
Возвраты из review/practice/learning допустимы для ремонта evidence. Любое
незавершённое состояние может перейти в `paused`; `resume` возвращает только в
`diagnosing`, `planned`, `learning`, `practicing` или `reviewing`.
