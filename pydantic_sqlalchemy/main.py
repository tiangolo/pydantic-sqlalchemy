from typing import Container, Optional, Type

from pydantic import ConfigDict, BaseModel, create_model
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty
from pydantic.config import ConfigDict


config = ConfigDict(from_attributes=True, populate_by_name=True)


def sqlalchemy_to_pydantic(
    db_model: Type, *, config: ConfigDict = config, exclude: Container[str] = []
) -> Type[BaseModel]:
    mapper = inspect(db_model)
    fields = {}
    for attr in mapper.attrs:
        if (
            not isinstance(attr, ColumnProperty)
            or not attr.columns):
            continue
        name = attr.key
        if name in exclude:
            continue
        column = attr.columns[0]
        python_type: Optional[type] = None
        if hasattr(column.type, "python_type"):
            python_type = column.type.python_type
        elif hasattr(column.type, "impl") and hasattr(column.type.impl, "python_type"):
            python_type = column.type.impl.python_type
        else:
            assert python_type, f"Could not infer python_type for {column}"
        default = None
        if column.default is None and not column.nullable:
            default = ...
        fields[name] = (python_type, default)
    pydantic_model = create_model(
        db_model.__name__, __config__=config, **fields  # type: ignore
    )
    return pydantic_model
