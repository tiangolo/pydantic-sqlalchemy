from copy import copy
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Type

from pydantic import BaseConfig, BaseModel, create_model
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlalchemy.util import ImmutableProperties

_schema_cache: Set[str] = set()


class OrmConfig(BaseConfig):
    orm_mode = True


def get_field_attr(attr: ColumnProperty) -> Any:
    assert len(attr.columns) == 1
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
    return python_type, default


def _sqlalchemy_to_pydantic(
    mapper: Mapper,
    include: Iterable[str],
    exclude: Iterable[str],
    schema_name: str,
    depth: int,
    father_db_names: List[str],
    config: Type = OrmConfig,
) -> Type[BaseModel]:
    fields: Dict[str, Tuple[Any, Any]] = {}
    father_db_names.append(mapper.class_.__name__)
    model_fields: ImmutableProperties = mapper.attrs  # type: ignore
    for model_field in model_fields:
        if (
            (include and model_field.key in include)
            or (exclude and model_field.key not in exclude)
            or (not include and not exclude)
        ):
            if isinstance(model_field, RelationshipProperty):
                if depth <= 0:
                    continue
                else:
                    if model_field.mapper.class_.__name__ in father_db_names:
                        continue
                    if include:
                        subinclude = [
                            i.replace(model_field.key + ".", "")
                            for i in include
                            if i.startswith(model_field.key + ".")
                        ]
                    else:
                        subinclude = []
                    if exclude:
                        subexclude = [
                            i.replace(model_field.key + ".", "")
                            for i in exclude
                            if i.startswith(model_field.key + ".")
                        ]
                    else:
                        subexclude = []
                    children_schema = _sqlalchemy_to_pydantic(
                        model_field.mapper,
                        subinclude,
                        subexclude,
                        schema_name + "." + model_field.key,
                        depth - 1,
                        father_db_names,
                        config,
                    )
                    if model_field.uselist:
                        fields[model_field.key] = List[children_schema], []  # type: ignore
                    else:
                        remote_side = copy(model_field.remote_side).pop()
                        fields[model_field.key] = (
                            children_schema,
                            None if remote_side.nullable else ...,
                        )

            else:
                fields[model_field.key] = get_field_attr(model_field)

    return create_model(
        schema_name, __config__=config, **fields  # type: ignore
    )


def sqlalchemy_to_pydantic(
    db_model: Type,
    *,
    name: str,
    config: Type = OrmConfig,
    include: Optional[Iterable[str]] = None,
    exclude: Optional[Iterable[str]] = None,
    depth: int = 0,
) -> Type[BaseModel]:
    if name in _schema_cache:
        raise AttributeError("Can't create the same name model twice.")
    if include and exclude:
        raise AttributeError("Between include and exclude must at least one is None")
    if not include:
        include = []
    if not exclude:
        exclude = []
    mapper = inspect(db_model)
    schema = _sqlalchemy_to_pydantic(mapper, include, exclude, name, depth, [], config)
    _schema_cache.add(name)
    return schema
