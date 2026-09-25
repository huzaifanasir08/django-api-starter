"""Command line interface: ``django-starter new <name>``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .generator import DATABASES, ProjectConfig, generate_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="django-starter",
        description="Generate a production-ready Django REST API project.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subcommands = parser.add_subparsers(dest="command", required=True)

    new = subcommands.add_parser("new", help="Create a new project.")
    new.add_argument("name", help="Project name, e.g. myproject.")
    new.add_argument("directory", nargs="?", help="Where to create it (default: ./<name>).")
    new.add_argument("--database", choices=DATABASES, help="Database backend.")
    new.add_argument(
        "--2fa", dest="two_factor", action=argparse.BooleanOptionalAction,
        help="Email OTP: verify email on signup and optional per-user two-factor login.",
    )
    new.add_argument(
        "--celery", action=argparse.BooleanOptionalAction,
        help="Celery background tasks with Redis (also used as the cache).",
    )
    new.add_argument("--docker", action=argparse.BooleanOptionalAction, help="Add Dockerfile and docker-compose.yml.")
    new.add_argument("--api-docs", action=argparse.BooleanOptionalAction, help="Add OpenAPI schema and Swagger UI.")
    new.add_argument(
        "-y", "--yes", action="store_true",
        help="Don't prompt; use defaults for any option not given.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    interactive = not args.yes and sys.stdin.isatty()

    defaults = ProjectConfig.__dataclass_fields__
    database = args.database or (
        _choose("Database", DATABASES, defaults["database"].default) if interactive
        else defaults["database"].default
    )
    options = {}
    for key, question in (
        ("two_factor", "Enable email OTP / two-factor authentication?"),
        ("celery", "Add Celery background tasks with Redis?"),
        ("docker", "Add Docker support?"),
        ("api_docs", "Add API documentation (Swagger)?"),
    ):
        value = getattr(args, key)
        if value is None:
            value = _confirm(question, defaults[key].default) if interactive else defaults[key].default
        options[key] = value

    try:
        config = ProjectConfig(name=args.name, database=database, **options)
        target = Path(args.directory or args.name).resolve()
        generate_project(config, target)
    except (ValueError, FileExistsError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    _print_summary(config, target)
    return 0


def _confirm(question: str, default: bool) -> bool:
    hint = "Y/n" if default else "y/N"
    while True:
        answer = input(f"{question} [{hint}] ").strip().lower()
        if not answer:
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False


def _choose(question: str, choices: tuple[str, ...], default: str) -> str:
    while True:
        answer = input(f"{question} ({'/'.join(choices)}) [{default}] ").strip().lower()
        if not answer:
            return default
        if answer in choices:
            return answer


def _print_summary(config: ProjectConfig, target: Path) -> None:
    def mark(enabled: bool) -> str:
        return "yes" if enabled else "no"

    print(f"\nCreated {config.name} in {target}\n")
    print(f"  Database        {config.database}")
    print(f"  Email OTP / 2FA {mark(config.two_factor)}")
    print(f"  Celery + Redis  {mark(config.celery)}")
    print(f"  Docker          {mark(config.docker)}")
    print(f"  API docs        {mark(config.api_docs)}")
    print("\nNext steps:\n")
    print(f"  cd {target.name}")
    if config.docker:
        print("  docker compose up --build")
        print("\n  or, without Docker:\n")
    print("  python -m venv .venv  (then activate it)")
    print("  pip install -r requirements/development.txt")
    if config.database == "postgres":
        print("  # point DATABASE_URL in .env at your PostgreSQL server")
    if config.celery:
        print("  # start Redis and point REDIS_URL in .env at it")
    print("  python manage.py migrate")
    print("  python manage.py createsuperuser")
    print("  python manage.py runserver")
    if config.celery:
        print("  celery -A conf worker -l info   (in a second terminal; add --pool=solo on Windows)")
        print("  celery -A conf beat -l info     (in a third terminal, for scheduled tasks)")
    print()
