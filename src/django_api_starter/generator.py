"""Render the project template into a new directory.

Template conventions (everything lives under ``template/``):

* ``*.j2`` files are rendered with Jinja2 and lose the ``.j2`` suffix.
  Python files are always ``.j2`` so pip never tries to byte-compile them.
* Any other file is copied byte-for-byte (e.g. Django email templates, whose
  ``{{ }}`` syntax must reach the generated project untouched).
* A leading ``dot-`` becomes ``.`` (``dot-gitignore`` -> ``.gitignore``), because
  dotfiles are easy to lose when building a wheel.
* Files listed in ``OPTIONAL_FILES`` are only written when their feature is on.
"""

from __future__ import annotations

import re
import secrets
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

TEMPLATE_DIR = Path(__file__).parent / "template"

DATABASES = ("postgres", "sqlite")

# Template path (relative, before renaming) -> ProjectConfig flag that enables it.
OPTIONAL_FILES = {
    "Dockerfile.j2": "docker",
    "docker-compose.yml.j2": "docker",
    "dot-dockerignore": "docker",
    "templates/emails/otp.html": "two_factor",
    "tests/accounts/test_otp.py.j2": "two_factor",
    "conf/celery.py.j2": "celery",
    "core/tasks.py.j2": "celery",
    "apps/accounts/tasks.py.j2": "celery",
    "tests/accounts/test_tasks.py.j2": "celery",
}

PROJECT_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


@dataclass(frozen=True)
class ProjectConfig:
    name: str
    database: str = "postgres"
    two_factor: bool = False
    celery: bool = False
    docker: bool = True
    api_docs: bool = True

    def __post_init__(self):
        if not PROJECT_NAME_RE.match(self.name):
            raise ValueError(
                f"Invalid project name {self.name!r}: use letters, digits, '-' or '_', "
                "starting with a letter."
            )
        if self.database not in DATABASES:
            raise ValueError(f"Unknown database {self.database!r}; choose from {', '.join(DATABASES)}.")

    @property
    def slug(self) -> str:
        """Identifier-safe form of the name (used for database names)."""
        return self.name.lower().replace("-", "_")


def generate_project(config: ProjectConfig, target: Path) -> list[Path]:
    """Write the project for ``config`` into ``target`` and return the files created."""
    target = Path(target)
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(f"Target directory {target} already exists and is not empty.")

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    context = {**asdict(config), "slug": config.slug, "secret_key": _secret_key()}
    enabled = asdict(config)

    created = []
    for source in sorted(TEMPLATE_DIR.rglob("*")):
        relative = source.relative_to(TEMPLATE_DIR)
        if source.is_dir() or "__pycache__" in relative.parts:
            continue
        flag = OPTIONAL_FILES.get(relative.as_posix())
        if flag and not enabled[flag]:
            continue

        destination = target / _output_path(relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix == ".j2":
            content = env.get_template(relative.as_posix()).render(context)
            destination.write_text(content, encoding="utf-8", newline="\n")
        else:
            shutil.copyfile(source, destination)
        created.append(destination)

    # A ready-to-use .env for local development (git-ignored); .env.example is the committed copy.
    env_file = target / ".env"
    env_file.write_text(
        (target / ".env.example").read_text(encoding="utf-8").replace(
            "SECRET_KEY=change-me", f"SECRET_KEY={context['secret_key']}"
        ),
        encoding="utf-8",
        newline="\n",
    )
    created.append(env_file)
    return created


def _output_path(relative: Path) -> Path:
    name = relative.name.removesuffix(".j2")
    if name.startswith("dot-"):
        name = "." + name.removeprefix("dot-")
    return relative.parent / name


def _secret_key() -> str:
    # URL-safe characters only, so the key survives .env parsing unquoted.
    return secrets.token_urlsafe(50)
