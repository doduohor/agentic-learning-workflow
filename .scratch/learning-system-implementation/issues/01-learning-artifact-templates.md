# 01: Сделать шаблоны учебных артефактов

**What to build:** возможность создавать новую Topic Workspace из готовых human-first Markdown-шаблонов, а не копировать prototype вручную. Шаблоны должны покрывать `Goal.md`, `Knowledge.md`, `Practice.md`, `Questions.md`, `Weaknesses.md`, `RepetitionLog.md`, `Sources.md` и optional `sessions/`, сохраняя принятые owner files, ID formats, edit policies и запрет на YAML/JSON machine-readable schema.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Есть reusable templates для семи основных Topic Workspace artifacts.
- [ ] Шаблоны явно сохраняют owner files: `Goal.md` для Topic State, Active Block, Block Status и Mastery Level; `Sources.md` для Source Check Result; `Questions.md` для Question State и Card Candidate status.
- [ ] Шаблоны показывают, где хранятся curated Knowledge, structured Practice Attempts, Weakness records, Active Repetition records и Source Records.
- [ ] Optional `sessions/` описан как архив Session Notes и Practice Artifacts, а не обязательная часть каждой темы.
- [ ] В шаблонах нет YAML/JSON machine-readable schema.
- [ ] Создание шаблонов не создает новую учебную тему и не расширяет prototype.
