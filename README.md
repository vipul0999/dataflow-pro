# DataFlow Pro

A real-time analytics platform. Clients send raw events (page views, clicks,
etc.) tied to a project; DataFlow Pro stores them, rolls them up into daily
aggregates, and exposes analytics.

## Architecture

DataFlow Pro is a monorepo with a polyglot-persistence backend: structured
relational data lives in **PostgreSQL**, while high-volume raw events live in
**MongoDB**.

```
                  ┌─────────────────────────────────────────┐
   client ──▶ API │  FastAPI (backend/fastapi_app)           │
   (event)        │                                          │
                  │   raw event ──▶ MongoDB  (dataflow_raw)   │  schema-less,
                  │                  raw_events collection    │  high write volume
                  │                                          │
                  │   rollup    ──▶ PostgreSQL                │  structured,
                  │                  users / projects /       │  relational
                  │                  api_keys / event_aggregates
                  └─────────────────────────────────────────┘
                         Alembic manages the Postgres schema
```

**Why two databases?** Raw events are append-only, vary by event type, and
arrive at high volume — a natural fit for MongoDB's schema-less documents.
Aggregated counts and account data (users, projects, keys) have a fixed schema
and benefit from relational queries and constraints, so they live in Postgres.
See [DECISIONS.md](DECISIONS.md) for the full rationale.

### Data model (PostgreSQL)

| Table | Purpose |
|-------|---------|
| `users` | Accounts that own projects |
| `projects` | Workspaces owned by a user; group events and keys |
| `api_keys` | Per-project tokens used to ingest events (revocable) |
| `event_aggregates` | Daily rollup of event counts per project / type |

Raw events themselves are stored in MongoDB (`dataflow_raw.raw_events`).

## Project layout

```
dataflow-pro/
├── backend/
│   ├── alembic/                # database migrations
│   ├── alembic.ini             # alembic config
│   └── fastapi_app/
│       ├── database.py         # PostgreSQL engine, session, Base
│       ├── mongo.py            # MongoDB connection + event helpers
│       ├── models/             # SQLAlchemy ORM models
│       ├── routers/            # API route handlers
│       ├── schemas/            # Pydantic request/response schemas
│       ├── .env                # local secrets (gitignored)
│       └── .env.example        # template for required env vars
├── frontend/                   # web UI
├── pipeline/                   # data pipeline (dags, jobs, transforms)
├── messaging/                  # messaging layer
├── tests/
├── DECISIONS.md                # architecture decision records
└── README.md
```

## Prerequisites

- **Python 3.14**
- **Docker Desktop** (runs PostgreSQL and MongoDB locally)
- **Git**

## Setup

### 1. Clone and install dependencies

```powershell
git clone https://github.com/vipul0999/dataflow-pro.git
cd dataflow-pro
pip install -r backend/fastapi_app/requirements.txt
```

### 2. Configure environment variables

```powershell
# from backend/fastapi_app/
copy .env.example .env
```

Then edit `.env` and set a real `SECRET_KEY`. The defaults for
`DATABASE_URL` and `MONGO_URL` match the Docker setup below.

### 3. Start the databases (Docker)

```powershell
# PostgreSQL
docker run --name dataflow-postgres `
  -e POSTGRES_USER=dfuser -e POSTGRES_PASSWORD=dfpass -e POSTGRES_DB=dataflow `
  -p 5432:5432 -d postgres

# MongoDB
docker run --name dataflow-mongo -p 27017:27017 -d mongo
```

On later sessions, reuse the existing containers instead of recreating them:

```powershell
docker start dataflow-postgres dataflow-mongo
```

### 4. Run database migrations

```powershell
cd backend
alembic upgrade head
```

Verify the tables were created:

```powershell
docker exec dataflow-postgres psql -U dfuser -d dataflow -c "\dt"
```

## Database migrations (Alembic)

Alembic lives in `backend/` and manages the PostgreSQL schema.

```powershell
cd backend

# After changing a model, autogenerate a migration:
alembic revision --autogenerate -m "describe your change"

# Apply pending migrations:
alembic upgrade head

# Roll back the most recent migration:
alembic downgrade -1
```

`alembic/env.py` imports the models' `Base.metadata` and reads `DATABASE_URL`
from the app config, so autogenerate stays in sync with the ORM models.

## Testing the MongoDB layer

```powershell
cd backend
python -c "from fastapi_app.mongo import insert_event, get_events_by_project; insert_event({'project_id':'test','event_type':'page_view','ts':'2024-01-01'}); print(get_events_by_project('test'))"
```

You should see the inserted document echoed back with an `_id` field.
