"""Generate a production-ready Django REST API project."""

from .generator import ProjectConfig, generate_project

__version__ = "0.2.0"

__all__ = ["ProjectConfig", "generate_project", "__version__"]
