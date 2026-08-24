# 08: Сделать проверку дублей в Obsidian и Anki

**What to build:** read/check workflow, который перед Card Promotion и Knowledge Consolidation ищет похожие Obsidian notes и Anki cards, фиксирует Duplicate Check summary и помогает выбрать `skip`, `replace`, `merge`, `add`, `append` или `replace-section` без фактической записи во внешние системы.

**Blocked by:** 02: Сделать легковесную проверку Topic Workspace; 03: Сделать общие инструкции для учебных агентов; 07: Сделать поддержку проверки источников.

**Status:** ready-for-agent

- [ ] Workflow проверяет релевантный Obsidian-контекст перед Card Promotion и Knowledge Consolidation.
- [ ] Workflow проверяет Anki только перед фактическим добавлением или изменением карточки.
- [ ] Если Anki или Obsidian недоступны, workflow оставляет pending/unavailable outcome и не продвигает карточку или знание как выполненное.
- [ ] Duplicate Check summary записывается в owner artifacts без внешней записи.
- [ ] Strong duplicate, `replace`, спорный `merge` и сомнительная ценность требуют решения Learning Orchestrator и при необходимости пользователя.
- [ ] Workflow не создает Anki cards и не меняет Obsidian vault.
