# Idempotent consumer starting point established

The user understands that duplicate `BookingCreated` delivery can repeat consumer side effects, and correctly identified `event_id` as a better dedup key than `booking_id` because one booking can produce multiple different events. Future lessons can build on this by focusing on ack timing, local transactions, and durable side-effect orchestration.
