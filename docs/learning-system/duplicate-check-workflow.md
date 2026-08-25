# Workflow проверки дублей в Obsidian и Anki

Этот workflow собирает read-only evidence до Card Promotion или Knowledge
Consolidation. Он не создаёт карточки, не меняет Obsidian vault и не записывает
summary самостоятельно: итоговый trace применяет только Learning Orchestrator.

## Когда и что проверять

- Перед Card Promotion проверяются релевантный Obsidian-контекст и Anki, но Anki
  запускается только перед планируемым `add`, `replace` или `merge` карточки.
- Перед Knowledge Consolidation проверяется только Obsidian; доступ к Anki для
  этого действия не нужен.
- Сначала проверяются очевидная заметка или папка темы, `maps`, `40_project` и
  профильные заметки. Если первый круг не дал совпадений, инструмент расширяет
  поиск сам. Если он дал partial match, Learning Orchestrator решает, нужен ли
  полный vault, и запускает команду с `--full-vault`.

## Запуск

```sh
python3 tools/duplicate_check.py \
  --target card \
  --query "retry without idempotency" \
  --anki-required
```

Команда читает Markdown из vault `/mnt/c/Users/Sergey/Documents/GPT/Work`. Для
Anki она разрешает только read-only AnkiConnect actions `findNotes` и
`notesInfo`. Режим `--anki-required` допустим только для `--target card`.

## Duplicate Check summary

Результат содержит target, запрос, похожие объекты с силой совпадения,
availability, outcome, рекомендованное действие и next step. Силы совпадения:

- `strong` — совпадает одна единица знания по явной семантической оценке
  Learning Orchestrator, а не только по текстовому сходству. Утилита возвращает
  текстовые candidates как `partial` и не принимает это решение сама;
- `partial` — есть пересечение, которое требует человеческой оценки.

Learning Orchestrator переносит summary:

- в `Questions.md`, в Card Candidate и Card Trace — для Card Promotion;
- в `Knowledge.md`, в Knowledge Consolidation Trace — для Knowledge
  Consolidation.

Supporting agent возвращает summary как Agent Proposal. Он не меняет owner
artifacts и не принимает Promotion/Consolidation decision.

## Действия и решение

Для карточки допустимы `skip`, `replace`, `merge`, `add`; для Knowledge —
`skip`, `add`, `append`, `merge`, `replace-section`. Инструмент предлагает
`add`, когда совпадений нет, и `merge` при partial match. `skip` при strong
duplicate, `replace`, `append` и `replace-section` требуют контекстного решения
Orchestrator, а не автоматического выбора по поиску.

Strong duplicate, `replace`, спорный `merge` и сомнительная ценность требуют
решения Learning Orchestrator и при необходимости пользователя. Любое действие
внешней записи остаётся вне этого workflow.

## Недоступность

Если Obsidian или обязательный Anki-check недоступны, summary получает
`Outcome: pending`, соответствующий target — `unavailable`, а действие — `-`.
Он также указывает owner artifact и `Card Promotion pending` либо `Knowledge
Consolidation pending`; Orchestrator переносит этот trace для конкретного
source entity. Card Candidate остаётся `candidate`; Knowledge Consolidation не
считается выполненной. Следующий безопасный шаг — повторить проверку до нужного
gate.

## Границы

Workflow не заменяет Lightweight Checker и Source Check. Для чувствительных
claims `needs-check`, `rejected` и `superseded` по-прежнему блокируют Card
Promotion или Knowledge Consolidation согласно `Sources.md`.
