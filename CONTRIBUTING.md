# Contributing

## Setup

```bash
pip install -e ".[dev]"
pytest
```

## How the template works

`src/django_api_starter/template/` holds the project template:

- `*.j2` files are rendered with Jinja2. Python files are always `.j2`, so they are never byte-compiled at install time.
- Other files are copied as they are. This keeps Django's own `{{ }}` syntax in the email templates intact.
- `dot-name` becomes `.name`.
- `OPTIONAL_FILES` in `generator.py` maps files to the feature flag that turns them on.

Templates use `trim_blocks`: a `{% ... %}` tag at the very end of a line removes
the newline after it.

## End-to-end tests

If the generated project's dependencies are installed, `pytest` also generates
projects (plain, 2FA, Celery, 2FA + Celery) and runs their migration check,
OpenAPI validation and test suites. Install them from a generated project:

```bash
django-starter new deps ../deps --database sqlite --celery -y
pip install -r ../deps/requirements/development.txt
```

## Changing a model

Regenerate `apps/accounts/migrations/0001_initial.py.j2`: generate a project,
delete its migration, run `makemigrations`, and copy the result back with the
`{% if two_factor %}` blocks. The end-to-end tests fail if the migration and
the models disagree.

## Releasing

The version lives only in `src/django_api_starter/__init__.py` (`__version__`).

1. Bump `__version__`, commit and push to `main`, and wait for CI to pass.
2. Create a GitHub release with the tag `v<version>` (for example `v0.2.0`).
3. The **Publish** workflow checks that the tag matches `__version__`, builds,
   and uploads to PyPI with trusted publishing. No token is needed.

Run the Publish workflow manually (Actions → Publish → Run workflow) to upload
to TestPyPI instead. TestPyPI rejects a version it already has, so bump
`__version__` before each rehearsal upload.
