from typing import Any, Container, Dict, Optional, Tuple, Type, cast

from pydantic import BaseConfig, BaseModel, Field, create_model
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.sql.base import DialectKWArgs, _DialectArgView

__field_arguments = (
    "alias",
    "title",
    "description",
    "const",
    "gt",
    "ge",
    "lt",
    "le",
    "multiple_of",
    "min_items",
    "max_items",
    "min_length",
    "max_length",
    "regex",
    "example",
)


def make_field(
    column: DialectKWArgs, python_type: Optional[type], default: Any
) -> Tuple[Optional[type], Any]:
    arguments: Dict[str, Any]
    dialect_options = column.dialect_options
    cast(_DialectArgView, dialect_options)
    if "pydantic" not in dialect_options:
        return python_type, default
    pydantic_args = dialect_options["pydantic"]
    arguments = {
        arg: pydantic_args[arg] for arg in __field_arguments if arg in pydantic_args
    }
    return python_type, Field(default, **arguments)


class OrmConfig(BaseConfig):
    orm_mode = True


def sqlalchemy_to_pydantic(
    db_model: Type, *, config: Type = OrmConfig, exclude: Container[str] = []
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
                fields[name] = make_field(column, python_type, default)
    pydantic_model = create_model(
        db_model.__name__, __config__=config, **fields  # type: ignore
    )
    return pydantic_model
