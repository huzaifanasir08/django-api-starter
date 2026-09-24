# django-api-starter

Generate a production-ready Django REST API project in one command. You get a
custom email-based user, JWT authentication, profile and password APIs, and
optional email OTP / two-factor login. The layout is flat and easy to read.

```bash
pip install django-api-starter
django-starter new myproject
```

This creates a `myproject/` folder. The command is also available as
`django-api-starter`, and `python -m django_api_starter` works too.

## What you get

```text
myproject/
├── apps/
│   └── accounts/          # User model, serializers, views, urls, admin, migrations
├── conf/
│   ├── settings/          # base.py, development.py, production.py, test.py
│   ├── asgi.py
│   ├── urls.py
│   └── wsgi.py
├── core/                  # JWT helpers, error format, pagination, permissions, middleware
│   └── management/commands/wait_for_db.py
├── requirements/          # base.txt, development.txt, production.txt
├── templates/emails/      # password reset (and OTP) emails
├── tests/                 # pytest suite for every endpoint
├── .env / .env.example
├── Dockerfile / docker-compose.yml   (optional)
├── manage.py
└── pytest.ini
```

**User model:** email login, name, phone, profile picture, role (`admin` / `user`), active flag and timestamps. With 2FA it also has `is_email_verified` and `two_factor_enabled`.

**Endpoints** (under `/api/v1/`):

| | |
| --- | --- |
| `auth/register/`, `auth/login/`, `auth/logout/`, `auth/token/refresh/` | Registration and JWT login. Refresh tokens rotate and are blacklisted after use |
| `auth/me/` (GET / PATCH) | Read or update your profile, including the picture upload |
| `auth/password/change/`, `auth/password/reset/`, `auth/password/reset/confirm/` | Change a password, or reset a forgotten one by email |
| `auth/otp/verify/`, `auth/otp/resend/` | Email OTP (only with `--2fa`) |
| `users/`, `users/<id>/` | Admin-only user list and management |

**With `--2fa`:**

- Signup emails a code to verify the address.
- Login asks for a code when the email isn't verified yet, or when the user has turned on `two_factor_enabled`.
- No JWT is issued until the code is verified.
- Codes are hashed, single-use, expire, lock after too many wrong tries, and have a resend cooldown.

**Also included:** a consistent error format, rate limiting on the auth endpoints, CORS, `.env` config, a request-ID middleware, a health check, Swagger docs, PostgreSQL or SQLite, and Docker.

## Usage

```bash
django-starter new myproject                  # interactive: asks about each option
django-starter new myproject -y               # accept the defaults
django-starter new myproject ./path/to/dir --database sqlite --2fa --no-docker -y
```

| Option | Default | |
| --- | --- | --- |
| `--database {postgres,sqlite}` | `postgres` | Sets up requirements, `.env` and docker-compose |
| `--2fa / --no-2fa` | off | Email OTP verification and two-factor login |
| `--docker / --no-docker` | on | `Dockerfile`, `docker-compose.yml`, `.dockerignore` |
| `--api-docs / --no-api-docs` | on | OpenAPI schema at `/api/schema/`, Swagger UI at `/api/docs/` |
| `-y, --yes` | | Don't prompt |

Generated projects need Python 3.12+ and Django 6.1+.

## Developing this package

```bash
pip install -e ".[dev]"
pytest
```

`src/django_api_starter/template/` holds the project template:

- `*.j2` files are rendered with Jinja2. Python files are always `.j2`, so they are never byte-compiled at install time.
- Other files are copied as they are. This keeps Django's own `{{ }}` syntax in the email templates intact.
- `dot-name` becomes `.name`.
- `OPTIONAL_FILES` in `generator.py` maps files to the feature flag that turns them on.

If the generated project's dependencies are installed, `pytest` also generates
projects and runs their migration check, OpenAPI validation and test suites.
Install them from a generated project:

```bash
django-starter new deps ../deps --database sqlite -y
pip install -r ../deps/requirements/development.txt
```

If you change a model, regenerate `apps/accounts/migrations/0001_initial.py.j2`:
generate a project, delete its migration, run `makemigrations`, and copy the
result back with the `{% if two_factor %}` blocks.

### Releasing

The version lives only in `src/django_api_starter/__init__.py` (`__version__`).

1. Bump `__version__`, commit and push to `main`, and wait for CI to pass.
2. Create a GitHub release with the tag `v<version>` (for example `v0.1.1`).
3. The **Publish** workflow checks that the tag matches `__version__`, builds,
   and uploads to PyPI with trusted publishing. No token is needed.

Run the Publish workflow manually (Actions → Publish → Run workflow) to upload
to TestPyPI instead. TestPyPI rejects a version it already has, so bump
`__version__` before each rehearsal upload.
