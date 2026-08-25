## Grilling answer options

В `grilling` каждый вопрос с вариантами ответа должен давать пользователю реальный выбор. Варианты должны быть сопоставимыми по качеству и различаться по настоящему trade-off: например скорость против надежности, гибкость против простоты, строгий gate против мягкого процесса.

Запрещено делать варианты, где рекомендация выглядит единственно профессиональной, а остальные варианты очевидно слабые, утрированные или декоративные. Формулируй варианты коротко, конкретно и нормальным русским языком: без усложнения ради солидности и без чрезмерного упрощения.

## Agent skills

### Issue tracker

Issues and specs for this repo are tracked in GitHub Issues via `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

This repo uses the default five triage labels. See `docs/agents/triage-labels.md`.

### Domain docs

This repo uses a single-context domain doc layout with root `CONTEXT.md` and decisions in `docs/wayfinder/decisions/`. See `docs/agents/domain.md`.

## Anki cards and Obsidian context

When preparing or judging Anki cards for the user, use the Obsidian vault at `/mnt/c/Users/Sergey/Documents/GPT/Work` as required context.

Rules:
- Before deciding whether a card is important, consider the user's current learning target, stack, architecture, and job requirements from the vault.
- Current target context: Junior+/Middle Kotlin Backend for ЦУП РТ / АИС МИДИО.
- Current stack and architecture context includes Kotlin, Ktor, Git, Postgres/Exposed, Docker/Docker Compose, RabbitMQ, Prometheus, Grafana, MongoDB, ClickHouse, DDD, Transactional Outbox, system design, CI/CD, backend feature development, reliability, security, observability, and the Sports Facility Booking / MIDIO-inspired project.
- Before proposing or adding a card, check the vault for similar existing knowledge and tell the user what similar material already exists.
- Also check logically appropriate Anki decks for similar cards when possible.
- If similarity is strong, do not add the card immediately. Inspect the logically matching deck/cards first, then ask the user whether to skip, replace, merge, or add anyway.
- Prefer fewer, higher-value cards over many small cards. Rank card value by modern backend relevance, fit to the user's stack/project, interview usefulness, and cost of forgetting the concept.

Card content rules for better memorization:
- Optimize cards for active recall, not passive recognition. The front side should ask the user to retrieve an answer, make a distinction, explain a cause, choose an approach, or find a mistake.
- Do not create cards from material the user has not conceptually understood. First build a short explanation or link the card to existing Obsidian context; then create memorization cards.
- Prefer atomic cards: one card should test one retrievable unit. If an answer contains definition, types, algorithms, production risks, and examples, split it into several cards.
- Keep the required answer short and easy to self-grade: ideally 1-3 sentences or 3-4 bullets. Put optional detail after a clear `Дополнительно:` section, or create separate deeper cards.
- Start the back side with the direct answer. Add nuance only after the core answer is clear. Avoid answers that require rereading a paragraph to know whether the user was correct.
- Use backend-shaped prompts: `Когда использовать X?`, `Чем X отличается от Y?`, `Почему X опасен в production?`, `Что сломается, если ...?`, `Найди ошибку в утверждении ...`.
- For lists, avoid large unordered sets. If a list has more than 3-4 important items, create multiple cards, cloze cards, or grouped cards by category. Do not expect the user to recall a long catalogue from one prompt.
- Use cloze deletion for exact terms, small contrasts, syntax, or short causal chains. Do not use cloze to hide large paragraphs or several unrelated facts.
- Use examples to reduce ambiguity and interference. Prefer examples from the user's backend stack: Ktor services, Postgres transactions, RabbitMQ messages, Docker Compose, Prometheus metrics, Nginx/gateway traffic, CI/CD, or the Sports Facility Booking / MIDIO-inspired project.
- Create contrast cards for confusable concepts: `L4 vs L7`, `API Gateway vs reverse proxy`, `retry vs idempotency`, `metrics vs logs vs traces`. Include the distinguishing criterion, not only two definitions.
- Create production-risk cards for concepts the user must apply at Junior+/Middle backend level: failure mode, timeout, retry, idempotency, consistency, observability, security, deployment, and operational trade-off.
- If the user provides a long monolithic answer, do not silently turn it into one card unless explicitly requested. Suggest or perform a split into layered cards: `01-foundation`, `02-mechanics`, `03-api-and-design`, `04-architecture-and-production`.
- When a card becomes a leech or feels hard to answer, first suspect formulation: too much information, weak context, similarity to another card, or missing prerequisite. Fix by splitting, adding a contrast/example, or deleting low-value detail.
- Prefer durable understanding over trivia. Avoid memorizing volatile defaults, version-specific limits, command flags, or vendor details unless they are important for the user's stack and are source/date stamped.

Source quality rules:
- Use modern, verifiable knowledge for Anki cards. If a claim can depend on current versions, current tooling behavior, deprecations, cloud/provider features, security guidance, performance characteristics, or production best practices, verify it against current authoritative sources before creating or changing the card.
- Prefer primary sources: official documentation, language/framework docs, database vendor docs, protocol specifications/RFCs, release notes, standards bodies, and well-maintained project documentation. Use reputable engineering articles, books, conference talks, and vendor blogs only as secondary context.
- For this stack, especially prefer official/current docs for Kotlin, Ktor, JVM, Postgres/Exposed, Docker/Docker Compose, RabbitMQ, Prometheus, Grafana, MongoDB, ClickHouse, CI/CD tools, and security/observability practices.
- For networking and protocols, prefer RFCs, IETF/W3C materials, official project docs, and vendor docs. Avoid relying on simplified tutorials when the card teaches protocol semantics or production behavior.
- If current verification is unavailable, say `Нужно проверить` and do not present version-sensitive claims as certain. For user-provided text, fact-check risky or version-sensitive claims before importing or upgrading a card.
- When adding or replacing cards, briefly report what was checked: similar Obsidian material, similar Anki cards, and the source basis used for the final wording. Do not overload the card text with source names unless they help learning.
- Keep cards concise and durable. Avoid hype, tool ranking without context, outdated defaults, and overly specific limits unless the version/source is clear.

Card formulation evidence basis:
- Anki Manual: active recall, spaced repetition, effective learning, duplicate checks, leeches, cloze deletion, tags, and filtered decks: https://docs.ankiweb.net/
- SuperMemo / Piotr Wozniak: "Twenty rules of formulating knowledge", especially understand first, minimum information principle, simple wording, examples, interference, sources, date stamping, and prioritization: https://www.supermemo.com/en/blog/twenty-rules-of-formulating-knowledge
- Cognitive psychology evidence: practice testing/retrieval practice and distributed practice have strong support; interleaving is useful especially for discrimination between problem types. Prefer cards that force retrieval and help distinguish similar concepts.
