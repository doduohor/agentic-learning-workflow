# 06: Сделать создание новой Topic Workspace через intake

**What to build:** первый рабочий сценарий `start/intake`, который превращает сырой учебный запрос в новую Topic Workspace. Пользователь должен получить созданную тему с начальным `Goal.md`, корректной строкой в Topic Index, stable slug, начальным Topic State и результатом проверки checker.

**Blocked by:** 01: Сделать шаблоны учебных артефактов; 02: Сделать легковесную проверку Topic Workspace; 05: Спроектировать интерфейс учебных команд.

**Status:** ready-for-agent

- [x] Intake собирает Subject, Topic, Stable Slug, Topic Workspace path, Learning Profile и черновую цель.
- [x] Новая Topic Workspace создается из принятых templates, а не из ручной копии prototype.
- [x] Topic Index получает навигационную строку, но не становится source of truth для Topic State.
- [x] `Goal.md` получает Topic State `intake` или другой разрешенный стартовый state по принятому lifecycle.
- [x] После создания запускается read-only checker или эквивалентная проверка созданной структуры.
- [x] Сценарий не создает Anki cards, Obsidian notes, Agent Files или новую полноценную учебную тему сверх intake-структуры.
