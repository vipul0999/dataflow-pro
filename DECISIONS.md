# Architecture Decisions

### MongoDB for raw events

We use MongoDB for raw event data because:

- Event payloads vary by event type and can evolve without requiring relational schema migrations.
- Raw events are append-only and fit naturally into a document-oriented storage model.
- MongoDB allows each event to retain flexible metadata while keeping ingestion logic simple.

This does not mean MongoDB is always faster than PostgreSQL. Actual performance depends on indexing, batching, schema design, durability settings, and workload characteristics.

Aggregated and relational data remains in PostgreSQL because it benefits from constraints, joins, and a fixed schema.
