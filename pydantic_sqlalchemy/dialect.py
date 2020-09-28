from sqlalchemy.dialects import registry
from sqlalchemy.engine.default import DefaultDialect


class PydanticDialect(DefaultDialect):
    """
    Dialect to hide sqlalchemy error messages
    """

    pass


registry.register("pydantic", __name__, "PydanticDialect")
