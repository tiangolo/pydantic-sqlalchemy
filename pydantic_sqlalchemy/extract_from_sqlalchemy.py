from dataclasses import dataclass, field
import inspect
from typing import Container, Optional, Type, Dict, Set, Any, List, Union

from sqlalchemy.inspection import inspect as inspect_sqlalchemy_model
from sqlalchemy.orm import CompositeProperty
from sqlalchemy.orm.interfaces import MANYTOONE, MANYTOMANY, ONETOMANY
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlalchemy.sql.type_api import UserDefinedType


@dataclass
class GeneratedImportReference:
    path: List[str]
    name: str
    original: Type

    def __hash__(self):
        return hash(".".join(self.path)) + hash(self.name)

    @staticmethod
    def from_raw(raw: Type):
        module = inspect.getmodule(raw)
        print(module)
        return GeneratedImportReference(
            path=[],
            name=raw.__name__,
            original=raw,
        )

@dataclass
class ExtractedField:
    typ: Union[Type, GeneratedImportReference]
    default: Any
    pass


@dataclass
class ExtractedModel:
    # depends_on: pass
    original_cls: Type
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
    print("Inspecting: ", db_model)
    mapper = inspect_sqlalchemy_model(db_model)
    to_return = ExtractedModel(db_model)
    for attr in mapper.attrs:
        if isinstance(attr, RelationshipProperty):
            model_class = attr.entity.class_
            print('GOT model_class: ', model_class)
            if model_class != db_model:
                to_return.depends_on\
                    .add(GeneratedImportReference.from_raw(model_class))

            if attr.direction == MANYTOMANY:
                print('MANYTOMANY!', attr)
            elif attr.direction == MANYTOONE:  #
                print('MANY_TO_ONE!', attr)
            elif attr.direction == ONETOMANY:  # user.addresses
                print('ONE_TO_MANY!', attr)
            else:
                print(attr.direction, attr)
        elif isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if name in exclude:
                    continue
                column = attr.columns[0]
                python_type: Optional[type] = None
                if hasattr(column.type, "impl"):
                    if hasattr(column.type.impl, "python_type"):
                        python_type = column.type.impl.python_type
                elif isinstance(column.type, UserDefinedType):
                    python_type = type(column.type)
                elif hasattr(column.type, "python_type"):
                        python_type = column.type.python_type
                assert python_type, f"Could not infer python_type for {column}"
                default = None
                if column.default is None and not column.nullable:
                    default = ...
                to_return.fields[name] = ExtractedField(python_type, default)
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
