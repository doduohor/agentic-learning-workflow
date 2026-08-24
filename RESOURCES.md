# Kotlin Backend Production Readiness Resources

## Knowledge

- [PostgreSQL documentation: Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)
  Use for: atomicity, commit/rollback, transaction visibility, and why database changes must be grouped when a business operation has multiple writes.
- [RabbitMQ documentation: Consumer Acknowledgements and Publisher Confirms](https://www.rabbitmq.com/docs/confirms)
  Use for: publisher confirms, consumer acknowledgements, requeueing, prefetch, and the boundary between broker responsibility and application responsibility.
- [RabbitMQ documentation: Reliability Guide](https://www.rabbitmq.com/docs/reliability)
  Use for: distributed messaging failure modes, retransmission, at-least-once delivery, duplicate handling, and publisher/consumer data safety.
- [Microservices.io: Transactional Outbox](https://microservices.io/patterns/data/transactional-outbox.html)
  Use for: the transactional outbox pattern, why 2PC is usually avoided, why relay duplication is expected, and why consumers must be idempotent.

- [Microservices.io: Idempotent Consumer](https://microservices.io/patterns/communication-style/idempotent-consumer.html)
  Use for: duplicate message handling, processed-message tables, and why at-least-once delivery requires idempotent consumers.

- [RabbitMQ docs: Dead Letter Exchanges](https://www.rabbitmq.com/docs/dlx)
  Use for: routing messages that cannot be processed, poison message handling, and DLX/DLQ design.

- [RabbitMQ docs: Time-To-Live and Expiration](https://www.rabbitmq.com/docs/ttl)
  Use for: delayed retry patterns, message expiration, and retry queue timing caveats.

## Wisdom (Communities)

- [r/PostgreSQL](https://www.reddit.com/r/PostgreSQL/)
  Use for: real-world database design questions, operational caveats, and practical feedback on schema/transaction choices.
- [RabbitMQ GitHub Discussions](https://github.com/rabbitmq/rabbitmq-server/discussions)
  Use for: RabbitMQ behavior questions and operational design checks that need practitioner feedback.

## Gaps

- Add Kotlin/Ktor official resources for transaction management and integration testing after the first hands-on Ktor lesson.
- Add Exposed documentation only when a lesson uses Exposed directly.
