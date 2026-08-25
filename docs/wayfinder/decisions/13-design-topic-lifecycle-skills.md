# Запись решения: скиллы жизненного цикла темы

## Статус

Принято.

## Контекст

Проект уже закрепил Topic Workspace, Topic State, роли агентов, lifecycle scenarios, Lightweight Checker, Source Check, Duplicate Check и write automation. Оставалось решить, как пользователь будет запускать повторяемую учебную работу через Codex skills, не превращая каждый запрос в новый ad hoc prompt.

Факт по Codex Manual, проверенный 2026-08-25: skill является папкой с обязательным `SKILL.md`, где есть `name` и `description`; Codex может загружать локальные скиллы репозитория из `.agents/skills`; skill подходит для повторяемого workflow, а plugin нужен позже для распространяемого пакета или связки с connectors/MCP.

## Решение

Первая версия вводит три Topic Lifecycle Skills репозитория под `.agents/skills/`:

```text
learn-start
learn-continue
learn-report
```

Это источник истины для проекта. Личная установка за пределами репозитория не входит в первую версию.

Скиллы остаются пользовательским интерфейсом к уже принятым lifecycle scenarios. Они не создают новую модель владения состоянием и не обходят single-writer state model: state-changing edits применяет Learning Orchestrator, а supporting roles работают через Agent Proposal или явную append-only boundary.

`learn-start` запускает новую тему:

- показывает preview перед записью: Learning Profile, Subject, Topic, Stable Slug, путь Topic Workspace и draft goal;
- после подтверждения вызывает существующую утилиту `tools/start_topic_intake.py`;
- создаёт Topic Workspace в состоянии `intake`;
- после создания задаёт первый диагностический вопрос, но не переводит тему дальше без ответа пользователя и нового подтверждения.

`learn-continue` продолжает существующую тему:

- если Topic Workspace не указан, выбирает единственную активную тему; при неоднозначности спрашивает пользователя;
- читает `Goal.md` как источник истины и идёт от ближайшего безопасного `Next Actions`;
- по умолчанию выполняет один мини-цикл Active Block: теория, пример, изменение примера, поломка или разбор ошибки, обратная связь;
- если `Next Actions` уже задаёт более узкий шаг, выполняет его вместо полного мини-цикла;
- показывает долги: blocker Weaknesses, pending Source Checks и active/missed repetitions;
- останавливается, если долг блокирует текущий шаг или gate;
- подключает supporting roles только при явной причине: диагностика, практика, Source Check, вопросы, карточки или повторение;
- в конце показывает пакет proposed changes и просит подтверждение перед записью.

`learn-report` показывает рабочий отчёт:

- читает `topics/INDEX.md`, затем сверяет активные темы с их `Goal.md`;
- для активных тем запускает read-only Lightweight Checker;
- отвечает на русском;
- по умолчанию показывает Topic State, Active Block, Next Actions, blocker Weaknesses, pending Source Checks, active/missed repetitions и краткие warnings/errors по индексу или Topic Workspace.

Card Promotion и Knowledge Consolidation не входят в первую тройку скиллов. Они остаются отдельными будущими skills или workflows, потому что требуют Duplicate Check, Source Check, dry-run preview, user approval и внешних write targets.

## Рассмотренные варианты

Был рассмотрен минимальный набор из трёх skills, более подробный набор из 5-6 lifecycle skills и один крупный orchestration skill. Выбран набор из трёх, потому что он совпадает с естественными пользовательскими намерениями: начать, продолжить, посмотреть состояние. Более подробный набор лучше отражает внутренние gates, но тяжелее для пользователя. Один крупный skill удобнее на входе, но хуже делает скрытые решения видимыми.

По месту хранения выбрана `.agents/skills/`, потому что эти skills привязаны к доменной модели и утилитам этого репозитория. Личный каталог skills оставлен за пределами первой версии, чтобы не потерять воспроизводимость проекта.

## Последствия

- Будущая реализация должна создать `.agents/skills/learn-start/SKILL.md`, `.agents/skills/learn-continue/SKILL.md` и `.agents/skills/learn-report/SKILL.md`.
- `learn-start` должен использовать `tools/start_topic_intake.py`, а не вручную копировать templates и править `topics/INDEX.md`.
- `learn-report` должен быть read-only и не менять `Goal.md`, `topics/INDEX.md` или owner artifacts.
- `learn-continue` должен явно отделять учебную работу от применения изменений: сначала proposed changes, затем подтверждение пользователя.
- Для будущих skills продвижения карточек и консолидации знания потребуется отдельное решение или план реализации.

## Вне области

Это решение не создаёт реальные `SKILL.md`, не реализует slash commands, не пишет в Obsidian или Anki, не меняет Topic Workspace и не добавляет новые Python-утилиты.
