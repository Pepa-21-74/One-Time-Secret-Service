# One-Time Secret Service

A small FastAPI service for sharing sensitive data (passwords, API keys, tokens) via a link that can only be opened **once**. After the secret is viewed, it is permanently gone.

Inspired by services like onetimesecret.com — built as a learning project to practice async FastAPI, SQLAlchemy, and basic security patterns (encryption, hashing, brute-force protection).

## Features

- **Encrypt-at-rest** — the secret payload is encrypted with Fernet (symmetric encryption) before being stored.
- **Optional password protection** — a secret can additionally be protected with a password (stored as a bcrypt hash, never in plain text).
- **One-time read** — a secret is marked as viewed on first successful read and can never be retrieved again.
- **Race-condition safe** — concurrent reads of the same secret are protected with `SELECT ... FOR UPDATE`, so two simultaneous requests can't both "win" a read.
- **Brute-force protection** — after 5 failed password attempts, the client (IP, or the record ID as a fallback) is blocked for 5 minutes.
- **No information leak** — a missing secret, an already viewed secret, and a missing password all return the same `403` message.
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
├── models/               # SQLAlchemy ORM models
├── repository/           # data access layer (queries and commits, no HTTP logic)
├── router/               # HTTP layer — request/response only
├── schemas/              # Pydantic request/response schemas
├── services/             # business logic (rate limiting)
├── tests/                # integration tests
├── database.py           # engine/session setup
├── security.py           # encryption, hashing, token generation
├── docker-compose.yaml
├── init-test-db.sql      # creates the test database on first Postgres start
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

2. Create a `.env` file in the project root:

   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:8291/postgres
   DATABASE_URL_TEST=postgresql+asyncpg://postgres:postgres@localhost:8291/secrets_test
   ENCRYPTION_KEY=any-long-random-string
   ```

   `ENCRYPTION_KEY` is hashed into a Fernet key, so any sufficiently long random string works. Keep it safe: if it changes, existing secrets can no longer be decrypted.

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

API docs are available at `http://localhost:8000/docs`.

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

Read and permanently consume a secret. The body is only needed for password-protected secrets.

```json
{ "password": "optional-password" }
```

Returns:

```json
{ "secret": "my-sensitive-value" }
```

Returns `403` in all failure cases:

| Case | `detail` |
| --- | --- |
| Secret doesn't exist, was already viewed, or a password is required but not sent | `Secret not found or already view` |
| Wrong password | `Incorrect password` |
| Too many failed attempts (5 per client, blocked for 5 minutes) | `Too many attempts. Enter the password in 5 minutes.` |

## Running Tests

Tests run against a separate Postgres database (not your dev database).

1. The `secrets_test` database is created automatically by `init-test-db.sql` when the Postgres container starts for the first time. If your container was created earlier, create it manually:

   ```bash
   docker compose exec postgres psql -U postgres -c "CREATE DATABASE secrets_test;"
   ```

2. Make sure `DATABASE_URL_TEST` is set in `.env` (see above).

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
