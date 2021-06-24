from typing import Optional, Type, List

from pydantic import BaseConfig, BaseModel, create_model
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import RelationshipProperty

_schema_cache = {}


class OrmConfig(BaseConfig):
    orm_mode = True


def get_field_attr(attr):
    if attr.columns:
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
    return None


def _sqlalchemy_to_pydantic(mapper, include, exclude, schema_name, depth, father_db_names: List[str],
                            config: Type = OrmConfig, ) -> Optional[Type[BaseModel]]:
    fields = {}
    if not include:
        include = []
    if not exclude:
        exclude = []
    if mapper.class_.__name__ in father_db_names:
        return None
    else:
        father_db_names.append(mapper.class_.__name__)
        model_fields = mapper.attrs
        for model_field in model_fields:
            if include and model_field.key in include or exclude and model_field.key not in exclude or not include and not exclude:
                if isinstance(model_field, RelationshipProperty):
                    if depth <= 0:
                        continue
                    else:
                        children_schema = _sqlalchemy_to_pydantic(model_field.mapper, include, exclude,
                                                                  schema_name + "." + model_field.key,
                                                                  depth - 1,
                                                                  father_db_names, config)
                        if children_schema:
                            fields[model_field.key] = children_schema
                else:
                    fields[model_field.key] = get_field_attr(model_field)

        return create_model(
            schema_name, __config__=config, **fields  # type: ignore
        )


def sqlalchemy_to_pydantic(
        db_model: Type, *, name: str, config: Type = OrmConfig,
        include=None, exclude=None, depth=0,
) -> Type[BaseModel]:
    if _schema_cache.get(name):
        return _schema_cache[name]

    mapper = inspect(db_model)
    schema = _sqlalchemy_to_pydantic(mapper, include, exclude, name, depth, [], config)
    _schema_cache[name] = schema
    print(schema.schema())
    return schema
