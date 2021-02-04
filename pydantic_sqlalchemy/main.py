import inspect
import typing
from typing import Container, Optional, Type

import sqlalchemy.inspection
from pydantic import BaseConfig, BaseModel, create_model
from sqlalchemy.orm.attributes import InstrumentedAttribute, QueryableAttribute
from sqlalchemy.orm.properties import ColumnProperty


class OrmConfig(BaseConfig):
    orm_mode = True


def sqlalchemy_to_pydantic(
    db_model: Type, *, config: Type = OrmConfig, exclude: Container[str] = None
) -> Type[BaseModel]:
    exclude = exclude or []

    mapper = sqlalchemy.inspection.inspect(db_model)
    fields = {}
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if name in exclude:
                    continue
                column = attr.columns[0]
                python_type: Optional[type] = None
                if hasattr(column.type, "impl"):
                    if hasattr(column.type.impl, "python_type"):
                        python_type = column.type.impl.python_type
                elif hasattr(column.type, "python_type"):
                    python_type = column.type.python_type
                assert python_type, f"Could not infer python_type for {column}"
                default = None
                if column.default is None and not column.nullable:
                    default = ...
                fields[name] = (python_type, default)

    for name, attr in inspect.getmembers(db_model):
        if isinstance(attr, property) or (
            isinstance(attr, QueryableAttribute)
            and not isinstance(attr, InstrumentedAttribute)
        ):
            if name in exclude:
                continue
            return_type = typing.get_type_hints(attr.fget).get("return")
            if return_type:
                fields[name] = (return_type, None)

    pydantic_model = create_model(
        db_model.__name__, __config__=config, **fields  # type: ignore
    )

    return pydantic_model
