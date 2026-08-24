# 10: Сделать поддержку handoff между Codex-сессиями

**What to build:** workflow продолжения работы после паузы или смены Codex-сессии. Новая сессия должна восстановить wayfinder или Topic Workspace context из устойчивых файлов, увидеть next safe action, Role Mode, Agent Write Boundary, pending checks и не нарушить owner model.

**Blocked by:** 02: Сделать легковесную проверку Topic Workspace; 03: Сделать общие инструкции для учебных агентов; 05: Спроектировать интерфейс учебных команд.

**Status:** ready-for-agent

- [ ] Handoff workflow различает Wayfinder Handoff и Topic Workspace Handoff.
- [ ] Для Topic Workspace новая сессия читает `Goal.md` и связанные owner artifacts, если следующий шаг зависит от Weaknesses, Questions, Sources, RepetitionLog, Practice или Knowledge.
- [ ] Optional `Handoff.md` создается только при риске потери контекста и не становится source of truth.
- [ ] Handoff явно показывает next safe action, Role Mode и Agent Write Boundary.
- [ ] Open Weaknesses, pending Source Checks, Card Candidates, Active Repetitions и missed repetitions не теряются при `pause`/`resume`.
- [ ] Supporting agent без ясного Role Mode работает через Agent Proposal и не меняет state-changing artifacts.
