from typing import Container, Optional, Type

from pydantic import BaseConfig, BaseModel, create_model, Field
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.sql.selectable import Select


class OrmConfig(BaseConfig):
    orm_mode = True


def __column_to_field(column):
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

    return (
        python_type,
        Field(
            **{
                "description": str(column.comment) if column.comment else None,
                "default": default,
            }
        ),
    )


def sqlalchemy_to_pydantic(
    db_model: Type, *, config: Type = OrmConfig, exclude: Container[str] = [],
) -> Type[BaseModel]:
    mapper = inspect(db_model)
    fields = {}
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if name in exclude:
                    continue
                column = attr.columns[0]
                fields[name] = __column_to_field(column)
    pydantic_model = create_model(
        db_model.__name__, __config__=config, **fields  # type: ignore
    )
    return pydantic_model


def sqlalchemy_select_to_pydantic(
    module_name: str, sql: Select, *, config: Type = OrmConfig,
) -> Type[BaseModel]:
    fields = {}
    for attr in sql.selected_columns:
        name = attr.key
        column = list(attr.base_columns)[0]
        fields[name] = __column_to_field(column)
    pydantic_model = create_model(
        module_name, __config__=config, **fields  # type: ignore
    )
    return pydantic_model
