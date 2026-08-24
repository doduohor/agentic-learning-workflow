# 03: Сделать общие инструкции для учебных агентов

**What to build:** общий рабочий контракт для будущих Codex-агентов учебной системы. Документ должен объяснять, как агент читает Learning System Specification, соблюдает single-writer state model, оформляет Agent Proposal, распознает gates и не выходит за Agent Write Boundary.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Общие инструкции используют термины из `CONTEXT.md` и не переопределяют доменную модель.
- [ ] Инструкции явно закрепляют, что Learning Orchestrator применяет state-changing edits, а supporting agents работают через Agent Proposal или узкую append-only boundary.
- [ ] Инструкции описывают обязательные evidence и traceability для Practice Attempts, Questions, Weaknesses, Source Checks, Repetitions, Card Candidates и Knowledge Consolidation.
- [ ] Инструкции фиксируют правила `Нужно проверить`, Source Check, Duplicate Check и Card Promotion.
- [ ] Инструкции говорят, что supporting agents не пишут в Obsidian или Anki напрямую.
- [ ] Документ является рабочими правилами для агентов, а не копией всех decision records.
