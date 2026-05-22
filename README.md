# Kazi Mikononi — Backend API

> **"Kazi Mikononi"** (Swahili: *Work in your hands*) is a platform that connects **clients** who need casual/skilled labour with **workers** who offer those services. This is the Flask REST API + WebSocket backend.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Getting Started](#getting-started)
- [Database Models](#database-models)
- [API Reference](#api-reference)
  - [Auth](#auth-endpoints)
  - [Jobs](#jobs-endpoints)
  - [Applications](#applications-endpoints)
  - [Workers](#workers-endpoints)
  - [Users](#users-endpoints)
  - [Ratings](#ratings-endpoints)
  - [Messages](#messages-endpoints)
- [WebSocket / Realtime](#websocket--realtime)
- [Authentication](#authentication)
- [File Uploads](#file-uploads)
- [Running Tests](#running-tests)
- [Deployment](#deployment)

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Framework | Flask | 3.1.3 |
| Database | PostgreSQL | — |
| ORM | Flask-SQLAlchemy / SQLAlchemy | 3.1.1 / 2.0.49 |
| Migrations | Flask-Migrate (Alembic) | 4.1.0 |
| Auth | Flask-JWT-Extended | 4.7.1 |
| Realtime | Flask-SocketIO | 5.6.1 |
| Email | Flask-Mail | 0.10.0 |
| CORS | Flask-Cors | 6.0.2 |
| Image Processing | Pillow | 12.2.0 |
| Password Hashing | Werkzeug | 3.1.8 |
| Email Verification | itsdangerous | 2.2.0 |
| HTTP Client | requests | 2.34.2 |
| WSGI Server | Gunicorn | 26.0.0 |
| Config | python-dotenv | 1.2.2 |

---

## Project Structure

```
kazi-mikononi-back-end/
├── app.py                  # App factory (create_app)
├── wsgi.py                 # Gunicorn entry point
├── config.py               # Config class (loads .env)
├── extensions.py           # All Flask extensions (db, jwt, socketio, etc.)
├── blacklist.py            # In-memory JWT revocation set
├── procfile                # Heroku/render deploy command
│
├── models/                 # SQLAlchemy models
│   ├── user.py
│   ├── job.py
│   ├── application.py
│   ├── message.py
│   ├── rating.py
│   └── skill.py
│
├── modules/                # Feature blueprints
│   ├── auth/               # Register, login, logout, verify email
│   ├── jobs/               # CRUD + image upload
│   ├── applications/       # Apply, view, update status
│   ├── workers/            # Worker profile, skills, availability
│   ├── users/              # Public/private profile management
│   ├── ratings/            # Worker ratings
│   └── messages/           # REST messaging + socket bridge
│
├── realtime/               # WebSocket event handlers
│   ├── socket.py           # init_socket() entry point
│   └── events.py           # connect, join, leave, send_message events
│
├── services/               # Shared service helpers
├── utils/                  # response helpers, security, validators
├── migrations/             # Alembic migration files
├── tests/                  # pytest test files
└── static/uploads/         # Uploaded job images (auto-created)
```

---

## Environment Variables

Create a `.env` file in the project root with the following keys:

```env
# Flask
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# JWT
JWT_SECRET_KEY=your-jwt-secret

# Email (Resend)
RESEND_API_KEY=your-resend-api-key
MAIL_DEFAULT_SENDER=noreply@yourdomain.com

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:5000
```

> JWT access tokens expire after **7 days**.  
> Max image upload size is **5 MB**.

---

## Getting Started

### 1. Clone & install dependencies

```bash
git clone <repo-url>
cd kazi-mikononi-back-end
pip install -r requirements.txt
```

### 2. Set up environment

```bash
cp .env.example .env
# Fill in your values
```

### 3. Set up the database

```bash
flask db upgrade
```

### 4. Run the development server

```bash
flask run
# or with SocketIO support:
python wsgi.py
```

The API will be available at `http://localhost:5000`.

---

## Database Models

### `User`

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| full_name | String(120) | Required |
| email | String(120) | Unique, required |
| password_hash | String(255) | Bcrypt hashed |
| role | String(20) | `client` or `worker` |
| phone | String(20) | Unique, optional |
| location | String(120) | Optional |
| is_verified | Boolean | Email verified flag |
| created_at | DateTime | Auto timestamp |

---

### `Job`

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| title | String(150) | Required |
| description | Text | Required |
| category | String(50) | Optional |
| budget | Float | Required |
| location | String(120) | Required |
| status | String(20) | `open` / `in_progress` / `completed` |
| urgency | String(50) | e.g. "Flexible - No rush" |
| duration | String(50) | e.g. "Few hours" |
| contact_method | String(50) | e.g. "Platform Messages" |
| image_url | String(255) | Optional uploaded image |
| client_id | FK → users | The client who posted the job |
| created_at | DateTime | Auto timestamp |

---

### `Application`

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| message | Text | Optional cover message |
| status | String(20) | `pending` / `accepted` / `rejected` |
| job_id | FK → jobs | The job applied to |
| user_id | FK → users | The worker who applied |
| created_at | DateTime | Auto timestamp |

---

### `Message`

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| content | Text | Required |
| sender_id | FK → users | Message author |
| receiver_id | Integer | Recipient user ID |
| created_at | DateTime | Auto timestamp |

---

### `Rating`

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| score | Integer | 1–5 stars |
| comment | Text | Optional |
| user_id | FK → users | Who gave the rating |
| worker_id | Integer | Worker being rated |
| created_at | DateTime | Auto timestamp |

---

### `Skill` / `WorkerSkill` / `WorkerProfile` / `WorkerAvailability`

Worker-specific models that extend the base `User`:
- **Skill** — master list of available skills (name, unique)
- **WorkerSkill** — many-to-many join between workers and skills
- **WorkerProfile** — extended worker bio/profile fields
- **WorkerAvailability** — worker's available time slots

---

## API Reference

> All protected routes require the header:
> ```
> Authorization: Bearer <access_token>
> ```

---

### Auth Endpoints

Base: `/auth`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | ❌ | Register new user (client or worker) |
| `POST` | `/auth/login` | ❌ | Login, returns JWT access token |
| `POST` | `/auth/logout` | ✅ | Logout, revokes JWT token |
| `GET` | `/auth/me` | ✅ | Get current logged-in user |
| `GET` | `/auth/verify/<token>` | ❌ | Verify email via token link |

**Register body:**
```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "password": "securepassword",
  "role": "worker"
}
```

**Login body:**
```json
{
  "email": "jane@example.com",
  "password": "securepassword"
}
```

**Login response:**
```json
{
  "access_token": "<jwt>",
  "user": { "id": 1, "full_name": "Jane Doe", "role": "worker", ... }
}
```

---

### Jobs Endpoints

Base: `/jobs`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/jobs/` | ❌ | List all open jobs |
| `POST` | `/jobs/` | ✅ Client | Create a new job |
| `GET` | `/jobs/<job_id>` | ❌ | Get single job details |
| `PUT` | `/jobs/<job_id>` | ✅ Client | Update a job |
| `DELETE` | `/jobs/<job_id>` | ✅ Client | Delete a job |
| `GET` | `/jobs/mine` | ✅ Client | List jobs posted by current client |
| `POST` | `/jobs/upload-image` | ✅ | Upload a job image (returns URL) |

**Create/Update Job body:**
```json
{
  "title": "Fix leaking pipe",
  "description": "Kitchen pipe leaking...",
  "category": "Plumbing",
  "budget": 1500.00,
  "location": "Nairobi, Kenya",
  "urgency": "Urgent",
  "duration": "Half day",
  "contact_method": "Platform Messages",
  "image_url": "/static/uploads/job-123.jpg"
}
```

---

### Applications Endpoints

Base: `/applications`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/applications/<job_id>` | ✅ Worker | Apply to a job |
| `GET` | `/applications/job/<job_id>` | ✅ Client | Get all applications for a job |
| `PUT` | `/applications/<application_id>/status` | ✅ Client | Accept or reject an application |
| `GET` | `/applications/mine` | ✅ Worker | Get all my applications |

**Apply body:**
```json
{ "message": "I have 5 years of experience..." }
```

**Update status body:**
```json
{ "status": "accepted" }
```

---

### Workers Endpoints

Base: `/workers`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/workers/` | ❌ | List all workers |
| `GET` | `/workers/<worker_id>` | ❌ | Get worker public profile |
| `POST` | `/workers/profile` | ✅ Worker | Create or update worker profile |
| `GET` | `/workers/profile` | ✅ Worker | Get own worker profile |
| `POST` | `/workers/skills` | ✅ Worker | Add a skill |
| `DELETE` | `/workers/skills` | ✅ Worker | Remove a skill |
| `GET` | `/workers/skills` | ✅ Worker | Get own skills |
| `POST` | `/workers/availability` | ✅ Worker | Set availability |
| `GET` | `/workers/availability` | ✅ Worker | Get availability |

---

### Users Endpoints

Base: `/users`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/users/<user_id>` | ❌ | Get any user's public profile |
| `GET` | `/users/me` | ✅ | Get current user's full profile |
| `PUT` | `/users/me` | ✅ | Update current user's profile |
| `DELETE` | `/users/me` | ✅ | Delete own account |

---

### Ratings Endpoints

Base: `/ratings`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/ratings/workers/<worker_id>` | ✅ Client | Rate a worker (1–5 stars) |
| `GET` | `/ratings/workers/<worker_id>` | ❌ | Get all ratings for a worker |

**Rate body:**
```json
{
  "score": 5,
  "comment": "Excellent work, very professional!"
}
```

---

### Messages Endpoints

Base: `/messages`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/messages/` | ✅ | Send a message (REST fallback) |
| `GET` | `/messages/<other_user_id>` | ✅ | Get conversation with a user |
| `GET` | `/messages/conversations` | ✅ | Get all conversations list |

---

## WebSocket / Realtime

The app uses **Flask-SocketIO** for real-time messaging. Connect to the WebSocket server at the same base URL.

### Client Events (emit from frontend → server)

| Event | Payload | Description |
|---|---|---|
| `join` | `{ "room": "chat_1_2" }` | Join a private chat room |
| `leave` | `{ "room": "chat_1_2" }` | Leave a chat room |
| `send_message` | `{ "sender_id": 1, "receiver_id": 2, "content": "Hello!" }` | Send a real-time message (saves to DB) |

### Server Events (listen on frontend ← server)

| Event | Payload | Description |
|---|---|---|
| `connected` | `{ "message": "Connected to Kazi Mikononi realtime server" }` | Emitted on successful connect |
| `joined` | `{ "message": "Joined room chat_1_2" }` | Confirmation of room join |
| `left` | `{ "message": "Left room chat_1_2" }` | Confirmation of room leave |
| `new_message` | `{ "id", "sender_id", "receiver_id", "content", "created_at" }` | New message broadcast to room |
| `error` | `{ "message": "..." }` | Error from invalid socket payload |

### Room Naming Convention

Chat rooms are deterministically named to ensure both users share the same room regardless of who initiates:

```
chat_{min(user_a_id, user_b_id)}_{max(user_a_id, user_b_id)}
```

**Example:** Users 3 and 7 share room `chat_3_7`.

---

## Authentication

- JWT tokens are issued on login and expire after **7 days**
- Tokens are revoked on logout using an in-memory **blacklist** (`blacklist.py`)
- Email verification is token-based via `itsdangerous` — a verification link is emailed on registration
- Password hashing uses `werkzeug.security` (PBKDF2 + SHA-256)

**Error responses from JWT middleware:**

| Code | HTTP | Meaning |
|---|---|---|
| `token_expired` | 401 | Token has passed its 7-day TTL |
| `token_invalid` | 401 | Malformed or tampered token |
| `token_missing` | 401 | No Authorization header provided |
| `token_revoked` | 401 | Token was explicitly revoked (logout) |

---

## File Uploads

Job images are uploaded via `POST /jobs/upload-image`.

- Saved to `static/uploads/` (auto-created on app start)
- Max file size: **5 MB** (`MAX_CONTENT_LENGTH`)
- Served statically at `/static/uploads/<filename>`
- The `image_url` field on a Job stores this path

---

## Running Tests

```bash
pytest tests/
```

Test files:
- `tests/test_auth.py` — Registration, login, logout, JWT
- `tests/test_jobs.py` — Job CRUD
- `tests/test_messages.py` — Messaging

Test config uses `.env.test` for an isolated test database.

---

## Deployment

The project includes a `procfile` for Heroku/Render:

```
web: gunicorn wsgi:app
```

For SocketIO support in production, use `eventlet` or `gevent`:

```bash
pip install eventlet
gunicorn --worker-class eventlet -w 1 wsgi:app
```

> ⚠️ Flask-SocketIO requires a single worker process. Do **not** use multiple Gunicorn workers without a message queue (e.g. Redis).

---

## User Roles Summary

| Role | Can Do |
|---|---|
| `client` | Post jobs, view applications, accept/reject workers, rate workers, message workers |
| `worker` | Browse jobs, apply to jobs, manage profile/skills/availability, message clients |

---

*Built with  using Flask + PostgreSQL + SocketIO*
