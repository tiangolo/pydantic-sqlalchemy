from typing import Container, Optional, Type, Dict, Any

from pydantic import BaseModel, create_model
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty


class OrmConfig:
    model_config = {"from_attributes": True}


def sqlalchemy_to_pydantic(
    db_model: Type, *, config: Type = OrmConfig, exclude: Container[str] = []
) -> Type[BaseModel]:
    mapper = inspect(db_model)
    fields: Dict[str, Any] = {}

    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if name in exclude:
                    continue
                column = attr.columns[0]
                python_type: Optional[type] = None

                if hasattr(column.type, "impl") and hasattr(
                    column.type.impl, "python_type"
                ):
                    python_type = column.type.impl.python_type
                elif hasattr(column.type, "python_type"):
                    python_type = column.type.python_type

                if not python_type:
                    raise ValueError(
                        f"Could not infer python_type for column '{name}' in model '{db_model.__name__}'"
                    )

                default = None
                if column.default is None and not column.nullable:
                    default = ...

                fields[name] = (python_type, default)

    pydantic_model = create_model(
        db_model.__name__, **fields, __config__=config.model_config  # type: ignore
    )
    return pydantic_model
