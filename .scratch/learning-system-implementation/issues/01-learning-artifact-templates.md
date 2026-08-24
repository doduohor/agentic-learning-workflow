# 01: Сделать шаблоны учебных артефактов

**What to build:** возможность создавать новую Topic Workspace из готовых human-first Markdown-шаблонов, а не копировать prototype вручную. Шаблоны должны покрывать `Goal.md`, `Knowledge.md`, `Practice.md`, `Questions.md`, `Weaknesses.md`, `RepetitionLog.md`, `Sources.md` и optional `sessions/`, сохраняя принятые owner files, ID formats, edit policies и запрет на YAML/JSON machine-readable schema.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [x] Есть reusable templates для семи основных Topic Workspace artifacts.
- [x] Шаблоны явно сохраняют owner files: `Goal.md` для Topic State, Active Block, Block Status и Mastery Level; `Sources.md` для Source Check Result; `Questions.md` для Question State и Card Candidate status.
- [x] Шаблоны показывают, где хранятся curated Knowledge, structured Practice Attempts, Weakness records, Active Repetition records и Source Records.
- [x] Optional `sessions/` описан как архив Session Notes и Practice Artifacts, а не обязательная часть каждой темы.
- [x] В шаблонах нет YAML/JSON machine-readable schema.
- [x] Создание шаблонов не создает новую учебную тему и не расширяет prototype.
