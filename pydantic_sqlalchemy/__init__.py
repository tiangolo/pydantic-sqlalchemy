from importlib_metadata import version

__version__ = version(__package__)

from .main import sqlalchemy_to_pydantic
