# Architecture Decisions

## MongoDB for raw events

We use MongoDB to store raw event data (page views, clicks, etc.) instead of PostgreSQL because:

- **Schema-less**: event payloads vary by event type and evolve over time without requiring migrations.
- **High write volume**: raw events are append-only and high-throughput; MongoDB handles this more efficiently than relational inserts with constraints/indexes on every write.

Aggregated/derived data still lives in PostgreSQL (`event_aggregates`), where a fixed schema and relational queries make more sense.
