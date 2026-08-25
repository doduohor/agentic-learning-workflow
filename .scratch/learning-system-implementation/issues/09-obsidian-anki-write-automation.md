# 09: Сделать запись в Obsidian и Anki через подтверждаемый preview

**What to build:** Orchestrator-controlled write automation для уже принятого Card Promotion или Knowledge Consolidation decision. Пользователь должен увидеть dry-run preview, подтвердить внешний write target, а система должна записать trace outcome и безопасно переживать повторный запуск или частичный сбой.

**Blocked by:** 02: Сделать легковесную проверку Topic Workspace; 07: Сделать поддержку проверки источников; 08: Сделать проверку дублей в Obsidian и Anki.

**Status:** ready-for-agent

- [x] Перед любой внешней записью формируется dry-run preview с target, action, proposed content, Duplicate Check summary, Source Check summary, trace и expected Markdown updates.
- [x] Внешняя запись не выполняется без user approval после preview.
- [x] Anki write выполняется только после Card Promotion decision и пройденных gates.
- [x] Obsidian write выполняется только после Knowledge Consolidation decision и пройденных gates.
- [x] Write outcome фиксируется в owner artifacts: `Questions.md` для Anki/Card Promotion, `Knowledge.md` для Obsidian/Knowledge Consolidation, `Goal.md` только кратко при влиянии на next action или Completion Criteria.
- [x] Re-run/idempotency behavior покрывает no-op, pending, partial, failed и reconciliation preview cases.
