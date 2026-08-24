# 07: Сделать поддержку проверки источников

**What to build:** workflow для Source Verification, который позволяет фиксировать Source Records, результаты `verified`, `rejected`, `needs-check`, `superseded` и gate impact. Агент должен уметь записать, что claim не проверен, не выдавая его за подтвержденный факт.

**Blocked by:** 01: Сделать шаблоны учебных артефактов; 02: Сделать легковесную проверку Topic Workspace; 03: Сделать общие инструкции для учебных агентов.

**Status:** ready-for-agent

- [ ] Source workflow создает или обновляет Source Records в `Sources.md` в рамках принятого owner model.
- [ ] `Sources.md` остается единственным владельцем Source Check Result.
- [ ] `needs-check` и `Нужно проверить` блокируют `production-ready`, `completed`, Card Promotion и Knowledge Consolidation, когда claim нужен для gate.
- [ ] Source Agent может предлагать изменения в Knowledge, Questions или Goal, но state-changing edits применяет Learning Orchestrator.
- [ ] Workflow явно обрабатывает недоступность источников и не подтверждает claims по памяти агента.
- [ ] Реальная внешняя проверка конкретной RabbitMQ-темы не входит в этот ticket, если она не задана отдельно.
