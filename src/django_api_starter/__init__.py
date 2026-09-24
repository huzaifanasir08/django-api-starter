"""Generate a production-ready Django REST API project."""

from .generator import ProjectConfig, generate_project

__version__ = "0.1.1"

__all__ = ["ProjectConfig", "generate_project", "__version__"]
