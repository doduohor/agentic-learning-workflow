# 04: Создать файлы Codex-агентов

**What to build:** набор Codex Agent Files для Learning Orchestrator и supporting agents, которые можно использовать в учебном процессе. Каждый агент должен иметь понятный Role Mode, границу чтения/записи и формат результата, не получая лишних прав на состояние темы.

**Blocked by:** 03: Сделать общие инструкции для учебных агентов.

**Status:** ready-for-agent

- [x] Перед созданием файлов проверена актуальная схема Codex custom agent files.
- [x] Созданы agent definitions для Learning Orchestrator, learning support, practice, question/card, source и repetition ролей.
- [x] Learning Orchestrator явно владеет Topic State, Active Block, Block Status, Mastery Level, Completion Criteria, Card Promotion и Knowledge Consolidation decisions.
- [x] Supporting agents явно не могут менять `Goal.md`, `Knowledge.md`, `Weaknesses.md` напрямую.
- [x] Каждый supporting agent либо возвращает Agent Proposal, либо пишет только append-only в один разрешенный owner file по явному поручению.
- [x] Agent Files ссылаются на общие инструкции и не дублируют всю спецификацию.
