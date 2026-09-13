# One-Time Secret Service

A small FastAPI service for sharing sensitive data (passwords, API keys, tokens) via a link that can only be opened **once**. After the secret is viewed, it is permanently gone.

Inspired by services like onetimesecret.com — built as a learning project to practice async FastAPI, SQLAlchemy, and basic security patterns (encryption, hashing, brute-force protection).

## Features

- **Encrypt-at-rest** — secret payload is encrypted with Fernet (symmetric encryption) before being stored.
- **Optional password protection** — a secret can additionally be protected with a password (stored as a bcrypt hash, never in plain text).
- **One-time read** — a secret is marked as viewed on first successful read and can never be retrieved again.
- **Race-condition safe** — concurrent reads of the same secret are protected with `SELECT ... FOR UPDATE`, so two simultaneous requests can't both "win" a read.
- **Brute-force protection** — failed password attempts are rate-limited per client (IP, or the secret ID itself as a fallback). 
- **Alembic migrations** for schema versioning.
- **Integration tests** with pytest + httpx, running against a real Postgres instance.

## Tech Stack

- **FastAPI** — async web framework
- **SQLAlchemy 2.0 (async)** — ORM
- **PostgreSQL** — database
- **Alembic** — migrations
- **Docker Compose** — local Postgres instance
- **pytest / pytest-asyncio / httpx** — testing

## Project Structure

```
.
├── alembic/              # migration scripts
├── models/                # SQLAlchemy ORM models
├── repository/            # data access layer (no business logic, no commits)
├── router/                # HTTP layer — request/response only
├── schemas/                # Pydantic request/response schemas
├── services/                # business logic (rate limiting, orchestration)
├── tests/                # integration tests
├── database.py            # engine/session setup
├── security.py             # encryption, hashing, token generation
├── docker-compose.yaml
├── alembic.ini
└── main.py
```

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose

### Installation

1. Clone the repo:

   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   ```

2. Copy `.env.example` to `.env` and fill in the values:

   ```bash
   cp .env.example .env
   ```

3. Start Postgres:

   ```bash
   docker compose up -d
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Apply migrations:

   ```bash
   alembic upgrade head
   ```

6. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

API docs available at `http://localhost:8000/docs`.

## API Endpoints

### `POST /keys/conceal`

Create a new secret.

```json
{
  "secret_data": {
    "key": "my-sensitive-value",
    "password": "optional-password"
  }
}
```

Returns:

```json
{ "id": "generated-secret-id" }
```

### `POST /keys/secrets/{secret_key}/reveal`

Read and permanently consume a secret.

```json
{ "password": "optional-password" }
```

Returns:

```json
{ "secret": "my-sensitive-value" }
```

Returns `403` if the secret doesn't exist, was already viewed, or the password is wrong. Returns `429` if the client has exceeded the allowed number of password attempts.

## Running Tests

Tests run against a separate Postgres database (not your dev database).

1. Create a test database inside the same Postgres container:

   ```bash
   docker compose exec postgres psql -U postgres -c "CREATE DATABASE secrets_test;"
   ```

2. Set `DATABASE_URL_TEST` in `.env` (see `.env.example`).

3. Run:
   ```bash
   pytest -v
   ```

## Design Notes & Trade-offs

A few decisions were made deliberately, favoring simplicity over production-grade robustness — worth knowing when reading the code:

- **`secret_id` is nullable** in the ORM model. This is a leftover from an earlier schema version where secrets didn't have a `secret_id` yet. Rather than writing a data migration to backfill old records, the column was left nullable. In a production system, this would be backfilled and the column made `NOT NULL`.
- **The rate limiter is in-memory** (a plain Python dict), not backed by Redis or the database. This means:
  - it doesn't survive a server restart,
  - it isn't shared across multiple worker processes or instances.

  This is an acceptable trade-off for a single-process learning project; a production deployment would move this state to Redis.

## License

MIT
