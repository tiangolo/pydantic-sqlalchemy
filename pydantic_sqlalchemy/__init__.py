try:  # pragma: nocover
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

from .main import sqlalchemy_to_pydantic

__version__ = version(__package__)
