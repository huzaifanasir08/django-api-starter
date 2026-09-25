# django-api-starter

[![PyPI](https://img.shields.io/pypi/v/django-api-starter)](https://pypi.org/project/django-api-starter/)
[![Python](https://img.shields.io/pypi/pyversions/django-api-starter)](https://pypi.org/project/django-api-starter/)
[![CI](https://github.com/huzaifanasir08/django-api-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/huzaifanasir08/django-api-starter/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/huzaifanasir08/django-api-starter/blob/main/LICENSE)

Generate a production-ready Django REST API project in one command.

Every new API needs the same foundation: a custom user model, JWT login,
profile and password endpoints, settings per environment, Docker and tests.
`django-api-starter` writes all of it for you, with a flat structure you can
read in one sitting. You choose the extras: email two-factor authentication,
Celery with Redis, PostgreSQL or SQLite, Docker, and API docs.

```bash
pip install django-api-starter
django-starter new myproject
```

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Command reference](#command-reference)
- [Generated project](#generated-project)
- [API reference](#api-reference)
- [Email verification and two-factor login](#email-verification-and-two-factor-login)
- [Background tasks with Celery and Redis](#background-tasks-with-celery-and-redis)
- [Configuration](#configuration)
- [Security defaults](#security-defaults)
- [Testing](#testing)
- [Deployment](#deployment)
- [Customizing the project](#customizing-the-project)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [License](#license)

## Features

### Always included

- **Custom user model** that logs in with email: name, phone, profile picture, role (`admin` / `user`), active flag and timestamps. It is set up before the first migration, as Django recommends.
- **JWT authentication** with [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/): short-lived access tokens, and refresh tokens that rotate and can't be reused.
- **Account APIs**: register, login, logout, token refresh, profile read and update (including picture upload), change password, and forgotten-password reset by email.
- **Admin user management**: an admin-only list with search, ordering and pagination, where admins can change a user's role or deactivate them.
- **Settings per environment**: `development`, `production` and `test`, all configured from a `.env` file.
- **One error format** for every endpoint, so frontends handle errors in one place.
- **Rate limiting** on the login, signup and reset endpoints.
- **Extras**: CORS, request IDs for tracing, a `/health/` endpoint, a `wait_for_db` command, and Django admin set up for the custom user.
- **A pytest suite** that covers every endpoint.

### Optional

| Option | Adds |
| --- | --- |
| `--2fa` | Email one-time codes: signup verifies the email address, and users can require a code at every login |
| `--celery` | Celery worker and scheduler with Redis. Emails are sent in the background, and clean-up jobs run on a schedule |
| `--database postgres` | PostgreSQL driver, `DATABASE_URL` and a Docker database service |
| `--docker` | `Dockerfile` for production and `docker-compose.yml` for local development |
| `--api-docs` | OpenAPI schema and Swagger UI with [drf-spectacular](https://drf-spectacular.readthedocs.io/) |

## Requirements

| To... | You need |
| --- | --- |
| Run the generator | Python 3.10+ |
| Run a generated project | Python 3.12+ (Django 6.1), **or** Docker |
| Use `--database postgres` without Docker | A PostgreSQL server |
| Use `--celery` without Docker | A Redis server |
| Send real emails | An SMTP account (Gmail, SendGrid, Amazon SES, Mailgun, and so on) |

With Docker, PostgreSQL and Redis run in containers, so you only need Docker installed.

## Quick start

### Option 1: SQLite, no Docker

This is the fastest way to try it. You only need Python 3.12+.

```bash
pip install django-api-starter
django-starter new myproject --database sqlite --no-docker -y
cd myproject

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements/development.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open <http://localhost:8000/api/docs/> to try the endpoints, and
<http://localhost:8000/admin/> for the Django admin. In development, emails
(reset links and codes) are printed to the terminal.

### Option 2: Docker (PostgreSQL, Redis, Celery)

```bash
pip install django-api-starter
django-starter new myproject --2fa --celery -y
cd myproject

docker compose up --build
docker compose exec web python manage.py createsuperuser
```

This starts the API on port 8000 together with PostgreSQL, Redis, a Celery
worker and the Celery scheduler. Your code is mounted into the containers, and
the server reloads when you save a file.

### Option 3: Interactive

```bash
django-starter new myproject
```

```text
Database (postgres/sqlite) [postgres]
Enable email OTP / two-factor authentication? [y/N]
Add Celery background tasks with Redis? [y/N]
Add Docker support? [Y/n]
Add API documentation (Swagger)? [Y/n]
```

Press Enter to accept the default shown in brackets.

## Command reference

```text
django-starter new NAME [DIRECTORY] [options]
```

The command is also available as `django-api-starter`, and
`python -m django_api_starter` works too.

| Argument / option | Default | Description |
| --- | --- | --- |
| `NAME` | | Project name. Letters, digits, `-` and `_`, starting with a letter. No spaces |
| `DIRECTORY` | `./NAME` | Where to create the project. The folder must be empty or not exist yet |
| `--database {postgres,sqlite}` | `postgres` | Database backend |
| `--2fa` / `--no-2fa` | off | Email verification and two-factor login |
| `--celery` / `--no-celery` | off | Celery background tasks with Redis |
| `--docker` / `--no-docker` | on | Docker files |
| `--api-docs` / `--no-api-docs` | on | OpenAPI schema and Swagger UI |
| `-y`, `--yes` | | Don't ask questions; use defaults for options you didn't give |
| `--version` | | Show the version |

Examples:

```bash
# Everything on
django-starter new shop --2fa --celery -y

# Minimal: SQLite, no Docker, no API docs
django-starter new shop --database sqlite --no-docker --no-api-docs -y

# Into a specific folder
django-starter new shop ~/projects/shop-api -y
```

## Generated project

```text
myproject/
├── apps/
│   └── accounts/
│       ├── migrations/
│       │   └── 0001_initial.py
│       ├── admin.py              # Django admin for users (and codes)
│       ├── apps.py
│       ├── models.py             # User (and OTP)
│       ├── serializers.py        # Validation for every endpoint
│       ├── tasks.py              # Scheduled clean-up tasks (--celery)
│       ├── urls.py
│       └── views.py              # Every account endpoint
├── conf/
│   ├── settings/
│   │   ├── base.py               # Shared settings, read from .env
│   │   ├── development.py        # DEBUG on, emails printed to the console
│   │   ├── production.py         # HTTPS, secure cookies, HSTS
│   │   └── test.py               # Fast hashing, in-memory email
│   ├── celery.py                 # Celery app (--celery)
│   ├── asgi.py
│   ├── urls.py
│   └── wsgi.py
├── core/                         # Code shared by every app
│   ├── management/commands/
│   │   └── wait_for_db.py
│   ├── auth.py                   # Issue and revoke JWTs
│   ├── exceptions.py             # The shared error format
│   ├── factories.py              # Test data factories
│   ├── middleware.py             # Request IDs
│   ├── pagination.py
│   ├── permissions.py            # IsAdmin, IsOwnerOrAdmin
│   ├── tasks.py                  # Background email sending (--celery)
│   ├── utils.py                  # send_templated_email()
│   └── views.py                  # /health/
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── templates/emails/             # password_reset.html (and otp.html)
├── tests/
│   ├── conftest.py
│   └── accounts/                 # auth, profile, password (otp, tasks)
├── .env                          # Your local settings, with a random SECRET_KEY
├── .env.example                  # Every setting, documented
├── Dockerfile                    # (--docker)
├── docker-compose.yml            # (--docker)
├── manage.py
├── pytest.ini
└── README.md                     # Docs for the generated project
```

Files marked with an option are only created when you choose it. The
`accounts` app keeps its models, serializers and views in one file each, so you
can follow any endpoint from URL to database without jumping between folders.

### The user model

| Field | Type | Notes |
| --- | --- | --- |
| `email` | email, unique | Used to log in. Saved in lowercase |
| `name` | text | Required |
| `phone` | text | Optional |
| `profile_picture` | image | Optional. Saved under a random file name |
| `role` | `admin` / `user` | Application role; defaults to `user`. Users can't change their own role |
| `is_active` | boolean | Inactive users can't log in, and their tokens stop working |
| `is_staff`, `is_superuser` | boolean | Access to the Django admin, separate from `role` |
| `is_email_verified` | boolean | `--2fa` only |
| `two_factor_enabled` | boolean | `--2fa` only. Asks for a code at every login |
| `date_joined`, `updated_at`, `last_login` | date and time | Set automatically |

The password is hashed by Django and never returned by the API.

## API reference

All endpoints are under `/api/v1/`. Send the access token in the header
`Authorization: Bearer <access>`.

| Method | Endpoint | Login required | Description |
| --- | --- | --- | --- |
| POST | `auth/register/` | no | Create an account |
| POST | `auth/login/` | no | Log in with email and password |
| POST | `auth/logout/` | yes | Revoke a refresh token |
| POST | `auth/token/refresh/` | no | Exchange a refresh token for new tokens |
| POST | `auth/otp/verify/` | no | Verify an emailed code and receive tokens (`--2fa`) |
| POST | `auth/otp/resend/` | no | Send a new code (`--2fa`) |
| GET | `auth/me/` | yes | Your profile |
| PATCH | `auth/me/` | yes | Update your name, phone or picture (or `two_factor_enabled`) |
| POST | `auth/password/change/` | yes | Change your password |
| POST | `auth/password/reset/` | no | Email a password reset link |
| POST | `auth/password/reset/confirm/` | no | Set a new password with the link's `uid` and `token` |
| GET | `users/` | admin | List users. Supports `?search=`, `?ordering=`, `?page=` and `?page_size=` |
| GET | `users/<id>/` | admin | Get one user |
| PATCH | `users/<id>/` | admin | Change a user's details, `role` or `is_active` |

### Examples

#### Register

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane@example.com", "phone": "+15550100",
       "password": "Sup3r-Secret-pass", "password_confirm": "Sup3r-Secret-pass"}'
```

```json
{
  "user": {"id": 1, "email": "jane@example.com", "name": "Jane Doe", "role": "user", "...": "..."},
  "tokens": {"access": "eyJ...", "refresh": "eyJ..."}
}
```

With `--2fa`, the response has no tokens yet. It asks for the code sent by email
(see [below](#email-verification-and-two-factor-login)).

#### Log in

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com", "password": "Sup3r-Secret-pass"}'
```

The response has the same shape as registration: `user` and `tokens`.

#### Refresh tokens

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ..."}'
```

This returns a new `access` **and** a new `refresh` token. The old refresh token
stops working, so always store the new one.

#### Update your profile, including a picture

```bash
curl -X PATCH http://localhost:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer eyJ..." \
  -F name="Jane Smith" \
  -F profile_picture=@photo.jpg
```

Use JSON for text fields only, or `multipart/form-data` when you upload a picture.

#### Reset a forgotten password

1. `POST auth/password/reset/` with `{"email": "jane@example.com"}`. The
   response is the same whether or not the account exists.
2. The email links to `PASSWORD_RESET_URL`, your frontend page, with `uid`
   and `token` added to it.
3. Your frontend sends `POST auth/password/reset/confirm/` with
   `{"uid": "...", "token": "...", "new_password": "...", "new_password_confirm": "..."}`.

The link works once and expires after `PASSWORD_RESET_TIMEOUT` seconds (1 hour by default).

### Errors

Every error uses the same shape:

```json
{
  "message": "Passwords do not match.",
  "code": "invalid",
  "errors": {"password_confirm": ["Passwords do not match."]}
}
```

- `message` is a human-readable summary you can show directly.
- `code` is stable text your code can check, such as `invalid`, `not_authenticated`, `permission_denied`, `throttled` or `token_not_valid`.
- `errors` lists messages per field. It is only present for validation errors (status 400).

## Email verification and two-factor login

Generate with `--2fa` to turn this on.

```text
register ──► code emailed ──► otp/verify ──► tokens
                                  ▲
login ──► password OK ──┬── email not verified ──► code emailed ─┤
                        ├── 2FA turned on ───────► code emailed ─┘
                        └── otherwise ──────────► tokens
```

1. **Register.** The account is created and a code is emailed. The response has no tokens:

   ```json
   {
     "message": "A verification code was sent to jane@example.com.",
     "requires_otp": true,
     "verification_id": "0b6f6f4e-...",
     "purpose": "email_verification",
     "expires_at": "2026-09-25T10:15:00Z"
   }
   ```

2. **Verify.** `POST auth/otp/verify/` with `{"verification_id": "...", "code": "123456"}`
   marks the email as verified and returns `user` and `tokens`.
3. **Log in.** If the email isn't verified yet, or the user has turned on
   `two_factor_enabled`, login returns a challenge like the one in step 1
   instead of tokens. Verify it the same way.
4. **Resend.** `POST auth/otp/resend/` with `{"verification_id": "..."}` sends a new
   code and returns a **new** `verification_id`. The old code stops working.
5. **Turn 2FA on or off.** `PATCH auth/me/` with `{"two_factor_enabled": true}`.

How codes are protected:

- Only a keyed hash of each code is stored, never the code itself.
- Each code works once and expires after `OTP_EXPIRY_MINUTES` (10 by default).
- After `OTP_MAX_ATTEMPTS` wrong tries (5 by default), the code is locked and the user must request a new one.
- Resending has a cooldown of `OTP_RESEND_COOLDOWN_SECONDS` (60 by default).
- No token is issued until the code is verified.

## Background tasks with Celery and Redis

Generate with `--celery` to turn this on. Redis is used for three things:

- **Celery broker**: the queue that carries tasks to the worker.
- **Task results**, kept for one day.
- **Django's cache.** Rate limits are counted in the cache, so with Redis they
  are shared by all server processes. With the default in-memory cache, each
  process would keep its own counters.

### What runs in the background

| Task | When | What it does |
| --- | --- | --- |
| `core.tasks.send_email` | Whenever an email is sent | Sends the email. Retries up to 5 times with increasing delays if the mail server fails. API requests don't wait for it |
| `flush_expired_tokens` | Daily | Deletes expired refresh tokens from the database |
| `delete_stale_otps` | Hourly (`--2fa` only) | Deletes used and expired codes |

**Running it without Docker** (Redis must be running at `REDIS_URL`):

```bash
celery -A conf worker -l info        # Windows: add --pool=solo
celery -A conf beat -l info          # runs the scheduled tasks
```

**Adding your own task.** Create `tasks.py` in any app; Celery finds it
automatically:

```python
from celery import shared_task

@shared_task
def generate_report(report_id):
    ...

generate_report.delay(report_id=42)   # returns immediately
```

Pass IDs and plain values to tasks, not model instances. To run a task on a
schedule, add it to `CELERY_BEAT_SCHEDULE` in `conf/settings/base.py`.

The test settings run tasks immediately and use an in-memory cache, so `pytest`
doesn't need Redis.

## Configuration

Settings are read from environment variables or the `.env` file. The generator
creates `.env` with a random `SECRET_KEY`. `.env.example` lists every setting and
should be committed; `.env` is git-ignored and should not be.

| Variable | Default | Description |
| --- | --- | --- |
| `SECRET_KEY` | (random in `.env`) | Required in production |
| `DEBUG` | `False` | Always `True` in development settings and `False` in production |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Required in production |
| `DATABASE_URL` | SQLite file | For example `postgres://user:pass@host:5432/db` |
| `DB_CONN_MAX_AGE` | `60` | Seconds to keep database connections open |
| `CORS_ALLOWED_ORIGINS` | none | Frontend origins allowed to call the API, comma-separated |
| `CSRF_TRUSTED_ORIGINS` | none | Production only; for the admin behind HTTPS |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | `15` | |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | `30` | |
| `EMAIL_BACKEND` | SMTP (console in development) | |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_TIMEOUT` | | SMTP settings |
| `DEFAULT_FROM_EMAIL` | `<project> <noreply@example.com>` | Sender address |
| `PASSWORD_RESET_URL` | `http://localhost:3000/reset-password?uid={uid}&token={token}` | Your frontend's reset page |
| `PASSWORD_RESET_TIMEOUT` | `3600` | Reset link lifetime in seconds |
| `THROTTLE_AUTH_RATE` | `10/min` | Rate limit for login, signup and reset, per IP address |
| `THROTTLE_OTP_RATE` | `10/min` | Rate limit for code verify and resend (`--2fa`) |
| `OTP_LENGTH`, `OTP_EXPIRY_MINUTES`, `OTP_MAX_ATTEMPTS`, `OTP_RESEND_COOLDOWN_SECONDS` | `6`, `10`, `5`, `60` | `--2fa` |
| `REDIS_URL` | `redis://localhost:6379/0` | `--celery` |
| `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | `REDIS_URL` | `--celery`. Only set these to use something other than Redis |
| `TIME_ZONE` | `UTC` | |
| `LOG_LEVEL` | `INFO` | |
| `SECURE_SSL_REDIRECT` | `True` | Production |
| `SECURE_HSTS_SECONDS` | 30 days | Production |

`manage.py` uses `conf.settings.development` by default. `wsgi.py` and `asgi.py`
use `conf.settings.production`. Set `DJANGO_SETTINGS_MODULE` to override either.

## Security defaults

- Passwords are hashed by Django and checked against Django's password validators.
- Access tokens last 15 minutes. Refresh tokens rotate, and a used one can't be reused.
- Logout revokes the refresh token, and a user can only log out their own token.
- Changing or resetting a password logs the user out everywhere.
- Deactivated users can't log in, and their existing tokens are rejected.
- Login gives the same error for a wrong password, an unknown email and an inactive account, so accounts can't be discovered.
- Password reset responds the same way whether or not the email is registered.
- Login, signup, reset and code endpoints are rate-limited per IP address.
- Users can't set their own role, email or active status through the API.
- Uploaded pictures get random file names.
- Production settings require `SECRET_KEY` and `ALLOWED_HOSTS`, and turn on HTTPS redirect, secure cookies and HSTS.
- The Docker image runs as a non-root user.

## Testing

```bash
pytest
```

The suite covers registration, login, token rotation, logout, profile updates
(including picture upload), admin permissions, password change and reset, and
every code and task path when those options are on. It uses fast password
hashing and in-memory email, so it runs in a few seconds. It needs no Redis;
it only needs PostgreSQL if `DATABASE_URL` points to it.

Use `core.factories.UserFactory` to create test users:

```python
from core.factories import UserFactory

admin = UserFactory(role="admin")
```

## Deployment

1. Set `DJANGO_SETTINGS_MODULE=conf.settings.production`.
2. Set `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`, the
   email settings, and `REDIS_URL` if you use Celery.
3. Run `python manage.py migrate` on each deploy.
4. Serve with gunicorn: `gunicorn conf.wsgi:application --bind 0.0.0.0:8000`.
   The `Dockerfile` already does this, and runs `collectstatic` when the image
   is built.
5. With Celery, run the same image twice more with the commands
   `celery -A conf worker -l info` and `celery -A conf beat -l info`.
   Run only **one** beat process, or scheduled tasks will run more than once.
6. Put the app behind a proxy or load balancer that handles HTTPS and sets
   `X-Forwarded-Proto`.

Build the production image with:

```bash
docker build -t myproject .
```

## Customizing the project

The generated code is yours to change. It has no runtime dependency on
`django-api-starter`. Common changes:

- **Add a role.** Add it to `User.Role` in `apps/accounts/models.py`, run
  `python manage.py makemigrations`, and use `request.user.role` in a
  permission class in `core/permissions.py`.
- **Add a field to users.** Add it to the model, run `makemigrations`, and list
  it in `UserSerializer.Meta.fields` (and in `read_only_fields` if users
  shouldn't edit it).
- **Add an app.** Run `mkdir apps/orders` then `python manage.py startapp orders apps/orders`. In its `apps.py`, set
  `name = "apps.orders"`, then add `"apps.orders"` to `LOCAL_APPS` and include
  its URLs in `conf/urls.py`.
- **Change token lifetimes.** Set `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` and
  `JWT_REFRESH_TOKEN_LIFETIME_DAYS` in `.env`.
- **Restyle emails.** Edit the HTML files in `templates/emails/`. The plain-text
  version is created from the HTML automatically.
- **Switch email provider.** Use any SMTP service by setting the `EMAIL_*`
  variables, or set `EMAIL_BACKEND` to a provider's Django backend.

## Troubleshooting

**`django-api-starter: command not found`**
Use `django-starter`, or upgrade with `pip install --upgrade django-api-starter`;
the latest version accepts both names. If
neither is found, pip's scripts folder isn't on your `PATH`. Run
`python -m django_api_starter new myproject` instead.

**`error: unrecognized arguments`**
Project names can't contain spaces: `new home care` reads `home` as the name and
`care` as the folder. Use `home_care` or `home-care`.

**`Target directory ... is not empty`**
The generator never writes into a folder that already has files, so it can't
overwrite your work. Leave out the directory to create a new folder, or pass an
empty folder.

**Django fails to install, or says it needs a newer Python**
Generated projects use Django 6.1, which needs Python 3.12+. Upgrade Python or
use Docker.

**`Error loading psycopg2 or psycopg module`**
The project uses PostgreSQL, but the driver isn't installed. Run
`pip install -r requirements/development.txt` inside the project's virtual
environment.

**`Connection refused` on port 6379, or `/health/` reports the cache as unavailable**
Redis isn't running. Start it with `docker compose up -d redis`, or install Redis
locally and check `REDIS_URL`.

**The Celery worker exits or hangs on Windows**
Celery's default worker pool doesn't support Windows. Run
`celery -A conf worker -l info --pool=solo`.

**I don't see the OTP or reset email**
In development, emails are printed to the console: the `runserver` terminal, or
the Celery worker's terminal with `--celery`. Set the `EMAIL_*` variables to send
real emails.

**`401` with `token_not_valid` on refresh**
Each refresh token works once. Store the new `refresh` token from every refresh
response.

## Roadmap

- SMS codes
- Authenticator app (TOTP) codes
- Social login (Google, GitHub, Apple)
- Listing and ending active sessions
- More storage options, such as Amazon S3

Suggestions and pull requests are welcome; see
[CONTRIBUTING.md](https://github.com/huzaifanasir08/django-api-starter/blob/main/CONTRIBUTING.md).

## License

[MIT](https://github.com/huzaifanasir08/django-api-starter/blob/main/LICENSE)
