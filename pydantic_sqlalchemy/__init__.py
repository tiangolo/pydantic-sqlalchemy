try:  # pragma: nocover
    from importlib.metadata import version  # type: ignore
except ImportError:
    from importlib_metadata import version  # type: ignore

from .main import sqlalchemy_to_pydantic

__version__ = version(__package__)
