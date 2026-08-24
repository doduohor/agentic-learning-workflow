# 02: Сделать легковесную проверку Topic Workspace

**What to build:** read-only Lightweight Checker, который помогает Learning Orchestrator и supporting agents проверять Topic Workspace перед gates. Пользователь должен получить человекочитаемый отчет о broken Entity References, неверных ID, stale links, owner violations, Draft Orphans и gate-blocking inconsistencies без автоматического исправления файлов.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Checker читает Topic Index и одну Topic Workspace и сообщает findings без изменения файлов.
- [ ] Checker проверяет owner invariants для `Goal.md`, `Sources.md`, `Questions.md`, `Knowledge.md`, `Practice.md`, `Weaknesses.md` и `RepetitionLog.md`.
- [ ] Checker различает severity и gate impact: например `blocks production-ready`, `blocks completed`, `blocks card-promotion`, `blocks knowledge-consolidation`, `blocks handoff`, `does not block`.
- [ ] Checker сообщает blocking finding, если `needs-check` используется как подтвержденное evidence для `production-ready`, `completed`, Card Promotion или Knowledge Consolidation.
- [ ] Checker сообщает, когда Card Candidate имеет `promoted` без Duplicate Check, Card Trace, Promotion Decision или Source Check gates.
- [ ] Checker ничего не исправляет сам и не вводит YAML/JSON machine-readable schema.
