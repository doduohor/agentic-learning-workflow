# 05: Спроектировать интерфейс учебных команд

**What to build:** понятный интерфейс будущих lifecycle commands для Topic Workspace. Пользователь и агент должны понимать, что делают `start/intake`, `diagnose`, `plan`, `learn-block`, `practice`, `review`, `repeat`, `pause`, `resume`, `complete`, какие файлы они читают, какие gates проверяют и где останавливаются.

**Blocked by:** 01: Сделать шаблоны учебных артефактов; 02: Сделать легковесную проверку Topic Workspace; 03: Сделать общие инструкции для учебных агентов.

**Status:** ready-for-agent

- [x] Для каждого lifecycle scenario описаны входные условия, читаемый контекст, допустимые изменения и stop conditions.
- [x] Интерфейс сохраняет single-writer state model: state-changing edits применяет Learning Orchestrator.
- [x] Команды не обходят Source Check, Duplicate Check, Card Promotion, Knowledge Consolidation и Lightweight Checker gates.
- [x] `pause` и `resume` сохраняют next safe action и не теряют open Weaknesses, pending Source Checks, Card Candidates или Active Repetitions.
- [x] `complete` явно блокируется при open blocker Weakness, missing Completion Evidence или blocking `needs-check`.
- [x] Решение не создает реальные slash commands, если ticket ограничен только дизайном интерфейса.
