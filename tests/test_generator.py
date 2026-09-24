import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from django_api_starter import ProjectConfig, generate_project
from django_api_starter.cli import main

CORE_FILES = [
    "manage.py",
    "apps/__init__.py",
    "apps/accounts/__init__.py",
    "apps/accounts/admin.py",
    "apps/accounts/apps.py",
    "apps/accounts/models.py",
    "apps/accounts/serializers.py",
    "apps/accounts/urls.py",
    "apps/accounts/views.py",
    "apps/accounts/migrations/__init__.py",
    "apps/accounts/migrations/0001_initial.py",
    "conf/__init__.py",
    "conf/asgi.py",
    "conf/urls.py",
    "conf/wsgi.py",
    "conf/settings/__init__.py",
    "conf/settings/base.py",
    "conf/settings/development.py",
    "conf/settings/production.py",
    "conf/settings/test.py",
    "core/__init__.py",
    "core/apps.py",
    "core/auth.py",
    "core/exceptions.py",
    "core/factories.py",
    "core/middleware.py",
    "core/pagination.py",
    "core/permissions.py",
    "core/utils.py",
    "core/views.py",
    "core/management/commands/wait_for_db.py",
    "requirements/base.txt",
    "requirements/development.txt",
    "requirements/production.txt",
    "templates/emails/password_reset.html",
    "tests/conftest.py",
    "tests/accounts/test_auth.py",
    ".env",
    ".env.example",
    ".gitignore",
    ".gitattributes",
    "pytest.ini",
    "README.md",
]


def generate(tmp_path, **options):
    config = ProjectConfig(name="myproject", **options)
    target = tmp_path / "myproject"
    generate_project(config, target)
    return target


def test_generates_core_files(tmp_path):
    target = generate(tmp_path)

    for path in CORE_FILES:
        assert (target / path).is_file(), path


def test_no_template_artifacts_left(tmp_path):
    target = generate(tmp_path, two_factor=True)

    for path in target.rglob("*"):
        assert not path.name.endswith(".j2")
        assert not path.name.startswith("dot-")
        if path.suffix == ".py":
            source = path.read_text(encoding="utf-8")
            assert "{%" not in source and "{{" not in source, path
            compile(source, str(path), "exec")


def test_email_templates_are_copied_verbatim(tmp_path):
    target = generate(tmp_path)

    assert "{{ reset_url }}" in (target / "templates/emails/password_reset.html").read_text(encoding="utf-8")


def test_two_factor_off(tmp_path):
    target = generate(tmp_path, two_factor=False)

    assert not (target / "templates/emails/otp.html").exists()
    assert not (target / "tests/accounts/test_otp.py").exists()
    assert "class OTP" not in (target / "apps/accounts/models.py").read_text(encoding="utf-8")
    assert "otp/verify" not in (target / "apps/accounts/urls.py").read_text(encoding="utf-8")


def test_two_factor_on(tmp_path):
    target = generate(tmp_path, two_factor=True)

    assert (target / "templates/emails/otp.html").exists()
    models = (target / "apps/accounts/models.py").read_text(encoding="utf-8")
    assert "class OTP" in models
    assert "two_factor_enabled" in models
    assert "otp/verify" in (target / "apps/accounts/urls.py").read_text(encoding="utf-8")


def test_docker_toggle(tmp_path):
    with_docker = generate(tmp_path / "a", docker=True)
    without_docker = generate(tmp_path / "b", docker=False)

    for name in ("Dockerfile", "docker-compose.yml", ".dockerignore"):
        assert (with_docker / name).exists()
        assert not (without_docker / name).exists()


def test_database_choice(tmp_path):
    postgres = generate(tmp_path / "a", database="postgres")
    sqlite = generate(tmp_path / "b", database="sqlite")

    assert "psycopg" in (postgres / "requirements/base.txt").read_text(encoding="utf-8")
    assert "psycopg" not in (sqlite / "requirements/base.txt").read_text(encoding="utf-8")
    assert "DATABASE_URL=postgres://" in (postgres / ".env.example").read_text(encoding="utf-8")


def test_api_docs_toggle(tmp_path):
    off = generate(tmp_path, api_docs=False)

    assert "spectacular" not in (off / "conf/settings/base.py").read_text(encoding="utf-8")
    assert "spectacular" not in (off / "conf/urls.py").read_text(encoding="utf-8")
    assert "spectacular" not in (off / "requirements/base.txt").read_text(encoding="utf-8")


def test_env_file_gets_unique_secret_key(tmp_path):
    first = generate(tmp_path / "a")
    second = generate(tmp_path / "b")

    first_env = (first / ".env").read_text(encoding="utf-8")
    assert "SECRET_KEY=change-me" in (first / ".env.example").read_text(encoding="utf-8")
    assert "SECRET_KEY=change-me" not in first_env
    assert first_env != (second / ".env").read_text(encoding="utf-8")


def test_refuses_non_empty_directory(tmp_path):
    target = tmp_path / "myproject"
    target.mkdir()
    (target / "existing.txt").write_text("keep me")

    with pytest.raises(FileExistsError):
        generate_project(ProjectConfig(name="myproject"), target)


@pytest.mark.parametrize("name", ["1project", "my project", "", "my.project"])
def test_rejects_invalid_names(name):
    with pytest.raises(ValueError):
        ProjectConfig(name=name)


def test_cli_non_interactive(tmp_path, capsys):
    target = tmp_path / "cli-project"

    exit_code = main(["new", "cli-project", str(target), "--2fa", "--no-docker", "--database", "sqlite", "-y"])

    assert exit_code == 0
    assert (target / "apps/accounts/models.py").exists()
    assert not (target / "Dockerfile").exists()
    assert "Email OTP / 2FA yes" in capsys.readouterr().out


def test_cli_reports_errors(tmp_path, capsys):
    target = tmp_path / "taken"
    target.mkdir()
    (target / "file").write_text("x")

    assert main(["new", "taken", str(target), "-y"]) == 1
    assert "not empty" in capsys.readouterr().err


# End-to-end: run each generated project's own checks. Needs the generated
# project's dependencies (pip install -r requirements/development.txt).
DJANGO_INSTALLED = all(
    importlib.util.find_spec(module)
    for module in ("django", "rest_framework", "rest_framework_simplejwt", "environ", "corsheaders",
                   "drf_spectacular", "factory", "pytest_django", "PIL")
)


@pytest.mark.skipif(not DJANGO_INSTALLED, reason="generated project's dependencies are not installed")
@pytest.mark.parametrize("two_factor", [False, True], ids=["plain", "2fa"])
def test_generated_project_passes_its_own_checks(tmp_path, two_factor):
    target = generate(tmp_path, database="sqlite", two_factor=two_factor)

    def run(*args):
        result = subprocess.run([sys.executable, *args], cwd=target, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr

    run("manage.py", "makemigrations", "--check", "--dry-run")
    run("manage.py", "spectacular", "--validate", "--fail-on-warn", "--file", str(Path(tmp_path) / "schema.yml"))
    run("-m", "pytest", "-q", "-p", "no:cacheprovider")
