# Outbox stuck metric nuance understood

The user correctly explained that retry count alone is insufficient for detecting a stuck outbox because retries can grow due to temporary publish errors, while age oldest unpublished directly shows whether unpublished events are aging and backlog freshness is degrading.
