from dataclasses import dataclass, field
from datetime import datetime
from typing import Container, Optional, Type, Dict, Set, Any, Union

from sqlalchemy import (
    Enum as SQLAlchemyEnum,
    Date as SQLAlchemyDate,
)
from sqlalchemy.inspection import inspect as inspect_sqlalchemy_model
from sqlalchemy.orm import CompositeProperty
from sqlalchemy.orm.interfaces import MANYTOONE, MANYTOMANY, ONETOMANY
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlalchemy.sql.type_api import UserDefinedType

from pydantic_sqlalchemy.module_path_typ import ModulePathType


@dataclass
class GeneratedImportReference:
    module_path: ModulePathType
    name: str
    original: Type

    def __hash__(self):
        return hash(".".join(self.module_path)) + hash(self.name)

    @staticmethod
    def from_raw(raw: Type):
        # module_path = ModulePathType(module.__path__) if module is not None else None
        return GeneratedImportReference(
            module_path=ModulePathType(raw.__module__),
            name=raw.__name__,
            original=raw,
        )


@dataclass
class ExtractedField:
    typ: Union[Type, GeneratedImportReference, SQLAlchemyEnum]
    is_nullable: bool
    is_array: bool
    default: Any = None
    pass


@dataclass
class ExtractedModel:
    # depends_on: pass
    original_cls: Type
    ref: GeneratedImportReference
    fields: Dict[str, ExtractedField] = field(default_factory=dict)
    depends_on: Set[Union[Type, GeneratedImportReference]] = field(default_factory=set)

    def __hash__(self):
        return id(self)

    def __str__(self):
        return f"""ExtractedModel(
            {self.original_cls}, 
            {self.fields}, 
            {self.depends_on}
        )"""


def extract_from_sqlalchemy(
    db_model: Type, *, exclude: Container[str] = []
):
    mapper = inspect_sqlalchemy_model(db_model)
    to_return = ExtractedModel(
        original_cls=db_model,
        ref=GeneratedImportReference.from_raw(db_model),
    )
    for attr in mapper.attrs:
        if isinstance(attr, RelationshipProperty):
            model_class = attr.entity.class_
            print('GOT model_class: ', model_class)
            ref = GeneratedImportReference.from_raw(model_class)
            if model_class != db_model:
                to_return.depends_on\
                    .add(ref)
            name = attr.key
            if attr.direction == MANYTOMANY:
                to_return.fields[name] = ExtractedField(ref, is_array=True, is_nullable=False, default=None)
            elif attr.direction == MANYTOONE:  #
                to_return.fields[name] = ExtractedField(ref, is_array=False, is_nullable=False, default=None)
            elif attr.direction == ONETOMANY:  # user.addresses
                to_return.fields[name] = ExtractedField(ref, is_array=True, is_nullable=True, default=None)
            else:
                print("NOT PROCESSED: ", attr.direction, attr)
        elif isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if name in exclude:
                    continue
                column = attr.columns[0]
                python_type: Union[type, None] = None
                if isinstance(column.type, SQLAlchemyEnum):
                    python_type = column.type
                elif isinstance(column.type, SQLAlchemyDate):
                    python_type = datetime
                elif hasattr(column.type, "impl"):
                    if hasattr(column.type.impl, "python_type"):
                        python_type = column.type.impl.python_type
                elif isinstance(column.type, UserDefinedType):
                    python_type = type(column.type)
                elif hasattr(column.type, "python_type"):
                        python_type = column.type.python_type
                assert python_type, f"Could not infer python_type for {column}"
                default = ... if column.default is None else column.default
                to_return.fields[name] = ExtractedField(
                    typ=python_type,
                    is_array=False,
                    is_nullable=column.nullable,
                    default=default,
                )
        elif isinstance(attr, CompositeProperty):
            # FIXME
            print("Composite property!", attr)
            # import pdb
            # pdb.set_trace()
        else:
            # import pdb
            # pdb.set_trace()
            print("wtf is this property!", attr)
            pass
    return to_return
