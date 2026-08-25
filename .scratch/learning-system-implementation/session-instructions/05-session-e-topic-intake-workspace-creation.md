# Сессия E: создание Topic Workspace через intake

## Назначение запуска

Отдельный агент выполняет тикет `06-topic-intake-workspace-creation.md`:
реализует первый рабочий сценарий `start/intake`, создающий минимальную Topic
Workspace из утвержденных шаблонов.

Рабочая директория: `/home/doduohor/learning/agentic-learning-workflow`.

## Предпосылки

Нужны завершенные A, B и D: templates, общий контракт, checker и lifecycle
interface. Прочитай их наличие и контракты до первого изменения. При отсутствии
любого из результатов сообщи блокер, не создавай собственные шаблоны или
упрощенный checker.

## Обязательные skills

1. Используй `$implement`, `$tdd`, `verification-before-completion` и
   `$code-review`.
2. Используй `domain-modeling` только если появится действительно новый
   устойчивый термин для `CONTEXT.md`.

## Обязательное чтение до изменений

1. `AGENTS.md`, `CONTEXT.md`, `docs/wayfinder/00-map.md` и
   `docs/learning-system-spec.md`.
2. Тикет 06.
3. `docs/learning-system/templates/`.
4. `docs/learning-system/lifecycle-command-interface.md`.
5. Реализация и contract Lightweight Checker из сессии B.
6. Decisions 01, 02, 04, 08 и 11 в `docs/wayfinder/decisions/`.
7. `topics/INDEX.md` и prototype только как пример структуры.

## Результат сессии

Реализуй узкий интерактивный или аргументный сценарий `start/intake` в
согласованном с checker инструментальном слое. Он собирает Subject, Topic,
Stable Slug, путь `topics/<subject>/<stable-slug>/`, Learning Profile и
черновую цель; создает семь артефактов из templates; обновляет `topics/INDEX.md`
только как навигацию; устанавливает разрешенный стартовый Topic State в
`Goal.md`; затем запускает checker и показывает его отчет.

Сценарий обязан валидировать конфликт пути/Stable Slug до записи и не оставлять
частично созданную Workspace при ошибке. Он не создает Anki cards, Obsidian
notes, Agent Files или наполненную учебную тему сверх intake-структуры.

## Границы и проверка

Разрешены implementation files/tests/docs для intake, тикет 06 и `CONTEXT.md`
только для нового термина. Для тестов используй временные каталоги и fixtures;
не создавай постоянную новую тему в `topics/`.

Покрой тестами валидный intake, конфликт пути, недопустимый slug, отказ checker
и отсутствие частичного состояния. Запускай отдельные тесты регулярно, затем
весь набор. Проверь, что `topics/INDEX.md` не владеет Topic State. После
`$code-review` повтори tests, выполни `git diff --check` и закоммить.

В финальной передаче укажи интерфейс intake, тестовые результаты, отсутствие
новой постоянной Topic Workspace, результат ревью, коммит и закрытые criteria.
Следующая зависимая сессия — F.
